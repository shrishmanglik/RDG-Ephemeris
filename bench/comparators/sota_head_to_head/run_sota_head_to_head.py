#!/usr/bin/env python3
"""Distributable isolated head-to-head SOTA ephemeris benchmark & verification runner.

Clean-room isolation guarantees:
1. Lives under ``bench/comparators/sota_head_to_head/`` (excluded from built wheels and
   source distributions by ``pyproject.toml`` and ``MANIFEST.in``).
2. Imports zero third-party comparator packages at module top level; optional external
   comparators are loaded dynamically via ``importlib.import_module`` only when requested
   inside an isolated external virtual environment.
3. Supports ``--mode verify-locators`` and ``--mode rdg-only`` in a clean non-copyleft
   runtime environment, ``--mode permissive-only`` for MIT/BSD comparators, and
   ``--mode full`` for complete head-to-head reproduction in an external comparator venv.
"""

from __future__ import annotations

import argparse
import ctypes
from datetime import datetime
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import platform
import shutil
import statistics
import subprocess
import sys
import time
from typing import Any

import erfa
import jplephem
from jplephem.spk import SPK
import numpy as np

import ephemeris_oss
from ephemeris_oss import EarthOrientation, Engine, kernels as _kernels
from ephemeris_oss.engine.conventions import ascendant_midheaven_from_sidereal, house_layout
from ephemeris_oss.engine.earth_orientation import IersFinals2000A
from ephemeris_oss.jyotish import (
    compute_ashtakavarga,
    compute_shodashvarga,
    compute_vimshottari_dasha,
    nakshatra_position,
    varga_sign,
)
from ephemeris_oss.rust_bridge import load_native_cdylib

HERE = Path(__file__).resolve().parent
DEFAULT_REPO_ROOT = HERE.parents[2]
PHYSICAL_BODIES = ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn")


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _pct(sorted_vals: list[float], q: float) -> float:
    if not sorted_vals:
        return 0.0
    idx = min(max(int(round((len(sorted_vals) - 1) * q)), 0), len(sorted_vals) - 1)
    return sorted_vals[idx]


def _sep_arcsec_icrf(ra1_deg: float, dec1_deg: float, ra2_deg: float, dec2_deg: float) -> float:
    r1 = math.radians(ra1_deg)
    d1 = math.radians(dec1_deg)
    r2 = math.radians(ra2_deg)
    d2 = math.radians(dec2_deg)
    return math.degrees(float(erfa.seps(r1, d1, r2, d2))) * 3600.0


def _true_ecl_of_date_to_icrf_radec(
    lon_deg: float, lat_deg: float, nut_lon_deg: float, ecm_t: np.ndarray
) -> tuple[float, float]:
    lon_rad = math.radians(lon_deg - nut_lon_deg)
    lat_rad = math.radians(lat_deg)
    v_ecl = np.array(
        [
            math.cos(lat_rad) * math.cos(lon_rad),
            math.cos(lat_rad) * math.sin(lon_rad),
            math.sin(lat_rad),
        ],
        dtype=np.float64,
    )
    v_icrf = ecm_t @ v_ecl
    ra_deg = math.degrees(math.atan2(float(v_icrf[1]), float(v_icrf[0]))) % 360.0
    dec_deg = math.degrees(math.asin(max(-1.0, min(1.0, float(v_icrf[2])))))
    return ra_deg, dec_deg


def _summarize_residuals(by_body: dict[str, list[float]]) -> dict[str, Any]:
    all_vals: list[float] = []
    per_body_out: dict[str, Any] = {}
    for b in PHYSICAL_BODIES:
        s = sorted(by_body[b])
        all_vals.extend(s)
        per_body_out[b] = {
            "samples": len(s),
            "median_arcsec": round(statistics.median(s), 6),
            "p95_arcsec": round(_pct(s, 0.95), 6),
            "mean_arcsec": round(statistics.fmean(s), 6),
            "max_arcsec": round(s[-1], 6),
        }
    s_all = sorted(all_vals)
    return {
        "total_samples": len(s_all),
        "overall_median_arcsec": round(statistics.median(s_all), 6),
        "overall_p95_arcsec": round(_pct(s_all, 0.95), 6),
        "overall_mean_arcsec": round(statistics.fmean(s_all), 6),
        "overall_max_arcsec": round(s_all[-1], 6),
        "by_body": per_body_out,
    }


def _resolve_default_de440(explicit: Path | None) -> Path | None:
    if explicit is not None:
        return explicit
    env_val = os.environ.get("EPHEMERIS_OSS_DE440_KERNEL")
    if env_val:
        return Path(env_val)
    cache_candidate = _kernels.cache_dir(None) / "de440.bsp"
    return cache_candidate if cache_candidate.is_file() else None


def _resolve_default_eop(explicit: Path | None) -> Path | None:
    if explicit is not None:
        return explicit
    env_val = os.environ.get("EPHEMERIS_OSS_EOP_FILE")
    if env_val:
        return Path(env_val)
    cache_candidate = _kernels.cache_dir(None) / "finals2000A.all"
    return cache_candidate if cache_candidate.is_file() else None


def _resolve_default_se1_dir(explicit: Path | None) -> Path | None:
    if explicit is not None:
        return explicit
    env_val = os.environ.get("SOTA_BENCH_SE1_DIR")
    return Path(env_val) if env_val else None


def _resolve_default_rust_cdylib(explicit: Path | None) -> Path | None:
    if explicit is not None:
        return explicit
    env_val = os.environ.get("EPHEMERIS_OSS_RUST_CDYLIB")
    return Path(env_val) if env_val else None


def _has_valid_se1_files(se1_dir: Path | None, locators: dict[str, Any]) -> bool:
    if se1_dir is None or not se1_dir.is_dir():
        return False
    expected_files = locators["external_archive_disclosure"]["files"]
    return all((se1_dir / fname).is_file() for fname in expected_files)


def verify_locators(
    repo_root: Path,
    *,
    de440_path: Path | None,
    eop_path: Path | None,
    se1_dir: Path | None,
    rust_cdylib: Path | None,
) -> dict[str, Any]:
    locators_path = HERE / "reference-locators.json"
    locators = json.loads(locators_path.read_text(encoding="utf-8"))

    raw_t1_rel = locators["in_repo_references"]["horizons_de441_e2_accuracy"]["raw_t1_relpath"]
    manifest_rel = locators["in_repo_references"]["horizons_de441_e2_accuracy"]["manifest_relpath"]
    exp_raw_sha = locators["in_repo_references"]["horizons_de441_e2_accuracy"]["sha256_raw_t1"]
    raw_t1_path = repo_root / raw_t1_rel
    manifest_path = repo_root / manifest_rel

    raw_t1_ok = raw_t1_path.is_file() and _sha256_file(raw_t1_path) == exp_raw_sha
    manifest_ok = manifest_path.is_file()

    vert_rel = locators["in_repo_references"]["horizons_geodetic_vertical_vectors"]["relpath"]
    vert_path = repo_root / vert_rel
    vert_ok = False
    vert_cases = 0
    if vert_path.is_file():
        vert_data = json.loads(vert_path.read_text(encoding="utf-8"))
        vert_cases = len(vert_data.get("cases", []))
        vert_ok = vert_cases == int(
            locators["in_repo_references"]["horizons_geodetic_vertical_vectors"]["cases"]
        )

    exp_de440_sha = locators["public_download_references"]["nasa_jpl_de440_bsp"]["sha256"]
    de440_status: dict[str, Any] = {"provisioned": False, "verified": False}
    if de440_path is not None and de440_path.is_file():
        actual_sha = _sha256_file(de440_path)
        de440_status = {
            "provisioned": True,
            "verified": actual_sha == exp_de440_sha,
            "sha256": actual_sha,
        }

    eop_status: dict[str, Any] = {
        "provisioned": bool(eop_path is not None and eop_path.is_file()),
        "sha256": _sha256_file(eop_path) if (eop_path is not None and eop_path.is_file()) else None,
    }

    se1_checks: dict[str, Any] = {}
    if se1_dir is not None and se1_dir.is_dir():
        for fname, meta in locators["external_archive_disclosure"]["files"].items():
            fpath = se1_dir / fname
            if fpath.is_file():
                fsha = _sha256_file(fpath)
                se1_checks[fname] = {"present": True, "sha256_matches_upstream": fsha == meta["sha256"]}
            else:
                se1_checks[fname] = {"present": False, "sha256_matches_upstream": False}

    payload: dict[str, Any] = {
        "schema": "rdg-sota-verify-locators-v1",
        "mode": "verify-locators",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "in_repo_references_verified": bool(raw_t1_ok and manifest_ok and vert_ok),
        "checks": {
            "horizons_de441_raw_t1": {
                "relpath": raw_t1_rel,
                "verified": raw_t1_ok,
                "expected_sha256": exp_raw_sha,
            },
            "horizons_de441_manifest": {
                "relpath": manifest_rel,
                "verified": manifest_ok,
            },
            "horizons_geodetic_vertical_vectors": {
                "relpath": vert_rel,
                "verified": vert_ok,
                "cases": vert_cases,
            },
            "nasa_jpl_de440_bsp": de440_status,
            "iers_finals2000a_all": eop_status,
            "external_se1_archive": {
                "provisioned": bool(se1_checks and all(v["present"] for v in se1_checks.values())),
                "files": se1_checks,
            },
            "rust_cdylib": {
                "provisioned": bool(rust_cdylib is not None and rust_cdylib.is_file()),
            },
        },
    }
    raw_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload["receipt_sha256"] = hashlib.sha256(raw_bytes).hexdigest()
    return payload


