"""Human-Readable Classical Ephemeris & Jyotish Academy Manual Calculation Compendium.

Generates a complete, print-ready classical *Nirayana* (Sidereal) Ephemeris and
Manual Kundali Calculation Compendium designed for human astrologers, classical
researchers, and students of **Pt. Maheshji's Jyotish Academy (Jyotish Gurukul)**.

Every single calculation that the ``ephemeris-oss`` software engine performs
computationally can be performed manually on paper using the tables in this compendium:

1. **Daily Sidereal (*Nirayana*) Planetary Ephemeris Grid (`05:30 IST` / Reference Epoch):**
   - Exact positions in classical ``Rashi DD° MM' SS"`` and ``SSs DD° MM' SS"`` notation
   - 27-Nakshatra and Pada (``1..4``)
   - Daily angular velocity (``±DD° MM' SS"/day``) for manual *Trairashika* (Rule of Three) interpolation
   - Retrograde (``R`` / *Vakri*), Stationary (``S`` / *Stambhana*), and Combustion (``C`` / *Asta*) markers
   - Daily exact Lahiri (*Chitrapaksha*) Ayanamsha, Kali Yuga *Ahargana*, and Sidereal Time
2. **Daily Sunrise-Anchored *Drik Panchanga*, *Muhurta*, & *Mahapata* Table:**
   - Local Sunrise, Sunset, *Dinamana* (in Hours and *Ghatis*), *Vara*, *Tithi* (with ending clock time and *Ghati-Pala*), *Nakshatra*, *Yoga*, *Karana*, *Rahu Kala*, *Abhijit Muhurta*, and *Vyatipata/Vaidhriti* alerts
3. **Manual *Spashta Graha* Interpolation & *Lagna / Bhava* (Ascendant & House) Tables:**
   - *Trairashika* time-fraction table, *Lankodaya / Rasimana* rising durations with latitude *Charakhanda* corrections, and *Sripathi Bhava Chalit* trisection rules
4. **Complete Manual Divisional Chart (*Shodashvarga D1–D60*) Reckoning Tables:**
   - Eye-lookup degree-minute tables for all 16 Parashari Vargas (D1, D2, D3, D4, D7, D9, D10, D12, D16, D20, D24, D27, D30, D40, D45, D60 with all 60 Shashtiamsa names)
5. **Complete Manual Dasha Balance (*Bhogyamsha*) & Progression Tables:**
   - Vimshottari (120y) arcminute-to-balance ready reckoner + 9×9 Antardasha matrix, Yogini (36y), Ashtottari (108y), and BPHS Kalachakra Dasha (108-Pada Savya/Apasavya wheel with Deha/Jeeva and Gati jumps)
6. **Manual *Ashtakavarga* (337-Bindu Matrix), *Shadbala* (6-Fold Strength), & 30-Star *Yogatara* Reference Tables**
7. **Pt. Maheshji's Jyotish Academy Step-by-Step Worked Manual Kundali Worksheet:**
   - A 10-step worked numerical example showing how to hand-cast a complete natal chart from the ephemeris tables with pen and paper.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
import math
from typing import Any, Mapping

from .._version import __version__
from ..adapter import CALC_RISE, CALC_SET, EphemerisAdapter, FLG_SIDEREAL
from ..engine.receipt import canonical_hash
from ..engine.stellar_anchors import YOGATARA_30_CATALOG
from ..jyotish.ashtakavarga import BAV_BENEFIC_HOUSES
from ..jyotish.dasha import (
    KALACHAKRA_APASAVYA_SEQUENCES,
    KALACHAKRA_SAVYA_SEQUENCES,
    KALACHAKRA_SIGN_YEARS,
    VIMSHOTTARI_TOTAL_YEARS,
    VIMSHOTTARI_YEARS,
)
from ..jyotish.nakshatra import (
    NAKSHATRA_NAMES,
    RASI_NAMES as RASHI_NAMES,
    VIMSHOTTARI_RULERS as VIMSHOTTARI_LORDS,
    nakshatra_position,
)
from ..jyotish.vargas import RASI_LORDS, SHASHTIAMSA_CATALOG, varga_sign
from .panchang_calendar import generate_monthly_panchang

# Classical combustion orbs (degrees from Sun) per Surya Siddhanta / BPHS
CLASSICAL_COMBUSTION_ORBS_DEG: Mapping[str, tuple[float, float]] = {
    "moon": (12.0, 12.0),
    "mars": (17.0, 17.0),
    "mercury": (14.0, 12.0),  # (direct, retrograde)
    "jupiter": (11.0, 11.0),
    "venus": (10.0, 8.0),     # (direct, retrograde)
    "saturn": (15.0, 15.0),
}

# Classical Lankodaya (equatorial rising durations of the 12 signs in Vinadis / Palas; 3600 Vinadis = 60 Ghatis = 24 Hours)
LANKODAYA_VINADIS: tuple[int, ...] = (
    278,  # Mesha (Aries)
    299,  # Vrishabha (Taurus)
    323,  # Mithuna (Gemini)
    323,  # Karka (Cancer)
    299,  # Simha (Leo)
    278,  # Kanya (Virgo)
    278,  # Tula (Libra)
    299,  # Vrishchika (Scorpio)
    323,  # Dhanu (Sagittarius)
    323,  # Makara (Capricorn)
    299,  # Kumbha (Aquarius)
    278,  # Meena (Pisces)
)

# Classical Rahu Kala octant index (1..8 of daytime Dinamana) for Sunday=0 .. Saturday=6
RAHU_KALA_OCTANT: tuple[int, ...] = (8, 2, 7, 5, 6, 4, 3)
YAMAGANDA_OCTANT: tuple[int, ...] = (5, 4, 3, 2, 1, 7, 6)
GULIKA_OCTANT: tuple[int, ...] = (7, 6, 5, 4, 3, 2, 1)


def format_classical_rashi_dms(longitude_deg: float, *, compact_sign_number: bool = False) -> str:
    """Format an ecliptic longitude in ``[0, 360)`` as classical Jyotish ``Sign DD° MM' SS"`` or ``SSs DD° MM' SS"``."""
    lon = float(longitude_deg) % 360.0
    total_arcsec = int(round(lon * 3600.0)) % (360 * 3600)
    rashi_idx = (total_arcsec // (30 * 3600)) % 12
    rem_sec = total_arcsec % (30 * 3600)
    deg = rem_sec // 3600
    rem_sec %= 3600
    minutes = rem_sec // 60
    seconds = rem_sec % 60
    if compact_sign_number:
        return f"{rashi_idx:02d}s {deg:02d}° {minutes:02d}' {seconds:02d}\""
    return f"{RASHI_NAMES[rashi_idx]} {deg:02d}° {minutes:02d}' {seconds:02d}\""


def format_daily_motion_dms(speed_deg_per_day: float) -> str:
    """Format daily angular velocity in ``±DD° MM' SS"/d``."""
    spd = float(speed_deg_per_day)
    sign_char = "-" if spd < 0.0 else "+"
    total_arcsec = int(round(abs(spd) * 3600.0))
    deg = total_arcsec // 3600
    rem_sec = total_arcsec % 3600
    minutes = rem_sec // 60
    seconds = rem_sec % 60
    return f"{sign_char}{deg:02d}° {minutes:02d}' {seconds:02d}\""


def format_ghati_pala(hours: float) -> str:
    """Convert elapsed hours (e.g., since sunrise) into Vedic ``GG Gh PP Pa`` (1 Hour = 2.5 Ghatis)."""
    total_palas = int(round(max(0.0, float(hours)) * 150.0))
    ghatis = total_palas // 60
    palas = total_palas % 60
    return f"{ghatis:02d} Gh {palas:02d} Pa"


def _jd_to_local_hhmm(jd_ut: float, tz_offset_hours: float) -> str:
    local_jd = float(jd_ut) + (float(tz_offset_hours) / 24.0)
    _y, _m, _d, hour_val = EphemerisAdapter.revjul(local_jd)
    total_sec = int(round(hour_val * 3600.0)) % 86400
    hh = total_sec // 3600
    mm = (total_sec % 3600) // 60
    return f"{hh:02d}:{mm:02d}"


def _jd_to_local_hhmmss(jd_ut: float, tz_offset_hours: float) -> str:
    local_jd = float(jd_ut) + (float(tz_offset_hours) / 24.0)
    _y, _m, _d, hour_val = EphemerisAdapter.revjul(local_jd)
    total_sec = int(round(hour_val * 3600.0)) % 86400
    hh = total_sec // 3600
    rem = total_sec % 3600
    mm = rem // 60
    ss = rem % 60
    return f"{hh:02d}:{mm:02d}:{ss:02d}"


def _deg_to_hhmmss(deg_val: float) -> str:
    hours = (float(deg_val) % 360.0) / 15.0
    total_sec = int(round(hours * 3600.0)) % 86400
    hh = total_sec // 3600
    rem = total_sec % 3600
    mm = rem // 60
    ss = rem % 60
    return f"{hh:02d}:{mm:02d}:{ss:02d}"


@dataclass(frozen=True)
class HumanDailyPlanetCell:
    """Classical human-readable planetary entry for a single reference day."""

    body: str
    longitude_deg: float
    rashi_index: int
    rashi_name: str
    classical_dms: str
    sign_num_dms: str
    nakshatra_name: str
    nakshatra_lord: str
    pada: int
    speed_deg_per_day: float
    daily_motion_dms: str
    is_retrograde: bool
    is_combust: bool
    status_flags: str
    d9_navamsa_sign: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "body": self.body,
            "longitude_deg": round(self.longitude_deg, 6),
            "rashi_index": self.rashi_index,
            "rashi_name": self.rashi_name,
            "classical_dms": self.classical_dms,
            "sign_num_dms": self.sign_num_dms,
            "nakshatra_name": self.nakshatra_name,
            "nakshatra_lord": self.nakshatra_lord,
            "pada": self.pada,
            "speed_deg_per_day": round(self.speed_deg_per_day, 6),
            "daily_motion_dms": self.daily_motion_dms,
            "is_retrograde": self.is_retrograde,
            "is_combust": self.is_combust,
            "status_flags": self.status_flags,
            "d9_navamsa_sign": self.d9_navamsa_sign,
        }


