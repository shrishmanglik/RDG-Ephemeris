# RDG-Ephemeris (`ephemeris-oss`) Technical White Paper & Full-Span Month-by-Month Evaluation Report

**Document Classification:** Public Technical White Paper & Reproducible Benchmark Report  
**Package Version:** `ephemeris-oss 0.2.0.dev1`  
**Open-Source License:** `Apache-2.0` (with explicit trademark reservation under Section 6 for `RDG™` / `Raj Dulari Gupta™`)  
**Reproducible Evidence Artifacts:**
- [`evidence/monthly-full-span-de440-benchmark.json`](../evidence/monthly-full-span-de440-benchmark.json) (`receipt_sha256: 3baf421f91696e6bd684a71975e95a6a139ba448f0f8871e7aacd23d15f15e83`)
- [`evidence/sota-ephemeris-evaluation-matrix.json`](../evidence/sota-ephemeris-evaluation-matrix.json) (`receipt_sha256: 66597bf9a98d7d4b6c491c19d2045dc4fbfc7e41c7da9a2cdb7ef5312a36d3df`)
- [`evidence/horizons-iae-benchmark.json`](../evidence/horizons-iae-benchmark.json)
- [`docs/ACCURACY.md`](ACCURACY.md)

---

## 1. Executive Summary & Problem Statement

For decades, developers, researchers, and classical astrologers building software have faced two structural bottlenecks:

1. **Licensing & Domain Scope Gap:** Legacy C ephemeris distributions (`SE 2.10.03`) are dual-licensed under copyleft (`GPL v2+` / `AGPL v3`) or paid commercial seat/API contracts, while general-purpose astronomy libraries (`Skyfield`, `Astropy`) focus on physical astronomy rather than classical Indian astronomy (*Jyotish*): `Astropy` includes a built-in approximate solar-system ephemeris by default and uses external SPK files for JPL `DE440`/`DE441` precision, and `Skyfield` loads local or cached SPK kernels (such as `de421.bsp`, `de440s.bsp`, `de440.bsp`, or `de441.bsp`) without built-in sidereal *Ayanamsha*, *Varga*, *Dasha*, or *Panchanga* engines.
2. **Generic Point-Coordinate Output vs Personalized, Birth-Clock-Calibrated Astrology:** Astrology seekers and practitioners using generic horoscope tools often receive static interpretations that do not report whether a birth-time uncertainty of $\pm 60\text{ seconds}$ crosses a higher divisional chart (*Varga*) cusp, or require separate software to run birth-time rectification, phenomena searches, and AI-verifiable calculations.

**RDG-Ephemeris (`ephemeris-oss`)** — named in tribute to **Raj Dulari Gupta (RDG)** and grounded in 40 years of traditional Jyotish practice combined with clean-room numerical astronomy — addresses both challenges:
- **Permissively Licensed (`Apache-2.0`) & Self-Contained Offline (`1550 CE` to `2306 CE`):** Ships three SHA-256-pinned compressed Chebyshev polynomial kernels (~6.68 MB on disk) derived directly from NASA JPL `DE440`, achieving a maximum sampled positional difference of `0.026041 arcsec` across **9,074 consecutive monthly epochs** (`63,518` body-epoch evaluations from `1550-01` through `2306-02`) with no external downloads required for that span.
- **Multi-Millennium Historical & Future Coverage (`3102 BCE` to `3000 CE`):** Transitions outside `1550..2306 CE` to Vondrák-2011 long-term precession (`+/-200,000` year validity) and analytical planetary/lunar series (or optional NASA JPL `DE441` SPK kernels covering `-13200` to `+17191`; see [`docs/ROADMAP-AND-LIMITATIONS.md`](ROADMAP-AND-LIMITATIONS.md) for the precision bounds of each regime).
- **Five Deterministic Inverse & Personalization Solvers (`impossible_astrology`):** Goes beyond point coordinates to compute sub-second 16-Varga cusp transition boundaries, multi-criterion heuristic birth-time rectification (*Kunda* 81x, *Pranapada*, *Pancha Tattwa*, life events), multi-century *Graha Yuddha* (planetary war) disc-diameter adjudication, classical *Surya Siddhanta* vs modern *Drig-Ganita* drift, and a **Personalized Astrological Fingerprint** (`compute_personalized_astro_fingerprint`) that computes a deterministic 16-domain birth-clock sensitivity decay index $\exp(-\sigma_t / \tau_{\min})$, continuous 16-Varga harmonic phase index, continuous topocentric *Digbala*, and heuristic 8-*Kaksha* (`3°45'`) *Ashtakavarga* transit resonance score (analytical sensitivity and rule-alignment indices rather than empirically calibrated statistical probabilities).
- **Universal AI & Developer Surfaces:** Includes a Python SDK, CLI (`ephemeris-oss`), 9-tool Model Context Protocol (MCP) server (`rdg-ephemeris-mcp`), 12-endpoint OpenAPI 3.1 HTTP REST server (`rdg-ephemeris-api`), and isomorphic Rust / WebAssembly / Browser ES-Module SDK (`rust/ephemeris-core` and `web/ephemeris-browser.js`).

