# Scientific Limitations, Precision Regimes & Honest Roadmap

**Package:** `ephemeris-oss` (**RDG-Ephemeris**, in tribute to **Raj Dulari Gupta**)  
**Doctrine:** Every accuracy claim in this repository is bound to a reproducible script, a SHA-256 receipt, and an explicit statement of scope and limitations. We publish what is measured, what is approximated outside the embedded kernel window, and what remains on our engineering roadmap.

---

## 1. The Three Precision Regimes Across Time (`3102 BCE` to `3000 CE`)

Users and researchers should distinguish the three distinct calculation regimes supported by `ephemeris-oss`:

| Regime | Date Span | Data Source | Measured Positional Fidelity & Scope |
|---|---|---|---|
| **Regime A1: Core Embedded Chebyshev DE440 (`1800–2100 CE`)** | `1800-01-01` to `2100-01-01 TT` | Bundled `de440_compact.bin.zlib` (~1.84 MB) | **`<= 0.000717 arcsec` worst error** (`0.000019 arcsec` median) across 3,612 monthly TT epochs per physical graha vs full 114 MB NASA JPL `de440.bsp`. Against independent NASA JPL Horizons `DE441` (`2,100` apparent ICRF rows), full `de440.bsp` reaches `<= 0.025351 arcsec` worst error (Moon) and live embedded Chebyshev reaches `<= 0.036858 arcsec` worst error (`0.000233 arcsec` median, `0.009849 arcsec` P95). |
| **Regime A2: Extended Embedded Chebyshev Wings (`1550–1800 CE` & `2101–2306 CE`)** | `1550-01-01` to `2306-01-01 TT` | Bundled `de440_wing_1550_1800.bin.zlib` (~2.64 MB) & `de440_wing_2101_2306.bin.zlib` (~2.19 MB) | **`<= 0.018191 arcsec` worst error** across 3,864 live body-epoch evaluations (`552` epochs × `7` bodies) vs full 114 MB `de440.bsp` (`0.007410 arcsec` max in `1550–1800 CE`; `0.007091 arcsec` max in `2101–2306 CE`). **Note on Pre-1600 Nutation:** Because the IAU 2000A nutation validation window in `Engine.positions_tt` is bounded to `1600–2400 CE` (`±4` centuries from J2000), direct TT calls in `1550–1599 CE` use `mean_equinox=True` with explicit `jd_tdb`. |
| **Regime B: Full Provisioned NASA JPL SPK (`-13200 to +17191`)** | `1550–2650 CE` (`de440.bsp`) or `-13200 to +17191` (`de441.bsp`) | External NASA NAIF `.bsp` files fetched via `ephemeris-oss kernels fetch --verify` or loaded via `SpkReader` | Direct evaluation of NASA JPL DAF/SPK Type 2 Chebyshev segments in Terrestrial/Barycentric Dynamical Time (`TT`/`TDB`), providing full JPL numerical integration accuracy across multi-millennium historical and future spans. |
| **Regime C: Offline Analytical Fallback Outside `1550–2306 CE` (Without External `.bsp`)** | `3102 BCE` (`JD 588465.5`) to `1549 CE` & `2307 CE` to `3000 CE` | Built-in `Vondrák-2011` precession (`erfa.ltp` / `erfa.ltecm`, valid `±200,000 yr`) + truncated Keplerian / Meeus / ELP analytical series | **Important Limitation:** While Vondrák-2011 models Earth's precession axis to high long-term accuracy, the offline analytical planetary and lunar series used when `de441.bsp` is not downloaded on disk are truncated analytical approximations (`ephemeris_source = "vondrak2011-analytical"`). In deep antiquity (`3102 BCE`, `499 CE`), offline analytical planetary longitudes have an accuracy envelope of **several arcminutes to ~0.5°** (sufficient for Rashi sign and historical Siddhanta comparison, but **not** arcsecond JPL precision). For sub-arcsecond historical research prior to `1550 CE`, provision `de441.bsp`. |

---

## 2. Known Scientific & Astronomical Boundaries

1. **Planetary System Barycentres (`NAIF 4/5/6`) vs. Planet Physical Centres (`NAIF 499/599/699`):**
   - Following standard NASA JPL `DE440` / `DE441` SPK packaging, the targets for Mars (`NAIF 4`), Jupiter (`NAIF 5`), and Saturn (`NAIF 6`) in the planetary ephemeris are the **planetary system barycentres** (centre of mass of the planet plus its satellites), whereas Mercury (`199`), Venus (`299`), Moon (`301`), and Earth (`399`) are physical body centres.
   - For Mars, the system barycentre differs from the physical centre by `< 0.001 arcsec`. For Jupiter (displaced by Galilean moons Io, Europa, Ganymede, Callisto) and Saturn (displaced by Titan), the geocentric offset between the system barycentre and the planet's physical disk centre can reach **`~0.15 to 0.45 arcsec`**. Our benchmarks against JPL `DE440` and Horizons `DE441` evaluate the exact matched `NAIF 4/5/6` system barycentres (`docs/ACCURACY.md`).
