# Seekable JPL SPK reader

Decision, 2026-10-26. Extend the existing Rust core rather than replacing the
Python engine or copying the active compatibility-shim work. Base: 2bc89be.

The input contract is `SpkKernel::open(reader: impl Read + Seek)`. The caller
retains responsibility for asset identity using the existing kernel registry.
`state(target, center, tdb_seconds)` returns geometric J2000 position in km and
velocity in km/s. Epoch is TDB seconds since J2000, not TT, UT1 or UTC. The reader
hides DAF byte order, linked summaries, one-based word addressing, segment
priority, center paths, record selection and analytic polynomial derivatives.
It reads one record at a time. Native DE441 access does not allocate the whole
kernel. The reader itself adds no dependency or network call. The optional
long-term convention layer adds the pinned permissive dependency described below.

Python exposes the opt-in `rust_bridge.read_spk_state()` with an explicit native
library path. JavaScript/TypeScript exposes `readSpkState()` after loading the
reader-enabled WebAssembly artifact. The browser copies caller-supplied bytes
into a temporary WASM allocation and releases it in `finally`; output is copied
before that allocation is freed. A multi-gigabyte DE441 browser allocation may
be refused. Neither SDK silently falls back to approximate coordinates.

`readSpkStateSeekable({size, read(offset, length)}, ...)` provides the large-file
browser path. Its asynchronous source supplies exact byte ranges; callers can
adapt a File, local range service, or permitted HTTP range endpoint. Sparse
records are passed to the same Rust parser using a framed virtual-file view.
Each call owns its cache, bounded to 512 requests and 16 MiB by default, with
caller limits allowed only downward. No WASM allocation survives an await.
Malformed, short, out-of-range, repeated-no-progress or exhausted requests fail.
The SDK never fetches an external asset or accepts its identity on the caller's
behalf. Whole-file `readSpkState` remains available for smaller supplied buffers.

The old math-only `ephemeris_core.wasm` retains its existing 64 KiB gate. The
optional `spk-reader` feature produces `ephemeris_spk.wasm`, containing the same
math plus the binary reader and allocator. Ordinary and size-optimized combined
builds exceeded the old budget; raising that budget was rejected. Keeping the
optional file separate preserves the lightweight path. Both modules execute
the same existing Clenshaw implementation, not parallel numerical engines.

Supported: IEEE little/big-endian DAF/SPK, Type 2 position polynomials with
analytic velocity, Type 3 position/velocity polynomials, J2000 frame, inclusive
segment endpoints, later-segment priority and connected center paths. Invalid
directories, cycles, missing coverage, unsupported selected frames/types and
nonfinite data fail explicitly. A selected unsupported segment cannot fall back
to an earlier one. Record allocations are capped at 65,536 double words.

This primitive does not apply light-time, relativistic apparent-place effects,
topocentric observer correction, atmospheric refraction or civil-time models.
The existing engine owns those operations. Numerical agreement with another
reader of the same kernel is not physical prediction accuracy or apparent-place
agreement with Horizons. In particular it cannot remove DE440/DE441 model
differences in the existing lunar benchmark.

Build declared inputs before testing:

```sh
rustup target add wasm32-unknown-unknown
python tools/build_rust_inputs.py
cargo test --manifest-path rust/ephemeris-core/Cargo.toml
pytest -q tests/test_spk_reader.py tests/test_rust_crate_parity.py
```

The repository CI definition runs this preparation before Python tests. Node.js
is required for actual WASM execution. The Python wheel remains pure Python:
native libraries and browser assets are optional repository builds, not bundled
platform binaries. This increment does not claim a released binary distribution.

Tests use independently written polynomial fixtures in both byte orders, actual
native file calls, actual WASM execution, malformed/unsupported controls and
the installed MIT-licensed jplephem reader as a numerical comparator. Real
kernel hashes and raw sampled errors belong in the task evidence.

Primary format references, consulted 2026-10-26:

