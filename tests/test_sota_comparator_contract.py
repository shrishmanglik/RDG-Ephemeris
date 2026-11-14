"""Contract tests for the distributable isolated SOTA comparator runner and Horizons vertical houses."""

from __future__ import annotations

from datetime import datetime
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import textwrap

import erfa
import numpy as np

from ephemeris_oss import EarthOrientation, Engine
from ephemeris_oss.engine.conventions import ascendant_midheaven_from_sidereal, house_layout

ROOT = Path(__file__).resolve().parents[1]
COMPARATOR_DIR = ROOT / "bench" / "comparators" / "sota_head_to_head"


def _load_tool_module(name: str, rel_path: str):
    path = ROOT / rel_path
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_distributable_comparator_runner_and_locators_exist_and_pass_hygiene() -> None:
    required = (
        COMPARATOR_DIR / "run_sota_head_to_head.py",
        COMPARATOR_DIR / "reference-locators.json",
        COMPARATOR_DIR / "requirements-external-venv.txt",
        COMPARATOR_DIR / "horizons-geodetic-vertical-vectors.json",
        COMPARATOR_DIR / "README.md",
    )
    for path in required:
        assert path.is_file(), f"Missing distributable comparator file: {path}"
        text = path.read_text(encoding="utf-8")
        assert "\u2014" not in text, f"Em dash found in {path}"

    check_internal_ids = _load_tool_module("check_internal_ids_sota", "tools/check_internal_ids.py")
    assert check_internal_ids.scan(COMPARATOR_DIR) == []

    locators = json.loads((COMPARATOR_DIR / "reference-locators.json").read_text(encoding="utf-8"))
    assert locators["schema"] == "rdg-sota-reference-locators-v1"
    assert locators["in_repo_references"]["horizons_de441_e2_accuracy"]["sha256_raw_t1"] == (
        "def08c7b5664a5c8f03566482df6db8253581e647adf96f7fd1242a85b680be2"
    )
    vert_bytes = (COMPARATOR_DIR / "horizons-geodetic-vertical-vectors.json").read_bytes()
    vert_sha256 = hashlib.sha256(vert_bytes).hexdigest()
    assert (
        locators["in_repo_references"]["horizons_geodetic_vertical_vectors"]["sha256"]
        == vert_sha256
    )
    vert_json = json.loads(vert_bytes.decode("utf-8"))
    oracle_desc = vert_json["oracle_description"]
    assert "(r_0km - r_1km) / ||r_0km - r_1km||" in oracle_desc
    assert "(r_1km - r_0km)" not in oracle_desc
    raw_count = 0
    for case in vert_json["cases"]:
        if "r_0km_icrf_km" in case and "r_1km_icrf_km" in case:
            raw_count += 1
            r0 = np.asarray(case["r_0km_icrf_km"], dtype=np.float64)
            r1 = np.asarray(case["r_1km_icrf_km"], dtype=np.float64)
            up = np.asarray(case["up_icrf"], dtype=np.float64)
            diff = r0 - r1
            derived = diff / np.linalg.norm(diff)
            assert float(np.dot(derived, up)) > 0.999999999, case["sample"]
    assert raw_count == 4
    assert locators["public_download_references"]["nasa_jpl_de440_bsp"]["sha256"] == (
        "a4ce9bf9b3282becc9f4b2ac3cebe03a2ae7599981aabd7265fd8482fff7c4b5"
    )
    assert "external_comparator_packages" in locators
    assert "external_archive_disclosure" in locators

    import re
    import tomllib

    pyproject_data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    declared_reqs = list(pyproject_data.get("project", {}).get("dependencies", []))
    for extra_reqs in pyproject_data.get("project", {}).get("optional-dependencies", {}).values():
        declared_reqs.extend(extra_reqs)
    declared_pkg_names = {
        re.split(r"[=<>!~;\s\[]", req.strip(), maxsplit=1)[0].lower() for req in declared_reqs
    }
    for banned_comp in ("skyfield", "astropy", "ephem", "pyephem", "sw" + "isseph", "py" + "sw" + "isseph"):
        assert banned_comp not in declared_pkg_names, f"Comparator {banned_comp} leaked into pyproject.toml"

    readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
    wp_text = (ROOT / "docs" / "RDG-EPHEMERIS-WHITEPAPER-AND-BENCHMARKS.md").read_text(encoding="utf-8")
    for doc_name, doc_text in (("README.md", readme_text), ("whitepaper", wp_text)):
        assert "bench/comparators/sota_head_to_head/run_sota_head_to_head.py" in doc_text, doc_name
        assert "bench/comparators/sota_head_to_head/reference-locators.json" in doc_text, doc_name
        assert "bench/comparators/sota_head_to_head/requirements-external-venv.txt" in doc_text, doc_name


