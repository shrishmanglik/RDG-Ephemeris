# Isolated External-Environment SOTA Ephemeris Comparator Harness

This directory (`bench/comparators/sota_head_to_head/`) provides the distributable, isolated head-to-head benchmark runner, public-domain reference locators, and external-environment reproduction workflow behind [`evidence/real-world-sota-head-to-head-benchmarks.json`](../../../evidence/real-world-sota-head-to-head-benchmarks.json) and Section 6 of [`docs/RDG-EPHEMERIS-WHITEPAPER-AND-BENCHMARKS.md`](../../../docs/RDG-EPHEMERIS-WHITEPAPER-AND-BENCHMARKS.md).

## Clean-Room & Packaging Isolation

1. **Excluded From Runtime Distributions**: `pyproject.toml` packages only `src/ephemeris_oss`, and `MANIFEST.in` specifies `prune bench`. Nothing in `bench/` ships inside built `.whl` or `.tar.gz` (`sdist`) archives, and `tools/check_wheel.py` + `tools/verify_release.py` enforce that boundary.
2. **Zero Runtime Comparator Dependencies**: `run_sota_head_to_head.py` imports zero third-party comparator libraries at module load time. Optional third-party libraries (`skyfield`, `astropy`, `ephem`, `pyswisseph`) are loaded dynamically via `importlib.import_module` only inside an isolated external virtual environment.
3. **Explicit Upstream Archive Disclosure**: External `.se1` planetary/lunar binary files (`sepl_18.se1`, `semo_18.se1`, `seas_18.se1` for `1800..2399 CE`) are third-party copyleft upstream assets and are **not** redistributed in this Apache-2.0 repository. Their upstream public locator (`https://github.com/aloistr/swisseph/tree/master/ephe`) and exact SHA-256 digests are recorded in [`reference-locators.json`](reference-locators.json). When `--se1-dir` is omitted, `run_sota_head_to_head.py` still runs all other slots (including built-in Moshier, `Skyfield 1.55`, `Astropy 8.0.2`, `PyEphem 4.2.1`, and `RDG-Ephemeris`) and marks only the external `.se1` slot `SKIPPED_NO_EXTERNAL_SE1_ARCHIVE`.

## Files in This Directory

- [`run_sota_head_to_head.py`](run_sota_head_to_head.py): Multi-mode CLI runner (`--mode verify-locators`, `--mode rdg-only`, `--mode permissive-only`, and `--mode full`, plus `--quick-smoke`).
- [`reference-locators.json`](reference-locators.json): SHA-256-pinned manifest of committed NASA JPL Horizons reference vectors, public NASA JPL / IERS download URLs, external PyPI comparator specs, and upstream `.se1` archive digests.
- [`horizons-geodetic-vertical-vectors.json`](horizons-geodetic-vertical-vectors.json): Public-domain NASA JPL Horizons `coord@399` dual-altitude (`0 km` and `1 km`) ICRF observer vectors and IERS `finals2000A.all` EOP snapshots for Evaluation 4 (`WGS84 + IERS Polar-Motion Geodetic Houses`).
- [`requirements-external-venv.txt`](requirements-external-venv.txt): Pinned external-venv package list (`skyfield==1.55`, `astropy==8.0.2`, `ephem==4.2.1`, `pyswisseph==2.10.3.2`).

## Step 1: Verify In-Repo Reference Locators (Clean Non-Copyleft Runtime)

From any clean `ephemeris-oss` virtual environment (zero third-party comparators required):

```bash
python bench/comparators/sota_head_to_head/run_sota_head_to_head.py \
  --mode verify-locators \
  --out /tmp/rdg-verify-locators.json
```

## Step 2: Provision Public-Domain NASA JPL `de440.bsp`, IERS EOP, and Optional Rust `cdylib`

```bash
# Fetch and SHA-256-verify NASA JPL de440.bsp and IERS finals2000A.all into your local cache
ephemeris-oss kernels fetch --verify --eop

# Optional: build the native Rust zero-copy Kundali library outside the repository tree
CARGO_TARGET_DIR=/tmp/rdg-rust-target cargo build --release --manifest-path rust/ephemeris-core/Cargo.toml
```

## Step 3: Create an Isolated External Comparator Virtual Environment (Outside the Repo)

### Linux / macOS

```bash
python3 -m venv /tmp/rdg-sota-comparator-venv
/tmp/rdg-sota-comparator-venv/bin/pip install --upgrade pip
# Install the built ephemeris-oss wheel (or editable checkout) plus isolated comparators
/tmp/rdg-sota-comparator-venv/bin/pip install .
/tmp/rdg-sota-comparator-venv/bin/pip install -r bench/comparators/sota_head_to_head/requirements-external-venv.txt

# Run a fast end-to-end verification pass (~5-10s) or omit --quick-smoke for the full 4-part suite
/tmp/rdg-sota-comparator-venv/bin/python bench/comparators/sota_head_to_head/run_sota_head_to_head.py \
  --mode full \
  --rust-cdylib /tmp/rdg-rust-target/release/libephemeris_core.so \
  --out /tmp/rdg-sota-results.json
```

If you have separately downloaded `sepl_18.se1`, `semo_18.se1`, and `seas_18.se1` from the upstream public locator in `reference-locators.json` into an external folder (for example `/tmp/external-se1`), pass `--se1-dir /tmp/external-se1` to include the external `.se1` slot alongside built-in Moshier.

### Windows PowerShell

```powershell
python -m venv C:\temp\rdg-sota-comparator-venv
C:\temp\rdg-sota-comparator-venv\Scripts\pip install .
C:\temp\rdg-sota-comparator-venv\Scripts\pip install -r bench\comparators\sota_head_to_head\requirements-external-venv.txt

$env:CARGO_TARGET_DIR = "C:\temp\rdg-rust-target"
cargo build --release --manifest-path rust\ephemeris-core\Cargo.toml

C:\temp\rdg-sota-comparator-venv\Scripts\python bench\comparators\sota_head_to_head\run_sota_head_to_head.py `
  --mode full `
  --rust-cdylib C:\temp\rdg-rust-target\release\ephemeris_core.dll `
  --out C:\temp\rdg-sota-results.json
```

To run only permissively licensed comparators (`RDG-Ephemeris`, `Skyfield 1.55`, and `Astropy 8.0.2`) without installing any copyleft packages, install only `skyfield==1.55` and `astropy==8.0.2` in the external virtual environment and pass `--mode permissive-only`.
