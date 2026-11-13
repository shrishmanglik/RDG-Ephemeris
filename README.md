# RDG-Ephemeris (`ephemeris-oss`)

An independently built, permissively licensed (`Apache-2.0`) planetary ephemeris and classical Indian astronomy (Jyotish) engine designed for real Jyotish applications with **40 years of lived traditional Jyotish practice** (in tribute to **Raj Dulari Gupta  -  RDG**) and modern clean-room software engineering. Derived directly from NASA JPL DE440/DE441 Chebyshev polynomials, IAU 2006/2000A precession-nutation, Vondrák-2011 long-term precession, and primary astronomical and Jyotish treatises, every calculation carries explicit conventions, transparent accuracy and limitation disclosures, and a deterministic SHA-256 cryptographic receipt.

- **Technical White Paper & Real-World SOTA Head-to-Head Benchmarks:** [`docs/RDG-EPHEMERIS-WHITEPAPER-AND-BENCHMARKS.md`](docs/RDG-EPHEMERIS-WHITEPAPER-AND-BENCHMARKS.md)
- **30-Chapter Human-Readable Classical Ephemeris & Pt. Maheshji's Jyotish Academy Manual Calculation Compendium:** [`docs/HUMAN-READABLE-EPHEMERIS-AND-JYOTISH-ACADEMY-MANUAL.md`](docs/HUMAN-READABLE-EPHEMERIS-AND-JYOTISH-ACADEMY-MANUAL.md)
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

## Real-World Head-to-Head SOTA Ephemeris Benchmarks & Evaluations

Evaluations 1-4 below report **retained external-environment head-to-head measurements** stored in [`evidence/real-world-sota-head-to-head-benchmarks.json`](evidence/real-world-sota-head-to-head-benchmarks.json) (canonical JSON payload digest `7ddccc06799d4f76dbe0f3dca349d33205a98bf7e05d91beb8f93b9c12ed6393`), executed on `Windows 11` (`16-core AMD64`, `Python 3.13.13`, `rustc 1.96.0`, `Node V8 v24.16.0`) in a strictly isolated external virtual environment outside this repository against the `2,100` NASA JPL Horizons `DE441` vectors in `bench/studies/E2-accuracy/` and `de440.bsp` (`sha256: a4ce9bf9b3282becc9f4b2ac3cebe03a2ae7599981aabd7265fd8482fff7c4b5`), comparing `ephemeris-oss 0.2.0.dev1` against externally installed `SE 2.10.03` (Swiss-compatible convention), `Skyfield 1.55`, `Astropy 8.0.2`, and `PyEphem 4.2.1`. By clean-room design, zero third-party copyleft packages, runner scripts, or archives are bundled in `ephemeris-oss`; clean-checkout commands (`python tools/evaluate_sota_ephemerides.py`, `ephemeris-oss bench`, `pytest`, and `cargo test`) reproduce the in-repo clean-room evaluations ([`evidence/monthly-full-span-de440-benchmark.json`](evidence/monthly-full-span-de440-benchmark.json), [`evidence/sota-ephemeris-evaluation-matrix.json`](evidence/sota-ephemeris-evaluation-matrix.json) where third-party slots remain `UNKNOWN`, [`docs/ACCURACY.md`](docs/ACCURACY.md), and [`docs/researcher-benchmark.json`](docs/researcher-benchmark.json); see [`docs/RDG-EPHEMERIS-WHITEPAPER-AND-BENCHMARKS.md`](docs/RDG-EPHEMERIS-WHITEPAPER-AND-BENCHMARKS.md) Section 7).

### Evaluation 1: Independent NASA JPL Horizons `DE441` Accuracy (`2,100` Reference Vectors, `1800..2100 CE`)

Evaluated across `300` independent timestamps x `7` physical bodies = `2,100` apparent geocentric ICRF RA/DEC reference rows (`Horizons QUANTITIES=45`, `DE441`). Each comparison engine is evaluated in its highest-precision apparent ICRF frame:

| Ephemeris Engine & Configuration | License | External Files Needed? | Median Error (arcsec) | P95 Error (arcsec) | Worst Error (arcsec) | Accuracy Advantage of RDG |
|---|---|---|---|---:|---:|---|
| **`RDG-Ephemeris 0.2.0.dev1` (`de440.bsp`)** | **Apache-2.0** | Yes (`114 MB` SPK) | **`0.000002"`** | **`0.004149"`** | **`0.025335"`** | **Reference baseline (`2 micro-arcsec` median; `0.000005"` Mercury max)** |
| **`RDG-Ephemeris 0.2.0.dev1` (Embedded `6.68 MB` Chebyshev)** | **Apache-2.0** | **No (`0` downloads)** | **`0.000229"`** | **`0.009523"`** | **`0.035737"`** | **Best zero-download accuracy (`77.3x` lower max error vs Moshier)** |
| `SE 2.10.03` (Swiss-compatible convention, External Archive) | GPL v2+ / AGPL v3 | Yes (external archive) | `0.001666"` | `0.018287"` | `0.672586"` | RDG `de440.bsp` has **`833x` lower median error** & **`26.5x` lower worst error** (`134,517x` lower on solar-occulted Mercury; see lunar note below) |
| `Skyfield 1.55` (`de440.bsp`) | MIT | Yes (`114 MB` SPK) | `0.000002"` | `0.004158"` | `0.676582"` | RDG `de440.bsp` matches median & achieves **`26.7x` lower worst error** via opaque-solar-photosphere limb clamping (`1.7505"`) |
| `Astropy 8.0.2` (`de440.bsp`, vectorized) | BSD-3-Clause | Yes (`114 MB` SPK) | `0.000002"` | `0.012284"` | `0.676577"` | RDG `de440.bsp` achieves **`3.0x` lower P95** & **`26.7x` lower worst error** (Sun max `0.000004"` vs `0.239412"`; Mercury max `0.000005"` vs `0.676577"`) |
| `SE 2.10.03` (Swiss-compatible convention, Built-in Moshier) | GPL v2+ / AGPL v3 | No (`0` downloads) | `0.068255"` | `0.870226"` | `2.761400"` | RDG Zero-Download achieves **`298.1x` lower median**, **`91.4x` lower P95**, & **`77.3x` lower worst error** (`1,659x` on Jupiter, `1,465x` on Saturn) |
| `Astropy 8.0.2` (Built-in approximate ephemeris) | BSD-3-Clause | No (`0` downloads) | `1.672544"` | `33.000830"` | `93.359855"` | RDG Zero-Download achieves **`7,303.7x` lower median** & **`2,612.4x` lower worst error** |
| `PyEphem 4.2.1` (Built-in VSOP87 / Chapront) | Lesser Copyleft | No (`0` downloads) | `0.978196"` | `32.151046"` | `131.292211"` | RDG Zero-Download achieves **`4,271.6x` lower median** & **`3,673.8x` lower worst error** |

> **Scientific Transparency Note on Solar Occultation & Lunar `DE431`/`DE440`/`DE441` Differences:** On superior-conjunction samples where Mercury passes behind the solar disc (`d < R_sun`), `SE 2.10.03`, `Skyfield 1.55`, and `Astropy 8.0.2` bend rays through the transparent point-mass interior (`~0.673"` to `0.677"` jump vs Horizons `DE441`), whereas `RDG-Ephemeris` applies Horizons' opaque-solar-photosphere grazing-limb clamp (`1.7505"`, keeping Mercury `<= 0.000005"` on `de440.bsp`). On the Moon alone (`300` samples), external-archive `SE 2.10.03` (`DE431`-derived) sits `0.002148"` median / `0.013032"` max from `DE441` vs `DE440`'s `0.002438"` median / `0.025335"` max, reflecting the known `~0.012"` inter-ephemeris lunar tidal evolution offset between JPL `DE431`, `DE440`, and `DE441`.

### Evaluation 2: 756-Year Zero-Download Out-of-the-Box Span (`1550-01` to `2306-02`, `63,518` Live Evaluations vs Full `DE440`)

Evaluated on the 15th of every consecutive calendar month from January 1550 through February 2306 (`9,074` months x `7` physical bodies = `63,518` points) with **zero external kernel files downloaded**:

| Zero-Download Engine (`pip install` Out-of-the-Box) | Bundled Footprint | Median Error vs `DE440` | P95 Error vs `DE440` | Worst Error Across 756 Years | Precision Factor of RDG |
|---|---|---:|---:|---:|---|
| **`RDG-Ephemeris` (`ephemeris-oss` Embedded Chebyshev)** | **`6.68 MB` in wheel** | **`0.000099"`** | **`0.005456"`** | **`0.026041"` (`0` failures)** | **`1.0x` (sub-`0.03"` across 8 centuries)** |
| `SE 2.10.03` (Swiss-compatible convention, Built-in Moshier) | C analytical tables | `0.070218"` | `1.130750"` | `5.279657"` | **`709.3x` lower median error** & **`202.7x` lower worst error** |
| `Astropy 8.0.2` (Built-in default ephemeris) | Approximate tables | `1.658412"` | `35.554768"` | `100.258718"` | **`16,751.6x` lower median error** & **`3,850.0x` lower worst error** |
| `PyEphem 4.2.1` (Built-in analytical series) | VSOP87 / Chapront | `21.101276"` | `81.042625"` | `471.023129"` | **`213,144.2x` lower median error** & **`18,087.8x` lower worst error** |