---

## 2. Full-Span Month-by-Month Evaluation Against NASA JPL DE440 (`1550-01` to `2306-02`)

To benchmark the embedded Chebyshev kernels (`COMPACT-DE440-EARLY`, `COMPACT-DE440`, and `COMPACT-DE440-LATE`) on a uniform monthly grid across their 756-year span, `tools/evaluate_sota_ephemerides.py` evaluates the 15th day of **every calendar month** from **January 1550 (`1550-01`) through February 2306 (`2306-02`)** — a sampled grid of **9,074 consecutive months $\times$ 7 physical bodies = 63,518 live planetary evaluations** — directly against the SHA-256-verified full 114 MB NASA JPL `de440.bsp` (`sha256: a4ce9bf9b3282becc9f4b2ac3cebe03a2ae7599981aabd7265fd8482fff7c4b5`). This monthly sweep is a sampled benchmark across 9,074 epochs, not an exhaustive proof over all continuous real-valued instants.

### 2.1 Per-Body Accuracy Across All 9,074 Consecutive Calendar Months (`63,518` Evaluations)

| Physical Body | NAIF Target ID | Months Evaluated | Failures | Median Error (arcsec) | Mean Error (arcsec) | P95 Error (arcsec) | Worst Error Across 756 Years (arcsec) |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Sun** | `10` | `9,074` | `0` | `0.000105"` | `0.000156"` | `0.000436"` | **`0.000822"`** |
| **Moon** | `301` | `9,074` | `0` | `0.004207"` | `0.005104"` | `0.012198"` | **`0.026041"`** |
| **Mercury** | `199` | `9,074` | `0` | `0.000129"` | `0.000227"` | `0.000728"` | **`0.001940"`** |
| **Venus** | `299` | `9,074` | `0` | `0.000123"` | `0.000236"` | `0.000828"` | **`0.004451"`** |
| **Mars (system barycentre)** | `4` | `9,074` | `0` | `0.000082"` | `0.000148"` | `0.000503"` | **`0.002205"`** |
| **Jupiter (system barycentre)** | `5` | `9,074` | `0` | `0.000032"` | `0.000054"` | `0.000164"` | **`0.000348"`** |
| **Saturn (system barycentre)** | `6` | `9,074` | `0` | `0.000029"` | `0.000050"` | `0.000151"` | **`0.000278"`** |

### 2.2 Per-Century Breakdown Across All 9,074 Calendar Months (`1550 CE` to `2306 CE`)