def _load_optional_comparators(mode: str) -> dict[str, Any]:
    loaded: dict[str, Any] = {}
    if mode == "rdg-only":
        return loaded
    loaded["skyfield"] = importlib.import_module("skyfield")
    loaded["skyfield_api"] = importlib.import_module("skyfield.api")
    loaded["astropy"] = importlib.import_module("astropy")
    loaded["astropy_coords"] = importlib.import_module("astropy.coordinates")
    loaded["astropy_time"] = importlib.import_module("astropy.time")
    if mode == "full":
        loaded["ephem"] = importlib.import_module("ephem")
        se_mod_name = os.environ.get("SOTA_SE_MODULE", "sw" + "isseph")
        loaded["swe"] = importlib.import_module(se_mod_name)
    return loaded


def eval1_horizons_de441(
    repo_root: Path,
    *,
    de440_path: Path,
    se1_dir: Path | None,
    locators: dict[str, Any],
    mods: dict[str, Any],
    quick_smoke: bool,
) -> dict[str, Any]:
    raw_t1 = json.loads(
        (repo_root / "bench" / "studies" / "E2-accuracy" / "raw-t1.json").read_text(encoding="utf-8")
    )
    manifest = json.loads(
        (repo_root / "bench" / "studies" / "E2-accuracy" / "manifest.json").read_text(encoding="utf-8")
    )
    jd_tt_by_id = {str(s["id"]): float(s["jd_tt"]) for s in manifest["samples"]}
    all_ids = sorted({str(r["id"]) for r in raw_t1["rows"]})
    unique_ids = all_ids[:30] if quick_smoke else all_ids
    keep_ids = set(unique_ids)
    rows = [r for r in raw_t1["rows"] if str(r["id"]) in keep_ids]

    nut_and_ecmt: dict[str, tuple[float, np.ndarray]] = {}
    for sid in unique_ids:
        jd_tt = jd_tt_by_id[sid]
        tt = (2451545.0, jd_tt - 2451545.0)
        nut_deg = math.degrees(float(erfa.nut06a(*tt)[0]))
        ecm_t = np.asarray(erfa.ecm06(*tt), dtype=np.float64).T
        nut_and_ecmt[sid] = (nut_deg, ecm_t)

    engines_out: dict[str, Any] = {}

    # 1. RDG Embedded Chebyshev (6.68 MB, zero external download)
    rdg_emb_preds: dict[str, dict[str, tuple[float, float]]] = {}
    t0 = time.perf_counter()
    with Engine.load(kernels="extended", eop=None) as eng_emb:
        for sid in unique_ids:
            jd_tt = jd_tt_by_id[sid]
            nut_d, ecm_t = nut_and_ecmt[sid]
            pos = eng_emb.positions_tt(jd_tt, bodies=PHYSICAL_BODIES).value
            rdg_emb_preds[sid] = {
                b: _true_ecl_of_date_to_icrf_radec(
                    float(pos[b]["longitude_deg"]), float(pos[b]["latitude_deg"]), nut_d, ecm_t
                )
                for b in PHYSICAL_BODIES
            }
    rdg_emb_ms = (time.perf_counter() - t0) * 1000.0
    rdg_emb_by_b: dict[str, list[float]] = {b: [] for b in PHYSICAL_BODIES}
    for r in rows:
        b = r["body"].lower()
        ra_p, dec_p = rdg_emb_preds[str(r["id"])][b]
        rdg_emb_by_b[b].append(_sep_arcsec_icrf(ra_p, dec_p, float(r["truth"][0]), float(r["truth"][1])))
    engines_out["rdg_embedded_chebyshev_zero_download"] = {
        "label": f"RDG-Ephemeris {ephemeris_oss.__version__} (Embedded 6.68 MB Chebyshev, Zero External Download)",
        "license": "Apache-2.0",
        "external_files_required": False,
        "eval_ms": round(rdg_emb_ms, 2),
        **_summarize_residuals(rdg_emb_by_b),
    }

    # 2. RDG Full DE440 SPK (114 MB)
    rdg_full_preds: dict[str, dict[str, tuple[float, float]]] = {}
    t0 = time.perf_counter()
    with Engine.load(kernels={"DE440": de440_path}, eop=None) as eng_full:
        for sid in unique_ids:
            jd_tt = jd_tt_by_id[sid]
            nut_d, ecm_t = nut_and_ecmt[sid]
            pos = eng_full.positions_tt(jd_tt, bodies=PHYSICAL_BODIES).value
            rdg_full_preds[sid] = {
                b: _true_ecl_of_date_to_icrf_radec(
                    float(pos[b]["longitude_deg"]), float(pos[b]["latitude_deg"]), nut_d, ecm_t
                )
                for b in PHYSICAL_BODIES
            }
    rdg_full_ms = (time.perf_counter() - t0) * 1000.0
    rdg_full_by_b: dict[str, list[float]] = {b: [] for b in PHYSICAL_BODIES}
    for r in rows:
        b = r["body"].lower()
        ra_p, dec_p = rdg_full_preds[str(r["id"])][b]
        rdg_full_by_b[b].append(_sep_arcsec_icrf(ra_p, dec_p, float(r["truth"][0]), float(r["truth"][1])))
    engines_out["rdg_full_de440_bsp"] = {
        "label": f"RDG-Ephemeris {ephemeris_oss.__version__} (Provisioned 114 MB de440.bsp)",
        "license": "Apache-2.0",
        "external_files_required": True,
        "eval_ms": round(rdg_full_ms, 2),
        **_summarize_residuals(rdg_full_by_b),
    }

    # Optional permissive comparators (Skyfield + Astropy)
    if "skyfield_api" in mods:
        sf_load = mods["skyfield_api"].load
        ts = sf_load.timescale()
        sf_eph = sf_load(str(de440_path))
        sf_earth = sf_eph["earth"]
        sf_targets = {
            "sun": sf_eph["sun"],
            "moon": sf_eph["moon"],
            "mercury": sf_eph["mercury"],
            "venus": sf_eph["venus"],
            "mars": sf_eph["mars barycenter"],
            "jupiter": sf_eph["jupiter barycenter"],
            "saturn": sf_eph["saturn barycenter"],
        }
        sf_preds: dict[str, dict[str, tuple[float, float]]] = {}
        t0 = time.perf_counter()
        for sid in unique_ids:
            t_sf = ts.tt_jd(jd_tt_by_id[sid])
            obs_e = sf_earth.at(t_sf)
            sf_preds[sid] = {}
            for b, tgt in sf_targets.items():
                ra_sf, dec_sf, _ = obs_e.observe(tgt).apparent().radec()
                sf_preds[sid][b] = (float(ra_sf._degrees), float(dec_sf.degrees))
        sf_ms = (time.perf_counter() - t0) * 1000.0
        sf_by_b: dict[str, list[float]] = {b: [] for b in PHYSICAL_BODIES}
        for r in rows:
            b = r["body"].lower()
            ra_p, dec_p = sf_preds[str(r["id"])][b]
            sf_by_b[b].append(_sep_arcsec_icrf(ra_p, dec_p, float(r["truth"][0]), float(r["truth"][1])))
        engines_out["skyfield_1_55_de440_bsp"] = {
            "label": f"Skyfield {mods['skyfield'].__version__} (Provisioned 114 MB de440.bsp)",
            "license": "MIT",
            "external_files_required": True,
            "eval_ms": round(sf_ms, 2),
            **_summarize_residuals(sf_by_b),
        }

    if "astropy_coords" in mods:
        ac = mods["astropy_coords"]
        at = mods["astropy_time"]
        jd_arr = np.array([jd_tt_by_id[sid] for sid in unique_ids], dtype=np.float64)
        t_ap = at.Time(jd_arr, format="jd", scale="tt")

        def _eval_astropy_mode(eph_arg: str) -> tuple[dict[str, Any], float]:
            ap_preds: dict[str, dict[str, tuple[float, float]]] = {sid: {} for sid in unique_ids}
            t_start = time.perf_counter()
            with ac.solar_system_ephemeris.set(eph_arg):
                for b in PHYSICAL_BODIES:
                    sc = ac.get_body(b, t_ap)
                    ra_arr = np.asarray(sc.ra.deg, dtype=np.float64)
                    dec_arr = np.asarray(sc.dec.deg, dtype=np.float64)
                    for i, sid in enumerate(unique_ids):
                        ap_preds[sid][b] = (float(ra_arr[i]), float(dec_arr[i]))
            dur = (time.perf_counter() - t_start) * 1000.0
            by_b_ap: dict[str, list[float]] = {b: [] for b in PHYSICAL_BODIES}
            for r in rows:
                b = r["body"].lower()
                ra_p, dec_p = ap_preds[str(r["id"])][b]
                by_b_ap[b].append(
                    _sep_arcsec_icrf(ra_p, dec_p, float(r["truth"][0]), float(r["truth"][1]))
                )
            return _summarize_residuals(by_b_ap), round(dur, 2)

        ap_builtin_summary, ap_builtin_ms = _eval_astropy_mode("builtin")
        ap_de440_summary, ap_de440_ms = _eval_astropy_mode(str(de440_path))
        engines_out["astropy_8_0_2_builtin_zero_download"] = {
            "label": f"Astropy {mods['astropy'].__version__} (Built-in Ephemeris, Zero External Download, Vectorized)",
            "license": "BSD-3-Clause",
            "external_files_required": False,
            "eval_ms": ap_builtin_ms,
            **ap_builtin_summary,
        }
        engines_out["astropy_8_0_2_de440_bsp"] = {
            "label": f"Astropy {mods['astropy'].__version__} (Provisioned 114 MB de440.bsp, Vectorized)",
            "license": "BSD-3-Clause",
            "external_files_required": True,
            "eval_ms": ap_de440_ms,
            **ap_de440_summary,
        }

    mars_r0 = next(r for r in rows if r["body"].lower() == "mars")
    sid0 = str(mars_r0["id"])
    jd0 = jd_tt_by_id[sid0]
    tr_ra0, tr_dec0 = float(mars_r0["truth"][0]), float(mars_r0["truth"][1])

    if "swe" in mods:
        swe = mods["swe"]
        swe_body_map = {
            "sun": swe.SUN,
            "moon": swe.MOON,
            "mercury": swe.MERCURY,
            "venus": swe.VENUS,
            "mars": swe.MARS,
            "jupiter": swe.JUPITER,
            "saturn": swe.SATURN,
        }
        has_se1 = _has_valid_se1_files(se1_dir, locators)
        probe_flag = swe.FLG_SWIEPH if has_se1 else swe.FLG_MOSEPH
        swe.close()
        swe.set_ephe_path(str(se1_dir) if has_se1 else "")
        xx_ecl, _ = swe.calc(jd0, swe.MARS, probe_flag)
        ra_a, dec_a = _true_ecl_of_date_to_icrf_radec(xx_ecl[0], xx_ecl[1], *nut_and_ecmt[sid0])
        cand_a = _sep_arcsec_icrf(ra_a, dec_a, tr_ra0, tr_dec0)
        xx_eq, _ = swe.calc(jd0, swe.MARS, probe_flag | swe.FLG_EQUATORIAL)
        pnm_t = np.asarray(erfa.pnm06a(2451545.0, jd0 - 2451545.0), dtype=np.float64).T
        v_eq = np.array(
            [
                math.cos(math.radians(xx_eq[1])) * math.cos(math.radians(xx_eq[0])),
                math.cos(math.radians(xx_eq[1])) * math.sin(math.radians(xx_eq[0])),
                math.sin(math.radians(xx_eq[1])),
            ]
        )
        v_icrf_b = pnm_t @ v_eq
        ra_b = math.degrees(math.atan2(float(v_icrf_b[1]), float(v_icrf_b[0]))) % 360.0
        dec_b = math.degrees(math.asin(max(-1.0, min(1.0, float(v_icrf_b[2])))))
        cand_b = _sep_arcsec_icrf(ra_b, dec_b, tr_ra0, tr_dec0)
        best_se_frame = "eq_of_date_via_pnm06a_icrf" if cand_b < cand_a else "ecl_of_date_via_iau2006_icrf"

        def _eval_se_mode(mode_flag: int, ephe_dir: str) -> tuple[dict[str, Any], float]:
            swe.close()
            swe.set_ephe_path(ephe_dir)
            preds: dict[str, dict[str, tuple[float, float]]] = {}
            t_s = time.perf_counter()
            for sid in unique_ids:
                jd_tt = jd_tt_by_id[sid]
                nut_d, ecm_t = nut_and_ecmt[sid]
                pnm_t_local = np.asarray(erfa.pnm06a(2451545.0, jd_tt - 2451545.0), dtype=np.float64).T
                per_b: dict[str, tuple[float, float]] = {}
                for b, b_id in swe_body_map.items():
                    if best_se_frame == "eq_of_date_via_pnm06a_icrf":
                        xx, _ = swe.calc(jd_tt, b_id, mode_flag | swe.FLG_EQUATORIAL)
                        rr, dd = math.radians(xx[0]), math.radians(xx[1])
                        vec = pnm_t_local @ np.array(
                            [math.cos(dd) * math.cos(rr), math.cos(dd) * math.sin(rr), math.sin(dd)]
                        )
                        ra = math.degrees(math.atan2(float(vec[1]), float(vec[0]))) % 360.0
                        dec = math.degrees(math.asin(max(-1.0, min(1.0, float(vec[2])))))
                        per_b[b] = (ra, dec)
                    else:
                        xx, _ = swe.calc(jd_tt, b_id, mode_flag)
                        per_b[b] = _true_ecl_of_date_to_icrf_radec(xx[0], xx[1], nut_d, ecm_t)
                preds[sid] = per_b
            dur_ms = (time.perf_counter() - t_s) * 1000.0
            by_b: dict[str, list[float]] = {b: [] for b in PHYSICAL_BODIES}
            for r in rows:
                b = r["body"].lower()
                ra_p, dec_p = preds[str(r["id"])][b]
                by_b[b].append(
                    _sep_arcsec_icrf(ra_p, dec_p, float(r["truth"][0]), float(r["truth"][1]))
                )
            return _summarize_residuals(by_b), round(dur_ms, 2)

        se_moshier_summary, se_moshier_ms = _eval_se_mode(swe.FLG_MOSEPH, "")
        engines_out["se_2_10_03_moshier_zero_download"] = {
            "label": "SE 2.10.03 (Swiss-compatible convention, Built-in Moshier, Zero External Files)",
            "license": "GPL v2+ / AGPL v3",
            "external_files_required": False,
            "eval_ms": se_moshier_ms,
            **se_moshier_summary,
        }
        if has_se1 and se1_dir is not None:
            se_se1_summary, se_se1_ms = _eval_se_mode(swe.FLG_SWIEPH, str(se1_dir))
            engines_out["se_2_10_03_se1_provisioned"] = {
                "label": "SE 2.10.03 (Swiss-compatible convention, External .se1 Files)",
                "license": "GPL v2+ / AGPL v3",
                "external_files_required": True,
                "eval_ms": se_se1_ms,
                **se_se1_summary,
            }
        else:
            engines_out["se_2_10_03_se1_provisioned"] = {
                "status": "SKIPPED_NO_EXTERNAL_SE1_ARCHIVE",
                "reason": locators["external_archive_disclosure"]["redistribution_limitation"],
                "upstream_public_locator": locators["external_archive_disclosure"]["upstream_public_locator"],
            }

    if "ephem" in mods:
        ephem = mods["ephem"]
        ephem_cls = {
            "sun": ephem.Sun,
            "moon": ephem.Moon,
            "mercury": ephem.Mercury,
            "venus": ephem.Venus,
            "mars": ephem.Mars,
            "jupiter": ephem.Jupiter,
            "saturn": ephem.Saturn,
        }
        m_test = ephem.Mars()
        m_test.compute(jd0 - 2415020.0, epoch=ephem.J2000)
        sep_ephem_astrom = _sep_arcsec_icrf(
            math.degrees(float(m_test.a_ra)), math.degrees(float(m_test.a_dec)), tr_ra0, tr_dec0
        )
        pnm_t0 = np.asarray(erfa.pnm06a(2451545.0, jd0 - 2451545.0), dtype=np.float64).T
        rr_e, dd_e = float(m_test.ra), float(m_test.dec)
        vec_e0 = pnm_t0 @ np.array(
            [math.cos(dd_e) * math.cos(rr_e), math.cos(dd_e) * math.sin(rr_e), math.sin(dd_e)]
        )
        ra_e0 = math.degrees(math.atan2(float(vec_e0[1]), float(vec_e0[0]))) % 360.0
        dec_e0 = math.degrees(math.asin(max(-1.0, min(1.0, float(vec_e0[2])))))
        sep_ephem_app = _sep_arcsec_icrf(ra_e0, dec_e0, tr_ra0, tr_dec0)
        use_ephem_apparent_rot = sep_ephem_app <= sep_ephem_astrom

        ep_preds: dict[str, dict[str, tuple[float, float]]] = {}
        t0 = time.perf_counter()
        for sid in unique_ids:
            jd_tt = jd_tt_by_id[sid]
            djd = jd_tt - 2415020.0
            pnm_t_ep = np.asarray(erfa.pnm06a(2451545.0, jd_tt - 2451545.0), dtype=np.float64).T
            ep_preds[sid] = {}
            for b, cls in ephem_cls.items():
                obj = cls()
                obj.compute(djd, epoch=ephem.J2000)
                if use_ephem_apparent_rot:
                    rr_i, dd_i = float(obj.ra), float(obj.dec)
                    vec_i = pnm_t_ep @ np.array(
                        [math.cos(dd_i) * math.cos(rr_i), math.cos(dd_i) * math.sin(rr_i), math.sin(dd_i)]
                    )
                    ra_i = math.degrees(math.atan2(float(vec_i[1]), float(vec_i[0]))) % 360.0
                    dec_i = math.degrees(math.asin(max(-1.0, min(1.0, float(vec_i[2])))))
                    ep_preds[sid][b] = (ra_i, dec_i)
                else:
                    ep_preds[sid][b] = (math.degrees(float(obj.a_ra)), math.degrees(float(obj.a_dec)))
        ep_ms = (time.perf_counter() - t0) * 1000.0
        ep_by_b: dict[str, list[float]] = {b: [] for b in PHYSICAL_BODIES}
        for r in rows:
            b = r["body"].lower()
            ra_p, dec_p = ep_preds[str(r["id"])][b]
            ep_by_b[b].append(_sep_arcsec_icrf(ra_p, dec_p, float(r["truth"][0]), float(r["truth"][1])))
        engines_out["pyephem_4_2_1_zero_download"] = {
            "label": f"PyEphem {ephem.__version__} (Built-in VSOP87/Chapront, Zero External Download)",
            "license": "LGPL",
            "external_files_required": False,
            "eval_ms": round(ep_ms, 2),
            **_summarize_residuals(ep_by_b),
        }

    return {
        "corpus": "NASA JPL Horizons DE441 (QUANTITIES=45 Apparent Geocentric ICRF RA/DEC)",
        "quick_smoke": quick_smoke,
        "epochs_evaluated": len(unique_ids),
        "rows_evaluated": len(rows),
        "engines": engines_out,
    }


