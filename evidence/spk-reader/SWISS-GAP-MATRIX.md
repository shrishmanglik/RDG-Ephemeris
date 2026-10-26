# Clean-room capability gap matrix

Inventory date: 2026-10-26. Existing main: 2bc89be35dac39c38f0ec189acc83a1a4918b369.
This is a source-grounded inventory, not a declaration that every listed
calculation is independently qualified. HAVE means an existing callable
implementation; PARTIAL means a known coverage, convention or proof gap.

The dispatch's named specification/worktree were absent. The recovered master
plan is the estate's 2026-10-25 march-2027-offline-super-apps-and-mds-mass-production
specification, section 9.2. Product integration belongs to Astro-AI-Studio; this
engine belongs to ephemeris-oss-staging. The other active engine worktree owns
the compatibility adapter. This branch does not touch either of those surfaces.

| Requested capability | Existing implementation | State and remaining work |
|---|---|---|
| DE440/DE441 kernel identity and selection | `kernels.py`, `engine/kernel_registry.py` | HAVE pinned hashes, separate parts and fail-closed registry. Data availability and epoch coverage must be verified for each actual calculation. |
| Native binary Chebyshev reader | Python `jplephem` integration; new `rust/ephemeris-core/src/spk.rs` | Rust Type 2/3 reader and analytic velocity added in this branch; actual SDK/numerical controls in `tests/test_spk_reader.py`. |
| 13,200 BCE to 17,191 CE | DE441 metadata/registry; TT API | PARTIAL. JPL publishes this DE441 data span; that does not extend UTC, EOP, ayanamsa, precession or every astrology model to those dates. Full-range data qualification remains separate. |
| Embedded 3000 BCE..3000 CE pack and historical time | `compact_kernel.py`, `engine/civil_time.py`, `engine/earth_orientation.py` | PARTIAL. Existing compact data is not the requested deep-time pack. The historical Delta-T implementation explicitly uses Espenak/Meeus over -1999..3000, not the requested Stephenson-Morrison-Hohenkerk spline. Modern UTC policy and historical UT1/TT are distinct inputs. |
| Topocentric parallax | `engine/apparent.py`, `engine/numerical_provider.py` | HAVE caller-supplied observer/EOP models; broad held-out qualification remains required. |
| Atmospheric refraction | `engine/events.py` optical atmosphere and ERFA model | HAVE explicit atmosphere inputs; precision depends on actual conditions. Not a universal milliarcsecond guarantee. |
| 27+ independent ayanamsa conventions | `engine/conventions.py`, `engine/stellar_anchors.py` | PARTIAL. Seven canonical definitions, with aliases, are present. Aliases are not additional models. Additional independently sourced definitions and domain/epoch qualification are needed; fixed-epoch validity is currently 1600..2400 TT. |
| Mean and osculating true lunar nodes | `engine/conventions.py` | HAVE explicit definition-derived nodes. Osculating-node and alternate mean-node conventions are not interchangeable. |
| Lunar apogee/perigee | No public implementation located in `src/ephemeris_oss` | MISSING scoped mean/osculating/true definitions and reference fixtures. Do not infer an apsis merely from node support. |
| Planetary phenomena | `engine/phenomena.py` | HAVE callable event solvers; inspect each configured provider and inherited approximation before a precision claim. |
| Solar/lunar eclipses and local circumstances | `engine/eclipses.py` | HAVE Besselian/contact/visibility interfaces and tests. New full-range contact accuracy and uncertainty study still required. |
| Six-fold Shadbala | `jyotish/shadbala.py` | PARTIAL. Existing implementation includes a documented Seeghra Kendra approximation. Presence does not establish full classical-method parity. |
| Ashtakavarga | `jyotish/ashtakavarga.py` | HAVE tables and conservation tests. Classical-source/convention qualification remains a separate claim. |
| Upagrahas | `jyotish_transit/prashna.py` | HAVE solar and Kalavela routines. Named alternatives, sunrise policy and all eleven conventions need explicit comparison fixtures. |
| Jaimini Karakas/Arudhas | `jyotish/dasha.py`, `jyotish_jaimini/sutras.py` and public API | HAVE existing convention-based rules. Not all schools are one formula; school-specific gold fixtures are required. |
| Jaimini Chara Dasha | `jyotish/dasha.py:compute_chara_dasha`, exported by `jyotish/__init__.py` | HAVE a callable Chara timeline. School-specific direction, duration and sub-period qualification remains separate; other dasha names are not evidence of parity. |
| Tajika Varshaphal | `jyotish_advanced/varshphal.py` | HAVE annual-return, Muntha, Tajika aspects/yogas, strength and dasha/saham routines. Annual-return clock/EOP and method qualification remain separate. |
| KP | `jyotish_advanced/kp.py`, Rust/browser sub-lord operations | HAVE existing routines and tests. KP ayanamsa realization and boundary conventions must travel with results. |
| Rust + WASM | `rust/ephemeris-core`, `rust_bridge.py` | HAVE existing math/arena engine. This branch adds optional binary reader WASM while preserving the lightweight module budget. |
| Python + TypeScript SDKs | `_api.py`, `rust_bridge.py`, `web/ephemeris-browser.js/.d.ts` | HAVE existing API; explicit geometric binary-reader SDK entry points added here. This does not make the two complete chart pipelines numerically equivalent. |
| Swiss signature compatibility | Separate active compatibility worktree | OWNED ELSEWHERE. Do not duplicate or overwrite its uncommitted adapter. |
| Less than 0.001 arcsecond | `docs/ACCURACY.md`, preserved benchmark records | NOT MET as a universal apparent-place claim. Existing Moon/Horizons P95 is 0.0172649702 arcseconds and sampled worst 0.0253509189. Same-kernel reader residuals measure a different question. |
| True physical centers | Existing accuracy table labels Mars/Jupiter/Saturn system barycentres | PARTIAL. Must provide actual center kernels/targets and matching reference reductions, never relabel barycentres. |
| Solar, Jovian and Saturnian deflection | `engine/apparent.py:apply_solar_gravitational_deflection` | PARTIAL. Solar finite-distance ERFA reduction exists; no Jovian/Saturnian extension was found in that reduction. Three-body apparent-place qualification remains required. |
| 300+ stars, all Yogataras and major asteroids | `engine/stellar_anchors.py` | PARTIAL. Two sourced astrometric anchors with proper motion/parallax/radial velocity exist. No requested complete stellar/asteroid catalogue was found in the scoped source inventory; catalogue identity, target kernels and held-out astrometry are still required. |
| Analytic second derivative and sub-millisecond station times | Rust Chebyshev recurrence, `compact_kernel.py`, `engine/phenomena.py` | PARTIAL. Analytic Cartesian first derivatives exist. The existing longitude speed/acceleration helpers use finite differences. First-derivative reader parity does not prove analytic apparent longitude acceleration or a station-time error bound. |
| SHA-256 receipts and less than 3 KB AI fact sheets | `engine/receipt.py`, `fact_sheet.py` | HAVE explicit existing contracts and tests. New primitive returns geometric state and requires caller asset verification; it does not silently become a fully receipted apparent-place calculation or prove all four product runtime adapters. |
| Million charts per second | `docs/researcher-benchmark.json` | NOT MEASURED. The retained benchmark compares seven individual Python TT calls against one batch over 32 epochs in two reversed-order rounds on Python 3.11.9. It is neither a complete-chart throughput measurement nor a native/WASM million-chart result. |
| Public open-source distribution / world-first superiority | Apache-2.0 source and private staging/release gates | NOT PROVEN. No public package/index release, universal superiority or historical first claim follows from this branch. |

Swiss comparison intake used only its [published programming documentation](https://www.astro.com/swisseph/swephprg.htm),
not implementation source. JPL format/coverage references are in
`design/spk-reader.md`. A comparative capability is accepted only after its
specific behavior, input data, convention and executable evidence are bound.

The recovered specification contains outcome targets and promotional language.
Its phrase "100% ... our own IP" does not remove the actual JPL, ERFA, NumPy,
jplephem and other dependency/data provenance obligations. Apache licensing of
this code is distinct from authorship of those inputs. No historical-first or
universal superiority statement is accepted from the specification alone.

The next deterministic sequence is: qualify the binary reader and its real data;
add explicitly defined lunar apsides; source additional distinct ayanamsa
definitions; qualify remaining classical-method and apparent-place gaps. None
of these is silently treated as complete because its name appears in a spec.