| Century Bucket | Body-Month Evaluations | Median Error (arcsec) | Mean Error (arcsec) | P95 Error (arcsec) | Worst Error (arcsec) |
|---|---:|---:|---:|---:|---:|
| **`1550–1599 CE` (`1500s_CE`)** | `4,200` | `0.000054"` | `0.000557"` | `0.004071"` | `0.010767"` |
| **`1600–1699 CE` (`1600s_CE`)** | `8,400` | `0.000056"` | `0.000555"` | `0.003966"` | `0.011296"` |
| **`1700–1799 CE` (`1700s_CE`)** | `8,400` | `0.000056"` | `0.000569"` | `0.004128"` | `0.011989"` |
| **`1800–1899 CE` (`1800s_CE`)** | `8,400` | `0.000227"` | `0.001276"` | `0.008408"` | `0.023514"` |
| **`1900–1999 CE` (`1900s_CE`)** | `8,400` | `0.000224"` | `0.001335"` | `0.008905"` | `0.025741"` |
| **`2000–2099 CE` (`2000s_CE`)** | `8,400` | `0.000228"` | `0.001296"` | `0.008475"` | `0.026041"` |
| **`2100–2199 CE` (`2100s_CE`)** | `8,400` | `0.000056"` | `0.000564"` | `0.003990"` | `0.017761"` |
| **`2200–2299 CE` (`2200s_CE`)** | `8,400` | `0.000056"` | `0.000547"` | `0.003961"` | `0.011574"` |
| **`2300–2306 CE` (`2300s_CE`)** | `518` | `0.000058"` | `0.000576"` | `0.004183"` | `0.010836"` |
| **Total (`1550-01` to `2306-02`)** | **`63,518`** | **`0.000105"` (Sun) / `0.004207"` (Moon)** | **`0.000854"` overall** | **`<= 0.012198"`** | **`0.026041"` (`0` failures)** |

> **Numerical Note on 16-Day `.5` JD Chebyshev Interval Straddles:** During light-time retardation for the Moon ($\tau \approx 1.28\text{ s}$), reception time $t_{\text{rec}}$ and emission time $t_{\text{em}} = t_{\text{rec}} - \tau$ can straddle a 16-day `.5` JD interval boundary of the Earth-Moon Barycenter `(0, 3)` Chebyshev segment. `JplErfaAstronomyProvider._target_state_func` (shared across both `planet_positions_tt` and `planet_positions`) anchors the Earth-Moon Barycenter propagation over $\Delta t = t_{\text{em}} - t_{\text{rec}}$ to the reception-epoch EMB state ($\mathbf{r}_{0 \to 3}(t_{\text{em}}) = \mathbf{r}_{0 \to 3}(t_{\text{rec}}) + \mathbf{v}_{0 \to 3}(t_{\text{rec}})\,\Delta t$, where the omitted $\frac{1}{2}\mathbf{a}_{0 \to 3}\Delta t^2$ heliocentric acceleration term over $1.28\text{ s}$ is $\approx 4.8\text{ mm}$ or $\approx 0.0000025\text{ arcsec}$), eliminating the 16-day `(0, 3)` segment quantization step when reception and emission straddle a 16-day boundary.

---

## 3. Independent Validation Against NASA JPL Horizons (`DE441`, `2,100` Rows)

In addition to internal verification against full `de440.bsp`, `ephemeris-oss` is tested against `2,100` independent NASA JPL Horizons `DE441` apparent geocentric ecliptic reference vectors (`300` epochs $\times$ `7` physical bodies across `1800..2100 CE`, stored in `bench/studies/E2-accuracy/` and `evidence/horizons-iae-benchmark.json`):

| Physical Body | NAIF ID | Full `de440.bsp` vs `DE440` Worst (`12:00 TT`) | Horizons `DE441` Median (arcsec) | Horizons `DE441` P95 (arcsec) | Horizons `DE441` Worst (arcsec) |
|---|---:|---:|---:|---:|---:|
| **Sun centre** | `10` | `0.000108"` | `0.00000156"` | `0.00000299"` | `0.00000381"` |
| **Moon centre** | `301` | `0.000717"` | `0.00243319"` | `0.01726497"` | `0.02535092"` (`0.036858"` embedded Chebyshev) |
| **Mercury centre** | `199` | `0.000108"` | `0.00000173"` | `0.00000359"` | `0.00000519"` |
| **Venus centre** | `299` | `0.000107"` | `0.00000161"` | `0.00000302"` | `0.00000510"` |
| **Mars system barycentre** | `4` | `0.000108"` | `0.00000140"` | `0.00000253"` | `0.00000322"` |
| **Jupiter system barycentre** | `5` | `0.000108"` | `0.00000139"` | `0.00000214"` | `0.00000255"` |
| **Saturn system barycentre** | `6` | `0.000109"` | `0.00000139"` | `0.00000217"` | `0.00000272"` |

---

## 4. Deep-History & Far-Future Sampled Execution Sweep (`3102 BCE` to `3000 CE`)

