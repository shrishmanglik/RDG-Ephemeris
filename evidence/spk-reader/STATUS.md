# Binary reader checkpoint

## Latest author qualification, 2026-10-26 08:22 UTC

The historical checkpoints below are superseded by this qualification, not
rewritten. The saved source now implements the long-term conventions and sparse
browser reader. Full Python 3.13 and isolated Python 3.11 runs each passed
914 tests with no skips and two expected dubious-year warnings. The later wheel
boundary change adds four focused cases (7/7 distribution cases passed); the
exact-head local CI reruns the full suite before Track R readiness is reported.
Rust passed 8 unit and 11 integration tests. Final-build.txt binds the native
binary and both real WASM artifacts. The math-only artifact remains 63,184 bytes.

Current-jpl-qualification.json and its linked -wasm.json sample 714 states in
DE440 and both split DE441 files (17 per segment, including endpoints). Both
native and actual seekable browser SDK execution passed with sampled position
and velocity residuals of zero against jplephem on those identical inputs.
The browser additionally repeated first/last cases and used individual ranges
of at most 1,024 bytes; it did not copy either multi-gigabyte DE441 file.
This is geometric same-kernel reader agreement, not apparent-place accuracy.

The 27 distinct convention operations execute through Python, the native v2
export and actual optional WASM at five epochs, including both JPL bounds.
Stale generated catalog bytes are rejected. Stellar/polar anchors and their
rates remain explicit caller inputs. True nutation and mean lunar polynomials
retain their modern bounds. Remote public TT calls require explicit TDB and
mean-equinox output; a one-second guard rejects unrelated time-scale epochs.
Full-span calendar arithmetic uses astronomical years without datetime/ERFA's
ancient-calendar floor. Actual far-date checks cover each DE441 half.

The original compatibility contribution remains preserved at its owner's
checkout. Its adopted copy now binds final values/flags/time policy into receipts,
uses UT1 by default and explicit DUT1 for UTC, reports actual JPL selection,
returns real coordinate derivatives, distinguishes true/mean nodes, and labels
sidereal reduction correctly. CLI retrograde outputs consume the actual speed
field. Independent static intake findings were repaired; that intake is not a
Track R verdict. The wheel gate now permits only this independently authored
module's exact filename and matching RECORD filename field, while still refusing
comparator imports/text/data, including planted controls inside that module.
Both built release archives pass their separate bounded inspections.

No universal <0.001 arcsecond apparent-place claim, complete-chart throughput,
full signature parity, physical-center expansion, broad star/asteroid catalog,
new deep-time compact pack, product integration or public release is established.
The unchanged Moon/Horizons baseline remains in the accuracy document and the
broader master targets remain explicitly open in SWISS-GAP-MATRIX.md. Track R
must independently review this bounded increment. Public whole-repository export
is still blocked by retained machine paths in forensic evidence; no secret was
reported. Only private branch/PR review in the already-private repository is in
scope. No merge/deploy/provider action has occurred.

Owner: Codex chat 01a17381-8eb1-73e0-86ce-b39e8680dbfc, Track A ephemeris-oss.
Date: 2026-10-26. Base: 2bc89be35dac39c38f0ec189acc83a1a4918b369.
Workspace: C:/AGI/worktrees/ephemeris-oss-staging/chebyshev-reader-20261026.
Branch: codex/chebyshev-reader-20261026. No commit/push/PR at this checkpoint.

The originally named specification and Astro worktree were absent. The recovered
master specification is the estate's
command-centre/war-room/chief-of-staff/specs/2026-10-25-march-2027-offline-super-apps-and-mds-mass-production/SPEC.md,
section 9.2. The gap matrix was reconciled against existing source before
continuing. This is an increment of the existing engine, not a parallel engine.

Collision boundary: only this engine checkout is edited. The separate
ephemeris-gurukul-compat checkout owns the Swiss-signature adapter. Astro-AI-Studio,
Gurukul UI, pricing, sidecar, case data and media remain with their named owners.
The coordination ownership table dated 2026-10-25 section 2b was read back.

Configured model: gpt-6.1-sol, model_reasoning_effort high, read from selected
configuration fields. Requested Ultra override has no verifiable in-flight
readback in this turn. Do not claim that it took effect.

Bound: zero added spend, no paid compute or model/API inference; no Swiss source;
two failed attempts with the same signature require a changed approach. Normal
memory/admission gates apply; no priority or threshold overrides. No public
release, publishing, credentials, provider mutation or payments. A draft PR
requires green relevant checks; broader physical accuracy remains a separate gate.

Independent review identified reserved-record addressing, inconsistent record
normalization and unnecessary evaluation above a common ancestor. All three have
failing-before regressions and repaired Rust tests. Latest Rust run: 5 unit and
11 reader integration tests passed. Disabling the frame detector made its actual
regression fail; restored Rust tests passed. Review of the repairs found no
remaining concrete defect; that is draft feedback, not release approval.