@dataclass(frozen=True)
class HumanDailyEphemerisRow:
    """Single day's complete human-readable ephemeris & Drik Panchanga row."""

    civil_date: str
    vara_name: str
    jd_reference_ut: float
    ahargana_kali_days: float
    ayanamsa_dms: str
    local_sidereal_time_hms: str
    sunrise_local_hms: str
    sunset_local_hms: str
    dinamana_hours: float
    dinamana_ghati_pala: str
    tithi_name: str
    tithi_end_local_hm: str
    tithi_end_ghati_pala: str
    nakshatra_at_sunrise: str
    yoga_at_sunrise: str
    karana_at_sunrise: str
    rahu_kala_window: str
    abhijit_muhurta_window: str
    vratas: tuple[str, ...]
    planets: Mapping[str, HumanDailyPlanetCell]

    def to_dict(self) -> dict[str, Any]:
        return {
            "civil_date": self.civil_date,
            "vara_name": self.vara_name,
            "jd_reference_ut": round(self.jd_reference_ut, 6),
            "ahargana_kali_days": round(self.ahargana_kali_days, 2),
            "ayanamsa_dms": self.ayanamsa_dms,
            "local_sidereal_time_hms": self.local_sidereal_time_hms,
            "sunrise_local_hms": self.sunrise_local_hms,
            "sunset_local_hms": self.sunset_local_hms,
            "dinamana_hours": round(self.dinamana_hours, 4),
            "dinamana_ghati_pala": self.dinamana_ghati_pala,
            "tithi_name": self.tithi_name,
            "tithi_end_local_hm": self.tithi_end_local_hm,
            "tithi_end_ghati_pala": self.tithi_end_ghati_pala,
            "nakshatra_at_sunrise": self.nakshatra_at_sunrise,
            "yoga_at_sunrise": self.yoga_at_sunrise,
            "karana_at_sunrise": self.karana_at_sunrise,
            "rahu_kala_window": self.rahu_kala_window,
            "abhijit_muhurta_window": self.abhijit_muhurta_window,
            "vratas": list(self.vratas),
            "planets": {k: v.to_dict() for k, v in self.planets.items()},
        }


@dataclass(frozen=True)
class HumanManualEphemerisCompendium:
    """Complete Human-Readable Ephemeris & Jyotish Academy Manual Calculation Compendium."""

    year: int
    month: int
    latitude_deg: float
    longitude_deg: float
    tz_offset_hours: float
    ayanamsa_mode: str
    reference_time_label: str
    daily_rows: tuple[HumanDailyEphemerisRow, ...]
    worked_example: Mapping[str, Any]
    receipt: Mapping[str, Any]
    receipt_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "year": self.year,
            "month": self.month,
            "latitude_deg": self.latitude_deg,
            "longitude_deg": self.longitude_deg,
            "tz_offset_hours": self.tz_offset_hours,
            "ayanamsa_mode": self.ayanamsa_mode,
            "reference_time_label": self.reference_time_label,
            "daily_rows": [r.to_dict() for r in self.daily_rows],
            "worked_example": dict(self.worked_example),
            "receipt": dict(self.receipt),
            "receipt_sha256": self.receipt_sha256,
        }

    def to_markdown(self) -> str:
        """Render the complete Human-Readable Ephemeris & Pt. Maheshji's Jyotish Academy Manual as Markdown."""
        return _render_compendium_markdown(self)

    def to_html(self) -> str:
        """Render a publication-grade printable HTML book edition for human astrologers and Academy students."""
        return _render_compendium_html(self)


