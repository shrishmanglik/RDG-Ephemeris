"""Parity and binary verification tests for the Rust/WebAssembly core crate (`rust/ephemeris-core`)."""

from __future__ import annotations

import ctypes
import json
import math
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest

from ephemeris_oss.compact_kernel import CompactChebyshevKernel, CompactChebyshevSegment
from ephemeris_oss.rust_bridge import (
    EXPECTED_WASM_EXPORTS,
    J2000_JD,
    ayanamsa_deg,
    chebyshev_state_3d,
    evaluate_chebyshev_1d,
    evaluate_chebyshev_clenshaw_1d,
    evaluate_chebyshev_clenshaw_3d,
    fnv1a64_f64_slice,
    general_precession_deg,
    load_native_cdylib,
    mean_lunar_node_deg,
    normalize_deg,
    varga_sign,
    verify_wasm_binary,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
WASM_PATH = REPO_ROOT / "rust" / "ephemeris-core" / "wasm" / "ephemeris_core.wasm"
NATIVE_DLL_PATH = REPO_ROOT / "rust" / "ephemeris-core" / "target" / "release" / "ephemeris_core.dll"
WEB_PACKAGE_JSON = REPO_ROOT / "web" / "package.json"
WEB_BROWSER_JS = REPO_ROOT / "web" / "ephemeris-browser.js"
WEB_BROWSER_DTS = REPO_ROOT / "web" / "ephemeris-browser.d.ts"


def test_compiled_wasm_binary_header_and_exports() -> None:
    assert WASM_PATH.is_file(), f"Missing compiled WebAssembly binary at {WASM_PATH}"
    report = verify_wasm_binary(WASM_PATH)
    assert int(report["size_bytes"]) < 65_536
    assert report["exports_verified"] == EXPECTED_WASM_EXPORTS
    assert "eoss_eval_chebyshev_1d" in report["exports_verified"]


def test_chebyshev_1d_and_3d_exact_polynomial_and_velocity() -> None:
    # f(tau) = 5*T0 + 3*T1 - 1.5*T2 + 0.5*T3
    coeffs = (5.0, 3.0, -1.5, 0.5)
    coeffs_rev = (0.5, -1.5, 3.0, 5.0)
    span_days = 8.0
    for tau in (-0.85, -0.25, 0.0, 0.4, 0.95):
        t2 = 2.0 * tau * tau - 1.0
        t3 = 4.0 * (tau**3) - 3.0 * tau
        expected_val = 5.0 + 3.0 * tau - 1.5 * t2 + 0.5 * t3
        expected_der = 3.0 - 1.5 * (4.0 * tau) + 0.5 * (12.0 * tau * tau - 3.0)
        val, der = evaluate_chebyshev_1d(coeffs, tau)
        assert val == pytest.approx(expected_val, abs=1e-14)
        assert der == pytest.approx(expected_der, abs=1e-14)

        pos_c, vel_c = evaluate_chebyshev_clenshaw_1d(coeffs_rev, tau, span_days)
        assert pos_c == pytest.approx(expected_val, abs=1e-14)
        assert vel_c == pytest.approx(expected_der * (2.0 / span_days), abs=1e-14)

    coeffs_xyz = (
        100.0, 10.0, -2.0, 0.5,
        -200.0, 5.0, 1.0, -0.25,
        50.0, -3.0, 0.5, 0.1,
    )
    t_start = 2451545.0
    t_end = 2451561.0
    t_eval = 2451551.4
    x, y, z, vx, vy, vz = chebyshev_state_3d(coeffs_xyz, 4, t_start, t_end, t_eval)
    dt = 1e-3
    x_plus, y_plus, z_plus, _, _, _ = chebyshev_state_3d(coeffs_xyz, 4, t_start, t_end, t_eval + dt)
    x_minus, y_minus, z_minus, _, _, _ = chebyshev_state_3d(coeffs_xyz, 4, t_start, t_end, t_eval - dt)
    assert vx == pytest.approx((x_plus - x_minus) / (2.0 * dt), abs=1e-6)
    assert vy == pytest.approx((y_plus - y_minus) / (2.0 * dt), abs=1e-6)
    assert vz == pytest.approx((z_plus - z_minus) / (2.0 * dt), abs=1e-6)


def test_evaluate_chebyshev_clenshaw_3d_matches_compact_kernel_segments() -> None:
    kernel = CompactChebyshevKernel.open()
    seg_map = {
        (seg.center, seg.target): seg
        for seg in kernel.segments
        if isinstance(seg, CompactChebyshevSegment)
    }
    target_pairs = ((3, 301), (0, 3), (0, 10), (0, 5), (0, 6))
    test_epochs = (2415020.0, 2440587.5, 2451545.0, 2460500.25, 2475000.75)

    for pair in target_pairs:
        seg = seg_map[pair]
        for jd_tdb in test_epochs:
            ref_pos, ref_vel = seg.compute_and_differentiate(jd_tdb)

            # Test full 3D segment array evaluation
            pos_3d, vel_3d = evaluate_chebyshev_clenshaw_3d(
                seg.coefficients_rev, jd_tdb, seg.start_jd, seg.intlen_days
            )
            assert float(np.max(np.abs(pos_3d - ref_pos))) < 1e-9
            assert float(np.max(np.abs(vel_3d - ref_vel))) < 1e-9

            # Test single-interval 2D slice evaluation
            idx = int((jd_tdb - seg.start_jd) // seg.intlen_days)
            interval_start = seg.start_jd + idx * seg.intlen_days
            pos_2d, vel_2d = evaluate_chebyshev_clenshaw_3d(
                seg.coefficients_rev[:, :, idx], jd_tdb, interval_start, seg.intlen_days
            )
            assert float(np.max(np.abs(pos_2d - ref_pos))) < 1e-9
            assert float(np.max(np.abs(vel_2d - ref_vel))) < 1e-9


def test_jyotish_wasm_package_json_and_browser_exports() -> None:
    assert WEB_PACKAGE_JSON.is_file(), f"Missing {WEB_PACKAGE_JSON}"
    pkg = json.loads(WEB_PACKAGE_JSON.read_text(encoding="utf-8"))
    assert pkg["name"] == "@theagistudio/jyotish-wasm"
    assert pkg["version"] == "0.2.0"
    assert pkg["license"] == "Apache-2.0"
    assert pkg["type"] == "module"
    assert pkg["main"] == "./ephemeris-browser.js"
    assert pkg["types"] == "./ephemeris-browser.d.ts"
    assert pkg.get("dependencies", {}) == {}

    js_source = WEB_BROWSER_JS.read_text(encoding="utf-8")
    dts_source = WEB_BROWSER_DTS.read_text(encoding="utf-8")
    assert "export function evaluateChebyshevSegment3D(" in js_source
    assert "export function benchmarkClientKundali(" in js_source
    assert "export function evaluateChebyshevSegment3D(" in dts_source
    assert "export function benchmarkClientKundali(" in dts_source

    node_bin = shutil.which("node")
    if node_bin is not None:
        kernel = CompactChebyshevKernel.open()
        moon_seg = next(
            s for s in kernel.segments if isinstance(s, CompactChebyshevSegment) and (s.center, s.target) == (3, 301)
        )
        jd_tdb = 2451545.375
        idx = int((jd_tdb - moon_seg.start_jd) // moon_seg.intlen_days)
        interval_start = moon_seg.start_jd + idx * moon_seg.intlen_days
        ref_pos, ref_vel = moon_seg.compute_and_differentiate(jd_tdb)
        cx = moon_seg.coefficients_rev[:, 0, idx].tolist()
        cy = moon_seg.coefficients_rev[:, 1, idx].tolist()
        cz = moon_seg.coefficients_rev[:, 2, idx].tolist()

        script = (
            f"import {{ evaluateChebyshevSegment3D, benchmarkClientKundali }} from './web/ephemeris-browser.js';"
            f"const state = evaluateChebyshevSegment3D({json.dumps(cx)}, {json.dumps(cy)}, {json.dumps(cz)}, {jd_tdb}, {interval_start}, {moon_seg.intlen_days});"
            f"const bench = benchmarkClientKundali(16);"
            f"console.log(JSON.stringify({{ state, bench }}));"
        )
        proc = subprocess.run(
            [node_bin, "--input-type=module", "-e", script],
            cwd=str(REPO_ROOT),
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(proc.stdout.strip())
        state = payload["state"]
        assert len(state) == 6
        for axis in range(3):
            assert state[axis] == pytest.approx(float(ref_pos[axis]), abs=1e-9)
            assert state[axis + 3] == pytest.approx(float(ref_vel[axis]), abs=1e-9)

        bench = payload["bench"]
        assert bench["iterations"] == 16
        assert bench["medianMs"] < 2.0
        assert bench["sub2msQualified"] is True
        assert len(bench["sampleReceiptSha256"]) == 64


def test_mean_lunar_node_and_ayanamsa_formulas() -> None:
    assert mean_lunar_node_deg(J2000_JD) == pytest.approx(125.0445479, abs=1e-12)
    assert general_precession_deg(J2000_JD) == pytest.approx(0.0, abs=1e-15)
    assert ayanamsa_deg(J2000_JD, 0) == pytest.approx(23.853055555555556, abs=1e-12)
    assert ayanamsa_deg(J2000_JD + 36525.0, 0) > ayanamsa_deg(J2000_JD, 0) + 1.39


@pytest.mark.parametrize("varga_d", [1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60])
def test_all_16_shodashvarga_charts_across_zodiac(varga_d: int) -> None:
    for deg in range(0, 360, 3):
        sign = varga_sign(deg + 0.37, varga_d)
        assert 0 <= sign < 12


def test_fnv1a64_receipt_determinism() -> None:
    sample = (2451545.0, 280.46, 218.31, 23.8530556)
    h1 = fnv1a64_f64_slice(sample)
    h2 = fnv1a64_f64_slice(sample)
    h3 = fnv1a64_f64_slice((2451545.0, 280.46, 218.31, 23.8530557))
    assert h1 == h2
    assert h1 != h3


@pytest.mark.skipif(not NATIVE_DLL_PATH.is_file(), reason="compiled native Rust cdylib not present")
def test_native_rust_cdylib_matches_python_reference_to_machine_epsilon() -> None:
    lib = load_native_cdylib(NATIVE_DLL_PATH)
    for angle in (-725.4, -0.1, 0.0, 123.456, 360.0, 745.2):
        assert lib.ephemeris_normalize_deg(angle) == pytest.approx(normalize_deg(angle), abs=1e-13)

    for jd in (2415020.0, 2451545.0, 2461328.5):
        assert lib.ephemeris_mean_lunar_node_deg(jd) == pytest.approx(mean_lunar_node_deg(jd), abs=1e-12)
        for sys_id in range(6):
            assert lib.ephemeris_ayanamsa_deg(jd, sys_id) == pytest.approx(ayanamsa_deg(jd, sys_id), abs=1e-12)

    coeffs = (100.0, 10.0, -2.0, 0.5, -200.0, 5.0, 1.0, -0.25, 50.0, -3.0, 0.5, 0.1)
    c_coeffs = (ctypes.c_double * 12)(*coeffs)
    c_out = (ctypes.c_double * 6)()
    rc = lib.ephemeris_chebyshev_state_3d(c_coeffs, 4, 2451545.0, 2451561.0, 2451551.4, c_out)
    assert rc == 0
    py_out = chebyshev_state_3d(coeffs, 4, 2451545.0, 2451561.0, 2451551.4)
    for r_val, p_val in zip(c_out, py_out):
        assert r_val == pytest.approx(p_val, abs=1e-13)

    for varga_d in (1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60):
        for deg in range(0, 360, 7):
            lon = deg + 1.23
            assert int(lib.ephemeris_varga_sign(lon, varga_d)) == varga_sign(lon, varga_d)
