# Swiss Ephemeris comparator (separate process, AGPL-3.0)

This directory is licensed under the GNU Affero General Public License v3 (`LICENSE`, the text distributed with
pyswisseph 2.10.3.2). It is never imported by the package or by `bench/harness`; the harness runs it as a separate
process and reads only the results file it writes.

Setup, in its own virtual environment:

    python -m venv .venv-swiss
    .venv-swiss/Scripts/python -m pip install -r requirements.txt
    .venv-swiss/Scripts/python run_swiss.py --samples <samples.jsonl> --out <results.jsonl> --ephemeris swieph --ephe-path <dir of .se1 files>

The Swiss data files are downloaded from the publisher's site, pinned by SHA-256 in `data-files.sha256`, and are
never committed to this repository.