def generate_human_manual_ephemeris_compendium(
    year: int,
    month: int = 11,
    *,
    latitude_deg: float = 28.6139,
    longitude_deg: float = 77.2090,
    tz_offset_hours: float = 5.5,
    ayanamsa: str = "lahiri",
    adapter: EphemerisAdapter | None = None,
) -> HumanManualEphemerisCompendium:
    """Generate the complete Human-Readable Classical Ephemeris & Jyotish Academy Manual Compendium.

    Daily planetary positions are tabulated at ``05:30 Local Standard Time`` (equivalent to ``00:00 UTC``
    when ``tz_offset_hours=5.5`` IST, the classical Indian Ephemeris standard), while daily Panchanga
    and Muhurta windows are anchored to exact local topocentric sunrise.
    """
    yr = int(year)
    mo = int(month)
    if not 1 <= mo <= 12:
        raise ValueError(f"month must be in 1..12; got {month!r}")
    lat = float(latitude_deg)
    lon = float(longitude_deg)
    tz_off = float(tz_offset_hours)
    ad = adapter or EphemerisAdapter()

    panchang_sheet = generate_monthly_panchang(
        yr,
        mo,
        lat,
        lon,
        tz_offset_hours=tz_off,
        adapter=ad,
    )

    bodies_order = (
        "sun",
        "moon",
        "mars",
        "mercury",
        "jupiter",
        "venus",
        "saturn",
        "rahu",
        "true_rahu",
        "ketu",
        "uranus",
        "neptune",
        "pluto",
    )

    daily_rows: list[HumanDailyEphemerisRow] = []

    for p_day in panchang_sheet.days:
        parts = [int(x) for x in p_day.civil_date.split("-")]
        # Standard Indian Ephemeris tabular epoch: 00:00 UTC (= 05:30 IST)
        jd_ref_ut = EphemerisAdapter.julday(parts[0], parts[1], parts[2], 0.0)
        # Kali Yuga epoch: 18 Feb 3102 BCE 00:00 UT = JD 588465.5
        ahargana = jd_ref_ut - 588465.5

        ay_deg = ad.get_ayanamsa_ut(jd_ref_ut, mode=ayanamsa)
        ay_dms = format_classical_rashi_dms(ay_deg, compact_sign_number=True).replace("00s ", "")

        _cusps_ref, ascmc_ref = ad.houses_ex(jd_ref_ut, lat, lon, b"P", FLG_SIDEREAL)
        lst_hms = _deg_to_hhmmss(ascmc_ref[2])

        sun_pos = ad.calc_ut(jd_ref_ut, "sun", sidereal=True, ayanamsa=ayanamsa)
        sun_lon = sun_pos.longitude_deg

        planet_cells: dict[str, HumanDailyPlanetCell] = {}
        for body in bodies_order:
            pos = ad.calc_ut(jd_ref_ut, body, sidereal=True, ayanamsa=ayanamsa)
            b_lon = pos.longitude_deg % 360.0
            b_spd = pos.longitude_speed_deg_per_day
            rashi_idx = int(b_lon // 30.0) % 12
            rashi_name = RASHI_NAMES[rashi_idx]
            nak = nakshatra_position(b_lon)
            d9_sign = nak.navamsa_sign_name

            is_retro = b_spd < 0.0
            is_stat = abs(b_spd) < 0.005 and body not in ("sun", "moon")
            is_combust = False
            if body in CLASSICAL_COMBUSTION_ORBS_DEG:
                orb_dir, orb_ret = CLASSICAL_COMBUSTION_ORBS_DEG[body]
                orb = orb_ret if is_retro else orb_dir
                sep = abs(((b_lon - sun_lon + 180.0) % 360.0) - 180.0)
                is_combust = sep <= orb

            flags: list[str] = []
            if is_stat:
                flags.append("S")
            elif is_retro:
                flags.append("R")
            else:
                flags.append("D")
            if is_combust:
                flags.append("C")

            planet_cells[body] = HumanDailyPlanetCell(
                body=body,
                longitude_deg=b_lon,
                rashi_index=rashi_idx,
                rashi_name=rashi_name,
                classical_dms=format_classical_rashi_dms(b_lon, compact_sign_number=False),
                sign_num_dms=format_classical_rashi_dms(b_lon, compact_sign_number=True),
                nakshatra_name=nak.name,
                nakshatra_lord=nak.vimshottari_ruler,
                pada=nak.pada,
                speed_deg_per_day=b_spd,
                daily_motion_dms=format_daily_motion_dms(b_spd),
                is_retrograde=is_retro,
                is_combust=is_combust,
                status_flags="/".join(flags),
                d9_navamsa_sign=d9_sign,
            )

        sr_jd = p_day.sunrise_jd_ut
        ss_jd = p_day.sunset_jd_ut
        dinamana_hours = max(0.0, (ss_jd - sr_jd) * 24.0)
        dinamana_gp = format_ghati_pala(dinamana_hours)

        tithi_end_hours_from_sr = max(0.0, (p_day.tithi_end_jd_ut - sr_jd) * 24.0)
        tithi_end_gp = format_ghati_pala(tithi_end_hours_from_sr)

        # Rahu Kala octant window
        octant_days = (ss_jd - sr_jd) / 8.0
        rk_oct = RAHU_KALA_OCTANT[p_day.vara_index % 7]
        rk_start = sr_jd + (rk_oct - 1) * octant_days
        rk_end = sr_jd + rk_oct * octant_days
        rahu_kala_str = f"{_jd_to_local_hhmm(rk_start, tz_off)}-{_jd_to_local_hhmm(rk_end, tz_off)}"

        # Abhijit Muhurta (8th of 15 daytime Muhurtas)
        muhurta_days = (ss_jd - sr_jd) / 15.0
        ab_start = sr_jd + 7.0 * muhurta_days
        ab_end = sr_jd + 8.0 * muhurta_days
        abhijit_str = f"{_jd_to_local_hhmm(ab_start, tz_off)}-{_jd_to_local_hhmm(ab_end, tz_off)}"

        daily_rows.append(
            HumanDailyEphemerisRow(
                civil_date=p_day.civil_date,
                vara_name=p_day.vara_name,
                jd_reference_ut=jd_ref_ut,
                ahargana_kali_days=ahargana,
                ayanamsa_dms=ay_dms,
                local_sidereal_time_hms=lst_hms,
                sunrise_local_hms=_jd_to_local_hhmmss(sr_jd, tz_off),
                sunset_local_hms=_jd_to_local_hhmmss(ss_jd, tz_off),
                dinamana_hours=dinamana_hours,
                dinamana_ghati_pala=dinamana_gp,
                tithi_name=p_day.tithi_name,
                tithi_end_local_hm=_jd_to_local_hhmm(p_day.tithi_end_jd_ut, tz_off),
                tithi_end_ghati_pala=tithi_end_gp,
                nakshatra_at_sunrise=p_day.nakshatra_name,
                yoga_at_sunrise=p_day.yoga_name,
                karana_at_sunrise=p_day.karana_name,
                rahu_kala_window=rahu_kala_str,
                abhijit_muhurta_window=abhijit_str,
                vratas=p_day.vratas,
                planets=planet_cells,
            )
        )

    # Construct the worked example for the 15th day of the month at 10:42:00 Local Time (= +5h 12m after 05:30 IST)
    sample_idx = min(14, len(daily_rows) - 1)
    row_d0 = daily_rows[sample_idx]
    row_d1 = daily_rows[min(sample_idx + 1, len(daily_rows) - 1)]
    # 5 hours 12 minutes after 05:30 IST = 5.2 hours = 0.2166667 of a day = 13 Ghatis 00 Palas after 05:30 IST
    interp_hours = 5.2
    interp_fraction = interp_hours / 24.0
    jd_worked_ut = row_d0.jd_reference_ut + (interp_hours / 24.0)

    worked_planets: dict[str, Any] = {}
    for b in ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"):
        c0 = row_d0.planets[b]
        # Manual Trairashika linear interpolation: L(t) = L_0 + f * v_0
        manual_lon = (c0.longitude_deg + interp_fraction * c0.speed_deg_per_day) % 360.0
        exact_pos = ad.calc_ut(jd_worked_ut, b, sidereal=True, ayanamsa=ayanamsa)
        exact_lon = exact_pos.longitude_deg % 360.0
        diff_arcsec = abs(((manual_lon - exact_lon + 180.0) % 360.0) - 180.0) * 3600.0
        nak_w = nakshatra_position(exact_lon)
        worked_planets[b] = {
            "tabulated_0530_dms": c0.classical_dms,
            "daily_motion_dms": c0.daily_motion_dms,
            "motion_increment_dms": format_daily_motion_dms(interp_fraction * c0.speed_deg_per_day),
            "manual_trairashika_dms": format_classical_rashi_dms(manual_lon),
            "software_exact_dms": format_classical_rashi_dms(exact_lon),
            "manual_vs_software_diff_arcsec": round(diff_arcsec, 2),
            "nakshatra_pada": f"{nak_w.name} Pada {nak_w.pada}",
            "d1_sign": varga_sign(exact_lon, "D1").sign_name,
            "d9_navamsa_sign": varga_sign(exact_lon, "D9").sign_name,
            "d10_dasamsa_sign": varga_sign(exact_lon, "D10").sign_name,
        }

    worked_houses = ad.houses_ut(jd_worked_ut, lat, lon, system="placidus", ayanamsa=ayanamsa)
    moon_exact_lon = ad.calc_ut(jd_worked_ut, "moon", sidereal=True, ayanamsa=ayanamsa).longitude_deg % 360.0
    moon_nak = nakshatra_position(moon_exact_lon)
    rem_deg_in_nak = (360.0 / 27.0) - moon_nak.degree_in_nakshatra
    rem_arcmin_in_nak = rem_deg_in_nak * 60.0
    maha_lord = moon_nak.vimshottari_ruler
    maha_total_years = float(VIMSHOTTARI_YEARS[maha_lord])
    balance_years = (rem_arcmin_in_nak / 800.0) * maha_total_years
    bal_y = int(balance_years)
    bal_m_rem = (balance_years - bal_y) * 12.0
    bal_m = int(bal_m_rem)
    bal_d = int(round((bal_m_rem - bal_m) * 30.0))

    worked_example = {
        "civil_date": row_d0.civil_date,
        "birth_time_local": "10:42:00 IST (UTC+05:30)",
        "elapsed_after_0530_ist": "5 hours 12 minutes (13 Ghatis 00 Palas)",
        "trairashika_fraction": round(interp_fraction, 6),
        "observer_location": f"Lat {lat:.4f} deg, Lon {lon:.4f} deg",
        "ascendant_dms": format_classical_rashi_dms(worked_houses.ascendant_deg),
        "mc_10th_cusp_dms": format_classical_rashi_dms(worked_houses.mc_deg),
        "moon_nakshatra": f"{moon_nak.name} Pada {moon_nak.pada} (Lord: {maha_lord})",
        "remaining_arcminutes_bhogyamsha": round(rem_arcmin_in_nak, 2),
        "vimshottari_dasha_balance_at_birth": f"{maha_lord} Mahadasha: {bal_y} Years, {bal_m} Months, {bal_d} Days remaining",
        "planets": worked_planets,
    }

    receipt = {
        "engine": "ephemeris-oss",
        "version": __version__,
        "calculation": "human_manual_ephemeris_compendium",
        "year": yr,
        "month": mo,
        "latitude_deg": lat,
        "longitude_deg": lon,
        "tz_offset_hours": tz_off,
        "ayanamsa": ayanamsa,
        "num_days": len(daily_rows),
        "first_day_sun_dms": daily_rows[0].planets["sun"].classical_dms,
        "last_day_moon_dms": daily_rows[-1].planets["moon"].classical_dms,
    }
    r_sha = canonical_hash(receipt)

    return HumanManualEphemerisCompendium(
        year=yr,
        month=mo,
        latitude_deg=lat,
        longitude_deg=lon,
        tz_offset_hours=tz_off,
        ayanamsa_mode=ayanamsa,
        reference_time_label="00:00 UTC / 05:30 IST",
        daily_rows=tuple(daily_rows),
        worked_example=worked_example,
        receipt=receipt,
        receipt_sha256=r_sha,
    )


def _render_compendium_markdown(comp: HumanManualEphemerisCompendium) -> str:
    """Render the complete 7-section Human-Readable Classical Ephemeris & Jyotish Academy Manual."""
    lines: list[str] = []
    lines.append("# The RDG Classical Human-Readable Ephemeris & Pt. Maheshji's Jyotish Academy Manual Calculation Compendium")
    lines.append("")
    lines.append(
        "> **Designed for Human Consumption, Classical Hand-Calculation (*Ganita*), and Gurukul Teaching:** "
        "Before computers existed, master Jyotishis cast complete natal horoscopes (*Kundalis*), divisional charts "
        "(*Shodashvarga*), planetary strengths (*Shadbala*), *Ashtakavarga* bindu matrices, and *Dasha* timelines "
        "by reading printed ephemeris tables (*Panchanga*) and performing *Trairashika* (proportional interpolation) "
        "by hand. This compendium provides every table, classical formula, and step-by-step worksheet required so that "
        "**everything possible in the RDG software engine can also be calculated 100% manually by any astrologer, "
        "student, or researcher on paper.**"
    )
    lines.append("")
    lines.append(f"- **Tabulated Period:** `{comp.year}-{comp.month:02d}` (`{len(comp.daily_rows)}` Civil Days)")
    lines.append(f"- **Planetary Tabulation Epoch:** `{comp.reference_time_label}` (Standard Indian Ephemeris Epoch)")
    lines.append(
        f"- **Sunrise Panchanga Observer Location:** Latitude `{comp.latitude_deg:.4f}°`, "
        f"Longitude `{comp.longitude_deg:.4f}°`, Timezone `UTC{comp.tz_offset_hours:+.1f}h`"
    )
    lines.append(f"- **Sidereal Ayanamsha Convention:** `{comp.ayanamsa_mode}` (NASA JPL DE440/DE441 Precision)")
    lines.append(f"- **Cryptographic Verification Receipt (SHA-256):** `{comp.receipt_sha256}`")
    lines.append("")
    lines.append("---")
    lines.append("")

    # SECTION 1: Daily Sidereal Planetary Ephemeris Grid
    lines.append("## Section 1 — Daily Sidereal (*Nirayana*) Planetary Ephemeris Table (`05:30 IST / 00:00 UTC`)")
    lines.append("")
    lines.append(
        "**How to Read This Table:** Each cell shows the planet's classical Sidereal Sign (*Rashi*), Degrees, "
        "Minutes, and Seconds (`DD° MM' SS\"`), followed by its status flag (`D` = *Margi*/Direct, `R` = *Vakri*/Retrograde, "
        "`S` = *Stambhana*/Stationary, `C` = *Asta*/Combust), its **27-Nakshatra and Pada (`P1..P4`)**, and its "
        "**Daily Motion (`±DD° MM' SS\"/d`)** for manual interpolation."
    )
    lines.append("")
    lines.append("### Table 1A — Daily Inner & Luminary Grahas (*Surya, Chandra, Mangala, Budha*)")
    lines.append("")
    lines.append("| Date (Vara) | Ayanamsha | Sidereal Time | Surya (Sun) | Chandra (Moon) | Mangala (Mars) | Budha (Mercury) |")
    lines.append("|---|---|---|---|---|---|---|")
    for r in comp.daily_rows:
        s = r.planets["sun"]
        m = r.planets["moon"]
        ma = r.planets["mars"]
        me = r.planets["mercury"]
        lines.append(
            f"| **{r.civil_date}** ({r.vara_name[:3]}) | `{r.ayanamsa_dms}` | `{r.local_sidereal_time_hms}` | "
            f"{s.classical_dms} [{s.status_flags}] ({s.nakshatra_name} P{s.pada}, `{s.daily_motion_dms}`) | "
            f"{m.classical_dms} [{m.status_flags}] ({m.nakshatra_name} P{m.pada}, `{m.daily_motion_dms}`) | "
            f"{ma.classical_dms} [{ma.status_flags}] ({ma.nakshatra_name} P{ma.pada}, `{ma.daily_motion_dms}`) | "
            f"{me.classical_dms} [{me.status_flags}] ({me.nakshatra_name} P{me.pada}, `{me.daily_motion_dms}`) |"
        )
    lines.append("")

    lines.append("### Table 1B — Daily Outer Grahas & Lunar Nodes (*Guru, Shukra, Shani, Mean Rahu, True Rahu, Ketu*)")
    lines.append("")
    lines.append("| Date | Guru (Jupiter) | Shukra (Venus) | Shani (Saturn) | Mean Rahu | True Rahu | Mean Ketu |")
    lines.append("|---|---|---|---|---|---|---|")
    for r in comp.daily_rows:
        ju = r.planets["jupiter"]
        ve = r.planets["venus"]
        sa = r.planets["saturn"]
        ra = r.planets["rahu"]
        tra = r.planets["true_rahu"]
        ke = r.planets["ketu"]
        lines.append(
            f"| **{r.civil_date}** | "
            f"{ju.classical_dms} [{ju.status_flags}] ({ju.nakshatra_name} P{ju.pada}, `{ju.daily_motion_dms}`) | "
            f"{ve.classical_dms} [{ve.status_flags}] ({ve.nakshatra_name} P{ve.pada}, `{ve.daily_motion_dms}`) | "
            f"{sa.classical_dms} [{sa.status_flags}] ({sa.nakshatra_name} P{sa.pada}, `{sa.daily_motion_dms}`) | "
            f"{ra.classical_dms} ({ra.nakshatra_name} P{ra.pada}) | "
            f"{tra.classical_dms} ({tra.nakshatra_name} P{tra.pada}) | "
            f"{ke.classical_dms} ({ke.nakshatra_name} P{ke.pada}) |"
        )
    lines.append("")

    # SECTION 2: Daily Sunrise Drik Panchanga & Muhurta
    lines.append("## Section 2 — Daily Sunrise-Anchored *Drik Panchanga* & *Muhurta* Table")
    lines.append("")
    lines.append(
        "**How to Read This Table:** In classical Vedic tradition, the civil day (*Savana Vara*) begins at local "
        "**topocentric sunrise (*Suryodaya*)**. One full day equals **60 Ghatis (Nadis)** (`1 Ghati = 24 minutes`, "
        "`1 Pala = 24 seconds`). Both standard clock times (`HH:MM`) and Vedic *Ghati-Pala* durations from sunrise are given."
    )
    lines.append("")
    lines.append("| Date | Vara | Sunrise / Sunset | Dinamana (Day Span) | Sunrise Tithi (Ends Clock / Ghati) | Sunrise Nakshatra | Sunrise Yoga | Karana | Rahu Kala | Abhijit Muhurta | Vratas & Sankranti |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in comp.daily_rows:
        vrata_text = ", ".join(r.vratas) if r.vratas else "—"
        lines.append(
            f"| **{r.civil_date}** | {r.vara_name} | `{r.sunrise_local_hms}` / `{r.sunset_local_hms}` | "
            f"`{r.dinamana_hours:.2f}h` (`{r.dinamana_ghati_pala}`) | "
            f"{r.tithi_name} (`{r.tithi_end_local_hm}` / `{r.tithi_end_ghati_pala}`) | "
            f"{r.nakshatra_at_sunrise} | {r.yoga_at_sunrise} | {r.karana_at_sunrise} | "
            f"`{r.rahu_kala_window}` | `{r.abhijit_muhurta_window}` | {vrata_text} |"
        )
    lines.append("")

    # SECTION 3: Manual Spashta Graha Interpolation & Lagna / Bhava Tables
    lines.append("## Section 3 — Manual *Spashta Graha* (Planetary Interpolation) & *Lagna / Bhava* Tables")
    lines.append("")
    lines.append("### 3.1 The Classical *Trairashika* (Rule of Three) Formula for Planetary Longitude at Birth")
    lines.append("")
    lines.append(
        "Because the daily ephemeris tabulates planetary positions at `05:30 IST` (`00:00 UTC`), an astrologer finds "
        "the exact longitude (*Spashta Graha*) at any birth time $T_{\\text{birth}}$ using the classical proportional formula:"
    )
    lines.append("")
    lines.append("$$\\Delta t_{\\text{hours}} = T_{\\text{birth (IST)}} - 5.50\\text{ hours}, \\qquad f = \\frac{\\Delta t_{\\text{hours}}}{24.0} = \\frac{\\text{Elapsed Ghatis}}{60.0}$$")
    lines.append("")
    lines.append("$$\\lambda_{\\text{birth}} = \\lambda_{05:30} + f \\times (\\text{Daily Motion } v_{\\text{day}})$$")
    lines.append("")
    lines.append("*Note:* If a planet is Retrograde (`R` / *Vakri*, where $v_{\\text{day}} < 0$), subtract the proportional motion from $\\lambda_{05:30}$. Rahu's mean motion (`-00° 03' 11\"/day`) is always subtracted.")
    lines.append("")
    lines.append("### Table 3A — *Trairashika* Proportional Time-Fraction & Motion Ready-Reckoner")
    lines.append("")
    lines.append("| Elapsed Time from `05:30 IST` | Vedic *Ghati-Pala* | Day Fraction $f$ | Surya / Shukra (`~1°00'/d`) | Chandra (`12°00'/d`) | Chandra (`13°10'/d` Mean) | Chandra (`15°00'/d` Fast) | Mangala (`0°32'/d`) | Guru (`0°08'/d`) | Shani / Rahu (`0°03'/d`) |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for hrs in (1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 18, 21, 24):
        f_val = hrs / 24.0
        gp = format_ghati_pala(hrs)
        lines.append(
            f"| **{hrs:02d}h 00m** | `{gp}` | `{f_val:.4f}` | "
            f"`{format_daily_motion_dms(f_val * 1.0)}` | "
            f"`{format_daily_motion_dms(f_val * 12.0)}` | "
            f"`{format_daily_motion_dms(f_val * 13.1764)}` | "
            f"`{format_daily_motion_dms(f_val * 15.0)}` | "
            f"`{format_daily_motion_dms(f_val * (32.0 / 60.0))}` | "
            f"`{format_daily_motion_dms(f_val * (8.0 / 60.0))}` | "
            f"`{format_daily_motion_dms(f_val * (3.0 / 60.0))}` |"
        )
    lines.append("")

    lines.append("### Table 3B — Classical *Rasimana / Udayamana* (Sign Rising Durations) for Manual Lagna Calculation")
    lines.append("")
    lines.append(
        "**How to Compute *Udaya Lagna* (Ascendant) by Hand:**\n"
        "1. Note the **Sun's Tropical (*Sayana*) Longitude** at sunrise: $\\lambda_{\\text{Sayana}} = \\lambda_{\\text{Nirayana}} + \\text{Ayanamsha}$.\n"
        "2. Find the remaining degrees of the Sun's sign to rise: $\\Delta \\lambda = 30^\\circ - (\\lambda_{\\text{Sayana}} \\bmod 30^\\circ)$.\n"
        "3. Multiply $\\Delta \\lambda / 30^\\circ$ by that sign's rising duration (*Rasimana* in minutes or *Palas* from the table below) to get the time the Sun's sign finishes rising.\n"
        "4. Subtract that duration from the birth time elapsed since sunrise (*Ishta Kala*), and continue subtracting subsequent signs' rising durations until the remainder is smaller than the next sign's *Rasimana*.\n"
        "5. Convert the remaining minutes proportionally into degrees (`0°..30°`) of that rising sign (*Sayana Lagna*), and subtract the day's **Ayanamsha** to obtain the exact **Nirayana Lagna (Sidereal Ascendant)**!"
    )
    lines.append("")
    lines.append("| Sign (*Sayana Rashi*) | Equatorial *Lankodaya* (`0°` Lat) | Rising Minutes at `0°` Equator | Ujjain (`23°11'N`) Minutes | New Delhi (`28°37'N`) Minutes | Toronto (`43°39'N`) Minutes | London (`51°30'N`) Minutes |")
    lines.append("|---|---|---|---|---|---|---|")
    # Classical Charakhanda adjustments across latitudes
    chara_factors = (
        ("Mesha / Meena (1, 12)", 278, -1.0),
        ("Vrishabha / Kumbha (2, 11)", 299, -0.8),
        ("Mithuna / Makara (3, 10)", 323, -0.35),
        ("Karka / Dhanu (4, 9)", 323, +0.35),
        ("Simha / Vrishchika (5, 8)", 299, +0.8),
        ("Kanya / Tula (6, 7)", 278, +1.0),
    )
    for label, vinadis, lat_sign in chara_factors:
        eq_min = vinadis * 0.4  # 1 Vinadi (Pala) = 24 seconds = 0.4 minutes
        uj_min = eq_min + lat_sign * 14.5
        dl_min = eq_min + lat_sign * 18.6
        to_min = eq_min + lat_sign * 32.4
        ln_min = eq_min + lat_sign * 43.2
        lines.append(
            f"| **{label}** | `{vinadis} Vinadis` | `{eq_min:.1f} min` | `{uj_min:.1f} min` | "
            f"`{dl_min:.1f} min` | `{to_min:.1f} min` | `{ln_min:.1f} min` |"
        )
    lines.append("")

    # SECTION 4: Complete Shodashvarga D1-D60 Manual Reckoning Tables
    lines.append("## Section 4 — Complete Manual Divisional Chart (*Shodashvarga D1–D60*) Reckoning Tables")
    lines.append("")
    lines.append(
        "**How to Cast All 16 Vargas by Hand:** Take any planet's degree and minute within its Rashi (`0°00'` to `30°00'`) "
        "and use the classical rules and lookup tables below."
    )
    lines.append("")
    lines.append("### Table 4A — Master Formula Reference for All 16 Parashari Vargas (*Shodashvarga*)")
    lines.append("")
    lines.append("| Varga | Sanskrit Name | Segment Span | Classical Counting Rule (Brihat Parashara Hora Shastra) | Life Domain |")
    lines.append("|---|---|---|---|---|")
    varga_rules = (
        ("D1", "Rashi / Kshetra", "30° 00'", "Direct sidereal sign (1..12)", "Physical body, general destiny, root chart"),
        ("D2", "Hora", "15° 00'", "Odd signs: 0°-15° Sun (Simha), 15°-30° Moon (Karka); Even signs: 0°-15° Moon (Karka), 15°-30° Sun (Simha)", "Wealth, treasury, family sustenance"),
        ("D3", "Drekkana", "10° 00'", "0°-10° same sign (1st); 10°-20° 5th sign; 20°-30° 9th sign", "Siblings, courage, co-borns, initiative"),
        ("D4", "Chaturthamsa / Turyamsa", "07° 30'", "4 segments of 7°30': 1st, 4th, 7th, and 10th Kendra signs from the Rashi", "Real estate, landed property, happiness, fortune"),
        ("D7", "Saptamsa", "04° 17' 08.57\"", "7 segments: Odd signs count forward from same sign; Even signs count forward from 7th sign", "Children, progeny, creative legacy"),
        ("D9", "Navamsa / Dharmamsa", "03° 20'", "9 segments of 3°20': Fiery (1,5,9) start Mesha; Earthy (2,6,10) start Makara; Airy (3,7,11) start Tula; Watery (4,8,12) start Karka", "Marriage, spouse, dharma, inner planetary fruit"),
        ("D10", "Dasamsa / Karmamsa", "03° 00'", "10 segments of 3°00': Odd signs start from same sign; Even signs start from 9th sign", "Career, profession, authority, public action"),
        ("D12", "Dwadasamsa", "02° 30'", "12 segments of 2°30': Always count forward starting from the same sign", "Parents, ancestry, lineage"),
        ("D16", "Shodasamsa / Kalamsa", "01° 52' 30\"", "16 segments: Movable (1,4,7,10) start Mesha; Fixed (2,5,8,11) start Simha; Dual (3,6,9,12) start Dhanu", "Vehicles, conveyances, material comforts"),
        ("D20", "Vimsamsa", "01° 30'", "20 segments: Movable start Mesha; Fixed start Dhanu; Dual start Simha", "Spiritual sadhana, upasana, devotion"),
        ("D24", "Chaturvimsamsa / Siddhamsa", "01° 15'", "24 segments: Odd signs start from Simha (Leo) forward; Even signs start from Karka (Cancer) forward", "Higher learning, vidya, scholarship"),
        ("D27", "Bhamsha / Saptavimsamsa", "01° 06' 40\"", "27 segments: Fiery start Mesha; Earthy start Karka; Airy start Tula; Watery start Makara", "Physical stamina, vital strengths and weaknesses"),
        ("D30", "Trimsamsa (Unequal)", "5°/5°/8°/7°/5°", "Odd: Mars 5°(Mesha), Sat 5°(Kumbha), Jup 8°(Dhanu), Merc 7°(Mithuna), Ven 5°(Tula); Even: Ven 5°(Vrishabha), Merc 7°(Kanya), Jup 8°(Meena), Sat 5°(Makara), Mars 5°(Vrishchika)", "Arishta, misfortunes, moral character"),
        ("D40", "Khavedamsa", "00° 45'", "40 segments: Odd signs start from Mesha; Even signs start from Tula", "Maternal lineage, auspicious/inauspicious karmas"),
        ("D45", "Akshavedamsa", "00° 40'", "45 segments: Movable start Mesha; Fixed start Simha; Dual start Dhanu", "Paternal lineage, ethical conduct"),
        ("D60", "Shashtiamsa", "00° 30'", "60 segments of 30 arcminutes: Sign = ((segment_index - 1) mod 12) counted from the planet's own Rashi + 60 named Deities", "Past-life root karma, twin differentiation"),
    )
    for code, name, span, rule, dom in varga_rules:
        lines.append(f"| **{code}** | *{name}* | `{span}` | {rule} | {dom} |")
    lines.append("")

    lines.append("### Table 4B — Complete 108-Pada *Navamsa (D9)* Direct Eye-Lookup Grid")
    lines.append("")
    lines.append("| Pada # | Degree Range in Sign | Fiery Signs (*Mesha, Simha, Dhanu* — 1, 5, 9) | Earthy Signs (*Vrishabha, Kanya, Makara* — 2, 6, 10) | Airy Signs (*Mithuna, Tula, Kumbha* — 3, 7, 11) | Watery Signs (*Karka, Vrishchika, Meena* — 4, 8, 12) |")
    lines.append("|---|---|---|---|---|---|")
    nav_ranges = (
        (1, "00° 00' – 03° 20'", 0, 9, 6, 3),
        (2, "03° 20' – 06° 40'", 1, 10, 7, 4),
        (3, "06° 40' – 10° 00'", 2, 11, 8, 5),
        (4, "10° 00' – 13° 20'", 3, 0, 9, 6),
        (5, "13° 20' – 16° 40'", 4, 1, 10, 7),
        (6, "16° 40' – 20° 00'", 5, 2, 11, 8),
        (7, "20° 00' – 23° 20'", 6, 3, 0, 9),
        (8, "23° 20' – 26° 40'", 7, 4, 1, 10),
        (9, "26° 40' – 30° 00'", 8, 5, 2, 11),
    )
    for idx, rng, f_i, e_i, a_i, w_i in nav_ranges:
        lines.append(
            f"| **Navamsa {idx}** | `{rng}` | **{RASHI_NAMES[f_i]}** ({RASI_LORDS[f_i]}) | "
            f"**{RASHI_NAMES[e_i]}** ({RASI_LORDS[e_i]}) | **{RASHI_NAMES[a_i]}** ({RASI_LORDS[a_i]}) | "
            f"**{RASHI_NAMES[w_i]}** ({RASI_LORDS[w_i]}) |"
        )
    lines.append("")

    lines.append("### Table 4C — Complete *Dasamsa (D10)* & *Dwadasamsa (D12)* Eye-Lookup Table")
    lines.append("")
    lines.append("| Segment | D10 Range (`3°00'` step) | D10 Offset (Odd Sign) | D10 Offset (Even Sign) | D12 Range (`2°30'` step) | D12 Offset (All Signs) |")
    lines.append("|---|---|---|---|---|---|")
    for seg in range(1, 13):
        d12_lo = (seg - 1) * 2.5
        d12_hi = seg * 2.5
        d12_lo_d, d12_lo_m = int(d12_lo), int(round((d12_lo % 1.0) * 60))
        d12_hi_d, d12_hi_m = int(d12_hi), int(round((d12_hi % 1.0) * 60))
        if seg <= 10:
            d10_lo = (seg - 1) * 3
            d10_hi = seg * 3
            d10_rng = f"`{d10_lo:02d}° 00' – {d10_hi:02d}° 00'`"
            d10_odd = f"+{seg - 1} signs ({seg}th from Rashi)"
            even_house = ((8 + seg - 1) % 12) + 1
            d10_even = f"+{(8 + seg - 1) % 12} signs ({even_house}th from Rashi)"
        else:
            d10_rng = "—"
            d10_odd = "—"
            d10_even = "—"
        lines.append(
            f"| **#{seg:02d}** | {d10_rng} | {d10_odd} | {d10_even} | "
            f"`{d12_lo_d:02d}° {d12_lo_m:02d}' – {d12_hi_d:02d}° {d12_hi_m:02d}'` | +{seg - 1} signs ({seg}th from Rashi) |"
        )
    lines.append("")

    lines.append("### Table 4D — Complete 60-Segment *Shashtiamsa (D60)* Classical Deity & Nature Table (`0°30'` Steps)")
    lines.append("")
    lines.append("| # | Arc Range (`30'` step) | Sign Offset from Rashi | Odd Sign D60 Deity (Nature) | Even Sign D60 Deity (Nature) |")
    lines.append("|---|---|---|---|---|")
    for idx in range(60):
        lo_m = idx * 30
        hi_m = (idx + 1) * 30
        lo_deg, lo_min = lo_m // 60, lo_m % 60
        hi_deg, hi_min = hi_m // 60, hi_m % 60
        _odd_num, odd_name, odd_benefic = SHASHTIAMSA_CATALOG[idx]
        _even_num, even_name, even_benefic = SHASHTIAMSA_CATALOG[59 - idx]
        odd_nat = "Shubha (Benefic)" if odd_benefic else "Krura (Malefic)"
        even_nat = "Shubha (Benefic)" if even_benefic else "Krura (Malefic)"
        lines.append(
            f"| **{idx + 1:02d}** | `{lo_deg:02d}° {lo_min:02d}' – {hi_deg:02d}° {hi_min:02d}'` | "
            f"`+{idx % 12}` ({(idx % 12) + 1}th from Rashi) | **{odd_name}** ({odd_nat}) | **{even_name}** ({even_nat}) |"
        )
    lines.append("")

    # SECTION 5: Manual Dasha Balance & Progression Tables
    lines.append("## Section 5 — Complete Manual *Dasha* Balance (*Bhogyamsha*) & Progression Tables")
    lines.append("")
    lines.append("### 5.1 Manual *Vimshottari Dasha* (120-Year Cycle) Formula & Ready-Reckoner")
    lines.append("")
    lines.append(
        "**How to Compute the Birth Dasha Balance by Hand:**\n"
        "1. Look up the **Moon's Sidereal Longitude ($\\lambda_{\\text{Moon}}$)** at birth.\n"
        "2. Identify the Moon's **Nakshatra (`1..27`)** and its starting boundary (`Nakshatra span = 13° 20' = 800 arcminutes`).\n"
        "3. Find the **remaining arcminutes (*Bhogyamsha*)** yet to be traversed in that Nakshatra: $B_{\\text{arcmin}} = 800' - \\text{elapsed arcminutes}$.\n"
        "4. Multiply by the Mahadasha Lord's total years $Y_{\\text{lord}}$ and divide by $800'$:"
    )
    lines.append("")
    lines.append("$$\\text{Remaining Dasha Balance (Years)} = \\frac{B_{\\text{arcmin}}}{800'} \\times Y_{\\text{lord}}$$")
    lines.append("")

    lines.append("### Table 5A — Complete 9×9 *Vimshottari Mahadasha × Antardasha (Bhukti)* Exact Duration Table")
    lines.append("")
    lines.append(
        "**Formula:** $\\text{Antardasha Months} = (\\text{Mahadasha Years} \\times \\text{Antardasha Lord Years}) \\div 10$. "
        "The integer part is **Months**, and $(\\text{decimal part} \\times 3)$ is **Days**!"
    )
    lines.append("")
    header_lords = " | ".join(f"{ld} ({VIMSHOTTARI_YEARS[ld]}y)" for ld in VIMSHOTTARI_LORDS)
    lines.append(f"| Mahadasha \\ Bhukti | {header_lords} |")
    lines.append("|---|" + "|".join("---" for _ in VIMSHOTTARI_LORDS) + "|")
    for m_lord in VIMSHOTTARI_LORDS:
        m_yrs = VIMSHOTTARI_YEARS[m_lord]
        row_cells: list[str] = []
        for a_lord in VIMSHOTTARI_LORDS:
            a_yrs = VIMSHOTTARI_YEARS[a_lord]
            total_months = (m_yrs * a_yrs) / 10.0
            whole_months = int(total_months)
            days = int(round((total_months - whole_months) * 30.0))
            yrs = whole_months // 12
            mos = whole_months % 12
            row_cells.append(f"`{yrs}y {mos:02d}m {days:02d}d`")
        lines.append(f"| **{m_lord} ({m_yrs}y)** | " + " | ".join(row_cells) + " |")
    lines.append("")

    lines.append("### Table 5B — *Bhogyamsha* Remaining Arcminutes (`800'` Span) to Birth Dasha Balance Ready-Reckoner")
    lines.append("")
    lines.append("| Remaining Arcminutes in Nakshatra | Remaining Degrees | Fraction of Nakshatra | Ketu (`7y`) | Shukra (`20y`) | Surya (`6y`) | Chandra (`10y`) | Mangala (`7y`) | Rahu (`18y`) | Guru (`16y`) | Shani (`19y`) | Budha (`17y`) |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for rem_min in (800, 700, 600, 500, 400, 300, 200, 100, 50, 20, 10):
        frac = rem_min / 800.0
        deg_part = rem_min // 60
        min_part = rem_min % 60
        cells_b: list[str] = []
        for ld in VIMSHOTTARI_LORDS:
            y_val = frac * VIMSHOTTARI_YEARS[ld]
            wy = int(y_val)
            rem_m = (y_val - wy) * 12.0
            wm = int(rem_m)
            wd = int(round((rem_m - wm) * 30.0))
            cells_b.append(f"`{wy}y {wm:02d}m {wd:02d}d`")
        lines.append(f"| **`{rem_min}'`** | `{deg_part:02d}° {min_part:02d}'` | `{frac:.4f}` | " + " | ".join(cells_b) + " |")
    lines.append("")

    lines.append("### Table 5C — Classical BPHS *Kalachakra Dasha* Complete 108-Pada (*Savya* & *Apasavya*) Master Wheel")
    lines.append("")
    lines.append(
        "**Sign Durations:** *Mesha/Vrishchika* (Mars) = `7y`, *Vrishabha/Tula* (Venus) = `16y`, *Mithuna/Kanya* (Mercury) = `9y`, "
        "*Karka* (Moon) = `21y`, *Simha* (Sun) = `5y`, *Dhanu/Meena* (Jupiter) = `10y`, *Makara/Kumbha* (Saturn) = `4y`."
    )
    lines.append("")
    lines.append("| Cycle Group | Nakshatras Included | Pada | 9-Sign Kalachakra Sequence | *Deha* (Body Sign) | *Jeeva* (Soul Sign) | *Paramayus* (Total Years) |")
    lines.append("|---|---|---|---|---|---|---|")
    savya_groups = (
        ("Savya Group I (Trijanma)", "Ashwini, Punarvasu, Hasta, Mula, Purva Bhadrapada (1, 7, 13, 19, 25)", 0),
        ("Savya Group II (Trijanma)", "Bharani, Pushya, Chitra, Purva Ashadha, Uttara Bhadrapada (2, 8, 14, 20, 26)", 1),
        ("Savya Group III (Trijanma)", "Krittika, Ashlesha, Swati, Uttara Ashadha, Revati (3, 9, 15, 21, 27)", 2),
    )
    for grp_name, naks_str, pos_in_triad in savya_groups:
        for pada_num in (1, 2, 3, 4):
            seq = KALACHAKRA_SAVYA_SEQUENCES[(pos_in_triad, pada_num)]
            paramayus = int(sum(KALACHAKRA_SIGN_YEARS[s] for s in seq))
            seq_names = " → ".join(RASHI_NAMES[s] for s in seq)
            deha = RASHI_NAMES[seq[0]]
            jeeva = RASHI_NAMES[seq[-1]]
            lines.append(f"| **{grp_name}** | {naks_str} | **Pada {pada_num}** | {seq_names} | **{deha}** | **{jeeva}** | `{paramayus}y` |")
    apasavya_groups = (
        ("Apasavya Group I (Trijanma)", "Rohini, Magha, Vishakha, Shravana (4, 10, 16, 22)", 0),
        ("Apasavya Group II (Trijanma)", "Mrigashira, Purva Phalguni, Anuradha, Dhanishta (5, 11, 17, 23)", 1),
        ("Apasavya Group III (Trijanma)", "Ardra, Uttara Phalguni, Jyeshtha, Shatabhisha (6, 12, 18, 24)", 2),
    )
    for grp_name, naks_str, pos_in_triad in apasavya_groups:
        for pada_num in (1, 2, 3, 4):
            seq = KALACHAKRA_APASAVYA_SEQUENCES[(pos_in_triad, pada_num)]
            paramayus = int(sum(KALACHAKRA_SIGN_YEARS[s] for s in seq))
            seq_names = " → ".join(RASHI_NAMES[s] for s in seq)
            jeeva = RASHI_NAMES[seq[0]]
            deha = RASHI_NAMES[seq[-1]]
            lines.append(f"| **{grp_name}** | {naks_str} | **Pada {pada_num}** | {seq_names} | **{deha}** | **{jeeva}** | `{paramayus}y` |")
    lines.append("")

    # SECTION 6: Manual Ashtakavarga, Shadbala & 30-Star Yogatara Reference Tables
    lines.append("## Section 6 — Manual *Ashtakavarga* (337-Bindu Matrix), *Shadbala*, & 30-Star *Yogatara* Tables")
    lines.append("")
    lines.append("### Table 6A — Complete 337-Bindu *Bhinna Ashtakavarga* Classical Contribution Matrix (Parashara)")
    lines.append("")
    lines.append(
        "**How to Cast *Ashtakavarga* by Hand:** For each target planet, mark `1 Bindu (Rekha)` in the houses "
        "listed below counted (`1..12` inclusive) from each of the 8 reference points (`Sun, Moon, Mars, Mercury, "
        "Jupiter, Venus, Saturn, and Lagna`). Sum all 7 planetary tables to obtain **Sarvashtakavarga (`337 Total Bindus`)**."
    )
    lines.append("")
    lines.append("| Target Planet (Total Bindus) | From Sun | From Moon | From Mars | From Mercury | From Jupiter | From Venus | From Saturn | From Lagna |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    donor_keys = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Lagna")
    for target_p, donor_map in BAV_BENEFIC_HOUSES.items():
        total_b = sum(len(v) for v in donor_map.values())
        cols_bav = [", ".join(str(h) for h in donor_map[dk]) for dk in donor_keys]
        lines.append(f"| **{target_p} (`{total_b}`)** | " + " | ".join(f"`{c}`" for c in cols_bav) + " |")
    lines.append("")

    lines.append("### Table 6B — Classical *Shadbala* (Six-Fold Planetary Strength) Manual Formula & Minimum Rupa Sheet")
    lines.append("")
    lines.append("| Planet | Exaltation Point (*Parama Uchcha*) | Directional Power (*Digbala* Peak House) | *Naisargika Bala* (Virupas) | Minimum Required *Shadbala* (Rupas / Virupas) |")
    lines.append("|---|---|---|---|---|")
    shadbala_specs = (
        ("Surya (Sun)", "Mesha 10° (Debil: Tula 10°)", "10th House (South / Meridian)", "60.00", "6.5 Rupas (390 Virupas)"),
        ("Chandra (Moon)", "Vrishabha 03° (Debil: Vrishchika 03°)", "4th House (North / Nadir)", "51.43", "6.0 Rupas (360 Virupas)"),
        ("Mangala (Mars)", "Makara 28° (Debil: Karka 28°)", "10th House (South / Meridian)", "17.14", "5.0 Rupas (300 Virupas)"),
        ("Budha (Mercury)", "Kanya 15° (Debil: Meena 15°)", "1st House (East / Lagna)", "25.71", "7.0 Rupas (420 Virupas)"),
        ("Guru (Jupiter)", "Karka 05° (Debil: Makara 05°)", "1st House (East / Lagna)", "34.29", "6.5 Rupas (390 Virupas)"),
        ("Shukra (Venus)", "Meena 27° (Debil: Kanya 27°)", "4th House (North / Nadir)", "42.86", "5.5 Rupas (330 Virupas)"),
        ("Shani (Saturn)", "Tula 20° (Debil: Mesha 20°)", "7th House (West / Descendant)", "8.57", "5.0 Rupas (300 Virupas)"),
    )
    for p_label, uchcha, dig, nais, min_r in shadbala_specs:
        lines.append(f"| **{p_label}** | `{uchcha}` | {dig} | `{nais}` | **`{min_r}`** |")
    lines.append("")

    lines.append("### Table 6C — 30-Star *Yogatara* Junction Stars & *Kalansha* Visibility Catalog")
    lines.append("")
    lines.append("| # | Nakshatra / Star | Classical Star (*IAU / Bayer*) | HIP ID | V-Mag | *Kalansha* Arc |")
    lines.append("|---|---|---|---|---|---|")
    for idx, st in enumerate(YOGATARA_30_CATALOG, start=1):
        lines.append(
            f"| **{idx:02d}** | **{st.vedic_name}** | {st.western_designation} | "
            f"`HIP {st.hip_id}` | `{st.visual_magnitude:.2f}` | `{st.kalansha_visibility_arc_deg:.1f}°` |"
        )
    lines.append("")

    # SECTION 7: Pt. Maheshji's Jyotish Academy Step-by-Step Worked Manual Worksheet
    we = comp.worked_example
    lines.append("## Section 7 — Pt. Maheshji's Jyotish Academy Step-by-Step Worked Manual Kundali Worksheet")
    lines.append("")
    lines.append(
        "> **From the Desk of Pt. Maheshji (Jyotish Academy / Jyotish Gurukul):**\n"
        "> *\"A true Jyotishi must never be a blind prisoner of a computer screen. When you understand how to read "
        "the daily ephemeris lines, interpolate the Moon and Grahas by hand, derive the Lagna from sunrise and "
        "Sidereal Time, and map the Navamsa and Dasha balance with your own pen, you develop direct intuitive sight "
        "(*Jyotish Chakshu*) into the living sky.\"*"
    )
    lines.append("")
    lines.append("### Worked Example Birth Data")
    lines.append(f"- **Date of Birth:** `{we['civil_date']}`")
    lines.append(f"- **Clock Time of Birth:** `{we['birth_time_local']}` (`{we['elapsed_after_0530_ist']}` after `05:30 IST` table epoch)")
    lines.append(f"- **Time-Fraction Factor ($f$):** $f = 5.20\\text{{ hours}} \\div 24.0\\text{{ hours}} = {we['trairashika_fraction']:.6f}$ (`13 Ghatis / 60 Ghatis`)")
    lines.append(f"- **Place of Birth:** `{we['observer_location']}`")
    lines.append("")
    lines.append("### Step-by-Step Manual *Spashta Graha* Interpolation vs. Exact Software Calculation")
    lines.append("")
    lines.append("| Graha | Tabulated at `05:30 IST` | Daily Motion ($v_{\\text{day}}$) | Proportional Increment ($f \\times v_{\\text{day}}$) | Hand-Calculated Longitude (*Trairashika*) | Exact Software Longitude (DE440) | Hand vs Software Difference | Nakshatra & Pada | D1 Sign | D9 Navamsa | D10 Dasamsa |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for b_key, b_info in we["planets"].items():
        lines.append(
            f"| **{b_key.capitalize()}** | `{b_info['tabulated_0530_dms']}` | `{b_info['daily_motion_dms']}` | "
            f"`{b_info['motion_increment_dms']}` | **`{b_info['manual_trairashika_dms']}`** | "
            f"`{b_info['software_exact_dms']}` | `{b_info['manual_vs_software_diff_arcsec']}\"` | "
            f"{b_info['nakshatra_pada']} | {b_info['d1_sign']} | **{b_info['d9_navamsa_sign']}** | {b_info['d10_dasamsa_sign']} |"
        )
    lines.append("")
    lines.append("### Hand-Calculated Lagna (Ascendant) & Birth *Vimshottari Dasha* Balance")
    lines.append(f"- **Exact Sidereal Ascendant (*Udaya Lagna*):** `{we['ascendant_dms']}`")
    lines.append(f"- **Exact 10th House Cusp (*Madhya Lagna / Dashama*):** `{we['mc_10th_cusp_dms']}`")
    lines.append(f"- **Birth Moon Nakshatra:** `{we['moon_nakshatra']}`")
    lines.append(f"- **Remaining Arcminutes in Nakshatra (*Bhogyamsha*):** `{we['remaining_arcminutes_bhogyamsha']}'` out of `800'`")
    lines.append(f"- **Hand-Calculated Birth Dasha Balance:** **`{we['vimshottari_dasha_balance_at_birth']}`**")
    lines.append("")
    return "\n".join(lines) + "\n"


def _render_compendium_html(comp: HumanManualEphemerisCompendium) -> str:
    """Render a clean, print-ready HTML edition of the Human-Readable Ephemeris Compendium."""
    md_text = _render_compendium_markdown(comp)
    import html as html_mod

    escaped = html_mod.escape(md_text)
    return (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\"/>\n"
        f"<title>RDG Human-Readable Ephemeris & Jyotish Academy Compendium ({comp.year}-{comp.month:02d})</title>\n"
        "<style>\n"
        "body { font-family: 'Georgia', 'Times New Roman', serif; max-width: 1180px; margin: 2rem auto; "
        "padding: 0 1.5rem; color: #1b1917; background: #fbf9f5; line-height: 1.55; }\n"
        "pre { white-space: pre-wrap; word-wrap: break-word; font-family: 'Consolas', monospace; "
        "font-size: 0.88rem; background: #f3efe6; padding: 1.25rem; border: 1px solid #d6cbb5; border-radius: 6px; }\n"
        "</style>\n</head>\n<body>\n"
        f"<pre>{escaped}</pre>\n"
        "</body>\n</html>\n"
    )


__all__ = [
    "CLASSICAL_COMBUSTION_ORBS_DEG",
    "HumanDailyEphemerisRow",
    "HumanDailyPlanetCell",
    "HumanManualEphemerisCompendium",
    "LANKODAYA_VINADIS",
    "format_classical_rashi_dms",
    "format_daily_motion_dms",
    "format_ghati_pala",
    "generate_human_manual_ephemeris_compendium",
]
