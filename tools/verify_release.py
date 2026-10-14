"""Inspect deliberately bounded wheel/source archives without executing their contents."""
from pathlib import PurePosixPath, Path
import argparse
import re
import tarfile
import zipfile

PRIVATE = re.compile(rb"vedic[ _-]*astro|the-last-product|BAR-v1|\bBAR R[0-9]|\bcodex\b|C:[\\/]AGI|\bShrish\b", re.I)
PROHIBITED = {"bench", "evidence", ".git", "node_modules", ".venv", "__pycache__"}

def inspect(path):
    issues = []
    if path.suffix == ".whl":
        with zipfile.ZipFile(path) as archive: members = [(name, archive.read(name)) for name in archive.namelist() if not name.endswith("/")]
    else:
        with tarfile.open(path, "r:gz") as archive:
            if any(member.issym() or member.islnk() for member in archive.getmembers()): issues.append("archive contains links")
            members = [(member.name, archive.extractfile(member).read()) for member in archive.getmembers() if member.isfile()]
    for name, data in members:
        parts = PurePosixPath(name).parts
        if PROHIBITED.intersection(parts) or any(part.startswith(".venv") for part in parts): issues.append(f"prohibited path: {name}")
        if name.endswith((".bsp", ".se1", ".sqlite", ".db", ".env", ".pyc")): issues.append(f"prohibited file: {name}")
        if PRIVATE.search(name.encode()) or PRIVATE.search(data): issues.append(f"private identifier: {name}")
    if not any(name.endswith("LICENSE") for name, _ in members): issues.append("license missing")
    if not any(name.endswith("NOTICE") for name, _ in members): issues.append("notice missing")
    if path.suffix != ".whl" and any("/tests/" in name for name, _ in members) and not any(name.endswith("tools/check_wheel.py") for name, _ in members): issues.append("source tests require wheel checker")
    return issues

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("archives", nargs="+", type=Path); args=parser.parse_args()
    issues=[f"{path.name}: {issue}" for path in args.archives for issue in inspect(path)]
    for issue in issues: print(issue)
    print(f"release-archive-check: files={len(args.archives)} issues={len(issues)}")
    return 1 if issues else 0
if __name__ == "__main__": raise SystemExit(main())
