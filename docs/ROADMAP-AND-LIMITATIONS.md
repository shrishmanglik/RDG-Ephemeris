# Scientific Limitations, Precision Regimes & Honest Roadmap

**Package:** `ephemeris-oss` (**RDG-Ephemeris**, in tribute to **Raj Dulari Gupta**)  
**Doctrine:** Every accuracy claim in this repository is bound to a reproducible script, a SHA-256 receipt, and an explicit statement of scope and limitations. We publish what is measured, what is approximated outside the embedded kernel window, and what remains on our engineering roadmap.

---

## 1. The Three Precision Regimes Across Time (`3102 BCE` to `3000 CE`)

Users and researchers should distinguish the three distinct calculation regimes supported by `ephemeris-oss`:

| Regime | Date Span | Data Source | Measured Positional Fidelity & Scope |
|---|---|---|---|
| **Regime A1: Core Embedded Chebyshev DE440 (`1800-2100 CE`)** | `1800-01-01` to `2100-01-01 TT` | Bundled `de440_compact.bin.zlib` (~1.84 MB) | **`<= 0.018191 arcsec` worst sampled residual** against SHA-256-pinned full 114 MB NASA JPL `de440.bsp` in matched observer-free apparent ecliptic coordinates (`Moon worst 0.018191 arcsec` at `JD 2464185.0 TT`; `0.007944 arcsec` at calendar-month start `JD 2464175.5 TT`; `Sun 0.000397 arcsec` at `JD 2451545.0 TT`). Note that [`docs/ACCURACY.md`](ACCURACY.md)'s `0.000717 arcsec` Moon DE440 column and `0.025351 arcsec` Horizons `DE441` column come from the retained full-kernel accuracy study (`Engine.load(kernels={"DE440": de440.bsp})`), whereas [`evidence/horizons-iae-benchmark.json`](../evidence/horizons-iae-benchmark.json) measures the live embedded Chebyshev kernel against Horizons `DE441` (`<= 0.036858 arcsec` worst error, `0.000233 arcsec` median, `0.009849 arcsec` P95 across 2,100 rows). This is sampled numerical validation, not a claim of continuous all-epoch proof or perfect physical prediction. |
| **Regime A2: Extended Embedded Chebyshev Wings (`1550-1800 CE` & `2101-2306 CE`)** | `1550-01-01` to `2306-01-01 TT` | Bundled `de440_wing_1550_1800.bin.zlib` (~2.64 MB) & `de440_wing_2101_2306.bin.zlib` (~2.19 MB) | **`<= 0.018191 arcsec` worst sampled residual** across 3,864 live body-epoch evaluations (`552` epochs x `7` bodies across `1550-2306 CE`) vs full 114 MB `de440.bsp` (`0.007410 arcsec` max in `1550-1800 CE`; `0.018191 arcsec` max in `1800-2100 CE`; `0.007091 arcsec` max in `2101-2306 CE`). **Note on Pre-1600 Nutation:** Because the IAU 2000A nutation validation window in `Engine.positions_tt` is bounded to `1600-2400 CE` (`+/-4` centuries from J2000), direct TT calls in `1550-1599 CE` use `mean_equinox=True` with explicit `jd_tdb`. |
| **Regime B: Full Provisioned NASA JPL SPK (`-13200 to +17191`)** | `1550-2650 CE` (`de440.bsp`) or `-13200 to +17191` (`de441.bsp`) | External NASA NAIF `.bsp` files fetched via `ephemeris-oss kernels fetch --verify` or loaded via `SpkReader` | Direct evaluation of NASA JPL DAF/SPK Type 2 Chebyshev segments in Terrestrial/Barycentric Dynamical Time (`TT`/`TDB`). In the retained [`docs/ACCURACY.md`](ACCURACY.md) 3,612-month study (`1800-2100 CE`), full `de440.bsp` achieves `<= 0.000717 arcsec` worst sampled residual (`0.000019 arcsec` median) and `<= 0.025351 arcsec` worst sampled residual against independent Horizons `DE441`. |
| **Regime C: Offline Analytical Fallback Outside `1550-2306 CE` (Without External `.bsp`)** | `3102 BCE` (`JD 588465.5`) to `1549 CE` & `2307 CE` to `3000 CE` | Built-in `Vondrak-2011` precession (`erfa.ltp` / `erfa.ltecm`, valid `+/-200,000 yr`) + truncated Keplerian / Meeus / ELP analytical series | **Important Limitation:** While Vondrak-2011 models Earth's precession axis over multi-millennium spans, the offline analytical planetary and lunar series used when `de441.bsp` is not downloaded on disk are truncated analytical approximations (`ephemeris_source = "vondrak2011-analytical"`). Their multi-millennium positional error envelope is **UNVERIFIED against a primary ancient numerical ephemeris** unless an external NASA JPL `de441.bsp` SPK kernel is provisioned, and no all-epoch/all-body accuracy ceiling or Rashi/Varga sign-boundary stability guarantee is claimed for the analytical fallback. For verified numerical research outside `1550-2306 CE`, provision `de441.bsp`. |

