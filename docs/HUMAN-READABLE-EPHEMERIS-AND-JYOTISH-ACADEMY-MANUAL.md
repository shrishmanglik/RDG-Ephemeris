# RDG Ephemeris — Human-Readable Classical *Nirayana* & *Sayana* Ephemeris & Pt. Maheshji's Jyotish Academy Manual Calculation Compendium (2026-11)

> **For Practising Jyotishis, Positional Astronomers, Classical Researchers, and Students of Pt. Maheshji's Jyotish Academy:**
> Before computers existed, every master astrologer cast a *Kundali* (natal chart), *Shodashvarga* (16 divisional charts), *Panchanga* (5-limb daily almanac), *Vishesha Lagnas* (8 special ascendants), *Upagrahas* (11 shadow planets), *KP 249 Sub-Lords*, *Jaimini Arudha Padas & Chara Karakas*, *Vimshottari/Yogini/Ashtottari/Kalachakra Dashas*, *Shadbala* (6-fold planetary strength), *Ashtakavarga* (337-bindu transit grid), *Ayurdaya* (longevity), and *Tajika Varshphal* (annual solar return with 36 Sahams) **entirely by hand** using printed ephemeris tables. This 30-chapter master volume restores that unbroken lineage with sub-arcsecond NASA JPL DE440/DE441 astronomical precision.

### Master Document Metadata & Cryptographic Provenance Receipt
- **Ephemeris Month & Year:** `2026-11` (`30 Complete Chapters`)
- **Daily Tabular Reference Epoch:** `05:30:00 IST (00:00:00 UTC)`
- **Reference Meridian / Location:** Latitude `23.1765°`, Longitude `75.7885°` (UTC`+5.50h` — Ujjain Mahakaleshwar Prime Meridian)
- **Primary Sidereal Ayanamsha:** `lahiri` (Chitrapaksha / IAE 1989 Lahiri Standard + 25-Ayanamsha Conversion Table in Chapter 1)
- **Astronomical Kernel Backbone:** NASA JPL DE440 / DE441 + IAU 2006/2000A Precession-Nutation (`ephemeris-oss v0.2.0.dev1`)
- **Cryptographic SHA-256 Receipt:** `sha256:1c1f878f6ea66828da96dc3f58231bf3ee2d3bbf46555ec21fcaf60640ce11de`

## Chapter 1 — Fundamental Astronomical Constants, Julian Day Tables (`1900–2050`), ΔT, & 25-Ayanamsha Master Conversion Table

### Table 1A — Fundamental Astronomical & Vedic Siddhantic Constants

| Constant / Parameter | Exact Numerical Value | Classical / IAU Standard Reference |
|---|---|---|
| **J2000.0 Fundamental Epoch** | `JD 2451545.0 TT` (`2000-01-01 12:00:00 TT`) | IAU 2006 / 2000A Standard Epoch |
| **Kali Yuga Fundamental Epoch** | `JD 588465.5 UT` (`3102 BCE Feb 18 00:00 Ujjain`) | *Surya Siddhanta* & *Aryabhatiya* |
| **Astronomical Unit (`1 AU`)** | `149,597,870.700 km` (exact) | IAU 2012 Resolution B2 |
| **Speed of Light (`c`)** | `299,792.458 km/s` (`173.144632674 AU/day`) | IAU / SI Exact Constant |
| **Mean Obliquity at J2000.0 (`ε₀`)** | `23° 26' 21.406"` (`84381.406"`) | Capitaine et al. (2003) / IAU 2006 |
| **General Precession Rate (`p_A` at J2000)** | `50.28796195" / Julian year` (`1° in 71.5877 years`) | IAU 2006 Precession Model |
| **Mean Tropical Year (`Y_trop`)** | `365.24218967 days` (`365d 05h 48m 45.2s`) | Simon et al. (1994) |
| **Mean Sidereal Year (`Y_sid`)** | `365.256363004 days` (`365d 06h 09m 09.8s`) | IAU Standard Sidereal Year |
| **Surya Siddhanta Sidereal Year** | `365.25875648 days` (`365d 15g 31p 31.4v`) | `1,577,917,828 / 4,320,000` Savana days |
| **Mean Synodic Lunar Month** | `29.530588853 days` (`29d 12h 44m 02.9s`) | Mean New Moon to New Moon |
| **Mean Sidereal Lunar Month** | `27.321661547 days` (`27d 07h 43m 11.6s`) | `1 Nakshatra ≈ 24h 18m` |
| **Vedic Time Units (*Ghati / Pala / Vipala*)** | `1 Day = 60 Ghatis = 3,600 Palas = 216,000 Vipalas` | `1 Ghati = 24 min`, `1 Pala = 24 sec`, `1 Vipala = 0.4 sec` |

### Table 1B — Master 25-Ayanamsha Reference & Conversion Table (Evaluated at Epoch `2026-11-01 00:00 UTC`)

**How to Convert Any Position in This Compendium to Another Ayanamsha:** Every sidereal table in this book is printed in **Chitrapaksha / Lahiri (`IAE 1989`)**. To convert any longitude to another Ayanamsha, simply **subtract `Δ = (Target Ayanamsha − Lahiri Ayanamsha)`** listed in the column below:

| # | Ayanamsha Key | Canonical Name & Lineage | Value on `2026-11-01` (`DD° MM' SS"`) | Decimal (`deg`) | Offset vs Lahiri (`Δ = A − A_Lahiri`) | Precession / Anchor Model |
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
`JD = JD_Jan0.0(Year) + Month Offset (Table 1D) + Day of Month + (UTC Hours / 24)`

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

### Table 1D — Cumulative Month Day-Offsets & Historical `ΔT = TT − UT1` Table

| Month | Regular Year Offset | Leap Year (`*`) Offset | Historical Epoch | `ΔT = TT − UT1` (Seconds) | `ΔT` (Minutes) |
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
| `2026-11-10` | Mangalavara | `24° 13' 56"` | `08h 19m 50s` | **Tula 23° 21' 56"**<br/>Vishakha P2 (D/PN)<br/>`+01° 00' 18"/d` | **Vrishchika 01° 22' 43"**<br/>Vishakha P4 (D/C/PN)<br/>`+12° 16' 44"/d` | **Karka 28° 46' 47"**<br/>Ashlesha P4 (D)<br/>`+00° 28' 17"/d` | **Tula 12° 05' 19"**<br/>Swati P2 (R/C)<br/>`-00° 42' 13"/d` | **Simha 01° 05' 04"**<br/>Magha P1 (D)<br/>`+00° 05' 57"/d` | **Kanya 28° 57' 29"**<br/>Chitra P2 (R/V)<br/>`-00° 09' 51"/d` | **Meena 14° 32' 01"**<br/>Uttara Bhadrapada P4 (R/MB)<br/>`-00° 03' 06"/d` | **Kumbha 01° 21' 45"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Kumbha 01° 47' 46"**<br/>Dhanishta P3 (R)<br/>`-00° 14' 27"/d` | **Simha 01° 21' 45"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-11` | Budhavara | `24° 13' 56"` | `08h 23m 47s` | **Tula 24° 22' 15"**<br/>Vishakha P2 (D/PN)<br/>`+01° 00' 19"/d` | **Vrishchika 13° 34' 23"**<br/>Anuradha P4 (D/V/MB)<br/>`+12° 06' 43"/d` | **Karka 29° 14' 57"**<br/>Ashlesha P4 (D)<br/>`+00° 28' 03"/d` | **Tula 11° 28' 44"**<br/>Swati P2 (R)<br/>`-00° 30' 52"/d` | **Simha 01° 10' 57"**<br/>Magha P1 (D)<br/>`+00° 05' 48"/d` | **Kanya 28° 48' 51"**<br/>Chitra P2 (R/V)<br/>`-00° 07' 24"/d` | **Meena 14° 28' 57"**<br/>Uttara Bhadrapada P4 (R)<br/>`-00° 03' 01"/d` | **Kumbha 01° 18' 34"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Kumbha 01° 33' 36"**<br/>Dhanishta P3 (R)<br/>`-00° 13' 42"/d` | **Simha 01° 18' 34"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-12` | Guruvara | `24° 13' 56"` | `08h 27m 43s` | **Tula 25° 22' 35"**<br/>Vishakha P2 (D/PN)<br/>`+01° 00' 21"/d` | **Vrishchika 25° 36' 37"**<br/>Jyeshtha P3 (D)<br/>`+11° 57' 58"/d` | **Karka 29° 42' 53"**<br/>Ashlesha P4 (D)<br/>`+00° 27' 48"/d` | **Tula 11° 03' 43"**<br/>Swati P2 (R)<br/>`-00° 19' 10"/d` | **Simha 01° 16' 40"**<br/>Magha P1 (D)<br/>`+00° 05' 38"/d` | **Kanya 28° 42' 42"**<br/>Chitra P2 (R/V)<br/>`-00° 04' 56"/d` | **Meena 14° 25' 58"**<br/>Uttara Bhadrapada P4 (R)<br/>`-00° 02' 56"/d` | **Kumbha 01° 15' 23"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Kumbha 01° 20' 45"**<br/>Dhanishta P3 (R)<br/>`-00° 11' 50"/d` | **Simha 01° 15' 23"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-13` | Shukravara | `24° 13' 57"` | `08h 31m 40s` | **Tula 26° 22' 57"**<br/>Vishakha P2 (D/PN)<br/>`+01° 00' 23"/d` | **Dhanu 07° 31' 05"**<br/>Mula P3 (D)<br/>`+11° 51' 21"/d` | **Simha 00° 10' 34"**<br/>Magha P1 (D)<br/>`+00° 27' 33"/d` | **Tula 10° 50' 24"**<br/>Swati P2 (R)<br/>`-00° 07' 31"/d` | **Simha 01° 22' 14"**<br/>Magha P1 (D)<br/>`+00° 05' 28"/d` | **Kanya 28° 39' 00"**<br/>Chitra P2 (R/V)<br/>`-00° 02' 29"/d` | **Meena 14° 23' 05"**<br/>Uttara Bhadrapada P4 (R)<br/>`-00° 02' 51"/d` | **Kumbha 01° 12' 12"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Kumbha 01° 10' 10"**<br/>Dhanishta P3 (R)<br/>`-00° 09' 13"/d` | **Simha 01° 12' 12"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
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
| `2026-11-28` | Shanivara | `24° 13' 59"` | `09h 30m 48s` | **Vrishchika 11° 31' 06"**<br/>Anuradha P3 (D)<br/>`+01° 00' 43"/d` | **Mithuna 28° 50' 59"**<br/>Punarvasu P3 (D/V)<br/>`+14° 42' 32"/d` | **Simha 06° 33' 31"**<br/>Magha P2 (D)<br/>`+00° 23' 18"/d` | **Tula 23° 33' 12"**<br/>Vishakha P2 (D/PN)<br/>`+01° 22' 54"/d` | **Simha 02° 25' 22"**<br/>Magha P1 (D)<br/>`+00° 02' 53"/d` | **Tula 02° 12' 04"**<br/>Chitra P3 (D/V)<br/>`+00° 28' 51"/d` | **Meena 13° 50' 55"**<br/>Uttara Bhadrapada P4 (R)<br/>`-00° 01' 24"/d` | **Kumbha 00° 24' 31"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Makara 29° 40' 52"**<br/>Dhanishta P2 (R)<br/>`-00° 04' 12"/d` | **Simha 00° 24' 31"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-29` | Ravivara | `24° 13' 59"` | `09h 34m 45s` | **Vrishchika 12° 31' 50"**<br/>Anuradha P3 (D)<br/>`+01° 00' 45"/d` | **Karka 13° 23' 13"**<br/>Pushya P4 (D)<br/>`+14° 21' 32"/d` | **Simha 06° 56' 39"**<br/>Magha P3 (D)<br/>`+00° 22' 58"/d` | **Tula 24° 56' 55"**<br/>Vishakha P2 (D/PN)<br/>`+01° 24' 31"/d` | **Simha 02° 28' 10"**<br/>Magha P1 (D)<br/>`+00° 02' 42"/d` | **Tula 02° 41' 44"**<br/>Chitra P3 (D/V)<br/>`+00° 30' 29"/d` | **Meena 13° 49' 34"**<br/>Uttara Bhadrapada P4 (R)<br/>`-00° 01' 17"/d` | **Kumbha 00° 21' 20"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Makara 29° 37' 59"**<br/>Dhanishta P2 (R)<br/>`-00° 01' 41"/d` | **Simha 00° 21' 20"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |
| `2026-11-30` | Somavara | `24° 13' 59"` | `09h 38m 41s` | **Vrishchika 13° 32' 35"**<br/>Anuradha P4 (D/V)<br/>`+01° 00' 46"/d` | **Karka 27° 33' 17"**<br/>Ashlesha P4 (D)<br/>`+13° 58' 42"/d` | **Simha 07° 19' 27"**<br/>Magha P3 (D)<br/>`+00° 22' 37"/d` | **Tula 26° 22' 07"**<br/>Vishakha P2 (D/PN)<br/>`+01° 25' 52"/d` | **Simha 02° 30' 46"**<br/>Magha P1 (D)<br/>`+00° 02' 31"/d` | **Tula 03° 13' 01"**<br/>Chitra P3 (D/V)<br/>`+00° 32' 03"/d` | **Meena 13° 48' 19"**<br/>Uttara Bhadrapada P4 (R)<br/>`-00° 01' 11"/d` | **Kumbha 00° 18' 09"**<br/>Dhanishta P3 (R)<br/>`-00° 03' 11"/d` | **Makara 29° 37' 10"**<br/>Dhanishta P2 (S)<br/>`-00° 00' 08"/d` | **Simha 00° 18' 09"**<br/>Magha P1 (R)<br/>`-00° 03' 11"/d` |

### Table 2B — Daily Outer Planets (*Aruna / Uranus, Varuna / Neptune, Yama / Pluto*), Tropical (*Sayana*) Luminaries, & Second-Order Tabular Differences (`Δ²λ`)

| Date | Kali *Ahargana* | Tropical Sun (`λ_trop`) | Tropical Moon (`λ_trop`) | Uranus (*Aruna*) Sidereal | Neptune (*Varuna*) Sidereal | Pluto (*Yama*) Sidereal | Moon `Δ²λ` (`"/d²`) | Mercury `Δ²λ` (`"/d²`) | Venus `Δ²λ` (`"/d²`) | Mars `Δ²λ` (`"/d²`) |
|---|---|---|---|---|---|---|---|---|---|---|
| `2026-11-01` | `1872880.0` | `Vrishchika 08° 34' 29"` | `Karka 27° 28' 06"` | **Vrishabha 10° 26' 30"** (`-00° 02' 11"/d`) | **Meena 07° 50' 59"** (`-00° 01' 15"/d`) | **Makara 08° 53' 39"** (`+00° 00' 27"/d`) | `-924.2"` | `-403.1"` | `+103.2"` | `-11.7"` |
| `2026-11-02` | `1872881.0` | `Vrishchika 09° 34' 30"` | `Simha 11° 28' 06"` | **Vrishabha 10° 24' 19"** (`-00° 02' 13"/d`) | **Meena 07° 49' 44"** (`-00° 01' 14"/d`) | **Makara 08° 54' 07"** (`+00° 00' 29"/d`) | `-926.8"` | `-304.8"` | `+112.7"` | `-11.9"` |
| `2026-11-03` | `1872882.0` | `Vrishchika 10° 34' 33"` | `Simha 25° 12' 39"` | **Vrishabha 10° 22' 05"** (`-00° 02' 14"/d`) | **Meena 07° 48' 31"** (`-00° 01' 13"/d`) | **Makara 08° 54' 37"** (`+00° 00' 31"/d`) | `-868.2"` | `-183.4"` | `+120.9"` | `-12.2"` |
| `2026-11-04` | `1872883.0` | `Vrishchika 11° 34' 38"` | `Kanya 08° 42' 43"` | **Vrishabha 10° 19' 51"** (`-00° 02' 16"/d`) | **Meena 07° 47' 18"** (`-00° 01' 11"/d`) | **Makara 08° 55' 08"** (`+00° 00' 32"/d`) | `-787.2"` | `-44.5"` | `+128.0"` | `-12.5"` |
| `2026-11-05` | `1872884.0` | `Vrishchika 12° 34' 46"` | `Kanya 21° 59' 41"` | **Vrishabha 10° 17' 34"** (`-00° 02' 17"/d`) | **Meena 07° 46' 08"** (`-00° 01' 10"/d`) | **Makara 08° 55' 41"** (`+00° 00' 34"/d`) | `-713.6"` | `+103.9"` | `+133.9"` | `-12.7"` |
| `2026-11-06` | `1872885.0` | `Vrishchika 13° 34' 55"` | `Tula 05° 04' 45"` | **Vrishabha 10° 15' 17"** (`-00° 02' 18"/d`) | **Meena 07° 44' 58"** (`-00° 01' 08"/d`) | **Makara 08° 56' 16"** (`+00° 00' 36"/d`) | `-664.4"` | `+251.7"` | `+138.7"` | `-13.0"` |
| `2026-11-07` | `1872886.0` | `Vrishchika 14° 35' 07"` | `Tula 17° 58' 44"` | **Vrishabha 10° 12' 58"** (`-00° 02' 20"/d`) | **Meena 07° 43' 50"** (`-00° 01' 07"/d`) | **Makara 08° 56' 52"** (`+00° 00' 38"/d`) | `-642.4"` | `+388.7"` | `+142.4"` | `-13.3"` |
| `2026-11-08` | `1872887.0` | `Vrishchika 15° 35' 20"` | `Vrishchika 00° 42' 01"` | **Vrishabha 10° 10' 38"** (`-00° 02' 21"/d`) | **Meena 07° 42' 44"** (`-00° 01' 05"/d`) | **Makara 08° 57' 30"** (`+00° 00' 39"/d`) | `-639.0"` | `+506.0"` | `+145.1"` | `-13.6"` |
| `2026-11-09` | `1872888.0` | `Vrishchika 16° 35' 35"` | `Vrishchika 13° 14' 39"` | **Vrishabha 10° 08' 16"** (`-00° 02' 22"/d`) | **Meena 07° 41' 39"** (`-00° 01' 04"/d`) | **Makara 08° 58' 10"** (`+00° 00' 41"/d`) | `-638.0"` | `+597.4"` | `+146.8"` | `-13.8"` |
| `2026-11-10` | `1872889.0` | `Vrishchika 17° 35' 52"` | `Vrishchika 25° 36' 39"` | **Vrishabha 10° 05' 54"** (`-00° 02' 23"/d`) | **Meena 07° 40' 36"** (`-00° 01' 02"/d`) | **Makara 08° 58' 51"** (`+00° 00' 43"/d`) | `-619.8"` | `+660.1"` | `+147.8"` | `-14.1"` |
| `2026-11-11` | `1872890.0` | `Vrishchika 18° 36' 11"` | `Dhanu 07° 48' 20"` | **Vrishabha 10° 03' 30"** (`-00° 02' 24"/d`) | **Meena 07° 39' 34"** (`-00° 01' 01"/d`) | **Makara 08° 59' 34"** (`+00° 00' 44"/d`) | `-566.5"` | `+694.0"` | `+147.9"` | `-14.3"` |
| `2026-11-12` | `1872891.0` | `Vrishchika 19° 36' 31"` | `Dhanu 19° 50' 33"` | **Vrishabha 10° 01' 06"** (`-00° 02' 25"/d`) | **Meena 07° 38' 34"** (`-00° 00' 59"/d`) | **Makara 09° 00' 19"** (`+00° 00' 46"/d`) | `-465.1"` | `+702.0"` | `+147.4"` | `-14.6"` |
| `2026-11-13` | `1872892.0` | `Vrishchika 20° 36' 53"` | `Makara 01° 45' 02"` | **Vrishabha 09° 58' 40"** (`-00° 02' 26"/d`) | **Meena 07° 37' 35"** (`-00° 00' 57"/d`) | **Makara 09° 01' 05"** (`+00° 00' 47"/d`) | `-308.8"` | `+688.2"` | `+146.3"` | `-14.9"` |
| `2026-11-14` | `1872893.0` | `Vrishchika 21° 37' 17"` | `Makara 13° 34' 22"` | **Vrishabha 09° 56' 14"** (`-00° 02' 27"/d`) | **Meena 07° 36' 38"** (`-00° 00' 56"/d`) | **Makara 09° 01' 53"** (`+00° 00' 49"/d`) | `-97.2"` | `+657.6"` | `+144.7"` | `-15.1"` |
| `2026-11-15` | `1872894.0` | `Vrishchika 22° 37' 42"` | `Makara 25° 22' 04"` | **Vrishabha 09° 53' 47"** (`-00° 02' 28"/d`) | **Meena 07° 35' 43"** (`-00° 00' 54"/d`) | **Makara 09° 02' 42"** (`+00° 00' 51"/d`) | `+164.7"` | `+615.3"` | `+142.7"` | `-15.4"` |
| `2026-11-16` | `1872895.0` | `Vrishchika 23° 38' 08"` | `Kumbha 07° 12' 32"` | **Vrishabha 09° 51' 19"** (`-00° 02' 28"/d`) | **Meena 07° 34' 50"** (`-00° 00' 52"/d`) | **Makara 09° 03' 34"** (`+00° 00' 52"/d`) | `+466.9"` | `+565.7"` | `+140.2"` | `-15.7"` |
| `2026-11-17` | `1872896.0` | `Vrishchika 24° 38' 35"` | `Kumbha 19° 10' 46"` | **Vrishabha 09° 48' 51"** (`-00° 02' 29"/d`) | **Meena 07° 33' 58"** (`-00° 00' 51"/d`) | **Makara 09° 04' 26"** (`+00° 00' 54"/d`) | `+794.2"` | `+512.6"` | `+137.5"` | `-15.9"` |
| `2026-11-18` | `1872897.0` | `Vrishchika 25° 39' 04"` | `Meena 01° 22' 14"` | **Vrishabha 09° 46' 22"** (`-00° 02' 29"/d`) | **Meena 07° 33' 08"** (`-00° 00' 49"/d`) | **Makara 09° 05' 20"** (`+00° 00' 55"/d`) | `+1124.4"` | `+458.8"` | `+134.5"` | `-16.2"` |
| `2026-11-19` | `1872898.0` | `Vrishchika 26° 39' 35"` | `Meena 13° 52' 27"` | **Vrishabha 09° 43' 52"** (`-00° 02' 30"/d`) | **Meena 07° 32' 20"** (`-00° 00' 47"/d`) | **Makara 09° 06' 16"** (`+00° 00' 57"/d`) | `+1426.4"` | `+406.6"` | `+131.3"` | `-16.5"` |
| `2026-11-20` | `1872899.0` | `Vrishchika 27° 40' 06"` | `Meena 26° 46' 26"` | **Vrishabha 09° 41' 22"** (`-00° 02' 30"/d`) | **Meena 07° 31' 33"** (`-00° 00' 45"/d`) | **Makara 09° 07' 14"** (`+00° 00' 58"/d`) | `+1658.4"` | `+357.1"` | `+128.0"` | `-16.8"` |
| `2026-11-21` | `1872900.0` | `Vrishchika 28° 40' 39"` | `Mesha 10° 08' 04"` | **Vrishabha 09° 38' 52"** (`-00° 02' 31"/d`) | **Meena 07° 30' 49"** (`-00° 00' 43"/d`) | **Makara 09° 08' 13"** (`+00° 01' 00"/d`) | `+1770.1"` | `+311.5"` | `+124.6"` | `-17.1"` |
| `2026-11-22` | `1872901.0` | `Vrishchika 29° 41' 13"` | `Mesha 23° 59' 12"` | **Vrishabha 09° 36' 21"** (`-00° 02' 31"/d`) | **Meena 07° 30' 06"** (`-00° 00' 42"/d`) | **Makara 09° 09' 13"** (`+00° 01' 01"/d`) | `+1711.3"` | `+270.0"` | `+121.1"` | `-17.4"` |
| `2026-11-23` | `1872902.0` | `Dhanu 00° 41' 48"` | `Vrishabha 08° 18' 51"` | **Vrishabha 09° 33' 50"** (`-00° 02' 31"/d`) | **Meena 07° 29' 25"** (`-00° 00' 40"/d`) | **Makara 09° 10' 15"** (`+00° 01' 03"/d`) | `+1450.1"` | `+232.9"` | `+117.6"` | `-17.7"` |
| `2026-11-24` | `1872903.0` | `Dhanu 01° 42' 25"` | `Vrishabha 23° 02' 40"` | **Vrishabha 09° 31' 19"** (`-00° 02' 31"/d`) | **Meena 07° 28' 46"** (`-00° 00' 38"/d`) | **Makara 09° 11' 18"** (`+00° 01' 04"/d`) | `+994.7"` | `+199.9"` | `+114.0"` | `-18.1"` |
| `2026-11-25` | `1872904.0` | `Dhanu 02° 43' 03"` | `Mithuna 08° 03' 04"` | **Vrishabha 09° 28' 48"** (`-00° 02' 31"/d`) | **Meena 07° 28' 09"** (`-00° 00' 36"/d`) | **Makara 09° 12' 23"** (`+00° 01' 06"/d`) | `+406.1"` | `+171.0"` | `+110.4"` | `-18.4"` |
| `2026-11-26` | `1872905.0` | `Dhanu 03° 43' 42"` | `Mithuna 23° 10' 14"` | **Vrishabha 09° 26' 16"** (`-00° 02' 31"/d`) | **Meena 07° 27' 34"** (`-00° 00' 34"/d`) | **Makara 09° 13' 29"** (`+00° 01' 07"/d`) | `-212.5"` | `+145.8"` | `+106.8"` | `-18.8"` |
| `2026-11-27` | `1872906.0` | `Dhanu 04° 44' 23"` | `Karka 08° 13' 51"` | **Vrishabha 09° 23' 45"** (`-00° 02' 31"/d`) | **Meena 07° 27' 00"** (`-00° 00' 32"/d`) | **Makara 09° 14' 37"** (`+00° 01' 09"/d`) | `-751.2"` | `+123.9"` | `+103.1"` | `-19.3"` |
| `2026-11-28` | `1872907.0` | `Dhanu 05° 45' 05"` | `Karka 23° 04' 57"` | **Vrishabha 09° 21' 14"** (`-00° 02' 31"/d`) | **Meena 07° 26' 29"** (`-00° 00' 30"/d`) | **Makara 09° 15' 46"** (`+00° 01' 10"/d`) | `-1132.0"` | `+105.0"` | `+99.5"` | `-19.7"` |
| `2026-11-29` | `1872908.0` | `Dhanu 06° 45' 49"` | `Simha 07° 37' 11"` | **Vrishabha 09° 18' 42"** (`-00° 02' 31"/d`) | **Meena 07° 25' 59"** (`-00° 00' 28"/d`) | **Makara 09° 16' 57"** (`+00° 01' 12"/d`) | `-1329.3"` | `+88.8"` | `+95.8"` | `-20.2"` |
| `2026-11-30` | `1872909.0` | `Dhanu 07° 46' 34"` | `Simha 21° 47' 16"` | **Vrishabha 09° 16' 11"** (`-00° 02' 31"/d`) | **Meena 07° 25' 31"** (`-00° 00' 26"/d`) | **Makara 09° 18' 09"** (`+00° 01' 13"/d`) | `-1363.7"` | `+74.9"` | `+92.2"` | `-20.7"` |

## Chapter 3 — Daily Spherical & Physical Ephemeris Grid (Declination `δ`, Right Ascension `α`, Ecliptic Latitude `β`, Distance `R`, Parallax, Diameter, Phase & Magnitude)

**Why Spherical & Physical Coordinates Are Essential for Manual Jyotish:**
- **Declination (`δ` / *Kranti*):** Required to compute *Ayana Bala* in *Shadbala*, Parallel/Contra-Parallel Declination aspects (*Kranti Yoga*), and *Vyatipata / Vaidhriti Mahapata*.
- **Ecliptic Latitude (`β` / *Shara / Vikshepa*):** Required to adjudicate the winner of a *Graha Yuddha* (Planetary War — the planet with the more northern latitude wins) and *Nakshatra Tara Bheda*.
- **True Distance (`R` in AU), Horizontal Parallax (`HP`), Apparent Diameter (`"`), & Visual Magnitude (`V_mag`):** Required for topocentric Moon correction, eclipse contact sizing, and *Cheshta / Brihat Samhita* brightness diagnostics.

### Table 3A — Daily Declination (`δ` / *Kranti*) & Right Ascension (`α`) Across the *Navagrahas* (`05:30 IST`)

| Date | Sun `δ / α` | Moon `δ / α` | Mars `δ / α` | Mercury `δ / α` | Jupiter `δ / α` | Venus `δ / α` | Saturn `δ / α` | Rahu `δ` |
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

### Table 3B — Daily Ecliptic Latitude (`β` / *Shara*), Geocentric Distance (`R` in AU), Lunar Parallax (`HP`), Disk Illumination (`%`), & Visual Magnitude (`V_mag`)

| Date | Moon `β` (`DMS`) | Moon `HP` / Diam | Moon Illum `%` | Mars `β` / Dist (`AU`) / `V_mag` | Mercury `β` / Dist (`AU`) / `V_mag` | Jupiter `β` / Dist (`AU`) / `V_mag` | Venus `β` / Dist (`AU`) / `V_mag` | Saturn `β` / Dist (`AU`) / `V_mag` |
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

| Mahapata Type | Classical Condition | Peak Exact JD (`UT`) | Window Start (`JD UT`) | Window End (`JD UT`) | Sun Declination (`δ_Sun`) | Moon Declination (`δ_Moon`) |
|---|---|---|---|---|---|---|
| **Vaidhriti Mahapata** | `δ_Sun = -δ_Moon` (Opposite Hemisphere) | `2461347.20768` | `2461347.11724` | `2461347.29811` | `-14.9018°` | `+14.9018°` |
| **Vyatipata Mahapata** | `δ_Sun = +δ_Moon` (Same Hemisphere) | `2461360.79495` | `2461360.67755` | `2461360.91234` | `-18.7535°` | `-18.7535°` |
| **Vaidhriti Mahapata** | `δ_Sun = -δ_Moon` (Opposite Hemisphere) | `2461373.14836` | `2461373.03515` | `2461373.26156` | `-21.3758°` | `+21.3758°` |

## Chapter 5 — Section 2 — Daily Sunrise-Anchored *Drik Panchanga*, *Ghati-Pala* Almanac, & *Muhurta* Table

**Vedic Timekeeping Conversion:** `1 Solar Day = 24 Hours = 60 Ghatis (Nadis)`; `1 Hour = 2.5 Ghatis`; `1 Ghati = 24 Minutes = 60 Palas (Vinadis)`; `1 Pala = 24 Seconds`.

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
  `λ₁(t) = λ(05:30 IST) + f × v_day`, where `f = Δt_hours / 24 = ΔG_ghatis / 60`
- **Second-Order Quadratic Formula (For Sub-Arcsecond Manual Interpolation of the Fast-Moving Moon using Instantaneous Velocity `v_day`):**
  `λ₂(t) = λ₁(t) + (f² / 2) × Δ²λ`
  where `Δ²λ` is printed in **Table 2B** and the quadratic multiplier `B₂(f) = f² / 2` is printed in **Table 6A** below.

### Table 6A — Complete 96-Row 15-Minute (`00:00` to `24:00`) *Trairashika* Fraction (`f`), *Ghati-Pala*, & 2nd-Difference Coefficient (`B₂(f)`) Table

| Elapsed Time (`HH:MM`) | Elapsed *Ghati-Pala* | Fraction `f = Δt / 24` | Quadratic `B₂(f) = f² / 2` | Sun Incr (`+59'08"/d`) | Mean Moon Incr (`+13°10'35"/d`) | Elapsed Time (`HH:MM`) | Elapsed *Ghati-Pala* | Fraction `f = Δt / 24` | Quadratic `B₂(f) = f² / 2` | Sun Incr (`+59'08"/d`) | Mean Moon Incr (`+13°10'35"/d`) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `00:15` | `00g 38p` | **`0.01042`** | `+0.00005` | `+00° 00' 37"` | `+00° 08' 14"` | `12:15` | `30g 38p` | **`0.51042`** | `+0.13026` | `+00° 30' 11"` | `+06° 43' 32"` |
| `00:30` | `01g 15p` | **`0.02083`** | `+0.00022` | `+00° 01' 14"` | `+00° 16' 28"` | `12:30` | `31g 15p` | **`0.52083`** | `+0.13563` | `+00° 30' 48"` | `+06° 51' 46"` |
| `00:45` | `01g 52p` | **`0.03125`** | `+0.00049` | `+00° 01' 51"` | `+00° 24' 42"` | `12:45` | `31g 52p` | **`0.53125`** | `+0.14111` | `+00° 31' 25"` | `+07° 00' 00"` |
| `01:00` | `02g 30p` | **`0.04167`** | `+0.00087` | `+00° 02' 28"` | `+00° 32' 56"` | `13:00` | `32g 30p` | **`0.54167`** | `+0.14670` | `+00° 32' 02"` | `+07° 08' 14"` |
| `01:15` | `03g 08p` | **`0.05208`** | `+0.00136` | `+00° 03' 05"` | `+00° 41' 11"` | `13:15` | `33g 08p` | **`0.55208`** | `+0.15240` | `+00° 32' 39"` | `+07° 16' 28"` |
| `01:30` | `03g 45p` | **`0.06250`** | `+0.00195` | `+00° 03' 42"` | `+00° 49' 25"` | `13:30` | `33g 45p` | **`0.56250`** | `+0.15820` | `+00° 33' 16"` | `+07° 24' 42"` |
| `01:45` | `04g 22p` | **`0.07292`** | `+0.00266` | `+00° 04' 19"` | `+00° 57' 39"` | `13:45` | `34g 22p` | **`0.57292`** | `+0.16412` | `+00° 33' 53"` | `+07° 32' 56"` |
| `02:00` | `05g 00p` | **`0.08333`** | `+0.00347` | `+00° 04' 56"` | `+01° 05' 53"` | `14:00` | `35g 00p` | **`0.58333`** | `+0.17014` | `+00° 34' 30"` | `+07° 41' 10"` |
| `02:15` | `05g 38p` | **`0.09375`** | `+0.00439` | `+00° 05' 33"` | `+01° 14' 07"` | `14:15` | `35g 38p` | **`0.59375`** | `+0.17627` | `+00° 35' 07"` | `+07° 49' 25"` |
| `02:30` | `06g 15p` | **`0.10417`** | `+0.00543` | `+00° 06' 10"` | `+01° 22' 21"` | `14:30` | `36g 15p` | **`0.60417`** | `+0.18251` | `+00° 35' 44"` | `+07° 57' 39"` |
| `02:45` | `06g 52p` | **`0.11458`** | `+0.00656` | `+00° 06' 47"` | `+01° 30' 35"` | `14:45` | `36g 52p` | **`0.61458`** | `+0.18886` | `+00° 36' 21"` | `+08° 05' 53"` |
| `03:00` | `07g 30p` | **`0.12500`** | `+0.00781` | `+00° 07' 23"` | `+01° 38' 49"` | `15:00` | `37g 30p` | **`0.62500`** | `+0.19531` | `+00° 36' 57"` | `+08° 14' 07"` |
| `03:15` | `08g 08p` | **`0.13542`** | `+0.00917` | `+00° 08' 00"` | `+01° 47' 03"` | `15:15` | `38g 08p` | **`0.63542`** | `+0.20188` | `+00° 37' 34"` | `+08° 22' 21"` |
| `03:30` | `08g 45p` | **`0.14583`** | `+0.01063` | `+00° 08' 37"` | `+01° 55' 18"` | `15:30` | `38g 45p` | **`0.64583`** | `+0.20855` | `+00° 38' 11"` | `+08° 30' 35"` |
| `03:45` | `09g 22p` | **`0.15625`** | `+0.01221` | `+00° 09' 14"` | `+02° 03' 32"` | `15:45` | `39g 22p` | **`0.65625`** | `+0.21533` | `+00° 38' 48"` | `+08° 38' 49"` |
| `04:00` | `10g 00p` | **`0.16667`** | `+0.01389` | `+00° 09' 51"` | `+02° 11' 46"` | `16:00` | `40g 00p` | **`0.66667`** | `+0.22222` | `+00° 39' 25"` | `+08° 47' 03"` |
| `04:15` | `10g 38p` | **`0.17708`** | `+0.01568` | `+00° 10' 28"` | `+02° 20' 00"` | `16:15` | `40g 38p` | **`0.67708`** | `+0.22922` | `+00° 40' 02"` | `+08° 55' 17"` |
| `04:30` | `11g 15p` | **`0.18750`** | `+0.01758` | `+00° 11' 05"` | `+02° 28' 14"` | `16:30` | `41g 15p` | **`0.68750`** | `+0.23633` | `+00° 40' 39"` | `+09° 03' 32"` |
| `04:45` | `11g 52p` | **`0.19792`** | `+0.01959` | `+00° 11' 42"` | `+02° 36' 28"` | `16:45` | `41g 52p` | **`0.69792`** | `+0.24354` | `+00° 41' 16"` | `+09° 11' 46"` |
| `05:00` | `12g 30p` | **`0.20833`** | `+0.02170` | `+00° 12' 19"` | `+02° 44' 42"` | `17:00` | `42g 30p` | **`0.70833`** | `+0.25087` | `+00° 41' 53"` | `+09° 20' 00"` |
| `05:15` | `13g 08p` | **`0.21875`** | `+0.02393` | `+00° 12' 56"` | `+02° 52' 56"` | `17:15` | `43g 08p` | **`0.71875`** | `+0.25830` | `+00° 42' 30"` | `+09° 28' 14"` |
| `05:30` | `13g 45p` | **`0.22917`** | `+0.02626` | `+00° 13' 33"` | `+03° 01' 11"` | `17:30` | `43g 45p` | **`0.72917`** | `+0.26584` | `+00° 43' 07"` | `+09° 36' 28"` |
| `05:45` | `14g 22p` | **`0.23958`** | `+0.02870` | `+00° 14' 10"` | `+03° 09' 25"` | `17:45` | `44g 22p` | **`0.73958`** | `+0.27349` | `+00° 43' 44"` | `+09° 44' 42"` |
| `06:00` | `15g 00p` | **`0.25000`** | `+0.03125` | `+00° 14' 47"` | `+03° 17' 39"` | `18:00` | `45g 00p` | **`0.75000`** | `+0.28125` | `+00° 44' 21"` | `+09° 52' 56"` |
| `06:15` | `15g 38p` | **`0.26042`** | `+0.03391` | `+00° 15' 24"` | `+03° 25' 53"` | `18:15` | `45g 38p` | **`0.76042`** | `+0.28912` | `+00° 44' 58"` | `+10° 01' 10"` |
| `06:30` | `16g 15p` | **`0.27083`** | `+0.03668` | `+00° 16' 01"` | `+03° 34' 07"` | `18:30` | `46g 15p` | **`0.77083`** | `+0.29709` | `+00° 45' 35"` | `+10° 09' 24"` |
| `06:45` | `16g 52p` | **`0.28125`** | `+0.03955` | `+00° 16' 38"` | `+03° 42' 21"` | `18:45` | `46g 52p` | **`0.78125`** | `+0.30518` | `+00° 46' 12"` | `+10° 17' 39"` |
| `07:00` | `17g 30p` | **`0.29167`** | `+0.04253` | `+00° 17' 15"` | `+03° 50' 35"` | `19:00` | `47g 30p` | **`0.79167`** | `+0.31337` | `+00° 46' 49"` | `+10° 25' 53"` |
| `07:15` | `18g 08p` | **`0.30208`** | `+0.04563` | `+00° 17' 52"` | `+03° 58' 49"` | `19:15` | `48g 08p` | **`0.80208`** | `+0.32167` | `+00° 47' 26"` | `+10° 34' 07"` |
| `07:30` | `18g 45p` | **`0.31250`** | `+0.04883` | `+00° 18' 29"` | `+04° 07' 03"` | `19:30` | `48g 45p` | **`0.81250`** | `+0.33008` | `+00° 48' 03"` | `+10° 42' 21"` |
| `07:45` | `19g 22p` | **`0.32292`** | `+0.05214` | `+00° 19' 06"` | `+04° 15' 18"` | `19:45` | `49g 22p` | **`0.82292`** | `+0.33860` | `+00° 48' 40"` | `+10° 50' 35"` |
| `08:00` | `20g 00p` | **`0.33333`** | `+0.05556` | `+00° 19' 43"` | `+04° 23' 32"` | `20:00` | `50g 00p` | **`0.83333`** | `+0.34722` | `+00° 49' 17"` | `+10° 58' 49"` |
| `08:15` | `20g 38p` | **`0.34375`** | `+0.05908` | `+00° 20' 20"` | `+04° 31' 46"` | `20:15` | `50g 38p` | **`0.84375`** | `+0.35596` | `+00° 49' 54"` | `+11° 07' 03"` |
| `08:30` | `21g 15p` | **`0.35417`** | `+0.06272` | `+00° 20' 57"` | `+04° 40' 00"` | `20:30` | `51g 15p` | **`0.85417`** | `+0.36480` | `+00° 50' 31"` | `+11° 15' 17"` |
| `08:45` | `21g 52p` | **`0.36458`** | `+0.06646` | `+00° 21' 34"` | `+04° 48' 14"` | `20:45` | `51g 52p` | **`0.86458`** | `+0.37375` | `+00° 51' 08"` | `+11° 23' 32"` |
| `09:00` | `22g 30p` | **`0.37500`** | `+0.07031` | `+00° 22' 10"` | `+04° 56' 28"` | `21:00` | `52g 30p` | **`0.87500`** | `+0.38281` | `+00° 51' 44"` | `+11° 31' 46"` |
| `09:15` | `23g 08p` | **`0.38542`** | `+0.07427` | `+00° 22' 47"` | `+05° 04' 42"` | `21:15` | `53g 08p` | **`0.88542`** | `+0.39198` | `+00° 52' 21"` | `+11° 40' 00"` |
| `09:30` | `23g 45p` | **`0.39583`** | `+0.07834` | `+00° 23' 24"` | `+05° 12' 56"` | `21:30` | `53g 45p` | **`0.89583`** | `+0.40126` | `+00° 52' 58"` | `+11° 48' 14"` |
| `09:45` | `24g 22p` | **`0.40625`** | `+0.08252` | `+00° 24' 01"` | `+05° 21' 10"` | `21:45` | `54g 22p` | **`0.90625`** | `+0.41064` | `+00° 53' 35"` | `+11° 56' 28"` |
| `10:00` | `25g 00p` | **`0.41667`** | `+0.08681` | `+00° 24' 38"` | `+05° 29' 25"` | `22:00` | `55g 00p` | **`0.91667`** | `+0.42014` | `+00° 54' 12"` | `+12° 04' 42"` |
| `10:15` | `25g 38p` | **`0.42708`** | `+0.09120` | `+00° 25' 15"` | `+05° 37' 39"` | `22:15` | `55g 38p` | **`0.92708`** | `+0.42974` | `+00° 54' 49"` | `+12° 12' 56"` |
| `10:30` | `26g 15p` | **`0.43750`** | `+0.09570` | `+00° 25' 52"` | `+05° 45' 53"` | `22:30` | `56g 15p` | **`0.93750`** | `+0.43945` | `+00° 55' 26"` | `+12° 21' 10"` |
| `10:45` | `26g 52p` | **`0.44792`** | `+0.10031` | `+00° 26' 29"` | `+05° 54' 07"` | `22:45` | `56g 52p` | **`0.94792`** | `+0.44927` | `+00° 56' 03"` | `+12° 29' 24"` |
| `11:00` | `27g 30p` | **`0.45833`** | `+0.10503` | `+00° 27' 06"` | `+06° 02' 21"` | `23:00` | `57g 30p` | **`0.95833`** | `+0.45920` | `+00° 56' 40"` | `+12° 37' 39"` |
| `11:15` | `28g 08p` | **`0.46875`** | `+0.10986` | `+00° 27' 43"` | `+06° 10' 35"` | `23:15` | `58g 08p` | **`0.96875`** | `+0.46924` | `+00° 57' 17"` | `+12° 45' 53"` |
| `11:30` | `28g 45p` | **`0.47917`** | `+0.11480` | `+00° 28' 20"` | `+06° 18' 49"` | `23:30` | `58g 45p` | **`0.97917`** | `+0.47938` | `+00° 57' 54"` | `+12° 54' 07"` |
| `11:45` | `29g 22p` | **`0.48958`** | `+0.11985` | `+00° 28' 57"` | `+06° 27' 03"` | `23:45` | `59g 22p` | **`0.98958`** | `+0.48964` | `+00° 58' 31"` | `+13° 02' 21"` |
| `12:00` | `30g 00p` | **`0.50000`** | `+0.12500` | `+00° 29' 34"` | `+06° 35' 18"` | `24:00` | `60g 00p` | **`1.00000`** | `+0.50000` | `+00° 59' 08"` | `+13° 10' 35"` |

## Chapter 7 — Master Tables of Ascendants (*Udaya Lagna*), 10th House Midheaven (*Madhya Lagna*), & *Sripathi Bhava Chalit* Across World Latitudes

**How to Find the Exact Sidereal Ascendant (*Udaya Lagna*) and 10th Cusp (*Madhya Lagna*) from Table 7A:**
1. Take the **Local Sidereal Time (LST)** at `05:30 IST` from **Table 2A** (already computed for the compendium reference meridian `75.7885°`).
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
| **2** | **Hora Lagna (HL)** | `0.5° per min` (`1 sign per Hora`) | `HL = λ_Sun(Sunrise) + (Elapsed Minutes since Sunrise / 2.0)` | Personal wealth, sustenance, liquid resources, financial inflow |
| **3** | **Ghati Lagna (GL)** | `1.25° per min` (`1 sign per Ghati`) | `GL = λ_Sun(Sunrise) + (Elapsed Ghatis since Sunrise × 30°)` | Power, royal authority, political/executive rank, fame |
| **4** | **Bhava Lagna (BL)** | `0.25° per min` (`1 sign per 5 Ghatis`) | `BL = λ_Sun(Sunrise) + (Elapsed Ghatis since Sunrise × 6°)` | Inner psychological disposition and bodily constitution |
| **5** | **Sree Lagna (SL)** | Linked to Moon's Pada | `SL = λ_Udaya_Lagna + ((λ_Moon mod 13°20') / 13°20') × 360°` | Goddess Lakshmi's grace, prosperity, marriage fortune |
| **6** | **Indu Lagna (IL)** | Planetary *Kala* Sum | Sum *Kalas* (`Sun 30, Moon 16, Mars 6, Mercury 8, Jupiter 10, Venus 12, Saturn 1`) of 9th Lord from Lagna + 9th Lord from Moon; take `Sum mod 12` (`0 -> 12`) and count that many signs from Natal Moon | Millionaire/billionaire *Dhana Yogas* and windfall wealth Dasha triggers |
| **7** | **Pranapada Lagna (PL)** | `2° per Pala` (`1 sign per 15 Palas`) | `PL = λ_Sun + ((Elapsed Palas since Sunrise / 15) × 30°) + Offset` (`0°` Movable, `240°` Fixed, `120°` Dual Solar Sign) | Birth-time rectification (must fall in trine/10th to Moon or Lagna) |
| **8** | **Varnada Lagna (VL)** | Sign-Parity Vector | Count Udaya Lagna & Hora Lagna from Mesha (if Odd) or Meena backwards (if Even); add if same parity, subtract if opposite parity | Social class, vocational calling, and public duty |

### Table 8B — Complete Manual Formulas for the 5 Solar *Upagrahas* & 6 *Kalavela* Time-of-Day *Upagrahas* (*Gulika/Mandi*)

| Category | Upagraha Name | Ruling Planet | Exact Manual Calculation Formula | Daytime Octant (`Sun..Sat`, out of 8) | Nighttime Octant (`Sun..Sat`, out of 8) |
|---|---|---|---|---|---|
| **Solar Upagraha 1** | **Dhuma** | Mars (Fiery Smoke) | `λ_Dhuma = (λ_Sun + 133° 20') mod 360°` | Instantaneous from `λ_Sun` | Instantaneous from `λ_Sun` |
| **Solar Upagraha 2** | **Vyatipata** | Rahu (Calamity) | `λ_Vyatipata = (360° - λ_Dhuma) mod 360°` | Instantaneous from `λ_Sun` | Instantaneous from `λ_Sun` |
| **Solar Upagraha 3** | **Parivesha** | Moon (Halo) | `λ_Parivesha = (λ_Vyatipata + 180°) mod 360°` | Instantaneous from `λ_Sun` | Instantaneous from `λ_Sun` |
| **Solar Upagraha 4** | **Indrachapa (Kodanda)** | Venus (Rainbow Bow) | `λ_Indrachapa = (360° - λ_Parivesha) mod 360°` | Instantaneous from `λ_Sun` | Instantaneous from `λ_Sun` |
| **Solar Upagraha 5** | **Upaketu (Sikhi)** | Ketu (Comet Crest) | `λ_Upaketu = (λ_Indrachapa + 16° 40') mod 360° = (λ_Sun - 30°)` | Instantaneous from `λ_Sun` | Instantaneous from `λ_Sun` |
| **Kalavela 1** | **Gulika (Mandi)** | Saturn's Son | Ascendant rising at start of Saturn's 1/8th portion of *Dinamana* / *Ratrimana* | `Sun:7, Mon:6, Tue:5, Wed:4, Thu:3, Fri:2, Sat:1` | `Sun:3, Mon:2, Tue:1, Wed:7, Thu:6, Fri:5, Sat:4` |
| **Kalavela 2** | **Kala** | Sun's Portion | Ascendant rising at start of Sun's 1/8th portion | `Sun:1, Mon:7, Tue:6, Wed:5, Thu:4, Fri:3, Sat:2` | `Sun:4, Mon:3, Tue:2, Wed:1, Thu:7, Fri:6, Sat:5` |
| **Kalavela 3** | **Mrityu** | Mars's Portion | Ascendant rising at start of Mars's 1/8th portion | `Sun:3, Mon:2, Tue:1, Wed:7, Thu:6, Fri:5, Sat:4` | `Sun:6, Mon:5, Tue:4, Wed:3, Thu:2, Fri:1, Sat:7` |
| **Kalavela 4** | **Ardhaprahara** | Mercury's Portion | Ascendant rising at start of Mercury's 1/8th portion | `Sun:4, Mon:3, Tue:2, Wed:1, Thu:7, Fri:6, Sat:5` | `Sun:7, Mon:6, Tue:5, Wed:4, Thu:3, Fri:2, Sat:1` |
| **Kalavela 5** | **Yamaghantaka** | Jupiter's Portion | Ascendant rising at start of Jupiter's 1/8th portion | `Sun:5, Mon:4, Tue:3, Wed:2, Thu:1, Fri:7, Sat:6` | `Sun:1, Mon:7, Tue:6, Wed:5, Thu:4, Fri:3, Sat:2` |

### Table 8C — Complete Manual Formulas for *Yogi / Sahayogi / Avayogi* & the 9 Kerala *Prashna Marga Sphutas*

| Sensitive Point (*Sphuta*) | Exact Mathematical Formula (`Mod 360°`) | Classical Interpretation Rule (*Prashna Marga* & *BPHS*) |
|---|---|---|
| **Yogi Point & Yogi Planet** | `λ_Yogi = (λ_Sun + λ_Moon + 93° 20') mod 360°` | Nakshatra Lord of `λ_Yogi` is **Yogi Planet** (supreme prosperity significator); Sign Lord is **Sahayogi** |
| **Avayogi Point & Planet** | `λ_Avayogi = (λ_Yogi + 186° 40') mod 360°` | Nakshatra Lord of `λ_Avayogi` is **Avayogi Planet** (obstruction/drain significator) |
| **1. Trisphuta** | `(λ_Lagna + λ_Moon + λ_Gulika) mod 360°` | Core vitality, health, and immediate horary crisis indicator |
| **2. Chatusphuta** | `(λ_Trisphuta + λ_Sun) mod 360°` | Soul-level endurance and royal/spiritual support |
| **3. Panchasphuta** | `(λ_Chatusphuta + λ_Rahu) mod 360°` | Karmic destiny and hidden snakes/curses in Prashna |
| **4. Prana Sphuta** | `(5 × λ_Lagna + λ_Gulika) mod 360°` | Vital breath (*Prana*) — conjunction with Mrityu Sphuta indicates acute danger |
| **5. Deha Sphuta** | `(8 × λ_Moon + λ_Gulika) mod 360°` | Physical body resilience and recovery capacity |
| **6. Mrityu Sphuta** | `(7 × λ_Gulika + λ_Sun) mod 360°` | Mortality / critical vulnerability point |
| **7. Tithi Sphuta** | `(λ_Lagna + (λ_Moon - λ_Sun)) mod 360°` | Lunar-phase harmony in relationships and undertakings |
| **8. Beeja Sphuta (Male)** | `(λ_Sun + λ_Venus + λ_Jupiter) mod 360°` | Male virility and progeny seed strength (must occupy odd signs/navamsas with benefic aspect) |
| **9. Kshetra Sphuta (Female)** | `(λ_Moon + λ_Mars + λ_Jupiter) mod 360°` | Female fertility and womb strength (must occupy even signs/navamsas with benefic aspect) |

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
| **Navamsa 8** | `23° 20' – 26° 40'` | `1400'–1600'` | **Vrishchika** | **Simha** | **Vrishabha** *PN* | **Kumbha** |
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
| **Level A (1st Order)** | Highest (`4x`) | Planet(s) occupying the **Nakshatra (Star)** of the Occupants of House `H` | Strongest driver of the event when its Dasha/Bhukti/Antara runs |
| **Level B (2nd Order)** | High (`3x`) | Planet(s) directly **occupying** House `H` in the *Placidus Bhava Chalit* chart | Delivers the house result directly unless vacated by Star tenants |
| **Level C (3rd Order)** | Moderate (`2x`) | Planet(s) occupying the **Nakshatra (Star)** of the Cusp Sign Lord of House `H` | Activates the house promise through stellar rulership over the cusp lord |
| **Level D (4th Order)** | Baseline (`1x`) | The **Sign Lord** of the Cusp of House `H` itself | Background significator; strong when untenanted in both house and star |
| **Cuspal Sub-Lord Gate** | **Decider** | The **Sub-Lord (`#001–#249`)** of Cusp `H` | **The Star Lord shows the nature of the involvement; the Sub-Lord decides YES or NO** |

## Chapter 12 — Section 5 — Complete Manual Dasha Balance & Multi-System *Dasha* Compendium (*Vimshottari, Yogini, Ashtottari, & Kalachakra*)

**Classical Formula for Balance of Dasha at Birth (*Bhogyamsha*):**
- Each Nakshatra spans `13° 20' = 800 arcminutes` (`4 Padas × 200' = 800'`).
- If the Natal Moon is at `λ_Moon`, find its elapsed arcminutes inside the current Nakshatra (`G_elapsed`) and the remaining arcminutes to complete the Nakshatra (`B_rem = 800' - G_elapsed`).
- `Balance of Mahadasha at Birth (Years) = Y_Mahadasha × (800' - G_elapsed) / 800'`

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

**Manual Antardasha (Bhukti) Formula:** Multiply the Mahadasha years by the Antardasha years and divide by 10 to obtain total months (`Total Months = (Y_MD × Y_AD) / 10`); divide integer months by 12 for years and remaining months, and multiply any fractional month by **30** (`Days = Fractional Month × 30`) to obtain days.

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

| Yogini # | Yogini Name | Planetary Ruler | Duration (`Years`) | Starting Nakshatra Rule `(N + 3) mod 8` | Ashtottari # | Ashtottari Lord | Duration (`Years`) | Assigned 28-Nakshatra Group |
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

| Cycle Group | Nakshatra Triad | Pada | *Dehamsha* (Body Sign) | *Jeevamsha* (Soul Sign) | Total Cycle (`Paramayus`) | 9-Sign *Kalachakra* Progression Sequence |
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
| **Apasavya 1** | Rohini, Magha, Vishakha, Shravana (I) | **Pada 1** | **Meena** | **Vrishchika** | `100 Years` | Vrishchika → Tula → Kanya → Karka → Simha → Mithuna → Vrishabha → Mesha → Meena |
| **Apasavya 1** | Rohini, Magha, Vishakha, Shravana (I) | **Pada 2** | **Kanya** | **Kumbha** | `85 Years` | Kumbha → Makara → Dhanu → Mesha → Vrishabha → Mithuna → Karka → Simha → Kanya |
| **Apasavya 1** | Rohini, Magha, Vishakha, Shravana (I) | **Pada 3** | **Kanya** | **Tula** | `83 Years` | Tula → Vrishchika → Meena → Kumbha → Makara → Dhanu → Vrishchika → Tula → Kanya |
| **Apasavya 1** | Rohini, Magha, Vishakha, Shravana (I) | **Pada 4** | **Dhanu** | **Karka** | `86 Years` | Karka → Simha → Mithuna → Vrishabha → Mesha → Meena → Kumbha → Makara → Dhanu |
| **Apasavya 2** | Mrigashirsha, P.Phalguni, Anuradha, Dhanishta (II) | **Pada 1** | **Karka** | **Dhanu** | `86 Years` | Dhanu → Makara → Kumbha → Meena → Mesha → Vrishabha → Mithuna → Simha → Karka |
| **Apasavya 2** | Mrigashirsha, P.Phalguni, Anuradha, Dhanishta (II) | **Pada 2** | **Tula** | **Kanya** | `83 Years` | Kanya → Tula → Vrishchika → Meena → Kumbha → Makara → Dhanu → Vrishchika → Tula |
| **Apasavya 2** | Mrigashirsha, P.Phalguni, Anuradha, Dhanishta (II) | **Pada 3** | **Kumbha** | **Kanya** | `85 Years` | Kanya → Simha → Karka → Mithuna → Vrishabha → Mesha → Dhanu → Makara → Kumbha |
| **Apasavya 2** | Mrigashirsha, P.Phalguni, Anuradha, Dhanishta (II) | **Pada 4** | **Vrishchika** | **Meena** | `100 Years` | Meena → Mesha → Vrishabha → Mithuna → Simha → Karka → Kanya → Tula → Vrishchika |
| **Apasavya 3** | Ardra, U.Phalguni, Jyeshtha, Shatabhisha (III) | **Pada 1** | **Karka** | **Meena** | `86 Years` | Meena → Kumbha → Makara → Dhanu → Vrishchika → Tula → Kanya → Simha → Karka |
| **Apasavya 3** | Ardra, U.Phalguni, Jyeshtha, Shatabhisha (III) | **Pada 2** | **Vrishabha** | **Mithuna** | `83 Years` | Mithuna → Vrishabha → Mesha → Dhanu → Makara → Kumbha → Meena → Mesha → Vrishabha |
| **Apasavya 3** | Ardra, U.Phalguni, Jyeshtha, Shatabhisha (III) | **Pada 3** | **Makara** | **Mithuna** | `85 Years` | Mithuna → Simha → Karka → Kanya → Tula → Vrishchika → Meena → Kumbha → Makara |
| **Apasavya 3** | Ardra, U.Phalguni, Jyeshtha, Shatabhisha (III) | **Pada 4** | **Mesha** | **Dhanu** | `100 Years` | Dhanu → Vrishchika → Tula → Kanya → Simha → Karka → Mithuna → Vrishabha → Mesha |

## Chapter 13 — Complete *Jaimini Upadesha Sutras* Manual Compendium (*Chara Karakas*, *Arudha Padas*, *Rashi Drishti*, *Argala*, & *Jaimini Ayurdaya*)

### Table 13A — Complete 144-Cell `12 × 12` *Jaimini Arudha Pada* (*Swastha* 1st/7th Exception Included) Master Lookup Matrix

**How to Read This Table:** Find the **Sign of the House (`H`)** in the left column, and the **Sign Occupied by Its Lord (`L`)** across the top row. The cell gives the **exact Arudha Pada Sign** (automatically applying the Jaimini *Swastha* rule: when the projected Arudha lands in the 1st or 7th from the house, the Arudha jumps 10 signs from the raw position).

| House Sign \ Lord Sign | **Mesha** | **Vrish** | **Mithu** | **Karka** | **Simha** | **Kanya** | **Tula** | **Vrish** | **Dhanu** | **Makar** | **Kumbh** | **Meena** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **01 Mesha** | **Makar*** | Mithu | Simha | **Karka*** | Dhanu | Kumbh | **Makar*** | Mithu | Simha | **Karka*** | Dhanu | Kumbh |
| **02 Vrishabha** | Meena | **Kumbh*** | Karka | Kanya | **Simha*** | Makar | Meena | **Kumbh*** | Karka | Kanya | **Simha*** | Makar |
| **03 Mithuna** | Kumbh | Mesha | **Meena*** | Simha | Tula | **Kanya*** | Kumbh | Mesha | **Meena*** | Simha | Tula | **Kanya*** |
| **04 Karka** | **Tula*** | Meena | Vrish | **Mesha*** | Kanya | Vrish | **Tula*** | Meena | Vrish | **Mesha*** | Kanya | Vrish |
| **05 Simha** | Dhanu | **Vrish*** | Mesha | Mithu | **Vrish*** | Tula | Dhanu | **Vrish*** | Mesha | Mithu | **Vrish*** | Tula |
| **06 Kanya** | Vrish | Makar | **Dhanu*** | Vrish | Karka | **Mithu*** | Vrish | Makar | **Dhanu*** | Vrish | Karka | **Mithu*** |
| **07 Tula** | **Karka*** | Dhanu | Kumbh | **Makar*** | Mithu | Simha | **Karka*** | Dhanu | Kumbh | **Makar*** | Mithu | Simha |
| **08 Vrishchika** | Kanya | **Simha*** | Makar | Meena | **Kumbh*** | Karka | Kanya | **Simha*** | Makar | Meena | **Kumbh*** | Karka |
| **09 Dhanu** | Simha | Tula | **Kanya*** | Kumbh | Mesha | **Meena*** | Simha | Tula | **Kanya*** | Kumbh | Mesha | **Meena*** |
| **10 Makara** | **Mesha*** | Kanya | Vrish | **Tula*** | Meena | Vrish | **Mesha*** | Kanya | Vrish | **Tula*** | Meena | Vrish |
| **11 Kumbha** | Mithu | **Vrish*** | Tula | Dhanu | **Vrish*** | Mesha | Mithu | **Vrish*** | Tula | Dhanu | **Vrish*** | Mesha |
| **12 Meena** | Vrish | Karka | **Mithu*** | Vrish | Makar | **Dhanu*** | Vrish | Karka | **Mithu*** | Vrish | Makar | **Dhanu*** |

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
| **Rahu / Ketu** | **Durga / Ganesha** | 8-Karaka Scheme (`Rahu` at `30° - d`) | *Moksha Karaka* (`Ketu` in 12th from *Karakamsa*) | — | Ketu in 4th/8th/12th from *Karakamsa* grants final liberation |

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

**Classical Piecewise Formula (*Brihat Parashara Hora Shastra*):** Let `Δ = (λ_Target - λ_Aspecting) mod 360°`. Base *Drishti* is `0v` for `0°..30°` and `300°..360°`; rises from `30°..60°` (`(Δ-30)/2`); rises from `60°..90°` (`(Δ-60)+15`); drops from `90°..120°` (`45-(Δ-90)/2`); drops from `120°..150°` (`30-(Δ-120)`); rises sharply from `150°..180°` (`2*(Δ-150)` peaking at `60v` at `180°`); and decreases linearly from `180°..300°` (`(300-Δ)/2`). **Special Vishesha Drishti:** Mars gets `60v` across `90°..120°` & `210°..240°`; Jupiter gets `60v` across `120°..150°` & `240°..270°`; Saturn gets `60v` across `60°..90°` & `270°..300°`.

| Separation `Δ` | House Span | Standard (*Sun, Moon, Mer, Ven*) | Mars (*4th & 8th Vishesha*) | Jupiter (*5th & 9th Vishesha*) | Saturn (*3rd & 10th Vishesha*) |
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
| **Saturn** | ``20° Tula (200°)`` | **`20 Years`** | **`50 Years`** | **Exempt** (Saturn & Venus never lose years by combustion) | Lose **`1/3` (`33.3%`)** in Enemy Sign (Exempt if Retrograde) | **Amsayu Rule:** Total Elapsed Arcminutes `÷ 200' mod 12 =` Base Years (multiplied by `2×` or `3×` in Own/Exalted Rashi or D9) |

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

**Universal Saham Rule (*Tajika Neelakanthi*):** Compute `λ_Saham = (A - B + C) mod 360°`. Whenever the Ascendant (`C`) is **not** geometrically situated on the zodiacal arc moving forward from `B` to `A`, **add `+30°` (`1 Sign`)** to the result.

| # | Classical *Saham* Name | Life Domain / Signification | Day Birth Formula (`A - B + C`) | Night Birth Formula (`A - B + C`) |
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

| # | Nakshatra / Star | Sanskrit *Yogatara* Name | Modern IAU Star | J2000 RA (`deg`) | J2000 Dec (`deg`) | Visual Mag (`V`) | *Kalansha* Heliacal Arc |
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
- **Elapsed Time After `05:30 IST` Tabular Epoch:** `5 hours 12 minutes (13 Ghatis 00 Palas)` (Interpolation Fraction `f = 0.216667`)
- **Manual Ascendant (*Udaya Lagna*):** `Dhanu 22° 18' 00"` | **10th Cusp (*Madhya Lagna*):** `Tula 05° 57' 51"`
- **Natal Moon Nakshatra & Pada:** `Uttara Ashadha Pada 3 (Lord: Sun)` (`378.34'` *Bhogyamsha* remaining)
- **Natal *Vimshottari Dasha* Balance at Birth:** **`Sun Mahadasha: 2 Years, 10 Months, 2 Days remaining`**

### Step 1 & Step 2 — Complete 1st-Order (*Trairashika*) & 2nd-Order (*Bessel*) Manual *Spashta Graha* Worksheet

| Body | `05:30 IST` Day `D` | `05:30 IST` Day `D+1` | Daily Motion `v₁` | 1st-Order *Trairashika* | 2nd-Order *Bessel* Exact | `D9` Navamsa | `D10` Dasamsa | `D60` Shashtiamsa | *KP* Star / Sub / Sub-Sub |
|---|---|---|---|---|---|---|---|---|---|
| **Surya (Sun)** | `Tula 28° 23' 45"` | `+00° 13' 06"` | `+01° 00' 25"` | `Tula 28° 36' 50"` | **`Tula 28° 36' 50"`** | **Mithuna** | **Karka** | Karka | `venus / jupiter / venus / mercury` |
| **Chandra (Moon)** | `Makara 01° 08' 07"` | `+02° 33' 27"` | `+11° 48' 14"` | `Makara 03° 41' 34"` | **`Makara 03° 41' 38"`** | **Kumbha** | **Tula** | Simha | `saturn / sun / saturn / ketu` |
| **Mangala (Mars)** | `Simha 01° 05' 12"` | `+00° 05' 52"` | `+00° 27' 03"` | `Simha 01° 11' 03"` | **`Simha 01° 11' 03"`** | **Mesha** | **Simha** | Tula | `sun / ketu / venus / sun` |
| **Budha (Mercury)** | `Tula 10° 57' 40"` | `+00° 03' 07"` | `+00° 14' 22"` | `Tula 11° 00' 47"` | **`Tula 11° 01' 02"`** | **Makara** | **Makara** | Simha | `venus / rahu / saturn / mercury` |
| **Guru (Jupiter)** | `Simha 01° 32' 52"` | `+00° 01' 07"` | `+00° 05' 09"` | `Simha 01° 33' 59"` | **`Simha 01° 33' 59"`** | **Mesha** | **Simha** | Vrishchika | `sun / ketu / venus / mars` |
| **Shukra (Venus)** | `Kanya 28° 38' 53"` | `+00° 00' 30"` | `+00° 02' 21"` | `Kanya 28° 39' 24"` | **`Kanya 28° 39' 27"`** | **Kanya** | **Kumbha** | Mithuna | `mercury / mars / saturn / venus` |
| **Shani (Saturn)** | `Meena 14° 17' 33"` | `-00° 00' 35"` | `-00° 02' 40"` | `Meena 14° 16' 59"` | **`Meena 14° 16' 59"`** | **Vrishchika** | **Meena** | Karka | `jupiter / saturn / rahu / venus` |
| **Rahu (Node)** | `Kumbha 01° 05' 51"` | `-00° 00' 41"` | `-00° 03' 11"` | `Kumbha 01° 05' 10"` | **`Kumbha 01° 05' 10"`** | **Tula** | **Kumbha** | Mesha | `saturn / mars / mercury / rahu` |
| **Ketu (S. Node)** | `Simha 01° 05' 51"` | `-00° 00' 41"` | `-00° 03' 11"` | `Simha 01° 05' 10"` | **`Simha 01° 05' 10"`** | **Mesha** | **Simha** | Tula | `sun / ketu / venus / venus` |

### Step 3 & Step 4 — All 12 *Sripathi Bhava* Cusps, 8 *Vishesha Lagnas*, *Yogi/Avayogi*, 11 *Upagrahas*, & 9 *Prashna Sphutas*

| Special Point Category | Point Name | Computed Sidereal Longitude (`DMS`) | Sign (`Rashi`) | `D9` Navamsa / Nakshatra Details |
|---|---|---|---|---|
| **8 Vishesha Lagnas** | **Udaya Lagna (Birth Ascendant)** | **`Dhanu 22° 18' 00"`** | Dhanu (Jupiter) | `D9:` **Tula**; *Purva Ashadha* P3 (Eastern horizon intersection with the sidereal ecliptic at birth) |
| **8 Vishesha Lagnas** | **Hora Lagna (HL — Sustenance & Wealth)** | **`Kumbha 29° 16' 26"`** | Kumbha (Saturn) | `D9:` **Mithuna**; *Purva Bhadrapada* P3 (Sun at Sunrise + (Elapsed Minutes since Sunrise / 2.0)) |
| **8 Vishesha Lagnas** | **Ghati Lagna (GL — Power, Rank & Authority)** | **`Kanya 00° 31' 03"`** | Kanya (Mercury) | `D9:` **Makara**; *Uttara Phalguni* P2 (Sun at Sunrise + (Elapsed Ghatis since Sunrise × 30°)) |
| **8 Vishesha Lagnas** | **Bhava Lagna (BL — Disposition & Vitality)** | **`Dhanu 28° 51' 34"`** | Dhanu (Jupiter) | `D9:` **Dhanu**; *Uttara Ashadha* P1 (Sun at Sunrise + (Elapsed Ghatis since Sunrise × 6°)) |
| **8 Vishesha Lagnas** | **Sree Lagna (SL — Lakshmi Prosperity & Grace)** | **`Karka 02° 02' 46"`** | Karka (Moon) | `D9:` **Karka**; *Punarvasu* P4 (Udaya Lagna + (Moon's Traversed Nakshatra Fraction × 360°)) |
| **8 Vishesha Lagnas** | **Indu Lagna (IL — Kalidasa Wealth & Dhana Yoga Point)** | **`Kumbha 03° 41' 39"`** | Kumbha (Saturn) | `D9:` **Vrishchika**; *Dhanishta* P4 (9th Lord from Lagna (Sun=30) + 9th Lord from Moon (Mercury=8) = 38 Kalas -> 2th sign from Moon) |
| **8 Vishesha Lagnas** | **Pranapada Lagna (PL — Vital Breath & Rectification Anchor)** | **`Meena 06° 54' 16"`** | Meena (Jupiter) | `D9:` **Kanya**; *Uttara Bhadrapada* P2 (Sun at Birth + Modality Offset (Movable +0°, Fixed +240°, Dual +120°) + ((Elapsed Palas / 15) × 30°)) |
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

**Worked 12 *Jaimini Arudha Padas* (`AL` to `UL`):** **AL:** Mesha, **A2:** Vrishabha, **A3:** Mesha, **A4:** Makara, **A5:** Dhanu, **A6:** Makara, **A7:** Kumbha, **A8:** Mesha *(Swastha)*, **A9:** Dhanu, **A10:** Vrishchika, **A11:** Simha, **UL:** Kumbha *(Swastha)*.

**Worked *Kalachakra Dasha* at Birth:** Chakra Group = **Savya**, *Dehamsha* = **Kanya**, *Jeevamsha* = **Kumbha**, Paramayus = `85 Years`, Birth Period = **Simha** (`Krama Gati` Gati).

**Worked Sample of 36 *Tajika Sahams*:** **Punya Saham:** `Kumbha 27° 22' 49"`, **Vidya Saham:** `Vrishchika 17° 13' 11"`, **Yasas Saham:** `Mithuna 26° 29' 09"`, **Mitra Saham:** `Mesha 02° 50' 37"`, **Mahatmya Saham:** `Karka 18° 29' 46"`, **Asha Saham:** `Mithuna 07° 55' 31"`, **Samarthya Saham:** `Dhanu 21° 55' 04"`, **Bhratri Saham:** `Mithuna 09° 35' 00"`, **Gaurava Saham:** `Vrishabha 26° 29' 09"`, **Pitri Saham:** `Vrishabha 07° 58' 08"`, **Matri Saham:** `Meena 27° 20' 12"`, **Putra Saham:** `Simha 20° 10' 19"` *(all `36` Sahams computed deterministically)*.

## Chapter 21 — Topocentric WGS84 Surface-Observer Astrometry, Lunar Parallax (`1°02'`), Atmospheric Refraction, Air Mass, Doppler Velocity, & Relativistic Shapiro Delay

> **Why Topocentric & Relativistic Astrometry Matters:** Classical *Surya Siddhanta* (*Lambana* & *Nati* chapters) and modern IAU observatory physics agree that an observer stands on the rotating, oblate surface of the Earth (`r ≈ 6,378.137 km`), not at Earth's center. For the Moon, surface parallax shifts apparent sidereal longitude by up to **`1° 02' 00"` (`3,720"`)** — enough to flip `D9 Navamsa`, `D60 Shashtiamsa`, `Nakshatra Pada`, and `KP 249 Sub-Lords`.

### 21.1 Worked Case Study: 13-Body Geocentric vs Topocentric & Relativistic Astrometry Table

| Body | Geocentric Sidereal (`DMS`) | Topocentric Sidereal (`DMS`) | Parallax Shift (`Δλ" / Δβ"`) | Azimuth / True Alt / Refracted Alt | Air Mass `X` | Doppler `v_r` (`km/s`) | Light-Time `τ` (`s`) | Shapiro `Δt` (`μs`) | GR Defl (`mas`) | `D9 / D60 / KP` Flip Audit |
|---|---|---|---|---|---|---|---|---|---|---|
| **sun** | `Tula 28° 36' 50"` | **`Tula 28° 36' 55"`** | `+4.45" / -4.72"` | `Az 150.5° / Alt +42.97° -> +42.99° (+62.1")` | `1.47` | `-0.393` | `493.65s` | `29.89μs` | `0.00` | `D9:OK(Mithuna->Mithuna) D60:OK(58->58) KP:OK(venus->venus)` |
| **moon** | `Makara 03° 41' 39"` | **`Makara 04° 26' 35"`** | `+2695.54" / -1698.76"` | `Az 110.3° / Alt -11.75° -> -11.75° (+0.0")` | `40.00` | `-0.020` | `1.35s` | `0.10μs` | `6.38` | `D9:OK(Kumbha->Kumbha) D60:FLIP(8->9) KP:OK(saturn->saturn)` |
| **mars** | `Simha 01° 11' 03"` | **`Simha 01° 10' 59"`** | `-4.42" / -3.43"` | `Az 273.0° / Alt +33.27° -> +33.29° (+87.9")` | `1.82` | `-14.758` | `655.70s` | `10.97μs` | `4.26` | `D9:OK(Mesha->Mesha) D60:OK(3->3) KP:OK(venus->venus)` |
| **mercury** | `Tula 11° 01' 01"` | **`Tula 11° 01' 04"`** | `+2.80" / -5.16"` | `Az 170.3° / Alt +55.22° -> +55.23° (+40.3")` | `1.22` | `+44.165` | `424.62s` | `15.39μs` | `26.31` | `D9:OK(Makara->Makara) D60:OK(23->23) KP:OK(saturn->saturn)` |
| **jupiter** | `Simha 01° 33' 59"` | **`Simha 01° 33' 57"`** | `-1.09" / -0.87"` | `Az 271.6° / Alt +32.84° -> +32.86° (+89.4")` | `1.84` | `-27.185` | `2634.61s` | `23.84μs` | `4.29` | `D9:OK(Mesha->Mesha) D60:OK(4->4) KP:OK(venus->venus)` |
| **venus** | `Kanya 28° 39' 27"` | **`Kanya 28° 39' 30"`** | `+2.46" / -14.62"` | `Az 193.1° / Alt +55.85° -> +55.86° (+39.3")` | `1.21` | `+8.723` | `165.49s` | `3.87μs` | `15.22` | `D9:OK(Kanya->Kanya) D60:OK(58->58) KP:OK(saturn->saturn)` |
| **saturn** | `Meena 14° 16' 59"` | **`Meena 14° 16' 59"`** | `+0.12" / -0.50"` | `Az 40.4° / Alt -59.47° -> -59.47° (+0.0")` | `40.00` | `+20.065` | `4335.70s` | `23.70μs` | `1.66` | `D9:OK(Vrishchika->Vrishchika) D60:OK(29->29) KP:OK(rahu->rahu)` |
| **rahu** | `Kumbha 01° 05' 10"` | **`Kumbha 01° 40' 41"`** | `+2131.09" / -1713.44"` | `Az 91.3° / Alt -32.76° -> -32.76° (+0.0")` | `40.00` | `+0.000` | `1.28s` | `0.10μs` | `3.90` | `D9:OK(Tula->Tula) D60:FLIP(3->4) KP:OK(mercury->mercury)` |
| **true_rahu** | `Kumbha 00° 56' 51"` | **`Kumbha 01° 32' 27"`** | `+2135.26" / -1713.48"` | `Az 91.4° / Alt -32.65° -> -32.65° (+0.0")` | `40.00` | `-0.020` | `1.35s` | `0.10μs` | `3.91` | `D9:OK(Tula->Tula) D60:FLIP(2->4) KP:OK(mercury->mercury)` |
| **ketu** | `Simha 01° 05' 10"` | **`Simha 00° 29' 03"`** | `-2166.98" / -1742.29"` | `Az 271.3° / Alt +31.23° -> +31.25° (+95.1")` | `1.93` | `+0.000` | `1.28s` | `0.10μs` | `4.25` | `D9:OK(Mesha->Mesha) D60:FLIP(3->1) KP:FLIP(venus->ketu)` |
| **uranus** | `Vrishabha 09° 53' 15"` | **`Vrishabha 09° 53' 15"`** | `-0.30" / -0.25"` | `Az 320.3° / Alt -34.89° -> -34.89° (+0.0")` | `40.00` | `-5.742` | `9212.59s` | `29.43μs` | `0.40` | `D9:OK(Meena->Meena) D60:OK(20->20) KP:OK(venus->venus)` |
| **neptune** | `Meena 07° 35' 31"` | **`Meena 07° 35' 32"`** | `+0.06" / -0.15"` | `Az 51.7° / Alt -56.21° -> -56.21° (+0.0")` | `40.00` | `+23.468` | `14593.45s` | `35.59μs` | `1.94` | `D9:OK(Kanya->Kanya) D60:OK(16->16) KP:OK(ketu->ketu)` |
| **pluto** | `Makara 09° 02' 53"` | **`Makara 09° 02' 54"`** | `+0.20" / -0.13"` | `Az 109.1° / Alt -16.42° -> -16.42° (+0.0")` | `40.00` | `+29.233` | `17944.09s` | `46.15μs` | `5.77` | `D9:OK(Meena->Meena) D60:OK(19->19) KP:OK(venus->venus)` |

### 21.2 Daily Geocentric vs Topocentric Moon & Sun Parallax Almanac Across the Month (`05:30 IST`)

| Date | Local Sidereal Time | Geocentric Moon (`DMS`) | Topocentric Moon (`DMS`) | Lunar Parallax Shift (`Δλ" / Δβ"`) | Moon Alt / Azimuth / Refraction | Geocentric vs Topocentric `D9 / D60 / KP-Sub` Audit |
|---|---|---|---|---|---|---|
| `2026-11-01` | `07h 44m 21s` | `Karka 03° 14' 11"` | **`Karka 03° 17' 57"`** | **`+226.4" / +47.2"`** | `Alt +86.3° / Az 90.3° (Refr +3.9")` | `D9: Karka->Karka | D60: #7->#7 | KP: rahu->rahu` |
| `2026-11-02` | `07h 48m 18s` | `Karka 17° 14' 11"` | **`Karka 17° 31' 20"`** | **`+1029.1" / -37.9"`** | `Alt +73.0° / Az 102.5° (Refr +18.4")` | `D9: Dhanu->Dhanu | D60: #35->#36 | KP: mercury->mercury` |
| `2026-11-03` | `07h 52m 14s` | `Simha 00° 58' 43"` | **`Simha 01° 27' 50"`** | **`+1746.9" / -119.7"`** | `Alt +59.9° / Az 104.4° (Refr +34.9")` | `D9: Mesha->Mesha | D60: #2->#3 | KP: venus->venus` |
| `2026-11-04` | `07h 56m 11s` | `Simha 14° 28' 48"` | **`Simha 15° 07' 58"`** | **`+2350.1" / -183.4"`** | `Alt +47.1° / Az 105.3° (Refr +55.9")` | `D9: Simha->Simha | D60: #29->#31 | KP: venus->venus` |
| `2026-11-05` | `08h 00m 07s` | `Simha 27° 45' 45"` | **`Simha 28° 32' 45"`** | **`+2819.3" / -220.1"`** | `Alt +34.5° / Az 105.9° (Refr +87.2")` | `D9: Dhanu->Dhanu | D60: #56->#58 | KP: moon->mars` |
| `2026-11-06` | `08h 04m 04s` | `Kanya 10° 50' 49"` | **`Kanya 11° 43' 12"`** | **`+3143.2" / -227.0"`** | `Alt +22.2° / Az 106.4° (Refr +145.7")` | `D9: Mesha->Mesha | D60: #22->#24 | KP: moon->mars` |
| `2026-11-07` | `08h 08m 00s` | `Kanya 23° 44' 48"` | **`Kanya 24° 40' 06"`** | **`+3317.4" / -207.1"`** | `Alt +10.1° / Az 106.7° (Refr +318.5")` | `D9: Simha->Simha | D60: #48->#50 | KP: mars->rahu` |
| `2026-11-08` | `08h 11m 57s` | `Tula 06° 28' 05"` | **`Tula 07° 23' 50"`** | **`+3344.5" / -168.4"`** | `Alt -1.8° / Az 107.0° (Refr +0.0")` | `D9: Vrishchika->Dhanu | D60: #13->#15 | KP: moon->rahu` |
| `2026-11-09` | `08h 15m 54s` | `Tula 19° 00' 43"` | **`Tula 19° 54' 36"`** | **`+3233.3" / -121.1"`** | `Alt -13.4° / Az 107.1° (Refr +0.0")` | `D9: Meena->Meena | D60: #39->#40 | KP: moon->mars` |
| `2026-11-10` | `08h 19m 50s` | `Vrishchika 01° 22' 43"` | **`Vrishchika 02° 12' 41"`** | **`+2998.0" / -76.2"`** | `Alt -24.8° / Az 107.1° (Refr +0.0")` | `D9: Karka->Karka | D60: #3->#5 | KP: rahu->rahu` |
| `2026-11-11` | `08h 23m 47s` | `Vrishchika 13° 34' 23"` | **`Vrishchika 14° 18' 40"`** | **`+2656.7" / -42.9"`** | `Alt -36.0° / Az 106.9° (Refr +0.0")` | `D9: Vrishchika->Vrishchika | D60: #28->#29 | KP: rahu->rahu` |
| `2026-11-12` | `08h 27m 43s` | `Vrishchika 25° 36' 37"` | **`Vrishchika 26° 13' 46"`** | **`+2228.9" / -27.9"`** | `Alt -47.0° / Az 106.3° (Refr +0.0")` | `D9: Kumbha->Kumbha | D60: #52->#53 | KP: rahu->jupiter` |
| `2026-11-13` | `08h 31m 40s` | `Dhanu 07° 31' 05"` | **`Dhanu 07° 59' 59"`** | **`+1733.5" / -34.8"`** | `Alt -57.8° / Az 105.2° (Refr +0.0")` | `D9: Mithuna->Mithuna | D60: #16->#16 | KP: rahu->jupiter` |
| `2026-11-14` | `08h 35m 36s` | `Dhanu 19° 20' 25"` | **`Dhanu 19° 40' 13"`** | **`+1187.5" / -63.9"`** | `Alt -68.5° / Az 102.5° (Refr +0.0")` | `D9: Kanya->Kanya | D60: #39->#40 | KP: rahu->rahu` |
| `2026-11-15` | `08h 39m 33s` | `Makara 01° 08' 07"` | **`Makara 01° 18' 13"`** | **`+605.1" / -112.9"`** | `Alt -79.1° / Az 94.2° (Refr +0.0")` | `D9: Makara->Makara | D60: #3->#3 | KP: rahu->jupiter` |
| `2026-11-16` | `08h 43m 30s` | `Makara 12° 58' 35"` | **`Makara 12° 58' 33"`** | **`-2.0" / -177.4"`** | `Alt -86.8° / Az 13.9° (Refr +0.0")` | `D9: Mesha->Mesha | D60: #26->#26 | KP: rahu->rahu` |
| `2026-11-17` | `08h 47m 26s` | `Makara 24° 56' 49"` | **`Makara 24° 46' 26"`** | **`-623.2" / -251.1"`** | `Alt -78.1° / Az 307.4° (Refr +0.0")` | `D9: Simha->Simha | D60: #50->#50 | KP: rahu->rahu` |
| `2026-11-18` | `08h 51m 23s` | `Kumbha 07° 08' 17"` | **`Kumbha 06° 47' 31"`** | **`-1246.5" / -326.2"`** | `Alt -67.1° / Az 299.8° (Refr +0.0")` | `D9: Dhanu->Dhanu | D60: #15->#14 | KP: rahu->rahu` |
| `2026-11-19` | `08h 55m 19s` | `Kumbha 19° 38' 30"` | **`Kumbha 19° 07' 33"`** | **`-1856.4" / -394.0"`** | `Alt -55.7° / Az 297.0° (Refr +0.0")` | `D9: Meena->Meena | D60: #40->#39 | KP: mars->moon` |
| `2026-11-20` | `08h 59m 16s` | `Meena 02° 32' 29"` | **`Meena 01° 51' 59"`** | **`-2429.9" / -444.8"`** | `Alt -43.8° / Az 295.5° (Refr +0.0")` | `D9: Karka->Karka | D60: #6->#4 | KP: rahu->rahu` |
| `2026-11-21` | `09h 03m 12s` | `Meena 15° 54' 06"` | **`Meena 15° 05' 12"`** | **`-2934.4" / -470.3"`** | `Alt -31.5° / Az 294.5° (Refr +0.0")` | `D9: Vrishchika->Vrishchika | D60: #32->#31 | KP: jupiter->jupiter` |
| `2026-11-22` | `09h 07m 09s` | `Meena 29° 45' 14"` | **`Meena 28° 49' 47"`** | **`-3326.8" / -465.5"`** | `Alt -18.7° / Az 293.6° (Refr +0.0")` | `D9: Meena->Meena | D60: #60->#58 | KP: saturn->saturn` |
| `2026-11-23` | `09h 11m 05s` | `Mesha 14° 04' 53"` | **`Mesha 13° 05' 35"`** | **`-3558.0" / -432.1"`** | `Alt -5.3° / Az 292.6° (Refr +0.0")` | `D9: Simha->Karka | D60: #29->#27 | KP: venus->mercury` |
| `2026-11-24` | `09h 15m 02s` | `Mesha 28° 48' 42"` | **`Mesha 27° 49' 00"`** | **`-3582.3" / -380.8"`** | `Alt +8.5° / Az 291.5° (Refr +373.1")` | `D9: Dhanu->Dhanu | D60: #58->#56 | KP: mars->moon` |
| `2026-11-25` | `09h 18m 59s` | `Vrishabha 13° 49' 06"` | **`Vrishabha 12° 52' 54"`** | **`-3371.5" / -330.3"`** | `Alt +22.5° / Az 290.0° (Refr +143.1")` | `D9: Vrishabha->Mesha | D60: #28->#26 | KP: rahu->rahu` |
| `2026-11-26` | `09h 22m 55s` | `Vrishabha 28° 56' 15"` | **`Vrishabha 28° 07' 27"`** | **`-2928.4" / -301.5"`** | `Alt +36.7° / Az 287.9° (Refr +80.3")` | `D9: Kanya->Kanya | D60: #58->#57 | KP: saturn->saturn` |
| `2026-11-27` | `09h 26m 52s` | `Mithuna 13° 59' 53"` | **`Mithuna 13° 21' 43"`** | **`-2289.5" / -308.9"`** | `Alt +50.9° / Az 284.4° (Refr +48.9")` | `D9: Kumbha->Kumbha | D60: #28->#27 | KP: mercury->mercury` |
| `2026-11-28` | `09h 30m 48s` | `Mithuna 28° 50' 59"` | **`Mithuna 28° 25' 42"`** | **`-1517.1" / -355.4"`** | `Alt +64.6° / Az 277.4° (Refr +28.6")` | `D9: Mithuna->Mithuna | D60: #58->#57 | KP: sun->venus` |
| `2026-11-29` | `09h 34m 45s` | `Karka 13° 23' 13"` | **`Karka 13° 11' 50"`** | **`-682.3" / -431.3"`** | `Alt +77.0° / Az 256.9° (Refr +14.0")` | `D9: Vrishchika->Tula | D60: #27->#27 | KP: rahu->rahu` |
| `2026-11-30` | `09h 38m 41s` | `Karka 27° 33' 17"` | **`Karka 27° 35' 47"`** | **`+149.5" / -519.5"`** | `Alt +81.1° / Az 182.9° (Refr +9.5")` | `D9: Meena->Meena | D60: #56->#56 | KP: jupiter->jupiter` |

### 21.3 Saemundsson-Bennett Atmospheric Refraction & Rozenberg Optical Air Mass Master Table (`-1°` to `90°` Altitude)

| True Altitude `h₀` | Std Refraction (`15°C, 1013 hPa`) | Hot Tropical (`35°C, 1005 hPa`) | Cold Winter (`0°C, 1020 hPa`) | High Altitude (`2200m, 780 hPa`) | Rozenberg Optical Air Mass `X(z)` | Extinction Loss (`Δmag`, `k=0.20`) |
|---|---|---|---|---|---|---|
| **` -1.0°`** | `2294.8"` (`38.25'`) | `2128.3"` | `2437.0"` | `1797.7"` | **`40.00x`** | `+8.00 mag` |
| **` -0.5°`** | `1992.7"` (`33.21'`) | `1848.1"` | `2116.2"` | `1561.1"` | **`38.94x`** | `+7.79 mag` |
| **` +0.0°`** | `1714.3"` (`28.57'`) | `1590.0"` | `1820.6"` | `1343.0"` | **`32.13x`** | `+6.43 mag` |
| **` +0.5°`** | `1479.0"` (`24.65'`) | `1371.7"` | `1570.7"` | `1158.7"` | **`27.11x`** | `+5.42 mag` |
| **` +1.0°`** | `1286.2"` (`21.44'`) | `1192.9"` | `1365.9"` | `1007.6"` | **`23.28x`** | `+4.66 mag` |
| **` +1.5°`** | `1129.3"` (`18.82'`) | `1047.4"` | `1199.3"` | ` 884.7"` | **`20.28x`** | `+4.06 mag` |
| **` +2.0°`** | `1001.2"` (`16.69'`) | ` 928.6"` | `1063.3"` | ` 784.4"` | **`17.89x`** | `+3.58 mag` |
| **` +3.0°`** | ` 808.1"` (`13.47'`) | ` 749.5"` | ` 858.2"` | ` 633.1"` | **`14.34x`** | `+2.87 mag` |
| **` +4.0°`** | ` 672.1"` (`11.20'`) | ` 623.3"` | ` 713.7"` | ` 526.5"` | **`11.88x`** | `+2.38 mag` |
| **` +5.0°`** | ` 572.3"` (`9.54'`) | ` 530.8"` | ` 607.8"` | ` 448.4"` | **`10.08x`** | `+2.02 mag` |
| **` +6.0°`** | ` 496.7"` (`8.28'`) | ` 460.7"` | ` 527.5"` | ` 389.1"` | **` 8.72x`** | `+1.74 mag` |
| **` +8.0°`** | ` 390.5"` (`6.51'`) | ` 362.1"` | ` 414.7"` | ` 305.9"` | **` 6.83x`** | `+1.37 mag` |
| **`+10.0°`** | ` 320.0"` (`5.33'`) | ` 296.8"` | ` 339.8"` | ` 250.7"` | **` 5.59x`** | `+1.12 mag` |
| **`+12.0°`** | ` 270.0"` (`4.50'`) | ` 250.4"` | ` 286.7"` | ` 211.5"` | **` 4.72x`** | `+0.94 mag` |
| **`+15.0°`** | ` 217.5"` (`3.62'`) | ` 201.7"` | ` 231.0"` | ` 170.4"` | **` 3.83x`** | `+0.77 mag` |
| **`+20.0°`** | ` 162.3"` (`2.70'`) | ` 150.5"` | ` 172.3"` | ` 127.1"` | **` 2.91x`** | `+0.58 mag` |
| **`+25.0°`** | ` 127.5"` (`2.13'`) | ` 118.3"` | ` 135.4"` | `  99.9"` | **` 2.36x`** | `+0.47 mag` |
| **`+30.0°`** | ` 103.4"` (`1.72'`) | `  95.9"` | ` 109.8"` | `  81.0"` | **` 2.00x`** | `+0.40 mag` |
| **`+35.0°`** | `  85.5"` (`1.42'`) | `  79.3"` | `  90.8"` | `  66.9"` | **` 1.74x`** | `+0.35 mag` |
| **`+40.0°`** | `  71.4"` (`1.19'`) | `  66.3"` | `  75.9"` | `  56.0"` | **` 1.56x`** | `+0.31 mag` |
| **`+45.0°`** | `  60.0"` (`1.00'`) | `  55.7"` | `  63.7"` | `  47.0"` | **` 1.41x`** | `+0.28 mag` |
| **`+50.0°`** | `  50.4"` (`0.84'`) | `  46.7"` | `  53.5"` | `  39.5"` | **` 1.31x`** | `+0.26 mag` |
| **`+60.0°`** | `  34.7"` (`0.58'`) | `  32.2"` | `  36.9"` | `  27.2"` | **` 1.15x`** | `+0.23 mag` |
| **`+70.0°`** | `  21.9"` (`0.37'`) | `  20.3"` | `  23.3"` | `  17.2"` | **` 1.06x`** | `+0.21 mag` |
| **`+80.0°`** | `  10.6"` (`0.18'`) | `   9.9"` | `  11.3"` | `   8.3"` | **` 1.02x`** | `+0.20 mag` |
| **`+90.0°`** | `   0.0"` (`0.00'`) | `   0.0"` | `   0.0"` | `   0.0"` | **` 1.00x`** | `+0.20 mag` |

## Chapter 22 — Synodic Retrograde Phase-Space Loops (*Vakri / Vakra-Tyaga*), Perigee Brilliance, & 360° Natal Triple-Pass Transit Matrix

### 22.1 Complete 5-Point Synodic Retrograde Phase-Space Loops (±180 Days Around Reference Epoch)

| Body | Pre-Shadow Entry | First Station `S₁` (*Vakri*) | Minimum Distance / Opposition Peak | Second Station `S₂` (*Margi*) | Post-Shadow Exit | Retrograde Arc Width | Loop Duration (`Days`) |
|---|---|---|---|---|---|---|---|
| **Mercury** | `2026-06-13T00:50:17Z` | **`2026-06-29T17:35:03Z`** (`Karka 02° 01' 41"`) | `2026-07-10T15:12:52Z` (`0.5687 AU`, `+128.31 mag`) | **`2026-07-23T22:59:06Z`** (`Mithuna 22° 05' 09"`) | `2026-08-07T03:38:51Z` | **`9.94°`** | **`24.23 d`** |
| **Saturn** | `2026-04-20T10:15:20Z` | **`2026-07-26T17:41:58Z`** (`Meena 20° 31' 09"`) | `2026-10-03T08:28:21Z` (`8.4345 AU`, `+0.59 mag`) | **`2026-12-10T23:14:44Z`** (`Meena 13° 41' 42"`) | `2027-03-15T08:42:53Z` | **`6.82°`** | **`137.23 d`** |
| **Venus** | `2026-08-31T14:40:57Z` | **`2026-10-03T07:15:04Z`** (`Tula 14° 15' 29"`) | `2026-10-24T03:53:17Z` (`0.2729 AU`, `+4.22 mag`) | **`2026-11-14T00:31:30Z`** (`Kanya 28° 37' 44"`) | `2026-12-15T18:49:21Z` | **`15.63°`** | **`41.72 d`** |
| **Mercury** | `2026-10-04T09:07:43Z` | **`2026-10-24T07:13:01Z`** (`Tula 26° 44' 43"`) | `2026-11-03T11:33:49Z` (`0.6726 AU`, `+129.86 mag`) | **`2026-11-13T15:54:36Z`** (`Tula 10° 47' 56"`) | `2026-11-30T06:18:09Z` | **`15.95°`** | **`20.36 d`** |
| **Jupiter** | `2026-09-17T03:26:17Z` | **`2026-12-12T23:50:18Z`** (`Simha 02° 47' 18"`) | `2027-02-11T12:56:10Z` (`4.3612 AU`, `-2.56 mag`) | **`2027-04-13T02:02:01Z`** (`Karka 22° 45' 15"`) | `2027-07-11T05:57:21Z` | **`10.03°`** | **`121.09 d`** |
| **Mars** | `2026-11-05T15:14:34Z` | **`2027-01-10T12:45:29Z`** (`Simha 16° 11' 28"`) | `2027-02-20T01:24:04Z` (`0.6779 AU`, `-1.33 mag`) | **`2027-04-01T14:02:39Z`** (`Karka 26° 41' 09"`) | `2027-06-08T02:15:34Z` | **`19.51°`** | **`81.05 d`** |
| **Mercury** | `2027-01-25T18:56:10Z` | **`2027-02-09T17:36:07Z`** (`Kumbha 11° 44' 32"`) | `2027-02-20T15:04:34Z` (`0.6377 AU`, `+121.26 mag`) | **`2027-03-03T12:33:01Z`** (`Makara 26° 41' 00"`) | `2027-03-23T14:59:25Z` | **`15.06°`** | **`21.79 d`** |

### 22.2 Complete 360-Degree Zodiacal Retrograde Triple-Pass, Divisional (`D9/D10/D60`), & `KP` Master Reference Table (`0°` to `359°`)

| Zodiacal Degree (`Nirayana`) | Classical `Rashi DMS` | `Nakshatra & Pada` | `D9 Navamsa` | `D10 Dasamsa` | `D60 Shashtiamsa` | `KP Sign / Star / Sub / Sub-Sub` | Active Retrograde Shadow Zone Status (±180d Window) |
|---|---|---|---|---|---|---|---|
| **`000° 00'`** | `Mesha 00° 00' 00"` | *Ashwini* P1 (Ketu) | **Mesha** | Mesha | Mesha | `mars/ketu/ketu/ketu` | Single Direct Transit Pass |
| **`001° 00'`** | `Mesha 01° 00' 00"` | *Ashwini* P1 (Ketu) | **Mesha** | Mesha | Mithuna | `mars/ketu/venus/venus` | Single Direct Transit Pass |
| **`002° 00'`** | `Mesha 02° 00' 00"` | *Ashwini* P1 (Ketu) | **Mesha** | Mesha | Simha | `mars/ketu/venus/jupiter` | Single Direct Transit Pass |
| **`003° 00'`** | `Mesha 03° 00' 00"` | *Ashwini* P1 (Ketu) | **Mesha** | Vrishabha | Tula | `mars/ketu/sun/sun` | Single Direct Transit Pass |
| **`004° 00'`** | `Mesha 04° 00' 00"` | *Ashwini* P2 (Ketu) | **Vrishabha** | Vrishabha | Dhanu | `mars/ketu/moon/jupiter` | Single Direct Transit Pass |
| **`005° 00'`** | `Mesha 05° 00' 00"` | *Ashwini* P2 (Ketu) | **Vrishabha** | Vrishabha | Kumbha | `mars/ketu/mars/jupiter` | Single Direct Transit Pass |
| **`006° 00'`** | `Mesha 06° 00' 00"` | *Ashwini* P2 (Ketu) | **Vrishabha** | Mithuna | Mesha | `mars/ketu/rahu/jupiter` | Single Direct Transit Pass |
| **`007° 00'`** | `Mesha 07° 00' 00"` | *Ashwini* P3 (Ketu) | **Mithuna** | Mithuna | Mithuna | `mars/ketu/rahu/venus` | Single Direct Transit Pass |
| **`008° 00'`** | `Mesha 08° 00' 00"` | *Ashwini* P3 (Ketu) | **Mithuna** | Mithuna | Simha | `mars/ketu/jupiter/saturn` | Single Direct Transit Pass |
| **`009° 00'`** | `Mesha 09° 00' 00"` | *Ashwini* P3 (Ketu) | **Mithuna** | Karka | Tula | `mars/ketu/jupiter/mars` | Single Direct Transit Pass |
| **`010° 00'`** | `Mesha 10° 00' 00"` | *Ashwini* P4 (Ketu) | **Karka** | Karka | Dhanu | `mars/ketu/saturn/ketu` | Single Direct Transit Pass |
| **`011° 00'`** | `Mesha 11° 00' 00"` | *Ashwini* P4 (Ketu) | **Karka** | Karka | Kumbha | `mars/ketu/saturn/rahu` | Single Direct Transit Pass |
| **`012° 00'`** | `Mesha 12° 00' 00"` | *Ashwini* P4 (Ketu) | **Karka** | Simha | Mesha | `mars/ketu/mercury/venus` | Single Direct Transit Pass |
| **`013° 00'`** | `Mesha 13° 00' 00"` | *Ashwini* P4 (Ketu) | **Karka** | Simha | Mithuna | `mars/ketu/mercury/jupiter` | Single Direct Transit Pass |
| **`014° 00'`** | `Mesha 14° 00' 00"` | *Bharani* P1 (Venus) | **Simha** | Simha | Simha | `mars/venus/venus/moon` | Single Direct Transit Pass |
| **`015° 00'`** | `Mesha 15° 00' 00"` | *Bharani* P1 (Venus) | **Simha** | Kanya | Tula | `mars/venus/venus/saturn` | Single Direct Transit Pass |
| **`016° 00'`** | `Mesha 16° 00' 00"` | *Bharani* P1 (Venus) | **Simha** | Kanya | Dhanu | `mars/venus/sun/mercury` | Single Direct Transit Pass |
| **`017° 00'`** | `Mesha 17° 00' 00"` | *Bharani* P2 (Venus) | **Kanya** | Kanya | Kumbha | `mars/venus/moon/mercury` | Single Direct Transit Pass |
| **`018° 00'`** | `Mesha 18° 00' 00"` | *Bharani* P2 (Venus) | **Kanya** | Tula | Mesha | `mars/venus/mars/venus` | Single Direct Transit Pass |
| **`019° 00'`** | `Mesha 19° 00' 00"` | *Bharani* P2 (Venus) | **Kanya** | Tula | Mithuna | `mars/venus/rahu/mercury` | Single Direct Transit Pass |
| **`020° 00'`** | `Mesha 20° 00' 00"` | *Bharani* P2 (Venus) | **Tula** | Tula | Simha | `mars/venus/rahu/mars` | Single Direct Transit Pass |
| **`021° 00'`** | `Mesha 21° 00' 00"` | *Bharani* P3 (Venus) | **Tula** | Vrishchika | Tula | `mars/venus/jupiter/venus` | Single Direct Transit Pass |
| **`022° 00'`** | `Mesha 22° 00' 00"` | *Bharani* P3 (Venus) | **Tula** | Vrishchika | Dhanu | `mars/venus/saturn/saturn` | Single Direct Transit Pass |
| **`023° 00'`** | `Mesha 23° 00' 00"` | *Bharani* P3 (Venus) | **Tula** | Vrishchika | Kumbha | `mars/venus/saturn/sun` | Single Direct Transit Pass |
| **`024° 00'`** | `Mesha 24° 00' 00"` | *Bharani* P4 (Venus) | **Vrishchika** | Dhanu | Mesha | `mars/venus/mercury/mercury` | Single Direct Transit Pass |
| **`025° 00'`** | `Mesha 25° 00' 00"` | *Bharani* P4 (Venus) | **Vrishchika** | Dhanu | Mithuna | `mars/venus/mercury/mars` | Single Direct Transit Pass |
| **`026° 00'`** | `Mesha 26° 00' 00"` | *Bharani* P4 (Venus) | **Vrishchika** | Dhanu | Simha | `mars/venus/ketu/venus` | Single Direct Transit Pass |
| **`027° 00'`** | `Mesha 27° 00' 00"` | *Krittika* P1 (Sun) | **Dhanu** | Makara | Tula | `mars/sun/sun/saturn` | Single Direct Transit Pass |
| **`028° 00'`** | `Mesha 28° 00' 00"` | *Krittika* P1 (Sun) | **Dhanu** | Makara | Dhanu | `mars/sun/moon/mercury` | Single Direct Transit Pass |
| **`029° 00'`** | `Mesha 29° 00' 00"` | *Krittika* P1 (Sun) | **Dhanu** | Makara | Kumbha | `mars/sun/mars/venus` | Single Direct Transit Pass |
| **`030° 00'`** | `Vrishabha 00° 00' 00"` | *Krittika* P1 (Sun) | **Makara** | Makara | Vrishabha | `venus/sun/rahu/saturn` | Single Direct Transit Pass |
| **`031° 00'`** | `Vrishabha 01° 00' 00"` | *Krittika* P2 (Sun) | **Makara** | Makara | Karka | `venus/sun/rahu/moon` | Single Direct Transit Pass |
| **`032° 00'`** | `Vrishabha 02° 00' 00"` | *Krittika* P2 (Sun) | **Makara** | Makara | Kanya | `venus/sun/jupiter/ketu` | Single Direct Transit Pass |
| **`033° 00'`** | `Vrishabha 03° 00' 00"` | *Krittika* P2 (Sun) | **Makara** | Kumbha | Vrishchika | `venus/sun/jupiter/rahu` | Single Direct Transit Pass |
| **`034° 00'`** | `Vrishabha 04° 00' 00"` | *Krittika* P3 (Sun) | **Kumbha** | Kumbha | Makara | `venus/sun/saturn/venus` | Single Direct Transit Pass |
| **`035° 00'`** | `Vrishabha 05° 00' 00"` | *Krittika* P3 (Sun) | **Kumbha** | Kumbha | Meena | `venus/sun/saturn/jupiter` | Single Direct Transit Pass |
| **`036° 00'`** | `Vrishabha 06° 00' 00"` | *Krittika* P3 (Sun) | **Kumbha** | Meena | Vrishabha | `venus/sun/mercury/moon` | Single Direct Transit Pass |
| **`037° 00'`** | `Vrishabha 07° 00' 00"` | *Krittika* P4 (Sun) | **Meena** | Meena | Karka | `venus/sun/mercury/saturn` | Single Direct Transit Pass |
| **`038° 00'`** | `Vrishabha 08° 00' 00"` | *Krittika* P4 (Sun) | **Meena** | Meena | Kanya | `venus/sun/venus/venus` | Single Direct Transit Pass |
| **`039° 00'`** | `Vrishabha 09° 00' 00"` | *Krittika* P4 (Sun) | **Meena** | Mesha | Vrishchika | `venus/sun/venus/jupiter` | Single Direct Transit Pass |
| **`040° 00'`** | `Vrishabha 10° 00' 00"` | *Rohini* P1 (Moon) | **Mesha** | Mesha | Makara | `venus/sun/venus/ketu` | Single Direct Transit Pass |
| **`041° 00'`** | `Vrishabha 11° 00' 00"` | *Rohini* P1 (Moon) | **Mesha** | Mesha | Meena | `venus/moon/moon/venus` | Single Direct Transit Pass |
| **`042° 00'`** | `Vrishabha 12° 00' 00"` | *Rohini* P1 (Moon) | **Mesha** | Vrishabha | Vrishabha | `venus/moon/rahu/rahu` | Single Direct Transit Pass |
| **`043° 00'`** | `Vrishabha 13° 00' 00"` | *Rohini* P1 (Moon) | **Mesha** | Vrishabha | Karka | `venus/moon/rahu/mercury` | Single Direct Transit Pass |
| **`044° 00'`** | `Vrishabha 14° 00' 00"` | *Rohini* P2 (Moon) | **Vrishabha** | Vrishabha | Kanya | `venus/moon/jupiter/jupiter` | Single Direct Transit Pass |
| **`045° 00'`** | `Vrishabha 15° 00' 00"` | *Rohini* P2 (Moon) | **Vrishabha** | Mithuna | Vrishchika | `venus/moon/jupiter/venus` | Single Direct Transit Pass |
| **`046° 00'`** | `Vrishabha 16° 00' 00"` | *Rohini* P2 (Moon) | **Vrishabha** | Mithuna | Makara | `venus/moon/saturn/saturn` | Single Direct Transit Pass |
| **`047° 00'`** | `Vrishabha 17° 00' 00"` | *Rohini* P3 (Moon) | **Mithuna** | Mithuna | Meena | `venus/moon/saturn/moon` | Single Direct Transit Pass |
| **`048° 00'`** | `Vrishabha 18° 00' 00"` | *Rohini* P3 (Moon) | **Mithuna** | Karka | Vrishabha | `venus/moon/mercury/mercury` | Single Direct Transit Pass |
| **`049° 00'`** | `Vrishabha 19° 00' 00"` | *Rohini* P3 (Moon) | **Mithuna** | Karka | Karka | `venus/moon/mercury/rahu` | Single Direct Transit Pass |
| **`050° 00'`** | `Vrishabha 20° 00' 00"` | *Rohini* P4 (Moon) | **Karka** | Karka | Kanya | `venus/moon/ketu/rahu` | Single Direct Transit Pass |
| **`051° 00'`** | `Vrishabha 21° 00' 00"` | *Rohini* P4 (Moon) | **Karka** | Simha | Vrishchika | `venus/moon/venus/moon` | Single Direct Transit Pass |
| **`052° 00'`** | `Vrishabha 22° 00' 00"` | *Rohini* P4 (Moon) | **Karka** | Simha | Makara | `venus/moon/venus/saturn` | Single Direct Transit Pass |
| **`053° 00'`** | `Vrishabha 23° 00' 00"` | *Rohini* P4 (Moon) | **Karka** | Simha | Meena | `venus/moon/sun/saturn` | Single Direct Transit Pass |
| **`054° 00'`** | `Vrishabha 24° 00' 00"` | *Mrigashirsha* P1 (Mars) | **Simha** | Kanya | Vrishabha | `venus/mars/mars/venus` | Single Direct Transit Pass |
| **`055° 00'`** | `Vrishabha 25° 00' 00"` | *Mrigashirsha* P1 (Mars) | **Simha** | Kanya | Karka | `venus/mars/rahu/mercury` | Single Direct Transit Pass |
| **`056° 00'`** | `Vrishabha 26° 00' 00"` | *Mrigashirsha* P1 (Mars) | **Simha** | Kanya | Kanya | `venus/mars/rahu/mars` | Single Direct Transit Pass |
| **`057° 00'`** | `Vrishabha 27° 00' 00"` | *Mrigashirsha* P2 (Mars) | **Kanya** | Tula | Vrishchika | `venus/mars/jupiter/venus` | Single Direct Transit Pass |
| **`058° 00'`** | `Vrishabha 28° 00' 00"` | *Mrigashirsha* P2 (Mars) | **Kanya** | Tula | Makara | `venus/mars/saturn/saturn` | Single Direct Transit Pass |
| **`059° 00'`** | `Vrishabha 29° 00' 00"` | *Mrigashirsha* P2 (Mars) | **Kanya** | Tula | Meena | `venus/mars/saturn/sun` | Single Direct Transit Pass |
| **`060° 00'`** | `Mithuna 00° 00' 00"` | *Mrigashirsha* P2 (Mars) | **Tula** | Mithuna | Mithuna | `mercury/mars/saturn/jupiter` | Single Direct Transit Pass |
| **`061° 00'`** | `Mithuna 01° 00' 00"` | *Mrigashirsha* P3 (Mars) | **Tula** | Mithuna | Simha | `mercury/mars/mercury/mars` | Single Direct Transit Pass |
| **`062° 00'`** | `Mithuna 02° 00' 00"` | *Mrigashirsha* P3 (Mars) | **Tula** | Mithuna | Tula | `mercury/mars/ketu/venus` | Single Direct Transit Pass |
| **`063° 00'`** | `Mithuna 03° 00' 00"` | *Mrigashirsha* P3 (Mars) | **Tula** | Karka | Dhanu | `mercury/mars/venus/venus` | Single Direct Transit Pass |
| **`064° 00'`** | `Mithuna 04° 00' 00"` | *Mrigashirsha* P4 (Mars) | **Vrishchika** | Karka | Kumbha | `mercury/mars/venus/jupiter` | Single Direct Transit Pass |
| **`065° 00'`** | `Mithuna 05° 00' 00"` | *Mrigashirsha* P4 (Mars) | **Vrishchika** | Karka | Mesha | `mercury/mars/sun/mars` | Single Direct Transit Pass |
| **`066° 00'`** | `Mithuna 06° 00' 00"` | *Mrigashirsha* P4 (Mars) | **Vrishchika** | Simha | Mithuna | `mercury/mars/moon/jupiter` | Single Direct Transit Pass |
| **`067° 00'`** | `Mithuna 07° 00' 00"` | *Ardra* P1 (Rahu) | **Dhanu** | Simha | Simha | `mercury/rahu/rahu/jupiter` | Single Direct Transit Pass |
| **`068° 00'`** | `Mithuna 08° 00' 00"` | *Ardra* P1 (Rahu) | **Dhanu** | Simha | Tula | `mercury/rahu/rahu/venus` | Single Direct Transit Pass |
| **`069° 00'`** | `Mithuna 09° 00' 00"` | *Ardra* P1 (Rahu) | **Dhanu** | Kanya | Dhanu | `mercury/rahu/jupiter/saturn` | Single Direct Transit Pass |
| **`070° 00'`** | `Mithuna 10° 00' 00"` | *Ardra* P1 (Rahu) | **Makara** | Kanya | Kumbha | `mercury/rahu/jupiter/moon` | Single Direct Transit Pass |
| **`071° 00'`** | `Mithuna 11° 00' 00"` | *Ardra* P2 (Rahu) | **Makara** | Kanya | Mesha | `mercury/rahu/saturn/mercury` | Single Direct Transit Pass |
| **`072° 00'`** | `Mithuna 12° 00' 00"` | *Ardra* P2 (Rahu) | **Makara** | Tula | Mithuna | `mercury/rahu/saturn/rahu` | Single Direct Transit Pass |
| **`073° 00'`** | `Mithuna 13° 00' 00"` | *Ardra* P2 (Rahu) | **Makara** | Tula | Simha | `mercury/rahu/mercury/venus` | Single Direct Transit Pass |
| **`074° 00'`** | `Mithuna 14° 00' 00"` | *Ardra* P3 (Rahu) | **Kumbha** | Tula | Tula | `mercury/rahu/mercury/jupiter` | Single Direct Transit Pass |
| **`075° 00'`** | `Mithuna 15° 00' 00"` | *Ardra* P3 (Rahu) | **Kumbha** | Vrishchika | Dhanu | `mercury/rahu/ketu/saturn` | Single Direct Transit Pass |
| **`076° 00'`** | `Mithuna 16° 00' 00"` | *Ardra* P3 (Rahu) | **Kumbha** | Vrishchika | Kumbha | `mercury/rahu/venus/mars` | Single Direct Transit Pass |
| **`077° 00'`** | `Mithuna 17° 00' 00"` | *Ardra* P4 (Rahu) | **Meena** | Vrishchika | Mesha | `mercury/rahu/venus/saturn` | Single Direct Transit Pass |
| **`078° 00'`** | `Mithuna 18° 00' 00"` | *Ardra* P4 (Rahu) | **Meena** | Dhanu | Mithuna | `mercury/rahu/sun/ketu` | Single Direct Transit Pass |
| **`079° 00'`** | `Mithuna 19° 00' 00"` | *Ardra* P4 (Rahu) | **Meena** | Dhanu | Simha | `mercury/rahu/moon/venus` | Single Direct Transit Pass |
| **`080° 00'`** | `Mithuna 20° 00' 00"` | *Punarvasu* P1 (Jupiter) | **Mesha** | Dhanu | Tula | `mercury/rahu/mars/moon` | Single Direct Transit Pass |
| **`081° 00'`** | `Mithuna 21° 00' 00"` | *Punarvasu* P1 (Jupiter) | **Mesha** | Makara | Dhanu | `mercury/jupiter/jupiter/venus` | Single Direct Transit Pass |
| **`082° 00'`** | `Mithuna 22° 00' 00"` | *Punarvasu* P1 (Jupiter) | **Mesha** | Makara | Kumbha | `mercury/jupiter/saturn/saturn` | Single Direct Transit Pass |
| **`083° 00'`** | `Mithuna 23° 00' 00"` | *Punarvasu* P1 (Jupiter) | **Mesha** | Makara | Mesha | `mercury/jupiter/saturn/moon` | **Mercury Triple-Pass Zone** (`Mithuna 22° 05' 09"`..`Karka 02° 01' 41"`) |
| **`084° 00'`** | `Mithuna 24° 00' 00"` | *Punarvasu* P2 (Jupiter) | **Vrishabha** | Kumbha | Mithuna | `mercury/jupiter/mercury/mercury` | **Mercury Triple-Pass Zone** (`Mithuna 22° 05' 09"`..`Karka 02° 01' 41"`) |
| **`085° 00'`** | `Mithuna 25° 00' 00"` | *Punarvasu* P2 (Jupiter) | **Vrishabha** | Kumbha | Simha | `mercury/jupiter/mercury/rahu` | **Mercury Triple-Pass Zone** (`Mithuna 22° 05' 09"`..`Karka 02° 01' 41"`) |
| **`086° 00'`** | `Mithuna 26° 00' 00"` | *Punarvasu* P2 (Jupiter) | **Vrishabha** | Kumbha | Tula | `mercury/jupiter/ketu/moon` | **Mercury Triple-Pass Zone** (`Mithuna 22° 05' 09"`..`Karka 02° 01' 41"`) |
| **`087° 00'`** | `Mithuna 27° 00' 00"` | *Punarvasu* P3 (Jupiter) | **Mithuna** | Meena | Dhanu | `mercury/jupiter/venus/sun` | **Mercury Triple-Pass Zone** (`Mithuna 22° 05' 09"`..`Karka 02° 01' 41"`) |
| **`088° 00'`** | `Mithuna 28° 00' 00"` | *Punarvasu* P3 (Jupiter) | **Mithuna** | Meena | Kumbha | `mercury/jupiter/venus/saturn` | **Mercury Triple-Pass Zone** (`Mithuna 22° 05' 09"`..`Karka 02° 01' 41"`) |
| **`089° 00'`** | `Mithuna 29° 00' 00"` | *Punarvasu* P3 (Jupiter) | **Mithuna** | Meena | Mesha | `mercury/jupiter/sun/rahu` | **Mercury Triple-Pass Zone** (`Mithuna 22° 05' 09"`..`Karka 02° 01' 41"`) |
| **`090° 00'`** | `Karka 00° 00' 00"` | *Punarvasu* P4 (Jupiter) | **Karka** | Meena | Karka | `moon/jupiter/moon/saturn` | **Mercury Triple-Pass Zone** (`Mithuna 22° 05' 09"`..`Karka 02° 01' 41"`) |
| **`091° 00'`** | `Karka 01° 00' 00"` | *Punarvasu* P4 (Jupiter) | **Karka** | Meena | Kanya | `moon/jupiter/mars/mercury` | **Mercury Triple-Pass Zone** (`Mithuna 22° 05' 09"`..`Karka 02° 01' 41"`) |
| **`092° 00'`** | `Karka 02° 00' 00"` | *Punarvasu* P4 (Jupiter) | **Karka** | Meena | Vrishchika | `moon/jupiter/rahu/saturn` | **Mercury Triple-Pass Zone** (`Mithuna 22° 05' 09"`..`Karka 02° 01' 41"`) |
| **`093° 00'`** | `Karka 03° 00' 00"` | *Punarvasu* P4 (Jupiter) | **Karka** | Mesha | Makara | `moon/jupiter/rahu/sun` | Single Direct Transit Pass |
| **`094° 00'`** | `Karka 04° 00' 00"` | *Pushya* P1 (Saturn) | **Simha** | Mesha | Meena | `moon/saturn/saturn/ketu` | Single Direct Transit Pass |
| **`095° 00'`** | `Karka 05° 00' 00"` | *Pushya* P1 (Saturn) | **Simha** | Mesha | Vrishabha | `moon/saturn/saturn/rahu` | Single Direct Transit Pass |
| **`096° 00'`** | `Karka 06° 00' 00"` | *Pushya* P1 (Saturn) | **Simha** | Vrishabha | Karka | `moon/saturn/mercury/venus` | Single Direct Transit Pass |
| **`097° 00'`** | `Karka 07° 00' 00"` | *Pushya* P2 (Saturn) | **Kanya** | Vrishabha | Kanya | `moon/saturn/mercury/jupiter` | Single Direct Transit Pass |
| **`098° 00'`** | `Karka 08° 00' 00"` | *Pushya* P2 (Saturn) | **Kanya** | Vrishabha | Vrishchika | `moon/saturn/ketu/saturn` | Single Direct Transit Pass |
| **`099° 00'`** | `Karka 09° 00' 00"` | *Pushya* P2 (Saturn) | **Kanya** | Mithuna | Makara | `moon/saturn/venus/rahu` | Single Direct Transit Pass |
| **`100° 00'`** | `Karka 10° 00' 00"` | *Pushya* P2 (Saturn) | **Tula** | Mithuna | Meena | `moon/saturn/venus/mercury` | Single Direct Transit Pass |
| **`101° 00'`** | `Karka 11° 00' 00"` | *Pushya* P3 (Saturn) | **Tula** | Mithuna | Vrishabha | `moon/saturn/sun/venus` | Single Direct Transit Pass |
| **`102° 00'`** | `Karka 12° 00' 00"` | *Pushya* P3 (Saturn) | **Tula** | Karka | Karka | `moon/saturn/moon/venus` | Single Direct Transit Pass |
| **`103° 00'`** | `Karka 13° 00' 00"` | *Pushya* P3 (Saturn) | **Tula** | Karka | Kanya | `moon/saturn/rahu/rahu` | Single Direct Transit Pass |
| **`104° 00'`** | `Karka 14° 00' 00"` | *Pushya* P4 (Saturn) | **Vrishchika** | Karka | Vrishchika | `moon/saturn/rahu/mercury` | Single Direct Transit Pass |
| **`105° 00'`** | `Karka 15° 00' 00"` | *Pushya* P4 (Saturn) | **Vrishchika** | Simha | Makara | `moon/saturn/jupiter/jupiter` | Single Direct Transit Pass |
| **`106° 00'`** | `Karka 16° 00' 00"` | *Pushya* P4 (Saturn) | **Vrishchika** | Simha | Meena | `moon/saturn/jupiter/venus` | Single Direct Transit Pass |
| **`107° 00'`** | `Karka 17° 00' 00"` | *Ashlesha* P1 (Mercury) | **Dhanu** | Simha | Vrishabha | `moon/mercury/mercury/ketu` | Single Direct Transit Pass |
| **`108° 00'`** | `Karka 18° 00' 00"` | *Ashlesha* P1 (Mercury) | **Dhanu** | Kanya | Karka | `moon/mercury/mercury/rahu` | Single Direct Transit Pass |
| **`109° 00'`** | `Karka 19° 00' 00"` | *Ashlesha* P1 (Mercury) | **Dhanu** | Kanya | Kanya | `moon/mercury/ketu/jupiter` | Single Direct Transit Pass |
| **`110° 00'`** | `Karka 20° 00' 00"` | *Ashlesha* P1 (Mercury) | **Makara** | Kanya | Vrishchika | `moon/mercury/venus/moon` | Single Direct Transit Pass |
| **`111° 00'`** | `Karka 21° 00' 00"` | *Ashlesha* P2 (Mercury) | **Makara** | Tula | Makara | `moon/mercury/venus/saturn` | Single Direct Transit Pass |
| **`112° 00'`** | `Karka 22° 00' 00"` | *Ashlesha* P2 (Mercury) | **Makara** | Tula | Meena | `moon/mercury/sun/mercury` | Single Direct Transit Pass |
| **`113° 00'`** | `Karka 23° 00' 00"` | *Ashlesha* P2 (Mercury) | **Makara** | Tula | Vrishabha | `moon/mercury/moon/mercury` | **Jupiter Triple-Pass Zone** (`Karka 22° 45' 15"`..`Simha 02° 47' 18"`) |
| **`114° 00'`** | `Karka 24° 00' 00"` | *Ashlesha* P3 (Mercury) | **Kumbha** | Vrishchika | Karka | `moon/mercury/mars/venus` | **Jupiter Triple-Pass Zone** (`Karka 22° 45' 15"`..`Simha 02° 47' 18"`) |
| **`115° 00'`** | `Karka 25° 00' 00"` | *Ashlesha* P3 (Mercury) | **Kumbha** | Vrishchika | Kanya | `moon/mercury/rahu/mercury` | **Jupiter Triple-Pass Zone** (`Karka 22° 45' 15"`..`Simha 02° 47' 18"`) |
| **`116° 00'`** | `Karka 26° 00' 00"` | *Ashlesha* P3 (Mercury) | **Kumbha** | Vrishchika | Vrishchika | `moon/mercury/rahu/mars` | **Jupiter Triple-Pass Zone** (`Karka 22° 45' 15"`..`Simha 02° 47' 18"`) |
| **`117° 00'`** | `Karka 27° 00' 00"` | *Ashlesha* P4 (Mercury) | **Meena** | Dhanu | Makara | `moon/mercury/jupiter/venus` | **Jupiter Triple-Pass Zone** (`Karka 22° 45' 15"`..`Simha 02° 47' 18"`); **Mars Triple-Pass Zone** (`Karka 26° 41' 09"`..`Simha 16° 11' 28"`) |
| **`118° 00'`** | `Karka 28° 00' 00"` | *Ashlesha* P4 (Mercury) | **Meena** | Dhanu | Meena | `moon/mercury/saturn/saturn` | **Jupiter Triple-Pass Zone** (`Karka 22° 45' 15"`..`Simha 02° 47' 18"`); **Mars Triple-Pass Zone** (`Karka 26° 41' 09"`..`Simha 16° 11' 28"`) |
| **`119° 00'`** | `Karka 29° 00' 00"` | *Ashlesha* P4 (Mercury) | **Meena** | Dhanu | Vrishabha | `moon/mercury/saturn/sun` | **Jupiter Triple-Pass Zone** (`Karka 22° 45' 15"`..`Simha 02° 47' 18"`); **Mars Triple-Pass Zone** (`Karka 26° 41' 09"`..`Simha 16° 11' 28"`) |
| **`120° 00'`** | `Simha 00° 00' 00"` | *Magha* P1 (Ketu) | **Mesha** | Simha | Simha | `sun/mercury/saturn/jupiter` | **Jupiter Triple-Pass Zone** (`Karka 22° 45' 15"`..`Simha 02° 47' 18"`); **Mars Triple-Pass Zone** (`Karka 26° 41' 09"`..`Simha 16° 11' 28"`) |
| **`121° 00'`** | `Simha 01° 00' 00"` | *Magha* P1 (Ketu) | **Mesha** | Simha | Tula | `sun/ketu/venus/venus` | **Jupiter Triple-Pass Zone** (`Karka 22° 45' 15"`..`Simha 02° 47' 18"`); **Mars Triple-Pass Zone** (`Karka 26° 41' 09"`..`Simha 16° 11' 28"`) |
| **`122° 00'`** | `Simha 02° 00' 00"` | *Magha* P1 (Ketu) | **Mesha** | Simha | Dhanu | `sun/ketu/venus/jupiter` | **Jupiter Triple-Pass Zone** (`Karka 22° 45' 15"`..`Simha 02° 47' 18"`); **Mars Triple-Pass Zone** (`Karka 26° 41' 09"`..`Simha 16° 11' 28"`) |
| **`123° 00'`** | `Simha 03° 00' 00"` | *Magha* P1 (Ketu) | **Mesha** | Kanya | Kumbha | `sun/ketu/sun/sun` | **Mars Triple-Pass Zone** (`Karka 26° 41' 09"`..`Simha 16° 11' 28"`) |
| **`124° 00'`** | `Simha 04° 00' 00"` | *Magha* P2 (Ketu) | **Vrishabha** | Kanya | Mesha | `sun/ketu/moon/jupiter` | **Mars Triple-Pass Zone** (`Karka 26° 41' 09"`..`Simha 16° 11' 28"`) |
| **`125° 00'`** | `Simha 05° 00' 00"` | *Magha* P2 (Ketu) | **Vrishabha** | Kanya | Mithuna | `sun/ketu/mars/jupiter` | **Mars Triple-Pass Zone** (`Karka 26° 41' 09"`..`Simha 16° 11' 28"`) |
| **`126° 00'`** | `Simha 06° 00' 00"` | *Magha* P2 (Ketu) | **Vrishabha** | Tula | Simha | `sun/ketu/rahu/jupiter` | **Mars Triple-Pass Zone** (`Karka 26° 41' 09"`..`Simha 16° 11' 28"`) |
| **`127° 00'`** | `Simha 07° 00' 00"` | *Magha* P3 (Ketu) | **Mithuna** | Tula | Tula | `sun/ketu/rahu/venus` | **Mars Triple-Pass Zone** (`Karka 26° 41' 09"`..`Simha 16° 11' 28"`) |
| **`128° 00'`** | `Simha 08° 00' 00"` | *Magha* P3 (Ketu) | **Mithuna** | Tula | Dhanu | `sun/ketu/jupiter/saturn` | **Mars Triple-Pass Zone** (`Karka 26° 41' 09"`..`Simha 16° 11' 28"`) |
| **`129° 00'`** | `Simha 09° 00' 00"` | *Magha* P3 (Ketu) | **Mithuna** | Vrishchika | Kumbha | `sun/ketu/jupiter/mars` | **Mars Triple-Pass Zone** (`Karka 26° 41' 09"`..`Simha 16° 11' 28"`) |
| **`130° 00'`** | `Simha 10° 00' 00"` | *Magha* P4 (Ketu) | **Karka** | Vrishchika | Mesha | `sun/ketu/saturn/ketu` | **Mars Triple-Pass Zone** (`Karka 26° 41' 09"`..`Simha 16° 11' 28"`) |
| **`131° 00'`** | `Simha 11° 00' 00"` | *Magha* P4 (Ketu) | **Karka** | Vrishchika | Mithuna | `sun/ketu/saturn/rahu` | **Mars Triple-Pass Zone** (`Karka 26° 41' 09"`..`Simha 16° 11' 28"`) |
| **`132° 00'`** | `Simha 12° 00' 00"` | *Magha* P4 (Ketu) | **Karka** | Dhanu | Simha | `sun/ketu/mercury/venus` | **Mars Triple-Pass Zone** (`Karka 26° 41' 09"`..`Simha 16° 11' 28"`) |
| **`133° 00'`** | `Simha 13° 00' 00"` | *Magha* P4 (Ketu) | **Karka** | Dhanu | Tula | `sun/ketu/mercury/jupiter` | **Mars Triple-Pass Zone** (`Karka 26° 41' 09"`..`Simha 16° 11' 28"`) |
| **`134° 00'`** | `Simha 14° 00' 00"` | *Purva Phalguni* P1 (Venus) | **Simha** | Dhanu | Dhanu | `sun/venus/venus/moon` | **Mars Triple-Pass Zone** (`Karka 26° 41' 09"`..`Simha 16° 11' 28"`) |
| **`135° 00'`** | `Simha 15° 00' 00"` | *Purva Phalguni* P1 (Venus) | **Simha** | Makara | Kumbha | `sun/venus/venus/saturn` | **Mars Triple-Pass Zone** (`Karka 26° 41' 09"`..`Simha 16° 11' 28"`) |
| **`136° 00'`** | `Simha 16° 00' 00"` | *Purva Phalguni* P1 (Venus) | **Simha** | Makara | Mesha | `sun/venus/sun/mercury` | **Mars Triple-Pass Zone** (`Karka 26° 41' 09"`..`Simha 16° 11' 28"`) |
| **`137° 00'`** | `Simha 17° 00' 00"` | *Purva Phalguni* P2 (Venus) | **Kanya** | Makara | Mithuna | `sun/venus/moon/mercury` | Single Direct Transit Pass |
| **`138° 00'`** | `Simha 18° 00' 00"` | *Purva Phalguni* P2 (Venus) | **Kanya** | Kumbha | Simha | `sun/venus/mars/venus` | Single Direct Transit Pass |
| **`139° 00'`** | `Simha 19° 00' 00"` | *Purva Phalguni* P2 (Venus) | **Kanya** | Kumbha | Tula | `sun/venus/rahu/mercury` | Single Direct Transit Pass |
| **`140° 00'`** | `Simha 20° 00' 00"` | *Purva Phalguni* P2 (Venus) | **Tula** | Kumbha | Dhanu | `sun/venus/rahu/mars` | Single Direct Transit Pass |
| **`141° 00'`** | `Simha 21° 00' 00"` | *Purva Phalguni* P3 (Venus) | **Tula** | Meena | Kumbha | `sun/venus/jupiter/venus` | Single Direct Transit Pass |
| **`142° 00'`** | `Simha 22° 00' 00"` | *Purva Phalguni* P3 (Venus) | **Tula** | Meena | Mesha | `sun/venus/saturn/saturn` | Single Direct Transit Pass |
| **`143° 00'`** | `Simha 23° 00' 00"` | *Purva Phalguni* P3 (Venus) | **Tula** | Meena | Mithuna | `sun/venus/saturn/sun` | Single Direct Transit Pass |
| **`144° 00'`** | `Simha 24° 00' 00"` | *Purva Phalguni* P4 (Venus) | **Vrishchika** | Mesha | Simha | `sun/venus/saturn/jupiter` | Single Direct Transit Pass |
| **`145° 00'`** | `Simha 25° 00' 00"` | *Purva Phalguni* P4 (Venus) | **Vrishchika** | Mesha | Tula | `sun/venus/mercury/mars` | Single Direct Transit Pass |
| **`146° 00'`** | `Simha 26° 00' 00"` | *Purva Phalguni* P4 (Venus) | **Vrishchika** | Mesha | Dhanu | `sun/venus/ketu/venus` | Single Direct Transit Pass |
| **`147° 00'`** | `Simha 27° 00' 00"` | *Uttara Phalguni* P1 (Sun) | **Dhanu** | Vrishabha | Kumbha | `sun/sun/sun/saturn` | Single Direct Transit Pass |
| **`148° 00'`** | `Simha 28° 00' 00"` | *Uttara Phalguni* P1 (Sun) | **Dhanu** | Vrishabha | Mesha | `sun/sun/moon/mercury` | Single Direct Transit Pass |
| **`149° 00'`** | `Simha 29° 00' 00"` | *Uttara Phalguni* P1 (Sun) | **Dhanu** | Vrishabha | Mithuna | `sun/sun/mars/venus` | Single Direct Transit Pass |
| **`150° 00'`** | `Kanya 00° 00' 00"` | *Uttara Phalguni* P1 (Sun) | **Makara** | Vrishabha | Kanya | `mercury/sun/rahu/saturn` | Single Direct Transit Pass |
| **`151° 00'`** | `Kanya 01° 00' 00"` | *Uttara Phalguni* P2 (Sun) | **Makara** | Vrishabha | Vrishchika | `mercury/sun/rahu/moon` | Single Direct Transit Pass |
| **`152° 00'`** | `Kanya 02° 00' 00"` | *Uttara Phalguni* P2 (Sun) | **Makara** | Vrishabha | Makara | `mercury/sun/jupiter/ketu` | Single Direct Transit Pass |
| **`153° 00'`** | `Kanya 03° 00' 00"` | *Uttara Phalguni* P2 (Sun) | **Makara** | Mithuna | Meena | `mercury/sun/jupiter/rahu` | Single Direct Transit Pass |
| **`154° 00'`** | `Kanya 04° 00' 00"` | *Uttara Phalguni* P3 (Sun) | **Kumbha** | Mithuna | Vrishabha | `mercury/sun/saturn/venus` | Single Direct Transit Pass |
| **`155° 00'`** | `Kanya 05° 00' 00"` | *Uttara Phalguni* P3 (Sun) | **Kumbha** | Mithuna | Karka | `mercury/sun/saturn/jupiter` | Single Direct Transit Pass |
| **`156° 00'`** | `Kanya 06° 00' 00"` | *Uttara Phalguni* P3 (Sun) | **Kumbha** | Karka | Kanya | `mercury/sun/mercury/moon` | Single Direct Transit Pass |
| **`157° 00'`** | `Kanya 07° 00' 00"` | *Uttara Phalguni* P4 (Sun) | **Meena** | Karka | Vrishchika | `mercury/sun/mercury/saturn` | Single Direct Transit Pass |
| **`158° 00'`** | `Kanya 08° 00' 00"` | *Uttara Phalguni* P4 (Sun) | **Meena** | Karka | Makara | `mercury/sun/venus/venus` | Single Direct Transit Pass |
| **`159° 00'`** | `Kanya 09° 00' 00"` | *Uttara Phalguni* P4 (Sun) | **Meena** | Simha | Meena | `mercury/sun/venus/jupiter` | Single Direct Transit Pass |
| **`160° 00'`** | `Kanya 10° 00' 00"` | *Hasta* P1 (Moon) | **Mesha** | Simha | Vrishabha | `mercury/sun/venus/ketu` | Single Direct Transit Pass |
| **`161° 00'`** | `Kanya 11° 00' 00"` | *Hasta* P1 (Moon) | **Mesha** | Simha | Karka | `mercury/moon/moon/venus` | Single Direct Transit Pass |
| **`162° 00'`** | `Kanya 12° 00' 00"` | *Hasta* P1 (Moon) | **Mesha** | Kanya | Kanya | `mercury/moon/rahu/rahu` | Single Direct Transit Pass |
| **`163° 00'`** | `Kanya 13° 00' 00"` | *Hasta* P1 (Moon) | **Mesha** | Kanya | Vrishchika | `mercury/moon/rahu/mercury` | Single Direct Transit Pass |
| **`164° 00'`** | `Kanya 14° 00' 00"` | *Hasta* P2 (Moon) | **Vrishabha** | Kanya | Makara | `mercury/moon/jupiter/jupiter` | Single Direct Transit Pass |
| **`165° 00'`** | `Kanya 15° 00' 00"` | *Hasta* P2 (Moon) | **Vrishabha** | Tula | Meena | `mercury/moon/jupiter/venus` | Single Direct Transit Pass |
| **`166° 00'`** | `Kanya 16° 00' 00"` | *Hasta* P2 (Moon) | **Vrishabha** | Tula | Vrishabha | `mercury/moon/saturn/saturn` | Single Direct Transit Pass |
| **`167° 00'`** | `Kanya 17° 00' 00"` | *Hasta* P3 (Moon) | **Mithuna** | Tula | Karka | `mercury/moon/saturn/moon` | Single Direct Transit Pass |
| **`168° 00'`** | `Kanya 18° 00' 00"` | *Hasta* P3 (Moon) | **Mithuna** | Vrishchika | Kanya | `mercury/moon/mercury/mercury` | Single Direct Transit Pass |
| **`169° 00'`** | `Kanya 19° 00' 00"` | *Hasta* P3 (Moon) | **Mithuna** | Vrishchika | Vrishchika | `mercury/moon/mercury/rahu` | Single Direct Transit Pass |
| **`170° 00'`** | `Kanya 20° 00' 00"` | *Hasta* P4 (Moon) | **Karka** | Vrishchika | Makara | `mercury/moon/ketu/rahu` | Single Direct Transit Pass |
| **`171° 00'`** | `Kanya 21° 00' 00"` | *Hasta* P4 (Moon) | **Karka** | Dhanu | Meena | `mercury/moon/venus/moon` | Single Direct Transit Pass |
| **`172° 00'`** | `Kanya 22° 00' 00"` | *Hasta* P4 (Moon) | **Karka** | Dhanu | Vrishabha | `mercury/moon/venus/saturn` | Single Direct Transit Pass |
| **`173° 00'`** | `Kanya 23° 00' 00"` | *Hasta* P4 (Moon) | **Karka** | Dhanu | Karka | `mercury/moon/sun/saturn` | Single Direct Transit Pass |
| **`174° 00'`** | `Kanya 24° 00' 00"` | *Chitra* P1 (Mars) | **Simha** | Makara | Kanya | `mercury/mars/mars/venus` | Single Direct Transit Pass |
| **`175° 00'`** | `Kanya 25° 00' 00"` | *Chitra* P1 (Mars) | **Simha** | Makara | Vrishchika | `mercury/mars/rahu/mercury` | Single Direct Transit Pass |
| **`176° 00'`** | `Kanya 26° 00' 00"` | *Chitra* P1 (Mars) | **Simha** | Makara | Makara | `mercury/mars/rahu/mars` | Single Direct Transit Pass |
| **`177° 00'`** | `Kanya 27° 00' 00"` | *Chitra* P2 (Mars) | **Kanya** | Kumbha | Meena | `mercury/mars/jupiter/venus` | Single Direct Transit Pass |
| **`178° 00'`** | `Kanya 28° 00' 00"` | *Chitra* P2 (Mars) | **Kanya** | Kumbha | Vrishabha | `mercury/mars/saturn/saturn` | Single Direct Transit Pass |
| **`179° 00'`** | `Kanya 29° 00' 00"` | *Chitra* P2 (Mars) | **Kanya** | Kumbha | Karka | `mercury/mars/saturn/sun` | **Venus Triple-Pass Zone** (`Kanya 28° 37' 44"`..`Tula 14° 15' 29"`) |
| **`180° 00'`** | `Tula 00° 00' 00"` | *Chitra* P2 (Mars) | **Tula** | Tula | Tula | `venus/mars/saturn/jupiter` | **Venus Triple-Pass Zone** (`Kanya 28° 37' 44"`..`Tula 14° 15' 29"`) |
| **`181° 00'`** | `Tula 01° 00' 00"` | *Chitra* P3 (Mars) | **Tula** | Tula | Dhanu | `venus/mars/mercury/mars` | **Venus Triple-Pass Zone** (`Kanya 28° 37' 44"`..`Tula 14° 15' 29"`) |
| **`182° 00'`** | `Tula 02° 00' 00"` | *Chitra* P3 (Mars) | **Tula** | Tula | Kumbha | `venus/mars/ketu/venus` | **Venus Triple-Pass Zone** (`Kanya 28° 37' 44"`..`Tula 14° 15' 29"`) |
| **`183° 00'`** | `Tula 03° 00' 00"` | *Chitra* P3 (Mars) | **Tula** | Vrishchika | Mesha | `venus/mars/venus/venus` | **Venus Triple-Pass Zone** (`Kanya 28° 37' 44"`..`Tula 14° 15' 29"`) |
| **`184° 00'`** | `Tula 04° 00' 00"` | *Chitra* P4 (Mars) | **Vrishchika** | Vrishchika | Mithuna | `venus/mars/venus/jupiter` | **Venus Triple-Pass Zone** (`Kanya 28° 37' 44"`..`Tula 14° 15' 29"`) |
| **`185° 00'`** | `Tula 05° 00' 00"` | *Chitra* P4 (Mars) | **Vrishchika** | Vrishchika | Simha | `venus/mars/sun/mars` | **Venus Triple-Pass Zone** (`Kanya 28° 37' 44"`..`Tula 14° 15' 29"`) |
| **`186° 00'`** | `Tula 06° 00' 00"` | *Chitra* P4 (Mars) | **Vrishchika** | Dhanu | Tula | `venus/mars/moon/jupiter` | **Venus Triple-Pass Zone** (`Kanya 28° 37' 44"`..`Tula 14° 15' 29"`) |
| **`187° 00'`** | `Tula 07° 00' 00"` | *Swati* P1 (Rahu) | **Dhanu** | Dhanu | Dhanu | `venus/rahu/rahu/jupiter` | **Venus Triple-Pass Zone** (`Kanya 28° 37' 44"`..`Tula 14° 15' 29"`) |
| **`188° 00'`** | `Tula 08° 00' 00"` | *Swati* P1 (Rahu) | **Dhanu** | Dhanu | Kumbha | `venus/rahu/rahu/venus` | **Venus Triple-Pass Zone** (`Kanya 28° 37' 44"`..`Tula 14° 15' 29"`) |
| **`189° 00'`** | `Tula 09° 00' 00"` | *Swati* P1 (Rahu) | **Dhanu** | Makara | Mesha | `venus/rahu/jupiter/saturn` | **Venus Triple-Pass Zone** (`Kanya 28° 37' 44"`..`Tula 14° 15' 29"`) |
| **`190° 00'`** | `Tula 10° 00' 00"` | *Swati* P1 (Rahu) | **Makara** | Makara | Mithuna | `venus/rahu/jupiter/moon` | **Venus Triple-Pass Zone** (`Kanya 28° 37' 44"`..`Tula 14° 15' 29"`) |
| **`191° 00'`** | `Tula 11° 00' 00"` | *Swati* P2 (Rahu) | **Makara** | Makara | Simha | `venus/rahu/saturn/mercury` | **Venus Triple-Pass Zone** (`Kanya 28° 37' 44"`..`Tula 14° 15' 29"`); **Mercury Triple-Pass Zone** (`Tula 10° 47' 56"`..`Tula 26° 44' 43"`) |
| **`192° 00'`** | `Tula 12° 00' 00"` | *Swati* P2 (Rahu) | **Makara** | Kumbha | Tula | `venus/rahu/saturn/rahu` | **Venus Triple-Pass Zone** (`Kanya 28° 37' 44"`..`Tula 14° 15' 29"`); **Mercury Triple-Pass Zone** (`Tula 10° 47' 56"`..`Tula 26° 44' 43"`) |
| **`193° 00'`** | `Tula 13° 00' 00"` | *Swati* P2 (Rahu) | **Makara** | Kumbha | Dhanu | `venus/rahu/mercury/venus` | **Venus Triple-Pass Zone** (`Kanya 28° 37' 44"`..`Tula 14° 15' 29"`); **Mercury Triple-Pass Zone** (`Tula 10° 47' 56"`..`Tula 26° 44' 43"`) |
| **`194° 00'`** | `Tula 14° 00' 00"` | *Swati* P3 (Rahu) | **Kumbha** | Kumbha | Kumbha | `venus/rahu/mercury/jupiter` | **Venus Triple-Pass Zone** (`Kanya 28° 37' 44"`..`Tula 14° 15' 29"`); **Mercury Triple-Pass Zone** (`Tula 10° 47' 56"`..`Tula 26° 44' 43"`) |
| **`195° 00'`** | `Tula 15° 00' 00"` | *Swati* P3 (Rahu) | **Kumbha** | Meena | Mesha | `venus/rahu/ketu/saturn` | **Mercury Triple-Pass Zone** (`Tula 10° 47' 56"`..`Tula 26° 44' 43"`) |
| **`196° 00'`** | `Tula 16° 00' 00"` | *Swati* P3 (Rahu) | **Kumbha** | Meena | Mithuna | `venus/rahu/venus/mars` | **Mercury Triple-Pass Zone** (`Tula 10° 47' 56"`..`Tula 26° 44' 43"`) |
| **`197° 00'`** | `Tula 17° 00' 00"` | *Swati* P4 (Rahu) | **Meena** | Meena | Simha | `venus/rahu/venus/saturn` | **Mercury Triple-Pass Zone** (`Tula 10° 47' 56"`..`Tula 26° 44' 43"`) |
| **`198° 00'`** | `Tula 18° 00' 00"` | *Swati* P4 (Rahu) | **Meena** | Mesha | Tula | `venus/rahu/sun/ketu` | **Mercury Triple-Pass Zone** (`Tula 10° 47' 56"`..`Tula 26° 44' 43"`) |
| **`199° 00'`** | `Tula 19° 00' 00"` | *Swati* P4 (Rahu) | **Meena** | Mesha | Dhanu | `venus/rahu/moon/venus` | **Mercury Triple-Pass Zone** (`Tula 10° 47' 56"`..`Tula 26° 44' 43"`) |
| **`200° 00'`** | `Tula 20° 00' 00"` | *Vishakha* P1 (Jupiter) | **Mesha** | Mesha | Kumbha | `venus/rahu/mars/moon` | **Mercury Triple-Pass Zone** (`Tula 10° 47' 56"`..`Tula 26° 44' 43"`) |
| **`201° 00'`** | `Tula 21° 00' 00"` | *Vishakha* P1 (Jupiter) | **Mesha** | Vrishabha | Mesha | `venus/jupiter/jupiter/venus` | **Mercury Triple-Pass Zone** (`Tula 10° 47' 56"`..`Tula 26° 44' 43"`) |
| **`202° 00'`** | `Tula 22° 00' 00"` | *Vishakha* P1 (Jupiter) | **Mesha** | Vrishabha | Mithuna | `venus/jupiter/saturn/saturn` | **Mercury Triple-Pass Zone** (`Tula 10° 47' 56"`..`Tula 26° 44' 43"`) |
| **`203° 00'`** | `Tula 23° 00' 00"` | *Vishakha* P1 (Jupiter) | **Mesha** | Vrishabha | Simha | `venus/jupiter/saturn/moon` | **Mercury Triple-Pass Zone** (`Tula 10° 47' 56"`..`Tula 26° 44' 43"`) |
| **`204° 00'`** | `Tula 24° 00' 00"` | *Vishakha* P2 (Jupiter) | **Vrishabha** | Mithuna | Tula | `venus/jupiter/mercury/mercury` | **Mercury Triple-Pass Zone** (`Tula 10° 47' 56"`..`Tula 26° 44' 43"`) |
| **`205° 00'`** | `Tula 25° 00' 00"` | *Vishakha* P2 (Jupiter) | **Vrishabha** | Mithuna | Dhanu | `venus/jupiter/mercury/rahu` | **Mercury Triple-Pass Zone** (`Tula 10° 47' 56"`..`Tula 26° 44' 43"`) |
| **`206° 00'`** | `Tula 26° 00' 00"` | *Vishakha* P2 (Jupiter) | **Vrishabha** | Mithuna | Kumbha | `venus/jupiter/ketu/moon` | **Mercury Triple-Pass Zone** (`Tula 10° 47' 56"`..`Tula 26° 44' 43"`) |
| **`207° 00'`** | `Tula 27° 00' 00"` | *Vishakha* P3 (Jupiter) | **Mithuna** | Karka | Mesha | `venus/jupiter/venus/sun` | Single Direct Transit Pass |
| **`208° 00'`** | `Tula 28° 00' 00"` | *Vishakha* P3 (Jupiter) | **Mithuna** | Karka | Mithuna | `venus/jupiter/venus/saturn` | Single Direct Transit Pass |
| **`209° 00'`** | `Tula 29° 00' 00"` | *Vishakha* P3 (Jupiter) | **Mithuna** | Karka | Simha | `venus/jupiter/sun/rahu` | Single Direct Transit Pass |
| **`210° 00'`** | `Vrishchika 00° 00' 00"` | *Vishakha* P4 (Jupiter) | **Karka** | Karka | Vrishchika | `mars/jupiter/moon/saturn` | Single Direct Transit Pass |
| **`211° 00'`** | `Vrishchika 01° 00' 00"` | *Vishakha* P4 (Jupiter) | **Karka** | Karka | Makara | `mars/jupiter/mars/mercury` | Single Direct Transit Pass |
| **`212° 00'`** | `Vrishchika 02° 00' 00"` | *Vishakha* P4 (Jupiter) | **Karka** | Karka | Meena | `mars/jupiter/rahu/saturn` | Single Direct Transit Pass |
| **`213° 00'`** | `Vrishchika 03° 00' 00"` | *Vishakha* P4 (Jupiter) | **Karka** | Simha | Vrishabha | `mars/jupiter/rahu/sun` | Single Direct Transit Pass |
| **`214° 00'`** | `Vrishchika 04° 00' 00"` | *Anuradha* P1 (Saturn) | **Simha** | Simha | Karka | `mars/saturn/saturn/ketu` | Single Direct Transit Pass |
| **`215° 00'`** | `Vrishchika 05° 00' 00"` | *Anuradha* P1 (Saturn) | **Simha** | Simha | Kanya | `mars/saturn/saturn/rahu` | Single Direct Transit Pass |
| **`216° 00'`** | `Vrishchika 06° 00' 00"` | *Anuradha* P1 (Saturn) | **Simha** | Kanya | Vrishchika | `mars/saturn/mercury/venus` | Single Direct Transit Pass |
| **`217° 00'`** | `Vrishchika 07° 00' 00"` | *Anuradha* P2 (Saturn) | **Kanya** | Kanya | Makara | `mars/saturn/mercury/jupiter` | Single Direct Transit Pass |
| **`218° 00'`** | `Vrishchika 08° 00' 00"` | *Anuradha* P2 (Saturn) | **Kanya** | Kanya | Meena | `mars/saturn/ketu/saturn` | Single Direct Transit Pass |
| **`219° 00'`** | `Vrishchika 09° 00' 00"` | *Anuradha* P2 (Saturn) | **Kanya** | Tula | Vrishabha | `mars/saturn/venus/rahu` | Single Direct Transit Pass |
| **`220° 00'`** | `Vrishchika 10° 00' 00"` | *Anuradha* P2 (Saturn) | **Tula** | Tula | Karka | `mars/saturn/venus/mercury` | Single Direct Transit Pass |
| **`221° 00'`** | `Vrishchika 11° 00' 00"` | *Anuradha* P3 (Saturn) | **Tula** | Tula | Kanya | `mars/saturn/sun/venus` | Single Direct Transit Pass |
| **`222° 00'`** | `Vrishchika 12° 00' 00"` | *Anuradha* P3 (Saturn) | **Tula** | Vrishchika | Vrishchika | `mars/saturn/moon/venus` | Single Direct Transit Pass |
| **`223° 00'`** | `Vrishchika 13° 00' 00"` | *Anuradha* P3 (Saturn) | **Tula** | Vrishchika | Makara | `mars/saturn/rahu/rahu` | Single Direct Transit Pass |
| **`224° 00'`** | `Vrishchika 14° 00' 00"` | *Anuradha* P4 (Saturn) | **Vrishchika** | Vrishchika | Meena | `mars/saturn/rahu/mercury` | Single Direct Transit Pass |
| **`225° 00'`** | `Vrishchika 15° 00' 00"` | *Anuradha* P4 (Saturn) | **Vrishchika** | Dhanu | Vrishabha | `mars/saturn/jupiter/jupiter` | Single Direct Transit Pass |
| **`226° 00'`** | `Vrishchika 16° 00' 00"` | *Anuradha* P4 (Saturn) | **Vrishchika** | Dhanu | Karka | `mars/saturn/jupiter/venus` | Single Direct Transit Pass |
| **`227° 00'`** | `Vrishchika 17° 00' 00"` | *Jyeshtha* P1 (Mercury) | **Dhanu** | Dhanu | Kanya | `mars/mercury/mercury/ketu` | Single Direct Transit Pass |
| **`228° 00'`** | `Vrishchika 18° 00' 00"` | *Jyeshtha* P1 (Mercury) | **Dhanu** | Makara | Vrishchika | `mars/mercury/mercury/rahu` | Single Direct Transit Pass |
| **`229° 00'`** | `Vrishchika 19° 00' 00"` | *Jyeshtha* P1 (Mercury) | **Dhanu** | Makara | Makara | `mars/mercury/ketu/jupiter` | Single Direct Transit Pass |
| **`230° 00'`** | `Vrishchika 20° 00' 00"` | *Jyeshtha* P1 (Mercury) | **Makara** | Makara | Meena | `mars/mercury/venus/moon` | Single Direct Transit Pass |
| **`231° 00'`** | `Vrishchika 21° 00' 00"` | *Jyeshtha* P2 (Mercury) | **Makara** | Kumbha | Vrishabha | `mars/mercury/venus/saturn` | Single Direct Transit Pass |
| **`232° 00'`** | `Vrishchika 22° 00' 00"` | *Jyeshtha* P2 (Mercury) | **Makara** | Kumbha | Karka | `mars/mercury/sun/mercury` | Single Direct Transit Pass |
| **`233° 00'`** | `Vrishchika 23° 00' 00"` | *Jyeshtha* P2 (Mercury) | **Makara** | Kumbha | Kanya | `mars/mercury/moon/mercury` | Single Direct Transit Pass |
| **`234° 00'`** | `Vrishchika 24° 00' 00"` | *Jyeshtha* P3 (Mercury) | **Kumbha** | Meena | Vrishchika | `mars/mercury/mars/venus` | Single Direct Transit Pass |
| **`235° 00'`** | `Vrishchika 25° 00' 00"` | *Jyeshtha* P3 (Mercury) | **Kumbha** | Meena | Makara | `mars/mercury/rahu/mercury` | Single Direct Transit Pass |
| **`236° 00'`** | `Vrishchika 26° 00' 00"` | *Jyeshtha* P3 (Mercury) | **Kumbha** | Meena | Meena | `mars/mercury/rahu/mars` | Single Direct Transit Pass |
| **`237° 00'`** | `Vrishchika 27° 00' 00"` | *Jyeshtha* P4 (Mercury) | **Meena** | Mesha | Vrishabha | `mars/mercury/jupiter/venus` | Single Direct Transit Pass |
| **`238° 00'`** | `Vrishchika 28° 00' 00"` | *Jyeshtha* P4 (Mercury) | **Meena** | Mesha | Karka | `mars/mercury/saturn/saturn` | Single Direct Transit Pass |
| **`239° 00'`** | `Vrishchika 29° 00' 00"` | *Jyeshtha* P4 (Mercury) | **Meena** | Mesha | Kanya | `mars/mercury/saturn/sun` | Single Direct Transit Pass |
| **`240° 00'`** | `Dhanu 00° 00' 00"` | *Mula* P1 (Ketu) | **Mesha** | Dhanu | Dhanu | `jupiter/mercury/saturn/jupiter` | Single Direct Transit Pass |
| **`241° 00'`** | `Dhanu 01° 00' 00"` | *Mula* P1 (Ketu) | **Mesha** | Dhanu | Kumbha | `jupiter/ketu/venus/venus` | Single Direct Transit Pass |
| **`242° 00'`** | `Dhanu 02° 00' 00"` | *Mula* P1 (Ketu) | **Mesha** | Dhanu | Mesha | `jupiter/ketu/venus/jupiter` | Single Direct Transit Pass |
| **`243° 00'`** | `Dhanu 03° 00' 00"` | *Mula* P1 (Ketu) | **Mesha** | Makara | Mithuna | `jupiter/ketu/sun/sun` | Single Direct Transit Pass |
| **`244° 00'`** | `Dhanu 04° 00' 00"` | *Mula* P2 (Ketu) | **Vrishabha** | Makara | Simha | `jupiter/ketu/moon/jupiter` | Single Direct Transit Pass |
| **`245° 00'`** | `Dhanu 05° 00' 00"` | *Mula* P2 (Ketu) | **Vrishabha** | Makara | Tula | `jupiter/ketu/mars/jupiter` | Single Direct Transit Pass |
| **`246° 00'`** | `Dhanu 06° 00' 00"` | *Mula* P2 (Ketu) | **Vrishabha** | Kumbha | Dhanu | `jupiter/ketu/rahu/jupiter` | Single Direct Transit Pass |
| **`247° 00'`** | `Dhanu 07° 00' 00"` | *Mula* P3 (Ketu) | **Mithuna** | Kumbha | Kumbha | `jupiter/ketu/rahu/venus` | Single Direct Transit Pass |
| **`248° 00'`** | `Dhanu 08° 00' 00"` | *Mula* P3 (Ketu) | **Mithuna** | Kumbha | Mesha | `jupiter/ketu/jupiter/saturn` | Single Direct Transit Pass |
| **`249° 00'`** | `Dhanu 09° 00' 00"` | *Mula* P3 (Ketu) | **Mithuna** | Meena | Mithuna | `jupiter/ketu/jupiter/mars` | Single Direct Transit Pass |
| **`250° 00'`** | `Dhanu 10° 00' 00"` | *Mula* P4 (Ketu) | **Karka** | Meena | Simha | `jupiter/ketu/saturn/ketu` | Single Direct Transit Pass |
| **`251° 00'`** | `Dhanu 11° 00' 00"` | *Mula* P4 (Ketu) | **Karka** | Meena | Tula | `jupiter/ketu/saturn/rahu` | Single Direct Transit Pass |
| **`252° 00'`** | `Dhanu 12° 00' 00"` | *Mula* P4 (Ketu) | **Karka** | Mesha | Dhanu | `jupiter/ketu/mercury/venus` | Single Direct Transit Pass |
| **`253° 00'`** | `Dhanu 13° 00' 00"` | *Mula* P4 (Ketu) | **Karka** | Mesha | Kumbha | `jupiter/ketu/mercury/jupiter` | Single Direct Transit Pass |
| **`254° 00'`** | `Dhanu 14° 00' 00"` | *Purva Ashadha* P1 (Venus) | **Simha** | Mesha | Mesha | `jupiter/venus/venus/moon` | Single Direct Transit Pass |
| **`255° 00'`** | `Dhanu 15° 00' 00"` | *Purva Ashadha* P1 (Venus) | **Simha** | Vrishabha | Mithuna | `jupiter/venus/venus/saturn` | Single Direct Transit Pass |
| **`256° 00'`** | `Dhanu 16° 00' 00"` | *Purva Ashadha* P1 (Venus) | **Simha** | Vrishabha | Simha | `jupiter/venus/sun/mercury` | Single Direct Transit Pass |
| **`257° 00'`** | `Dhanu 17° 00' 00"` | *Purva Ashadha* P2 (Venus) | **Kanya** | Vrishabha | Tula | `jupiter/venus/moon/mercury` | Single Direct Transit Pass |
| **`258° 00'`** | `Dhanu 18° 00' 00"` | *Purva Ashadha* P2 (Venus) | **Kanya** | Mithuna | Dhanu | `jupiter/venus/mars/venus` | Single Direct Transit Pass |
| **`259° 00'`** | `Dhanu 19° 00' 00"` | *Purva Ashadha* P2 (Venus) | **Kanya** | Mithuna | Kumbha | `jupiter/venus/rahu/mercury` | Single Direct Transit Pass |
| **`260° 00'`** | `Dhanu 20° 00' 00"` | *Purva Ashadha* P2 (Venus) | **Tula** | Mithuna | Mesha | `jupiter/venus/rahu/mars` | Single Direct Transit Pass |
| **`261° 00'`** | `Dhanu 21° 00' 00"` | *Purva Ashadha* P3 (Venus) | **Tula** | Karka | Mithuna | `jupiter/venus/jupiter/venus` | Single Direct Transit Pass |
| **`262° 00'`** | `Dhanu 22° 00' 00"` | *Purva Ashadha* P3 (Venus) | **Tula** | Karka | Simha | `jupiter/venus/saturn/saturn` | Single Direct Transit Pass |
| **`263° 00'`** | `Dhanu 23° 00' 00"` | *Purva Ashadha* P3 (Venus) | **Tula** | Karka | Tula | `jupiter/venus/saturn/sun` | Single Direct Transit Pass |
| **`264° 00'`** | `Dhanu 24° 00' 00"` | *Purva Ashadha* P4 (Venus) | **Vrishchika** | Simha | Dhanu | `jupiter/venus/saturn/jupiter` | Single Direct Transit Pass |
| **`265° 00'`** | `Dhanu 25° 00' 00"` | *Purva Ashadha* P4 (Venus) | **Vrishchika** | Simha | Kumbha | `jupiter/venus/mercury/mars` | Single Direct Transit Pass |
| **`266° 00'`** | `Dhanu 26° 00' 00"` | *Purva Ashadha* P4 (Venus) | **Vrishchika** | Simha | Mesha | `jupiter/venus/ketu/venus` | Single Direct Transit Pass |
| **`267° 00'`** | `Dhanu 27° 00' 00"` | *Uttara Ashadha* P1 (Sun) | **Dhanu** | Kanya | Mithuna | `jupiter/sun/sun/saturn` | Single Direct Transit Pass |
| **`268° 00'`** | `Dhanu 28° 00' 00"` | *Uttara Ashadha* P1 (Sun) | **Dhanu** | Kanya | Simha | `jupiter/sun/moon/mercury` | Single Direct Transit Pass |
| **`269° 00'`** | `Dhanu 29° 00' 00"` | *Uttara Ashadha* P1 (Sun) | **Dhanu** | Kanya | Tula | `jupiter/sun/mars/venus` | Single Direct Transit Pass |
| **`270° 00'`** | `Makara 00° 00' 00"` | *Uttara Ashadha* P1 (Sun) | **Makara** | Kanya | Makara | `saturn/sun/rahu/saturn` | Single Direct Transit Pass |
| **`271° 00'`** | `Makara 01° 00' 00"` | *Uttara Ashadha* P2 (Sun) | **Makara** | Kanya | Meena | `saturn/sun/rahu/moon` | Single Direct Transit Pass |
| **`272° 00'`** | `Makara 02° 00' 00"` | *Uttara Ashadha* P2 (Sun) | **Makara** | Kanya | Vrishabha | `saturn/sun/jupiter/ketu` | Single Direct Transit Pass |
| **`273° 00'`** | `Makara 03° 00' 00"` | *Uttara Ashadha* P2 (Sun) | **Makara** | Tula | Karka | `saturn/sun/jupiter/rahu` | Single Direct Transit Pass |
| **`274° 00'`** | `Makara 04° 00' 00"` | *Uttara Ashadha* P3 (Sun) | **Kumbha** | Tula | Kanya | `saturn/sun/saturn/venus` | Single Direct Transit Pass |
| **`275° 00'`** | `Makara 05° 00' 00"` | *Uttara Ashadha* P3 (Sun) | **Kumbha** | Tula | Vrishchika | `saturn/sun/saturn/jupiter` | Single Direct Transit Pass |
| **`276° 00'`** | `Makara 06° 00' 00"` | *Uttara Ashadha* P3 (Sun) | **Kumbha** | Vrishchika | Makara | `saturn/sun/mercury/moon` | Single Direct Transit Pass |
| **`277° 00'`** | `Makara 07° 00' 00"` | *Uttara Ashadha* P4 (Sun) | **Meena** | Vrishchika | Meena | `saturn/sun/mercury/saturn` | Single Direct Transit Pass |
| **`278° 00'`** | `Makara 08° 00' 00"` | *Uttara Ashadha* P4 (Sun) | **Meena** | Vrishchika | Vrishabha | `saturn/sun/venus/venus` | Single Direct Transit Pass |
| **`279° 00'`** | `Makara 09° 00' 00"` | *Uttara Ashadha* P4 (Sun) | **Meena** | Dhanu | Karka | `saturn/sun/venus/jupiter` | Single Direct Transit Pass |
| **`280° 00'`** | `Makara 10° 00' 00"` | *Shravana* P1 (Moon) | **Mesha** | Dhanu | Kanya | `saturn/sun/venus/ketu` | Single Direct Transit Pass |
| **`281° 00'`** | `Makara 11° 00' 00"` | *Shravana* P1 (Moon) | **Mesha** | Dhanu | Vrishchika | `saturn/moon/moon/venus` | Single Direct Transit Pass |
| **`282° 00'`** | `Makara 12° 00' 00"` | *Shravana* P1 (Moon) | **Mesha** | Makara | Makara | `saturn/moon/rahu/rahu` | Single Direct Transit Pass |
| **`283° 00'`** | `Makara 13° 00' 00"` | *Shravana* P1 (Moon) | **Mesha** | Makara | Meena | `saturn/moon/rahu/mercury` | Single Direct Transit Pass |
| **`284° 00'`** | `Makara 14° 00' 00"` | *Shravana* P2 (Moon) | **Vrishabha** | Makara | Vrishabha | `saturn/moon/jupiter/jupiter` | Single Direct Transit Pass |
| **`285° 00'`** | `Makara 15° 00' 00"` | *Shravana* P2 (Moon) | **Vrishabha** | Kumbha | Karka | `saturn/moon/jupiter/venus` | Single Direct Transit Pass |
| **`286° 00'`** | `Makara 16° 00' 00"` | *Shravana* P2 (Moon) | **Vrishabha** | Kumbha | Kanya | `saturn/moon/saturn/saturn` | Single Direct Transit Pass |
| **`287° 00'`** | `Makara 17° 00' 00"` | *Shravana* P3 (Moon) | **Mithuna** | Kumbha | Vrishchika | `saturn/moon/saturn/moon` | Single Direct Transit Pass |
| **`288° 00'`** | `Makara 18° 00' 00"` | *Shravana* P3 (Moon) | **Mithuna** | Meena | Makara | `saturn/moon/mercury/mercury` | Single Direct Transit Pass |
| **`289° 00'`** | `Makara 19° 00' 00"` | *Shravana* P3 (Moon) | **Mithuna** | Meena | Meena | `saturn/moon/mercury/rahu` | Single Direct Transit Pass |
| **`290° 00'`** | `Makara 20° 00' 00"` | *Shravana* P4 (Moon) | **Karka** | Meena | Vrishabha | `saturn/moon/ketu/rahu` | Single Direct Transit Pass |
| **`291° 00'`** | `Makara 21° 00' 00"` | *Shravana* P4 (Moon) | **Karka** | Mesha | Karka | `saturn/moon/venus/moon` | Single Direct Transit Pass |
| **`292° 00'`** | `Makara 22° 00' 00"` | *Shravana* P4 (Moon) | **Karka** | Mesha | Kanya | `saturn/moon/venus/saturn` | Single Direct Transit Pass |
| **`293° 00'`** | `Makara 23° 00' 00"` | *Shravana* P4 (Moon) | **Karka** | Mesha | Vrishchika | `saturn/moon/sun/saturn` | Single Direct Transit Pass |
| **`294° 00'`** | `Makara 24° 00' 00"` | *Dhanishta* P1 (Mars) | **Simha** | Vrishabha | Makara | `saturn/mars/mars/venus` | Single Direct Transit Pass |
| **`295° 00'`** | `Makara 25° 00' 00"` | *Dhanishta* P1 (Mars) | **Simha** | Vrishabha | Meena | `saturn/mars/rahu/mercury` | Single Direct Transit Pass |
| **`296° 00'`** | `Makara 26° 00' 00"` | *Dhanishta* P1 (Mars) | **Simha** | Vrishabha | Vrishabha | `saturn/mars/rahu/mars` | Single Direct Transit Pass |
| **`297° 00'`** | `Makara 27° 00' 00"` | *Dhanishta* P2 (Mars) | **Kanya** | Mithuna | Karka | `saturn/mars/jupiter/venus` | **Mercury Triple-Pass Zone** (`Makara 26° 41' 00"`..`Kumbha 11° 44' 32"`) |
| **`298° 00'`** | `Makara 28° 00' 00"` | *Dhanishta* P2 (Mars) | **Kanya** | Mithuna | Kanya | `saturn/mars/saturn/saturn` | **Mercury Triple-Pass Zone** (`Makara 26° 41' 00"`..`Kumbha 11° 44' 32"`) |
| **`299° 00'`** | `Makara 29° 00' 00"` | *Dhanishta* P2 (Mars) | **Kanya** | Mithuna | Vrishchika | `saturn/mars/saturn/sun` | **Mercury Triple-Pass Zone** (`Makara 26° 41' 00"`..`Kumbha 11° 44' 32"`) |
| **`300° 00'`** | `Kumbha 00° 00' 00"` | *Dhanishta* P2 (Mars) | **Tula** | Kumbha | Kumbha | `saturn/mars/saturn/jupiter` | **Mercury Triple-Pass Zone** (`Makara 26° 41' 00"`..`Kumbha 11° 44' 32"`) |
| **`301° 00'`** | `Kumbha 01° 00' 00"` | *Dhanishta* P3 (Mars) | **Tula** | Kumbha | Mesha | `saturn/mars/mercury/mars` | **Mercury Triple-Pass Zone** (`Makara 26° 41' 00"`..`Kumbha 11° 44' 32"`) |
| **`302° 00'`** | `Kumbha 02° 00' 00"` | *Dhanishta* P3 (Mars) | **Tula** | Kumbha | Mithuna | `saturn/mars/ketu/venus` | **Mercury Triple-Pass Zone** (`Makara 26° 41' 00"`..`Kumbha 11° 44' 32"`) |
| **`303° 00'`** | `Kumbha 03° 00' 00"` | *Dhanishta* P3 (Mars) | **Tula** | Meena | Simha | `saturn/mars/venus/venus` | **Mercury Triple-Pass Zone** (`Makara 26° 41' 00"`..`Kumbha 11° 44' 32"`) |
| **`304° 00'`** | `Kumbha 04° 00' 00"` | *Dhanishta* P4 (Mars) | **Vrishchika** | Meena | Tula | `saturn/mars/venus/jupiter` | **Mercury Triple-Pass Zone** (`Makara 26° 41' 00"`..`Kumbha 11° 44' 32"`) |
| **`305° 00'`** | `Kumbha 05° 00' 00"` | *Dhanishta* P4 (Mars) | **Vrishchika** | Meena | Dhanu | `saturn/mars/sun/mars` | **Mercury Triple-Pass Zone** (`Makara 26° 41' 00"`..`Kumbha 11° 44' 32"`) |
| **`306° 00'`** | `Kumbha 06° 00' 00"` | *Dhanishta* P4 (Mars) | **Vrishchika** | Mesha | Kumbha | `saturn/mars/moon/jupiter` | **Mercury Triple-Pass Zone** (`Makara 26° 41' 00"`..`Kumbha 11° 44' 32"`) |
| **`307° 00'`** | `Kumbha 07° 00' 00"` | *Shatabhisha* P1 (Rahu) | **Dhanu** | Mesha | Mesha | `saturn/rahu/rahu/jupiter` | **Mercury Triple-Pass Zone** (`Makara 26° 41' 00"`..`Kumbha 11° 44' 32"`) |
| **`308° 00'`** | `Kumbha 08° 00' 00"` | *Shatabhisha* P1 (Rahu) | **Dhanu** | Mesha | Mithuna | `saturn/rahu/rahu/venus` | **Mercury Triple-Pass Zone** (`Makara 26° 41' 00"`..`Kumbha 11° 44' 32"`) |
| **`309° 00'`** | `Kumbha 09° 00' 00"` | *Shatabhisha* P1 (Rahu) | **Dhanu** | Vrishabha | Simha | `saturn/rahu/jupiter/saturn` | **Mercury Triple-Pass Zone** (`Makara 26° 41' 00"`..`Kumbha 11° 44' 32"`) |
| **`310° 00'`** | `Kumbha 10° 00' 00"` | *Shatabhisha* P1 (Rahu) | **Makara** | Vrishabha | Tula | `saturn/rahu/jupiter/moon` | **Mercury Triple-Pass Zone** (`Makara 26° 41' 00"`..`Kumbha 11° 44' 32"`) |
| **`311° 00'`** | `Kumbha 11° 00' 00"` | *Shatabhisha* P2 (Rahu) | **Makara** | Vrishabha | Dhanu | `saturn/rahu/saturn/mercury` | **Mercury Triple-Pass Zone** (`Makara 26° 41' 00"`..`Kumbha 11° 44' 32"`) |
| **`312° 00'`** | `Kumbha 12° 00' 00"` | *Shatabhisha* P2 (Rahu) | **Makara** | Mithuna | Kumbha | `saturn/rahu/saturn/rahu` | Single Direct Transit Pass |
| **`313° 00'`** | `Kumbha 13° 00' 00"` | *Shatabhisha* P2 (Rahu) | **Makara** | Mithuna | Mesha | `saturn/rahu/mercury/venus` | Single Direct Transit Pass |
| **`314° 00'`** | `Kumbha 14° 00' 00"` | *Shatabhisha* P3 (Rahu) | **Kumbha** | Mithuna | Mithuna | `saturn/rahu/mercury/jupiter` | Single Direct Transit Pass |
| **`315° 00'`** | `Kumbha 15° 00' 00"` | *Shatabhisha* P3 (Rahu) | **Kumbha** | Karka | Simha | `saturn/rahu/ketu/saturn` | Single Direct Transit Pass |
| **`316° 00'`** | `Kumbha 16° 00' 00"` | *Shatabhisha* P3 (Rahu) | **Kumbha** | Karka | Tula | `saturn/rahu/venus/mars` | Single Direct Transit Pass |
| **`317° 00'`** | `Kumbha 17° 00' 00"` | *Shatabhisha* P4 (Rahu) | **Meena** | Karka | Dhanu | `saturn/rahu/venus/saturn` | Single Direct Transit Pass |
| **`318° 00'`** | `Kumbha 18° 00' 00"` | *Shatabhisha* P4 (Rahu) | **Meena** | Simha | Kumbha | `saturn/rahu/sun/ketu` | Single Direct Transit Pass |
| **`319° 00'`** | `Kumbha 19° 00' 00"` | *Shatabhisha* P4 (Rahu) | **Meena** | Simha | Mesha | `saturn/rahu/moon/venus` | Single Direct Transit Pass |
| **`320° 00'`** | `Kumbha 20° 00' 00"` | *Purva Bhadrapada* P1 (Jupiter) | **Mesha** | Simha | Mithuna | `saturn/rahu/mars/moon` | Single Direct Transit Pass |
| **`321° 00'`** | `Kumbha 21° 00' 00"` | *Purva Bhadrapada* P1 (Jupiter) | **Mesha** | Kanya | Simha | `saturn/jupiter/jupiter/venus` | Single Direct Transit Pass |
| **`322° 00'`** | `Kumbha 22° 00' 00"` | *Purva Bhadrapada* P1 (Jupiter) | **Mesha** | Kanya | Tula | `saturn/jupiter/saturn/saturn` | Single Direct Transit Pass |
| **`323° 00'`** | `Kumbha 23° 00' 00"` | *Purva Bhadrapada* P1 (Jupiter) | **Mesha** | Kanya | Dhanu | `saturn/jupiter/saturn/moon` | Single Direct Transit Pass |
| **`324° 00'`** | `Kumbha 24° 00' 00"` | *Purva Bhadrapada* P2 (Jupiter) | **Vrishabha** | Tula | Kumbha | `saturn/jupiter/mercury/mercury` | Single Direct Transit Pass |
| **`325° 00'`** | `Kumbha 25° 00' 00"` | *Purva Bhadrapada* P2 (Jupiter) | **Vrishabha** | Tula | Mesha | `saturn/jupiter/mercury/rahu` | Single Direct Transit Pass |
| **`326° 00'`** | `Kumbha 26° 00' 00"` | *Purva Bhadrapada* P2 (Jupiter) | **Vrishabha** | Tula | Mithuna | `saturn/jupiter/ketu/moon` | Single Direct Transit Pass |
| **`327° 00'`** | `Kumbha 27° 00' 00"` | *Purva Bhadrapada* P3 (Jupiter) | **Mithuna** | Vrishchika | Simha | `saturn/jupiter/venus/sun` | Single Direct Transit Pass |
| **`328° 00'`** | `Kumbha 28° 00' 00"` | *Purva Bhadrapada* P3 (Jupiter) | **Mithuna** | Vrishchika | Tula | `saturn/jupiter/venus/saturn` | Single Direct Transit Pass |
| **`329° 00'`** | `Kumbha 29° 00' 00"` | *Purva Bhadrapada* P3 (Jupiter) | **Mithuna** | Vrishchika | Dhanu | `saturn/jupiter/sun/rahu` | Single Direct Transit Pass |
| **`330° 00'`** | `Meena 00° 00' 00"` | *Purva Bhadrapada* P4 (Jupiter) | **Karka** | Vrishchika | Meena | `jupiter/jupiter/moon/saturn` | Single Direct Transit Pass |
| **`331° 00'`** | `Meena 01° 00' 00"` | *Purva Bhadrapada* P4 (Jupiter) | **Karka** | Vrishchika | Vrishabha | `jupiter/jupiter/mars/mercury` | Single Direct Transit Pass |
| **`332° 00'`** | `Meena 02° 00' 00"` | *Purva Bhadrapada* P4 (Jupiter) | **Karka** | Vrishchika | Karka | `jupiter/jupiter/rahu/saturn` | Single Direct Transit Pass |
| **`333° 00'`** | `Meena 03° 00' 00"` | *Purva Bhadrapada* P4 (Jupiter) | **Karka** | Dhanu | Kanya | `jupiter/jupiter/rahu/sun` | Single Direct Transit Pass |
| **`334° 00'`** | `Meena 04° 00' 00"` | *Uttara Bhadrapada* P1 (Saturn) | **Simha** | Dhanu | Vrishchika | `jupiter/saturn/saturn/ketu` | Single Direct Transit Pass |
| **`335° 00'`** | `Meena 05° 00' 00"` | *Uttara Bhadrapada* P1 (Saturn) | **Simha** | Dhanu | Makara | `jupiter/saturn/saturn/rahu` | Single Direct Transit Pass |
| **`336° 00'`** | `Meena 06° 00' 00"` | *Uttara Bhadrapada* P1 (Saturn) | **Simha** | Makara | Meena | `jupiter/saturn/mercury/venus` | Single Direct Transit Pass |
| **`337° 00'`** | `Meena 07° 00' 00"` | *Uttara Bhadrapada* P2 (Saturn) | **Kanya** | Makara | Vrishabha | `jupiter/saturn/mercury/jupiter` | Single Direct Transit Pass |
| **`338° 00'`** | `Meena 08° 00' 00"` | *Uttara Bhadrapada* P2 (Saturn) | **Kanya** | Makara | Karka | `jupiter/saturn/ketu/saturn` | Single Direct Transit Pass |
| **`339° 00'`** | `Meena 09° 00' 00"` | *Uttara Bhadrapada* P2 (Saturn) | **Kanya** | Kumbha | Kanya | `jupiter/saturn/venus/rahu` | Single Direct Transit Pass |
| **`340° 00'`** | `Meena 10° 00' 00"` | *Uttara Bhadrapada* P2 (Saturn) | **Tula** | Kumbha | Vrishchika | `jupiter/saturn/venus/mercury` | Single Direct Transit Pass |
| **`341° 00'`** | `Meena 11° 00' 00"` | *Uttara Bhadrapada* P3 (Saturn) | **Tula** | Kumbha | Makara | `jupiter/saturn/sun/venus` | Single Direct Transit Pass |
| **`342° 00'`** | `Meena 12° 00' 00"` | *Uttara Bhadrapada* P3 (Saturn) | **Tula** | Meena | Meena | `jupiter/saturn/moon/venus` | Single Direct Transit Pass |
| **`343° 00'`** | `Meena 13° 00' 00"` | *Uttara Bhadrapada* P3 (Saturn) | **Tula** | Meena | Vrishabha | `jupiter/saturn/rahu/rahu` | Single Direct Transit Pass |
| **`344° 00'`** | `Meena 14° 00' 00"` | *Uttara Bhadrapada* P4 (Saturn) | **Vrishchika** | Meena | Karka | `jupiter/saturn/rahu/mercury` | **Saturn Triple-Pass Zone** (`Meena 13° 41' 42"`..`Meena 20° 31' 09"`) |
| **`345° 00'`** | `Meena 15° 00' 00"` | *Uttara Bhadrapada* P4 (Saturn) | **Vrishchika** | Mesha | Kanya | `jupiter/saturn/jupiter/jupiter` | **Saturn Triple-Pass Zone** (`Meena 13° 41' 42"`..`Meena 20° 31' 09"`) |
| **`346° 00'`** | `Meena 16° 00' 00"` | *Uttara Bhadrapada* P4 (Saturn) | **Vrishchika** | Mesha | Vrishchika | `jupiter/saturn/jupiter/venus` | **Saturn Triple-Pass Zone** (`Meena 13° 41' 42"`..`Meena 20° 31' 09"`) |
| **`347° 00'`** | `Meena 17° 00' 00"` | *Revati* P1 (Mercury) | **Dhanu** | Mesha | Makara | `jupiter/mercury/mercury/ketu` | **Saturn Triple-Pass Zone** (`Meena 13° 41' 42"`..`Meena 20° 31' 09"`) |
| **`348° 00'`** | `Meena 18° 00' 00"` | *Revati* P1 (Mercury) | **Dhanu** | Vrishabha | Meena | `jupiter/mercury/mercury/rahu` | **Saturn Triple-Pass Zone** (`Meena 13° 41' 42"`..`Meena 20° 31' 09"`) |
| **`349° 00'`** | `Meena 19° 00' 00"` | *Revati* P1 (Mercury) | **Dhanu** | Vrishabha | Vrishabha | `jupiter/mercury/ketu/jupiter` | **Saturn Triple-Pass Zone** (`Meena 13° 41' 42"`..`Meena 20° 31' 09"`) |
| **`350° 00'`** | `Meena 20° 00' 00"` | *Revati* P1 (Mercury) | **Makara** | Vrishabha | Karka | `jupiter/mercury/venus/moon` | **Saturn Triple-Pass Zone** (`Meena 13° 41' 42"`..`Meena 20° 31' 09"`) |
| **`351° 00'`** | `Meena 21° 00' 00"` | *Revati* P2 (Mercury) | **Makara** | Mithuna | Kanya | `jupiter/mercury/venus/saturn` | Single Direct Transit Pass |
| **`352° 00'`** | `Meena 22° 00' 00"` | *Revati* P2 (Mercury) | **Makara** | Mithuna | Vrishchika | `jupiter/mercury/sun/mercury` | Single Direct Transit Pass |
| **`353° 00'`** | `Meena 23° 00' 00"` | *Revati* P2 (Mercury) | **Makara** | Mithuna | Makara | `jupiter/mercury/moon/mercury` | Single Direct Transit Pass |
| **`354° 00'`** | `Meena 24° 00' 00"` | *Revati* P3 (Mercury) | **Kumbha** | Karka | Meena | `jupiter/mercury/mars/venus` | Single Direct Transit Pass |
| **`355° 00'`** | `Meena 25° 00' 00"` | *Revati* P3 (Mercury) | **Kumbha** | Karka | Vrishabha | `jupiter/mercury/rahu/mercury` | Single Direct Transit Pass |
| **`356° 00'`** | `Meena 26° 00' 00"` | *Revati* P3 (Mercury) | **Kumbha** | Karka | Karka | `jupiter/mercury/rahu/mars` | Single Direct Transit Pass |
| **`357° 00'`** | `Meena 27° 00' 00"` | *Revati* P4 (Mercury) | **Meena** | Simha | Kanya | `jupiter/mercury/jupiter/venus` | Single Direct Transit Pass |
| **`358° 00'`** | `Meena 28° 00' 00"` | *Revati* P4 (Mercury) | **Meena** | Simha | Vrishchika | `jupiter/mercury/saturn/saturn` | Single Direct Transit Pass |
| **`359° 00'`** | `Meena 29° 00' 00"` | *Revati* P4 (Mercury) | **Meena** | Simha | Makara | `jupiter/mercury/saturn/sun` | Single Direct Transit Pass |

## Chapter 23 — Solar & Lunar Eclipse (*Surya & Chandra Grahan*) Local Obscuration, Nodal Limits, & Natal *Grahan* Sensitivity Compendium

### 23.1 Solar & Lunar Eclipses Around Epoch & Local Observer Obscuration

| Eclipse Category | Subtype | Maximum Eclipse (`UTC`) | Sidereal Longitude (`DMS`) | Sign (`Rashi`) | `Nakshatra & Pada` | Local Visible? | Local Obscuration Fraction |
|---|---|---|---|---|---|---|---|
| **Solar** | **Partial Solar** | `2026-02-17T12:01:09Z` | **`Kumbha 04° 36' 17"`** | Kumbha | *Dhanishta* P4 | `No` | **`0.0%`** |
| **Lunar** | **Total Lunar** | `2026-03-03T11:37:54Z` | **`Simha 18° 40' 25"`** | Simha | *Purva Phalguni* P2 | `No` | **`0.0%`** |
| **Solar** | **Partial Solar** | `2026-08-12T17:36:44Z` | **`Karka 25° 48' 05"`** | Karka | *Ashlesha* P3 | `No` | **`0.0%`** |
| **Lunar** | **Partial Lunar** | `2026-08-28T04:18:32Z` | **`Kumbha 10° 40' 12"`** | Kumbha | *Shatabhisha* P2 | `No` | **`0.0%`** |
| **Solar** | **Total/Annular Solar** | `2027-02-06T15:56:01Z` | **`Makara 23° 23' 17"`** | Makara | *Dhanishta* P1 | `No` | **`0.0%`** |
| **Lunar** | **Penumbral Lunar** | `2027-02-20T23:23:32Z` | **`Simha 07° 51' 12"`** | Simha | *Magha* P3 | `YES` | **`2.1%`** |

### 23.2 Worked Case Study: Natal *Grahan* Sensitivity Hits

| Natal Point | Natal Longitude | Eclipse Type & Date (`UTC`) | Eclipse Longitude (`DMS`) | Aspect Type | Orb (`deg`) | Impact Severity |
|---|---|---|---|---|---|---|
| **mars** | `Simha 01° 11' 03"` | **Partial Solar** (`2026-02-17T12:01:09Z`) | `Kumbha 04° 36' 17"` | **Opposition (180 deg Axis)** | `3.42°` | **`43.0 / 100`** |
| **jupiter** | `Simha 01° 33' 59"` | **Partial Solar** (`2026-02-17T12:01:09Z`) | `Kumbha 04° 36' 17"` | **Opposition (180 deg Axis)** | `3.04°` | **`49.4 / 100`** |
| **rahu** | `Kumbha 01° 05' 10"` | **Partial Solar** (`2026-02-17T12:01:09Z`) | `Kumbha 04° 36' 17"` | **Conjunction (0 deg)** | `3.52°` | **`41.4 / 100`** |
| **ketu** | `Simha 01° 05' 10"` | **Partial Solar** (`2026-02-17T12:01:09Z`) | `Kumbha 04° 36' 17"` | **Opposition (180 deg Axis)** | `3.52°` | **`41.4 / 100`** |
| **mars** | `Simha 01° 11' 03"` | **Partial Solar** (`2026-08-12T17:36:44Z`) | `Karka 25° 48' 05"` | **Conjunction (0 deg)** | `5.38°` | **`10.3 / 100`** |
| **jupiter** | `Simha 01° 33' 59"` | **Partial Solar** (`2026-08-12T17:36:44Z`) | `Karka 25° 48' 05"` | **Conjunction (0 deg)** | `5.76°` | **`3.9 / 100`** |
| **rahu** | `Kumbha 01° 05' 10"` | **Partial Solar** (`2026-08-12T17:36:44Z`) | `Karka 25° 48' 05"` | **Opposition (180 deg Axis)** | `5.28°` | **`11.9 / 100`** |
| **ketu** | `Simha 01° 05' 10"` | **Partial Solar** (`2026-08-12T17:36:44Z`) | `Karka 25° 48' 05"` | **Conjunction (0 deg)** | `5.28°` | **`11.9 / 100`** |

## Chapter 24 — Complete Manual Compendium of All 10 Conditional Parashari *Nakshatra Dashas* (BPHS Ch. 46) & Multi-Dasha Synchronicity

> **Unabridged BPHS Chapter 46 Conditional Nakshatra Dasha Suite:** Beyond universal *Vimshottari* (`120y`), Maharishi Parashara prescribes nine conditional *Nakshatra Dashas* (*Ashtottari 108y, Shodashottari 116y, Dwadashottari 112y, Panchottari 105y, Shatabdika 100y, Chaturashiti-Sama 84y, Dwisaptati-Sama 72y, Shat-Trimsha-Sama 36y, and Yogini 36y*). Below is the complete 27-Nakshatra Opening Lord & Duration Master Matrix.

### 24.1 Master 27-Nakshatra Opening Lord & Full Duration Lookup Table Across All 10 BPHS Nakshatra Dasha Systems

| `#` | Nakshatra (`0°..360°`) | Vimshottari (`120y`) | Ashtottari (`108y`) | Shodashottari (`116y`) | Dwadashottari (`112y`) | Panchottari (`105y`) | Shatabdika (`100y`) | Chaturashiti (`84y`) | Dwisaptati (`72y`) | Shat-Trimsha (`36y`) | Yogini (`36y`) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `#01` | **Ashwini** | `Ketu (7y)` | `Rahu (12y)` | `Ketu (15y)` | `Ketu (11y)` | `Venus (16y)` | `Sun (5y)` | `Saturn (12y)` | `Moon (9y)` | `Venus (7y)` | `Bhramari (Mars) (4y)` |
| `#02` | **Bharani** | `Venus (20y)` | `Rahu (12y)` | `Moon (16y)` | `Jupiter (9y)` | `Moon (17y)` | `Moon (10y)` | `Sun (12y)` | `Mars (9y)` | `Rahu (8y)` | `Bhadrika (Mercury) (5y)` |
| `#03` | **Krittika** | `Sun (6y)` | `Venus (21y)` | `Mercury (17y)` | `Sun (7y)` | `Jupiter (18y)` | `Mercury (10y)` | `Moon (12y)` | `Mercury (9y)` | `Moon (1y)` | `Ulka (Saturn) (6y)` |
| `#04` | **Rohini** | `Moon (10y)` | `Venus (21y)` | `Venus (18y)` | `Moon (21y)` | `Sun (12y)` | `Jupiter (20y)` | `Mars (12y)` | `Jupiter (9y)` | `Sun (2y)` | `Siddha (Venus) (7y)` |
| `#05` | **Mrigashirsha** | `Mars (7y)` | `Venus (21y)` | `Sun (11y)` | `Saturn (19y)` | `Mercury (13y)` | `Mars (20y)` | `Mercury (12y)` | `Venus (9y)` | `Jupiter (3y)` | `Sankata (Rahu) (8y)` |
| `#06` | **Ardra** | `Rahu (18y)` | `Sun (6y)` | `Mars (12y)` | `Mars (17y)` | `Saturn (14y)` | `Saturn (30y)` | `Jupiter (12y)` | `Saturn (9y)` | `Mars (4y)` | `Mangala (Moon) (1y)` |
| `#07` | **Punarvasu** | `Jupiter (16y)` | `Sun (6y)` | `Jupiter (13y)` | `Rahu (15y)` | `Mars (15y)` | `Venus (5y)` | `Venus (12y)` | `Rahu (9y)` | `Mercury (5y)` | `Pingala (Sun) (2y)` |
| `#08` | **Pushya** | `Saturn (19y)` | `Sun (6y)` | `Sun (11y)` | `Mercury (13y)` | `Venus (16y)` | `Sun (5y)` | `Saturn (12y)` | `Sun (9y)` | `Saturn (6y)` | `Dhanya (Jupiter) (3y)` |
| `#09` | **Ashlesha** | `Mercury (17y)` | `Sun (6y)` | `Mars (12y)` | `Ketu (11y)` | `Moon (17y)` | `Moon (10y)` | `Sun (12y)` | `Moon (9y)` | `Venus (7y)` | `Bhramari (Mars) (4y)` |
| `#10` | **Magha** | `Ketu (7y)` | `Moon (15y)` | `Jupiter (13y)` | `Jupiter (9y)` | `Jupiter (18y)` | `Mercury (10y)` | `Moon (12y)` | `Mars (9y)` | `Rahu (8y)` | `Bhadrika (Mercury) (5y)` |
| `#11` | **Purva Phalguni** | `Venus (20y)` | `Moon (15y)` | `Saturn (14y)` | `Sun (7y)` | `Sun (12y)` | `Jupiter (20y)` | `Mars (12y)` | `Mercury (9y)` | `Moon (1y)` | `Ulka (Saturn) (6y)` |
| `#12` | **Uttara Phalguni** | `Sun (6y)` | `Moon (15y)` | `Ketu (15y)` | `Moon (21y)` | `Mercury (13y)` | `Mars (20y)` | `Mercury (12y)` | `Jupiter (9y)` | `Sun (2y)` | `Siddha (Venus) (7y)` |
| `#13` | **Hasta** | `Moon (10y)` | `Mars (8y)` | `Moon (16y)` | `Saturn (19y)` | `Saturn (14y)` | `Saturn (30y)` | `Jupiter (12y)` | `Venus (9y)` | `Jupiter (3y)` | `Sankata (Rahu) (8y)` |
| `#14` | **Chitra** | `Mars (7y)` | `Mars (8y)` | `Mercury (17y)` | `Mars (17y)` | `Mars (15y)` | `Venus (5y)` | `Venus (12y)` | `Saturn (9y)` | `Mars (4y)` | `Mangala (Moon) (1y)` |
| `#15` | **Swati** | `Rahu (18y)` | `Mars (8y)` | `Venus (18y)` | `Rahu (15y)` | `Venus (16y)` | `Sun (5y)` | `Sun (12y)` | `Rahu (9y)` | `Mercury (5y)` | `Pingala (Sun) (2y)` |
| `#16` | **Vishakha** | `Jupiter (16y)` | `Mars (8y)` | `Sun (11y)` | `Mercury (13y)` | `Moon (17y)` | `Moon (10y)` | `Moon (12y)` | `Sun (9y)` | `Saturn (6y)` | `Dhanya (Jupiter) (3y)` |
| `#17` | **Anuradha** | `Saturn (19y)` | `Mercury (17y)` | `Mars (12y)` | `Ketu (11y)` | `Sun (12y)` | `Mercury (10y)` | `Mars (12y)` | `Moon (9y)` | `Venus (7y)` | `Bhramari (Mars) (4y)` |
| `#18` | **Jyeshtha** | `Mercury (17y)` | `Mercury (17y)` | `Jupiter (13y)` | `Jupiter (9y)` | `Mercury (13y)` | `Jupiter (20y)` | `Mercury (12y)` | `Mars (9y)` | `Rahu (8y)` | `Bhadrika (Mercury) (5y)` |
| `#19` | **Mula** | `Ketu (7y)` | `Mercury (17y)` | `Saturn (14y)` | `Sun (7y)` | `Saturn (14y)` | `Mars (20y)` | `Jupiter (12y)` | `Sun (9y)` | `Moon (1y)` | `Ulka (Saturn) (6y)` |
| `#20` | **Purva Ashadha** | `Venus (20y)` | `Saturn (10y)` | `Ketu (15y)` | `Moon (21y)` | `Mars (15y)` | `Saturn (30y)` | `Venus (12y)` | `Moon (9y)` | `Sun (2y)` | `Siddha (Venus) (7y)` |
| `#21` | **Uttara Ashadha** | `Sun (6y)` | `Saturn (10y)` | `Moon (16y)` | `Saturn (19y)` | `Venus (16y)` | `Venus (5y)` | `Saturn (12y)` | `Mars (9y)` | `Jupiter (3y)` | `Sankata (Rahu) (8y)` |
| `#22` | **Shravana** | `Moon (10y)` | `Saturn (10y)` | `Mercury (17y)` | `Mars (17y)` | `Moon (17y)` | `Sun (5y)` | `Sun (12y)` | `Mercury (9y)` | `Moon (1y)` | `Mangala (Moon) (1y)` |
| `#23` | **Dhanishta** | `Mars (7y)` | `Jupiter (19y)` | `Venus (18y)` | `Rahu (15y)` | `Jupiter (18y)` | `Moon (10y)` | `Moon (12y)` | `Jupiter (9y)` | `Sun (2y)` | `Pingala (Sun) (2y)` |
| `#24` | **Shatabhisha** | `Rahu (18y)` | `Jupiter (19y)` | `Sun (11y)` | `Mercury (13y)` | `Sun (12y)` | `Mercury (10y)` | `Mars (12y)` | `Venus (9y)` | `Jupiter (3y)` | `Dhanya (Jupiter) (3y)` |
| `#25` | **Purva Bhadrapada** | `Jupiter (16y)` | `Jupiter (19y)` | `Mars (12y)` | `Ketu (11y)` | `Mercury (13y)` | `Jupiter (20y)` | `Mercury (12y)` | `Saturn (9y)` | `Mars (4y)` | `Bhramari (Mars) (4y)` |
| `#26` | **Uttara Bhadrapada** | `Saturn (19y)` | `Rahu (12y)` | `Jupiter (13y)` | `Jupiter (9y)` | `Saturn (14y)` | `Mars (20y)` | `Jupiter (12y)` | `Rahu (9y)` | `Mercury (5y)` | `Bhadrika (Mercury) (5y)` |
| `#27` | **Revati** | `Mercury (17y)` | `Rahu (12y)` | `Saturn (14y)` | `Sun (7y)` | `Mars (15y)` | `Venus (5y)` | `Venus (12y)` | `Sun (9y)` | `Saturn (6y)` | `Ulka (Saturn) (6y)` |

### 24.2 Worked Case Study: All 10 BPHS Conditional Dasha Eligibility & Active Period Synchronicity

| Dasha System | Cycle (`Years`) | BPHS Conditional Eligibility | Eligibility Reason | Opening Lord & Balance (`Years`) | Active Mahadasha (`+24y`) | Active Antardasha (`+24y`) |
|---|---|---|---|---|---|---|
| **Vimshottari Dasha (120-Year Universal Mahadasha)** | `120y` | **`ELIGIBLE`** | Universal Kali Yuga primary Nakshatra Dasha (always applicable). | `Sun` (`2.84y`) | **`Rahu`** | **`Jupiter`** |
| **Ashtottari Dasha (108-Year Conditional Mahadasha)** | `108y` | **`ELIGIBLE`** | Eligible: Rahu is in House 7 from Lagna Lord (Jupiter) / Paksha-Day condition met. | `Saturn` (`2.97y`) | **`Rahu`** | **`Venus`** |
| **Shodashottari Dasha (116-Year Conditional Mahadasha)** | `116y` | **`Secondary`** | Secondary: Hora Lagna and Paksha polarity do not trigger primary Shodashottari condition. | `Moon` (`7.57y`) | **`Mercury`** | **`Moon`** |
| **Dwadashottari Dasha (112-Year Conditional Mahadasha)** | `112y` | **`ELIGIBLE`** | Eligible: Ascendant D9 Navamsa is Tula (ruled by Venus). | `Saturn` (`8.99y`) | **`Moon`** | **`Mars`** |
| **Panchottari Dasha (105-Year Conditional Mahadasha)** | `105y` | **`Secondary`** | Secondary: Ascendant is Dhanu (D12 Simha). | `Venus` (`7.57y`) | **`Moon`** | **`Venus`** |
| **Shatabdika Dasha (100-Year Vargottama Mahadasha)** | `100y` | **`Secondary`** | Secondary: Ascendant D1 (Dhanu) != D9 (Tula). | `Venus` (`2.36y`) | **`Mercury`** | **`Saturn`** |
| **Chaturashiti-Sama Dasha (84-Year 10th-Lord Mahadasha)** | `84y` | **`Secondary`** | Secondary: 10th Lord (Mercury) is in Tula. | `Saturn` (`5.68y`) | **`Moon`** | **`Jupiter`** |
| **Dwisaptati-Sama Dasha (72-Year Lagna/7th-Lord Mahadasha)** | `72y` | **`Secondary`** | Secondary: Lagna Lord (Jupiter) in Simha. | `Mars` (`4.26y`) | **`Venus`** | **`Saturn`** |
| **Shat-Trimsha-Sama Dasha (36-Year Hora-Aligned Mahadasha)** | `36y` | **`Secondary`** | Secondary: Day/Night birth does not match Sun/Moon Hora Lagna. | `Jupiter` (`1.42y`) | **`Rahu`** | **`Rahu`** |
| **Yogini Dasha (36-Year Tantric/Parashari Mahadasha)** | `36y` | **`ELIGIBLE`** | Universal companion 36-year Yogini Dasha cycle. | `Sankata (Rahu)` (`3.78y`) | **`Ulka (Saturn)`** | **`Bhadrika (Mercury)`** |

### 24.3 Worked Multi-Dasha Consensus Ranking

| Rank | Graha | Active Mahadasha Count | Active Antardasha Count | Eligible-System MD Count | Consensus Score (`0..100`) | Supporting Dasha Systems |
|---|---|---|---|---|---|---|
| `#1` | **Rahu** | `3` | `1` | `2` | **`70.0`** | `vimshottari:MD, ashtottari:MD, shat_trimsha_sama:MD, shat_trimsha_sama:AD` |
| `#2` | **Moon** | `3` | `1` | `1` | **`60.0`** | `dwadashottari:MD, panchottari:MD, chaturashiti_sama:MD, shodashottari:AD` |
| `#3` | **Saturn** | `1` | `2` | `1` | **`40.0`** | `yogini:MD, shatabdika:AD, dwisaptati_sama:AD` |
| `#4` | **Mercury** | `2` | `1` | `0` | **`36.0`** | `shodashottari:MD, shatabdika:MD, yogini:AD` |
| `#5` | **Venus** | `1` | `2` | `0` | **`30.0`** | `dwisaptati_sama:MD, ashtottari:AD, panchottari:AD` |
| `#6` | **Jupiter** | `0` | `2` | `0` | **`16.0`** | `vimshottari:AD, chaturashiti_sama:AD` |
| `#7` | **Mars** | `0` | `1` | `0` | **`8.0`** | `dwadashottari:AD` |

## Chapter 25 — 5-Level *Vimshottari Prana-Dasha* Sub-Hour Chronometer (*Mahadasha -> Antardasha -> Pratyantardasha -> Sookshma -> Prana*)

### 25.1 Complete 81-Row *Mahadasha × Antardasha* Proportional Sub-Period Ready Reckoner (Exact Days, Hours, & Self-Sub *Pratyantardasha / Sookshma / Prana* Durations)

| Mahadasha (`MD`) | Antardasha (`AD`) | `MD × AD` Duration (`Years`) | Exact Solar Days (`365.2425d/y`) | Self-`PD` Duration (`Days`) | Self-`Sookshma` Duration (`Hours`) | Self-`Prana` Duration (`Minutes`) |
|---|---|---|---|---|---|---|
| **Ketu** (`7y`) | **Ketu** (`7y`) | `0.4083y` | **`149.14 d`** | `8.70 d` | `12.18 h` | **`42.63 min`** |
| **Ketu** (`7y`) | **Venus** (`20y`) | `1.1667y` | **`426.12 d`** | `71.02 d` | `284.08 h` | **`2840.77 min`** |
| **Ketu** (`7y`) | **Sun** (`6y`) | `0.3500y` | **`127.83 d`** | `6.39 d` | `7.67 h` | **`23.01 min`** |
| **Ketu** (`7y`) | **Moon** (`10y`) | `0.5833y` | **`213.06 d`** | `17.75 d` | `35.51 h` | **`177.55 min`** |
| **Ketu** (`7y`) | **Mars** (`7y`) | `0.4083y` | **`149.14 d`** | `8.70 d` | `12.18 h` | **`42.63 min`** |
| **Ketu** (`7y`) | **Rahu** (`18y`) | `1.0500y` | **`383.50 d`** | `57.53 d` | `207.09 h` | **`1863.83 min`** |
| **Ketu** (`7y`) | **Jupiter** (`16y`) | `0.9333y` | **`340.89 d`** | `45.45 d` | `145.45 h` | **`1163.58 min`** |
| **Ketu** (`7y`) | **Saturn** (`19y`) | `1.1083y` | **`404.81 d`** | `64.09 d` | `243.56 h` | **`2313.83 min`** |
| **Ketu** (`7y`) | **Mercury** (`17y`) | `0.9917y` | **`362.20 d`** | `51.31 d` | `174.46 h` | **`1482.90 min`** |
| **Venus** (`20y`) | **Ketu** (`7y`) | `1.1667y` | **`426.12 d`** | `24.86 d` | `34.80 h` | **`121.80 min`** |
| **Venus** (`20y`) | **Venus** (`20y`) | `3.3333y` | **`1217.47 d`** | `202.91 d` | `811.65 h` | **`8116.50 min`** |
| **Venus** (`20y`) | **Sun** (`6y`) | `1.0000y` | **`365.24 d`** | `18.26 d` | `21.91 h` | **`65.74 min`** |
| **Venus** (`20y`) | **Moon** (`10y`) | `1.6667y` | **`608.74 d`** | `50.73 d` | `101.46 h` | **`507.28 min`** |
| **Venus** (`20y`) | **Mars** (`7y`) | `1.1667y` | **`426.12 d`** | `24.86 d` | `34.80 h` | **`121.80 min`** |
| **Venus** (`20y`) | **Rahu** (`18y`) | `3.0000y` | **`1095.73 d`** | `164.36 d` | `591.69 h` | **`5325.24 min`** |
| **Venus** (`20y`) | **Jupiter** (`16y`) | `2.6667y` | **`973.98 d`** | `129.86 d` | `415.56 h` | **`3324.52 min`** |
| **Venus** (`20y`) | **Saturn** (`19y`) | `3.1667y` | **`1156.60 d`** | `183.13 d` | `695.89 h` | **`6610.94 min`** |
| **Venus** (`20y`) | **Mercury** (`17y`) | `2.8333y` | **`1034.85 d`** | `146.60 d` | `498.45 h` | **`4236.86 min`** |
| **Sun** (`6y`) | **Ketu** (`7y`) | `0.3500y` | **`127.83 d`** | `7.46 d` | `10.44 h` | **`36.54 min`** |
| **Sun** (`6y`) | **Venus** (`20y`) | `1.0000y` | **`365.24 d`** | `60.87 d` | `243.49 h` | **`2434.95 min`** |
| **Sun** (`6y`) | **Sun** (`6y`) | `0.3000y` | **`109.57 d`** | `5.48 d` | `6.57 h` | **`19.72 min`** |
| **Sun** (`6y`) | **Moon** (`10y`) | `0.5000y` | **`182.62 d`** | `15.22 d` | `30.44 h` | **`152.18 min`** |
| **Sun** (`6y`) | **Mars** (`7y`) | `0.3500y` | **`127.83 d`** | `7.46 d` | `10.44 h` | **`36.54 min`** |
| **Sun** (`6y`) | **Rahu** (`18y`) | `0.9000y` | **`328.72 d`** | `49.31 d` | `177.51 h` | **`1597.57 min`** |
| **Sun** (`6y`) | **Jupiter** (`16y`) | `0.8000y` | **`292.19 d`** | `38.96 d` | `124.67 h` | **`997.36 min`** |
| **Sun** (`6y`) | **Saturn** (`19y`) | `0.9500y` | **`346.98 d`** | `54.94 d` | `208.77 h` | **`1983.28 min`** |
| **Sun** (`6y`) | **Mercury** (`17y`) | `0.8500y` | **`310.46 d`** | `43.98 d` | `149.54 h` | **`1271.06 min`** |
| **Moon** (`10y`) | **Ketu** (`7y`) | `0.5833y` | **`213.06 d`** | `12.43 d` | `17.40 h` | **`60.90 min`** |
| **Moon** (`10y`) | **Venus** (`20y`) | `1.6667y` | **`608.74 d`** | `101.46 d` | `405.82 h` | **`4058.25 min`** |
| **Moon** (`10y`) | **Sun** (`6y`) | `0.5000y` | **`182.62 d`** | `9.13 d` | `10.96 h` | **`32.87 min`** |
| **Moon** (`10y`) | **Moon** (`10y`) | `0.8333y` | **`304.37 d`** | `25.36 d` | `50.73 h` | **`253.64 min`** |
| **Moon** (`10y`) | **Mars** (`7y`) | `0.5833y` | **`213.06 d`** | `12.43 d` | `17.40 h` | **`60.90 min`** |
| **Moon** (`10y`) | **Rahu** (`18y`) | `1.5000y` | **`547.86 d`** | `82.18 d` | `295.85 h` | **`2662.62 min`** |
| **Moon** (`10y`) | **Jupiter** (`16y`) | `1.3333y` | **`486.99 d`** | `64.93 d` | `207.78 h` | **`1662.26 min`** |
| **Moon** (`10y`) | **Saturn** (`19y`) | `1.5833y` | **`578.30 d`** | `91.56 d` | `347.94 h` | **`3305.47 min`** |
| **Moon** (`10y`) | **Mercury** (`17y`) | `1.4167y` | **`517.43 d`** | `73.30 d` | `249.23 h` | **`2118.43 min`** |
| **Mars** (`7y`) | **Ketu** (`7y`) | `0.4083y` | **`149.14 d`** | `8.70 d` | `12.18 h` | **`42.63 min`** |
| **Mars** (`7y`) | **Venus** (`20y`) | `1.1667y` | **`426.12 d`** | `71.02 d` | `284.08 h` | **`2840.77 min`** |
| **Mars** (`7y`) | **Sun** (`6y`) | `0.3500y` | **`127.83 d`** | `6.39 d` | `7.67 h` | **`23.01 min`** |
| **Mars** (`7y`) | **Moon** (`10y`) | `0.5833y` | **`213.06 d`** | `17.75 d` | `35.51 h` | **`177.55 min`** |
| **Mars** (`7y`) | **Mars** (`7y`) | `0.4083y` | **`149.14 d`** | `8.70 d` | `12.18 h` | **`42.63 min`** |
| **Mars** (`7y`) | **Rahu** (`18y`) | `1.0500y` | **`383.50 d`** | `57.53 d` | `207.09 h` | **`1863.83 min`** |
| **Mars** (`7y`) | **Jupiter** (`16y`) | `0.9333y` | **`340.89 d`** | `45.45 d` | `145.45 h` | **`1163.58 min`** |
| **Mars** (`7y`) | **Saturn** (`19y`) | `1.1083y` | **`404.81 d`** | `64.09 d` | `243.56 h` | **`2313.83 min`** |
| **Mars** (`7y`) | **Mercury** (`17y`) | `0.9917y` | **`362.20 d`** | `51.31 d` | `174.46 h` | **`1482.90 min`** |
| **Rahu** (`18y`) | **Ketu** (`7y`) | `1.0500y` | **`383.50 d`** | `22.37 d` | `31.32 h` | **`109.62 min`** |
| **Rahu** (`18y`) | **Venus** (`20y`) | `3.0000y` | **`1095.73 d`** | `182.62 d` | `730.48 h` | **`7304.85 min`** |
| **Rahu** (`18y`) | **Sun** (`6y`) | `0.9000y` | **`328.72 d`** | `16.44 d` | `19.72 h` | **`59.17 min`** |
| **Rahu** (`18y`) | **Moon** (`10y`) | `1.5000y` | **`547.86 d`** | `45.66 d` | `91.31 h` | **`456.55 min`** |
| **Rahu** (`18y`) | **Mars** (`7y`) | `1.0500y` | **`383.50 d`** | `22.37 d` | `31.32 h` | **`109.62 min`** |
| **Rahu** (`18y`) | **Rahu** (`18y`) | `2.7000y` | **`986.15 d`** | `147.92 d` | `532.52 h` | **`4792.71 min`** |
| **Rahu** (`18y`) | **Jupiter** (`16y`) | `2.4000y` | **`876.58 d`** | `116.88 d` | `374.01 h` | **`2992.07 min`** |
| **Rahu** (`18y`) | **Saturn** (`19y`) | `2.8500y` | **`1040.94 d`** | `164.82 d` | `626.30 h` | **`5949.85 min`** |
| **Rahu** (`18y`) | **Mercury** (`17y`) | `2.5500y` | **`931.37 d`** | `131.94 d` | `448.61 h` | **`3813.18 min`** |
| **Jupiter** (`16y`) | **Ketu** (`7y`) | `0.9333y` | **`340.89 d`** | `19.89 d` | `27.84 h` | **`97.44 min`** |
| **Jupiter** (`16y`) | **Venus** (`20y`) | `2.6667y` | **`973.98 d`** | `162.33 d` | `649.32 h` | **`6493.20 min`** |
| **Jupiter** (`16y`) | **Sun** (`6y`) | `0.8000y` | **`292.19 d`** | `14.61 d` | `17.53 h` | **`52.59 min`** |
| **Jupiter** (`16y`) | **Moon** (`10y`) | `1.3333y` | **`486.99 d`** | `40.58 d` | `81.16 h` | **`405.82 min`** |
| **Jupiter** (`16y`) | **Mars** (`7y`) | `0.9333y` | **`340.89 d`** | `19.89 d` | `27.84 h` | **`97.44 min`** |
| **Jupiter** (`16y`) | **Rahu** (`18y`) | `2.4000y` | **`876.58 d`** | `131.49 d` | `473.35 h` | **`4260.19 min`** |
| **Jupiter** (`16y`) | **Jupiter** (`16y`) | `2.1333y` | **`779.18 d`** | `103.89 d` | `332.45 h` | **`2659.61 min`** |
| **Jupiter** (`16y`) | **Saturn** (`19y`) | `2.5333y` | **`925.28 d`** | `146.50 d` | `556.71 h` | **`5288.75 min`** |
| **Jupiter** (`16y`) | **Mercury** (`17y`) | `2.2667y` | **`827.88 d`** | `117.28 d` | `398.76 h` | **`3389.49 min`** |
| **Saturn** (`19y`) | **Ketu** (`7y`) | `1.1083y` | **`404.81 d`** | `23.61 d` | `33.06 h` | **`115.71 min`** |
| **Saturn** (`19y`) | **Venus** (`20y`) | `3.1667y` | **`1156.60 d`** | `192.77 d` | `771.07 h` | **`7710.67 min`** |
| **Saturn** (`19y`) | **Sun** (`6y`) | `0.9500y` | **`346.98 d`** | `17.35 d` | `20.82 h` | **`62.46 min`** |
| **Saturn** (`19y`) | **Moon** (`10y`) | `1.5833y` | **`578.30 d`** | `48.19 d` | `96.38 h` | **`481.92 min`** |
| **Saturn** (`19y`) | **Mars** (`7y`) | `1.1083y` | **`404.81 d`** | `23.61 d` | `33.06 h` | **`115.71 min`** |
| **Saturn** (`19y`) | **Rahu** (`18y`) | `2.8500y` | **`1040.94 d`** | `156.14 d` | `562.11 h` | **`5058.97 min`** |
| **Saturn** (`19y`) | **Jupiter** (`16y`) | `2.5333y` | **`925.28 d`** | `123.37 d` | `394.79 h` | **`3158.29 min`** |
| **Saturn** (`19y`) | **Saturn** (`19y`) | `3.0083y` | **`1098.77 d`** | `173.97 d` | `661.09 h` | **`6280.39 min`** |
| **Saturn** (`19y`) | **Mercury** (`17y`) | `2.6917y` | **`983.11 d`** | `139.27 d` | `473.53 h` | **`4025.02 min`** |
| **Mercury** (`17y`) | **Ketu** (`7y`) | `0.9917y` | **`362.20 d`** | `21.13 d` | `29.58 h` | **`103.53 min`** |
| **Mercury** (`17y`) | **Venus** (`20y`) | `2.8333y` | **`1034.85 d`** | `172.48 d` | `689.90 h` | **`6899.02 min`** |
| **Mercury** (`17y`) | **Sun** (`6y`) | `0.8500y` | **`310.46 d`** | `15.52 d` | `18.63 h` | **`55.88 min`** |
| **Mercury** (`17y`) | **Moon** (`10y`) | `1.4167y` | **`517.43 d`** | `43.12 d` | `86.24 h` | **`431.19 min`** |
| **Mercury** (`17y`) | **Mars** (`7y`) | `0.9917y` | **`362.20 d`** | `21.13 d` | `29.58 h` | **`103.53 min`** |
| **Mercury** (`17y`) | **Rahu** (`18y`) | `2.5500y` | **`931.37 d`** | `139.71 d` | `502.94 h` | **`4526.45 min`** |
| **Mercury** (`17y`) | **Jupiter** (`16y`) | `2.2667y` | **`827.88 d`** | `110.38 d` | `353.23 h` | **`2825.84 min`** |
| **Mercury** (`17y`) | **Saturn** (`19y`) | `2.6917y` | **`983.11 d`** | `155.66 d` | `591.51 h` | **`5619.30 min`** |
| **Mercury** (`17y`) | **Mercury** (`17y`) | `2.4083y` | **`879.63 d`** | `124.61 d` | `423.69 h` | **`3601.33 min`** |

### 25.2 Worked Case Study: 5-Level *Prana-Dasha* Sub-Hour Chronometer at `2050-11-15T00:52:47Z`

- **Level 1 (*Mahadasha*):** **Rahu** (`2046-09-16T17:43:33Z` to `2064-09-16T02:29:09Z`)
- **Level 2 (*Antardasha*):** **Jupiter** (`2049-05-29T21:26:24Z` to `2051-10-23T11:24:29Z`)
- **Level 3 (*Pratyantardasha*):** **Venus** (`2050-08-03T21:06:27Z` to `2050-12-27T23:26:08Z`)
- **Level 4 (*Sookshma Dasha*):** **Saturn** (`2050-11-05T15:00:05Z` to `2050-11-28T18:10:12Z`, Duration = `555.17 hours`)
- **Level 5 (*Active Prana Dasha*):** **`Venus`**

| Prana Order | Level-5 *Prana Dasha* Lord | Start (`UTC`) | End (`UTC`) | Duration (`Minutes`) | Active at Query? |
|---|---|---|---|---|---|
| `#1` | **Saturn** | `2050-11-05T15:00:05Z` | `2050-11-09T06:54:11Z` | **`5274.10 min`** | `—` |
| `#2` | **Mercury** | `2050-11-09T06:54:11Z` | `2050-11-12T13:33:07Z` | **`4718.93 min`** | `—` |
| `#3` | **Ketu** | `2050-11-12T13:33:07Z` | `2050-11-13T21:56:12Z` | **`1943.09 min`** | `—` |
| `#4` | **Venus** | `2050-11-13T21:56:12Z` | `2050-11-17T18:27:54Z` | **`5551.69 min`** | `ACTIVE` |
| `#5` | **Sun** | `2050-11-17T18:27:54Z` | `2050-11-18T22:13:24Z` | **`1665.51 min`** | `—` |
| `#6` | **Moon** | `2050-11-18T22:13:24Z` | `2050-11-20T20:29:15Z` | **`2775.84 min`** | `—` |
| `#7` | **Mars** | `2050-11-20T20:29:15Z` | `2050-11-22T04:52:20Z` | **`1943.09 min`** | `—` |
| `#8` | **Rahu** | `2050-11-22T04:52:20Z` | `2050-11-25T16:08:51Z` | **`4996.52 min`** | `—` |
| `#9` | **Jupiter** | `2050-11-25T16:08:51Z` | `2050-11-28T18:10:12Z` | **`4441.35 min`** | `—` |

## Chapter 26 — Complete 150-Division *Nadi Amsa* (`0°12'` *Chandra Kala Nadi / Deva Keralam*) Master Reckoning Table (`#001` to `#150`) & Birth-Time Rectification

> **150 *Nadi Amsas* per Rashi (`1,800` Across `360°`):** Each `30°` sign is divided into `150` micro-slices of **`0° 12' 00"`** (`720"`). In *Chara* (Movable: Mesha, Karka, Tula, Makara) signs, numbering runs directly `1..150`; in *Sthira* (Fixed: Vrishabha, Simha, Vrishchika, Kumbha) signs, numbering reverses `150..1`; in *Dwiswabhava* (Dual: Mithuna, Kanya, Dhanu, Meena) signs, numbering begins at the midpoint `76..150` followed by `1..75`.

### 26.1 Unabridged 150-*Nadi Amsa* (`0°00'` to `30°00'`) Master Lookup Table

| Slice `#` | Degree Span in Sign (`0°..30°`) | *Chara* (Movable) Nadi `#` & Name | *Sthira* (Fixed) Nadi `#` & Name | *Dwiswabhava* (Dual) Nadi `#` & Name | Nadi Planetary Ruler | Lagna Rectification Window (`Seconds`) |
|---|---|---|---|---|---|---|
| **`#001`** | `00° 00' .. 00° 12'` | `#001` **Vasudha** *(Prathama-Kala)* | `#150` **Kumbhini** *(Dashama-Kala)* | `#076` **Vasudha** *(Shashtha-Kala)* | **Ketu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#002`** | `00° 12' .. 00° 24'` | `#002` **Vaishnavi** *(Prathama-Kala)* | `#149` **Ghora** *(Dashama-Kala)* | `#077` **Vaishnavi** *(Shashtha-Kala)* | **Venus** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#003`** | `00° 24' .. 00° 36'` | `#003` **Brahmi** *(Prathama-Kala)* | `#148` **Manjuswana** *(Dashama-Kala)* | `#078` **Brahmi** *(Shashtha-Kala)* | **Sun** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#004`** | `00° 36' .. 00° 48'` | `#004` **Kalakoota** *(Prathama-Kala)* | `#147` **Madhavi** *(Dashama-Kala)* | `#079` **Kalakoota** *(Shashtha-Kala)* | **Moon** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#005`** | `00° 48' .. 01° 00'` | `#005` **Shankari** *(Prathama-Kala)* | `#146` **Manohara** *(Dashama-Kala)* | `#080` **Shankari** *(Shashtha-Kala)* | **Mars** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#006`** | `01° 00' .. 01° 12'` | `#006` **Sudhakara** *(Prathama-Kala)* | `#145` **Maya** *(Dashama-Kala)* | `#081` **Sudhakara** *(Shashtha-Kala)* | **Rahu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#007`** | `01° 12' .. 01° 24'` | `#007` **Sama** *(Prathama-Kala)* | `#144` **Sura** *(Dashama-Kala)* | `#082` **Sama** *(Shashtha-Kala)* | **Jupiter** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#008`** | `01° 24' .. 01° 36'` | `#008` **Saumya** *(Prathama-Kala)* | `#143` **Saumya** *(Dashama-Kala)* | `#083` **Saumya** *(Shashtha-Kala)* | **Saturn** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#009`** | `01° 36' .. 01° 48'` | `#009` **Sura** *(Prathama-Kala)* | `#142` **Sama** *(Dashama-Kala)* | `#084` **Sura** *(Shashtha-Kala)* | **Mercury** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#010`** | `01° 48' .. 02° 00'` | `#010` **Maya** *(Prathama-Kala)* | `#141` **Sudhakara** *(Dashama-Kala)* | `#085` **Maya** *(Shashtha-Kala)* | **Ketu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#011`** | `02° 00' .. 02° 12'` | `#011` **Manohara** *(Prathama-Kala)* | `#140` **Shankari** *(Dashama-Kala)* | `#086` **Manohara** *(Shashtha-Kala)* | **Venus** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#012`** | `02° 12' .. 02° 24'` | `#012` **Madhavi** *(Prathama-Kala)* | `#139` **Kalakoota** *(Dashama-Kala)* | `#087` **Madhavi** *(Shashtha-Kala)* | **Sun** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#013`** | `02° 24' .. 02° 36'` | `#013` **Manjuswana** *(Prathama-Kala)* | `#138` **Brahmi** *(Dashama-Kala)* | `#088` **Manjuswana** *(Shashtha-Kala)* | **Moon** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#014`** | `02° 36' .. 02° 48'` | `#014` **Ghora** *(Prathama-Kala)* | `#137` **Vaishnavi** *(Dashama-Kala)* | `#089` **Ghora** *(Shashtha-Kala)* | **Mars** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#015`** | `02° 48' .. 03° 00'` | `#015` **Kumbhini** *(Prathama-Kala)* | `#136` **Vasudha** *(Dashama-Kala)* | `#090` **Kumbhini** *(Shashtha-Kala)* | **Rahu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#016`** | `03° 00' .. 03° 12'` | `#016` **Vasudha** *(Dvitiya-Kala)* | `#135` **Kumbhini** *(Navama-Kala)* | `#091` **Vasudha** *(Saptama-Kala)* | **Jupiter** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#017`** | `03° 12' .. 03° 24'` | `#017` **Vaishnavi** *(Dvitiya-Kala)* | `#134` **Ghora** *(Navama-Kala)* | `#092` **Vaishnavi** *(Saptama-Kala)* | **Saturn** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#018`** | `03° 24' .. 03° 36'` | `#018` **Brahmi** *(Dvitiya-Kala)* | `#133` **Manjuswana** *(Navama-Kala)* | `#093` **Brahmi** *(Saptama-Kala)* | **Mercury** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#019`** | `03° 36' .. 03° 48'` | `#019` **Kalakoota** *(Dvitiya-Kala)* | `#132` **Madhavi** *(Navama-Kala)* | `#094` **Kalakoota** *(Saptama-Kala)* | **Ketu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#020`** | `03° 48' .. 04° 00'` | `#020` **Shankari** *(Dvitiya-Kala)* | `#131` **Manohara** *(Navama-Kala)* | `#095` **Shankari** *(Saptama-Kala)* | **Venus** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#021`** | `04° 00' .. 04° 12'` | `#021` **Sudhakara** *(Dvitiya-Kala)* | `#130` **Maya** *(Navama-Kala)* | `#096` **Sudhakara** *(Saptama-Kala)* | **Sun** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#022`** | `04° 12' .. 04° 24'` | `#022` **Sama** *(Dvitiya-Kala)* | `#129` **Sura** *(Navama-Kala)* | `#097` **Sama** *(Saptama-Kala)* | **Moon** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#023`** | `04° 24' .. 04° 36'` | `#023` **Saumya** *(Dvitiya-Kala)* | `#128` **Saumya** *(Navama-Kala)* | `#098` **Saumya** *(Saptama-Kala)* | **Mars** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#024`** | `04° 36' .. 04° 48'` | `#024` **Sura** *(Dvitiya-Kala)* | `#127` **Sama** *(Navama-Kala)* | `#099` **Sura** *(Saptama-Kala)* | **Rahu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#025`** | `04° 48' .. 05° 00'` | `#025` **Maya** *(Dvitiya-Kala)* | `#126` **Sudhakara** *(Navama-Kala)* | `#100` **Maya** *(Saptama-Kala)* | **Jupiter** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#026`** | `05° 00' .. 05° 12'` | `#026` **Manohara** *(Dvitiya-Kala)* | `#125` **Shankari** *(Navama-Kala)* | `#101` **Manohara** *(Saptama-Kala)* | **Saturn** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#027`** | `05° 12' .. 05° 24'` | `#027` **Madhavi** *(Dvitiya-Kala)* | `#124` **Kalakoota** *(Navama-Kala)* | `#102` **Madhavi** *(Saptama-Kala)* | **Mercury** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#028`** | `05° 24' .. 05° 36'` | `#028` **Manjuswana** *(Dvitiya-Kala)* | `#123` **Brahmi** *(Navama-Kala)* | `#103` **Manjuswana** *(Saptama-Kala)* | **Ketu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#029`** | `05° 36' .. 05° 48'` | `#029` **Ghora** *(Dvitiya-Kala)* | `#122` **Vaishnavi** *(Navama-Kala)* | `#104` **Ghora** *(Saptama-Kala)* | **Venus** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#030`** | `05° 48' .. 06° 00'` | `#030` **Kumbhini** *(Dvitiya-Kala)* | `#121` **Vasudha** *(Navama-Kala)* | `#105` **Kumbhini** *(Saptama-Kala)* | **Sun** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#031`** | `06° 00' .. 06° 12'` | `#031` **Vasudha** *(Tritiya-Kala)* | `#120` **Kumbhini** *(Ashtama-Kala)* | `#106` **Vasudha** *(Ashtama-Kala)* | **Moon** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#032`** | `06° 12' .. 06° 24'` | `#032` **Vaishnavi** *(Tritiya-Kala)* | `#119` **Ghora** *(Ashtama-Kala)* | `#107` **Vaishnavi** *(Ashtama-Kala)* | **Mars** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#033`** | `06° 24' .. 06° 36'` | `#033` **Brahmi** *(Tritiya-Kala)* | `#118` **Manjuswana** *(Ashtama-Kala)* | `#108` **Brahmi** *(Ashtama-Kala)* | **Rahu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#034`** | `06° 36' .. 06° 48'` | `#034` **Kalakoota** *(Tritiya-Kala)* | `#117` **Madhavi** *(Ashtama-Kala)* | `#109` **Kalakoota** *(Ashtama-Kala)* | **Jupiter** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#035`** | `06° 48' .. 07° 00'` | `#035` **Shankari** *(Tritiya-Kala)* | `#116` **Manohara** *(Ashtama-Kala)* | `#110` **Shankari** *(Ashtama-Kala)* | **Saturn** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#036`** | `07° 00' .. 07° 12'` | `#036` **Sudhakara** *(Tritiya-Kala)* | `#115` **Maya** *(Ashtama-Kala)* | `#111` **Sudhakara** *(Ashtama-Kala)* | **Mercury** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#037`** | `07° 12' .. 07° 24'` | `#037` **Sama** *(Tritiya-Kala)* | `#114` **Sura** *(Ashtama-Kala)* | `#112` **Sama** *(Ashtama-Kala)* | **Ketu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#038`** | `07° 24' .. 07° 36'` | `#038` **Saumya** *(Tritiya-Kala)* | `#113` **Saumya** *(Ashtama-Kala)* | `#113` **Saumya** *(Ashtama-Kala)* | **Venus** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#039`** | `07° 36' .. 07° 48'` | `#039` **Sura** *(Tritiya-Kala)* | `#112` **Sama** *(Ashtama-Kala)* | `#114` **Sura** *(Ashtama-Kala)* | **Sun** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#040`** | `07° 48' .. 08° 00'` | `#040` **Maya** *(Tritiya-Kala)* | `#111` **Sudhakara** *(Ashtama-Kala)* | `#115` **Maya** *(Ashtama-Kala)* | **Moon** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#041`** | `08° 00' .. 08° 12'` | `#041` **Manohara** *(Tritiya-Kala)* | `#110` **Shankari** *(Ashtama-Kala)* | `#116` **Manohara** *(Ashtama-Kala)* | **Mars** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#042`** | `08° 12' .. 08° 24'` | `#042` **Madhavi** *(Tritiya-Kala)* | `#109` **Kalakoota** *(Ashtama-Kala)* | `#117` **Madhavi** *(Ashtama-Kala)* | **Rahu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#043`** | `08° 24' .. 08° 36'` | `#043` **Manjuswana** *(Tritiya-Kala)* | `#108` **Brahmi** *(Ashtama-Kala)* | `#118` **Manjuswana** *(Ashtama-Kala)* | **Jupiter** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#044`** | `08° 36' .. 08° 48'` | `#044` **Ghora** *(Tritiya-Kala)* | `#107` **Vaishnavi** *(Ashtama-Kala)* | `#119` **Ghora** *(Ashtama-Kala)* | **Saturn** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#045`** | `08° 48' .. 09° 00'` | `#045` **Kumbhini** *(Tritiya-Kala)* | `#106` **Vasudha** *(Ashtama-Kala)* | `#120` **Kumbhini** *(Ashtama-Kala)* | **Mercury** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#046`** | `09° 00' .. 09° 12'` | `#046` **Vasudha** *(Chaturtha-Kala)* | `#105` **Kumbhini** *(Saptama-Kala)* | `#121` **Vasudha** *(Navama-Kala)* | **Ketu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#047`** | `09° 12' .. 09° 24'` | `#047` **Vaishnavi** *(Chaturtha-Kala)* | `#104` **Ghora** *(Saptama-Kala)* | `#122` **Vaishnavi** *(Navama-Kala)* | **Venus** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#048`** | `09° 24' .. 09° 36'` | `#048` **Brahmi** *(Chaturtha-Kala)* | `#103` **Manjuswana** *(Saptama-Kala)* | `#123` **Brahmi** *(Navama-Kala)* | **Sun** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#049`** | `09° 36' .. 09° 48'` | `#049` **Kalakoota** *(Chaturtha-Kala)* | `#102` **Madhavi** *(Saptama-Kala)* | `#124` **Kalakoota** *(Navama-Kala)* | **Moon** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#050`** | `09° 48' .. 10° 00'` | `#050` **Shankari** *(Chaturtha-Kala)* | `#101` **Manohara** *(Saptama-Kala)* | `#125` **Shankari** *(Navama-Kala)* | **Mars** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#051`** | `10° 00' .. 10° 12'` | `#051` **Sudhakara** *(Chaturtha-Kala)* | `#100` **Maya** *(Saptama-Kala)* | `#126` **Sudhakara** *(Navama-Kala)* | **Rahu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#052`** | `10° 12' .. 10° 24'` | `#052` **Sama** *(Chaturtha-Kala)* | `#099` **Sura** *(Saptama-Kala)* | `#127` **Sama** *(Navama-Kala)* | **Jupiter** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#053`** | `10° 24' .. 10° 36'` | `#053` **Saumya** *(Chaturtha-Kala)* | `#098` **Saumya** *(Saptama-Kala)* | `#128` **Saumya** *(Navama-Kala)* | **Saturn** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#054`** | `10° 36' .. 10° 48'` | `#054` **Sura** *(Chaturtha-Kala)* | `#097` **Sama** *(Saptama-Kala)* | `#129` **Sura** *(Navama-Kala)* | **Mercury** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#055`** | `10° 48' .. 11° 00'` | `#055` **Maya** *(Chaturtha-Kala)* | `#096` **Sudhakara** *(Saptama-Kala)* | `#130` **Maya** *(Navama-Kala)* | **Ketu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#056`** | `11° 00' .. 11° 12'` | `#056` **Manohara** *(Chaturtha-Kala)* | `#095` **Shankari** *(Saptama-Kala)* | `#131` **Manohara** *(Navama-Kala)* | **Venus** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#057`** | `11° 12' .. 11° 24'` | `#057` **Madhavi** *(Chaturtha-Kala)* | `#094` **Kalakoota** *(Saptama-Kala)* | `#132` **Madhavi** *(Navama-Kala)* | **Sun** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#058`** | `11° 24' .. 11° 36'` | `#058` **Manjuswana** *(Chaturtha-Kala)* | `#093` **Brahmi** *(Saptama-Kala)* | `#133` **Manjuswana** *(Navama-Kala)* | **Moon** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#059`** | `11° 36' .. 11° 48'` | `#059` **Ghora** *(Chaturtha-Kala)* | `#092` **Vaishnavi** *(Saptama-Kala)* | `#134` **Ghora** *(Navama-Kala)* | **Mars** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#060`** | `11° 48' .. 12° 00'` | `#060` **Kumbhini** *(Chaturtha-Kala)* | `#091` **Vasudha** *(Saptama-Kala)* | `#135` **Kumbhini** *(Navama-Kala)* | **Rahu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#061`** | `12° 00' .. 12° 12'` | `#061` **Vasudha** *(Panchama-Kala)* | `#090` **Kumbhini** *(Shashtha-Kala)* | `#136` **Vasudha** *(Dashama-Kala)* | **Jupiter** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#062`** | `12° 12' .. 12° 24'` | `#062` **Vaishnavi** *(Panchama-Kala)* | `#089` **Ghora** *(Shashtha-Kala)* | `#137` **Vaishnavi** *(Dashama-Kala)* | **Saturn** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#063`** | `12° 24' .. 12° 36'` | `#063` **Brahmi** *(Panchama-Kala)* | `#088` **Manjuswana** *(Shashtha-Kala)* | `#138` **Brahmi** *(Dashama-Kala)* | **Mercury** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#064`** | `12° 36' .. 12° 48'` | `#064` **Kalakoota** *(Panchama-Kala)* | `#087` **Madhavi** *(Shashtha-Kala)* | `#139` **Kalakoota** *(Dashama-Kala)* | **Ketu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#065`** | `12° 48' .. 13° 00'` | `#065` **Shankari** *(Panchama-Kala)* | `#086` **Manohara** *(Shashtha-Kala)* | `#140` **Shankari** *(Dashama-Kala)* | **Venus** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#066`** | `13° 00' .. 13° 12'` | `#066` **Sudhakara** *(Panchama-Kala)* | `#085` **Maya** *(Shashtha-Kala)* | `#141` **Sudhakara** *(Dashama-Kala)* | **Sun** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#067`** | `13° 12' .. 13° 24'` | `#067` **Sama** *(Panchama-Kala)* | `#084` **Sura** *(Shashtha-Kala)* | `#142` **Sama** *(Dashama-Kala)* | **Moon** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#068`** | `13° 24' .. 13° 36'` | `#068` **Saumya** *(Panchama-Kala)* | `#083` **Saumya** *(Shashtha-Kala)* | `#143` **Saumya** *(Dashama-Kala)* | **Mars** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#069`** | `13° 36' .. 13° 48'` | `#069` **Sura** *(Panchama-Kala)* | `#082` **Sama** *(Shashtha-Kala)* | `#144` **Sura** *(Dashama-Kala)* | **Rahu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#070`** | `13° 48' .. 14° 00'` | `#070` **Maya** *(Panchama-Kala)* | `#081` **Sudhakara** *(Shashtha-Kala)* | `#145` **Maya** *(Dashama-Kala)* | **Jupiter** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#071`** | `14° 00' .. 14° 12'` | `#071` **Manohara** *(Panchama-Kala)* | `#080` **Shankari** *(Shashtha-Kala)* | `#146` **Manohara** *(Dashama-Kala)* | **Saturn** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#072`** | `14° 12' .. 14° 24'` | `#072` **Madhavi** *(Panchama-Kala)* | `#079` **Kalakoota** *(Shashtha-Kala)* | `#147` **Madhavi** *(Dashama-Kala)* | **Mercury** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#073`** | `14° 24' .. 14° 36'` | `#073` **Manjuswana** *(Panchama-Kala)* | `#078` **Brahmi** *(Shashtha-Kala)* | `#148` **Manjuswana** *(Dashama-Kala)* | **Ketu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#074`** | `14° 36' .. 14° 48'` | `#074` **Ghora** *(Panchama-Kala)* | `#077` **Vaishnavi** *(Shashtha-Kala)* | `#149` **Ghora** *(Dashama-Kala)* | **Venus** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#075`** | `14° 48' .. 15° 00'` | `#075` **Kumbhini** *(Panchama-Kala)* | `#076` **Vasudha** *(Shashtha-Kala)* | `#150` **Kumbhini** *(Dashama-Kala)* | **Sun** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#076`** | `15° 00' .. 15° 12'` | `#076` **Vasudha** *(Shashtha-Kala)* | `#075` **Kumbhini** *(Panchama-Kala)* | `#001` **Vasudha** *(Prathama-Kala)* | **Moon** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#077`** | `15° 12' .. 15° 24'` | `#077` **Vaishnavi** *(Shashtha-Kala)* | `#074` **Ghora** *(Panchama-Kala)* | `#002` **Vaishnavi** *(Prathama-Kala)* | **Mars** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#078`** | `15° 24' .. 15° 36'` | `#078` **Brahmi** *(Shashtha-Kala)* | `#073` **Manjuswana** *(Panchama-Kala)* | `#003` **Brahmi** *(Prathama-Kala)* | **Rahu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#079`** | `15° 36' .. 15° 48'` | `#079` **Kalakoota** *(Shashtha-Kala)* | `#072` **Madhavi** *(Panchama-Kala)* | `#004` **Kalakoota** *(Prathama-Kala)* | **Jupiter** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#080`** | `15° 48' .. 16° 00'` | `#080` **Shankari** *(Shashtha-Kala)* | `#071` **Manohara** *(Panchama-Kala)* | `#005` **Shankari** *(Prathama-Kala)* | **Saturn** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#081`** | `16° 00' .. 16° 12'` | `#081` **Sudhakara** *(Shashtha-Kala)* | `#070` **Maya** *(Panchama-Kala)* | `#006` **Sudhakara** *(Prathama-Kala)* | **Mercury** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#082`** | `16° 12' .. 16° 24'` | `#082` **Sama** *(Shashtha-Kala)* | `#069` **Sura** *(Panchama-Kala)* | `#007` **Sama** *(Prathama-Kala)* | **Ketu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#083`** | `16° 24' .. 16° 36'` | `#083` **Saumya** *(Shashtha-Kala)* | `#068` **Saumya** *(Panchama-Kala)* | `#008` **Saumya** *(Prathama-Kala)* | **Venus** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#084`** | `16° 36' .. 16° 48'` | `#084` **Sura** *(Shashtha-Kala)* | `#067` **Sama** *(Panchama-Kala)* | `#009` **Sura** *(Prathama-Kala)* | **Sun** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#085`** | `16° 48' .. 17° 00'` | `#085` **Maya** *(Shashtha-Kala)* | `#066` **Sudhakara** *(Panchama-Kala)* | `#010` **Maya** *(Prathama-Kala)* | **Moon** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#086`** | `17° 00' .. 17° 12'` | `#086` **Manohara** *(Shashtha-Kala)* | `#065` **Shankari** *(Panchama-Kala)* | `#011` **Manohara** *(Prathama-Kala)* | **Mars** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#087`** | `17° 12' .. 17° 24'` | `#087` **Madhavi** *(Shashtha-Kala)* | `#064` **Kalakoota** *(Panchama-Kala)* | `#012` **Madhavi** *(Prathama-Kala)* | **Rahu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#088`** | `17° 24' .. 17° 36'` | `#088` **Manjuswana** *(Shashtha-Kala)* | `#063` **Brahmi** *(Panchama-Kala)* | `#013` **Manjuswana** *(Prathama-Kala)* | **Jupiter** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#089`** | `17° 36' .. 17° 48'` | `#089` **Ghora** *(Shashtha-Kala)* | `#062` **Vaishnavi** *(Panchama-Kala)* | `#014` **Ghora** *(Prathama-Kala)* | **Saturn** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#090`** | `17° 48' .. 18° 00'` | `#090` **Kumbhini** *(Shashtha-Kala)* | `#061` **Vasudha** *(Panchama-Kala)* | `#015` **Kumbhini** *(Prathama-Kala)* | **Mercury** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#091`** | `18° 00' .. 18° 12'` | `#091` **Vasudha** *(Saptama-Kala)* | `#060` **Kumbhini** *(Chaturtha-Kala)* | `#016` **Vasudha** *(Dvitiya-Kala)* | **Ketu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#092`** | `18° 12' .. 18° 24'` | `#092` **Vaishnavi** *(Saptama-Kala)* | `#059` **Ghora** *(Chaturtha-Kala)* | `#017` **Vaishnavi** *(Dvitiya-Kala)* | **Venus** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#093`** | `18° 24' .. 18° 36'` | `#093` **Brahmi** *(Saptama-Kala)* | `#058` **Manjuswana** *(Chaturtha-Kala)* | `#018` **Brahmi** *(Dvitiya-Kala)* | **Sun** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#094`** | `18° 36' .. 18° 48'` | `#094` **Kalakoota** *(Saptama-Kala)* | `#057` **Madhavi** *(Chaturtha-Kala)* | `#019` **Kalakoota** *(Dvitiya-Kala)* | **Moon** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#095`** | `18° 48' .. 19° 00'` | `#095` **Shankari** *(Saptama-Kala)* | `#056` **Manohara** *(Chaturtha-Kala)* | `#020` **Shankari** *(Dvitiya-Kala)* | **Mars** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#096`** | `19° 00' .. 19° 12'` | `#096` **Sudhakara** *(Saptama-Kala)* | `#055` **Maya** *(Chaturtha-Kala)* | `#021` **Sudhakara** *(Dvitiya-Kala)* | **Rahu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#097`** | `19° 12' .. 19° 24'` | `#097` **Sama** *(Saptama-Kala)* | `#054` **Sura** *(Chaturtha-Kala)* | `#022` **Sama** *(Dvitiya-Kala)* | **Jupiter** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#098`** | `19° 24' .. 19° 36'` | `#098` **Saumya** *(Saptama-Kala)* | `#053` **Saumya** *(Chaturtha-Kala)* | `#023` **Saumya** *(Dvitiya-Kala)* | **Saturn** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#099`** | `19° 36' .. 19° 48'` | `#099` **Sura** *(Saptama-Kala)* | `#052` **Sama** *(Chaturtha-Kala)* | `#024` **Sura** *(Dvitiya-Kala)* | **Mercury** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#100`** | `19° 48' .. 20° 00'` | `#100` **Maya** *(Saptama-Kala)* | `#051` **Sudhakara** *(Chaturtha-Kala)* | `#025` **Maya** *(Dvitiya-Kala)* | **Ketu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#101`** | `20° 00' .. 20° 12'` | `#101` **Manohara** *(Saptama-Kala)* | `#050` **Shankari** *(Chaturtha-Kala)* | `#026` **Manohara** *(Dvitiya-Kala)* | **Venus** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#102`** | `20° 12' .. 20° 24'` | `#102` **Madhavi** *(Saptama-Kala)* | `#049` **Kalakoota** *(Chaturtha-Kala)* | `#027` **Madhavi** *(Dvitiya-Kala)* | **Sun** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#103`** | `20° 24' .. 20° 36'` | `#103` **Manjuswana** *(Saptama-Kala)* | `#048` **Brahmi** *(Chaturtha-Kala)* | `#028` **Manjuswana** *(Dvitiya-Kala)* | **Moon** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#104`** | `20° 36' .. 20° 48'` | `#104` **Ghora** *(Saptama-Kala)* | `#047` **Vaishnavi** *(Chaturtha-Kala)* | `#029` **Ghora** *(Dvitiya-Kala)* | **Mars** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#105`** | `20° 48' .. 21° 00'` | `#105` **Kumbhini** *(Saptama-Kala)* | `#046` **Vasudha** *(Chaturtha-Kala)* | `#030` **Kumbhini** *(Dvitiya-Kala)* | **Rahu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#106`** | `21° 00' .. 21° 12'` | `#106` **Vasudha** *(Ashtama-Kala)* | `#045` **Kumbhini** *(Tritiya-Kala)* | `#031` **Vasudha** *(Tritiya-Kala)* | **Jupiter** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#107`** | `21° 12' .. 21° 24'` | `#107` **Vaishnavi** *(Ashtama-Kala)* | `#044` **Ghora** *(Tritiya-Kala)* | `#032` **Vaishnavi** *(Tritiya-Kala)* | **Saturn** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#108`** | `21° 24' .. 21° 36'` | `#108` **Brahmi** *(Ashtama-Kala)* | `#043` **Manjuswana** *(Tritiya-Kala)* | `#033` **Brahmi** *(Tritiya-Kala)* | **Mercury** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#109`** | `21° 36' .. 21° 48'` | `#109` **Kalakoota** *(Ashtama-Kala)* | `#042` **Madhavi** *(Tritiya-Kala)* | `#034` **Kalakoota** *(Tritiya-Kala)* | **Ketu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#110`** | `21° 48' .. 22° 00'` | `#110` **Shankari** *(Ashtama-Kala)* | `#041` **Manohara** *(Tritiya-Kala)* | `#035` **Shankari** *(Tritiya-Kala)* | **Venus** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#111`** | `22° 00' .. 22° 12'` | `#111` **Sudhakara** *(Ashtama-Kala)* | `#040` **Maya** *(Tritiya-Kala)* | `#036` **Sudhakara** *(Tritiya-Kala)* | **Sun** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#112`** | `22° 12' .. 22° 24'` | `#112` **Sama** *(Ashtama-Kala)* | `#039` **Sura** *(Tritiya-Kala)* | `#037` **Sama** *(Tritiya-Kala)* | **Moon** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#113`** | `22° 24' .. 22° 36'` | `#113` **Saumya** *(Ashtama-Kala)* | `#038` **Saumya** *(Tritiya-Kala)* | `#038` **Saumya** *(Tritiya-Kala)* | **Mars** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#114`** | `22° 36' .. 22° 48'` | `#114` **Sura** *(Ashtama-Kala)* | `#037` **Sama** *(Tritiya-Kala)* | `#039` **Sura** *(Tritiya-Kala)* | **Rahu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#115`** | `22° 48' .. 23° 00'` | `#115` **Maya** *(Ashtama-Kala)* | `#036` **Sudhakara** *(Tritiya-Kala)* | `#040` **Maya** *(Tritiya-Kala)* | **Jupiter** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#116`** | `23° 00' .. 23° 12'` | `#116` **Manohara** *(Ashtama-Kala)* | `#035` **Shankari** *(Tritiya-Kala)* | `#041` **Manohara** *(Tritiya-Kala)* | **Saturn** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#117`** | `23° 12' .. 23° 24'` | `#117` **Madhavi** *(Ashtama-Kala)* | `#034` **Kalakoota** *(Tritiya-Kala)* | `#042` **Madhavi** *(Tritiya-Kala)* | **Mercury** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#118`** | `23° 24' .. 23° 36'` | `#118` **Manjuswana** *(Ashtama-Kala)* | `#033` **Brahmi** *(Tritiya-Kala)* | `#043` **Manjuswana** *(Tritiya-Kala)* | **Ketu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#119`** | `23° 36' .. 23° 48'` | `#119` **Ghora** *(Ashtama-Kala)* | `#032` **Vaishnavi** *(Tritiya-Kala)* | `#044` **Ghora** *(Tritiya-Kala)* | **Venus** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#120`** | `23° 48' .. 24° 00'` | `#120` **Kumbhini** *(Ashtama-Kala)* | `#031` **Vasudha** *(Tritiya-Kala)* | `#045` **Kumbhini** *(Tritiya-Kala)* | **Sun** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#121`** | `24° 00' .. 24° 12'` | `#121` **Vasudha** *(Navama-Kala)* | `#030` **Kumbhini** *(Dvitiya-Kala)* | `#046` **Vasudha** *(Chaturtha-Kala)* | **Moon** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#122`** | `24° 12' .. 24° 24'` | `#122` **Vaishnavi** *(Navama-Kala)* | `#029` **Ghora** *(Dvitiya-Kala)* | `#047` **Vaishnavi** *(Chaturtha-Kala)* | **Mars** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#123`** | `24° 24' .. 24° 36'` | `#123` **Brahmi** *(Navama-Kala)* | `#028` **Manjuswana** *(Dvitiya-Kala)* | `#048` **Brahmi** *(Chaturtha-Kala)* | **Rahu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#124`** | `24° 36' .. 24° 48'` | `#124` **Kalakoota** *(Navama-Kala)* | `#027` **Madhavi** *(Dvitiya-Kala)* | `#049` **Kalakoota** *(Chaturtha-Kala)* | **Jupiter** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#125`** | `24° 48' .. 25° 00'` | `#125` **Shankari** *(Navama-Kala)* | `#026` **Manohara** *(Dvitiya-Kala)* | `#050` **Shankari** *(Chaturtha-Kala)* | **Saturn** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#126`** | `25° 00' .. 25° 12'` | `#126` **Sudhakara** *(Navama-Kala)* | `#025` **Maya** *(Dvitiya-Kala)* | `#051` **Sudhakara** *(Chaturtha-Kala)* | **Mercury** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#127`** | `25° 12' .. 25° 24'` | `#127` **Sama** *(Navama-Kala)* | `#024` **Sura** *(Dvitiya-Kala)* | `#052` **Sama** *(Chaturtha-Kala)* | **Ketu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#128`** | `25° 24' .. 25° 36'` | `#128` **Saumya** *(Navama-Kala)* | `#023` **Saumya** *(Dvitiya-Kala)* | `#053` **Saumya** *(Chaturtha-Kala)* | **Venus** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#129`** | `25° 36' .. 25° 48'` | `#129` **Sura** *(Navama-Kala)* | `#022` **Sama** *(Dvitiya-Kala)* | `#054` **Sura** *(Chaturtha-Kala)* | **Sun** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#130`** | `25° 48' .. 26° 00'` | `#130` **Maya** *(Navama-Kala)* | `#021` **Sudhakara** *(Dvitiya-Kala)* | `#055` **Maya** *(Chaturtha-Kala)* | **Moon** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#131`** | `26° 00' .. 26° 12'` | `#131` **Manohara** *(Navama-Kala)* | `#020` **Shankari** *(Dvitiya-Kala)* | `#056` **Manohara** *(Chaturtha-Kala)* | **Mars** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#132`** | `26° 12' .. 26° 24'` | `#132` **Madhavi** *(Navama-Kala)* | `#019` **Kalakoota** *(Dvitiya-Kala)* | `#057` **Madhavi** *(Chaturtha-Kala)* | **Rahu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#133`** | `26° 24' .. 26° 36'` | `#133` **Manjuswana** *(Navama-Kala)* | `#018` **Brahmi** *(Dvitiya-Kala)* | `#058` **Manjuswana** *(Chaturtha-Kala)* | **Jupiter** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#134`** | `26° 36' .. 26° 48'` | `#134` **Ghora** *(Navama-Kala)* | `#017` **Vaishnavi** *(Dvitiya-Kala)* | `#059` **Ghora** *(Chaturtha-Kala)* | **Saturn** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#135`** | `26° 48' .. 27° 00'` | `#135` **Kumbhini** *(Navama-Kala)* | `#016` **Vasudha** *(Dvitiya-Kala)* | `#060` **Kumbhini** *(Chaturtha-Kala)* | **Mercury** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#136`** | `27° 00' .. 27° 12'` | `#136` **Vasudha** *(Dashama-Kala)* | `#015` **Kumbhini** *(Prathama-Kala)* | `#061` **Vasudha** *(Panchama-Kala)* | **Ketu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#137`** | `27° 12' .. 27° 24'` | `#137` **Vaishnavi** *(Dashama-Kala)* | `#014` **Ghora** *(Prathama-Kala)* | `#062` **Vaishnavi** *(Panchama-Kala)* | **Venus** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#138`** | `27° 24' .. 27° 36'` | `#138` **Brahmi** *(Dashama-Kala)* | `#013` **Manjuswana** *(Prathama-Kala)* | `#063` **Brahmi** *(Panchama-Kala)* | **Sun** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#139`** | `27° 36' .. 27° 48'` | `#139` **Kalakoota** *(Dashama-Kala)* | `#012` **Madhavi** *(Prathama-Kala)* | `#064` **Kalakoota** *(Panchama-Kala)* | **Moon** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#140`** | `27° 48' .. 28° 00'` | `#140` **Shankari** *(Dashama-Kala)* | `#011` **Manohara** *(Prathama-Kala)* | `#065` **Shankari** *(Panchama-Kala)* | **Mars** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#141`** | `28° 00' .. 28° 12'` | `#141` **Sudhakara** *(Dashama-Kala)* | `#010` **Maya** *(Prathama-Kala)* | `#066` **Sudhakara** *(Panchama-Kala)* | **Rahu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#142`** | `28° 12' .. 28° 24'` | `#142` **Sama** *(Dashama-Kala)* | `#009` **Sura** *(Prathama-Kala)* | `#067` **Sama** *(Panchama-Kala)* | **Jupiter** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#143`** | `28° 24' .. 28° 36'` | `#143` **Saumya** *(Dashama-Kala)* | `#008` **Saumya** *(Prathama-Kala)* | `#068` **Saumya** *(Panchama-Kala)* | **Saturn** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#144`** | `28° 36' .. 28° 48'` | `#144` **Sura** *(Dashama-Kala)* | `#007` **Sama** *(Prathama-Kala)* | `#069` **Sura** *(Panchama-Kala)* | **Mercury** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#145`** | `28° 48' .. 29° 00'` | `#145` **Maya** *(Dashama-Kala)* | `#006` **Sudhakara** *(Prathama-Kala)* | `#070` **Maya** *(Panchama-Kala)* | **Ketu** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#146`** | `29° 00' .. 29° 12'` | `#146` **Manohara** *(Dashama-Kala)* | `#005` **Shankari** *(Prathama-Kala)* | `#071` **Manohara** *(Panchama-Kala)* | **Venus** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#147`** | `29° 12' .. 29° 24'` | `#147` **Madhavi** *(Dashama-Kala)* | `#004` **Kalakoota** *(Prathama-Kala)* | `#072` **Madhavi** *(Panchama-Kala)* | **Sun** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#148`** | `29° 24' .. 29° 36'` | `#148` **Manjuswana** *(Dashama-Kala)* | `#003` **Brahmi** *(Prathama-Kala)* | `#073` **Manjuswana** *(Panchama-Kala)* | **Moon** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#149`** | `29° 36' .. 29° 48'` | `#149` **Ghora** *(Dashama-Kala)* | `#002` **Vaishnavi** *(Prathama-Kala)* | `#074` **Ghora** *(Panchama-Kala)* | **Mars** | `48.0 sec` (`0°12'` Lagna shift) |
| **`#150`** | `29° 48' .. 30° 00'` | `#150` **Kumbhini** *(Dashama-Kala)* | `#001` **Vasudha** *(Prathama-Kala)* | `#075` **Kumbhini** *(Panchama-Kala)* | **Rahu** | `48.0 sec` (`0°12'` Lagna shift) |

### 26.2 Worked Case Study: Natal 150-*Nadi Amsa* Coordinates & Exact Seconds to Boundary Flip

| Point | Sidereal Longitude (`DMS`) | Sign & Modality | Nadi `#` (`1..150`) | Zodiacal Nadi (`1..1800`) | Classical *Deva Keralam* Nadi Name | Nadi Ruler | Seconds to Prev / Next Nadi Flip |
|---|---|---|---|---|---|---|---|
| **Ascendant (Lagna)** | `Dhanu 22° 18' 00"` | Dhanu *(Dwiswabhava (Dual: 76..150, 1..75))* | **`#037`** | `#1237` | **Sama (Tritiya-Kala)** | `Ketu` | `-24.0s / +24.0s` |
| **Sun** | `Tula 28° 36' 50"` | Tula *(Chara (Movable: Direct 1..150))* | **`#144`** | `#1044` | **Sura (Dashama-Kala)** | `Mercury` | `-1224.3s / +16308.1s` |
| **Moon** | `Makara 03° 41' 39"` | Makara *(Chara (Movable: Direct 1..150))* | **`#019`** | `#1369` | **Kalakoota (Dvitiya-Kala)** | `Ketu` | `-618.3s / +693.1s` |
| **Mars** | `Simha 01° 11' 03"` | Simha *(Sthira (Fixed: Reverse 150..1))* | **`#145`** | `#0745` | **Maya (Dashama-Kala)** | `Ketu` | `-30373.9s / +2603.2s` |
| **Mercury** | `Tula 11° 01' 01"` | Tula *(Chara (Movable: Direct 1..150))* | **`#056`** | `#0956` | **Manohara (Chaturtha-Kala)** | `Venus` | `-1229.3s / +13170.7s` |
| **Jupiter** | `Simha 01° 33' 59"` | Simha *(Sthira (Fixed: Reverse 150..1))* | **`#143`** | `#0743` | **Saumya (Dashama-Kala)** | `Saturn` | `-172874.6s / +35067.7s` |
| **Venus** | `Kanya 28° 39' 27"` | Kanya *(Dwiswabhava (Dual: 76..150, 1..75))* | **`#069`** | `#0819` | **Sura (Panchama-Kala)** | `Rahu` | `-4322.0s / +10704.1s` |
| **Saturn** | `Meena 14° 16' 59"` | Meena *(Dwiswabhava (Dual: 76..150, 1..75))* | **`#147`** | `#1797` | **Madhavi (Dashama-Kala)** | `Sun` | `-213965.5s / +301855.4s` |
| **Rahu** | `Kumbha 01° 05' 10"` | Kumbha *(Sthira (Fixed: Reverse 150..1))* | **`#145`** | `#1645` | **Maya (Dashama-Kala)** | `Ketu` | `-140418.7s / +186235.4s` |
| **Ketu** | `Simha 01° 05' 10"` | Simha *(Sthira (Fixed: Reverse 150..1))* | **`#145`** | `#0745` | **Maya (Dashama-Kala)** | `Ketu` | `-140418.7s / +186235.4s` |

### 26.3 Complete 360-Degree Zodiacal *Deva Keralam Nadi Amsa* (`1..1800`) & *Shashtiamsa* (`D60`) Deity Cross-Reference Encyclopedia (`0°` to `359°`)

| Zodiacal Degree | `Rashi & Degree` | Sign Modality | Slice (`1..150`) | Modality-Adjusted Nadi `#` | Zodiacal Nadi (`1..1800`) | *Deva Keralam* Nadi Name & Quality | `D60` *Shashtiamsa* `#` & Deity |
|---|---|---|---|---|---|---|---|
| **`000° 00'`** | **Mesha** `00° 00'` | Chara (Direct) | `Slice #001` | **`Nadi #001`** | `#0001 / 1800` | **Vasudha** *(Prathama-Kala)* | `D60 #01` **Ghora** *(False)* |
| **`001° 00'`** | **Mesha** `01° 00'` | Chara (Direct) | `Slice #006` | **`Nadi #006`** | `#0006 / 1800` | **Sudhakara** *(Prathama-Kala)* | `D60 #03` **Deva** *(True)* |
| **`002° 00'`** | **Mesha** `02° 00'` | Chara (Direct) | `Slice #011` | **`Nadi #011`** | `#0011 / 1800` | **Manohara** *(Prathama-Kala)* | `D60 #05` **Yaksha** *(True)* |
| **`003° 00'`** | **Mesha** `03° 00'` | Chara (Direct) | `Slice #016` | **`Nadi #016`** | `#0016 / 1800` | **Vasudha** *(Dvitiya-Kala)* | `D60 #07` **Bhrashta** *(False)* |
| **`004° 00'`** | **Mesha** `04° 00'` | Chara (Direct) | `Slice #021` | **`Nadi #021`** | `#0021 / 1800` | **Sudhakara** *(Dvitiya-Kala)* | `D60 #09` **Garala** *(False)* |
| **`005° 00'`** | **Mesha** `05° 00'` | Chara (Direct) | `Slice #026` | **`Nadi #026`** | `#0026 / 1800` | **Manohara** *(Dvitiya-Kala)* | `D60 #11` **Maya** *(False)* |
| **`006° 00'`** | **Mesha** `06° 00'` | Chara (Direct) | `Slice #031` | **`Nadi #031`** | `#0031 / 1800` | **Vasudha** *(Tritiya-Kala)* | `D60 #13` **Apampati** *(True)* |
| **`007° 00'`** | **Mesha** `07° 00'` | Chara (Direct) | `Slice #036` | **`Nadi #036`** | `#0036 / 1800` | **Sudhakara** *(Tritiya-Kala)* | `D60 #15` **Kala** *(False)* |
| **`008° 00'`** | **Mesha** `08° 00'` | Chara (Direct) | `Slice #041` | **`Nadi #041`** | `#0041 / 1800` | **Manohara** *(Tritiya-Kala)* | `D60 #17` **Amrita** *(True)* |
| **`009° 00'`** | **Mesha** `09° 00'` | Chara (Direct) | `Slice #046` | **`Nadi #046`** | `#0046 / 1800` | **Vasudha** *(Chaturtha-Kala)* | `D60 #19` **Mridu** *(True)* |
| **`010° 00'`** | **Mesha** `10° 00'` | Chara (Direct) | `Slice #051` | **`Nadi #051`** | `#0051 / 1800` | **Sudhakara** *(Chaturtha-Kala)* | `D60 #21` **Heramba** *(True)* |
| **`011° 00'`** | **Mesha** `11° 00'` | Chara (Direct) | `Slice #056` | **`Nadi #056`** | `#0056 / 1800` | **Manohara** *(Chaturtha-Kala)* | `D60 #23` **Vishnu** *(True)* |
| **`012° 00'`** | **Mesha** `12° 00'` | Chara (Direct) | `Slice #061` | **`Nadi #061`** | `#0061 / 1800` | **Vasudha** *(Panchama-Kala)* | `D60 #25` **Deva** *(True)* |
| **`013° 00'`** | **Mesha** `13° 00'` | Chara (Direct) | `Slice #066` | **`Nadi #066`** | `#0066 / 1800` | **Sudhakara** *(Panchama-Kala)* | `D60 #27` **Kalinasa** *(True)* |
| **`014° 00'`** | **Mesha** `14° 00'` | Chara (Direct) | `Slice #071` | **`Nadi #071`** | `#0071 / 1800` | **Manohara** *(Panchama-Kala)* | `D60 #29` **Kamalakara** *(True)* |
| **`015° 00'`** | **Mesha** `15° 00'` | Chara (Direct) | `Slice #076` | **`Nadi #076`** | `#0076 / 1800` | **Vasudha** *(Shashtha-Kala)* | `D60 #31` **Mrityu** *(False)* |
| **`016° 00'`** | **Mesha** `16° 00'` | Chara (Direct) | `Slice #081` | **`Nadi #081`** | `#0081 / 1800` | **Sudhakara** *(Shashtha-Kala)* | `D60 #33` **Davagni** *(False)* |
| **`017° 00'`** | **Mesha** `17° 00'` | Chara (Direct) | `Slice #086` | **`Nadi #086`** | `#0086 / 1800` | **Manohara** *(Shashtha-Kala)* | `D60 #35` **Yama** *(False)* |
| **`018° 00'`** | **Mesha** `18° 00'` | Chara (Direct) | `Slice #091` | **`Nadi #091`** | `#0091 / 1800` | **Vasudha** *(Saptama-Kala)* | `D60 #37` **Sudha** *(True)* |
| **`019° 00'`** | **Mesha** `19° 00'` | Chara (Direct) | `Slice #096` | **`Nadi #096`** | `#0096 / 1800` | **Sudhakara** *(Saptama-Kala)* | `D60 #39` **Purnachandra** *(True)* |
| **`020° 00'`** | **Mesha** `20° 00'` | Chara (Direct) | `Slice #101` | **`Nadi #101`** | `#0101 / 1800` | **Manohara** *(Saptama-Kala)* | `D60 #41` **Kulanasa** *(False)* |
| **`021° 00'`** | **Mesha** `21° 00'` | Chara (Direct) | `Slice #106` | **`Nadi #106`** | `#0106 / 1800` | **Vasudha** *(Ashtama-Kala)* | `D60 #43` **Utpata** *(False)* |
| **`022° 00'`** | **Mesha** `22° 00'` | Chara (Direct) | `Slice #111` | **`Nadi #111`** | `#0111 / 1800` | **Sudhakara** *(Ashtama-Kala)* | `D60 #45` **Saumya** *(True)* |
| **`023° 00'`** | **Mesha** `23° 00'` | Chara (Direct) | `Slice #116` | **`Nadi #116`** | `#0116 / 1800` | **Manohara** *(Ashtama-Kala)* | `D60 #47` **Sheetala** *(True)* |
| **`024° 00'`** | **Mesha** `24° 00'` | Chara (Direct) | `Slice #121` | **`Nadi #121`** | `#0121 / 1800` | **Vasudha** *(Navama-Kala)* | `D60 #49` **Chandramukhi** *(True)* |
| **`025° 00'`** | **Mesha** `25° 00'` | Chara (Direct) | `Slice #126` | **`Nadi #126`** | `#0126 / 1800` | **Sudhakara** *(Navama-Kala)* | `D60 #51` **Kalapavaka** *(False)* |
| **`026° 00'`** | **Mesha** `26° 00'` | Chara (Direct) | `Slice #131` | **`Nadi #131`** | `#0131 / 1800` | **Manohara** *(Navama-Kala)* | `D60 #53` **Nirmala** *(True)* |
| **`027° 00'`** | **Mesha** `27° 00'` | Chara (Direct) | `Slice #136` | **`Nadi #136`** | `#0136 / 1800` | **Vasudha** *(Dashama-Kala)* | `D60 #55` **Krura** *(False)* |
| **`028° 00'`** | **Mesha** `28° 00'` | Chara (Direct) | `Slice #141` | **`Nadi #141`** | `#0141 / 1800` | **Sudhakara** *(Dashama-Kala)* | `D60 #57` **Amrita** *(True)* |
| **`029° 00'`** | **Mesha** `29° 00'` | Chara (Direct) | `Slice #146` | **`Nadi #146`** | `#0146 / 1800` | **Manohara** *(Dashama-Kala)* | `D60 #59` **Bhramana** *(False)* |
| **`030° 00'`** | **Vrishabha** `00° 00'` | Sthira (Reverse) | `Slice #001` | **`Nadi #150`** | `#0300 / 1800` | **Kumbhini** *(Dashama-Kala)* | `D60 #01` **Ghora** *(False)* |
| **`031° 00'`** | **Vrishabha** `01° 00'` | Sthira (Reverse) | `Slice #006` | **`Nadi #145`** | `#0295 / 1800` | **Maya** *(Dashama-Kala)* | `D60 #03` **Deva** *(True)* |
| **`032° 00'`** | **Vrishabha** `02° 00'` | Sthira (Reverse) | `Slice #011` | **`Nadi #140`** | `#0290 / 1800` | **Shankari** *(Dashama-Kala)* | `D60 #05` **Yaksha** *(True)* |
| **`033° 00'`** | **Vrishabha** `03° 00'` | Sthira (Reverse) | `Slice #016` | **`Nadi #135`** | `#0285 / 1800` | **Kumbhini** *(Navama-Kala)* | `D60 #07` **Bhrashta** *(False)* |
| **`034° 00'`** | **Vrishabha** `04° 00'` | Sthira (Reverse) | `Slice #021` | **`Nadi #130`** | `#0280 / 1800` | **Maya** *(Navama-Kala)* | `D60 #09` **Garala** *(False)* |
| **`035° 00'`** | **Vrishabha** `05° 00'` | Sthira (Reverse) | `Slice #026` | **`Nadi #125`** | `#0275 / 1800` | **Shankari** *(Navama-Kala)* | `D60 #11` **Maya** *(False)* |
| **`036° 00'`** | **Vrishabha** `06° 00'` | Sthira (Reverse) | `Slice #031` | **`Nadi #120`** | `#0270 / 1800` | **Kumbhini** *(Ashtama-Kala)* | `D60 #13` **Apampati** *(True)* |
| **`037° 00'`** | **Vrishabha** `07° 00'` | Sthira (Reverse) | `Slice #036` | **`Nadi #115`** | `#0265 / 1800` | **Maya** *(Ashtama-Kala)* | `D60 #15` **Kala** *(False)* |
| **`038° 00'`** | **Vrishabha** `08° 00'` | Sthira (Reverse) | `Slice #041` | **`Nadi #110`** | `#0260 / 1800` | **Shankari** *(Ashtama-Kala)* | `D60 #17` **Amrita** *(True)* |
| **`039° 00'`** | **Vrishabha** `09° 00'` | Sthira (Reverse) | `Slice #046` | **`Nadi #105`** | `#0255 / 1800` | **Kumbhini** *(Saptama-Kala)* | `D60 #19` **Mridu** *(True)* |
| **`040° 00'`** | **Vrishabha** `10° 00'` | Sthira (Reverse) | `Slice #051` | **`Nadi #100`** | `#0250 / 1800` | **Maya** *(Saptama-Kala)* | `D60 #21` **Heramba** *(True)* |
| **`041° 00'`** | **Vrishabha** `11° 00'` | Sthira (Reverse) | `Slice #056` | **`Nadi #095`** | `#0245 / 1800` | **Shankari** *(Saptama-Kala)* | `D60 #23` **Vishnu** *(True)* |
| **`042° 00'`** | **Vrishabha** `12° 00'` | Sthira (Reverse) | `Slice #061` | **`Nadi #090`** | `#0240 / 1800` | **Kumbhini** *(Shashtha-Kala)* | `D60 #25` **Deva** *(True)* |
| **`043° 00'`** | **Vrishabha** `13° 00'` | Sthira (Reverse) | `Slice #066` | **`Nadi #085`** | `#0235 / 1800` | **Maya** *(Shashtha-Kala)* | `D60 #27` **Kalinasa** *(True)* |
| **`044° 00'`** | **Vrishabha** `14° 00'` | Sthira (Reverse) | `Slice #071` | **`Nadi #080`** | `#0230 / 1800` | **Shankari** *(Shashtha-Kala)* | `D60 #29` **Kamalakara** *(True)* |
| **`045° 00'`** | **Vrishabha** `15° 00'` | Sthira (Reverse) | `Slice #076` | **`Nadi #075`** | `#0225 / 1800` | **Kumbhini** *(Panchama-Kala)* | `D60 #31` **Mrityu** *(False)* |
| **`046° 00'`** | **Vrishabha** `16° 00'` | Sthira (Reverse) | `Slice #081` | **`Nadi #070`** | `#0220 / 1800` | **Maya** *(Panchama-Kala)* | `D60 #33` **Davagni** *(False)* |
| **`047° 00'`** | **Vrishabha** `17° 00'` | Sthira (Reverse) | `Slice #086` | **`Nadi #065`** | `#0215 / 1800` | **Shankari** *(Panchama-Kala)* | `D60 #35` **Yama** *(False)* |
| **`048° 00'`** | **Vrishabha** `18° 00'` | Sthira (Reverse) | `Slice #091` | **`Nadi #060`** | `#0210 / 1800` | **Kumbhini** *(Chaturtha-Kala)* | `D60 #37` **Sudha** *(True)* |
| **`049° 00'`** | **Vrishabha** `19° 00'` | Sthira (Reverse) | `Slice #096` | **`Nadi #055`** | `#0205 / 1800` | **Maya** *(Chaturtha-Kala)* | `D60 #39` **Purnachandra** *(True)* |
| **`050° 00'`** | **Vrishabha** `20° 00'` | Sthira (Reverse) | `Slice #101` | **`Nadi #050`** | `#0200 / 1800` | **Shankari** *(Chaturtha-Kala)* | `D60 #41` **Kulanasa** *(False)* |
| **`051° 00'`** | **Vrishabha** `21° 00'` | Sthira (Reverse) | `Slice #106` | **`Nadi #045`** | `#0195 / 1800` | **Kumbhini** *(Tritiya-Kala)* | `D60 #43` **Utpata** *(False)* |
| **`052° 00'`** | **Vrishabha** `22° 00'` | Sthira (Reverse) | `Slice #111` | **`Nadi #040`** | `#0190 / 1800` | **Maya** *(Tritiya-Kala)* | `D60 #45` **Saumya** *(True)* |
| **`053° 00'`** | **Vrishabha** `23° 00'` | Sthira (Reverse) | `Slice #116` | **`Nadi #035`** | `#0185 / 1800` | **Shankari** *(Tritiya-Kala)* | `D60 #47` **Sheetala** *(True)* |
| **`054° 00'`** | **Vrishabha** `24° 00'` | Sthira (Reverse) | `Slice #121` | **`Nadi #030`** | `#0180 / 1800` | **Kumbhini** *(Dvitiya-Kala)* | `D60 #49` **Chandramukhi** *(True)* |
| **`055° 00'`** | **Vrishabha** `25° 00'` | Sthira (Reverse) | `Slice #126` | **`Nadi #025`** | `#0175 / 1800` | **Maya** *(Dvitiya-Kala)* | `D60 #51` **Kalapavaka** *(False)* |
| **`056° 00'`** | **Vrishabha** `26° 00'` | Sthira (Reverse) | `Slice #131` | **`Nadi #020`** | `#0170 / 1800` | **Shankari** *(Dvitiya-Kala)* | `D60 #53` **Nirmala** *(True)* |
| **`057° 00'`** | **Vrishabha** `27° 00'` | Sthira (Reverse) | `Slice #136` | **`Nadi #015`** | `#0165 / 1800` | **Kumbhini** *(Prathama-Kala)* | `D60 #55` **Krura** *(False)* |
| **`058° 00'`** | **Vrishabha** `28° 00'` | Sthira (Reverse) | `Slice #141` | **`Nadi #010`** | `#0160 / 1800` | **Maya** *(Prathama-Kala)* | `D60 #57` **Amrita** *(True)* |
| **`059° 00'`** | **Vrishabha** `29° 00'` | Sthira (Reverse) | `Slice #146` | **`Nadi #005`** | `#0155 / 1800` | **Shankari** *(Prathama-Kala)* | `D60 #59` **Bhramana** *(False)* |
| **`060° 00'`** | **Mithuna** `00° 00'` | Dwiswabhava (Mid) | `Slice #001` | **`Nadi #076`** | `#0376 / 1800` | **Vasudha** *(Shashtha-Kala)* | `D60 #01` **Ghora** *(False)* |
| **`061° 00'`** | **Mithuna** `01° 00'` | Dwiswabhava (Mid) | `Slice #006` | **`Nadi #081`** | `#0381 / 1800` | **Sudhakara** *(Shashtha-Kala)* | `D60 #03` **Deva** *(True)* |
| **`062° 00'`** | **Mithuna** `02° 00'` | Dwiswabhava (Mid) | `Slice #011` | **`Nadi #086`** | `#0386 / 1800` | **Manohara** *(Shashtha-Kala)* | `D60 #05` **Yaksha** *(True)* |
| **`063° 00'`** | **Mithuna** `03° 00'` | Dwiswabhava (Mid) | `Slice #016` | **`Nadi #091`** | `#0391 / 1800` | **Vasudha** *(Saptama-Kala)* | `D60 #07` **Bhrashta** *(False)* |
| **`064° 00'`** | **Mithuna** `04° 00'` | Dwiswabhava (Mid) | `Slice #021` | **`Nadi #096`** | `#0396 / 1800` | **Sudhakara** *(Saptama-Kala)* | `D60 #09` **Garala** *(False)* |
| **`065° 00'`** | **Mithuna** `05° 00'` | Dwiswabhava (Mid) | `Slice #026` | **`Nadi #101`** | `#0401 / 1800` | **Manohara** *(Saptama-Kala)* | `D60 #11` **Maya** *(False)* |
| **`066° 00'`** | **Mithuna** `06° 00'` | Dwiswabhava (Mid) | `Slice #031` | **`Nadi #106`** | `#0406 / 1800` | **Vasudha** *(Ashtama-Kala)* | `D60 #13` **Apampati** *(True)* |
| **`067° 00'`** | **Mithuna** `07° 00'` | Dwiswabhava (Mid) | `Slice #036` | **`Nadi #111`** | `#0411 / 1800` | **Sudhakara** *(Ashtama-Kala)* | `D60 #15` **Kala** *(False)* |
| **`068° 00'`** | **Mithuna** `08° 00'` | Dwiswabhava (Mid) | `Slice #041` | **`Nadi #116`** | `#0416 / 1800` | **Manohara** *(Ashtama-Kala)* | `D60 #17` **Amrita** *(True)* |
| **`069° 00'`** | **Mithuna** `09° 00'` | Dwiswabhava (Mid) | `Slice #046` | **`Nadi #121`** | `#0421 / 1800` | **Vasudha** *(Navama-Kala)* | `D60 #19` **Mridu** *(True)* |
| **`070° 00'`** | **Mithuna** `10° 00'` | Dwiswabhava (Mid) | `Slice #051` | **`Nadi #126`** | `#0426 / 1800` | **Sudhakara** *(Navama-Kala)* | `D60 #21` **Heramba** *(True)* |
| **`071° 00'`** | **Mithuna** `11° 00'` | Dwiswabhava (Mid) | `Slice #056` | **`Nadi #131`** | `#0431 / 1800` | **Manohara** *(Navama-Kala)* | `D60 #23` **Vishnu** *(True)* |
| **`072° 00'`** | **Mithuna** `12° 00'` | Dwiswabhava (Mid) | `Slice #061` | **`Nadi #136`** | `#0436 / 1800` | **Vasudha** *(Dashama-Kala)* | `D60 #25` **Deva** *(True)* |
| **`073° 00'`** | **Mithuna** `13° 00'` | Dwiswabhava (Mid) | `Slice #066` | **`Nadi #141`** | `#0441 / 1800` | **Sudhakara** *(Dashama-Kala)* | `D60 #27` **Kalinasa** *(True)* |
| **`074° 00'`** | **Mithuna** `14° 00'` | Dwiswabhava (Mid) | `Slice #071` | **`Nadi #146`** | `#0446 / 1800` | **Manohara** *(Dashama-Kala)* | `D60 #29` **Kamalakara** *(True)* |
| **`075° 00'`** | **Mithuna** `15° 00'` | Dwiswabhava (Mid) | `Slice #076` | **`Nadi #001`** | `#0301 / 1800` | **Vasudha** *(Prathama-Kala)* | `D60 #31` **Mrityu** *(False)* |
| **`076° 00'`** | **Mithuna** `16° 00'` | Dwiswabhava (Mid) | `Slice #081` | **`Nadi #006`** | `#0306 / 1800` | **Sudhakara** *(Prathama-Kala)* | `D60 #33` **Davagni** *(False)* |
| **`077° 00'`** | **Mithuna** `17° 00'` | Dwiswabhava (Mid) | `Slice #086` | **`Nadi #011`** | `#0311 / 1800` | **Manohara** *(Prathama-Kala)* | `D60 #35` **Yama** *(False)* |
| **`078° 00'`** | **Mithuna** `18° 00'` | Dwiswabhava (Mid) | `Slice #091` | **`Nadi #016`** | `#0316 / 1800` | **Vasudha** *(Dvitiya-Kala)* | `D60 #37` **Sudha** *(True)* |
| **`079° 00'`** | **Mithuna** `19° 00'` | Dwiswabhava (Mid) | `Slice #096` | **`Nadi #021`** | `#0321 / 1800` | **Sudhakara** *(Dvitiya-Kala)* | `D60 #39` **Purnachandra** *(True)* |
| **`080° 00'`** | **Mithuna** `20° 00'` | Dwiswabhava (Mid) | `Slice #101` | **`Nadi #026`** | `#0326 / 1800` | **Manohara** *(Dvitiya-Kala)* | `D60 #41` **Kulanasa** *(False)* |
| **`081° 00'`** | **Mithuna** `21° 00'` | Dwiswabhava (Mid) | `Slice #106` | **`Nadi #031`** | `#0331 / 1800` | **Vasudha** *(Tritiya-Kala)* | `D60 #43` **Utpata** *(False)* |
| **`082° 00'`** | **Mithuna** `22° 00'` | Dwiswabhava (Mid) | `Slice #111` | **`Nadi #036`** | `#0336 / 1800` | **Sudhakara** *(Tritiya-Kala)* | `D60 #45` **Saumya** *(True)* |
| **`083° 00'`** | **Mithuna** `23° 00'` | Dwiswabhava (Mid) | `Slice #116` | **`Nadi #041`** | `#0341 / 1800` | **Manohara** *(Tritiya-Kala)* | `D60 #47` **Sheetala** *(True)* |
| **`084° 00'`** | **Mithuna** `24° 00'` | Dwiswabhava (Mid) | `Slice #121` | **`Nadi #046`** | `#0346 / 1800` | **Vasudha** *(Chaturtha-Kala)* | `D60 #49` **Chandramukhi** *(True)* |
| **`085° 00'`** | **Mithuna** `25° 00'` | Dwiswabhava (Mid) | `Slice #126` | **`Nadi #051`** | `#0351 / 1800` | **Sudhakara** *(Chaturtha-Kala)* | `D60 #51` **Kalapavaka** *(False)* |
| **`086° 00'`** | **Mithuna** `26° 00'` | Dwiswabhava (Mid) | `Slice #131` | **`Nadi #056`** | `#0356 / 1800` | **Manohara** *(Chaturtha-Kala)* | `D60 #53` **Nirmala** *(True)* |
| **`087° 00'`** | **Mithuna** `27° 00'` | Dwiswabhava (Mid) | `Slice #136` | **`Nadi #061`** | `#0361 / 1800` | **Vasudha** *(Panchama-Kala)* | `D60 #55` **Krura** *(False)* |
| **`088° 00'`** | **Mithuna** `28° 00'` | Dwiswabhava (Mid) | `Slice #141` | **`Nadi #066`** | `#0366 / 1800` | **Sudhakara** *(Panchama-Kala)* | `D60 #57` **Amrita** *(True)* |
| **`089° 00'`** | **Mithuna** `29° 00'` | Dwiswabhava (Mid) | `Slice #146` | **`Nadi #071`** | `#0371 / 1800` | **Manohara** *(Panchama-Kala)* | `D60 #59` **Bhramana** *(False)* |
| **`090° 00'`** | **Karka** `00° 00'` | Chara (Direct) | `Slice #001` | **`Nadi #001`** | `#0451 / 1800` | **Vasudha** *(Prathama-Kala)* | `D60 #01` **Ghora** *(False)* |
| **`091° 00'`** | **Karka** `01° 00'` | Chara (Direct) | `Slice #006` | **`Nadi #006`** | `#0456 / 1800` | **Sudhakara** *(Prathama-Kala)* | `D60 #03` **Deva** *(True)* |
| **`092° 00'`** | **Karka** `02° 00'` | Chara (Direct) | `Slice #011` | **`Nadi #011`** | `#0461 / 1800` | **Manohara** *(Prathama-Kala)* | `D60 #05` **Yaksha** *(True)* |
| **`093° 00'`** | **Karka** `03° 00'` | Chara (Direct) | `Slice #016` | **`Nadi #016`** | `#0466 / 1800` | **Vasudha** *(Dvitiya-Kala)* | `D60 #07` **Bhrashta** *(False)* |
| **`094° 00'`** | **Karka** `04° 00'` | Chara (Direct) | `Slice #021` | **`Nadi #021`** | `#0471 / 1800` | **Sudhakara** *(Dvitiya-Kala)* | `D60 #09` **Garala** *(False)* |
| **`095° 00'`** | **Karka** `05° 00'` | Chara (Direct) | `Slice #026` | **`Nadi #026`** | `#0476 / 1800` | **Manohara** *(Dvitiya-Kala)* | `D60 #11` **Maya** *(False)* |
| **`096° 00'`** | **Karka** `06° 00'` | Chara (Direct) | `Slice #031` | **`Nadi #031`** | `#0481 / 1800` | **Vasudha** *(Tritiya-Kala)* | `D60 #13` **Apampati** *(True)* |
| **`097° 00'`** | **Karka** `07° 00'` | Chara (Direct) | `Slice #036` | **`Nadi #036`** | `#0486 / 1800` | **Sudhakara** *(Tritiya-Kala)* | `D60 #15` **Kala** *(False)* |
| **`098° 00'`** | **Karka** `08° 00'` | Chara (Direct) | `Slice #041` | **`Nadi #041`** | `#0491 / 1800` | **Manohara** *(Tritiya-Kala)* | `D60 #17` **Amrita** *(True)* |
| **`099° 00'`** | **Karka** `09° 00'` | Chara (Direct) | `Slice #046` | **`Nadi #046`** | `#0496 / 1800` | **Vasudha** *(Chaturtha-Kala)* | `D60 #19` **Mridu** *(True)* |
| **`100° 00'`** | **Karka** `10° 00'` | Chara (Direct) | `Slice #051` | **`Nadi #051`** | `#0501 / 1800` | **Sudhakara** *(Chaturtha-Kala)* | `D60 #21` **Heramba** *(True)* |
| **`101° 00'`** | **Karka** `11° 00'` | Chara (Direct) | `Slice #056` | **`Nadi #056`** | `#0506 / 1800` | **Manohara** *(Chaturtha-Kala)* | `D60 #23` **Vishnu** *(True)* |
| **`102° 00'`** | **Karka** `12° 00'` | Chara (Direct) | `Slice #061` | **`Nadi #061`** | `#0511 / 1800` | **Vasudha** *(Panchama-Kala)* | `D60 #25` **Deva** *(True)* |
| **`103° 00'`** | **Karka** `13° 00'` | Chara (Direct) | `Slice #066` | **`Nadi #066`** | `#0516 / 1800` | **Sudhakara** *(Panchama-Kala)* | `D60 #27` **Kalinasa** *(True)* |
| **`104° 00'`** | **Karka** `14° 00'` | Chara (Direct) | `Slice #071` | **`Nadi #071`** | `#0521 / 1800` | **Manohara** *(Panchama-Kala)* | `D60 #29` **Kamalakara** *(True)* |
| **`105° 00'`** | **Karka** `15° 00'` | Chara (Direct) | `Slice #076` | **`Nadi #076`** | `#0526 / 1800` | **Vasudha** *(Shashtha-Kala)* | `D60 #31` **Mrityu** *(False)* |
| **`106° 00'`** | **Karka** `16° 00'` | Chara (Direct) | `Slice #081` | **`Nadi #081`** | `#0531 / 1800` | **Sudhakara** *(Shashtha-Kala)* | `D60 #33` **Davagni** *(False)* |
| **`107° 00'`** | **Karka** `17° 00'` | Chara (Direct) | `Slice #086` | **`Nadi #086`** | `#0536 / 1800` | **Manohara** *(Shashtha-Kala)* | `D60 #35` **Yama** *(False)* |
| **`108° 00'`** | **Karka** `18° 00'` | Chara (Direct) | `Slice #091` | **`Nadi #091`** | `#0541 / 1800` | **Vasudha** *(Saptama-Kala)* | `D60 #37` **Sudha** *(True)* |
| **`109° 00'`** | **Karka** `19° 00'` | Chara (Direct) | `Slice #096` | **`Nadi #096`** | `#0546 / 1800` | **Sudhakara** *(Saptama-Kala)* | `D60 #39` **Purnachandra** *(True)* |
| **`110° 00'`** | **Karka** `20° 00'` | Chara (Direct) | `Slice #101` | **`Nadi #101`** | `#0551 / 1800` | **Manohara** *(Saptama-Kala)* | `D60 #41` **Kulanasa** *(False)* |
| **`111° 00'`** | **Karka** `21° 00'` | Chara (Direct) | `Slice #106` | **`Nadi #106`** | `#0556 / 1800` | **Vasudha** *(Ashtama-Kala)* | `D60 #43` **Utpata** *(False)* |
| **`112° 00'`** | **Karka** `22° 00'` | Chara (Direct) | `Slice #111` | **`Nadi #111`** | `#0561 / 1800` | **Sudhakara** *(Ashtama-Kala)* | `D60 #45` **Saumya** *(True)* |
| **`113° 00'`** | **Karka** `23° 00'` | Chara (Direct) | `Slice #116` | **`Nadi #116`** | `#0566 / 1800` | **Manohara** *(Ashtama-Kala)* | `D60 #47` **Sheetala** *(True)* |
| **`114° 00'`** | **Karka** `24° 00'` | Chara (Direct) | `Slice #121` | **`Nadi #121`** | `#0571 / 1800` | **Vasudha** *(Navama-Kala)* | `D60 #49` **Chandramukhi** *(True)* |
| **`115° 00'`** | **Karka** `25° 00'` | Chara (Direct) | `Slice #126` | **`Nadi #126`** | `#0576 / 1800` | **Sudhakara** *(Navama-Kala)* | `D60 #51` **Kalapavaka** *(False)* |
| **`116° 00'`** | **Karka** `26° 00'` | Chara (Direct) | `Slice #131` | **`Nadi #131`** | `#0581 / 1800` | **Manohara** *(Navama-Kala)* | `D60 #53` **Nirmala** *(True)* |
| **`117° 00'`** | **Karka** `27° 00'` | Chara (Direct) | `Slice #136` | **`Nadi #136`** | `#0586 / 1800` | **Vasudha** *(Dashama-Kala)* | `D60 #55` **Krura** *(False)* |
| **`118° 00'`** | **Karka** `28° 00'` | Chara (Direct) | `Slice #141` | **`Nadi #141`** | `#0591 / 1800` | **Sudhakara** *(Dashama-Kala)* | `D60 #57` **Amrita** *(True)* |
| **`119° 00'`** | **Karka** `29° 00'` | Chara (Direct) | `Slice #146` | **`Nadi #146`** | `#0596 / 1800` | **Manohara** *(Dashama-Kala)* | `D60 #59` **Bhramana** *(False)* |
| **`120° 00'`** | **Simha** `00° 00'` | Sthira (Reverse) | `Slice #001` | **`Nadi #150`** | `#0750 / 1800` | **Kumbhini** *(Dashama-Kala)* | `D60 #01` **Ghora** *(False)* |
| **`121° 00'`** | **Simha** `01° 00'` | Sthira (Reverse) | `Slice #006` | **`Nadi #145`** | `#0745 / 1800` | **Maya** *(Dashama-Kala)* | `D60 #03` **Deva** *(True)* |
| **`122° 00'`** | **Simha** `02° 00'` | Sthira (Reverse) | `Slice #011` | **`Nadi #140`** | `#0740 / 1800` | **Shankari** *(Dashama-Kala)* | `D60 #05` **Yaksha** *(True)* |
| **`123° 00'`** | **Simha** `03° 00'` | Sthira (Reverse) | `Slice #016` | **`Nadi #135`** | `#0735 / 1800` | **Kumbhini** *(Navama-Kala)* | `D60 #07` **Bhrashta** *(False)* |
| **`124° 00'`** | **Simha** `04° 00'` | Sthira (Reverse) | `Slice #021` | **`Nadi #130`** | `#0730 / 1800` | **Maya** *(Navama-Kala)* | `D60 #09` **Garala** *(False)* |
| **`125° 00'`** | **Simha** `05° 00'` | Sthira (Reverse) | `Slice #026` | **`Nadi #125`** | `#0725 / 1800` | **Shankari** *(Navama-Kala)* | `D60 #11` **Maya** *(False)* |
| **`126° 00'`** | **Simha** `06° 00'` | Sthira (Reverse) | `Slice #031` | **`Nadi #120`** | `#0720 / 1800` | **Kumbhini** *(Ashtama-Kala)* | `D60 #13` **Apampati** *(True)* |
| **`127° 00'`** | **Simha** `07° 00'` | Sthira (Reverse) | `Slice #036` | **`Nadi #115`** | `#0715 / 1800` | **Maya** *(Ashtama-Kala)* | `D60 #15` **Kala** *(False)* |
| **`128° 00'`** | **Simha** `08° 00'` | Sthira (Reverse) | `Slice #041` | **`Nadi #110`** | `#0710 / 1800` | **Shankari** *(Ashtama-Kala)* | `D60 #17` **Amrita** *(True)* |
| **`129° 00'`** | **Simha** `09° 00'` | Sthira (Reverse) | `Slice #046` | **`Nadi #105`** | `#0705 / 1800` | **Kumbhini** *(Saptama-Kala)* | `D60 #19` **Mridu** *(True)* |
| **`130° 00'`** | **Simha** `10° 00'` | Sthira (Reverse) | `Slice #051` | **`Nadi #100`** | `#0700 / 1800` | **Maya** *(Saptama-Kala)* | `D60 #21` **Heramba** *(True)* |
| **`131° 00'`** | **Simha** `11° 00'` | Sthira (Reverse) | `Slice #056` | **`Nadi #095`** | `#0695 / 1800` | **Shankari** *(Saptama-Kala)* | `D60 #23` **Vishnu** *(True)* |
| **`132° 00'`** | **Simha** `12° 00'` | Sthira (Reverse) | `Slice #061` | **`Nadi #090`** | `#0690 / 1800` | **Kumbhini** *(Shashtha-Kala)* | `D60 #25` **Deva** *(True)* |
| **`133° 00'`** | **Simha** `13° 00'` | Sthira (Reverse) | `Slice #066` | **`Nadi #085`** | `#0685 / 1800` | **Maya** *(Shashtha-Kala)* | `D60 #27` **Kalinasa** *(True)* |
| **`134° 00'`** | **Simha** `14° 00'` | Sthira (Reverse) | `Slice #071` | **`Nadi #080`** | `#0680 / 1800` | **Shankari** *(Shashtha-Kala)* | `D60 #29` **Kamalakara** *(True)* |
| **`135° 00'`** | **Simha** `15° 00'` | Sthira (Reverse) | `Slice #076` | **`Nadi #075`** | `#0675 / 1800` | **Kumbhini** *(Panchama-Kala)* | `D60 #31` **Mrityu** *(False)* |
| **`136° 00'`** | **Simha** `16° 00'` | Sthira (Reverse) | `Slice #081` | **`Nadi #070`** | `#0670 / 1800` | **Maya** *(Panchama-Kala)* | `D60 #33` **Davagni** *(False)* |
| **`137° 00'`** | **Simha** `17° 00'` | Sthira (Reverse) | `Slice #086` | **`Nadi #065`** | `#0665 / 1800` | **Shankari** *(Panchama-Kala)* | `D60 #35` **Yama** *(False)* |
| **`138° 00'`** | **Simha** `18° 00'` | Sthira (Reverse) | `Slice #091` | **`Nadi #060`** | `#0660 / 1800` | **Kumbhini** *(Chaturtha-Kala)* | `D60 #37` **Sudha** *(True)* |
| **`139° 00'`** | **Simha** `19° 00'` | Sthira (Reverse) | `Slice #096` | **`Nadi #055`** | `#0655 / 1800` | **Maya** *(Chaturtha-Kala)* | `D60 #39` **Purnachandra** *(True)* |
| **`140° 00'`** | **Simha** `20° 00'` | Sthira (Reverse) | `Slice #101` | **`Nadi #050`** | `#0650 / 1800` | **Shankari** *(Chaturtha-Kala)* | `D60 #41` **Kulanasa** *(False)* |
| **`141° 00'`** | **Simha** `21° 00'` | Sthira (Reverse) | `Slice #106` | **`Nadi #045`** | `#0645 / 1800` | **Kumbhini** *(Tritiya-Kala)* | `D60 #43` **Utpata** *(False)* |
| **`142° 00'`** | **Simha** `22° 00'` | Sthira (Reverse) | `Slice #111` | **`Nadi #040`** | `#0640 / 1800` | **Maya** *(Tritiya-Kala)* | `D60 #45` **Saumya** *(True)* |
| **`143° 00'`** | **Simha** `23° 00'` | Sthira (Reverse) | `Slice #116` | **`Nadi #035`** | `#0635 / 1800` | **Shankari** *(Tritiya-Kala)* | `D60 #47` **Sheetala** *(True)* |
| **`144° 00'`** | **Simha** `24° 00'` | Sthira (Reverse) | `Slice #121` | **`Nadi #030`** | `#0630 / 1800` | **Kumbhini** *(Dvitiya-Kala)* | `D60 #49` **Chandramukhi** *(True)* |
| **`145° 00'`** | **Simha** `25° 00'` | Sthira (Reverse) | `Slice #126` | **`Nadi #025`** | `#0625 / 1800` | **Maya** *(Dvitiya-Kala)* | `D60 #51` **Kalapavaka** *(False)* |
| **`146° 00'`** | **Simha** `26° 00'` | Sthira (Reverse) | `Slice #131` | **`Nadi #020`** | `#0620 / 1800` | **Shankari** *(Dvitiya-Kala)* | `D60 #53` **Nirmala** *(True)* |
| **`147° 00'`** | **Simha** `27° 00'` | Sthira (Reverse) | `Slice #136` | **`Nadi #015`** | `#0615 / 1800` | **Kumbhini** *(Prathama-Kala)* | `D60 #55` **Krura** *(False)* |
| **`148° 00'`** | **Simha** `28° 00'` | Sthira (Reverse) | `Slice #141` | **`Nadi #010`** | `#0610 / 1800` | **Maya** *(Prathama-Kala)* | `D60 #57` **Amrita** *(True)* |
| **`149° 00'`** | **Simha** `29° 00'` | Sthira (Reverse) | `Slice #146` | **`Nadi #005`** | `#0605 / 1800` | **Shankari** *(Prathama-Kala)* | `D60 #59` **Bhramana** *(False)* |
| **`150° 00'`** | **Kanya** `00° 00'` | Dwiswabhava (Mid) | `Slice #001` | **`Nadi #076`** | `#0826 / 1800` | **Vasudha** *(Shashtha-Kala)* | `D60 #01` **Ghora** *(False)* |
| **`151° 00'`** | **Kanya** `01° 00'` | Dwiswabhava (Mid) | `Slice #006` | **`Nadi #081`** | `#0831 / 1800` | **Sudhakara** *(Shashtha-Kala)* | `D60 #03` **Deva** *(True)* |
| **`152° 00'`** | **Kanya** `02° 00'` | Dwiswabhava (Mid) | `Slice #011` | **`Nadi #086`** | `#0836 / 1800` | **Manohara** *(Shashtha-Kala)* | `D60 #05` **Yaksha** *(True)* |
| **`153° 00'`** | **Kanya** `03° 00'` | Dwiswabhava (Mid) | `Slice #016` | **`Nadi #091`** | `#0841 / 1800` | **Vasudha** *(Saptama-Kala)* | `D60 #07` **Bhrashta** *(False)* |
| **`154° 00'`** | **Kanya** `04° 00'` | Dwiswabhava (Mid) | `Slice #021` | **`Nadi #096`** | `#0846 / 1800` | **Sudhakara** *(Saptama-Kala)* | `D60 #09` **Garala** *(False)* |
| **`155° 00'`** | **Kanya** `05° 00'` | Dwiswabhava (Mid) | `Slice #026` | **`Nadi #101`** | `#0851 / 1800` | **Manohara** *(Saptama-Kala)* | `D60 #11` **Maya** *(False)* |
| **`156° 00'`** | **Kanya** `06° 00'` | Dwiswabhava (Mid) | `Slice #031` | **`Nadi #106`** | `#0856 / 1800` | **Vasudha** *(Ashtama-Kala)* | `D60 #13` **Apampati** *(True)* |
| **`157° 00'`** | **Kanya** `07° 00'` | Dwiswabhava (Mid) | `Slice #036` | **`Nadi #111`** | `#0861 / 1800` | **Sudhakara** *(Ashtama-Kala)* | `D60 #15` **Kala** *(False)* |
| **`158° 00'`** | **Kanya** `08° 00'` | Dwiswabhava (Mid) | `Slice #041` | **`Nadi #116`** | `#0866 / 1800` | **Manohara** *(Ashtama-Kala)* | `D60 #17` **Amrita** *(True)* |
| **`159° 00'`** | **Kanya** `09° 00'` | Dwiswabhava (Mid) | `Slice #046` | **`Nadi #121`** | `#0871 / 1800` | **Vasudha** *(Navama-Kala)* | `D60 #19` **Mridu** *(True)* |
| **`160° 00'`** | **Kanya** `10° 00'` | Dwiswabhava (Mid) | `Slice #051` | **`Nadi #126`** | `#0876 / 1800` | **Sudhakara** *(Navama-Kala)* | `D60 #21` **Heramba** *(True)* |
| **`161° 00'`** | **Kanya** `11° 00'` | Dwiswabhava (Mid) | `Slice #056` | **`Nadi #131`** | `#0881 / 1800` | **Manohara** *(Navama-Kala)* | `D60 #23` **Vishnu** *(True)* |
| **`162° 00'`** | **Kanya** `12° 00'` | Dwiswabhava (Mid) | `Slice #061` | **`Nadi #136`** | `#0886 / 1800` | **Vasudha** *(Dashama-Kala)* | `D60 #25` **Deva** *(True)* |
| **`163° 00'`** | **Kanya** `13° 00'` | Dwiswabhava (Mid) | `Slice #066` | **`Nadi #141`** | `#0891 / 1800` | **Sudhakara** *(Dashama-Kala)* | `D60 #27` **Kalinasa** *(True)* |
| **`164° 00'`** | **Kanya** `14° 00'` | Dwiswabhava (Mid) | `Slice #071` | **`Nadi #146`** | `#0896 / 1800` | **Manohara** *(Dashama-Kala)* | `D60 #29` **Kamalakara** *(True)* |
| **`165° 00'`** | **Kanya** `15° 00'` | Dwiswabhava (Mid) | `Slice #076` | **`Nadi #001`** | `#0751 / 1800` | **Vasudha** *(Prathama-Kala)* | `D60 #31` **Mrityu** *(False)* |
| **`166° 00'`** | **Kanya** `16° 00'` | Dwiswabhava (Mid) | `Slice #081` | **`Nadi #006`** | `#0756 / 1800` | **Sudhakara** *(Prathama-Kala)* | `D60 #33` **Davagni** *(False)* |
| **`167° 00'`** | **Kanya** `17° 00'` | Dwiswabhava (Mid) | `Slice #086` | **`Nadi #011`** | `#0761 / 1800` | **Manohara** *(Prathama-Kala)* | `D60 #35` **Yama** *(False)* |
| **`168° 00'`** | **Kanya** `18° 00'` | Dwiswabhava (Mid) | `Slice #091` | **`Nadi #016`** | `#0766 / 1800` | **Vasudha** *(Dvitiya-Kala)* | `D60 #37` **Sudha** *(True)* |
| **`169° 00'`** | **Kanya** `19° 00'` | Dwiswabhava (Mid) | `Slice #096` | **`Nadi #021`** | `#0771 / 1800` | **Sudhakara** *(Dvitiya-Kala)* | `D60 #39` **Purnachandra** *(True)* |
| **`170° 00'`** | **Kanya** `20° 00'` | Dwiswabhava (Mid) | `Slice #101` | **`Nadi #026`** | `#0776 / 1800` | **Manohara** *(Dvitiya-Kala)* | `D60 #41` **Kulanasa** *(False)* |
| **`171° 00'`** | **Kanya** `21° 00'` | Dwiswabhava (Mid) | `Slice #106` | **`Nadi #031`** | `#0781 / 1800` | **Vasudha** *(Tritiya-Kala)* | `D60 #43` **Utpata** *(False)* |
| **`172° 00'`** | **Kanya** `22° 00'` | Dwiswabhava (Mid) | `Slice #111` | **`Nadi #036`** | `#0786 / 1800` | **Sudhakara** *(Tritiya-Kala)* | `D60 #45` **Saumya** *(True)* |
| **`173° 00'`** | **Kanya** `23° 00'` | Dwiswabhava (Mid) | `Slice #116` | **`Nadi #041`** | `#0791 / 1800` | **Manohara** *(Tritiya-Kala)* | `D60 #47` **Sheetala** *(True)* |
| **`174° 00'`** | **Kanya** `24° 00'` | Dwiswabhava (Mid) | `Slice #121` | **`Nadi #046`** | `#0796 / 1800` | **Vasudha** *(Chaturtha-Kala)* | `D60 #49` **Chandramukhi** *(True)* |
| **`175° 00'`** | **Kanya** `25° 00'` | Dwiswabhava (Mid) | `Slice #126` | **`Nadi #051`** | `#0801 / 1800` | **Sudhakara** *(Chaturtha-Kala)* | `D60 #51` **Kalapavaka** *(False)* |
| **`176° 00'`** | **Kanya** `26° 00'` | Dwiswabhava (Mid) | `Slice #131` | **`Nadi #056`** | `#0806 / 1800` | **Manohara** *(Chaturtha-Kala)* | `D60 #53` **Nirmala** *(True)* |
| **`177° 00'`** | **Kanya** `27° 00'` | Dwiswabhava (Mid) | `Slice #136` | **`Nadi #061`** | `#0811 / 1800` | **Vasudha** *(Panchama-Kala)* | `D60 #55` **Krura** *(False)* |
| **`178° 00'`** | **Kanya** `28° 00'` | Dwiswabhava (Mid) | `Slice #141` | **`Nadi #066`** | `#0816 / 1800` | **Sudhakara** *(Panchama-Kala)* | `D60 #57` **Amrita** *(True)* |
| **`179° 00'`** | **Kanya** `29° 00'` | Dwiswabhava (Mid) | `Slice #146` | **`Nadi #071`** | `#0821 / 1800` | **Manohara** *(Panchama-Kala)* | `D60 #59` **Bhramana** *(False)* |
| **`180° 00'`** | **Tula** `00° 00'` | Chara (Direct) | `Slice #001` | **`Nadi #001`** | `#0901 / 1800` | **Vasudha** *(Prathama-Kala)* | `D60 #01` **Ghora** *(False)* |
| **`181° 00'`** | **Tula** `01° 00'` | Chara (Direct) | `Slice #006` | **`Nadi #006`** | `#0906 / 1800` | **Sudhakara** *(Prathama-Kala)* | `D60 #03` **Deva** *(True)* |
| **`182° 00'`** | **Tula** `02° 00'` | Chara (Direct) | `Slice #011` | **`Nadi #011`** | `#0911 / 1800` | **Manohara** *(Prathama-Kala)* | `D60 #05` **Yaksha** *(True)* |
| **`183° 00'`** | **Tula** `03° 00'` | Chara (Direct) | `Slice #016` | **`Nadi #016`** | `#0916 / 1800` | **Vasudha** *(Dvitiya-Kala)* | `D60 #07` **Bhrashta** *(False)* |
| **`184° 00'`** | **Tula** `04° 00'` | Chara (Direct) | `Slice #021` | **`Nadi #021`** | `#0921 / 1800` | **Sudhakara** *(Dvitiya-Kala)* | `D60 #09` **Garala** *(False)* |
| **`185° 00'`** | **Tula** `05° 00'` | Chara (Direct) | `Slice #026` | **`Nadi #026`** | `#0926 / 1800` | **Manohara** *(Dvitiya-Kala)* | `D60 #11` **Maya** *(False)* |
| **`186° 00'`** | **Tula** `06° 00'` | Chara (Direct) | `Slice #031` | **`Nadi #031`** | `#0931 / 1800` | **Vasudha** *(Tritiya-Kala)* | `D60 #13` **Apampati** *(True)* |
| **`187° 00'`** | **Tula** `07° 00'` | Chara (Direct) | `Slice #036` | **`Nadi #036`** | `#0936 / 1800` | **Sudhakara** *(Tritiya-Kala)* | `D60 #15` **Kala** *(False)* |
| **`188° 00'`** | **Tula** `08° 00'` | Chara (Direct) | `Slice #041` | **`Nadi #041`** | `#0941 / 1800` | **Manohara** *(Tritiya-Kala)* | `D60 #17` **Amrita** *(True)* |
| **`189° 00'`** | **Tula** `09° 00'` | Chara (Direct) | `Slice #046` | **`Nadi #046`** | `#0946 / 1800` | **Vasudha** *(Chaturtha-Kala)* | `D60 #19` **Mridu** *(True)* |
| **`190° 00'`** | **Tula** `10° 00'` | Chara (Direct) | `Slice #051` | **`Nadi #051`** | `#0951 / 1800` | **Sudhakara** *(Chaturtha-Kala)* | `D60 #21` **Heramba** *(True)* |
| **`191° 00'`** | **Tula** `11° 00'` | Chara (Direct) | `Slice #056` | **`Nadi #056`** | `#0956 / 1800` | **Manohara** *(Chaturtha-Kala)* | `D60 #23` **Vishnu** *(True)* |
| **`192° 00'`** | **Tula** `12° 00'` | Chara (Direct) | `Slice #061` | **`Nadi #061`** | `#0961 / 1800` | **Vasudha** *(Panchama-Kala)* | `D60 #25` **Deva** *(True)* |
| **`193° 00'`** | **Tula** `13° 00'` | Chara (Direct) | `Slice #066` | **`Nadi #066`** | `#0966 / 1800` | **Sudhakara** *(Panchama-Kala)* | `D60 #27` **Kalinasa** *(True)* |
| **`194° 00'`** | **Tula** `14° 00'` | Chara (Direct) | `Slice #071` | **`Nadi #071`** | `#0971 / 1800` | **Manohara** *(Panchama-Kala)* | `D60 #29` **Kamalakara** *(True)* |
| **`195° 00'`** | **Tula** `15° 00'` | Chara (Direct) | `Slice #076` | **`Nadi #076`** | `#0976 / 1800` | **Vasudha** *(Shashtha-Kala)* | `D60 #31` **Mrityu** *(False)* |
| **`196° 00'`** | **Tula** `16° 00'` | Chara (Direct) | `Slice #081` | **`Nadi #081`** | `#0981 / 1800` | **Sudhakara** *(Shashtha-Kala)* | `D60 #33` **Davagni** *(False)* |
| **`197° 00'`** | **Tula** `17° 00'` | Chara (Direct) | `Slice #086` | **`Nadi #086`** | `#0986 / 1800` | **Manohara** *(Shashtha-Kala)* | `D60 #35` **Yama** *(False)* |
| **`198° 00'`** | **Tula** `18° 00'` | Chara (Direct) | `Slice #091` | **`Nadi #091`** | `#0991 / 1800` | **Vasudha** *(Saptama-Kala)* | `D60 #37` **Sudha** *(True)* |
| **`199° 00'`** | **Tula** `19° 00'` | Chara (Direct) | `Slice #096` | **`Nadi #096`** | `#0996 / 1800` | **Sudhakara** *(Saptama-Kala)* | `D60 #39` **Purnachandra** *(True)* |
| **`200° 00'`** | **Tula** `20° 00'` | Chara (Direct) | `Slice #101` | **`Nadi #101`** | `#1001 / 1800` | **Manohara** *(Saptama-Kala)* | `D60 #41` **Kulanasa** *(False)* |
| **`201° 00'`** | **Tula** `21° 00'` | Chara (Direct) | `Slice #106` | **`Nadi #106`** | `#1006 / 1800` | **Vasudha** *(Ashtama-Kala)* | `D60 #43` **Utpata** *(False)* |
| **`202° 00'`** | **Tula** `22° 00'` | Chara (Direct) | `Slice #111` | **`Nadi #111`** | `#1011 / 1800` | **Sudhakara** *(Ashtama-Kala)* | `D60 #45` **Saumya** *(True)* |
| **`203° 00'`** | **Tula** `23° 00'` | Chara (Direct) | `Slice #116` | **`Nadi #116`** | `#1016 / 1800` | **Manohara** *(Ashtama-Kala)* | `D60 #47` **Sheetala** *(True)* |
| **`204° 00'`** | **Tula** `24° 00'` | Chara (Direct) | `Slice #121` | **`Nadi #121`** | `#1021 / 1800` | **Vasudha** *(Navama-Kala)* | `D60 #49` **Chandramukhi** *(True)* |
| **`205° 00'`** | **Tula** `25° 00'` | Chara (Direct) | `Slice #126` | **`Nadi #126`** | `#1026 / 1800` | **Sudhakara** *(Navama-Kala)* | `D60 #51` **Kalapavaka** *(False)* |
| **`206° 00'`** | **Tula** `26° 00'` | Chara (Direct) | `Slice #131` | **`Nadi #131`** | `#1031 / 1800` | **Manohara** *(Navama-Kala)* | `D60 #53` **Nirmala** *(True)* |
| **`207° 00'`** | **Tula** `27° 00'` | Chara (Direct) | `Slice #136` | **`Nadi #136`** | `#1036 / 1800` | **Vasudha** *(Dashama-Kala)* | `D60 #55` **Krura** *(False)* |
| **`208° 00'`** | **Tula** `28° 00'` | Chara (Direct) | `Slice #141` | **`Nadi #141`** | `#1041 / 1800` | **Sudhakara** *(Dashama-Kala)* | `D60 #57` **Amrita** *(True)* |
| **`209° 00'`** | **Tula** `29° 00'` | Chara (Direct) | `Slice #146` | **`Nadi #146`** | `#1046 / 1800` | **Manohara** *(Dashama-Kala)* | `D60 #59` **Bhramana** *(False)* |
| **`210° 00'`** | **Vrishchika** `00° 00'` | Sthira (Reverse) | `Slice #001` | **`Nadi #150`** | `#1200 / 1800` | **Kumbhini** *(Dashama-Kala)* | `D60 #01` **Ghora** *(False)* |
| **`211° 00'`** | **Vrishchika** `01° 00'` | Sthira (Reverse) | `Slice #006` | **`Nadi #145`** | `#1195 / 1800` | **Maya** *(Dashama-Kala)* | `D60 #03` **Deva** *(True)* |
| **`212° 00'`** | **Vrishchika** `02° 00'` | Sthira (Reverse) | `Slice #011` | **`Nadi #140`** | `#1190 / 1800` | **Shankari** *(Dashama-Kala)* | `D60 #05` **Yaksha** *(True)* |
| **`213° 00'`** | **Vrishchika** `03° 00'` | Sthira (Reverse) | `Slice #016` | **`Nadi #135`** | `#1185 / 1800` | **Kumbhini** *(Navama-Kala)* | `D60 #07` **Bhrashta** *(False)* |
| **`214° 00'`** | **Vrishchika** `04° 00'` | Sthira (Reverse) | `Slice #021` | **`Nadi #130`** | `#1180 / 1800` | **Maya** *(Navama-Kala)* | `D60 #09` **Garala** *(False)* |
| **`215° 00'`** | **Vrishchika** `05° 00'` | Sthira (Reverse) | `Slice #026` | **`Nadi #125`** | `#1175 / 1800` | **Shankari** *(Navama-Kala)* | `D60 #11` **Maya** *(False)* |
| **`216° 00'`** | **Vrishchika** `06° 00'` | Sthira (Reverse) | `Slice #031` | **`Nadi #120`** | `#1170 / 1800` | **Kumbhini** *(Ashtama-Kala)* | `D60 #13` **Apampati** *(True)* |
| **`217° 00'`** | **Vrishchika** `07° 00'` | Sthira (Reverse) | `Slice #036` | **`Nadi #115`** | `#1165 / 1800` | **Maya** *(Ashtama-Kala)* | `D60 #15` **Kala** *(False)* |
| **`218° 00'`** | **Vrishchika** `08° 00'` | Sthira (Reverse) | `Slice #041` | **`Nadi #110`** | `#1160 / 1800` | **Shankari** *(Ashtama-Kala)* | `D60 #17` **Amrita** *(True)* |
| **`219° 00'`** | **Vrishchika** `09° 00'` | Sthira (Reverse) | `Slice #046` | **`Nadi #105`** | `#1155 / 1800` | **Kumbhini** *(Saptama-Kala)* | `D60 #19` **Mridu** *(True)* |
| **`220° 00'`** | **Vrishchika** `10° 00'` | Sthira (Reverse) | `Slice #051` | **`Nadi #100`** | `#1150 / 1800` | **Maya** *(Saptama-Kala)* | `D60 #21` **Heramba** *(True)* |
| **`221° 00'`** | **Vrishchika** `11° 00'` | Sthira (Reverse) | `Slice #056` | **`Nadi #095`** | `#1145 / 1800` | **Shankari** *(Saptama-Kala)* | `D60 #23` **Vishnu** *(True)* |
| **`222° 00'`** | **Vrishchika** `12° 00'` | Sthira (Reverse) | `Slice #061` | **`Nadi #090`** | `#1140 / 1800` | **Kumbhini** *(Shashtha-Kala)* | `D60 #25` **Deva** *(True)* |
| **`223° 00'`** | **Vrishchika** `13° 00'` | Sthira (Reverse) | `Slice #066` | **`Nadi #085`** | `#1135 / 1800` | **Maya** *(Shashtha-Kala)* | `D60 #27` **Kalinasa** *(True)* |
| **`224° 00'`** | **Vrishchika** `14° 00'` | Sthira (Reverse) | `Slice #071` | **`Nadi #080`** | `#1130 / 1800` | **Shankari** *(Shashtha-Kala)* | `D60 #29` **Kamalakara** *(True)* |
| **`225° 00'`** | **Vrishchika** `15° 00'` | Sthira (Reverse) | `Slice #076` | **`Nadi #075`** | `#1125 / 1800` | **Kumbhini** *(Panchama-Kala)* | `D60 #31` **Mrityu** *(False)* |
| **`226° 00'`** | **Vrishchika** `16° 00'` | Sthira (Reverse) | `Slice #081` | **`Nadi #070`** | `#1120 / 1800` | **Maya** *(Panchama-Kala)* | `D60 #33` **Davagni** *(False)* |
| **`227° 00'`** | **Vrishchika** `17° 00'` | Sthira (Reverse) | `Slice #086` | **`Nadi #065`** | `#1115 / 1800` | **Shankari** *(Panchama-Kala)* | `D60 #35` **Yama** *(False)* |
| **`228° 00'`** | **Vrishchika** `18° 00'` | Sthira (Reverse) | `Slice #091` | **`Nadi #060`** | `#1110 / 1800` | **Kumbhini** *(Chaturtha-Kala)* | `D60 #37` **Sudha** *(True)* |
| **`229° 00'`** | **Vrishchika** `19° 00'` | Sthira (Reverse) | `Slice #096` | **`Nadi #055`** | `#1105 / 1800` | **Maya** *(Chaturtha-Kala)* | `D60 #39` **Purnachandra** *(True)* |
| **`230° 00'`** | **Vrishchika** `20° 00'` | Sthira (Reverse) | `Slice #101` | **`Nadi #050`** | `#1100 / 1800` | **Shankari** *(Chaturtha-Kala)* | `D60 #41` **Kulanasa** *(False)* |
| **`231° 00'`** | **Vrishchika** `21° 00'` | Sthira (Reverse) | `Slice #106` | **`Nadi #045`** | `#1095 / 1800` | **Kumbhini** *(Tritiya-Kala)* | `D60 #43` **Utpata** *(False)* |
| **`232° 00'`** | **Vrishchika** `22° 00'` | Sthira (Reverse) | `Slice #111` | **`Nadi #040`** | `#1090 / 1800` | **Maya** *(Tritiya-Kala)* | `D60 #45` **Saumya** *(True)* |
| **`233° 00'`** | **Vrishchika** `23° 00'` | Sthira (Reverse) | `Slice #116` | **`Nadi #035`** | `#1085 / 1800` | **Shankari** *(Tritiya-Kala)* | `D60 #47` **Sheetala** *(True)* |
| **`234° 00'`** | **Vrishchika** `24° 00'` | Sthira (Reverse) | `Slice #121` | **`Nadi #030`** | `#1080 / 1800` | **Kumbhini** *(Dvitiya-Kala)* | `D60 #49` **Chandramukhi** *(True)* |
| **`235° 00'`** | **Vrishchika** `25° 00'` | Sthira (Reverse) | `Slice #126` | **`Nadi #025`** | `#1075 / 1800` | **Maya** *(Dvitiya-Kala)* | `D60 #51` **Kalapavaka** *(False)* |
| **`236° 00'`** | **Vrishchika** `26° 00'` | Sthira (Reverse) | `Slice #131` | **`Nadi #020`** | `#1070 / 1800` | **Shankari** *(Dvitiya-Kala)* | `D60 #53` **Nirmala** *(True)* |
| **`237° 00'`** | **Vrishchika** `27° 00'` | Sthira (Reverse) | `Slice #136` | **`Nadi #015`** | `#1065 / 1800` | **Kumbhini** *(Prathama-Kala)* | `D60 #55` **Krura** *(False)* |
| **`238° 00'`** | **Vrishchika** `28° 00'` | Sthira (Reverse) | `Slice #141` | **`Nadi #010`** | `#1060 / 1800` | **Maya** *(Prathama-Kala)* | `D60 #57` **Amrita** *(True)* |
| **`239° 00'`** | **Vrishchika** `29° 00'` | Sthira (Reverse) | `Slice #146` | **`Nadi #005`** | `#1055 / 1800` | **Shankari** *(Prathama-Kala)* | `D60 #59` **Bhramana** *(False)* |
| **`240° 00'`** | **Dhanu** `00° 00'` | Dwiswabhava (Mid) | `Slice #001` | **`Nadi #076`** | `#1276 / 1800` | **Vasudha** *(Shashtha-Kala)* | `D60 #01` **Ghora** *(False)* |
| **`241° 00'`** | **Dhanu** `01° 00'` | Dwiswabhava (Mid) | `Slice #006` | **`Nadi #081`** | `#1281 / 1800` | **Sudhakara** *(Shashtha-Kala)* | `D60 #03` **Deva** *(True)* |
| **`242° 00'`** | **Dhanu** `02° 00'` | Dwiswabhava (Mid) | `Slice #011` | **`Nadi #086`** | `#1286 / 1800` | **Manohara** *(Shashtha-Kala)* | `D60 #05` **Yaksha** *(True)* |
| **`243° 00'`** | **Dhanu** `03° 00'` | Dwiswabhava (Mid) | `Slice #016` | **`Nadi #091`** | `#1291 / 1800` | **Vasudha** *(Saptama-Kala)* | `D60 #07` **Bhrashta** *(False)* |
| **`244° 00'`** | **Dhanu** `04° 00'` | Dwiswabhava (Mid) | `Slice #021` | **`Nadi #096`** | `#1296 / 1800` | **Sudhakara** *(Saptama-Kala)* | `D60 #09` **Garala** *(False)* |
| **`245° 00'`** | **Dhanu** `05° 00'` | Dwiswabhava (Mid) | `Slice #026` | **`Nadi #101`** | `#1301 / 1800` | **Manohara** *(Saptama-Kala)* | `D60 #11` **Maya** *(False)* |
| **`246° 00'`** | **Dhanu** `06° 00'` | Dwiswabhava (Mid) | `Slice #031` | **`Nadi #106`** | `#1306 / 1800` | **Vasudha** *(Ashtama-Kala)* | `D60 #13` **Apampati** *(True)* |
| **`247° 00'`** | **Dhanu** `07° 00'` | Dwiswabhava (Mid) | `Slice #036` | **`Nadi #111`** | `#1311 / 1800` | **Sudhakara** *(Ashtama-Kala)* | `D60 #15` **Kala** *(False)* |
| **`248° 00'`** | **Dhanu** `08° 00'` | Dwiswabhava (Mid) | `Slice #041` | **`Nadi #116`** | `#1316 / 1800` | **Manohara** *(Ashtama-Kala)* | `D60 #17` **Amrita** *(True)* |
| **`249° 00'`** | **Dhanu** `09° 00'` | Dwiswabhava (Mid) | `Slice #046` | **`Nadi #121`** | `#1321 / 1800` | **Vasudha** *(Navama-Kala)* | `D60 #19` **Mridu** *(True)* |
| **`250° 00'`** | **Dhanu** `10° 00'` | Dwiswabhava (Mid) | `Slice #051` | **`Nadi #126`** | `#1326 / 1800` | **Sudhakara** *(Navama-Kala)* | `D60 #21` **Heramba** *(True)* |
| **`251° 00'`** | **Dhanu** `11° 00'` | Dwiswabhava (Mid) | `Slice #056` | **`Nadi #131`** | `#1331 / 1800` | **Manohara** *(Navama-Kala)* | `D60 #23` **Vishnu** *(True)* |
| **`252° 00'`** | **Dhanu** `12° 00'` | Dwiswabhava (Mid) | `Slice #061` | **`Nadi #136`** | `#1336 / 1800` | **Vasudha** *(Dashama-Kala)* | `D60 #25` **Deva** *(True)* |
| **`253° 00'`** | **Dhanu** `13° 00'` | Dwiswabhava (Mid) | `Slice #066` | **`Nadi #141`** | `#1341 / 1800` | **Sudhakara** *(Dashama-Kala)* | `D60 #27` **Kalinasa** *(True)* |
| **`254° 00'`** | **Dhanu** `14° 00'` | Dwiswabhava (Mid) | `Slice #071` | **`Nadi #146`** | `#1346 / 1800` | **Manohara** *(Dashama-Kala)* | `D60 #29` **Kamalakara** *(True)* |
| **`255° 00'`** | **Dhanu** `15° 00'` | Dwiswabhava (Mid) | `Slice #076` | **`Nadi #001`** | `#1201 / 1800` | **Vasudha** *(Prathama-Kala)* | `D60 #31` **Mrityu** *(False)* |
| **`256° 00'`** | **Dhanu** `16° 00'` | Dwiswabhava (Mid) | `Slice #081` | **`Nadi #006`** | `#1206 / 1800` | **Sudhakara** *(Prathama-Kala)* | `D60 #33` **Davagni** *(False)* |
| **`257° 00'`** | **Dhanu** `17° 00'` | Dwiswabhava (Mid) | `Slice #086` | **`Nadi #011`** | `#1211 / 1800` | **Manohara** *(Prathama-Kala)* | `D60 #35` **Yama** *(False)* |
| **`258° 00'`** | **Dhanu** `18° 00'` | Dwiswabhava (Mid) | `Slice #091` | **`Nadi #016`** | `#1216 / 1800` | **Vasudha** *(Dvitiya-Kala)* | `D60 #37` **Sudha** *(True)* |
| **`259° 00'`** | **Dhanu** `19° 00'` | Dwiswabhava (Mid) | `Slice #096` | **`Nadi #021`** | `#1221 / 1800` | **Sudhakara** *(Dvitiya-Kala)* | `D60 #39` **Purnachandra** *(True)* |
| **`260° 00'`** | **Dhanu** `20° 00'` | Dwiswabhava (Mid) | `Slice #101` | **`Nadi #026`** | `#1226 / 1800` | **Manohara** *(Dvitiya-Kala)* | `D60 #41` **Kulanasa** *(False)* |
| **`261° 00'`** | **Dhanu** `21° 00'` | Dwiswabhava (Mid) | `Slice #106` | **`Nadi #031`** | `#1231 / 1800` | **Vasudha** *(Tritiya-Kala)* | `D60 #43` **Utpata** *(False)* |
| **`262° 00'`** | **Dhanu** `22° 00'` | Dwiswabhava (Mid) | `Slice #111` | **`Nadi #036`** | `#1236 / 1800` | **Sudhakara** *(Tritiya-Kala)* | `D60 #45` **Saumya** *(True)* |
| **`263° 00'`** | **Dhanu** `23° 00'` | Dwiswabhava (Mid) | `Slice #116` | **`Nadi #041`** | `#1241 / 1800` | **Manohara** *(Tritiya-Kala)* | `D60 #47` **Sheetala** *(True)* |
| **`264° 00'`** | **Dhanu** `24° 00'` | Dwiswabhava (Mid) | `Slice #121` | **`Nadi #046`** | `#1246 / 1800` | **Vasudha** *(Chaturtha-Kala)* | `D60 #49` **Chandramukhi** *(True)* |
| **`265° 00'`** | **Dhanu** `25° 00'` | Dwiswabhava (Mid) | `Slice #126` | **`Nadi #051`** | `#1251 / 1800` | **Sudhakara** *(Chaturtha-Kala)* | `D60 #51` **Kalapavaka** *(False)* |
| **`266° 00'`** | **Dhanu** `26° 00'` | Dwiswabhava (Mid) | `Slice #131` | **`Nadi #056`** | `#1256 / 1800` | **Manohara** *(Chaturtha-Kala)* | `D60 #53` **Nirmala** *(True)* |
| **`267° 00'`** | **Dhanu** `27° 00'` | Dwiswabhava (Mid) | `Slice #136` | **`Nadi #061`** | `#1261 / 1800` | **Vasudha** *(Panchama-Kala)* | `D60 #55` **Krura** *(False)* |
| **`268° 00'`** | **Dhanu** `28° 00'` | Dwiswabhava (Mid) | `Slice #141` | **`Nadi #066`** | `#1266 / 1800` | **Sudhakara** *(Panchama-Kala)* | `D60 #57` **Amrita** *(True)* |
| **`269° 00'`** | **Dhanu** `29° 00'` | Dwiswabhava (Mid) | `Slice #146` | **`Nadi #071`** | `#1271 / 1800` | **Manohara** *(Panchama-Kala)* | `D60 #59` **Bhramana** *(False)* |
| **`270° 00'`** | **Makara** `00° 00'` | Chara (Direct) | `Slice #001` | **`Nadi #001`** | `#1351 / 1800` | **Vasudha** *(Prathama-Kala)* | `D60 #01` **Ghora** *(False)* |
| **`271° 00'`** | **Makara** `01° 00'` | Chara (Direct) | `Slice #006` | **`Nadi #006`** | `#1356 / 1800` | **Sudhakara** *(Prathama-Kala)* | `D60 #03` **Deva** *(True)* |
| **`272° 00'`** | **Makara** `02° 00'` | Chara (Direct) | `Slice #011` | **`Nadi #011`** | `#1361 / 1800` | **Manohara** *(Prathama-Kala)* | `D60 #05` **Yaksha** *(True)* |
| **`273° 00'`** | **Makara** `03° 00'` | Chara (Direct) | `Slice #016` | **`Nadi #016`** | `#1366 / 1800` | **Vasudha** *(Dvitiya-Kala)* | `D60 #07` **Bhrashta** *(False)* |
| **`274° 00'`** | **Makara** `04° 00'` | Chara (Direct) | `Slice #021` | **`Nadi #021`** | `#1371 / 1800` | **Sudhakara** *(Dvitiya-Kala)* | `D60 #09` **Garala** *(False)* |
| **`275° 00'`** | **Makara** `05° 00'` | Chara (Direct) | `Slice #026` | **`Nadi #026`** | `#1376 / 1800` | **Manohara** *(Dvitiya-Kala)* | `D60 #11` **Maya** *(False)* |
| **`276° 00'`** | **Makara** `06° 00'` | Chara (Direct) | `Slice #031` | **`Nadi #031`** | `#1381 / 1800` | **Vasudha** *(Tritiya-Kala)* | `D60 #13` **Apampati** *(True)* |
| **`277° 00'`** | **Makara** `07° 00'` | Chara (Direct) | `Slice #036` | **`Nadi #036`** | `#1386 / 1800` | **Sudhakara** *(Tritiya-Kala)* | `D60 #15` **Kala** *(False)* |
| **`278° 00'`** | **Makara** `08° 00'` | Chara (Direct) | `Slice #041` | **`Nadi #041`** | `#1391 / 1800` | **Manohara** *(Tritiya-Kala)* | `D60 #17` **Amrita** *(True)* |
| **`279° 00'`** | **Makara** `09° 00'` | Chara (Direct) | `Slice #046` | **`Nadi #046`** | `#1396 / 1800` | **Vasudha** *(Chaturtha-Kala)* | `D60 #19` **Mridu** *(True)* |
| **`280° 00'`** | **Makara** `10° 00'` | Chara (Direct) | `Slice #051` | **`Nadi #051`** | `#1401 / 1800` | **Sudhakara** *(Chaturtha-Kala)* | `D60 #21` **Heramba** *(True)* |
| **`281° 00'`** | **Makara** `11° 00'` | Chara (Direct) | `Slice #056` | **`Nadi #056`** | `#1406 / 1800` | **Manohara** *(Chaturtha-Kala)* | `D60 #23` **Vishnu** *(True)* |
| **`282° 00'`** | **Makara** `12° 00'` | Chara (Direct) | `Slice #061` | **`Nadi #061`** | `#1411 / 1800` | **Vasudha** *(Panchama-Kala)* | `D60 #25` **Deva** *(True)* |
| **`283° 00'`** | **Makara** `13° 00'` | Chara (Direct) | `Slice #066` | **`Nadi #066`** | `#1416 / 1800` | **Sudhakara** *(Panchama-Kala)* | `D60 #27` **Kalinasa** *(True)* |
| **`284° 00'`** | **Makara** `14° 00'` | Chara (Direct) | `Slice #071` | **`Nadi #071`** | `#1421 / 1800` | **Manohara** *(Panchama-Kala)* | `D60 #29` **Kamalakara** *(True)* |
| **`285° 00'`** | **Makara** `15° 00'` | Chara (Direct) | `Slice #076` | **`Nadi #076`** | `#1426 / 1800` | **Vasudha** *(Shashtha-Kala)* | `D60 #31` **Mrityu** *(False)* |
| **`286° 00'`** | **Makara** `16° 00'` | Chara (Direct) | `Slice #081` | **`Nadi #081`** | `#1431 / 1800` | **Sudhakara** *(Shashtha-Kala)* | `D60 #33` **Davagni** *(False)* |
| **`287° 00'`** | **Makara** `17° 00'` | Chara (Direct) | `Slice #086` | **`Nadi #086`** | `#1436 / 1800` | **Manohara** *(Shashtha-Kala)* | `D60 #35` **Yama** *(False)* |
| **`288° 00'`** | **Makara** `18° 00'` | Chara (Direct) | `Slice #091` | **`Nadi #091`** | `#1441 / 1800` | **Vasudha** *(Saptama-Kala)* | `D60 #37` **Sudha** *(True)* |
| **`289° 00'`** | **Makara** `19° 00'` | Chara (Direct) | `Slice #096` | **`Nadi #096`** | `#1446 / 1800` | **Sudhakara** *(Saptama-Kala)* | `D60 #39` **Purnachandra** *(True)* |
| **`290° 00'`** | **Makara** `20° 00'` | Chara (Direct) | `Slice #101` | **`Nadi #101`** | `#1451 / 1800` | **Manohara** *(Saptama-Kala)* | `D60 #41` **Kulanasa** *(False)* |
| **`291° 00'`** | **Makara** `21° 00'` | Chara (Direct) | `Slice #106` | **`Nadi #106`** | `#1456 / 1800` | **Vasudha** *(Ashtama-Kala)* | `D60 #43` **Utpata** *(False)* |
| **`292° 00'`** | **Makara** `22° 00'` | Chara (Direct) | `Slice #111` | **`Nadi #111`** | `#1461 / 1800` | **Sudhakara** *(Ashtama-Kala)* | `D60 #45` **Saumya** *(True)* |
| **`293° 00'`** | **Makara** `23° 00'` | Chara (Direct) | `Slice #116` | **`Nadi #116`** | `#1466 / 1800` | **Manohara** *(Ashtama-Kala)* | `D60 #47` **Sheetala** *(True)* |
| **`294° 00'`** | **Makara** `24° 00'` | Chara (Direct) | `Slice #121` | **`Nadi #121`** | `#1471 / 1800` | **Vasudha** *(Navama-Kala)* | `D60 #49` **Chandramukhi** *(True)* |
| **`295° 00'`** | **Makara** `25° 00'` | Chara (Direct) | `Slice #126` | **`Nadi #126`** | `#1476 / 1800` | **Sudhakara** *(Navama-Kala)* | `D60 #51` **Kalapavaka** *(False)* |
| **`296° 00'`** | **Makara** `26° 00'` | Chara (Direct) | `Slice #131` | **`Nadi #131`** | `#1481 / 1800` | **Manohara** *(Navama-Kala)* | `D60 #53` **Nirmala** *(True)* |
| **`297° 00'`** | **Makara** `27° 00'` | Chara (Direct) | `Slice #136` | **`Nadi #136`** | `#1486 / 1800` | **Vasudha** *(Dashama-Kala)* | `D60 #55` **Krura** *(False)* |
| **`298° 00'`** | **Makara** `28° 00'` | Chara (Direct) | `Slice #141` | **`Nadi #141`** | `#1491 / 1800` | **Sudhakara** *(Dashama-Kala)* | `D60 #57` **Amrita** *(True)* |
| **`299° 00'`** | **Makara** `29° 00'` | Chara (Direct) | `Slice #146` | **`Nadi #146`** | `#1496 / 1800` | **Manohara** *(Dashama-Kala)* | `D60 #59` **Bhramana** *(False)* |
| **`300° 00'`** | **Kumbha** `00° 00'` | Sthira (Reverse) | `Slice #001` | **`Nadi #150`** | `#1650 / 1800` | **Kumbhini** *(Dashama-Kala)* | `D60 #01` **Ghora** *(False)* |
| **`301° 00'`** | **Kumbha** `01° 00'` | Sthira (Reverse) | `Slice #006` | **`Nadi #145`** | `#1645 / 1800` | **Maya** *(Dashama-Kala)* | `D60 #03` **Deva** *(True)* |
| **`302° 00'`** | **Kumbha** `02° 00'` | Sthira (Reverse) | `Slice #011` | **`Nadi #140`** | `#1640 / 1800` | **Shankari** *(Dashama-Kala)* | `D60 #05` **Yaksha** *(True)* |
| **`303° 00'`** | **Kumbha** `03° 00'` | Sthira (Reverse) | `Slice #016` | **`Nadi #135`** | `#1635 / 1800` | **Kumbhini** *(Navama-Kala)* | `D60 #07` **Bhrashta** *(False)* |
| **`304° 00'`** | **Kumbha** `04° 00'` | Sthira (Reverse) | `Slice #021` | **`Nadi #130`** | `#1630 / 1800` | **Maya** *(Navama-Kala)* | `D60 #09` **Garala** *(False)* |
| **`305° 00'`** | **Kumbha** `05° 00'` | Sthira (Reverse) | `Slice #026` | **`Nadi #125`** | `#1625 / 1800` | **Shankari** *(Navama-Kala)* | `D60 #11` **Maya** *(False)* |
| **`306° 00'`** | **Kumbha** `06° 00'` | Sthira (Reverse) | `Slice #031` | **`Nadi #120`** | `#1620 / 1800` | **Kumbhini** *(Ashtama-Kala)* | `D60 #13` **Apampati** *(True)* |
| **`307° 00'`** | **Kumbha** `07° 00'` | Sthira (Reverse) | `Slice #036` | **`Nadi #115`** | `#1615 / 1800` | **Maya** *(Ashtama-Kala)* | `D60 #15` **Kala** *(False)* |
| **`308° 00'`** | **Kumbha** `08° 00'` | Sthira (Reverse) | `Slice #041` | **`Nadi #110`** | `#1610 / 1800` | **Shankari** *(Ashtama-Kala)* | `D60 #17` **Amrita** *(True)* |
| **`309° 00'`** | **Kumbha** `09° 00'` | Sthira (Reverse) | `Slice #046` | **`Nadi #105`** | `#1605 / 1800` | **Kumbhini** *(Saptama-Kala)* | `D60 #19` **Mridu** *(True)* |
| **`310° 00'`** | **Kumbha** `10° 00'` | Sthira (Reverse) | `Slice #051` | **`Nadi #100`** | `#1600 / 1800` | **Maya** *(Saptama-Kala)* | `D60 #21` **Heramba** *(True)* |
| **`311° 00'`** | **Kumbha** `11° 00'` | Sthira (Reverse) | `Slice #056` | **`Nadi #095`** | `#1595 / 1800` | **Shankari** *(Saptama-Kala)* | `D60 #23` **Vishnu** *(True)* |
| **`312° 00'`** | **Kumbha** `12° 00'` | Sthira (Reverse) | `Slice #061` | **`Nadi #090`** | `#1590 / 1800` | **Kumbhini** *(Shashtha-Kala)* | `D60 #25` **Deva** *(True)* |
| **`313° 00'`** | **Kumbha** `13° 00'` | Sthira (Reverse) | `Slice #066` | **`Nadi #085`** | `#1585 / 1800` | **Maya** *(Shashtha-Kala)* | `D60 #27` **Kalinasa** *(True)* |
| **`314° 00'`** | **Kumbha** `14° 00'` | Sthira (Reverse) | `Slice #071` | **`Nadi #080`** | `#1580 / 1800` | **Shankari** *(Shashtha-Kala)* | `D60 #29` **Kamalakara** *(True)* |
| **`315° 00'`** | **Kumbha** `15° 00'` | Sthira (Reverse) | `Slice #076` | **`Nadi #075`** | `#1575 / 1800` | **Kumbhini** *(Panchama-Kala)* | `D60 #31` **Mrityu** *(False)* |
| **`316° 00'`** | **Kumbha** `16° 00'` | Sthira (Reverse) | `Slice #081` | **`Nadi #070`** | `#1570 / 1800` | **Maya** *(Panchama-Kala)* | `D60 #33` **Davagni** *(False)* |
| **`317° 00'`** | **Kumbha** `17° 00'` | Sthira (Reverse) | `Slice #086` | **`Nadi #065`** | `#1565 / 1800` | **Shankari** *(Panchama-Kala)* | `D60 #35` **Yama** *(False)* |
| **`318° 00'`** | **Kumbha** `18° 00'` | Sthira (Reverse) | `Slice #091` | **`Nadi #060`** | `#1560 / 1800` | **Kumbhini** *(Chaturtha-Kala)* | `D60 #37` **Sudha** *(True)* |
| **`319° 00'`** | **Kumbha** `19° 00'` | Sthira (Reverse) | `Slice #096` | **`Nadi #055`** | `#1555 / 1800` | **Maya** *(Chaturtha-Kala)* | `D60 #39` **Purnachandra** *(True)* |
| **`320° 00'`** | **Kumbha** `20° 00'` | Sthira (Reverse) | `Slice #101` | **`Nadi #050`** | `#1550 / 1800` | **Shankari** *(Chaturtha-Kala)* | `D60 #41` **Kulanasa** *(False)* |
| **`321° 00'`** | **Kumbha** `21° 00'` | Sthira (Reverse) | `Slice #106` | **`Nadi #045`** | `#1545 / 1800` | **Kumbhini** *(Tritiya-Kala)* | `D60 #43` **Utpata** *(False)* |
| **`322° 00'`** | **Kumbha** `22° 00'` | Sthira (Reverse) | `Slice #111` | **`Nadi #040`** | `#1540 / 1800` | **Maya** *(Tritiya-Kala)* | `D60 #45` **Saumya** *(True)* |
| **`323° 00'`** | **Kumbha** `23° 00'` | Sthira (Reverse) | `Slice #116` | **`Nadi #035`** | `#1535 / 1800` | **Shankari** *(Tritiya-Kala)* | `D60 #47` **Sheetala** *(True)* |
| **`324° 00'`** | **Kumbha** `24° 00'` | Sthira (Reverse) | `Slice #121` | **`Nadi #030`** | `#1530 / 1800` | **Kumbhini** *(Dvitiya-Kala)* | `D60 #49` **Chandramukhi** *(True)* |
| **`325° 00'`** | **Kumbha** `25° 00'` | Sthira (Reverse) | `Slice #126` | **`Nadi #025`** | `#1525 / 1800` | **Maya** *(Dvitiya-Kala)* | `D60 #51` **Kalapavaka** *(False)* |
| **`326° 00'`** | **Kumbha** `26° 00'` | Sthira (Reverse) | `Slice #131` | **`Nadi #020`** | `#1520 / 1800` | **Shankari** *(Dvitiya-Kala)* | `D60 #53` **Nirmala** *(True)* |
| **`327° 00'`** | **Kumbha** `27° 00'` | Sthira (Reverse) | `Slice #136` | **`Nadi #015`** | `#1515 / 1800` | **Kumbhini** *(Prathama-Kala)* | `D60 #55` **Krura** *(False)* |
| **`328° 00'`** | **Kumbha** `28° 00'` | Sthira (Reverse) | `Slice #141` | **`Nadi #010`** | `#1510 / 1800` | **Maya** *(Prathama-Kala)* | `D60 #57` **Amrita** *(True)* |
| **`329° 00'`** | **Kumbha** `29° 00'` | Sthira (Reverse) | `Slice #146` | **`Nadi #005`** | `#1505 / 1800` | **Shankari** *(Prathama-Kala)* | `D60 #59` **Bhramana** *(False)* |
| **`330° 00'`** | **Meena** `00° 00'` | Dwiswabhava (Mid) | `Slice #001` | **`Nadi #076`** | `#1726 / 1800` | **Vasudha** *(Shashtha-Kala)* | `D60 #01` **Ghora** *(False)* |
| **`331° 00'`** | **Meena** `01° 00'` | Dwiswabhava (Mid) | `Slice #006` | **`Nadi #081`** | `#1731 / 1800` | **Sudhakara** *(Shashtha-Kala)* | `D60 #03` **Deva** *(True)* |
| **`332° 00'`** | **Meena** `02° 00'` | Dwiswabhava (Mid) | `Slice #011` | **`Nadi #086`** | `#1736 / 1800` | **Manohara** *(Shashtha-Kala)* | `D60 #05` **Yaksha** *(True)* |
| **`333° 00'`** | **Meena** `03° 00'` | Dwiswabhava (Mid) | `Slice #016` | **`Nadi #091`** | `#1741 / 1800` | **Vasudha** *(Saptama-Kala)* | `D60 #07` **Bhrashta** *(False)* |
| **`334° 00'`** | **Meena** `04° 00'` | Dwiswabhava (Mid) | `Slice #021` | **`Nadi #096`** | `#1746 / 1800` | **Sudhakara** *(Saptama-Kala)* | `D60 #09` **Garala** *(False)* |
| **`335° 00'`** | **Meena** `05° 00'` | Dwiswabhava (Mid) | `Slice #026` | **`Nadi #101`** | `#1751 / 1800` | **Manohara** *(Saptama-Kala)* | `D60 #11` **Maya** *(False)* |
| **`336° 00'`** | **Meena** `06° 00'` | Dwiswabhava (Mid) | `Slice #031` | **`Nadi #106`** | `#1756 / 1800` | **Vasudha** *(Ashtama-Kala)* | `D60 #13` **Apampati** *(True)* |
| **`337° 00'`** | **Meena** `07° 00'` | Dwiswabhava (Mid) | `Slice #036` | **`Nadi #111`** | `#1761 / 1800` | **Sudhakara** *(Ashtama-Kala)* | `D60 #15` **Kala** *(False)* |
| **`338° 00'`** | **Meena** `08° 00'` | Dwiswabhava (Mid) | `Slice #041` | **`Nadi #116`** | `#1766 / 1800` | **Manohara** *(Ashtama-Kala)* | `D60 #17` **Amrita** *(True)* |
| **`339° 00'`** | **Meena** `09° 00'` | Dwiswabhava (Mid) | `Slice #046` | **`Nadi #121`** | `#1771 / 1800` | **Vasudha** *(Navama-Kala)* | `D60 #19` **Mridu** *(True)* |
| **`340° 00'`** | **Meena** `10° 00'` | Dwiswabhava (Mid) | `Slice #051` | **`Nadi #126`** | `#1776 / 1800` | **Sudhakara** *(Navama-Kala)* | `D60 #21` **Heramba** *(True)* |
| **`341° 00'`** | **Meena** `11° 00'` | Dwiswabhava (Mid) | `Slice #056` | **`Nadi #131`** | `#1781 / 1800` | **Manohara** *(Navama-Kala)* | `D60 #23` **Vishnu** *(True)* |
| **`342° 00'`** | **Meena** `12° 00'` | Dwiswabhava (Mid) | `Slice #061` | **`Nadi #136`** | `#1786 / 1800` | **Vasudha** *(Dashama-Kala)* | `D60 #25` **Deva** *(True)* |
| **`343° 00'`** | **Meena** `13° 00'` | Dwiswabhava (Mid) | `Slice #066` | **`Nadi #141`** | `#1791 / 1800` | **Sudhakara** *(Dashama-Kala)* | `D60 #27` **Kalinasa** *(True)* |
| **`344° 00'`** | **Meena** `14° 00'` | Dwiswabhava (Mid) | `Slice #071` | **`Nadi #146`** | `#1796 / 1800` | **Manohara** *(Dashama-Kala)* | `D60 #29` **Kamalakara** *(True)* |
| **`345° 00'`** | **Meena** `15° 00'` | Dwiswabhava (Mid) | `Slice #076` | **`Nadi #001`** | `#1651 / 1800` | **Vasudha** *(Prathama-Kala)* | `D60 #31` **Mrityu** *(False)* |
| **`346° 00'`** | **Meena** `16° 00'` | Dwiswabhava (Mid) | `Slice #081` | **`Nadi #006`** | `#1656 / 1800` | **Sudhakara** *(Prathama-Kala)* | `D60 #33` **Davagni** *(False)* |
| **`347° 00'`** | **Meena** `17° 00'` | Dwiswabhava (Mid) | `Slice #086` | **`Nadi #011`** | `#1661 / 1800` | **Manohara** *(Prathama-Kala)* | `D60 #35` **Yama** *(False)* |
| **`348° 00'`** | **Meena** `18° 00'` | Dwiswabhava (Mid) | `Slice #091` | **`Nadi #016`** | `#1666 / 1800` | **Vasudha** *(Dvitiya-Kala)* | `D60 #37` **Sudha** *(True)* |
| **`349° 00'`** | **Meena** `19° 00'` | Dwiswabhava (Mid) | `Slice #096` | **`Nadi #021`** | `#1671 / 1800` | **Sudhakara** *(Dvitiya-Kala)* | `D60 #39` **Purnachandra** *(True)* |
| **`350° 00'`** | **Meena** `20° 00'` | Dwiswabhava (Mid) | `Slice #101` | **`Nadi #026`** | `#1676 / 1800` | **Manohara** *(Dvitiya-Kala)* | `D60 #41` **Kulanasa** *(False)* |
| **`351° 00'`** | **Meena** `21° 00'` | Dwiswabhava (Mid) | `Slice #106` | **`Nadi #031`** | `#1681 / 1800` | **Vasudha** *(Tritiya-Kala)* | `D60 #43` **Utpata** *(False)* |
| **`352° 00'`** | **Meena** `22° 00'` | Dwiswabhava (Mid) | `Slice #111` | **`Nadi #036`** | `#1686 / 1800` | **Sudhakara** *(Tritiya-Kala)* | `D60 #45` **Saumya** *(True)* |
| **`353° 00'`** | **Meena** `23° 00'` | Dwiswabhava (Mid) | `Slice #116` | **`Nadi #041`** | `#1691 / 1800` | **Manohara** *(Tritiya-Kala)* | `D60 #47` **Sheetala** *(True)* |
| **`354° 00'`** | **Meena** `24° 00'` | Dwiswabhava (Mid) | `Slice #121` | **`Nadi #046`** | `#1696 / 1800` | **Vasudha** *(Chaturtha-Kala)* | `D60 #49` **Chandramukhi** *(True)* |
| **`355° 00'`** | **Meena** `25° 00'` | Dwiswabhava (Mid) | `Slice #126` | **`Nadi #051`** | `#1701 / 1800` | **Sudhakara** *(Chaturtha-Kala)* | `D60 #51` **Kalapavaka** *(False)* |
| **`356° 00'`** | **Meena** `26° 00'` | Dwiswabhava (Mid) | `Slice #131` | **`Nadi #056`** | `#1706 / 1800` | **Manohara** *(Chaturtha-Kala)* | `D60 #53` **Nirmala** *(True)* |
| **`357° 00'`** | **Meena** `27° 00'` | Dwiswabhava (Mid) | `Slice #136` | **`Nadi #061`** | `#1711 / 1800` | **Vasudha** *(Panchama-Kala)* | `D60 #55` **Krura** *(False)* |
| **`358° 00'`** | **Meena** `28° 00'` | Dwiswabhava (Mid) | `Slice #141` | **`Nadi #066`** | `#1716 / 1800` | **Sudhakara** *(Panchama-Kala)* | `D60 #57` **Amrita** *(True)* |
| **`359° 00'`** | **Meena** `29° 00'` | Dwiswabhava (Mid) | `Slice #146` | **`Nadi #071`** | `#1721 / 1800` | **Manohara** *(Panchama-Kala)* | `D60 #59` **Bhramana** *(False)* |

## Chapter 27 — Complete 3-Ring *Sudarshana Chakra* (BPHS Ch. 67: *Lagna, Chandra, & Surya* Wheels) & 100-Year Cyclic Progression Table

### 27.1 Worked Case Study: 12-House 3-Ring *Sudarshana Chakra* Synthesis Matrix

| Bhava (`1..12`) | Inner Ring: *Lagna* Sign & Lord | *Lagna* Occupants | Middle Ring: *Chandra* Sign & Lord | *Chandra* Occupants | Outer Ring: *Surya* Sign & Lord | *Surya* Occupants | 3-Ring Convergence Score (`0..100`) |
|---|---|---|---|---|---|---|---|
| **Bhava `01`** | **Dhanu** (Jupiter) | `—` | **Makara** (Saturn) | `Moon` | **Tula** (Venus) | `Sun, Mercury` | **`76.0`** |
| **Bhava `02`** | **Makara** (Saturn) | `Moon` | **Kumbha** (Saturn) | `Rahu` | **Vrishchika** (Mars) | `—` | **`56.0`** |
| **Bhava `03`** | **Kumbha** (Saturn) | `Rahu` | **Meena** (Jupiter) | `Saturn` | **Dhanu** (Jupiter) | `—` | **`38.0`** |
| **Bhava `04`** | **Meena** (Jupiter) | `Saturn` | **Mesha** (Mars) | `—` | **Makara** (Saturn) | `Moon` | **`64.0`** |
| **Bhava `05`** | **Mesha** (Mars) | `—` | **Vrishabha** (Venus) | `—` | **Kumbha** (Saturn) | `Rahu` | **`52.0`** |
| **Bhava `06`** | **Vrishabha** (Venus) | `—` | **Mithuna** (Mercury) | `—` | **Meena** (Jupiter) | `Saturn` | **`44.0`** |
| **Bhava `07`** | **Mithuna** (Mercury) | `—` | **Karka** (Moon) | `—` | **Mesha** (Mars) | `—` | **`58.0`** |
| **Bhava `08`** | **Karka** (Moon) | `—` | **Simha** (Sun) | `Mars, Jupiter, Ketu` | **Vrishabha** (Venus) | `—` | **`50.0`** |
| **Bhava `09`** | **Simha** (Sun) | `Mars, Jupiter, Ketu` | **Kanya** (Mercury) | `Venus` | **Mithuna** (Mercury) | `—` | **`70.0`** |
| **Bhava `10`** | **Kanya** (Mercury) | `Venus` | **Tula** (Venus) | `Sun, Mercury` | **Karka** (Moon) | `—` | **`76.0`** |
| **Bhava `11`** | **Tula** (Venus) | `Sun, Mercury` | **Vrishchika** (Mars) | `—` | **Simha** (Sun) | `Mars, Jupiter, Ketu` | **`64.0`** |
| **Bhava `12`** | **Vrishchika** (Mars) | `—` | **Dhanu** (Jupiter) | `—` | **Kanya** (Mercury) | `Venus` | **`62.0`** |

### 27.2 Complete 100-Year *Sudarshana Chakra* Annual Progression Table (Ages `1` to `100`)

| AgeYear | Progressed House (`Bhava`) | Progressed *Lagna* Sign & Lord | Progressed *Chandra* Sign & Lord | Progressed *Surya* Sign & Lord | Annual 3-Ring Convergence Score |
|---|---|---|---|---|---|
| **Year `001`** (Age 0..1) | **Bhava `01`** | **Dhanu** (Jupiter) | **Makara** (Saturn) | **Tula** (Venus) | **`76.0`** |
| **Year `002`** (Age 1..2) | **Bhava `02`** | **Makara** (Saturn) | **Kumbha** (Saturn) | **Vrishchika** (Mars) | **`56.0`** |
| **Year `003`** (Age 2..3) | **Bhava `03`** | **Kumbha** (Saturn) | **Meena** (Jupiter) | **Dhanu** (Jupiter) | **`38.0`** |
| **Year `004`** (Age 3..4) | **Bhava `04`** | **Meena** (Jupiter) | **Mesha** (Mars) | **Makara** (Saturn) | **`64.0`** |
| **Year `005`** (Age 4..5) | **Bhava `05`** | **Mesha** (Mars) | **Vrishabha** (Venus) | **Kumbha** (Saturn) | **`52.0`** |
| **Year `006`** (Age 5..6) | **Bhava `06`** | **Vrishabha** (Venus) | **Mithuna** (Mercury) | **Meena** (Jupiter) | **`44.0`** |
| **Year `007`** (Age 6..7) | **Bhava `07`** | **Mithuna** (Mercury) | **Karka** (Moon) | **Mesha** (Mars) | **`58.0`** |
| **Year `008`** (Age 7..8) | **Bhava `08`** | **Karka** (Moon) | **Simha** (Sun) | **Vrishabha** (Venus) | **`50.0`** |
| **Year `009`** (Age 8..9) | **Bhava `09`** | **Simha** (Sun) | **Kanya** (Mercury) | **Mithuna** (Mercury) | **`70.0`** |
| **Year `010`** (Age 9..10) | **Bhava `10`** | **Kanya** (Mercury) | **Tula** (Venus) | **Karka** (Moon) | **`76.0`** |
| **Year `011`** (Age 10..11) | **Bhava `11`** | **Tula** (Venus) | **Vrishchika** (Mars) | **Simha** (Sun) | **`64.0`** |
| **Year `012`** (Age 11..12) | **Bhava `12`** | **Vrishchika** (Mars) | **Dhanu** (Jupiter) | **Kanya** (Mercury) | **`62.0`** |
| **Year `013`** (Age 12..13) | **Bhava `01`** | **Dhanu** (Jupiter) | **Makara** (Saturn) | **Tula** (Venus) | **`76.0`** |
| **Year `014`** (Age 13..14) | **Bhava `02`** | **Makara** (Saturn) | **Kumbha** (Saturn) | **Vrishchika** (Mars) | **`56.0`** |
| **Year `015`** (Age 14..15) | **Bhava `03`** | **Kumbha** (Saturn) | **Meena** (Jupiter) | **Dhanu** (Jupiter) | **`38.0`** |
| **Year `016`** (Age 15..16) | **Bhava `04`** | **Meena** (Jupiter) | **Mesha** (Mars) | **Makara** (Saturn) | **`64.0`** |
| **Year `017`** (Age 16..17) | **Bhava `05`** | **Mesha** (Mars) | **Vrishabha** (Venus) | **Kumbha** (Saturn) | **`52.0`** |
| **Year `018`** (Age 17..18) | **Bhava `06`** | **Vrishabha** (Venus) | **Mithuna** (Mercury) | **Meena** (Jupiter) | **`44.0`** |
| **Year `019`** (Age 18..19) | **Bhava `07`** | **Mithuna** (Mercury) | **Karka** (Moon) | **Mesha** (Mars) | **`58.0`** |
| **Year `020`** (Age 19..20) | **Bhava `08`** | **Karka** (Moon) | **Simha** (Sun) | **Vrishabha** (Venus) | **`50.0`** |
| **Year `021`** (Age 20..21) | **Bhava `09`** | **Simha** (Sun) | **Kanya** (Mercury) | **Mithuna** (Mercury) | **`70.0`** |
| **Year `022`** (Age 21..22) | **Bhava `10`** | **Kanya** (Mercury) | **Tula** (Venus) | **Karka** (Moon) | **`76.0`** |
| **Year `023`** (Age 22..23) | **Bhava `11`** | **Tula** (Venus) | **Vrishchika** (Mars) | **Simha** (Sun) | **`64.0`** |
| **Year `024`** (Age 23..24) | **Bhava `12`** | **Vrishchika** (Mars) | **Dhanu** (Jupiter) | **Kanya** (Mercury) | **`62.0`** |
| **Year `025`** (Age 24..25) | **Bhava `01`** | **Dhanu** (Jupiter) | **Makara** (Saturn) | **Tula** (Venus) | **`76.0`** |
| **Year `026`** (Age 25..26) | **Bhava `02`** | **Makara** (Saturn) | **Kumbha** (Saturn) | **Vrishchika** (Mars) | **`56.0`** |
| **Year `027`** (Age 26..27) | **Bhava `03`** | **Kumbha** (Saturn) | **Meena** (Jupiter) | **Dhanu** (Jupiter) | **`38.0`** |
| **Year `028`** (Age 27..28) | **Bhava `04`** | **Meena** (Jupiter) | **Mesha** (Mars) | **Makara** (Saturn) | **`64.0`** |
| **Year `029`** (Age 28..29) | **Bhava `05`** | **Mesha** (Mars) | **Vrishabha** (Venus) | **Kumbha** (Saturn) | **`52.0`** |
| **Year `030`** (Age 29..30) | **Bhava `06`** | **Vrishabha** (Venus) | **Mithuna** (Mercury) | **Meena** (Jupiter) | **`44.0`** |
| **Year `031`** (Age 30..31) | **Bhava `07`** | **Mithuna** (Mercury) | **Karka** (Moon) | **Mesha** (Mars) | **`58.0`** |
| **Year `032`** (Age 31..32) | **Bhava `08`** | **Karka** (Moon) | **Simha** (Sun) | **Vrishabha** (Venus) | **`50.0`** |
| **Year `033`** (Age 32..33) | **Bhava `09`** | **Simha** (Sun) | **Kanya** (Mercury) | **Mithuna** (Mercury) | **`70.0`** |
| **Year `034`** (Age 33..34) | **Bhava `10`** | **Kanya** (Mercury) | **Tula** (Venus) | **Karka** (Moon) | **`76.0`** |
| **Year `035`** (Age 34..35) | **Bhava `11`** | **Tula** (Venus) | **Vrishchika** (Mars) | **Simha** (Sun) | **`64.0`** |
| **Year `036`** (Age 35..36) | **Bhava `12`** | **Vrishchika** (Mars) | **Dhanu** (Jupiter) | **Kanya** (Mercury) | **`62.0`** |
| **Year `037`** (Age 36..37) | **Bhava `01`** | **Dhanu** (Jupiter) | **Makara** (Saturn) | **Tula** (Venus) | **`76.0`** |
| **Year `038`** (Age 37..38) | **Bhava `02`** | **Makara** (Saturn) | **Kumbha** (Saturn) | **Vrishchika** (Mars) | **`56.0`** |
| **Year `039`** (Age 38..39) | **Bhava `03`** | **Kumbha** (Saturn) | **Meena** (Jupiter) | **Dhanu** (Jupiter) | **`38.0`** |
| **Year `040`** (Age 39..40) | **Bhava `04`** | **Meena** (Jupiter) | **Mesha** (Mars) | **Makara** (Saturn) | **`64.0`** |
| **Year `041`** (Age 40..41) | **Bhava `05`** | **Mesha** (Mars) | **Vrishabha** (Venus) | **Kumbha** (Saturn) | **`52.0`** |
| **Year `042`** (Age 41..42) | **Bhava `06`** | **Vrishabha** (Venus) | **Mithuna** (Mercury) | **Meena** (Jupiter) | **`44.0`** |
| **Year `043`** (Age 42..43) | **Bhava `07`** | **Mithuna** (Mercury) | **Karka** (Moon) | **Mesha** (Mars) | **`58.0`** |
| **Year `044`** (Age 43..44) | **Bhava `08`** | **Karka** (Moon) | **Simha** (Sun) | **Vrishabha** (Venus) | **`50.0`** |
| **Year `045`** (Age 44..45) | **Bhava `09`** | **Simha** (Sun) | **Kanya** (Mercury) | **Mithuna** (Mercury) | **`70.0`** |
| **Year `046`** (Age 45..46) | **Bhava `10`** | **Kanya** (Mercury) | **Tula** (Venus) | **Karka** (Moon) | **`76.0`** |
| **Year `047`** (Age 46..47) | **Bhava `11`** | **Tula** (Venus) | **Vrishchika** (Mars) | **Simha** (Sun) | **`64.0`** |
| **Year `048`** (Age 47..48) | **Bhava `12`** | **Vrishchika** (Mars) | **Dhanu** (Jupiter) | **Kanya** (Mercury) | **`62.0`** |
| **Year `049`** (Age 48..49) | **Bhava `01`** | **Dhanu** (Jupiter) | **Makara** (Saturn) | **Tula** (Venus) | **`76.0`** |
| **Year `050`** (Age 49..50) | **Bhava `02`** | **Makara** (Saturn) | **Kumbha** (Saturn) | **Vrishchika** (Mars) | **`56.0`** |
| **Year `051`** (Age 50..51) | **Bhava `03`** | **Kumbha** (Saturn) | **Meena** (Jupiter) | **Dhanu** (Jupiter) | **`38.0`** |
| **Year `052`** (Age 51..52) | **Bhava `04`** | **Meena** (Jupiter) | **Mesha** (Mars) | **Makara** (Saturn) | **`64.0`** |
| **Year `053`** (Age 52..53) | **Bhava `05`** | **Mesha** (Mars) | **Vrishabha** (Venus) | **Kumbha** (Saturn) | **`52.0`** |
| **Year `054`** (Age 53..54) | **Bhava `06`** | **Vrishabha** (Venus) | **Mithuna** (Mercury) | **Meena** (Jupiter) | **`44.0`** |
| **Year `055`** (Age 54..55) | **Bhava `07`** | **Mithuna** (Mercury) | **Karka** (Moon) | **Mesha** (Mars) | **`58.0`** |
| **Year `056`** (Age 55..56) | **Bhava `08`** | **Karka** (Moon) | **Simha** (Sun) | **Vrishabha** (Venus) | **`50.0`** |
| **Year `057`** (Age 56..57) | **Bhava `09`** | **Simha** (Sun) | **Kanya** (Mercury) | **Mithuna** (Mercury) | **`70.0`** |
| **Year `058`** (Age 57..58) | **Bhava `10`** | **Kanya** (Mercury) | **Tula** (Venus) | **Karka** (Moon) | **`76.0`** |
| **Year `059`** (Age 58..59) | **Bhava `11`** | **Tula** (Venus) | **Vrishchika** (Mars) | **Simha** (Sun) | **`64.0`** |
| **Year `060`** (Age 59..60) | **Bhava `12`** | **Vrishchika** (Mars) | **Dhanu** (Jupiter) | **Kanya** (Mercury) | **`62.0`** |
| **Year `061`** (Age 60..61) | **Bhava `01`** | **Dhanu** (Jupiter) | **Makara** (Saturn) | **Tula** (Venus) | **`76.0`** |
| **Year `062`** (Age 61..62) | **Bhava `02`** | **Makara** (Saturn) | **Kumbha** (Saturn) | **Vrishchika** (Mars) | **`56.0`** |
| **Year `063`** (Age 62..63) | **Bhava `03`** | **Kumbha** (Saturn) | **Meena** (Jupiter) | **Dhanu** (Jupiter) | **`38.0`** |
| **Year `064`** (Age 63..64) | **Bhava `04`** | **Meena** (Jupiter) | **Mesha** (Mars) | **Makara** (Saturn) | **`64.0`** |
| **Year `065`** (Age 64..65) | **Bhava `05`** | **Mesha** (Mars) | **Vrishabha** (Venus) | **Kumbha** (Saturn) | **`52.0`** |
| **Year `066`** (Age 65..66) | **Bhava `06`** | **Vrishabha** (Venus) | **Mithuna** (Mercury) | **Meena** (Jupiter) | **`44.0`** |
| **Year `067`** (Age 66..67) | **Bhava `07`** | **Mithuna** (Mercury) | **Karka** (Moon) | **Mesha** (Mars) | **`58.0`** |
| **Year `068`** (Age 67..68) | **Bhava `08`** | **Karka** (Moon) | **Simha** (Sun) | **Vrishabha** (Venus) | **`50.0`** |
| **Year `069`** (Age 68..69) | **Bhava `09`** | **Simha** (Sun) | **Kanya** (Mercury) | **Mithuna** (Mercury) | **`70.0`** |
| **Year `070`** (Age 69..70) | **Bhava `10`** | **Kanya** (Mercury) | **Tula** (Venus) | **Karka** (Moon) | **`76.0`** |
| **Year `071`** (Age 70..71) | **Bhava `11`** | **Tula** (Venus) | **Vrishchika** (Mars) | **Simha** (Sun) | **`64.0`** |
| **Year `072`** (Age 71..72) | **Bhava `12`** | **Vrishchika** (Mars) | **Dhanu** (Jupiter) | **Kanya** (Mercury) | **`62.0`** |
| **Year `073`** (Age 72..73) | **Bhava `01`** | **Dhanu** (Jupiter) | **Makara** (Saturn) | **Tula** (Venus) | **`76.0`** |
| **Year `074`** (Age 73..74) | **Bhava `02`** | **Makara** (Saturn) | **Kumbha** (Saturn) | **Vrishchika** (Mars) | **`56.0`** |
| **Year `075`** (Age 74..75) | **Bhava `03`** | **Kumbha** (Saturn) | **Meena** (Jupiter) | **Dhanu** (Jupiter) | **`38.0`** |
| **Year `076`** (Age 75..76) | **Bhava `04`** | **Meena** (Jupiter) | **Mesha** (Mars) | **Makara** (Saturn) | **`64.0`** |
| **Year `077`** (Age 76..77) | **Bhava `05`** | **Mesha** (Mars) | **Vrishabha** (Venus) | **Kumbha** (Saturn) | **`52.0`** |
| **Year `078`** (Age 77..78) | **Bhava `06`** | **Vrishabha** (Venus) | **Mithuna** (Mercury) | **Meena** (Jupiter) | **`44.0`** |
| **Year `079`** (Age 78..79) | **Bhava `07`** | **Mithuna** (Mercury) | **Karka** (Moon) | **Mesha** (Mars) | **`58.0`** |
| **Year `080`** (Age 79..80) | **Bhava `08`** | **Karka** (Moon) | **Simha** (Sun) | **Vrishabha** (Venus) | **`50.0`** |
| **Year `081`** (Age 80..81) | **Bhava `09`** | **Simha** (Sun) | **Kanya** (Mercury) | **Mithuna** (Mercury) | **`70.0`** |
| **Year `082`** (Age 81..82) | **Bhava `10`** | **Kanya** (Mercury) | **Tula** (Venus) | **Karka** (Moon) | **`76.0`** |
| **Year `083`** (Age 82..83) | **Bhava `11`** | **Tula** (Venus) | **Vrishchika** (Mars) | **Simha** (Sun) | **`64.0`** |
| **Year `084`** (Age 83..84) | **Bhava `12`** | **Vrishchika** (Mars) | **Dhanu** (Jupiter) | **Kanya** (Mercury) | **`62.0`** |
| **Year `085`** (Age 84..85) | **Bhava `01`** | **Dhanu** (Jupiter) | **Makara** (Saturn) | **Tula** (Venus) | **`76.0`** |
| **Year `086`** (Age 85..86) | **Bhava `02`** | **Makara** (Saturn) | **Kumbha** (Saturn) | **Vrishchika** (Mars) | **`56.0`** |
| **Year `087`** (Age 86..87) | **Bhava `03`** | **Kumbha** (Saturn) | **Meena** (Jupiter) | **Dhanu** (Jupiter) | **`38.0`** |
| **Year `088`** (Age 87..88) | **Bhava `04`** | **Meena** (Jupiter) | **Mesha** (Mars) | **Makara** (Saturn) | **`64.0`** |
| **Year `089`** (Age 88..89) | **Bhava `05`** | **Mesha** (Mars) | **Vrishabha** (Venus) | **Kumbha** (Saturn) | **`52.0`** |
| **Year `090`** (Age 89..90) | **Bhava `06`** | **Vrishabha** (Venus) | **Mithuna** (Mercury) | **Meena** (Jupiter) | **`44.0`** |
| **Year `091`** (Age 90..91) | **Bhava `07`** | **Mithuna** (Mercury) | **Karka** (Moon) | **Mesha** (Mars) | **`58.0`** |
| **Year `092`** (Age 91..92) | **Bhava `08`** | **Karka** (Moon) | **Simha** (Sun) | **Vrishabha** (Venus) | **`50.0`** |
| **Year `093`** (Age 92..93) | **Bhava `09`** | **Simha** (Sun) | **Kanya** (Mercury) | **Mithuna** (Mercury) | **`70.0`** |
| **Year `094`** (Age 93..94) | **Bhava `10`** | **Kanya** (Mercury) | **Tula** (Venus) | **Karka** (Moon) | **`76.0`** |
| **Year `095`** (Age 94..95) | **Bhava `11`** | **Tula** (Venus) | **Vrishchika** (Mars) | **Simha** (Sun) | **`64.0`** |
| **Year `096`** (Age 95..96) | **Bhava `12`** | **Vrishchika** (Mars) | **Dhanu** (Jupiter) | **Kanya** (Mercury) | **`62.0`** |
| **Year `097`** (Age 96..97) | **Bhava `01`** | **Dhanu** (Jupiter) | **Makara** (Saturn) | **Tula** (Venus) | **`76.0`** |
| **Year `098`** (Age 97..98) | **Bhava `02`** | **Makara** (Saturn) | **Kumbha** (Saturn) | **Vrishchika** (Mars) | **`56.0`** |
| **Year `099`** (Age 98..99) | **Bhava `03`** | **Kumbha** (Saturn) | **Meena** (Jupiter) | **Dhanu** (Jupiter) | **`38.0`** |
| **Year `100`** (Age 99..100) | **Bhava `04`** | **Meena** (Jupiter) | **Mesha** (Mars) | **Makara** (Saturn) | **`64.0`** |

## Chapter 28 — Golden *Muhurta* Electional Optimization, Complete `27 × 9` *Tarabala* & `12 × 12` *Chandrabala* Master Reckoners, & *Panchaka Rahita* Matrix

### 28.1 Complete 27-Nakshatra *Navatara* (`9-Tara` Cycle) *Tarabala* Master Lookup Matrix

| Birth Star (`Janma Nakshatra`) | `1: Janma` (Mixed) | `2: Sampat` (Wealth) | `3: Vipat` (Danger) | `4: Kshema` (Prosperity) | `5: Pratyak` (Obstacle) | `6: Sadhana` (Success) | `7: Naidhana` (Peril) | `8: Mitra` (Friend) | `9: Parama Mitra` (Supreme) |
|---|---|---|---|---|---|---|---|---|---|
| **`#01` Ashwini** | Ashwini, Magha, Mula | Bharani, Purva Phalguni, Purva Ashadha | Krittika, Uttara Phalguni, Uttara Ashadha | Rohini, Hasta, Shravana | Mrigashirsha, Chitra, Dhanishta | Ardra, Swati, Shatabhisha | Punarvasu, Vishakha, Purva Bhadrapada | Pushya, Anuradha, Uttara Bhadrapada | Ashlesha, Jyeshtha, Revati |
| **`#02` Bharani** | Bharani, Purva Phalguni, Purva Ashadha | Krittika, Uttara Phalguni, Uttara Ashadha | Rohini, Hasta, Shravana | Mrigashirsha, Chitra, Dhanishta | Ardra, Swati, Shatabhisha | Punarvasu, Vishakha, Purva Bhadrapada | Pushya, Anuradha, Uttara Bhadrapada | Ashlesha, Jyeshtha, Revati | Magha, Mula, Ashwini |
| **`#03` Krittika** | Krittika, Uttara Phalguni, Uttara Ashadha | Rohini, Hasta, Shravana | Mrigashirsha, Chitra, Dhanishta | Ardra, Swati, Shatabhisha | Punarvasu, Vishakha, Purva Bhadrapada | Pushya, Anuradha, Uttara Bhadrapada | Ashlesha, Jyeshtha, Revati | Magha, Mula, Ashwini | Purva Phalguni, Purva Ashadha, Bharani |
| **`#04` Rohini** | Rohini, Hasta, Shravana | Mrigashirsha, Chitra, Dhanishta | Ardra, Swati, Shatabhisha | Punarvasu, Vishakha, Purva Bhadrapada | Pushya, Anuradha, Uttara Bhadrapada | Ashlesha, Jyeshtha, Revati | Magha, Mula, Ashwini | Purva Phalguni, Purva Ashadha, Bharani | Uttara Phalguni, Uttara Ashadha, Krittika |
| **`#05` Mrigashirsha** | Mrigashirsha, Chitra, Dhanishta | Ardra, Swati, Shatabhisha | Punarvasu, Vishakha, Purva Bhadrapada | Pushya, Anuradha, Uttara Bhadrapada | Ashlesha, Jyeshtha, Revati | Magha, Mula, Ashwini | Purva Phalguni, Purva Ashadha, Bharani | Uttara Phalguni, Uttara Ashadha, Krittika | Hasta, Shravana, Rohini |
| **`#06` Ardra** | Ardra, Swati, Shatabhisha | Punarvasu, Vishakha, Purva Bhadrapada | Pushya, Anuradha, Uttara Bhadrapada | Ashlesha, Jyeshtha, Revati | Magha, Mula, Ashwini | Purva Phalguni, Purva Ashadha, Bharani | Uttara Phalguni, Uttara Ashadha, Krittika | Hasta, Shravana, Rohini | Chitra, Dhanishta, Mrigashirsha |
| **`#07` Punarvasu** | Punarvasu, Vishakha, Purva Bhadrapada | Pushya, Anuradha, Uttara Bhadrapada | Ashlesha, Jyeshtha, Revati | Magha, Mula, Ashwini | Purva Phalguni, Purva Ashadha, Bharani | Uttara Phalguni, Uttara Ashadha, Krittika | Hasta, Shravana, Rohini | Chitra, Dhanishta, Mrigashirsha | Swati, Shatabhisha, Ardra |
| **`#08` Pushya** | Pushya, Anuradha, Uttara Bhadrapada | Ashlesha, Jyeshtha, Revati | Magha, Mula, Ashwini | Purva Phalguni, Purva Ashadha, Bharani | Uttara Phalguni, Uttara Ashadha, Krittika | Hasta, Shravana, Rohini | Chitra, Dhanishta, Mrigashirsha | Swati, Shatabhisha, Ardra | Vishakha, Purva Bhadrapada, Punarvasu |
| **`#09` Ashlesha** | Ashlesha, Jyeshtha, Revati | Magha, Mula, Ashwini | Purva Phalguni, Purva Ashadha, Bharani | Uttara Phalguni, Uttara Ashadha, Krittika | Hasta, Shravana, Rohini | Chitra, Dhanishta, Mrigashirsha | Swati, Shatabhisha, Ardra | Vishakha, Purva Bhadrapada, Punarvasu | Anuradha, Uttara Bhadrapada, Pushya |
| **`#10` Magha** | Magha, Mula, Ashwini | Purva Phalguni, Purva Ashadha, Bharani | Uttara Phalguni, Uttara Ashadha, Krittika | Hasta, Shravana, Rohini | Chitra, Dhanishta, Mrigashirsha | Swati, Shatabhisha, Ardra | Vishakha, Purva Bhadrapada, Punarvasu | Anuradha, Uttara Bhadrapada, Pushya | Jyeshtha, Revati, Ashlesha |
| **`#11` Purva Phalguni** | Purva Phalguni, Purva Ashadha, Bharani | Uttara Phalguni, Uttara Ashadha, Krittika | Hasta, Shravana, Rohini | Chitra, Dhanishta, Mrigashirsha | Swati, Shatabhisha, Ardra | Vishakha, Purva Bhadrapada, Punarvasu | Anuradha, Uttara Bhadrapada, Pushya | Jyeshtha, Revati, Ashlesha | Mula, Ashwini, Magha |
| **`#12` Uttara Phalguni** | Uttara Phalguni, Uttara Ashadha, Krittika | Hasta, Shravana, Rohini | Chitra, Dhanishta, Mrigashirsha | Swati, Shatabhisha, Ardra | Vishakha, Purva Bhadrapada, Punarvasu | Anuradha, Uttara Bhadrapada, Pushya | Jyeshtha, Revati, Ashlesha | Mula, Ashwini, Magha | Purva Ashadha, Bharani, Purva Phalguni |
| **`#13` Hasta** | Hasta, Shravana, Rohini | Chitra, Dhanishta, Mrigashirsha | Swati, Shatabhisha, Ardra | Vishakha, Purva Bhadrapada, Punarvasu | Anuradha, Uttara Bhadrapada, Pushya | Jyeshtha, Revati, Ashlesha | Mula, Ashwini, Magha | Purva Ashadha, Bharani, Purva Phalguni | Uttara Ashadha, Krittika, Uttara Phalguni |
| **`#14` Chitra** | Chitra, Dhanishta, Mrigashirsha | Swati, Shatabhisha, Ardra | Vishakha, Purva Bhadrapada, Punarvasu | Anuradha, Uttara Bhadrapada, Pushya | Jyeshtha, Revati, Ashlesha | Mula, Ashwini, Magha | Purva Ashadha, Bharani, Purva Phalguni | Uttara Ashadha, Krittika, Uttara Phalguni | Shravana, Rohini, Hasta |
| **`#15` Swati** | Swati, Shatabhisha, Ardra | Vishakha, Purva Bhadrapada, Punarvasu | Anuradha, Uttara Bhadrapada, Pushya | Jyeshtha, Revati, Ashlesha | Mula, Ashwini, Magha | Purva Ashadha, Bharani, Purva Phalguni | Uttara Ashadha, Krittika, Uttara Phalguni | Shravana, Rohini, Hasta | Dhanishta, Mrigashirsha, Chitra |
| **`#16` Vishakha** | Vishakha, Purva Bhadrapada, Punarvasu | Anuradha, Uttara Bhadrapada, Pushya | Jyeshtha, Revati, Ashlesha | Mula, Ashwini, Magha | Purva Ashadha, Bharani, Purva Phalguni | Uttara Ashadha, Krittika, Uttara Phalguni | Shravana, Rohini, Hasta | Dhanishta, Mrigashirsha, Chitra | Shatabhisha, Ardra, Swati |
| **`#17` Anuradha** | Anuradha, Uttara Bhadrapada, Pushya | Jyeshtha, Revati, Ashlesha | Mula, Ashwini, Magha | Purva Ashadha, Bharani, Purva Phalguni | Uttara Ashadha, Krittika, Uttara Phalguni | Shravana, Rohini, Hasta | Dhanishta, Mrigashirsha, Chitra | Shatabhisha, Ardra, Swati | Purva Bhadrapada, Punarvasu, Vishakha |
| **`#18` Jyeshtha** | Jyeshtha, Revati, Ashlesha | Mula, Ashwini, Magha | Purva Ashadha, Bharani, Purva Phalguni | Uttara Ashadha, Krittika, Uttara Phalguni | Shravana, Rohini, Hasta | Dhanishta, Mrigashirsha, Chitra | Shatabhisha, Ardra, Swati | Purva Bhadrapada, Punarvasu, Vishakha | Uttara Bhadrapada, Pushya, Anuradha |
| **`#19` Mula** | Mula, Ashwini, Magha | Purva Ashadha, Bharani, Purva Phalguni | Uttara Ashadha, Krittika, Uttara Phalguni | Shravana, Rohini, Hasta | Dhanishta, Mrigashirsha, Chitra | Shatabhisha, Ardra, Swati | Purva Bhadrapada, Punarvasu, Vishakha | Uttara Bhadrapada, Pushya, Anuradha | Revati, Ashlesha, Jyeshtha |
| **`#20` Purva Ashadha** | Purva Ashadha, Bharani, Purva Phalguni | Uttara Ashadha, Krittika, Uttara Phalguni | Shravana, Rohini, Hasta | Dhanishta, Mrigashirsha, Chitra | Shatabhisha, Ardra, Swati | Purva Bhadrapada, Punarvasu, Vishakha | Uttara Bhadrapada, Pushya, Anuradha | Revati, Ashlesha, Jyeshtha | Ashwini, Magha, Mula |
| **`#21` Uttara Ashadha** | Uttara Ashadha, Krittika, Uttara Phalguni | Shravana, Rohini, Hasta | Dhanishta, Mrigashirsha, Chitra | Shatabhisha, Ardra, Swati | Purva Bhadrapada, Punarvasu, Vishakha | Uttara Bhadrapada, Pushya, Anuradha | Revati, Ashlesha, Jyeshtha | Ashwini, Magha, Mula | Bharani, Purva Phalguni, Purva Ashadha |
| **`#22` Shravana** | Shravana, Rohini, Hasta | Dhanishta, Mrigashirsha, Chitra | Shatabhisha, Ardra, Swati | Purva Bhadrapada, Punarvasu, Vishakha | Uttara Bhadrapada, Pushya, Anuradha | Revati, Ashlesha, Jyeshtha | Ashwini, Magha, Mula | Bharani, Purva Phalguni, Purva Ashadha | Krittika, Uttara Phalguni, Uttara Ashadha |
| **`#23` Dhanishta** | Dhanishta, Mrigashirsha, Chitra | Shatabhisha, Ardra, Swati | Purva Bhadrapada, Punarvasu, Vishakha | Uttara Bhadrapada, Pushya, Anuradha | Revati, Ashlesha, Jyeshtha | Ashwini, Magha, Mula | Bharani, Purva Phalguni, Purva Ashadha | Krittika, Uttara Phalguni, Uttara Ashadha | Rohini, Hasta, Shravana |
| **`#24` Shatabhisha** | Shatabhisha, Ardra, Swati | Purva Bhadrapada, Punarvasu, Vishakha | Uttara Bhadrapada, Pushya, Anuradha | Revati, Ashlesha, Jyeshtha | Ashwini, Magha, Mula | Bharani, Purva Phalguni, Purva Ashadha | Krittika, Uttara Phalguni, Uttara Ashadha | Rohini, Hasta, Shravana | Mrigashirsha, Chitra, Dhanishta |
| **`#25` Purva Bhadrapada** | Purva Bhadrapada, Punarvasu, Vishakha | Uttara Bhadrapada, Pushya, Anuradha | Revati, Ashlesha, Jyeshtha | Ashwini, Magha, Mula | Bharani, Purva Phalguni, Purva Ashadha | Krittika, Uttara Phalguni, Uttara Ashadha | Rohini, Hasta, Shravana | Mrigashirsha, Chitra, Dhanishta | Ardra, Swati, Shatabhisha |
| **`#26` Uttara Bhadrapada** | Uttara Bhadrapada, Pushya, Anuradha | Revati, Ashlesha, Jyeshtha | Ashwini, Magha, Mula | Bharani, Purva Phalguni, Purva Ashadha | Krittika, Uttara Phalguni, Uttara Ashadha | Rohini, Hasta, Shravana | Mrigashirsha, Chitra, Dhanishta | Ardra, Swati, Shatabhisha | Punarvasu, Vishakha, Purva Bhadrapada |
| **`#27` Revati** | Revati, Ashlesha, Jyeshtha | Ashwini, Magha, Mula | Bharani, Purva Phalguni, Purva Ashadha | Krittika, Uttara Phalguni, Uttara Ashadha | Rohini, Hasta, Shravana | Mrigashirsha, Chitra, Dhanishta | Ardra, Swati, Shatabhisha | Punarvasu, Vishakha, Purva Bhadrapada | Pushya, Anuradha, Uttara Bhadrapada |

### 28.2 Complete `12 × 12` *Chandrabala* (Natal Moon Rashi vs Transit Moon Rashi) Master Matrix

| Natal Moon Rashi (`Janma Rashi`) | Auspicious Transit Moon Signs (`1, 3, 6, 7, 10, 11` = *Shubha Chandrabala*) | Avoided *Ashtama / Dusthana* Signs (`4, 8, 12` = *Chandrashtama / Ari*) | Neutral Signs (`2, 5, 9`) |
|---|---|---|---|
| **Mesha** | **Mesha** (1H), **Mithuna** (3H), **Kanya** (6H), **Tula** (7H), **Makara** (10H), **Kumbha** (11H) | `Karka` (4H), `Vrishchika` (8H), `Meena` (12H) | Vrishabha (2H), Simha (5H), Dhanu (9H) |
| **Vrishabha** | **Vrishabha** (1H), **Karka** (3H), **Tula** (6H), **Vrishchika** (7H), **Kumbha** (10H), **Meena** (11H) | `Simha` (4H), `Dhanu` (8H), `Mesha` (12H) | Mithuna (2H), Kanya (5H), Makara (9H) |
| **Mithuna** | **Mithuna** (1H), **Simha** (3H), **Vrishchika** (6H), **Dhanu** (7H), **Meena** (10H), **Mesha** (11H) | `Kanya` (4H), `Makara` (8H), `Vrishabha` (12H) | Karka (2H), Tula (5H), Kumbha (9H) |
| **Karka** | **Karka** (1H), **Kanya** (3H), **Dhanu** (6H), **Makara** (7H), **Mesha** (10H), **Vrishabha** (11H) | `Tula` (4H), `Kumbha` (8H), `Mithuna` (12H) | Simha (2H), Vrishchika (5H), Meena (9H) |
| **Simha** | **Simha** (1H), **Tula** (3H), **Makara** (6H), **Kumbha** (7H), **Vrishabha** (10H), **Mithuna** (11H) | `Vrishchika` (4H), `Meena` (8H), `Karka` (12H) | Kanya (2H), Dhanu (5H), Mesha (9H) |
| **Kanya** | **Kanya** (1H), **Vrishchika** (3H), **Kumbha** (6H), **Meena** (7H), **Mithuna** (10H), **Karka** (11H) | `Dhanu` (4H), `Mesha` (8H), `Simha` (12H) | Tula (2H), Makara (5H), Vrishabha (9H) |
| **Tula** | **Tula** (1H), **Dhanu** (3H), **Meena** (6H), **Mesha** (7H), **Karka** (10H), **Simha** (11H) | `Makara` (4H), `Vrishabha` (8H), `Kanya` (12H) | Vrishchika (2H), Kumbha (5H), Mithuna (9H) |
| **Vrishchika** | **Vrishchika** (1H), **Makara** (3H), **Mesha** (6H), **Vrishabha** (7H), **Simha** (10H), **Kanya** (11H) | `Kumbha` (4H), `Mithuna` (8H), `Tula` (12H) | Dhanu (2H), Meena (5H), Karka (9H) |
| **Dhanu** | **Dhanu** (1H), **Kumbha** (3H), **Vrishabha** (6H), **Mithuna** (7H), **Kanya** (10H), **Tula** (11H) | `Meena` (4H), `Karka` (8H), `Vrishchika` (12H) | Makara (2H), Mesha (5H), Simha (9H) |
| **Makara** | **Makara** (1H), **Meena** (3H), **Mithuna** (6H), **Karka** (7H), **Tula** (10H), **Vrishchika** (11H) | `Mesha` (4H), `Simha` (8H), `Dhanu` (12H) | Kumbha (2H), Vrishabha (5H), Kanya (9H) |
| **Kumbha** | **Kumbha** (1H), **Mesha** (3H), **Karka** (6H), **Simha** (7H), **Vrishchika** (10H), **Dhanu** (11H) | `Vrishabha` (4H), `Kanya` (8H), `Makara` (12H) | Meena (2H), Mithuna (5H), Tula (9H) |
| **Meena** | **Meena** (1H), **Vrishabha** (3H), **Simha** (6H), **Kanya** (7H), **Dhanu** (10H), **Makara** (11H) | `Mithuna` (4H), `Tula` (8H), `Kumbha` (12H) | Mesha (2H), Karka (5H), Vrishchika (9H) |

### 28.3 Worked Case Study: Top 15 Golden *Muhurta* Electional Windows (12-Constraint Multi-Objective Optimization)

| Rank | Window (`UTC`) | Vara | Tithi | Nakshatra | Yoga | Ascendant (`Lagna`) | *Panchaka Rahita* | *Tarabala* | *Chandrabala* | Score (`0..100`) | Grade & Auspicious Factors |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `#01` | `2026-11-01T02:00:00Z` | Sunday | Krishna #22 | *Pushya* | Yoga #22 | **Tula** | `Shubha (r=5)` | `Sadhana (Realization/Success)` | 7H | **`100.0`** | **Uttama (Supreme Golden Muhurta)**: Free of Rahu Kalam, Free of Yamagandam, Non-Rikta Tithi (Krishna 7) |
| `#02` | `2026-11-01T04:00:00Z` | Sunday | Krishna #22 | *Pushya* | Yoga #22 | **Vrishchika** | `Dosha (r=6)` | `Sadhana (Realization/Success)` | 7H | **`100.0`** | **Uttama (Supreme Golden Muhurta)**: Free of Rahu Kalam, Free of Yamagandam, Non-Rikta Tithi (Krishna 7) |
| `#03` | `2026-11-01T10:00:00Z` | Sunday | Krishna #23 | *Pushya* | Yoga #23 | **Meena** | `Dosha (r=2)` | `Sadhana (Realization/Success)` | 7H | **`100.0`** | **Uttama (Supreme Golden Muhurta)**: Free of Rahu Kalam, Free of Yamagandam, Non-Rikta Tithi (Krishna 8) |
| `#04` | `2026-11-01T14:00:00Z` | Sunday | Krishna #23 | *Pushya* | Yoga #23 | **Vrishabha** | `Dosha (r=1)` | `Sadhana (Realization/Success)` | 7H | **`100.0`** | **Uttama (Supreme Golden Muhurta)**: Free of Rahu Kalam, Free of Yamagandam, Non-Rikta Tithi (Krishna 8) |
| `#05` | `2026-11-01T18:00:00Z` | Sunday | Krishna #23 | *Pushya* | Yoga #23 | **Karka** | `Shubha (r=3)` | `Sadhana (Realization/Success)` | 7H | **`100.0`** | **Uttama (Supreme Golden Muhurta)**: Free of Rahu Kalam, Free of Yamagandam, Non-Rikta Tithi (Krishna 8) |
| `#06` | `2026-11-01T20:00:00Z` | Monday | Krishna #23 | *Pushya* | Yoga #23 | **Simha** | `Shubha (r=5)` | `Sadhana (Realization/Success)` | 7H | **`100.0`** | **Uttama (Supreme Golden Muhurta)**: Free of Rahu Kalam, Free of Yamagandam, Shubha Vara (Monday) |
| `#07` | `2026-11-01T22:00:00Z` | Monday | Krishna #23 | *Pushya* | Yoga #23 | **Kanya** | `Dosha (r=6)` | `Sadhana (Realization/Success)` | 7H | **`100.0`** | **Uttama (Supreme Golden Muhurta)**: Free of Rahu Kalam, Free of Yamagandam, Shubha Vara (Monday) |
| `#08` | `2026-11-01T06:00:00Z` | Sunday | Krishna #22 | *Pushya* | Yoga #22 | **Dhanu** | `Shubha (r=7)` | `Sadhana (Realization/Success)` | 7H | **`98.0`** | **Uttama (Supreme Golden Muhurta)**: Free of Rahu Kalam, Free of Yamagandam, Non-Rikta Tithi (Krishna 7) |
| `#09` | `2026-11-01T08:00:00Z` | Sunday | Krishna #22 | *Pushya* | Yoga #22 | **Makara** | `Dosha (r=8)` | `Sadhana (Realization/Success)` | 7H | **`94.0`** | **Madhyama (Auspicious)**: Free of Rahu Kalam, Non-Rikta Tithi (Krishna 7), Activity-Favored Nakshatra (Pushya) |
| `#10` | `2026-11-01T12:00:00Z` | Sunday | Krishna #23 | *Pushya* | Yoga #23 | **Mesha** | `Shubha (r=0)` | `Sadhana (Realization/Success)` | 7H | **`93.0`** | **Madhyama (Auspicious)**: Free of Yamagandam, Non-Rikta Tithi (Krishna 8), Activity-Favored Nakshatra (Pushya) |
| `#11` | `2026-11-01T16:00:00Z` | Sunday | Krishna #23 | *Pushya* | Yoga #23 | **Mithuna** | `Dosha (r=2)` | `Sadhana (Realization/Success)` | 7H | **`92.0`** | **Uttama (Supreme Golden Muhurta)**: Free of Rahu Kalam, Free of Yamagandam, Non-Rikta Tithi (Krishna 8) |
| `#12` | `2026-11-01T00:00:00Z` | Sunday | Krishna #22 | *Punarvasu* | Yoga #22 | **Kanya** | `Shubha (r=3)` | `Pratyak (Obstacles)` | 7H | **`90.0`** | **Uttama (Supreme Golden Muhurta)**: Free of Rahu Kalam, Free of Yamagandam, Non-Rikta Tithi (Krishna 7) |
| `#13` | `2026-11-02T04:00:00Z` | Monday | Krishna #23 | *Ashlesha* | Yoga #23 | **Vrishchika** | `Shubha (r=0)` | `Naidhana (Peril/Destruction)` | 7H | **`86.0`** | **Uttama (Supreme Golden Muhurta)**: Free of Rahu Kalam, Free of Yamagandam, Shubha Vara (Monday) |
| `#14` | `2026-11-04T12:00:00Z` | Wednesday | Krishna #26 | *Purva Phalguni* | Yoga #26 | **Mesha** | `Shubha (r=0)` | `Parama Mitra (Supreme Friend)` | 8H | **`86.0`** | **Uttama (Supreme Golden Muhurta)**: Free of Rahu Kalam, Free of Yamagandam, Shubha Vara (Wednesday) |
| `#15` | `2026-11-04T18:00:00Z` | Wednesday | Krishna #26 | *Purva Phalguni* | Yoga #26 | **Karka** | `Shubha (r=3)` | `Parama Mitra (Supreme Friend)` | 8H | **`86.0`** | **Uttama (Supreme Golden Muhurta)**: Free of Rahu Kalam, Free of Yamagandam, Shubha Vara (Wednesday) |

### 28.4 Complete `30 Tithi × 7 Vara` (`210-Row`) *Panchaka Rahita*, *Dagdha Rashi*, & *Amrita/Sarvartha Siddhi* Electional Master Table

| Lunar Tithi (`1..30`) | Paksha & Tithi Group (*Nanda/Bhadra/Jaya/Rikta/Purna*) | Weekday (`Vara`) | *Dagdha Rashi* (Burnt Sign to Avoid) | *Amrita Siddhi* Star | *Sarvartha Siddhi* Stars | Safe *Panchaka Rahita* Ascendants (`Mesha..Meena` for Star #1) |
|---|---|---|---|---|---|---|
| **`Tithi #01`** (Shukla 01) | Nanda (Joy) | **Sunday** | `Tula, Makara` | *Hasta* | Ashwini, Pushya, Uttara Phalguni, Hasta | Vrishabha, Karka, Kanya, Dhanu, Kumbha |
| **`Tithi #01`** (Shukla 01) | Nanda (Joy) | **Monday** | `Tula, Makara` | *Mrigashirsha* | Rohini, Mrigashirsha, Pushya, Anuradha | Mesha, Mithuna, Simha, Vrishchika, Makara, Meena |
| **`Tithi #01`** (Shukla 01) | Nanda (Joy) | **Tuesday** | `Tula, Makara` | *Ashwini* | Ashwini, Krittika, Ashlesha, Uttara Bhadrapada | Vrishabha, Karka, Tula, Dhanu, Kumbha |
| **`Tithi #01`** (Shukla 01) | Nanda (Joy) | **Wednesday** | `Tula, Makara` | *Anuradha* | Krittika, Rohini, Mrigashirsha, Hasta | Mesha, Mithuna, Kanya, Vrishchika, Makara, Meena |
| **`Tithi #01`** (Shukla 01) | Nanda (Joy) | **Thursday** | `Tula, Makara` | *Pushya* | Ashwini, Punarvasu, Pushya, Anuradha | Vrishabha, Simha, Tula, Dhanu, Kumbha |
| **`Tithi #01`** (Shukla 01) | Nanda (Joy) | **Friday** | `Tula, Makara` | *Revati* | Ashwini, Punarvasu, Anuradha, Shravana | Mesha, Karka, Kanya, Vrishchika, Makara |
| **`Tithi #01`** (Shukla 01) | Nanda (Joy) | **Saturday** | `Tula, Makara` | *Rohini* | Rohini, Swati, Shravana | Mithuna, Simha, Tula, Dhanu, Meena |
| **`Tithi #02`** (Shukla 02) | Bhadra (Good) | **Sunday** | `Dhanu, Meena` | *Hasta* | Ashwini, Pushya, Uttara Phalguni, Hasta | Mesha, Mithuna, Simha, Vrishchika, Makara, Meena |
| **`Tithi #02`** (Shukla 02) | Bhadra (Good) | **Monday** | `Dhanu, Meena` | *Mrigashirsha* | Rohini, Mrigashirsha, Pushya, Anuradha | Vrishabha, Karka, Tula, Dhanu, Kumbha |
| **`Tithi #02`** (Shukla 02) | Bhadra (Good) | **Tuesday** | `Dhanu, Meena` | *Ashwini* | Ashwini, Krittika, Ashlesha, Uttara Bhadrapada | Mesha, Mithuna, Kanya, Vrishchika, Makara, Meena |
| **`Tithi #02`** (Shukla 02) | Bhadra (Good) | **Wednesday** | `Dhanu, Meena` | *Anuradha* | Krittika, Rohini, Mrigashirsha, Hasta | Vrishabha, Simha, Tula, Dhanu, Kumbha |
| **`Tithi #02`** (Shukla 02) | Bhadra (Good) | **Thursday** | `Dhanu, Meena` | *Pushya* | Ashwini, Punarvasu, Pushya, Anuradha | Mesha, Karka, Kanya, Vrishchika, Makara |
| **`Tithi #02`** (Shukla 02) | Bhadra (Good) | **Friday** | `Dhanu, Meena` | *Revati* | Ashwini, Punarvasu, Anuradha, Shravana | Mithuna, Simha, Tula, Dhanu, Meena |
| **`Tithi #02`** (Shukla 02) | Bhadra (Good) | **Saturday** | `Dhanu, Meena` | *Rohini* | Rohini, Swati, Shravana | Vrishabha, Karka, Kanya, Vrishchika, Kumbha |
| **`Tithi #03`** (Shukla 03) | Jaya (Victory) | **Sunday** | `Simha, Makara` | *Hasta* | Ashwini, Pushya, Uttara Phalguni, Hasta | Vrishabha, Karka, Tula, Dhanu, Kumbha |
| **`Tithi #03`** (Shukla 03) | Jaya (Victory) | **Monday** | `Simha, Makara` | *Mrigashirsha* | Rohini, Mrigashirsha, Pushya, Anuradha | Mesha, Mithuna, Kanya, Vrishchika, Makara, Meena |
| **`Tithi #03`** (Shukla 03) | Jaya (Victory) | **Tuesday** | `Simha, Makara` | *Ashwini* | Ashwini, Krittika, Ashlesha, Uttara Bhadrapada | Vrishabha, Simha, Tula, Dhanu, Kumbha |
| **`Tithi #03`** (Shukla 03) | Jaya (Victory) | **Wednesday** | `Simha, Makara` | *Anuradha* | Krittika, Rohini, Mrigashirsha, Hasta | Mesha, Karka, Kanya, Vrishchika, Makara |
| **`Tithi #03`** (Shukla 03) | Jaya (Victory) | **Thursday** | `Simha, Makara` | *Pushya* | Ashwini, Punarvasu, Pushya, Anuradha | Mithuna, Simha, Tula, Dhanu, Meena |
| **`Tithi #03`** (Shukla 03) | Jaya (Victory) | **Friday** | `Simha, Makara` | *Revati* | Ashwini, Punarvasu, Anuradha, Shravana | Vrishabha, Karka, Kanya, Vrishchika, Kumbha |
| **`Tithi #03`** (Shukla 03) | Jaya (Victory) | **Saturday** | `Simha, Makara` | *Rohini* | Rohini, Swati, Shravana | Mesha, Mithuna, Simha, Tula, Makara, Meena |
| **`Tithi #04`** (Shukla 04) | Rikta (Empty/Avoid) | **Sunday** | `Vrishabha, Kumbha` | *Hasta* | Ashwini, Pushya, Uttara Phalguni, Hasta | Mesha, Mithuna, Kanya, Vrishchika, Makara, Meena |
| **`Tithi #04`** (Shukla 04) | Rikta (Empty/Avoid) | **Monday** | `Vrishabha, Kumbha` | *Mrigashirsha* | Rohini, Mrigashirsha, Pushya, Anuradha | Vrishabha, Simha, Tula, Dhanu, Kumbha |
| **`Tithi #04`** (Shukla 04) | Rikta (Empty/Avoid) | **Tuesday** | `Vrishabha, Kumbha` | *Ashwini* | Ashwini, Krittika, Ashlesha, Uttara Bhadrapada | Mesha, Karka, Kanya, Vrishchika, Makara |
| **`Tithi #04`** (Shukla 04) | Rikta (Empty/Avoid) | **Wednesday** | `Vrishabha, Kumbha` | *Anuradha* | Krittika, Rohini, Mrigashirsha, Hasta | Mithuna, Simha, Tula, Dhanu, Meena |
| **`Tithi #04`** (Shukla 04) | Rikta (Empty/Avoid) | **Thursday** | `Vrishabha, Kumbha` | *Pushya* | Ashwini, Punarvasu, Pushya, Anuradha | Vrishabha, Karka, Kanya, Vrishchika, Kumbha |
| **`Tithi #04`** (Shukla 04) | Rikta (Empty/Avoid) | **Friday** | `Vrishabha, Kumbha` | *Revati* | Ashwini, Punarvasu, Anuradha, Shravana | Mesha, Mithuna, Simha, Tula, Makara, Meena |
| **`Tithi #04`** (Shukla 04) | Rikta (Empty/Avoid) | **Saturday** | `Vrishabha, Kumbha` | *Rohini* | Rohini, Swati, Shravana | Vrishabha, Karka, Kanya, Dhanu, Kumbha |
| **`Tithi #05`** (Shukla 05) | Purna (Fullness) | **Sunday** | `Mithuna, Kanya` | *Hasta* | Ashwini, Pushya, Uttara Phalguni, Hasta | Vrishabha, Simha, Tula, Dhanu, Kumbha |
| **`Tithi #05`** (Shukla 05) | Purna (Fullness) | **Monday** | `Mithuna, Kanya` | *Mrigashirsha* | Rohini, Mrigashirsha, Pushya, Anuradha | Mesha, Karka, Kanya, Vrishchika, Makara |
| **`Tithi #05`** (Shukla 05) | Purna (Fullness) | **Tuesday** | `Mithuna, Kanya` | *Ashwini* | Ashwini, Krittika, Ashlesha, Uttara Bhadrapada | Mithuna, Simha, Tula, Dhanu, Meena |
| **`Tithi #05`** (Shukla 05) | Purna (Fullness) | **Wednesday** | `Mithuna, Kanya` | *Anuradha* | Krittika, Rohini, Mrigashirsha, Hasta | Vrishabha, Karka, Kanya, Vrishchika, Kumbha |
| **`Tithi #05`** (Shukla 05) | Purna (Fullness) | **Thursday** | `Mithuna, Kanya` | *Pushya* | Ashwini, Punarvasu, Pushya, Anuradha | Mesha, Mithuna, Simha, Tula, Makara, Meena |
| **`Tithi #05`** (Shukla 05) | Purna (Fullness) | **Friday** | `Mithuna, Kanya` | *Revati* | Ashwini, Punarvasu, Anuradha, Shravana | Vrishabha, Karka, Kanya, Dhanu, Kumbha |
| **`Tithi #05`** (Shukla 05) | Purna (Fullness) | **Saturday** | `Mithuna, Kanya` | *Rohini* | Rohini, Swati, Shravana | Mesha, Mithuna, Simha, Vrishchika, Makara, Meena |
| **`Tithi #06`** (Shukla 06) | Nanda (Joy) | **Sunday** | `Mesha, Simha` | *Hasta* | Ashwini, Pushya, Uttara Phalguni, Hasta | Mesha, Karka, Kanya, Vrishchika, Makara |
| **`Tithi #06`** (Shukla 06) | Nanda (Joy) | **Monday** | `Mesha, Simha` | *Mrigashirsha* | Rohini, Mrigashirsha, Pushya, Anuradha | Mithuna, Simha, Tula, Dhanu, Meena |
| **`Tithi #06`** (Shukla 06) | Nanda (Joy) | **Tuesday** | `Mesha, Simha` | *Ashwini* | Ashwini, Krittika, Ashlesha, Uttara Bhadrapada | Vrishabha, Karka, Kanya, Vrishchika, Kumbha |
| **`Tithi #06`** (Shukla 06) | Nanda (Joy) | **Wednesday** | `Mesha, Simha` | *Anuradha* | Krittika, Rohini, Mrigashirsha, Hasta | Mesha, Mithuna, Simha, Tula, Makara, Meena |
| **`Tithi #06`** (Shukla 06) | Nanda (Joy) | **Thursday** | `Mesha, Simha` | *Pushya* | Ashwini, Punarvasu, Pushya, Anuradha | Vrishabha, Karka, Kanya, Dhanu, Kumbha |
| **`Tithi #06`** (Shukla 06) | Nanda (Joy) | **Friday** | `Mesha, Simha` | *Revati* | Ashwini, Punarvasu, Anuradha, Shravana | Mesha, Mithuna, Simha, Vrishchika, Makara, Meena |
| **`Tithi #06`** (Shukla 06) | Nanda (Joy) | **Saturday** | `Mesha, Simha` | *Rohini* | Rohini, Swati, Shravana | Vrishabha, Karka, Tula, Dhanu, Kumbha |
| **`Tithi #07`** (Shukla 07) | Bhadra (Good) | **Sunday** | `Karka, Dhanu` | *Hasta* | Ashwini, Pushya, Uttara Phalguni, Hasta | Mithuna, Simha, Tula, Dhanu, Meena |
| **`Tithi #07`** (Shukla 07) | Bhadra (Good) | **Monday** | `Karka, Dhanu` | *Mrigashirsha* | Rohini, Mrigashirsha, Pushya, Anuradha | Vrishabha, Karka, Kanya, Vrishchika, Kumbha |
| **`Tithi #07`** (Shukla 07) | Bhadra (Good) | **Tuesday** | `Karka, Dhanu` | *Ashwini* | Ashwini, Krittika, Ashlesha, Uttara Bhadrapada | Mesha, Mithuna, Simha, Tula, Makara, Meena |
| **`Tithi #07`** (Shukla 07) | Bhadra (Good) | **Wednesday** | `Karka, Dhanu` | *Anuradha* | Krittika, Rohini, Mrigashirsha, Hasta | Vrishabha, Karka, Kanya, Dhanu, Kumbha |
| **`Tithi #07`** (Shukla 07) | Bhadra (Good) | **Thursday** | `Karka, Dhanu` | *Pushya* | Ashwini, Punarvasu, Pushya, Anuradha | Mesha, Mithuna, Simha, Vrishchika, Makara, Meena |
| **`Tithi #07`** (Shukla 07) | Bhadra (Good) | **Friday** | `Karka, Dhanu` | *Revati* | Ashwini, Punarvasu, Anuradha, Shravana | Vrishabha, Karka, Tula, Dhanu, Kumbha |
| **`Tithi #07`** (Shukla 07) | Bhadra (Good) | **Saturday** | `Karka, Dhanu` | *Rohini* | Rohini, Swati, Shravana | Mesha, Mithuna, Kanya, Vrishchika, Makara, Meena |
| **`Tithi #08`** (Shukla 08) | Jaya (Victory) | **Sunday** | `Mithuna, Kanya` | *Hasta* | Ashwini, Pushya, Uttara Phalguni, Hasta | Vrishabha, Karka, Kanya, Vrishchika, Kumbha |
| **`Tithi #08`** (Shukla 08) | Jaya (Victory) | **Monday** | `Mithuna, Kanya` | *Mrigashirsha* | Rohini, Mrigashirsha, Pushya, Anuradha | Mesha, Mithuna, Simha, Tula, Makara, Meena |
| **`Tithi #08`** (Shukla 08) | Jaya (Victory) | **Tuesday** | `Mithuna, Kanya` | *Ashwini* | Ashwini, Krittika, Ashlesha, Uttara Bhadrapada | Vrishabha, Karka, Kanya, Dhanu, Kumbha |
| **`Tithi #08`** (Shukla 08) | Jaya (Victory) | **Wednesday** | `Mithuna, Kanya` | *Anuradha* | Krittika, Rohini, Mrigashirsha, Hasta | Mesha, Mithuna, Simha, Vrishchika, Makara, Meena |
| **`Tithi #08`** (Shukla 08) | Jaya (Victory) | **Thursday** | `Mithuna, Kanya` | *Pushya* | Ashwini, Punarvasu, Pushya, Anuradha | Vrishabha, Karka, Tula, Dhanu, Kumbha |
| **`Tithi #08`** (Shukla 08) | Jaya (Victory) | **Friday** | `Mithuna, Kanya` | *Revati* | Ashwini, Punarvasu, Anuradha, Shravana | Mesha, Mithuna, Kanya, Vrishchika, Makara, Meena |
| **`Tithi #08`** (Shukla 08) | Jaya (Victory) | **Saturday** | `Mithuna, Kanya` | *Rohini* | Rohini, Swati, Shravana | Vrishabha, Simha, Tula, Dhanu, Kumbha |
| **`Tithi #09`** (Shukla 09) | Rikta (Empty/Avoid) | **Sunday** | `Simha, Vrishchika` | *Hasta* | Ashwini, Pushya, Uttara Phalguni, Hasta | Mesha, Mithuna, Simha, Tula, Makara, Meena |
| **`Tithi #09`** (Shukla 09) | Rikta (Empty/Avoid) | **Monday** | `Simha, Vrishchika` | *Mrigashirsha* | Rohini, Mrigashirsha, Pushya, Anuradha | Vrishabha, Karka, Kanya, Dhanu, Kumbha |
| **`Tithi #09`** (Shukla 09) | Rikta (Empty/Avoid) | **Tuesday** | `Simha, Vrishchika` | *Ashwini* | Ashwini, Krittika, Ashlesha, Uttara Bhadrapada | Mesha, Mithuna, Simha, Vrishchika, Makara, Meena |
| **`Tithi #09`** (Shukla 09) | Rikta (Empty/Avoid) | **Wednesday** | `Simha, Vrishchika` | *Anuradha* | Krittika, Rohini, Mrigashirsha, Hasta | Vrishabha, Karka, Tula, Dhanu, Kumbha |
| **`Tithi #09`** (Shukla 09) | Rikta (Empty/Avoid) | **Thursday** | `Simha, Vrishchika` | *Pushya* | Ashwini, Punarvasu, Pushya, Anuradha | Mesha, Mithuna, Kanya, Vrishchika, Makara, Meena |
| **`Tithi #09`** (Shukla 09) | Rikta (Empty/Avoid) | **Friday** | `Simha, Vrishchika` | *Revati* | Ashwini, Punarvasu, Anuradha, Shravana | Vrishabha, Simha, Tula, Dhanu, Kumbha |
| **`Tithi #09`** (Shukla 09) | Rikta (Empty/Avoid) | **Saturday** | `Simha, Vrishchika` | *Rohini* | Rohini, Swati, Shravana | Mesha, Karka, Kanya, Vrishchika, Makara |
| **`Tithi #10`** (Shukla 10) | Purna (Fullness) | **Sunday** | `Simha, Vrishchika` | *Hasta* | Ashwini, Pushya, Uttara Phalguni, Hasta | Vrishabha, Karka, Kanya, Dhanu, Kumbha |
| **`Tithi #10`** (Shukla 10) | Purna (Fullness) | **Monday** | `Simha, Vrishchika` | *Mrigashirsha* | Rohini, Mrigashirsha, Pushya, Anuradha | Mesha, Mithuna, Simha, Vrishchika, Makara, Meena |
| **`Tithi #10`** (Shukla 10) | Purna (Fullness) | **Tuesday** | `Simha, Vrishchika` | *Ashwini* | Ashwini, Krittika, Ashlesha, Uttara Bhadrapada | Vrishabha, Karka, Tula, Dhanu, Kumbha |
| **`Tithi #10`** (Shukla 10) | Purna (Fullness) | **Wednesday** | `Simha, Vrishchika` | *Anuradha* | Krittika, Rohini, Mrigashirsha, Hasta | Mesha, Mithuna, Kanya, Vrishchika, Makara, Meena |
| **`Tithi #10`** (Shukla 10) | Purna (Fullness) | **Thursday** | `Simha, Vrishchika` | *Pushya* | Ashwini, Punarvasu, Pushya, Anuradha | Vrishabha, Simha, Tula, Dhanu, Kumbha |
| **`Tithi #10`** (Shukla 10) | Purna (Fullness) | **Friday** | `Simha, Vrishchika` | *Revati* | Ashwini, Punarvasu, Anuradha, Shravana | Mesha, Karka, Kanya, Vrishchika, Makara |
| **`Tithi #10`** (Shukla 10) | Purna (Fullness) | **Saturday** | `Simha, Vrishchika` | *Rohini* | Rohini, Swati, Shravana | Mithuna, Simha, Tula, Dhanu, Meena |
| **`Tithi #11`** (Shukla 11) | Nanda (Joy) | **Sunday** | `Dhanu, Meena` | *Hasta* | Ashwini, Pushya, Uttara Phalguni, Hasta | Mesha, Mithuna, Simha, Vrishchika, Makara, Meena |
| **`Tithi #11`** (Shukla 11) | Nanda (Joy) | **Monday** | `Dhanu, Meena` | *Mrigashirsha* | Rohini, Mrigashirsha, Pushya, Anuradha | Vrishabha, Karka, Tula, Dhanu, Kumbha |
| **`Tithi #11`** (Shukla 11) | Nanda (Joy) | **Tuesday** | `Dhanu, Meena` | *Ashwini* | Ashwini, Krittika, Ashlesha, Uttara Bhadrapada | Mesha, Mithuna, Kanya, Vrishchika, Makara, Meena |
| **`Tithi #11`** (Shukla 11) | Nanda (Joy) | **Wednesday** | `Dhanu, Meena` | *Anuradha* | Krittika, Rohini, Mrigashirsha, Hasta | Vrishabha, Simha, Tula, Dhanu, Kumbha |
| **`Tithi #11`** (Shukla 11) | Nanda (Joy) | **Thursday** | `Dhanu, Meena` | *Pushya* | Ashwini, Punarvasu, Pushya, Anuradha | Mesha, Karka, Kanya, Vrishchika, Makara |
| **`Tithi #11`** (Shukla 11) | Nanda (Joy) | **Friday** | `Dhanu, Meena` | *Revati* | Ashwini, Punarvasu, Anuradha, Shravana | Mithuna, Simha, Tula, Dhanu, Meena |
| **`Tithi #11`** (Shukla 11) | Nanda (Joy) | **Saturday** | `Dhanu, Meena` | *Rohini* | Rohini, Swati, Shravana | Vrishabha, Karka, Kanya, Vrishchika, Kumbha |
| **`Tithi #12`** (Shukla 12) | Bhadra (Good) | **Sunday** | `Tula, Makara` | *Hasta* | Ashwini, Pushya, Uttara Phalguni, Hasta | Vrishabha, Karka, Tula, Dhanu, Kumbha |
| **`Tithi #12`** (Shukla 12) | Bhadra (Good) | **Monday** | `Tula, Makara` | *Mrigashirsha* | Rohini, Mrigashirsha, Pushya, Anuradha | Mesha, Mithuna, Kanya, Vrishchika, Makara, Meena |
| **`Tithi #12`** (Shukla 12) | Bhadra (Good) | **Tuesday** | `Tula, Makara` | *Ashwini* | Ashwini, Krittika, Ashlesha, Uttara Bhadrapada | Vrishabha, Simha, Tula, Dhanu, Kumbha |
| **`Tithi #12`** (Shukla 12) | Bhadra (Good) | **Wednesday** | `Tula, Makara` | *Anuradha* | Krittika, Rohini, Mrigashirsha, Hasta | Mesha, Karka, Kanya, Vrishchika, Makara |
| **`Tithi #12`** (Shukla 12) | Bhadra (Good) | **Thursday** | `Tula, Makara` | *Pushya* | Ashwini, Punarvasu, Pushya, Anuradha | Mithuna, Simha, Tula, Dhanu, Meena |
| **`Tithi #12`** (Shukla 12) | Bhadra (Good) | **Friday** | `Tula, Makara` | *Revati* | Ashwini, Punarvasu, Anuradha, Shravana | Vrishabha, Karka, Kanya, Vrishchika, Kumbha |
| **`Tithi #12`** (Shukla 12) | Bhadra (Good) | **Saturday** | `Tula, Makara` | *Rohini* | Rohini, Swati, Shravana | Mesha, Mithuna, Simha, Tula, Makara, Meena |
| **`Tithi #13`** (Shukla 13) | Jaya (Victory) | **Sunday** | `Vrishabha, Simha` | *Hasta* | Ashwini, Pushya, Uttara Phalguni, Hasta | Mesha, Mithuna, Kanya, Vrishchika, Makara, Meena |
| **`Tithi #13`** (Shukla 13) | Jaya (Victory) | **Monday** | `Vrishabha, Simha` | *Mrigashirsha* | Rohini, Mrigashirsha, Pushya, Anuradha | Vrishabha, Simha, Tula, Dhanu, Kumbha |
| **`Tithi #13`** (Shukla 13) | Jaya (Victory) | **Tuesday** | `Vrishabha, Simha` | *Ashwini* | Ashwini, Krittika, Ashlesha, Uttara Bhadrapada | Mesha, Karka, Kanya, Vrishchika, Makara |
| **`Tithi #13`** (Shukla 13) | Jaya (Victory) | **Wednesday** | `Vrishabha, Simha` | *Anuradha* | Krittika, Rohini, Mrigashirsha, Hasta | Mithuna, Simha, Tula, Dhanu, Meena |
| **`Tithi #13`** (Shukla 13) | Jaya (Victory) | **Thursday** | `Vrishabha, Simha` | *Pushya* | Ashwini, Punarvasu, Pushya, Anuradha | Vrishabha, Karka, Kanya, Vrishchika, Kumbha |
| **`Tithi #13`** (Shukla 13) | Jaya (Victory) | **Friday** | `Vrishabha, Simha` | *Revati* | Ashwini, Punarvasu, Anuradha, Shravana | Mesha, Mithuna, Simha, Tula, Makara, Meena |
| **`Tithi #13`** (Shukla 13) | Jaya (Victory) | **Saturday** | `Vrishabha, Simha` | *Rohini* | Rohini, Swati, Shravana | Vrishabha, Karka, Kanya, Dhanu, Kumbha |
| **`Tithi #14`** (Shukla 14) | Rikta (Empty/Avoid) | **Sunday** | `Mithuna, Kanya, Dhanu, Meena` | *Hasta* | Ashwini, Pushya, Uttara Phalguni, Hasta | Vrishabha, Simha, Tula, Dhanu, Kumbha |
| **`Tithi #14`** (Shukla 14) | Rikta (Empty/Avoid) | **Monday** | `Mithuna, Kanya, Dhanu, Meena` | *Mrigashirsha* | Rohini, Mrigashirsha, Pushya, Anuradha | Mesha, Karka, Kanya, Vrishchika, Makara |
| **`Tithi #14`** (Shukla 14) | Rikta (Empty/Avoid) | **Tuesday** | `Mithuna, Kanya, Dhanu, Meena` | *Ashwini* | Ashwini, Krittika, Ashlesha, Uttara Bhadrapada | Mithuna, Simha, Tula, Dhanu, Meena |
| **`Tithi #14`** (Shukla 14) | Rikta (Empty/Avoid) | **Wednesday** | `Mithuna, Kanya, Dhanu, Meena` | *Anuradha* | Krittika, Rohini, Mrigashirsha, Hasta | Vrishabha, Karka, Kanya, Vrishchika, Kumbha |
| **`Tithi #14`** (Shukla 14) | Rikta (Empty/Avoid) | **Thursday** | `Mithuna, Kanya, Dhanu, Meena` | *Pushya* | Ashwini, Punarvasu, Pushya, Anuradha | Mesha, Mithuna, Simha, Tula, Makara, Meena |
| **`Tithi #14`** (Shukla 14) | Rikta (Empty/Avoid) | **Friday** | `Mithuna, Kanya, Dhanu, Meena` | *Revati* | Ashwini, Punarvasu, Anuradha, Shravana | Vrishabha, Karka, Kanya, Dhanu, Kumbha |
| **`Tithi #14`** (Shukla 14) | Rikta (Empty/Avoid) | **Saturday** | `Mithuna, Kanya, Dhanu, Meena` | *Rohini* | Rohini, Swati, Shravana | Mesha, Mithuna, Simha, Vrishchika, Makara, Meena |
| **`Tithi #15`** (Shukla 15) | Purna (Fullness) | **Sunday** | `None (Shubha)` | *Hasta* | Ashwini, Pushya, Uttara Phalguni, Hasta | Mesha, Karka, Kanya, Vrishchika, Makara |
| **`Tithi #15`** (Shukla 15) | Purna (Fullness) | **Monday** | `None (Shubha)` | *Mrigashirsha* | Rohini, Mrigashirsha, Pushya, Anuradha | Mithuna, Simha, Tula, Dhanu, Meena |
| **`Tithi #15`** (Shukla 15) | Purna (Fullness) | **Tuesday** | `None (Shubha)` | *Ashwini* | Ashwini, Krittika, Ashlesha, Uttara Bhadrapada | Vrishabha, Karka, Kanya, Vrishchika, Kumbha |
| **`Tithi #15`** (Shukla 15) | Purna (Fullness) | **Wednesday** | `None (Shubha)` | *Anuradha* | Krittika, Rohini, Mrigashirsha, Hasta | Mesha, Mithuna, Simha, Tula, Makara, Meena |
| **`Tithi #15`** (Shukla 15) | Purna (Fullness) | **Thursday** | `None (Shubha)` | *Pushya* | Ashwini, Punarvasu, Pushya, Anuradha | Vrishabha, Karka, Kanya, Dhanu, Kumbha |
| **`Tithi #15`** (Shukla 15) | Purna (Fullness) | **Friday** | `None (Shubha)` | *Revati* | Ashwini, Punarvasu, Anuradha, Shravana | Mesha, Mithuna, Simha, Vrishchika, Makara, Meena |
| **`Tithi #15`** (Shukla 15) | Purna (Fullness) | **Saturday** | `None (Shubha)` | *Rohini* | Rohini, Swati, Shravana | Vrishabha, Karka, Tula, Dhanu, Kumbha |
| **`Tithi #16`** (Krishna 01) | Nanda (Joy) | **Sunday** | `Tula, Makara` | *Hasta* | Ashwini, Pushya, Uttara Phalguni, Hasta | Mithuna, Simha, Tula, Dhanu, Meena |
| **`Tithi #16`** (Krishna 01) | Nanda (Joy) | **Monday** | `Tula, Makara` | *Mrigashirsha* | Rohini, Mrigashirsha, Pushya, Anuradha | Vrishabha, Karka, Kanya, Vrishchika, Kumbha |
| **`Tithi #16`** (Krishna 01) | Nanda (Joy) | **Tuesday** | `Tula, Makara` | *Ashwini* | Ashwini, Krittika, Ashlesha, Uttara Bhadrapada | Mesha, Mithuna, Simha, Tula, Makara, Meena |
| **`Tithi #16`** (Krishna 01) | Nanda (Joy) | **Wednesday** | `Tula, Makara` | *Anuradha* | Krittika, Rohini, Mrigashirsha, Hasta | Vrishabha, Karka, Kanya, Dhanu, Kumbha |
| **`Tithi #16`** (Krishna 01) | Nanda (Joy) | **Thursday** | `Tula, Makara` | *Pushya* | Ashwini, Punarvasu, Pushya, Anuradha | Mesha, Mithuna, Simha, Vrishchika, Makara, Meena |
| **`Tithi #16`** (Krishna 01) | Nanda (Joy) | **Friday** | `Tula, Makara` | *Revati* | Ashwini, Punarvasu, Anuradha, Shravana | Vrishabha, Karka, Tula, Dhanu, Kumbha |
| **`Tithi #16`** (Krishna 01) | Nanda (Joy) | **Saturday** | `Tula, Makara` | *Rohini* | Rohini, Swati, Shravana | Mesha, Mithuna, Kanya, Vrishchika, Makara, Meena |
| **`Tithi #17`** (Krishna 02) | Bhadra (Good) | **Sunday** | `Dhanu, Meena` | *Hasta* | Ashwini, Pushya, Uttara Phalguni, Hasta | Vrishabha, Karka, Kanya, Vrishchika, Kumbha |
| **`Tithi #17`** (Krishna 02) | Bhadra (Good) | **Monday** | `Dhanu, Meena` | *Mrigashirsha* | Rohini, Mrigashirsha, Pushya, Anuradha | Mesha, Mithuna, Simha, Tula, Makara, Meena |
| **`Tithi #17`** (Krishna 02) | Bhadra (Good) | **Tuesday** | `Dhanu, Meena` | *Ashwini* | Ashwini, Krittika, Ashlesha, Uttara Bhadrapada | Vrishabha, Karka, Kanya, Dhanu, Kumbha |
| **`Tithi #17`** (Krishna 02) | Bhadra (Good) | **Wednesday** | `Dhanu, Meena` | *Anuradha* | Krittika, Rohini, Mrigashirsha, Hasta | Mesha, Mithuna, Simha, Vrishchika, Makara, Meena |
| **`Tithi #17`** (Krishna 02) | Bhadra (Good) | **Thursday** | `Dhanu, Meena` | *Pushya* | Ashwini, Punarvasu, Pushya, Anuradha | Vrishabha, Karka, Tula, Dhanu, Kumbha |
| **`Tithi #17`** (Krishna 02) | Bhadra (Good) | **Friday** | `Dhanu, Meena` | *Revati* | Ashwini, Punarvasu, Anuradha, Shravana | Mesha, Mithuna, Kanya, Vrishchika, Makara, Meena |
| **`Tithi #17`** (Krishna 02) | Bhadra (Good) | **Saturday** | `Dhanu, Meena` | *Rohini* | Rohini, Swati, Shravana | Vrishabha, Simha, Tula, Dhanu, Kumbha |
| **`Tithi #18`** (Krishna 03) | Jaya (Victory) | **Sunday** | `Simha, Makara` | *Hasta* | Ashwini, Pushya, Uttara Phalguni, Hasta | Mesha, Mithuna, Simha, Tula, Makara, Meena |
| **`Tithi #18`** (Krishna 03) | Jaya (Victory) | **Monday** | `Simha, Makara` | *Mrigashirsha* | Rohini, Mrigashirsha, Pushya, Anuradha | Vrishabha, Karka, Kanya, Dhanu, Kumbha |
| **`Tithi #18`** (Krishna 03) | Jaya (Victory) | **Tuesday** | `Simha, Makara` | *Ashwini* | Ashwini, Krittika, Ashlesha, Uttara Bhadrapada | Mesha, Mithuna, Simha, Vrishchika, Makara, Meena |
| **`Tithi #18`** (Krishna 03) | Jaya (Victory) | **Wednesday** | `Simha, Makara` | *Anuradha* | Krittika, Rohini, Mrigashirsha, Hasta | Vrishabha, Karka, Tula, Dhanu, Kumbha |
| **`Tithi #18`** (Krishna 03) | Jaya (Victory) | **Thursday** | `Simha, Makara` | *Pushya* | Ashwini, Punarvasu, Pushya, Anuradha | Mesha, Mithuna, Kanya, Vrishchika, Makara, Meena |
| **`Tithi #18`** (Krishna 03) | Jaya (Victory) | **Friday** | `Simha, Makara` | *Revati* | Ashwini, Punarvasu, Anuradha, Shravana | Vrishabha, Simha, Tula, Dhanu, Kumbha |
| **`Tithi #18`** (Krishna 03) | Jaya (Victory) | **Saturday** | `Simha, Makara` | *Rohini* | Rohini, Swati, Shravana | Mesha, Karka, Kanya, Vrishchika, Makara |
| **`Tithi #19`** (Krishna 04) | Rikta (Empty/Avoid) | **Sunday** | `Vrishabha, Kumbha` | *Hasta* | Ashwini, Pushya, Uttara Phalguni, Hasta | Vrishabha, Karka, Kanya, Dhanu, Kumbha |
| **`Tithi #19`** (Krishna 04) | Rikta (Empty/Avoid) | **Monday** | `Vrishabha, Kumbha` | *Mrigashirsha* | Rohini, Mrigashirsha, Pushya, Anuradha | Mesha, Mithuna, Simha, Vrishchika, Makara, Meena |
| **`Tithi #19`** (Krishna 04) | Rikta (Empty/Avoid) | **Tuesday** | `Vrishabha, Kumbha` | *Ashwini* | Ashwini, Krittika, Ashlesha, Uttara Bhadrapada | Vrishabha, Karka, Tula, Dhanu, Kumbha |
| **`Tithi #19`** (Krishna 04) | Rikta (Empty/Avoid) | **Wednesday** | `Vrishabha, Kumbha` | *Anuradha* | Krittika, Rohini, Mrigashirsha, Hasta | Mesha, Mithuna, Kanya, Vrishchika, Makara, Meena |
| **`Tithi #19`** (Krishna 04) | Rikta (Empty/Avoid) | **Thursday** | `Vrishabha, Kumbha` | *Pushya* | Ashwini, Punarvasu, Pushya, Anuradha | Vrishabha, Simha, Tula, Dhanu, Kumbha |
| **`Tithi #19`** (Krishna 04) | Rikta (Empty/Avoid) | **Friday** | `Vrishabha, Kumbha` | *Revati* | Ashwini, Punarvasu, Anuradha, Shravana | Mesha, Karka, Kanya, Vrishchika, Makara |
| **`Tithi #19`** (Krishna 04) | Rikta (Empty/Avoid) | **Saturday** | `Vrishabha, Kumbha` | *Rohini* | Rohini, Swati, Shravana | Mithuna, Simha, Tula, Dhanu, Meena |
| **`Tithi #20`** (Krishna 05) | Purna (Fullness) | **Sunday** | `Mithuna, Kanya` | *Hasta* | Ashwini, Pushya, Uttara Phalguni, Hasta | Mesha, Mithuna, Simha, Vrishchika, Makara, Meena |
| **`Tithi #20`** (Krishna 05) | Purna (Fullness) | **Monday** | `Mithuna, Kanya` | *Mrigashirsha* | Rohini, Mrigashirsha, Pushya, Anuradha | Vrishabha, Karka, Tula, Dhanu, Kumbha |
| **`Tithi #20`** (Krishna 05) | Purna (Fullness) | **Tuesday** | `Mithuna, Kanya` | *Ashwini* | Ashwini, Krittika, Ashlesha, Uttara Bhadrapada | Mesha, Mithuna, Kanya, Vrishchika, Makara, Meena |
| **`Tithi #20`** (Krishna 05) | Purna (Fullness) | **Wednesday** | `Mithuna, Kanya` | *Anuradha* | Krittika, Rohini, Mrigashirsha, Hasta | Vrishabha, Simha, Tula, Dhanu, Kumbha |
| **`Tithi #20`** (Krishna 05) | Purna (Fullness) | **Thursday** | `Mithuna, Kanya` | *Pushya* | Ashwini, Punarvasu, Pushya, Anuradha | Mesha, Karka, Kanya, Vrishchika, Makara |
| **`Tithi #20`** (Krishna 05) | Purna (Fullness) | **Friday** | `Mithuna, Kanya` | *Revati* | Ashwini, Punarvasu, Anuradha, Shravana | Mithuna, Simha, Tula, Dhanu, Meena |
| **`Tithi #20`** (Krishna 05) | Purna (Fullness) | **Saturday** | `Mithuna, Kanya` | *Rohini* | Rohini, Swati, Shravana | Vrishabha, Karka, Kanya, Vrishchika, Kumbha |
| **`Tithi #21`** (Krishna 06) | Nanda (Joy) | **Sunday** | `Mesha, Simha` | *Hasta* | Ashwini, Pushya, Uttara Phalguni, Hasta | Vrishabha, Karka, Tula, Dhanu, Kumbha |
| **`Tithi #21`** (Krishna 06) | Nanda (Joy) | **Monday** | `Mesha, Simha` | *Mrigashirsha* | Rohini, Mrigashirsha, Pushya, Anuradha | Mesha, Mithuna, Kanya, Vrishchika, Makara, Meena |
| **`Tithi #21`** (Krishna 06) | Nanda (Joy) | **Tuesday** | `Mesha, Simha` | *Ashwini* | Ashwini, Krittika, Ashlesha, Uttara Bhadrapada | Vrishabha, Simha, Tula, Dhanu, Kumbha |
| **`Tithi #21`** (Krishna 06) | Nanda (Joy) | **Wednesday** | `Mesha, Simha` | *Anuradha* | Krittika, Rohini, Mrigashirsha, Hasta | Mesha, Karka, Kanya, Vrishchika, Makara |
| **`Tithi #21`** (Krishna 06) | Nanda (Joy) | **Thursday** | `Mesha, Simha` | *Pushya* | Ashwini, Punarvasu, Pushya, Anuradha | Mithuna, Simha, Tula, Dhanu, Meena |
| **`Tithi #21`** (Krishna 06) | Nanda (Joy) | **Friday** | `Mesha, Simha` | *Revati* | Ashwini, Punarvasu, Anuradha, Shravana | Vrishabha, Karka, Kanya, Vrishchika, Kumbha |
| **`Tithi #21`** (Krishna 06) | Nanda (Joy) | **Saturday** | `Mesha, Simha` | *Rohini* | Rohini, Swati, Shravana | Mesha, Mithuna, Simha, Tula, Makara, Meena |
| **`Tithi #22`** (Krishna 07) | Bhadra (Good) | **Sunday** | `Karka, Dhanu` | *Hasta* | Ashwini, Pushya, Uttara Phalguni, Hasta | Mesha, Mithuna, Kanya, Vrishchika, Makara, Meena |
| **`Tithi #22`** (Krishna 07) | Bhadra (Good) | **Monday** | `Karka, Dhanu` | *Mrigashirsha* | Rohini, Mrigashirsha, Pushya, Anuradha | Vrishabha, Simha, Tula, Dhanu, Kumbha |
| **`Tithi #22`** (Krishna 07) | Bhadra (Good) | **Tuesday** | `Karka, Dhanu` | *Ashwini* | Ashwini, Krittika, Ashlesha, Uttara Bhadrapada | Mesha, Karka, Kanya, Vrishchika, Makara |
| **`Tithi #22`** (Krishna 07) | Bhadra (Good) | **Wednesday** | `Karka, Dhanu` | *Anuradha* | Krittika, Rohini, Mrigashirsha, Hasta | Mithuna, Simha, Tula, Dhanu, Meena |
| **`Tithi #22`** (Krishna 07) | Bhadra (Good) | **Thursday** | `Karka, Dhanu` | *Pushya* | Ashwini, Punarvasu, Pushya, Anuradha | Vrishabha, Karka, Kanya, Vrishchika, Kumbha |
| **`Tithi #22`** (Krishna 07) | Bhadra (Good) | **Friday** | `Karka, Dhanu` | *Revati* | Ashwini, Punarvasu, Anuradha, Shravana | Mesha, Mithuna, Simha, Tula, Makara, Meena |
| **`Tithi #22`** (Krishna 07) | Bhadra (Good) | **Saturday** | `Karka, Dhanu` | *Rohini* | Rohini, Swati, Shravana | Vrishabha, Karka, Kanya, Dhanu, Kumbha |
| **`Tithi #23`** (Krishna 08) | Jaya (Victory) | **Sunday** | `Mithuna, Kanya` | *Hasta* | Ashwini, Pushya, Uttara Phalguni, Hasta | Vrishabha, Simha, Tula, Dhanu, Kumbha |
| **`Tithi #23`** (Krishna 08) | Jaya (Victory) | **Monday** | `Mithuna, Kanya` | *Mrigashirsha* | Rohini, Mrigashirsha, Pushya, Anuradha | Mesha, Karka, Kanya, Vrishchika, Makara |
| **`Tithi #23`** (Krishna 08) | Jaya (Victory) | **Tuesday** | `Mithuna, Kanya` | *Ashwini* | Ashwini, Krittika, Ashlesha, Uttara Bhadrapada | Mithuna, Simha, Tula, Dhanu, Meena |
| **`Tithi #23`** (Krishna 08) | Jaya (Victory) | **Wednesday** | `Mithuna, Kanya` | *Anuradha* | Krittika, Rohini, Mrigashirsha, Hasta | Vrishabha, Karka, Kanya, Vrishchika, Kumbha |
| **`Tithi #23`** (Krishna 08) | Jaya (Victory) | **Thursday** | `Mithuna, Kanya` | *Pushya* | Ashwini, Punarvasu, Pushya, Anuradha | Mesha, Mithuna, Simha, Tula, Makara, Meena |
| **`Tithi #23`** (Krishna 08) | Jaya (Victory) | **Friday** | `Mithuna, Kanya` | *Revati* | Ashwini, Punarvasu, Anuradha, Shravana | Vrishabha, Karka, Kanya, Dhanu, Kumbha |
| **`Tithi #23`** (Krishna 08) | Jaya (Victory) | **Saturday** | `Mithuna, Kanya` | *Rohini* | Rohini, Swati, Shravana | Mesha, Mithuna, Simha, Vrishchika, Makara, Meena |
| **`Tithi #24`** (Krishna 09) | Rikta (Empty/Avoid) | **Sunday** | `Simha, Vrishchika` | *Hasta* | Ashwini, Pushya, Uttara Phalguni, Hasta | Mesha, Karka, Kanya, Vrishchika, Makara |
| **`Tithi #24`** (Krishna 09) | Rikta (Empty/Avoid) | **Monday** | `Simha, Vrishchika` | *Mrigashirsha* | Rohini, Mrigashirsha, Pushya, Anuradha | Mithuna, Simha, Tula, Dhanu, Meena |
| **`Tithi #24`** (Krishna 09) | Rikta (Empty/Avoid) | **Tuesday** | `Simha, Vrishchika` | *Ashwini* | Ashwini, Krittika, Ashlesha, Uttara Bhadrapada | Vrishabha, Karka, Kanya, Vrishchika, Kumbha |
| **`Tithi #24`** (Krishna 09) | Rikta (Empty/Avoid) | **Wednesday** | `Simha, Vrishchika` | *Anuradha* | Krittika, Rohini, Mrigashirsha, Hasta | Mesha, Mithuna, Simha, Tula, Makara, Meena |
| **`Tithi #24`** (Krishna 09) | Rikta (Empty/Avoid) | **Thursday** | `Simha, Vrishchika` | *Pushya* | Ashwini, Punarvasu, Pushya, Anuradha | Vrishabha, Karka, Kanya, Dhanu, Kumbha |
| **`Tithi #24`** (Krishna 09) | Rikta (Empty/Avoid) | **Friday** | `Simha, Vrishchika` | *Revati* | Ashwini, Punarvasu, Anuradha, Shravana | Mesha, Mithuna, Simha, Vrishchika, Makara, Meena |
| **`Tithi #24`** (Krishna 09) | Rikta (Empty/Avoid) | **Saturday** | `Simha, Vrishchika` | *Rohini* | Rohini, Swati, Shravana | Vrishabha, Karka, Tula, Dhanu, Kumbha |
| **`Tithi #25`** (Krishna 10) | Purna (Fullness) | **Sunday** | `Simha, Vrishchika` | *Hasta* | Ashwini, Pushya, Uttara Phalguni, Hasta | Mithuna, Simha, Tula, Dhanu, Meena |
| **`Tithi #25`** (Krishna 10) | Purna (Fullness) | **Monday** | `Simha, Vrishchika` | *Mrigashirsha* | Rohini, Mrigashirsha, Pushya, Anuradha | Vrishabha, Karka, Kanya, Vrishchika, Kumbha |
| **`Tithi #25`** (Krishna 10) | Purna (Fullness) | **Tuesday** | `Simha, Vrishchika` | *Ashwini* | Ashwini, Krittika, Ashlesha, Uttara Bhadrapada | Mesha, Mithuna, Simha, Tula, Makara, Meena |
| **`Tithi #25`** (Krishna 10) | Purna (Fullness) | **Wednesday** | `Simha, Vrishchika` | *Anuradha* | Krittika, Rohini, Mrigashirsha, Hasta | Vrishabha, Karka, Kanya, Dhanu, Kumbha |
| **`Tithi #25`** (Krishna 10) | Purna (Fullness) | **Thursday** | `Simha, Vrishchika` | *Pushya* | Ashwini, Punarvasu, Pushya, Anuradha | Mesha, Mithuna, Simha, Vrishchika, Makara, Meena |
| **`Tithi #25`** (Krishna 10) | Purna (Fullness) | **Friday** | `Simha, Vrishchika` | *Revati* | Ashwini, Punarvasu, Anuradha, Shravana | Vrishabha, Karka, Tula, Dhanu, Kumbha |
| **`Tithi #25`** (Krishna 10) | Purna (Fullness) | **Saturday** | `Simha, Vrishchika` | *Rohini* | Rohini, Swati, Shravana | Mesha, Mithuna, Kanya, Vrishchika, Makara, Meena |
| **`Tithi #26`** (Krishna 11) | Nanda (Joy) | **Sunday** | `Dhanu, Meena` | *Hasta* | Ashwini, Pushya, Uttara Phalguni, Hasta | Vrishabha, Karka, Kanya, Vrishchika, Kumbha |
| **`Tithi #26`** (Krishna 11) | Nanda (Joy) | **Monday** | `Dhanu, Meena` | *Mrigashirsha* | Rohini, Mrigashirsha, Pushya, Anuradha | Mesha, Mithuna, Simha, Tula, Makara, Meena |
| **`Tithi #26`** (Krishna 11) | Nanda (Joy) | **Tuesday** | `Dhanu, Meena` | *Ashwini* | Ashwini, Krittika, Ashlesha, Uttara Bhadrapada | Vrishabha, Karka, Kanya, Dhanu, Kumbha |
| **`Tithi #26`** (Krishna 11) | Nanda (Joy) | **Wednesday** | `Dhanu, Meena` | *Anuradha* | Krittika, Rohini, Mrigashirsha, Hasta | Mesha, Mithuna, Simha, Vrishchika, Makara, Meena |
| **`Tithi #26`** (Krishna 11) | Nanda (Joy) | **Thursday** | `Dhanu, Meena` | *Pushya* | Ashwini, Punarvasu, Pushya, Anuradha | Vrishabha, Karka, Tula, Dhanu, Kumbha |
| **`Tithi #26`** (Krishna 11) | Nanda (Joy) | **Friday** | `Dhanu, Meena` | *Revati* | Ashwini, Punarvasu, Anuradha, Shravana | Mesha, Mithuna, Kanya, Vrishchika, Makara, Meena |
| **`Tithi #26`** (Krishna 11) | Nanda (Joy) | **Saturday** | `Dhanu, Meena` | *Rohini* | Rohini, Swati, Shravana | Vrishabha, Simha, Tula, Dhanu, Kumbha |
| **`Tithi #27`** (Krishna 12) | Bhadra (Good) | **Sunday** | `Tula, Makara` | *Hasta* | Ashwini, Pushya, Uttara Phalguni, Hasta | Mesha, Mithuna, Simha, Tula, Makara, Meena |
| **`Tithi #27`** (Krishna 12) | Bhadra (Good) | **Monday** | `Tula, Makara` | *Mrigashirsha* | Rohini, Mrigashirsha, Pushya, Anuradha | Vrishabha, Karka, Kanya, Dhanu, Kumbha |
| **`Tithi #27`** (Krishna 12) | Bhadra (Good) | **Tuesday** | `Tula, Makara` | *Ashwini* | Ashwini, Krittika, Ashlesha, Uttara Bhadrapada | Mesha, Mithuna, Simha, Vrishchika, Makara, Meena |
| **`Tithi #27`** (Krishna 12) | Bhadra (Good) | **Wednesday** | `Tula, Makara` | *Anuradha* | Krittika, Rohini, Mrigashirsha, Hasta | Vrishabha, Karka, Tula, Dhanu, Kumbha |
| **`Tithi #27`** (Krishna 12) | Bhadra (Good) | **Thursday** | `Tula, Makara` | *Pushya* | Ashwini, Punarvasu, Pushya, Anuradha | Mesha, Mithuna, Kanya, Vrishchika, Makara, Meena |
| **`Tithi #27`** (Krishna 12) | Bhadra (Good) | **Friday** | `Tula, Makara` | *Revati* | Ashwini, Punarvasu, Anuradha, Shravana | Vrishabha, Simha, Tula, Dhanu, Kumbha |
| **`Tithi #27`** (Krishna 12) | Bhadra (Good) | **Saturday** | `Tula, Makara` | *Rohini* | Rohini, Swati, Shravana | Mesha, Karka, Kanya, Vrishchika, Makara |
| **`Tithi #28`** (Krishna 13) | Jaya (Victory) | **Sunday** | `Vrishabha, Simha` | *Hasta* | Ashwini, Pushya, Uttara Phalguni, Hasta | Vrishabha, Karka, Kanya, Dhanu, Kumbha |
| **`Tithi #28`** (Krishna 13) | Jaya (Victory) | **Monday** | `Vrishabha, Simha` | *Mrigashirsha* | Rohini, Mrigashirsha, Pushya, Anuradha | Mesha, Mithuna, Simha, Vrishchika, Makara, Meena |
| **`Tithi #28`** (Krishna 13) | Jaya (Victory) | **Tuesday** | `Vrishabha, Simha` | *Ashwini* | Ashwini, Krittika, Ashlesha, Uttara Bhadrapada | Vrishabha, Karka, Tula, Dhanu, Kumbha |
| **`Tithi #28`** (Krishna 13) | Jaya (Victory) | **Wednesday** | `Vrishabha, Simha` | *Anuradha* | Krittika, Rohini, Mrigashirsha, Hasta | Mesha, Mithuna, Kanya, Vrishchika, Makara, Meena |
| **`Tithi #28`** (Krishna 13) | Jaya (Victory) | **Thursday** | `Vrishabha, Simha` | *Pushya* | Ashwini, Punarvasu, Pushya, Anuradha | Vrishabha, Simha, Tula, Dhanu, Kumbha |
| **`Tithi #28`** (Krishna 13) | Jaya (Victory) | **Friday** | `Vrishabha, Simha` | *Revati* | Ashwini, Punarvasu, Anuradha, Shravana | Mesha, Karka, Kanya, Vrishchika, Makara |
| **`Tithi #28`** (Krishna 13) | Jaya (Victory) | **Saturday** | `Vrishabha, Simha` | *Rohini* | Rohini, Swati, Shravana | Mithuna, Simha, Tula, Dhanu, Meena |
| **`Tithi #29`** (Krishna 14) | Rikta (Empty/Avoid) | **Sunday** | `Mithuna, Kanya, Dhanu, Meena` | *Hasta* | Ashwini, Pushya, Uttara Phalguni, Hasta | Mesha, Mithuna, Simha, Vrishchika, Makara, Meena |
| **`Tithi #29`** (Krishna 14) | Rikta (Empty/Avoid) | **Monday** | `Mithuna, Kanya, Dhanu, Meena` | *Mrigashirsha* | Rohini, Mrigashirsha, Pushya, Anuradha | Vrishabha, Karka, Tula, Dhanu, Kumbha |
| **`Tithi #29`** (Krishna 14) | Rikta (Empty/Avoid) | **Tuesday** | `Mithuna, Kanya, Dhanu, Meena` | *Ashwini* | Ashwini, Krittika, Ashlesha, Uttara Bhadrapada | Mesha, Mithuna, Kanya, Vrishchika, Makara, Meena |
| **`Tithi #29`** (Krishna 14) | Rikta (Empty/Avoid) | **Wednesday** | `Mithuna, Kanya, Dhanu, Meena` | *Anuradha* | Krittika, Rohini, Mrigashirsha, Hasta | Vrishabha, Simha, Tula, Dhanu, Kumbha |
| **`Tithi #29`** (Krishna 14) | Rikta (Empty/Avoid) | **Thursday** | `Mithuna, Kanya, Dhanu, Meena` | *Pushya* | Ashwini, Punarvasu, Pushya, Anuradha | Mesha, Karka, Kanya, Vrishchika, Makara |
| **`Tithi #29`** (Krishna 14) | Rikta (Empty/Avoid) | **Friday** | `Mithuna, Kanya, Dhanu, Meena` | *Revati* | Ashwini, Punarvasu, Anuradha, Shravana | Mithuna, Simha, Tula, Dhanu, Meena |
| **`Tithi #29`** (Krishna 14) | Rikta (Empty/Avoid) | **Saturday** | `Mithuna, Kanya, Dhanu, Meena` | *Rohini* | Rohini, Swati, Shravana | Vrishabha, Karka, Kanya, Vrishchika, Kumbha |
| **`Tithi #30`** (Krishna 15) | Purna (Fullness) | **Sunday** | `None (Shubha)` | *Hasta* | Ashwini, Pushya, Uttara Phalguni, Hasta | Vrishabha, Karka, Tula, Dhanu, Kumbha |
| **`Tithi #30`** (Krishna 15) | Purna (Fullness) | **Monday** | `None (Shubha)` | *Mrigashirsha* | Rohini, Mrigashirsha, Pushya, Anuradha | Mesha, Mithuna, Kanya, Vrishchika, Makara, Meena |
| **`Tithi #30`** (Krishna 15) | Purna (Fullness) | **Tuesday** | `None (Shubha)` | *Ashwini* | Ashwini, Krittika, Ashlesha, Uttara Bhadrapada | Vrishabha, Simha, Tula, Dhanu, Kumbha |
| **`Tithi #30`** (Krishna 15) | Purna (Fullness) | **Wednesday** | `None (Shubha)` | *Anuradha* | Krittika, Rohini, Mrigashirsha, Hasta | Mesha, Karka, Kanya, Vrishchika, Makara |
| **`Tithi #30`** (Krishna 15) | Purna (Fullness) | **Thursday** | `None (Shubha)` | *Pushya* | Ashwini, Punarvasu, Pushya, Anuradha | Mithuna, Simha, Tula, Dhanu, Meena |
| **`Tithi #30`** (Krishna 15) | Purna (Fullness) | **Friday** | `None (Shubha)` | *Revati* | Ashwini, Punarvasu, Anuradha, Shravana | Vrishabha, Karka, Kanya, Vrishchika, Kumbha |
| **`Tithi #30`** (Krishna 15) | Purna (Fullness) | **Saturday** | `None (Shubha)` | *Rohini* | Rohini, Swati, Shravana | Mesha, Mithuna, Simha, Tula, Makara, Meena |

## Chapter 29 — Continuous Sinusoidal *Uchcha-Neecha* Exaltation Potential, *Arohi/Avarohi* Orbital Climb Velocity, 3D *Digbala*, & *Surya Siddhanta Kalansha* Heliacal Phenomena

> **Why Continuous Dignity Replaces Binary Lookup Tables:** Traditional software treats exaltation (*Uchcha*) as a step function by sign. RDG evaluates both the classical linear *Uchcha Bala* (`0..60 Virupas`) and the smooth harmonic potential `U(lambda) = 50 * (1 + cos(lambda - lambda_uchcha))` along with its exact time derivative `dU/dt` (*Arohi* ascending toward exaltation vs. *Avarohi* descending toward debilitation) and exact *Surya Siddhanta Kalansha* heliacal rising (*Udaya*) and setting (*Asta*) crossings.

### 29.1 Worked Case Study: 9-Graha Continuous *Uchcha* Potential, *Arohi/Avarohi* Gradient, 3D *Digbala*, & Heliacal State (`Chart Uchcha Harmony = 32.76/100`)

| Graha | Sidereal Lon (`deg`) | Speed (`deg/d`) | Deep Exaltation (`deg`) | *Uchcha* Potential (`0..100`) | *Uchcha Bala* (`0..60v`) | *Arohi / Avarohi* Climb State | `dU/dt` (`/day`) | Peak *Digbala* House | *Digbala* (`0..60v`) | Solar Elongation | *Kalansha* Limit | Heliacal Visibility & Nearest Crossing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Sun** | `208.6140°` | `+1.0071°` | `10.0°` | **`2.62`** | `6.20v` | `AROHI_ASCENDING_TO_EXALTATION` | `+0.2805` | `10H` | `52.45v` | `0.00°` | `0.0°` | **SOLAR_SOURCE** (None in ±45d) |
| **Moon** | `273.6943°` | `+11.8154°` | `33.0°` | **`25.53`** | `20.23v` | `AROHI_ASCENDING_TO_EXALTATION` | `+8.9913` | `4H` | `29.24v` | `65.08°` | `12.0°` | **VISIBLE_UDAYA** (None in ±45d) |
| **Mars** | `121.1842°` | `+0.4500°` | `298.0°` | **`0.08`** | `1.06v` | `AROHI_ASCENDING_TO_EXALTATION` | `+0.0218` | `10H` | `38.41v` | `87.43°` | `17.0°` | **VISIBLE_UDAYA** (None in ±45d) |
| **Mercury** | `191.0171°` | `+0.2763°` | `165.0°` | **`94.93`** | `51.33v` | `AVAROHI_DESCENDING_TO_DEBILITATION` | `-0.1058` | `1H` | `36.24v` | `17.60°` | `14.0°` | **VISIBLE_UDAYA** (HELIACAL_RISING_UDAYA @ `2026-11-10T10:24:09Z`) |
| **Jupiter** | `121.5663°` | `+0.0852°` | `95.0°` | **`94.72`** | `51.14v` | `AVAROHI_DESCENDING_TO_DEBILITATION` | `-0.0332` | `1H` | `13.09v` | `87.05°` | `11.0°` | **VISIBLE_UDAYA** (None in ±45d) |
| **Venus** | `178.6575°` | `+0.0476°` | `357.0°` | **`0.02`** | `0.55v` | `AROHI_ASCENDING_TO_EXALTATION` | `+0.0012` | `4H` | `2.44v` | `29.96°` | `10.0°` | **VISIBLE_UDAYA** (HELIACAL_RISING_UDAYA @ `2026-10-29T04:09:57Z`) |
| **Saturn** | `344.2830°` | `-0.0441°` | `200.0°` | **`9.40`** | `11.91v` | `AROHI_ASCENDING_TO_EXALTATION` | `+0.0225` | `7H` | `27.33v` | `135.67°` | `15.0°` | **VISIBLE_UDAYA** (None in ±45d) |
| **Rahu** | `301.0860°` | `-0.0530°` | `50.0°` | **`33.79`** | `23.70v` | `AVAROHI_DESCENDING_TO_DEBILITATION` | `-0.0437` | `1H` | `47.07v` | `92.47°` | `0.0°` | **SHADOW_NODE_EXEMPT** (None in ±45d) |
| **Ketu** | `121.0860°` | `-0.0530°` | `230.0°` | **`33.79`** | `23.70v` | `AVAROHI_DESCENDING_TO_DEBILITATION` | `-0.0437` | `1H` | `12.93v` | `87.53°` | `0.0°` | **SHADOW_NODE_EXEMPT** (None in ±45d) |

### 29.2 Complete 36-Row (`0°` to `350°` in `10°` Steps) Manual *Uchcha-Neecha* Harmonic Potential & *Arohi/Avarohi* Lookup Reckoner

| Angular Offset `Δλ = λ - λ_uchcha` | Absolute Distance `|Δλ|` | Classical *Uchcha Bala* (`(180 - |Δλ|)/3` Virupas) | Harmonic Potential `50*(1 + cos Δλ)` (`0..100`) | Orbital Climb Phase (Direct Motion `v > 0`) | Orbital Climb Phase (Retrograde Motion `v < 0`) |
|---|---|---|---|---|---|
| **`000°`** (`+0°`) | `0°` | **`60.00 Virupas`** | **`100.00 / 100`** | PEAK / NADIR | PEAK / NADIR |
| **`010°`** (`+10°`) | `10°` | **`56.67 Virupas`** | **`99.24 / 100`** | AVAROHI (Descending to Neecha) | AROHI (Retrograde Climb) |
| **`020°`** (`+20°`) | `20°` | **`53.33 Virupas`** | **`96.98 / 100`** | AVAROHI (Descending to Neecha) | AROHI (Retrograde Climb) |
| **`030°`** (`+30°`) | `30°` | **`50.00 Virupas`** | **`93.30 / 100`** | AVAROHI (Descending to Neecha) | AROHI (Retrograde Climb) |
| **`040°`** (`+40°`) | `40°` | **`46.67 Virupas`** | **`88.30 / 100`** | AVAROHI (Descending to Neecha) | AROHI (Retrograde Climb) |
| **`050°`** (`+50°`) | `50°` | **`43.33 Virupas`** | **`82.14 / 100`** | AVAROHI (Descending to Neecha) | AROHI (Retrograde Climb) |
| **`060°`** (`+60°`) | `60°` | **`40.00 Virupas`** | **`75.00 / 100`** | AVAROHI (Descending to Neecha) | AROHI (Retrograde Climb) |
| **`070°`** (`+70°`) | `70°` | **`36.67 Virupas`** | **`67.10 / 100`** | AVAROHI (Descending to Neecha) | AROHI (Retrograde Climb) |
| **`080°`** (`+80°`) | `80°` | **`33.33 Virupas`** | **`58.68 / 100`** | AVAROHI (Descending to Neecha) | AROHI (Retrograde Climb) |
| **`090°`** (`+90°`) | `90°` | **`30.00 Virupas`** | **`50.00 / 100`** | AVAROHI (Descending to Neecha) | AROHI (Retrograde Climb) |
| **`100°`** (`+100°`) | `100°` | **`26.67 Virupas`** | **`41.32 / 100`** | AVAROHI (Descending to Neecha) | AROHI (Retrograde Climb) |
| **`110°`** (`+110°`) | `110°` | **`23.33 Virupas`** | **`32.90 / 100`** | AVAROHI (Descending to Neecha) | AROHI (Retrograde Climb) |
| **`120°`** (`+120°`) | `120°` | **`20.00 Virupas`** | **`25.00 / 100`** | AVAROHI (Descending to Neecha) | AROHI (Retrograde Climb) |
| **`130°`** (`+130°`) | `130°` | **`16.67 Virupas`** | **`17.86 / 100`** | AVAROHI (Descending to Neecha) | AROHI (Retrograde Climb) |
| **`140°`** (`+140°`) | `140°` | **`13.33 Virupas`** | **`11.70 / 100`** | AVAROHI (Descending to Neecha) | AROHI (Retrograde Climb) |
| **`150°`** (`+150°`) | `150°` | **`10.00 Virupas`** | **`6.70 / 100`** | AVAROHI (Descending to Neecha) | AROHI (Retrograde Climb) |
| **`160°`** (`+160°`) | `160°` | **`6.67 Virupas`** | **`3.02 / 100`** | AVAROHI (Descending to Neecha) | AROHI (Retrograde Climb) |
| **`170°`** (`+170°`) | `170°` | **`3.33 Virupas`** | **`0.76 / 100`** | AVAROHI (Descending to Neecha) | AROHI (Retrograde Climb) |
| **`180°`** (`-180°`) | `180°` | **`0.00 Virupas`** | **`0.00 / 100`** | PEAK / NADIR | PEAK / NADIR |
| **`190°`** (`-170°`) | `170°` | **`3.33 Virupas`** | **`0.76 / 100`** | AROHI (Ascending to Uchcha) | AVAROHI (Retrograde Descent) |
| **`200°`** (`-160°`) | `160°` | **`6.67 Virupas`** | **`3.02 / 100`** | AROHI (Ascending to Uchcha) | AVAROHI (Retrograde Descent) |
| **`210°`** (`-150°`) | `150°` | **`10.00 Virupas`** | **`6.70 / 100`** | AROHI (Ascending to Uchcha) | AVAROHI (Retrograde Descent) |
| **`220°`** (`-140°`) | `140°` | **`13.33 Virupas`** | **`11.70 / 100`** | AROHI (Ascending to Uchcha) | AVAROHI (Retrograde Descent) |
| **`230°`** (`-130°`) | `130°` | **`16.67 Virupas`** | **`17.86 / 100`** | AROHI (Ascending to Uchcha) | AVAROHI (Retrograde Descent) |
| **`240°`** (`-120°`) | `120°` | **`20.00 Virupas`** | **`25.00 / 100`** | AROHI (Ascending to Uchcha) | AVAROHI (Retrograde Descent) |
| **`250°`** (`-110°`) | `110°` | **`23.33 Virupas`** | **`32.90 / 100`** | AROHI (Ascending to Uchcha) | AVAROHI (Retrograde Descent) |
| **`260°`** (`-100°`) | `100°` | **`26.67 Virupas`** | **`41.32 / 100`** | AROHI (Ascending to Uchcha) | AVAROHI (Retrograde Descent) |
| **`270°`** (`-90°`) | `90°` | **`30.00 Virupas`** | **`50.00 / 100`** | AROHI (Ascending to Uchcha) | AVAROHI (Retrograde Descent) |
| **`280°`** (`-80°`) | `80°` | **`33.33 Virupas`** | **`58.68 / 100`** | AROHI (Ascending to Uchcha) | AVAROHI (Retrograde Descent) |
| **`290°`** (`-70°`) | `70°` | **`36.67 Virupas`** | **`67.10 / 100`** | AROHI (Ascending to Uchcha) | AVAROHI (Retrograde Descent) |
| **`300°`** (`-60°`) | `60°` | **`40.00 Virupas`** | **`75.00 / 100`** | AROHI (Ascending to Uchcha) | AVAROHI (Retrograde Descent) |
| **`310°`** (`-50°`) | `50°` | **`43.33 Virupas`** | **`82.14 / 100`** | AROHI (Ascending to Uchcha) | AVAROHI (Retrograde Descent) |
| **`320°`** (`-40°`) | `40°` | **`46.67 Virupas`** | **`88.30 / 100`** | AROHI (Ascending to Uchcha) | AVAROHI (Retrograde Descent) |
| **`330°`** (`-30°`) | `30°` | **`50.00 Virupas`** | **`93.30 / 100`** | AROHI (Ascending to Uchcha) | AVAROHI (Retrograde Descent) |
| **`340°`** (`-20°`) | `20°` | **`53.33 Virupas`** | **`96.98 / 100`** | AROHI (Ascending to Uchcha) | AVAROHI (Retrograde Descent) |
| **`350°`** (`-10°`) | `10°` | **`56.67 Virupas`** | **`99.24 / 100`** | AROHI (Ascending to Uchcha) | AVAROHI (Retrograde Descent) |

## Chapter 30 — 81-Cell *Sarvatobhadra Trishula* Ray-Tracer, 7-Planet *Shodhya Pinda* Trigger Stars, 12-House *Vitta-Ayavyaya* Wealth Matrix, & Continuous Harmonic *Yoga* Potency

### 30.1 Worked Case Study: 9x9 *Sarvatobhadra Chakra* 3-Way *Trishula Vedha* Ray-Trace (`Net Protection Index = +0.0`, Verdict: Balanced / neutral Sarvatobhadra Chakra ray geometry across natal sensitivity cells.)

| Transiting Graha | Source 28-Star (`Nakshatra`) | Border Grid `(r, c)` | Ray Direction (*Sammukha / Vama / Dakshina*) | Target Cell `(r, c)` | Target Type | Target Label | *Vedha* Nature | Hits Natal *Janma Star / Rashi / Akshara* |
|---|---|---|---|---|---|---|---|---|
| **Sun** | *Vishakha* | `(7, 8)` | `FRONT_SAMMUKHA` | `(7, 0)` | `nakshatra` | **Dhanishta** | `KRURA_MALEFIC_VEDHA` | `Perimeter Nakshatra` |
| **Sun** | *Vishakha* | `(7, 8)` | `LEFT_DIAGONAL_VAMA` | `(8, 7)` | `nakshatra` | **Anuradha** | `KRURA_MALEFIC_VEDHA` | `Perimeter Nakshatra` |
| **Sun** | *Vishakha* | `(7, 8)` | `RIGHT_DIAGONAL_DAKSHINA` | `(0, 1)` | `nakshatra` | **Krittika** | `KRURA_MALEFIC_VEDHA` | `Perimeter Nakshatra` |
| **Moon** | *Uttara Ashadha* | `(8, 3)` | `FRONT_SAMMUKHA` | `(0, 3)` | `nakshatra` | **Mrigashirsha** | `SUBHA_BENEFIC_VEDHA` | `Perimeter Nakshatra` |
| **Moon** | *Uttara Ashadha* | `(8, 3)` | `LEFT_DIAGONAL_VAMA` | `(5, 0)` | `nakshatra` | **Purva Bhadrapada** | `SUBHA_BENEFIC_VEDHA` | `Perimeter Nakshatra` |
| **Moon** | *Uttara Ashadha* | `(8, 3)` | `RIGHT_DIAGONAL_DAKSHINA` | `(3, 8)` | `nakshatra` | **Uttara Phalguni** | `SUBHA_BENEFIC_VEDHA` | `Perimeter Nakshatra` |
| **Mars** | *Magha* | `(1, 8)` | `FRONT_SAMMUKHA` | `(1, 0)` | `nakshatra` | **Bharani** | `KRURA_MALEFIC_VEDHA` | `Perimeter Nakshatra` |
| **Mars** | *Magha* | `(1, 8)` | `LEFT_DIAGONAL_VAMA` | `(8, 1)` | `nakshatra` | **Shravana** | `KRURA_MALEFIC_VEDHA` | `Perimeter Nakshatra` |
| **Mars** | *Magha* | `(1, 8)` | `RIGHT_DIAGONAL_DAKSHINA` | `(0, 7)` | `nakshatra` | **Ashlesha** | `KRURA_MALEFIC_VEDHA` | `Perimeter Nakshatra` |
| **Mercury** | *Swati* | `(6, 8)` | `FRONT_SAMMUKHA` | `(6, 0)` | `nakshatra` | **Shatabhisha** | `SUBHA_BENEFIC_VEDHA` | `Perimeter Nakshatra` |
| **Mercury** | *Swati* | `(6, 8)` | `LEFT_DIAGONAL_VAMA` | `(8, 6)` | `nakshatra` | **Jyeshtha** | `SUBHA_BENEFIC_VEDHA` | `Perimeter Nakshatra` |
| **Mercury** | *Swati* | `(6, 8)` | `RIGHT_DIAGONAL_DAKSHINA` | `(0, 2)` | `nakshatra` | **Rohini** | `SUBHA_BENEFIC_VEDHA` | `Perimeter Nakshatra` |
| **Jupiter** | *Magha* | `(1, 8)` | `FRONT_SAMMUKHA` | `(1, 0)` | `nakshatra` | **Bharani** | `SUBHA_BENEFIC_VEDHA` | `Perimeter Nakshatra` |
| **Jupiter** | *Magha* | `(1, 8)` | `LEFT_DIAGONAL_VAMA` | `(8, 1)` | `nakshatra` | **Shravana** | `SUBHA_BENEFIC_VEDHA` | `Perimeter Nakshatra` |
| **Jupiter** | *Magha* | `(1, 8)` | `RIGHT_DIAGONAL_DAKSHINA` | `(0, 7)` | `nakshatra` | **Ashlesha** | `SUBHA_BENEFIC_VEDHA` | `Perimeter Nakshatra` |
| **Venus** | *Chitra* | `(5, 8)` | `FRONT_SAMMUKHA` | `(5, 2)` | `rasi` | **Makara** | `SUBHA_BENEFIC_VEDHA` | `JANMA_RASHI` |
| **Venus** | *Chitra* | `(5, 8)` | `FRONT_SAMMUKHA` | `(5, 0)` | `nakshatra` | **Purva Bhadrapada** | `SUBHA_BENEFIC_VEDHA` | `Perimeter Nakshatra` |
| **Venus** | *Chitra* | `(5, 8)` | `LEFT_DIAGONAL_VAMA` | `(8, 5)` | `nakshatra` | **Mula** | `SUBHA_BENEFIC_VEDHA` | `Perimeter Nakshatra` |
| **Venus** | *Chitra* | `(5, 8)` | `RIGHT_DIAGONAL_DAKSHINA` | `(0, 3)` | `nakshatra` | **Mrigashirsha** | `SUBHA_BENEFIC_VEDHA` | `Perimeter Nakshatra` |
| **Saturn** | *Uttara Bhadrapada* | `(4, 0)` | `FRONT_SAMMUKHA` | `(4, 8)` | `nakshatra` | **Hasta** | `ATI_VEDHA_RETROGRADE` | `Perimeter Nakshatra` |
| **Saturn** | *Uttara Bhadrapada* | `(4, 0)` | `LEFT_DIAGONAL_VAMA` | `(0, 4)` | `nakshatra` | **Ardra** | `ATI_VEDHA_RETROGRADE` | `Perimeter Nakshatra` |
| **Saturn** | *Uttara Bhadrapada* | `(4, 0)` | `RIGHT_DIAGONAL_DAKSHINA` | `(8, 4)` | `nakshatra` | **Purva Ashadha** | `ATI_VEDHA_RETROGRADE` | `Perimeter Nakshatra` |
| **Rahu** | *Dhanishta* | `(7, 0)` | `FRONT_SAMMUKHA` | `(7, 8)` | `nakshatra` | **Vishakha** | `KRURA_MALEFIC_VEDHA` | `Perimeter Nakshatra` |
| **Rahu** | *Dhanishta* | `(7, 0)` | `LEFT_DIAGONAL_VAMA` | `(5, 2)` | `rasi` | **Makara** | `KRURA_MALEFIC_VEDHA` | `JANMA_RASHI` |
| **Rahu** | *Dhanishta* | `(7, 0)` | `LEFT_DIAGONAL_VAMA` | `(0, 7)` | `nakshatra` | **Ashlesha** | `KRURA_MALEFIC_VEDHA` | `Perimeter Nakshatra` |
| **Rahu** | *Dhanishta* | `(7, 0)` | `RIGHT_DIAGONAL_DAKSHINA` | `(8, 1)` | `nakshatra` | **Shravana** | `KRURA_MALEFIC_VEDHA` | `Perimeter Nakshatra` |
| **Ketu** | *Magha* | `(1, 8)` | `FRONT_SAMMUKHA` | `(1, 0)` | `nakshatra` | **Bharani** | `KRURA_MALEFIC_VEDHA` | `Perimeter Nakshatra` |
| **Ketu** | *Magha* | `(1, 8)` | `LEFT_DIAGONAL_VAMA` | `(8, 1)` | `nakshatra` | **Shravana** | `KRURA_MALEFIC_VEDHA` | `Perimeter Nakshatra` |
| **Ketu** | *Magha* | `(1, 8)` | `RIGHT_DIAGONAL_DAKSHINA` | `(0, 7)` | `nakshatra` | **Ashlesha** | `KRURA_MALEFIC_VEDHA` | `Perimeter Nakshatra` |

### 30.2 Worked Case Study: 7-Planet *Trikona & Ekadhipatya Shodhana*, *Rashi / Graha / Shodhya Pinda*, & 27-Nakshatra Transit Trigger Stars

| Graha | Raw BAV Bindus | *Trikona* Reduced Sum | *Ekadhipatya* Reduced Sum | *Rashi Pinda* | *Graha Pinda* | *Shodhya Pinda* (`S`) | Classical Trigger Star (`(S × 7) mod 27`) | *Lagna-Bindu* Trigger Star | Current Transit Star | Active Trigger Hit |
|---|---|---|---|---|---|---|---|---|---|---|
| **Sun** | `48` | `12` | `8` | `79` | `45` | **`124`** | **#05 Mrigashirsha** | *Shravana* | Vishakha | `No` |
| **Moon** | `49` | `16` | `14` | `104` | `48` | **`152`** | **#12 Uttara Phalguni** | *Swati* | Uttara Ashadha | `No` |
| **Mars** | `39` | `15` | `12` | `119` | `71` | **`190`** | **#08 Pushya** | *Mrigashirsha* | Magha | `No` |
| **Mercury** | `54` | `9` | `7` | `51` | `46` | **`97`** | **#05 Mrigashirsha** | *Purva Phalguni* | Swati | `No` |
| **Jupiter** | `56` | `11` | `11` | `101` | `72` | **`173`** | **#24 Shatabhisha** | *Dhanishta* | Magha | `No` |
| **Venus** | `52` | `13` | `11` | `84` | `25` | **`109`** | **#08 Pushya** | *Pushya* | Chitra | `No` |
| **Saturn** | `39` | `18` | `16` | `120` | `79` | **`199`** | **#17 Anuradha** | *Rohini* | Uttara Bhadrapada | `No` |

### 30.3 Worked Case Study: 12-House *Bandhu / Sevaka / Poshaka / Ghataka* Vitality & *Vitta-Ayavyaya* Wealth Surplus (`Wealth Index = 64.0/100`)

| House (`Bhava`) | Sign (`Rashi`) | SAV Bindus | *Bandhu* (`7th` from House) | *Sevaka* (`6th` from House) | *Poshaka* (`11th` Gains) | *Ghataka* (`12th` Loss) | *Artha* Net Surplus (`Poshaka - Ghataka`) | Prosperity Tier |
|---|---|---|---|---|---|---|---|---|
| **House `01`** | **Dhanu** | **`27`** | `35` | `33` | `27` | `25` | **`+2`** | `MADHYAMA_BALANCED_SUSTENANCE` |
| **House `02`** | **Makara** | **`27`** | `30` | `35` | `25` | `27` | **`-2`** | `KSHINA_HIGH_EXPENDITURE` |
| **House `03`** | **Kumbha** | **`27`** | `30` | `30` | `27` | `27` | **`+0`** | `MADHYAMA_BALANCED_SUSTENANCE` |
| **House `04`** | **Meena** | **`32`** | `24` | `30` | `27` | `27` | **`+0`** | `MADHYAMA_BALANCED_SUSTENANCE` |
| **House `05`** | **Mesha** | **`20`** | `27` | `24` | `27` | `32` | **`-5`** | `KSHINA_HIGH_EXPENDITURE` |
| **House `06`** | **Vrishabha** | **`33`** | `25` | `27` | `32` | `20` | **`+12`** | `UTTAMA_HIGH_ACCUMULATION` |
| **House `07`** | **Mithuna** | **`35`** | `27` | `25` | `20` | `33` | **`-13`** | `MADHYAMA_BALANCED_SUSTENANCE` |
| **House `08`** | **Karka** | **`30`** | `27` | `27` | `33` | `35` | **`-2`** | `MADHYAMA_BALANCED_SUSTENANCE` |
| **House `09`** | **Simha** | **`30`** | `27` | `27` | `35` | `30` | **`+5`** | `UTTAMA_HIGH_ACCUMULATION` |
| **House `10`** | **Kanya** | **`24`** | `32` | `27` | `30` | `30` | **`+0`** | `MADHYAMA_BALANCED_SUSTENANCE` |
| **House `11`** | **Tula** | **`27`** | `20` | `32` | `30` | `24` | **`+6`** | `MADHYAMA_BALANCED_SUSTENANCE` |
| **House `12`** | **Vrishchika** | **`25`** | `33` | `20` | `24` | `27` | **`-3`** | `KSHINA_HIGH_EXPENDITURE` |

### 30.4 Worked Case Study: Continuous Harmonic Phase-Coherence *Yoga* Potency Tensor

| Classical *Yoga* Resonance | Category | Participating Grahas | Exact Separation (`deg`) | Ideal Harmonic (`deg`) | Orb Error (`deg`) | Phase Coherence (`0..100`) | Dignity-Weighted Potency (`0..100`) | Plain-English Effect |
|---|---|---|---|---|---|---|---|---|
| **Lakshmi-Narayana / Shukra-Budha Creative Resonance** | `SHUKRA_BUDHA_HARMONIC` | Venus, Mercury | `12.36°` | `0.0°` | `12.36°` | `21.7` | **`30.7`** | Aesthetic and commercial phase coherence uniting design taste with articulate communication. |
| **Dharma-Karmadhipati / Guru-Shani Structural Resonance** | `GURU_SHANI_HARMONIC` | Jupiter, Saturn | `137.28°` | `120.0°` | `17.28°` | `5.0` | **`21.5`** | Expansion-structure harmonic alignment governing institutional leadership and long-term career architecture. |
| **Gaja-Kesari Harmonic Resonance** | `CHANDRA_GURU_KENDRA` | Moon, Jupiter | `152.13°` | `180.0°` | `27.87°` | `0.0` | **`21.1`** | Continuous 4th-harmonic (Kendra) phase lock between Moon and Jupiter amplifying wisdom and lasting reputation. |
| **Budha-Aditya Solar-Mental Coherence** | `SURYA_BUDHA_YUTI` | Sun, Mercury | `17.60°` | `0.0°` | `17.60°` | `4.5` | **`20.0`** | 1st-harmonic conjunction coherence (peaking outside deep combustion) sharpening analytical intelligence. |
| **Chandra-Mangala Wealth Impulse Resonance** | `CHANDRA_MANGALA_HARMONIC` | Moon, Mars | `152.51°` | `180.0°` | `27.49°` | `0.1` | **`4.5`** | Emotional courage and enterprise execution harmonic driving decisive financial action. |
