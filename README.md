# RDG-Ephemeris (`ephemeris-oss`)

An independently built, permissively licensed (`Apache-2.0`) planetary ephemeris and classical Indian astronomy (Jyotish) engine designed for real Jyotish applications with **40 years of lived traditional Jyotish practice** (in tribute to **Raj Dulari Gupta  -  RDG**) and modern clean-room software engineering. Derived directly from NASA JPL DE440/DE441 Chebyshev polynomials, IAU 2006/2000A precession-nutation, Vondrák-2011 long-term precession, and primary astronomical and Jyotish treatises, every calculation carries explicit conventions, transparent accuracy and limitation disclosures, and a deterministic SHA-256 cryptographic receipt.

- **Technical White Paper & 9,074-Month Full-Span DE440 Benchmark:** [`docs/RDG-EPHEMERIS-WHITEPAPER-AND-BENCHMARKS.md`](docs/RDG-EPHEMERIS-WHITEPAPER-AND-BENCHMARKS.md)
- **28-Chapter Human-Readable Classical Ephemeris & Pt. Maheshji's Jyotish Academy Manual Calculation Compendium:** [`docs/HUMAN-READABLE-EPHEMERIS-AND-JYOTISH-ACADEMY-MANUAL.md`](docs/HUMAN-READABLE-EPHEMERIS-AND-JYOTISH-ACADEMY-MANUAL.md)
- **AI Agent, MCP Server, CLI & REST Plugin Integration Guide:** [`docs/AI-MCP-AND-PLUGIN-INTEGRATION-GUIDE.md`](docs/AI-MCP-AND-PLUGIN-INTEGRATION-GUIDE.md)
- **Jyotish Capabilities & Lineage Conventions:** [`docs/JYOTISH-CAPABILITIES-AND-CONVENTIONS.md`](docs/JYOTISH-CAPABILITIES-AND-CONVENTIONS.md)
- **Scientific Limitations, Precision Regimes & Honest Roadmap:** [`docs/ROADMAP-AND-LIMITATIONS.md`](docs/ROADMAP-AND-LIMITATIONS.md)
- **Trademark Reservation (`RDG™` / `Raj Dulari Gupta™`) & Commercial Boundary:** [`docs/TRADEMARK-AND-COMMERCIAL-BOUNDARY.md`](docs/TRADEMARK-AND-COMMERCIAL-BOUNDARY.md)
- **Clean-Room Provenance & Dependency Clearance:** [`docs/PROVENANCE-CLEARANCE.md`](docs/PROVENANCE-CLEARANCE.md)
- **Internal AI Role-Based Domain Analysis Report:** [`docs/EXPERT-TESTER-COHORT-REPORT.md`](docs/EXPERT-TESTER-COHORT-REPORT.md)

---

## Why RDG-Ephemeris Exists

1. **Permissive Commercial & API Freedom (`Apache-2.0`) With Explicit Trademark & Open-Core Boundaries**:
   Legacy C ephemeris distributions are dual-licensed under copyleft (`GPL v2+ / AGPL v3`) or commercial developer contracts that impose specific conditions on proprietary SaaS, mobile apps, and commercial API businesses. `ephemeris-oss` is published under the permissive **Apache-2.0** license with automated clean-room provenance verification, allowing developers and researchers to build commercial software and APIs without copyleft source-disclosure obligations while **The Million Dollar AI Studio Ltd.** retains copyright in its code, reserves the **`RDG™` (`Raj Dulari Gupta™`)** and **`Jyotish Studio™`** trademarks (`Apache-2.0 Section 6`), and offers proprietary applications, hosted managed APIs, and commercial support on top.
2. **Designed for Complete Jyotish Applications, Not Just Planetary Longitudes**:
   Covers explicit time scales (`UTC`, `UT1`, `TT`, `TDB`), 21 named Ayanamsha realizations (with primary citations and historical ambiguity disclosures), 8 house systems (with explicit polar/circumpolar handling), both Mean (Meeus Eq. 47.7) and True/Osculating ($\mathbf{k} \times (\mathbf{r} \times \mathbf{v})$) Lunar Nodes (`Rahu`/`Ketu`), 23 Divisional Vargas (`D1..D144`), 8 Dasha systems (`365.2425` solar and `360.0` *Savana* year options), 6-fold *Shadbala*, conserved 337-bindu *Ashtakavarga*, 86 classical *Parashari* and *Tajika* Yogas, Jaimini Sutras, and sunrise-anchored regional *Drik Panchanga*.