---

## 2. Known Scientific & Astronomical Boundaries

1. **Planetary System Barycentres (`NAIF 4/5/6`) vs. Planet Physical Centres (`NAIF 499/599/699`):**
   - Following standard NASA JPL `DE440` / `DE441` SPK packaging, the targets for Mars (`NAIF 4`), Jupiter (`NAIF 5`), and Saturn (`NAIF 6`) in the planetary ephemeris are the **planetary system barycentres** (centre of mass of the planet plus its satellites), whereas Mercury (`199`), Venus (`299`), Moon (`301`), and Earth (`399`) are physical body centres.
   - For Mars, the system barycentre differs from the physical centre by `< 0.001 arcsec`. For Jupiter (displaced by Galilean moons Io, Europa, Ganymede, Callisto) and Saturn (displaced by Titan), the geocentric offset between the system barycentre and the planet's physical disk centre can reach **`~0.15 to 0.45 arcsec`**. Our benchmarks against JPL `DE440` and Horizons `DE441` evaluate the exact matched `NAIF 4/5/6` system barycentres (`docs/ACCURACY.md`).
2. **Geophysical $\Delta T$ (`TT - UT1`) Uncertainty in Deep Antiquity (`3102 BCE`):**
   - Earth's rotational deceleration (tidal friction and post-glacial rebound) is not strictly constant over millennia. Outside the modern IERS atomic-clock window (`1960-2026 CE`), `EphemerisAdapter` uses standard Espenak & Meeus (2006) five-millennium $\Delta T$ polynomials.
   - At `3102 BCE`, empirical $\Delta T$ extrapolation carries an intrinsic geophysical uncertainty of **several hours ($\pm 10^4\text{ seconds}$)** in Earth rotation angle (`UT1`). While `TT` coordinate transformations remain 100% deterministic, any `UT1`-dependent quantity in deep antiquity (specifically the **Ascendant / House Cusps** and the fast-moving **Moon**) is bounded by modern geophysical knowledge of ancient Earth rotation.
3. **Solar Occultation Gravitational Deflection Cutoff:**
   - As documented in [`docs/ACCURACY.md`](ACCURACY.md), when a superior planet is occulted behind the solar photosphere (such as Mercury in November 2094), relativistic solar gravitational light deflection switches off at the opaque solar photosphere radius to match the observed NASA JPL Horizons quantity-45 convention.
4. **Browser Pure-ESM SDK vs. Native Python / Rust / WASM Kernels:**
   - The zero-dependency browser ES module (`web/ephemeris-browser.js`) includes both a WebAssembly/SPK binary reader (`readSpkState`) and a pure-JavaScript analytical calculator for instant client-side rendering without large network payloads. When running in pure-JS analytical mode without a loaded `.bsp` / `.ephc` binary buffer, it operates in the analytical precision regime rather than the `<= 0.018191"` embedded Python DE440 Chebyshev regime.
5. **Clean-Room Third-Party Non-Execution:**
   - To preserve strict clean-room provenance (`tools/check_provenance.py`), third-party copyleft C ephemeris libraries and their `.se1` data tables are never installed, linked, or executed inside this repository. In [`README.md`](../README.md) and [`evidence/sota-ephemeris-evaluation-matrix.json`](../evidence/sota-ephemeris-evaluation-matrix.json), numeric accuracy cells for unexecuted third-party libraries are explicitly marked `UNKNOWN (not executed in this clean-room repository)`.
6. **IAE 1989 / CSIR 1955 Lahiri Anchor Classification:**
   - In [`tools/benchmark_horizons_iae.py`](../tools/benchmark_horizons_iae.py), the `1956-03-21 00:00 TT` (`23 deg 15' 00.658"` IAU 1980 true -> `23 deg 14' 44.019"` mean) and `J2000.0 TT` (`23.85709235 deg`) Lahiri evaluations are classified strictly as **`CONVENTION_REGRESSION_ONLY`** (`independent_external_verification: false`), verifying mathematical self-consistency of our precession/nutation transport rather than claiming an independent external physical measurement.

---

## 3. Recently Completed Next-Level Capabilities & Remaining Roadmap

