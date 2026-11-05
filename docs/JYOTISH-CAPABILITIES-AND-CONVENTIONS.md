# Jyotish Capabilities, Lineage Conventions & Mathematical Coverage

**Engine:** `ephemeris-oss` (**RDG-Ephemeris**, in tribute to **Raj Dulari Gupta**)  
**Lineage Foundation:** Designed for real Jyotish applications with 40 years of lived traditional consultation, Panchanga, and teaching practice alongside modern clean-room astronomical software engineering.

---

## 1. Time Scales & Historical Date Regimes

Accurate Jyotish calculation requires strict separation between Earth-rotation time (`UTC` / `UT1`, which governs the observer's horizon, Ascendant, house cusps, and local sunrise) and uniform dynamical ephemeris time (`TT` / `TDB`, which governs planetary and lunar orbital equations of motion).

| Time Scale / Span | API Surface | Mathematical Realization | Scope & Precision Regime |
|---|---|---|---|
| **Explicit Terrestrial Time (`TT`) & Barycentric Dynamical Time (`TDB`)** | `Engine.positions_tt(jd_tt, ...)` & `EphemerisAdapter.calc_tt(jd_tt, ...)` | 2-part IAU SOFA / ERFA split Julian Date `(J2000_JD, offset)`; `erfa.dtdb` & `erfa.tttdb`relativistic clock transformation | Zero civil-time or $\Delta T$ ambiguity; reproduces NASA JPL DE440 to `<= 0.000717"` (`1800–2100 CE`) and `<= 0.018191"` (`1550–2306 CE` embedded Chebyshev wings). |
| **Modern Civil UTC (`1960–2026 CE`)** | `Engine.positions(datetime_utc, ...)` | Exact IAU SOFA / ERFA leap-second tables (`erfa.utctai` -> `erfa.taitt`) and IERS Bulletin A (`finals2000A.all`) `UT1 - UTC` Earth Orientation Parameters | Strict modern civil-time window; fails explicitly if required EOP data are absent rather than silently guessing. |
| **Embedded Offline DE440 Chebyshev Span (`1550–2306 CE`)** | `Engine.load(kernels="extended")` & `EphemerisAdapter.calc_ut(jd_ut, ...)` | Three bundled SHA-256-pinned Chebyshev polynomial kernels (`de440_wing_1550_1800.bin.zlib`, `de440_compact.bin.zlib`, `de440_wing_2101_2306.bin.zlib`) | Works 100% offline immediately after `pip install` across 756 years (`1550–2306 CE`) with `<= 0.018191"` max positional difference vs full 114 MB `de440.bsp`. |
| **Deep Historical & Future Span (`3102 BCE–3000 CE`)** | `EphemerisAdapter.calc_ut(jd_ut, ...)` & `SpkReader` | When full NASA JPL `de441.bsp` (`-13200 to +17191`) is provisioned, uses numerical SPK evaluation; offline without external `.bsp`, uses Vondrák-2011 long-term precession (`±200,000 yr`) + Keplerian/Meeus/ELP analytical series | Covers the classical Kali Yuga epoch (`3102 BCE-02-18 00:00 UT`, `JD 588465.5`) through `3000 CE`. See [`ROADMAP-AND-LIMITATIONS.md`](ROADMAP-AND-LIMITATIONS.md) for $\Delta T$ and analytical fallback envelopes outside `1550–2306 CE`. |

---

## 2. Ayanamsha Models (21 Named Realizations with Primary Citations)

`ephemeris-oss` does not treat Ayanamsha as a single magic constant. [`AYANAMSA_CATALOG`](../src/ephemeris_oss/engine/conventions.py) implements **21 named sidereal realizations**, each documenting its defining anchor epoch, reference frame, transport model (IAU 2006/Vondrák-2011 3D ecliptic plane rotation vs linear rate), and an explicit `original_author_ambiguity` note where historical texts and later software conventions diverge:

1. **`lahiri` (IAE 1989 / Calendar Reform Committee 1955 Default):** Anchored to $23^\circ 15' 00.658''$ true (reduced to $23^\circ 14' 44.019''$ mean via IAU 1980 Wahr nutation) at `1956-03-21 00:00 TT` (`JD 2435553.5`), transported along the moving ecliptic via Vondrák-2011 / IAU 2006 precession ($23.85709235^\circ$ at `J2000.0 TT`).
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
   - Verified against an independent arbitrary-precision `Decimal` replay across 3,612 monthly TT epochs (`1800–2100 CE`) to a median residual of `4.09272616e-10"` and max residual of `3.27418093e-09"`.
   - Mean nodes move strictly retrograde at `~ -0.05295376 deg/day`, with Ketu at the exact $180^\circ$ antipode.
2. **True / Osculating Rahu & Ketu (`true_node=True` or `body="true_node"` / `"true_rahu"` / `"true_ketu"`):**
   - Computed from the instantaneous Earth-Moon orbital angular momentum vector $\mathbf{h} = \mathbf{r} \times \mathbf{v}$ on the rotating ecliptic of date ($\mathbf{n} = \mathbf{k} \times \mathbf{h}$), capturing the Moon's true nodal wobble and temporary stationary/direct phases.
   - Pass `true_node=True` to `adapter.calc_ut(jd_ut, "rahu", true_node=True)`, `adapter.compute_complete_kundali_bundle(..., true_node=True)`, or `"true_node": true` in MCP / REST requests.