3. **Zero-Config Embedded NASA JPL DE440 Chebyshev Span (`1550 CE` to `2306 CE`) + Multi-Millennium Coverage (`3102 BCE` to `3000 CE`)**:
   Ships with three SHA-256-pinned embedded Chebyshev polynomial kernels (`de440_wing_1550_1800.bin.zlib`, `de440_compact.bin.zlib`, and `de440_wing_2101_2306.bin.zlib`, ~6.68 MB compressed) covering `1550 CE` through `2306 CE` completely offline with zero external downloads required. Outside `1550..2306 CE`, `EphemerisAdapter` transitions to Vondrák-2011 long-term precession (`+/-200,000` year validity) plus analytical series across `3102 BCE` (`JD 588465.5`) through `3000 CE` (or optional NASA JPL DE441 SPK kernels covering `-13200` to `+17191`; see [`docs/ROADMAP-AND-LIMITATIONS.md`](docs/ROADMAP-AND-LIMITATIONS.md) for the exact precision envelope of each regime).
4. **Universal Integration Surfaces (Python SDK, CLI, LLM MCP Server, HTTP REST API, Rust & WebAssembly)**:
   Call it directly from Python, run it from the terminal, connect it to Claude Desktop / Cursor / AI agents via the built-in **Model Context Protocol (MCP)** server (`rdg-ephemeris-mcp`), serve it as an **OpenAPI 3.1 HTTP REST microservice** (`rdg-ephemeris-api`), or embed the **Rust / WebAssembly / Browser ES-Module SDK** (`rust/ephemeris-core` and `web/ephemeris-browser.js`).
5. **Solves Computational Problems Legacy Point-Coordinate Ephemerides Leave Unsolved**:
   Includes five deterministic, SHA-256-receipt-sealed solvers: (1) sub-second 16-Varga (`D1..D60`) cusp transition sensitivity, (2) multi-criterion Bayesian birth-time rectification (*Kunda* 81x harmonic, *Pranapada Shuddhi*, *Pancha Tattwa* 90-minute elemental cycles, and life-event Dasha triggers), (3) multi-century *Graha Yuddha* (planetary war) disc-diameter adjudication, (4) classical *Surya Siddhanta* vs modern *Drig-Ganita* epicyclic drift analysis, and (5) **Personalized Astrological Fingerprint** (`compute_personalized_astro_fingerprint`) combining 16-domain birth-clock confidence decay $\exp(-\sigma_t / \tau_{\min})$, continuous 16-Varga harmonic phase stability, continuous topocentric *Digbala*, and 8-*Kaksha* (`3°45'`) *Ashtakavarga* transit resonance.

---

## Multi-Ephemeris Capability & Licensing Matrix

The table below separates reproduced `ephemeris-oss` measurements from sourced capability and licensing attributes of legacy copyleft C ephemeris distributions (`SE 2.10.03`), `Skyfield 1.55`, and `Astropy 6.x`. Third-party engines are not executed inside this clean-room repository, so their numeric accuracy cells are marked `UNKNOWN` here. Full reproducible JSON evidence for `ephemeris-oss` is stored in [`evidence/sota-ephemeris-evaluation-matrix.json`](evidence/sota-ephemeris-evaluation-matrix.json) and [`evidence/monthly-full-span-de440-benchmark.json`](evidence/monthly-full-span-de440-benchmark.json), generated via `python tools/evaluate_sota_ephemerides.py`.

