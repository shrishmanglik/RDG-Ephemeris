"""Sample verified JPL kernels against jplephem; this is reader agreement only."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from importlib.metadata import version
import json
import math
from pathlib import Path
import subprocess

import numpy as np
from jplephem.spk import SPK

from ephemeris_oss.kernels import KERNELS, sha256_file
from ephemeris_oss.rust_bridge import read_spk_state


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kernels", nargs="+", type=Path)
    parser.add_argument("--library", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--wasm", type=Path, help="Also qualify the actual seekable browser SDK")
    args = parser.parse_args()
    receipt = {
        "scope": "same-kernel geometric reader agreement, not physical or apparent-place accuracy",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "jplephem_version": version("jplephem"),
        "native_sha256": sha256_file(args.library),
        "sampling": "17 evenly spaced epochs per segment, including both endpoints; not exhaustive",
        "position_tolerance_km": 2e-6,
        "velocity_tolerance_km_s": 1e-10,
        "angular_tolerance_arcsec": .001,
        "kernels": [],
        "passed": False,
    }
    wasm_input = {"kernels": []}
    try:
        for path in args.kernels:
            digest = sha256_file(path)
            matches = [spec for spec in KERNELS.values() if spec.sha256 == digest]
            if len(matches) != 1:
                raise ValueError("Kernel hash does not match exactly one declared JPL input")
            rows = []
            kernel_record = {"identifier": matches[0].identifier, "sha256": digest,
                             "bytes": path.stat().st_size, "samples": rows}
            receipt["kernels"].append(kernel_record)
            wasm_kernel = {"path": str(path.resolve()), "identifier": matches[0].identifier,
                           "sha256": digest, "bytes": path.stat().st_size, "samples": []}
            wasm_input["kernels"].append(wasm_kernel)
            with SPK.open(str(path)) as reference:
                for segment in reference.segments:
                    if segment.data_type not in (2, 3):
                        raise ValueError("Qualification requires every segment type to be supported")
                    first = (segment.start_jd - 2451545.) * 86400.
                    last = (segment.end_jd - 2451545.) * 86400.
                    for seconds in np.linspace(first, last, 17):
                        state = read_spk_state(path, segment.target, segment.center, float(seconds),
                                               library_path=args.library)
                        position, velocity_day = segment.compute_and_differentiate(2451545., float(seconds)/86400.)
                        actual = np.asarray(state[:3])
                        expected = np.asarray(position)
                        wasm_kernel["samples"].append({
                            "target": segment.target, "center": segment.center,
                            "tdb_seconds": float(seconds),
                            "expected": [float(v) for v in (*position, *(velocity_day/86400.))],
                        })
                        position_error = float(np.max(np.abs(actual-expected)))
                        velocity_error = float(np.max(np.abs(np.asarray(state[3:])-velocity_day/86400.)))
                        angular = None
                        if np.linalg.norm(expected) > 0.:
                            a = actual/np.linalg.norm(actual)
                            b = expected/np.linalg.norm(expected)
                            angular = math.degrees(math.atan2(float(np.linalg.norm(np.cross(a, b))),
                                                             float(np.dot(a, b))))*3600.
                        rows.append({"target": segment.target, "center": segment.center,
                                     "tdb_seconds": float(seconds),
                                     "jd_tdb": 2451545.+float(seconds)/86400.,
                                     "position_error_km": position_error,
                                     "velocity_error_km_s": velocity_error,
                                     "angular_residual_arcsec": angular})
                        if (not all(math.isfinite(value) for value in state)
                                or position_error > 2e-6 or velocity_error > 1e-10
                                or (angular is not None and angular >= .001)):
                            raise ValueError("Sample exceeds the declared reader agreement bounds")
            if not rows:
                raise ValueError("A kernel with no sampled segments cannot pass qualification")
        if args.wasm is not None:
            input_path = args.output.with_name(args.output.stem + "-wasm-input.json")
            wasm_output = args.output.with_name(args.output.stem + "-wasm.json")
            input_path.write_text(json.dumps(wasm_input, indent=2)+"\n", encoding="utf-8")
            subprocess.run(["node", str(Path(__file__).with_name("qualify_wasm_reader.mjs")),
                            str(input_path), str(args.wasm), str(wasm_output)], check=True)
            wasm_receipt = json.loads(wasm_output.read_text(encoding="utf-8"))
            if wasm_receipt.get("pass") is not True:
                raise ValueError("WASM reader qualification did not pass")
            receipt["wasm_qualification"] = {"file": wasm_output.name,
                                             "sha256": sha256_file(wasm_output), "passed": True}
        receipt["passed"] = True
    except Exception as error:
        receipt["error"] = str(error)
        raise
    finally:
        args.output.write_text(json.dumps(receipt, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"passed": True, "kernels": len(receipt["kernels"]),
                      "samples": sum(len(kernel["samples"]) for kernel in receipt["kernels"])}))


if __name__ == "__main__":
    main()
