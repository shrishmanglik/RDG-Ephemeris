# Extend the JPL reader and explicit long-term convention APIs

The engine can now seek JPL DAF/SPK Type 2/3 records natively and through the
actual browser WASM SDK, without copying a multi-gigabyte DE441 file into
browser memory. Python, native and optional WASM share 27 distinct convention
definitions generated from one catalog. Remote mean-frame positions accept
explicit TT/TDB with fail-closed time/frame policies and full-span calendar
arithmetic. Existing modern entry points and the small math-only WASM remain.

The adopted bounded compatibility facade repairs UT1/UTC handling, node IDs,
all three speed fields, real JPL flags, stellar-anchor rates and request/result
receipt binding. The CLI uses the actual planetary speed field for retrograde
markers. The contributor's original checkout is preserved.

## Validation

- Python 3.13 and Python 3.11: 914 passed each, no skips; two expected warnings.
- Rust: 8 unit and 11 integration tests passed.
- All 27 conventions evaluated across five epochs in native/Python/actual WASM;
  browser execution repeated twice. Invalid dates/anchors/IDs are refused.
- 714 geometric states per native/browser implementation against the same
  checksum-verified DE440 and both DE441 halves; both coverage edges included.
  Sampled position/velocity residuals were zero. Browser range requests were
  at most 1,024 bytes, with first/last repetitions per file.
- Built wheel and source archive pass bounded distribution checks; provenance,
  internal-ID, import and generated-catalog controls pass. A later exact-head
  local CI run covers all workflow jobs and includes four additional wheel
  boundary controls. Its results are the terminal check record.

## Learnings landed

- DAF comments, record timing and common-ancestor resolution have behavioral
  regressions, including a disabled-detector control.
- Native and actual WASM execution qualify the SDK; symbols alone do not.
- Shared generated catalogs reject stale bytes, and coordinate/time policies
  bind the exact returned values and flags.
- Independently authored compatibility names are distinct from comparator
  implementation content; only the exact module/RECORD path is permitted,
  while planted code/data and other metadata remain refused.

## Limits and Track R handoff

This is same-kernel reader and mathematical-convention qualification, not a
uniform apparent-place accuracy certificate. In particular the preserved
Moon/Horizons residual exceeds 0.001 arcsecond. True nutation, mean lunar nodes,
stellar propagation, UTC/UT1 and Earth orientation keep their separate validity
bounds. Full eclipse/rise-set/fixed-star facade parity, physical-center kernels,
extra deflectors, the deep-time compact pack, broad stellar/asteroid catalog and
complete-chart throughput are not claimed. See evidence/spk-reader/STATUS.md,
FINAL-QUALIFICATION.json and SWISS-GAP-MATRIX.md. No public release, production
cutover, merge or deployment is included; independent Track R acceptance remains
required. Retained forensic evidence includes machine paths, so the whole
repository is not cleared for public export.