| Parameter | RDG-Ephemeris (`ephemeris-oss`) | Legacy C Ephemeris (`SE 2.10.03`) | `Skyfield 1.55` | `Astropy 6.x` |
|---|---|---|---|---|
| **Open-Source License** | **Apache-2.0** (free for commercial SaaS, apps, and research) | GPL v2+ / AGPL v3 or paid commercial license | MIT (astronomy only) | BSD-3-Clause (astronomy only) |
| **Offline Embedded NASA JPL DE440 Span** | **`1550 CE` to `2306 CE`** bundled in wheel (~6.68 MB Chebyshev polynomials, `9,074` months) | Uses external `.se1` or `.bsp` files on disk | Loads local/cached SPK files (e.g., `de421.bsp`, `de440s.bsp`, `de440.bsp`; not bundled in wheel) | Built-in approximate ephemeris default; JPL `DE440`/`DE441` uses external SPK |
| **Multi-Millennium Historical Span** | **`3102 BCE` to `3000 CE`** offline (`Vondrak-2011` + analytical) + optional `DE441` (`-13200..+17191`) | Uses multi-file `.se1` archive across centuries | Loads local/cached SPK files (e.g., `de440.bsp` / `de441.bsp`) | Built-in approximate ephemeris default; JPL `DE441` uses external SPK |
| **Reproduced Fidelity vs Full NASA JPL DE440 (`1800..2100 CE`, `12:00 TT`)** | **`<= 0.000717 arcsec` max** (`0.000019 arcsec` median across 3,612 monthly TT epochs/planet) | UNKNOWN (not executed in this clean-room repository; depends on external `.se1`/`.bsp` files) | UNKNOWN (not executed in this clean-room repository; depends on selected SPK file) | UNKNOWN (not executed in this clean-room repository; depends on selected ephemeris) |
| **Reproduced Month-by-Month Fidelity vs Full NASA JPL DE440 (`1550-01` to `2306-02`, `9,074` Months)** | **`<= 0.026041 arcsec` max** across **63,518 live body-epoch evaluations** (`0` failures; `0.011989"` in `1550..1800`, `0.026041"` in `1800..2100`, `0.013609"` in `2101..2306`) | UNKNOWN (not executed in this clean-room repository; depends on external `.se1` files) | UNKNOWN (not executed in this clean-room repository; depends on selected SPK file) | UNKNOWN (not executed in this clean-room repository; depends on selected ephemeris) |
| **Cryptographic Receipts (`SHA-256`)** | **Built-in on every result** (binds kernel SHA-256, NAIF IDs, conventions, and output) | None (mutable C arrays) | None | None |
| **Built-in LLM MCP Server (`stdio`)** | **Built-in (`rdg-ephemeris-mcp`)** with **18 tools** + AI hallucination auditor | None | None | None |
| **Built-in HTTP REST API (`OpenAPI 3.1`)** | **Built-in (`rdg-ephemeris-api`)** zero-dependency JSON server (**21 endpoints**) | None | None | None |
| **Classical Jyotish & Almanac Stack** | **25 Ayanamshas, 13 Bodies (inc. Uranus/Neptune/Pluto + NAIF 599/699 physical centers), 23 Vargas (`D1..D144`), 150-Division *Nadi Amsa* (`1,800` slices), 10 Conditional *BPHS* Nakshatra Dashas + 108-Pada *Kalachakra* + 5-Level *Prana* Chronometer, 3-Ring *Sudarshana Chakra*, 8 *Vishesha Lagnas*, 11 *Upagrahas*, 9 *Prashna Sphutas*, 86 Classical & *Tajika* Yogas, 36 *Tajika Sahams*, *Shadbala*, 337-Bindu *Ashtakavarga*, *Jaimini*, *Ayurdaya*, 30-Star *Yogatara* Catalog, 28-Chapter Human Manual Compendium, SVG** | Coordinates, ayanamsa, houses, and basic phenomena only | None | None |
| **Frontier Astrodynamics & Inverse Solvers** | **12 built-in solvers**: WGS84 Topocentric/Relativistic Astrometry & Varga Flip Auditor, Synodic Retrograde Phase-Space Loop & Triple-Pass Solver, Solar/Lunar Eclipse Local Obscuration & Natal *Grahan* Scanner, Inverse Sky-to-Date Time-Machine (`3102 BCE..3000 CE`), Triple-Lock Life-Event Convergence, *Krantisamya Mahapata* Root Solver, 30-Star *Yogatara Bheda*, Sub-Second Varga Cusp Solver, Bayesian Rectification, *Graha Yuddha* Scanner, *Surya Siddhanta* Drift Analyzer, Golden *Muhurta* Electional Optimizer | None | None | None |
| **Rust & Browser WebAssembly SDK** | **Included** (`rust/ephemeris-core` + `web/ephemeris-browser.js`) | C source requiring Emscripten port and AGPL compliance | Python only | Python/C only |