- [NAIF DAF Required Reading](https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/daf.html)
- [NAIF SPK Required Reading, Types 2 and 3](https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/spk.html)
- [JPL DE440/DE441 coverage](https://ssd.jpl.nasa.gov/planets/eph_export.html)

Only public format/theory documentation and independently generated test data
were used; no competing implementation source was read or copied.

## Long-term convention interface decision

The existing `ayanamsa_degrees(jd_tt, convention, *,
anchor_tropical_longitude_deg=None, true=False)` remains the Python boundary.
The named catalog is extended in place. Fixed reference rays use Vondrak 2011
long-term precession across the declared DE441 JD interval. The existing lunar
node polynomial and IAU-2006-only helpers keep their independent modern bounds.
True-frame nutation also keeps its modern bound; accepting a long-term mean
convention is not authority to extrapolate that nutation series.

Stellar entries require a separately supplied date-specific longitude. A polar
entry requires the polar longitude, not the ordinary ecliptic longitude. Neither
operation fabricates a star position at a remote date. Frozen galactic planes
are geometric conventions whose ascending intersection with the mean ecliptic
is computed directly. Catalog astrometry, historical time-scale uncertainty,
precession-model error and same-kernel reader error are separate quantities.

The seven historical 499/522 entries are explicitly labelled modern realizations.
Their source calendar is Julian, years use astronomical numbering, and published
UT1 instants are converted with the versioned historical Delta-T policy. These
are documented software choices rather than author-canonical TT epochs.

The native/optional WASM long-term evaluator shares this contract and catalog
identifiers. It uses the permissive sofars implementation of the SOFA long-term
precession computations, with its complete MIT and SOFA notices retained. The
small math-only WASM budget remains unchanged. The existing approximate scalar
precession entry point is not evidence for the long-term evaluator.

Rejected: widening the old IAU 2006 polynomial's date check; treating aliases as
new conventions; inferring UTC or terrestrial rotation throughout the JPL span;
using one residual measurement to claim physical accuracy for every date.

Implemented extension contract:

- Keep the existing seven catalog entries first, then the twenty entries listed
  in the research intake. Catalog iteration defines stable v2 integer IDs;
  aliases do not receive IDs. Python is the definition home. A deterministic
  generator must emit the Rust table and browser metadata from that catalog,
  with a check mode that refuses stale generated data.
- `ephemeris_ayanamsa_v2(jd_tt, system_id, anchor_longitude_deg)` returns mean
  degrees, or NaN for unsupported IDs, dates, or missing required anchor input.
  `computeAyanamsaLongTerm(jd_tt, name, options)` calls that actual optional
  WASM export and raises on refusal. It must not substitute the old polynomial.
- A fixed ray is the date equinox expressed on the reference mean ecliptic:
  `ltp(reference_epoch) * ltp(date_epoch).transpose() * [1,0,0]`.
  Obliquity comes from the dot product of the reference long-term equator and
  ecliptic poles. Subtract its longitude from the recorded reference offset.
  Preserve Lahiri's existing IAU-1976 reference-equinox displacement explicitly.
- The optional dependency belongs behind a `long-term` feature. Native builds
  enable it; the small browser artifact disables default features. The reader
  browser artifact enables both its reader and long-term conventions. Building
  all declared inputs and checking the existing size ceiling precedes tests.
- Do not broaden the native legacy approximation's scientific claims. The v2
  export, generated catalog and actual native/browser execution are the new
  qualification target. A complete chart, civil-time input and physical stellar
  propagation have independent requirements beyond this convention operation.

The source generator, permissive dependency, v2 export, sparse reader and actual
native/browser execution are implemented. Runtime evidence, generated catalog
freshness controls and precise binary bindings are retained in the task's
qualification record. These establish the sampled mathematical and reader
contracts; they do not establish full-range physical apparent-place accuracy.

The Python TT interface accepts explicit `jd_tdb` and `mean_equinox=True` for
the long-term mean frame. Beyond 1600..2400 TT it refuses derived TDB or true
nutation. The compatibility facade uses the same policy through `calc` with
`FLG_NONUT`; modern UTC remains a separately versioned input with explicit DUT1.
Neither TT entry point invents terrestrial rotation or leap seconds for remote
dates. The convention catalog is a set of 27 mathematical definitions; stellar
and polar entries require date-specific caller anchors, and their speed output
additionally requires the corresponding caller-supplied anchor rate.