### Evaluation 3: 10,000-Chart Complete Vedic Kundali Throughput & Interactive API Latency

Real-world astrology and research workloads compute complete charts (`9` sidereal Grahas + `12` house cusps + `16` *Shodashvarga* `D1..D60` divisional charts + `337`-bindu *Ashtakavarga* + `120`-year `9x9` *Vimshottari Dasha*), not isolated coordinates:

| Workload & Runtime Stack | Total Time (`10,000` Charts) | Latency Per Chart | Sustained Throughput | Measured Throughput Multiplier |
|---|---:|---:|---:|---|
| **`RDG-Ephemeris` Native Rust Zero-Copy Arena (`ephemeris-core`, Full 16-Varga + 337-SAV + 9x9 Dasha Kundali)** | **`164.93 ms`** | **`0.0165 ms` (`16.5 us`)** | **`60,632.6 charts/sec`** | **`174.9x` speedup** vs Python + `SE 2.10.03` full Kundali (`3.56x` to `6.17x` speedup even vs `SE 2.10.03` computing coordinates + houses alone!) |
| **`RDG-Ephemeris` Browser V8 ES-Module (`web/ephemeris-browser.js`, Full 16-Varga + 337-SAV + 9x9 Dasha Kundali)** | **`2,253.93 ms`** | **`0.2254 ms`** | **`4,436.7 charts/sec`** | **`12.8x` speedup** right in JavaScript (`0` server calls) vs Python + `SE 2.10.03` full Kundali |
| Python + `SE 2.10.03` (Swiss-compatible convention, External Archive + Full 16-Varga + 337-SAV + 9x9 Dasha) | `28,845.65 ms` | `2.8846 ms` | `346.7 charts/sec` | `1.0x` legacy full-chart baseline |
| `SE 2.10.03` C Extension Only (Coordinates + Houses ONLY; **zero** Vargas, **zero** SAV, **zero** Dashas) | `587.06 ms` (`1,017.73 ms` Moshier) | `0.0587 ms` | `17,034.0 coords/sec` | Coordinates-only C call (`0` Jyotish domain layers, `0` cryptographic receipts) |

- **Interactive Uncached Python 7-Body Stream (`1,000` Distinct Epochs = `7,000` Body Evaluations):** `RDG-Ephemeris` Python (`Engine.positions_tt` with full `SHA-256` receipt generation on every call) completes `1,000` 7-body epochs in **`6.30 s`** (`6.30 ms/epoch` embedded Chebyshev; **`7.30 ms/epoch`** `de440.bsp`) vs **`11.14 ms/epoch` on `Skyfield 1.55`** (**`1.53x` to `1.77x` throughput advantage**) and **`51.54 ms/epoch` on scalar `Astropy 8.0.2`** (**`7.06x` to `8.19x` throughput advantage**). Note that vectorized `Astropy` over pre-batched arrays runs in `0.155 s / 300 epochs`, and unreceipted C scalar calls in `SE 2.10.03` run in `~0.04 to 0.06 ms/epoch`, whereas `RDG` Rust `ephemeris-core` delivers `0.0165 ms` per complete 16-Varga Vedic chart.

### Evaluation 4: WGS84 + IERS Polar-Motion Geodetic Houses vs Legacy House Vertical (`Horizons` Physical Vertical Oracle)

Tested against NASA JPL Horizons dual-altitude (`0 km` and `1 km`) ICRF observer vectors, legacy house routines (`SE 2.10.03`, Swiss-compatible convention) omit IERS polar motion of the physical geodetic vertical, shifting the Ascendant by `0.61"` to `8.22"` and flipping cusp-adjacent Nakshatra Padas and `D9` Navamsas (e.g. `2019-06-22 10:55 UTC`: *Magha* Pada 4 -> Pada 3, `D9` Aries -> Pisces):

| Geodetic Benchmark Site | `SE 2.10.03` Ascendant Vertical Discrepancy | `RDG-Ephemeris` WGS84 + IERS Polar-Motion Max Error | Geodetic Vertical Precision Gain |
|---|---:|---:|---|
| **New Delhi (`1975`)** | `8.223485"` | **`0.002047"`** | **`4,017.3x` lower vertical error** |
| **Toronto (`J2000`)** | `4.491520"` | **`0.001938"`** | **`2,317.6x` lower vertical error** |
| **Singapore (`2016`)** | `3.044462"` | **`0.001601"`** | **`1,901.6x` lower vertical error** |
| **New Delhi (`2026`)** | `0.605789"` | **`0.009008"`** | **`67.3x` lower vertical error** |