---

## Installation & Quick Start

Requires Python 3.11 or later. Runtime dependencies are `numpy`, `pyerfa`, `jplephem`, and `tzdata`, each under its own permissive license.

```bash
# Install directly from a local checkout or built wheel
pip install .

# Or build a standalone wheel and install it
python -m build
pip install dist/ephemeris_oss-*.whl
```

The embedded Chebyshev DE440 kernels (`1550 CE` to `2306 CE`) work immediately offline with zero extra downloads. If you also want the full 114 MB NASA NAIF `de440.bsp` or 3.3 GB `de441.bsp` in your local cache, run:

```bash
ephemeris-oss kernels fetch --verify
```

---

## Every Way to Use RDG-Ephemeris

### 1. Python SDK (`EphemerisAdapter` and `Engine`)

Compute planetary positions, houses, and a complete chart bundle anywhere from `3102 BCE` (`JD 588465.5`) through `2300 CE` and `3000 CE`:

```python
from ephemeris_oss import Engine, EphemerisAdapter

# 1. Explicit Terrestrial Time (TT) scientific interface with SHA-256 receipt (zero-config embedded 1550-2306 CE Chebyshev kernels)
with Engine.load(kernels="extended", eop=None) as engine:
    result = engine.positions_tt(2451545.0, bodies=("sun", "moon", "mars", "jupiter", "saturn"))
    print("Moon Tropical Lon (deg):", result.value["moon"]["longitude_deg"])
    print("Receipt SHA-256:", result.receipt_sha256)

# 2. Full Jyotish & Multi-Millennium Adapter (3102 BCE Kali Yuga to 2300 CE / 3000 CE)
adapter = EphemerisAdapter()
for label, jd_ut in [
    ("3102 BCE Kali Yuga", 588465.5),
    ("1600 CE Early DE440", 2305447.5),
    ("2026 CE Modern DE440", 2461139.0),
    ("2300 CE Future DE440", 2561117.5),
]:
    bundle = adapter.compute_complete_kundali_bundle(
        jd_ut,
        latitude_deg=28.6139,
        longitude_deg=77.2090,
        ayanamsa="lahiri",
        true_node=False,  # Set true_node=True for True/Osculating Rahu & Ketu (default is Mean Node, Meeus Eq. 47.7)
        include_svg=False,
    )
    print(label, "Sun Sidereal:", round(bundle.positions["sun"].longitude_deg, 4), "Receipt:", bundle.bundle_receipt_sha256[:16])
```

### 2. Command-Line Interface (`ephemeris-oss` / `rdg-ephemeris`)

```bash
# Compute sidereal planetary positions and houses as JSON
ephemeris-oss chart --at 2026-10-06T12:00:00Z --lat 28.6139 --lon 77.2090 --ayanamsa lahiri --compact --json

# Compute a complete Jyotish chart analysis (Vargas, Dashas, Yogas, Shadbala, Ashtakavarga)
ephemeris-oss jyotish --at 2026-10-06T12:00:00Z --lat 28.6139 --lon 77.2090 --ayanamsa lahiri --compact

# Emit a compact (<3 KB) SHA-256-sealed AI Fact Sheet for LLM prompts
ephemeris-oss fact-sheet --at 2026-10-06T12:00:00Z --lat 28.6139 --lon 77.2090 --compact

# Render publication-grade North Indian, South Indian, East Indian, or Circular Wheel SVG charts
ephemeris-oss svg --at 2026-10-06T12:00:00Z --lat 28.6139 --lon 77.2090 --style north_indian --theme obsidian --compact --out chart.svg

# Solve sub-second D1-D60 varga cusp margins, Bayesian birth-time rectification, Surya Siddhanta drift, and personalized fingerprint
ephemeris-oss impossible --at 2026-10-06T12:00:00Z --lat 28.6139 --lon 77.2090

# Compute the Personalized Astrological Fingerprint (16-domain clock confidence decay, 16-Varga phase stability, Digbala, 8-Kaksha transit resonance)
ephemeris-oss fingerprint --at 2026-10-06T12:00:00Z --lat 28.6139 --lon 77.2090 --uncertainty-sec 60

# Generate the Human-Readable Classical Ephemeris & Pt. Maheshji's Jyotish Academy Manual Calculation Compendium
ephemeris-oss human-ephemeris --year 2026 --month 11 --format markdown --out docs/HUMAN-READABLE-EPHEMERIS-AND-JYOTISH-ACADEMY-MANUAL.md
```