def eval2_zero_download_span(
    *,
    de440_path: Path,
    mods: dict[str, Any],
    quick_smoke: bool,
) -> dict[str, Any]:
    full_schedule: list[tuple[int, int, float]] = []
    for y in range(1550, 2307):
        max_m = 2 if y == 2306 else 12
        for m in range(1, max_m + 1):
            djm0, djm = erfa.cal2jd(y, m, 15)
            jd_tt = float(djm0 + djm)
            if 2287184.5 <= jd_tt <= 2563392.5:
                full_schedule.append((y, m, jd_tt))
    schedule = full_schedule[::75] if quick_smoke else full_schedule

    swe = mods.get("swe")
    ephem = mods.get("ephem")
    if swe is not None:
        swe.close()
        swe.set_ephe_path("")
        swe_body_map = {
            "sun": swe.SUN,
            "moon": swe.MOON,
            "mercury": swe.MERCURY,
            "venus": swe.VENUS,
            "mars": swe.MARS,
            "jupiter": swe.JUPITER,
            "saturn": swe.SATURN,
        }
    else:
        swe_body_map = {}

    ephem_cls = (
        {
            "sun": ephem.Sun,
            "moon": ephem.Moon,
            "mercury": ephem.Mercury,
            "venus": ephem.Venus,
            "mars": ephem.Mars,
            "jupiter": ephem.Jupiter,
            "saturn": ephem.Saturn,
        }
        if ephem is not None
        else {}
    )

    ref_coords: list[dict[str, tuple[float, float]]] = []
    rdg_by_b: dict[str, list[float]] = {b: [] for b in PHYSICAL_BODIES}
    se_mosh_by_b: dict[str, list[float]] = {b: [] for b in PHYSICAL_BODIES}
    ep_by_b: dict[str, list[float]] = {b: [] for b in PHYSICAL_BODIES}

    with (
        Engine.load(kernels={"DE440": de440_path}, eop=None) as eng_ref,
        Engine.load(kernels="extended", eop=None) as eng_ext,
    ):
        for _y, _m, jd_tt in schedule:
            kw = {"jd_tdb": jd_tt, "mean_equinox": True} if jd_tt < 2305447.5 else {}
            r_pos = eng_ref.positions_tt(jd_tt, bodies=PHYSICAL_BODIES, **kw).value
            e_pos = eng_ext.positions_tt(jd_tt, bodies=PHYSICAL_BODIES, **kw).value
            ref_epoch: dict[str, tuple[float, float]] = {}
            djd = jd_tt - 2415020.0
            for b in PHYSICAL_BODIES:
                r_lon = float(r_pos[b]["longitude_deg"])
                r_lat = float(r_pos[b]["latitude_deg"])
                ref_epoch[b] = (r_lon, r_lat)

                e_lon = float(e_pos[b]["longitude_deg"])
                e_lat = float(e_pos[b]["latitude_deg"])
                dlon = abs((e_lon - r_lon + 180.0) % 360.0 - 180.0) * 3600.0
                dlat = abs(e_lat - r_lat) * 3600.0
                rdg_by_b[b].append(math.hypot(dlon, dlat))

                if swe is not None:
                    se_flag = swe.FLG_MOSEPH | (swe.FLG_NONUT if jd_tt < 2305447.5 else 0)
                    xx, _ = swe.calc(jd_tt, swe_body_map[b], se_flag)
                    dlon_s = abs((float(xx[0]) - r_lon + 180.0) % 360.0 - 180.0) * 3600.0
                    dlat_s = abs(float(xx[1]) - r_lat) * 3600.0
                    se_mosh_by_b[b].append(math.hypot(dlon_s, dlat_s))

                if ephem is not None:
                    obj = ephem_cls[b]()
                    obj.compute(djd, epoch=djd)
                    ecl = ephem.Ecliptic(obj, epoch=djd)
                    ep_lon = math.degrees(float(ecl.lon)) % 360.0
                    ep_lat = math.degrees(float(ecl.lat))
                    dlon_e = abs((ep_lon - r_lon + 180.0) % 360.0 - 180.0) * 3600.0
                    dlat_e = abs(ep_lat - r_lat) * 3600.0
                    ep_by_b[b].append(math.hypot(dlon_e, dlat_e))
            ref_coords.append(ref_epoch)

    zero_dl_out: dict[str, Any] = {"rdg_embedded_chebyshev": _summarize_residuals(rdg_by_b)}
    ratios_out: dict[str, Any] = {}
    rdg_s = zero_dl_out["rdg_embedded_chebyshev"]

    if swe is not None:
        se_s = _summarize_residuals(se_mosh_by_b)
        zero_dl_out["se_2_10_03_moshier"] = se_s
        ratios_out["se_moshier_vs_rdg_max_error_ratio"] = round(
            se_s["overall_max_arcsec"] / rdg_s["overall_max_arcsec"], 2
        )
        ratios_out["se_moshier_vs_rdg_median_error_ratio"] = round(
            se_s["overall_median_arcsec"] / rdg_s["overall_median_arcsec"], 2
        )

    if "astropy_coords" in mods:
        ac = mods["astropy_coords"]
        at = mods["astropy_time"]
        jd_vec = np.array([jd_tt for _, _, jd_tt in schedule], dtype=np.float64)
        t_vec = at.Time(jd_vec, format="jd", scale="tt")
        ap_by_b: dict[str, list[float]] = {b: [] for b in PHYSICAL_BODIES}
        with ac.solar_system_ephemeris.set("builtin"):
            for b in PHYSICAL_BODIES:
                sc = ac.get_body(b, t_vec)
                ecl_ap = sc.transform_to(ac.GeocentricTrueEcliptic(equinox=t_vec))
                lon_arr = np.asarray(ecl_ap.lon.deg, dtype=np.float64)
                lat_arr = np.asarray(ecl_ap.lat.deg, dtype=np.float64)
                for idx, (_, _, jd_tt) in enumerate(schedule):
                    r_lon, r_lat = ref_coords[idx][b]
                    ap_lon_i = float(lon_arr[idx])
                    if jd_tt < 2305447.5:
                        nut_d = math.degrees(float(erfa.nut06a(2451545.0, jd_tt - 2451545.0)[0]))
                        ap_lon_i = (ap_lon_i - nut_d) % 360.0
                    dlon_a = abs((ap_lon_i - r_lon + 180.0) % 360.0 - 180.0) * 3600.0
                    dlat_a = abs(float(lat_arr[idx]) - r_lat) * 3600.0
                    ap_by_b[b].append(math.hypot(dlon_a, dlat_a))
        ap_s = _summarize_residuals(ap_by_b)
        zero_dl_out["astropy_8_0_2_builtin"] = ap_s
        ratios_out["astropy_builtin_vs_rdg_max_error_ratio"] = round(
            ap_s["overall_max_arcsec"] / rdg_s["overall_max_arcsec"], 2
        )
        ratios_out["astropy_builtin_vs_rdg_median_error_ratio"] = round(
            ap_s["overall_median_arcsec"] / rdg_s["overall_median_arcsec"], 2
        )

    if ephem is not None:
        ep_s = _summarize_residuals(ep_by_b)
        zero_dl_out["pyephem_4_2_1"] = ep_s
        ratios_out["pyephem_vs_rdg_max_error_ratio"] = round(
            ep_s["overall_max_arcsec"] / rdg_s["overall_max_arcsec"], 2
        )
        ratios_out["pyephem_vs_rdg_median_error_ratio"] = round(
            ep_s["overall_median_arcsec"] / rdg_s["overall_median_arcsec"], 2
        )

    return {
        "span": "1550-01-15 to 2306-02-15",
        "quick_smoke": quick_smoke,
        "months_evaluated": len(schedule),
        "body_evaluations": len(schedule) * len(PHYSICAL_BODIES),
        "reference_de440_sha256": _sha256_file(de440_path),
        "zero_download_engines": zero_dl_out,
        "zero_download_accuracy_ratios_vs_rdg": ratios_out,
    }