### Multi-Ephemeris Capability, Edge-Case & Licensing Matrix

| Parameter | RDG-Ephemeris (`ephemeris-oss`) | Legacy C Ephemeris (`SE 2.10.03`) | `Skyfield 1.55` | `Astropy 8.x` |
|---|---|---|---|---|
| **Open-Source License** | **Apache-2.0** (free for commercial SaaS, apps, and research) | GPL v2+ / AGPL v3 or paid commercial license | MIT (astronomy only) | BSD-3-Clause (astronomy only) |
| **Offline Embedded NASA JPL DE440 Span** | **`1550 CE` to `2306 CE`** bundled in wheel (~6.68 MB Chebyshev polynomials, `9,074` months, `<= 0.026041"` max) | Uses external archive or `.bsp` files on disk (`5.28"` max in built-in Moshier) | Loads local/cached SPK files (not bundled in wheel) | Built-in approximate ephemeris (`100.26"` max); `DE440` uses external SPK |
| **Multi-Millennium Historical Span** | **`3102 BCE` to `3000 CE`** offline (`Vondrak-2011` + analytical, `0` failures) + optional `DE441` (`-13200..+17191`) | Uses multi-file archive across centuries | Loads local/cached SPK files (`de440.bsp` / `de441.bsp`) | Built-in approximate ephemeris default; `DE441` uses external SPK |
| **Western Pre-Sunrise & Arctic Polar Handling** | **Preceding-sunrise solar-day anchor (`r_j <= jd_ut`, inc. cross-month Day 1) + explicit circumpolar `UNAVAILABLE` / `Undefined`** | Caller must manually wire *Savana Dina* & circumpolar guards | Astronomy rise/set events only | Astronomy coordinates only |
| **Cryptographic Receipts (`SHA-256`)** | **Built-in on every result** (binds kernel SHA-256, NAIF IDs, conventions, and output) | None (mutable C arrays) | None | None |
| **Built-in LLM MCP Server (`stdio`)** | **Built-in (`rdg-ephemeris-mcp`)** with **18 tools** + AI hallucination auditor | None | None | None |
| **Built-in HTTP REST API (`OpenAPI 3.1`)** | **Built-in (`rdg-ephemeris-api`)** zero-dependency JSON server (**21 endpoints**) | None | None | None |
| **Classical Jyotish & Almanac Stack** | **25 Ayanamshas, 13 Bodies (inc. Uranus/Neptune/Pluto + NAIF 599/699 physical centers), 23 Vargas (`D1..D144`), 150-Division *Nadi Amsa* (`1,800` slices), 10 Conditional *BPHS* Nakshatra Dashas + 108-Pada *Kalachakra* + 5-Level *Prana* Chronometer, 3-Ring *Sudarshana Chakra*, 8 *Vishesha Lagnas*, 11 *Upagrahas*, 9 *Prashna Sphutas*, 86 Classical & *Tajika* Yogas, 36 *Tajika Sahams*, *Shadbala*, 337-Bindu *Ashtakavarga*, *Jaimini*, *Ayurdaya*, 30-Star *Yogatara* Catalog, 30-Chapter Human Manual Compendium (`.md`/`.html`/`.pdf`), SVG** | Coordinates, ayanamsa, houses, and basic phenomena only | None | None |
| **Frontier Astrodynamics & Inverse Solvers** | **12 built-in solvers**: WGS84 Topocentric/Relativistic Astrometry & Varga Flip Auditor, Synodic Retrograde Phase-Space Loop & Triple-Pass Solver, Solar/Lunar Eclipse Local Obscuration & Natal *Grahan* Scanner, Inverse Sky-to-Date Time-Machine (`3102 BCE..3000 CE`), Triple-Lock Life-Event Convergence, *Krantisamya Mahapata* Root Solver, 30-Star *Yogatara Bheda*, Sub-Second Varga Cusp Solver, Bayesian Rectification, *Graha Yuddha* Scanner, *Surya Siddhanta* Drift Analyzer, Golden *Muhurta* Electional Optimizer | None | None | None |
| **Rust & Browser WebAssembly SDK** | **Included** (`rust/ephemeris-core` `60,633 charts/s` + `web/ephemeris-browser.js` `4,437 charts/s`) | C source requiring Emscripten port and copyleft compliance | Python only | Python/C only |

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
