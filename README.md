# ephemeris-oss

A Python engine for planetary positions from NASA JPL kernels, named
ayanamsas, houses, lunar nodes and rise/set calculations. Calculations carry
explicit conventions and reproducible receipts. The source is Apache-2.0.

This repository is private staging. The package is prepared for independent
release review; no public repository or package-index release has occurred.
The Vedic Astro production switch and the full release qualification remain
pending. The 50 ms / API speed gate has not passed.

## Install and data

Requires Python 3.11 or later. Build a wheel with `python -m build`, then install
the wheel with `pip install <wheel-path>`. Runtime dependencies are NumPy,
PyERFA, jplephem and tzdata, each under its own permissive licence.

Run `ephemeris-oss kernels fetch --verify` to provision the pinned DE440 kernel
from NASA NAIF into the user cache. Kernels are verified by SHA-256 and are
downloaded separately. They are not bundled in the wheel. No subscription,
account, API credential, customer record or proprietary report is required.

## Measured TT interface

```python
from ephemeris_oss import Engine

with Engine.load(kernels="auto", eop=None) as engine:
    result = engine.positions_tt(2451545.0, bodies=("sun", "moon"))
    print(result.value["moon"]["longitude_deg"])
    print(result.receipt_sha256)
```

`positions_tt()` uses an explicit Terrestrial Time instant. It returns
apparent geocentric true-ecliptic-of-date longitude and latitude for the seven
classical physical grahas. It does not infer UTC, UT1, civil time or an
Earth-orientation model. Rahu/Ketu are derived definitions through the node
interface, rather than physical JPL targets.

The existing `positions(datetime, ...)` interface accepts UTC only in its
declared 1960..2026 window. Houses, topocentric coordinates and rise/set also
need verified Earth-orientation data or an explicitly supplied model. Missing
data fail explicitly. Unsupported/undefined geometry is reported with a
reason, not silently replaced by another system.

## Accuracy

[The measured accuracy table](docs/ACCURACY.md) covers 3,612 monthly TT instants
over 1800..2100 per physical graha on DE440 and 300 independent Horizons
instants per graha. It lists median, P95, worst sampled error and worst date in
arcseconds. Mars, Jupiter and Saturn use compact-kernel system barycentres.
Node rows are definition-derived. Horizons' responses identify DE441.

The corrected sample set passes the stated 0.02 arcsecond P95 and 0.1 arcsecond
maximum position limits. This is sampled component validation, not a claim of
perfect physical prediction, full production readiness, continuous coverage
proof or superiority to another engine. Independent reproduction is pending.
The package includes the Horizons-compatible opaque-solar-photosphere
convention established by the preserved occulted-Mercury diagnostic.

## Distribution boundaries

The wheel carries engine code and licence notices. It excludes bulk kernels,
benchmark/comparator code, local databases and environment files. The build
gate tests clean wheels and planted prohibited files before accepting a wheel.
The source tree is scanned for copyleft-source markers and internal identifiers.

`LICENSE` contains Apache-2.0; `NOTICE` identifies The Million Dollar AI Studio
Ltd. and third-party dependencies. NASA/JPL data use and separately installed
libraries do not imply endorsement of this package by those organisations.
