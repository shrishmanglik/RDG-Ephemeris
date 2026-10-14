# ephemeris-oss

A Python engine for planetary positions from NASA JPL kernels, named
ayanamsas, houses, lunar nodes and rise/set calculations. Calculations carry
explicit conventions and reproducible receipts. The source is Apache-2.0.

This repository is private staging. The package is prepared for independent
release review; no public repository or package-index release has occurred.
Application-level production qualification remains separate from the public
TT component measurements. No complete-chart or service-speed claim is made.

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

The TT receipt binds the normalized body list, explicit NAIF targets, TT
instant, kernel hash and returned numeric result. Repeated identical inputs
produce the same receipt; a changed request or result changes its hash.

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

The original node rows remain as legacy evidence. The mean-node policy now
matches Meeus equation 47.7; its new Decimal reference replay and exact source
binding sit beside the unchanged legacy records in the accuracy study.

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

## Individual Researcher & Indie Builder Amplification

Use one deterministic interface to obtain coordinates, explicit conventions and
source-bound receipts. The engine computes the facts in Python; a language model
may explain a supplied result but must not calculate or replace its numbers.
There is no account, subscription or model API required to run the package.

### Quickstart

```bash
python -m pip install ephemeris_oss-0.2.0.dev1-py3-none-any.whl
ephemeris-oss kernels fetch --verify
```

```python
from ephemeris_oss import Engine

with Engine.load(kernels="auto", eop=None) as engine:
    result = engine.positions_tt(2451545.0, bodies=("sun", "moon"))
    print(result.value["moon"]["longitude_deg"])
    print(result.receipt_sha256)
```

The wheel above is a locally built development artifact, not a claim that it is
available on a public package index. Supply verified Earth-orientation data
when using UTC, houses or rise/set. Missing input fails rather than being
filled by an AI model. Nodes are definition-derived and documented separately.

### Reproduce a scoped benchmark

```bash
ephemeris-oss bench --kernel /path/to/de440.bsp --samples 32 --rounds 2 > benchmark.json
```

The workload compares seven separate public TT calls with one seven-body call
at distinct fixed epochs. It warms the engine, interleaves AB/BA, reverses the
order in alternate rounds and records an A/A control. It checks output
equivalence at a declared numerical tolerance and reports raw milliseconds,
median, P95, kernel/source hashes, Python and platform. A noisy A/A control is
labelled NOISY_CONTROL, never silently treated as a qualified comparison.

This is a reproducible researcher workload, not a measurement of business value,
real human hours, cost savings, a full chart, an HTTP service or another engine.
The benchmark JSON explicitly records those limits. Independent release review
still precedes public distribution.

A retained local run on Windows and Python 3.11 used 32 distinct epochs and two
rounds. These are warm TT workload timings, not saved human hours.

| Round | Seven calls median / P95 ms | One batch median / P95 ms | A/A median ratio |
|---|---|---|---|
| 1 | 5.9635 / 7.6404 | 3.2652 / 5.9134 | 0.987681 |
| 2 | 5.6203 / 10.4830 | 3.1937 / 6.8014 | 0.995893 |

Both A/A controls qualified within the declared 0.9 to 1.1 ratio band. The
[raw measurement](docs/researcher-benchmark.json) binds the runtime source and
kernel hashes. The comparison does not qualify complete-chart performance.
