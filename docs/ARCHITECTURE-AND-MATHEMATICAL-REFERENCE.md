# Architecture and Mathematical Reference (`ephemeris-oss`)

This reference documents the clean-room architecture, coordinate reduction pipelines, classical Indian astronomical (*Siddhanta*) and astrological (*Jyotish*) algorithms, and deterministic receipt invariants implemented in `ephemeris-oss` under the Apache-2.0 licence.

---

## 1. Core JPL DE440/DE441 & IAU 2006/2000A ERFA Reduction Pipeline

### 1.1 Time Scales & Barycentric Coordinate Evaluation
`ephemeris-oss` separates civil UTC, UT1, Terrestrial Time ($\text{TT}$), and Barycentric Dynamical Time ($\text{TDB}$):
1. **Explicit Terrestrial Time Interface (`Engine.positions_tt`):** Accepts an explicit $\text{JD}_{\text{TT}}$ instant without inferring UTC or UT1.
2. **Civil UTC Interface (`Engine.positions`):** Accepts a timezone-aware UTC `datetime`, converts $\text{UTC} \to \text{TAI} \to \text{TT}$ via IAU SOFA/ERFA (`erfa.dtf2d`, `erfa.utctai`, `erfa.taitt`), and relates $\text{TT}$ to $\text{TDB}$ via `erfa.dtdb` and `erfa.tttdb`.
3. **Barycentric State Chaining:** Planetary states $\mathbf{r}_{\text{ICRF}}(t_{\text{TDB}}), \dot{\mathbf{r}}_{\text{ICRF}}(t_{\text{TDB}})$ are evaluated relative to the Solar System Barycentre (`NAIF 0`) by chaining the Earth-Moon Barycentre (`NAIF 3`) with Earth (`NAIF 399`) and Moon (`NAIF 301`).
4. **Newtonian Light-Time Iteration, Relativistic Deflection & Aberration:**
   - Given observer position $\mathbf{r}_{\text{obs}}(t)$ and target $\mathbf{r}_{\text{target}}(t - \tau)$, light time $\tau = \|\mathbf{r}_{\text{target}}(t - \tau) - \mathbf{r}_{\text{obs}}(t)\| / c$ is solved iteratively to convergence.
   - Gravitational light deflection in the solar potential applies the Horizons-compatible opaque-solar-photosphere convention during solar occultation.
   - Relativistic stellar aberration transforms the geometric light-time-corrected unit vector into the apparent geocentric ICRF unit vector $\mathbf{u}_{\text{app}}$.

### 1.2 IAU 2006 Precession & IAU 2000A Nutation
The apparent ICRF direction is rotated into the true ecliptic and equinox of date via the Fukushima-Williams four-angle parameterization (`erfa.ecm06` and `erfa.nut06a`):
$$\lambda_{\text{trop}} = \left(\lambda_{\text{mean\_ecl}} + \Delta\psi\right) \bmod 360^\circ$$
where $\Delta\psi$ and $\Delta\epsilon$ are the IAU 2000A nutation in longitude and obliquity, and $\epsilon = \epsilon_A + \Delta\epsilon$ is the true obliquity of date.

### 1.3 Cryptographic Calculation Receipts (`receipt_sha256`)
Every public calculation returns a `Result` (or typed dataclass) carrying a canonical 64-hex SHA-256 digest computed over sorted JSON keys binding the schema identifier, package version, input epoch, coordinate conventions, kernel SHA-256 hash, and rounded numerical outputs.

---

## 2. Embedded Compact 1.84 MB Chebyshev DE440 Kernel (`compact_kernel.py`)

To enable offline execution without a 114 MB raw SPK download, `src/ephemeris_oss/data/de440_compact.bin.zlib` (`1,839,230 bytes`) stores Chebyshev position polynomials fitted directly to NASA JPL DE440 over `JD 2378448.5` (`1799-10-28`) through `JD 2488512.5` (`2101-03-20`).

