"""Regional Indian Almanac Layer: Amanta vs Purnimanta Lunar Months, Regional Solar Calendars, Samvatsara, Ritu, Ayana, and Eclipse Windows.

Implements deterministic regional Panchanga rules across India:
1. Lunar Months (*Chandra Masa*):
   - **Amanta** (New-Moon ending: Maharashtra, Gujarat, Karnataka, Andhra, Telangana)
   - **Purnimanta** (Full-Moon ending: Uttar Pradesh, Bihar, Madhya Pradesh, Rajasthan, Delhi;
     during Krishna Paksha, Purnimanta month is `(amanta_index + 1) % 12`)
   - **Adhika Masa** (*Purushottama Masa*): Detected when two consecutive Amavasyas (New Moons)
     fall within the same sidereal Surya Rashi (no solar Sankranti inside the synodic lunation).
2. Regional Solar Months (*Saura Masa*) & Eras:
   - **Sanskrit Saura:** Mesha .. Meena
   - **Tamil Tirukanitha/Vakya:** Chithirai .. Panguni
   - **Malayalam Kollavarsham:** Medam .. Meenam + Kollam Era
   - **Bengali Panjika:** Boishakh .. Choitro + Bangabda Era
   - **Odia Panji:** Baisakha .. Chaitra
3. 60-Year *Samvatsara* Cycle (`Prabhava` #1 .. `Akshaya` #60), Vikram Samvat, Shaka Samvat, and Kali Era.
4. *Ayana* (`Uttarayana` / `Dakshinayana`), *Ritu* (both Sidereal Vedic and Tropical Drik), and
   active Solar/Lunar Eclipse visibility windows (`find_solar_eclipses`, `find_lunar_eclipses`).
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Mapping

from .._version import __version__
from ..adapter import AnalyticalEphemerisProvider, EphemerisAdapter, FLG_SIDEREAL
from ..engine.eclipses import (
    LunarEclipse,
    SolarEclipse,
    find_lunar_eclipses,
    find_solar_eclipses,
    lunar_eclipse_local_visibility,
    solar_eclipse_local_circumstances,
)
from ..engine.receipt import canonical_hash
from ..jyotish.nakshatra import NAKSHATRA_NAMES, RASI_NAMES
from ..jyotish.panchanga import (
    RITU_CATALOG,
    SAMVATSARA_NAMES,
    compute_ayana_and_ritu,
    compute_panchanga,
    compute_samvatsara,
)

LUNAR_MASA_NAMES: tuple[str, ...] = (
    "Chaitra",
    "Vaishakha",
    "Jyeshtha",
    "Ashadha",
    "Shravana",
    "Bhadrapada",
    "Ashwin",
    "Kartika",
    "Margashirsha",
    "Pausha",
    "Magha",
    "Phalguna",
)

TAMIL_SOLAR_MONTHS: tuple[str, ...] = (
    "Chithirai",
    "Vaikasi",
    "Aani",
    "Aadi",
    "Avani",
    "Purattasi",
    "Aippasi",
    "Karthigai",
    "Margazhi",
    "Thai",
    "Maasi",
    "Panguni",
)

MALAYALAM_SOLAR_MONTHS: tuple[str, ...] = (
    "Medam",
    "Edavam",
    "Mithunam",
    "Karkidakam",
    "Chingam",
    "Kanni",
    "Thulam",
    "Vrischikam",
    "Dhanu",
    "Makaram",
    "Kumbham",
    "Meenam",
)

BENGALI_SOLAR_MONTHS: tuple[str, ...] = (
    "Boishakh",
    "Joishtho",
    "Asharh",
    "Shrabon",
    "Bhadro",
    "Ashwin",
    "Kartik",
    "Ogrohayon",
    "Poush",
    "Magh",
    "Falgun",
    "Choitro",
)

ODIA_SOLAR_MONTHS: tuple[str, ...] = (
    "Baisakha",
    "Jyestha",
    "Ashadha",
    "Shravana",
    "Bhadra",
    "Ashwina",
    "Kartika",
    "Margashira",
    "Pausha",
    "Magha",
    "Phalguna",
    "Chaitra",
)


@dataclass(frozen=True)
class LunarMonthInfo:
    """Amanta and Purnimanta lunar month determination with Adhika Masa status."""

    amanta_index: int
    amanta_name: str
    purnimanta_index: int
    purnimanta_name: str
    paksha: str
    tithi_number: int
    is_adhika_masa: bool
    prev_amavasya_jd_ut: float
    next_amavasya_jd_ut: float
    sun_rashi_at_prev_amavasya: int
    sun_rashi_at_next_amavasya: int


@dataclass(frozen=True)
class RegionalSolarCalendarInfo:
    """Regional solar month (*Saura Masa*) and traditional Indian calendar eras."""

    surya_rashi_index: int
    sanskrit_saura_masa: str
    tamil_month: str
    malayalam_month: str
    bengali_month: str
    odia_month: str
    solar_day_of_month: int
    vikram_samvat_year: int
    shaka_samvat_year: int
    kali_yuga_year: int
    kollam_era_year: int
    bangabda_era_year: int


@dataclass(frozen=True)
class EclipseWindowSummary:
    """Nearby solar and lunar eclipse events and observer visibility within +/- window_days."""

    window_days: float
    nearest_solar_eclipse: dict[str, Any] | None
    nearest_lunar_eclipse: dict[str, Any] | None
    has_eclipse_within_window: bool


@dataclass(frozen=True)
class RegionalPanchangReport:
    """Complete regional Indian almanac report for a given epoch and observer location."""

    jd_ut: float
    ce_year: int
    latitude_deg: float
    longitude_deg: float
    sun_sidereal_lon_deg: float
    moon_sidereal_lon_deg: float
    sun_tropical_lon_deg: float
    tithi_number: int
    tithi_name: str
    paksha: str
    nakshatra_number: int
    nakshatra_name: str
    yoga_number: int
    yoga_name: str
    karana_number: int
    karana_name: str
    vara_name: str
    lunar_month: LunarMonthInfo
    solar_calendar: RegionalSolarCalendarInfo
    samvatsara_number: int
    samvatsara_name: str
    sidereal_ayana: str
    sidereal_ritu: str
    tropical_ayana: str
    tropical_ritu: str
    eclipse_window: EclipseWindowSummary
    receipt_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "jd_ut": self.jd_ut,
            "ce_year": self.ce_year,
            "latitude_deg": self.latitude_deg,
            "longitude_deg": self.longitude_deg,
            "sun_sidereal_lon_deg": self.sun_sidereal_lon_deg,
            "moon_sidereal_lon_deg": self.moon_sidereal_lon_deg,
            "sun_tropical_lon_deg": self.sun_tropical_lon_deg,
            "tithi_number": self.tithi_number,
            "tithi_name": self.tithi_name,
            "paksha": self.paksha,
            "nakshatra_number": self.nakshatra_number,
            "nakshatra_name": self.nakshatra_name,
            "yoga_number": self.yoga_number,
            "yoga_name": self.yoga_name,
            "karana_number": self.karana_number,
            "karana_name": self.karana_name,
            "vara_name": self.vara_name,
            "lunar_month": {
                "amanta_index": self.lunar_month.amanta_index,
                "amanta_name": self.lunar_month.amanta_name,
                "purnimanta_index": self.lunar_month.purnimanta_index,
                "purnimanta_name": self.lunar_month.purnimanta_name,
                "paksha": self.lunar_month.paksha,
                "tithi_number": self.lunar_month.tithi_number,
                "is_adhika_masa": self.lunar_month.is_adhika_masa,
                "prev_amavasya_jd_ut": self.lunar_month.prev_amavasya_jd_ut,
                "next_amavasya_jd_ut": self.lunar_month.next_amavasya_jd_ut,
            },
            "solar_calendar": {
                "surya_rashi_index": self.solar_calendar.surya_rashi_index,
                "sanskrit_saura_masa": self.solar_calendar.sanskrit_saura_masa,
                "tamil_month": self.solar_calendar.tamil_month,
                "malayalam_month": self.solar_calendar.malayalam_month,
                "bengali_month": self.solar_calendar.bengali_month,
                "odia_month": self.solar_calendar.odia_month,
                "solar_day_of_month": self.solar_calendar.solar_day_of_month,
                "vikram_samvat_year": self.solar_calendar.vikram_samvat_year,
                "shaka_samvat_year": self.solar_calendar.shaka_samvat_year,
                "kali_yuga_year": self.solar_calendar.kali_yuga_year,
                "kollam_era_year": self.solar_calendar.kollam_era_year,
                "bangabda_era_year": self.solar_calendar.bangabda_era_year,
            },
            "samvatsara_number": self.samvatsara_number,
            "samvatsara_name": self.samvatsara_name,
            "sidereal_ayana": self.sidereal_ayana,
            "sidereal_ritu": self.sidereal_ritu,
            "tropical_ayana": self.tropical_ayana,
            "tropical_ritu": self.tropical_ritu,
            "eclipse_window": {
                "window_days": self.eclipse_window.window_days,
                "has_eclipse_within_window": self.eclipse_window.has_eclipse_within_window,
                "nearest_solar_eclipse": self.eclipse_window.nearest_solar_eclipse,
                "nearest_lunar_eclipse": self.eclipse_window.nearest_lunar_eclipse,
            },
            "receipt_sha256": self.receipt_sha256,
        }


def _find_amavasya_near(
    jd_guess: float,
    sun_moon_fn: Any,
) -> float:
    """Refine the exact UT Julian Date of New Moon (elongation = 0 mod 360) near jd_guess."""
    jd = float(jd_guess)
    for _ in range(6):
        s_lon, m_lon, s_spd, m_spd = sun_moon_fn(jd)
        elong = (m_lon - s_lon + 180.0) % 360.0 - 180.0
        rel_spd = max(10.0, m_spd - s_spd)
        jd -= elong / rel_spd
    return float(jd)


def compute_lunar_month_amanta_purnimanta(
    jd_ut: float,
    *,
    adapter: EphemerisAdapter | None = None,
) -> LunarMonthInfo:
    """Compute Amanta and Purnimanta lunar month names and Adhika Masa status at ``jd_ut``."""
    analytical = AnalyticalEphemerisProvider()

    def _sun_moon(jd: float) -> tuple[float, float, float, float]:
        if adapter is not None:
            s_p = adapter.calc_ut(jd, "sun", sidereal=True)
            m_p = adapter.calc_ut(jd, "moon", sidereal=True)
            return (
                s_p.longitude_deg,
                m_p.longitude_deg,
                s_p.longitude_speed_deg_per_day,
                m_p.longitude_speed_deg_per_day,
            )
        s_r, _ = analytical.calc_ut(jd, "Sun", flags=FLG_SIDEREAL)
        m_r, _ = analytical.calc_ut(jd, "Moon", flags=FLG_SIDEREAL)
        return float(s_r[0]), float(m_r[0]), float(s_r[3]), float(m_r[3])

    s_now, m_now, s_spd, m_spd = _sun_moon(jd_ut)
    elong = (m_now - s_now) % 360.0
    tithi_num = min(30, int(elong // 12.0) + 1)
    paksha = "Shukla" if tithi_num <= 15 else "Krishna"

    rel_spd = max(11.0, m_spd - s_spd)
    prev_amavasya_guess = float(jd_ut) - (elong / rel_spd)
    next_amavasya_guess = float(jd_ut) + ((360.0 - elong) / rel_spd)

    prev_amavasya_jd = _find_amavasya_near(prev_amavasya_guess, _sun_moon)
    next_amavasya_jd = _find_amavasya_near(next_amavasya_guess, _sun_moon)
    if next_amavasya_jd <= prev_amavasya_jd + 20.0:
        next_amavasya_jd = _find_amavasya_near(prev_amavasya_jd + 29.530589, _sun_moon)

    s_prev, _, _, _ = _sun_moon(prev_amavasya_jd)
    s_next, _, _, _ = _sun_moon(next_amavasya_jd)
    rashi_prev = int((s_prev % 360.0) // 30.0) % 12
    rashi_next = int((s_next % 360.0) // 30.0) % 12

    # In classical Siddhantic/Drik reckoning:
    # When Sun is in Meena (11) at New Moon and enters Mesha (0) before the next New Moon,
    # the lunar month is Chaitra (0). Thus amanta_index = (rashi_prev + 1) % 12 when normal,
    # or rashi_next when a Sankranti occurs; if rashi_prev == rashi_next, no Sankranti occurred
    # inside the lunation -> Adhika Masa of month (rashi_prev + 1) % 12.
    is_adhika = rashi_prev == rashi_next
    amanta_idx = (rashi_prev + 1) % 12

    # In Purnimanta tradition, Krishna Paksha (Tithi 16..30) belongs to the next lunar month
    # compared to Amanta, whereas Shukla Paksha (Tithi 1..15) has the same month name.
    if paksha == "Krishna":
        purnimanta_idx = (amanta_idx + 1) % 12
    else:
        purnimanta_idx = amanta_idx

    return LunarMonthInfo(
        amanta_index=amanta_idx,
        amanta_name=LUNAR_MASA_NAMES[amanta_idx],
        purnimanta_index=purnimanta_idx,
        purnimanta_name=LUNAR_MASA_NAMES[purnimanta_idx],
        paksha=paksha,
        tithi_number=tithi_num,
        is_adhika_masa=is_adhika,
        prev_amavasya_jd_ut=round(prev_amavasya_jd, 6),
        next_amavasya_jd_ut=round(next_amavasya_jd, 6),
        sun_rashi_at_prev_amavasya=rashi_prev,
        sun_rashi_at_next_amavasya=rashi_next,
    )


def compute_regional_solar_calendar(
    sun_sidereal_lon_deg: float,
    ce_year: int,
) -> RegionalSolarCalendarInfo:
    """Compute regional Indian solar month names, day-of-month, and regional eras."""
    lon = float(sun_sidereal_lon_deg) % 360.0
    rashi_idx = int(lon // 30.0) % 12
    deg_in_sign = lon % 30.0
    solar_day = min(32, max(1, int(deg_in_sign) + 1))

    # After Mesha Sankranti (rashi_idx in 0..8 roughly Apr-Dec), Shaka is ce_year - 78;
    # in Makara/Kumbha/Meena (Jan-Apr, rashi_idx in 9..11), civil year has incremented by 1.
    before_mesha = rashi_idx in (9, 10, 11)
    shaka_year = (int(ce_year) - 79) if before_mesha else (int(ce_year) - 78)
    vikram_year = (int(ce_year) + 56) if before_mesha else (int(ce_year) + 57)
    kali_year = (int(ce_year) + 3100) if before_mesha else (int(ce_year) + 3101)
    bangabda_year = (int(ce_year) - 594) if before_mesha else (int(ce_year) - 593)

    # Malayalam Kollam Era increments at Simha (Chingam, rashi_idx == 4, mid-August)
    in_or_after_chingam = rashi_idx in (4, 5, 6, 7, 8)
    kollam_year = (int(ce_year) - 824) if in_or_after_chingam else (int(ce_year) - 825)

    return RegionalSolarCalendarInfo(
        surya_rashi_index=rashi_idx,
        sanskrit_saura_masa=RASI_NAMES[rashi_idx],
        tamil_month=TAMIL_SOLAR_MONTHS[rashi_idx],
        malayalam_month=MALAYALAM_SOLAR_MONTHS[rashi_idx],
        bengali_month=BENGALI_SOLAR_MONTHS[rashi_idx],
        odia_month=ODIA_SOLAR_MONTHS[rashi_idx],
        solar_day_of_month=solar_day,
        vikram_samvat_year=vikram_year,
        shaka_samvat_year=shaka_year,
        kali_yuga_year=kali_year,
        kollam_era_year=kollam_year,
        bangabda_era_year=bangabda_year,
    )


def compute_eclipse_window_summary(
    jd_ut: float,
    *,
    latitude_deg: float | None = None,
    longitude_deg: float | None = None,
    window_days: float = 16.0,
) -> EclipseWindowSummary:
    """Check for solar and lunar eclipses within ``+/- window_days`` of ``jd_ut``."""
    w = max(1.0, float(window_days))
    sol_list = find_solar_eclipses(jd_ut - w, jd_ut + w)
    lun_list = find_lunar_eclipses(jd_ut - w, jd_ut + w)

    nearest_sol: dict[str, Any] | None = None
    if sol_list:
        s_ev: SolarEclipse = min(sol_list, key=lambda e: abs(e.greatest_jd_tt - jd_ut))
        nearest_sol = {
            "classification": s_ev.classification,
            "greatest_jd_tt": round(s_ev.greatest_jd_tt, 6),
            "gamma": round(s_ev.gamma, 5),
            "max_magnitude": round(s_ev.magnitude, 5),
            "receipt_sha256": s_ev.receipt_sha256,
        }
        if latitude_deg is not None and longitude_deg is not None:
            loc = solar_eclipse_local_circumstances(s_ev, float(latitude_deg), float(longitude_deg))
            nearest_sol["local_visible"] = loc.visible
            nearest_sol["local_magnitude"] = round(loc.magnitude, 5)
            nearest_sol["local_obscuration"] = round(loc.obscuration, 5)

    nearest_lun: dict[str, Any] | None = None
    if lun_list:
        l_ev: LunarEclipse = min(lun_list, key=lambda e: abs(l_ev_item.greatest_jd_tt - jd_ut) if (l_ev_item := e) else 0.0)
        nearest_lun = {
            "classification": l_ev.classification,
            "greatest_jd_tt": round(l_ev.greatest_jd_tt, 6),
            "gamma": round(l_ev.gamma, 5),
            "umbral_magnitude": round(l_ev.umbral_magnitude, 5),
            "penumbral_magnitude": round(l_ev.penumbral_magnitude, 5),
            "receipt_sha256": l_ev.receipt_sha256,
        }
        if latitude_deg is not None and longitude_deg is not None:
            l_vis = lunar_eclipse_local_visibility(l_ev, float(latitude_deg), float(longitude_deg))
            nearest_lun["local_visible"] = l_vis.visible
            nearest_lun["moon_altitude_at_max_deg"] = (
                round(float(l_vis.greatest.moon_altitude_deg), 3)
                if l_vis.greatest.moon_altitude_deg is not None
                else None
            )

    return EclipseWindowSummary(
        window_days=w,
        nearest_solar_eclipse=nearest_sol,
        nearest_lunar_eclipse=nearest_lun,
        has_eclipse_within_window=bool(nearest_sol is not None or nearest_lun is not None),
    )


def compute_regional_panchang(
    jd_ut: float,
    latitude_deg: float = 28.6139,
    longitude_deg: float = 77.2090,
    *,
    adapter: EphemerisAdapter | None = None,
    eclipse_window_days: float = 16.0,
) -> RegionalPanchangReport:
    """Compute a complete regional Indian almanac report with SHA-256 receipt."""
    jd_val = float(jd_ut)
    lat = float(latitude_deg)
    lon = float(longitude_deg)
    if not math.isfinite(jd_val):
        raise ValueError("jd_ut must be finite")
    if not math.isfinite(lat) or not -90.0 < lat < 90.0:
        raise ValueError("latitude_deg must be finite and within (-90, 90)")
    if not math.isfinite(lon) or not -180.0 <= lon <= 180.0:
        raise ValueError("longitude_deg must be finite and within [-180, 180]")

    ce_year, _m, _d, _h = EphemerisAdapter.revjul(jd_val)
    if adapter is not None:
        s_sid = adapter.calc_ut(jd_val, "sun", sidereal=True).longitude_deg
        m_sid = adapter.calc_ut(jd_val, "moon", sidereal=True).longitude_deg
        s_trop = adapter.calc_ut(jd_val, "sun", sidereal=False).longitude_deg
    else:
        analytical = AnalyticalEphemerisProvider()
        s_res_sid, _ = analytical.calc_ut(jd_val, "Sun", flags=FLG_SIDEREAL)
        m_res_sid, _ = analytical.calc_ut(jd_val, "Moon", flags=FLG_SIDEREAL)
        s_res_trop, _ = analytical.calc_ut(jd_val, "Sun", flags=0)
        s_sid = float(s_res_sid[0])
        m_sid = float(m_res_sid[0])
        s_trop = float(s_res_trop[0])

    panch = compute_panchanga(
        sun_lon_deg=s_sid,
        moon_lon_deg=m_sid,
        jd_ut=jd_val,
        ce_year=ce_year,
    )
    lunar_month = compute_lunar_month_amanta_purnimanta(jd_val, adapter=adapter)
    solar_cal = compute_regional_solar_calendar(s_sid, ce_year)
    samvatsara = compute_samvatsara(solar_cal.shaka_samvat_year, calendar="shaka")
    sid_ayana, sid_ritu, _ = compute_ayana_and_ritu(s_sid)
    trop_ayana, trop_ritu, _ = compute_ayana_and_ritu(s_trop)
    eclipse_win = compute_eclipse_window_summary(
        jd_val,
        latitude_deg=lat,
        longitude_deg=lon,
        window_days=eclipse_window_days,
    )

    receipt_payload = {
        "schema": "ephemeris-oss.almanac.regional-panchang.v1",
        "version": __version__,
        "jd_ut": round(jd_val, 8),
        "latitude_deg": round(lat, 6),
        "longitude_deg": round(lon, 6),
        "sun_sidereal_lon_deg": round(s_sid, 8),
        "moon_sidereal_lon_deg": round(m_sid, 8),
        "tithi_number": panch.tithi.number,
        "amanta_month": lunar_month.amanta_name,
        "purnimanta_month": lunar_month.purnimanta_name,
        "is_adhika_masa": lunar_month.is_adhika_masa,
        "tamil_month": solar_cal.tamil_month,
        "samvatsara_name": samvatsara.name,
        "sidereal_ayana": sid_ayana,
        "sidereal_ritu": sid_ritu,
        "has_eclipse_within_window": eclipse_win.has_eclipse_within_window,
    }
    receipt_sha256 = canonical_hash(receipt_payload)

    return RegionalPanchangReport(
        jd_ut=jd_val,
        ce_year=ce_year,
        latitude_deg=lat,
        longitude_deg=lon,
        sun_sidereal_lon_deg=s_sid,
        moon_sidereal_lon_deg=m_sid,
        sun_tropical_lon_deg=s_trop,
        tithi_number=panch.tithi.number,
        tithi_name=panch.tithi.name,
        paksha=panch.tithi.paksha,
        nakshatra_number=panch.nakshatra.number,
        nakshatra_name=panch.nakshatra.name,
        yoga_number=panch.yoga.number,
        yoga_name=panch.yoga.name,
        karana_number=panch.karana.number,
        karana_name=panch.karana.name,
        vara_name=panch.vara.english_name,
        lunar_month=lunar_month,
        solar_calendar=solar_cal,
        samvatsara_number=samvatsara.number,
        samvatsara_name=samvatsara.name,
        sidereal_ayana=sid_ayana,
        sidereal_ritu=sid_ritu,
        tropical_ayana=trop_ayana,
        tropical_ritu=trop_ritu,
        eclipse_window=eclipse_win,
        receipt_sha256=receipt_sha256,
    )
