# RDG Ephemeris — Human-Readable Classical *Nirayana* & *Sayana* Ephemeris & Pt. Maheshji's Jyotish Academy Manual Calculation Compendium (2026-11)

> **For Practising Jyotishis, Positional Astronomers, Classical Researchers, and Students of Pt. Maheshji's Jyotish Academy:**
> Before computers existed, every master astrologer cast a *Kundali* (natal chart), *Shodashvarga* (16 divisional charts), *Panchanga* (5-limb daily almanac), *Vishesha Lagnas* (8 special ascendants), *Upagrahas* (11 shadow planets), *KP 249 Sub-Lords*, *Jaimini Arudha Padas & Chara Karakas*, *Vimshottari/Yogini/Ashtottari/Kalachakra Dashas*, *Shadbala* (6-fold planetary strength), *Ashtakavarga* (337-bindu transit grid), *Ayurdaya* (longevity), and *Tajika Varshphal* (annual solar return with 36 Sahams) **entirely by hand** using printed ephemeris tables. This 20-chapter master volume restores that unbroken lineage with sub-arcsecond NASA JPL DE440/DE441 astronomical precision.

## Master Document Metadata & Cryptographic Provenance Receipt
- **Ephemeris Month & Year:** `2026-11` (`20 Complete Chapters`)
- **Daily Tabular Reference Epoch:** `05:30:00 IST (00:00:00 UTC)`
- **Reference Meridian / Location:** Latitude `23.1765°`, Longitude `75.7885°` (UTC`+5.50h` — Ujjain Mahakaleshwar Prime Meridian)
- **Primary Sidereal Ayanamsha:** `lahiri` (Chitrapaksha / IAE 1989 Lahiri Standard + 25-Ayanamsha Conversion Table in Chapter 1)
- **Astronomical Kernel Backbone:** NASA JPL DE440 / DE441 + IAU 2006/2000A Precession-Nutation (`ephemeris-oss v0.2.0.dev1`)
- **Cryptographic SHA-256 Receipt:** `sha256:21e2f634318de88bd7610e870cdefbd3b3e7ec65bf9db5abc72c0fc82bec694b`

## Chapter 1 — Fundamental Astronomical Constants, Julian Day Tables (`1900–2050`), $\Delta T$, & 25-Ayanamsha Master Conversion Table

### Table 1A — Fundamental Astronomical & Vedic Siddhantic Constants

| Constant / Parameter | Exact Numerical Value | Classical / IAU Standard Reference |
|---|---|---|
| **J2000.0 Fundamental Epoch** | `JD 2451545.0 TT` (`2000-01-01 12:00:00 TT`) | IAU 2006 / 2000A Standard Epoch |
| **Kali Yuga Fundamental Epoch** | `JD 588465.5 UT` (`3102 BCE Feb 18 00:00 Ujjain`) | *Surya Siddhanta* & *Aryabhatiya* |
| **Astronomical Unit ($1\text{ AU}$)** | `149,597,870.700 km` (exact) | IAU 2012 Resolution B2 |
| **Speed of Light ($c$)** | `299,792.458 km/s` (`173.144632674 AU/day`) | IAU / SI Exact Constant |
| **Mean Obliquity at J2000.0 ($\varepsilon_0$)** | `23° 26' 21.406"` (`84381.406"`) | Capitaine et al. (2003) / IAU 2006 |
| **General Precession Rate ($p_A$ at J2000)** | `50.28796195" / Julian year` (`1° in 71.5877 years`) | IAU 2006 Precession Model |
| **Mean Tropical Year ($Y_{\text{trop}}$)** | `365.24218967 days` (`365d 05h 48m 45.2s`) | Simon et al. (1994) |
| **Mean Sidereal Year ($Y_{\text{sid}}$)** | `365.256363004 days` (`365d 06h 09m 09.8s`) | IAU Standard Sidereal Year |
| **Surya Siddhanta Sidereal Year** | `365.25875648 days` (`365d 15g 31p 31.4v`) | `1,577,917,828 / 4,320,000` Savana days |
| **Mean Synodic Lunar Month** | `29.530588853 days` (`29d 12h 44m 02.9s`) | Mean New Moon to New Moon |
| **Mean Sidereal Lunar Month** | `27.321661547 days` (`27d 07h 43m 11.6s`) | `1 Nakshatra` $\approx 24\text{h } 18\text{m}$ |
| **Vedic Time Units (*Ghati / Pala / Vipala*)** | `1 Day = 60 Ghatis = 3,600 Palas = 216,000 Vipalas` | `1 Ghati = 24 min`, `1 Pala = 24 sec`, `1 Vipala = 0.4 sec` |

### Table 1B — Master 25-Ayanamsha Reference & Conversion Table (Evaluated at Epoch `2026-11-01 00:00 UTC`)

**How to Convert Any Position in This Compendium to Another Ayanamsha:** Every sidereal table in this book is printed in **Chitrapaksha / Lahiri (`IAE 1989`)**. To convert any longitude to another Ayanamsha, simply **subtract $\Delta = (\text{Target Ayanamsha} - \text{Lahiri Ayanamsha})$** listed in the column below:

| # | Ayanamsha Key | Canonical Name & Lineage | Value on `2026-11-01` (`DD° MM' SS"`) | Decimal (`deg`) | Offset vs Lahiri ($\Delta = A - A_{\text{Lahiri}}$) | Precession / Anchor Model |
|---|---|---|---|---|---|---|
| **01** | `lahiri` | **Lahiri / Chitra Paksha (mean)** | `24° 13' 55"` | `24.231932°` | `+00° 00' 00"` | published_lahiri_anchor |
| **02** | `raman` | **Raman (Hand/NOVA modern realization)** | `22° 47' 08"` | `22.785630°` | `-01° 26' 47"` | modern_reference_ecliptic |
| **03** | `kp` | **KP (Hand/NOVA modern realization)** | `24° 08' 06"` | `24.135079°` | `-00° 05' 49"` | modern_reference_ecliptic |
| **04** | `yukteshwar` | **Yukteshwar (Cochrane/Dawson modern realization)** | `22° 51' 13"` | `22.853642°` | `-01° 22' 42"` | modern_reference_ecliptic |
| **05** | `fagan_bradley` | **Fagan-Bradley (published1950 anchor)** | `25° 06' 55"` | `25.115139°` | `+00° 53' 00"` | modern_reference_ecliptic |
| **06** | `true_citra` | **True Citra (Spica)** | `24° 12' 37"` | `24.210336°` | `-00° 01' 18"` | star_anchor |
| **07** | `pushya` | **Pushya Paksha (Delta Cancri)** | `23° 05' 50"` | `23.097182°` | `-01° 08' 05"` | star_anchor |
| **08** | `lahiri_icrc` | **Lahiri ICRC (1956 realization)** | `24° 13' 54"` | `24.231749°` | `-00° 00' 01"` | modern_reference_ecliptic |
| **09** | `lahiri_1940` | **Lahiri 1940 realization** | `24° 13' 03"` | `24.217393°` | `-00° 00' 52"` | modern_reference_ecliptic |
| **10** | `kp_senthilathiban` | **KP Senthilathiban realization** | `24° 09' 19"` | `24.155202°` | `-00° 04' 36"` | modern_reference_ecliptic |
| **11** | `sassanian` | **Sassanian (Mercier modern realization)** | `20° 22' 04"` | `20.367800°` | `-03° 51' 51"` | modern_reference_ecliptic |
| **12** | `galactic_equator_iau1958` | **IAU1958 transformed galactic plane** | `210° 24' 00"` | `210.400063°` | `+186° 10' 05"` | galactic_plane |
| **13** | `galactic_equator_modern` | **Liu/Zhu/Zhang proposed ICRS galactic plane** | `210° 27' 11"` | `210.452929°` | `+186° 13' 16"` | galactic_plane |
| **14** | `ardra_galactic_plane` | **Ardra / middle Mula galactic intersection** | `203° 47' 11"` | `203.786263°` | `+179° 33' 16"` | galactic_plane |
| **15** | `suryasiddhanta_equinox` | **Surya-Siddhanta equinox** | `21° 16' 12"` | `21.269897°` | `-02° 57' 43"` | modern_reference_ecliptic |
| **16** | `suryasiddhanta_mean_sun` | **Surya-Siddhanta mean Sun** | `21° 03' 19"` | `21.055263°` | `-03° 10' 36"` | modern_reference_ecliptic |
| **17** | `aryabhata_equinox` | **Aryabhata equinox** | `21° 16' 12"` | `21.269898°` | `-02° 57' 43"` | modern_reference_ecliptic |
| **18** | `aryabhata_mean_sun` | **Aryabhata mean Sun** | `21° 01' 56"` | `21.032265°` | `-03° 11' 59"` | modern_reference_ecliptic |
| **19** | `aryabhata_522` | **Aryabhata / Govindasvamin 522** | `20° 57' 02"` | `20.950685°` | `-03° 16' 52"` | modern_reference_ecliptic |
| **20** | `suryasiddhanta_revati` | **Surya-Siddhanta Revati polar realization** | `20° 28' 42"` | `20.478226°` | `-03° 45' 13"` | modern_reference_ecliptic |
| **21** | `suryasiddhanta_citra` | **Surya-Siddhanta Citra polar realization** | `23° 22' 50"` | `23.380601°` | `-00° 51' 05"` | modern_reference_ecliptic |

### Table 1C — Manual Julian Day Number (`JDN`) Lookup Table for Years `1900` to `2050` (`Jan 0.0 UTC`)

**How to Compute Any Julian Date (`JD`) by Hand:**
$$\text{JD} = \text{JD}_{\text{Jan 0.0}}(\text{Year}) + \text{Month Offset (Table 1D)} + \text{Day of Month} + \frac{\text{UTC Hours}}{24}$$

| Year | `JD (Jan 0.0)` | Year | `JD (Jan 0.0)` | Year | `JD (Jan 0.0)` | Year | `JD (Jan 0.0)` | Year | `JD (Jan 0.0)` |
|---|---|---|---|---|---|---|---|---|---|
| **1900** | `2415019.5` | **1930** | `2425976.5` | **1960*** | `2436933.5` | **1990** | `2447891.5` | **2020*** | `2458848.5` |
| **1901** | `2415384.5` | **1931** | `2426341.5` | **1961** | `2437299.5` | **1991** | `2448256.5` | **2021** | `2459214.5` |
| **1902** | `2415749.5` | **1932*** | `2426706.5` | **1962** | `2437664.5` | **1992*** | `2448621.5` | **2022** | `2459579.5` |
| **1903** | `2416114.5` | **1933** | `2427072.5` | **1963** | `2438029.5` | **1993** | `2448987.5` | **2023** | `2459944.5` |
| **1904*** | `2416479.5` | **1934** | `2427437.5` | **1964*** | `2438394.5` | **1994** | `2449352.5` | **2024*** | `2460309.5` |
| **1905** | `2416845.5` | **1935** | `2427802.5` | **1965** | `2438760.5` | **1995** | `2449717.5` | **2025** | `2460675.5` |
| **1906** | `2417210.5` | **1936*** | `2428167.5` | **1966** | `2439125.5` | **1996*** | `2450082.5` | **2026** | `2461040.5` |
| **1907** | `2417575.5` | **1937** | `2428533.5` | **1967** | `2439490.5` | **1997** | `2450448.5` | **2027** | `2461405.5` |
| **1908*** | `2417940.5` | **1938** | `2428898.5` | **1968*** | `2439855.5` | **1998** | `2450813.5` | **2028*** | `2461770.5` |
| **1909** | `2418306.5` | **1939** | `2429263.5` | **1969** | `2440221.5` | **1999** | `2451178.5` | **2029** | `2462136.5` |
| **1910** | `2418671.5` | **1940*** | `2429628.5` | **1970** | `2440586.5` | **2000*** | `2451543.5` | **2030** | `2462501.5` |
| **1911** | `2419036.5` | **1941** | `2429994.5` | **1971** | `2440951.5` | **2001** | `2451909.5` | **2031** | `2462866.5` |
| **1912*** | `2419401.5` | **1942** | `2430359.5` | **1972*** | `2441316.5` | **2002** | `2452274.5` | **2032*** | `2463231.5` |
| **1913** | `2419767.5` | **1943** | `2430724.5` | **1973** | `2441682.5` | **2003** | `2452639.5` | **2033** | `2463597.5` |
| **1914** | `2420132.5` | **1944*** | `2431089.5` | **1974** | `2442047.5` | **2004*** | `2453004.5` | **2034** | `2463962.5` |
| **1915** | `2420497.5` | **1945** | `2431455.5` | **1975** | `2442412.5` | **2005** | `2453370.5` | **2035** | `2464327.5` |
| **1916*** | `2420862.5` | **1946** | `2431820.5` | **1976*** | `2442777.5` | **2006** | `2453735.5` | **2036*** | `2464692.5` |
| **1917** | `2421228.5` | **1947** | `2432185.5` | **1977** | `2443143.5` | **2007** | `2454100.5` | **2037** | `2465058.5` |
| **1918** | `2421593.5` | **1948*** | `2432550.5` | **1978** | `2443508.5` | **2008*** | `2454465.5` | **2038** | `2465423.5` |
| **1919** | `2421958.5` | **1949** | `2432916.5` | **1979** | `2443873.5` | **2009** | `2454831.5` | **2039** | `2465788.5` |
| **1920*** | `2422323.5` | **1950** | `2433281.5` | **1980*** | `2444238.5` | **2010** | `2455196.5` | **2040*** | `2466153.5` |
| **1921** | `2422689.5` | **1951** | `2433646.5` | **1981** | `2444604.5` | **2011** | `2455561.5` | **2041** | `2466519.5` |
| **1922** | `2423054.5` | **1952*** | `2434011.5` | **1982** | `2444969.5` | **2012*** | `2455926.5` | **2042** | `2466884.5` |
| **1923** | `2423419.5` | **1953** | `2434377.5` | **1983** | `2445334.5` | **2013** | `2456292.5` | **2043** | `2467249.5` |
| **1924*** | `2423784.5` | **1954** | `2434742.5` | **1984*** | `2445699.5` | **2014** | `2456657.5` | **2044*** | `2467614.5` |
| **1925** | `2424150.5` | **1955** | `2435107.5` | **1985** | `2446065.5` | **2015** | `2457022.5` | **2045** | `2467980.5` |
| **1926** | `2424515.5` | **1956*** | `2435472.5` | **1986** | `2446430.5` | **2016*** | `2457387.5` | **2046** | `2468345.5` |
| **1927** | `2424880.5` | **1957** | `2435838.5` | **1987** | `2446795.5` | **2017** | `2457753.5` | **2047** | `2468710.5` |
| **1928*** | `2425245.5` | **1958** | `2436203.5` | **1988*** | `2447160.5` | **2018** | `2458118.5` | **2048*** | `2469075.5` |
| **1929** | `2425611.5` | **1959** | `2436568.5` | **1989** | `2447526.5` | **2019** | `2458483.5` | **2049** | `2469441.5` |

### Table 1D — Cumulative Month Day-Offsets & Historical $\Delta T = \text{TT} - \text{UT1}$ Table

| Month | Regular Year Offset | Leap Year (`*`) Offset | Historical Epoch | $\Delta T = \text{TT} - \text{UT1}$ (Seconds) | $\Delta T$ (Minutes) |
|---|---|---|---|---|---|
| **January** | `+0 days` | `+0 days` | **500 BCE** | `+17203.7 s` | `+286.73 min` |
| **February** | `+31 days` | `+31 days` | **1 BCE / 0** | `+10583.6 s` | `+176.39 min` |
| **March** | `+59 days` | `+60 days` | **500 CE** | `+5710.0 s` | `+95.17 min` |
| **April** | `+90 days` | `+91 days` | **1000 CE** | `+1574.2 s` | `+26.24 min` |
| **May** | `+120 days` | `+121 days` | **1500 CE** | `+198.3 s` | `+3.31 min` |
| **June** | `+151 days` | `+152 days` | **1700 CE** | `+8.8 s` | `+0.15 min` |
| **July** | `+181 days` | `+182 days` | **1800 CE** | `+13.7 s` | `+0.23 min` |
| **August** | `+212 days` | `+213 days` | **1900 CE** | `-2.8 s` | `-0.05 min` |
| **September** | `+243 days` | `+244 days` | **1950 CE** | `+29.1 s` | `+0.48 min` |
| **October** | `+273 days` | `+274 days` | **2000 CE** | `+63.9 s` | `+1.06 min` |
| **November** | `+304 days` | `+305 days` | **2026 CE** | `+75.1 s` | `+1.25 min` |
| **December** | `+334 days` | `+335 days` | **2100 CE** | `+202.7 s` | `+3.38 min` |

## Chapter 2 — Section 1 — Daily Sidereal (*Nirayana*) & Tropical (*Sayana*) Planetary Ephemeris Grid (`05:30 IST / 00:00 UTC`)

**How to Read This Grid:** Each cell gives (1) the exact sidereal longitude in `Rashi DD° MM' SS"`, (2) the 27-Nakshatra and Pada (`P1..P4`) plus KP Sub-Lord, and (3) the signed 24-hour daily motion (`±DD° MM' SS"/d`) with status flags (`D` = Direct, `R` = Retrograde/*Vakri*, `S` = Stationary, `C` = Combust/*Asta*, `V` = *Vargottama*, `PN` = *Pushkara Navamsa*, `MB` = *Mrityu Bhaga*).

### Table 2A — Daily *Navagraha* Sidereal Longitudes, Nakshatra-Padas, & Daily Angular Velocities

| Date | Vara | Lahiri Ayanamsha | LST | Surya (Sun) | Chandra (Moon) | Mangala (Mars) | Budha (Mercury) | Guru (Jupiter) | Shukra (Venus) | Shani (Saturn) | Mean Rahu | True Rahu | Ketu |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `2026-11-01` | Ravivara | `24° 13' 55"` | `07h 44m 21s` | **Tula 14° 20' 34"**<br/>Swati P3 (D)<br/>`+01° 00' 00"/d` | **Karka 03° 14' 11"**<br/>Punarvasu P4 (D/V/PN)<br/>`+14° 07' 54"/d` | **Karka 24° 23' 15"**<br/>Ashlesha P3 (D)<br/>`+00° 30' 13"/d` | **Tula 22° 25' 38"**<br/>Vishakha P1 (R/C)<br/>`-01° 06' 23"/d` | **Simha 00° 05' 20"**<br/>Magha P1 (D)<br/>`+00° 07' 17"/d` | **Tula 02° 00' 46"**<br/>Chitra P3 (R/V)<br/>`-00° 29' 47"/d` | **Meena 15° 03' 08"**<br/>Uttara Bhadrapada P4 (R/MB)<br/>`-00° 03' 47"/d` | **Kumbha 01° 50' 22"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Kumbha 02° 42' 16"**<br/>Dhanishta P3 (R)<br/>`-00° 01' 07"/d` | **Simha 01° 50' 22"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-02` | Somavara | `24° 13' 55"` | `07h 48m 18s` | **Tula 15° 20' 34"**<br/>Swati P3 (D)<br/>`+01° 00' 02"/d` | **Karka 17° 14' 11"**<br/>Ashlesha P1 (D)<br/>`+13° 52' 15"/d` | **Karka 24° 53' 22"**<br/>Ashlesha P3 (D)<br/>`+00° 30' 01"/d` | **Tula 21° 16' 08"**<br/>Vishakha P1 (R/C)<br/>`-01° 12' 21"/d` | **Simha 00° 12' 34"**<br/>Magha P1 (D)<br/>`+00° 07' 09"/d` | **Tula 01° 31' 53"**<br/>Chitra P3 (R/V)<br/>`-00° 27' 59"/d` | **Meena 14° 59' 23"**<br/>Uttara Bhadrapada P4 (R/MB)<br/>`-00° 03' 43"/d` | **Kumbha 01° 47' 11"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Kumbha 02° 41' 50"**<br/>Dhanishta P3 (S)<br/>`+00° 00' 06"/d` | **Simha 01° 47' 11"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-03` | Mangalavara | `24° 13' 55"` | `07h 52m 14s` | **Tula 16° 20' 38"**<br/>Swati P3 (D/MB)<br/>`+01° 00' 04"/d` | **Simha 00° 58' 43"**<br/>Magha P1 (D)<br/>`+13° 37' 10"/d` | **Karka 25° 23' 17"**<br/>Ashlesha P3 (D)<br/>`+00° 29' 49"/d` | **Tula 20° 01' 33"**<br/>Vishakha P1 (R/C/MB)<br/>`-01° 16' 28"/d` | **Simha 00° 19' 38"**<br/>Magha P1 (D)<br/>`+00° 07' 00"/d` | **Tula 01° 04' 52"**<br/>Chitra P3 (R/V)<br/>`-00° 26' 02"/d` | **Meena 14° 55' 42"**<br/>Uttara Bhadrapada P4 (R/MB)<br/>`-00° 03' 38"/d` | **Kumbha 01° 44' 00"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Kumbha 02° 42' 03"**<br/>Dhanishta P3 (S)<br/>`+00° 00' 06"/d` | **Simha 01° 44' 00"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-04` | Budhavara | `24° 13' 55"` | `07h 56m 11s` | **Tula 17° 20' 43"**<br/>Swati P4 (D/PN)<br/>`+01° 00' 06"/d` | **Simha 14° 28' 48"**<br/>Purva Phalguni P1 (D/V)<br/>`+13° 23' 21"/d` | **Karka 25° 53' 00"**<br/>Ashlesha P3 (D)<br/>`+00° 29' 37"/d` | **Tula 18° 43' 54"**<br/>Swati P4 (R/C/PN)<br/>`-01° 18' 25"/d` | **Simha 00° 26' 34"**<br/>Magha P1 (D)<br/>`+00° 06' 51"/d` | **Tula 00° 39' 52"**<br/>Chitra P3 (R/V)<br/>`-00° 23' 57"/d` | **Meena 14° 52' 06"**<br/>Uttara Bhadrapada P4 (R/MB)<br/>`-00° 03' 34"/d` | **Kumbha 01° 40' 49"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Kumbha 02° 41' 36"**<br/>Dhanishta P3 (R)<br/>`-00° 01' 12"/d` | **Simha 01° 40' 49"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-05` | Guruvara | `24° 13' 56"` | `08h 00m 07s` | **Tula 18° 20' 50"**<br/>Swati P4 (D/PN)<br/>`+01° 00' 08"/d` | **Simha 27° 45' 45"**<br/>Uttara Phalguni P1 (D/PN)<br/>`+13° 10' 53"/d` | **Karka 26° 22' 31"**<br/>Ashlesha P3 (D)<br/>`+00° 29' 24"/d` | **Tula 17° 25' 32"**<br/>Swati P4 (R/C/PN)<br/>`-01° 17' 56"/d` | **Simha 00° 33' 22"**<br/>Magha P1 (D)<br/>`+00° 06' 43"/d` | **Tula 00° 17' 00"**<br/>Chitra P3 (R/V)<br/>`-00° 21' 46"/d` | **Meena 14° 48' 34"**<br/>Uttara Bhadrapada P4 (R/MB)<br/>`-00° 03' 30"/d` | **Kumbha 01° 37' 39"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Kumbha 02° 39' 18"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 33"/d` | **Simha 01° 37' 39"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-06` | Shukravara | `24° 13' 56"` | `08h 04m 04s` | **Tula 19° 20' 59"**<br/>Swati P4 (D/PN)<br/>`+01° 00' 10"/d` | **Kanya 10° 50' 49"**<br/>Hasta P1 (D/MB)<br/>`+12° 59' 28"/d` | **Karka 26° 51' 49"**<br/>Ashlesha P4 (D)<br/>`+00° 29' 11"/d` | **Tula 16° 08' 53"**<br/>Swati P3 (R/C)<br/>`-01° 14' 57"/d` | **Simha 00° 40' 01"**<br/>Magha P1 (D)<br/>`+00° 06' 34"/d` | **Kanya 29° 56' 22"**<br/>Chitra P2 (R/V)<br/>`-00° 19' 30"/d` | **Meena 14° 45' 06"**<br/>Uttara Bhadrapada P4 (R/MB)<br/>`-00° 03' 25"/d` | **Kumbha 01° 34' 28"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Kumbha 02° 34' 16"**<br/>Dhanishta P3 (R)<br/>`-00° 06' 33"/d` | **Simha 01° 34' 28"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-07` | Shanivara | `24° 13' 56"` | `08h 08m 00s` | **Tula 20° 21' 11"**<br/>Vishakha P1 (D)<br/>`+01° 00' 12"/d` | **Kanya 23° 44' 48"**<br/>Chitra P1 (D)<br/>`+12° 48' 38"/d` | **Karka 27° 20' 54"**<br/>Ashlesha P4 (D)<br/>`+00° 28' 58"/d` | **Tula 14° 56' 26"**<br/>Swati P3 (R/C)<br/>`-01° 09' 35"/d` | **Simha 00° 46' 30"**<br/>Magha P1 (D)<br/>`+00° 06' 25"/d` | **Kanya 29° 38' 03"**<br/>Chitra P2 (R/V)<br/>`-00° 17' 09"/d` | **Meena 14° 41' 43"**<br/>Uttara Bhadrapada P4 (R/MB)<br/>`-00° 03' 21"/d` | **Kumbha 01° 31' 17"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Kumbha 02° 26' 10"**<br/>Dhanishta P3 (R)<br/>`-00° 09' 36"/d` | **Simha 01° 31' 17"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-08` | Ravivara | `24° 13' 56"` | `08h 11m 57s` | **Tula 21° 21' 24"**<br/>Vishakha P1 (D)<br/>`+01° 00' 14"/d` | **Tula 06° 28' 05"**<br/>Chitra P4 (D)<br/>`+12° 37' 59"/d` | **Karka 27° 49' 45"**<br/>Ashlesha P4 (D)<br/>`+00° 28' 45"/d` | **Tula 13° 50' 27"**<br/>Swati P3 (R/C)<br/>`-01° 02' 03"/d` | **Simha 00° 52' 51"**<br/>Magha P1 (D)<br/>`+00° 06' 16"/d` | **Kanya 29° 22' 06"**<br/>Chitra P2 (R/V)<br/>`-00° 14' 45"/d` | **Meena 14° 38' 24"**<br/>Uttara Bhadrapada P4 (R/MB)<br/>`-00° 03' 16"/d` | **Kumbha 01° 28' 06"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Kumbha 02° 15' 14"**<br/>Dhanishta P3 (D)<br/>`+00° 12' 46"/d` | **Simha 01° 28' 06"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-09` | Somavara | `24° 13' 56"` | `08h 15m 54s` | **Tula 22° 21' 39"**<br/>Vishakha P1 (D)<br/>`+01° 00' 16"/d` | **Tula 19° 00' 43"**<br/>Swati P4 (D/C/PN)<br/>`+12° 27' 18"/d` | **Karka 28° 18' 23"**<br/>Ashlesha P4 (D)<br/>`+00° 28' 31"/d` | **Tula 12° 52' 55"**<br/>Swati P2 (R/C)<br/>`-00° 52' 47"/d` | **Simha 00° 59' 02"**<br/>Magha P1 (D)<br/>`+00° 06' 06"/d` | **Kanya 29° 08' 34"**<br/>Chitra P2 (R/V)<br/>`-00° 12' 19"/d` | **Meena 14° 35' 10"**<br/>Uttara Bhadrapada P4 (R/MB)<br/>`-00° 03' 11"/d` | **Kumbha 01° 24' 55"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Kumbha 02° 02' 03"**<br/>Dhanishta P3 (R)<br/>`-00° 13' 54"/d` | **Simha 01° 24' 55"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-10` | Mangalavara | `24° 13' 56"` | `08h 19m 50s` | **Tula 23° 21' 56"**<br/>Vishakha P2 (D)<br/>`+01° 00' 18"/d` | **Vrishchika 01° 22' 43"**<br/>Vishakha P4 (D/C/PN)<br/>`+12° 16' 44"/d` | **Karka 28° 46' 47"**<br/>Ashlesha P4 (D)<br/>`+00° 28' 17"/d` | **Tula 12° 05' 19"**<br/>Swati P2 (R/C)<br/>`-00° 42' 13"/d` | **Simha 01° 05' 04"**<br/>Magha P1 (D)<br/>`+00° 05' 57"/d` | **Kanya 28° 57' 29"**<br/>Chitra P2 (R/V)<br/>`-00° 09' 51"/d` | **Meena 14° 32' 01"**<br/>Uttara Bhadrapada P4 (R/MB)<br/>`-00° 03' 06"/d` | **Kumbha 01° 21' 45"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Kumbha 01° 47' 46"**<br/>Dhanishta P3 (R)<br/>`-00° 14' 27"/d` | **Simha 01° 21' 45"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-11` | Budhavara | `24° 13' 56"` | `08h 23m 47s` | **Tula 24° 22' 15"**<br/>Vishakha P2 (D)<br/>`+01° 00' 19"/d` | **Vrishchika 13° 34' 23"**<br/>Anuradha P4 (D/V/MB)<br/>`+12° 06' 43"/d` | **Karka 29° 14' 57"**<br/>Ashlesha P4 (D)<br/>`+00° 28' 03"/d` | **Tula 11° 28' 44"**<br/>Swati P2 (R)<br/>`-00° 30' 52"/d` | **Simha 01° 10' 57"**<br/>Magha P1 (D)<br/>`+00° 05' 48"/d` | **Kanya 28° 48' 51"**<br/>Chitra P2 (R/V)<br/>`-00° 07' 24"/d` | **Meena 14° 28' 57"**<br/>Uttara Bhadrapada P4 (R)<br/>`-00° 03' 01"/d` | **Kumbha 01° 18' 34"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Kumbha 01° 33' 36"**<br/>Dhanishta P3 (R)<br/>`-00° 13' 42"/d` | **Simha 01° 18' 34"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-12` | Guruvara | `24° 13' 56"` | `08h 27m 43s` | **Tula 25° 22' 35"**<br/>Vishakha P2 (D)<br/>`+01° 00' 21"/d` | **Vrishchika 25° 36' 37"**<br/>Jyeshtha P3 (D)<br/>`+11° 57' 58"/d` | **Karka 29° 42' 53"**<br/>Ashlesha P4 (D)<br/>`+00° 27' 48"/d` | **Tula 11° 03' 43"**<br/>Swati P2 (R)<br/>`-00° 19' 10"/d` | **Simha 01° 16' 40"**<br/>Magha P1 (D)<br/>`+00° 05' 38"/d` | **Kanya 28° 42' 42"**<br/>Chitra P2 (R/V)<br/>`-00° 04' 56"/d` | **Meena 14° 25' 58"**<br/>Uttara Bhadrapada P4 (R)<br/>`-00° 02' 56"/d` | **Kumbha 01° 15' 23"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Kumbha 01° 20' 45"**<br/>Dhanishta P3 (R)<br/>`-00° 11' 50"/d` | **Simha 01° 15' 23"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-13` | Shukravara | `24° 13' 57"` | `08h 31m 40s` | **Tula 26° 22' 57"**<br/>Vishakha P2 (D)<br/>`+01° 00' 23"/d` | **Dhanu 07° 31' 05"**<br/>Mula P3 (D)<br/>`+11° 51' 21"/d` | **Simha 00° 10' 34"**<br/>Magha P1 (D)<br/>`+00° 27' 33"/d` | **Tula 10° 50' 24"**<br/>Swati P2 (R)<br/>`-00° 07' 31"/d` | **Simha 01° 22' 14"**<br/>Magha P1 (D)<br/>`+00° 05' 28"/d` | **Kanya 28° 39' 00"**<br/>Chitra P2 (R/V)<br/>`-00° 02' 29"/d` | **Meena 14° 23' 05"**<br/>Uttara Bhadrapada P4 (R)<br/>`-00° 02' 51"/d` | **Kumbha 01° 12' 12"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Kumbha 01° 10' 10"**<br/>Dhanishta P3 (R)<br/>`-00° 09' 13"/d` | **Simha 01° 12' 12"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-14` | Shanivara | `24° 13' 57"` | `08h 35m 36s` | **Tula 27° 23' 20"**<br/>Vishakha P3 (D)<br/>`+01° 00' 24"/d` | **Dhanu 19° 20' 25"**<br/>Purva Ashadha P2 (D)<br/>`+11° 47' 48"/d` | **Simha 00° 38' 01"**<br/>Magha P1 (D)<br/>`+00° 27' 18"/d` | **Tula 10° 48' 34"**<br/>Swati P2 (D)<br/>`+00° 03' 44"/d` | **Simha 01° 27' 38"**<br/>Magha P1 (D)<br/>`+00° 05' 19"/d` | **Kanya 28° 37' 44"**<br/>Chitra P2 (S/V)<br/>`-00° 00' 03"/d` | **Meena 14° 20' 16"**<br/>Uttara Bhadrapada P4 (R)<br/>`-00° 02' 45"/d` | **Kumbha 01° 09' 02"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Kumbha 01° 02' 24"**<br/>Dhanishta P3 (R)<br/>`-00° 06' 17"/d` | **Simha 01° 09' 02"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-15` | Ravivara | `24° 13' 57"` | `08h 39m 33s` | **Tula 28° 23' 45"**<br/>Vishakha P3 (D)<br/>`+01° 00' 25"/d` | **Makara 01° 08' 07"**<br/>Uttara Ashadha P2 (D/V)<br/>`+11° 48' 14"/d` | **Simha 01° 05' 12"**<br/>Magha P1 (D)<br/>`+00° 27' 03"/d` | **Tula 10° 57' 40"**<br/>Swati P2 (D)<br/>`+00° 14' 22"/d` | **Simha 01° 32' 52"**<br/>Magha P1 (D)<br/>`+00° 05' 09"/d` | **Kanya 28° 38' 53"**<br/>Chitra P2 (D/V)<br/>`+00° 02' 21"/d` | **Meena 14° 17' 33"**<br/>Uttara Bhadrapada P4 (R)<br/>`-00° 02' 40"/d` | **Kumbha 01° 05' 51"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Kumbha 00° 57' 33"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 29"/d` | **Simha 01° 05' 51"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-16` | Somavara | `24° 13' 57"` | `08h 43m 30s` | **Tula 29° 24' 11"**<br/>Vishakha P3 (D)<br/>`+01° 00' 27"/d` | **Makara 12° 58' 35"**<br/>Shravana P1 (D)<br/>`+11° 53' 24"/d` | **Simha 01° 32' 08"**<br/>Magha P1 (D)<br/>`+00° 26' 48"/d` | **Tula 11° 17' 02"**<br/>Swati P2 (D)<br/>`+00° 24' 14"/d` | **Simha 01° 37' 56"**<br/>Magha P1 (D)<br/>`+00° 04' 59"/d` | **Kanya 28° 42' 25"**<br/>Chitra P2 (D/V)<br/>`+00° 04' 42"/d` | **Meena 14° 14' 56"**<br/>Uttara Bhadrapada P4 (R)<br/>`-00° 02' 35"/d` | **Kumbha 01° 02' 40"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Kumbha 00° 55' 14"**<br/>Dhanishta P3 (R)<br/>`-00° 09' 10"/d` | **Simha 01° 02' 40"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-17` | Mangalavara | `24° 13' 57"` | `08h 47m 26s` | **Vrishchika 00° 24' 38"**<br/>Vishakha P4 (D/PN)<br/>`+01° 00' 28"/d` | **Makara 24° 56' 49"**<br/>Dhanishta P1 (D/MB)<br/>`+12° 03' 52"/d` | **Simha 01° 58' 48"**<br/>Magha P1 (D)<br/>`+00° 26' 32"/d` | **Tula 11° 45' 50"**<br/>Swati P2 (D)<br/>`+00° 33' 13"/d` | **Simha 01° 42' 50"**<br/>Magha P1 (D)<br/>`+00° 04' 49"/d` | **Kanya 28° 48' 17"**<br/>Chitra P2 (D/V)<br/>`+00° 07' 01"/d` | **Meena 14° 12' 24"**<br/>Uttara Bhadrapada P4 (R)<br/>`-00° 02' 29"/d` | **Kumbha 00° 59' 29"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Kumbha 00° 54' 35"**<br/>Dhanishta P3 (S)<br/>`-00° 00' 09"/d` | **Simha 00° 59' 29"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-18` | Budhavara | `24° 13' 57"` | `08h 51m 23s` | **Vrishchika 01° 25' 07"**<br/>Vishakha P4 (D/PN)<br/>`+01° 00' 29"/d` | **Kumbha 07° 08' 17"**<br/>Shatabhisha P1 (D)<br/>`+12° 19' 53"/d` | **Simha 02° 25' 12"**<br/>Magha P1 (D)<br/>`+00° 26' 16"/d` | **Tula 12° 23' 11"**<br/>Swati P2 (D)<br/>`+00° 41' 19"/d` | **Simha 01° 47' 34"**<br/>Magha P1 (D)<br/>`+00° 04' 39"/d` | **Kanya 28° 56' 26"**<br/>Chitra P2 (D/V)<br/>`+00° 09' 17"/d` | **Meena 14° 09' 57"**<br/>Uttara Bhadrapada P4 (R)<br/>`-00° 02' 23"/d` | **Kumbha 00° 56' 19"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Kumbha 00° 54' 32"**<br/>Dhanishta P3 (S)<br/>`-00° 00' 10"/d` | **Simha 00° 56' 19"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-19` | Guruvara | `24° 13' 57"` | `08h 55m 19s` | **Vrishchika 02° 25' 37"**<br/>Vishakha P4 (D/PN)<br/>`+01° 00' 31"/d` | **Kumbha 19° 38' 30"**<br/>Shatabhisha P4 (D/PN)<br/>`+12° 41' 16"/d` | **Simha 02° 51' 20"**<br/>Magha P1 (D)<br/>`+00° 25' 59"/d` | **Tula 13° 08' 10"**<br/>Swati P2 (D)<br/>`+00° 48' 31"/d` | **Simha 01° 52' 08"**<br/>Magha P1 (D)<br/>`+00° 04' 28"/d` | **Kanya 29° 06' 50"**<br/>Chitra P2 (D/V)<br/>`+00° 11' 30"/d` | **Meena 14° 07' 36"**<br/>Uttara Bhadrapada P4 (R)<br/>`-00° 02' 18"/d` | **Kumbha 00° 53' 08"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Kumbha 00° 53' 52"**<br/>Dhanishta P3 (R)<br/>`-00° 01' 22"/d` | **Simha 00° 53' 08"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-20` | Shukravara | `24° 13' 58"` | `08h 59m 16s` | **Vrishchika 03° 26' 09"**<br/>Anuradha P1 (D)<br/>`+01° 00' 32"/d` | **Meena 02° 32' 29"**<br/>Purva Bhadrapada P4 (D/PN)<br/>`+13° 07' 14"/d` | **Simha 03° 17' 11"**<br/>Magha P1 (D)<br/>`+00° 25' 43"/d` | **Tula 13° 59' 56"**<br/>Swati P3 (D)<br/>`+00° 54' 53"/d` | **Simha 01° 56' 32"**<br/>Magha P1 (D)<br/>`+00° 04' 18"/d` | **Kanya 29° 19' 26"**<br/>Chitra P2 (D/V)<br/>`+00° 13' 40"/d` | **Meena 14° 05' 21"**<br/>Uttara Bhadrapada P4 (R)<br/>`-00° 02' 12"/d` | **Kumbha 00° 49' 57"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Kumbha 00° 51' 29"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 31"/d` | **Simha 00° 49' 57"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-21` | Shanivara | `24° 13' 58"` | `09h 03m 12s` | **Vrishchika 04° 26' 41"**<br/>Anuradha P1 (D)<br/>`+01° 00' 33"/d` | **Meena 15° 54' 06"**<br/>Uttara Bhadrapada P4 (D)<br/>`+13° 36' 13"/d` | **Simha 03° 42' 46"**<br/>Magha P2 (D)<br/>`+00° 25' 26"/d` | **Tula 14° 57' 39"**<br/>Swati P3 (D)<br/>`+01° 00' 26"/d` | **Simha 02° 00' 45"**<br/>Magha P1 (D)<br/>`+00° 04' 08"/d` | **Kanya 29° 34' 09"**<br/>Chitra P2 (D/V)<br/>`+00° 15' 46"/d` | **Meena 14° 03' 12"**<br/>Uttara Bhadrapada P4 (R)<br/>`-00° 02' 06"/d` | **Kumbha 00° 46' 46"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Kumbha 00° 46' 39"**<br/>Dhanishta P3 (R)<br/>`-00° 06' 13"/d` | **Simha 00° 46' 46"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-22` | Ravivara | `24° 13' 58"` | `09h 07m 09s` | **Vrishchika 05° 27' 15"**<br/>Anuradha P1 (D)<br/>`+01° 00' 34"/d` | **Meena 29° 45' 14"**<br/>Revati P4 (D/V)<br/>`+14° 05' 47"/d` | **Simha 04° 08' 03"**<br/>Magha P2 (D)<br/>`+00° 25' 09"/d` | **Tula 16° 00' 33"**<br/>Swati P3 (D)<br/>`+01° 05' 17"/d` | **Simha 02° 04' 48"**<br/>Magha P1 (D)<br/>`+00° 03' 57"/d` | **Kanya 29° 50' 57"**<br/>Chitra P2 (D/V)<br/>`+00° 17' 49"/d` | **Meena 14° 01' 09"**<br/>Uttara Bhadrapada P4 (R)<br/>`-00° 02' 00"/d` | **Kumbha 00° 43' 35"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Kumbha 00° 39' 03"**<br/>Dhanishta P3 (R)<br/>`-00° 08' 55"/d` | **Simha 00° 43' 35"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-23` | Somavara | `24° 13' 58"` | `09h 11m 05s` | **Vrishchika 06° 27' 50"**<br/>Anuradha P1 (D)<br/>`+01° 00' 36"/d` | **Mesha 14° 04' 53"**<br/>Bharani P1 (D)<br/>`+14° 32' 43"/d` | **Simha 04° 33' 03"**<br/>Magha P2 (D)<br/>`+00° 24' 51"/d` | **Tula 17° 07' 57"**<br/>Swati P4 (D/PN)<br/>`+01° 09' 27"/d` | **Simha 02° 08' 40"**<br/>Magha P1 (D)<br/>`+00° 03' 47"/d` | **Tula 00° 09' 46"**<br/>Chitra P3 (D/V)<br/>`+00° 19' 48"/d` | **Meena 13° 59' 11"**<br/>Uttara Bhadrapada P4 (R)<br/>`-00° 01' 54"/d` | **Kumbha 00° 40' 25"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Kumbha 00° 29' 01"**<br/>Dhanishta P3 (R)<br/>`-00° 11' 00"/d` | **Simha 00° 40' 25"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-24` | Mangalavara | `24° 13' 58"` | `09h 15m 02s` | **Vrishchika 07° 28' 27"**<br/>Anuradha P2 (D/PN)<br/>`+01° 00' 37"/d` | **Mesha 28° 48' 42"**<br/>Krittika P1 (D/PN)<br/>`+14° 53' 35"/d` | **Simha 04° 57' 46"**<br/>Magha P2 (D)<br/>`+00° 24' 33"/d` | **Tula 18° 19' 15"**<br/>Swati P4 (D/PN)<br/>`+01° 13' 03"/d` | **Simha 02° 12' 22"**<br/>Magha P1 (D)<br/>`+00° 03' 36"/d` | **Tula 00° 30' 33"**<br/>Chitra P3 (D/V)<br/>`+00° 21' 44"/d` | **Meena 13° 57' 20"**<br/>Uttara Bhadrapada P4 (R)<br/>`-00° 01' 48"/d` | **Kumbha 00° 37' 14"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Kumbha 00° 17' 40"**<br/>Dhanishta P3 (D)<br/>`+00° 28' 22"/d` | **Simha 00° 37' 14"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-25` | Budhavara | `24° 13' 58"` | `09h 18m 59s` | **Vrishchika 08° 29' 04"**<br/>Anuradha P2 (D/PN)<br/>`+01° 00' 38"/d` | **Vrishabha 13° 49' 06"**<br/>Rohini P2 (D/V/PN)<br/>`+15° 05' 32"/d` | **Simha 05° 22' 10"**<br/>Magha P2 (D)<br/>`+00° 24' 15"/d` | **Tula 19° 33' 52"**<br/>Swati P4 (D/PN/MB)<br/>`+01° 16' 08"/d` | **Simha 02° 15' 53"**<br/>Magha P1 (D)<br/>`+00° 03' 25"/d` | **Tula 00° 53' 14"**<br/>Chitra P3 (D/V)<br/>`+00° 23' 36"/d` | **Meena 13° 55' 35"**<br/>Uttara Bhadrapada P4 (R)<br/>`-00° 01' 42"/d` | **Kumbha 00° 34' 03"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Kumbha 00° 05' 42"**<br/>Dhanishta P3 (R)<br/>`-00° 11' 22"/d` | **Simha 00° 34' 03"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-26` | Guruvara | `24° 13' 58"` | `09h 22m 55s` | **Vrishchika 09° 29' 43"**<br/>Anuradha P2 (D/PN)<br/>`+01° 00' 40"/d` | **Vrishabha 28° 56' 15"**<br/>Mrigashirsha P2 (D)<br/>`+15° 07' 05"/d` | **Simha 05° 46' 16"**<br/>Magha P2 (D)<br/>`+00° 23' 56"/d` | **Tula 20° 51' 20"**<br/>Vishakha P1 (D)<br/>`+01° 18' 46"/d` | **Simha 02° 19' 14"**<br/>Magha P1 (D)<br/>`+00° 03' 15"/d` | **Tula 01° 17' 45"**<br/>Chitra P3 (D/V)<br/>`+00° 25' 25"/d` | **Meena 13° 53' 55"**<br/>Uttara Bhadrapada P4 (R)<br/>`-00° 01' 36"/d` | **Kumbha 00° 30' 52"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Makara 29° 55' 00"**<br/>Dhanishta P2 (R)<br/>`-00° 09' 47"/d` | **Simha 00° 30' 52"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-27` | Shukravara | `24° 13' 59"` | `09h 26m 52s` | **Vrishchika 10° 30' 24"**<br/>Anuradha P3 (D)<br/>`+01° 00' 41"/d` | **Mithuna 13° 59' 53"**<br/>Ardra P3 (D)<br/>`+14° 58' 43"/d` | **Simha 06° 10' 03"**<br/>Magha P2 (D)<br/>`+00° 23' 37"/d` | **Tula 22° 11' 14"**<br/>Vishakha P1 (D)<br/>`+01° 21' 00"/d` | **Simha 02° 22' 23"**<br/>Magha P1 (D)<br/>`+00° 03' 04"/d` | **Tula 01° 44' 03"**<br/>Chitra P3 (D/V)<br/>`+00° 27' 10"/d` | **Meena 13° 52' 22"**<br/>Uttara Bhadrapada P4 (R)<br/>`-00° 01' 30"/d` | **Kumbha 00° 27' 42"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Makara 29° 46' 30"**<br/>Dhanishta P2 (R)<br/>`-00° 07' 06"/d` | **Simha 00° 27' 42"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-28` | Shanivara | `24° 13' 59"` | `09h 30m 48s` | **Vrishchika 11° 31' 06"**<br/>Anuradha P3 (D)<br/>`+01° 00' 43"/d` | **Mithuna 28° 50' 59"**<br/>Punarvasu P3 (D/V)<br/>`+14° 42' 32"/d` | **Simha 06° 33' 31"**<br/>Magha P2 (D)<br/>`+00° 23' 18"/d` | **Tula 23° 33' 12"**<br/>Vishakha P2 (D)<br/>`+01° 22' 54"/d` | **Simha 02° 25' 22"**<br/>Magha P1 (D)<br/>`+00° 02' 53"/d` | **Tula 02° 12' 04"**<br/>Chitra P3 (D/V)<br/>`+00° 28' 51"/d` | **Meena 13° 50' 55"**<br/>Uttara Bhadrapada P4 (R)<br/>`-00° 01' 24"/d` | **Kumbha 00° 24' 31"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Makara 29° 40' 52"**<br/>Dhanishta P2 (R)<br/>`-00° 04' 12"/d` | **Simha 00° 24' 31"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-29` | Ravivara | `24° 13' 59"` | `09h 34m 45s` | **Vrishchika 12° 31' 50"**<br/>Anuradha P3 (D)<br/>`+01° 00' 45"/d` | **Karka 13° 23' 13"**<br/>Pushya P4 (D)<br/>`+14° 21' 32"/d` | **Simha 06° 56' 39"**<br/>Magha P3 (D)<br/>`+00° 22' 58"/d` | **Tula 24° 56' 55"**<br/>Vishakha P2 (D)<br/>`+01° 24' 31"/d` | **Simha 02° 28' 10"**<br/>Magha P1 (D)<br/>`+00° 02' 42"/d` | **Tula 02° 41' 44"**<br/>Chitra P3 (D/V)<br/>`+00° 30' 29"/d` | **Meena 13° 49' 34"**<br/>Uttara Bhadrapada P4 (R)<br/>`-00° 01' 17"/d` | **Kumbha 00° 21' 20"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Makara 29° 37' 59"**<br/>Dhanishta P2 (R)<br/>`-00° 01' 41"/d` | **Simha 00° 21' 20"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-30` | Somavara | `24° 13' 59"` | `09h 38m 41s` | **Vrishchika 13° 32' 35"**<br/>Anuradha P4 (D/V)<br/>`+01° 00' 46"/d` | **Karka 27° 33' 17"**<br/>Ashlesha P4 (D)<br/>`+13° 58' 42"/d` | **Simha 07° 19' 27"**<br/>Magha P3 (D)<br/>`+00° 22' 37"/d` | **Tula 26° 22' 07"**<br/>Vishakha P2 (D)<br/>`+01° 25' 52"/d` | **Simha 02° 30' 46"**<br/>Magha P1 (D)<br/>`+00° 02' 31"/d` | **Tula 03° 13' 01"**<br/>Chitra P3 (D/V)<br/>`+00° 32' 03"/d` | **Meena 13° 48' 19"**<br/>Uttara Bhadrapada P4 (R)<br/>`-00° 01' 11"/d` | **Kumbha 00° 18' 09"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Makara 29° 37' 10"**<br/>Dhanishta P2 (S)<br/>`-00° 00' 08"/d` | **Simha 00° 18' 09"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |

### Table 2B — Daily Outer Planets (*Aruna / Uranus, Varuna / Neptune, Yama / Pluto*), Tropical (*Sayana*) Luminaries, & Second-Order Tabular Differences ($\Delta^2 \lambda$)

| Date | Kali *Ahargana* | Tropical Sun ($\lambda_{\text{trop}}$) | Tropical Moon ($\lambda_{\text{trop}}$) | Uranus (*Aruna*) Sidereal | Neptune (*Varuna*) Sidereal | Pluto (*Yama*) Sidereal | Moon $\Delta^2 \lambda$ (`"/d²`) | Mercury $\Delta^2 \lambda$ (`"/d²`) | Venus $\Delta^2 \lambda$ (`"/d²`) | Mars $\Delta^2 \lambda$ (`"/d²`) |
|---|---|---|---|---|---|---|---|---|---|---|
| `2026-11-01` | `1872880.0` | `Vrishchika 08° 34' 29"` | `Karka 27° 28' 06"` | **Vrishabha 10° 26' 33"** (`-00° 02' 11"/d`) | **Meena 07° 50' 28"** (`-00° 01' 15"/d`) | **Makara 08° 53' 37"** (`+00° 00' 27"/d`) | `-924.2"` | `-403.1"` | `+103.2"` | `-11.7"` |
| `2026-11-02` | `1872881.0` | `Vrishchika 09° 34' 30"` | `Simha 11° 28' 06"` | **Vrishabha 10° 24' 21"** (`-00° 02' 13"/d`) | **Meena 07° 49' 14"** (`-00° 01' 14"/d`) | **Makara 08° 54' 05"** (`+00° 00' 29"/d`) | `-926.8"` | `-304.8"` | `+112.7"` | `-11.9"` |
| `2026-11-03` | `1872882.0` | `Vrishchika 10° 34' 33"` | `Simha 25° 12' 39"` | **Vrishabha 10° 22' 07"** (`-00° 02' 14"/d`) | **Meena 07° 48' 00"** (`-00° 01' 13"/d`) | **Makara 08° 54' 35"** (`+00° 00' 31"/d`) | `-868.2"` | `-183.4"` | `+120.9"` | `-12.2"` |
| `2026-11-04` | `1872883.0` | `Vrishchika 11° 34' 38"` | `Kanya 08° 42' 43"` | **Vrishabha 10° 19' 52"** (`-00° 02' 16"/d`) | **Meena 07° 46' 48"** (`-00° 01' 11"/d`) | **Makara 08° 55' 07"** (`+00° 00' 33"/d`) | `-787.2"` | `-44.5"` | `+128.0"` | `-12.5"` |
| `2026-11-05` | `1872884.0` | `Vrishchika 12° 34' 46"` | `Kanya 21° 59' 41"` | **Vrishabha 10° 17' 36"** (`-00° 02' 17"/d`) | **Meena 07° 45' 38"** (`-00° 01' 10"/d`) | **Makara 08° 55' 41"** (`+00° 00' 34"/d`) | `-713.6"` | `+103.9"` | `+133.9"` | `-12.7"` |
| `2026-11-06` | `1872885.0` | `Vrishchika 13° 34' 55"` | `Tula 05° 04' 45"` | **Vrishabha 10° 15' 18"** (`-00° 02' 18"/d`) | **Meena 07° 44' 29"** (`-00° 01' 08"/d`) | **Makara 08° 56' 16"** (`+00° 00' 36"/d`) | `-664.4"` | `+251.7"` | `+138.7"` | `-13.0"` |
| `2026-11-07` | `1872886.0` | `Vrishchika 14° 35' 07"` | `Tula 17° 58' 44"` | **Vrishabha 10° 12' 59"** (`-00° 02' 20"/d`) | **Meena 07° 43' 21"** (`-00° 01' 07"/d`) | **Makara 08° 56' 52"** (`+00° 00' 38"/d`) | `-642.4"` | `+388.7"` | `+142.4"` | `-13.3"` |
| `2026-11-08` | `1872887.0` | `Vrishchika 15° 35' 20"` | `Vrishchika 00° 42' 01"` | **Vrishabha 10° 10' 39"** (`-00° 02' 21"/d`) | **Meena 07° 42' 15"** (`-00° 01' 05"/d`) | **Makara 08° 57' 31"** (`+00° 00' 39"/d`) | `-639.0"` | `+506.0"` | `+145.1"` | `-13.6"` |
| `2026-11-09` | `1872888.0` | `Vrishchika 16° 35' 35"` | `Vrishchika 13° 14' 39"` | **Vrishabha 10° 08' 17"** (`-00° 02' 22"/d`) | **Meena 07° 41' 11"** (`-00° 01' 04"/d`) | **Makara 08° 58' 11"** (`+00° 00' 41"/d`) | `-638.0"` | `+597.4"` | `+146.8"` | `-13.8"` |
| `2026-11-10` | `1872889.0` | `Vrishchika 17° 35' 52"` | `Vrishchika 25° 36' 39"` | **Vrishabha 10° 05' 55"** (`-00° 02' 23"/d`) | **Meena 07° 40' 08"** (`-00° 01' 02"/d`) | **Makara 08° 58' 53"** (`+00° 00' 43"/d`) | `-619.8"` | `+660.1"` | `+147.8"` | `-14.1"` |
| `2026-11-11` | `1872890.0` | `Vrishchika 18° 36' 11"` | `Dhanu 07° 48' 20"` | **Vrishabha 10° 03' 31"** (`-00° 02' 24"/d`) | **Meena 07° 39' 06"** (`-00° 01' 01"/d`) | **Makara 08° 59' 36"** (`+00° 00' 44"/d`) | `-566.5"` | `+694.0"` | `+147.9"` | `-14.3"` |
| `2026-11-12` | `1872891.0` | `Vrishchika 19° 36' 31"` | `Dhanu 19° 50' 33"` | **Vrishabha 10° 01' 06"** (`-00° 02' 25"/d`) | **Meena 07° 38' 06"** (`-00° 00' 59"/d`) | **Makara 09° 00' 21"** (`+00° 00' 46"/d`) | `-465.1"` | `+702.0"` | `+147.4"` | `-14.6"` |
| `2026-11-13` | `1872892.0` | `Vrishchika 20° 36' 53"` | `Makara 01° 45' 02"` | **Vrishabha 09° 58' 41"** (`-00° 02' 26"/d`) | **Meena 07° 37' 08"** (`-00° 00' 57"/d`) | **Makara 09° 01' 08"** (`+00° 00' 47"/d`) | `-308.8"` | `+688.2"` | `+146.3"` | `-14.9"` |
| `2026-11-14` | `1872893.0` | `Vrishchika 21° 37' 17"` | `Makara 13° 34' 22"` | **Vrishabha 09° 56' 14"** (`-00° 02' 27"/d`) | **Meena 07° 36' 12"** (`-00° 00' 56"/d`) | **Makara 09° 01' 56"** (`+00° 00' 49"/d`) | `-97.2"` | `+657.6"` | `+144.7"` | `-15.1"` |
| `2026-11-15` | `1872894.0` | `Vrishchika 22° 37' 42"` | `Makara 25° 22' 04"` | **Vrishabha 09° 53' 47"** (`-00° 02' 28"/d`) | **Meena 07° 35' 17"** (`-00° 00' 54"/d`) | **Makara 09° 02' 46"** (`+00° 00' 51"/d`) | `+164.7"` | `+615.3"` | `+142.7"` | `-15.4"` |
| `2026-11-16` | `1872895.0` | `Vrishchika 23° 38' 08"` | `Kumbha 07° 12' 32"` | **Vrishabha 09° 51' 19"** (`-00° 02' 28"/d`) | **Meena 07° 34' 24"** (`-00° 00' 52"/d`) | **Makara 09° 03' 37"** (`+00° 00' 52"/d`) | `+466.9"` | `+565.7"` | `+140.2"` | `-15.7"` |
| `2026-11-17` | `1872896.0` | `Vrishchika 24° 38' 35"` | `Kumbha 19° 10' 46"` | **Vrishabha 09° 48' 51"** (`-00° 02' 29"/d`) | **Meena 07° 33' 32"** (`-00° 00' 51"/d`) | **Makara 09° 04' 30"** (`+00° 00' 54"/d`) | `+794.2"` | `+512.6"` | `+137.5"` | `-15.9"` |
| `2026-11-18` | `1872897.0` | `Vrishchika 25° 39' 04"` | `Meena 01° 22' 14"` | **Vrishabha 09° 46' 22"** (`-00° 02' 29"/d`) | **Meena 07° 32' 42"** (`-00° 00' 49"/d`) | **Makara 09° 05' 25"** (`+00° 00' 55"/d`) | `+1124.4"` | `+458.8"` | `+134.5"` | `-16.2"` |
| `2026-11-19` | `1872898.0` | `Vrishchika 26° 39' 35"` | `Meena 13° 52' 27"` | **Vrishabha 09° 43' 52"** (`-00° 02' 30"/d`) | **Meena 07° 31' 55"** (`-00° 00' 47"/d`) | **Makara 09° 06' 21"** (`+00° 00' 57"/d`) | `+1426.4"` | `+406.6"` | `+131.3"` | `-16.5"` |
| `2026-11-20` | `1872899.0` | `Vrishchika 27° 40' 06"` | `Meena 26° 46' 26"` | **Vrishabha 09° 41' 22"** (`-00° 02' 30"/d`) | **Meena 07° 31' 08"** (`-00° 00' 45"/d`) | **Makara 09° 07' 18"** (`+00° 00' 58"/d`) | `+1658.4"` | `+357.1"` | `+128.0"` | `-16.8"` |
| `2026-11-21` | `1872900.0` | `Vrishchika 28° 40' 39"` | `Mesha 10° 08' 04"` | **Vrishabha 09° 38' 51"** (`-00° 02' 31"/d`) | **Meena 07° 30' 24"** (`-00° 00' 43"/d`) | **Makara 09° 08' 18"** (`+00° 01' 00"/d`) | `+1770.1"` | `+311.5"` | `+124.6"` | `-17.1"` |
| `2026-11-22` | `1872901.0` | `Vrishchika 29° 41' 13"` | `Mesha 23° 59' 12"` | **Vrishabha 09° 36' 20"** (`-00° 02' 31"/d`) | **Meena 07° 29' 42"** (`-00° 00' 42"/d`) | **Makara 09° 09' 18"** (`+00° 01' 01"/d`) | `+1711.3"` | `+270.0"` | `+121.1"` | `-17.4"` |
| `2026-11-23` | `1872902.0` | `Dhanu 00° 41' 48"` | `Vrishabha 08° 18' 51"` | **Vrishabha 09° 33' 49"** (`-00° 02' 31"/d`) | **Meena 07° 29' 01"** (`-00° 00' 40"/d`) | **Makara 09° 10' 21"** (`+00° 01' 03"/d`) | `+1450.1"` | `+232.9"` | `+117.6"` | `-17.7"` |
| `2026-11-24` | `1872903.0` | `Dhanu 01° 42' 25"` | `Vrishabha 23° 02' 40"` | **Vrishabha 09° 31' 18"** (`-00° 02' 31"/d`) | **Meena 07° 28' 22"** (`-00° 00' 38"/d`) | **Makara 09° 11' 24"** (`+00° 01' 04"/d`) | `+994.7"` | `+199.9"` | `+114.0"` | `-18.1"` |
| `2026-11-25` | `1872904.0` | `Dhanu 02° 43' 03"` | `Mithuna 08° 03' 04"` | **Vrishabha 09° 28' 46"** (`-00° 02' 32"/d`) | **Meena 07° 27' 45"** (`-00° 00' 36"/d`) | **Makara 09° 12' 30"** (`+00° 01' 06"/d`) | `+406.1"` | `+171.0"` | `+110.4"` | `-18.4"` |
| `2026-11-26` | `1872905.0` | `Dhanu 03° 43' 42"` | `Mithuna 23° 10' 14"` | **Vrishabha 09° 26' 15"** (`-00° 02' 32"/d`) | **Meena 07° 27' 10"** (`-00° 00' 34"/d`) | **Makara 09° 13' 36"** (`+00° 01' 07"/d`) | `-212.5"` | `+145.8"` | `+106.8"` | `-18.8"` |
| `2026-11-27` | `1872906.0` | `Dhanu 04° 44' 23"` | `Karka 08° 13' 51"` | **Vrishabha 09° 23' 43"** (`-00° 02' 32"/d`) | **Meena 07° 26' 37"** (`-00° 00' 32"/d`) | **Makara 09° 14' 44"** (`+00° 01' 09"/d`) | `-751.2"` | `+123.9"` | `+103.1"` | `-19.3"` |
| `2026-11-28` | `1872907.0` | `Dhanu 05° 45' 05"` | `Karka 23° 04' 57"` | **Vrishabha 09° 21' 12"** (`-00° 02' 31"/d`) | **Meena 07° 26' 06"** (`-00° 00' 30"/d`) | **Makara 09° 15' 54"** (`+00° 01' 10"/d`) | `-1132.0"` | `+105.0"` | `+99.5"` | `-19.7"` |
| `2026-11-29` | `1872908.0` | `Dhanu 06° 45' 49"` | `Simha 07° 37' 11"` | **Vrishabha 09° 18' 40"** (`-00° 02' 31"/d`) | **Meena 07° 25' 37"** (`-00° 00' 28"/d`) | **Makara 09° 17' 05"** (`+00° 01' 12"/d`) | `-1329.3"` | `+88.8"` | `+95.8"` | `-20.2"` |
| `2026-11-30` | `1872909.0` | `Dhanu 07° 46' 34"` | `Simha 21° 47' 16"` | **Vrishabha 09° 16' 09"** (`-00° 02' 31"/d`) | **Meena 07° 25' 10"** (`-00° 00' 26"/d`) | **Makara 09° 18' 17"** (`+00° 01' 13"/d`) | `-1363.7"` | `+74.9"` | `+92.2"` | `-20.7"` |

## Chapter 3 — Daily Spherical & Physical Ephemeris Grid (Declination $\delta$, Right Ascension $\alpha$, Ecliptic Latitude $\beta$, Distance $R$, Parallax, Diameter, Phase & Magnitude)

**Why Spherical & Physical Coordinates Are Essential for Manual Jyotish:**
- **Declination ($\delta$ / *Kranti*):** Required to compute *Ayana Bala* in *Shadbala*, Parallel/Contra-Parallel Declination aspects (*Kranti Yoga*), and *Vyatipata / Vaidhriti Mahapata*.
- **Ecliptic Latitude ($\beta$ / *Shara / Vikshepa*):** Required to adjudicate the winner of a *Graha Yuddha* (Planetary War — the planet with the more northern latitude wins) and *Nakshatra Tara Bheda*.
- **True Distance ($R$ in AU), Horizontal Parallax (`HP`), Apparent Diameter (`"`), & Visual Magnitude ($V_{\text{mag}}$):** Required for topocentric Moon correction, eclipse contact sizing, and *Cheshta / Brihat Samhita* brightness diagnostics.

### Table 3A — Daily Declination ($\delta$ / *Kranti*) & Right Ascension ($\alpha$) Across the *Navagrahas* (`05:30 IST`)

| Date | Sun $\delta$ / $\alpha$ | Moon $\delta$ / $\alpha$ | Mars $\delta$ / $\alpha$ | Mercury $\delta$ / $\alpha$ | Jupiter $\delta$ / $\alpha$ | Venus $\delta$ / $\alpha$ | Saturn $\delta$ / $\alpha$ | Rahu $\delta$ |
|---|---|---|---|---|---|---|---|---|
| `2026-11-01` | `-14° 21' 31"`<br/>`14h 24m 47s` | `+23° 06' 22"`<br/>`08h 00m 16s` | `+16° 45' 52"`<br/>`09h 26m 16s` | `-18° 17' 51"`<br/>`14h 54m 55s` | `+14° 03' 50"`<br/>`09h 47m 26s` | `-14° 39' 36"`<br/>`13h 30m 05s` | `+01° 12' 36"`<br/>`00h 38m 21s` | `-12° 49' 34"` |
| `2026-11-02` | `-14° 40' 40"`<br/>`14h 28m 42s` | `+18° 38' 13"`<br/>`08h 57m 17s` | `+16° 37' 39"`<br/>`09h 28m 17s` | `-17° 40' 09"`<br/>`14h 50m 38s` | `+14° 01' 37"`<br/>`09h 47m 55s` | `-14° 15' 26"`<br/>`13h 28m 36s` | `+01° 11' 16"`<br/>`00h 38m 07s` | `-12° 50' 38"` |
| `2026-11-03` | `-14° 59' 34"`<br/>`14h 32m 38s` | `+13° 15' 34"`<br/>`09h 50m 09s` | `+16° 29' 26"`<br/>`09h 30m 17s` | `-16° 59' 30"`<br/>`14h 46m 03s` | `+13° 59' 27"`<br/>`09h 48m 23s` | `-13° 51' 43"`<br/>`13h 27m 16s` | `+01° 09' 57"`<br/>`00h 37m 53s` | `-12° 51' 43"` |
| `2026-11-04` | `-15° 18' 14"`<br/>`14h 36m 35s` | `+07° 20' 38"`<br/>`10h 39m 45s` | `+16° 21' 14"`<br/>`09h 32m 16s` | `-16° 16' 49"`<br/>`14h 41m 20s` | `+13° 57' 19"`<br/>`09h 48m 50s` | `-13° 28' 34"`<br/>`13h 26m 03s` | `+01° 08' 40"`<br/>`00h 37m 39s` | `-12° 52' 47"` |
| `2026-11-05` | `-15° 36' 39"`<br/>`14h 40m 32s` | `+01° 12' 25"`<br/>`11h 27m 13s` | `+16° 13' 02"`<br/>`09h 34m 15s` | `-15° 33' 10"`<br/>`14h 36m 35s` | `+13° 55' 15"`<br/>`09h 49m 16s` | `-13° 06' 05"`<br/>`13h 24m 59s` | `+01° 07' 26"`<br/>`00h 37m 26s` | `-12° 53' 52"` |
| `2026-11-06` | `-15° 54' 49"`<br/>`14h 44m 30s` | `-04° 52' 46"`<br/>`12h 13m 41s` | `+16° 04' 52"`<br/>`09h 36m 12s` | `-14° 49' 45"`<br/>`14h 32m 00s` | `+13° 53' 13"`<br/>`09h 49m 43s` | `-12° 44' 23"`<br/>`13h 24m 04s` | `+01° 06' 13"`<br/>`00h 37m 13s` | `-12° 54' 56"` |
| `2026-11-07` | `-16° 12' 43"`<br/>`14h 48m 30s` | `-10° 40' 12"`<br/>`13h 00m 15s` | `+15° 56' 43"`<br/>`09h 38m 08s` | `-14° 07' 49"`<br/>`14h 27m 42s` | `+13° 51' 14"`<br/>`09h 50m 08s` | `-12° 23' 30"`<br/>`13h 23m 17s` | `+01° 05' 02"`<br/>`00h 37m 01s` | `-12° 56' 00"` |
| `2026-11-08` | `-16° 30' 20"`<br/>`14h 52m 30s` | `-15° 56' 03"`<br/>`13h 47m 47s` | `+15° 48' 35"`<br/>`09h 40m 03s` | `-13° 28' 35"`<br/>`14h 23m 50s` | `+13° 49' 19"`<br/>`09h 50m 33s` | `-12° 03' 33"`<br/>`13h 22m 40s` | `+01° 03' 53"`<br/>`00h 36m 48s` | `-12° 57' 05"` |
| `2026-11-09` | `-16° 47' 41"`<br/>`14h 56m 31s` | `-20° 26' 56"`<br/>`14h 36m 55s` | `+15° 40' 29"`<br/>`09h 41m 58s` | `-12° 53' 06"`<br/>`14h 20m 30s` | `+13° 47' 26"`<br/>`09h 50m 57s` | `-11° 44' 35"`<br/>`13h 22m 12s` | `+01° 02' 47"`<br/>`00h 36m 36s` | `-12° 58' 09"` |
| `2026-11-10` | `-17° 04' 45"`<br/>`15h 00m 32s` | `-24° 00' 22"`<br/>`15h 27m 55s` | `+15° 32' 25"`<br/>`09h 43m 51s` | `-12° 22' 15"`<br/>`14h 17m 47s` | `+13° 45' 36"`<br/>`09h 51m 21s` | `-11° 26' 39"`<br/>`13h 21m 52s` | `+01° 01' 42"`<br/>`00h 36m 24s` | `-12° 59' 13"` |
| `2026-11-11` | `-17° 21' 31"`<br/>`15h 04m 35s` | `-26° 25' 43"`<br/>`16h 20m 35s` | `+15° 24' 23"`<br/>`09h 45m 43s` | `-11° 56' 37"`<br/>`14h 15m 46s` | `+13° 43' 50"`<br/>`09h 51m 44s` | `-11° 09' 47"`<br/>`13h 21m 42s` | `+01° 00' 40"`<br/>`00h 36m 13s` | `-13° 00' 17"` |
| `2026-11-12` | `-17° 37' 59"`<br/>`15h 08m 38s` | `-27° 35' 45"`<br/>`17h 14m 14s` | `+15° 16' 23"`<br/>`09h 47m 34s` | `-11° 36' 34"`<br/>`14h 14m 26s` | `+13° 42' 06"`<br/>`09h 52m 07s` | `-10° 54' 02"`<br/>`13h 21m 41s` | `+00° 59' 40"`<br/>`00h 36m 01s` | `-13° 01' 21"` |
| `2026-11-13` | `-17° 54' 09"`<br/>`15h 12m 43s` | `-27° 27' 49"`<br/>`18h 07m 52s` | `+15° 08' 26"`<br/>`09h 49m 24s` | `-11° 22' 12"`<br/>`14h 13m 49s` | `+13° 40' 26"`<br/>`09h 52m 28s` | `-10° 39' 24"`<br/>`13h 21m 49s` | `+00° 58' 42"`<br/>`00h 35m 50s` | `-13° 02' 26"` |
| `2026-11-14` | `-18° 10' 00"`<br/>`15h 16m 48s` | `-26° 04' 18"`<br/>`19h 00m 28s` | `+15° 00' 32"`<br/>`09h 51m 13s` | `-11° 13' 27"`<br/>`14h 13m 54s` | `+13° 38' 49"`<br/>`09h 52m 50s` | `-10° 25' 56"`<br/>`13h 22m 05s` | `+00° 57' 47"`<br/>`00h 35m 40s` | `-13° 03' 30"` |
| `2026-11-15` | `-18° 25' 33"`<br/>`15h 20m 54s` | `-23° 31' 33"`<br/>`19h 51m 19s` | `+14° 52' 41"`<br/>`09h 53m 01s` | `-11° 10' 04"`<br/>`14h 14m 38s` | `+13° 37' 16"`<br/>`09h 53m 10s` | `-10° 13' 38"`<br/>`13h 22m 30s` | `+00° 56' 54"`<br/>`00h 35m 30s` | `-13° 04' 34"` |
| `2026-11-16` | `-18° 40' 45"`<br/>`15h 25m 01s` | `-19° 58' 18"`<br/>`20h 40m 07s` | `+14° 44' 53"`<br/>`09h 54m 48s` | `-11° 11' 41"`<br/>`14h 15m 59s` | `+13° 35' 45"`<br/>`09h 53m 30s` | `-10° 02' 29"`<br/>`13h 23m 04s` | `+00° 56' 03"`<br/>`00h 35m 20s` | `-13° 05' 38"` |
| `2026-11-17` | `-18° 55' 38"`<br/>`15h 29m 08s` | `-15° 34' 06"`<br/>`21h 27m 05s` | `+14° 37' 08"`<br/>`09h 56m 33s` | `-11° 17' 51"`<br/>`14h 17m 55s` | `+13° 34' 19"`<br/>`09h 53m 50s` | `-09° 52' 29"`<br/>`13h 23m 46s` | `+00° 55' 14"`<br/>`00h 35m 10s` | `-13° 06' 42"` |
| `2026-11-18` | `-19° 10' 10"`<br/>`15h 33m 17s` | `-10° 28' 23"`<br/>`22h 12m 47s` | `+14° 29' 27"`<br/>`09h 58m 18s` | `-11° 28' 08"`<br/>`14h 20m 21s` | `+13° 32' 55"`<br/>`09h 54m 08s` | `-09° 43' 39"`<br/>`13h 24m 36s` | `+00° 54' 28"`<br/>`00h 35m 01s` | `-13° 07' 46"` |
| `2026-11-19` | `-19° 24' 22"`<br/>`15h 37m 26s` | `-04° 50' 37"`<br/>`22h 58m 04s` | `+14° 21' 50"`<br/>`10h 00m 01s` | `-11° 42' 00"`<br/>`14h 23m 16s` | `+13° 31' 35"`<br/>`09h 54m 26s` | `-09° 35' 58"`<br/>`13h 25m 34s` | `+00° 53' 44"`<br/>`00h 34m 52s` | `-13° 08' 49"` |
| `2026-11-20` | `-19° 38' 13"`<br/>`15h 41m 36s` | `+01° 08' 50"`<br/>`23h 43m 57s` | `+14° 14' 17"`<br/>`10h 01m 43s` | `-11° 59' 01"`<br/>`14h 26m 35s` | `+13° 30' 18"`<br/>`09h 54m 44s` | `-09° 29' 24"`<br/>`13h 26m 39s` | `+00° 53' 03"`<br/>`00h 34m 43s` | `-13° 09' 53"` |
| `2026-11-21` | `-19° 51' 42"`<br/>`15h 45m 47s` | `+07° 17' 21"`<br/>`00h 31m 37s` | `+14° 06' 48"`<br/>`10h 03m 24s` | `-12° 18' 43"`<br/>`14h 30m 17s` | `+13° 29' 05"`<br/>`09h 55m 00s` | `-09° 23' 56"`<br/>`13h 27m 52s` | `+00° 52' 24"`<br/>`00h 34m 35s` | `-13° 10' 57"` |
| `2026-11-22` | `-20° 04' 50"`<br/>`15h 49m 58s` | `+13° 18' 12"`<br/>`01h 22m 19s` | `+13° 59' 23"`<br/>`10h 05m 04s` | `-12° 40' 40"`<br/>`14h 34m 19s` | `+13° 27' 56"`<br/>`09h 55m 16s` | `-09° 19' 33"`<br/>`13h 29m 13s` | `+00° 51' 48"`<br/>`00h 34m 27s` | `-13° 12' 01"` |
| `2026-11-23` | `-20° 17' 36"`<br/>`15h 54m 11s` | `+18° 49' 05"`<br/>`02h 17m 14s` | `+13° 52' 03"`<br/>`10h 06m 43s` | `-13° 04' 28"`<br/>`14h 38m 38s` | `+13° 26' 50"`<br/>`09h 55m 31s` | `-09° 16' 14"`<br/>`13h 30m 40s` | `+00° 51' 14"`<br/>`00h 34m 19s` | `-13° 13' 05"` |
| `2026-11-24` | `-20° 29' 59"`<br/>`15h 58m 24s` | `+23° 22' 03"`<br/>`03h 17m 06s` | `+13° 44' 48"`<br/>`10h 08m 20s` | `-13° 29' 48"`<br/>`14h 43m 12s` | `+13° 25' 48"`<br/>`09h 55m 46s` | `-09° 13' 57"`<br/>`13h 32m 14s` | `+00° 50' 42"`<br/>`00h 34m 12s` | `-13° 14' 08"` |
| `2026-11-25` | `-20° 42' 00"`<br/>`16h 02m 38s` | `+26° 26' 49"`<br/>`04h 21m 41s` | `+13° 37' 39"`<br/>`10h 09m 56s` | `-13° 56' 19"`<br/>`14h 47m 59s` | `+13° 24' 49"`<br/>`09h 56m 00s` | `-09° 12' 40"`<br/>`13h 33m 55s` | `+00° 50' 13"`<br/>`00h 34m 06s` | `-13° 15' 12"` |
| `2026-11-26` | `-20° 53' 37"`<br/>`16h 06m 53s` | `+27° 38' 23"`<br/>`05h 29m 14s` | `+13° 30' 34"`<br/>`10h 11m 31s` | `-14° 23' 45"`<br/>`14h 52m 59s` | `+13° 23' 54"`<br/>`09h 56m 13s` | `-09° 12' 21"`<br/>`13h 35m 42s` | `+00° 49' 47"`<br/>`00h 33m 59s` | `-13° 16' 16"` |
| `2026-11-27` | `-21° 04' 52"`<br/>`16h 11m 08s` | `+26° 46' 36"`<br/>`06h 36m 50s` | `+13° 23' 35"`<br/>`10h 13m 05s` | `-14° 51' 51"`<br/>`14h 58m 09s` | `+13° 23' 03"`<br/>`09h 56m 26s` | `-09° 13' 00"`<br/>`13h 37m 35s` | `+00° 49' 23"`<br/>`00h 33m 53s` | `-13° 17' 19"` |
| `2026-11-28` | `-21° 15' 42"`<br/>`16h 15m 24s` | `+24° 00' 31"`<br/>`07h 41m 33s` | `+13° 16' 42"`<br/>`10h 14m 37s` | `-15° 20' 24"`<br/>`15h 03m 28s` | `+13° 22' 15"`<br/>`09h 56m 38s` | `-09° 14' 32"`<br/>`13h 39m 35s` | `+00° 49' 01"`<br/>`00h 33m 47s` | `-13° 18' 23"` |
| `2026-11-29` | `-21° 26' 09"`<br/>`16h 19m 41s` | `+19° 43' 44"`<br/>`08h 41m 39s` | `+13° 09' 55"`<br/>`10h 16m 08s` | `-15° 49' 12"`<br/>`15h 08m 55s` | `+13° 21' 31"`<br/>`09h 56m 49s` | `-09° 16' 58"`<br/>`13h 41m 40s` | `+00° 48' 43"`<br/>`00h 33m 42s` | `-13° 19' 26"` |
| `2026-11-30` | `-21° 36' 11"`<br/>`16h 23m 59s` | `+14° 24' 53"`<br/>`09h 36m 53s` | `+13° 03' 15"`<br/>`10h 17m 38s` | `-16° 18' 05"`<br/>`15h 14m 29s` | `+13° 20' 51"`<br/>`09h 56m 59s` | `-09° 20' 14"`<br/>`13h 43m 51s` | `+00° 48' 26"`<br/>`00h 33m 37s` | `-13° 20' 30"` |

### Table 3B — Daily Ecliptic Latitude ($\beta$ / *Shara*), Geocentric Distance ($R$ in AU), Lunar Parallax (`HP`), Disk Illumination (`%`), & Visual Magnitude ($V_{\text{mag}}$)

| Date | Moon $\beta$ (`DMS`) | Moon `HP` / Diam | Moon Illum `%` | Mars $\beta$ / Dist (`AU`) / $V_{\text{mag}}$ | Mercury $\beta$ / Dist (`AU`) / $V_{\text{mag}}$ | Jupiter $\beta$ / Dist (`AU`) / $V_{\text{mag}}$ | Venus $\beta$ / Dist (`AU`) / $V_{\text{mag}}$ | Saturn $\beta$ / Dist (`AU`) / $V_{\text{mag}}$ |
|---|---|---|---|---|---|---|---|---|
| `2026-11-01` | `+02° 29' 29"` | `3556.7"` / `1937.6"` | **`59.6%`** | `+01° 36' 02"`<br/>`1.4325 AU` (`+1.05m`) | `-01° 32' 56"`<br/>`0.6816 AU` (`+92.27m`) | `+00° 41' 24"`<br/>`5.4996 AU` (`-2.01m`) | `-04° 52' 00"`<br/>`0.2798 AU` (`+2.10m`) | `-02° 41' 05"`<br/>`8.5479 AU` (`+0.69m`) |
| `2026-11-02` | `+01° 21' 04"` | `3526.6"` / `1921.2"` | **`48.4%`** | `+01° 37' 17"`<br/>`1.4244 AU` (`+1.04m`) | `-01° 14' 36"`<br/>`0.6760 AU` (`+106.03m`) | `+00° 41' 37"`<br/>`5.4845 AU` (`-2.02m`) | `-04° 37' 26"`<br/>`0.2819 AU` (`+1.86m`) | `-02° 40' 57"`<br/>`8.5561 AU` (`+0.70m`) |
| `2026-11-03` | `+00° 09' 08"` | `3494.6"` / `1903.7"` | **`37.4%`** | `+01° 38' 33"`<br/>`1.4162 AU` (`+1.03m`) | `-00° 55' 06"`<br/>`0.6730 AU` (`+121.64m`) | `+00° 41' 49"`<br/>`5.4693 AU` (`-2.02m`) | `-04° 22' 38"`<br/>`0.2843 AU` (`+1.64m`) | `-02° 40' 48"`<br/>`8.5646 AU` (`+0.70m`) |
| `2026-11-04` | `-01° 02' 00"` | `3462.1"` / `1886.1"` | **`27.2%`** | `+01° 39' 50"`<br/>`1.4080 AU` (`+1.02m`) | `-00° 34' 48"`<br/>`0.6728 AU` (`+139.21m`) | `+00° 42' 01"`<br/>`5.4540 AU` (`-2.03m`) | `-04° 07' 40"`<br/>`0.2869 AU` (`+1.42m`) | `-02° 40' 39"`<br/>`8.5734 AU` (`+0.71m`) |
| `2026-11-05` | `-02° 08' 30"` | `3430.2"` / `1868.7"` | **`18.2%`** | `+01° 41' 07"`<br/>`1.3998 AU` (`+1.01m`) | `-00° 14' 08"`<br/>`0.6756 AU` (`+142.91m`) | `+00° 42' 14"`<br/>`5.4387 AU` (`-2.04m`) | `-03° 52' 35"`<br/>`0.2898 AU` (`+1.21m`) | `-02° 40' 30"`<br/>`8.5824 AU` (`+0.71m`) |
| `2026-11-06` | `-03° 07' 04"` | `3399.3"` / `1851.9"` | **`10.9%`** | `+01° 42' 25"`<br/>`1.3915 AU` (`+1.00m`) | `+00° 06' 29"`<br/>`0.6814 AU` (`+124.45m`) | `+00° 42' 27"`<br/>`5.4233 AU` (`-2.04m`) | `-03° 37' 26"`<br/>`0.2929 AU` (`+1.01m`) | `-02° 40' 21"`<br/>`8.5917 AU` (`+0.72m`) |
| `2026-11-07` | `-03° 55' 01"` | `3369.6"` / `1835.7"` | **`5.3%`** | `+01° 43' 44"`<br/>`1.3832 AU` (`+0.98m`) | `+00° 26' 34"`<br/>`0.6902 AU` (`+107.57m`) | `+00° 42' 39"`<br/>`5.4079 AU` (`-2.05m`) | `-03° 22' 16"`<br/>`0.2963 AU` (`+0.82m`) | `-02° 40' 11"`<br/>`8.6012 AU` (`+0.72m`) |
| `2026-11-08` | `-04° 30' 26"` | `3341.3"` / `1820.3"` | **`1.7%`** | `+01° 45' 03"`<br/>`1.3749 AU` (`+0.97m`) | `+00° 45' 42"`<br/>`0.7019 AU` (`+92.32m`) | `+00° 42' 52"`<br/>`5.3924 AU` (`-2.05m`) | `-03° 07' 10"`<br/>`0.2999 AU` (`+0.64m`) | `-02° 40' 01"`<br/>`8.6110 AU` (`+0.73m`) |
| `2026-11-09` | `-04° 52' 08"` | `3314.8"` / `1805.8"` | **`0.1%`** | `+01° 46' 23"`<br/>`1.3665 AU` (`+0.96m`) | `+01° 03' 31"`<br/>`0.7163 AU` (`+78.71m`) | `+00° 43' 05"`<br/>`5.3769 AU` (`-2.06m`) | `-02° 52' 09"`<br/>`0.3037 AU` (`+0.47m`) | `-02° 39' 50"`<br/>`8.6210 AU` (`+0.73m`) |
| `2026-11-10` | `-04° 59' 39"` | `3290.9"` / `1792.8"` | **`0.5%`** | `+01° 47' 43"`<br/>`1.3582 AU` (`+0.95m`) | `+01° 19' 43"`<br/>`0.7333 AU` (`+66.70m`) | `+00° 43' 18"`<br/>`5.3613 AU` (`-2.07m`) | `-02° 37' 16"`<br/>`0.3077 AU` (`+0.30m`) | `-02° 39' 40"`<br/>`8.6313 AU` (`+0.74m`) |
| `2026-11-11` | `-04° 53' 15"` | `3270.6"` / `1781.8"` | **`2.8%`** | `+01° 49' 04"`<br/>`1.3497 AU` (`+0.94m`) | `+01° 34' 07"`<br/>`0.7525 AU` (`+56.19m`) | `+00° 43' 31"`<br/>`5.3458 AU` (`-2.07m`) | `-02° 22' 33"`<br/>`0.3119 AU` (`+0.14m`) | `-02° 39' 29"`<br/>`8.6418 AU` (`+0.74m`) |
| `2026-11-12` | `-04° 33' 45"` | `3255.0"` / `1773.3"` | **`6.8%`** | `+01° 50' 26"`<br/>`1.3413 AU` (`+0.93m`) | `+01° 46' 36"`<br/>`0.7736 AU` (`+47.10m`) | `+00° 43' 44"`<br/>`5.3301 AU` (`-2.08m`) | `-02° 08' 03"`<br/>`0.3163 AU` (`-0.01m`) | `-02° 39' 18"`<br/>`8.6526 AU` (`+0.75m`) |
| `2026-11-13` | `-04° 02' 23"` | `3245.6"` / `1768.1"` | **`12.3%`** | `+01° 51' 49"`<br/>`1.3328 AU` (`+0.91m`) | `+01° 57' 08"`<br/>`0.7964 AU` (`+39.28m`) | `+00° 43' 58"`<br/>`5.3145 AU` (`-2.08m`) | `-01° 53' 47"`<br/>`0.3209 AU` (`-0.16m`) | `-02° 39' 07"`<br/>`8.6636 AU` (`+0.75m`) |
| `2026-11-14` | `-03° 20' 43"` | `3243.6"` / `1767.0"` | **`19.2%`** | `+01° 53' 12"`<br/>`1.3244 AU` (`+0.90m`) | `+02° 05' 46"`<br/>`0.8204 AU` (`+32.63m`) | `+00° 44' 11"`<br/>`5.2988 AU` (`-2.09m`) | `-01° 39' 46"`<br/>`0.3256 AU` (`-0.29m`) | `-02° 38' 55"`<br/>`8.6748 AU` (`+0.75m`) |
| `2026-11-15` | `-02° 30' 25"` | `3250.2"` / `1770.7"` | **`27.1%`** | `+01° 54' 36"`<br/>`1.3159 AU` (`+0.89m`) | `+02° 12' 34"`<br/>`0.8454 AU` (`+26.99m`) | `+00° 44' 24"`<br/>`5.2831 AU` (`-2.10m`) | `-01° 26' 02"`<br/>`0.3306 AU` (`-0.42m`) | `-02° 38' 43"`<br/>`8.6862 AU` (`+0.76m`) |
| `2026-11-16` | `-01° 33' 22"` | `3266.4"` / `1779.5"` | **`35.9%`** | `+01° 56' 01"`<br/>`1.3073 AU` (`+0.87m`) | `+02° 17' 38"`<br/>`0.8711 AU` (`+22.24m`) | `+00° 44' 38"`<br/>`5.2674 AU` (`-2.10m`) | `-01° 12' 37"`<br/>`0.3356 AU` (`-0.55m`) | `-02° 38' 31"`<br/>`8.6978 AU` (`+0.76m`) |
| `2026-11-17` | `-00° 31' 31"` | `3292.7"` / `1793.8"` | **`45.2%`** | `+01° 57' 27"`<br/>`1.2988 AU` (`+0.86m`) | `+02° 21' 07"`<br/>`0.8971 AU` (`+18.27m`) | `+00° 44' 52"`<br/>`5.2517 AU` (`-2.11m`) | `-00° 59' 30"`<br/>`0.3409 AU` (`-0.67m`) | `-02° 38' 19"`<br/>`8.7097 AU` (`+0.77m`) |
| `2026-11-18` | `+00° 32' 55"` | `3328.9"` / `1813.5"` | **`55.0%`** | `+01° 58' 53"`<br/>`1.2902 AU` (`+0.85m`) | `+02° 23' 10"`<br/>`0.9233 AU` (`+14.95m`) | `+00° 45' 05"`<br/>`5.2360 AU` (`-2.12m`) | `-00° 46' 43"`<br/>`0.3462 AU` (`-0.78m`) | `-02° 38' 07"`<br/>`8.7218 AU` (`+0.77m`) |
| `2026-11-19` | `+01° 37' 22"` | `3374.1"` / `1838.1"` | **`64.8%`** | `+02° 00' 20"`<br/>`1.2816 AU` (`+0.83m`) | `+02° 23' 54"`<br/>`0.9495 AU` (`+12.20m`) | `+00° 45' 19"`<br/>`5.2203 AU` (`-2.12m`) | `-00° 34' 17"`<br/>`0.3518 AU` (`-0.89m`) | `-02° 37' 54"`<br/>`8.7341 AU` (`+0.78m`) |
| `2026-11-20` | `+02° 38' 51"` | `3426.4"` / `1866.6"` | **`74.3%`** | `+02° 01' 48"`<br/>`1.2730 AU` (`+0.82m`) | `+02° 23' 28"`<br/>`0.9754 AU` (`+9.92m`) | `+00° 45' 33"`<br/>`5.2046 AU` (`-2.13m`) | `-00° 22' 12"`<br/>`0.3574 AU` (`-0.99m`) | `-02° 37' 42"`<br/>`8.7465 AU` (`+0.78m`) |
| `2026-11-21` | `+03° 33' 49"` | `3482.7"` / `1897.3"` | **`83.1%`** | `+02° 03' 16"`<br/>`1.2644 AU` (`+0.80m`) | `+02° 22' 00"`<br/>`1.0009 AU` (`+8.03m`) | `+00° 45' 47"`<br/>`5.1888 AU` (`-2.14m`) | `-00° 10' 29"`<br/>`0.3632 AU` (`-1.08m`) | `-02° 37' 29"`<br/>`8.7592 AU` (`+0.79m`) |
| `2026-11-22` | `+04° 18' 19"` | `3538.8"` / `1927.8"` | **`90.6%`** | `+02° 04' 46"`<br/>`1.2558 AU` (`+0.79m`) | `+02° 19' 38"`<br/>`1.0259 AU` (`+6.48m`) | `+00° 46' 01"`<br/>`5.1731 AU` (`-2.14m`) | `+00° 00' 54"`<br/>`0.3691 AU` (`-1.18m`) | `-02° 37' 16"`<br/>`8.7721 AU` (`+0.79m`) |
| `2026-11-23` | `+04° 48' 17"` | `3589.5"` / `1955.5"` | **`96.2%`** | `+02° 06' 16"`<br/>`1.2471 AU` (`+0.77m`) | `+02° 16' 28"`<br/>`1.0503 AU` (`+5.20m`) | `+00° 46' 15"`<br/>`5.1575 AU` (`-2.15m`) | `+00° 11' 54"`<br/>`0.3751 AU` (`-1.26m`) | `-02° 37' 03"`<br/>`8.7851 AU` (`+0.80m`) |
| `2026-11-24` | `+05° 00' 12"` | `3629.5"` / `1977.2"` | **`99.4%`** | `+02° 07' 47"`<br/>`1.2384 AU` (`+0.76m`) | `+02° 12' 36"`<br/>`1.0740 AU` (`+4.14m`) | `+00° 46' 29"`<br/>`5.1418 AU` (`-2.16m`) | `+00° 22' 32"`<br/>`0.3812 AU` (`-1.35m`) | `-02° 36' 49"`<br/>`8.7984 AU` (`+0.80m`) |
| `2026-11-25` | `+04° 51' 53"` | `3654.2"` / `1990.7"` | **`99.8%`** | `+02° 09' 18"`<br/>`1.2298 AU` (`+0.74m`) | `+02° 08' 09"`<br/>`1.0970 AU` (`+3.28m`) | `+00° 46' 43"`<br/>`5.1262 AU` (`-2.16m`) | `+00° 32' 49"`<br/>`0.3874 AU` (`-1.43m`) | `-02° 36' 36"`<br/>`8.8118 AU` (`+0.81m`) |
| `2026-11-26` | `+04° 23' 10"` | `3661.2"` / `1994.5"` | **`97.2%`** | `+02° 10' 51"`<br/>`1.2211 AU` (`+0.73m`) | `+02° 03' 10"`<br/>`1.1192 AU` (`+2.57m`) | `+00° 46' 57"`<br/>`5.1105 AU` (`-2.17m`) | `+00° 42' 44"`<br/>`0.3937 AU` (`-1.50m`) | `-02° 36' 22"`<br/>`8.8254 AU` (`+0.81m`) |
| `2026-11-27` | `+03° 36' 12"` | `3650.3"` / `1988.6"` | **`91.7%`** | `+02° 12' 24"`<br/>`1.2124 AU` (`+0.71m`) | `+01° 57' 44"`<br/>`1.1407 AU` (`+1.99m`) | `+00° 47' 12"`<br/>`5.0950 AU` (`-2.17m`) | `+00° 52' 18"`<br/>`0.4001 AU` (`-1.57m`) | `-02° 36' 08"`<br/>`8.8391 AU` (`+0.82m`) |
| `2026-11-28` | `+02° 35' 03"` | `3624.0"` / `1974.2"` | **`83.9%`** | `+02° 13' 58"`<br/>`1.2037 AU` (`+0.70m`) | `+01° 51' 56"`<br/>`1.1613 AU` (`+1.51m`) | `+00° 47' 26"`<br/>`5.0794 AU` (`-2.18m`) | `+01° 01' 30"`<br/>`0.4066 AU` (`-1.64m`) | `-02° 35' 54"`<br/>`8.8530 AU` (`+0.82m`) |
| `2026-11-29` | `+01° 24' 50"` | `3586.2"` / `1953.7"` | **`74.3%`** | `+02° 15' 33"`<br/>`1.1950 AU` (`+0.68m`) | `+01° 45' 48"`<br/>`1.1811 AU` (`+1.12m`) | `+00° 47' 40"`<br/>`5.0639 AU` (`-2.19m`) | `+01° 10' 21"`<br/>`0.4131 AU` (`-1.71m`) | `-02° 35' 40"`<br/>`8.8671 AU` (`+0.83m`) |
| `2026-11-30` | `+00° 10' 57"` | `3541.8"` / `1929.5"` | **`63.8%`** | `+02° 17' 09"`<br/>`1.1862 AU` (`+0.66m`) | `+01° 39' 23"`<br/>`1.2000 AU` (`+0.80m`) | `+00° 47' 55"`<br/>`5.0485 AU` (`-2.19m`) | `+01° 18' 52"`<br/>`0.4198 AU` (`-1.77m`) | `-02° 35' 26"`<br/>`8.8814 AU` (`+0.83m`) |

## Chapter 4 — Monthly Astronomical & Astrological Phenomena Almanac (Exact Sign Ingresses, Nakshatra Ingresses, Synodic Aspects, & *Krantisamya Mahapata* Windows)

### Table 4A — Exact Planetary Sign Ingresses (*Rashi Sankranti*) During the Month

| Planet | From Rashi | To Rashi | Exact Ingress Longitude | Exact UTC Timestamp | Exact Julian Date (`JD UT`) | Direction |
|---|---|---|---|---|---|---|
| **Venus** | Tula | **Kanya** | `180.0000°` | `2026-11-05T19:34:21Z` | `2461350.315519` | Retrograde Ingress |
| **Mars** | Karka | **Simha** | `120.0000°` | `2026-11-12T14:48:36Z` | `2461357.117086` | Direct Ingress |
| **Sun** | Tula | **Vrishchika** | `210.0000°` | `2026-11-16T14:13:13Z` | `2461361.092506` | Direct Ingress |
| **Venus** | Kanya | **Tula** | `180.0000°` | `2026-11-22T11:51:09Z` | `2461366.993850` | Direct Ingress |

### Table 4B — Exact Planetary *Nakshatra* Ingresses During the Month

| Planet | From Nakshatra | To Nakshatra | Exact UTC Timestamp | Exact Julian Date (`JD UT`) | Motion |
|---|---|---|---|---|---|
| **Mercury** | Vishakha | **Swati** | `2026-11-03T00:29:07Z` | `2461347.520214` | Retrograde |
| **Sun** | Swati | **Vishakha** | `2026-11-06T15:33:21Z` | `2461351.148164` | Direct |
| **Mars** | Ashlesha | **Magha** | `2026-11-12T14:48:36Z` | `2461357.117086` | Direct |
| **Sun** | Vishakha | **Anuradha** | `2026-11-19T21:33:53Z` | `2461364.398529` | Direct |
| **Mercury** | Swati | **Vishakha** | `2026-11-25T08:11:18Z` | `2461369.841175` | Direct |

### Table 4C — Exact Synodic Planetary Aspects (`0°, 60°, 90°, 120°, 180°`) During the Month

| Body 1 | Body 2 | Aspect Type | Exact Angle | Body 1 Longitude | Body 2 Longitude | Exact UTC Timestamp |
|---|---|---|---|---|---|---|
| **Sun** | **Mercury** | **Conjunction** | `0°` | `Tula 17° 56' 48"` | `Tula 17° 56' 48"` | `2026-11-04T14:24:19Z` |
| **Jupiter** | **Rahu** | **Opposition** | `180°` | `Simha 01° 15' 51"` | `Kumbha 01° 15' 51"` | `2026-11-11T20:30:18Z` |
| **Mars** | **Rahu** | **Opposition** | `180°` | `Simha 01° 05' 47"` | `Kumbha 01° 05' 47"` | `2026-11-15T00:31:01Z` |
| **Mars** | **Jupiter** | **Conjunction** | `0°` | `Simha 01° 39' 15"` | `Simha 01° 39' 15"` | `2026-11-16T06:23:39Z` |
| **Sun** | **Jupiter** | **Square** | `90°` | `Vrishchika 01° 49' 26"` | `Simha 01° 49' 26"` | `2026-11-18T09:38:35Z` |
| **Sun** | **Mars** | **Square** | `90°` | `Vrishchika 03° 10' 33"` | `Simha 03° 10' 33"` | `2026-11-19T17:49:01Z` |

### Table 4D — Exact *Surya Siddhanta Krantisamya* (*Vyatipata* & *Vaidhriti Mahapata*) Declination-Equality Windows

| Mahapata Type | Classical Condition | Peak Exact JD (`UT`) | Window Start (`JD UT`) | Window End (`JD UT`) | Sun Declination ($\delta_\odot$) | Moon Declination ($\delta_{\mathbb{C}}$) |
|---|---|---|---|---|---|---|
| **Vaidhriti Mahapata** | $\delta_\odot = -\delta_{\mathbb{C}}$ (Opposite Hemisphere) | `2461347.20768` | `2461347.11724` | `2461347.29811` | `-14.9018°` | `+14.9018°` |
| **Vyatipata Mahapata** | $\delta_\odot = +\delta_{\mathbb{C}}$ (Same Hemisphere) | `2461360.79495` | `2461360.67755` | `2461360.91234` | `-18.7535°` | `-18.7535°` |
| **Vaidhriti Mahapata** | $\delta_\odot = -\delta_{\mathbb{C}}$ (Opposite Hemisphere) | `2461373.14836` | `2461373.03515` | `2461373.26156` | `-21.3758°` | `+21.3758°` |

## Chapter 5 — Section 2 — Daily Sunrise-Anchored *Drik Panchanga*, *Ghati-Pala* Almanac, & *Muhurta* Table

**Vedic Timekeeping Conversion:** $1\text{ Solar Day} = 24\text{ Hours} = 60\text{ Ghatis (Nadis)}$; $1\text{ Hour} = 2.5\text{ Ghatis}$; $1\text{ Ghati} = 24\text{ Minutes} = 60\text{ Palas (Vinadis)}$; $1\text{ Pala} = 24\text{ Seconds}$.

| Date | Vara | Sunrise | Sunset | *Dinamana* (`Hours / Ghatis`) | Sunrise Tithi | Tithi Ends (`Clock / Ghati-Pala`) | Sunrise Nakshatra | Sunrise Yoga | Sunrise Karana | *Rahu Kala* | *Abhijit Muhurta* | Observances (*Vratas*) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `2026-11-01` | Ravivara | `06:31:53` | `17:48:44` | `11.28h` (`28g 12p`) | **Krishna Saptami** | `14:52` (`20g 51p`) | Pushya | Sadhya | Bava | `16:24-17:49` | `11:48-12:33` | — |
| `2026-11-02` | Somavara | `06:32:26` | `17:48:08` | `11.26h` (`28g 09p`) | **Krishna Ashtami** | `13:11` (`16g 36p`) | Ashlesha | Shubha | Kaulava | `07:57-09:21` | `11:48-12:33` | — |
| `2026-11-03` | Mangalavara | `06:33:00` | `17:47:33` | `11.24h` (`28g 06p`) | **Krishna Navami** | `11:55` (`13g 25p`) | Magha | Shukla | Gara | `14:59-16:23` | `11:48-12:33` | — |
| `2026-11-04` | Budhavara | `06:33:34` | `17:47:00` | `11.22h` (`28g 04p`) | **Krishna Dashami** | `11:04` (`11g 16p`) | Purva Phalguni | Brahma | Vishti | `12:10-13:34` | `11:48-12:33` | — |
| `2026-11-05` | Guruvara | `06:34:09` | `17:46:28` | `11.21h` (`28g 01p`) | **Krishna Ekadashi** | `10:36` (`10g 05p`) | Uttara Phalguni | Vaidhriti | Balava | `13:34-14:58` | `11:48-12:33` | Ekadashi (Shuddha (Smarta & Vaishnava)) |
| `2026-11-06` | Shukravara | `06:34:44` | `17:45:57` | `11.19h` (`27g 58p`) | **Krishna Dwadashi** | `10:31` (`09g 51p`) | Hasta | Vishkumbha | Taitila | `10:46-12:10` | `11:48-12:33` | Pradosha Vrata |
| `2026-11-07` | Shanivara | `06:35:20` | `17:45:27` | `11.17h` (`27g 55p`) | **Krishna Trayodashi** | `10:48` (`10g 33p`) | Chitra | Priti | Vanija | `09:23-10:47` | `11:48-12:33` | — |
| `2026-11-08` | Ravivara | `06:35:56` | `17:44:59` | `11.15h` (`27g 53p`) | **Krishna Chaturdashi** | `11:28` (`12g 11p`) | Swati | Ayushman | Shakuni | `16:21-17:45` | `11:48-12:33` | — |
| `2026-11-09` | Somavara | `06:36:33` | `17:44:31` | `11.13h` (`27g 50p`) | **Amavasya** | `12:32` (`14g 49p`) | Swati | Saubhagya | Naga | `08:00-09:24` | `11:48-12:33` | Amavasya |
| `2026-11-10` | Mangalavara | `06:37:10` | `17:44:05` | `11.12h` (`27g 47p`) | **Shukla Pratipada** | `14:01` (`18g 29p`) | Vishakha | Shobhana | Bava | `14:57-16:21` | `11:48-12:33` | — |
| `2026-11-11` | Budhavara | `06:37:47` | `17:43:41` | `11.10h` (`27g 45p`) | **Shukla Dwitiya** | `15:54` (`23g 10p`) | Anuradha | Atiganda | Kaulava | `12:11-13:34` | `11:49-12:33` | — |
| `2026-11-12` | Guruvara | `06:38:25` | `17:43:18` | `11.08h` (`27g 42p`) | **Shukla Tritiya** | `18:10` (`28g 49p`) | Jyeshtha | Sukarma | Gara | `13:34-14:57` | `11:49-12:33` | — |
| `2026-11-13` | Shukravara | `06:39:03` | `17:42:56` | `11.06h` (`27g 40p`) | **Shukla Chaturthi** | `20:43` (`35g 10p`) | Mula | Dhriti | Vanija | `10:48-12:11` | `11:49-12:33` | — |
| `2026-11-14` | Shanivara | `06:39:42` | `17:42:35` | `11.05h` (`27g 37p`) | **Shukla Panchami** | `23:24` (`41g 52p`) | Purva Ashadha | Shula | Bava | `09:25-10:48` | `11:49-12:33` | — |
| `2026-11-15` | Ravivara | `06:40:21` | `17:42:16` | `11.03h` (`27g 35p`) | **Shukla Shashthi** | `02:02` (`48g 23p`) | Uttara Ashadha | Ganda | Kaulava | `16:20-17:42` | `11:49-12:33` | — |
| `2026-11-16` | Somavara | `06:41:00` | `17:41:58` | `11.02h` (`27g 32p`) | **Shukla Saptami** | `04:20` (`54g 08p`) | Shravana | Ganda | Gara | `08:04-09:26` | `11:49-12:34` | Vrishchika Sankranti |
| `2026-11-17` | Mangalavara | `06:41:39` | `17:41:41` | `11.00h` (`27g 30p`) | **Shukla Ashtami** | `06:06` (`58g 30p`) | Dhanishta | Vriddhi | Vishti | `14:57-16:19` | `11:50-12:34` | — |
| `2026-11-18` | Budhavara | `06:42:19` | `17:41:26` | `10.99h` (`27g 28p`) | **Shukla Navami** | `07:07` (`61g 01p`) | Shatabhisha | Dhruva | Balava | `12:12-13:34` | `11:50-12:34` | — |
| `2026-11-19` | Guruvara | `06:42:59` | `17:41:12` | `10.97h` (`27g 26p`) | **Shukla Navami** | `07:07` (`00g 59p`) | Purva Bhadrapada | Vyaghata | Kaulava | `13:34-14:57` | `11:50-12:34` | — |
| `2026-11-20` | Shukravara | `06:43:39` | `17:41:00` | `10.96h` (`27g 23p`) | **Shukla Dashami** | `07:16` (`01g 21p`) | Purva Bhadrapada | Vajra | Gara | `10:50-12:12` | `11:50-12:34` | — |
| `2026-11-21` | Shanivara | `06:44:19` | `17:40:49` | `10.94h` (`27g 21p`) | **Shukla Dwadashi** | `04:57` (`55g 32p`) | Uttara Bhadrapada | Siddhi | Bava | `09:28-10:51` | `11:51-12:34` | — |
| `2026-11-22` | Ravivara | `06:45:00` | `17:40:39` | `10.93h` (`27g 19p`) | **Shukla Trayodashi** | `02:38` (`49g 42p`) | Ashwini | Vyatipata | Kaulava | `16:19-17:41` | `11:51-12:35` | Pradosha Vrata |
| `2026-11-23` | Somavara | `06:45:40` | `17:40:31` | `10.91h` (`27g 17p`) | **Shukla Chaturdashi** | `23:43` (`42g 23p`) | Bharani | Variyan | Gara | `08:08-09:29` | `11:51-12:35` | — |
| `2026-11-24` | Mangalavara | `06:46:21` | `17:40:24` | `10.90h` (`27g 15p`) | **Purnima** | `20:24` (`34g 03p`) | Krittika | Parigha | Vishti | `14:57-16:19` | `11:52-12:35` | Purnima |
| `2026-11-25` | Budhavara | `06:47:02` | `17:40:19` | `10.89h` (`27g 13p`) | **Krishna Pratipada** | `16:51` (`25g 09p`) | Rohini | Shiva | Kaulava | `12:14-13:35` | `11:52-12:35` | — |
| `2026-11-26` | Guruvara | `06:47:43` | `17:40:15` | `10.88h` (`27g 11p`) | **Krishna Dwitiya** | `13:16` (`16g 10p`) | Mrigashirsha | Siddha | Gara | `13:36-14:57` | `11:52-12:36` | — |
| `2026-11-27` | Shukravara | `06:48:24` | `17:40:13` | `10.86h` (`27g 10p`) | **Krishna Tritiya** | `09:49` (`07g 32p`) | Ardra | Shubha | Vishti | `10:53-12:14` | `11:53-12:36` | — |
| `2026-11-28` | Shanivara | `06:49:05` | `17:40:12` | `10.85h` (`27g 08p`) | **Krishna Panchami** | `03:58` (`52g 52p`) | Punarvasu | Shukla | Kaulava | `09:32-10:53` | `11:53-12:36` | — |
| `2026-11-29` | Ravivara | `06:49:46` | `17:40:13` | `10.84h` (`27g 06p`) | **Krishna Shashthi** | `01:47` (`47g 23p`) | Pushya | Brahma | Gara | `16:19-17:40` | `11:53-12:37` | — |
| `2026-11-30` | Somavara | `06:50:27` | `17:40:15` | `10.83h` (`27g 04p`) | **Krishna Saptami** | `00:12` (`43g 24p`) | Ashlesha | Indra | Vishti | `08:12-09:33` | `11:54-12:37` | — |

## Chapter 6 — Section 3 — Manual *Spashta Graha* Interpolation Compendium (1st-Order *Trairashika* & 2nd-Order Bessel Lunar Tables)

### 6.1 First-Order *Trairashika* (Rule of Three) & Second-Order Bessel Formula
- **First-Order Formula (Sufficient for Sun, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu to `< 0.5"`):**
  $$\lambda_1(t) = \lambda(05\text{:}30\text{ IST}) + f \times v_{\text{day}}, \quad f = \frac{\Delta t_{\text{hours}}}{24} = \frac{\Delta G_{\text{ghatis}}}{60}$$
- **Second-Order Bessel Formula (For Sub-Arcsecond Manual Interpolation of the Fast-Moving Moon):**
  $$\lambda_2(t) = \lambda_1(t) + \frac{f(f - 1)}{4} \times \Delta^2 \lambda$$
  where $\Delta^2 \lambda$ is printed in **Table 2B** and the Bessel multiplier $B_2(f) = \frac{f(f-1)}{4}$ is printed in **Table 6A** below.

### Table 6A — Complete 96-Row 15-Minute (`00:00` to `24:00`) *Trairashika* Fraction ($f$), *Ghati-Pala*, & Bessel 2nd-Difference Coefficient ($B_2(f)$) Table

| Elapsed Time (`HH:MM`) | Elapsed *Ghati-Pala* | Fraction $f = \Delta t / 24$ | Bessel $B_2(f)$ | Sun Incr (`+59'08"/d`) | Mean Moon Incr (`+13°10'35"/d`) | Elapsed Time (`HH:MM`) | Elapsed *Ghati-Pala* | Fraction $f = \Delta t / 24$ | Bessel $B_2(f)$ | Sun Incr (`+59'08"/d`) | Mean Moon Incr (`+13°10'35"/d`) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `00:15` | `00g 38p` | **`0.01042`** | `-0.00258` | `+00° 00' 37"` | `+00° 08' 14"` | `12:15` | `30g 38p` | **`0.51042`** | `-0.06247` | `+00° 30' 11"` | `+06° 43' 32"` |
| `00:30` | `01g 15p` | **`0.02083`** | `-0.00510` | `+00° 01' 14"` | `+00° 16' 28"` | `12:30` | `31g 15p` | **`0.52083`** | `-0.06239` | `+00° 30' 48"` | `+06° 51' 46"` |
| `00:45` | `01g 52p` | **`0.03125`** | `-0.00757` | `+00° 01' 51"` | `+00° 24' 42"` | `12:45` | `31g 52p` | **`0.53125`** | `-0.06226` | `+00° 31' 25"` | `+07° 00' 00"` |
| `01:00` | `02g 30p` | **`0.04167`** | `-0.00998` | `+00° 02' 28"` | `+00° 32' 56"` | `13:00` | `32g 30p` | **`0.54167`** | `-0.06207` | `+00° 32' 02"` | `+07° 08' 14"` |
| `01:15` | `03g 08p` | **`0.05208`** | `-0.01234` | `+00° 03' 05"` | `+00° 41' 11"` | `13:15` | `33g 08p` | **`0.55208`** | `-0.06182` | `+00° 32' 39"` | `+07° 16' 28"` |
| `01:30` | `03g 45p` | **`0.06250`** | `-0.01465` | `+00° 03' 42"` | `+00° 49' 25"` | `13:30` | `33g 45p` | **`0.56250`** | `-0.06152` | `+00° 33' 16"` | `+07° 24' 42"` |
| `01:45` | `04g 22p` | **`0.07292`** | `-0.01690` | `+00° 04' 19"` | `+00° 57' 39"` | `13:45` | `34g 22p` | **`0.57292`** | `-0.06117` | `+00° 33' 53"` | `+07° 32' 56"` |
| `02:00` | `05g 00p` | **`0.08333`** | `-0.01910` | `+00° 04' 56"` | `+01° 05' 53"` | `14:00` | `35g 00p` | **`0.58333`** | `-0.06076` | `+00° 34' 30"` | `+07° 41' 10"` |
| `02:15` | `05g 38p` | **`0.09375`** | `-0.02124` | `+00° 05' 33"` | `+01° 14' 07"` | `14:15` | `35g 38p` | **`0.59375`** | `-0.06030` | `+00° 35' 07"` | `+07° 49' 25"` |
| `02:30` | `06g 15p` | **`0.10417`** | `-0.02333` | `+00° 06' 10"` | `+01° 22' 21"` | `14:30` | `36g 15p` | **`0.60417`** | `-0.05979` | `+00° 35' 44"` | `+07° 57' 39"` |
| `02:45` | `06g 52p` | **`0.11458`** | `-0.02536` | `+00° 06' 47"` | `+01° 30' 35"` | `14:45` | `36g 52p` | **`0.61458`** | `-0.05922` | `+00° 36' 21"` | `+08° 05' 53"` |
| `03:00` | `07g 30p` | **`0.12500`** | `-0.02734` | `+00° 07' 23"` | `+01° 38' 49"` | `15:00` | `37g 30p` | **`0.62500`** | `-0.05859` | `+00° 36' 57"` | `+08° 14' 07"` |
| `03:15` | `08g 08p` | **`0.13542`** | `-0.02927` | `+00° 08' 00"` | `+01° 47' 03"` | `15:15` | `38g 08p` | **`0.63542`** | `-0.05792` | `+00° 37' 34"` | `+08° 22' 21"` |
| `03:30` | `08g 45p` | **`0.14583`** | `-0.03114` | `+00° 08' 37"` | `+01° 55' 18"` | `15:30` | `38g 45p` | **`0.64583`** | `-0.05718` | `+00° 38' 11"` | `+08° 30' 35"` |
| `03:45` | `09g 22p` | **`0.15625`** | `-0.03296` | `+00° 09' 14"` | `+02° 03' 32"` | `15:45` | `39g 22p` | **`0.65625`** | `-0.05640` | `+00° 38' 48"` | `+08° 38' 49"` |
| `04:00` | `10g 00p` | **`0.16667`** | `-0.03472` | `+00° 09' 51"` | `+02° 11' 46"` | `16:00` | `40g 00p` | **`0.66667`** | `-0.05556` | `+00° 39' 25"` | `+08° 47' 03"` |
| `04:15` | `10g 38p` | **`0.17708`** | `-0.03643` | `+00° 10' 28"` | `+02° 20' 00"` | `16:15` | `40g 38p` | **`0.67708`** | `-0.05466` | `+00° 40' 02"` | `+08° 55' 17"` |
| `04:30` | `11g 15p` | **`0.18750`** | `-0.03809` | `+00° 11' 05"` | `+02° 28' 14"` | `16:30` | `41g 15p` | **`0.68750`** | `-0.05371` | `+00° 40' 39"` | `+09° 03' 32"` |
| `04:45` | `11g 52p` | **`0.19792`** | `-0.03969` | `+00° 11' 42"` | `+02° 36' 28"` | `16:45` | `41g 52p` | **`0.69792`** | `-0.05271` | `+00° 41' 16"` | `+09° 11' 46"` |
| `05:00` | `12g 30p` | **`0.20833`** | `-0.04123` | `+00° 12' 19"` | `+02° 44' 42"` | `17:00` | `42g 30p` | **`0.70833`** | `-0.05165` | `+00° 41' 53"` | `+09° 20' 00"` |
| `05:15` | `13g 08p` | **`0.21875`** | `-0.04272` | `+00° 12' 56"` | `+02° 52' 56"` | `17:15` | `43g 08p` | **`0.71875`** | `-0.05054` | `+00° 42' 30"` | `+09° 28' 14"` |
| `05:30` | `13g 45p` | **`0.22917`** | `-0.04416` | `+00° 13' 33"` | `+03° 01' 11"` | `17:30` | `43g 45p` | **`0.72917`** | `-0.04937` | `+00° 43' 07"` | `+09° 36' 28"` |
| `05:45` | `14g 22p` | **`0.23958`** | `-0.04555` | `+00° 14' 10"` | `+03° 09' 25"` | `17:45` | `44g 22p` | **`0.73958`** | `-0.04815` | `+00° 43' 44"` | `+09° 44' 42"` |
| `06:00` | `15g 00p` | **`0.25000`** | `-0.04688` | `+00° 14' 47"` | `+03° 17' 39"` | `18:00` | `45g 00p` | **`0.75000`** | `-0.04688` | `+00° 44' 21"` | `+09° 52' 56"` |
| `06:15` | `15g 38p` | **`0.26042`** | `-0.04815` | `+00° 15' 24"` | `+03° 25' 53"` | `18:15` | `45g 38p` | **`0.76042`** | `-0.04555` | `+00° 44' 58"` | `+10° 01' 10"` |
| `06:30` | `16g 15p` | **`0.27083`** | `-0.04937` | `+00° 16' 01"` | `+03° 34' 07"` | `18:30` | `46g 15p` | **`0.77083`** | `-0.04416` | `+00° 45' 35"` | `+10° 09' 24"` |
| `06:45` | `16g 52p` | **`0.28125`** | `-0.05054` | `+00° 16' 38"` | `+03° 42' 21"` | `18:45` | `46g 52p` | **`0.78125`** | `-0.04272` | `+00° 46' 12"` | `+10° 17' 39"` |
| `07:00` | `17g 30p` | **`0.29167`** | `-0.05165` | `+00° 17' 15"` | `+03° 50' 35"` | `19:00` | `47g 30p` | **`0.79167`** | `-0.04123` | `+00° 46' 49"` | `+10° 25' 53"` |
| `07:15` | `18g 08p` | **`0.30208`** | `-0.05271` | `+00° 17' 52"` | `+03° 58' 49"` | `19:15` | `48g 08p` | **`0.80208`** | `-0.03969` | `+00° 47' 26"` | `+10° 34' 07"` |
| `07:30` | `18g 45p` | **`0.31250`** | `-0.05371` | `+00° 18' 29"` | `+04° 07' 03"` | `19:30` | `48g 45p` | **`0.81250`** | `-0.03809` | `+00° 48' 03"` | `+10° 42' 21"` |
| `07:45` | `19g 22p` | **`0.32292`** | `-0.05466` | `+00° 19' 06"` | `+04° 15' 18"` | `19:45` | `49g 22p` | **`0.82292`** | `-0.03643` | `+00° 48' 40"` | `+10° 50' 35"` |
| `08:00` | `20g 00p` | **`0.33333`** | `-0.05556` | `+00° 19' 43"` | `+04° 23' 32"` | `20:00` | `50g 00p` | **`0.83333`** | `-0.03472` | `+00° 49' 17"` | `+10° 58' 49"` |
| `08:15` | `20g 38p` | **`0.34375`** | `-0.05640` | `+00° 20' 20"` | `+04° 31' 46"` | `20:15` | `50g 38p` | **`0.84375`** | `-0.03296` | `+00° 49' 54"` | `+11° 07' 03"` |
| `08:30` | `21g 15p` | **`0.35417`** | `-0.05718` | `+00° 20' 57"` | `+04° 40' 00"` | `20:30` | `51g 15p` | **`0.85417`** | `-0.03114` | `+00° 50' 31"` | `+11° 15' 17"` |
| `08:45` | `21g 52p` | **`0.36458`** | `-0.05792` | `+00° 21' 34"` | `+04° 48' 14"` | `20:45` | `51g 52p` | **`0.86458`** | `-0.02927` | `+00° 51' 08"` | `+11° 23' 32"` |
| `09:00` | `22g 30p` | **`0.37500`** | `-0.05859` | `+00° 22' 10"` | `+04° 56' 28"` | `21:00` | `52g 30p` | **`0.87500`** | `-0.02734` | `+00° 51' 44"` | `+11° 31' 46"` |
| `09:15` | `23g 08p` | **`0.38542`** | `-0.05922` | `+00° 22' 47"` | `+05° 04' 42"` | `21:15` | `53g 08p` | **`0.88542`** | `-0.02536` | `+00° 52' 21"` | `+11° 40' 00"` |
| `09:30` | `23g 45p` | **`0.39583`** | `-0.05979` | `+00° 23' 24"` | `+05° 12' 56"` | `21:30` | `53g 45p` | **`0.89583`** | `-0.02333` | `+00° 52' 58"` | `+11° 48' 14"` |
| `09:45` | `24g 22p` | **`0.40625`** | `-0.06030` | `+00° 24' 01"` | `+05° 21' 10"` | `21:45` | `54g 22p` | **`0.90625`** | `-0.02124` | `+00° 53' 35"` | `+11° 56' 28"` |
| `10:00` | `25g 00p` | **`0.41667`** | `-0.06076` | `+00° 24' 38"` | `+05° 29' 25"` | `22:00` | `55g 00p` | **`0.91667`** | `-0.01910` | `+00° 54' 12"` | `+12° 04' 42"` |
| `10:15` | `25g 38p` | **`0.42708`** | `-0.06117` | `+00° 25' 15"` | `+05° 37' 39"` | `22:15` | `55g 38p` | **`0.92708`** | `-0.01690` | `+00° 54' 49"` | `+12° 12' 56"` |
| `10:30` | `26g 15p` | **`0.43750`** | `-0.06152` | `+00° 25' 52"` | `+05° 45' 53"` | `22:30` | `56g 15p` | **`0.93750`** | `-0.01465` | `+00° 55' 26"` | `+12° 21' 10"` |
| `10:45` | `26g 52p` | **`0.44792`** | `-0.06182` | `+00° 26' 29"` | `+05° 54' 07"` | `22:45` | `56g 52p` | **`0.94792`** | `-0.01234` | `+00° 56' 03"` | `+12° 29' 24"` |
| `11:00` | `27g 30p` | **`0.45833`** | `-0.06207` | `+00° 27' 06"` | `+06° 02' 21"` | `23:00` | `57g 30p` | **`0.95833`** | `-0.00998` | `+00° 56' 40"` | `+12° 37' 39"` |
| `11:15` | `28g 08p` | **`0.46875`** | `-0.06226` | `+00° 27' 43"` | `+06° 10' 35"` | `23:15` | `58g 08p` | **`0.96875`** | `-0.00757` | `+00° 57' 17"` | `+12° 45' 53"` |
| `11:30` | `28g 45p` | **`0.47917`** | `-0.06239` | `+00° 28' 20"` | `+06° 18' 49"` | `23:30` | `58g 45p` | **`0.97917`** | `-0.00510` | `+00° 57' 54"` | `+12° 54' 07"` |
| `11:45` | `29g 22p` | **`0.48958`** | `-0.06247` | `+00° 28' 57"` | `+06° 27' 03"` | `23:45` | `59g 22p` | **`0.98958`** | `-0.00258` | `+00° 58' 31"` | `+13° 02' 21"` |
| `12:00` | `30g 00p` | **`0.50000`** | `-0.06250` | `+00° 29' 34"` | `+06° 35' 18"` | `24:00` | `60g 00p` | **`1.00000`** | `+0.00000` | `+00° 59' 08"` | `+13° 10' 35"` |

## Chapter 7 — Master Tables of Ascendants (*Udaya Lagna*), 10th House Midheaven (*Madhya Lagna*), & *Sripathi Bhava Chalit* Across World Latitudes

**How to Find the Exact Sidereal Ascendant (*Udaya Lagna*) and 10th Cusp (*Madhya Lagna*) from Table 7A:**
1. Take the **Local Sidereal Time (LST)** at `05:30 IST` from **Table 2A**.
2. Add the time elapsed from `05:30 IST` to Birth Time, plus `10 seconds per hour` of elapsed solar time (`+3m 56.56s` per 24h), and adjust by `(Observer Longitude - 75.7885°) × 4 minutes/degree` to get **Birth Local Sidereal Time (RAMC)**.
3. Look up the Birth LST row in **Table 7A** under your city's latitude column and subtract `(Current Lahiri Ayanamsha - 24° 13' 55")` if casting for another century.

### Table 7A — Master Sidereal Ascendant (*Udaya Lagna*) & 10th Cusp (*MC*) Lookup Grid (`00h 00m` to `23h 52m` LST across 9 World Latitudes, Lahiri `2026` Epoch)

| LST (`HH:MM`) | RAMC (`°`) | Sidereal 10th Cusp (*MC*) | `0°00'` Equator (*Lanka*) | `13°05'N` Chennai / Bengaluru | `19°05'N` Mumbai | `23°11'N` Ujjain / Kolkata | `28°37'N` New Delhi | `34°03'N` Los Angeles | `40°43'N` New York | `43°39'N` Toronto | `51°30'N` London |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **`00h 00m`** | `000°` | `11s 05° 46' 05"` | `02s 05° 46' 05"` | `02s 11° 02' 58"` | `02s 13° 36' 01"` | `02s 15° 25' 57"` | `02s 18° 00' 41"` | `02s 20° 48' 55"` | `02s 24° 39' 50"` | `02s 26° 33' 00"` | `03s 02° 20' 33"` |
| **`00h 16m`** | `004°` | `11s 10° 07' 35"` | `02s 09° 26' 20"` | `02s 14° 40' 50"` | `02s 17° 11' 27"` | `02s 18° 59' 07"` | `02s 21° 30' 00"` | `02s 24° 13' 09"` | `02s 27° 55' 43"` | `02s 29° 44' 14"` | `03s 05° 15' 36"` |
| **`00h 32m`** | `008°` | `11s 14° 28' 37"` | `02s 13° 06' 56"` | `02s 18° 18' 02"` | `02s 20° 45' 46"` | `02s 22° 30' 55"` | `02s 24° 57' 36"` | `02s 27° 35' 24"` | `03s 01° 09' 26"` | `03s 02° 53' 19"` | `03s 08° 08' 44"` |
| **`00h 48m`** | `012°` | `11s 18° 48' 43"` | `02s 16° 48' 12"` | `02s 21° 54' 54"` | `02s 24° 19' 20"` | `02s 26° 01' 41"` | `02s 28° 23' 51"` | `03s 00° 56' 05"` | `03s 04° 21' 24"` | `03s 06° 00' 37"` | `03s 11° 00' 19"` |
| **`01h 04m`** | `016°` | `11s 23° 07' 26"` | `02s 20° 30' 28"` | `02s 25° 31' 44"` | `02s 27° 52' 27"` | `02s 29° 31' 45"` | `03s 01° 49' 08"` | `03s 04° 15' 32"` | `03s 07° 31' 58"` | `03s 09° 06' 30"` | `03s 13° 50' 42"` |
| **`01h 20m`** | `020°` | `11s 27° 24' 24"` | `02s 24° 14' 03"` | `02s 29° 08' 50"` | `03s 01° 25' 26"` | `03s 03° 01' 26"` | `03s 05° 13' 43"` | `03s 07° 34' 04"` | `03s 10° 41' 27"` | `03s 12° 11' 16"` | `03s 16° 40' 07"` |
| **`01h 36m`** | `024°` | `00s 01° 39' 15"` | `02s 27° 59' 15"` | `03s 02° 46' 30"` | `03s 04° 58' 34"` | `03s 06° 30' 59"` | `03s 08° 37' 54"` | `03s 10° 51' 58"` | `03s 13° 50' 07"` | `03s 15° 15' 12"` | `03s 19° 28' 50"` |
| **`01h 52m`** | `028°` | `00s 05° 51' 42"` | `03s 01° 46' 22"` | `03s 06° 24' 58"` | `03s 08° 32' 04"` | `03s 10° 00' 41"` | `03s 12° 01' 55"` | `03s 14° 09' 29"` | `03s 16° 58' 14"` | `03s 18° 18' 33"` | `03s 22° 17' 01"` |
| **`02h 08m`** | `032°` | `00s 10° 01' 32"` | `03s 05° 35' 38"` | `03s 10° 04' 27"` | `03s 12° 06' 10"` | `03s 13° 30' 43"` | `03s 15° 26' 00"` | `03s 17° 26' 49"` | `03s 20° 05' 59"` | `03s 21° 21' 29"` | `03s 25° 04' 52"` |
| **`02h 24m`** | `036°` | `00s 14° 08' 36"` | `03s 09° 27' 18"` | `03s 13° 45' 09"` | `03s 15° 41' 04"` | `03s 17° 01' 18"` | `03s 18° 50' 19"` | `03s 20° 44' 10"` | `03s 23° 13' 33"` | `03s 24° 24' 12"` | `03s 27° 52' 30"` |
| **`02h 40m`** | `040°` | `00s 18° 12' 47"` | `03s 13° 21' 33"` | `03s 17° 27' 15"` | `03s 19° 16' 55"` | `03s 20° 32' 34"` | `03s 22° 15' 02"` | `03s 24° 01' 41"` | `03s 26° 21' 05"` | `03s 27° 26' 49"` | `04s 00° 40' 03"` |
| **`02h 56m`** | `044°` | `00s 22° 14' 04"` | `03s 17° 18' 33"` | `03s 21° 10' 50"` | `03s 22° 53' 50"` | `03s 24° 04' 38"` | `03s 25° 40' 16"` | `03s 27° 19' 29"` | `03s 29° 28' 42"` | `04s 00° 29' 29"` | `04s 03° 27' 37"` |
| **`03h 12m`** | `048°` | `00s 26° 12' 28"` | `03s 21° 18' 23"` | `03s 24° 56' 02"` | `03s 26° 31' 55"` | `03s 27° 37' 37"` | `03s 29° 06' 08"` | `04s 00° 37' 40"` | `04s 02° 36' 31"` | `04s 03° 32' 17"` | `04s 06° 15' 16"` |
| **`03h 28m`** | `052°` | `01s 00° 08' 04"` | `03s 25° 21' 07"` | `03s 28° 42' 52"` | `04s 00° 11' 13"` | `04s 01° 11' 34"` | `04s 02° 32' 40"` | `04s 03° 56' 19"` | `04s 05° 44' 35"` | `04s 06° 35' 16"` | `04s 09° 03' 03"` |
| **`03h 44m`** | `056°` | `01s 04° 01' 00"` | `03s 29° 26' 45"` | `04s 02° 31' 22"` | `04s 03° 51' 45"` | `04s 04° 46' 31"` | `04s 05° 59' 56"` | `04s 07° 15' 28"` | `04s 08° 52' 57"` | `04s 09° 38' 30"` | `04s 11° 51' 01"` |
| **`04h 00m`** | `060°` | `01s 07° 51' 27"` | `04s 03° 35' 13"` | `04s 06° 21' 30"` | `04s 07° 33' 30"` | `04s 08° 22' 28"` | `04s 09° 27' 56"` | `04s 10° 35' 08"` | `04s 12° 01' 40"` | `04s 12° 42' 01"` | `04s 14° 39' 11"` |
| **`04h 16m`** | `064°` | `01s 11° 39' 37"` | `04s 07° 46' 23"` | `04s 10° 13' 11"` | `04s 11° 16' 27"` | `04s 11° 59' 22"` | `04s 12° 56' 39"` | `04s 13° 55' 19"` | `04s 15° 10' 43"` | `04s 15° 45' 49"` | `04s 17° 27' 34"` |
| **`04h 32m`** | `068°` | `01s 15° 25' 44"` | `04s 12° 00' 04"` | `04s 14° 06' 18"` | `04s 15° 00' 29"` | `04s 15° 37' 10"` | `04s 16° 26' 03"` | `04s 17° 16' 01"` | `04s 18° 20' 07"` | `04s 18° 49' 55"` | `04s 20° 16' 09"` |
| **`04h 48m`** | `072°` | `01s 19° 10' 06"` | `04s 16° 16' 01"` | `04s 18° 00' 43"` | `04s 18° 45' 30"` | `04s 19° 15' 46"` | `04s 19° 56' 03"` | `04s 20° 37' 10"` | `04s 21° 29' 49"` | `04s 21° 54' 16"` | `04s 23° 04' 56"` |
| **`05h 04m`** | `076°` | `01s 22° 52' 59"` | `04s 20° 33' 54"` | `04s 21° 56' 15"` | `04s 22° 31' 22"` | `04s 22° 55' 04"` | `04s 23° 26' 35"` | `04s 23° 58' 42"` | `04s 24° 39' 47"` | `04s 24° 58' 51"` | `04s 25° 53' 53"` |
| **`05h 20m`** | `080°` | `01s 26° 34' 43"` | `04s 24° 53' 21"` | `04s 25° 52' 41"` | `04s 26° 17' 55"` | `04s 26° 34' 57"` | `04s 26° 57' 33"` | `04s 27° 20' 34"` | `04s 27° 49' 59"` | `04s 28° 03' 38"` | `04s 28° 42' 58"` |
| **`05h 36m`** | `084°` | `02s 00° 15' 36"` | `04s 29° 13' 58"` | `04s 29° 49' 46"` | `05s 00° 04' 59"` | `05s 00° 15' 14"` | `05s 00° 28' 50"` | `05s 00° 42' 41"` | `05s 01° 00' 22"` | `05s 01° 08' 33"` | `05s 01° 32' 10"` |
| **`05h 52m`** | `088°` | `02s 03° 55' 59"` | `05s 03° 35' 18"` | `05s 03° 47' 16"` | `05s 03° 52' 21"` | `05s 03° 55' 46"` | `05s 04° 00' 19"` | `05s 04° 04' 56"` | `05s 04° 10' 50"` | `05s 04° 13' 34"` | `05s 04° 21' 26"` |
| **`06h 08m`** | `092°` | `02s 07° 36' 11"` | `05s 07° 56' 52"` | `05s 07° 44' 54"` | `05s 07° 39' 49"` | `05s 07° 36' 24"` | `05s 07° 31' 51"` | `05s 07° 27' 14"` | `05s 07° 21' 20"` | `05s 07° 18' 36"` | `05s 07° 10' 44"` |
| **`06h 24m`** | `096°` | `02s 11° 16' 34"` | `05s 12° 18' 12"` | `05s 11° 42' 24"` | `05s 11° 27' 11"` | `05s 11° 16' 56"` | `05s 11° 03' 20"` | `05s 10° 49' 29"` | `05s 10° 31' 49"` | `05s 10° 23' 37"` | `05s 10° 00' 00"` |
| **`06h 40m`** | `100°` | `02s 14° 57' 27"` | `05s 16° 38' 49"` | `05s 15° 39' 29"` | `05s 15° 14' 15"` | `05s 14° 57' 13"` | `05s 14° 34' 37"` | `05s 14° 11' 36"` | `05s 13° 42' 11"` | `05s 13° 28' 32"` | `05s 12° 49' 12"` |
| **`06h 56m`** | `104°` | `02s 18° 39' 11"` | `05s 20° 58' 16"` | `05s 19° 35' 55"` | `05s 19° 00' 48"` | `05s 18° 37' 06"` | `05s 18° 05' 35"` | `05s 17° 33' 28"` | `05s 16° 52' 23"` | `05s 16° 33' 19"` | `05s 15° 38' 17"` |
| **`07h 12m`** | `108°` | `02s 22° 22' 04"` | `05s 25° 16' 09"` | `05s 23° 31' 27"` | `05s 22° 46' 40"` | `05s 22° 16' 24"` | `05s 21° 36' 07"` | `05s 20° 55' 00"` | `05s 20° 02' 21"` | `05s 19° 37' 54"` | `05s 18° 27' 15"` |
| **`07h 28m`** | `112°` | `02s 26° 06' 26"` | `05s 29° 32' 06"` | `05s 27° 25' 52"` | `05s 26° 31' 41"` | `05s 25° 55' 00"` | `05s 25° 06' 08"` | `05s 24° 16' 09"` | `05s 23° 12' 03"` | `05s 22° 42' 16"` | `05s 21° 16' 01"` |
| **`07h 44m`** | `116°` | `02s 29° 52' 33"` | `06s 03° 45' 47"` | `06s 01° 19' 00"` | `06s 00° 15' 44"` | `05s 29° 32' 48"` | `05s 28° 35' 31"` | `05s 27° 36' 51"` | `05s 26° 21' 27"` | `05s 25° 46' 21"` | `05s 24° 04' 36"` |
| **`08h 00m`** | `120°` | `03s 03° 40' 43"` | `06s 07° 56' 58"` | `06s 05° 10' 40"` | `06s 03° 58' 40"` | `06s 03° 09' 42"` | `06s 02° 04' 14"` | `06s 00° 57' 02"` | `05s 29° 30' 30"` | `05s 28° 50' 09"` | `05s 26° 52' 59"` |
| **`08h 16m`** | `124°` | `03s 07° 31' 10"` | `06s 12° 05' 25"` | `06s 09° 00' 48"` | `06s 07° 40' 25"` | `06s 06° 45' 39"` | `06s 05° 32' 14"` | `06s 04° 16' 43"` | `06s 02° 39' 13"` | `06s 01° 53' 40"` | `05s 29° 41' 09"` |
| **`08h 32m`** | `128°` | `03s 11° 24' 06"` | `06s 16° 11' 03"` | `06s 12° 49' 18"` | `06s 11° 20' 58"` | `06s 10° 20' 36"` | `06s 08° 59' 30"` | `06s 07° 35' 51"` | `06s 05° 47' 35"` | `06s 04° 56' 54"` | `06s 02° 29' 07"` |
| **`08h 48m`** | `132°` | `03s 15° 19' 42"` | `06s 20° 13' 47"` | `06s 16° 36' 08"` | `06s 15° 00' 15"` | `06s 13° 54' 33"` | `06s 12° 26' 02"` | `06s 10° 54' 30"` | `06s 08° 55' 39"` | `06s 07° 59' 53"` | `06s 05° 16' 54"` |
| **`09h 04m`** | `136°` | `03s 19° 18' 06"` | `06s 24° 13' 37"` | `06s 20° 21' 20"` | `06s 18° 38' 20"` | `06s 17° 27' 32"` | `06s 15° 51' 54"` | `06s 14° 12' 41"` | `06s 12° 03' 28"` | `06s 11° 02' 41"` | `06s 08° 04' 33"` |
| **`09h 20m`** | `140°` | `03s 23° 19' 23"` | `06s 28° 10' 37"` | `06s 24° 04' 55"` | `06s 22° 15' 15"` | `06s 20° 59' 37"` | `06s 19° 17' 08"` | `06s 17° 30' 30"` | `06s 15° 11' 05"` | `06s 14° 05' 21"` | `06s 10° 52' 07"` |
| **`09h 36m`** | `144°` | `03s 27° 23' 34"` | `07s 02° 04' 52"` | `06s 27° 47' 01"` | `06s 25° 51' 06"` | `06s 24° 30' 52"` | `06s 22° 41' 51"` | `06s 20° 48' 00"` | `06s 18° 18' 37"` | `06s 17° 07' 58"` | `06s 13° 39' 40"` |
| **`09h 52m`** | `148°` | `04s 01° 30' 38"` | `07s 05° 56' 32"` | `07s 01° 27' 43"` | `06s 29° 26' 00"` | `06s 28° 01' 27"` | `06s 26° 06' 11"` | `06s 24° 05' 21"` | `06s 21° 26' 11"` | `06s 20° 10' 41"` | `06s 16° 27' 18"` |
| **`10h 08m`** | `152°` | `04s 05° 40' 28"` | `07s 09° 45' 48"` | `07s 05° 07' 13"` | `07s 03° 00' 06"` | `07s 01° 31' 29"` | `06s 29° 30' 15"` | `06s 27° 22' 41"` | `06s 24° 33' 56"` | `06s 23° 13' 38"` | `06s 19° 15' 09"` |
| **`10h 24m`** | `156°` | `04s 09° 52' 55"` | `07s 13° 32' 55"` | `07s 08° 45' 40"` | `07s 06° 33' 36"` | `07s 05° 01' 11"` | `07s 02° 54' 16"` | `07s 00° 40' 12"` | `06s 27° 42' 03"` | `06s 26° 16' 58"` | `06s 22° 03' 20"` |
| **`10h 40m`** | `160°` | `04s 14° 07' 46"` | `07s 17° 18' 07"` | `07s 12° 23' 20"` | `07s 10° 06' 44"` | `07s 08° 30' 45"` | `07s 06° 18' 27"` | `07s 03° 58' 06"` | `07s 00° 50' 43"` | `06s 29° 20' 54"` | `06s 24° 52' 03"` |
| **`10h 56m`** | `164°` | `04s 18° 24' 44"` | `07s 21° 01' 43"` | `07s 16° 00' 26"` | `07s 13° 39' 43"` | `07s 12° 00' 25"` | `07s 09° 43' 02"` | `07s 07° 16' 38"` | `07s 04° 00' 12"` | `07s 02° 25' 41"` | `06s 27° 41' 28"` |
| **`11h 12m`** | `168°` | `04s 22° 43' 27"` | `07s 24° 43' 59"` | `07s 19° 37' 16"` | `07s 17° 12' 50"` | `07s 15° 30' 29"` | `07s 13° 08' 19"` | `07s 10° 36' 05"` | `07s 07° 10' 46"` | `07s 05° 31' 33"` | `07s 00° 31' 51"` |
| **`11h 28m`** | `172°` | `04s 27° 03' 33"` | `07s 28° 25' 14"` | `07s 23° 14' 08"` | `07s 20° 46' 24"` | `07s 19° 01' 15"` | `07s 16° 34' 35"` | `07s 13° 56' 46"` | `07s 10° 22' 44"` | `07s 08° 38' 51"` | `07s 03° 23' 26"` |
| **`11h 44m`** | `176°` | `05s 01° 24' 35"` | `08s 02° 05' 50"` | `07s 26° 51' 20"` | `07s 24° 20' 43"` | `07s 22° 33' 03"` | `07s 20° 02' 10"` | `07s 17° 19' 01"` | `07s 13° 36' 27"` | `07s 11° 47' 56"` | `07s 06° 16' 34"` |
| **`12h 00m`** | `180°` | `05s 05° 46' 05"` | `08s 05° 46' 05"` | `08s 00° 29' 12"` | `07s 27° 56' 09"` | `07s 26° 06' 13"` | `07s 23° 31' 29"` | `07s 20° 43' 15"` | `07s 16° 52' 20"` | `07s 14° 59' 10"` | `07s 09° 11' 37"` |
| **`12h 16m`** | `184°` | `05s 10° 07' 35"` | `08s 09° 26' 20"` | `08s 04° 08' 06"` | `08s 01° 33' 03"` | `07s 29° 41' 09"` | `07s 27° 02' 54"` | `07s 24° 09' 53"` | `07s 20° 10' 49"` | `07s 18° 13' 02"` | `07s 12° 08' 59"` |
| **`12h 32m`** | `188°` | `05s 14° 28' 37"` | `08s 13° 06' 56"` | `08s 07° 48' 24"` | `08s 05° 11' 50"` | `08s 03° 18' 16"` | `08s 00° 36' 52"` | `07s 27° 39' 23"` | `07s 23° 32' 25"` | `07s 21° 30' 03"` | `07s 15° 09' 10"` |
| **`12h 48m`** | `192°` | `05s 18° 48' 43"` | `08s 16° 48' 12"` | `08s 11° 30' 28"` | `08s 08° 52' 52"` | `08s 06° 57' 59"` | `08s 04° 13' 52"` | `08s 01° 12' 16"` | `07s 26° 57' 41"` | `07s 24° 50' 47"` | `07s 18° 12' 45"` |
| **`13h 04m`** | `196°` | `05s 23° 07' 26"` | `08s 20° 30' 28"` | `08s 15° 14' 40"` | `08s 12° 36' 36"` | `08s 10° 40' 45"` | `08s 07° 54' 23"` | `08s 04° 49' 05"` | `08s 00° 27' 16"` | `07s 28° 15' 53"` | `07s 21° 20' 23"` |
| **`13h 20m`** | `200°` | `05s 27° 24' 24"` | `08s 24° 14' 03"` | `08s 19° 01' 24"` | `08s 16° 23' 26"` | `08s 14° 27' 03"` | `08s 11° 38' 58"` | `08s 08° 30' 28"` | `08s 04° 01' 51"` | `08s 01° 46' 06"` | `07s 24° 32' 52"` |
| **`13h 36m`** | `204°` | `06s 01° 39' 15"` | `08s 27° 59' 15"` | `08s 22° 51' 01"` | `08s 20° 13' 49"` | `08s 18° 17' 21"` | `08s 15° 28' 09"` | `08s 12° 17' 02"` | `08s 07° 42' 14"` | `08s 05° 22' 16"` | `07s 27° 51' 06"` |
| **`13h 52m`** | `208°` | `06s 05° 51' 42"` | `09s 01° 46' 22"` | `08s 26° 43' 55"` | `08s 24° 08' 11"` | `08s 22° 12' 08"` | `08s 19° 22' 32"` | `08s 16° 09' 31"` | `08s 11° 29' 16"` | `08s 09° 05' 19"` | `08s 01° 16' 08"` |
| **`14h 08m`** | `212°` | `06s 10° 01' 32"` | `09s 05° 35' 38"` | `09s 00° 40' 25"` | `08s 28° 06' 57"` | `08s 26° 11' 54"` | `08s 23° 22' 44"` | `08s 20° 08' 38"` | `08s 15° 23' 53"` | `08s 12° 56' 19"` | `08s 04° 49' 16"` |
| **`14h 24m`** | `216°` | `06s 14° 08' 36"` | `09s 09° 27' 18"` | `09s 04° 40' 52"` | `09s 02° 10' 31"` | `09s 00° 17' 08"` | `08s 27° 29' 19"` | `08s 24° 15' 09"` | `08s 19° 27' 09"` | `08s 16° 56' 24"` | `08s 08° 32' 00"` |
| **`14h 40m`** | `220°` | `06s 18° 12' 47"` | `09s 13° 21' 33"` | `09s 08° 45' 33"` | `09s 06° 19' 16"` | `09s 04° 28' 16"` | `09s 01° 42' 54"` | `08s 28° 29' 53"` | `08s 23° 40' 11"` | `08s 21° 06' 55"` | `08s 12° 26' 05"` |
| **`14h 56m`** | `224°` | `06s 22° 14' 04"` | `09s 17° 18' 33"` | `09s 12° 54' 43"` | `09s 10° 33' 31"` | `09s 08° 45' 44"` | `09s 06° 04' 02"` | `09s 02° 53' 36"` | `08s 28° 04' 09"` | `08s 25° 29' 14"` | `08s 16° 33' 40"` |
| **`15h 12m`** | `228°` | `06s 26° 12' 28"` | `09s 21° 18' 23"` | `09s 17° 08' 32"` | `09s 14° 53' 34"` | `09s 13° 09' 53"` | `09s 10° 33' 16"` | `09s 07° 27' 04"` | `09s 02° 40' 19"` | `09s 00° 04' 55"` | `08s 20° 57' 12"` |
| **`15h 28m`** | `232°` | `07s 00° 08' 04"` | `09s 25° 21' 07"` | `09s 21° 27' 09"` | `09s 19° 19' 34"` | `09s 17° 40' 59"` | `09s 15° 11' 00"` | `09s 12° 10' 59"` | `09s 07° 29' 54"` | `09s 04° 55' 32"` | `08s 25° 39' 39"` |
| **`15h 44m`** | `236°` | `07s 04° 01' 00"` | `09s 29° 26' 45"` | `09s 25° 50' 34"` | `09s 23° 51' 39"` | `09s 22° 19' 11"` | `09s 19° 57' 34"` | `09s 17° 05' 56"` | `09s 12° 34' 05"` | `09s 10° 02' 42"` | `09s 00° 44' 23"` |
| **`16h 00m`** | `240°` | `07s 07° 51' 27"` | `10s 03° 35' 13"` | `10s 00° 18' 45"` | `09s 28° 29' 45"` | `09s 27° 04' 32"` | `09s 24° 53' 06"` | `09s 22° 12' 18"` | `09s 17° 53' 54"` | `09s 15° 27' 53"` | `09s 06° 15' 14"` |
| **`16h 16m`** | `244°` | `07s 11° 39' 37"` | `10s 07° 46' 23"` | `10s 04° 51' 31"` | `10s 03° 13' 44"` | `10s 01° 56' 52"` | `09s 29° 57' 35"` | `09s 27° 30' 15"` | `09s 23° 30' 06"` | `09s 21° 12' 22"` | `09s 12° 16' 18"` |
| **`16h 32m`** | `248°` | `07s 15° 25' 44"` | `10s 12° 00' 04"` | `10s 09° 28' 35"` | `10s 08° 03' 17"` | `10s 06° 55' 54"` | `10s 05° 10' 41"` | `10s 02° 59' 37"` | `09s 29° 22' 58"` | `09s 27° 16' 53"` | `09s 18° 51' 41"` |
| **`16h 48m`** | `252°` | `07s 19° 10' 06"` | `10s 16° 16' 01"` | `10s 14° 09' 33"` | `10s 12° 57' 55"` | `10s 12° 01' 04"` | `10s 10° 31' 50"` | `10s 08° 39' 48"` | `10s 05° 32' 13"` | `10s 03° 41' 32"` | `09s 26° 04' 48"` |
| **`17h 04m`** | `256°` | `07s 22° 52' 59"` | `10s 20° 33' 54"` | `10s 18° 53' 55"` | `10s 17° 56' 59"` | `10s 17° 11' 38"` | `10s 16° 00' 09"` | `10s 14° 29' 46"` | `10s 11° 56' 45"` | `10s 10° 25' 19"` | `10s 03° 57' 28"` |
| **`17h 20m`** | `260°` | `07s 26° 34' 43"` | `10s 24° 53' 21"` | `10s 23° 41' 03"` | `10s 22° 59' 42"` | `10s 22° 26' 41"` | `10s 21° 34' 26"` | `10s 20° 28' 02"` | `10s 18° 34' 34"` | `10s 17° 26' 05"` | `10s 12° 28' 29"` |
| **`17h 36m`** | `264°` | `08s 00° 15' 36"` | `10s 29° 13' 58"` | `10s 28° 30' 13"` | `10s 28° 05' 08"` | `10s 27° 45' 04"` | `10s 27° 13' 13"` | `10s 26° 32' 36"` | `10s 25° 22' 45"` | `10s 24° 40' 17"` | `10s 21° 32' 25"` |
| **`17h 52m`** | `268°` | `08s 03° 55' 59"` | `11s 03° 35' 18"` | `11s 03° 20' 39"` | `11s 03° 12' 15"` | `11s 03° 05' 31"` | `11s 02° 54' 49"` | `11s 02° 41' 08"` | `11s 02° 17' 33"` | `11s 02° 03' 09"` | `11s 00° 58' 51"` |
| **`18h 08m`** | `272°` | `08s 07° 36' 11"` | `11s 07° 56' 52"` | `11s 08° 11' 31"` | `11s 08° 19' 55"` | `11s 08° 26' 39"` | `11s 08° 37' 21"` | `11s 08° 51' 02"` | `11s 09° 14' 37"` | `11s 09° 29' 01"` | `11s 10° 33' 19"` |
| **`18h 24m`** | `276°` | `08s 11° 16' 34"` | `11s 12° 18' 12"` | `11s 13° 01' 57"` | `11s 13° 27' 02"` | `11s 13° 47' 06"` | `11s 14° 18' 57"` | `11s 14° 59' 34"` | `11s 16° 09' 25"` | `11s 16° 51' 53"` | `11s 19° 59' 45"` |
| **`18h 40m`** | `280°` | `08s 14° 57' 27"` | `11s 16° 38' 49"` | `11s 17° 51' 07"` | `11s 18° 32' 28"` | `11s 19° 05' 29"` | `11s 19° 57' 44"` | `11s 21° 04' 08"` | `11s 22° 57' 36"` | `11s 24° 06' 05"` | `11s 29° 03' 41"` |
| **`18h 56m`** | `284°` | `08s 18° 39' 11"` | `11s 20° 58' 16"` | `11s 22° 38' 15"` | `11s 23° 35' 11"` | `11s 24° 20' 32"` | `11s 25° 32' 02"` | `11s 27° 02' 24"` | `11s 29° 35' 25"` | `00s 01° 06' 51"` | `00s 07° 34' 43"` |
| **`19h 12m`** | `288°` | `08s 22° 22' 04"` | `11s 25° 16' 09"` | `11s 27° 22' 37"` | `11s 28° 34' 15"` | `11s 29° 31' 06"` | `00s 01° 00' 20"` | `00s 02° 52' 23"` | `00s 05° 59' 57"` | `00s 07° 50' 39"` | `00s 15° 27' 22"` |
| **`19h 28m`** | `292°` | `08s 26° 06' 26"` | `11s 29° 32' 06"` | `00s 02° 03' 35"` | `00s 03° 28' 53"` | `00s 04° 36' 16"` | `00s 06° 21' 30"` | `00s 08° 32' 33"` | `00s 12° 09' 12"` | `00s 14° 15' 17"` | `00s 22° 40' 29"` |
| **`19h 44m`** | `296°` | `08s 29° 52' 33"` | `00s 03° 45' 47"` | `00s 06° 40' 39"` | `00s 08° 18' 26"` | `00s 09° 35' 18"` | `00s 11° 34' 36"` | `00s 14° 01' 55"` | `00s 18° 02' 04"` | `00s 20° 19' 48"` | `00s 29° 15' 52"` |
| **`20h 00m`** | `300°` | `09s 03° 40' 43"` | `00s 07° 56' 58"` | `00s 11° 13' 25"` | `00s 13° 02' 25"` | `00s 14° 27' 38"` | `00s 16° 39' 04"` | `00s 19° 19' 52"` | `00s 23° 38' 16"` | `00s 26° 04' 17"` | `01s 05° 16' 56"` |
| **`20h 16m`** | `304°` | `09s 07° 31' 10"` | `00s 12° 05' 25"` | `00s 15° 41' 36"` | `00s 17° 40' 31"` | `00s 19° 12' 59"` | `00s 21° 34' 36"` | `00s 24° 26' 14"` | `00s 28° 58' 05"` | `01s 01° 29' 28"` | `01s 10° 47' 47"` |
| **`20h 32m`** | `308°` | `09s 11° 24' 06"` | `00s 16° 11' 03"` | `00s 20° 05' 01"` | `00s 22° 12' 36"` | `00s 23° 51' 11"` | `00s 26° 21' 10"` | `00s 29° 21' 11"` | `01s 04° 02' 16"` | `01s 06° 36' 38"` | `01s 15° 52' 31"` |
| **`20h 48m`** | `312°` | `09s 15° 19' 42"` | `00s 20° 13' 47"` | `00s 24° 23' 38"` | `00s 26° 38' 36"` | `00s 28° 22' 17"` | `01s 00° 58' 54"` | `01s 04° 05' 06"` | `01s 08° 51' 51"` | `01s 11° 27' 15"` | `01s 20° 34' 58"` |
| **`21h 04m`** | `316°` | `09s 19° 18' 06"` | `00s 24° 13' 37"` | `00s 28° 37' 27"` | `01s 00° 58' 39"` | `01s 02° 46' 26"` | `01s 05° 28' 08"` | `01s 08° 38' 34"` | `01s 13° 28' 01"` | `01s 16° 02' 56"` | `01s 24° 58' 30"` |
| **`21h 20m`** | `320°` | `09s 23° 19' 23"` | `00s 28° 10' 37"` | `01s 02° 46' 37"` | `01s 05° 12' 54"` | `01s 07° 03' 54"` | `01s 09° 49' 16"` | `01s 13° 02' 17"` | `01s 17° 51' 59"` | `01s 20° 25' 15"` | `01s 29° 06' 05"` |
| **`21h 36m`** | `324°` | `09s 27° 23' 34"` | `01s 02° 04' 52"` | `01s 06° 51' 18"` | `01s 09° 21' 39"` | `01s 11° 15' 02"` | `01s 14° 02' 51"` | `01s 17° 17' 01"` | `01s 22° 05' 01"` | `01s 24° 35' 46"` | `02s 03° 00' 10"` |
| **`21h 52m`** | `328°` | `10s 01° 30' 38"` | `01s 05° 56' 32"` | `01s 10° 51' 45"` | `01s 13° 25' 13"` | `01s 15° 20' 16"` | `01s 18° 09' 27"` | `01s 21° 23' 32"` | `01s 26° 08' 17"` | `01s 28° 35' 52"` | `02s 06° 42' 54"` |
| **`22h 08m`** | `332°` | `10s 05° 40' 28"` | `01s 09° 45' 48"` | `01s 14° 48' 15"` | `01s 17° 23' 59"` | `01s 19° 20' 02"` | `01s 22° 09' 38"` | `01s 25° 22' 39"` | `02s 00° 02' 55"` | `02s 02° 26' 51"` | `02s 10° 16' 02"` |
| **`22h 24m`** | `336°` | `10s 09° 52' 55"` | `01s 13° 32' 55"` | `01s 18° 41' 09"` | `01s 21° 18' 21"` | `01s 23° 14' 50"` | `01s 26° 04' 01"` | `01s 29° 15' 08"` | `02s 03° 49' 56"` | `02s 06° 09' 54"` | `02s 13° 41' 05"` |
| **`22h 40m`** | `340°` | `10s 14° 07' 46"` | `01s 17° 18' 07"` | `01s 22° 30' 46"` | `01s 25° 08' 44"` | `01s 27° 05' 07"` | `01s 29° 53' 13"` | `02s 03° 01' 42"` | `02s 07° 30' 19"` | `02s 09° 46' 04"` | `02s 16° 59' 18"` |
| **`22h 56m`** | `344°` | `10s 18° 24' 44"` | `01s 21° 01' 43"` | `01s 26° 17' 30"` | `01s 28° 55' 34"` | `02s 00° 51' 25"` | `02s 03° 37' 47"` | `02s 06° 43' 05"` | `02s 11° 04' 54"` | `02s 13° 16' 17"` | `02s 20° 11' 47"` |
| **`23h 12m`** | `348°` | `10s 22° 43' 27"` | `01s 24° 43' 59"` | `02s 00° 01' 42"` | `02s 02° 39' 18"` | `02s 04° 34' 11"` | `02s 07° 18' 18"` | `02s 10° 19' 54"` | `02s 14° 34' 29"` | `02s 16° 41' 24"` | `02s 23° 19' 25"` |
| **`23h 28m`** | `352°` | `10s 27° 03' 33"` | `01s 28° 25' 14"` | `02s 03° 43' 46"` | `02s 06° 20' 20"` | `02s 08° 13' 54"` | `02s 10° 55' 18"` | `02s 13° 52' 47"` | `02s 17° 59' 45"` | `02s 20° 02' 07"` | `02s 26° 23' 00"` |
| **`23h 44m`** | `356°` | `11s 01° 24' 35"` | `02s 02° 05' 50"` | `02s 07° 24' 04"` | `02s 09° 59' 07"` | `02s 11° 51' 01"` | `02s 14° 29' 16"` | `02s 17° 22' 17"` | `02s 21° 21' 21"` | `02s 23° 19' 08"` | `02s 29° 23' 11"` |

### Table 7B — Classical *Lankodaya* (Equatorial Rising Durations) & *Charakhanda* Latitude Adjustments

| Rashi # | Sanskrit Rashi | Western Sign | *Lankodaya* (*Vinadis*) | *Lankodaya* (*Ghatis & Palas*) | *Lankodaya* (Clock Minutes) | *odaya* Type (*Shirshodaya / Prishtodaya*) |
|---|---|---|---|---|---|---|
| `01` | **Mesha** | Aries | `278 v` | `4g 38p` | `111.2 min` | Prishtodaya (Rises by Hind Part) |
| `02` | **Vrishabha** | Taurus | `299 v` | `4g 59p` | `119.6 min` | Prishtodaya (Rises by Hind Part) |
| `03` | **Mithuna** | Gemini | `323 v` | `5g 23p` | `129.2 min` | Ubhayodaya (Rises Both Ways) |
| `04` | **Karka** | Cancer | `323 v` | `5g 23p` | `129.2 min` | Prishtodaya (Rises by Hind Part) |
| `05` | **Simha** | Leo | `299 v` | `4g 59p` | `119.6 min` | Shirshodaya (Rises by Head) |
| `06` | **Kanya** | Virgo | `278 v` | `4g 38p` | `111.2 min` | Shirshodaya (Rises by Head) |
| `07` | **Tula** | Libra | `278 v` | `4g 38p` | `111.2 min` | Shirshodaya (Rises by Head) |
| `08` | **Vrishchika** | Scorpio | `299 v` | `4g 59p` | `119.6 min` | Shirshodaya (Rises by Head) |
| `09` | **Dhanu** | Sagittarius | `323 v` | `5g 23p` | `129.2 min` | Prishtodaya (Rises by Hind Part) |
| `10` | **Makara** | Capricorn | `323 v` | `5g 23p` | `129.2 min` | Prishtodaya (Rises by Hind Part) |
| `11` | **Kumbha** | Aquarius | `299 v` | `4g 59p` | `119.6 min` | Shirshodaya (Rises by Head) |
| `12` | **Meena** | Pisces | `278 v` | `4g 38p` | `111.2 min` | Ubhayodaya (Rises Both Ways) |

## Chapter 8 — Complete Manual Compendium of All 8 *Vishesha Lagnas*, 11 *Upagrahas*, *Yogi/Avayogi*, & 9 *Prashna Sphutas*

### Table 8A — Complete Manual Formulas for the 8 *Vishesha Lagnas* (Special Ascendants)

| # | Special Lagna (*Vishesha Lagna*) | Rate of Motion | Exact Classical Manual Formula (*Brihat Parashara Hora Shastra* & *Uttara Kalamrita*) | Primary Predictive Domain |
|---|---|---|---|---|
| **1** | **Udaya Lagna (Birth Ascendant)** | `~1° per 4 min` (`12 signs / 24h`) | Eastern horizon intersection with the sidereal ecliptic at birth (Table 7A) | Physical body, vitality, self, overall life trajectory |
| **2** | **Hora Lagna (HL)** | `1° per 2.5 min` (`24 signs / 24h`) | $\text{HL} = \lambda_\odot(\text{Sunrise}) + \frac{\text{Elapsed Minutes since Sunrise}}{2.5}$ | Personal wealth, sustenance, liquid resources, financial inflow |
| **3** | **Ghati Lagna (GL)** | `1.25° per min` (`1 sign per Ghati`) | $\text{GL} = \lambda_\odot(\text{Sunrise}) + (\text{Elapsed Ghatis since Sunrise} \times 30^\circ)$ | Power, royal authority, political/executive rank, fame |
| **4** | **Bhava Lagna (BL)** | `0.25° per min` (`1 sign per 5 Ghatis`) | $\text{BL} = \lambda_\odot(\text{Sunrise}) + (\text{Elapsed Ghatis since Sunrise} \times 6^\circ)$ | Inner psychological disposition and bodily constitution |
| **5** | **Sree Lagna (SL)** | Linked to Moon's Pada | $\text{SL} = \lambda_{\text{Udaya Lagna}} + \left(\frac{\lambda_{\mathbb{C}} \bmod 13^\circ 20'}{13^\circ 20'} \times 360^\circ\right)$ | Goddess Lakshmi's grace, prosperity, marriage fortune |
| **6** | **Indu Lagna (IL)** | Planetary *Kala* Sum | Sum *Kalas* (`Sun 30, Moon 16, Mars 6, Mercury 8, Jupiter 10, Venus 12, Saturn 1`) of 9th Lord from Lagna + 9th Lord from Moon; take $\text{Sum} \bmod 12$ (`0 -> 12`) and count that many signs from Natal Moon | Millionaire/billionaire *Dhana Yogas* and windfall wealth Dasha triggers |
| **7** | **Pranapada Lagna (PL)** | `4° per minute` (`1° per 15 Palas`) | $\text{PL} = \lambda_\odot + \frac{\text{Elapsed Palas since Sunrise}}{15} + \begin{cases} 0^\circ & \text{Sun in Movable Sign} \\ 240^\circ & \text{Sun in Fixed Sign} \\ 120^\circ & \text{Sun in Dual Sign} \end{cases}$ | Birth-time rectification (must fall in trine/10th to Moon or Lagna) |
| **8** | **Varnada Lagna (VL)** | Sign-Parity Vector | Count Udaya Lagna & Hora Lagna from Mesha (if Odd) or Meena backwards (if Even); add if same parity, subtract if opposite parity | Social class, vocational calling, and public duty |

### Table 8B — Complete Manual Formulas for the 5 Solar *Upagrahas* & 6 *Kalavela* Time-of-Day *Upagrahas* (*Gulika/Mandi*)

| Category | Upagraha Name | Ruling Planet | Exact Manual Calculation Formula | Daytime Octant (`Sun..Sat`, out of 8) | Nighttime Octant (`Sun..Sat`, out of 8) |
|---|---|---|---|---|---|
| **Solar Upagraha 1** | **Dhuma** | Mars (Fiery Smoke) | $\lambda_{\text{Dhuma}} = (\lambda_\odot + 133^\circ 20') \bmod 360^\circ$ | Instantaneous from $\lambda_\odot$ | Instantaneous from $\lambda_\odot$ |
| **Solar Upagraha 2** | **Vyatipata** | Rahu (Calamity) | $\lambda_{\text{Vyatipata}} = (360^\circ - \lambda_{\text{Dhuma}}) \bmod 360^\circ$ | Instantaneous from $\lambda_\odot$ | Instantaneous from $\lambda_\odot$ |
| **Solar Upagraha 3** | **Parivesha** | Moon (Halo) | $\lambda_{\text{Parivesha}} = (\lambda_{\text{Vyatipata}} + 180^\circ) \bmod 360^\circ$ | Instantaneous from $\lambda_\odot$ | Instantaneous from $\lambda_\odot$ |
| **Solar Upagraha 4** | **Indrachapa (Kodanda)** | Venus (Rainbow Bow) | $\lambda_{\text{Indrachapa}} = (360^\circ - \lambda_{\text{Parivesha}}) \bmod 360^\circ$ | Instantaneous from $\lambda_\odot$ | Instantaneous from $\lambda_\odot$ |
| **Solar Upagraha 5** | **Upaketu (Sikhi)** | Ketu (Comet Crest) | $\lambda_{\text{Upaketu}} = (\lambda_{\text{Indrachapa}} + 16^\circ 40') \bmod 360^\circ = (\lambda_\odot - 30^\circ)$ | Instantaneous from $\lambda_\odot$ | Instantaneous from $\lambda_\odot$ |
| **Kalavela 1** | **Gulika (Mandi)** | Saturn's Son | Ascendant rising at start of Saturn's 1/8th portion of *Dinamana* / *Ratrimana* | `Sun:7, Mon:6, Tue:5, Wed:4, Thu:3, Fri:2, Sat:1` | `Sun:3, Mon:2, Tue:1, Wed:7, Thu:6, Fri:5, Sat:4` |
| **Kalavela 2** | **Kala** | Sun's Portion | Ascendant rising at start of Sun's 1/8th portion | `Sun:1, Mon:7, Tue:6, Wed:5, Thu:4, Fri:3, Sat:2` | `Sun:4, Mon:3, Tue:2, Wed:1, Thu:7, Fri:6, Sat:5` |
| **Kalavela 3** | **Mrityu** | Mars's Portion | Ascendant rising at start of Mars's 1/8th portion | `Sun:3, Mon:2, Tue:1, Wed:7, Thu:6, Fri:5, Sat:4` | `Sun:6, Mon:5, Tue:4, Wed:3, Thu:2, Fri:1, Sat:7` |
| **Kalavela 4** | **Ardhaprahara** | Mercury's Portion | Ascendant rising at start of Mercury's 1/8th portion | `Sun:4, Mon:3, Tue:2, Wed:1, Thu:7, Fri:6, Sat:5` | `Sun:7, Mon:6, Tue:5, Wed:4, Thu:3, Fri:2, Sat:1` |
| **Kalavela 5** | **Yamaghantaka** | Jupiter's Portion | Ascendant rising at start of Jupiter's 1/8th portion | `Sun:5, Mon:4, Tue:3, Wed:2, Thu:1, Fri:7, Sat:6` | `Sun:1, Mon:7, Tue:6, Wed:5, Thu:4, Fri:3, Sat:2` |

### Table 8C — Complete Manual Formulas for *Yogi / Sahayogi / Avayogi* & the 9 Kerala *Prashna Marga Sphutas*

| Sensitive Point (*Sphuta*) | Exact Mathematical Formula (`Mod 360°`) | Classical Interpretation Rule (*Prashna Marga* & *BPHS*) |
|---|---|---|
| **Yogi Point & Yogi Planet** | $\lambda_{\text{Yogi}} = (\lambda_\odot + \lambda_{\mathbb{C}} + 93^\circ 20') \bmod 360^\circ$ | Nakshatra Lord of $\lambda_{\text{Yogi}}$ is **Yogi Planet** (supreme prosperity significator); Sign Lord is **Sahayogi** |
| **Avayogi Point & Planet** | $\lambda_{\text{Avayogi}} = (\lambda_{\text{Yogi}} + 186^\circ 40') \bmod 360^\circ$ | Nakshatra Lord of $\lambda_{\text{Avayogi}}$ is **Avayogi Planet** (obstruction/drain significator) |
| **1. Trisphuta** | $(\lambda_{\text{Lagna}} + \lambda_{\mathbb{C}} + \lambda_{\text{Gulika}}) \bmod 360^\circ$ | Core vitality, health, and immediate horary crisis indicator |
| **2. Chatusphuta** | $(\lambda_{\text{Trisphuta}} + \lambda_\odot) \bmod 360^\circ$ | Soul-level endurance and royal/spiritual support |
| **3. Panchasphuta** | $(\lambda_{\text{Chatusphuta}} + \lambda_{\text{Rahu}}) \bmod 360^\circ$ | Karmic destiny and hidden snakes/curses in Prashna |
| **4. Prana Sphuta** | $(5 \times \lambda_{\text{Lagna}} + \lambda_{\text{Gulika}}) \bmod 360^\circ$ | Vital breath (*Prana*) — conjunction with Mrityu Sphuta indicates acute danger |
| **5. Deha Sphuta** | $(8 \times \lambda_{\mathbb{C}} + \lambda_{\text{Gulika}}) \bmod 360^\circ$ | Physical body resilience and recovery capacity |
| **6. Mrityu Sphuta** | $(7 \times \lambda_{\text{Gulika}} + \lambda_\odot) \bmod 360^\circ$ | Mortality / critical vulnerability point |
| **7. Tithi Sphuta** | $\left(\lambda_{\text{Lagna}} + (\lambda_{\mathbb{C}} - \lambda_\odot)\right) \bmod 360^\circ$ | Lunar-phase harmony in relationships and undertakings |
| **8. Beeja Sphuta (Male)** | $(\lambda_\odot + \lambda_{\text{Venus}} + \lambda_{\text{Jupiter}}) \bmod 360^\circ$ | Male virility and progeny seed strength (must occupy odd signs/navamsas with benefic aspect) |
| **9. Kshetra Sphuta (Female)** | $(\lambda_{\mathbb{C}} + \lambda_{\text{Mars}} + \lambda_{\text{Jupiter}}) \bmod 360^\circ$ | Female fertility and womb strength (must occupy even signs/navamsas with benefic aspect) |

## Chapter 9 — Section 4 — Complete Manual Divisional Chart (*Shodashvarga D1–D60*) Master Lookup Tables, 36 *Drekkana Swarupas*, & *Vimsopaka Bala*

### Table 9A — All 16 Parashari *Shodashvarga* Divisional Rules & *Vimsopaka Bala* Weights (`20-Point Scale`)

| Varga | Sanskrit Name | Slice Size | Classical Manual Counting Rule | Primary Life Domain | *Shadvarga* Wt | *Saptavarga* Wt | *Dashavarga* Wt | *Shodashvarga* Wt |
|---|---|---|---|---|---|---|---|---|
| **D1** | *Rashi* | `30° 00'` | 1st sign itself (`0°–30°`) | Physical body, general fortune & identity | `6` | `5` | `3` | **`3.5`** |
| **D2** | *Hora* | `15° 00'` | Odd signs: `0°–15°` Simha (Sun), `15°–30°` Karka (Moon); Even signs: reversed | Wealth, family sustenance & speech | `2` | `2` | `1.5` | **`1.0`** |
| **D3** | *Drekkana* | `10° 00'` | `0°–10°` 1st sign; `10°–20°` 5th sign; `20°–30°` 9th sign | Siblings, courage, enterprise & co-born | `4` | `3` | `1.5` | **`1.0`** |
| **D4** | *Chaturthamsa* | `07° 30'` | 4 slices of `7°30'`: 1st, 4th, 7th, and 10th (Kendra) signs from the Rashi | Real estate, homes, fixed assets & happiness | `—` | `—` | `—` | **`0.5`** |
| **D7** | *Saptamsa* | `04° 17' 08.6"` | 7 slices: Odd signs count from same sign; Even signs count from 7th sign | Children, grandchildren & creative legacy | `—` | `1` | `1.5` | **`0.5`** |
| **D9** | *Navamsa* | `03° 20'` | 9 slices: Fire from Mesha, Earth from Makara, Air from Tula, Water from Karka | Marriage, spouse, Dharma & inner fruit of planets | `5` | `2.5` | `1.5` | **`3.0`** |
| **D10** | *Dasamsa* | `03° 00'` | 10 slices of `3°`: Odd signs count from same sign; Even signs count from 9th sign | Career, profession, authority, fame & karma | `—` | `—` | `1.5` | **`1.5`** |
| **D12** | *Dwadasamsa* | `02° 30'` | 12 slices of `2°30'`: Always count consecutively starting from the same sign | Parents, ancestral lineage & hereditary karma | `2` | `4.5` | `1.5` | **`0.5`** |
| **D16** | *Shodasamsa* | `01° 52' 30"` | 16 slices: Movable from Mesha, Fixed from Simha, Dual from Dhanu | Vehicles, luxury, conveyances & inner contentment | `—` | `—` | `1.5` | **`2.0`** |
| **D20** | *Vimsamsa* | `01° 30'` | 20 slices: Movable from Mesha, Fixed from Dhanu, Dual from Simha | Spiritual sadhana, Upasana, mantra & devotion | `—` | `—` | `—` | **`0.5`** |
| **D24** | *Chaturvimsamsa* | `01° 15'` | 24 slices: Odd signs count from Simha (`04`); Even signs count from Karka (`03`) | Higher learning, scholarship, Vidya & wisdom | `—` | `—` | `—` | **`0.5`** |
| **D27** | *Saptavimsamsa* | `01° 06' 40"` | 27 slices: Fire from Mesha, Earth from Karka, Air from Tula, Water from Makara | Physical stamina, bodily strength & vitality | `—` | `—` | `—` | **`0.5`** |
| **D30** | *Trimsamsa* | `Unequal (5/5/8/7/5°)` | Odd: Mars 5°, Sat 5°, Jup 8°, Mer 7°, Ven 5°; Even: Ven 5°, Mer 7°, Jup 8°, Sat 5°, Mars 5° | Arishta, misfortune, character & crisis resilience | `1` | `2` | `1.5` | **`1.0`** |
| **D40** | *Khavedamsa* | `00° 45'` | 40 slices: Odd signs count from Mesha (`00`); Even signs count from Tula (`06`) | Matrilineal karma & auspicious/inauspicious habits | `—` | `—` | `—` | **`0.5`** |
| **D45** | *Akshavedamsa* | `00° 40'` | 45 slices: Movable from Mesha, Fixed from Simha, Dual from Dhanu | Patrilineal karma, ethical conduct & royal character | `—` | `—` | `—` | **`0.5`** |
| **D60** | *Shashtiamsa* | `00° 30'` | 60 slices of `30'`: Count `⌊deg × 2⌋` from the same sign; 60 named Sanskrit deities | Past-life Sanchita Karma & twin birth differentiation | `—` | `—` | `5.0` | **`4.0`** |

### Table 9B — Complete 108-Pada *Navamsa* (`D9`), *Pushkara Navamsa* (`*PN*`), & *Vargottama* (`*V*`) Master Lookup Grid

| Slice # | Degree Range in Sign | Arcminutes | Fire Signs (`Mesha, Simha, Dhanu`) | Earth Signs (`Vrishabha, Kanya, Makara`) | Air Signs (`Mithuna, Tula, Kumbha`) | Water Signs (`Karka, Vrishchika, Meena`) |
|---|---|---|---|---|---|---|
| **Navamsa 1** | `00° 00' – 03° 20'` | `0'–200'` | **Mesha** | **Makara** | **Tula** | **Karka** *PN* |
| **Navamsa 2** | `03° 20' – 06° 40'` | `200'–400'` | **Vrishabha** | **Kumbha** | **Vrishchika** | **Simha** |
| **Navamsa 3** | `06° 40' – 10° 00'` | `400'–600'` | **Mithuna** | **Meena** *PN* | **Dhanu** | **Kanya** *PN* |
| **Navamsa 4** | `10° 00' – 13° 20'` | `600'–800'` | **Karka** | **Mesha** | **Makara** | **Tula** |
| **Navamsa 5** | `13° 20' – 16° 40'` | `800'–1000'` | **Simha** | **Vrishabha** *PN* | **Kumbha** | **Vrishchika** |
| **Navamsa 6** | `16° 40' – 20° 00'` | `1000'–1200'` | **Kanya** | **Mithuna** | **Meena** *PN* | **Dhanu** |
| **Navamsa 7** | `20° 00' – 23° 20'` | `1200'–1400'` | **Tula** *PN* | **Karka** | **Mesha** | **Makara** |
| **Navamsa 8** | `23° 20' – 26° 40'` | `1400'–1600'` | **Vrishchika** | **Simha** | **Vrishabha** | **Kumbha** |
| **Navamsa 9** | `26° 40' – 30° 00'` | `1600'–1800'` | **Dhanu** *PN* | **Kanya** | **Mithuna** | **Meena** |

### Table 9C — Complete *Dasamsa* (`D10` — `3° 00'` per Slice) & *Dwadasamsa* (`D12` — `2° 30'` per Slice) Lookup Grid

| Slice # | D10 Degree Span | D10 Odd Signs (`1,3,5,7,9,11`) | D10 Even Signs (`2,4,6,8,10,12`) | D12 Degree Span | D12 Any Sign (Offset from Sign) |
|---|---|---|---|---|---|
| **01** | `00° 00' – 03° 00'` | **+0 signs** (1th from Rashi) | **+8 signs** (9th from Rashi) | `00° 00' – 02° 30'` | **+0 signs** (1th sign from Rashi) |
| **02** | `03° 00' – 06° 00'` | **+1 signs** (2th from Rashi) | **+9 signs** (10th from Rashi) | `02° 30' – 05° 00'` | **+1 signs** (2th sign from Rashi) |
| **03** | `06° 00' – 09° 00'` | **+2 signs** (3th from Rashi) | **+10 signs** (11th from Rashi) | `05° 00' – 07° 30'` | **+2 signs** (3th sign from Rashi) |
| **04** | `09° 00' – 12° 00'` | **+3 signs** (4th from Rashi) | **+11 signs** (12th from Rashi) | `07° 30' – 10° 00'` | **+3 signs** (4th sign from Rashi) |
| **05** | `12° 00' – 15° 00'` | **+4 signs** (5th from Rashi) | **+0 signs** (1th from Rashi) | `10° 00' – 12° 30'` | **+4 signs** (5th sign from Rashi) |
| **06** | `15° 00' – 18° 00'` | **+5 signs** (6th from Rashi) | **+1 signs** (2th from Rashi) | `12° 30' – 15° 00'` | **+5 signs** (6th sign from Rashi) |
| **07** | `18° 00' – 21° 00'` | **+6 signs** (7th from Rashi) | **+2 signs** (3th from Rashi) | `15° 00' – 17° 30'` | **+6 signs** (7th sign from Rashi) |
| **08** | `21° 00' – 24° 00'` | **+7 signs** (8th from Rashi) | **+3 signs** (4th from Rashi) | `17° 30' – 20° 00'` | **+7 signs** (8th sign from Rashi) |
| **09** | `24° 00' – 27° 00'` | **+8 signs** (9th from Rashi) | **+4 signs** (5th from Rashi) | `20° 00' – 22° 30'` | **+8 signs** (9th sign from Rashi) |
| **10** | `27° 00' – 30° 00'` | **+9 signs** (10th from Rashi) | **+5 signs** (6th from Rashi) | `22° 30' – 25° 00'` | **+9 signs** (10th sign from Rashi) |
| **11** | — | — | — | `25° 00' – 27° 30'` | **+10 signs** (11th sign from Rashi) |
| **12** | — | — | — | `27° 30' – 30° 00'` | **+11 signs** (12th sign from Rashi) |

### Table 9D — Complete 36 *Drekkana Swarupas* (`D3` Decanates — *Brihat Jataka* & *Phaladeepika* Classification)

| # | Rashi | Decanate (`D3` Span) | Resulting D3 Sign & Lord | Classical *Drekkana Swarupa* Name | Nature (*Sarpa / Pakshi / Ayudha / Chatushpada / Pasa*) |
|---|---|---|---|---|---|
| **01** | **Mesha** | Decanate 1 (`00°–10°`) | **Mesha** (Mars) | *Fierce man in white cloth holding a raised battle-axe* | `Ayudha (Ayudha, Krura)` |
| **02** | **Mesha** | Decanate 2 (`10°–20°`) | **Simha** (Sun) | *Horse-faced woman wearing red garments with a pot of jewels* | `Chatushpada (Chatushpada, Saumya)` |
| **03** | **Mesha** | Decanate 3 (`20°–30°`) | **Dhanu** (Jupiter) | *Fierce man skilled in arts holding an uplifted staff* | `Krura (Krura, Ayudha)` |
| **04** | **Vrishabha** | Decanate 1 (`00°–10°`) | **Vrishabha** (Venus) | *Woman with curled hair carrying a water vessel desiring food and ornaments* | `Saumya (Saumya)` |
| **05** | **Vrishabha** | Decanate 2 (`10°–20°`) | **Kanya** (Mercury) | *Man skilled in agriculture and cattle with a ram-like neck* | `Chatushpada (Chatushpada, Saumya)` |
| **06** | **Vrishabha** | Decanate 3 (`20°–30°`) | **Makara** (Saturn) | *Elephant-bodied figure with white tusks and tawny eyes thinking of deer* | `Chatushpada (Chatushpada, Krura)` |
| **07** | **Mithuna** | Decanate 1 (`00°–10°`) | **Mithuna** (Mercury) | *Graceful woman fond of needlework and ornaments* | `Saumya (Saumya)` |
| **08** | **Mithuna** | Decanate 2 (`10°–20°`) | **Tula** (Venus) | *Eagle-faced warrior in a flower garden holding bow and arrows* | `Pakshi (Pakshi, Ayudha)` |
| **09** | **Mithuna** | Decanate 3 (`20°–30°`) | **Kumbha** (Saturn) | *Man adorned with jewels holding bow, quiver, mail, and lute* | `Ayudha (Ayudha, Saumya)` |
| **10** | **Karka** | Decanate 1 (`00°–10°`) | **Karka** (Moon) | *Figure holding leaves, roots, and fruits with elephant body and horse neck* | `Chatushpada (Chatushpada, Saumya)` |
| **11** | **Karka** | Decanate 2 (`10°–20°`) | **Vrishchika** (Mars) | *Youthful woman in forest with a lotus on head and a serpent* | `Sarpa (Sarpa, Krura)` |
| **12** | **Karka** | Decanate 3 (`20°–30°`) | **Meena** (Jupiter) | *Man coiled by a serpent setting out on a boat across the ocean for gems* | `Sarpa (Sarpa, Krura)` |
| **13** | **Simha** | Decanate 1 (`00°–10°`) | **Simha** (Sun) | *Vulture and jackal atop a Shalmali tree* | `Pakshi (Pakshi, Chatushpada, Krura)` |
| **14** | **Simha** | Decanate 2 (`10°–20°`) | **Dhanu** (Jupiter) | *Horse-shaped figure wearing a white floral garland holding a bow* | `Chatushpada (Chatushpada, Ayudha)` |
| **15** | **Simha** | Decanate 3 (`20°–30°`) | **Mesha** (Mars) | *Bear-faced figure with ape-like deeds holding a club and bow* | `Ayudha (Ayudha, Chatushpada, Krura)` |
| **16** | **Kanya** | Decanate 1 (`00°–10°`) | **Kanya** (Mercury) | *Maiden carrying a jar filled with blooming flowers* | `Saumya (Saumya)` |
| **17** | **Kanya** | Decanate 2 (`10°–20°`) | **Makara** (Saturn) | *Accountant holding a stylus calculating income and expenditure* | `Saumya (Saumya)` |
| **18** | **Kanya** | Decanate 3 (`20°–30°`) | **Vrishabha** (Venus) | *Tall golden woman holding a pot and sacrificial ladle heading to a temple* | `Saumya (Saumya)` |
| **19** | **Tula** | Decanate 1 (`00°–10°`) | **Tula** (Venus) | *Merchant seated in a market holding scales and weights* | `Saumya (Saumya)` |
| **20** | **Tula** | Decanate 2 (`10°–20°`) | **Kumbha** (Saturn) | *Vulture-faced figure hungry and thirsty thinking of wife and children* | `Pakshi (Pakshi, Krura)` |
| **21** | **Tula** | Decanate 3 (`20°–30°`) | **Mithuna** (Mercury) | *Horse-faced figure with golden quiver and armor frightening animals in woods* | `Chatushpada (Chatushpada, Ayudha)` |
| **22** | **Vrishchika** | Decanate 1 (`00°–10°`) | **Vrishchika** (Mars) | *Woman without garments coming from the sea with feet bound by serpents* | `Sarpa (Sarpa, Krura)` |
| **23** | **Vrishchika** | Decanate 2 (`10°–20°`) | **Meena** (Jupiter) | *Woman desiring comfort with body encircled by serpents* | `Sarpa (Sarpa, Pasha)` |
| **24** | **Vrishchika** | Decanate 3 (`20°–30°`) | **Karka** (Moon) | *Lion with broad face resembling a tortoise guarding a sandalwood forest* | `Chatushpada (Chatushpada, Krura)` |
| **25** | **Dhanu** | Decanate 1 (`00°–10°`) | **Dhanu** (Jupiter) | *Centaur with human face and horse body holding a long bow at a hermitage* | `Ayudha (Ayudha, Chatushpada)` |
| **26** | **Dhanu** | Decanate 2 (`10°–20°`) | **Mesha** (Mars) | *Graceful woman seated on a throne picking gems from the ocean* | `Saumya (Saumya)` |
| **27** | **Dhanu** | Decanate 3 (`20°–30°`) | **Simha** (Sun) | *Bearded man of golden hue seated on a throne holding a staff* | `Ayudha (Ayudha, Saumya)` |
| **28** | **Makara** | Decanate 1 (`00°–10°`) | **Makara** (Saturn) | *Hairy fierce man like a crocodile holding iron fetters and nose-rope* | `Nigada (Nigada, Pasha, Krura)` |
| **29** | **Makara** | Decanate 2 (`10°–20°`) | **Vrishabha** (Venus) | *Woman skilled in arts with lotus eyes wearing iron ear-ornaments* | `Krura (Krura, Saumya)` |
| **30** | **Makara** | Decanate 3 (`20°–30°`) | **Kanya** (Mercury) | *Kinnara-bodied figure with blanket, quiver, bow, and armor* | `Ayudha (Ayudha, Chatushpada)` |
| **31** | **Kumbha** | Decanate 1 (`00°–10°`) | **Kumbha** (Saturn) | *Vulture-faced figure anxious over oil, wine, water, and pots* | `Pakshi (Pakshi, Krura)` |
| **32** | **Kumbha** | Decanate 2 (`10°–20°`) | **Mithuna** (Mercury) | *Woman in a burnt wagon in a forest carrying iron pots bound by cords* | `Pasha (Pasha, Krura)` |
| **33** | **Kumbha** | Decanate 3 (`20°–30°`) | **Tula** (Venus) | *Dark man with hairy ears wearing a bark crown carrying pots of iron and resin* | `Krura (Krura, Saumya)` |
| **34** | **Meena** | Decanate 1 (`00°–10°`) | **Meena** (Jupiter) | *Man carrying sacrificial vessels, pearls, and gems crossing the sea in a boat* | `Saumya (Saumya)` |
| **35** | **Meena** | Decanate 2 (`10°–20°`) | **Karka** (Moon) | *Bright-faced woman steering a bannered ship to the coast* | `Saumya (Saumya)` |
| **36** | **Meena** | Decanate 3 (`20°–30°`) | **Vrishchika** (Mars) | *Man coiled by a serpent in a forest pit crying from thieves and fire* | `Sarpa (Sarpa, Pasha, Krura)` |

### Table 9E — Complete 60 *Shashtiamsa* (`D60` — `00° 30'` Each) Deities & *Shubha / Krura* Classification

| # | Odd Sign Span | Even Sign Span (Reversed) | Sanskrit *Shashtiamsa* Deity | Nature | # | Odd Sign Span | Even Sign Span (Reversed) | Sanskrit *Shashtiamsa* Deity | Nature |
|---|---|---|---|---|---|---|---|---|---|
| **01** | `00°00'–00°30'` | `29°30'–30°00'` | **Ghora** | Krura (Malefic) | **31** | `15°00'–15°30'` | `14°30'–15°00'` | **Mrityu** | Krura (Malefic) |
| **02** | `00°30'–01°00'` | `29°00'–29°30'` | **Rakshasa** | Krura (Malefic) | **32** | `15°30'–16°00'` | `14°00'–14°30'` | **Kaala** | Krura (Malefic) |
| **03** | `01°00'–01°30'` | `28°30'–29°00'` | **Deva** | Krura (Malefic) | **33** | `16°00'–16°30'` | `13°30'–14°00'` | **Davagni** | Krura (Malefic) |
| **04** | `01°30'–02°00'` | `28°00'–28°30'` | **Kubera** | Krura (Malefic) | **34** | `16°30'–17°00'` | `13°00'–13°30'` | **Ghora** | Krura (Malefic) |
| **05** | `02°00'–02°30'` | `27°30'–28°00'` | **Yaksha** | Krura (Malefic) | **35** | `17°00'–17°30'` | `12°30'–13°00'` | **Yama** | Krura (Malefic) |
| **06** | `02°30'–03°00'` | `27°00'–27°30'` | **Kinnara** | Krura (Malefic) | **36** | `17°30'–18°00'` | `12°00'–12°30'` | **Kantaka** | Krura (Malefic) |
| **07** | `03°00'–03°30'` | `26°30'–27°00'` | **Bhrashta** | Krura (Malefic) | **37** | `18°00'–18°30'` | `11°30'–12°00'` | **Sudha** | Krura (Malefic) |
| **08** | `03°30'–04°00'` | `26°00'–26°30'` | **Kulaghna** | Krura (Malefic) | **38** | `18°30'–19°00'` | `11°00'–11°30'` | **Amrita** | Krura (Malefic) |
| **09** | `04°00'–04°30'` | `25°30'–26°00'` | **Garala** | Krura (Malefic) | **39** | `19°00'–19°30'` | `10°30'–11°00'` | **Purnachandra** | Krura (Malefic) |
| **10** | `04°30'–05°00'` | `25°00'–25°30'` | **Vahni** | Krura (Malefic) | **40** | `19°30'–20°00'` | `10°00'–10°30'` | **Vishadagdha** | Krura (Malefic) |
| **11** | `05°00'–05°30'` | `24°30'–25°00'` | **Maya** | Krura (Malefic) | **41** | `20°00'–20°30'` | `09°30'–10°00'` | **Kulanasa** | Krura (Malefic) |
| **12** | `05°30'–06°00'` | `24°00'–24°30'` | **Purishaka** | Krura (Malefic) | **42** | `20°30'–21°00'` | `09°00'–09°30'` | **Vamshakshaya** | Krura (Malefic) |
| **13** | `06°00'–06°30'` | `23°30'–24°00'` | **Apampati** | Krura (Malefic) | **43** | `21°00'–21°30'` | `08°30'–09°00'` | **Utpata** | Krura (Malefic) |
| **14** | `06°30'–07°00'` | `23°00'–23°30'` | **Marutwan** | Krura (Malefic) | **44** | `21°30'–22°00'` | `08°00'–08°30'` | **Kala** | Krura (Malefic) |
| **15** | `07°00'–07°30'` | `22°30'–23°00'` | **Kala** | Krura (Malefic) | **45** | `22°00'–22°30'` | `07°30'–08°00'` | **Saumya** | Krura (Malefic) |
| **16** | `07°30'–08°00'` | `22°00'–22°30'` | **Sarpa** | Krura (Malefic) | **46** | `22°30'–23°00'` | `07°00'–07°30'` | **Komala** | Krura (Malefic) |
| **17** | `08°00'–08°30'` | `21°30'–22°00'` | **Amrita** | Krura (Malefic) | **47** | `23°00'–23°30'` | `06°30'–07°00'` | **Sheetala** | Krura (Malefic) |
| **18** | `08°30'–09°00'` | `21°00'–21°30'` | **Indu** | Krura (Malefic) | **48** | `23°30'–24°00'` | `06°00'–06°30'` | **Karaladamshtra** | Krura (Malefic) |
| **19** | `09°00'–09°30'` | `20°30'–21°00'` | **Mridu** | Krura (Malefic) | **49** | `24°00'–24°30'` | `05°30'–06°00'` | **Chandramukhi** | Krura (Malefic) |
| **20** | `09°30'–10°00'` | `20°00'–20°30'` | **Komala** | Krura (Malefic) | **50** | `24°30'–25°00'` | `05°00'–05°30'` | **Praveena** | Krura (Malefic) |
| **21** | `10°00'–10°30'` | `19°30'–20°00'` | **Heramba** | Krura (Malefic) | **51** | `25°00'–25°30'` | `04°30'–05°00'` | **Kalapavaka** | Krura (Malefic) |
| **22** | `10°30'–11°00'` | `19°00'–19°30'` | **Brahma** | Krura (Malefic) | **52** | `25°30'–26°00'` | `04°00'–04°30'` | **Dandayudha** | Krura (Malefic) |
| **23** | `11°00'–11°30'` | `18°30'–19°00'` | **Vishnu** | Krura (Malefic) | **53** | `26°00'–26°30'` | `03°30'–04°00'` | **Nirmala** | Krura (Malefic) |
| **24** | `11°30'–12°00'` | `18°00'–18°30'` | **Maheshwara** | Krura (Malefic) | **54** | `26°30'–27°00'` | `03°00'–03°30'` | **Saumya** | Krura (Malefic) |
| **25** | `12°00'–12°30'` | `17°30'–18°00'` | **Deva** | Krura (Malefic) | **55** | `27°00'–27°30'` | `02°30'–03°00'` | **Krura** | Krura (Malefic) |
| **26** | `12°30'–13°00'` | `17°00'–17°30'` | **Ardra** | Krura (Malefic) | **56** | `27°30'–28°00'` | `02°00'–02°30'` | **Atisheetala** | Krura (Malefic) |
| **27** | `13°00'–13°30'` | `16°30'–17°00'` | **Kalinasa** | Krura (Malefic) | **57** | `28°00'–28°30'` | `01°30'–02°00'` | **Amrita** | Krura (Malefic) |
| **28** | `13°30'–14°00'` | `16°00'–16°30'` | **Kshitishwara** | Krura (Malefic) | **58** | `28°30'–29°00'` | `01°00'–01°30'` | **Payodhi** | Krura (Malefic) |
| **29** | `14°00'–14°30'` | `15°30'–16°00'` | **Kamalakara** | Krura (Malefic) | **59** | `29°00'–29°30'` | `00°30'–01°00'` | **Bhramana** | Krura (Malefic) |
| **30** | `14°30'–15°00'` | `15°00'–15°30'` | **Gulika** | Krura (Malefic) | **60** | `29°30'–30°00'` | `00°00'–00°30'` | **Indurekha** | Krura (Malefic) |

## Chapter 10 — Complete 132-Cell *Mrityu Bhaga* (Fatal Degrees), 22nd *Khara Drekkana*, & 64th *Khara Navamsa* Master Vulnerability Tables

### Table 10A — Complete 132-Cell *Mrityu Bhaga* (Fatal Degree) Master Table Across All 12 Signs (`Phaladeepika` & `Jataka Parijata`)

| Rashi (Sign) | *Pushkara Bhaga* (Auspicious) | Lagna | Surya (Sun) | Chandra (Moon) | Mangala (Mars) | Budha (Mercury) | Guru (Jupiter) | Shukra (Venus) | Shani (Saturn) | Rahu | Ketu | Mandi (Gulika) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Mesha** | **`21°`** | `01°` | `20°` | `26°` | `19°` | `15°` | `19°` | `28°` | `10°` | `14°` | `08°` | `23°` |
| **Vrishabha** | **`14°`** | `09°` | `09°` | `12°` | `28°` | `14°` | `29°` | `15°` | `04°` | `13°` | `18°` | `24°` |
| **Mithuna** | **`18°`** | `22°` | `12°` | `13°` | `25°` | `13°` | `12°` | `11°` | `07°` | `12°` | `20°` | `16°` |
| **Karka** | **`08°`** | `22°` | `06°` | `25°` | `23°` | `12°` | `27°` | `17°` | `09°` | `11°` | `10°` | `12°` |
| **Simha** | **`19°`** | `25°` | `08°` | `24°` | `29°` | `08°` | `06°` | `10°` | `12°` | `24°` | `21°` | `19°` |
| **Kanya** | **`09°`** | `02°` | `24°` | `11°` | `28°` | `18°` | `04°` | `13°` | `16°` | `23°` | `22°` | `28°` |
| **Tula** | **`24°`** | `04°` | `16°` | `26°` | `14°` | `20°` | `13°` | `04°` | `03°` | `22°` | `23°` | `14°` |
| **Vrishchika** | **`11°`** | `23°` | `17°` | `14°` | `21°` | `10°` | `10°` | `06°` | `18°` | `21°` | `24°` | `13°` |
| **Dhanu** | **`23°`** | `18°` | `22°` | `13°` | `02°` | `21°` | `17°` | `27°` | `28°` | `10°` | `11°` | `04°` |
| **Makara** | **`14°`** | `20°` | `02°` | `25°` | `15°` | `22°` | `11°` | `12°` | `14°` | `20°` | `12°` | `20°` |
| **Kumbha** | **`19°`** | `24°` | `03°` | `05°` | `11°` | `07°` | `15°` | `29°` | `13°` | `18°` | `13°` | `15°` |
| **Meena** | **`09°`** | `10°` | `23°` | `12°` | `06°` | `05°` | `28°` | `19°` | `15°` | `08°` | `14°` | `09°` |

### Table 10B — Complete 22nd *Khara Drekkana* & 64th *Khara Navamsa* Lookup Table for Every Ascendant / Moon Position

| Natal Sign (`D1`) | Decanate 1 (`0°–10°`) 22nd Drekkana Sign & Lord | Decanate 2 (`10°–20°`) 22nd Drekkana Sign & Lord | Decanate 3 (`20°–30°`) 22nd Drekkana Sign & Lord | 64th *Khara Navamsa* Rule (From Any Natal `D9` Sign) |
|---|---|---|---|---|
| **Mesha** | **Vrishchika** (Mars) | **Meena** (Jupiter) | **Karka** (Moon) | If Natal `D9` is **Mesha**, 64th *Khara D9* is **Karka** (Moon) |
| **Vrishabha** | **Dhanu** (Jupiter) | **Mesha** (Mars) | **Simha** (Sun) | If Natal `D9` is **Vrishabha**, 64th *Khara D9* is **Simha** (Sun) |
| **Mithuna** | **Makara** (Saturn) | **Vrishabha** (Venus) | **Kanya** (Mercury) | If Natal `D9` is **Mithuna**, 64th *Khara D9* is **Kanya** (Mercury) |
| **Karka** | **Kumbha** (Saturn) | **Mithuna** (Mercury) | **Tula** (Venus) | If Natal `D9` is **Karka**, 64th *Khara D9* is **Tula** (Venus) |
| **Simha** | **Meena** (Jupiter) | **Karka** (Moon) | **Vrishchika** (Mars) | If Natal `D9` is **Simha**, 64th *Khara D9* is **Vrishchika** (Mars) |
| **Kanya** | **Mesha** (Mars) | **Simha** (Sun) | **Dhanu** (Jupiter) | If Natal `D9` is **Kanya**, 64th *Khara D9* is **Dhanu** (Jupiter) |
| **Tula** | **Vrishabha** (Venus) | **Kanya** (Mercury) | **Makara** (Saturn) | If Natal `D9` is **Tula**, 64th *Khara D9* is **Makara** (Saturn) |
| **Vrishchika** | **Mithuna** (Mercury) | **Tula** (Venus) | **Kumbha** (Saturn) | If Natal `D9` is **Vrishchika**, 64th *Khara D9* is **Kumbha** (Saturn) |
| **Dhanu** | **Karka** (Moon) | **Vrishchika** (Mars) | **Meena** (Jupiter) | If Natal `D9` is **Dhanu**, 64th *Khara D9* is **Meena** (Jupiter) |
| **Makara** | **Simha** (Sun) | **Dhanu** (Jupiter) | **Mesha** (Mars) | If Natal `D9` is **Makara**, 64th *Khara D9* is **Mesha** (Mars) |
| **Kumbha** | **Kanya** (Mercury) | **Makara** (Saturn) | **Vrishabha** (Venus) | If Natal `D9` is **Kumbha**, 64th *Khara D9* is **Vrishabha** (Venus) |
| **Meena** | **Tula** (Venus) | **Kumbha** (Saturn) | **Mithuna** (Mercury) | If Natal `D9` is **Meena**, 64th *Khara D9* is **Mithuna** (Mercury) |

## Chapter 11 — Complete Krishnamurti Padhati (*KP*) 249 Sub-Lord Master Table (`#001` to `#249`) & 4-Fold Significator Rules

### Table 11A — Complete 249-Division *KP* Sign-Star-Sub Master Reference Table (`000° 00' 00"` to `360° 00' 00"`)

| Sub # | Zodiac Sign (`Rashi`) | Sign Lord | Nakshatra (`Star`) | Star Lord | Sub Lord | Start (`DMS` in Sign) | End (`DMS` in Sign) | Span (`MM' SS"`) |
|---|---|---|---|---|---|---|---|---|
| **`#001`** | **Mesha** | Mars | Ashwini | **Ketu** | **`Ketu`** | `00° 00' 00"` | `00° 46' 40"` | `46' 40"` |
| **`#002`** | **Mesha** | Mars | Ashwini | **Ketu** | **`Venus`** | `00° 46' 40"` | `03° 00' 00"` | `133' 20"` |
| **`#003`** | **Mesha** | Mars | Ashwini | **Ketu** | **`Sun`** | `03° 00' 00"` | `03° 40' 00"` | `40' 00"` |
| **`#004`** | **Mesha** | Mars | Ashwini | **Ketu** | **`Moon`** | `03° 40' 00"` | `04° 46' 40"` | `66' 40"` |
| **`#005`** | **Mesha** | Mars | Ashwini | **Ketu** | **`Mars`** | `04° 46' 40"` | `05° 33' 20"` | `46' 40"` |
| **`#006`** | **Mesha** | Mars | Ashwini | **Ketu** | **`Rahu`** | `05° 33' 20"` | `07° 33' 20"` | `120' 00"` |
| **`#007`** | **Mesha** | Mars | Ashwini | **Ketu** | **`Jupiter`** | `07° 33' 20"` | `09° 20' 00"` | `106' 40"` |
| **`#008`** | **Mesha** | Mars | Ashwini | **Ketu** | **`Saturn`** | `09° 20' 00"` | `11° 26' 40"` | `126' 40"` |
| **`#009`** | **Mesha** | Mars | Ashwini | **Ketu** | **`Mercury`** | `11° 26' 40"` | `13° 20' 00"` | `113' 20"` |
| **`#010`** | **Mesha** | Mars | Bharani | **Venus** | **`Venus`** | `13° 20' 00"` | `15° 33' 20"` | `133' 20"` |
| **`#011`** | **Mesha** | Mars | Bharani | **Venus** | **`Sun`** | `15° 33' 20"` | `16° 13' 20"` | `40' 00"` |
| **`#012`** | **Mesha** | Mars | Bharani | **Venus** | **`Moon`** | `16° 13' 20"` | `17° 20' 00"` | `66' 40"` |
| **`#013`** | **Mesha** | Mars | Bharani | **Venus** | **`Mars`** | `17° 20' 00"` | `18° 06' 40"` | `46' 40"` |
| **`#014`** | **Mesha** | Mars | Bharani | **Venus** | **`Rahu`** | `18° 06' 40"` | `20° 06' 40"` | `120' 00"` |
| **`#015`** | **Mesha** | Mars | Bharani | **Venus** | **`Jupiter`** | `20° 06' 40"` | `21° 53' 20"` | `106' 40"` |
| **`#016`** | **Mesha** | Mars | Bharani | **Venus** | **`Saturn`** | `21° 53' 20"` | `24° 00' 00"` | `126' 40"` |
| **`#017`** | **Mesha** | Mars | Bharani | **Venus** | **`Mercury`** | `24° 00' 00"` | `25° 53' 20"` | `113' 20"` |
| **`#018`** | **Mesha** | Mars | Bharani | **Venus** | **`Ketu`** | `25° 53' 20"` | `26° 40' 00"` | `46' 40"` |
| **`#019`** | **Mesha** | Mars | Krittika | **Sun** | **`Sun`** | `26° 40' 00"` | `27° 20' 00"` | `40' 00"` |
| **`#020`** | **Mesha** | Mars | Krittika | **Sun** | **`Moon`** | `27° 20' 00"` | `28° 26' 40"` | `66' 40"` |
| **`#021`** | **Mesha** | Mars | Krittika | **Sun** | **`Mars`** | `28° 26' 40"` | `29° 13' 20"` | `46' 40"` |
| **`#022`** | **Mesha** | Mars | Krittika | **Sun** | **`Rahu`** | `29° 13' 20"` | `30° 00' 00"` | `46' 40"` |
| **`#023`** | **Vrishabha** | Venus | Krittika | **Sun** | **`Rahu`** | `00° 00' 00"` | `01° 13' 20"` | `73' 20"` |
| **`#024`** | **Vrishabha** | Venus | Krittika | **Sun** | **`Jupiter`** | `01° 13' 20"` | `03° 00' 00"` | `106' 40"` |
| **`#025`** | **Vrishabha** | Venus | Krittika | **Sun** | **`Saturn`** | `03° 00' 00"` | `05° 06' 40"` | `126' 40"` |
| **`#026`** | **Vrishabha** | Venus | Krittika | **Sun** | **`Mercury`** | `05° 06' 40"` | `07° 00' 00"` | `113' 20"` |
| **`#027`** | **Vrishabha** | Venus | Krittika | **Sun** | **`Ketu`** | `07° 00' 00"` | `07° 46' 40"` | `46' 40"` |
| **`#028`** | **Vrishabha** | Venus | Krittika | **Sun** | **`Venus`** | `07° 46' 40"` | `10° 00' 00"` | `133' 20"` |
| **`#029`** | **Vrishabha** | Venus | Rohini | **Moon** | **`Moon`** | `10° 00' 00"` | `11° 06' 40"` | `66' 40"` |
| **`#030`** | **Vrishabha** | Venus | Rohini | **Moon** | **`Mars`** | `11° 06' 40"` | `11° 53' 20"` | `46' 40"` |
| **`#031`** | **Vrishabha** | Venus | Rohini | **Moon** | **`Rahu`** | `11° 53' 20"` | `13° 53' 20"` | `120' 00"` |
| **`#032`** | **Vrishabha** | Venus | Rohini | **Moon** | **`Jupiter`** | `13° 53' 20"` | `15° 40' 00"` | `106' 40"` |
| **`#033`** | **Vrishabha** | Venus | Rohini | **Moon** | **`Saturn`** | `15° 40' 00"` | `17° 46' 40"` | `126' 40"` |
| **`#034`** | **Vrishabha** | Venus | Rohini | **Moon** | **`Mercury`** | `17° 46' 40"` | `19° 40' 00"` | `113' 20"` |
| **`#035`** | **Vrishabha** | Venus | Rohini | **Moon** | **`Ketu`** | `19° 40' 00"` | `20° 26' 40"` | `46' 40"` |
| **`#036`** | **Vrishabha** | Venus | Rohini | **Moon** | **`Venus`** | `20° 26' 40"` | `22° 40' 00"` | `133' 20"` |
| **`#037`** | **Vrishabha** | Venus | Rohini | **Moon** | **`Sun`** | `22° 40' 00"` | `23° 20' 00"` | `40' 00"` |
| **`#038`** | **Vrishabha** | Venus | Mrigashira | **Mars** | **`Mars`** | `23° 20' 00"` | `24° 06' 40"` | `46' 40"` |
| **`#039`** | **Vrishabha** | Venus | Mrigashira | **Mars** | **`Rahu`** | `24° 06' 40"` | `26° 06' 40"` | `120' 00"` |
| **`#040`** | **Vrishabha** | Venus | Mrigashira | **Mars** | **`Jupiter`** | `26° 06' 40"` | `27° 53' 20"` | `106' 40"` |
| **`#041`** | **Vrishabha** | Venus | Mrigashira | **Mars** | **`Saturn`** | `27° 53' 20"` | `30° 00' 00"` | `126' 40"` |
| **`#042`** | **Mithuna** | Mercury | Mrigashira | **Mars** | **`Mercury`** | `00° 00' 00"` | `01° 53' 20"` | `113' 20"` |
| **`#043`** | **Mithuna** | Mercury | Mrigashira | **Mars** | **`Ketu`** | `01° 53' 20"` | `02° 40' 00"` | `46' 40"` |
| **`#044`** | **Mithuna** | Mercury | Mrigashira | **Mars** | **`Venus`** | `02° 40' 00"` | `04° 53' 20"` | `133' 20"` |
| **`#045`** | **Mithuna** | Mercury | Mrigashira | **Mars** | **`Sun`** | `04° 53' 20"` | `05° 33' 20"` | `40' 00"` |
| **`#046`** | **Mithuna** | Mercury | Mrigashira | **Mars** | **`Moon`** | `05° 33' 20"` | `06° 40' 00"` | `66' 40"` |
| **`#047`** | **Mithuna** | Mercury | Ardra | **Rahu** | **`Rahu`** | `06° 40' 00"` | `08° 40' 00"` | `120' 00"` |
| **`#048`** | **Mithuna** | Mercury | Ardra | **Rahu** | **`Jupiter`** | `08° 40' 00"` | `10° 26' 40"` | `106' 40"` |
| **`#049`** | **Mithuna** | Mercury | Ardra | **Rahu** | **`Saturn`** | `10° 26' 40"` | `12° 33' 20"` | `126' 40"` |
| **`#050`** | **Mithuna** | Mercury | Ardra | **Rahu** | **`Mercury`** | `12° 33' 20"` | `14° 26' 40"` | `113' 20"` |
| **`#051`** | **Mithuna** | Mercury | Ardra | **Rahu** | **`Ketu`** | `14° 26' 40"` | `15° 13' 20"` | `46' 40"` |
| **`#052`** | **Mithuna** | Mercury | Ardra | **Rahu** | **`Venus`** | `15° 13' 20"` | `17° 26' 40"` | `133' 20"` |
| **`#053`** | **Mithuna** | Mercury | Ardra | **Rahu** | **`Sun`** | `17° 26' 40"` | `18° 06' 40"` | `40' 00"` |
| **`#054`** | **Mithuna** | Mercury | Ardra | **Rahu** | **`Moon`** | `18° 06' 40"` | `19° 13' 20"` | `66' 40"` |
| **`#055`** | **Mithuna** | Mercury | Ardra | **Rahu** | **`Mars`** | `19° 13' 20"` | `20° 00' 00"` | `46' 40"` |
| **`#056`** | **Mithuna** | Mercury | Punarvasu | **Jupiter** | **`Jupiter`** | `20° 00' 00"` | `21° 46' 40"` | `106' 40"` |
| **`#057`** | **Mithuna** | Mercury | Punarvasu | **Jupiter** | **`Saturn`** | `21° 46' 40"` | `23° 53' 20"` | `126' 40"` |
| **`#058`** | **Mithuna** | Mercury | Punarvasu | **Jupiter** | **`Mercury`** | `23° 53' 20"` | `25° 46' 40"` | `113' 20"` |
| **`#059`** | **Mithuna** | Mercury | Punarvasu | **Jupiter** | **`Ketu`** | `25° 46' 40"` | `26° 33' 20"` | `46' 40"` |
| **`#060`** | **Mithuna** | Mercury | Punarvasu | **Jupiter** | **`Venus`** | `26° 33' 20"` | `28° 46' 40"` | `133' 20"` |
| **`#061`** | **Mithuna** | Mercury | Punarvasu | **Jupiter** | **`Sun`** | `28° 46' 40"` | `29° 26' 40"` | `40' 00"` |
| **`#062`** | **Mithuna** | Mercury | Punarvasu | **Jupiter** | **`Moon`** | `29° 26' 40"` | `30° 00' 00"` | `33' 20"` |
| **`#063`** | **Karka** | Moon | Punarvasu | **Jupiter** | **`Moon`** | `00° 00' 00"` | `00° 33' 20"` | `33' 20"` |
| **`#064`** | **Karka** | Moon | Punarvasu | **Jupiter** | **`Mars`** | `00° 33' 20"` | `01° 20' 00"` | `46' 40"` |
| **`#065`** | **Karka** | Moon | Punarvasu | **Jupiter** | **`Rahu`** | `01° 20' 00"` | `03° 20' 00"` | `120' 00"` |
| **`#066`** | **Karka** | Moon | Pushya | **Saturn** | **`Saturn`** | `03° 20' 00"` | `05° 26' 40"` | `126' 40"` |
| **`#067`** | **Karka** | Moon | Pushya | **Saturn** | **`Mercury`** | `05° 26' 40"` | `07° 20' 00"` | `113' 20"` |
| **`#068`** | **Karka** | Moon | Pushya | **Saturn** | **`Ketu`** | `07° 20' 00"` | `08° 06' 40"` | `46' 40"` |
| **`#069`** | **Karka** | Moon | Pushya | **Saturn** | **`Venus`** | `08° 06' 40"` | `10° 20' 00"` | `133' 20"` |
| **`#070`** | **Karka** | Moon | Pushya | **Saturn** | **`Sun`** | `10° 20' 00"` | `11° 00' 00"` | `40' 00"` |
| **`#071`** | **Karka** | Moon | Pushya | **Saturn** | **`Moon`** | `11° 00' 00"` | `12° 06' 40"` | `66' 40"` |
| **`#072`** | **Karka** | Moon | Pushya | **Saturn** | **`Mars`** | `12° 06' 40"` | `12° 53' 20"` | `46' 40"` |
| **`#073`** | **Karka** | Moon | Pushya | **Saturn** | **`Rahu`** | `12° 53' 20"` | `14° 53' 20"` | `120' 00"` |
| **`#074`** | **Karka** | Moon | Pushya | **Saturn** | **`Jupiter`** | `14° 53' 20"` | `16° 40' 00"` | `106' 40"` |
| **`#075`** | **Karka** | Moon | Ashlesha | **Mercury** | **`Mercury`** | `16° 40' 00"` | `18° 33' 20"` | `113' 20"` |
| **`#076`** | **Karka** | Moon | Ashlesha | **Mercury** | **`Ketu`** | `18° 33' 20"` | `19° 20' 00"` | `46' 40"` |
| **`#077`** | **Karka** | Moon | Ashlesha | **Mercury** | **`Venus`** | `19° 20' 00"` | `21° 33' 20"` | `133' 20"` |
| **`#078`** | **Karka** | Moon | Ashlesha | **Mercury** | **`Sun`** | `21° 33' 20"` | `22° 13' 20"` | `40' 00"` |
| **`#079`** | **Karka** | Moon | Ashlesha | **Mercury** | **`Moon`** | `22° 13' 20"` | `23° 20' 00"` | `66' 40"` |
| **`#080`** | **Karka** | Moon | Ashlesha | **Mercury** | **`Mars`** | `23° 20' 00"` | `24° 06' 40"` | `46' 40"` |
| **`#081`** | **Karka** | Moon | Ashlesha | **Mercury** | **`Rahu`** | `24° 06' 40"` | `26° 06' 40"` | `120' 00"` |
| **`#082`** | **Karka** | Moon | Ashlesha | **Mercury** | **`Jupiter`** | `26° 06' 40"` | `27° 53' 20"` | `106' 40"` |
| **`#083`** | **Karka** | Moon | Ashlesha | **Mercury** | **`Saturn`** | `27° 53' 20"` | `30° 00' 00"` | `126' 40"` |
| **`#084`** | **Simha** | Sun | Magha | **Ketu** | **`Ketu`** | `00° 00' 00"` | `00° 46' 40"` | `46' 40"` |
| **`#085`** | **Simha** | Sun | Magha | **Ketu** | **`Venus`** | `00° 46' 40"` | `03° 00' 00"` | `133' 20"` |
| **`#086`** | **Simha** | Sun | Magha | **Ketu** | **`Sun`** | `03° 00' 00"` | `03° 40' 00"` | `40' 00"` |
| **`#087`** | **Simha** | Sun | Magha | **Ketu** | **`Moon`** | `03° 40' 00"` | `04° 46' 40"` | `66' 40"` |
| **`#088`** | **Simha** | Sun | Magha | **Ketu** | **`Mars`** | `04° 46' 40"` | `05° 33' 20"` | `46' 40"` |
| **`#089`** | **Simha** | Sun | Magha | **Ketu** | **`Rahu`** | `05° 33' 20"` | `07° 33' 20"` | `120' 00"` |
| **`#090`** | **Simha** | Sun | Magha | **Ketu** | **`Jupiter`** | `07° 33' 20"` | `09° 20' 00"` | `106' 40"` |
| **`#091`** | **Simha** | Sun | Magha | **Ketu** | **`Saturn`** | `09° 20' 00"` | `11° 26' 40"` | `126' 40"` |
| **`#092`** | **Simha** | Sun | Magha | **Ketu** | **`Mercury`** | `11° 26' 40"` | `13° 20' 00"` | `113' 20"` |
| **`#093`** | **Simha** | Sun | Purva Phalguni | **Venus** | **`Venus`** | `13° 20' 00"` | `15° 33' 20"` | `133' 20"` |
| **`#094`** | **Simha** | Sun | Purva Phalguni | **Venus** | **`Sun`** | `15° 33' 20"` | `16° 13' 20"` | `40' 00"` |
| **`#095`** | **Simha** | Sun | Purva Phalguni | **Venus** | **`Moon`** | `16° 13' 20"` | `17° 20' 00"` | `66' 40"` |
| **`#096`** | **Simha** | Sun | Purva Phalguni | **Venus** | **`Mars`** | `17° 20' 00"` | `18° 06' 40"` | `46' 40"` |
| **`#097`** | **Simha** | Sun | Purva Phalguni | **Venus** | **`Rahu`** | `18° 06' 40"` | `20° 06' 40"` | `120' 00"` |
| **`#098`** | **Simha** | Sun | Purva Phalguni | **Venus** | **`Jupiter`** | `20° 06' 40"` | `21° 53' 20"` | `106' 40"` |
| **`#099`** | **Simha** | Sun | Purva Phalguni | **Venus** | **`Saturn`** | `21° 53' 20"` | `24° 00' 00"` | `126' 40"` |
| **`#100`** | **Simha** | Sun | Purva Phalguni | **Venus** | **`Mercury`** | `24° 00' 00"` | `25° 53' 20"` | `113' 20"` |
| **`#101`** | **Simha** | Sun | Purva Phalguni | **Venus** | **`Ketu`** | `25° 53' 20"` | `26° 40' 00"` | `46' 40"` |
| **`#102`** | **Simha** | Sun | Uttara Phalguni | **Sun** | **`Sun`** | `26° 40' 00"` | `27° 20' 00"` | `40' 00"` |
| **`#103`** | **Simha** | Sun | Uttara Phalguni | **Sun** | **`Moon`** | `27° 20' 00"` | `28° 26' 40"` | `66' 40"` |
| **`#104`** | **Simha** | Sun | Uttara Phalguni | **Sun** | **`Mars`** | `28° 26' 40"` | `29° 13' 20"` | `46' 40"` |
| **`#105`** | **Simha** | Sun | Uttara Phalguni | **Sun** | **`Rahu`** | `29° 13' 20"` | `30° 00' 00"` | `46' 40"` |
| **`#106`** | **Kanya** | Mercury | Uttara Phalguni | **Sun** | **`Rahu`** | `00° 00' 00"` | `01° 13' 20"` | `73' 20"` |
| **`#107`** | **Kanya** | Mercury | Uttara Phalguni | **Sun** | **`Jupiter`** | `01° 13' 20"` | `03° 00' 00"` | `106' 40"` |
| **`#108`** | **Kanya** | Mercury | Uttara Phalguni | **Sun** | **`Saturn`** | `03° 00' 00"` | `05° 06' 40"` | `126' 40"` |
| **`#109`** | **Kanya** | Mercury | Uttara Phalguni | **Sun** | **`Mercury`** | `05° 06' 40"` | `07° 00' 00"` | `113' 20"` |
| **`#110`** | **Kanya** | Mercury | Uttara Phalguni | **Sun** | **`Ketu`** | `07° 00' 00"` | `07° 46' 40"` | `46' 40"` |
| **`#111`** | **Kanya** | Mercury | Uttara Phalguni | **Sun** | **`Venus`** | `07° 46' 40"` | `10° 00' 00"` | `133' 20"` |
| **`#112`** | **Kanya** | Mercury | Hasta | **Moon** | **`Moon`** | `10° 00' 00"` | `11° 06' 40"` | `66' 40"` |
| **`#113`** | **Kanya** | Mercury | Hasta | **Moon** | **`Mars`** | `11° 06' 40"` | `11° 53' 20"` | `46' 40"` |
| **`#114`** | **Kanya** | Mercury | Hasta | **Moon** | **`Rahu`** | `11° 53' 20"` | `13° 53' 20"` | `120' 00"` |
| **`#115`** | **Kanya** | Mercury | Hasta | **Moon** | **`Jupiter`** | `13° 53' 20"` | `15° 40' 00"` | `106' 40"` |
| **`#116`** | **Kanya** | Mercury | Hasta | **Moon** | **`Saturn`** | `15° 40' 00"` | `17° 46' 40"` | `126' 40"` |
| **`#117`** | **Kanya** | Mercury | Hasta | **Moon** | **`Mercury`** | `17° 46' 40"` | `19° 40' 00"` | `113' 20"` |
| **`#118`** | **Kanya** | Mercury | Hasta | **Moon** | **`Ketu`** | `19° 40' 00"` | `20° 26' 40"` | `46' 40"` |
| **`#119`** | **Kanya** | Mercury | Hasta | **Moon** | **`Venus`** | `20° 26' 40"` | `22° 40' 00"` | `133' 20"` |
| **`#120`** | **Kanya** | Mercury | Hasta | **Moon** | **`Sun`** | `22° 40' 00"` | `23° 20' 00"` | `40' 00"` |
| **`#121`** | **Kanya** | Mercury | Chitra | **Mars** | **`Mars`** | `23° 20' 00"` | `24° 06' 40"` | `46' 40"` |
| **`#122`** | **Kanya** | Mercury | Chitra | **Mars** | **`Rahu`** | `24° 06' 40"` | `26° 06' 40"` | `120' 00"` |
| **`#123`** | **Kanya** | Mercury | Chitra | **Mars** | **`Jupiter`** | `26° 06' 40"` | `27° 53' 20"` | `106' 40"` |
| **`#124`** | **Kanya** | Mercury | Chitra | **Mars** | **`Saturn`** | `27° 53' 20"` | `30° 00' 00"` | `126' 40"` |
| **`#125`** | **Tula** | Venus | Chitra | **Mars** | **`Mercury`** | `00° 00' 00"` | `01° 53' 20"` | `113' 20"` |
| **`#126`** | **Tula** | Venus | Chitra | **Mars** | **`Ketu`** | `01° 53' 20"` | `02° 40' 00"` | `46' 40"` |
| **`#127`** | **Tula** | Venus | Chitra | **Mars** | **`Venus`** | `02° 40' 00"` | `04° 53' 20"` | `133' 20"` |
| **`#128`** | **Tula** | Venus | Chitra | **Mars** | **`Sun`** | `04° 53' 20"` | `05° 33' 20"` | `40' 00"` |
| **`#129`** | **Tula** | Venus | Chitra | **Mars** | **`Moon`** | `05° 33' 20"` | `06° 40' 00"` | `66' 40"` |
| **`#130`** | **Tula** | Venus | Swati | **Rahu** | **`Rahu`** | `06° 40' 00"` | `08° 40' 00"` | `120' 00"` |
| **`#131`** | **Tula** | Venus | Swati | **Rahu** | **`Jupiter`** | `08° 40' 00"` | `10° 26' 40"` | `106' 40"` |
| **`#132`** | **Tula** | Venus | Swati | **Rahu** | **`Saturn`** | `10° 26' 40"` | `12° 33' 20"` | `126' 40"` |
| **`#133`** | **Tula** | Venus | Swati | **Rahu** | **`Mercury`** | `12° 33' 20"` | `14° 26' 40"` | `113' 20"` |
| **`#134`** | **Tula** | Venus | Swati | **Rahu** | **`Ketu`** | `14° 26' 40"` | `15° 13' 20"` | `46' 40"` |
| **`#135`** | **Tula** | Venus | Swati | **Rahu** | **`Venus`** | `15° 13' 20"` | `17° 26' 40"` | `133' 20"` |
| **`#136`** | **Tula** | Venus | Swati | **Rahu** | **`Sun`** | `17° 26' 40"` | `18° 06' 40"` | `40' 00"` |
| **`#137`** | **Tula** | Venus | Swati | **Rahu** | **`Moon`** | `18° 06' 40"` | `19° 13' 20"` | `66' 40"` |
| **`#138`** | **Tula** | Venus | Swati | **Rahu** | **`Mars`** | `19° 13' 20"` | `20° 00' 00"` | `46' 40"` |
| **`#139`** | **Tula** | Venus | Vishakha | **Jupiter** | **`Jupiter`** | `20° 00' 00"` | `21° 46' 40"` | `106' 40"` |
| **`#140`** | **Tula** | Venus | Vishakha | **Jupiter** | **`Saturn`** | `21° 46' 40"` | `23° 53' 20"` | `126' 40"` |
| **`#141`** | **Tula** | Venus | Vishakha | **Jupiter** | **`Mercury`** | `23° 53' 20"` | `25° 46' 40"` | `113' 20"` |
| **`#142`** | **Tula** | Venus | Vishakha | **Jupiter** | **`Ketu`** | `25° 46' 40"` | `26° 33' 20"` | `46' 40"` |
| **`#143`** | **Tula** | Venus | Vishakha | **Jupiter** | **`Venus`** | `26° 33' 20"` | `28° 46' 40"` | `133' 20"` |
| **`#144`** | **Tula** | Venus | Vishakha | **Jupiter** | **`Sun`** | `28° 46' 40"` | `29° 26' 40"` | `40' 00"` |
| **`#145`** | **Tula** | Venus | Vishakha | **Jupiter** | **`Moon`** | `29° 26' 40"` | `30° 00' 00"` | `33' 20"` |
| **`#146`** | **Vrischika** | Mars | Vishakha | **Jupiter** | **`Moon`** | `00° 00' 00"` | `00° 33' 20"` | `33' 20"` |
| **`#147`** | **Vrischika** | Mars | Vishakha | **Jupiter** | **`Mars`** | `00° 33' 20"` | `01° 20' 00"` | `46' 40"` |
| **`#148`** | **Vrischika** | Mars | Vishakha | **Jupiter** | **`Rahu`** | `01° 20' 00"` | `03° 20' 00"` | `120' 00"` |
| **`#149`** | **Vrischika** | Mars | Anuradha | **Saturn** | **`Saturn`** | `03° 20' 00"` | `05° 26' 40"` | `126' 40"` |
| **`#150`** | **Vrischika** | Mars | Anuradha | **Saturn** | **`Mercury`** | `05° 26' 40"` | `07° 20' 00"` | `113' 20"` |
| **`#151`** | **Vrischika** | Mars | Anuradha | **Saturn** | **`Ketu`** | `07° 20' 00"` | `08° 06' 40"` | `46' 40"` |
| **`#152`** | **Vrischika** | Mars | Anuradha | **Saturn** | **`Venus`** | `08° 06' 40"` | `10° 20' 00"` | `133' 20"` |
| **`#153`** | **Vrischika** | Mars | Anuradha | **Saturn** | **`Sun`** | `10° 20' 00"` | `11° 00' 00"` | `40' 00"` |
| **`#154`** | **Vrischika** | Mars | Anuradha | **Saturn** | **`Moon`** | `11° 00' 00"` | `12° 06' 40"` | `66' 40"` |
| **`#155`** | **Vrischika** | Mars | Anuradha | **Saturn** | **`Mars`** | `12° 06' 40"` | `12° 53' 20"` | `46' 40"` |
| **`#156`** | **Vrischika** | Mars | Anuradha | **Saturn** | **`Rahu`** | `12° 53' 20"` | `14° 53' 20"` | `120' 00"` |
| **`#157`** | **Vrischika** | Mars | Anuradha | **Saturn** | **`Jupiter`** | `14° 53' 20"` | `16° 40' 00"` | `106' 40"` |
| **`#158`** | **Vrischika** | Mars | Jyeshtha | **Mercury** | **`Mercury`** | `16° 40' 00"` | `18° 33' 20"` | `113' 20"` |
| **`#159`** | **Vrischika** | Mars | Jyeshtha | **Mercury** | **`Ketu`** | `18° 33' 20"` | `19° 20' 00"` | `46' 40"` |
| **`#160`** | **Vrischika** | Mars | Jyeshtha | **Mercury** | **`Venus`** | `19° 20' 00"` | `21° 33' 20"` | `133' 20"` |
| **`#161`** | **Vrischika** | Mars | Jyeshtha | **Mercury** | **`Sun`** | `21° 33' 20"` | `22° 13' 20"` | `40' 00"` |
| **`#162`** | **Vrischika** | Mars | Jyeshtha | **Mercury** | **`Moon`** | `22° 13' 20"` | `23° 20' 00"` | `66' 40"` |
| **`#163`** | **Vrischika** | Mars | Jyeshtha | **Mercury** | **`Mars`** | `23° 20' 00"` | `24° 06' 40"` | `46' 40"` |
| **`#164`** | **Vrischika** | Mars | Jyeshtha | **Mercury** | **`Rahu`** | `24° 06' 40"` | `26° 06' 40"` | `120' 00"` |
| **`#165`** | **Vrischika** | Mars | Jyeshtha | **Mercury** | **`Jupiter`** | `26° 06' 40"` | `27° 53' 20"` | `106' 40"` |
| **`#166`** | **Vrischika** | Mars | Jyeshtha | **Mercury** | **`Saturn`** | `27° 53' 20"` | `30° 00' 00"` | `126' 40"` |
| **`#167`** | **Dhanus** | Jupiter | Mula | **Ketu** | **`Ketu`** | `00° 00' 00"` | `00° 46' 40"` | `46' 40"` |
| **`#168`** | **Dhanus** | Jupiter | Mula | **Ketu** | **`Venus`** | `00° 46' 40"` | `03° 00' 00"` | `133' 20"` |
| **`#169`** | **Dhanus** | Jupiter | Mula | **Ketu** | **`Sun`** | `03° 00' 00"` | `03° 40' 00"` | `40' 00"` |
| **`#170`** | **Dhanus** | Jupiter | Mula | **Ketu** | **`Moon`** | `03° 40' 00"` | `04° 46' 40"` | `66' 40"` |
| **`#171`** | **Dhanus** | Jupiter | Mula | **Ketu** | **`Mars`** | `04° 46' 40"` | `05° 33' 20"` | `46' 40"` |
| **`#172`** | **Dhanus** | Jupiter | Mula | **Ketu** | **`Rahu`** | `05° 33' 20"` | `07° 33' 20"` | `120' 00"` |
| **`#173`** | **Dhanus** | Jupiter | Mula | **Ketu** | **`Jupiter`** | `07° 33' 20"` | `09° 20' 00"` | `106' 40"` |
| **`#174`** | **Dhanus** | Jupiter | Mula | **Ketu** | **`Saturn`** | `09° 20' 00"` | `11° 26' 40"` | `126' 40"` |
| **`#175`** | **Dhanus** | Jupiter | Mula | **Ketu** | **`Mercury`** | `11° 26' 40"` | `13° 20' 00"` | `113' 20"` |
| **`#176`** | **Dhanus** | Jupiter | Purva Ashadha | **Venus** | **`Venus`** | `13° 20' 00"` | `15° 33' 20"` | `133' 20"` |
| **`#177`** | **Dhanus** | Jupiter | Purva Ashadha | **Venus** | **`Sun`** | `15° 33' 20"` | `16° 13' 20"` | `40' 00"` |
| **`#178`** | **Dhanus** | Jupiter | Purva Ashadha | **Venus** | **`Moon`** | `16° 13' 20"` | `17° 20' 00"` | `66' 40"` |
| **`#179`** | **Dhanus** | Jupiter | Purva Ashadha | **Venus** | **`Mars`** | `17° 20' 00"` | `18° 06' 40"` | `46' 40"` |
| **`#180`** | **Dhanus** | Jupiter | Purva Ashadha | **Venus** | **`Rahu`** | `18° 06' 40"` | `20° 06' 40"` | `120' 00"` |
| **`#181`** | **Dhanus** | Jupiter | Purva Ashadha | **Venus** | **`Jupiter`** | `20° 06' 40"` | `21° 53' 20"` | `106' 40"` |
| **`#182`** | **Dhanus** | Jupiter | Purva Ashadha | **Venus** | **`Saturn`** | `21° 53' 20"` | `24° 00' 00"` | `126' 40"` |
| **`#183`** | **Dhanus** | Jupiter | Purva Ashadha | **Venus** | **`Mercury`** | `24° 00' 00"` | `25° 53' 20"` | `113' 20"` |
| **`#184`** | **Dhanus** | Jupiter | Purva Ashadha | **Venus** | **`Ketu`** | `25° 53' 20"` | `26° 40' 00"` | `46' 40"` |
| **`#185`** | **Dhanus** | Jupiter | Uttara Ashadha | **Sun** | **`Sun`** | `26° 40' 00"` | `27° 20' 00"` | `40' 00"` |
| **`#186`** | **Dhanus** | Jupiter | Uttara Ashadha | **Sun** | **`Moon`** | `27° 20' 00"` | `28° 26' 40"` | `66' 40"` |
| **`#187`** | **Dhanus** | Jupiter | Uttara Ashadha | **Sun** | **`Mars`** | `28° 26' 40"` | `29° 13' 20"` | `46' 40"` |
| **`#188`** | **Dhanus** | Jupiter | Uttara Ashadha | **Sun** | **`Rahu`** | `29° 13' 20"` | `30° 00' 00"` | `46' 40"` |
| **`#189`** | **Makara** | Saturn | Uttara Ashadha | **Sun** | **`Rahu`** | `00° 00' 00"` | `01° 13' 20"` | `73' 20"` |
| **`#190`** | **Makara** | Saturn | Uttara Ashadha | **Sun** | **`Jupiter`** | `01° 13' 20"` | `03° 00' 00"` | `106' 40"` |
| **`#191`** | **Makara** | Saturn | Uttara Ashadha | **Sun** | **`Saturn`** | `03° 00' 00"` | `05° 06' 40"` | `126' 40"` |
| **`#192`** | **Makara** | Saturn | Uttara Ashadha | **Sun** | **`Mercury`** | `05° 06' 40"` | `07° 00' 00"` | `113' 20"` |
| **`#193`** | **Makara** | Saturn | Uttara Ashadha | **Sun** | **`Ketu`** | `07° 00' 00"` | `07° 46' 40"` | `46' 40"` |
| **`#194`** | **Makara** | Saturn | Uttara Ashadha | **Sun** | **`Venus`** | `07° 46' 40"` | `10° 00' 00"` | `133' 20"` |
| **`#195`** | **Makara** | Saturn | Shravana | **Moon** | **`Moon`** | `10° 00' 00"` | `11° 06' 40"` | `66' 40"` |
| **`#196`** | **Makara** | Saturn | Shravana | **Moon** | **`Mars`** | `11° 06' 40"` | `11° 53' 20"` | `46' 40"` |
| **`#197`** | **Makara** | Saturn | Shravana | **Moon** | **`Rahu`** | `11° 53' 20"` | `13° 53' 20"` | `120' 00"` |
| **`#198`** | **Makara** | Saturn | Shravana | **Moon** | **`Jupiter`** | `13° 53' 20"` | `15° 40' 00"` | `106' 40"` |
| **`#199`** | **Makara** | Saturn | Shravana | **Moon** | **`Saturn`** | `15° 40' 00"` | `17° 46' 40"` | `126' 40"` |
| **`#200`** | **Makara** | Saturn | Shravana | **Moon** | **`Mercury`** | `17° 46' 40"` | `19° 40' 00"` | `113' 20"` |
| **`#201`** | **Makara** | Saturn | Shravana | **Moon** | **`Ketu`** | `19° 40' 00"` | `20° 26' 40"` | `46' 40"` |
| **`#202`** | **Makara** | Saturn | Shravana | **Moon** | **`Venus`** | `20° 26' 40"` | `22° 40' 00"` | `133' 20"` |
| **`#203`** | **Makara** | Saturn | Shravana | **Moon** | **`Sun`** | `22° 40' 00"` | `23° 20' 00"` | `40' 00"` |
| **`#204`** | **Makara** | Saturn | Dhanishta | **Mars** | **`Mars`** | `23° 20' 00"` | `24° 06' 40"` | `46' 40"` |
| **`#205`** | **Makara** | Saturn | Dhanishta | **Mars** | **`Rahu`** | `24° 06' 40"` | `26° 06' 40"` | `120' 00"` |
| **`#206`** | **Makara** | Saturn | Dhanishta | **Mars** | **`Jupiter`** | `26° 06' 40"` | `27° 53' 20"` | `106' 40"` |
| **`#207`** | **Makara** | Saturn | Dhanishta | **Mars** | **`Saturn`** | `27° 53' 20"` | `30° 00' 00"` | `126' 40"` |
| **`#208`** | **Kumbha** | Saturn | Dhanishta | **Mars** | **`Mercury`** | `00° 00' 00"` | `01° 53' 20"` | `113' 20"` |
| **`#209`** | **Kumbha** | Saturn | Dhanishta | **Mars** | **`Ketu`** | `01° 53' 20"` | `02° 40' 00"` | `46' 40"` |
| **`#210`** | **Kumbha** | Saturn | Dhanishta | **Mars** | **`Venus`** | `02° 40' 00"` | `04° 53' 20"` | `133' 20"` |
| **`#211`** | **Kumbha** | Saturn | Dhanishta | **Mars** | **`Sun`** | `04° 53' 20"` | `05° 33' 20"` | `40' 00"` |
| **`#212`** | **Kumbha** | Saturn | Dhanishta | **Mars** | **`Moon`** | `05° 33' 20"` | `06° 40' 00"` | `66' 40"` |
| **`#213`** | **Kumbha** | Saturn | Shatabhisha | **Rahu** | **`Rahu`** | `06° 40' 00"` | `08° 40' 00"` | `120' 00"` |
| **`#214`** | **Kumbha** | Saturn | Shatabhisha | **Rahu** | **`Jupiter`** | `08° 40' 00"` | `10° 26' 40"` | `106' 40"` |
| **`#215`** | **Kumbha** | Saturn | Shatabhisha | **Rahu** | **`Saturn`** | `10° 26' 40"` | `12° 33' 20"` | `126' 40"` |
| **`#216`** | **Kumbha** | Saturn | Shatabhisha | **Rahu** | **`Mercury`** | `12° 33' 20"` | `14° 26' 40"` | `113' 20"` |
| **`#217`** | **Kumbha** | Saturn | Shatabhisha | **Rahu** | **`Ketu`** | `14° 26' 40"` | `15° 13' 20"` | `46' 40"` |
| **`#218`** | **Kumbha** | Saturn | Shatabhisha | **Rahu** | **`Venus`** | `15° 13' 20"` | `17° 26' 40"` | `133' 20"` |
| **`#219`** | **Kumbha** | Saturn | Shatabhisha | **Rahu** | **`Sun`** | `17° 26' 40"` | `18° 06' 40"` | `40' 00"` |
| **`#220`** | **Kumbha** | Saturn | Shatabhisha | **Rahu** | **`Moon`** | `18° 06' 40"` | `19° 13' 20"` | `66' 40"` |
| **`#221`** | **Kumbha** | Saturn | Shatabhisha | **Rahu** | **`Mars`** | `19° 13' 20"` | `20° 00' 00"` | `46' 40"` |
| **`#222`** | **Kumbha** | Saturn | Purva Bhadrapada | **Jupiter** | **`Jupiter`** | `20° 00' 00"` | `21° 46' 40"` | `106' 40"` |
| **`#223`** | **Kumbha** | Saturn | Purva Bhadrapada | **Jupiter** | **`Saturn`** | `21° 46' 40"` | `23° 53' 20"` | `126' 40"` |
| **`#224`** | **Kumbha** | Saturn | Purva Bhadrapada | **Jupiter** | **`Mercury`** | `23° 53' 20"` | `25° 46' 40"` | `113' 20"` |
| **`#225`** | **Kumbha** | Saturn | Purva Bhadrapada | **Jupiter** | **`Ketu`** | `25° 46' 40"` | `26° 33' 20"` | `46' 40"` |
| **`#226`** | **Kumbha** | Saturn | Purva Bhadrapada | **Jupiter** | **`Venus`** | `26° 33' 20"` | `28° 46' 40"` | `133' 20"` |
| **`#227`** | **Kumbha** | Saturn | Purva Bhadrapada | **Jupiter** | **`Sun`** | `28° 46' 40"` | `29° 26' 40"` | `40' 00"` |
| **`#228`** | **Kumbha** | Saturn | Purva Bhadrapada | **Jupiter** | **`Moon`** | `29° 26' 40"` | `30° 00' 00"` | `33' 20"` |
| **`#229`** | **Meena** | Jupiter | Purva Bhadrapada | **Jupiter** | **`Moon`** | `00° 00' 00"` | `00° 33' 20"` | `33' 20"` |
| **`#230`** | **Meena** | Jupiter | Purva Bhadrapada | **Jupiter** | **`Mars`** | `00° 33' 20"` | `01° 20' 00"` | `46' 40"` |
| **`#231`** | **Meena** | Jupiter | Purva Bhadrapada | **Jupiter** | **`Rahu`** | `01° 20' 00"` | `03° 20' 00"` | `120' 00"` |
| **`#232`** | **Meena** | Jupiter | Uttara Bhadrapada | **Saturn** | **`Saturn`** | `03° 20' 00"` | `05° 26' 40"` | `126' 40"` |
| **`#233`** | **Meena** | Jupiter | Uttara Bhadrapada | **Saturn** | **`Mercury`** | `05° 26' 40"` | `07° 20' 00"` | `113' 20"` |
| **`#234`** | **Meena** | Jupiter | Uttara Bhadrapada | **Saturn** | **`Ketu`** | `07° 20' 00"` | `08° 06' 40"` | `46' 40"` |
| **`#235`** | **Meena** | Jupiter | Uttara Bhadrapada | **Saturn** | **`Venus`** | `08° 06' 40"` | `10° 20' 00"` | `133' 20"` |
| **`#236`** | **Meena** | Jupiter | Uttara Bhadrapada | **Saturn** | **`Sun`** | `10° 20' 00"` | `11° 00' 00"` | `40' 00"` |
| **`#237`** | **Meena** | Jupiter | Uttara Bhadrapada | **Saturn** | **`Moon`** | `11° 00' 00"` | `12° 06' 40"` | `66' 40"` |
| **`#238`** | **Meena** | Jupiter | Uttara Bhadrapada | **Saturn** | **`Mars`** | `12° 06' 40"` | `12° 53' 20"` | `46' 40"` |
| **`#239`** | **Meena** | Jupiter | Uttara Bhadrapada | **Saturn** | **`Rahu`** | `12° 53' 20"` | `14° 53' 20"` | `120' 00"` |
| **`#240`** | **Meena** | Jupiter | Uttara Bhadrapada | **Saturn** | **`Jupiter`** | `14° 53' 20"` | `16° 40' 00"` | `106' 40"` |
| **`#241`** | **Meena** | Jupiter | Revati | **Mercury** | **`Mercury`** | `16° 40' 00"` | `18° 33' 20"` | `113' 20"` |
| **`#242`** | **Meena** | Jupiter | Revati | **Mercury** | **`Ketu`** | `18° 33' 20"` | `19° 20' 00"` | `46' 40"` |
| **`#243`** | **Meena** | Jupiter | Revati | **Mercury** | **`Venus`** | `19° 20' 00"` | `21° 33' 20"` | `133' 20"` |
| **`#244`** | **Meena** | Jupiter | Revati | **Mercury** | **`Sun`** | `21° 33' 20"` | `22° 13' 20"` | `40' 00"` |
| **`#245`** | **Meena** | Jupiter | Revati | **Mercury** | **`Moon`** | `22° 13' 20"` | `23° 20' 00"` | `66' 40"` |
| **`#246`** | **Meena** | Jupiter | Revati | **Mercury** | **`Mars`** | `23° 20' 00"` | `24° 06' 40"` | `46' 40"` |
| **`#247`** | **Meena** | Jupiter | Revati | **Mercury** | **`Rahu`** | `24° 06' 40"` | `26° 06' 40"` | `120' 00"` |
| **`#248`** | **Meena** | Jupiter | Revati | **Mercury** | **`Jupiter`** | `26° 06' 40"` | `27° 53' 20"` | `106' 40"` |
| **`#249`** | **Meena** | Jupiter | Revati | **Mercury** | **`Saturn`** | `27° 53' 20"` | `30° 00' 00"` | `126' 40"` |

### Table 11B — *KP* 4-Fold Hierarchy of Planetary Significators (Manual Worksheet Rule)

| Significator Level | Priority | Classical *KP* Definition | Predictive Rule |
|---|---|---|---|
| **Level A (1st Order)** | Highest (`4x`) | Planet(s) occupying the **Nakshatra (Star)** of the Occupants of House $H$ | Strongest driver of the event when its Dasha/Bhukti/Antara runs |
| **Level B (2nd Order)** | High (`3x`) | Planet(s) directly **occupying** House $H$ in the *Placidus Bhava Chalit* chart | Delivers the house result directly unless vacated by Star tenants |
| **Level C (3rd Order)** | Moderate (`2x`) | Planet(s) occupying the **Nakshatra (Star)** of the Cusp Sign Lord of House $H$ | Activates the house promise through stellar rulership over the cusp lord |
| **Level D (4th Order)** | Baseline (`1x`) | The **Sign Lord** of the Cusp of House $H$ itself | Background significator; strong when untenanted in both house and star |
| **Cuspal Sub-Lord Gate** | **Decider** | The **Sub-Lord (`#001–#249`)** of Cusp $H$ | **The Star Lord shows the nature of the involvement; the Sub-Lord decides YES or NO** |

## Chapter 12 — Section 5 — Complete Manual Dasha Balance & Multi-System *Dasha* Compendium (*Vimshottari, Yogini, Ashtottari, & Kalachakra*)

**Classical Formula for Balance of Dasha at Birth (*Bhogyamsha*):**
- Each Nakshatra spans $13^\circ 20' = 800\text{ arcminutes}$ ($4\text{ Padas} \times 200' = 800'$).
- If the Natal Moon is at $\lambda_{\mathbb{C}}$, find its elapsed arcminutes inside the current Nakshatra ($G_{\text{elapsed}}$) and the remaining arcminutes to complete the Nakshatra ($B_{\text{rem}} = 800' - G_{\text{elapsed}}$).
$$\text{Balance of Mahadasha at Birth (Years)} = Y_{\text{Mahadasha}} \times \frac{800' - G_{\text{elapsed}}}{800'}$$

### Table 12A — 80-Row *Vimshottari Dasha* Balance Ready Reckoner (For Every `10'` of Remaining Lunar Arc `800'` down to `10'`)

| Rem. Arc (`B'`) | Deg:Min Left | Pada | Ketu (`7y`) | Venus (`20y`) | Sun (`6y`) | Moon (`10y`) | Mars (`7y`) | Rahu (`18y`) | Jupiter (`16y`) | Saturn (`19y`) | Mercury (`17y`) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **`800'`** | `13° 20'` | P1 | `07y 00m 00d` | `20y 00m 00d` | `06y 00m 00d` | `10y 00m 00d` | `07y 00m 00d` | `18y 00m 00d` | `16y 00m 00d` | `19y 00m 00d` | `17y 00m 00d` |
| **`790'`** | `13° 10'` | P1 | `06y 10m 29d` | `19y 09m 00d` | `05y 11m 03d` | `09y 10m 15d` | `06y 10m 29d` | `17y 09m 09d` | `15y 09m 18d` | `18y 09m 04d` | `16y 09m 14d` |
| **`780'`** | `13° 00'` | P1 | `06y 09m 27d` | `19y 06m 00d` | `05y 10m 06d` | `09y 09m 00d` | `06y 09m 27d` | `17y 06m 18d` | `15y 07m 06d` | `18y 06m 09d` | `16y 06m 27d` |
| **`770'`** | `12° 50'` | P1 | `06y 08m 25d` | `19y 03m 00d` | `05y 09m 09d` | `09y 07m 15d` | `06y 08m 25d` | `17y 03m 27d` | `15y 04m 24d` | `18y 03m 14d` | `16y 04m 11d` |
| **`760'`** | `12° 40'` | P1 | `06y 07m 24d` | `19y 00m 00d` | `05y 08m 12d` | `09y 06m 00d` | `06y 07m 24d` | `17y 01m 06d` | `15y 02m 12d` | `18y 00m 18d` | `16y 01m 24d` |
| **`750'`** | `12° 30'` | P1 | `06y 06m 22d` | `18y 09m 00d` | `05y 07m 15d` | `09y 04m 15d` | `06y 06m 22d` | `16y 10m 15d` | `15y 00m 00d` | `17y 09m 22d` | `15y 11m 08d` |
| **`740'`** | `12° 20'` | P1 | `06y 05m 21d` | `18y 06m 00d` | `05y 06m 18d` | `09y 03m 00d` | `06y 05m 21d` | `16y 07m 24d` | `14y 09m 18d` | `17y 06m 27d` | `15y 08m 21d` |
| **`730'`** | `12° 10'` | P1 | `06y 04m 20d` | `18y 03m 00d` | `05y 05m 21d` | `09y 01m 15d` | `06y 04m 20d` | `16y 05m 03d` | `14y 07m 06d` | `17y 04m 01d` | `15y 06m 04d` |
| **`720'`** | `12° 00'` | P1 | `06y 03m 18d` | `18y 00m 00d` | `05y 04m 24d` | `09y 00m 00d` | `06y 03m 18d` | `16y 02m 12d` | `14y 04m 24d` | `17y 01m 06d` | `15y 03m 18d` |
| **`710'`** | `11° 50'` | P1 | `06y 02m 16d` | `17y 09m 00d` | `05y 03m 27d` | `08y 10m 15d` | `06y 02m 16d` | `15y 11m 21d` | `14y 02m 12d` | `16y 10m 11d` | `15y 01m 01d` |
| **`700'`** | `11° 40'` | P1 | `06y 01m 15d` | `17y 06m 00d` | `05y 03m 00d` | `08y 09m 00d` | `06y 01m 15d` | `15y 09m 00d` | `14y 00m 00d` | `16y 07m 15d` | `14y 10m 15d` |
| **`690'`** | `11° 30'` | P1 | `06y 00m 14d` | `17y 03m 00d` | `05y 02m 03d` | `08y 07m 15d` | `06y 00m 14d` | `15y 06m 09d` | `13y 09m 18d` | `16y 04m 19d` | `14y 07m 29d` |
| **`680'`** | `11° 20'` | P1 | `05y 11m 12d` | `17y 00m 00d` | `05y 01m 06d` | `08y 06m 00d` | `05y 11m 12d` | `15y 03m 18d` | `13y 07m 06d` | `16y 01m 24d` | `14y 05m 12d` |
| **`670'`** | `11° 10'` | P1 | `05y 10m 10d` | `16y 09m 00d` | `05y 00m 09d` | `08y 04m 15d` | `05y 10m 10d` | `15y 00m 27d` | `13y 04m 24d` | `15y 10m 28d` | `14y 02m 26d` |
| **`660'`** | `11° 00'` | P1 | `05y 09m 09d` | `16y 06m 00d` | `04y 11m 12d` | `08y 03m 00d` | `05y 09m 09d` | `14y 10m 06d` | `13y 02m 12d` | `15y 08m 03d` | `14y 00m 09d` |
| **`650'`** | `10° 50'` | P1 | `05y 08m 08d` | `16y 03m 00d` | `04y 10m 15d` | `08y 01m 15d` | `05y 08m 08d` | `14y 07m 15d` | `13y 00m 00d` | `15y 05m 08d` | `13y 09m 22d` |
| **`640'`** | `10° 40'` | P1 | `05y 07m 06d` | `16y 00m 00d` | `04y 09m 18d` | `08y 00m 00d` | `05y 07m 06d` | `14y 04m 24d` | `12y 09m 18d` | `15y 02m 12d` | `13y 07m 06d` |
| **`630'`** | `10° 30'` | P1 | `05y 06m 05d` | `15y 09m 00d` | `04y 08m 21d` | `07y 10m 15d` | `05y 06m 05d` | `14y 02m 03d` | `12y 07m 06d` | `14y 11m 17d` | `13y 04m 19d` |
| **`620'`** | `10° 20'` | P1 | `05y 05m 03d` | `15y 06m 00d` | `04y 07m 24d` | `07y 09m 00d` | `05y 05m 03d` | `13y 11m 12d` | `12y 04m 24d` | `14y 08m 21d` | `13y 02m 03d` |
| **`610'`** | `10° 10'` | P1 | `05y 04m 01d` | `15y 03m 00d` | `04y 06m 27d` | `07y 07m 15d` | `05y 04m 01d` | `13y 08m 21d` | `12y 02m 12d` | `14y 05m 25d` | `12y 11m 16d` |
| **`600'`** | `10° 00'` | P2 | `05y 03m 00d` | `15y 00m 00d` | `04y 06m 00d` | `07y 06m 00d` | `05y 03m 00d` | `13y 06m 00d` | `12y 00m 00d` | `14y 03m 00d` | `12y 09m 00d` |
| **`590'`** | `09° 50'` | P2 | `05y 01m 29d` | `14y 09m 00d` | `04y 05m 03d` | `07y 04m 15d` | `05y 01m 29d` | `13y 03m 09d` | `11y 09m 18d` | `14y 00m 05d` | `12y 06m 14d` |
| **`580'`** | `09° 40'` | P2 | `05y 00m 27d` | `14y 06m 00d` | `04y 04m 06d` | `07y 03m 00d` | `05y 00m 27d` | `13y 00m 18d` | `11y 07m 06d` | `13y 09m 09d` | `12y 03m 27d` |
| **`570'`** | `09° 30'` | P2 | `04y 11m 25d` | `14y 03m 00d` | `04y 03m 09d` | `07y 01m 15d` | `04y 11m 25d` | `12y 09m 27d` | `11y 04m 24d` | `13y 06m 13d` | `12y 01m 11d` |
| **`560'`** | `09° 20'` | P2 | `04y 10m 24d` | `14y 00m 00d` | `04y 02m 12d` | `07y 00m 00d` | `04y 10m 24d` | `12y 07m 06d` | `11y 02m 12d` | `13y 03m 18d` | `11y 10m 24d` |
| **`550'`** | `09° 10'` | P2 | `04y 09m 22d` | `13y 09m 00d` | `04y 01m 15d` | `06y 10m 15d` | `04y 09m 22d` | `12y 04m 15d` | `11y 00m 00d` | `13y 00m 22d` | `11y 08m 08d` |
| **`540'`** | `09° 00'` | P2 | `04y 08m 21d` | `13y 06m 00d` | `04y 00m 18d` | `06y 09m 00d` | `04y 08m 21d` | `12y 01m 24d` | `10y 09m 18d` | `12y 09m 27d` | `11y 05m 21d` |
| **`530'`** | `08° 50'` | P2 | `04y 07m 20d` | `13y 03m 00d` | `03y 11m 21d` | `06y 07m 15d` | `04y 07m 20d` | `11y 11m 03d` | `10y 07m 06d` | `12y 07m 02d` | `11y 03m 04d` |
| **`520'`** | `08° 40'` | P2 | `04y 06m 18d` | `13y 00m 00d` | `03y 10m 24d` | `06y 06m 00d` | `04y 06m 18d` | `11y 08m 12d` | `10y 04m 24d` | `12y 04m 06d` | `11y 00m 18d` |
| **`510'`** | `08° 30'` | P2 | `04y 05m 16d` | `12y 09m 00d` | `03y 09m 27d` | `06y 04m 15d` | `04y 05m 16d` | `11y 05m 21d` | `10y 02m 12d` | `12y 01m 10d` | `10y 10m 01d` |
| **`500'`** | `08° 20'` | P2 | `04y 04m 15d` | `12y 06m 00d` | `03y 09m 00d` | `06y 03m 00d` | `04y 04m 15d` | `11y 03m 00d` | `10y 00m 00d` | `11y 10m 15d` | `10y 07m 15d` |
| **`490'`** | `08° 10'` | P2 | `04y 03m 14d` | `12y 03m 00d` | `03y 08m 03d` | `06y 01m 15d` | `04y 03m 14d` | `11y 00m 09d` | `09y 09m 18d` | `11y 07m 20d` | `10y 04m 29d` |
| **`480'`** | `08° 00'` | P2 | `04y 02m 12d` | `12y 00m 00d` | `03y 07m 06d` | `06y 00m 00d` | `04y 02m 12d` | `10y 09m 18d` | `09y 07m 06d` | `11y 04m 24d` | `10y 02m 12d` |
| **`470'`** | `07° 50'` | P2 | `04y 01m 10d` | `11y 09m 00d` | `03y 06m 09d` | `05y 10m 15d` | `04y 01m 10d` | `10y 06m 27d` | `09y 04m 24d` | `11y 01m 28d` | `09y 11m 26d` |
| **`460'`** | `07° 40'` | P2 | `04y 00m 09d` | `11y 06m 00d` | `03y 05m 12d` | `05y 09m 00d` | `04y 00m 09d` | `10y 04m 06d` | `09y 02m 12d` | `10y 11m 03d` | `09y 09m 09d` |
| **`450'`** | `07° 30'` | P2 | `03y 11m 08d` | `11y 03m 00d` | `03y 04m 15d` | `05y 07m 15d` | `03y 11m 08d` | `10y 01m 15d` | `09y 00m 00d` | `10y 08m 08d` | `09y 06m 22d` |
| **`440'`** | `07° 20'` | P2 | `03y 10m 06d` | `11y 00m 00d` | `03y 03m 18d` | `05y 06m 00d` | `03y 10m 06d` | `09y 10m 24d` | `08y 09m 18d` | `10y 05m 12d` | `09y 04m 06d` |
| **`430'`** | `07° 10'` | P2 | `03y 09m 04d` | `10y 09m 00d` | `03y 02m 21d` | `05y 04m 15d` | `03y 09m 04d` | `09y 08m 03d` | `08y 07m 06d` | `10y 02m 17d` | `09y 01m 19d` |
| **`420'`** | `07° 00'` | P2 | `03y 08m 03d` | `10y 06m 00d` | `03y 01m 24d` | `05y 03m 00d` | `03y 08m 03d` | `09y 05m 12d` | `08y 04m 24d` | `09y 11m 21d` | `08y 11m 03d` |
| **`410'`** | `06° 50'` | P2 | `03y 07m 01d` | `10y 03m 00d` | `03y 00m 27d` | `05y 01m 15d` | `03y 07m 01d` | `09y 02m 21d` | `08y 02m 12d` | `09y 08m 25d` | `08y 08m 16d` |
| **`400'`** | `06° 40'` | P3 | `03y 06m 00d` | `10y 00m 00d` | `03y 00m 00d` | `05y 00m 00d` | `03y 06m 00d` | `09y 00m 00d` | `08y 00m 00d` | `09y 06m 00d` | `08y 06m 00d` |
| **`390'`** | `06° 30'` | P3 | `03y 04m 29d` | `09y 09m 00d` | `02y 11m 03d` | `04y 10m 15d` | `03y 04m 29d` | `08y 09m 09d` | `07y 09m 18d` | `09y 03m 04d` | `08y 03m 13d` |
| **`380'`** | `06° 20'` | P3 | `03y 03m 27d` | `09y 06m 00d` | `02y 10m 06d` | `04y 09m 00d` | `03y 03m 27d` | `08y 06m 18d` | `07y 07m 06d` | `09y 00m 09d` | `08y 00m 27d` |
| **`370'`** | `06° 10'` | P3 | `03y 02m 26d` | `09y 03m 00d` | `02y 09m 09d` | `04y 07m 15d` | `03y 02m 26d` | `08y 03m 27d` | `07y 04m 24d` | `08y 09m 13d` | `07y 10m 11d` |
| **`360'`** | `06° 00'` | P3 | `03y 01m 24d` | `09y 00m 00d` | `02y 08m 12d` | `04y 06m 00d` | `03y 01m 24d` | `08y 01m 06d` | `07y 02m 12d` | `08y 06m 18d` | `07y 07m 24d` |
| **`350'`** | `05° 50'` | P3 | `03y 00m 22d` | `08y 09m 00d` | `02y 07m 15d` | `04y 04m 15d` | `03y 00m 22d` | `07y 10m 15d` | `07y 00m 00d` | `08y 03m 22d` | `07y 05m 08d` |
| **`340'`** | `05° 40'` | P3 | `02y 11m 21d` | `08y 06m 00d` | `02y 06m 18d` | `04y 03m 00d` | `02y 11m 21d` | `07y 07m 24d` | `06y 09m 18d` | `08y 00m 27d` | `07y 02m 21d` |
| **`330'`** | `05° 30'` | P3 | `02y 10m 19d` | `08y 03m 00d` | `02y 05m 21d` | `04y 01m 15d` | `02y 10m 19d` | `07y 05m 03d` | `06y 07m 06d` | `07y 10m 01d` | `07y 00m 04d` |
| **`320'`** | `05° 20'` | P3 | `02y 09m 18d` | `08y 00m 00d` | `02y 04m 24d` | `04y 00m 00d` | `02y 09m 18d` | `07y 02m 12d` | `06y 04m 24d` | `07y 07m 06d` | `06y 09m 18d` |
| **`310'`** | `05° 10'` | P3 | `02y 08m 16d` | `07y 09m 00d` | `02y 03m 27d` | `03y 10m 15d` | `02y 08m 16d` | `06y 11m 21d` | `06y 02m 12d` | `07y 04m 10d` | `06y 07m 02d` |
| **`300'`** | `05° 00'` | P3 | `02y 07m 15d` | `07y 06m 00d` | `02y 03m 00d` | `03y 09m 00d` | `02y 07m 15d` | `06y 09m 00d` | `06y 00m 00d` | `07y 01m 15d` | `06y 04m 15d` |
| **`290'`** | `04° 50'` | P3 | `02y 06m 14d` | `07y 03m 00d` | `02y 02m 03d` | `03y 07m 15d` | `02y 06m 14d` | `06y 06m 09d` | `05y 09m 18d` | `06y 10m 20d` | `06y 01m 28d` |
| **`280'`** | `04° 40'` | P3 | `02y 05m 12d` | `07y 00m 00d` | `02y 01m 06d` | `03y 06m 00d` | `02y 05m 12d` | `06y 03m 18d` | `05y 07m 06d` | `06y 07m 24d` | `05y 11m 12d` |
| **`270'`** | `04° 30'` | P3 | `02y 04m 11d` | `06y 09m 00d` | `02y 00m 09d` | `03y 04m 15d` | `02y 04m 11d` | `06y 00m 27d` | `05y 04m 24d` | `06y 04m 29d` | `05y 08m 26d` |
| **`260'`** | `04° 20'` | P3 | `02y 03m 09d` | `06y 06m 00d` | `01y 11m 12d` | `03y 03m 00d` | `02y 03m 09d` | `05y 10m 06d` | `05y 02m 12d` | `06y 02m 03d` | `05y 06m 09d` |
| **`250'`** | `04° 10'` | P3 | `02y 02m 08d` | `06y 03m 00d` | `01y 10m 15d` | `03y 01m 15d` | `02y 02m 08d` | `05y 07m 15d` | `05y 00m 00d` | `05y 11m 08d` | `05y 03m 22d` |
| **`240'`** | `04° 00'` | P3 | `02y 01m 06d` | `06y 00m 00d` | `01y 09m 18d` | `03y 00m 00d` | `02y 01m 06d` | `05y 04m 24d` | `04y 09m 18d` | `05y 08m 12d` | `05y 01m 06d` |
| **`230'`** | `03° 50'` | P3 | `02y 00m 04d` | `05y 09m 00d` | `01y 08m 21d` | `02y 10m 15d` | `02y 00m 04d` | `05y 02m 03d` | `04y 07m 06d` | `05y 05m 16d` | `04y 10m 19d` |
| **`220'`** | `03° 40'` | P3 | `01y 11m 03d` | `05y 06m 00d` | `01y 07m 24d` | `02y 09m 00d` | `01y 11m 03d` | `04y 11m 12d` | `04y 04m 24d` | `05y 02m 21d` | `04y 08m 03d` |
| **`210'`** | `03° 30'` | P3 | `01y 10m 02d` | `05y 03m 00d` | `01y 06m 27d` | `02y 07m 15d` | `01y 10m 02d` | `04y 08m 21d` | `04y 02m 12d` | `04y 11m 25d` | `04y 05m 17d` |
| **`200'`** | `03° 20'` | P4 | `01y 09m 00d` | `05y 00m 00d` | `01y 06m 00d` | `02y 06m 00d` | `01y 09m 00d` | `04y 06m 00d` | `04y 00m 00d` | `04y 09m 00d` | `04y 03m 00d` |
| **`190'`** | `03° 10'` | P4 | `01y 07m 28d` | `04y 09m 00d` | `01y 05m 03d` | `02y 04m 15d` | `01y 07m 28d` | `04y 03m 09d` | `03y 09m 18d` | `04y 06m 05d` | `04y 00m 13d` |
| **`180'`** | `03° 00'` | P4 | `01y 06m 27d` | `04y 06m 00d` | `01y 04m 06d` | `02y 03m 00d` | `01y 06m 27d` | `04y 00m 18d` | `03y 07m 06d` | `04y 03m 09d` | `03y 09m 27d` |
| **`170'`** | `02° 50'` | P4 | `01y 05m 26d` | `04y 03m 00d` | `01y 03m 09d` | `02y 01m 15d` | `01y 05m 26d` | `03y 09m 27d` | `03y 04m 24d` | `04y 00m 13d` | `03y 07m 10d` |
| **`160'`** | `02° 40'` | P4 | `01y 04m 24d` | `04y 00m 00d` | `01y 02m 12d` | `02y 00m 00d` | `01y 04m 24d` | `03y 07m 06d` | `03y 02m 12d` | `03y 09m 18d` | `03y 04m 24d` |
| **`150'`** | `02° 30'` | P4 | `01y 03m 22d` | `03y 09m 00d` | `01y 01m 15d` | `01y 10m 15d` | `01y 03m 22d` | `03y 04m 15d` | `03y 00m 00d` | `03y 06m 22d` | `03y 02m 08d` |
| **`140'`** | `02° 20'` | P4 | `01y 02m 21d` | `03y 06m 00d` | `01y 00m 18d` | `01y 09m 00d` | `01y 02m 21d` | `03y 01m 24d` | `02y 09m 18d` | `03y 03m 27d` | `02y 11m 21d` |
| **`130'`** | `02° 10'` | P4 | `01y 01m 19d` | `03y 03m 00d` | `00y 11m 21d` | `01y 07m 15d` | `01y 01m 19d` | `02y 11m 03d` | `02y 07m 06d` | `03y 01m 01d` | `02y 09m 05d` |
| **`120'`** | `02° 00'` | P4 | `01y 00m 18d` | `03y 00m 00d` | `00y 10m 24d` | `01y 06m 00d` | `01y 00m 18d` | `02y 08m 12d` | `02y 04m 24d` | `02y 10m 06d` | `02y 06m 18d` |
| **`110'`** | `01° 50'` | P4 | `00y 11m 17d` | `02y 09m 00d` | `00y 09m 27d` | `01y 04m 15d` | `00y 11m 17d` | `02y 05m 21d` | `02y 02m 12d` | `02y 07m 11d` | `02y 04m 02d` |
| **`100'`** | `01° 40'` | P4 | `00y 10m 15d` | `02y 06m 00d` | `00y 09m 00d` | `01y 03m 00d` | `00y 10m 15d` | `02y 03m 00d` | `02y 00m 00d` | `02y 04m 15d` | `02y 01m 15d` |
| **`090'`** | `01° 30'` | P4 | `00y 09m 13d` | `02y 03m 00d` | `00y 08m 03d` | `01y 01m 15d` | `00y 09m 13d` | `02y 00m 09d` | `01y 09m 18d` | `02y 01m 20d` | `01y 10m 29d` |
| **`080'`** | `01° 20'` | P4 | `00y 08m 12d` | `02y 00m 00d` | `00y 07m 06d` | `01y 00m 00d` | `00y 08m 12d` | `01y 09m 18d` | `01y 07m 06d` | `01y 10m 24d` | `01y 08m 12d` |
| **`070'`** | `01° 10'` | P4 | `00y 07m 10d` | `01y 09m 00d` | `00y 06m 09d` | `00y 10m 15d` | `00y 07m 10d` | `01y 06m 27d` | `01y 04m 24d` | `01y 07m 28d` | `01y 05m 25d` |
| **`060'`** | `01° 00'` | P4 | `00y 06m 09d` | `01y 06m 00d` | `00y 05m 12d` | `00y 09m 00d` | `00y 06m 09d` | `01y 04m 06d` | `01y 02m 12d` | `01y 05m 03d` | `01y 03m 09d` |
| **`050'`** | `00° 50'` | P4 | `00y 05m 08d` | `01y 03m 00d` | `00y 04m 15d` | `00y 07m 15d` | `00y 05m 08d` | `01y 01m 15d` | `01y 00m 00d` | `01y 02m 08d` | `01y 00m 22d` |
| **`040'`** | `00° 40'` | P4 | `00y 04m 06d` | `01y 00m 00d` | `00y 03m 18d` | `00y 06m 00d` | `00y 04m 06d` | `00y 10m 24d` | `00y 09m 18d` | `00y 11m 12d` | `00y 10m 06d` |
| **`030'`** | `00° 30'` | P4 | `00y 03m 05d` | `00y 09m 00d` | `00y 02m 21d` | `00y 04m 15d` | `00y 03m 05d` | `00y 08m 03d` | `00y 07m 06d` | `00y 08m 17d` | `00y 07m 19d` |
| **`020'`** | `00° 20'` | P4 | `00y 02m 03d` | `00y 06m 00d` | `00y 01m 24d` | `00y 03m 00d` | `00y 02m 03d` | `00y 05m 12d` | `00y 04m 24d` | `00y 05m 21d` | `00y 05m 03d` |
| **`010'`** | `00° 10'` | P4 | `00y 01m 02d` | `00y 03m 00d` | `00y 00m 27d` | `00y 01m 15d` | `00y 01m 02d` | `00y 02m 21d` | `00y 02m 12d` | `00y 02m 26d` | `00y 02m 17d` |

### Table 12B — Complete 81-Cell *Vimshottari Mahadasha × Antardasha (Bhukti)* Exact Duration Matrix (`Years-Months-Days`)

| Mahadasha \ Antardasha | Ketu (`7y`) | Venus (`20y`) | Sun (`6y`) | Moon (`10y`) | Mars (`7y`) | Rahu (`18y`) | Jupiter (`16y`) | Saturn (`19y`) | Mercury (`17y`) |
|---|---|---|---|---|---|---|---|---|---|
| **Ketu (7y)** | `0y 04m 27d` | `1y 02m 00d` | `0y 04m 06d` | `0y 07m 00d` | `0y 04m 27d` | `1y 00m 18d` | `0y 11m 06d` | `1y 01m 09d` | `0y 11m 27d` |
| **Venus (20y)** | `1y 02m 00d` | `3y 04m 00d` | `1y 00m 00d` | `1y 08m 00d` | `1y 02m 00d` | `3y 00m 00d` | `2y 08m 00d` | `3y 02m 00d` | `2y 10m 00d` |
| **Sun (6y)** | `0y 04m 06d` | `1y 00m 00d` | `0y 03m 18d` | `0y 06m 00d` | `0y 04m 06d` | `0y 10m 24d` | `0y 09m 18d` | `0y 11m 12d` | `0y 10m 06d` |
| **Moon (10y)** | `0y 07m 00d` | `1y 08m 00d` | `0y 06m 00d` | `0y 10m 00d` | `0y 07m 00d` | `1y 06m 00d` | `1y 04m 00d` | `1y 07m 00d` | `1y 05m 00d` |
| **Mars (7y)** | `0y 04m 27d` | `1y 02m 00d` | `0y 04m 06d` | `0y 07m 00d` | `0y 04m 27d` | `1y 00m 18d` | `0y 11m 06d` | `1y 01m 09d` | `0y 11m 27d` |
| **Rahu (18y)** | `1y 00m 18d` | `3y 00m 00d` | `0y 10m 24d` | `1y 06m 00d` | `1y 00m 18d` | `2y 08m 12d` | `2y 04m 24d` | `2y 10m 06d` | `2y 06m 18d` |
| **Jupiter (16y)** | `0y 11m 06d` | `2y 08m 00d` | `0y 09m 18d` | `1y 04m 00d` | `0y 11m 06d` | `2y 04m 24d` | `2y 01m 18d` | `2y 06m 12d` | `2y 03m 06d` |
| **Saturn (19y)** | `1y 01m 09d` | `3y 02m 00d` | `0y 11m 12d` | `1y 07m 00d` | `1y 01m 09d` | `2y 10m 06d` | `2y 06m 12d` | `3y 00m 03d` | `2y 08m 09d` |
| **Mercury (17y)** | `0y 11m 27d` | `2y 10m 00d` | `0y 10m 06d` | `1y 05m 00d` | `0y 11m 27d` | `2y 06m 18d` | `2y 03m 06d` | `2y 08m 09d` | `2y 04m 27d` |

### Table 12C — Complete 36-Year *Yogini Dasha* (`8 Yoginis`) & 108-Year *Ashtottari Dasha* (`8 Grahas`) Reference Tables

| Yogini # | Yogini Name | Planetary Ruler | Duration (`Years`) | Starting Nakshatra Rule $(N + 3) \bmod 8$ | Ashtottari # | Ashtottari Lord | Duration (`Years`) | Assigned 28-Nakshatra Group |
|---|---|---|---|---|---|---|---|---|
| **1** | **Mangala** | Moon | `1 Years` | Remainder `1` | **1** | **Sun** | `6 Years` | Ardra, Punarvasu, Pushya, Ashlesha (4) |
| **2** | **Pingala** | Sun | `2 Years` | Remainder `2` | **2** | **Moon** | `15 Years` | Magha, P.Phalguni, U.Phalguni (3) |
| **3** | **Dhanya** | Jupiter | `3 Years` | Remainder `3` | **3** | **Mars** | `8 Years` | Hasta, Chitra, Swati, Vishakha (4) |
| **4** | **Bhramari** | Mars | `4 Years` | Remainder `4` | **4** | **Mercury** | `17 Years` | Anuradha, Jyeshtha, Mula (3) |
| **5** | **Bhadrika** | Mercury | `5 Years` | Remainder `5` | **5** | **Saturn** | `10 Years` | P.Ashadha, U.Ashadha, Abhijit, Shravana (4) |
| **6** | **Ulka** | Saturn | `6 Years` | Remainder `6` | **6** | **Jupiter** | `19 Years` | Dhanishta, Shatabhisha, P.Bhadrapada (3) |
| **7** | **Siddha** | Venus | `7 Years` | Remainder `7` | **7** | **Rahu** | `12 Years` | U.Bhadrapada, Revati, Ashwini, Bharani (4) |
| **8** | **Sankata** | Rahu | `8 Years` | Remainder `0` | **8** | **Venus** | `21 Years` | Krittika, Rohini, Mrigashirsha (3) |

### Table 12D — Complete 108-Pada *Kalachakra Dasha* (*Savya* & *Apasavya*) Master Sequence & *Dehamsha / Jeevamsha* Table

**Sign Durations in *Kalachakra Dasha*:** Mesha/Vrishchika (`7y`), Vrishabha/Tula (`16y`), Mithuna/Kanya (`9y`), Karka (`21y`), Simha (`5y`), Dhanu/Meena (`10y`), Makara/Kumbha (`4y`).

| Cycle Group | Nakshatra Triad | Pada | *Dehamsha* (First Sign) | *Jeevamsha* (Last Sign) | Total Cycle (`Paramayus`) | 9-Sign *Kalachakra* Progression Sequence |
|---|---|---|---|---|---|---|
| **Savya 1** | Ashwini, Punarvasu, Hasta, Mula, P.Bhadra (I) | **Pada 1** | **Mesha** | **Dhanu** | `100 Years` | Mesha → Vrishabha → Mithuna → Karka → Simha → Kanya → Tula → Vrishchika → Dhanu |
| **Savya 1** | Ashwini, Punarvasu, Hasta, Mula, P.Bhadra (I) | **Pada 2** | **Makara** | **Mithuna** | `85 Years` | Makara → Kumbha → Meena → Vrishchika → Tula → Kanya → Karka → Simha → Mithuna |
| **Savya 1** | Ashwini, Punarvasu, Hasta, Mula, P.Bhadra (I) | **Pada 3** | **Vrishabha** | **Mithuna** | `83 Years` | Vrishabha → Mesha → Meena → Kumbha → Makara → Dhanu → Mesha → Vrishabha → Mithuna |
| **Savya 1** | Ashwini, Punarvasu, Hasta, Mula, P.Bhadra (I) | **Pada 4** | **Karka** | **Meena** | `86 Years` | Karka → Simha → Kanya → Tula → Vrishchika → Dhanu → Makara → Kumbha → Meena |
| **Savya 2** | Bharani, Pushya, Chitra, P.Ashadha, U.Bhadra (II) | **Pada 1** | **Vrishchika** | **Meena** | `100 Years` | Vrishchika → Tula → Kanya → Karka → Simha → Mithuna → Vrishabha → Mesha → Meena |
| **Savya 2** | Bharani, Pushya, Chitra, P.Ashadha, U.Bhadra (II) | **Pada 2** | **Kumbha** | **Kanya** | `85 Years` | Kumbha → Makara → Dhanu → Mesha → Vrishabha → Mithuna → Karka → Simha → Kanya |
| **Savya 2** | Bharani, Pushya, Chitra, P.Ashadha, U.Bhadra (II) | **Pada 3** | **Tula** | **Kanya** | `83 Years` | Tula → Vrishchika → Dhanu → Makara → Kumbha → Meena → Vrishchika → Tula → Kanya |
| **Savya 2** | Bharani, Pushya, Chitra, P.Ashadha, U.Bhadra (II) | **Pada 4** | **Karka** | **Dhanu** | `86 Years` | Karka → Simha → Mithuna → Vrishabha → Mesha → Meena → Kumbha → Makara → Dhanu |
| **Savya 3** | Krittika, Ashlesha, Swati, U.Ashadha, Revati (III) | **Pada 1** | **Dhanu** | **Karka** | `86 Years` | Dhanu → Makara → Kumbha → Meena → Mesha → Vrishabha → Mithuna → Simha → Karka |
| **Savya 3** | Krittika, Ashlesha, Swati, U.Ashadha, Revati (III) | **Pada 2** | **Kanya** | **Tula** | `83 Years` | Kanya → Tula → Vrishchika → Dhanu → Makara → Kumbha → Meena → Vrishchika → Tula |
| **Savya 3** | Krittika, Ashlesha, Swati, U.Ashadha, Revati (III) | **Pada 3** | **Kanya** | **Kumbha** | `85 Years` | Kanya → Simha → Karka → Mithuna → Vrishabha → Mesha → Dhanu → Makara → Kumbha |
| **Savya 3** | Krittika, Ashlesha, Swati, U.Ashadha, Revati (III) | **Pada 4** | **Meena** | **Vrishchika** | `100 Years` | Meena → Mesha → Vrishabha → Mithuna → Simha → Karka → Kanya → Tula → Vrishchika |
| **Apasavya 1** | Rohini, Magha, Vishakha, Shravana (I) | **Pada 1** | **Vrishchika** | **Meena** | `100 Years` | Vrishchika → Tula → Kanya → Karka → Simha → Mithuna → Vrishabha → Mesha → Meena |
| **Apasavya 1** | Rohini, Magha, Vishakha, Shravana (I) | **Pada 2** | **Kumbha** | **Kanya** | `85 Years` | Kumbha → Makara → Dhanu → Mesha → Vrishabha → Mithuna → Karka → Simha → Kanya |
| **Apasavya 1** | Rohini, Magha, Vishakha, Shravana (I) | **Pada 3** | **Tula** | **Kanya** | `83 Years` | Tula → Vrishchika → Meena → Kumbha → Makara → Dhanu → Vrishchika → Tula → Kanya |
| **Apasavya 1** | Rohini, Magha, Vishakha, Shravana (I) | **Pada 4** | **Karka** | **Dhanu** | `86 Years` | Karka → Simha → Mithuna → Vrishabha → Mesha → Meena → Kumbha → Makara → Dhanu |
| **Apasavya 2** | Mrigashirsha, P.Phalguni, Anuradha, Dhanishta (II) | **Pada 1** | **Dhanu** | **Karka** | `86 Years` | Dhanu → Makara → Kumbha → Meena → Mesha → Vrishabha → Mithuna → Simha → Karka |
| **Apasavya 2** | Mrigashirsha, P.Phalguni, Anuradha, Dhanishta (II) | **Pada 2** | **Kanya** | **Tula** | `83 Years` | Kanya → Tula → Vrishchika → Meena → Kumbha → Makara → Dhanu → Vrishchika → Tula |
| **Apasavya 2** | Mrigashirsha, P.Phalguni, Anuradha, Dhanishta (II) | **Pada 3** | **Kanya** | **Kumbha** | `85 Years` | Kanya → Simha → Karka → Mithuna → Vrishabha → Mesha → Dhanu → Makara → Kumbha |
| **Apasavya 2** | Mrigashirsha, P.Phalguni, Anuradha, Dhanishta (II) | **Pada 4** | **Meena** | **Vrishchika** | `100 Years` | Meena → Mesha → Vrishabha → Mithuna → Simha → Karka → Kanya → Tula → Vrishchika |
| **Apasavya 3** | Ardra, U.Phalguni, Jyeshtha, Shatabhisha (III) | **Pada 1** | **Meena** | **Karka** | `86 Years` | Meena → Kumbha → Makara → Dhanu → Vrishchika → Tula → Kanya → Simha → Karka |
| **Apasavya 3** | Ardra, U.Phalguni, Jyeshtha, Shatabhisha (III) | **Pada 2** | **Mithuna** | **Vrishabha** | `83 Years` | Mithuna → Vrishabha → Mesha → Dhanu → Makara → Kumbha → Meena → Mesha → Vrishabha |
| **Apasavya 3** | Ardra, U.Phalguni, Jyeshtha, Shatabhisha (III) | **Pada 3** | **Mithuna** | **Makara** | `85 Years` | Mithuna → Simha → Karka → Kanya → Tula → Vrishchika → Meena → Kumbha → Makara |
| **Apasavya 3** | Ardra, U.Phalguni, Jyeshtha, Shatabhisha (III) | **Pada 4** | **Dhanu** | **Mesha** | `100 Years` | Dhanu → Vrishchika → Tula → Kanya → Simha → Karka → Mithuna → Vrishabha → Mesha |

## Chapter 13 — Complete *Jaimini Upadesha Sutras* Manual Compendium (*Chara Karakas*, *Arudha Padas*, *Rashi Drishti*, *Argala*, & *Jaimini Ayurdaya*)

### Table 13A — Complete 144-Cell `12 × 12` *Jaimini Arudha Pada* (*Swastha* 1st/7th Exception Included) Master Lookup Matrix

**How to Read This Table:** Find the **Sign of the House ($H$)** in the left column, and the **Sign Occupied by Its Lord ($L$)** across the top row. The cell gives the **exact Arudha Pada Sign** (automatically applying the Jaimini *Swastha* rule: when the Lord is in the 1st or 7th from the house, the Arudha jumps 10 signs from the raw position).

| House Sign \ Lord Sign | **Mesha** | **Vrish** | **Mithu** | **Karka** | **Simha** | **Kanya** | **Tula** | **Vrish** | **Dhanu** | **Makar** | **Kumbh** | **Meena** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **01 Mesha** | **Makar*** | Mithu | Simha | Tula | Dhanu | Kumbh | **Makar*** | Mithu | Simha | Tula | Dhanu | Kumbh |
| **02 Vrishabha** | Meena | **Kumbh*** | Karka | Kanya | Vrish | Makar | Meena | **Kumbh*** | Karka | Kanya | Vrish | Makar |
| **03 Mithuna** | Kumbh | Mesha | **Meena*** | Simha | Tula | Dhanu | Kumbh | Mesha | **Meena*** | Simha | Tula | Dhanu |
| **04 Karka** | Makar | Meena | Vrish | **Mesha*** | Kanya | Vrish | Makar | Meena | Vrish | **Mesha*** | Kanya | Vrish |
| **05 Simha** | Dhanu | Kumbh | Mesha | Mithu | **Vrish*** | Tula | Dhanu | Kumbh | Mesha | Mithu | **Vrish*** | Tula |
| **06 Kanya** | Vrish | Makar | Meena | Vrish | Karka | **Mithu*** | Vrish | Makar | Meena | Vrish | Karka | **Mithu*** |
| **07 Tula** | **Karka*** | Dhanu | Kumbh | Mesha | Mithu | Simha | **Karka*** | Dhanu | Kumbh | Mesha | Mithu | Simha |
| **08 Vrishchika** | Kanya | **Simha*** | Makar | Meena | Vrish | Karka | Kanya | **Simha*** | Makar | Meena | Vrish | Karka |
| **09 Dhanu** | Simha | Tula | **Kanya*** | Kumbh | Mesha | Mithu | Simha | Tula | **Kanya*** | Kumbh | Mesha | Mithu |
| **10 Makara** | Karka | Kanya | Vrish | **Tula*** | Meena | Vrish | Karka | Kanya | Vrish | **Tula*** | Meena | Vrish |
| **11 Kumbha** | Mithu | Simha | Tula | Dhanu | **Vrish*** | Mesha | Mithu | Simha | Tula | Dhanu | **Vrish*** | Mesha |
| **12 Meena** | Vrish | Karka | Kanya | Vrish | Makar | **Dhanu*** | Vrish | Karka | Kanya | Vrish | Makar | **Dhanu*** |

### Table 13B — Complete `12 × 12` *Jaimini Rashi Drishti* (Sign Aspect) Matrix & *Argala / Virodhargala* Rules

| Sign (`Rashi`) | Modality | Signs Aspected by *Jaimini Rashi Drishti* (`Abhimukha` Rule) | Primary *Argala* Houses (`2nd, 4th, 11th`) | *Virodhargala* Obstruction Houses (`12th, 10th, 3rd`) | *Shoola Dasha* (`9y/sign`) | *Sthira Dasha* (`7/8/9y`) |
|---|---|---|---|---|---|---|
| **Mesha** | Chara (Movable) | **Simha**, **Vrishchika**, **Kumbha** | `2nd:` Vrishabha, `4th:` Karka, `11th:` Kumbha | `12th:` Meena, `10th:` Makara, `3rd:` Mithuna | `9 Years` | `7 Years` |
| **Vrishabha** | Sthira (Fixed) | **Karka**, **Tula**, **Makara** | `2nd:` Mithuna, `4th:` Simha, `11th:` Meena | `12th:` Mesha, `10th:` Kumbha, `3rd:` Karka | `9 Years` | `8 Years` |
| **Mithuna** | Dwiswabhava (Dual) | **Kanya**, **Dhanu**, **Meena** | `2nd:` Karka, `4th:` Kanya, `11th:` Mesha | `12th:` Vrishabha, `10th:` Meena, `3rd:` Simha | `9 Years` | `9 Years` |
| **Karka** | Chara (Movable) | **Vrishabha**, **Vrishchika**, **Kumbha** | `2nd:` Simha, `4th:` Tula, `11th:` Vrishabha | `12th:` Mithuna, `10th:` Mesha, `3rd:` Kanya | `9 Years` | `7 Years` |
| **Simha** | Sthira (Fixed) | **Mesha**, **Tula**, **Makara** | `2nd:` Kanya, `4th:` Vrishchika, `11th:` Mithuna | `12th:` Karka, `10th:` Vrishabha, `3rd:` Tula | `9 Years` | `8 Years` |
| **Kanya** | Dwiswabhava (Dual) | **Mithuna**, **Dhanu**, **Meena** | `2nd:` Tula, `4th:` Dhanu, `11th:` Karka | `12th:` Simha, `10th:` Mithuna, `3rd:` Vrishchika | `9 Years` | `9 Years` |
| **Tula** | Chara (Movable) | **Vrishabha**, **Simha**, **Kumbha** | `2nd:` Vrishchika, `4th:` Makara, `11th:` Simha | `12th:` Kanya, `10th:` Karka, `3rd:` Dhanu | `9 Years` | `7 Years` |
| **Vrishchika** | Sthira (Fixed) | **Mesha**, **Karka**, **Makara** | `2nd:` Dhanu, `4th:` Kumbha, `11th:` Kanya | `12th:` Tula, `10th:` Simha, `3rd:` Makara | `9 Years` | `8 Years` |
| **Dhanu** | Dwiswabhava (Dual) | **Mithuna**, **Kanya**, **Meena** | `2nd:` Makara, `4th:` Meena, `11th:` Tula | `12th:` Vrishchika, `10th:` Kanya, `3rd:` Kumbha | `9 Years` | `9 Years` |
| **Makara** | Chara (Movable) | **Vrishabha**, **Simha**, **Vrishchika** | `2nd:` Kumbha, `4th:` Mesha, `11th:` Vrishchika | `12th:` Dhanu, `10th:` Tula, `3rd:` Meena | `9 Years` | `7 Years` |
| **Kumbha** | Sthira (Fixed) | **Mesha**, **Karka**, **Tula** | `2nd:` Meena, `4th:` Vrishabha, `11th:` Dhanu | `12th:` Makara, `10th:` Vrishchika, `3rd:` Mesha | `9 Years` | `8 Years` |
| **Meena** | Dwiswabhava (Dual) | **Mithuna**, **Kanya**, **Dhanu** | `2nd:` Mesha, `4th:` Mithuna, `11th:` Makara | `12th:` Kumbha, `10th:` Dhanu, `3rd:` Vrishabha | `9 Years` | `9 Years` |

### Table 13C — *Jaimini Chara Karakas*, *Karakamsa* Deities (`Ishta / Palana / Dharma Devata`), & *Three-Pair Ayurdaya* Matrix

| Graha | *Jaimini Devata* (`Ishta / Dharma`) | Modality Pair 1 (`Lagna + Moon`) | Modality Pair 2 (`Lagna + Hora Lagna`) | Modality Pair 3 (`Lagna + 8th`) | Resulting *Ayurdaya* Tier (`Years`) |
|---|---|---|---|---|---|
| **Sun** | **Shiva** | Movable + Movable | Fixed + Dual | Movable + Movable | **Purnayu** (`66–100 Years`) |
| **Moon** | **Gauri** | Movable + Fixed | Movable + Dual | Fixed + Fixed | **Madhyayu** (`33–66 Years`) |
| **Mars** | **Skanda** | Fixed + Fixed | Movable + Movable | Dual + Dual | **Alpayu** (`0–33 Years`) |
| **Mercury** | **Vishnu** | Dual + Dual | Movable + Fixed | Movable + Dual | **Madhyayu** (`33–66 Years`) |
| **Jupiter** | **Sada Shiva** | Movable + Dual | Fixed + Fixed | Movable + Fixed | **Purnayu** (with Jupiter in Lagna/7th: *Kakshya Vriddhi* +1 tier) |
| **Venus** | **Lakshmi** | Fixed + Dual | Dual + Dual | Fixed + Dual | **Purnayu** (`66–100 Years`) |
| **Saturn** | **Narayana** | Malefic in 8th/Lagna | Afflicted Rudra | Saturn un-elevated | **Kakshya Hrasa** (-1 tier reduction when unassisted) |
| **Rahu / Ketu** | **Durga / Ganesha** | 8-Karaka Scheme (`Rahu` at $30^\circ - d$) | *Moksha Karaka* (`Ketu` in 12th from *Karakamsa*) | — | Ketu in 4th/8th/12th from *Karakamsa* grants final liberation |

## Chapter 14 — Complete Six-Fold *Shadbala*, 36-Row Continuous Parashari *Sphuta Drishti* Table, *Ishta/Kashta Phala*, & *Bhava Bala*

### Table 14A — Complete Six-Fold *Shadbala* Formulas, Deep Exaltation Points, *Naisargika Bala*, & Minimum Required *Rupas*

| Graha | Deep Exaltation (`Uchcha` = `60v`) | Deep Debilitation (`Neecha` = `0v`) | Zero *Dig Bala* House | Max *Dig Bala* House (`60v`) | *Naisargika Bala* (`Virupas`) | *Kala Bala* Day/Night Ruler | Min Required *Shadbala* (`Virupas` / `Rupas`) |
|---|---|---|---|---|---|---|---|
| **Sun** | `10° Mesha (010°)` | `10° Tula (190°)` | 4th Cusp (`IC`) | 10th Cusp (`MC`) | `60.00v` | Day (`Diwa`) +60v | **`390v` (`6.50 Rupas`)** |
| **Moon** | `03° Vrishabha (033°)` | `03° Vrishchika (213°)` | 10th Cusp (`MC`) | 4th Cusp (`IC`) | `51.43v` | Night (`Ratri`) +60v | **`360v` (`6.00 Rupas`)** |
| **Mars** | `28° Makara (298°)` | `28° Karka (118°)` | 4th Cusp (`IC`) | 10th Cusp (`MC`) | `17.14v` | Night (`Ratri`) +60v | **`300v` (`5.00 Rupas`)** |
| **Mercury** | `15° Kanya (165°)` | `15° Meena (345°)` | 7th Cusp (`Desc`) | 1st Cusp (`Lagna`) | `25.71v` | Always (`Sarvada`) +60v | **`420v` (`7.00 Rupas`)** |
| **Jupiter** | `05° Karka (095°)` | `05° Makara (275°)` | 7th Cusp (`Desc`) | 1st Cusp (`Lagna`) | `34.29v` | Day (`Diwa`) +60v | **`390v` (`6.50 Rupas`)** |
| **Venus** | `27° Meena (357°)` | `27° Kanya (177°)` | 10th Cusp (`MC`) | 4th Cusp (`IC`) | `42.86v` | Day (`Diwa`) +60v | **`330v` (`5.50 Rupas`)** |
| **Saturn** | `20° Tula (200°)` | `20° Mesha (020°)` | 1st Cusp (`Lagna`) | 7th Cusp (`Desc`) | `08.57v` | Night (`Ratri`) +60v | **`300v` (`5.00 Rupas`)** |

### Table 14B — Complete 36-Row Continuous Parashari *Sphuta Drishti* (Aspectual Strength in *Virupas* `0v–60v`) Lookup Table

**Classical Piecewise Formula (*Brihat Parashara Hora Shastra*):** Let $\Delta = (\lambda_{\text{Target}} - \lambda_{\text{Aspecting}}) \bmod 360^\circ$. Base *Drishti* is `0v` for $0^\circ..30^\circ$ and $300^\circ..360^\circ$; rises from $30^\circ..60^\circ$ (`(Δ-30)/2`); rises from $60^\circ..90^\circ$ (`(Δ-60)+15`); drops from $90^\circ..120^\circ$ (`45-(Δ-90)/2`); drops from $120^\circ..150^\circ$ (`30-(Δ-120)`); rises sharply from $150^\circ..180^\circ$ (`2*(Δ-150)` peaking at `60v` at $180^\circ$); and decreases linearly from $180^\circ..300^\circ$ (`(300-Δ)/2`). **Special Vishesha Drishti:** Mars gets `60v` across $90^\circ..120^\circ$ & $210^\circ..240^\circ$; Jupiter gets `60v` across $120^\circ..150^\circ$ & $240^\circ..270^\circ$; Saturn gets `60v` across $60^\circ..90^\circ$ & $270^\circ..300^\circ$.

| Separation $\Delta$ | House Span | Standard (*Sun, Moon, Mer, Ven*) | Mars (*4th & 8th Vishesha*) | Jupiter (*5th & 9th Vishesha*) | Saturn (*3rd & 10th Vishesha*) |
|---|---|---|---|---|---|
| **`000°`** | House 01 | `00.00v` | **`00.00v`** | **`00.00v`** | **`00.00v`** |
| **`010°`** | House 01 | `00.00v` | **`00.00v`** | **`00.00v`** | **`00.00v`** |
| **`020°`** | House 01 | `00.00v` | **`00.00v`** | **`00.00v`** | **`00.00v`** |
| **`030°`** | House 02 | `00.00v` | **`00.00v`** | **`00.00v`** | **`00.00v`** |
| **`040°`** | House 02 | `05.00v` | **`20.00v`** | **`35.00v`** | **`50.00v`** |
| **`050°`** | House 02 | `10.00v` | **`25.00v`** | **`40.00v`** | **`55.00v`** |
| **`060°`** | House 03 | `15.00v` | **`30.00v`** | **`45.00v`** | **`60.00v`** |
| **`070°`** | House 03 | `25.00v` | **`40.00v`** | **`55.00v`** | **`60.00v`** |
| **`080°`** | House 03 | `35.00v` | **`50.00v`** | **`60.00v`** | **`60.00v`** |
| **`090°`** | House 04 | `45.00v` | **`60.00v`** | **`60.00v`** | **`60.00v`** |
| **`100°`** | House 04 | `40.00v` | **`60.00v`** | **`60.00v`** | **`60.00v`** |
| **`110°`** | House 04 | `35.00v` | **`60.00v`** | **`60.00v`** | **`60.00v`** |
| **`120°`** | House 05 | `30.00v` | **`45.00v`** | **`60.00v`** | **`60.00v`** |
| **`130°`** | House 05 | `20.00v` | **`35.00v`** | **`60.00v`** | **`60.00v`** |
| **`140°`** | House 05 | `10.00v` | **`25.00v`** | **`60.00v`** | **`55.00v`** |
| **`150°`** | House 06 | `00.00v` | **`00.00v`** | **`00.00v`** | **`00.00v`** |
| **`160°`** | House 06 | `20.00v` | **`35.00v`** | **`50.00v`** | **`60.00v`** |
| **`170°`** | House 06 | `40.00v` | **`55.00v`** | **`60.00v`** | **`60.00v`** |
| **`180°`** | House 07 | `60.00v` | **`60.00v`** | **`60.00v`** | **`60.00v`** |
| **`190°`** | House 07 | `55.00v` | **`60.00v`** | **`60.00v`** | **`60.00v`** |
| **`200°`** | House 07 | `50.00v` | **`60.00v`** | **`60.00v`** | **`60.00v`** |
| **`210°`** | House 08 | `45.00v` | **`60.00v`** | **`60.00v`** | **`60.00v`** |
| **`220°`** | House 08 | `40.00v` | **`60.00v`** | **`60.00v`** | **`60.00v`** |
| **`230°`** | House 08 | `35.00v` | **`60.00v`** | **`60.00v`** | **`60.00v`** |
| **`240°`** | House 09 | `30.00v` | **`45.00v`** | **`60.00v`** | **`60.00v`** |
| **`250°`** | House 09 | `25.00v` | **`40.00v`** | **`60.00v`** | **`60.00v`** |
| **`260°`** | House 09 | `20.00v` | **`35.00v`** | **`60.00v`** | **`60.00v`** |
| **`270°`** | House 10 | `15.00v` | **`30.00v`** | **`45.00v`** | **`60.00v`** |
| **`280°`** | House 10 | `10.00v` | **`25.00v`** | **`40.00v`** | **`60.00v`** |
| **`290°`** | House 10 | `05.00v` | **`20.00v`** | **`35.00v`** | **`60.00v`** |
| **`300°`** | House 11 | `00.00v` | **`00.00v`** | **`00.00v`** | **`00.00v`** |
| **`310°`** | House 11 | `00.00v` | **`00.00v`** | **`00.00v`** | **`00.00v`** |
| **`320°`** | House 11 | `00.00v` | **`00.00v`** | **`00.00v`** | **`00.00v`** |
| **`330°`** | House 12 | `00.00v` | **`00.00v`** | **`00.00v`** | **`00.00v`** |
| **`340°`** | House 12 | `00.00v` | **`00.00v`** | **`00.00v`** | **`00.00v`** |
| **`350°`** | House 12 | `00.00v` | **`00.00v`** | **`00.00v`** | **`00.00v`** |

## Chapter 15 — Complete *Ashtakavarga* (337-Bindu BAV/SAV), *Shodhana* Reductions, *Pinda* Multipliers, & 8-Lord *Kakshya* (`3°45'`) Transit Table

### Table 15A — Complete 337-Bindu *Bhinna Ashtakavarga* (`BAV`) Benefic House Contribution Matrix (*Brihat Parashara Hora Shastra*)

| BAV Planet | Total Bindus | From Sun | From Moon | From Mars | From Mercury | From Jupiter | From Venus | From Saturn | From Lagna |
|---|---|---|---|---|---|---|---|---|---|
| **Sun** | **`48`** | `1,2,4,7,8,9,10,11` (8) | `3,6,10,11` (4) | `1,2,4,7,8,9,10,11` (8) | `3,5,6,9,10,11,12` (7) | `5,6,9,11` (4) | `6,7,12` (3) | `1,2,4,7,8,9,10,11` (8) | `3,4,6,10,11,12` (6) |
| **Moon** | **`49`** | `3,6,7,8,10,11` (6) | `1,3,6,7,10,11` (6) | `2,3,5,6,9,10,11` (7) | `1,3,4,5,7,8,10,11` (8) | `1,4,7,8,10,11,12` (7) | `3,4,5,7,9,10,11` (7) | `3,5,6,11` (4) | `3,6,10,11` (4) |
| **Mars** | **`39`** | `3,5,6,10,11` (5) | `3,6,11` (3) | `1,2,4,7,8,10,11` (7) | `3,5,6,11` (4) | `6,10,11,12` (4) | `6,8,11,12` (4) | `1,4,7,8,9,10,11` (7) | `1,3,6,10,11` (5) |
| **Mercury** | **`54`** | `5,6,9,11,12` (5) | `2,4,6,8,10,11` (6) | `1,2,4,7,8,9,10,11` (8) | `1,3,5,6,9,10,11,12` (8) | `6,8,11,12` (4) | `1,2,3,4,5,8,9,11` (8) | `1,2,4,7,8,9,10,11` (8) | `1,2,4,6,8,10,11` (7) |
| **Jupiter** | **`56`** | `1,2,3,4,7,8,9,10,11` (9) | `2,5,7,9,11` (5) | `1,2,4,7,8,10,11` (7) | `1,2,4,5,6,9,10,11` (8) | `1,2,3,4,7,8,10,11` (8) | `2,5,6,9,10,11` (6) | `3,5,6,12` (4) | `1,2,4,5,6,7,9,10,11` (9) |
| **Venus** | **`52`** | `8,11,12` (3) | `1,2,3,4,5,8,9,11,12` (9) | `3,5,6,9,11,12` (6) | `3,5,6,9,11` (5) | `5,8,9,10,11` (5) | `1,2,3,4,5,8,9,10,11` (9) | `3,4,5,8,9,10,11` (7) | `1,2,3,4,5,8,9,11` (8) |
| **Saturn** | **`39`** | `1,2,4,7,8,10,11` (7) | `3,6,11` (3) | `3,5,6,10,11,12` (6) | `6,8,9,10,11,12` (6) | `5,6,11,12` (4) | `6,11,12` (3) | `3,5,6,11` (4) | `1,3,4,6,10,11` (6) |

### Table 15B — *Rashi Gunakara*, *Graha Gunakara* (*Shodhya Pinda* Multipliers), & 8-Lord *Kakshya* (`3° 45'`) Sub-Sign Transit Grid

| Kakshya # | Degree Span in Sign | Arcminutes | Ruling *Kakshya* Lord | Speed Order | *Rashi Gunakara* (Signs 1–12) | *Graha Gunakara* (Planets) |
|---|---|---|---|---|---|---|
| **Kakshya 1** | `00° 00' – 03° 45'` | `0'–225'` | **Saturn** | Orbit #1 | Mesha `7`, Vrishabha `10` | Sun `5` |
| **Kakshya 2** | `03° 45' – 07° 30'` | `225'–450'` | **Jupiter** | Orbit #2 | Mithuna `8`, Karka `4` | Moon `5` |
| **Kakshya 3** | `07° 30' – 11° 15'` | `450'–675'` | **Mars** | Orbit #3 | Simha `10`, Kanya `5` | Mars `8` |
| **Kakshya 4** | `11° 15' – 15° 00'` | `675'–900'` | **Sun** | Orbit #4 | Tula `7`, Vrishchika `8` | Mercury `5` |
| **Kakshya 5** | `15° 00' – 18° 45'` | `900'–1125'` | **Venus** | Orbit #5 | Dhanu `9`, Makara `5` | Jupiter `10` |
| **Kakshya 6** | `18° 45' – 22° 30'` | `1125'–1350'` | **Mercury** | Orbit #6 | Kumbha `11`, Meena `12` | Venus `7` |
| **Kakshya 7** | `22° 30' – 26° 15'` | `1350'–1575'` | **Moon** | Orbit #7 | Trikona Reduction: Subtract minimum of `(1,5,9), (2,6,10), (3,7,11), (4,8,12)` | Saturn `5` |
| **Kakshya 8** | `26° 15' – 30° 00'` | `1575'–1800'` | **Lagna** | Orbit #8 | Ekadhipatya Reduction: Reduce dual-lord signs (`Mesha/Vrishchika`, `Vrishabha/Tula`, etc.) | Shodhya Pinda = Rashi Pinda + Graha Pinda |

## Chapter 16 — Complete Classical Mathematical Longevity (*Ayurdaya* — *Pindayu, Nisargayu, & Amsayu*) Manual Calculation Compendium

### Table 16A — Maximum *Pindayu* & *Nisargayu* Planetary Years & The Four Classical Reductions (*Harana*)

| Graha | Deep Exaltation | *Pindayu* Max Years | *Nisargayu* Max Years | *Astangata Harana* (Combustion Reduction) | *Shatru Kshetra Harana* (Enemy Sign Reduction) | *Chakrapata Harana* (Visible Hemisphere `H12..H7` Reduction) |
|---|---|---|---|---|---|---|
| **Sun** | ``10° Mesha (010°)`` | **`19 Years`** | **`20 Years`** | N/A (Luminary) | Lose **`1/3` (`33.3%`)** in Enemy Sign | `H12:` Lose `100%` (Malefic) / `50%` (Benefic) |
| **Moon** | ``03° Vrishabha (033°)`` | **`25 Years`** | **`1 Years`** | Lose **`1/2` (`50%`)** when combust | Lose **`1/3` (`33.3%`)** in Enemy Sign | `H11:` Lose `50%` (Malefic) / `25%` (Benefic) |
| **Mars** | ``28° Makara (298°)`` | **`15 Years`** | **`2 Years`** | Lose **`1/2` (`50%`)** when combust | Lose **`1/3` (`33.3%`)** in Enemy Sign (Exempt if Retrograde) | `H10:` Lose `1/3` (Malefic) / `1/6` (Benefic) |
| **Mercury** | ``15° Kanya (165°)`` | **`12 Years`** | **`9 Years`** | Lose **`1/2` (`50%`)** when combust | Lose **`1/3` (`33.3%`)** in Enemy Sign (Exempt if Retrograde) | `H9:` Lose `1/4` (Malefic) / `1/8` (Benefic) |
| **Jupiter** | ``05° Karka (095°)`` | **`15 Years`** | **`18 Years`** | Lose **`1/2` (`50%`)** when combust | Lose **`1/3` (`33.3%`)** in Enemy Sign (Exempt if Retrograde) | `H8:` Lose `1/5` (Malefic) / `1/10` (Benefic) |
| **Venus** | ``27° Meena (357°)`` | **`21 Years`** | **`20 Years`** | **Exempt** (Saturn & Venus never lose years by combustion) | Lose **`1/3` (`33.3%`)** in Enemy Sign (Exempt if Retrograde) | `H7:` Lose `1/6` (Malefic) / `1/12` (Benefic) |
| **Saturn** | ``20° Tula (200°)`` | **`20 Years`** | **`50 Years`** | **Exempt** (Saturn & Venus never lose years by combustion) | Lose **`1/3` (`33.3%`)** in Enemy Sign (Exempt if Retrograde) | **Amsayu Rule:** Total Elapsed Arcminutes $\div 200' \bmod 12 =$ Base Years (multiplied by $2\times$ or $3\times$ in Own/Exalted Rashi or D9) |

## Chapter 17 — Complete *Tajika Varshphal* (Annual Solar Return) Manual Compendium, 100-Year *Dhruvanka* Table, *Hadda* Bounds, & All 36 *Tajika Sahams*

### Table 17A — 100-Year *Tajika Varsha Pravesha Dhruvanka* (Constant Sidereal Solar Return Time Advance Table `Ages 1 to 100`)

**How to Find Any Annual Solar Return (*Varsha Pravesha*) Epoch by Hand:** 1 Sidereal Solar Year = `365d 06h 09m 09.8s` (`1d 06h 09m 09.8s` mod 7 weekdays). Add the **Cumulative Weekday + Hours:Minutes:Seconds Advance (*Dhruvanka*)** for the native's completed age to the Natal Birth Weekday and Time (then refine by final solar arcminutes using daily solar motion):

| Completed Age | Weekday & Time Advance (`d hh:mm:ss`) | Completed Age | Weekday & Time Advance (`d hh:mm:ss`) | Completed Age | Weekday & Time Advance (`d hh:mm:ss`) | Completed Age | Weekday & Time Advance (`d hh:mm:ss`) |
|---|---|---|---|---|---|---|---|
| **Age 001** | `+1d 06:09:10` | **Age 026** | `+4d 15:58:14` | **Age 051** | `+1d 01:47:18` | **Age 076** | `+4d 11:36:22` |
| **Age 002** | `+2d 12:18:20` | **Age 027** | `+5d 22:07:24` | **Age 052** | `+2d 07:56:28` | **Age 077** | `+5d 17:45:32` |
| **Age 003** | `+3d 18:27:29` | **Age 028** | `+0d 04:16:33` | **Age 053** | `+3d 14:05:37` | **Age 078** | `+6d 23:54:42` |
| **Age 004** | `+5d 00:36:39` | **Age 029** | `+1d 10:25:43` | **Age 054** | `+4d 20:14:47` | **Age 079** | `+1d 06:03:51` |
| **Age 005** | `+6d 06:45:49` | **Age 030** | `+2d 16:34:53` | **Age 055** | `+6d 02:23:57` | **Age 080** | `+2d 12:13:01` |
| **Age 006** | `+0d 12:54:59` | **Age 031** | `+3d 22:44:03` | **Age 056** | `+0d 08:33:07` | **Age 081** | `+3d 18:22:11` |
| **Age 007** | `+1d 19:04:08` | **Age 032** | `+5d 04:53:12` | **Age 057** | `+1d 14:42:17` | **Age 082** | `+5d 00:31:21` |
| **Age 008** | `+3d 01:13:18` | **Age 033** | `+6d 11:02:22` | **Age 058** | `+2d 20:51:26` | **Age 083** | `+6d 06:40:30` |
| **Age 009** | `+4d 07:22:28` | **Age 034** | `+0d 17:11:32` | **Age 059** | `+4d 03:00:36` | **Age 084** | `+0d 12:49:40` |
| **Age 010** | `+5d 13:31:38` | **Age 035** | `+1d 23:20:42` | **Age 060** | `+5d 09:09:46` | **Age 085** | `+1d 18:58:50` |
| **Age 011** | `+6d 19:40:47` | **Age 036** | `+3d 05:29:51` | **Age 061** | `+6d 15:18:56` | **Age 086** | `+3d 01:08:00` |
| **Age 012** | `+1d 01:49:57` | **Age 037** | `+4d 11:39:01` | **Age 062** | `+0d 21:28:05` | **Age 087** | `+4d 07:17:09` |
| **Age 013** | `+2d 07:59:07` | **Age 038** | `+5d 17:48:11` | **Age 063** | `+2d 03:37:15` | **Age 088** | `+5d 13:26:19` |
| **Age 014** | `+3d 14:08:17` | **Age 039** | `+6d 23:57:21` | **Age 064** | `+3d 09:46:25` | **Age 089** | `+6d 19:35:29` |
| **Age 015** | `+4d 20:17:26` | **Age 040** | `+1d 06:06:31` | **Age 065** | `+4d 15:55:35` | **Age 090** | `+1d 01:44:39` |
| **Age 016** | `+6d 02:26:36` | **Age 041** | `+2d 12:15:40` | **Age 066** | `+5d 22:04:44` | **Age 091** | `+2d 07:53:48` |
| **Age 017** | `+0d 08:35:46` | **Age 042** | `+3d 18:24:50` | **Age 067** | `+0d 04:13:54` | **Age 092** | `+3d 14:02:58` |
| **Age 018** | `+1d 14:44:56` | **Age 043** | `+5d 00:34:00` | **Age 068** | `+1d 10:23:04` | **Age 093** | `+4d 20:12:08` |
| **Age 019** | `+2d 20:54:06` | **Age 044** | `+6d 06:43:10` | **Age 069** | `+2d 16:32:14` | **Age 094** | `+6d 02:21:18` |
| **Age 020** | `+4d 03:03:15` | **Age 045** | `+0d 12:52:19` | **Age 070** | `+3d 22:41:23` | **Age 095** | `+0d 08:30:28` |
| **Age 021** | `+5d 09:12:25` | **Age 046** | `+1d 19:01:29` | **Age 071** | `+5d 04:50:33` | **Age 096** | `+1d 14:39:37` |
| **Age 022** | `+6d 15:21:35` | **Age 047** | `+3d 01:10:39` | **Age 072** | `+6d 10:59:43` | **Age 097** | `+2d 20:48:47` |
| **Age 023** | `+0d 21:30:45` | **Age 048** | `+4d 07:19:49` | **Age 073** | `+0d 17:08:53` | **Age 098** | `+4d 02:57:57` |
| **Age 024** | `+2d 03:39:54` | **Age 049** | `+5d 13:28:58` | **Age 074** | `+1d 23:18:03` | **Age 099** | `+5d 09:07:07` |
| **Age 025** | `+3d 09:49:04` | **Age 050** | `+6d 19:38:08` | **Age 075** | `+3d 05:27:12` | **Age 100** | `+6d 15:16:16` |

### Table 17B — Complete 12-Sign *Tajika Hadda* (Egyptian Terms) & *Tri-Rashi Pati* Table (*Tajika Neelakanthi*)

| Rashi (Sign) | Hadda 1 | Hadda 2 | Hadda 3 | Hadda 4 | Hadda 5 | *Tri-Rashi Pati* (Day / Night) |
|---|---|---|---|---|---|---|
| **Mesha** | `00°–06°` **Jupiter** | `06°–12°` **Venus** | `12°–20°` **Mercury** | `20°–25°` **Mars** | `25°–30°` **Saturn** | **Sun / Jupiter** |
| **Vrishabha** | `00°–08°` **Venus** | `08°–14°` **Mercury** | `14°–22°` **Jupiter** | `22°–27°` **Saturn** | `27°–30°` **Mars** | **Venus / Moon** |
| **Mithuna** | `00°–06°` **Mercury** | `06°–12°` **Jupiter** | `12°–17°` **Venus** | `17°–24°` **Mars** | `24°–30°` **Saturn** | **Saturn / Mercury** |
| **Karka** | `00°–07°` **Mars** | `07°–13°` **Venus** | `13°–19°` **Mercury** | `19°–26°` **Jupiter** | `26°–30°` **Saturn** | **Venus / Mars** |
| **Simha** | `00°–06°` **Jupiter** | `06°–11°` **Venus** | `11°–18°` **Saturn** | `18°–24°` **Mercury** | `24°–30°` **Mars** | **Jupiter / Sun** |
| **Kanya** | `00°–07°` **Mercury** | `07°–17°` **Venus** | `17°–21°` **Jupiter** | `21°–28°` **Mars** | `28°–30°` **Saturn** | **Moon / Venus** |
| **Tula** | `00°–06°` **Saturn** | `06°–14°` **Mercury** | `14°–21°` **Jupiter** | `21°–28°` **Venus** | `28°–30°` **Mars** | **Mercury / Saturn** |
| **Vrishchika** | `00°–07°` **Mars** | `07°–11°` **Venus** | `11°–19°` **Mercury** | `19°–24°` **Jupiter** | `24°–30°` **Saturn** | **Mars / Venus** |
| **Dhanu** | `00°–12°` **Jupiter** | `12°–17°` **Venus** | `17°–21°` **Mercury** | `21°–26°` **Saturn** | `26°–30°` **Mars** | **Saturn / Saturn** |
| **Makara** | `00°–07°` **Mercury** | `07°–14°` **Jupiter** | `14°–22°` **Venus** | `22°–26°` **Saturn** | `26°–30°` **Mars** | **Mars / Mars** |
| **Kumbha** | `00°–07°` **Mercury** | `07°–13°` **Venus** | `13°–20°` **Jupiter** | `20°–25°` **Mars** | `25°–30°` **Saturn** | **Jupiter / Jupiter** |
| **Meena** | `00°–12°` **Venus** | `12°–16°` **Jupiter** | `16°–19°` **Mercury** | `19°–28°` **Mars** | `28°–30°` **Saturn** | **Moon / Moon** |

### Table 17C — Complete Catalog of All 36 Classical *Tajika Sahams* (Arabic Lots — Day & Night Manual Formulas)

**Universal Saham Rule (*Tajika Neelakanthi*):** Compute $\lambda_{\text{Saham}} = (A - B + C) \bmod 360^\circ$. Whenever the Ascendant ($C$) is **not** geometrically situated on the zodiacal arc moving forward from $B$ to $A$, **add $+30^\circ$ ($1\text{ Sign}$)** to the result.

| # | Classical *Saham* Name | Life Domain / Signification | Day Birth Formula ($A - B + C$) | Night Birth Formula ($A - B + C$) |
|---|---|---|---|---|
| **`#01`** | **Punya Saham (Fortune)** | Overall fortune, dharma, prosperity & grace | `Moon - Sun + Lagna` | `Sun - Moon + Lagna` |
| **`#02`** | **Vidya Saham (Learning)** | Education, scholarship, wisdom & intellect | `Sun - Moon + Lagna` | `Moon - Sun + Lagna` |
| **`#03`** | **Yashas Saham (Fame)** | Fame, public honour, reputation & prestige | `Jupiter - Punya + Lagna` | `Punya - Jupiter + Lagna` |
| **`#04`** | **Mitra Saham (Friends)** | Alliances, patrons, benefactors & friendships | `Jupiter - Punya + Venus` | `Punya - Jupiter + Venus` |
| **`#05`** | **Mahatmya Saham (Greatness)** | Eminence, nobility, high rank & grandeur | `Punya - Mars + Lagna` | `Mars - Punya + Lagna` |
| **`#06`** | **Asha Saham (Desires)** | Fulfilment of hopes, wishes & long-term ambitions | `Saturn - Venus + Lagna` | `Venus - Saturn + Lagna` |
| **`#07`** | **Samarthya Saham (Enterprise)** | Capability, courage, stamina & executive power | `Mars - Lagna_Lord + Lagna` | `Lagna_Lord - Mars + Lagna` |
| **`#08`** | **Bhratri Saham (Brothers)** | Siblings, co-born, valour & teamwork | `Jupiter - Saturn + Lagna` | `Jupiter - Saturn + Lagna (Same)` |
| **`#09`** | **Gaurava Saham (Respect)** | Social standing, dignity & respect from elders | `Jupiter - Moon + Sun` | `Moon - Jupiter + Sun` |
| **`#10`** | **Pitri Saham (Father)** | Father's health, fortune, authority & blessings | `Saturn - Sun + Lagna` | `Sun - Saturn + Lagna` |
| **`#11`** | **Matri Saham (Mother)** | Mother's health, domestic peace & nourishment | `Moon - Venus + Lagna` | `Venus - Moon + Lagna` |
| **`#12`** | **Putra Saham (Children)** | Progeny, childbirth, creativity & disciples | `Jupiter - Moon + Lagna` | `Moon - Jupiter + Lagna` |
| **`#13`** | **Jeeva Saham (Vitality)** | Life force, longevity, recovery & bodily vigour | `Saturn - Jupiter + Lagna` | `Jupiter - Saturn + Lagna` |
| **`#14`** | **Karma Saham (Action/Deeds)** | Profession, career execution & righteous action | `Mars - Mercury + Lagna` | `Mercury - Mars + Lagna` |
| **`#15`** | **Roga Saham (Disease)** | Illness, vulnerability, diagnosis & convalescence | `Lagna - Moon + Lagna` | `Lagna - Moon + Lagna (Same)` |
| **`#16`** | **Kali Saham (Strife/Great Effort)** | Sudden upheaval, crisis or heroic breakthrough | `Jupiter - Mars + Lagna` | `Mars - Jupiter + Lagna` |
| **`#17`** | **Sastra Saham (Scriptures)** | Mastery of sacred texts, sciences & philosophy | `Jupiter - Saturn + Mercury` | `Saturn - Jupiter + Mercury` |
| **`#18`** | **Bandhu Saham (Relatives)** | Kinsmen, extended family & community support | `Mercury - Moon + Lagna` | `Moon - Mercury + Lagna` |
| **`#19`** | **Mrityu Saham (Death/Danger)** | Mortal danger, severe crisis & transformation | `8th Cusp - Moon + Lagna` | `8th Cusp - Moon + Lagna (Same)` |
| **`#20`** | **Paradesa Saham (Foreign Travel)** | Foreign residence, long journeys & pilgrimage | `9th Cusp - 9th Lord + Lagna` | `9th Cusp - 9th Lord + Lagna (Same)` |
| **`#21`** | **Artha / Dhana Saham (Wealth)** | Liquid wealth, treasury, income & financial gain | `2nd Cusp - 2nd Lord + Lagna` | `2nd Cusp - 2nd Lord + Lagna (Same)` |
| **`#22`** | **Paradara Saham (Illicit Liaison)** | Romantic entanglement & boundary testing | `Venus - Sun + Lagna` | `Venus - Sun + Lagna (Same)` |
| **`#23`** | **Vanik Saham (Commerce/Trade)** | Business, merchandising, trading & negotiation | `Moon - Mercury + Lagna` | `Mercury - Moon + Lagna` |
| **`#24`** | **Karyasiddhi Saham (Success)** | Completion of undertakings & victory in projects | `Saturn - Sun + Sun_Sign_Lord` | `Saturn - Moon + Moon_Sign_Lord` |
| **`#25`** | **Vivaha Saham (Marriage)** | Marriage, partnership, wedding & spousal bond | `Venus - Saturn + Lagna` | `Venus - Saturn + Lagna (Same)` |
| **`#26`** | **Santapa Saham (Grief/Sorrow)** | Mental anguish, bereavement & emotional trials | `Saturn - Moon + 6th Cusp` | `Saturn - Moon + 6th Cusp (Same)` |
| **`#27`** | **Shraddha Saham (Faith/Devotion)** | Religious devotion, trust, integrity & piety | `Venus - Mars + Lagna` | `Mars - Venus + Lagna` |
| **`#28`** | **Preeti Saham (Love/Affection)** | Deep affection, harmony & cordiality | `Vidya - Punya + Lagna` | `Punya - Vidya + Lagna` |
| **`#29`** | **Bala Saham (Strength)** | Physical and moral authority & command | `Punya - Vidya + Lagna` | `Vidya - Punya + Lagna` |
| **`#30`** | **Manmatha Saham (Passion)** | Romantic passion, artistic charm & attraction | `Moon - Lagna_Lord + Lagna` | `Lagna_Lord - Moon + Lagna` |
| **`#31`** | **Vyapara Saham (Business Venture)** | Commercial expansion, contracts & deals | `Mars - Saturn + Lagna` | `Mars - Saturn + Lagna (Same)` |
| **`#32`** | **Paniyapatana Saham (Water)** | Maritime travel, liquids, rainfall & water hazards | `Saturn - Moon + Lagna` | `Moon - Saturn + Lagna` |
| **`#33`** | **Shatru Saham (Enemies)** | Litigation, rivals, competitors & opposition | `Mars - Saturn + Lagna` | `Saturn - Mars + Lagna` |
| **`#34`** | **Bandhana Saham (Confinement)** | Restraint, hospitalization, debt or captivity | `Punya - Saturn + Lagna` | `Saturn - Punya + Lagna` |
| **`#35`** | **Apamrityu Saham (Accidents)** | Sudden accidents, surgical risk & acute hazards | `8th Cusp - Mars + Lagna` | `Mars - 8th Cusp + Lagna` |
| **`#36`** | **Labha Saham (Gains/Profits)** | Net profits, windfalls, dividends & awards | `11th Cusp - 11th Lord + Lagna` | `11th Cusp - 11th Lord + Lagna (Same)` |

## Chapter 18 — Complete *Ashtakoota* (36-Guna) Compatibility, `14 × 14` *Yoni* Matrix, 81-Cell *Sarvatobhadra Chakra*, & *Muhurta* Compendium

### Table 18A — Complete 27-Nakshatra *Ashtakoota* & *Dashakoota* Classification Directory (`Gana, Nadi, Yoni, Rajju, & Tara`)

| # | Nakshatra | Span (`Rashi` & Degrees) | Ruler | *Gana* (`6 pts`) | *Nadi* (`8 pts`) | *Yoni* Animal (`4 pts`) | *Rajju* Group (`Dashakoota`) |
|---|---|---|---|---|---|---|---|
| **01** | **Ashwini** | `Mesha 00° 00' 00"` – `Mesha 13° 20' 00"` | Ketu | Deva | **Adi** | Horse | Pada (Foot) |
| **02** | **Bharani** | `Mesha 13° 20' 00"` – `Mesha 26° 40' 00"` | Venus | Manushya | **Madhya** | Elephant | Kati (Waist) |
| **03** | **Krittika** | `Mesha 26° 40' 00"` – `Vrishabha 10° 00' 00"` | Sun | Rakshasa | **Antya** | Goat | Nabhi (Navel) |
| **04** | **Rohini** | `Vrishabha 10° 00' 00"` – `Vrishabha 23° 20' 00"` | Moon | Manushya | **Antya** | Serpent | Kantha (Neck) |
| **05** | **Mrigashirsha** | `Vrishabha 23° 20' 00"` – `Mithuna 06° 40' 00"` | Mars | Deva | **Madhya** | Serpent | Shiro (Head) |
| **06** | **Ardra** | `Mithuna 06° 40' 00"` – `Mithuna 20° 00' 00"` | Rahu | Manushya | **Adi** | Dog | Kantha (Neck) |
| **07** | **Punarvasu** | `Mithuna 20° 00' 00"` – `Karka 03° 20' 00"` | Jupiter | Deva | **Adi** | Cat | Nabhi (Navel) |
| **08** | **Pushya** | `Karka 03° 20' 00"` – `Karka 16° 40' 00"` | Saturn | Deva | **Madhya** | Goat | Kati (Waist) |
| **09** | **Ashlesha** | `Karka 16° 40' 00"` – `Simha 00° 00' 00"` | Mercury | Rakshasa | **Antya** | Cat | Pada (Foot) |
| **10** | **Magha** | `Simha 00° 00' 00"` – `Simha 13° 20' 00"` | Ketu | Rakshasa | **Antya** | Rat | Pada (Foot) |
| **11** | **Purva Phalguni** | `Simha 13° 20' 00"` – `Simha 26° 40' 00"` | Venus | Manushya | **Madhya** | Rat | Kati (Waist) |
| **12** | **Uttara Phalguni** | `Simha 26° 40' 00"` – `Kanya 10° 00' 00"` | Sun | Manushya | **Adi** | Cow | Nabhi (Navel) |
| **13** | **Hasta** | `Kanya 10° 00' 00"` – `Kanya 23° 20' 00"` | Moon | Deva | **Adi** | Buffalo | Kantha (Neck) |
| **14** | **Chitra** | `Kanya 23° 20' 00"` – `Tula 06° 40' 00"` | Mars | Rakshasa | **Madhya** | Tiger | Shiro (Head) |
| **15** | **Swati** | `Tula 06° 40' 00"` – `Tula 20° 00' 00"` | Rahu | Deva | **Antya** | Buffalo | Kantha (Neck) |
| **16** | **Vishakha** | `Tula 20° 00' 00"` – `Vrishchika 03° 20' 00"` | Jupiter | Rakshasa | **Antya** | Tiger | Nabhi (Navel) |
| **17** | **Anuradha** | `Vrishchika 03° 20' 00"` – `Vrishchika 16° 40' 00"` | Saturn | Deva | **Madhya** | Deer | Kati (Waist) |
| **18** | **Jyeshtha** | `Vrishchika 16° 40' 00"` – `Dhanu 00° 00' 00"` | Mercury | Rakshasa | **Adi** | Deer | Pada (Foot) |
| **19** | **Mula** | `Dhanu 00° 00' 00"` – `Dhanu 13° 20' 00"` | Ketu | Rakshasa | **Adi** | Dog | Pada (Foot) |
| **20** | **Purva Ashadha** | `Dhanu 13° 20' 00"` – `Dhanu 26° 40' 00"` | Venus | Manushya | **Madhya** | Monkey | Kati (Waist) |
| **21** | **Uttara Ashadha** | `Dhanu 26° 40' 00"` – `Makara 10° 00' 00"` | Sun | Manushya | **Antya** | Mongoose | Nabhi (Navel) |
| **22** | **Shravana** | `Makara 10° 00' 00"` – `Makara 23° 20' 00"` | Moon | Deva | **Antya** | Monkey | Kantha (Neck) |
| **23** | **Dhanishta** | `Makara 23° 20' 00"` – `Kumbha 06° 40' 00"` | Mars | Rakshasa | **Madhya** | Lion | Shiro (Head) |
| **24** | **Shatabhisha** | `Kumbha 06° 40' 00"` – `Kumbha 20° 00' 00"` | Rahu | Rakshasa | **Adi** | Horse | Kantha (Neck) |
| **25** | **Purva Bhadrapada** | `Kumbha 20° 00' 00"` – `Meena 03° 20' 00"` | Jupiter | Manushya | **Adi** | Lion | Nabhi (Navel) |
| **26** | **Uttara Bhadrapada** | `Meena 03° 20' 00"` – `Meena 16° 40' 00"` | Saturn | Manushya | **Madhya** | Cow | Kati (Waist) |
| **27** | **Revati** | `Meena 16° 40' 00"` – `Mesha 00° 00' 00"` | Mercury | Deva | **Antya** | Elephant | Pada (Foot) |

### Table 18B — Complete `14 × 14` *Yoni Koota* (`0 to 4 Points`) Classical Compatibility Matrix

| Yoni \ Yoni | **Horse** | **Eleph** | **Goat** | **Serpe** | **Dog** | **Cat** | **Rat** | **Cow** | **Buffa** | **Tiger** | **Deer** | **Monke** | **Mongo** | **Lion** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **01 Horse** | `4` | `2` | `2` | `3` | `2` | `2` | `2` | `1` | `0` | `1` | `3` | `3` | `2` | `1` |
| **02 Elephant** | `2` | `4` | `3` | `3` | `2` | `2` | `2` | `2` | `3` | `1` | `2` | `3` | `2` | `0` |
| **03 Goat** | `2` | `3` | `4` | `2` | `1` | `2` | `1` | `3` | `3` | `1` | `2` | `0` | `3` | `1` |
| **04 Serpent** | `3` | `3` | `2` | `4` | `2` | `1` | `1` | `1` | `1` | `2` | `2` | `2` | `0` | `2` |
| **05 Dog** | `2` | `2` | `1` | `2` | `4` | `2` | `1` | `2` | `2` | `1` | `0` | `2` | `1` | `1` |
| **06 Cat** | `2` | `2` | `2` | `1` | `2` | `4` | `0` | `2` | `2` | `1` | `3` | `3` | `2` | `1` |
| **07 Rat** | `2` | `2` | `1` | `1` | `1` | `0` | `4` | `2` | `2` | `2` | `2` | `2` | `1` | `2` |
| **08 Cow** | `1` | `2` | `3` | `1` | `2` | `2` | `2` | `4` | `3` | `0` | `3` | `2` | `2` | `1` |
| **09 Buffalo** | `0` | `3` | `3` | `1` | `2` | `2` | `2` | `3` | `4` | `1` | `2` | `2` | `2` | `1` |
| **10 Tiger** | `1` | `1` | `1` | `2` | `1` | `1` | `2` | `0` | `1` | `4` | `1` | `1` | `2` | `1` |
| **11 Deer** | `3` | `2` | `2` | `2` | `0` | `3` | `2` | `3` | `2` | `1` | `4` | `2` | `2` | `1` |
| **12 Monkey** | `3` | `3` | `0` | `2` | `2` | `3` | `2` | `2` | `2` | `1` | `2` | `4` | `3` | `2` |
| **13 Mongoose** | `2` | `2` | `3` | `0` | `1` | `2` | `1` | `2` | `2` | `2` | `2` | `3` | `4` | `2` |
| **14 Lion** | `1` | `0` | `1` | `2` | `1` | `1` | `2` | `1` | `1` | `1` | `1` | `2` | `2` | `4` |

### Table 18C — Complete `9 × 9` (81-Cell) *Sarvatobhadra Chakra* Master Transit & *Vedha* Grid

| Row \ Col | Col 0 (West) | Col 1 | Col 2 | Col 3 | Col 4 (Center) | Col 5 | Col 6 | Col 7 | Col 8 (East) |
|---|---|---|---|---|---|---|---|---|---|
| **Row 0** | **a** *(Vow)* | **Krittika** *(Nak)* | **Rohini** *(Nak)* | **Mrigashirsha** *(Nak)* | **Ardra** *(Nak)* | **Punarvasu** *(Nak)* | **Pushya** *(Nak)* | **Ashlesha** *(Nak)* | **aa** *(Vow)* |
| **Row 1** | **Bharani** *(Nak)* | **u** *(Vow)* | **g** *(Con)* | **s** *(Con)* | **d** *(Con)* | **ch** *(Con)* | **l** *(Con)* | **uu** *(Vow)* | **Magha** *(Nak)* |
| **Row 2** | **Ashwini** *(Nak)* | **k** *(Con)* | **li** *(Vow)* | **Mesha** *(Ras)* | **Vrishabha** *(Ras)* | **Mithuna** *(Ras)* | **lii** *(Vow)* | **u_c** *(Con)* | **Purva Phalguni** *(Nak)* |
| **Row 3** | **Revati** *(Nak)* | **sh** *(Con)* | **Meena** *(Ras)* | **o** *(Vow)* | **Nanda** *(Tit)* | **au** *(Vow)* | **Karka** *(Ras)* | **m** *(Con)* | **Uttara Phalguni** *(Nak)* |
| **Row 4** | **Uttara Bhadrapada** *(Nak)* | **v** *(Con)* | **Kumbha** *(Ras)* | **Rikta** *(Tit)* | **Purna** *(Tit)* | **Bhadra** *(Tit)* | **Simha** *(Ras)* | **t** *(Con)* | **Hasta** *(Nak)* |
| **Row 5** | **Purva Bhadrapada** *(Nak)* | **gh** *(Con)* | **Makara** *(Ras)* | **ah** *(Vow)* | **Jaya** *(Tit)* | **am** *(Vow)* | **Kanya** *(Ras)* | **p** *(Con)* | **Chitra** *(Nak)* |
| **Row 6** | **Shatabhisha** *(Nak)* | **kh** *(Con)* | **ai** *(Vow)* | **Dhanu** *(Ras)* | **Vrishchika** *(Ras)* | **Tula** *(Ras)* | **e** *(Vow)* | **r** *(Con)* | **Swati** *(Nak)* |
| **Row 7** | **Dhanishta** *(Nak)* | **rii** *(Vow)* | **j** *(Con)* | **y** *(Con)* | **bh** *(Con)* | **dh** *(Con)* | **n** *(Con)* | **ri** *(Vow)* | **Vishakha** *(Nak)* |
| **Row 8** | **ii** *(Vow)* | **Shravana** *(Nak)* | **Abhijit** *(Nak)* | **Uttara Ashadha** *(Nak)* | **Purva Ashadha** *(Nak)* | **Mula** *(Nak)* | **Jyeshtha** *(Nak)* | **Anuradha** *(Nak)* | **i** *(Vow)* |

### Table 18D — *Muhurta* Electional Compendium: *Amrita Siddhi*, *Sarvartha Siddhi*, & *Dagdha Rashi* (Burnt Signs by Tithi)

| Weekday (*Vara*) | *Amrita Siddhi* Nakshatra (Avoid Tithi) | *Sarvartha Siddhi* Nakshatras | Paksha Tithis | *Dagdha Rashi* (Burnt Signs to Avoid in Lagna) |
|---|---|---|---|---|
| **Sunday (Ravivara)** | **Hasta** *(excl. Panchami (5))* | Ashwini, Pushya, Uttara Phalguni, Hasta, Mula, Uttara Ashadha, Uttara Bhadrapada | Tithi 1 & 2 | `T1:` **Tula, Makara**; `T2:` **Dhanu, Meena** |
| **Monday (Somavara)** | **Mrigashirsha** *(excl. Shashthi (6))* | Rohini, Mrigashirsha, Pushya, Anuradha, Shravana | Tithi 3 & 4 | `T3:` **Simha, Makara**; `T4:` **Vrishabha, Kumbha** |
| **Tuesday (Mangalavara)** | **Ashwini** *(excl. Saptami (7))* | Ashwini, Krittika, Ashlesha, Uttara Bhadrapada | Tithi 5 & 6 | `T5:` **Mithuna, Kanya**; `T6:` **Mesha, Simha** |
| **Wednesday (Budhavara)** | **Anuradha** *(excl. Ashtami (8))* | Krittika, Rohini, Mrigashirsha, Hasta, Anuradha | Tithi 7 & 8 | `T7:` **Karka, Dhanu**; `T8:` **Mithuna, Kanya** |
| **Thursday (Guruvara)** | **Pushya** *(excl. Navami (9))* | Ashwini, Punarvasu, Pushya, Anuradha, Revati | Tithi 9 & 10 | `T9:` **Simha, Vrishchika**; `T10:` **Simha, Vrishchika** |
| **Friday (Shukravara)** | **Revati** *(excl. Dashami (10))* | Ashwini, Punarvasu, Anuradha, Shravana, Revati | Tithi 11 & 12 | `T11:` **Dhanu, Meena**; `T12:` **Tula, Makara** |
| **Saturday (Shanivara)** | **Rohini** *(excl. Ekadashi (11))* | Rohini, Swati, Shravana | Tithi 13 & 14 | `T13:` **Vrishabha, Simha**; `T14:` **Mithuna, Kanya, Dhanu, Meena**; Tithi 15:  |

## Chapter 19 — Complete Classical Parashari Yoga Identification Directory, 30-Star *Yogatara* Catalog, & *Surya Siddhanta* Reference

### Table 19A — Complete 30-Star *Yogatara* (Junction Star) Astrometric Reference Catalog (*Surya Siddhanta* Chapter 8)

| # | Nakshatra / Star | Sanskrit *Yogatara* Name | Modern IAU Star | J2000 RA (`deg`) | J2000 Dec (`deg`) | Visual Mag ($V$) | *Kalansha* Heliacal Arc |
|---|---|---|---|---|---|---|---|
| **01** | **Ashwini** *(Nakshatra #1)* | `ashwini` (`HIP 8903`) | `Sheratan / beta Arietis` | `028.660°` | `+20.808°` | `+2.64` | `13.0°` |
| **02** | **Bharani** *(Nakshatra #2)* | `bharani` (`HIP 13209`) | `41 Arietis / c Arietis` | `042.496°` | `+27.261°` | `+3.61` | `14.0°` |
| **03** | **Krittika** *(Nakshatra #3)* | `krittika` (`HIP 17702`) | `Alcyone / eta Tauri` | `056.871°` | `+24.105°` | `+2.87` | `13.0°` |
| **04** | **Rohini** *(Nakshatra #4)* | `rohini` (`HIP 21421`) | `Aldebaran / alpha Tauri` | `068.980°` | `+16.509°` | `+0.86` | `12.0°` |
| **05** | **Mrigashirsha** *(Nakshatra #5)* | `mrigashirsha` (`HIP 26207`) | `Meissa / lambda Orionis` | `083.784°` | `+09.934°` | `+3.39` | `14.0°` |
| **06** | **Ardra** *(Nakshatra #6)* | `ardra` (`HIP 27989`) | `Betelgeuse / alpha Orionis` | `088.793°` | `+07.407°` | `+0.50` | `12.0°` |
| **07** | **Punarvasu** *(Nakshatra #7)* | `punarvasu` (`HIP 37826`) | `Pollux / beta Geminorum` | `116.329°` | `+28.026°` | `+1.14` | `12.0°` |
| **08** | **Pushya** *(Nakshatra #8)* | `pushya` (`HIP 42911`) | `Asellus Australis / delta Cancri` | `131.171°` | `+18.154°` | `+3.94` | `14.0°` |
| **09** | **Ashlesha** *(Nakshatra #9)* | `ashlesha` (`HIP 43813`) | `Minchir / zeta Hydrae` | `133.848°` | `+05.946°` | `+3.11` | `13.5°` |
| **10** | **Magha** *(Nakshatra #10)* | `magha` (`HIP 49669`) | `Regulus / alpha Leonis` | `152.093°` | `+11.967°` | `+1.36` | `12.0°` |
| **11** | **Purva Phalguni** *(Nakshatra #11)* | `purva_phalguni` (`HIP 54872`) | `Zosma / delta Leonis` | `168.527°` | `+20.524°` | `+2.56` | `13.0°` |
| **12** | **Uttara Phalguni** *(Nakshatra #12)* | `uttara_phalguni` (`HIP 57632`) | `Denebola / beta Leonis` | `177.265°` | `+14.572°` | `+2.14` | `12.5°` |
| **13** | **Hasta** *(Nakshatra #13)* | `hasta` (`HIP 60965`) | `Algorab / delta Corvi` | `187.466°` | `-16.515°` | `+2.95` | `13.5°` |
| **14** | **Chitra** *(Nakshatra #14)* | `chitra` (`HIP 65474`) | `Spica / alpha Virginis` | `201.298°` | `-11.161°` | `+0.97` | `12.0°` |
| **15** | **Swati** *(Nakshatra #15)* | `swati` (`HIP 69673`) | `Arcturus / alpha Bootis` | `213.915°` | `+19.182°` | `-0.05` | `11.0°` |
| **16** | **Vishakha** *(Nakshatra #16)* | `vishakha` (`HIP 72622`) | `Zubenelgenubi / alpha2 Librae` | `222.720°` | `-16.042°` | `+2.75` | `13.0°` |
| **17** | **Anuradha** *(Nakshatra #17)* | `anuradha` (`HIP 78401`) | `Dschubba / delta Scorpii` | `240.083°` | `-22.622°` | `+2.31` | `13.0°` |
| **18** | **Jyeshtha** *(Nakshatra #18)* | `jyeshtha` (`HIP 80763`) | `Antares / alpha Scorpii` | `247.352°` | `-26.432°` | `+0.96` | `12.0°` |
| **19** | **Mula** *(Nakshatra #19)* | `mula` (`HIP 85927`) | `Shaula / lambda Scorpii` | `263.402°` | `-37.104°` | `+1.62` | `12.5°` |
| **20** | **Purva Ashadha** *(Nakshatra #20)* | `purva_ashadha` (`HIP 89931`) | `Kaus Media / delta Sagittarii` | `275.249°` | `-29.828°` | `+2.70` | `13.0°` |
| **21** | **Uttara Ashadha** *(Nakshatra #21)* | `uttara_ashadha` (`HIP 92855`) | `Nunki / sigma Sagittarii` | `283.816°` | `-26.297°` | `+2.05` | `12.5°` |
| **22** | **Shravana** *(Nakshatra #22)* | `shravana` (`HIP 97649`) | `Altair / alpha Aquilae` | `297.696°` | `+08.868°` | `+0.76` | `12.0°` |
| **23** | **Dhanishta** *(Nakshatra #23)* | `dhanishta` (`HIP 101769`) | `Rotanev / beta Delphini` | `309.387°` | `+14.595°` | `+3.63` | `14.0°` |
| **24** | **Shatabhisha** *(Nakshatra #24)* | `shatabhisha` (`HIP 112961`) | `Hydor / lambda Aquarii` | `343.154°` | `-07.580°` | `+3.73` | `14.0°` |
| **25** | **Purva Bhadrapada** *(Nakshatra #25)* | `purva_bhadrapada` (`HIP 113963`) | `Markab / alpha Pegasi` | `346.190°` | `+15.205°` | `+2.48` | `13.0°` |
| **26** | **Uttara Bhadrapada** *(Nakshatra #26)* | `uttara_bhadrapada` (`HIP 677`) | `Alpheratz / alpha Andromedae` | `002.097°` | `+29.090°` | `+2.06` | `12.5°` |
| **27** | **Revati** *(Nakshatra #27)* | `revati` (`HIP 5737`) | `Revati / zeta Piscium A` | `018.423°` | `+07.577°` | `+5.21` | `15.0°` |
| **28** | **Abhijit** *(Nakshatra #28)* | `abhijit` (`HIP 91262`) | `Vega / alpha Lyrae` | `279.235°` | `+38.784°` | `+0.03` | `11.0°` |
| **29** | **Agastya** *(Seasonal Star)* | `agastya` (`HIP 30438`) | `Canopus / alpha Carinae` | `095.988°` | `-52.696°` | `-0.74` | `13.0°` |
| **30** | **Lubdhaka** *(Seasonal Star)* | `lubdhaka` (`HIP 32349`) | `Sirius / alpha Canis Majoris` | `101.287°` | `-16.716°` | `-1.46` | `13.0°` |

### Table 19B — Classical *Surya Siddhanta* *Mahayuga Bhagana*, *Mandocca* (Apogees), & Epicycle (*Paridhi*) Constants

| Graha | *Mahayuga Bhagana* (`4,320,000` Solar Years) | *Mandocca* at Kali Epoch (`deg`) | *Manda Paridhi* (`Even / Odd` Quadrants) | *Sighra Paridhi* (`Even / Odd` Quadrants) |
|---|---|---|---|---|
| **Sun** | `4,320,000` revolutions | `77.2833°` | `14.0° / 13.7°` | — (No Sighra Samskara) |
| **Moon** | `57,753,336` revolutions | `0.0000°` | `32.0° / 31.7°` | — (No Sighra Samskara) |
| **Mars** | `2,296,832` revolutions | `130.0000°` | `75.0° / 72.0°` | `235.0° / 232.0°` |
| **Mercury** | `17,937,060` revolutions | `220.4500°` | `30.0° / 28.0°` | `133.0° / 132.0°` |
| **Jupiter** | `364,220` revolutions | `171.3000°` | `33.0° / 32.0°` | `70.0° / 72.0°` |
| **Venus** | `7,022,376` revolutions | `79.8333°` | `12.0° / 11.0°` | `262.0° / 260.0°` |
| **Saturn** | `146,568` revolutions | `236.6167°` | `49.0° / 48.0°` | `39.0° / 40.0°` |

## Chapter 20 — Section 7 — Pt. Maheshji's Jyotish Academy Step-by-Step Worked Manual Kundali Worksheet (Complete 15-Step Master Case Study)

- **Case Study Date & Time:** `2026-11-15` at `10:42:00 IST (UTC+05:30)`
- **Observer Location:** `Lat 23.1765 deg, Lon 75.7885 deg` (Ujjain Prime Meridian Reference)
- **Elapsed Time After `05:30 IST` Tabular Epoch:** `5 hours 12 minutes (13 Ghatis 00 Palas)` (Interpolation Fraction $f = 0.216667$)
- **Manual Ascendant (*Udaya Lagna*):** `Dhanu 22° 18' 00"` | **10th Cusp (*Madhya Lagna*):** `Tula 05° 57' 51"`
- **Natal Moon Nakshatra & Pada:** `Uttara Ashadha Pada 3 (Lord: Sun)` (`378.34'` *Bhogyamsha* remaining)
- **Natal *Vimshottari Dasha* Balance at Birth:** **`Sun Mahadasha: 2 Years, 10 Months, 2 Days remaining`**

### Step 1 & Step 2 — Complete 1st-Order (*Trairashika*) & 2nd-Order (*Bessel*) Manual *Spashta Graha* Worksheet

| Body | `05:30 IST` Day $D$ | `05:30 IST` Day $D+1$ | Daily Motion $v_1$ | 1st-Order *Trairashika* | 2nd-Order *Bessel* Exact | `D9` Navamsa | `D10` Dasamsa | `D60` Shashtiamsa | *KP* Star / Sub / Sub-Sub |
|---|---|---|---|---|---|---|---|---|---|
| **Surya (Sun)** | `Tula 28° 23' 45"` | `+00° 13' 06"` | `+01° 00' 25"` | `Tula 28° 36' 50"` | **`Tula 28° 36' 50"`** | **Mithuna** | **Karka** | Karka | `venus / jupiter / venus / mercury` |
| **Chandra (Moon)** | `Makara 01° 08' 07"` | `+02° 33' 27"` | `+11° 48' 14"` | `Makara 03° 41' 34"` | **`Makara 03° 41' 27"`** | **Kumbha** | **Tula** | Simha | `saturn / sun / saturn / ketu` |
| **Mangala (Mars)** | `Simha 01° 05' 12"` | `+00° 05' 52"` | `+00° 27' 03"` | `Simha 01° 11' 03"` | **`Simha 01° 11' 04"`** | **Mesha** | **Simha** | Tula | `sun / ketu / venus / sun` |
| **Budha (Mercury)** | `Tula 10° 57' 40"` | `+00° 03' 07"` | `+00° 14' 22"` | `Tula 11° 00' 47"` | **`Tula 11° 00' 21"`** | **Makara** | **Makara** | Simha | `venus / rahu / saturn / mercury` |
| **Guru (Jupiter)** | `Simha 01° 32' 52"` | `+00° 01' 07"` | `+00° 05' 09"` | `Simha 01° 33' 59"` | **`Simha 01° 33' 59"`** | **Mesha** | **Simha** | Vrishchika | `sun / ketu / venus / mars` |
| **Shukra (Venus)** | `Kanya 28° 38' 53"` | `+00° 00' 30"` | `+00° 02' 21"` | `Kanya 28° 39' 24"` | **`Kanya 28° 39' 18"`** | **Kanya** | **Kumbha** | Mithuna | `mercury / mars / saturn / venus` |
| **Shani (Saturn)** | `Meena 14° 17' 33"` | `-00° 00' 35"` | `-00° 02' 40"` | `Meena 14° 16' 59"` | **`Meena 14° 16' 58"`** | **Vrishchika** | **Meena** | Karka | `jupiter / saturn / rahu / venus` |
| **Rahu (Node)** | `Kumbha 01° 05' 51"` | `-00° 00' 41"` | `-00° 03' 11"` | `Kumbha 01° 05' 10"` | **`Kumbha 01° 05' 10"`** | **Tula** | **Kumbha** | Mesha | `saturn / mars / mercury / rahu` |
| **Ketu (S. Node)** | `Simha 01° 05' 51"` | `-00° 00' 41"` | `-00° 03' 11"` | `Simha 01° 05' 10"` | **`Simha 01° 05' 10"`** | **Mesha** | **Simha** | Tula | `sun / ketu / venus / venus` |

### Step 3 & Step 4 — All 12 *Sripathi Bhava* Cusps, 8 *Vishesha Lagnas*, *Yogi/Avayogi*, 11 *Upagrahas*, & 9 *Prashna Sphutas*

| Special Point Category | Point Name | Computed Sidereal Longitude (`DMS`) | Sign (`Rashi`) | `D9` Navamsa / Nakshatra Details |
|---|---|---|---|---|
| **8 Vishesha Lagnas** | **Udaya Lagna (Birth Ascendant)** | **`Dhanu 22° 18' 00"`** | Dhanu (Jupiter) | `D9:` **Tula**; *Purva Ashadha* P3 (Eastern horizon intersection with the sidereal ecliptic at birth) |
| **8 Vishesha Lagnas** | **Hora Lagna (HL — Sustenance & Wealth)** | **`Kumbha 05° 06' 30"`** | Kumbha (Saturn) | `D9:` **Vrishchika**; *Dhanishta* P4 (Sun at Sunrise + (Elapsed Minutes since Sunrise / 2.5)) |
| **8 Vishesha Lagnas** | **Ghati Lagna (GL — Power, Rank & Authority)** | **`Kanya 00° 31' 03"`** | Kanya (Mercury) | `D9:` **Makara**; *Uttara Phalguni* P2 (Sun at Sunrise + (Elapsed Ghatis since Sunrise × 30°)) |
| **8 Vishesha Lagnas** | **Bhava Lagna (BL — Disposition & Vitality)** | **`Dhanu 28° 51' 34"`** | Dhanu (Jupiter) | `D9:` **Dhanu**; *Uttara Ashadha* P1 (Sun at Sunrise + (Elapsed Ghatis since Sunrise × 6°)) |
| **8 Vishesha Lagnas** | **Sree Lagna (SL — Lakshmi Prosperity & Grace)** | **`Karka 02° 02' 46"`** | Karka (Moon) | `D9:` **Karka**; *Punarvasu* P4 (Udaya Lagna + (Moon's Traversed Nakshatra Fraction × 360°)) |
| **8 Vishesha Lagnas** | **Indu Lagna (IL — Kalidasa Wealth & Dhana Yoga Point)** | **`Kumbha 03° 41' 39"`** | Kumbha (Saturn) | `D9:` **Vrishchika**; *Dhanishta* P4 (9th Lord from Lagna (Sun=30) + 9th Lord from Moon (Mercury=8) = 38 Kalas -> 2th sign from Moon) |
| **8 Vishesha Lagnas** | **Pranapada Lagna (PL — Vital Breath & Rectification Anchor)** | **`Dhanu 08° 53' 25"`** | Dhanu (Jupiter) | `D9:` **Mithuna**; *Mula* P3 (Sun at Birth + Modality Offset (Movable +0°, Fixed +240°, Dual +120°) + (Elapsed Palas / 15)) |
| **8 Vishesha Lagnas** | **Varnada Lagna (VL — Social Standing & Vocational Destiny)** | **`Vrishchika 22° 18' 00"`** | Vrishchika (Mars) | `D9:` **Makara**; *Jyeshtha* P2 (Parashari Odd-Direct / Even-Reverse synthesis of Udaya Lagna and Hora Lagna) |
| **Yogi & Avayogi** | **Yogi Point & Yogi Planet** | **`Vrishchika 05° 38' 30"`** | Yogi: **Saturn** | Nakshatra: *Anuradha*; Sahayogi: **Mars** |
| **Yogi & Avayogi** | **Avayogi Point & Planet** | **`Vrishabha 12° 18' 30"`** | Avayogi: **Moon** | Nakshatra: *Rohini* |
| **11 Upagrahas** | **Dhuma** | `Meena 11° 56' 50"` | Meena | *Uttara Bhadrapada* Pada 3 |
| **11 Upagrahas** | **Vyatipata** | `Mesha 18° 03' 10"` | Mesha | *Bharani* Pada 2 |
| **11 Upagrahas** | **Parivesha** | `Tula 18° 03' 10"` | Tula | *Swati* Pada 4 |
| **11 Upagrahas** | **Indrachapa** | `Kanya 11° 56' 50"` | Kanya | *Hasta* Pada 1 |
| **11 Upagrahas** | **Upaketu** | `Kanya 28° 36' 50"` | Kanya | *Chitra* Pada 2 |
| **11 Upagrahas** | **Gulika (Mandi)** | `Meena 08° 24' 07"` | Meena | *Uttara Bhadrapada* Pada 2 |
| **11 Upagrahas** | **Kala** | `Tula 27° 36' 06"` | Tula | *Vishakha* Pada 3 |
| **11 Upagrahas** | **Mrityu** | `Dhanu 04° 13' 02"` | Dhanu | *Mula* Pada 2 |
| **11 Upagrahas** | **Ardhaprahara** | `Dhanu 23° 56' 01"` | Dhanu | *Purva Ashadha* Pada 4 |
| **11 Upagrahas** | **Yamaghantaka** | `Makara 15° 57' 31"` | Makara | *Shravana* Pada 2 |
| **11 Upagrahas** | **Ochcha** | `Kumbha 11° 01' 39"` | Kumbha | *Shatabhisha* Pada 2 |
| **9 Prashna Sphutas** | **Trisphuta** | `Kanya 04° 23' 47"` | Kanya | *Uttara Phalguni* Pada 3 |
| **9 Prashna Sphutas** | **Chatusphuta** | `Mesha 03° 00' 37"` | Mesha | *Ashwini* Pada 1 |
| **9 Prashna Sphutas** | **Panchasphuta** | `Kumbha 04° 05' 46"` | Kumbha | *Dhanishta* Pada 4 |
| **9 Prashna Sphutas** | **Prana Sphuta** | `Tula 29° 54' 07"` | Tula | *Vishakha* Pada 3 |
| **9 Prashna Sphutas** | **Deha Sphuta** | `Mesha 07° 57' 23"` | Mesha | *Ashwini* Pada 3 |
| **9 Prashna Sphutas** | **Mrityu Sphuta** | `Vrishabha 27° 25' 40"` | Vrishabha | *Mrigashirsha* Pada 2 |
| **9 Prashna Sphutas** | **Tithi Sphuta** | `Kumbha 27° 22' 49"` | Kumbha | *Purva Bhadrapada* Pada 3 |
| **9 Prashna Sphutas** | **Beeja Sphuta** | `Simha 28° 50' 16"` | Simha | *Uttara Phalguni* Pada 1 |
| **9 Prashna Sphutas** | **Kshetra Sphuta** | `Kanya 06° 26' 41"` | Kanya | *Uttara Phalguni* Pada 3 |

### Step 5 & Step 6 — Worked Case Study: *Jaimini Chara Karakas*, 12 *Arudha Padas*, *Shadbala*, & *Sarvashtakavarga*

| Graha | 7-Karaka Role | 8-Karaka Role | Total *Shadbala* (`Virupas` / `Rupas`) | Required (`Rupas`) | *Shadbala* Ratio | *Vimshopaka* (`D16` / `20`) | *Bhinna Ashtakavarga* Total |
|---|---|---|---|---|---|---|---|
| **Sun** | **AmK** (Amatyakaraka (Career & Minister Significator — 2nd Highest)) | **BK** (Bhratrukaraka (Siblings & Courage — 3rd Highest)) | **`474.5v` (`7.91R`)** | `5.00R` | `1.58x` | `12.97 / 20` | `48 Bindus` |
| **Moon** | **PK** (Putrakaraka (Children, Intelligence & Followers — 5th Highest)) | **PK** (Putrakaraka (Children, Intelligence & Merit — 6th Highest)) | **`405.5v` (`6.76R`)** | `6.00R` | `1.13x` | `14.60 / 20` | `49 Bindus` |
| **Mars** | **DK** (Darakaraka (Spouse & Business Partner — Lowest Degree)) | **DK** (Darakaraka (Spouse & Partner — Lowest Degree)) | **`422.1v` (`7.04R`)** | `5.00R` | `1.41x` | `17.25 / 20` | `39 Bindus` |
| **Mercury** | **MK** (Matrukaraka (Mother, Homeland & Emotional Peace — 4th Highest)) | **PiK** (Pitrukaraka (Father, Ancestors & Authority — 5th Highest)) | **`370.5v` (`6.17R`)** | `7.00R` | `0.88x` | `12.45 / 20` | `54 Bindus` |
| **Jupiter** | **GK** (Gnathikaraka (Rivals, Kinsmen & Obstacles — 6th Highest)) | **GK** (Gnathikaraka (Rivals, Kinsmen & Disease — 7th Highest)) | **`516.9v` (`8.61R`)** | `6.50R` | `1.33x` | `13.72 / 20` | `56 Bindus` |
| **Venus** | **AK** (Atmakaraka (Soul Significator — Highest Degree)) | **AmK** (Amatyakaraka (Career & Minister Significator — 2nd Highest)) | **`371.7v` (`6.20R`)** | `5.50R` | `1.13x` | `16.55 / 20` | `52 Bindus` |
| **Saturn** | **BK** (Bhratrukaraka (Siblings, Guru & Courage — 3rd Highest)) | **MK** (Matrukaraka (Mother & Emotional Peace — 4th Highest)) | **`337.9v` (`5.63R`)** | `5.00R` | `1.13x` | `8.55 / 20` | `39 Bindus` |
| **Rahu** | — | **AK** (Atmakaraka (Soul Significator — Highest Degree)) | — (Shadow Node) | — | — | — | — |

**Worked 12 *Sarvashtakavarga* (`SAV`) Totals by Sign (`Mesha` to `Meena`):** **Mesha:** `20`, **Vrishabha:** `33`, **Mithuna:** `35`, **Karka:** `30`, **Simha:** `30`, **Kanya:** `24`, **Tula:** `27`, **Vrishchika:** `25`, **Dhanu:** `27`, **Makara:** `27`, **Kumbha:** `27`, **Meena:** `32` (Grand Total = **`337 Bindus`**).

**Worked 12 *Jaimini Arudha Padas* (`AL` to `UL`):** **AL:** Mesha, **A2:** Vrishabha, **A3:** Mesha, **A4:** Makara, **A5:** Dhanu, **A6:** Makara, **A7:** Kumbha, **A8:** Mesha *(Swastha)*, **A9:** Dhanu, **A10:** Vrishchika, **A11:** Simha, **UL:** Vrishabha.

**Worked *Kalachakra Dasha* at Birth:** Chakra Group = **Savya**, *Dehamsha* = **Kanya**, *Jeevamsha* = **Kumbha**, Paramayus = `85 Years`, Birth Period = **Simha** (`Krama Gati` Gati).

**Worked Sample of 36 *Tajika Sahams*:** **Punya Saham:** `Kumbha 27° 22' 49"`, **Vidya Saham:** `Vrishchika 17° 13' 11"`, **Yasas Saham:** `Mithuna 26° 29' 09"`, **Mitra Saham:** `Mesha 02° 50' 37"`, **Mahatmya Saham:** `Karka 18° 29' 46"`, **Asha Saham:** `Mithuna 07° 55' 31"`, **Samarthya Saham:** `Dhanu 21° 55' 04"`, **Bhratri Saham:** `Mithuna 09° 35' 00"`, **Gaurava Saham:** `Vrishabha 26° 29' 09"`, **Pitri Saham:** `Vrishabha 07° 58' 08"`, **Matri Saham:** `Meena 27° 20' 12"`, **Putra Saham:** `Simha 20° 10' 19"` *(all `36` Sahams computed deterministically)*.