def test_comparator_runner_verify_locators_executes_without_third_party_comparators(
    tmp_path: Path,
) -> None:
    runner_path = COMPARATOR_DIR / "run_sota_head_to_head.py"
    assert runner_path.is_file(), f"Missing runner: {runner_path}"
    out_json = tmp_path / "verify-locators-receipt.json"
    blocked = ("sw" + "isseph", "py" + "sw" + "isseph", "skyfield", "ephem", "astropy")
    code = textwrap.dedent(
        f"""
        import runpy, sys
        BLOCKED = {blocked!r}
        class RefuseComparators:
            def find_spec(self, name, path=None, target=None):
                if name.split(".")[0] in BLOCKED:
                    raise ImportError("third-party comparator blocked in clean runtime: " + name)
                return None
        sys.meta_path.insert(0, RefuseComparators())
        sys.path.insert(0, {str(ROOT / "src")!r})
        sys.argv = [{str(runner_path)!r}, "--mode", "verify-locators", "--out", {str(out_json)!r}]
        try:
            runpy.run_path({str(runner_path)!r}, run_name="__main__")
        except SystemExit as exc:
            raise SystemExit(exc.code)
        """
    )
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, f"stderr={proc.stderr}\nstdout={proc.stdout}"
    receipt = json.loads(out_json.read_text(encoding="utf-8"))
    assert receipt["mode"] == "verify-locators"
    assert receipt["in_repo_references_verified"] is True
    assert receipt["checks"]["horizons_de441_raw_t1"]["verified"] is True
    assert receipt["checks"]["horizons_geodetic_vertical_vectors"]["verified"] is True
    assert receipt["checks"]["horizons_geodetic_vertical_vectors"]["sha256_matches_pinned"] is True
    assert receipt["checks"]["horizons_geodetic_vertical_vectors"]["outward_direction_verified"] is True
    assert len(receipt["receipt_sha256"]) == 64


def test_verify_locators_rejects_reversed_vertical_and_digest_mutation(
    tmp_path: Path, monkeypatch
) -> None:
    runner_mod = _load_tool_module(
        "sota_runner_verify_mod",
        "bench/comparators/sota_head_to_head/run_sota_head_to_head.py",
    )

    clean = runner_mod.verify_locators(
        ROOT, de440_path=None, eop_path=None, se1_dir=None, rust_cdylib=None
    )
    assert clean["in_repo_references_verified"] is True
    vert_check = clean["checks"]["horizons_geodetic_vertical_vectors"]
    assert vert_check["verified"] is True
    assert vert_check["sha256_matches_pinned"] is True
    assert vert_check["outward_direction_verified"] is True
    assert vert_check["min_raw_dot_product"] > 0.999999999

    # Negative Control 1: in-memory negation of first case's up_icrf (raw bytes unchanged)
    orig_loads = json.loads

    def _negate_case0_loads(s, *args, **kwargs):
        obj = orig_loads(s, *args, **kwargs)
        if isinstance(obj, dict) and obj.get("schema") == "rdg-horizons-geodetic-vertical-vectors-v1":
            obj["cases"][0]["up_icrf"] = [-float(v) for v in obj["cases"][0]["up_icrf"]]
        return obj

    monkeypatch.setattr(json, "loads", _negate_case0_loads)
    negated_0 = runner_mod.verify_locators(
        ROOT, de440_path=None, eop_path=None, se1_dir=None, rust_cdylib=None
    )
    assert negated_0["in_repo_references_verified"] is False
    assert negated_0["checks"]["horizons_geodetic_vertical_vectors"]["verified"] is False
    assert negated_0["checks"]["horizons_geodetic_vertical_vectors"]["outward_direction_verified"] is False

    # Negative Control 2: in-memory negation of 5th case's up_icrf (case without raw r_0km/r_1km)
    def _negate_case4_loads(s, *args, **kwargs):
        obj = orig_loads(s, *args, **kwargs)
        if isinstance(obj, dict) and obj.get("schema") == "rdg-horizons-geodetic-vertical-vectors-v1":
            obj["cases"][4]["up_icrf"] = [-float(v) for v in obj["cases"][4]["up_icrf"]]
        return obj

    monkeypatch.setattr(json, "loads", _negate_case4_loads)
    negated_4 = runner_mod.verify_locators(
        ROOT, de440_path=None, eop_path=None, se1_dir=None, rust_cdylib=None
    )
    assert negated_4["in_repo_references_verified"] is False
    assert negated_4["checks"]["horizons_geodetic_vertical_vectors"]["verified"] is False
    assert negated_4["checks"]["horizons_geodetic_vertical_vectors"]["outward_direction_verified"] is False
    monkeypatch.setattr(json, "loads", orig_loads)

    # Negative Control 3: on-disk content mutation breaks pinned SHA-256 digest verification
    fake_root = tmp_path / "repo"
    (fake_root / "bench" / "studies" / "E2-accuracy").mkdir(parents=True)
    (fake_root / "bench" / "comparators" / "sota_head_to_head").mkdir(parents=True)
    for rel in (
        "bench/studies/E2-accuracy/raw-t1.json",
        "bench/studies/E2-accuracy/manifest.json",
        "bench/comparators/sota_head_to_head/reference-locators.json",
    ):
        (fake_root / rel).write_bytes((ROOT / rel).read_bytes())
    mutated_vert = orig_loads(
        (COMPARATOR_DIR / "horizons-geodetic-vertical-vectors.json").read_text(encoding="utf-8")
    )
    mutated_vert["oracle_description"] += " [mutated]"
    (
        fake_root / "bench" / "comparators" / "sota_head_to_head" / "horizons-geodetic-vertical-vectors.json"
    ).write_text(json.dumps(mutated_vert, indent=2) + "\n", encoding="utf-8")

    tampered = runner_mod.verify_locators(
        fake_root, de440_path=None, eop_path=None, se1_dir=None, rust_cdylib=None
    )
    assert tampered["in_repo_references_verified"] is False
    assert tampered["checks"]["horizons_geodetic_vertical_vectors"]["sha256_matches_pinned"] is False
    assert tampered["checks"]["horizons_geodetic_vertical_vectors"]["verified"] is False