### 3. Model Context Protocol (MCP) Server for LLMs (`rdg-ephemeris-mcp`)

Language models hallucinate planetary degrees, retrograde stations, and divisional chart placements when asked to compute astronomy in weights. `ephemeris-oss` includes a built-in **MCP JSON-RPC 2.0 `stdio` server** exposing 9 deterministic tools:

- `compute_planetary_positions` (`3102 BCE` to `3000 CE`)
- `compute_complete_kundali` (`D1..D60` Vargas, Dashas, Shadbala, Ashtakavarga, Yogas)
- `compute_panchanga` (Sunrise-anchored regional Drik Panchanga, Tithi, Nakshatra, Yoga, Karana, Muhurta)
- `rectify_birth_time_and_varga_cusps` (Sub-second 16-Varga cusp margins + Kunda 81x / Pranapada / Pancha Tattwa birth-time rectification)
- `scan_planetary_wars_and_stations` (Exact-second *Graha Yuddha* planetary wars, retrograde stations, and combustion)
- `compare_surya_siddhanta_vs_de440` (Classical *Surya Siddhanta* epicyclic positions vs modern NASA JPL DE440)
- `compute_personalized_astro_fingerprint` (16-domain birth-clock confidence decay $\exp(-\sigma_t / \tau_{\min})$, 16-Varga harmonic phase stability, continuous topocentric *Digbala*, and 8-*Kaksha* *Ashtakavarga* transit resonance)
- `compile_verified_ai_fact_sheet` (`<3 KB` token-disciplined JSON fact sheet for LLM prompts)
- `verify_ai_astrology_text` (Audits LLM-generated prose against deterministic chart placements to catch hallucinations)

Add this block to your `claude_desktop_config.json`, Cursor MCP settings, or any MCP client configuration:

```json
{
  "mcpServers": {
    "rdg-ephemeris": {
      "command": "rdg-ephemeris-mcp",
      "args": []
    }
  }
}
```

Inspect all tool schemas from the command line:

```bash
rdg-ephemeris-mcp --dump-tools
```

### 4. HTTP REST JSON API Server with OpenAPI 3.1 (`rdg-ephemeris-api`)

Start a zero-dependency threaded HTTP REST API server for web applications, mobile apps, or microservices:

```bash
rdg-ephemeris-api --host 127.0.0.1 --port 8765
# Or via the main CLI:
ephemeris-oss serve --host 127.0.0.1 --port 8765
```

Available endpoints:
- `GET  /health` (Engine status, embedded DE440 Chebyshev span, and endpoint directory)
- `GET  /openapi.json` (Full OpenAPI 3.1.0 specification)
- `GET  /v1/tools` (JSON schemas for all calculation tools)
- `POST /v1/positions` (Planetary positions across `3102 BCE` to `3000 CE`)
- `POST /v1/kundali` (Complete Kundali bundle with `D1..D60`, Dashas, Shadbala, Ashtakavarga, and Yogas)
- `POST /v1/panchanga` (Regional sunrise-anchored Drik Panchanga)
- `POST /v1/rectify` (Sub-second 16-Varga cusp transition solver and Bayesian birth-time rectification)
- `POST /v1/phenomena` (Multi-century *Graha Yuddha* planetary wars, retrograde stations, and combustion windows)
- `POST /v1/siddhanta-diff` (*Surya Siddhanta* vs modern NASA JPL DE440 differential analysis)
- `POST /v1/fingerprint` (Personalized Astrological Fingerprint: 16-domain clock confidence decay, 16-Varga phase stability, topocentric Digbala, and 8-Kaksha transit resonance)
- `POST /v1/fact-sheet` (`<3 KB` SHA-256-sealed AI Fact Sheet)
- `POST /v1/verify-text` (Deterministic hallucination audit on AI-generated text)

