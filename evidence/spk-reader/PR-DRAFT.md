# Add a seekable JPL SPK reader with native and browser SDK access

The Rust core previously required callers to provide coefficients. This change
lets it read JPL DAF/SPK Type 2 and Type 3 data directly, return geometric J2000
positions and velocities, and resolve relative body states through common centers.
Native calls seek individual records instead of allocating an entire DE441 file.
Python and JavaScript/TypeScript expose explicit opt-in entry points. The old
math-only WASM keeps its existing size limit; the reader is an optional module.

## Validation

Pending final execution: use the terminal qualification record, not this draft,
for final commands, hashes and pass/fail counts. Earlier receipts remain dated
intermediate evidence. The actual native and WASM SDKs are executed; exported
symbol strings alone do not establish behavior. Verified DE440 and both DE441
inputs are compared with jplephem over sampled epochs including coverage edges.
This is same-kernel reader agreement, not a physical apparent-place accuracy claim.

## Learnings landed

- Comment/reserved DAF records cannot be interpreted as coefficient arrays;
  valid comment-bearing files remain supported in both byte orders.
- Selected-record MID/RADIUS must agree with INIT/INTLEN; plausible but shifted
  time normalization must fail.
- A relative state must resolve at its common ancestor even if an irrelevant
  higher edge is unsupported. A request that actually needs that edge still fails.
- Frame refusal is tested behaviorally, including disabling its detector and
  observing the regression fail before restoring the clean control.
- CI generates the native and browser inputs before executing dependent tests.

## Limits

No public release or product-provider replacement is included. The compatibility
adapter belongs to another active checkout. The capability matrix separates
existing implementations, measured results and unresolved specification targets:
additional ayanamsas, lunar apsides, the deep-time compact pack, expanded stellar
and asteroid catalogs, physical-center kernels, extra deflectors, classical-method
qualification, apparent precision and complete-chart throughput are still open.
No historical-first or universal superiority claim is made.
