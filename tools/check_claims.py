#!/usr/bin/env python3
"""Verify that all accuracy and benchmark numbers in public docs match registered receipts and contain no hyperbole.

Rules checked:
1. Every numeric claim registered in ``docs/claims.yaml`` (sample counts, ceilings,
   the 7 physical graha rows, lunar node residuals, and researcher benchmark rounds)
   must appear verbatim in its bound target document (``docs/ACCURACY.md`` / ``README.md``).
2. Sampled Horizons P95 and worst residuals in ``docs/claims.yaml`` must satisfy
   their declared ceilings (0.02 arcsec P95, 0.1 arcsec max).
3. ``README.md`` and ``docs/`` must contain zero banned unverified hyperbole phrases:
   ``more accurate than JPL``, ``beats any ephemeris``, ``best in the world``,
   ``most accurate ephemeris``, ``US government work``, ``faster than``.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

DEFAULT_BANNED_PHRASES: tuple[str, ...] = (
    "more accurate than JPL",
    "beats any ephemeris",
    "best in the world",
    "most accurate ephemeris",
    "US government work",
    "faster than",
)

SELF_SKIP_FILES = {"check_claims.py", "claims.yaml"}
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv", "node_modules", "build", "dist"}

def load_claims_manifest(manifest_path: Path) -> dict[str, Any]:
    raw = manifest_path.read_text(encoding="utf-8")
    return json.loads(raw)

def _format_comma_int(value: int) -> str:
    return f"{value:,}"

def verify_manifest_against_docs(root: Path, manifest_path: Path | None = None) -> list[str]:
    findings: list[str] = []
    manifest_file = manifest_path or (root / "docs" / "claims.yaml")
    if not manifest_file.is_file():
        return [f"{manifest_file.as_posix()}:0: MISSING_MANIFEST: claims manifest not found"]

    try:
        manifest = load_claims_manifest(manifest_file)
    except Exception as exc:
        return [f"{manifest_file.as_posix()}:0: INVALID_MANIFEST: {exc}"]

    accuracy_path = root / "docs" / "ACCURACY.md"
    readme_path = root / "README.md"
    if not accuracy_path.is_file():
        findings.append("docs/ACCURACY.md:0: MISSING_DOC: docs/ACCURACY.md not found")
        return findings
    if not readme_path.is_file():
        findings.append("README.md:0: MISSING_DOC: README.md not found")
        return findings

    accuracy_text = accuracy_path.read_text(encoding="utf-8")
    readme_text = readme_path.read_text(encoding="utf-8")

    # 1. Verify study parameters in docs/ACCURACY.md and README.md
    params = manifest.get("study_parameters", {})
    de440_samples = int(params.get("de440_monthly_tt_samples_per_graha", 3612))
    horizons_samples = int(params.get("horizons_samples_per_graha", 300))
    horizons_rows = int(params.get("horizons_total_rows", 2100))
    p95_ceiling = float(params.get("p95_ceiling_arcsec", 0.02))
    max_ceiling = float(params.get("max_ceiling_arcsec", 0.1))
    mean_node_ceiling = float(params.get("mean_node_ceiling_arcsec", 0.001))

    for label, token in (
        ("de440_monthly_tt_samples_per_graha", _format_comma_int(de440_samples)),
        ("horizons_samples_per_graha", str(horizons_samples)),
        ("horizons_total_rows", _format_comma_int(horizons_rows)),
        ("p95_ceiling_arcsec", str(p95_ceiling)),
        ("max_ceiling_arcsec", str(max_ceiling)),
        ("mean_node_ceiling_arcsec", str(mean_node_ceiling)),
    ):
        if token not in accuracy_text and str(token).replace(",", "") not in accuracy_text:
            findings.append(
                f"docs/ACCURACY.md:0: UNVERIFIED_PARAMETER: {label}={token} missing from docs/ACCURACY.md"
            )

    # 2. Verify each of the 7 physical graha rows in docs/ACCURACY.md
    grahas = manifest.get("physical_grahas", [])
    if len(grahas) != 7:
        findings.append(
            f"docs/claims.yaml:0: GRAHA_COUNT: expected 7 physical grahas, found {len(grahas)}"
        )

    for row in grahas:
        target = str(row["target_label"])
        de440_med = str(row["de440_median_arcsec"])
        de440_worst = str(row["de440_worst_arcsec"])
        hor_med = str(row["horizons_median_arcsec"])
        hor_p95 = str(row["horizons_p95_arcsec"])
        hor_worst = str(row["horizons_worst_arcsec"])
        worst_sample = str(row["worst_horizons_sample"])

        expected_table_row = (
            f"| {target} | {de440_med} | {de440_worst} | {hor_med} | "
            f"{hor_p95} | {hor_worst} | {worst_sample} |"
        )
        if expected_table_row not in accuracy_text:
            findings.append(
                f"docs/ACCURACY.md:0: GRAHA_ROW_MISMATCH: expected exact row '{expected_table_row}'"
            )

        if float(hor_p95) > p95_ceiling:
            findings.append(
                f"docs/claims.yaml:0: CEILING_EXCEEDED: {target} Horizons P95 {hor_p95} > {p95_ceiling}"
            )
        if float(hor_worst) > max_ceiling:
            findings.append(
                f"docs/claims.yaml:0: CEILING_EXCEEDED: {target} Horizons worst {hor_worst} > {max_ceiling}"
            )

    # 3. Verify lunar node metrics in docs/ACCURACY.md
    nodes = manifest.get("lunar_nodes", {})
    for key in (
        "policy_version",
        "true_rahu_typical_arcsec",
        "true_rahu_worst_arcsec",
        "mean_rahu_median_arcsec",
        "mean_rahu_max_arcsec",
        "legacy_mean_rahu_worst_arcsec",
        "antipode_residual_arcsec",
    ):
        val = str(nodes.get(key, ""))
        if not val or val not in accuracy_text:
            findings.append(
                f"docs/ACCURACY.md:0: NODE_CLAIM_MISMATCH: {key}={val!r} missing from docs/ACCURACY.md"
            )

    if float(nodes.get("mean_rahu_max_arcsec", 1.0)) > mean_node_ceiling:
        findings.append(
            f"docs/claims.yaml:0: NODE_CEILING_EXCEEDED: mean_rahu_max_arcsec exceeds {mean_node_ceiling}"
        )

    # 4. Verify researcher benchmark claims in README.md if present in manifest
    bench = manifest.get("researcher_benchmark_claims", {})
    for round_entry in bench.get("rounds", []):
        r_num = round_entry["round"]
        s_med = round_entry["scalar_median_ms"]
        s_p95 = round_entry["scalar_p95_ms"]
        b_med = round_entry["batched_median_ms"]
        b_p95 = round_entry["batched_p95_ms"]
        ratio = round_entry["aa_ratio"]
        expected_readme_row = f"| {r_num} | {s_med} / {s_p95} | {b_med} / {b_p95} | {ratio} |"
        if expected_readme_row not in readme_text:
            findings.append(
                f"README.md:0: BENCHMARK_ROW_MISMATCH: expected '{expected_readme_row}'"
            )

    # 5. Scan README.md and docs/ for banned hyperbole phrases
    banned_phrases = tuple(manifest.get("banned_hyperbole_phrases", DEFAULT_BANNED_PHRASES))
    compiled_banned = tuple(
        (phrase, re.compile(re.escape(phrase), re.IGNORECASE)) for phrase in banned_phrases
    )

    scan_targets: list[Path] = [readme_path]
    docs_dir = root / "docs"
    if docs_dir.is_dir():
        scan_targets.extend(
            sorted(
                p
                for p in docs_dir.rglob("*")
                if p.is_file()
                and p.name not in SELF_SKIP_FILES
                and not SKIP_DIRS.intersection(p.relative_to(root).parts)
            )
        )

    for target_file in scan_targets:
        if target_file.name in SELF_SKIP_FILES:
            continue
        rel = target_file.relative_to(root).as_posix()
        data = target_file.read_bytes()
        if b"\0" in data[:8192]:
            continue
        for line_no, line in enumerate(data.decode("utf-8", errors="replace").splitlines(), start=1):
            for phrase, pattern in compiled_banned:
                if pattern.search(line):
                    findings.append(
                        f"{rel}:{line_no}: BANNED_HYPERBOLE ({phrase}): {line.strip()[:140]}"
                    )

    return findings

def self_test() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    clean_accuracy = (repo_root / "docs" / "ACCURACY.md").read_text(encoding="utf-8")
    clean_readme = (repo_root / "README.md").read_text(encoding="utf-8")
    clean_claims = (repo_root / "docs" / "claims.yaml").read_text(encoding="utf-8")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "docs").mkdir(parents=True, exist_ok=True)
        (root / "docs" / "ACCURACY.md").write_text(clean_accuracy, encoding="utf-8", newline="\n")
        (root / "README.md").write_text(clean_readme, encoding="utf-8", newline="\n")
        (root / "docs" / "claims.yaml").write_text(clean_claims, encoding="utf-8", newline="\n")

        clean_findings = verify_manifest_against_docs(root)
        if clean_findings:
            for item in clean_findings:
                print(f"SELF-TEST FALSE POSITIVE: {item}")
            print("check_claims self-test: FAIL (clean control failed)")
            return 1

        # Plant 1: mutate a numerical residual in docs/ACCURACY.md
        mutated_accuracy = clean_accuracy.replace("0.0172649702", "0.0199999999", 1)
        (root / "docs" / "ACCURACY.md").write_text(mutated_accuracy, encoding="utf-8", newline="\n")

        # Plant 2: inject banned hyperbole phrases into README.md and docs/
        mutated_readme = clean_readme + "\nThis package is more accurate than JPL and faster than legacy tools.\n"
        (root / "README.md").write_text(mutated_readme, encoding="utf-8", newline="\n")

        planted_findings = verify_manifest_against_docs(root)
        caught_mismatch = any("GRAHA_ROW_MISMATCH" in f for f in planted_findings)
        caught_hyperbole = any("BANNED_HYPERBOLE" in f for f in planted_findings)

    ok = caught_mismatch and caught_hyperbole and not clean_findings
    print(
        f"check_claims self-test: {'PASS' if ok else 'FAIL'} "
        f"(clean={len(clean_findings)}, planted_findings={len(planted_findings)})"
    )
    return 0 if ok else 1

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()

    findings = verify_manifest_against_docs(args.root.resolve(), args.manifest)
    for finding in findings:
        print(finding)
    print(f"check_claims: {len(findings)} finding(s)")
    return 1 if findings else 0

if __name__ == "__main__":
    sys.exit(main())