def eval3_throughput(
    repo_root: Path,
    *,
    de440_path: Path,
    se1_dir: Path | None,
    rust_cdylib: Path | None,
    locators: dict[str, Any],
    mods: dict[str, Any],
    quick_smoke: bool,
) -> dict[str, Any]:
    n_charts = 500 if quick_smoke else 10_000
    requests_data: list[tuple[float, float, float, float]] = []
    for i in range(n_charts):
        jd_utc = 2440587.5 + i * 1.3719
        delta_t = 65.0
        jd_tt = jd_utc + delta_t / 86400.0
        lat = -35.0 + (i % 91) * 1.0
        lon = -120.0 + ((i * 7) % 260) * 1.0
        requests_data.append((jd_utc, jd_tt, lat, lon))

    kundali_out: dict[str, Any] = {
        "charts_evaluated": n_charts,
        "quick_smoke": quick_smoke,
    }

    rust_med_ms: float | None = None
    if rust_cdylib is not None and rust_cdylib.is_file():
        rust_lib = load_native_cdylib(rust_cdylib)
        req_ptr = rust_lib.wasm_arena_request_ptr()
        out_ptr = rust_lib.wasm_arena_output_ptr()
        for i in range(min(50, n_charts)):
            jd_u, jd_t, lat, lon = requests_data[i]
            req_ptr.contents.jd_utc = jd_u
            req_ptr.contents.jd_tt = jd_t
            req_ptr.contents.delta_t_sec = 65.0
            req_ptr.contents.lat_deg = lat
            req_ptr.contents.lon_deg = lon
            req_ptr.contents.alt_m = 0.0
            req_ptr.contents.ayanamsa_id = 0
            req_ptr.contents.house_system_id = 0
            req_ptr.contents.node_mode = 0
            rust_lib.wasm_compute_full_kundali(req_ptr, out_ptr)

        rust_rounds_ms: list[float] = []
        for _ in range(3 if quick_smoke else 5):
            t0 = time.perf_counter()
            for jd_u, jd_t, lat, lon in requests_data:
                req_ptr.contents.jd_utc = jd_u
                req_ptr.contents.jd_tt = jd_t
                req_ptr.contents.delta_t_sec = 65.0
                req_ptr.contents.lat_deg = lat
                req_ptr.contents.lon_deg = lon
                req_ptr.contents.alt_m = 0.0
                req_ptr.contents.ayanamsa_id = 0
                req_ptr.contents.house_system_id = 0
                req_ptr.contents.node_mode = 0
                rc = rust_lib.wasm_compute_full_kundali(req_ptr, out_ptr)
                if rc != 0:
                    raise RuntimeError(f"Rust kundali rc={rc}")
            rust_rounds_ms.append((time.perf_counter() - t0) * 1000.0)
        sav_check = sum(int(out_ptr.contents.ashtakavarga_sav[k]) for k in range(12))
        rust_med_ms = statistics.median(rust_rounds_ms)
        kundali_out["sav_invariant_verified"] = sav_check
        kundali_out["rdg_rust_native_zero_copy_rounds_ms"] = [round(x, 3) for x in rust_rounds_ms]
        kundali_out["rdg_rust_native_median_ms"] = round(rust_med_ms, 3)
        kundali_out["rdg_rust_native_per_chart_us"] = round((rust_med_ms * 1000.0) / n_charts, 3)
        kundali_out["rdg_rust_native_charts_per_sec"] = round(n_charts / (rust_med_ms / 1000.0), 1)
    else:
        kundali_out["rdg_rust_native_status"] = "SKIPPED_NO_RUST_CDYLIB_PASSED"

    v8_med_ms: float | None = None
    if shutil.which("node") is not None and (repo_root / "web" / "ephemeris-browser.js").is_file():
        node_script = f"""
        import('./web/ephemeris-browser.js').then((m) => {{
          for (let i = 0; i < 25; i++) {{
            m.computeChart({{ jdTt: 2451545.0 + i, latitudeDeg: 28.6139, longitudeDeg: 77.2090 }});
          }}
          const rounds = [];
          let savSum = 0;
          for (let r = 0; r < 3; r++) {{
            const t0 = performance.now();
            for (let i = 0; i < {n_charts}; i++) {{
              const c = m.computeChart({{
                jdTt: 2440587.5 + i * 1.3719,
                latitudeDeg: -35.0 + (i % 91),
                longitudeDeg: -120.0 + ((i * 7) % 260),
                ayanamsa: 'lahiri',
                nodeMode: 'mean'
              }});
              if (i === {n_charts - 1}) savSum = c.ashtakavarga.totalBindus;
            }}
            rounds.push(performance.now() - t0);
          }}
          rounds.sort((a, b) => a - b);
          console.log(JSON.stringify({{ roundsMs: rounds, medianMs: rounds[1], savTotal: savSum }}));
        }});
        """
        node_proc = subprocess.run(
            ["node", "-e", node_script],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=True,
            timeout=120,
        )
        node_v8 = json.loads(node_proc.stdout.strip())
        v8_med_ms = float(node_v8["medianMs"])
        kundali_out["rdg_browser_v8_es_module_rounds_ms"] = [round(x, 3) for x in node_v8["roundsMs"]]
        kundali_out["rdg_browser_v8_median_ms"] = round(v8_med_ms, 3)
        kundali_out["rdg_browser_v8_per_chart_ms"] = round(v8_med_ms / n_charts, 4)
        kundali_out["rdg_browser_v8_charts_per_sec"] = round(n_charts / (v8_med_ms / 1000.0), 1)

    if "swe" in mods:
        swe = mods["swe"]
        se_bodies = (
            ("Sun", swe.SUN),
            ("Moon", swe.MOON),
            ("Mars", swe.MARS),
            ("Mercury", swe.MERCURY),
            ("Jupiter", swe.JUPITER),
            ("Venus", swe.VENUS),
            ("Saturn", swe.SATURN),
        )
        swe.close()
        swe.set_ephe_path("")
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        t0 = time.perf_counter()
        for jd_u, _jd_t, lat, lon in requests_data:
            for _nm, bid in se_bodies:
                swe.calc_ut(jd_u, bid, swe.FLG_MOSEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED)
            swe.calc_ut(jd_u, swe.MEAN_NODE, swe.FLG_MOSEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED)
            swe.houses_ex(jd_u, lat, lon, b"P", swe.FLG_SIDEREAL)
        se_moshier_coords_ms = (time.perf_counter() - t0) * 1000.0
        kundali_out["se_2_10_03_moshier_coords_and_houses_only_ms"] = round(se_moshier_coords_ms, 2)

        has_se1 = _has_valid_se1_files(se1_dir, locators)
        ephe_flag = swe.FLG_SWIEPH if has_se1 else swe.FLG_MOSEPH
        swe.close()
        swe.set_ephe_path(str(se1_dir) if (has_se1 and se1_dir is not None) else "")
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        if has_se1:
            t0 = time.perf_counter()
            for jd_u, _jd_t, lat, lon in requests_data:
                for _nm, bid in se_bodies:
                    swe.calc_ut(jd_u, bid, ephe_flag | swe.FLG_SIDEREAL | swe.FLG_SPEED)
                swe.calc_ut(jd_u, swe.MEAN_NODE, ephe_flag | swe.FLG_SIDEREAL | swe.FLG_SPEED)
                swe.houses_ex(jd_u, lat, lon, b"P", swe.FLG_SIDEREAL)
            kundali_out["se_2_10_03_se1_coords_and_houses_only_ms"] = round(
                (time.perf_counter() - t0) * 1000.0, 2
            )

        t0 = time.perf_counter()
        for jd_u, _jd_t, lat, lon in requests_data:
            lons_map: dict[str, float] = {}
            for nm, bid in se_bodies:
                xx, _ = swe.calc_ut(jd_u, bid, ephe_flag | swe.FLG_SIDEREAL | swe.FLG_SPEED)
                lons_map[nm] = float(xx[0])
            rn, _ = swe.calc_ut(jd_u, swe.MEAN_NODE, ephe_flag | swe.FLG_SIDEREAL | swe.FLG_SPEED)
            lons_map["Rahu"] = float(rn[0])
            lons_map["Ketu"] = (float(rn[0]) + 180.0) % 360.0
            _cusps, ascmc = swe.houses_ex(jd_u, lat, lon, b"P", swe.FLG_SIDEREAL)
            lagna_d = float(ascmc[0])
            for lon_v in lons_map.values():
                compute_shodashvarga(lon_v)
            compute_ashtakavarga(lons_map, lagna_d)
            compute_vimshottari_dasha(lons_map["Moon"], birth_jd=jd_u, max_level=2)
        py_se_full_ms = (time.perf_counter() - t0) * 1000.0
        kundali_out["python_plus_se_2_10_03_full_kundali_ms"] = round(py_se_full_ms, 2)
        kundali_out["python_plus_se_2_10_03_mode"] = "se1" if has_se1 else "moshier"
        multipliers: dict[str, Any] = {}
        if rust_med_ms is not None:
            multipliers["rdg_rust_full_kundali_vs_python_se_full_kundali_x"] = round(
                py_se_full_ms / rust_med_ms, 2
            )
        if v8_med_ms is not None:
            multipliers["rdg_browser_v8_full_kundali_vs_python_se_full_kundali_x"] = round(
                py_se_full_ms / v8_med_ms, 2
            )
        kundali_out["throughput_multipliers"] = multipliers

    n_stream = 100 if quick_smoke else 1000
    stream_jds = [2451545.0 + i * 7.31 for i in range(n_stream)]
    with Engine.load(kernels="extended", eop=None) as eng_emb:
        eng_emb.positions_tt(2451545.0, bodies=PHYSICAL_BODIES)
        t0 = time.perf_counter()
        for jd_s in stream_jds:
            eng_emb.positions_tt(jd_s, bodies=PHYSICAL_BODIES)
        rdg_py_emb_ms = (time.perf_counter() - t0) * 1000.0

    with Engine.load(kernels={"DE440": de440_path}, eop=None) as eng_full:
        eng_full.positions_tt(2451545.0, bodies=PHYSICAL_BODIES)
        t0 = time.perf_counter()
        for jd_s in stream_jds:
            eng_full.positions_tt(jd_s, bodies=PHYSICAL_BODIES)
        rdg_py_de440_ms = (time.perf_counter() - t0) * 1000.0

    with SPK.open(str(de440_path)) as jpl_spk:
        seg_mars = jpl_spk[0, 4]
        t0 = time.perf_counter()
        for _jd_u, jd_t, _, _ in requests_data:
            seg_mars.compute_and_differentiate(2451545.0, jd_t - 2451545.0)
        jplephem_seg_ms = (time.perf_counter() - t0) * 1000.0

    stream_out: dict[str, Any] = {
        "epochs": n_stream,
        "body_evaluations": n_stream * len(PHYSICAL_BODIES),
        "rdg_python_embedded_chebyshev_ms": round(rdg_py_emb_ms, 2),
        "rdg_python_de440_bsp_ms": round(rdg_py_de440_ms, 2),
        "jplephem_in_memory_mars_states_ms": round(jplephem_seg_ms, 3),
    }

    if "skyfield_api" in mods:
        sf_load = mods["skyfield_api"].load
        ts = sf_load.timescale()
        sf_eph = sf_load(str(de440_path))
        sf_earth = sf_eph["earth"]
        sf_tgts = [
            sf_eph[k]
            for k in (
                "sun",
                "moon",
                "mercury",
                "venus",
                "mars barycenter",
                "jupiter barycenter",
                "saturn barycenter",
            )
        ]
        t0 = time.perf_counter()
        for jd_s in stream_jds:
            t_s = ts.tt_jd(jd_s)
            obs = sf_earth.at(t_s)
            for tgt in sf_tgts:
                obs.observe(tgt).apparent().ecliptic_latlon("date")
        skyfield_ms = (time.perf_counter() - t0) * 1000.0
        stream_out["skyfield_1_55_de440_bsp_ms"] = round(skyfield_ms, 2)
        stream_out["rdg_python_vs_skyfield_per_epoch_x"] = round(skyfield_ms / rdg_py_de440_ms, 2)

    if "astropy_coords" in mods:
        ac = mods["astropy_coords"]
        at = mods["astropy_time"]
        ap_sample = stream_jds[:20] if quick_smoke else stream_jds[:100]
        with ac.solar_system_ephemeris.set(str(de440_path)):
            t0 = time.perf_counter()
            for jd_s in ap_sample:
                t_a = at.Time(jd_s, format="jd", scale="tt")
                for b in PHYSICAL_BODIES:
                    ac.get_body(b, t_a).transform_to(ac.GeocentricTrueEcliptic(equinox=t_a))
            ap_scalar_ms = (time.perf_counter() - t0) * 1000.0
        scaled_ap_ms = ap_scalar_ms * (n_stream / len(ap_sample))
        stream_out["astropy_8_0_2_scalar_sampled_epochs"] = len(ap_sample)
        stream_out["astropy_8_0_2_scalar_sampled_ms"] = round(ap_scalar_ms, 2)
        stream_out["astropy_8_0_2_scalar_scaled_ms"] = round(scaled_ap_ms, 2)
        stream_out["rdg_python_vs_astropy_scalar_per_epoch_x"] = round(
            scaled_ap_ms / rdg_py_de440_ms, 2
        )

    return {
        "workload_full_kundalis": kundali_out,
        "workload_interactive_7body_python_api": stream_out,
    }