2. **Geophysical $\Delta T$ (`TT - UT1`) Uncertainty in Deep Antiquity (`3102 BCE`):**
   - Earth's rotational deceleration (tidal friction and post-glacial rebound) is not strictly constant over millennia. Outside the modern IERS atomic-clock window (`1960–2026 CE`), `EphemerisAdapter` uses standard Espenak & Meeus (2006) five-millennium $\Delta T$ polynomials.
   - At `3102 BCE`, empirical $\Delta T$ extrapolation carries an intrinsic geophysical uncertainty of **several hours ($\pm 10^4\text{ seconds}$)** in Earth rotation angle (`UT1`). While `TT` coordinate transformations remain 100% deterministic, any `UT1`-dependent quantity in deep antiquity (specifically the **Ascendant / House Cusps** and the fast-moving **Moon**) is bounded by modern geophysical knowledge of ancient Earth rotation.
3. **Solar Occultation Gravitational Deflection Cutoff:**
   - As documented in [`docs/ACCURACY.md`](ACCURACY.md), when a superior planet is occulted behind the solar photosphere (such as Mercury in November 2094), relativistic solar gravitational light deflection switches off at the opaque solar photosphere radius to match the observed NASA JPL Horizons quantity-45 convention.
4. **Browser Pure-ESM SDK vs. Native Python / Rust / WASM Kernels:**
   - The zero-dependency browser ES module (`web/ephemeris-browser.js`) includes both a WebAssembly/SPK binary reader (`readSpkState`) and a pure-JavaScript analytical calculator for instant client-side rendering without large network payloads. When running in pure-JS analytical mode without a loaded `.bsp` / `.ephc` binary buffer, it operates in the analytical precision regime rather than the `<= 0.018"` embedded Python DE440 Chebyshev regime.
5. **Clean-Room Third-Party Non-Execution:**
   - To preserve strict clean-room provenance (`tools/check_provenance.py`), third-party copyleft C ephemeris libraries and their `.se1` data tables are never installed, linked, or executed inside this repository. In [`README.md`](../README.md) and [`evidence/sota-ephemeris-evaluation-matrix.json`](../evidence/sota-ephemeris-evaluation-matrix.json), numeric accuracy cells for unexecuted third-party libraries are explicitly marked `UNKNOWN (not executed in this clean-room repository)`.
6. **IAE 1989 / CSIR 1955 Lahiri Anchor Classification:**
   - In [`tools/benchmark_horizons_iae.py`](../tools/benchmark_horizons_iae.py), the `1956-03-21 00:00 TT` (`23° 15' 00.658"` IAU 1980 true -> `23° 14' 44.019"` mean) and `J2000.0 TT` (`23.85709235°`) Lahiri evaluations are classified strictly as **`CONVENTION_REGRESSION_ONLY`** (`independent_external_verification: false`), verifying mathematical self-consistency of our precession/nutation transport rather than claiming an independent external physical measurement.

---

## 3. Honest Engineering Roadmap (Missing or Upcoming Features)

The following capabilities are not yet bundled in the default wheel and are scheduled on the public engineering roadmap:

1. **Kalachakra Dasha Engine (`jyotish/dasha.py`):**
   - While 8 Dasha systems (*Vimshottari, Ashtottari, Yogini, Jaimini Chara, Sthira, Shoola, Mandooka, and Tajika Mudda*) are fully implemented and tested, the full *BPHS Kalachakra Dasha* (*Savya/Apasavya* quarter-pada progressions, *Deha/Jeeva* signs, and *Mandooka/Markata/Simhavalokana Gati* jumps) is planned for an upcoming minor release.
2. **Embedded Ancient Chebyshev Wing Kernels (`3102 BCE to 1550 CE` from NASA JPL `DE441`):**
   - Currently, sub-arcsecond numerical integration prior to `1550 CE` requires provisioning the external `de441.bsp` kernel. We plan to publish an optional `ephemeris-oss-ancient-wings` data package containing compressed Chebyshev polynomial fits covering `3102 BCE to 1550 CE` so deep-antiquity numerical precision works without a 3.3 GB SPK download.
3. **Planetary Satellite-to-Centre Offset Corrections (`NAIF 499 / 599 / 699`):**
   - Optional satellite-barycentre correction polynomials (`MAR097`, `JUP365`, `SAT441`) for applications requiring sub-arcsecond physical disk-centre coordinates of Jupiter and Saturn in addition to their `DE440` system barycentres.
4. **Minor Planets, Asteroids & Additional Upagrahas:**
   - Support for user-supplied NASA JPL small-body SPK files (Chiron, Ceres, Pallas, Juno, Vesta) in the high-level `EphemerisAdapter` and MCP/REST tools.
5. **Production Multi-Tenant Deployment Reference for `rdg-ephemeris-api`:**
   - `rdg-ephemeris-api` uses Python's standard-library `ThreadingHTTPServer` for zero-dependency portability (`1 MB` request body limit, full OpenAPI 3.1 schema). For high-concurrency public internet deployment, it should be run behind a reverse proxy or ASGI worker pool (e.g., Nginx / Envoy / Gunicorn).
