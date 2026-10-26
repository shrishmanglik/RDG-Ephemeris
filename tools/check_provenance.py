#!/usr/bin/env python3
"""Fail on anything in a source tree that could carry copyleft provenance.

Rules (each finding prints ``path:line: RULE: text``; any finding exits 1):

* IMPORT   an ``import swisseph`` / ``from swisseph`` or any ``pyswisseph`` mention.
* DATAFILE a Swiss Ephemeris data file (``*.se1``) anywhere in the tree.
* LICENCE  a GPL or AGPL licence header or SPDX identifier.
* SOURCE   Swiss Ephemeris named as a source: ``swiss`` (any form, which covers
           ``swisseph``, ``Swiss manual`` and ``Swiss Ephemeris``), ``sweph``,
           ``swephprg``, ``aloistr``, ``astro.com/swisseph``, ``astrodienst``.

``swiss`` is matched as a bare substring on purpose. A narrower pattern
(``swiss ephemeris|swiss manual``) misses comments such as "Swiss horizon
formulation", which is exactly how a borrowed constant gets described. The
cost is that every legitimate mention must be named: the two label phrases
C8 requires ("Swiss-compatible realisation", "Swiss-compatible convention")
are stripped before matching, but a label line that also cites a Swiss
source still fails, because the rest of the line is still scanned. Any other
mention (a C3 agreement statement, say) needs an allow-list entry
``path|exact stripped line|reason`` in the file given by ``--allow``; an
entry that matches nothing fails the run, so the list cannot go stale.

``--self-test`` plants one positive per rule plus a clean control in a
temporary tree and exits 0 only if every planted positive is reported and the
control is not. A scanner that has never failed proves nothing.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

LABEL_PHRASES = re.compile(
    r"swiss-compatible (realisation|convention)|to swiss, or a complete release qualification",
    re.IGNORECASE,
)
RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("IMPORT", re.compile(r"^\s*(import|from)\s+swisseph\b|pyswisseph", re.IGNORECASE)),
    (
        "LICENCE",
        re.compile(
            r"GNU\s+(Affero\s+|Lesser\s+)?General\s+Public\s+License|SPDX-License-Identifier:[^\n]*GPL"
            r"|\b(A|L)?GPL-?v?[123](\.0)?(-only|-or-later|\+)?\b",
            re.IGNORECASE,
        ),
    ),
    ("SOURCE", re.compile(r"swiss|sweph|aloistr|astrodienst|astro\.com/swisseph", re.IGNORECASE)),
)
DATA_FILE = re.compile(r"\.se1$", re.IGNORECASE)
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".venv", "node_modules"}
SELF_NAMES = {
    "check_provenance.py",
    "check_wheel.py",
    "provenance-allow.txt",
    "test_import_graph.py",
    "test_api.py",
}
# Generated package inventories contain filenames, not implementation sources.
# Only these declared API/test paths in this exact manifest are name exceptions;
# imports, source citations, other paths and all other files remain scanned.
COMPATIBILITY_MANIFEST_PATHS = {
    "src/ephemeris_oss/swisseph_compat.py",
    "tests/test_swisseph_compat.py",
    "tests/test_swisseph_compat_contract.py",
}


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    rule: str
    text: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.rule}: {self.text}"


def load_allow(path: Path | None) -> dict[tuple[str, str], str]:
    if path is None:
        return {}
    entries: dict[tuple[str, str], str] = {}
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        parts = raw.split("|")
        if len(parts) < 3 or not parts[2].strip():
            raise SystemExit(f"{path}:{number}: allow entry needs path|line|reason")
        entries[(parts[0].strip().replace("\\", "/"), "|".join(parts[1:-1]).strip())] = parts[-1].strip()
    return entries


def scan(root: Path, allow: dict[tuple[str, str], str]) -> tuple[list[Finding], list[tuple[str, str]]]:
    findings: list[Finding] = []
    used: set[tuple[str, str]] = set()
    files = [root] if root.is_file() else sorted(
        p for p in root.rglob("*") if p.is_file() and not SKIP_DIRS.intersection(p.relative_to(root).parts)
    )
    for file in files:
        if file.name in SELF_NAMES:
            continue
        rel = file.name if root.is_file() else file.relative_to(root).as_posix()
        if DATA_FILE.search(file.name):
            findings.append(Finding(rel, 0, "DATAFILE", "Swiss Ephemeris data file"))
            continue
        data = file.read_bytes()
        if b"\0" in data[:8192]:
            continue  # binary: only the name rule applies
        text = data.decode("utf-8", errors="replace")
        for number, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            for rule, pattern in RULES:
                if (rule == "SOURCE" and rel == "ephemeris_oss.egg-info/SOURCES.txt"
                        and stripped in COMPATIBILITY_MANIFEST_PATHS):
                    continue
                subject = LABEL_PHRASES.sub("", line) if rule == "SOURCE" else line
                if not pattern.search(subject):
                    continue
                key = (rel, stripped)
                if key in allow:
                    used.add(key)
                    continue
                findings.append(Finding(rel, number, rule, stripped[:160]))
    stale = [key for key in allow if key not in used]
    return findings, stale


def run(paths: list[Path], allow_path: Path | None) -> int:
    allow = load_allow(allow_path)
    total: list[Finding] = []
    used_keys: set[tuple[str, str]] = set()
    for root in paths:
        findings, stale = scan(root, allow)
        total.extend(findings)
        used_keys.update(key for key in allow if key not in stale)
    for finding in total:
        print(finding)
    stale_all = [key for key in allow if key not in used_keys]
    for path, line in stale_all:
        print(f"{path}: STALE-ALLOW: entry matches nothing: {line[:120]}")
    print(f"check_provenance: {len(total)} finding(s), {len(stale_all)} stale allow entr(y/ies)")
    return 1 if total or stale_all else 0


def self_test() -> int:
    planted = {
        "a/imports.py": ("import swisseph as swe\n", "IMPORT"),
        "a/req.txt": ("pyswisseph==2.10.3.2\n", "IMPORT"),
        "a/header.py": ("# This program is free software under the GNU Affero General Public License\n", "LICENCE"),
        "a/spdx.py": ("# SPDX-License-Identifier: AGPL-3.0-only\n", "LICENCE"),
        "a/cite.py": ("# documented at astro.com/swisseph/swisseph.htm\n", "SOURCE"),
        "a/url.py": ("REF = 'https://github.com/aloistr/swisseph/blob/x/sweph.h'\n", "SOURCE"),
        "a/horizon.py": ("# Saemundsson / Swiss horizon formulation\n", "SOURCE"),
        "a/labelled_but_cited.py": ("# Swiss-compatible realisation, from sweph.h\n", "SOURCE"),
        "ephe/sepl_18.se1": ("x", "DATAFILE"),
        "ephemeris_oss.egg-info/SOURCES.txt": (
            "src/ephemeris_oss/swisseph_compat.py\nimport swisseph\n", "IMPORT"),
    }
    clean = "# planet and plane text; Swiss-compatible realisation of the anchor\nimport erfa\n"
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for rel, (body, _rule) in planted.items():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(body, encoding="utf-8", newline="\n")
        (root / "clean.py").write_text(clean, encoding="utf-8", newline="\n")
        findings, _ = scan(root, {})
        found = {(f.path, f.rule) for f in findings}
        missed = [(rel, rule) for rel, (_b, rule) in planted.items() if (rel, rule) not in found]
        false = [f for f in findings if f.path == "clean.py" or
                 (f.path == "ephemeris_oss.egg-info/SOURCES.txt" and f.line == 1)]
        # An allow entry silences exactly its line, and a stale one is reported.
        allow = {("a/cite.py", "# documented at astro.com/swisseph/swisseph.htm"): "test",
                 ("a/none.py", "nothing"): "stale"}
        allowed, stale = scan(root, allow)
        allow_ok = ("a/cite.py", "SOURCE") not in {(f.path, f.rule) for f in allowed} and stale == [("a/none.py", "nothing")]
    for rel, rule in missed:
        print(f"SELF-TEST MISSED {rule} in {rel}")
    for finding in false:
        print(f"SELF-TEST FALSE POSITIVE {finding}")
    if not allow_ok:
        print("SELF-TEST allow-list did not behave")
    ok = not missed and not false and allow_ok
    print(f"check_provenance self-test: {'PASS' if ok else 'FAIL'} ({len(planted)} planted, {len(findings)} found)")
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--allow", type=Path, default=None, help="path|exact stripped line|reason per line")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.paths:
        parser.error("give at least one path, or --self-test")
    return run(args.paths, args.allow)


if __name__ == "__main__":
    sys.exit(main())
