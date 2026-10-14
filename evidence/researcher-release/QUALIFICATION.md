# Ephemeris researcher release candidate

ROLE: BUILDER. Status: AUTHOR-PROOF, independent review pending.

The public wheel and source archive now have an explicit boundary. Both carry
Apache-2.0 license notices and contain zero findings under the archive private
identifier/data scanner. The existing clean-room JPL/ERFA calculation engine
is reused; no scientific threshold or production manifest changed.

## Verification

- Python 3.11 declared `python -m pytest -q`: 172 passed, 0 failed,
  4 optional DE441 skips, 2 expected ERFA warnings.
- Python 3.11 and 3.13 public suite plus Apache benchmark tests: each
  235 passed, 0 failed, 4 optional DE441 skips, 2 ERFA warnings.
- Installed source archive, shipped suite from unpacked archive: 171 passed,
  0 failed, 4 optional skips, 2 warnings. The staging-only archive-inspector
  test is deliberately excluded together with its non-shipped inspector.
- Wheel install into a fresh Python 3.13 environment: PASS. The source archive
  was then installed into that environment, and isolated import, real public TT
  calls and repeat receipt equality passed. Imports resolve to site-packages.
- `python -m build`: wheel and source archive built. Names, bytes, hashes and
  zero-findings content results are in archive-scan.json. Tested archives are
  retained under archives/.
- Internal-identifier and provenance checkers: self-tests passed, source scans
  0 findings and 0 stale provenance exceptions.
- Archive checker: clean/private/data controls run twice; disabling the private
  identifier detector makes its test fail; restored control passes.
- Researcher benchmark: real DE440, 32 distinct TT epochs, 2 rounds, scalar
  versus batched calls agree. Both A/A controls qualified. Raw durations,
  kernel/runtime source hashes and scope are in benchmark.json and the public
  docs/researcher-benchmark.json. Business savings are NOT_MEASURED.

## Corrections and limits

The first CLI test failed on unsupported benchmark arguments, then passed after
implementation. First expanded tests found stale benchmark adapter contracts:
mean-node coefficients had not followed the already-merged Meeus definition,
and a hashed EOP filename was not loaded by the adapter's auto-cache assumption.
The adapters now consume the existing definitions and explicit input. Legacy
rows and numerical ceilings are retained.

An exploratory run that collected the separate AGPL comparator in the Apache
environment was INVALID_SETUP: 41 absent-swisseph failures, 235 passes and
4 skips. Its own environment is named in bench/comparators/swiss/README.md.
This is retained in python311-expanded.log; no comparator dependency was added
to the public package. The qualified expanded command explicitly enumerates
only the Apache benchmark tests. A Windows wildcard sent literally to the
wheel checker and an initial archive containing its staging inspector were
also corrected; raw outputs remain retained.

DE441 completeness, independent numerical reproduction, complete-chart/R10
performance, public Git-history export, package-index publication and production
switching remain unqualified or unperformed. The public distribution scan does
not clear the private staging repository or its history for public export.
No scientific performance gate has been relaxed and no release was published.