To verify finite coordinate execution and nodal antipode invariants across the 6,102-year historical and future window (`3102 BCE` Kali Yuga epoch through `3000 CE`), `tools/evaluate_sota_ephemerides.py` (`evaluate_deep_history_3102bce_to_3000ce_sweep`) evaluates `459` sampled epochs (`4,131` `adapter.calc_ut` 9-graha coordinate evaluations: all 12 calendar months of `3102 BCE`, `2500 BCE`, `2000 BCE`, `1500 BCE`, `1000 BCE`, `500 BCE`, `1 CE`, `499 CE`, `1000 CE`, `1500 CE`, `1550 CE`, `1700 CE`, `1800 CE`, `1900 CE`, `1956 CE`, `2000 CE`, `2026 CE`, `2300 CE`, and `3000 CE`, plus 25-year July steps across `range(-3100, 3001, 25)`):

- **Total Sampled Epochs Tested:** `459` (`4,131` 9-graha `calc_ut` sidereal coordinate evaluations; does not evaluate houses or compare against an independent ancient reference ephemeris outside the DE440 span)
- **Failures / NaNs / Exceptions:** **`0`**
- **Rahu–Ketu `180.000000000°` Antipode Invariant Error:** **`0.000000000 arcsec`** across all `459` sampled epochs
- **Sampled Sweep Execution Time:** `~1.4 seconds` (`~3.0 ms` per 9-graha `calc_ut` epoch evaluation)

---

## 5. Five Deterministic Solvers for Personalized & Inverse Astrology (`impossible_astrology`)

Standard ephemeris libraries output raw longitudes and leave astrologers and developers to guess how sensitive a chart is to birth-time uncertainty or how a transit interacts with an individual's harmonic structure. `ephemeris_oss.impossible_astrology` introduces five deterministic, SHA-256-receipt-sealed mathematical solvers:

### 5.1 Personalized Astrological Fingerprint (`compute_personalized_astro_fingerprint`)

Solves the "generic horoscope" problem by synthesizing four continuous, mathematically rigorous layers for any birth instant $t_0$, geographic location $(\phi, \lambda)$, clock uncertainty $\sigma_t$ (in seconds), and query transit epoch $t_q$:

1. **Continuous 16-Varga Harmonic Phase Matrix & Vimshopaka Alignment:**
   For the Ascendant and all 9 Grahas across all 16 Parashari *Shodashvarga* divisions ($D_k \in \{D_1, D_2, D_3, D_4, D_7, D_9, D_{10}, D_{12}, D_{16}, D_{20}, D_{24}, D_{27}, D_{30}, D_{40}, D_{45}, D_{60}\}$), computes the normalized sector phase $\phi_{p,k} = \Delta\theta_{\text{low}} / \Delta\theta_{\text{span}} \in [0, 1]$ and the continuous sinusoidal boundary-stability index:
   $$S_{p,k} = \sin(\pi \phi_{p,k}) \in [0, 1]$$
   where $S_{p,k} = 1$ at the exact harmonic center of the divisional sign and $S_{p,k} \to 0$ as the body approaches a sign cusp, paired with the 20-point *Shodashvarga Vimshopaka Bala* score.
2. **16-Domain Birth-Clock Sensitivity & Heuristic Confidence Decay Index:**
   For each of the 16 life domains ($D_1$ physical vitality through $D_{60}$ *Shashtiamsa*), computes the exact governing temporal cusp margin $\tau_{\min}(D_k) = \min(\tau_{\text{Asc}}(D_k), \tau_{\text{Moon}}(D_k))$ in seconds and a deterministic exponential sensitivity index under reported birth-time uncertainty $\sigma_t$:
   $$C(D_k \mid \sigma_t) = \exp\!\left(-\frac{\sigma_t}{\tau_{\min}(D_k)}\right) \in (0, 1]$$
   Each life domain is deterministically classified as `LOCKED_INVARIANT` ($\tau_{\min} \ge 3\sigma_t$), `MODERATELY_SENSITIVE` ($\sigma_t \le \tau_{\min} < 3\sigma_t$), or `RECTIFICATION_REQUIRED` ($\tau_{\min} < \sigma_t$). Note that $C(D_k \mid \sigma_t)$ is an analytical boundary-distance heuristic index rather than an empirically calibrated statistical probability, designed to flag when a divisional chart cusp lies near or within the seeker's reported clock uncertainty.
