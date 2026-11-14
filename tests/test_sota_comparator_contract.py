"""Contract tests for the distributable isolated SOTA comparator runner and Horizons vertical houses."""

from __future__ import annotations

from datetime import datetime
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
    assert locators["public_download_references"]["nasa_jpl_de440_bsp"]["sha256"] == (
        "a4ce9bf9b3282becc9f4b2ac3cebe03a2ae7599981aabd7265fd8482fff7c4b5"
    )
    assert "external_comparator_packages" in locators
    assert "external_archive_disclosure" in locators

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
    assert len(receipt["receipt_sha256"]) == 64


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
