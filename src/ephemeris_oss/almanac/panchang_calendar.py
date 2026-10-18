"""Monthly and Annual Drik Panchang Calendar Generator with Sunrise-Anchored Vrata Detection.

Computes daily sunrise-anchored Vedic almanac entries (*Drik Panchanga*) across a calendar
month or year, including:
- Local sunrise and sunset Julian Dates (`rise_trans` spherical hour-angle solver)
- Vara (weekday, 0=Sunday .. 6=Saturday)
- Sunrise Tithi (1..30), Paksha (`Shukla` / `Krishna`), Nakshatra (1..27), Yoga (1..27), Karana (1..11)
- Exact UT Julian Date transition (`tithi_end_jd_ut`) when the sunrise Tithi ends
- *Kshaya Tithi* (lunar day that begins and ends between two consecutive sunrises) and
  *Adhika Tithi* (lunar day that spans two consecutive sunrises) detection
- Classical Vrata and festival markers:
  - *Sankranti* (solar sign ingress between consecutive sunrises)
  - *Ekadashi* (Tithi 11 or 26 at sunrise, with Smarta/Vaishnava Dashami-vedha check at Arunodaya = sunrise - 96 minutes)
  - *Pradosha Vrata* (Trayodashi Tithi 13 or 28 prevailing during sunset window)
  - *Purnima* (Tithi 15) and *Amavasya* (Tithi 30)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
import math
from typing import Any, Mapping

from .._version import __version__
from ..adapter import AnalyticalEphemerisProvider, CALC_RISE, CALC_SET, EphemerisAdapter, FLG_SIDEREAL
from ..engine.receipt import canonical_hash
from ..jyotish.nakshatra import NAKSHATRA_NAMES, RASI_NAMES as RASHI_NAMES
from ..jyotish.panchanga import MOVABLE_KARANAS, PAKSHA_TITHI_NAMES, VARA_CATALOG, YOGA_CATALOG

TITHI_NAMES: tuple[str, ...] = (
    tuple(f"Shukla {name}" for name in PAKSHA_TITHI_NAMES)
    + ("Purnima",)
    + tuple(f"Krishna {name}" for name in PAKSHA_TITHI_NAMES)
    + ("Amavasya",)
)
VARA_NAMES: tuple[str, ...] = tuple(item[1] for item in VARA_CATALOG)
YOGA_NAMES: tuple[str, ...] = tuple(item[1] for item in YOGA_CATALOG)
KARANA_NAMES: tuple[str, ...] = MOVABLE_KARANAS + (
    "Shakuni",
    "Chatushpada",
    "Naga",
    "Kimstughna",
)


@dataclass(frozen=True)
class DailyPanchangEntry:
    """Single civil day sunrise-anchored Drik Panchang record."""

    civil_date: str
    jd_midnight_ut: float
    sunrise_jd_ut: float
    sunset_jd_ut: float
    vara_index: int
    vara_name: str
    sun_sidereal_lon_deg: float
    moon_sidereal_lon_deg: float
    surya_rashi_index: int
    surya_rashi_name: str
    chandra_rashi_index: int
    chandra_rashi_name: str
    tithi_number: int
    tithi_name: str
    paksha: str
    tithi_end_jd_ut: float
    nakshatra_number: int
    nakshatra_name: str
    yoga_number: int
    yoga_name: str
    karana_name: str
    is_adhika_tithi: bool
    kshaya_tithi_number: int | None
    sankranti_rashi_name: str | None
    is_ekadashi: bool
    ekadashi_type: str | None
    is_pradosha: bool
    is_purnima: bool
    is_amavasya: bool
    vratas: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "civil_date": self.civil_date,
            "jd_midnight_ut": self.jd_midnight_ut,
            "sunrise_jd_ut": self.sunrise_jd_ut,
            "sunset_jd_ut": self.sunset_jd_ut,
            "vara_index": self.vara_index,
            "vara_name": self.vara_name,
            "sun_sidereal_lon_deg": self.sun_sidereal_lon_deg,
            "moon_sidereal_lon_deg": self.moon_sidereal_lon_deg,
            "surya_rashi_index": self.surya_rashi_index,
            "surya_rashi_name": self.surya_rashi_name,
            "chandra_rashi_index": self.chandra_rashi_index,
            "chandra_rashi_name": self.chandra_rashi_name,
            "tithi_number": self.tithi_number,
            "tithi_name": self.tithi_name,
            "paksha": self.paksha,
            "tithi_end_jd_ut": self.tithi_end_jd_ut,
            "nakshatra_number": self.nakshatra_number,
            "nakshatra_name": self.nakshatra_name,
            "yoga_number": self.yoga_number,
            "yoga_name": self.yoga_name,
            "karana_name": self.karana_name,
            "is_adhika_tithi": self.is_adhika_tithi,
            "kshaya_tithi_number": self.kshaya_tithi_number,
            "sankranti_rashi_name": self.sankranti_rashi_name,
            "is_ekadashi": self.is_ekadashi,
            "ekadashi_type": self.ekadashi_type,
            "is_pradosha": self.is_pradosha,
            "is_purnima": self.is_purnima,
            "is_amavasya": self.is_amavasya,
            "vratas": list(self.vratas),
        }


@dataclass(frozen=True)
class MonthlyPanchangSheet:
    """Complete monthly Drik Panchang calendar sheet with SHA-256 receipt."""

    year: int
    month: int
    latitude_deg: float
    longitude_deg: float
    tz_offset_hours: float
    days: tuple[DailyPanchangEntry, ...]
    vratas_summary: tuple[dict[str, Any], ...]
    receipt: Mapping[str, Any]
    receipt_sha256: str


def _karana_from_elongation(elong_deg: float) -> str:
    karana_idx = int((elong_deg % 360.0) // 6.0) % 60
    if karana_idx == 0:
        return KARANA_NAMES[10]  # Kimstughna
    if karana_idx == 57:
        return KARANA_NAMES[7]  # Shakuni
    if karana_idx == 58:
        return KARANA_NAMES[8]  # Chatushpada
    if karana_idx == 59:
        return KARANA_NAMES[9]  # Naga
    return KARANA_NAMES[(karana_idx - 1) % 7]


def generate_monthly_panchang(
    year: int,
    month: int,
    latitude_deg: float,
    longitude_deg: float,
    *,
    tz_offset_hours: float = 0.0,
    adapter: EphemerisAdapter | None = None,
) -> MonthlyPanchangSheet:
    """Generate a sunrise-anchored monthly Drik Panchang sheet with Vrata detection."""
    yr = int(year)
    mo = int(month)
    if not 1 <= mo <= 12:
        raise ValueError(f"month must be in 1..12; got {month!r}")
    lat = float(latitude_deg)
    lon = float(longitude_deg)
    tz_off = float(tz_offset_hours)
    if not math.isfinite(lat) or not -66.0 <= lat <= 66.0:
        raise ValueError("latitude_deg must be finite and within [-66.0, 66.0] for daily sunrise Panchang")
    if not math.isfinite(lon) or not -180.0 <= lon <= 180.0:
        raise ValueError("longitude_deg must be finite and within [-180.0, 180.0]")

    analytical = AnalyticalEphemerisProvider()

    def _sun_moon_sidereal(jd_ut: float) -> tuple[float, float, float, float]:
        if adapter is not None:
            s_pos = adapter.calc_ut(jd_ut, "sun", sidereal=True)
            m_pos = adapter.calc_ut(jd_ut, "moon", sidereal=True)
            return (
                s_pos.longitude_deg,
                m_pos.longitude_deg,
                s_pos.longitude_speed_deg_per_day,
                m_pos.longitude_speed_deg_per_day,
            )
        s_res, _ = analytical.calc_ut(jd_ut, "Sun", flags=FLG_SIDEREAL)
        m_res, _ = analytical.calc_ut(jd_ut, "Moon", flags=FLG_SIDEREAL)
        return float(s_res[0]), float(m_res[0]), float(s_res[3]), float(m_res[3])

    def _rise_set_for_civil_day(d: date) -> tuple[float, float, float]:
        jd_local_midnight_ut = EphemerisAdapter.julday(d.year, d.month, d.day, 0.0) - (tz_off / 24.0)
        if adapter is not None:
            _, (sr_jd,) = adapter.rise_trans(jd_local_midnight_ut, "sun", CALC_RISE, (lon, lat, 0.0))
            _, (ss_jd,) = adapter.rise_trans(sr_jd, "sun", CALC_SET, (lon, lat, 0.0))
        else:
            _, (sr_jd,) = analytical.rise_trans(jd_local_midnight_ut, "Sun", CALC_RISE, (lon, lat, 0.0))
            _, (ss_jd,) = analytical.rise_trans(sr_jd, "Sun", CALC_SET, (lon, lat, 0.0))
        return jd_local_midnight_ut, float(sr_jd), float(ss_jd)

    def _tithi_at(jd_ut: float) -> tuple[int, float, float]:
        s_lon, m_lon, s_spd, m_spd = _sun_moon_sidereal(jd_ut)
        elong = (m_lon - s_lon) % 360.0
        tithi_num = int(elong // 12.0) + 1
        if tithi_num > 30:
            tithi_num = 30
        rem_deg = (tithi_num * 12.0) - elong
        rel_spd = max(8.0, m_spd - s_spd)
        end_est = jd_ut + (rem_deg / rel_spd)
        # Two-step refinement for exact Tithi end
        target_elong = (tithi_num * 12.0) % 360.0
        for _ in range(3):
            s2, m2, ss2, ms2 = _sun_moon_sidereal(end_est)
            el2 = (m2 - s2) % 360.0
            diff = (target_elong - el2 + 540.0) % 360.0 - 180.0
            end_est += diff / max(8.0, ms2 - ss2)
        return tithi_num, elong, float(end_est)

    start_date = date(yr, mo, 1)
    if mo == 12:
        next_month_start = date(yr + 1, 1, 1)
    else:
        next_month_start = date(yr, mo + 1, 1)
    num_days = (next_month_start - start_date).days

    entries: list[DailyPanchangEntry] = []
    vratas_summary: list[dict[str, Any]] = []
    prev_tithi: int | None = None
    prev_surya_rashi: int | None = None

    for offset in range(num_days):
        cur_date = start_date + timedelta(days=offset)
        jd_mid_ut, sr_jd, ss_jd = _rise_set_for_civil_day(cur_date)
        s_lon, m_lon, _s_spd, _m_spd = _sun_moon_sidereal(sr_jd)
        tithi_num, elong, tithi_end_jd = _tithi_at(sr_jd)

        # Next day sunrise for Kshaya / Sankranti detection
        _, next_sr_jd, _ = _rise_set_for_civil_day(cur_date + timedelta(days=1))
        next_s_lon, _next_m_lon, _, _ = _sun_moon_sidereal(next_sr_jd)
        next_tithi_num, _, _ = _tithi_at(next_sr_jd)

        surya_rashi_idx = int(s_lon // 30.0) % 12
        next_surya_rashi_idx = int(next_s_lon // 30.0) % 12
        chandra_rashi_idx = int(m_lon // 30.0) % 12

        nak_idx = int(m_lon // (360.0 / 27.0)) % 27
        yoga_idx = int(((s_lon + m_lon) % 360.0) // (360.0 / 27.0)) % 27
        karana_name = _karana_from_elongation(elong)

        # Weekday: Python weekday() has Monday=0..Sunday=6; Vedic Vara has Sunday=0..Saturday=6
        vara_idx = (cur_date.weekday() + 1) % 7
        vara_name = VARA_NAMES[vara_idx]

        is_adhika = prev_tithi is not None and tithi_num == prev_tithi
        tithi_step = (next_tithi_num - tithi_num) % 30
        kshaya_tithi: int | None = ((tithi_num % 30) + 1) if tithi_step == 2 else None

        sankranti_rashi: str | None = None
        if surya_rashi_idx != next_surya_rashi_idx or (
            prev_surya_rashi is not None and surya_rashi_idx != prev_surya_rashi and offset == 0
        ):
            if surya_rashi_idx != next_surya_rashi_idx:
                sankranti_rashi = RASHI_NAMES[next_surya_rashi_idx]

        # Ekadashi detection with Arunodaya (sunrise - 96 min = 4 Ghatikas) Dashami-vedha check
        is_ekadashi = tithi_num in (11, 26)
        ekadashi_type: str | None = None
        if is_ekadashi:
            arunodaya_jd = sr_jd - (96.0 / 1440.0)
            arun_tithi, _, _ = _tithi_at(arunodaya_jd)
            if arun_tithi in (10, 25):
                ekadashi_type = "Smarta (Dashami-Viddha at Arunodaya)"
            else:
                ekadashi_type = "Shuddha (Smarta & Vaishnava)"

        # Pradosha detection: Trayodashi (13 or 28) prevailing at sunset
        ss_tithi, _, _ = _tithi_at(ss_jd)
        is_pradosha = ss_tithi in (13, 28)
        is_purnima = tithi_num == 15 or kshaya_tithi == 15
        is_amavasya = tithi_num == 30 or kshaya_tithi == 30

        vratas: list[str] = []
        if is_ekadashi:
            vratas.append(f"Ekadashi ({ekadashi_type})")
        if is_pradosha:
            vratas.append("Pradosha Vrata")
        if is_purnima:
            vratas.append("Purnima")
        if is_amavasya:
            vratas.append("Amavasya")
        if sankranti_rashi is not None:
            vratas.append(f"{sankranti_rashi} Sankranti")

        paksha = "Shukla" if tithi_num <= 15 else "Krishna"
        tithi_name = TITHI_NAMES[tithi_num - 1]
        iso_str = cur_date.isoformat()

        if vratas:
            vratas_summary.append(
                {
                    "civil_date": iso_str,
                    "tithi_number": tithi_num,
                    "tithi_name": tithi_name,
                    "vratas": list(vratas),
                }
            )

        entries.append(
            DailyPanchangEntry(
                civil_date=iso_str,
                jd_midnight_ut=round(jd_mid_ut, 8),
                sunrise_jd_ut=round(sr_jd, 8),
                sunset_jd_ut=round(ss_jd, 8),
                vara_index=vara_idx,
                vara_name=vara_name,
                sun_sidereal_lon_deg=round(s_lon, 6),
                moon_sidereal_lon_deg=round(m_lon, 6),
                surya_rashi_index=surya_rashi_idx,
                surya_rashi_name=RASHI_NAMES[surya_rashi_idx],
                chandra_rashi_index=chandra_rashi_idx,
                chandra_rashi_name=RASHI_NAMES[chandra_rashi_idx],
                tithi_number=tithi_num,
                tithi_name=tithi_name,
                paksha=paksha,
                tithi_end_jd_ut=round(tithi_end_jd, 8),
                nakshatra_number=nak_idx + 1,
                nakshatra_name=NAKSHATRA_NAMES[nak_idx],
                yoga_number=yoga_idx + 1,
                yoga_name=YOGA_NAMES[yoga_idx],
                karana_name=karana_name,
                is_adhika_tithi=is_adhika,
                kshaya_tithi_number=kshaya_tithi,
                sankranti_rashi_name=sankranti_rashi,
                is_ekadashi=is_ekadashi,
                ekadashi_type=ekadashi_type,
                is_pradosha=is_pradosha,
                is_purnima=is_purnima,
                is_amavasya=is_amavasya,
                vratas=tuple(vratas),
            )
        )
        prev_tithi = tithi_num
        prev_surya_rashi = surya_rashi_idx

    receipt_payload: dict[str, Any] = {
        "schema": "ephemeris-oss.almanac.monthly_panchang.v1",
        "version": __version__,
        "year": yr,
        "month": mo,
        "latitude_deg": round(lat, 6),
        "longitude_deg": round(lon, 6),
        "tz_offset_hours": round(tz_off, 4),
        "num_days": len(entries),
        "first_sunrise_jd_ut": entries[0].sunrise_jd_ut,
        "last_sunrise_jd_ut": entries[-1].sunrise_jd_ut,
        "vratas_count": len(vratas_summary),
    }
    return MonthlyPanchangSheet(
        year=yr,
        month=mo,
        latitude_deg=lat,
        longitude_deg=lon,
        tz_offset_hours=tz_off,
        days=tuple(entries),
        vratas_summary=tuple(vratas_summary),
        receipt=receipt_payload,
        receipt_sha256=canonical_hash(receipt_payload),
    )


__all__ = [
    "DailyPanchangEntry",
    "MonthlyPanchangSheet",
    "generate_monthly_panchang",
]