Example request:

```bash
curl -X POST http://127.0.0.1:8765/v1/positions \
  -H "Content-Type: application/json" \
  -d '{"iso_utc": "2026-10-06T12:00:00Z", "ayanamsa": "lahiri"}'
```

### 5. Solving Previously Unsolved Astrological & Astronomical Problems (`impossible_astrology`)

```python
from ephemeris_oss import (
    analyze_siddhanta_vs_jpl_de440_drift,
    compute_personalized_astro_fingerprint,
    rectify_birth_time_bayesian,
    scan_multi_century_rare_phenomena,
    solve_subsecond_shodashvarga_cusp_transitions,
)

# 1. Exact seconds to previous/next sign boundary across all 16 Shodashvarga charts (D1..D60)
cusps = solve_subsecond_shodashvarga_cusp_transitions(2461139.0, latitude_deg=28.6139, longitude_deg=77.2090)
print("Most sensitive Varga:", cusps.most_sensitive_varga, "Margin (sec):", cusps.minimum_ascendant_cusp_margin_seconds)

# 2. Multi-criterion classical birth-time rectification (Kunda 81x, Pranapada, Pancha Tattwa, Life Events)
rect = rectify_birth_time_bayesian(2461139.0, latitude_deg=28.6139, longitude_deg=77.2090, window_minutes=15.0)
print("Rectified offset (sec):", rect.offset_seconds, "Best score:", rect.best_candidate.total_score)

# 3. Exact-second Graha Yuddha (planetary wars), retrograde stations, and combustion windows
phen = scan_multi_century_rare_phenomena(2461041.5, 2461222.5)
print("Planetary wars:", phen.graha_yuddha_count, "Retrograde stations:", phen.retrograde_station_count)

# 4. Classical Surya Siddhanta (3102 BCE epicycles) vs modern NASA JPL DE440 differential drift
drift = analyze_siddhanta_vs_jpl_de440_drift(2461139.0)
print("Ahargana days:", drift.ahargana_days, "Mean abs delta (deg):", drift.mean_abs_delta_deg)

# 5. Personalized Astrological Fingerprint (16-domain clock confidence decay, 16-Varga phase stability, Digbala, 8-Kaksha transit resonance)
fp = compute_personalized_astro_fingerprint(2461139.0, latitude_deg=28.6139, longitude_deg=77.2090, birth_time_uncertainty_seconds=60.0)
print("Clock confidence:", fp.overall_clock_confidence_score, "Transit resonance:", fp.overall_personal_transit_resonance_score)
```

### 6. Native Rust Core and Browser WebAssembly / ES-Module SDK

The repository includes an isomorphic Rust core (`rust/ephemeris-core`) and zero-dependency browser ES module (`web/ephemeris-browser.js` + `web/ephemeris-browser.d.ts`) implementing 3D Clenshaw Chebyshev recurrence and NASA JPL DAF/SPK Type 2 and Type 3 binary record readers (`ephemeris_oss.rust_bridge.read_spk_state` and `readSpkState`). See [`docs/design/spk-reader.md`](docs/design/spk-reader.md) and [`docs/ARCHITECTURE-AND-MATHEMATICAL-REFERENCE.md`](docs/ARCHITECTURE-AND-MATHEMATICAL-REFERENCE.md).

---

## Measured TT Interface & Reproducible Accuracy

```python
from ephemeris_oss import Engine

# kernels="extended" loads the embedded 1550..2306 CE DE440 Chebyshev kernels offline;
# use kernels="auto" when full de440.bsp has been provisioned via `ephemeris-oss kernels fetch --verify`.
with Engine.load(kernels="extended", eop=None) as engine:
    result = engine.positions_tt(2451545.0, bodies=("sun", "moon"))
    print(result.value["moon"]["longitude_deg"])
    print(result.receipt_sha256)
```

`positions_tt()` uses an explicit Terrestrial Time instant. It returns apparent geocentric true-ecliptic-of-date longitude and latitude for the seven classical physical grahas. It does not infer UTC, UT1, civil time or an Earth-orientation model. Rahu/Ketu are derived definitions through the node interface, rather than physical JPL targets.

