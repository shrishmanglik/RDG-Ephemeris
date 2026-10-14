"""Matched public TT body-batching measurements; never chart or business qualification."""
from __future__ import annotations
import hashlib
import math
import platform
import statistics
import time
from pathlib import Path

BODIES = ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn")

def source_hash():
    digest = hashlib.sha256()
    root = Path(__file__).parent
    for file in sorted(root.rglob("*.py")):
        digest.update(file.relative_to(root).as_posix().encode())
        digest.update(file.read_bytes())
    return digest.hexdigest()

def _summary(rows):
    ordered = sorted(rows)
    return {"median_ms": statistics.median(ordered), "p95_ms": ordered[math.ceil(len(ordered) * .95) - 1]}

def measure(engine, *, samples=32, rounds=2, clock=time.perf_counter_ns):
    if isinstance(samples, bool) or not isinstance(samples, int) or not 2 <= samples <= 256:
        raise ValueError("samples must be an integer in2..256")
    if isinstance(rounds, bool) or not isinstance(rounds, int) or not 2 <= rounds <= 8:
        raise ValueError("rounds must be an integer in2..8")
    epochs = [2451545.0 + index * 37.0 for index in range(samples)]
    kernel_hash = None
    def run(instant, batched):
        nonlocal kernel_hash
        start = clock()
        if batched:
            result = engine.positions_tt(instant, bodies=BODIES)
            values = result.value
        else:
            values = {}
            for body in BODIES:
                result = engine.positions_tt(instant, bodies=(body,))
                values[body] = result.value[body]
        current_hash = result.receipt["kernel_sha256"]
        if kernel_hash is not None and kernel_hash != current_hash:
            raise ValueError("kernel changed during benchmark")
        kernel_hash = current_hash
        return (clock() - start) / 1_000_000, values
    def equivalent(left, right):
        if left.keys() != right.keys(): return False
        for body in BODIES:
            if left[body].keys() != right[body].keys(): return False
            for key, value in left[body].items():
                other = right[body][key]
                if isinstance(value, (int, float)):
                    if not math.isclose(value, other, rel_tol=0, abs_tol=1e-10): return False
                elif value != other: return False
        return True
    for instant in epochs[:2]:
        run(instant, False); run(instant, True)
    measured = []
    for repeat in range(rounds):
        scalar, batched, control_left, control_right = [], [], [], []
        for index, instant in enumerate(epochs):
            order = (False, True) if (index + repeat) % 2 == 0 else (True, False)
            pair = {}
            for mode in order: pair[mode] = run(instant, mode)
            if not equivalent(pair[False][1], pair[True][1]):
                raise ValueError("scalar/batched outputs differ")
            scalar.append(pair[False][0]); batched.append(pair[True][0])
            control_left.append(run(instant, True)[0]); control_right.append(run(instant, True)[0])
        first, second = _summary(control_left), _summary(control_right)
        ratio = first["median_ms"] / second["median_ms"] if second["median_ms"] > 0 else None
        measured.append({"round": repeat + 1, "scalar": _summary(scalar), "batched": _summary(batched),
            "aa_control_ratio": ratio, "comparison_status": "QUALIFIED_CONTROL" if ratio is not None and .9 <= ratio <= 1.1 else "NOISY_CONTROL",
            "raw_ms": {"scalar": scalar, "batched": batched, "aa_first": control_left, "aa_second": control_right}})
    return {"schema": "ephemeris-researcher-benchmark-v1", "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "source_sha256": source_hash(), "kernel_sha256": kernel_hash, "samples": samples, "epochs_tt": epochs,
        "bodies": list(BODIES), "rounds": measured, "warmup_epochs": 2, "order": "interleaved AB/BA, reversed on alternate rounds",
        "output_equivalence": True, "tolerance_absolute": 1e-10, "production_qualification": False,
        "scope": "Seven physical bodies at distinct TT epochs. No UTC conversion, nodes, houses, API transport or chart-speed qualification.",
        "business_savings": "NOT_MEASURED"}