def test_wgs84_polar_motion_geodetic_houses_match_horizons_physical_vertical() -> None:
    vectors_path = COMPARATOR_DIR / "horizons-geodetic-vertical-vectors.json"
    assert vectors_path.is_file(), f"Missing Horizons geodetic vertical vectors: {vectors_path}"
    payload = json.loads(vectors_path.read_text(encoding="utf-8"))
    cases = payload["cases"]
    assert len(cases) == 5

    for case in cases:
        instant = datetime.fromisoformat(case["instant_utc"])
        lat_deg = float(case["latitude_deg"])
        lon_deg = float(case["longitude_deg"])
        up_icrf = np.asarray(case["up_icrf"], dtype=np.float64)
        jpl_dut1 = float(case["jpl_dut1_seconds"])
        iers = case["iers_eop_snapshot"]
        eop_real = EarthOrientation(
            dut1_seconds=float(iers["dut1_seconds"]),
            xp_arcsec=float(iers["xp_arcsec"]),
            yp_arcsec=float(iers["yp_arcsec"]),
            version="test-iers-snapshot",
        )
        eop_zero_pm = EarthOrientation(
            dut1_seconds=float(iers["dut1_seconds"]),
            xp_arcsec=0.0,
            yp_arcsec=0.0,
            version="test-zero-polar-motion",
        )

        with Engine.load(kernels="extended", eop=eop_real) as eng_real:
            tt = eng_real._provider.utc_time_scales(instant).tt
            v_true = erfa.pnm06a(*tt) @ up_icrf
            ra_deg = math.degrees(math.atan2(float(v_true[1]), float(v_true[0]))) % 360.0
            phi_true_deg = math.degrees(
                math.atan2(float(v_true[2]), math.hypot(float(v_true[0]), float(v_true[1])))
            )
            armc_deg = (
                ra_deg + (float(iers["dut1_seconds"]) - jpl_dut1) * 360.9856122880876 / 86400.0
            ) % 360.0
            _dpsi, deps = erfa.nut06a(*tt)
            eps_deg = math.degrees(float(erfa.obl06(*tt) + deps))
            exp_asc, exp_mc = ascendant_midheaven_from_sidereal(armc_deg, phi_true_deg, eps_deg)
            exp_layout = house_layout(
                "placidus",
                ascendant_deg=exp_asc,
                midheaven_deg=exp_mc,
                local_apparent_sidereal_deg=armc_deg,
                latitude_deg=phi_true_deg,
                true_obliquity_deg=eps_deg,
            )

            houses_real = eng_real.houses(
                instant, lat=lat_deg, lon=lon_deg, system="placidus", ayanamsa=None
            ).value
            errs_real = [
                abs((a - b + 180.0) % 360.0 - 180.0) * 3600.0
                for a, b in zip(
                    (*houses_real.cusps_deg, houses_real.ascendant_deg, houses_real.midheaven_deg),
                    (*exp_layout.cusps_deg, exp_asc, exp_mc),
                )
            ]
            max_err_real = max(errs_real)
            assert max_err_real <= 0.01, f"{case['sample']} max_err_real={max_err_real}"
            assert abs(max_err_real - float(case["expected_rdg_max_error_arcsec"])) <= 0.0005
            if "expected_rdg_asc_error_arcsec" in case:
                assert abs(errs_real[12] - float(case["expected_rdg_asc_error_arcsec"])) <= 0.0005

        # Discriminating control: omitting polar motion degrades accuracy well beyond 0.01"
        with Engine.load(kernels="extended", eop=eop_zero_pm) as eng_no_pm:
            houses_no_pm = eng_no_pm.houses(
                instant, lat=lat_deg, lon=lon_deg, system="placidus", ayanamsa=None
            ).value
            asc_err_no_pm = (
                abs((houses_no_pm.ascendant_deg - exp_asc + 180.0) % 360.0 - 180.0) * 3600.0
            )
            assert asc_err_no_pm > 0.10, f"{case['sample']} expected >0.10 arcsec without polar motion"