Fresh native/WASM build after the common-ancestor fix is recorded in
rebuild-after-relative.txt. Math-only module remains 63,184 bytes; optional reader
82,468 bytes. Native SHA-256:
472d4aad6710c068a2bfdbe7fd569229dad6761610b12d2a59f1ef0224f6fea7.

The full Python 3.13 suite ran: 854 passed, 1 failed, 4 skipped. The failure was
provenance scanning of the internal comparison/ownership matrix in public docs.
That matrix was moved to this internal evidence folder and the public design
note now uses neutral wording. No scanner, exception list or test was weakened.
The full rerun, Python 3.11 run, package checks and exact-head CI remain pending.

Both DE441 files were downloaded with the existing streaming fetcher and verified
against the pinned hashes. jpl-reader-qualification.json records 714 sampled
same-kernel states over DE440 and both DE441 parts, including the published data
endpoints. It binds the preceding native binary f6c2ff3b..., not the final
common-ancestor repair, and must be regenerated for final qualification.
The DE440-only JSON's older hard-coded "asset absent" label is erroneous metadata;
preserved raw bytes are superseded by the verified fetch receipt and this note.
The test metadata has been corrected without rewriting its historical receipts.

Whole-repository export self-test controls passed but the scan found eight
inherited machine-path disclosures in old tracked evidence. No secret value was
printed. Public whole-repository export remains blocked; no public release is
authorized. This does not qualify or disqualify the separately bounded package.

Memory repeatedly crossed below 2,048 MiB; normal admission and physical-memory
checks are recorded separately. Unused slots were released. Cache reclamation
was executed twice when C: exceeded 88 percent and found zero eligible candidates.
No unrelated application or other owner's build was terminated.

## Resumed run 20261026-014432-backend-code-ephemeris-oss

OPEN, 2026-10-26. The former checkpoint is not task completion.
Normal 20-minute admission attempt expired; system commit then improved to
82 percent, and one new bounded waiter joined the ordinary queue. No admission
threshold, priority, other lane's lease or foreign process was overridden.

NEEDS-SEAT: restore ordinary testing capacity for this active engine task; the
lane is queued and cannot run the requested full suite without a normal slot.

New unrun behavior tests cover the CLI speed-field defect, full-range portable
SPK time coordinates, the proposed 27-convention contract, cross-SDK convention
execution, and the compatibility draft's receipt, derivative, calendar, node
and UTC/UT1 defects. None has a red/green receipt yet. No scientific implementation
was added behind those new contracts while test admission is unavailable.

The compatibility contributor's existing source, test and fixture were copied
byte-for-byte into this task so their behavior can be tested and repaired in
one coherent change. The separate contributor checkout was not edited, reset,
committed or removed. Source snapshot hashes:

- src/ephemeris_oss/swisseph_compat.py:
  c7ddeb18d65e8de5489c9a963f0715eb8c3a88e1b497b02e38c8d6d4aef4333c
- tests/test_swisseph_compat.py:
  fa88abe23b66447870c0e97796c2028d3c3887c263f0dab00928c3fa44a15024
- tests/fixtures/swisseph_compat_j2000_oracle.json:
  92703886dcc4bd2b464a685b91db2b9f3fe2f5d13354c6e3f082e766f3793068

Independent static intake found: houses use UTC as UT1; TRUE_NODE does not
resolve; output flags/values are not bound by the copied receipt; two SPEED
derivatives are fabricated zeros; compact-only routing and clamped time models
do not supply the requested long-range contract. These are repair requirements,
not a review approval. This adapter is not cleared for reuse or described as a
full drop-in replacement.

At 2026-10-26 06:38 UTC the second 20-minute normal waiter and final 5-minute
window had both expired without admission. The final window was prepared to
run the new regressions immediately on admission, after the physical-memory
floor check; it never reached pytest. The machine reached 95 percent system
commit and 782 MiB available during the wait. No new red or green test receipt
exists. The previous runtime results above remain historical, with their exact
stated scope and limits.

Stopped at the resource bound, INCOMPLETE. The reader plus all pending source,
tests and research are being committed as an explicitly unqualified local WIP
checkpoint. This is not a review-ready head, no PR has been opened, and no
merge, deployment or public release occurred. The same owner retains this task
checkout through 2026-10-29. Resume here; do not create another implementation
or change the contributor's original checkout. First obtain normal admission,
observe the new red cases, repair every defect, finish the pending convention
implementation, rebuild declared inputs and run all required checks before
requesting Track R review.

Checkpoint preparation only: Python AST parsing succeeded for the six new or
modified Python source/test files selected in the resumed run. Staged source
whitespace checking passed with evidence data excluded. A full whitespace check
had incorrectly treated verbatim Windows log line endings as source whitespace
and produced excessive output; the raw evidence bytes were preserved. Neither
syntax parsing nor whitespace checks are runtime tests or scientific proof.