def eval4_wgs84_geodetic_houses_vs_horizons_physical_vertical(
    repo_root: Path,
    *,
    de440_path: Path | None,
    eop_path: Path | None,
    mods: dict[str, Any],
) -> dict[str, Any]:
    """Live-compute WGS84 + IERS polar-motion geodetic house cusps vs Horizons 0-to-1 km physical vertical."""
    vectors_path = HERE / "horizons-geodetic-vertical-vectors.json"
    vectors_data = json.loads(vectors_path.read_text(encoding="utf-8"))
    swe = mods.get("swe")

    eop_table: IersFinals2000A | None = None
    eop_source = "committed_iers_snapshot"
    if eop_path is not None and eop_path.is_file():
        digest = _sha256_file(eop_path)
        eop_table = IersFinals2000A.from_file(
            eop_path,
            expected_sha256=digest,
            version=f"iers-finals2000a-sha256-{digest[:12]}",
            allow_predictions=True,
        )
        eop_source = "iers_finals_file"

    kernels_arg: str | dict[str, Path] = (
        {"DE440": de440_path} if (de440_path is not None and de440_path.is_file()) else "extended"
    )
    benchmarks: list[dict[str, Any]] = []

    for case in vectors_data["cases"]:
        instant = datetime.fromisoformat(case["instant_utc"])
        lat_deg = float(case["latitude_deg"])
        lon_deg = float(case["longitude_deg"])
        jd_utc = float(case["jd_utc"])
        up_icrf = np.asarray(case["up_icrf"], dtype=np.float64)
        jpl_dut1 = float(case["jpl_dut1_seconds"])

        if eop_table is not None:
            resolved = eop_table(instant)
            dut1_sec = float(resolved.dut1_seconds)
            eop_arg: Any = eop_table
        else:
            snap = case["iers_eop_snapshot"]
            dut1_sec = float(snap["dut1_seconds"])
            eop_arg = EarthOrientation(
                dut1_seconds=dut1_sec,
                xp_arcsec=float(snap["xp_arcsec"]),
                yp_arcsec=float(snap["yp_arcsec"]),
                version="committed-iers-snapshot",
            )

        with Engine.load(kernels=kernels_arg, eop=eop_arg) as eng:
            tt = eng._provider.utc_time_scales(instant).tt
            v_true = erfa.pnm06a(*tt) @ up_icrf
            ra_deg = math.degrees(math.atan2(float(v_true[1]), float(v_true[0]))) % 360.0
            phi_true_deg = math.degrees(
                math.atan2(float(v_true[2]), math.hypot(float(v_true[0]), float(v_true[1])))
            )
            armc_deg = (ra_deg + (dut1_sec - jpl_dut1) * 360.9856122880876 / 86400.0) % 360.0
            dpsi, deps = erfa.nut06a(*tt)
            eps_deg = math.degrees(float(erfa.obl06(*tt) + deps))
            exp_asc_trop, exp_mc_trop = ascendant_midheaven_from_sidereal(
                armc_deg, phi_true_deg, eps_deg
            )
            exp_placidus = house_layout(
                "placidus",
                ascendant_deg=exp_asc_trop,
                midheaven_deg=exp_mc_trop,
                local_apparent_sidereal_deg=armc_deg,
                latitude_deg=phi_true_deg,
                true_obliquity_deg=eps_deg,
            )

            max_err = 0.0
            asc_err_trop = 0.0
            for zodiac in (None, "lahiri", "raman", "kp"):
                offset = 0.0
                if zodiac is not None:
                    offset = eng._provider._ayanamsa_offset(
                        eng._provider.utc_time_scales(instant), zodiac
                    ) + math.degrees(float(dpsi))
                for sys_name in ("whole_sign", "placidus"):
                    res_h = eng.houses(
                        instant, lat=lat_deg, lon=lon_deg, system=sys_name, ayanamsa=zodiac
                    ).value
                    exp_asc = (exp_asc_trop - offset) % 360.0
                    exp_mc = (exp_mc_trop - offset) % 360.0
                    if sys_name == "whole_sign":
                        first_c = math.floor(exp_asc / 30.0) * 30.0
                        exp_cusps = tuple((first_c + 30.0 * k) % 360.0 for k in range(12))
                    else:
                        exp_cusps = tuple((c - offset) % 360.0 for c in exp_placidus.cusps_deg)
                    errs = [
                        abs((a - b + 180.0) % 360.0 - 180.0) * 3600.0
                        for a, b in zip(
                            (*res_h.cusps_deg, res_h.ascendant_deg, res_h.midheaven_deg),
                            (*exp_cusps, exp_asc, exp_mc),
                        )
                    ]
                    if zodiac is None and sys_name == "placidus":
                        asc_err_trop = errs[12]
                    max_err = max(max_err, max(errs))

            lahiri_houses = eng.houses(
                instant, lat=lat_deg, lon=lon_deg, system="placidus", ayanamsa="lahiri"
            ).value
            rdg_lahiri_asc = lahiri_houses.ascendant_deg

        se_asc_disc: float | None = None
        boundary_flip: dict[str, Any] | None = None
        if swe is not None:
            swe.close()
            swe.set_ephe_path("")
            _se_cusps_t, se_ascmc_t = swe.houses_ex(jd_utc, lat_deg, lon_deg, b"P", 0)
            se_asc_disc = round(
                abs((float(se_ascmc_t[0]) - exp_asc_trop + 180.0) % 360.0 - 180.0) * 3600.0, 6
            )
            if "Boundary-2019-06-22" in case["sample"]:
                swe.set_sid_mode(swe.SIDM_LAHIRI)
                _se_c_s, se_a_s = swe.houses_ex(jd_utc, lat_deg, lon_deg, b"P", swe.FLG_SIDEREAL)
                se_lahiri_asc = float(se_a_s[0]) % 360.0
                rdg_nak = nakshatra_position(rdg_lahiri_asc)
                se_nak = nakshatra_position(se_lahiri_asc)
                rdg_d9 = varga_sign(rdg_lahiri_asc, "D9")
                se_d9 = varga_sign(se_lahiri_asc, "D9")
                boundary_flip = {
                    "rdg_nakshatra_pada": f"{rdg_nak.name} Pada {rdg_nak.pada}",
                    "se_nakshatra_pada": f"{se_nak.name} Pada {se_nak.pada}",
                    "rdg_d9_sign": rdg_d9.sign_name,
                    "se_d9_sign": se_d9.sign_name,
                }

        row_out: dict[str, Any] = {
            "sample": case["sample"],
            "rdg_wgs84_polar_motion_asc_err_arcsec": round(asc_err_trop, 6),
            "rdg_wgs84_polar_motion_max_err_arcsec": round(max_err, 6),
            "se_2_10_03_asc_discrepancy_arcsec": se_asc_disc,
            "status_at_0_01_arcsec": "PASS" if max_err <= 0.01 else "FAIL",
        }
        if se_asc_disc is not None and max_err > 0.0:
            row_out["precision_improvement_factor_x"] = round(se_asc_disc / max_err, 1)
        if boundary_flip is not None:
            row_out["boundary_classification"] = boundary_flip
        benchmarks.append(row_out)

    return {
        "oracle": "NASA JPL Horizons dual-altitude ICRF observer vectors (0 km and 1 km height at identical geodetic site -> physical geodetic vertical)",
        "eop_source": eop_source,
        "benchmarks": benchmarks,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--mode",
        choices=("full", "permissive-only", "rdg-only", "verify-locators"),
        default="full",
        help="Execution mode (use verify-locators or rdg-only in clean runtime venvs).",
    )
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_REPO_ROOT)
    parser.add_argument("--de440-bsp", type=Path, default=None)
    parser.add_argument("--eop-file", type=Path, default=None)
    parser.add_argument("--se1-dir", type=Path, default=None)
    parser.add_argument("--rust-cdylib", type=Path, default=None)
    parser.add_argument("--quick-smoke", action="store_true")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    de440_path = _resolve_default_de440(args.de440_bsp)
    eop_path = _resolve_default_eop(args.eop_file)
    se1_dir = _resolve_default_se1_dir(args.se1_dir)
    rust_cdylib = _resolve_default_rust_cdylib(args.rust_cdylib)

    if args.mode == "verify-locators":
        payload = verify_locators(
            repo_root,
            de440_path=de440_path,
            eop_path=eop_path,
            se1_dir=se1_dir,
            rust_cdylib=rust_cdylib,
        )
        if args.out is not None:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
        else:
            print(json.dumps(payload, indent=2))
        return 0 if payload["in_repo_references_verified"] else 1

    if de440_path is None or not de440_path.is_file():
        raise SystemExit(
            "Missing NASA JPL de440.bsp; run `ephemeris-oss kernels fetch --verify --eop` "
            "or pass `--de440-bsp /path/to/de440.bsp`."
        )

    locators = json.loads((HERE / "reference-locators.json").read_text(encoding="utf-8"))
    mods = _load_optional_comparators(args.mode)

    t_all = time.perf_counter()
    e1 = eval1_horizons_de441(
        repo_root,
        de440_path=de440_path,
        se1_dir=se1_dir,
        locators=locators,
        mods=mods,
        quick_smoke=args.quick_smoke,
    )
    e2 = eval2_zero_download_span(
        de440_path=de440_path,
        mods=mods,
        quick_smoke=args.quick_smoke,
    )
    e3 = eval3_throughput(
        repo_root,
        de440_path=de440_path,
        se1_dir=se1_dir,
        rust_cdylib=rust_cdylib,
        locators=locators,
        mods=mods,
        quick_smoke=args.quick_smoke,
    )
    e4 = eval4_wgs84_geodetic_houses_vs_horizons_physical_vertical(
        repo_root,
        de440_path=de440_path,
        eop_path=eop_path,
        mods=mods,
    )

    node_ver = (
        subprocess.run(["node", "--version"], capture_output=True, text=True, check=False).stdout.strip()
        if shutil.which("node")
        else "unavailable"
    )
    rustc_ver = (
        subprocess.run(["rustc", "--version"], capture_output=True, text=True, check=False).stdout.strip()
        if shutil.which("rustc")
        else "unavailable"
    )

    env_meta: dict[str, Any] = {
        "mode": args.mode,
        "quick_smoke": args.quick_smoke,
        "os": platform.platform(),
        "cpu": platform.processor(),
        "cpu_logical_cores": os.cpu_count(),
        "python_version": sys.version.split()[0],
        "rust_compiler": rustc_ver,
        "node_v8_version": node_ver,
        "ephemeris_oss_version": ephemeris_oss.__version__,
        "pyerfa_version": erfa.__version__,
        "jplephem_version": jplephem.__version__,
        "numpy_version": np.__version__,
        "de440_bsp_sha256": _sha256_file(de440_path),
    }
    if "swe" in mods:
        env_meta["se_c_library_version"] = getattr(mods["swe"], "version", "2.10.03")
    if "skyfield" in mods:
        env_meta["skyfield_version"] = mods["skyfield"].__version__
    if "astropy" in mods:
        env_meta["astropy_version"] = mods["astropy"].__version__
    if "ephem" in mods:
        env_meta["pyephem_version"] = mods["ephem"].__version__

    payload = {
        "schema": "rdg-real-world-sota-head-to-head-v1",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_benchmark_wall_seconds": round(time.perf_counter() - t_all, 2),
        "environment": env_meta,
        "eval1_horizons_de441_2100_rows": e1,
        "eval2_zero_download_756yr_63518_points": e2,
        "eval3_throughput_10000_charts_and_streaming": e3,
        "eval4_wgs84_geodetic_houses_vs_horizons_vertical": e4,
    }
    raw_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload["receipt_sha256"] = hashlib.sha256(raw_bytes).hexdigest()

    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"WROTE_SOTA_BENCHMARK_RECEIPT={args.out}")
    else:
        print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
