#!/usr/bin/env python3
"""Fail if a tree names anything internal to The AGI Studio's estate or products.

The open package must not pre-empt the founder's name pick (gate 1) or leak the
estate's private machinery: product identifiers, review-harness names, order
ids, agent runtimes, local paths and personal names. ``lane`` is word-bounded
because the bare substring matches every "planet" and "plane" in an ephemeris.

``--self-test`` plants one hit per pattern plus a clean file that says
"planet", "plane" and "airlane", and exits 0 only if every hit is reported and
the clean file is not.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

PATTERNS: tuple[tuple[str, str], ...] = (
    ("vedicastro", r"vedicastro"),
    ("BAR-v1", r"BAR-v1"),
    ("BAR R", r"BAR R\d"),
    ("order E", r"order E\d"),
    ("the-last-product", r"the-last-product"),
    ("lane", r"\blane\b"),
    ("codex", r"codex"),
    ("estate path", r"C:\\AGI"),
    ("Shrish", r"Shrish"),
)
COMPILED = tuple((name, re.compile(pattern, re.IGNORECASE)) for name, pattern in PATTERNS)
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv", "node_modules", "build", "dist"}
# The checker and archive gate name their own patterns; scanning them would always fail.
SELF_NAMES = {"check_internal_ids.py", "verify_release.py"}


def scan(root: Path) -> list[str]:
    hits: list[str] = []
    files = [root] if root.is_file() else sorted(
        p for p in root.rglob("*") if p.is_file() and not SKIP_DIRS.intersection(p.relative_to(root).parts)
    )
    for file in files:
        if file.name in SELF_NAMES:
            continue
        rel = file.name if root.is_file() else file.relative_to(root).as_posix()
        for name, pattern in COMPILED:
            if pattern.search(rel):
                hits.append(f"{rel}:0: {name}: in path")
        data = file.read_bytes()
        if b"\0" in data[:8192]:
            continue
        for number, line in enumerate(data.decode("utf-8", errors="replace").splitlines(), start=1):
            for name, pattern in COMPILED:
                if pattern.search(line):
                    hits.append(f"{rel}:{number}: {name}: {line.strip()[:140]}")
    return hits


def self_test() -> int:
    planted = {
        "a.py": 'ID = "vedicastro-ephemeris"\n', "b.md": "per BAR-v1 tier\n", "c.md": "see BAR R3\n",
        "d.md": "built in order E3\n", "e.md": "the-last-product harness\n", "f.md": "the ephemeris lane owns it\n",
        "g.md": "a codex reviewer\n", "h.md": "path C:\\AGI\\ops\n", "i.md": "asked by Shrish\n",
    }
    clean = "The planet's orbital plane and the planes of planets.\n"
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for rel, body in planted.items():
            (root / rel).write_text(body, encoding="utf-8", newline="\n")
        (root / "clean.md").write_text(clean, encoding="utf-8", newline="\n")
        hits = scan(root)
    missed = [rel for rel in planted if not any(hit.startswith(f"{rel}:") for hit in hits)]
    false = [hit for hit in hits if hit.startswith("clean.md:")]
    for rel in missed:
        print(f"SELF-TEST MISSED {rel}")
    for hit in false:
        print(f"SELF-TEST FALSE POSITIVE {hit}")
    ok = not missed and not false
    print(f"check_internal_ids self-test: {'PASS' if ok else 'FAIL'} ({len(planted)} planted, {len(hits)} found)")
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.paths:
        parser.error("give at least one path, or --self-test")
    hits = [hit for path in args.paths for hit in scan(path)]
    for hit in hits:
        print(hit)
    print(f"check_internal_ids: {len(hits)} finding(s)")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