### Shipped in Current Release (`ephemeris-oss` v0.2 SOTA Suite)
1. **BPHS Kalachakra Dasha Engine (`jyotish/dasha.py` -> `compute_kalachakra_dasha`):**
   - Full implementation of the classical *Brihat Parashara Hora Shastra* "Wheel of Time" Dasha across all 27 Nakshatras x 4 Padas (*Savya* and *Apasavya* 9-sign progressions, Paramayus `83/85/86/100` years, *Deha* and *Jeeva* vitality signs, and *Mandooka / Markata / Simhavalokana Gati* sign jumps).
2. **30-Star Gaia/Hipparcos ICRS Yogatara Catalog, Stellar Piercing (`Rohini Shakata Bheda`) & Heliacal Visibility (`engine/stellar_anchors.py` & `impossible_astrology.py`):**
   - Complete 6-parameter ICRS J2000 astrometry (RA, Dec, proper motion $\mu_\alpha^*, \mu_\delta$, parallax $\pi$, radial velocity $v_r$) for all 27 Nakshatra Yogataras + 28th *Abhijit* (Vega) + *Agastya* (Canopus) + *Lubdhaka* (Sirius), propagated via `erfa.pmsafe` and `erfa.apci13` with *Tara Bheda*, *Rohini Shakata Bheda*, and *Kalansha* heliacal visibility (*Udaya/Asta*).
3. **Planetary Satellite-to-Physical-Centre Offset Corrections (`NAIF 499 / 599 / 699` via `physical_center=True`):**
   - `EphemerisAdapter.calc_ut(..., physical_center=True)` (or body aliases `"mars_center"`, `"jupiter_center"`, `"saturn_center"`, `"499"`, `"599"`, `"699"`) applies satellite-barycentre recoil corrections for the Galilean moons (Io, Europa, Ganymede, Callisto) on Jupiter (`NAIF 599`), Titan/Rhea/Iapetus on Saturn (`NAIF 699`), and Phobos on Mars (`NAIF 499`), while keeping `physical_center=False` (`NAIF 4/5/6` system barycentres) as the default for exact NASA JPL `DE440` SPK regression parity.
4. **Exact `Krantisamya` (`Vyatipata` & `Vaidhriti Mahapata`) Declination-Equality Solver (`solve_krantisamya_mahapata_windows`):**
   - Sub-second root solver for classical *Surya Siddhanta* (*Pata Adhikara*) solar-lunar equatorial declination equality ($\delta_{\text{Sun}} = \pm \delta_{\text{Moon}}$).
5. **Inverse Sky-to-Date "Astronomical Time-Machine" Solver (`solve_chart_date_from_planetary_constraints`):**
   - Hierarchical orbital-period sieve (`3102 BCE` to `3000 CE`) that dates undated historical horoscopes, manuscripts, and inscriptions from planetary sign and Nakshatra constraints.
6. **Triple-Lock Life-Event Peak Window Convergence Solver (`compute_triple_lock_life_event_convergence`):**
   - Synthesizes Lock 1 (Multi-Dasha Natal Promise: Vimshottari + Kalachakra Deha/Jeeva + Jaimini Chara) + Lock 2 (Guru-Shani Double Transit Gochara Lock) + Lock 3 (Ashtakavarga 8-Kakshya Bindu & Bhrigu Bindu Trigger) into ranked `0..100` peak manifestation windows.

### Remaining Engineering Roadmap (Upcoming Releases)
1. **Embedded Ancient Chebyshev Wing Kernels (`3102 BCE to 1550 CE` from NASA JPL `DE441`):**
   - Currently, sub-arcsecond numerical integration prior to `1550 CE` requires provisioning the external `de441.bsp` kernel. We plan to publish an optional `ephemeris-oss-ancient-wings` data package containing compressed Chebyshev polynomial fits covering `3102 BCE to 1550 CE` so deep-antiquity numerical precision works without a 3.3 GB SPK download.
2. **Minor Planets, Asteroids & Additional Upagrahas:**
   - Support for user-supplied NASA JPL small-body SPK files (Chiron, Ceres, Pallas, Juno, Vesta) in the high-level `EphemerisAdapter` and MCP/REST tools.
3. **Production Multi-Tenant Deployment Reference for `rdg-ephemeris-api`:**
   - `rdg-ephemeris-api` uses Python's standard-library `ThreadingHTTPServer` for zero-dependency portability (`1 MB` request body limit, full OpenAPI 3.1 schema). For high-concurrency public internet deployment, it should be run behind a reverse proxy or ASGI worker pool (e.g., Nginx / Envoy / Gunicorn).
