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
from ephemeris_oss.jyotish.ashtakavarga import BAV_BENEFIC_HOUSES
from ephemeris_oss.rust_bridge import (
    EXPECTED_WASM_EXPORTS,
    J2000_JD,
    BatchNatalRequest,
    FullKundaliOutput,
    ayanamsa_deg,
    chebyshev_state_3d,
    evaluate_chebyshev_1d,
    evaluate_chebyshev_clenshaw_1d,
    evaluate_chebyshev_clenshaw_3d,
    fnv1a64_f64_slice,
    general_precession_deg,
    kp_sub_index,
    load_native_cdylib,
    mean_lunar_node_deg,
    nakshatra_index,
    nakshatra_pada,
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


def test_zero_copy_struct_sizes_and_browser_arena() -> None:
    assert ctypes.sizeof(BatchNatalRequest) == 64
    assert ctypes.sizeof(FullKundaliOutput) == 1416

    js_source = WEB_BROWSER_JS.read_text(encoding="utf-8")
    dts_source = WEB_BROWSER_DTS.read_text(encoding="utf-8")
    assert "export async function initEphemerisWasm(" in js_source
    assert "export function computeFullChartZeroCopy(" in js_source
    assert "export function initEphemerisWasm(" in dts_source
    assert "export function computeFullChartZeroCopy(" in dts_source

    node_bin = shutil.which("node")
    if node_bin is not None:
        script = (
            "import fs from 'node:fs';"
            "import { initEphemerisWasm, computeFullChartZeroCopy } from './web/ephemeris-browser.js';"
            "const wasmBytes = fs.readFileSync('./rust/ephemeris-core/wasm/ephemeris_core.wasm');"
            "await initEphemerisWasm(wasmBytes);"
            "const polarView = computeFullChartZeroCopy({ jdUtc: 2451545.0, latDeg: 78.0, lonDeg: 15.6, houseSystemId: 2 });"
            "const savSum = Array.from(polarView.ashtakavargaSav).reduce((a, b) => a + b, 0);"
            "const lagnaBavSum = Array.from(polarView.ashtakavargaBav.subarray(84, 96)).reduce((a, b) => a + b, 0);"
            "const vargaMin = Math.min(...Array.from(polarView.vargaRashiMatrix));"
            "const vargaMax = Math.max(...Array.from(polarView.vargaRashiMatrix));"
            "console.log(JSON.stringify({ byteLength: polarView.byteLength, polarStatusFlag: polarView.polarStatusFlag, savSum, lagnaBavSum, vargaMin, vargaMax }));"
        )
        proc = subprocess.run(
            [node_bin, "--input-type=module", "-e", script],
            cwd=str(REPO_ROOT),
            check=True,
            capture_output=True,
            text=True,
        )
        out = json.loads(proc.stdout.strip())
        assert out["byteLength"] == 1416
        assert out["polarStatusFlag"] == 1
        assert out["savSum"] == 337
        assert out["lagnaBavSum"] == 49
        assert 1 <= out["vargaMin"] <= 12
        assert 1 <= out["vargaMax"] <= 12


@pytest.mark.skipif(not NATIVE_DLL_PATH.is_file(), reason="compiled native Rust cdylib not present")
def test_1000_stratified_epochs_python_to_rust_parity() -> None:
    lib = load_native_cdylib(NATIVE_DLL_PATH)
    shodashvarga_divs = (1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60)
    planet_names = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
    contrib_names = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Lagna")

    max_angular_diff = 0.0
    discrete_mismatches = 0

    for i in range(1000):
        # 1,000 stratified epochs across 1800..2100 CE (JD 2378496.5 .. 2488069.5)
        jd_tt = 2378496.5 + (i / 999.0) * (2488069.5 - 2378496.5)
        lon_deg = ((i * 137.50776405003785) + 0.0173) % 360.0

        # 1. Continuous angular parity (<= 1.0e-9 deg)
        node_diff = abs(float(lib.ephemeris_mean_lunar_node_deg(jd_tt)) - mean_lunar_node_deg(jd_tt))
        aya_diff = abs(float(lib.ephemeris_ayanamsa_deg(jd_tt, i % 6)) - ayanamsa_deg(jd_tt, i % 6))
        max_angular_diff = max(max_angular_diff, node_diff, aya_diff)

        # 2. Discrete Nakshatra (0..26), Pada (1..4), KP 249 (1..249), and 16-Varga sign parity
        if int(lib.ephemeris_nakshatra_index(lon_deg)) != nakshatra_index(lon_deg):
            discrete_mismatches += 1
        if int(lib.ephemeris_nakshatra_pada(lon_deg)) != nakshatra_pada(lon_deg):
            discrete_mismatches += 1
        if int(lib.ephemeris_kp_sub_index(lon_deg)) != kp_sub_index(lon_deg):
            discrete_mismatches += 1
        for v_div in shodashvarga_divs:
            if int(lib.ephemeris_varga_sign(lon_deg, v_div)) != varga_sign(lon_deg, v_div):
                discrete_mismatches += 1

    assert max_angular_diff <= 1.0e-9
    assert discrete_mismatches == 0

    # Verify zero-copy C-ABI arena + 337-bindu Ashtakavarga parity across stratified epochs
    req_ptr = lib.wasm_arena_request_ptr()
    out_ptr = lib.wasm_arena_output_ptr()
    for step in range(50):
        jd_utc = 2415020.0 + step * 1100.37
        lat = -60.0 + (step % 25) * 5.0
        lon = -120.0 + (step * 29.0) % 240.0
        req_ptr.contents.jd_utc = jd_utc
        req_ptr.contents.jd_tt = jd_utc + (69.184 / 86400.0)
        req_ptr.contents.delta_t_sec = 69.184
        req_ptr.contents.lat_deg = lat
        req_ptr.contents.lon_deg = lon
        req_ptr.contents.alt_m = 100.0
        req_ptr.contents.ayanamsa_id = step % 6
        req_ptr.contents.house_system_id = step % 3
        req_ptr.contents.node_mode = step % 2

        rc = lib.wasm_compute_full_kundali(req_ptr, out_ptr)
        assert rc == 0
        out = out_ptr.contents

        sav_list = [int(out.ashtakavarga_sav[s]) for s in range(12)]
        assert sum(sav_list) == 337
        lagna_bav_list = [int(out.ashtakavarga_bav[7][s]) for s in range(12)]
        assert sum(lagna_bav_list) == 49

        for v_idx in range(16):
            for b_idx in range(12):
                assert 1 <= int(out.varga_rashi_matrix[v_idx][b_idx]) <= 12

        # Recompute BAV and SAV in Python from the D1 Rasi placements in `varga_rashi_matrix[0]` (1-based -> 0-based)
        d1_signs = [int(out.varga_rashi_matrix[0][b]) - 1 for b in range(12)]
        contrib_signs = d1_signs[:7] + [d1_signs[11]]
        py_sav = [0] * 12
        for p_idx, p_name in enumerate(planet_names):
            py_bav = [0] * 12
            for c_idx, c_name in enumerate(contrib_names):
                ref_sign = contrib_signs[c_idx]
                for h_off in BAV_BENEFIC_HOUSES[p_name][c_name]:
                    target_sign = (ref_sign + h_off - 1) % 12
                    py_bav[target_sign] += 1
                    py_sav[target_sign] += 1
            rust_bav = [int(out.ashtakavarga_bav[p_idx][s]) for s in range(12)]
            assert rust_bav == py_bav
        assert sav_list == py_sav

    # Verify polar fallback flag (lat_deg = 78.0, house_system_id = 2 Placidus -> polar_status_flag == 1)
    req_ptr.contents.lat_deg = 78.0
    req_ptr.contents.house_system_id = 2
    assert lib.wasm_compute_full_kundali(req_ptr, out_ptr) == 0
    assert int(out_ptr.contents.polar_status_flag) == 1


