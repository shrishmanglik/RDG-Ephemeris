"""Study: why two internal measurements of Swiss Ephemeris accuracy disagree by about 10x.

One sample, four factors measured separately:

* truth: T1 (JPL Horizons, which reports DE441) against T2 (Skyfield reading DE440);
* quantity: geometric against apparent (same instants in both modes);
* statistic: angular separation against the larger ecliptic-of-date component;
* data files: the 2014 Swiss files (DE431-based) against the 2026 files (DE441-based).

Run from the repository root with the bench virtual environment:

    python -m bench.studies.swiss_contradiction --kernel <de440.bsp> --swiss-python <venv-swiss python> \
        --ephe-bundled <dir with the 2014 sepl_18/semo_18> --ephe-current <dir with the 2026 files>

Horizons responses are fetched once through ``bench/truth/horizons.py`` and read from its manifest
afterwards, so a rerun makes no network request. Swiss runs only as subprocesses of
``bench/comparators/swiss/run_swiss.py`` in its own environment; nothing here imports it.

Writes ``bench/data/studies/swiss-contradiction-samples.jsonl`` (and its ``.sha256``) and
``bench/data/studies/swiss-contradiction-result.json`` (sorted keys, no timestamps, no paths),
and prints the table.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from decimal import Decimal
from importlib import metadata
from pathlib import Path

import numpy as np

from bench.harness import engines as E
from bench.harness import samples as S
from bench.harness import stats as T
from bench.harness.scorecard import _stream_seed, file_sha256, render
from bench.truth import horizons as H

SCHEMA = "swiss-contradiction-v1"
SEED = 20261006
N_PER_BODY = 30
MODES = ("geometric", "apparent")
# 1900-01-01 0h up to 2041-01-01 0h, half-open: inside the 2014 files' 1800-2400 coverage.
STUDY_ERA = "S1"
START, END = S._jan1(1900), S._jan1(2041)
ECHO_TOLERANCE_DAY = Decimal("0.000000001")
STATISTICS = ("separation_arcsec", "ecliptic_max_component_arcsec")
SWISS_CONFIGS = {
    "swiss-swieph-2014": ("swieph", "bundled"),
    "swiss-swieph-2026": ("swieph", "current"),
    "swiss-jpl-de440": ("jpl", None),
    "swiss-moshier": ("moshier", None),
}
REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "bench" / "data" / "studies"
SAMPLES_PATH = OUT_DIR / "swiss-contradiction-samples.jsonl"
RESULT_PATH = OUT_DIR / "swiss-contradiction-result.json"
SWISS_RUNNER = REPO / "bench" / "comparators" / "swiss" / "run_swiss.py"


def make_samples() -> list[dict[str, str]]:
    """30 instants per body, one stream per body, each instant emitted once per mode."""

    start_ns = int(Decimal(repr(START)) * S.NANODAYS)
    span_ns = int(Decimal(repr(END)) * S.NANODAYS) - start_ns
    rows = []
    for body in S.BODIES:
        offsets = S._stream(SEED, body, STUDY_ERA, "shared-instants").integers(0, span_ns, size=N_PER_BODY)
        for mode in MODES:
            for index, offset in enumerate(offsets):
                total = start_ns + int(offset)
                rows.append({
                    "id": f"{body}-{STUDY_ERA}-{mode}-{index:05d}", "body": body, "era": STUDY_ERA,
                    "mode": mode, "jd_tdb": f"{total // S.NANODAYS}.{total % S.NANODAYS:09d}",
                })
    return rows


def t1_horizons(rows: list[dict[str, str]]) -> tuple[dict, list[str], dict, dict]:
    """T1 directions by id, through the existing fetcher; stops after two consecutive errors.

    Horizons parses each TLIST value as a binary double and prints it back with 9 decimals, so
    an echo can differ from the request by one unit in the last place (1e-9 day, 86.4 us). The
    fetcher's own pairing treats that as VOID. This study accepts it, counts every such row and
    records the fetcher's ``verify`` verdict unchanged, so the deviation is visible in the result.
    """

    out, sources, failures, echo_offsets = {}, set(), 0, []
    groups: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in rows:
        groups.setdefault((row["body"], row["mode"]), []).append(row)
    for (body, mode), members in groups.items():
        for i in range(0, len(members), H.CHUNK):
            chunk = members[i:i + H.CHUNK]
            jds = [r["jd_tdb"] for r in chunk]
            url = H.build_request(H.BODY_TO_NAIF[body], jds, H.MODE_TO_VEC_CORR[mode])
            try:
                entry = H.fetch(url)
                failures = 0
            except (H.HorizonsError, OSError) as error:
                failures += 1
                print(f"Horizons error {failures} for {body} {mode}: {error}", file=sys.stderr)
                if failures >= 2:
                    raise
                entry = H.fetch(url)
            raw = (H.DEFAULT_DIR / f"{entry['sha256']}.json").read_bytes()
            parsed = sorted(H.parse(raw), key=lambda g: Decimal(g["jd_tdb_echoed"]))
            if len(parsed) != len(jds):
                raise H.VoidRun(f"{entry['sha256']}: {len(parsed)} rows for {len(jds)} epochs")
            sources.add(entry["ephemeris_source"])
            for r, got in zip(sorted(chunk, key=lambda c: Decimal(c["jd_tdb"])), parsed):
                offset = abs(Decimal(got["jd_tdb_echoed"]) - Decimal(r["jd_tdb"]))
                if offset > ECHO_TOLERANCE_DAY:
                    raise H.VoidRun(f"{entry['sha256']}: echo {got['jd_tdb_echoed']} != requested {r['jd_tdb']}")
                if offset:
                    echo_offsets.append(r["id"])
                out[r["id"]] = E._unit((got["x"], got["y"], got["z"]))
    try:
        verified = {"status": "OK", "responses": H.verify(H.DEFAULT_DIR / "manifest.json")}
    except H.VoidRun as error:
        verified = {"status": "VOID", "reason": str(error)}
    echo = {"tolerance_day": str(ECHO_TOLERANCE_DAY), "rows_off_by_one_nanoday": len(echo_offsets),
            "ids": sorted(echo_offsets)}
    return out, sorted(sources), verified, echo


def run_swiss(config: str, swiss_python: Path, ephe: dict[str, Path], kernel: Path, tmp: Path) -> dict:
    method, files = SWISS_CONFIGS[config]
    out = tmp / f"{config}.jsonl"
    cmd = [str(swiss_python), str(SWISS_RUNNER), "--samples", str(SAMPLES_PATH), "--out", str(out),
           "--ephemeris", method]
    if files is not None:
        cmd += ["--ephe-path", str(ephe[files])]
    if method == "jpl":
        cmd += ["--ephe-path", str(kernel.parent), "--jpl-file", str(kernel)]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
    text = (proc.stdout + proc.stderr).strip()
    for path in (str(kernel), str(kernel.parent), *(str(p) for p in ephe.values()), str(tmp)):
        text = text.replace(path, "<path>").replace(path.replace("\\", "/"), "<path>")
    status = {"exit_code": proc.returncode, "output": text.splitlines()[-1] if text else ""}
    if proc.returncode != 0:
        status["status"] = "VOID"
        return {"status": status}
    status["status"] = "OK"
    vectors = {}
    for line in out.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        vectors[row["id"]] = (row["x"], row["y"], row["z"])
    return {"status": status, "vectors": vectors}


def _values(rows, truth, result, statistic):
    ids = [r["id"] for r in rows]
    a, b = np.array([truth[i] for i in ids]), np.array([result[i] for i in ids])
    if statistic == "separation_arcsec":
        return T.separations_arcsec(a, b)
    return T.ecliptic_component_diffs_arcsec(a, b, [float(r["jd_tdb"]) for r in rows])


def _formatted(summary: dict, floor: float) -> dict:
    out = {"n": summary["n"], "ci95": {}}
    for name in ("median", "p95", "max"):
        out[name] = T.tie(summary[name], floor)
        out["ci95"][name] = [T.tie(v, floor) for v in summary["ci95"][name]]
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--kernel", required=True, type=Path)
    parser.add_argument("--swiss-python", required=True, type=Path)
    parser.add_argument("--ephe-bundled", required=True, type=Path)
    parser.add_argument("--ephe-current", required=True, type=Path)
    args = parser.parse_args(argv)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = make_samples()
    S.write_samples(rows, SAMPLES_PATH)
    sample_sha = S.sample_sha256(SAMPLES_PATH)
    SAMPLES_PATH.with_suffix(".jsonl.sha256").write_bytes(
        f"{sample_sha}  {SAMPLES_PATH.name}\n".encode("ascii"))

    t1, horizons_sources, horizons_verify, horizons_echo = t1_horizons(rows)
    t2 = E.t2_skyfield(rows, args.kernel)
    results = {"ours": E.ours(rows, args.kernel)}
    statuses = {"ours": {"status": "OK"}}
    ephe = {"bundled": args.ephe_bundled, "current": args.ephe_current}
    with tempfile.TemporaryDirectory() as tmp:
        for config in SWISS_CONFIGS:
            run = run_swiss(config, args.swiss_python, ephe, args.kernel, Path(tmp))
            statuses[config] = run["status"]
            if "vectors" in run:
                results[config] = run["vectors"]

    by_mode = {m: [r for r in rows if r["mode"] == m] for m in MODES}
    floors, truth_vs_truth = {}, {}
    for mode, members in by_mode.items():
        floors[mode] = T.truth_floor({r["id"]: t1[r["id"]] for r in members},
                                     {r["id"]: t2[r["id"]] for r in members})
        truth_vs_truth[mode] = {
            stat: T.summary(_values(members, t1, t2, stat), _stream_seed(SEED, f"t1-vs-t2|{mode}|{stat}"))
            for stat in STATISTICS}
        seps = _values(members, t1, t2, "separation_arcsec")
        for body in S.BODIES:
            mask = np.array([r["body"] == body for r in members])
            truth_vs_truth[f"{mode}|{body}"] = {
                "median": float(np.median(seps[mask])),
                "p95": float(np.percentile(seps[mask], 95, method="linear")),
                "max": float(seps[mask].max())}

    table, per_body = {}, {}
    truths = {"T1": t1, "T2": t2}
    for engine, vectors in results.items():
        for truth_name, truth in truths.items():
            for mode, members in by_mode.items():
                for stat in STATISTICS:
                    key = f"{engine}|{truth_name}|{mode}|{stat}"
                    values = _values(members, truth, vectors, stat)
                    table[key] = _formatted(T.summary(values, _stream_seed(SEED, key)), floors[mode])
                    if stat == "separation_arcsec":
                        for body in S.BODIES:
                            mask = np.array([r["body"] == body for r in members])
                            per_body[f"{key}|{body}"] = {
                                "median": T.tie(float(np.median(values[mask])), floors[mode]),
                                "p95": T.tie(float(np.percentile(values[mask], 95, method="linear")), floors[mode]),
                            }

    result = {
        "schema": SCHEMA, "seed": SEED, "bootstrap_seed": SEED, "n_samples": len(rows),
        "n_per_body_per_mode": N_PER_BODY, "modes": list(MODES), "bodies": list(S.BODIES),
        "jd_tdb_range": [repr(START), repr(END)], "sample_sha256": sample_sha,
        "kernel_sha256": file_sha256(args.kernel), "skyfield_version": metadata.version("skyfield"),
        "horizons_ephemeris_source": horizons_sources, "horizons_verify": horizons_verify,
        "horizons_echo": horizons_echo,
        "swiss_data_sha256": {
            name: {p.name: file_sha256(p) for p in sorted(directory.glob("*.se1"))}
            for name, directory in ephe.items()},
        "engine_status": statuses, "truth_floor_arcsec": floors,
        "truth_vs_truth": truth_vs_truth, "table": table, "per_body_separation": per_body,
    }
    RESULT_PATH.write_bytes(render(result))
    print(table_text(result))
    print(f"result sha256 {hashlib.sha256(RESULT_PATH.read_bytes()).hexdigest()}")
    return 0


def _fmt(value) -> str:
    return "tie" if isinstance(value, dict) else f"{value:.6f}"


def table_text(result: dict) -> str:
    lines = ["| engine | truth | mode | statistic | n | median | P95 | P95 95% CI | max |",
             "|---|---|---|---|---|---|---|---|---|"]
    for key, row in result["table"].items():
        engine, truth, mode, stat = key.split("|")
        low, high = row["ci95"]["p95"]
        lines.append(f"| {engine} | {truth} | {mode} | {stat.replace('_arcsec', '')} | {row['n']} | "
                     f"{_fmt(row['median'])} | {_fmt(row['p95'])} | [{_fmt(low)}, {_fmt(high)}] | {_fmt(row['max'])} |")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
