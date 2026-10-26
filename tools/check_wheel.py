#!/usr/bin/env python3
"""Refuse comparator code/data while permitting the project's compatibility module name.

``--self-test`` builds two small wheels in a temporary directory, one clean and
one with a planted ``.se1`` file, a ``bench/`` file, a ``comparators/`` file and
a ``swisseph`` string, and exits 0 only if the clean one passes and each
planted item is reported.
"""

from __future__ import annotations

import argparse
import csv
import io
import re
import sys
import tempfile
import zipfile
from pathlib import Path

BANNED_NAMES = (
    re.compile(r"\.(se1|bsp|sqlite|sqlite3|db)$", re.I),
    re.compile(r"(^|/)\.env($|\.)", re.I),
    re.compile(r"(^|/)bench/"),
    re.compile(r"(^|/)comparators/"),
)
BANNED_TEXT = re.compile(rb"swisseph|sweph", re.I)
COMPATIBILITY_PATH = "ephemeris_oss/swisseph_compat.py"


def _scanned_content(name: str, content: bytes) -> bytes:
    # RECORD repeats installed filenames. Exempt only this exact first CSV field;
    # code inside the module and every other metadata field remain fully scanned.
    if not re.fullmatch(r"[^/]+\.dist-info/RECORD", name):
        return content
    try:
        rows = list(csv.reader(io.StringIO(content.decode("utf-8"))))
    except (UnicodeDecodeError, csv.Error):
        return content
    for row in rows:
        if row and row[0] == COMPATIBILITY_PATH:
            row[0] = "ephemeris_oss/compatibility.py"
    output = io.StringIO()
    csv.writer(output).writerows(rows)
    return output.getvalue().encode("utf-8")


def scan(wheel: Path) -> list[str]:
    problems: list[str] = []
    with zipfile.ZipFile(wheel) as archive:
        for name in archive.namelist():
            for pattern in BANNED_NAMES:
                if pattern.search(name):
                    problems.append(f"{name}: banned path ({pattern.pattern})")
            banned_name = name != COMPATIBILITY_PATH and BANNED_TEXT.search(name.encode())
            if banned_name or BANNED_TEXT.search(_scanned_content(name, archive.read(name))):
                problems.append(f"{name}: contains a swisseph/sweph string")
    return problems


def self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        clean = Path(tmp) / "clean.whl"
        dirty = Path(tmp) / "dirty.whl"
        with zipfile.ZipFile(clean, "w") as archive:
            archive.writestr("pkg/__init__.py", "PLANET = 'planet'\n")
            archive.writestr(COMPATIBILITY_PATH, "VALUE = 1\n")
            archive.writestr("pkg-0.0.dist-info/RECORD", COMPATIBILITY_PATH + ",sha256-test,10\n")
        with zipfile.ZipFile(dirty, "w") as archive:
            archive.writestr("pkg/__init__.py", "x = 1\n")
            archive.writestr("pkg/ephe/sepl_18.se1", "x")
            archive.writestr("bench/run.py", "x = 1\n")
            archive.writestr("pkg/comparators/c.py", "x = 1\n")
            archive.writestr("pkg/leak.py", "import swisseph\n")
            archive.writestr(COMPATIBILITY_PATH, "import swisseph\n")
            archive.writestr("pkg-0.0.dist-info/RECORD", "swisseph.py,sha256-test,10\n")
        clean_problems, dirty_problems = scan(clean), scan(dirty)
    expected = ("sepl_18.se1", "bench/run.py", "comparators/c.py", "leak.py",
                COMPATIBILITY_PATH, "pkg-0.0.dist-info/RECORD")
    missed = [item for item in expected if not any(item in problem for problem in dirty_problems)]
    for problem in clean_problems:
        print(f"SELF-TEST FALSE POSITIVE {problem}")
    for item in missed:
        print(f"SELF-TEST MISSED {item}")
    ok = not clean_problems and not missed
    print(f"check_wheel self-test: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("wheels", nargs="*", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.wheels:
        parser.error("give a wheel, or --self-test")
    problems = [f"{wheel.name}: {problem}" for wheel in args.wheels for problem in scan(wheel)]
    for problem in problems:
        print(problem)
    print(f"check_wheel: {len(problems)} problem(s) in {len(args.wheels)} wheel(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
