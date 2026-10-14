## Change
Prepares the deterministic ephemeris package for individual researchers and indie builders with a reproducible public TT batching benchmark and an installed-package quickstart. The CLI now accepts explicit kernel, sample and round bounds and refuses numerical disagreement. The source archive explicitly includes its shipped test dependencies and excludes private staging tools/evidence, bulk data and comparators. The setuptools floor matches the existing SPDX metadata.

## Validation
Python 3.11 and 3.13 public suite plus Apache benchmark tests: 235 passed, 0 failed, 4 optional DE441 skips each. Declared source suite: 172 passed. Installed source archive suite: 171 passed; the staging-only inspector test is excluded with its inspector. Fresh wheel/source installs, isolated real TT calls and repeat receipts passed. Both release archives have zero private identifier/data findings. Source identifier and provenance scans passed. Archive mutation control fails when disabled. Two 32-epoch benchmark rounds qualified their A/A controls. Raw artifacts, hashes, failed setups and full commands are committed in evidence/researcher-release.

## Learnings landed
Release verification must inspect both source and wheel archives and run shipped tests from the source archive. Real-kernel test inputs use a public cache or explicit environment binding. Benchmark adapters consume the current merged definition and explicit EOP input without changing their ceilings.

## Limits and handoff
Author proof only. Four optional DE441 tests remain unrun because full kernels are absent. The optional AGPL comparator collected in the wrong environment produced an invalid setup, retained in evidence; it is outside the public distribution. Scientific superiority, complete-chart/R10 performance, business savings, private Git-history export and public publication are not claimed. Independent reviewer reproduces checks and decides release. No production engine switch, merge or deployment.