For a granule of length $\Delta t$ starting at $t_0$, normalized time is:
$$\tau = 2\left(\frac{t_{\text{TDB}} - t_0}{\Delta t}\right) - 1 \in [-1, 1]$$
Position components $r_i(\tau)$ and derivatives $\dot{r}_i(\tau)$ are evaluated via backward Clenshaw recurrence:
$$b_{N} = b_{N+1} = 0, \quad b_k = 2\tau b_{k+1} - b_{k+2} + c_k \quad (k = N-1, \dots, 1), \quad r_i(\tau) = \tau b_1 - b_2 + c_0$$
Across `1800..2100`, the compact kernel reproduces full DE440 within `< 0.015` arcseconds for the Moon (`8-day` granules, degree 10) and `< 0.0019` arcseconds for the physical planets (`16-day` or `32-day` granules).

---

## 3. Ayanamsha Models, Lunar Nodes & Bhava Chalit House Systems

### 3.1 Named Ayanamsha Models & Nirayana Longitudes
Nirayana (sidereal) longitude is defined by:
$$\lambda_{\text{sid}} = \left(\lambda_{\text{trop}} - A(t)\right) \bmod 360^\circ$$
Supported named Ayanamsha conventions (`src/ephemeris_oss/engine/conventions.py` and `stellar_anchors.py`):
- **`lahiri` (Chitrapaksha):** Anchored to $23^\circ 15' 00.658''$ at `1956-03-21.0 TT` ($23.853^\circ$ at `J2000.0`) with IAU 2006 general precession in longitude.
- **`true_citra` (True Citra):** Dynamically locks apparent Spica ($\alpha\text{ Virginis}$ with proper motion and annual aberration) to $180^\circ 00' 00''$ Nirayana ($0^\circ\text{ Tula}$).
- **`raman`:** B.V. Raman reference ($22.41079^\circ$ at `J2000.0`).
- **`krishnamurti` / `kp`:** Krishnamurti Paddhati reference ($23.7586^\circ$ at `J2000.0`).
- **`yukteshwar`, `fagan_bradley`, and `pushya` ($\delta\text{ Cancri}$ anchored at $106^\circ 00' 00''$).**

### 3.2 Lunar Nodes (`ephemeris-oss-lunar-nodes-1.1.0-meeus47.7`)
- **Mean Rahu:** Jean Meeus, *Astronomical Algorithms* (2nd ed., Eq. 47.7) with $T = (\text{JD}_{\text{TT}} - 2451545.0) / 36525$:
  $$\Omega_{\text{mean}} = 125.0445479^\circ - 1934.1362891^\circ T + 0.0020754^\circ T^2 + \frac{T^3}{467441} - \frac{T^4}{60616000} \pmod{360^\circ}$$
- **True Rahu:** Instantaneous osculating intersection of the geocentric lunar orbit plane $\mathbf{h} = \mathbf{r}_{\text{Moon}} \times \mathbf{v}_{\text{Moon}}$ with the ecliptic of date.
- **Ketu:** Exact antipode $\lambda_{\text{Ketu}} = (\lambda_{\text{Rahu}} + 180^\circ) \pmod{360^\circ}$.

### 3.3 Bhava Chalit & House Cusps
Given local apparent sidereal time $\theta_{\text{LAST}}$, observer latitude $\phi$, and true obliquity $\epsilon$:
- **Midheaven ($\text{MC}$):** $\lambda_{\text{MC}} = \operatorname{atan2}(\sin\theta_{\text{LAST}}, \cos\theta_{\text{LAST}}\cos\epsilon) \pmod{360^\circ}$
- **Ascendant (*Lagna*):** $\lambda_{\text{Asc}} = \operatorname{atan2}(\cos\theta_{\text{LAST}}, -\sin\theta_{\text{LAST}}\cos\epsilon - \tan\phi\sin\epsilon) \pmod{360^\circ}$
- **House Layouts:** Supports `whole_sign` (`W`), `equal_house` (`E`), `porphyry` / Sripati quadrant trisection (`O`), and `placidus` (`P`, iterative semi-diurnal/nocturnal arc trisection). Inside the polar circles ($|\phi| \ge 90^\circ - \epsilon$), `placidus` returns an explicit `Undefined` value (on `Engine`) or raises `EphemerisError` (on `EphemerisAdapter`), never silently substituting another house system.

---

## 4. Core Parashari Jyotish Mathematical Suite (`src/ephemeris_oss/jyotish/`)

### 4.1 27 & 28 Nakshatras (`nakshatra.py`)
Each equal Nakshatra spans $13^\circ 20' = \frac{40^\circ}{3} = 13.333333333^\circ$, and each Pada (*Charana*) spans $3^\circ 20' = \frac{10^\circ}{3}$:
$$n = \left\lfloor \frac{\lambda_{\text{sid}}}{40^\circ / 3} \right\rfloor \in \{0, \dots, 26\}, \quad \text{Pada} = \left\lfloor \frac{\lambda_{\text{sid}} \bmod (40^\circ / 3)}{10^\circ / 3} \right\rfloor + 1 \in \{1, 2, 3, 4\}$$
In the 28-Nakshatra *Abhijit* scheme, *Uttara Ashadha* ($276^\circ 40'$ to $280^\circ 00'$) and *Shravana* ($280^\circ 00'$ to $280^\circ 53' 20''$) yield the intercalary *Abhijit* span ($276^\circ 40' 00''$ to $280^\circ 53' 20''$).

### 4.2 Twenty Divisional Vargas (`D1..D144`, `vargas.py`)
For sign index $r = \lfloor \lambda_{\text{sid}} / 30^\circ \rfloor \in \{0,\dots,11\}$ and degree-in-sign $d = \lambda_{\text{sid}} \bmod 30^\circ$:
- **D1 (Rasi):** $r$
- **D2 (Hora):** Odd signs map $[0^\circ, 15^\circ) \to \text{Leo (4)}$, $[15^\circ, 30^\circ) \to \text{Cancer (3)}$; even signs reverse.
- **D3 (Drekkana):** $(r + 4\lfloor d / 10^\circ \rfloor) \bmod 12$
- **D4 (Chaturthamsa):** $(r + 3\lfloor d / 7.5^\circ \rfloor) \bmod 12$
- **D7 (Saptamsa):** Odd signs start at $r$; even signs start at $(r + 6) \bmod 12$, advancing by $\lfloor d / (30^\circ/7) \rfloor$.
- **D9 (Navamsa):** $\lfloor \lambda_{\text{sid}} / (10^\circ / 3) \rfloor \bmod 12$
- **D10 (Dasamsa):** Odd signs start at $r$; even signs start at $(r + 8) \bmod 12$, advancing by $\lfloor d / 3^\circ \rfloor$.
- **D12 (Dwadasamsa):** $(r + \lfloor d / 2.5^\circ \rfloor) \bmod 12$
- **D16, D20, D24, D27, D30 (Parashari 5-band unequal Trimsamsa), D40, D45, D60 (Shashtiamsa), plus D5, D6, D8, D11, D81, D108, and D144.**

### 4.3 Five-Limb Panchanga (`panchanga.py`)
Let $\Delta\lambda = (\lambda_{\text{Moon}} - \lambda_{\text{Sun}}) \bmod 360^\circ$ and $\Sigma\lambda = (\lambda_{\text{Moon}} + \lambda_{\text{Sun}}) \bmod 360^\circ$:
$$\text{Tithi} = \left\lfloor \frac{\Delta\lambda}{12^\circ} \right\rfloor + 1 \in \{1,\dots,30\}, \quad \text{Karana} = \left\lfloor \frac{\Delta\lambda}{6^\circ} \right\rfloor + 1 \in \{1,\dots,60\}$$
$$\text{Nakshatra} = \left\lfloor \frac{\lambda_{\text{Moon}}}{40^\circ / 3} \right\rfloor + 1 \in \{1,\dots,27\}, \quad \text{Yoga} = \left\lfloor \frac{\Sigma\lambda}{40^\circ / 3} \right\rfloor + 1 \in \{1,\dots,27\}$$

### 4.4 Multi-Dasha Systems (`dasha.py`)
In the 120-year Vimshottari system with cycle weights $W = (7, 20, 6, 10, 7, 18, 16, 19, 17)$ for `(Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury)`:
- Remaining balance of the birth Mahadasha is $Y_{\text{rem}} = W_{n \bmod 9} \times \left(1 - \frac{\lambda_{\text{Moon}} \bmod (40^\circ/3)}{40^\circ/3}\right)$.
- Each sub-period at depth $k \in \{1,\dots,5\}$ (*Mahadasha*, *Antardasha*, *Pratyantardasha*, *Sookshma*, *Prana*) scales proportionally by $W_j / 120$.
- Also implements 36-year *Yogini*, 108-year *Ashtottari*, *Jaimini Chara*, *Sthira*, *Shoola*, *Mandooka*, and Tajika *Mudda* Dashas (8 Dasha systems total, with configurable `365.2425` solar vs `360.0` *Savana* year length; *Kalachakra Dasha* is tracked on the roadmap in [`ROADMAP-AND-LIMITATIONS.md`](ROADMAP-AND-LIMITATIONS.md)).

### 4.5 Six-Fold Shadbala (`shadbala.py`) & Ashtakavarga Conservation (`ashtakavarga.py`)
- **Shadbala:** Sums *Sthana Bala* (*Uchcha*, *Saptavargaja*, *Ojhayugmarasyamsa*, *Kendradi*, *Drekkana*), *Dig Bala*, *Kala Bala* (*Natonnata*, *Paksha*, *Tribhaga*, *Varsha-Masa-Dina-Hora*, *Ayana*, *Yuddha*), *Cheshta Bala*, *Naisargika Bala*, and *Drik Bala* in Virupas ($60\text{ Virupas} = 1\text{ Rupa}$).
- **Ashtakavarga Conservation Invariant:** The seven *Bhinnashtakavarga* tables satisfy exact classical totals:
  $$\text{Sun } 48 + \text{Moon } 49 + \text{Mars } 39 + \text{Mercury } 54 + \text{Jupiter } 56 + \text{Venus } 52 + \text{Saturn } 39 = 337\text{ Sarvashtakavarga bindus}$$
  followed by *Trikona Shodhana*, *Ekadhipatya Shodhana*, and 8-fold *Kakshya* ($3^\circ 45'$) transit grading.

---

## 5. Advanced Predictive, Jaimini, Nadi, Rectification, Siddhanta & Almanac Suites

1. **KP 249 Sub-Lords, Tajika Varshphal, Synastry & 70 Yogas (`jyotish_advanced`):**
   - Exact 249 Krishnamurti table boundaries (splitting signs at $30^\circ$ multiples where a sub-lord crosses a Rashi boundary), 4-step planetary/cuspal significators, sub-second Newton-bisection Solar Return (*Varshphal*) with *Muntha*, 16 *Tajika Yogas*, *Sahams*, *Mudda Dasha*, 36-point *Ashtakoota* + 10-point *Dashakoota* synastry, and 70 classical *Parashari* Yogas.
2. **Besselian Eclipses & Planetary Phenomena (`engine/eclipses.py`, `engine/phenomena.py`):**
   - Solar and lunar eclipse root-finding with Besselian elements, $\gamma$, magnitude, Saros series, and topocentric contact timings, plus stationary points ($\dot{\lambda} = 0$), maximum elongation, *Graha Yuddha*, and *Moudhya* (combustion).
3. **Jaimini Sutras & Birth-Time Sensitivity Envelope (`jyotish_jaimini`, `engine/uncertainty_envelope.py`):**
   - 7/8 *Chara Karakas*, *Arudha Padas* ($A_1..A_{12}$, *Upapada* $UL$), *Karakamsa*, *Rashi Drishti*, *Chara*/*Mandooka*/*Shoola* Dashas, and exact $\pm\Delta t$ birth-time margin envelopes to the nearest Rashi, Nakshatra, Navamsa (`D9`), Dasamsa (`D10`), and Shashtiamsa (`D60`) boundaries.
4. **Electional Muhurta, Prashna, Chakras, Bhrigu Nadi & Rectification (`jyotish_transit`, `jyotish_nadi`, `jyotish_rectification`):**
   - *Tarabala*/*Chandrabala*/*Panchaka* Muhurta scanner, Kerala *Prashna Marga* (*Sphutas* + *Ashtamangala* cowrie solver), 9x9 *Sarvatobhadra* and *Kota* Chakras, *Bhrigu Bindu* ($\frac{\lambda_{\text{Moon}} + \lambda_{\text{Rahu}}}{2}$), 22nd *Drekkana* / 64th *Navamsa* / *Mrityu Bhaga*, classical *Pindayu*/*Nisargayu*/*Amsayu* longevity, and *Kala Shodhana* birth-time rectification (*Kunda* $81\times\text{Lagna}$, *Pranapada*, *Tattwa*).
5. **Classical *Surya Siddhanta*, *Vedanga Jyotisha* & Observational Almanac (`jyotish_siddhanta`, `almanac`):**
   - Kali Yuga *Ahargana* (`JD 588465.5`), *Mahayuga* (`1,577,917,828` *Savana* days), 4-step *Ardha-Phala* epicyclic reduction (`surya_siddhanta_true_positions`), *Lagadha Vedanga Jyotisha* 5-year *Yuga* calendar, Yallop/Odeh crescent visibility, Schoch/Schaefer heliacal phenomena, sunrise-anchored monthly Drik Panchang (`generate_monthly_panchang`), and tabular ephemeris / ingress scanners (`generate_ephemeris_table`, `scan_ingresses_and_aspects`).
6. **Pure-Rust / WebAssembly Core, SVG Charts & `< 3 KB` AI Fact-Sheet Firewall (`rust/ephemeris-core`, `web/`, `visualization/`, `fact_sheet.py`):**
   - `29.9 KB` `.wasm` binary + zero-dependency browser SDK (`web/ephemeris-browser.js`), 5-style SVG Kundali renderer (`render_north_indian_svg`, `render_south_indian_svg`, `render_east_indian_svg`, `render_circular_wheel_svg`, `render_sarvatobhadra_svg`), and `< 3,072 byte` `AIFactSheet` compiler + `verify_ai_interpretation` hallucination detector.

---

## 6. Verified Python & CLI Quickstart Workflows

```python
from datetime import datetime, timezone
from ephemeris_oss import (
    Engine,
    EphemerisAdapter,
    compile_ai_fact_sheet,
    verify_ai_interpretation,
)
from ephemeris_oss.almanac import generate_ephemeris_table, generate_monthly_panchang
from ephemeris_oss.jyotish_siddhanta import surya_siddhanta_true_positions
from ephemeris_oss.visualization import render_north_indian_svg

# 1. Core TT and UTC Engine with embedded 1.84 MB compact Chebyshev DE440 kernel
with Engine.load(kernels="compact", eop=None) as engine:
    tt_res = engine.positions_tt(2451545.0, bodies=("sun", "moon"))
    assert len(tt_res.receipt_sha256) == 64

# 2. Unified Downstream Adapter & Complete Kundali Bundle
with EphemerisAdapter(kernels="compact") as adapter:
    bundle = adapter.compute_complete_kundali_bundle(
        datetime(2026, 10, 6, 12, 0, tzinfo=timezone.utc),
        latitude_deg=28.6139,
        longitude_deg=77.2090,
        ayanamsa="lahiri",
    )
    assert len(bundle.receipt_sha256) == 64
    assert len(bundle.ai_fact_sheet.json_str.encode("utf-8")) <= 3000

# 3. Monthly Sunrise-Anchored Drik Panchang, Tabular Ephemeris & Surya Siddhanta
panchang = generate_monthly_panchang(2026, 10, latitude_deg=28.6139, longitude_deg=77.2090)
table = generate_ephemeris_table(2461319.5, 2461324.5, step_days=1.0)
siddhanta = surya_siddhanta_true_positions(2461319.5)
svg_chart = render_north_indian_svg(
    {k.capitalize(): v.longitude_deg for k, v in bundle.positions.items()},
    bundle.houses.ascendant_deg,
)
assert len(panchang.receipt_sha256) == 64
assert len(table.receipt_sha256) == 64
assert len(siddhanta.receipt_sha256) == 64
assert len(svg_chart.receipt_sha256) == 64
```
