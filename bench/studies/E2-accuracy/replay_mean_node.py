"""Replay the package's declared mean-node policy against Meeus eq. 47.7.

The original raw rows are read without alteration. The new file carries both
the actual new node output and the independent Decimal equation's reference.
This is a mean-node definition check, not a new physical-body qualification.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal, localcontext
from pathlib import Path

from ephemeris_oss.engine.conventions import (
    LUNAR_NODE_CONVENTIONS_VERSION,
    mean_lunar_node_longitude_degrees,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--legacy", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    original = args.legacy.read_bytes()
    legacy = json.loads(original)
    manifest_path = args.legacy.with_name("manifest.json")
    manifest_raw = manifest_path.read_bytes()
    expected = {row["id"]: row["jd_tt"] for row in json.loads(manifest_raw)["samples"]}
    observed = {row["id"]: row["jd_tt"] for row in legacy["nodes"]}
    if observed != expected or len(observed) != len(legacy["nodes"]):
        raise ValueError("node samples do not match the preserved manifest")
    rows = []
    with localcontext() as context:
        context.prec = 40
        for row in legacy["nodes"]:
            t = (Decimal(str(row["jd_tt"])) - Decimal("2451545.0")) / Decimal(36525)
            reference = float((Decimal("125.0445479") - Decimal("1934.1362891") * t
                               + Decimal("0.0020754") * t**2 + t**3 / Decimal(467441)
                               - t**4 / Decimal(60616000)) % Decimal(360)) % 360.0
            actual = mean_lunar_node_longitude_degrees(row["jd_tt"])
            rows.append({"id": row["id"], "jd_tt": row["jd_tt"],
                         "mean_rahu_ours": actual, "mean_rahu_truth": reference,
                         "mean_ketu_ours": (actual + 180.0) % 360.0,
                         "error_arcsec": abs((actual - reference + 180.0) % 360.0 - 180.0) * 3600})
    source = Path(__file__).resolve().parents[3] / "src/ephemeris_oss/engine/conventions.py"
    worst = max(row["error_arcsec"] for row in rows)
    ordered = sorted(row["error_arcsec"] for row in rows)
    middle = len(ordered) // 2
    median = (ordered[middle - 1] + ordered[middle]) / 2 if len(ordered) % 2 == 0 else ordered[middle]
    report = {"reference": "Meeus, Astronomical Algorithms, second edition, eq. 47.7; independent Decimal",
              "version": LUNAR_NODE_CONVENTIONS_VERSION,
              "legacy_sha256": hashlib.sha256(original).hexdigest(),
              "manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
              "conventions_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "scorer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "samples": len(rows), "median_arcsec": median, "max_arcsec": worst,
              "limit_arcsec": 0.001, "status": "PASS" if worst <= 0.001 else "FAIL", "rows": rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n",
                           encoding="utf-8", newline="\n")
    print(json.dumps({key: report[key] for key in ("version", "samples", "median_arcsec", "max_arcsec", "status")}))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