---

## 5. Complete Jyotish Application Stack Beyond Planetary Longitudes

| Domain | Module | Capabilities & Configurable Lineage Options |
|---|---|---|
| **23 Divisional Charts (*Vargas*, `D1..D144`)** | `ephemeris_oss.jyotish.vargas` | All 16 Parashari *Shodashvargas* (`D1, D2, D3, D4, D7, D9, D10, D12, D16, D20, D24, D27, D30, D40, D45, D60` with all 60 BPHS *Shashtiamsa* deity names & benefic/malefic flags, plus unequal 5-band Parashari `D30` Trimsamsa) and 7 additional Vargas (`D5, D6, D8, D11, D81, D108, D144`), 7 Special Lagnas (*Hora, Ghati, Bhava, Varnada, Sree, Pranapada, Indu*), and 12 *Arudha Padas* (`A1..A12` with *Swasthe Daraye* exception). |
| **8 Dasha Systems & 5-Level *Prana* Solver** | `ephemeris_oss.jyotish.dasha`, `jyotish_jaimini`, `jyotish_advanced` | *Vimshottari* (5 levels down to *Prana Dasha*), *Ashtottari* (28-Nakshatra *Abhijit* scheme), *Yogini* (36-year cycle), *Jaimini Chara Dasha* (with optional $+1/-1$ year exaltation/debilitation adjustment), *Sthira*, *Shoola*, *Mandooka*, and Tajika *Mudda Dasha*. Configurable year length: Gregorian solar year (`SOLAR_YEAR_DAYS = 365.2425`, default) or 360-day *Savana* year (`SAVANA_YEAR_DAYS = 360.0`). |
| **6-Fold *Shadbala* & *Bhava Bala*** | `ephemeris_oss.jyotish.shadbala` | Complete *Sthana Bala* (*Uchcha, Saptavargaja, Ojhayugmarasyamsa, Kendradi, Drekkana*), *Dig Bala*, *Kala Bala* (*Natonnata, Paksha, Tribhaga, Varsha-Masa-Dina-Hora, Ayana, Yuddha Bala* Bimba Parimana transfer), *Cheshta Bala*, *Naisargika Bala*, and *Drik Bala* in Virupas and Rupas ($60\text{ Virupas} = 1\text{ Rupa}$). |
| **337-Bindu *Ashtakavarga* & *Kakshya* Transit** | `ephemeris_oss.jyotish.ashtakavarga` | All 7 *Bhinnashtakavarga* tables ($48+49+39+54+56+52+39 = 337$ conserved *Sarvashtakavarga* bindus), *Trikona Shodhana*, *Ekadhipatya Shodhana*, *Shodhya Pinda*, 8-fold *Kakshya* ($3^\circ 45'$) transit scoring, and *Gochara Vedha* with classical Father-Son (Sun-Saturn, Moon-Mercury) exemptions. |
| **86 Classical *Parashari* & *Tajika* Yogas** | `ephemeris_oss.jyotish_advanced.yogas`, `varshphal` | 70 classical *Parashari* Yogas (*Pancha Mahapurusha, Raja, Dhana, Daridra, Nabhasa, Gajakesari, Neecha Bhanga Raja Yoga*, etc.) + 16 *Tajika* annual Yogas (*Ithasala, Ishrafa, Nakta, Yamaya, Kamboola*, etc.) with cancellation rules and explicit triggering rationale. |
| **Jaimini Sutras & *Ayurdaya*** | `ephemeris_oss.jyotish_jaimini.sutras` | 7-Karaka and 8-Karaka (*Chara Karaka*) schemes, *Karakamsa* & *Swamsa*, *Rashi Drishti* (sign aspects), *Argala* & *Virodhargala* (planetary interventions), and 3-pair *Jaimini Ayurdaya* (*Alpayu, Madhyayu, Purnayu*). |
| **Sunrise-Anchored Regional *Drik Panchanga*** | `ephemeris_oss.almanac.regional_panchang` | Daily *Udaya Tithi, Nakshatra, Yoga, Karana*, local solar weekday (*Vara* anchored to observer's active local sunrise and longitude-shifted solar day, properly handling pre-sunrise births), *Amanta* vs *Purnimanta* lunar months, *Adhika/Kshaya Masa*, *Rahu Kala / Gulika Kala / Yamaganda / Abhijit Muhurta*, and 5 regional solar calendars. |
| **Sub-Second Rectification & *Graha Yuddha*** | `ephemeris_oss.impossible_astrology`, `engine.phenomena` | Exact seconds to previous/next `D1..D60` Varga sign boundary via Illinois secant-bisection root-finding; Bayesian birth-time rectification (*Kunda* $81\times\text{Lagna}$, *Pranapada Shuddhi*, *Pancha Tattwa*, life-event Dasha triggers); multi-century *Graha Yuddha* planetary war scanner (*Surya Siddhanta* Ch. 7 & *Brihat Samhita* Ch. 17 northern-latitude and disc-diameter adjudication); and classical *Surya Siddhanta* vs NASA JPL DE440 drift analysis. |