The TT receipt binds the normalized body list, explicit NAIF targets, TT instant, kernel hash and returned numeric result. Repeated identical inputs produce the same receipt; a changed request or result changes its hash.

The existing `positions(datetime, ...)` interface accepts UTC only in its declared 1960..2026 window. Houses, topocentric coordinates and rise/set also need verified Earth-orientation data or an explicitly supplied model. Missing data fail explicitly. Unsupported/undefined geometry is reported with a reason, not silently replaced by another system.

### Accuracy Against NASA JPL DE440 and Independent Horizons DE441

[The measured accuracy table](docs/ACCURACY.md) covers 3,612 monthly TT instants over 1800..2100 per physical graha on DE440 and 300 independent Horizons instants per graha. It lists median, P95, worst sampled error and worst date in arcseconds. Mars, Jupiter and Saturn use compact-kernel system barycentres. Node rows are definition-derived. Horizons' responses identify DE441.

| Physical Graha | NAIF ID | DE440 Median Error (arcsec) | DE440 Worst Error (arcsec) | Horizons DE441 Median (arcsec) | Horizons DE441 P95 (arcsec) | Horizons DE441 Worst (arcsec) |
|---|---:|---:|---:|---:|---:|---:|
| Sun centre | 10 | `1.93862718e-05` | `0.000108337531` | `1.5601669e-06` | `2.99024095e-06` | `3.80815838e-06` |
| Moon centre | 301 | `9.85119698e-05` | `0.000716859608` | `0.00243318773` | `0.0172649702` | `0.0253509189` |
| Mercury centre | 199 | `1.93394101e-05` | `0.000107906669` | `1.73181857e-06` | `3.58725987e-06` | `5.19406063e-06` |
| Venus centre | 299 | `1.9265741e-05` | `0.00010745473` | `1.61171841e-06` | `3.01558294e-06` | `5.10202485e-06` |
| Mars system barycentre | 4 | `1.94618337e-05` | `0.000108352879` | `1.40373266e-06` | `2.52963415e-06` | `3.22078937e-06` |
| Jupiter system barycentre | 5 | `1.936898e-05` | `0.000108498989` | `1.38976159e-06` | `2.14319505e-06` | `2.55158769e-06` |
| Saturn system barycentre | 6 | `1.95472182e-05` | `0.000108927907` | `1.39243358e-06` | `2.16523355e-06` | `2.71751497e-06` |

The original node rows remain as legacy evidence. The mean-node policy now matches Meeus equation 47.7; its new Decimal reference replay and exact source binding sit beside the unchanged legacy records in the accuracy study.

The corrected sample set passes the stated 0.02 arcsecond P95 and 0.1 arcsecond maximum position limits. Across every single calendar month of the extended embedded Chebyshev span (`1550-01` through `2306-02` = `9,074` consecutive months × `7` physical bodies = `63,518` live body-epoch evaluations in [`evidence/monthly-full-span-de440-benchmark.json`](evidence/monthly-full-span-de440-benchmark.json)), worst positional difference against full 114 MB `de440.bsp` is `0.026041 arcsec` with `0` failures (`0.011989 arcsec` in `1550..1800 CE`, `0.026041 arcsec` in `1800..2100 CE`, and `0.013609 arcsec` in `2101..2306 CE`, using `mean_equinox=True` with explicit `jd_tdb` prior to `1600 CE` where IAU 2000A nutation is bounded). Note that [`docs/ACCURACY.md`](docs/ACCURACY.md) reports full `de440.bsp` vs Horizons `DE441` (`Moon worst 0.0253509189 arcsec`), whereas [`evidence/horizons-iae-benchmark.json`](evidence/horizons-iae-benchmark.json) reports live embedded Chebyshev vs Horizons `DE441` (`Moon worst 0.036858 arcsec`, `0.000233 arcsec` median, `0.009849 arcsec` P95 across 2,100 rows). Outside `1550..2306 CE`, unless an external NASA JPL `de441.bsp` SPK file is provisioned, `EphemerisAdapter` uses Vondrák-2011 precession with an analytical planetary/lunar fallback (see [`docs/ROADMAP-AND-LIMITATIONS.md`](docs/ROADMAP-AND-LIMITATIONS.md) for the three precision regimes, Mars/Jupiter/Saturn `NAIF 4/5/6` system-barycentre offsets, and deep-antiquity $\Delta T$ uncertainty). This is sampled component validation, not a claim of perfect physical prediction, full production readiness, continuous coverage proof or superiority to another engine. The package includes the Horizons-compatible opaque-solar-photosphere convention established by the preserved occulted-Mercury diagnostic.