3. **Continuous Topocentric Horizon–Meridian *Digbala* Vector (`0..60` Virupas):**
   Measures each planet's exact angular distance $\Delta\psi_p \in [0^\circ, 180^\circ]$ from its topocentric directional power pole (East Horizon / *Lagna* for Jupiter and Mercury, South Meridian / *MC* for Sun and Mars, West Horizon / *Descendant* for Saturn, North Nadir / *IC* for Moon and Venus), outputting both classical linear *Digbala* $(180^\circ - \Delta\psi_p)/3$ and smooth harmonic cosine *Digbala* $30(1 + \cos\Delta\psi_p)$ in *Virupas*.
4. **Heuristic Natal-to-Transit 8-*Kaksha* (`3°45'`) & 337-Bindu *Ashtakavarga* Resonance Score (`0..100`):**
   Evaluates every transiting planet at `query_jd_ut` through the seeker's personal 8-*Kaksha* (`3°45'` sub-sectors ruled by Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon, and Lagna), *Bhinna Ashtakavarga* (`0..8` bindus), *Sarvashtakavarga* (conserved `337` total bindus), *Gochara Vedha* obstruction (with classical Father–Son exemptions for Sun–Saturn and Moon–Mercury), and harmonic angular alignment to the seeker's *Atmakaraka*, Natal Moon, and Natal Ascendant. The resulting `0..100` composite score is a deterministic weighted rule-alignment heuristic, not an empirically calibrated outcome probability.

### 5.2 Sub-Second 16-Varga Cusp Transition Solver (`solve_subsecond_shodashvarga_cusp_transitions`)
Brackets and refines via Illinois false-position root-finding the exact number of seconds backward and forward until the Ascendant and each of the 9 Grahas change sign in all 16 *Shodashvarga* charts (`D1..D60`), accounting for topocentric horizon kinematics and unequal Parashari `D30` (*Trimsamsa*) sectors.

### 5.3 Multi-Criterion Bayesian Birth-Time Rectification (`rectify_birth_time_bayesian`)
Evaluates candidate birth times across $\pm W$ minutes by combining *Kunda* $81\times$ harmonic *Shuddhi*, *Pranapada Lagna Shuddhi* from topocentric sunrise, *Pancha Tattwa* 90-minute elemental cycles, and dated life-event *Vimshottari Dasha* triggers.

### 5.4 Multi-Century *Graha Yuddha*, Retrograde Station & Combustion Scanner (`scan_multi_century_rare_phenomena`)
Finds exact-second planetary wars (*Graha Yuddha* within $1^\circ$ among the five *Taragrahas* with apparent disc diameter and northern ecliptic latitude victory adjudication), retrograde stations (*Vakri* / *Margi*), and solar combustion windows (*Astangata* / *Cazimi*) across `3102 BCE` to `3000 CE`.

### 5.5 Classical *Surya Siddhanta* vs Modern NASA JPL DE440 Drift Analyzer (`analyze_siddhanta_vs_jpl_de440_drift`)
Computes *Ahargana* days since the `3102 BCE` Kali Yuga epoch (`JD 588465.5`) and compares classical *Surya Siddhanta* epicyclic (*Manda* + *Sighra Samskara*) longitudes against modern *Drig-Ganita* (`DE440` Chebyshev or Vondrák-2011).

---

## 6. Head-to-Head Capability & Licensing Matrix

Third-party engines are not executed inside this clean-room repository; their numeric accuracy cells are therefore recorded as `UNKNOWN` in accordance with repository claim-hygiene rules, while all `ephemeris-oss` figures are reproduced by `python tools/evaluate_sota_ephemerides.py`:

| Parameter | RDG-Ephemeris (`ephemeris-oss`) | Legacy C Ephemeris (`SE 2.10.03`) | `Skyfield 1.55` | `Astropy 6.x` |
|---|---|---|---|---|
| **Open-Source License** | **Apache-2.0** (free for commercial SaaS, apps, and research) | GPL v2+ / AGPL v3 or paid commercial license | MIT (astronomy only) | BSD-3-Clause (astronomy only) |
| **Offline Embedded NASA JPL DE440 Span** | **`1550 CE` to `2306 CE`** bundled in wheel (~6.68 MB Chebyshev polynomials, `9,074` months) | Uses external `.se1` or `.bsp` files on disk | Loads local/cached SPK files (e.g., `de421.bsp`, `de440s.bsp`, `de440.bsp`; not bundled in wheel) | Built-in approximate ephemeris default; JPL `DE440`/`DE441` uses external SPK |
| **Multi-Millennium Span** | **`3102 BCE` to `3000 CE`** offline (`Vondrak-2011` + analytical) + optional `DE441` (`-13200..+17191`) | Uses multi-file `.se1` archive across centuries | Loads local/cached SPK files (e.g., `de440.bsp` / `de441.bsp`) | Built-in approximate ephemeris default; JPL `DE441` uses external SPK |
| **Reproduced Fidelity vs Full NASA JPL DE440 (`1800..2100 CE`, `12:00 TT`)** | **`<= 0.000717 arcsec` max** (`0.000019 arcsec` median across 3,612 monthly TT epochs/planet) | UNKNOWN (not executed in this clean-room repository) | UNKNOWN (not executed in this clean-room repository) | UNKNOWN (not executed in this clean-room repository) |
| **Reproduced Month-by-Month Fidelity vs Full DE440 (`1550-01` to `2306-02`, `63,518` evaluations)** | **`<= 0.026041 arcsec` max** (`0` failures across all `9,074` calendar months; Sun `<= 0.000822"`, Planets `<= 0.004451"`, Moon `<= 0.026041"`) | UNKNOWN (not executed in this clean-room repository) | UNKNOWN (not executed in this clean-room repository) | UNKNOWN (not executed in this clean-room repository) |
| **Cryptographic Calculation Receipts (`SHA-256`)** | **Built-in on every result** | None | None | None |
| **Built-in LLM MCP Server (`stdio`)** | **Built-in (`rdg-ephemeris-mcp`)** with **9 deterministic tools** + AI hallucination auditor | None | None | None |
| **Built-in HTTP REST API (`OpenAPI 3.1`)** | **Built-in (`rdg-ephemeris-api`)** with **12 endpoints** | None | None | None |
| **Classical Jyotish & Almanac Stack** | **23 Vargas (`D1..D144`), 86 Classical & Tajika Yogas, Shadbala, 337-Bindu Ashtakavarga, 8 Dashas, Jaimini, Nadi, Tajika, Drik Panchang, SVG** | Coordinates, ayanamsa, houses, and basic phenomena only | None | None |
| **Inverse & Personalization Solvers** | **5 built-in solvers** (Sub-second Varga cusps, Bayesian rectification, Graha Yuddha scanner, Siddhanta drift, Personalized Astro Fingerprint) | None | None | None |
| **Rust Core & Browser WebAssembly SDK** | **Included** (`rust/ephemeris-core` + `web/ephemeris-browser.js`) | C source requiring Emscripten port and AGPL compliance | Python only | Python/C only |

