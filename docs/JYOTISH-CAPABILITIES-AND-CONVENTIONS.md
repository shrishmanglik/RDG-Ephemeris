# Jyotish Capabilities, Lineage Conventions & Mathematical Coverage

**Engine:** `ephemeris-oss` (**RDG-Ephemeris**, in tribute to **Raj Dulari Gupta**)  
**Lineage Foundation:** Designed for real Jyotish applications with 40 years of lived traditional consultation, Panchanga, and teaching practice alongside modern clean-room astronomical software engineering.

---

## 1. Time Scales & Historical Date Regimes

Accurate Jyotish calculation requires strict separation between Earth-rotation time (`UTC` / `UT1`, which governs the observer's horizon, Ascendant, house cusps, and local sunrise) and uniform dynamical ephemeris time (`TT` / `TDB`, which governs planetary and lunar orbital equations of motion).

| Time Scale / Span | API Surface | Mathematical Realization | Scope & Precision Regime |
|---|---|---|---|
| **Explicit Terrestrial Time (`TT`) & Barycentric Dynamical Time (`TDB`)** | `Engine.positions_tt(jd_tt, ...)` & `EphemerisAdapter.calc_tt(jd_tt, ...)` | 2-part IAU SOFA / ERFA split Julian Date `(J2000_JD, offset)`; `erfa.dtdb` & `erfa.tttdb` relativistic clock transformation | Zero civil-time or $\Delta T$ ambiguity; embedded Chebyshev kernels (`1550-2306 CE`) match full 114 MB `de440.bsp` within `<= 0.018191"` worst sampled residual (`0.007410"` in `1550-1800 CE`, `0.018191"` in `1800-2100 CE`, `0.007091"` in `2101-2306 CE`), while provisioned full `de440.bsp` matches [`docs/ACCURACY.md`](ACCURACY.md) (`<= 0.000717"` DE440 table, `<= 0.025351"` vs Horizons `DE441`). |
| **Modern Civil UTC (`1960-2026 CE`)** | `Engine.positions(datetime_utc, ...)` | Exact IAU SOFA / ERFA leap-second tables (`erfa.utctai` -> `erfa.taitt`) and IERS Bulletin A (`finals2000A.all`) `UT1 - UTC` Earth Orientation Parameters | Strict modern civil-time window; fails explicitly if required EOP data are absent rather than silently guessing. |
| **Embedded Offline DE440 Chebyshev Span (`1550-2306 CE`)** | `Engine.load(kernels="extended")` & `EphemerisAdapter.calc_ut(jd_ut, ...)` | Three bundled SHA-256-pinned Chebyshev polynomial kernels (`de440_wing_1550_1800.bin.zlib`, `de440_compact.bin.zlib`, `de440_wing_2101_2306.bin.zlib`) | Works 100% offline immediately after `pip install` across 756 years (`1550-2306 CE`) with `<= 0.018191"` worst sampled positional residual vs full 114 MB `de440.bsp` (`<= 0.036858"` worst sampled residual vs independent NASA JPL Horizons `DE441`). |
| **Deep Historical & Future Span (`3102 BCE-3000 CE`)** | `EphemerisAdapter.calc_ut(jd_ut, ...)` & `SpkReader` | When full NASA JPL `de441.bsp` (`-13200 to +17191`) is provisioned, uses numerical SPK evaluation; offline without external `.bsp`, uses Vondrak-2011 long-term precession (`+/-200,000 yr`) + Keplerian/Meeus/ELP analytical series | Covers the classical Kali Yuga epoch (`3102 BCE-02-18 00:00 UT`, `JD 588465.5`) through `3000 CE`. Offline analytical fallback accuracy outside `1550-2306 CE` is unverified against a primary ancient ephemeris unless `de441.bsp` is provisioned; see [`ROADMAP-AND-LIMITATIONS.md`](ROADMAP-AND-LIMITATIONS.md). |

---

## 2. Ayanamsha Models (21 Named Realizations with Primary Citations)

`ephemeris-oss` does not treat Ayanamsha as a single magic constant. [`AYANAMSA_CATALOG`](../src/ephemeris_oss/engine/conventions.py) implements **21 named sidereal realizations**, each documenting its defining anchor epoch, reference frame, transport model (IAU 2006/Vondrak-2011 3D ecliptic plane rotation vs linear rate), and an explicit `original_author_ambiguity` note where historical texts and later software conventions diverge:

1. **`lahiri` (IAE 1989 / Calendar Reform Committee 1955 Default):** Anchored to $23^\circ 15' 00.658''$ true (reduced to $23^\circ 14' 44.019''$ mean via IAU 1980 Wahr nutation) at `1956-03-21 00:00 TT` (`JD 2435553.5`), transported along the moving ecliptic via Vondrak-2011 / IAU 2006 precession ($23.85709235^\circ$ at `J2000.0 TT`).
2. **`lahiri_icrc`:** Calendar Reform Committee 1955 mean value $23^\circ 15' 00.0''$ at `1956-03-21 00:00 TT`.
3. **`lahiri_1940`:** Earlier N. C. Lahiri tabular realization prior to the 1989 IAE revision.
4. **`true_citra` (*Spashta Chitrapaksha*):** Dynamically locks the apparent/mean tropical longitude of Spica ($\alpha\text{ Virginis}$, Hipparcos `HIP 65474`, including proper motion and parallax) to exactly $180^\circ 00' 00''$ sidereal ($0^\circ\text{ Libra}$).
5. **`pushya`:** Anchors $\delta\text{ Cancri}$ (*Asellus Australis*, `HIP 42911`) to $106^\circ 00' 00''$ sidereal ($16^\circ\text{ Cancer}$, middle of *Pushya* Nakshatra).
6. **`raman` (B. V. Raman):** Anchored to $21^\circ 00' 55.0''$ at `1900-01-00.5` (`JD 2415020.0`) with B. V. Raman's published $50.33''/\text{Julian year}$ rate.
7. **`kp` & `kp_senthilathiban` (Krishnamurti Paddhati):** Traditional KP realization and the modern Senthilathiban realization used with the 249-sub-lord table.
8. **`yukteshwar` (Swami Sri Yukteswar, *The Holy Science*, 1894):** Anchored to spring equinox `1894 CE` at $20^\circ 54' 36''$; discloses both Sri Yukteswar's textual $54''/\text{yr}$ *Daiva Yuga* rate and modern software realizations.
9. **`fagan_bradley`:** Western sidereal standard ($24^\circ 44' 25.0''$ at `1950.0`).
10. **`true_revati` & `true_mula`:** Stellar-anchored realizations locking $\zeta\text{ Piscium}$ (*Revati*) and the Galactic Centre (*Mula*).
11. **Classical *Surya Siddhanta* & *Aryabhata* Realizations (`suryasiddhanta_*`, `aryabhata_*`):** Including traditional *Trepanation* (*Bija*-corrected and oscillating *Ayanamsha* models for historical manuscript verification).

---

## 3. House Systems (*Bhava*) & High-Latitude Geometry

`EphemerisAdapter.houses_ut()` and `Engine.houses()` implement 8 house systems with explicit polar/circumpolar safety:

- **`whole_sign` (*Rashi-Tulya Bhava*, Default Parashari Standard):** Each $30^\circ$ sidereal Rashi starting from the Rashi containing the Ascendant (*Lagna*) forms one whole house ($0^\circ..30^\circ$). Valid at all latitudes.
- **`equal` (*Samabhava*):** Twelve $30^\circ$ houses measured directly from the exact degree of the Ascendant.
- **`sripati` (*Porphyry / Sripati Paddhati*):** Divides the four diurnal/nocturnal arcs between Ascendant, Midheaven (*Dashama*), Descendant, and IC (*Patala*) into three equal segments to locate the 12 *Bhava Madhyas* (house centres), with midpoints defining the *Bhava Sandhis* (junctions).
- **`porphyry`, `placidus`, `koch`, `campanus`, and `regiomontanus`:** Quadrant systems computed on the true equator and ecliptic of date (`local_apparent_sidereal_deg`, `true_obliquity_deg`).
- **High-Latitude Integrity:** Above the Arctic/Antarctic circles where ecliptic degrees become circumpolar and do not intersect the horizon, `placidus` and `koch` **never silently substitute another house system**; they return an explicit `Undefined` status with the geometric reason.

---

## 4. Lunar Nodes: Mean (*Madhyama*) vs. True (*Spashta*) Rahu and Ketu

Both classical *Paramparas* are supported across the Python SDK, CLI, MCP Server, and REST API:

1. **Mean Rahu & Ketu (`true_node=False`, Default):**
   - Computed from Meeus, *Astronomical Algorithms* (2nd ed., Ch. 47, Eq. 47.7) in Terrestrial Time (`ephemeris-oss-lunar-nodes-1.1.0-meeus47.7`).
   - Verified against an independent arbitrary-precision `Decimal` replay across 3,612 monthly TT epochs (`1800-2100 CE`) to a median residual of `4.09272616e-10"` and max residual of `3.27418093e-09"`.
   - Mean nodes move strictly retrograde at `~ -0.05295376 deg/day`, with Ketu at the exact $180^\circ$ antipode.
2. **True / Osculating Rahu & Ketu (`true_node=True` or `body="true_node"` / `"true_rahu"` / `"true_ketu"`):**
   - Computed from the instantaneous Earth-Moon orbital angular momentum vector $\mathbf{h} = \mathbf{r} \times \mathbf{v}$ on the rotating ecliptic of date ($\mathbf{n} = \mathbf{k} \times \mathbf{h}$), capturing the Moon's true nodal wobble and temporary stationary/direct phases, with coverage-aware one-sided derivative fallback within `0.001` day of the `1550` and `2306` embedded kernel boundaries.
   - Outside the `1550-2306 CE` embedded Chebyshev window (when an external SPK file is not loaded), `_calc_ut_historical_analytical` adds the primary Meeus Ch. 47 periodic nodal series ($\Delta\Omega \approx -1.4979^\circ \sin 2(F - D) - 0.1500^\circ \sin M - 0.1226^\circ \sin 2F + 0.1176^\circ \sin 2\Omega - 0.0801^\circ \sin 2(M' - F)$).

---

## 5. Complete Jyotish Computational Stack (`jyotish/`, `almanac/`, `impossible_astrology.py`)

- **23 Divisional Charts (*Shodashvarga* `D1..D60` + 7 Higher Vargas `D5, D6, D8, D11, D72, D81, D108, D144`):** Exact classical Parashari piecewise construction, including unequal `D30` *Trimsamsa* (`[5, 5, 8, 7, 5]` odd signs; `[5, 7, 8, 5, 5]` even signs) and continuous merged cross-sign sectors for `D2`, `D10`, and `D24`.
- **8 Dasha Systems (Up to 5 Nested Levels *Maha -> Antara -> Pratyantara -> Sookshma -> Prana*):** *Vimshottari* (`120 yr`), *Ashtottari* (`108 yr`), *Yogini* (`36 yr`), *Jaimini Chara*, *Sthira*, *Shoola*, *Mandooka*, and *Tajika Mudda* (`1 yr`), with configurable solar (`365.2425` days) vs *Savana* (`360.0` days) year length.
- **6-Fold *Shadbala* & *Bhava Bala*:** *Sthana Bala* (5 sub-components), *Dig Bala*, *Kala Bala* (9 sub-components including *Yuddha Bala*), *Cheshta Bala*, *Naisargika Bala*, and *Drik Bala* in both *Virupas* and *Rupas* against BPHS minimum thresholds.
- **337-Bindu *Ashtakavarga*:** Individual *Bhinna Ashtakavarga* for all 7 physical planets + Ascendant, conserving the invariant **337 total *Sarvashtakavarga* bindus** (`Sun 48 + Moon 49 + Mars 39 + Mercury 54 + Jupiter 56 + Venus 52 + Saturn 39 = 337`), plus *Trikona Shodhana*, *Ekadhipatya Shodhana*, and *Kakshya* transit analysis.
- **86 Classical & Tajika Yogas:** 70 Parashari Yogas (*Raja, Dhana, Pancha Mahapurusha, Nabhasa, Chandra, Surya, Viparita, Neecha Bhanga, Kemadruma, Shakata*) + 16 Tajika annual Yogas (*Ithasala, Ishrafa, Nakta, Yamaya, Kamboola*).
- **Jaimini Sutras:** 7-Karaka and 8-Karaka *Chara Karaka* schemes, *Rashi Drishti*, *Arudha Padas* (`AL`, `UL`, `A1..A12` with classical 1st/7th house exception rules), *Karakamsha*, and *Swamsha*.
- **Sunrise-Anchored Regional *Drik Panchanga*:** *Tithi, Nakshatra, Yoga, Karana, Vara* anchored to the observer's active daily local sunrise (`active_sunrise_jd_ut + longitude_deg / 360.0`), plus *Rahu Kala, Yamaganda, Gulika Kala, Abhijit Muhurta, Durmuhurta, Varjyam, Amrita Kalam, Disha Shoola, Chandra/Tara Bala, Panchaka Rahita*, and *Amanta/Purnimanta* lunar months with *Adhika/Kshaya Masa* detection.