---

## Reproducible Scoped Benchmark

```bash
ephemeris-oss bench --kernel /path/to/de440.bsp --samples 32 --rounds 2 > benchmark.json
```

The workload compares seven separate public TT calls with one seven-body call at distinct fixed epochs. It warms the engine, interleaves AB/BA, reverses the order in alternate rounds and records an A/A control. It checks output equivalence at a declared numerical tolerance and reports raw milliseconds, median, P95, kernel/source hashes, Python and platform. A noisy A/A control is labelled NOISY_CONTROL, never silently treated as a qualified comparison.

This is a reproducible researcher workload, not a measurement of business value, real human hours, cost savings, a full chart, an HTTP service or another engine. The benchmark JSON explicitly records those limits.

A retained local run on Windows and Python 3.11 used 32 distinct epochs and two rounds. These are warm TT workload timings, not saved human hours.

| Round | Seven calls median / P95 ms | One batch median / P95 ms | A/A median ratio |
|---|---|---|---|
| 1 | 5.9635 / 7.6404 | 3.2652 / 5.9134 | 0.987681 |
| 2 | 5.6203 / 10.4830 | 3.1937 / 6.8014 | 0.995893 |

Both A/A controls qualified within the declared 0.9 to 1.1 ratio band. The [raw measurement](docs/researcher-benchmark.json) binds the runtime source and kernel hashes. The comparison does not qualify complete-chart performance.

---

## Distribution Boundaries, Governance & Contributing

The wheel carries engine code, embedded Chebyshev DE440 data (`1550..2306 CE`), and licence notices. It excludes bulk raw `.bsp` kernels, local databases, and environment files. The build gate tests clean wheels and planted prohibited files before accepting a wheel. The source tree is scanned for copyleft-source markers and internal identifiers.

- **License & Copyright**: [`LICENSE`](LICENSE) contains Apache-2.0; [`NOTICE`](NOTICE) identifies **The Million Dollar AI Studio Ltd.** (which retains copyright in its original code) and third-party dependencies. NASA/JPL data use and separately installed libraries do not imply endorsement of this package by those organisations.
- **Trademarks & Commercial Boundary (`RDG™` / `Raj Dulari Gupta™`)**: Under Apache-2.0 Section 6, the trademarks **`RDG™`**, **`Raj Dulari Gupta™`**, **`RDG-Ephemeris™`**, **`Jyotish Studio™`**, **`Jyotish Gurukul™`**, and **`The AGI Studio™`** are reserved by **The Million Dollar AI Studio Ltd.** See [`docs/TRADEMARK-AND-COMMERCIAL-BOUNDARY.md`](docs/TRADEMARK-AND-COMMERCIAL-BOUNDARY.md) for permitted attribution and the boundary between this free open-source core and our proprietary applications, managed cloud APIs, and commercial support.
- **Limitations, Precision Regimes & Honest Roadmap**: See [`docs/ROADMAP-AND-LIMITATIONS.md`](docs/ROADMAP-AND-LIMITATIONS.md) and [`docs/JYOTISH-CAPABILITIES-AND-CONVENTIONS.md`](docs/JYOTISH-CAPABILITIES-AND-CONVENTIONS.md).
- **Contributing & Clean-Room Protocol**: See [`CONTRIBUTING.md`](CONTRIBUTING.md) for Developer Certificate of Origin (`git commit -s`), clean-room primary-source citation rules, and verification gates.
- **Code of Conduct**: [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) adopts Contributor Covenant v2.1.
- **Security Policy**: [`SECURITY.md`](SECURITY.md) covers SHA-256 kernel verification and private vulnerability reporting.