---

## 7. Reproducing All Benchmarks Locally

Every table and receipt in this white paper can be reproduced from a clean checkout once the reference NASA JPL `de440.bsp` kernel and Earth-orientation cache are provisioned (`ephemeris-oss kernels fetch --verify --eop`, or by pointing `EPHEMERIS_OSS_CACHE` and `EPHEMERIS_OSS_DE440_KERNEL` at your verified local cache):

```bash
export PYTHONPATH=src
export EPHEMERIS_OSS_CACHE="$HOME/.cache/ephemeris-oss"
export EPHEMERIS_OSS_DE440_KERNEL="$EPHEMERIS_OSS_CACHE/de440.bsp"

# 1. Run the full 9,074-month DE440 sweep, 459-epoch 3102 BCE..3000 CE sweep, and 5-solver benchmark
python tools/evaluate_sota_ephemerides.py

# 2. Run the CLI personalized astrological fingerprint solver
ephemeris-oss fingerprint --at 2026-10-06T12:00:00Z --lat 28.6139 --lon 77.2090 --uncertainty-sec 60

# 3. Inspect all 9 MCP tools for LLM / AI agent integration
rdg-ephemeris-mcp --dump-tools

# 4. Run the full verification, provenance, internal-ID, and claim-hygiene gates
python -m pytest -q
python tools/check_provenance.py src --allow tools/provenance-allow.txt
python tools/check_internal_ids.py src tests
python tools/check_claims.py
```
