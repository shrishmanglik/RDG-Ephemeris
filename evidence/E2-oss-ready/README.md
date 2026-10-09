# E2 private open-source staging preparation

Repository visibility was read as private before mutation. No visibility,
package-index, release, account or audience mutation occurred.

Apache-2.0 is the selected source licence; NOTICE names the registered legal
entity and permissive dependencies. Unsupported "JPL-grade" marketing language
was replaced with a factual description. README documents installation,
separately fetched/verified kernels, the explicit TT API, UTC-window limits,
accuracy, data conventions and incomplete production qualification.

The package now exposes positions_tt() with reproducible receipts. It ports
the measured numerical/apparent functions, including solve-local reuse and
opaque-photosphere handling. An AST comparison of all 69 functions against
the measured Astro source found zero missing or different function bodies;
identity/version branding differs. Existing provenance labels were retained.

Red: two missing-TT-interface failures; three planted-distribution failures.
Green: five focused API/distribution tests. Provenance scan: zero findings and
zero stale allow entries; internal-ID scan: zero findings. Wheel gate self-test
passes with both clean and planted controls.

Built wheel and source distribution: version 0.2.0.dev1. Wheel gate finds zero
problems. Source distribution has 47 entries and zero prohibited kernel,
database, environment, benchmark or comparator paths. Installed-wheel smoke
loads actual pinned DE440, calculates Sun/Moon at exact TT and confirms no UTC
inference. Wheel SHA-256:
16999144c075efaaa1f81d6102c9ea6b84d6548232b64bf3ee6b0c222eeda514.

Public numerical reference rows and JPL receipts are in bench/studies/E2-accuracy
and are excluded from the wheel. No birth profiles, customer records, private
reports, credentials or bulk kernels were exported. The whole Astro export
preflight found private/sensitive source classes, so only the reviewed engine
subset and public numeric reference material were transferred.

Full package suite and independently reproduced accuracy remain pending
capacity/review. This is a prepared private package, not a public release or
production-readiness assertion. R10 and the complete Astro switch gate remain
unqualified.
