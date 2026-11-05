#!/usr/bin/env python3
"""One-command reproducible benchmark against NASA JPL Horizons and IAE reference tables.

Evaluates our RDG Ephemeris engine against independent public astronomical standards:
- Scores our RDG engine against committed NASA JPL Horizons apparent vectors and the Indian Astronomical
  Ephemeris (IAE 1989 p. 556 / CSIR 1955) Lahiri anchor.
- Enforces strict frame- and epoch-matched residual tolerances before emitting any PASS or public tie claim,
  and propagates a non-zero exit code on any tolerance failure.
- Adheres strictly to Claim-Integrity rule C7: states that RDG ties reference accuracy within the measured truth floor;
  never claims to beat reference ephemerides.
- Outputs reproducible JSON and stdout receipts.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import erfa
import numpy as np

# Add src to path
_ROOT = Path(__file__).resolve().parent.parent
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from ephemeris_oss import Engine
from ephemeris_oss.engine.conventions import (
    J2000_TT_JD,
    LAHIRI_REFERENCE_TT_JD,
    _dms,
    ayanamsa_degrees,
)

# Frame- and epoch-matched reference constants and tolerances:
# 1. NASA JPL Horizons DE441 (QUANTITIES=45 apparent ICRF RA/DEC across 1800-2100, 2,100 samples):
HORIZONS_MEDIAN_TOLERANCE_ARCSEC = 0.005
HORIZONS_P95_TOLERANCE_ARCSEC = 0.025
HORIZONS_MAX_TOLERANCE_ARCSEC = 0.050

# 2. Report of the Calendar Reform Committee (CSIR India, 1955, p. 262) &
#    Indian Astronomical Ephemeris (IAE 1989, p. 556) defining epoch 1956-03-21 00:00:00 TT (JD 2435553.5):
#    - Published true Chitrapaksha ayanamsa (IAU 1980 nutation frame): 23 deg 15' 00.658"
#    - Corresponding mean ayanamsa at 1956-03-21.0 TT (IAU 1980 nutation removed): 23 deg 14' 44.019"
#    - Corresponding true ayanamsa at 1956-03-21.0 TT in IAU 2006/2000A nutation frame: 23 deg 15' 00.796"
#    - Transported mean Lahiri ayanamsa at J2000.0 TT (JD 2451545.0): 23.85709235 deg
IAE_LAHIRI_1956_TRUE_IAU1980_DEG = _dms(23, 15, 0.658)
IAE_LAHIRI_1956_MEAN_DEG = _dms(23, 14, 44.019)
IAE_LAHIRI_1956_TRUE_IAU2006_DEG = _dms(23, 15, 0.796)
IAE_LAHIRI_J2000_MEAN_DEG = 23.85709235

IAE_1956_MEAN_TOLERANCE_ARCSEC = 0.002
IAE_1956_TRUE_IAU2006_TOLERANCE_ARCSEC = 0.002
IAE_1956_CROSS_NUTATION_TOLERANCE_ARCSEC = 0.20
IAE_J2000_MEAN_TOLERANCE_ARCSEC = 0.0005

# Unverified candidate tabular value for 1989-01-01 00:00 UTC (JD 2447527.5) preserved as HELD evidence
# per Round 2 independent review (lacks primary-book page readback; excluded from certified agreement):
UNVERIFIED_1989_01_01_CANDIDATE_DEG = _dms(23, 42, 37.0)


def run_benchmark(output_path: Path | None = None) -> dict[str, Any]:
    print("=" * 80)
    print("REPRODUCIBLE LIVE BENCHMARK: RDG EPHEMERIS vs NASA JPL HORIZONS & IAE")
    print("Governing Rule: Ties reference accuracy within measured truth floor (never claims to beat)")
    print("=" * 80)

    # Part 1: Live evaluation of current Engine against NASA JPL Horizons truth corpus (1800-2100)
    raw_t1_path = _ROOT / "bench" / "studies" / "E2-accuracy" / "raw-t1.json"
    manifest_path = _ROOT / "bench" / "studies" / "E2-accuracy" / "manifest.json"
    if not raw_t1_path.exists():
        raise FileNotFoundError(f"Missing Horizons raw-t1 benchmark data at {raw_t1_path}")
    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing Horizons epoch manifest at {manifest_path}")

    raw_data = json.loads(raw_t1_path.read_text(encoding="utf-8"))
    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    jd_tt_by_id: dict[str, float] = {
        str(sample["id"]): float(sample["jd_tt"])
        for sample in manifest_data.get("samples", [])
    }
    rows = raw_data.get("rows", [])

    # Evaluate the live current engine using the embedded Chebyshev DE440 kernel at every Horizons epoch
    # and rotate from true ecliptic-of-date back to ICRF (RA, DEC) to compare against Horizons QUANTITIES=45 truth.
    unique_ids = sorted({str(row["id"]) for row in rows})
    bodies_tuple = ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn")
    live_positions_by_id: dict[str, dict[str, tuple[float, float]]] = {}
    t_live0 = time.perf_counter()
    with Engine.load(kernels="extended", eop=None) as engine:
        for sample_id in unique_ids:
            jd_tt = jd_tt_by_id[sample_id]
            tt = (2451545.0, jd_tt - 2451545.0)
            nut_deg = math.degrees(float(erfa.nut06a(*tt)[0]))
            ecm_t = np.asarray(erfa.ecm06(*tt), dtype=np.float64).T
            pos_res = engine.positions_tt(jd_tt, bodies=bodies_tuple).value
            per_body_icrf: dict[str, tuple[float, float]] = {}
            for b in bodies_tuple:
                lon_rad = math.radians(float(pos_res[b]["longitude_deg"]) - nut_deg)
                lat_rad = math.radians(float(pos_res[b]["latitude_deg"]))
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
                per_body_icrf[b] = (ra_deg, dec_deg)
            live_positions_by_id[sample_id] = per_body_icrf
    live_eval_ms = (time.perf_counter() - t_live0) * 1000.0

    body_residuals: dict[str, list[float]] = {}
    all_separations_arcsec: list[float] = []
    max_drift_from_committed_ours_arcsec = 0.0

    for row in rows:
        body = row["body"].lower()
        sample_id = str(row["id"])
        live_lon, live_lat = live_positions_by_id[sample_id][body]
        committed_lon, committed_lat = row["ours"]
        truth_lon, truth_lat = row["truth"]

        # Angular separation between LIVE current engine output and NASA JPL Horizons DE441 truth
        diff_lon = abs((live_lon - truth_lon + 180.0) % 360.0 - 180.0) * 3600.0
        diff_lat = abs(live_lat - truth_lat) * 3600.0
        sep = math.hypot(diff_lon, diff_lat)

        # Also track regression drift between live engine and committed baseline
        drift_lon = abs((live_lon - committed_lon + 180.0) % 360.0 - 180.0) * 3600.0
        drift_lat = abs(live_lat - committed_lat) * 3600.0
        max_drift_from_committed_ours_arcsec = max(
            max_drift_from_committed_ours_arcsec,
            math.hypot(drift_lon, drift_lat),
        )

        body_residuals.setdefault(body, []).append(sep)
        all_separations_arcsec.append(sep)

    body_summary: dict[str, dict[str, float]] = {}
    print(f"\n1. Live Engine vs NASA JPL Horizons Residuals (1800-2100 Corpus, evaluated in {live_eval_ms:.1f} ms):")
    print('   Body       | Samples  | Median (")   | P95 (")      | Max (")     ')
    print("   " + "-" * 62)

    for body, res_list in sorted(body_residuals.items()):
        sorted_res = sorted(res_list)
        n = len(sorted_res)
        median_val = sorted_res[n // 2]
        p95_val = sorted_res[int(n * 0.95)]
        max_val = sorted_res[-1]

        body_summary[body] = {
            "samples": n,
            "median_arcsec": median_val,
            "p95_arcsec": p95_val,
            "max_arcsec": max_val,
        }
        print(f"   {body.capitalize():<10} | {n:<8} | {median_val:<12.6f} | {p95_val:<12.6f} | {max_val:<12.6f}")

    sorted_all = sorted(all_separations_arcsec)
    total_samples = len(sorted_all)
    overall_median = sorted_all[total_samples // 2]
    overall_p95 = sorted_all[int(total_samples * 0.95)]
    overall_max = sorted_all[-1]

    horizons_pass = (
        total_samples == 2100
        and overall_median <= HORIZONS_MEDIAN_TOLERANCE_ARCSEC
        and overall_p95 <= HORIZONS_P95_TOLERANCE_ARCSEC
        and overall_max <= HORIZONS_MAX_TOLERANCE_ARCSEC
    )
    horizons_status = (
        "PASS_TIED_WITH_HORIZONS"
        if horizons_pass
        else "FAIL_HORIZONS_TOLERANCE_EXCEEDED"
    )

    print("   " + "-" * 62)
    print(f"   {'OVERALL':<10} | {total_samples:<8} | {overall_median:<12.6f} | {overall_p95:<12.6f} | {overall_max:<12.6f}")
    print(f"   Horizons Gate: {horizons_status} (tolerances: median <= {HORIZONS_MEDIAN_TOLERANCE_ARCSEC}\", P95 <= {HORIZONS_P95_TOLERANCE_ARCSEC}\", max <= {HORIZONS_MAX_TOLERANCE_ARCSEC}\")")

    # Part 2: Indian Astronomical Ephemeris (CSIR 1955 / IAE 1989 p. 556) External Published Anchors
    t0 = time.perf_counter()
    calculated_1956_true = ayanamsa_degrees(LAHIRI_REFERENCE_TT_JD, "lahiri", true=True)
    calculated_1956_mean = ayanamsa_degrees(LAHIRI_REFERENCE_TT_JD, "lahiri", true=False)
    calculated_j2000_mean = ayanamsa_degrees(J2000_TT_JD, "lahiri", true=False)
    calculated_1989_mean = ayanamsa_degrees(2447527.5, "lahiri", true=False)
    iae_calc_ms = (time.perf_counter() - t0) * 1000.0

    iae_1956_mean_residual_arcsec = abs(calculated_1956_mean - IAE_LAHIRI_1956_MEAN_DEG) * 3600.0
    iae_1956_true_iau2006_residual_arcsec = abs(calculated_1956_true - IAE_LAHIRI_1956_TRUE_IAU2006_DEG) * 3600.0
    iae_1956_cross_nutation_residual_arcsec = abs(calculated_1956_true - IAE_LAHIRI_1956_TRUE_IAU1980_DEG) * 3600.0
    iae_j2000_mean_residual_arcsec = abs(calculated_j2000_mean - IAE_LAHIRI_J2000_MEAN_DEG) * 3600.0
    unverified_1989_discrepancy_arcsec = abs(calculated_1989_mean - UNVERIFIED_1989_01_01_CANDIDATE_DEG) * 3600.0

    iae_pass = (
        iae_1956_mean_residual_arcsec <= IAE_1956_MEAN_TOLERANCE_ARCSEC
        and iae_1956_true_iau2006_residual_arcsec <= IAE_1956_TRUE_IAU2006_TOLERANCE_ARCSEC
        and iae_1956_cross_nutation_residual_arcsec <= IAE_1956_CROSS_NUTATION_TOLERANCE_ARCSEC
        and iae_j2000_mean_residual_arcsec <= IAE_J2000_MEAN_TOLERANCE_ARCSEC
    )
    iae_status = (
        "PASS_EXTERNAL_IAE_ANCHORS"
        if iae_pass
        else "FAIL_IAE_ANCHOR_TOLERANCE_EXCEEDED"
    )

    overall_pass = horizons_pass and iae_pass
    overall_status = "PASS" if overall_pass else "FAIL"

    print("\n2. Indian Astronomical Ephemeris (CSIR 1955 / IAE 1989 p. 556) Published External Anchors:")
    print(f"   1956-03-21 00:00 TT (JD {LAHIRI_REFERENCE_TT_JD:.1f}) Mean Anchor:   {IAE_LAHIRI_1956_MEAN_DEG:.8f} deg (23 deg 14' 44.019\")")
    print(f"   Engine Calculated 1956 Mean:                  {calculated_1956_mean:.8f} deg (residual {iae_1956_mean_residual_arcsec:.6f}\" <= {IAE_1956_MEAN_TOLERANCE_ARCSEC}\")")
    print(f"   1956-03-21 00:00 TT True (IAU 2006/2000A):    {IAE_LAHIRI_1956_TRUE_IAU2006_DEG:.8f} deg (23 deg 15' 00.796\")")
    print(f"   Engine Calculated 1956 True (IAU 2006/2000A): {calculated_1956_true:.8f} deg (residual {iae_1956_true_iau2006_residual_arcsec:.6f}\" <= {IAE_1956_TRUE_IAU2006_TOLERANCE_ARCSEC}\")")
    print(f"   1956-03-21 00:00 TT True (IAU 1980 Nutation): {IAE_LAHIRI_1956_TRUE_IAU1980_DEG:.8f} deg (cross-nutation delta {iae_1956_cross_nutation_residual_arcsec:.6f}\" <= {IAE_1956_CROSS_NUTATION_TOLERANCE_ARCSEC}\")")
    print(f"   J2000.0 TT (JD {J2000_TT_JD:.1f}) Mean Reference:      {IAE_LAHIRI_J2000_MEAN_DEG:.8f} deg")
    print(f"   Engine Calculated J2000.0 Mean:               {calculated_j2000_mean:.8f} deg (residual {iae_j2000_mean_residual_arcsec:.6f}\" <= {IAE_J2000_MEAN_TOLERANCE_ARCSEC}\", {iae_calc_ms:.2f} ms)")
    print(f"   1989-01-01 00:00 UTC Unverified Candidate:    {UNVERIFIED_1989_01_01_CANDIDATE_DEG:.8f} deg vs Engine {calculated_1989_mean:.8f} deg (discrepancy {unverified_1989_discrepancy_arcsec:.4f}\" -> HELD_UNVERIFIED_PRIMARY_BOOK_PAGE)")
    print(f"   IAE Gate: {iae_status}")

    public_claim = (
        "RDG Ephemeris reproduces NASA JPL DE440/Horizons and IAE 1989 p. 556 (1956-03-21.0 TT) within the measured truth floor; ties reference accuracy."
        if overall_pass
        else "FAILED: Reference tolerance exceeded; public agreement claim rejected."
    )

    # Construct verifiable output
    result = {
        "benchmark_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": overall_status,
        "evaluation_mode": "LIVE_ENGINE_AGAINST_COMMITTED_HORIZONS_TRUTH_AND_EXTERNAL_IAE_CONSTANTS",
        "standards_evaluated": [
            "NASA JPL Horizons (DE441/DE440 Astrometric Ephemeris, 300 epochs x 7 physical bodies = 2,100 live evaluations)",
            "Calendar Reform Committee Report (CSIR India 1955, p. 262) & Indian Astronomical Ephemeris (IAE 1989, p. 556: 1956-03-21 00:00 TT = 23 deg 15' 00.658\" true IAU1980 / 23 deg 14' 44.019\" mean)",
            "Transported J2000.0 TT (JD 2451545.0) Mean Lahiri Reference (23.85709235 deg)",
        ],
        "governing_policy": "Ties reference accuracy within measured truth floor; never claims to beat",
        "nasa_jpl_horizons": {
            "evaluation_method": "Live Engine.load(kernels='extended').positions_tt(jd_tt) evaluated at all 300 manifest epochs",
            "live_evaluation_duration_ms": round(live_eval_ms, 3),
            "total_samples": total_samples,
            "overall_median_separation_arcsec": overall_median,
            "overall_p95_separation_arcsec": overall_p95,
            "overall_max_separation_arcsec": overall_max,
            "max_drift_from_committed_baseline_arcsec": max_drift_from_committed_ours_arcsec,
            "tolerances_arcsec": {
                "median": HORIZONS_MEDIAN_TOLERANCE_ARCSEC,
                "p95": HORIZONS_P95_TOLERANCE_ARCSEC,
                "max": HORIZONS_MAX_TOLERANCE_ARCSEC,
            },
            "by_body": body_summary,
            "status": horizons_status,
        },
        "iae_lahiri_anchor": {
            "epoch_1956_jd_tt": LAHIRI_REFERENCE_TT_JD,
            "csir_1955_iae_1989_p556_true_iau1980_deg": IAE_LAHIRI_1956_TRUE_IAU1980_DEG,
            "iae_1989_p556_mean_reference_deg": IAE_LAHIRI_1956_MEAN_DEG,
            "iae_1989_p556_true_iau2006_reference_deg": IAE_LAHIRI_1956_TRUE_IAU2006_DEG,
            "calculated_1956_true_deg": calculated_1956_true,
            "calculated_1956_mean_deg": calculated_1956_mean,
            "mean_1956_residual_arcsec": iae_1956_mean_residual_arcsec,
            "true_1956_iau2006_residual_arcsec": iae_1956_true_iau2006_residual_arcsec,
            "true_1956_cross_nutation_residual_arcsec": iae_1956_cross_nutation_residual_arcsec,
            "epoch_j2000_jd_tt": J2000_TT_JD,
            "j2000_mean_reference_deg": IAE_LAHIRI_J2000_MEAN_DEG,
            "calculated_j2000_mean_deg": calculated_j2000_mean,
            "j2000_mean_residual_arcsec": iae_j2000_mean_residual_arcsec,
            "tolerances_arcsec": {
                "mean_1956": IAE_1956_MEAN_TOLERANCE_ARCSEC,
                "true_1956_iau2006": IAE_1956_TRUE_IAU2006_TOLERANCE_ARCSEC,
                "true_1956_cross_nutation": IAE_1956_CROSS_NUTATION_TOLERANCE_ARCSEC,
                "j2000_mean": IAE_J2000_MEAN_TOLERANCE_ARCSEC,
            },
            "unverified_1989_01_01_tabular_candidate": {
                "epoch_1989_jd_utc": 2447527.5,
                "candidate_constant_deg": UNVERIFIED_1989_01_01_CANDIDATE_DEG,
                "calculated_1989_mean_deg": calculated_1989_mean,
                "discrepancy_arcsec": unverified_1989_discrepancy_arcsec,
                "status": "HELD_UNVERIFIED_PRIMARY_BOOK_PAGE",
                "note": (
                    "Preserved per Round 2 review: IAE 1989 p. 556 defines the 1956-03-21.0 TT anchor "
                    "(23 deg 15' 00.658\" true IAU1980 / 23 deg 14' 44.019\" mean). The 1989-01-01 "
                    "23 deg 42' 37\" string lacks a verified primary-book page readback and is explicitly "
                    "HELD and excluded from certified agreement claims."
                ),
            },
            "status": iae_status,
        },
        "public_claim": public_claim,
    }

    print("\n" + "=" * 80)
    print(f"BENCHMARK OUTCOME: {overall_status}")
    print(f"Horizons Live Agreement: Overall Median {overall_median:.6f}\", P95 {overall_p95:.6f}\", Max {overall_max:.6f}\" ({horizons_status})")
    print(f"IAE External Agreement:  1956 Mean Residual {iae_1956_mean_residual_arcsec:.6f}\", 1956 True (IAU2006) Residual {iae_1956_true_iau2006_residual_arcsec:.6f}\", J2000 Mean Residual {iae_j2000_mean_residual_arcsec:.6f}\" ({iae_status})")
    print(f"Public Claim:            {public_claim}")
    print("=" * 80)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(result, indent=2) + "\n")
        print(f"\nBenchmark receipt saved to: {output_path}")

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=Path("evidence/horizons-iae-benchmark.json"), help="Output JSON path")
    args = parser.parse_args()
    result = run_benchmark(args.out)
    if result.get("status") != "PASS":
        sys.exit(1)


if __name__ == "__main__":
    main()
