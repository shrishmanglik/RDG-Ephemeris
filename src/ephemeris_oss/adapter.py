"""Unified downstream provider adapter and complete Kundali bundle facade.

Provides :class:`EphemerisAdapter`, a self-contained, drop-in positional
astronomy and Vedic Jyotish calculation facade backed by the embedded
compact Chebyshev DE440 kernel (``kernels="compact"`` by default) or a full
SPK kernel cache, with deterministic SHA-256 receipts at every layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
import math
import os
from pathlib import Path
from typing import Any, Callable, Iterator, Mapping, Sequence

import erfa
import numpy as np

from ._api import EarthOrientation, Engine, EphemerisError
from ._version import __version__
from .engine.contracts import AstronomyDataUnavailable
from .engine.conventions import (
    ascendant_midheaven_from_sidereal,
    ayanamsa_degrees,
    house_angles,
    house_layout,
    mean_lunar_node_longitude_degrees,
    mean_ecliptic_matrix,
    normalize_degrees,
    osculating_lunar_node_longitude_degrees,
    validate_tt_tdb,
)
from .engine.civil_time import CalendarSystem, calendar_date
from .engine.earth_orientation import UtcCalendarInstant, estimate_delta_t
from .engine.eclipses import find_lunar_eclipses, find_solar_eclipses
from .engine.numerical_provider import J2000_JD, SECONDS_PER_DAY, TimeScaleState
from .engine.receipt import canonical_hash
from .engine.stellar_anchors import (
    stellar_anchor_for_ayanamsa,
    tropical_longitude_degrees as stellar_tropical_longitude_degrees,
)
from .engine.uncertainty_envelope import (
    BoundarySensitivityEnvelope,
    compute_boundary_sensitivity,
)
from .fact_sheet import AIFactSheet, compile_ai_fact_sheet
from .jyotish import VedicChartAnalysis, compute_vedic_chart_analysis
from .jyotish_advanced.kp import KpPositionLords, kp_coordinate_lords
from .jyotish_advanced.yogas import ClassicalYogaReport, evaluate_classical_yogas
from .jyotish_jaimini.sutras import (
    JaiminiAyurdayaResult,
    KarakamsaAnalysis,
    compute_jaimini_ayurdaya,
    compute_karakamsa_analysis,
)
from .jyotish_nadi.bhrigu import BhriguBinduReport, compute_bhrigu_bindu
from .jyotish_nadi.khara_mrityu import KharaPointsReport, compute_khara_points
from .visualization.kundali_svg import (
    SvgChartArtifact,
    render_north_indian_svg,
    render_south_indian_svg,
)

AU_KM: float = 149597870.7

# Canonical integer body codes (0..11)
SUN: int = 0
MOON: int = 1
MERCURY: int = 2
VENUS: int = 3
MARS: int = 4
JUPITER: int = 5
SATURN: int = 6
URANUS: int = 7
NEPTUNE: int = 8
PLUTO: int = 9
RAHU: int = 10
MEAN_NODE: int = 10
KETU: int = 11
SOUTH_NODE: int = 11
TRUE_NODE: int = 100

# Sidecar-compatible bitflags and event codes
FLG_SWIEPH: int = 2
FLG_SPEED: int = 256
FLG_EQUATORIAL: int = 2048
FLG_TOPOCTR: int = 32768
FLG_SIDEREAL: int = 65536

CALC_RISE: int = 1
CALC_SET: int = 2

ECL_TOTAL: int = 4
ECL_ANNULAR: int = 8
ECL_PARTIAL: int = 16
ECL_ANNULAR_TOTAL: int = 32
ECL_PENUMBRAL: int = 64

BODY_CODE_MAP: Mapping[int, str] = {
    0: "sun",
    1: "moon",
    2: "mercury",
    3: "venus",
    4: "mars",
    5: "jupiter",
    6: "saturn",
    7: "uranus",
    8: "neptune",
    9: "pluto",
    10: "rahu",
    11: "ketu",
}

BODY_NAME_ALIASES: Mapping[str, str] = {
    "sun": "sun",
    "surya": "sun",
    "ravi": "sun",
    "0": "sun",
    "moon": "moon",
    "chandra": "moon",
    "soma": "moon",
    "1": "moon",
    "mercury": "mercury",
    "budha": "mercury",
    "2": "mercury",
    "venus": "venus",
    "shukra": "venus",
    "3": "venus",
    "mars": "mars",
    "mangala": "mars",
    "kuja": "mars",
    "mars_center": "mars",
    "499": "mars",
    "4": "mars",
    "jupiter": "jupiter",
    "guru": "jupiter",
    "brihaspati": "jupiter",
    "jupiter_center": "jupiter",
    "599": "jupiter",
    "5": "jupiter",
    "saturn": "saturn",
    "shani": "saturn",
    "saturn_center": "saturn",
    "699": "saturn",
    "6": "saturn",
    "uranus": "uranus",
    "aruna": "uranus",
    "7": "uranus",
    "neptune": "neptune",
    "varuna": "neptune",
    "8": "neptune",
    "pluto": "pluto",
    "yama": "pluto",
    "9": "pluto",
    "rahu": "rahu",
    "mean_node": "rahu",
    "true_node": "rahu",
    "true_rahu": "rahu",
    "osculating_node": "rahu",
    "north_node": "rahu",
    "10": "rahu",
    "ketu": "ketu",
    "true_ketu": "ketu",
    "south_node": "ketu",
    "11": "ketu",
}

VEDIC_NINE_GRAHAS: tuple[str, ...] = (
    "sun",
    "moon",
    "mars",
    "mercury",
    "jupiter",
    "venus",
    "saturn",
    "rahu",
    "ketu",
)


def _resolve_body_name(body: str | int) -> str:
    if isinstance(body, int) and not isinstance(body, bool):
        if body in BODY_CODE_MAP:
            return BODY_CODE_MAP[body]
        raise EphemerisError(
            f"unsupported integer body code {body!r}; expected 0..11"
        )
    key = str(body).strip().lower().replace(" ", "_")
    if key in BODY_NAME_ALIASES:
        return BODY_NAME_ALIASES[key]
    raise EphemerisError(f"unsupported astronomical body {body!r}")


def _planet_physical_center_offset_deg(
    *,
    body_key: str,
    jd_tt: float,
    planet_lon_deg: float,
    dist_au: float,
) -> tuple[float, float]:
    """Compute physical disk-centre (NAIF 499/599/699) minus system-barycentre (NAIF 4/5/6) offset in degrees.

    Models the centre-of-mass recoil caused by the Galilean moons (Io, Europa,
    Ganymede, Callisto) for Jupiter (NAIF 599), Titan/Rhea/Iapetus for Saturn
    (NAIF 699), and Phobos/Deimos for Mars (NAIF 499).
    """
    d_j2000 = float(jd_tt) - J2000_JD
    dist_km = max(float(dist_au) * AU_KM, 1.0e5)
    p_rad = math.radians(float(planet_lon_deg))

    if body_key == "jupiter":
        # Galilean satellites (mu_i * a_i in km, L0_deg, n_deg_per_day, inc_deg)
        # Io: 19.837 km, Europa: 16.964 km, Ganymede: 83.546 km, Callisto: 106.693 km
        sats = (
            (19.837, 106.077, 203.48895579, 0.05),
            (16.964, 175.731, 101.37472473, 0.47),
            (83.546, 120.558, 50.31760920, 0.20),
            (106.693, 84.444, 21.57107117, 0.20),
        )
        eq_inc_rad = math.radians(3.13)
    elif body_key == "saturn":
        # Titan: mu*a = 289.09 km, Rhea: 2.14 km, Iapetus: 11.33 km
        sats = (
            (289.090, 15.485, 22.57697680, 0.35),
            (2.140, 290.120, 79.69004780, 0.35),
            (11.330, 76.230, 4.53795720, 15.47),
        )
        eq_inc_rad = math.radians(26.73)
    elif body_key == "mars":
        # Phobos: mu*a = 0.000155 km
        sats = ((0.000155, 92.470, 1128.8445850, 1.09),)
        eq_inc_rad = math.radians(25.19)
    else:
        return 0.0, 0.0

    dx_km = 0.0
    dy_km = 0.0
    dz_km = 0.0
    for recoil_km, l0_deg, rate_deg_day, sat_inc_deg in sats:
        lam_rad = math.radians((l0_deg + rate_deg_day * d_j2000) % 360.0)
        inc_rad = eq_inc_rad + math.radians(sat_inc_deg)
        # Planet physical centre is opposite to satellite displacement (-mu * r_sat)
        dx_km -= recoil_km * math.cos(lam_rad)
        dy_km -= recoil_km * math.sin(lam_rad) * math.cos(inc_rad)
        dz_km -= recoil_km * math.sin(lam_rad) * math.sin(inc_rad)

    # Project transverse displacement onto the geocentric line of sight
    transverse_lon_km = -dx_km * math.sin(p_rad) + dy_km * math.cos(p_rad)
    dlon_deg = math.degrees(transverse_lon_km / dist_km)
    dlat_deg = math.degrees(dz_km / dist_km)
    return float(dlon_deg), float(dlat_deg)


@dataclass(frozen=True)
class PlanetCoordinateResult:
    """Computed ecliptic coordinates, speed, retrograde status, and SHA-256 receipt.

    Supports both named attribute access and 6-tuple unpacking:
    ``(longitude_deg, latitude_deg, distance_au, longitude_speed_deg_per_day, is_retrograde, receipt_sha256)``.
    """

    longitude_deg: float
    latitude_deg: float
    distance_au: float
    longitude_speed_deg_per_day: float
    is_retrograde: bool
    receipt_sha256: str
    body: str = "sun"
    latitude_speed_deg_per_day: float = 0.0
    distance_speed_au_per_day: float = 0.0

    @property
    def speed_deg_per_day(self) -> float:
        return self.longitude_speed_deg_per_day

    @property
    def retrograde(self) -> bool:
        return self.is_retrograde

    def as_tuple(self) -> tuple[float, float, float, float, bool, str]:
        return (
            self.longitude_deg,
            self.latitude_deg,
            self.distance_au,
            self.longitude_speed_deg_per_day,
            self.is_retrograde,
            self.receipt_sha256,
        )

    def __iter__(self) -> Iterator[Any]:
        return iter(self.as_tuple())

    def __len__(self) -> int:
        return 6

    def __getitem__(self, index: int) -> Any:
        return self.as_tuple()[index]

    def to_dict(self) -> dict[str, Any]:
        return {
            "body": self.body,
            "longitude_deg": self.longitude_deg,
            "latitude_deg": self.latitude_deg,
            "distance_au": self.distance_au,
            "longitude_speed_deg_per_day": self.longitude_speed_deg_per_day,
            "latitude_speed_deg_per_day": self.latitude_speed_deg_per_day,
            "distance_speed_au_per_day": self.distance_speed_au_per_day,
            "is_retrograde": self.is_retrograde,
            "receipt_sha256": self.receipt_sha256,
        }


NAKSHATRA_ARC: float = 360.0 / 27.0

NAKSHATRAS_27: tuple[tuple[str, str], ...] = (
    ("Ashwini", "Ketu"),
    ("Bharani", "Venus"),
    ("Krittika", "Sun"),
    ("Rohini", "Moon"),
    ("Mrigashira", "Mars"),
    ("Ardra", "Rahu"),
    ("Punarvasu", "Jupiter"),
    ("Pushya", "Saturn"),
    ("Ashlesha", "Mercury"),
    ("Magha", "Ketu"),
    ("Purva Phalguni", "Venus"),
    ("Uttara Phalguni", "Sun"),
    ("Hasta", "Moon"),
    ("Chitra", "Mars"),
    ("Swati", "Rahu"),
    ("Vishakha", "Jupiter"),
    ("Anuradha", "Saturn"),
    ("Jyeshtha", "Mercury"),
    ("Mula", "Ketu"),
    ("Purva Ashadha", "Venus"),
    ("Uttara Ashadha", "Sun"),
    ("Shravana", "Moon"),
    ("Dhanishta", "Mars"),
    ("Shatabhisha", "Rahu"),
    ("Purva Bhadrapada", "Jupiter"),
    ("Uttara Bhadrapada", "Saturn"),
    ("Revati", "Mercury"),
)

SIGNS_12: tuple[str, ...] = (
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
)


@dataclass(frozen=True)
class GeoCoords:
    """Observer geographic coordinates."""

    latitude: float = 0.0
    longitude: float = 0.0
    altitude_m: float = 0.0


@dataclass(frozen=True)
class NakshatraInfo:
    """Complete Nakshatra coordinate, pada, and arc interval mapping."""

    index: int
    number: int
    name: str
    lord: str
    pada: int
    degrees_in_nakshatra: float
    start_longitude: float
    end_longitude: float


@dataclass(frozen=True)
class PlanetPosition:
    """Standardized planetary coordinate matching downstream IEphemerisProvider."""

    name: str
    longitude: float
    sign: str
    sign_num: int
    degree_in_sign: float
    retrograde: bool
    speed: float
    nakshatra: NakshatraInfo


def nakshatra_from_longitude(longitude: float) -> NakshatraInfo:
    """Map a sidereal longitude to its nakshatra, lord, and pada."""
    lon = longitude % 360.0
    idx = int(lon / NAKSHATRA_ARC) % 27
    pos_in = lon - idx * NAKSHATRA_ARC
    pada = min(4, int(pos_in / (NAKSHATRA_ARC / 4.0)) + 1)
    name, lord = NAKSHATRAS_27[idx]
    return NakshatraInfo(
        index=idx,
        number=idx + 1,
        name=name,
        lord=lord,
        pada=pada,
        degrees_in_nakshatra=pos_in,
        start_longitude=idx * NAKSHATRA_ARC,
        end_longitude=(idx + 1) * NAKSHATRA_ARC,
    )


def sign_from_longitude(longitude: float) -> tuple[int, str, float]:
    """Return (sign_num 0..11, sign_name, degree_in_sign) for a celestial longitude."""
    lon = longitude % 360.0
    sign_num = int(lon / 30.0) % 12
    return sign_num, SIGNS_12[sign_num], lon - sign_num * 30.0


@dataclass(frozen=True)
class HouseSystemResult:
    """Computed 12 house cusps, Ascendant, MC, Vertex, and SHA-256 receipt."""

    system: str
    cusps_deg: tuple[float, ...]
    ascendant_deg: float
    mc_deg: float
    vertex_deg: float
    receipt_sha256: str

    @property
    def midheaven_deg(self) -> float:
        return self.mc_deg

    def to_dict(self) -> dict[str, Any]:
        return {
            "system": self.system,
            "cusps_deg": list(self.cusps_deg),
            "ascendant_deg": self.ascendant_deg,
            "mc_deg": self.mc_deg,
            "vertex_deg": self.vertex_deg,
            "receipt_sha256": self.receipt_sha256,
        }


@dataclass(frozen=True)
class CompleteKundaliBundle:
    """Unified deterministic Kundali analysis and visualization bundle with master SHA-256 receipt."""

    jd_ut: float
    latitude_deg: float
    longitude_deg: float
    ayanamsa_system: str
    ayanamsa_deg: float
    positions: Mapping[str, PlanetCoordinateResult]
    houses: HouseSystemResult
    vedic_analysis: VedicChartAnalysis
    kp_sublords: Mapping[str, KpPositionLords]
    classical_yogas: ClassicalYogaReport
    jaimini_karakamsa: KarakamsaAnalysis
    jaimini_ayurdaya: JaiminiAyurdayaResult
    bhrigu_bindu: BhriguBinduReport
    khara_points: KharaPointsReport
    boundary_margins: Mapping[str, BoundarySensitivityEnvelope]
    ai_fact_sheet: AIFactSheet
    north_indian_svg: SvgChartArtifact | None
    south_indian_svg: SvgChartArtifact | None
    bundle_receipt_sha256: str

    @property
    def receipt_sha256(self) -> str:
        return self.bundle_receipt_sha256


class EphemerisAdapter:
    """High-level drop-in ephemeris provider adapter and unified Kundali bundle facade.

    Defaults to ``kernels="compact"`` so all planetary, ayanamsa, house, and
    Vedic Kundali calculations run 100% offline with zero external downloads.
    """

    SUN = SUN
    MOON = MOON
    MERCURY = MERCURY
    VENUS = VENUS
    MARS = MARS
    JUPITER = JUPITER
    SATURN = SATURN
    URANUS = URANUS
    NEPTUNE = NEPTUNE
    PLUTO = PLUTO
    RAHU = RAHU
    MEAN_NODE = MEAN_NODE
    KETU = KETU
    SOUTH_NODE = SOUTH_NODE

    def __init__(
        self,
        kernels: str | Path | Mapping[str, str | Path] = "compact",
        *,
        eop: str | EarthOrientation | Callable[[Any], Any] | None = "auto",
        cache_dir: str | Path | None = None,
    ) -> None:
        if isinstance(kernels, Path):
            kernel_arg: str | Mapping[str, str | Path] = {"DE440": kernels}
        elif isinstance(kernels, str) and kernels == "compact":
            kernel_arg = "extended"
        elif isinstance(kernels, str) and kernels not in {"compact", "extended", "compact-extended", "auto"}:
            candidate = Path(kernels)
            if candidate.suffix.lower() == ".bsp" or candidate.is_file():
                kernel_arg = {"DE440": candidate}
            else:
                kernel_arg = kernels
        else:
            kernel_arg = kernels

        self._kernels_spec = kernels
        self._engine = Engine.load(kernels=kernel_arg, eop=eop, cache_dir=cache_dir)
        self._ayanamsa_mode: str = "lahiri"
        self._topo_coords: tuple[float, float, float] | None = None

    @property
    def engine(self) -> Engine:
        return self._engine

    def close(self) -> None:
        self._engine.close()

    def __enter__(self) -> "EphemerisAdapter":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def set_ayanamsa(self, mode: str | int = "lahiri") -> None:
        """Set active ayanamsa mode for sidereal calculations."""
        self._ayanamsa_mode = str(mode or "lahiri").strip().lower().replace("-", "_")

    def set_topo(self, longitude: float, latitude: float, altitude_m: float = 0.0) -> None:
        """Set topocentric observer coordinates."""
        self._topo_coords = (float(longitude), float(latitude), float(altitude_m))

    def clear_topo(self) -> None:
        """Clear topocentric observer coordinates (reset to geocentric)."""
        self._topo_coords = None

    def get_planet_positions(
        self,
        dt: datetime,
        location: GeoCoords | None = None,
        planets: Sequence[str] | None = None,
    ) -> dict[str, PlanetPosition]:
        """Sidereal positions at UTC datetime dt matching IEphemerisProvider."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        if location is not None:
            self.set_topo(location.longitude, location.latitude, getattr(location, "altitude_m", 0.0))
        hour_ut = (
            float(dt.hour)
            + float(dt.minute) / 60.0
            + (float(dt.second) + float(dt.microsecond) / 1_000_000.0) / 3600.0
        )
        jd = self.julday(dt.year, dt.month, dt.day, hour_ut)
        candidates = list(planets) if planets is not None else list(VEDIC_NINE_GRAHAS)
        result: dict[str, PlanetPosition] = {}
        for p in candidates:
            resolved_key = _resolve_body_name(p)
            canonical_name = resolved_key.capitalize() if resolved_key != "true_node" else "True Node"
            coord = self.calc_ut(jd, resolved_key, sidereal=True, ayanamsa=self._ayanamsa_mode)
            lon = coord.longitude_deg % 360.0
            sign_num, sign_name, deg_in_sign = sign_from_longitude(lon)
            nak = nakshatra_from_longitude(lon)
            result[canonical_name] = PlanetPosition(
                name=canonical_name,
                longitude=lon,
                sign=sign_name,
                sign_num=sign_num,
                degree_in_sign=deg_in_sign,
                retrograde=coord.is_retrograde,
                speed=coord.longitude_speed_deg_per_day,
                nakshatra=nak,
            )
        return result

    @staticmethod
    def julday(
        year: int,
        month: int,
        day: int,
        hour_ut: float = 0.0,
    ) -> float:
        """Convert proleptic Gregorian calendar date and decimal UT hour to Julian Date."""
        if not math.isfinite(hour_ut):
            raise EphemerisError("hour_ut must be finite")
        try:
            djm0, djm = erfa.cal2jd(int(year), int(month), int(day))
        except (ValueError, erfa.ErfaError) as error:
            raise EphemerisError(f"invalid calendar date ({year}, {month}, {day})") from error
        return float(djm0 + djm) + float(hour_ut) / 24.0

    @staticmethod
    def revjul(jd_ut: float) -> tuple[int, int, int, float]:
        """Convert Julian Date UT back to ``(year, month, day, hour_ut)``."""
        jd_val = float(jd_ut)
        if not math.isfinite(jd_val):
            raise EphemerisError("jd_ut must be finite")
        try:
            year, month, day, fd = erfa.jd2cal(J2000_JD, jd_val - J2000_JD)
        except (ValueError, erfa.ErfaError) as error:
            raise EphemerisError(f"invalid Julian Date {jd_ut!r}") from error
        hour_ut = float(fd) * 24.0
        # Guard against floating-point rounding near 24.0h
        if hour_ut >= 24.0:
            hour_ut = 0.0
        elif hour_ut < 0.0:
            hour_ut = 0.0
        return int(year), int(month), int(day), hour_ut

    def _coerce_jd_ut(self, instant_or_jd_ut: float | int | datetime | UtcCalendarInstant) -> float:
        if isinstance(instant_or_jd_ut, (int, float)) and not isinstance(instant_or_jd_ut, bool):
            jd_val = float(instant_or_jd_ut)
            if not math.isfinite(jd_val):
                raise EphemerisError("jd_ut must be finite")
            return jd_val
        if isinstance(instant_or_jd_ut, UtcCalendarInstant):
            hour = (
                float(instant_or_jd_ut.hour)
                + float(instant_or_jd_ut.minute) / 60.0
                + float(instant_or_jd_ut.second) / 3600.0
            )
            return self.julday(
                instant_or_jd_ut.year,
                instant_or_jd_ut.month,
                instant_or_jd_ut.day,
                hour,
            )
        if isinstance(instant_or_jd_ut, datetime):
            dt = (
                instant_or_jd_ut.astimezone(timezone.utc)
                if instant_or_jd_ut.tzinfo is not None and instant_or_jd_ut.utcoffset() is not None
                else instant_or_jd_ut.replace(tzinfo=timezone.utc)
            )
            hour = (
                float(dt.hour)
                + float(dt.minute) / 60.0
                + (float(dt.second) + float(dt.microsecond) / 1_000_000.0) / 3600.0
            )
            return self.julday(dt.year, dt.month, dt.day, hour)
        raise EphemerisError(
            f"expected float JD, datetime, or UtcCalendarInstant; got {type(instant_or_jd_ut).__name__}"
        )

    def _jd_ut_to_jd_tt(self, jd_ut: float) -> float:
        year, month, day, hour_ut = self.revjul(jd_ut)
        if 1960 <= year <= 2026:
            try:
                civil = date(year, month, day)
                if date(1960, 1, 1) <= civil <= date(2026, 12, 31):
                    tai_minus_utc = float(erfa.dat(year, month, day, hour_ut / 24.0))
                    return float(jd_ut) + (tai_minus_utc + 32.184) / SECONDS_PER_DAY
            except (ValueError, erfa.ErfaError, erfa.ErfaWarning):
                pass
        decimal_year = float(year) + (float(month) - 0.5) / 12.0 + (float(day) - 1.0) / 365.2425
        if -1999.0 <= decimal_year <= 3000.0:
            delta_t_seconds = float(estimate_delta_t(decimal_year).seconds)
        else:
            u_cent = (decimal_year - 1820.0) / 100.0
            delta_t_seconds = float(-20.0 + 32.0 * u_cent * u_cent)
        return float(jd_ut) + delta_t_seconds / SECONDS_PER_DAY

    def get_ayanamsa_ut(self, jd_ut: float, mode: str = "lahiri") -> float:
        """Return the exact sidereal ayanamsa in degrees at ``jd_ut``."""
        jd_val = self._coerce_jd_ut(jd_ut)
        jd_tt = self._jd_ut_to_jd_tt(jd_val)
        tt = (J2000_JD, jd_tt - J2000_JD)
        convention = str(mode or "lahiri").strip().lower()
        anchor = stellar_anchor_for_ayanamsa(convention)
        anchor_lon = (
            None
            if anchor is None
            else stellar_tropical_longitude_degrees(anchor, tt=tt)
        )
        return float(
            ayanamsa_degrees(
                jd_tt,
                convention,
                anchor_tropical_longitude_deg=anchor_lon,
            )
        )

    @staticmethod
    def _numeric_body(body: str | int) -> str:
        """Resolve the numeric-TT surface without inheriting legacy node IDs."""
        if isinstance(body, int) and not isinstance(body, bool):
            if body == 10:
                return "mean_node"
            if body == 11:
                return "true_node"
            return _resolve_body_name(body)
        key = str(body).strip().lower().replace(" ", "_")
        aliases = {
            "rahu": "mean_node",
            "mean_lunar_node": "mean_node",
            "north_node": "mean_node",
            "ketu": "south_node",
            "south_lunar_node": "south_node",
            "osculating_node": "true_node",
        }
        key = aliases.get(key, key)
        if key in {"mean_node", "true_node", "south_node"}:
            return key
        return _resolve_body_name(key)

    @staticmethod
    def _calendar_year(jd: float) -> int:
        return int(calendar_date(
            jd, calendar=CalendarSystem.PROLEPTIC_GREGORIAN
        )[0])

    def get_ayanamsa_tt(
        self,
        jd_tt: float,
        mode: str = "lahiri",
        *,
        anchor_tropical_longitude_deg: float | None = None,
        true: bool = False,
    ) -> float:
        """Return a named ayanamsa at an explicit TT Julian date."""
        value = float(jd_tt)
        if not math.isfinite(value):
            raise EphemerisError("jd_tt must be finite")
        convention = str(mode or "lahiri").strip().lower().replace("-", "_")
        anchor_lon = (
            None
            if anchor_tropical_longitude_deg is None
            else float(anchor_tropical_longitude_deg)
        )
        if anchor_lon is not None and not math.isfinite(anchor_lon):
            raise EphemerisError("anchor_tropical_longitude_deg must be finite")
        try:
            return float(ayanamsa_degrees(
                value,
                convention,
                anchor_tropical_longitude_deg=anchor_lon,
                true=bool(true),
            ))
        except Exception as error:
            raise EphemerisError(str(error)) from error

    def _coordinate_at_tt(
        self,
        jd_tt: float,
        body: str | int,
        *,
        jd_tdb: float | None,
        sidereal: bool,
        ayanamsa: str,
        nonut: bool,
        anchor_tropical_longitude_deg: float | None,
    ) -> tuple[tuple[float, float, float], Mapping[str, Any]]:
        """Evaluate one apparent geocentric coordinate through the JPL pipeline."""
        tt_value = float(jd_tt)
        if not math.isfinite(tt_value):
            raise EphemerisError("jd_tt must be finite")
        year = self._calendar_year(tt_value)
        modern = 1600 <= year <= 2400
        if not modern and not nonut:
            raise EphemerisError(
                "true-equinox output is supported only for TT years 1600..2400; "
                "request FLG_NONUT for the long-term mean ecliptic"
            )
        if jd_tdb is None:
            if not modern:
                raise EphemerisError("jd_tdb is required outside TT years 1600..2400")
            tt = (J2000_JD, tt_value - J2000_JD)
            offset = float(erfa.dtdb(*tt, 0.0, 0.0, 0.0, 0.0))
            tdb_value = float(sum(erfa.tttdb(*tt, offset)))
        else:
            tdb_value = float(jd_tdb)
            if not math.isfinite(tdb_value):
                raise EphemerisError("jd_tdb must be finite")
        tt = (J2000_JD, tt_value - J2000_JD)
        tdb = (J2000_JD, tdb_value - J2000_JD)
        times = TimeScaleState(utc=tt, tt=tt, tdb=tdb)
        body_key = self._numeric_body(body)
        provider = self._engine._provider
        artifact = provider._kernel_registry.artifact_for_tdb_jd(tdb_value)
        frame = np.asarray(mean_ecliptic_matrix(tt_value), dtype=np.float64)

        if body_key in {"mean_node", "south_node"}:
            if not modern:
                raise EphemerisError("mean lunar node is supported only for TT years 1600..2400")
            longitude = mean_lunar_node_longitude_degrees(tt_value)
            if body_key == "south_node":
                longitude = normalize_degrees(longitude + 180.0)
            latitude = 0.0
            distance_au = 0.00256955529
            position_type = "mean_lunar_node_axis"
        elif body_key == "true_node":
            state = provider.geocentric_state_at_tdb(body="moon", tdb=tdb, kernel_year=year)
            position = frame @ np.asarray(state.position_km, dtype=np.float64)
            velocity = frame @ np.asarray(state.velocity_km_per_day, dtype=np.float64)
            longitude = osculating_lunar_node_longitude_degrees(position, velocity)
            latitude = 0.0
            distance_au = float(np.linalg.norm(position) / AU_KM)
            position_type = "osculating_lunar_node_axis"
        else:
            earth_state = provider.barycentric_state_at_tdb(
                body="earth", tdb=tdb, kernel_year=year
            )
            sun_cache: dict[float, Any] = {}

            def sun_at(jd: float) -> Any:
                if jd not in sun_cache:
                    sun_cache[jd] = provider.barycentric_state_at_tdb(
                        body="sun", tdb=(J2000_JD, jd - J2000_JD), kernel_year=year
                    )
                return sun_cache[jd]

            apparent, _ = provider._apparent_state(
                body=body_key,
                instant_utc=None,
                kernel_year=year,
                observer=None,
                times=times,
                apply_deflection=(body_key != "sun"),
                apply_aberration=True,
                precomputed_earth_state=earth_state,
                precomputed_sun_func=sun_at,
            )
            transformed = frame @ np.asarray(apparent.apparent_vector_km, dtype=np.float64)
            longitude, latitude, radius_km = provider._spherical(transformed)
            distance_au = float(radius_km / AU_KM)
            position_type = "apparent_geocentric"

        if not nonut:
            longitude = normalize_degrees(
                longitude + math.degrees(float(erfa.nut06a(*tt)[0]))
            )
        ayan_deg = (
            self.get_ayanamsa_tt(
                tt_value,
                ayanamsa,
                anchor_tropical_longitude_deg=anchor_tropical_longitude_deg,
                true=not nonut,
            )
            if sidereal
            else 0.0
        )
        if sidereal:
            longitude = normalize_degrees(longitude - ayan_deg)
        values = (float(longitude), float(latitude), float(distance_au))
        receipt = {
            "schema": "ephemeris-oss.adapter.calc-tt.v1",
            "version": __version__,
            "jd_tt": tt_value,
            "jd_tdb": tdb_value,
            "body": body_key,
            "position_type": position_type,
            "sidereal": sidereal,
            "ayanamsa": ayanamsa if sidereal else None,
            "ayanamsa_deg": ayan_deg,
            "ayanamsa_true": bool(sidereal and not nonut),
            "anchor_tropical_longitude_deg": anchor_tropical_longitude_deg,
            "nonut": nonut,
            "kernel_identifier": artifact.identifier,
            "kernel_sha256": artifact.sha256.lower(),
            "values": values,
        }
        return values, receipt

    def calc_tt(
        self,
        jd_tt: float,
        body: str | int,
        *,
        jd_tdb: float | None = None,
        sidereal: bool = False,
        ayanamsa: str = "lahiri",
        nonut: bool = False,
        derivative_step_days: float = 0.001,
        anchor_tropical_longitude_deg: float | None = None,
        anchor_tropical_speed_deg_per_day: float | None = None,
        include_derivatives: bool = True,
    ) -> PlanetCoordinateResult:
        """Calculate apparent geocentric coordinates from explicit TT/TDB."""
        if jd_tdb is not None:
            try:
                validate_tt_tdb(jd_tt, jd_tdb)
            except Exception as error:
                raise EphemerisError(str(error)) from error
        step = float(derivative_step_days)
        if not math.isfinite(step) or step <= 0.0:
            raise EphemerisError("derivative_step_days must be finite and positive")
        anchor_speed = None
        if anchor_tropical_speed_deg_per_day is not None:
            anchor_speed = float(anchor_tropical_speed_deg_per_day)
            if not math.isfinite(anchor_speed):
                raise EphemerisError("anchor_tropical_speed_deg_per_day must be finite")
        if include_derivatives and anchor_tropical_longitude_deg is not None and anchor_speed is None:
            raise EphemerisError(
                "anchor_tropical_speed_deg_per_day is required for stellar-anchor derivatives"
            )
        center, payload = self._coordinate_at_tt(
            jd_tt, body, jd_tdb=jd_tdb, sidereal=sidereal,
            ayanamsa=ayanamsa, nonut=nonut,
            anchor_tropical_longitude_deg=anchor_tropical_longitude_deg,
        )
        longitude_speed = latitude_speed = distance_speed = 0.0
        if include_derivatives:
            tdb_plus = None if jd_tdb is None else float(jd_tdb) + step
            tdb_minus = None if jd_tdb is None else float(jd_tdb) - step
            before, _ = self._coordinate_at_tt(
                float(jd_tt) - step, body, jd_tdb=tdb_minus, sidereal=sidereal,
                ayanamsa=ayanamsa, nonut=nonut,
                anchor_tropical_longitude_deg=(
                    None if anchor_tropical_longitude_deg is None
                    else float(anchor_tropical_longitude_deg) - step * float(anchor_speed)
                ),
            )
            after, _ = self._coordinate_at_tt(
                float(jd_tt) + step, body, jd_tdb=tdb_plus, sidereal=sidereal,
                ayanamsa=ayanamsa, nonut=nonut,
                anchor_tropical_longitude_deg=(
                    None if anchor_tropical_longitude_deg is None
                    else float(anchor_tropical_longitude_deg) + step * float(anchor_speed)
                ),
            )
            longitude_speed = ((after[0] - before[0] + 180.0) % 360.0 - 180.0) / (2.0 * step)
            latitude_speed = (after[1] - before[1]) / (2.0 * step)
            distance_speed = (after[2] - before[2]) / (2.0 * step)
        payload = {
            **payload,
            "derivative_step_days": step if include_derivatives else None,
            "longitude_speed_deg_per_day": longitude_speed,
            "latitude_speed_deg_per_day": latitude_speed,
            "distance_speed_au_per_day": distance_speed,
            "anchor_tropical_speed_deg_per_day": anchor_speed,
        }
        body_key = self._numeric_body(body)
        return PlanetCoordinateResult(
            longitude_deg=center[0], latitude_deg=center[1], distance_au=center[2],
            longitude_speed_deg_per_day=longitude_speed,
            latitude_speed_deg_per_day=latitude_speed,
            distance_speed_au_per_day=distance_speed,
            is_retrograde=longitude_speed < 0.0,
            receipt_sha256=canonical_hash(payload), body=body_key,
        )

    def calc_ut(
        self,
        jd_ut: float,
        body: str | int,
        *,
        sidereal: bool = True,
        ayanamsa: str = "lahiri",
        true_node: bool = False,
        physical_center: bool = False,
    ) -> PlanetCoordinateResult:
        """Compute apparent geocentric coordinates, speed, retrograde flag, and receipt for ``body``."""
        jd_val = self._coerce_jd_ut(jd_ut)
        raw_body_str = (
            str(body).strip().lower().replace(" ", "_")
            if not (isinstance(body, int) and not isinstance(body, bool))
            else ""
        )
        use_true_node = bool(true_node) or (
            raw_body_str in {"true_node", "osculating_node", "true_rahu", "true_ketu"}
        )
        use_physical_center = bool(physical_center) or (
            raw_body_str in {"mars_center", "jupiter_center", "saturn_center", "499", "599", "699"}
        )
        body_key = _resolve_body_name(body)
        jd_tt = self._jd_ut_to_jd_tt(jd_val)
        tt = (J2000_JD, jd_tt - J2000_JD)
        year = int(erfa.jd2cal(*tt)[0])
        offset = float(erfa.dtdb(*tt, 0.0, 0.0, 0.0, 0.0))
        tdb = tuple(float(v) for v in erfa.tttdb(*tt, offset))
        times = TimeScaleState(utc=(J2000_JD, jd_val - J2000_JD), tt=tt, tdb=tdb)

        provider = self._engine._provider
        ayan_deg = self.get_ayanamsa_ut(jd_val, mode=ayanamsa) if sidereal else 0.0
        try:
            artifact = provider._kernel_registry.artifact_for_tdb_jd(times.tdb_jd)
        except AstronomyDataUnavailable:
            return self._calc_ut_historical_analytical(
                jd_val=jd_val,
                jd_tt=jd_tt,
                body_key=body_key,
                sidereal=sidereal,
                ayanamsa=ayanamsa,
                ayan_deg=ayan_deg,
                true_node=use_true_node,
                physical_center=use_physical_center,
            )

        if body_key in ("rahu", "ketu"):
            if use_true_node:
                frame = np.asarray(mean_ecliptic_matrix(jd_tt), dtype=np.float64)
                state = provider.geocentric_state_at_tdb(body="moon", tdb=tdb, kernel_year=year)
                pos = frame @ np.asarray(state.position_km, dtype=np.float64)
                vel = frame @ np.asarray(state.velocity_km_per_day, dtype=np.float64)
                tropical_node = osculating_lunar_node_longitude_degrees(pos, vel)
                step_d = 0.001
                node_minus: float | None = None
                node_plus: float | None = None
                try:
                    state_minus = provider.geocentric_state_at_tdb(
                        body="moon", tdb=(tdb[0], tdb[1] - step_d), kernel_year=year
                    )
                    node_minus = osculating_lunar_node_longitude_degrees(
                        frame @ np.asarray(state_minus.position_km, dtype=np.float64),
                        frame @ np.asarray(state_minus.velocity_km_per_day, dtype=np.float64),
                    )
                except AstronomyDataUnavailable:
                    node_minus = None
                try:
                    state_plus = provider.geocentric_state_at_tdb(
                        body="moon", tdb=(tdb[0], tdb[1] + step_d), kernel_year=year
                    )
                    node_plus = osculating_lunar_node_longitude_degrees(
                        frame @ np.asarray(state_plus.position_km, dtype=np.float64),
                        frame @ np.asarray(state_plus.velocity_km_per_day, dtype=np.float64),
                    )
                except AstronomyDataUnavailable:
                    node_plus = None
                if node_minus is not None and node_plus is not None:
                    speed_deg = ((node_plus - node_minus + 180.0) % 360.0 - 180.0) / (2.0 * step_d)
                elif node_plus is not None:
                    speed_deg = ((node_plus - tropical_node + 180.0) % 360.0 - 180.0) / step_d
                elif node_minus is not None:
                    speed_deg = ((tropical_node - node_minus + 180.0) % 360.0 - 180.0) / step_d
                else:
                    speed_deg = -0.05295376
                dist_au = float(np.linalg.norm(pos) / AU_KM)
                is_retro = bool(speed_deg < 0.0)
            else:
                try:
                    tropical_node = mean_lunar_node_longitude_degrees(jd_tt)
                except AstronomyDataUnavailable:
                    t_cent = (jd_tt - J2000_JD) / 36525.0
                    tropical_node = normalize_degrees(
                        125.0445479
                        - 1934.1362891 * t_cent
                        + 0.0020754 * t_cent * t_cent
                        + (t_cent ** 3) / 467441.0
                        - (t_cent ** 4) / 60616000.0
                    )
                dist_au = 0.00256955529
                speed_deg = -0.05295376
                is_retro = True
            if body_key == "ketu":
                tropical_node = (tropical_node + 180.0) % 360.0
            lon_deg = (
                (tropical_node - ayan_deg) % 360.0
                if sidereal
                else normalize_degrees(tropical_node)
            )
            lat_deg = 0.0
        else:
            try:
                earth_state = provider.barycentric_state_at_tdb(
                    body="earth", tdb=tdb, kernel_year=year
                )
                sun_cache: dict[float, Any] = {}

                def _sun_at(jd: float) -> Any:
                    if jd not in sun_cache:
                        sun_cache[jd] = provider.barycentric_state_at_tdb(
                            body="sun", tdb=(J2000_JD, jd - J2000_JD), kernel_year=year
                        )
                    return sun_cache[jd]

                apparent, _ = provider._apparent_state(
                    body=body_key,
                    instant_utc=None,
                    kernel_year=year,
                    observer=None,
                    times=times,
                    apply_deflection=(body_key != "sun"),
                    apply_aberration=True,
                    precomputed_earth_state=earth_state,
                    precomputed_sun_func=_sun_at,
                )
                icrf = np.asarray(apparent.apparent_vector_km, dtype=np.float64)
                tau_days = float(apparent.light_time_seconds) / SECONDS_PER_DAY
                target_emitted = provider.barycentric_state_at_tdb(
                    body=body_key,
                    tdb=(J2000_JD, times.tdb_jd - tau_days - J2000_JD),
                    kernel_year=year,
                )
            except (AstronomyDataUnavailable, KeyError, EphemerisError):
                return self._calc_ut_historical_analytical(
                    jd_val=jd_val,
                    jd_tt=jd_tt,
                    body_key=body_key,
                    sidereal=sidereal,
                    ayanamsa=ayanamsa,
                    ayan_deg=ayan_deg,
                    true_node=use_true_node,
                    physical_center=use_physical_center,
                )
            v_icrf = np.asarray(target_emitted.velocity_km_per_day, dtype=np.float64) - np.asarray(
                earth_state.velocity_km_per_day, dtype=np.float64
            )
            frame_matrix = np.asarray(erfa.ecm06(*tt), dtype=np.float64)
            transformed = frame_matrix @ icrf
            v_transformed = frame_matrix @ v_icrf
            tropical_lon, lat_deg, radius_km = provider._spherical(transformed)
            denom = float(transformed[0] * transformed[0] + transformed[1] * transformed[1])
            speed_deg = (
                math.degrees(
                    float(transformed[0] * v_transformed[1] - transformed[1] * v_transformed[0])
                    / denom
                )
                if denom > 1e-12
                else 0.0
            )
            is_retro = bool(speed_deg < 0.0) if body_key not in ("sun", "moon") else False
            dist_au = float(radius_km / AU_KM)
            if use_physical_center and body_key in ("mars", "jupiter", "saturn"):
                h_pc = 0.05
                dist_rate_au = (
                    float(np.dot(transformed, v_transformed)) / max(float(radius_km), 1e-12)
                ) / AU_KM
                dlon_center_deg, dlat_center_deg = _planet_physical_center_offset_deg(
                    body_key=body_key,
                    jd_tt=jd_tt,
                    planet_lon_deg=tropical_lon,
                    dist_au=dist_au,
                )
                dlon_plus, _ = _planet_physical_center_offset_deg(
                    body_key=body_key,
                    jd_tt=jd_tt + h_pc,
                    planet_lon_deg=(tropical_lon + speed_deg * h_pc) % 360.0,
                    dist_au=max(0.01, dist_au + dist_rate_au * h_pc),
                )
                dlon_minus, _ = _planet_physical_center_offset_deg(
                    body_key=body_key,
                    jd_tt=jd_tt - h_pc,
                    planet_lon_deg=(tropical_lon - speed_deg * h_pc) % 360.0,
                    dist_au=max(0.01, dist_au - dist_rate_au * h_pc),
                )
                tropical_lon = (tropical_lon + dlon_center_deg) % 360.0
                lat_deg = float(lat_deg + dlat_center_deg)
                speed_deg = float(speed_deg + (dlon_plus - dlon_minus) / (2.0 * h_pc))
                is_retro = bool(speed_deg < 0.0)
            if sidereal:
                lon_deg = (tropical_lon - ayan_deg) % 360.0
            else:
                nutation_deg = math.degrees(float(erfa.nut06a(*tt)[0]))
                lon_deg = (tropical_lon + nutation_deg) % 360.0

        receipt_payload: dict[str, Any] = {
            "schema": "ephemeris-oss.adapter.calc_ut.v1",
            "version": __version__,
            "jd_ut": round(jd_val, 9),
            "jd_tt": round(jd_tt, 9),
            "body": body_key,
            "sidereal": bool(sidereal),
            "ayanamsa": str(ayanamsa).lower() if sidereal else None,
            "ayanamsa_deg": round(ayan_deg, 9) if sidereal else 0.0,
            "kernel_identifier": artifact.identifier,
            "kernel_sha256": artifact.sha256.lower(),
            "longitude_deg": round(lon_deg, 9),
            "latitude_deg": round(lat_deg, 9),
            "distance_au": round(dist_au, 9),
            "longitude_speed_deg_per_day": round(speed_deg, 9),
            "is_retrograde": is_retro,
        }
        if use_physical_center:
            receipt_payload["physical_center"] = True
        return PlanetCoordinateResult(
            longitude_deg=float(lon_deg),
            latitude_deg=float(lat_deg),
            distance_au=float(dist_au),
            longitude_speed_deg_per_day=float(speed_deg),
            is_retrograde=is_retro,
            receipt_sha256=canonical_hash(receipt_payload),
            body=body_key,
        )

    def _calc_ut_historical_analytical(
        self,
        *,
        jd_val: float,
        jd_tt: float,
        body_key: str,
        sidereal: bool,
        ayanamsa: str,
        ayan_deg: float,
        true_node: bool = False,
        physical_center: bool = False,
    ) -> PlanetCoordinateResult:
        """Long-term Vondrak-2011 + Keplerian/Meeus/ELP historical analytical evaluator (3102 BCE to 3000 CE)."""

        def _eval_tropical(j_tt: float) -> tuple[float, float, float]:
            t_cent = (j_tt - J2000_JD) / 36525.0
            if body_key in ("rahu", "ketu", "true_node"):
                node = (
                    125.0445479
                    - 1934.1362891 * t_cent
                    + 0.0020754 * t_cent * t_cent
                    + (t_cent ** 3) / 467441.0
                    - (t_cent ** 4) / 60616000.0
                )
                if body_key == "true_node" or true_node:
                    d = 297.8501921 + 445267.1114034 * t_cent
                    m = 357.5291092 + 35999.0502909 * t_cent
                    mp = 134.9633964 + 477198.8675055 * t_cent
                    f = 93.2720950 + 483202.0175233 * t_cent
                    node += (
                        -1.4979 * math.sin(2.0 * (d - f) * _ANALYTICAL_DEG)
                        - 0.1500 * math.sin(m * _ANALYTICAL_DEG)
                        - 0.1226 * math.sin(2.0 * d * _ANALYTICAL_DEG)
                        + 0.1176 * math.sin(2.0 * f * _ANALYTICAL_DEG)
                        - 0.0801 * math.sin(2.0 * (mp - f) * _ANALYTICAL_DEG)
                    )
                if body_key == "ketu":
                    node += 180.0
                return normalize_degrees(node), 0.0, 0.00256955529
            if body_key == "moon":
                lp = 218.3164477 + 481267.88123421 * t_cent
                d = 297.8501921 + 445267.1114034 * t_cent
                m = 357.5291092 + 35999.0502909 * t_cent
                mp = 134.9633964 + 477198.8675055 * t_cent
                f = 93.2720950 + 483202.0175233 * t_cent
                lam = (
                    lp
                    + 6.288774 * math.sin(mp * _ANALYTICAL_DEG)
                    + 1.274027 * math.sin((2.0 * d - mp) * _ANALYTICAL_DEG)
                    + 0.658314 * math.sin(2.0 * d * _ANALYTICAL_DEG)
                    + 0.213618 * math.sin(2.0 * mp * _ANALYTICAL_DEG)
                    - 0.185116 * math.sin(m * _ANALYTICAL_DEG)
                    - 0.114332 * math.sin(2.0 * f * _ANALYTICAL_DEG)
                    + 0.058793 * math.sin((2.0 * d - 2.0 * mp) * _ANALYTICAL_DEG)
                    + 0.057066 * math.sin((2.0 * d - m - mp) * _ANALYTICAL_DEG)
                    + 0.053322 * math.sin((2.0 * d + mp) * _ANALYTICAL_DEG)
                    + 0.045758 * math.sin((2.0 * d - m) * _ANALYTICAL_DEG)
                )
                beta = (
                    5.128122 * math.sin(f * _ANALYTICAL_DEG)
                    + 0.280602 * math.sin((mp + f) * _ANALYTICAL_DEG)
                    + 0.277693 * math.sin((mp - f) * _ANALYTICAL_DEG)
                    + 0.173237 * math.sin((2.0 * d - f) * _ANALYTICAL_DEG)
                )
                r_km = (
                    385000.56
                    - 20905.355 * math.cos(mp * _ANALYTICAL_DEG)
                    - 3699.111 * math.cos((2.0 * d - mp) * _ANALYTICAL_DEG)
                    - 2955.968 * math.cos(2.0 * d * _ANALYTICAL_DEG)
                    - 569.925 * math.cos(2.0 * mp * _ANALYTICAL_DEG)
                )
                return normalize_degrees(lam), float(beta), float(r_km / AU_KM)

            ex, ey, ez = _analytical_heliocentric_xyz("Earth", t_cent)
            if body_key == "sun":
                gx, gy, gz = -ex, -ey, -ez
            else:
                cap_name = body_key.capitalize()
                if cap_name not in _ANALYTICAL_ELEMENTS:
                    raise EphemerisError(f"unsupported historical analytical body {body_key!r}")
                px, py, pz = _analytical_heliocentric_xyz(cap_name, t_cent)
                gx, gy, gz = px - ex, py - ey, pz - ez
            dist_au = math.sqrt(gx * gx + gy * gy + gz * gz)
            lam_j2000 = math.degrees(math.atan2(gy, gx)) % 360.0
            lat_deg = math.degrees(math.asin(max(-1.0, min(1.0, gz / max(dist_au, 1e-12)))))
            # Precess J2000 ecliptic longitude to tropical ecliptic of date via Vondrak-2011 Lahiri differential
            precession_shift = self.get_ayanamsa_ut(jd_val, mode="lahiri") - _ANALYTICAL_AYANAMSA_J2000
            trop_val = normalize_degrees(lam_j2000 + precession_shift)
            lat_val = float(lat_deg)
            dist_val = float(dist_au)
            if physical_center and body_key in ("mars", "jupiter", "saturn"):
                dlon_c, dlat_c = _planet_physical_center_offset_deg(
                    body_key=body_key,
                    jd_tt=j_tt,
                    planet_lon_deg=trop_val,
                    dist_au=dist_val,
                )
                trop_val = normalize_degrees(trop_val + dlon_c)
                lat_val = float(lat_val + dlat_c)
            return trop_val, lat_val, dist_val

        trop_lon, lat_deg, dist_au = _eval_tropical(jd_tt)
        step = 0.05
        trop_before, lat_before, dist_before = _eval_tropical(jd_tt - step)
        trop_after, lat_after, dist_after = _eval_tropical(jd_tt + step)
        speed_deg = ((trop_after - trop_before + 180.0) % 360.0 - 180.0) / (2.0 * step)
        lat_speed = (lat_after - lat_before) / (2.0 * step)
        dist_speed = (dist_after - dist_before) / (2.0 * step)
        if body_key in ("rahu", "ketu") and not true_node:
            speed_deg = -0.05295376
            is_retro = True
        elif body_key in ("sun", "moon"):
            is_retro = False
        else:
            is_retro = bool(speed_deg < 0.0)
        lon_deg = (trop_lon - ayan_deg) % 360.0 if sidereal else normalize_degrees(trop_lon)
        hist_kernel_id = "HISTORICAL-ANALYTICAL-VONDRAK2011"
        hist_sha = canonical_hash({"provider": hist_kernel_id, "version": __version__})
        receipt_payload: dict[str, Any] = {
            "schema": "ephemeris-oss.adapter.calc_ut.v1",
            "version": __version__,
            "jd_ut": round(jd_val, 9),
            "jd_tt": round(jd_tt, 9),
            "body": body_key,
            "sidereal": bool(sidereal),
            "ayanamsa": str(ayanamsa).lower() if sidereal else None,
            "ayanamsa_deg": round(ayan_deg, 9) if sidereal else 0.0,
            "kernel_identifier": hist_kernel_id,
            "kernel_sha256": hist_sha,
            "longitude_deg": round(lon_deg, 9),
            "latitude_deg": round(lat_deg, 9),
            "distance_au": round(dist_au, 9),
            "longitude_speed_deg_per_day": round(speed_deg, 9),
            "is_retrograde": is_retro,
        }
        if physical_center:
            receipt_payload["physical_center"] = True
        return PlanetCoordinateResult(
            longitude_deg=float(lon_deg),
            latitude_deg=float(lat_deg),
            distance_au=float(dist_au),
            longitude_speed_deg_per_day=float(speed_deg),
            latitude_speed_deg_per_day=float(lat_speed),
            distance_speed_au_per_day=float(dist_speed),
            is_retrograde=is_retro,
            receipt_sha256=canonical_hash(receipt_payload),
            body=body_key,
        )

    def houses_ut(
        self,
        jd_ut: float,
        latitude_deg: float,
        longitude_deg: float,
        *,
        system: str = "whole_sign",
        ayanamsa: str | None = "lahiri",
        tt_jd: float | None = None,
    ) -> HouseSystemResult:
        """Compute 12 house cusps, Ascendant, MC, Vertex, and SHA-256 receipt."""
        jd_val = self._coerce_jd_ut(jd_ut)
        lat = float(latitude_deg)
        lon = float(longitude_deg)
        if not math.isfinite(lat) or not -90.0 < lat < 90.0:
            raise EphemerisError("latitude_deg must be finite and strictly within (-90, 90)")
        if not math.isfinite(lon) or not -180.0 <= lon <= 180.0:
            raise EphemerisError("longitude_deg must be finite and within [-180, 180]")

        jd_tt = self._jd_ut_to_jd_tt(jd_val) if tt_jd is None else float(tt_jd)
        if not math.isfinite(jd_tt):
            raise EphemerisError("tt_jd must be finite")
        tt = (J2000_JD, jd_tt - J2000_JD)
        angles = house_angles(
            tt_jd=jd_tt,
            ut1_jd=jd_val,
            longitude_deg=lon,
            latitude_deg=lat,
        )

        # Compute tropical Vertex via co-latitude on the prime vertical
        if abs(lat) < 1e-6:
            tropical_vertex = normalize_degrees(angles.ascendant_deg + 180.0)
        else:
            co_lat = (90.0 - lat) if lat > 0.0 else (-90.0 - lat)
            co_lat = max(-89.9999, min(89.9999, co_lat))
            tropical_vertex, _ = ascendant_midheaven_from_sidereal(
                normalize_degrees(angles.local_apparent_sidereal_deg + 180.0),
                co_lat,
                angles.true_obliquity_deg,
            )

        use_sidereal = ayanamsa is not None and str(ayanamsa).strip().lower() not in {"", "none", "tropical"}
        if use_sidereal:
            ayan_name = str(ayanamsa).strip().lower()
            ayan_mean = (
                self.get_ayanamsa_ut(jd_val, mode=ayan_name)
                if tt_jd is None
                else self.get_ayanamsa_tt(jd_tt, mode=ayan_name)
            )
            dpsi, _ = erfa.nut06a(*tt)
            total_offset = ayan_mean + math.degrees(float(dpsi))
        else:
            ayan_name = "tropical"
            total_offset = 0.0

        asc_final = normalize_degrees(angles.ascendant_deg - total_offset)
        mc_final = normalize_degrees(angles.midheaven_deg - total_offset)
        vertex_final = normalize_degrees(tropical_vertex - total_offset)

        norm_sys = str(system or "whole_sign").strip().lower().replace("-", "_")
        try:
            if norm_sys in {"whole_sign", "whole", "w", "equal", "equal_house", "e"}:
                layout = house_layout(
                    norm_sys,
                    ascendant_deg=asc_final,
                    midheaven_deg=mc_final,
                )
                cusps_final = tuple(float(c) for c in layout.cusps_deg)
                canonical_sys = layout.system
            else:
                layout = house_layout(
                    norm_sys,
                    ascendant_deg=angles.ascendant_deg,
                    midheaven_deg=angles.midheaven_deg,
                    local_apparent_sidereal_deg=angles.local_apparent_sidereal_deg,
                    latitude_deg=lat,
                    true_obliquity_deg=angles.true_obliquity_deg,
                )
                cusps_final = tuple(
                    normalize_degrees(float(c) - total_offset) for c in layout.cusps_deg
                )
                canonical_sys = layout.system
        except Exception as error:
            if isinstance(error, EphemerisError):
                raise
            raise EphemerisError(str(error)) from error

        receipt_payload = {
            "schema": "ephemeris-oss.adapter.houses_ut.v1",
            "version": __version__,
            "jd_ut": round(jd_val, 9),
            "jd_tt": round(jd_tt, 9),
            "latitude_deg": round(lat, 8),
            "longitude_deg": round(lon, 8),
            "system": canonical_sys,
            "ayanamsa": ayan_name,
            "cusps_deg": [round(c, 9) for c in cusps_final],
            "ascendant_deg": round(asc_final, 9),
            "mc_deg": round(mc_final, 9),
            "vertex_deg": round(vertex_final, 9),
        }
        return HouseSystemResult(
            system=canonical_sys,
            cusps_deg=cusps_final,
            ascendant_deg=asc_final,
            mc_deg=mc_final,
            vertex_deg=vertex_final,
            receipt_sha256=canonical_hash(receipt_payload),
        )

    def compute_complete_kundali_bundle(
        self,
        instant_or_jd_ut: float | int | datetime | UtcCalendarInstant,
        latitude_deg: float,
        longitude_deg: float,
        *,
        ayanamsa: str = "lahiri",
        true_node: bool = False,
        include_svg: bool = True,
        svg_theme: str = "obsidian",
    ) -> CompleteKundaliBundle:
        """Compute a complete, unified Vedic Kundali bundle with a master SHA-256 receipt."""
        jd_ut = self._coerce_jd_ut(instant_or_jd_ut)
        ce_year, _m, _d, _h = self.revjul(jd_ut)
        ayan_deg = self.get_ayanamsa_ut(jd_ut, mode=ayanamsa)

        positions: dict[str, PlanetCoordinateResult] = {}
        lon_map: dict[str, float] = {}
        cap_lon_map: dict[str, float] = {}
        speed_map: dict[str, float] = {}
        cap_speed_map: dict[str, float] = {}
        retro_map: dict[str, bool] = {}

        for body in VEDIC_NINE_GRAHAS:
            coord = self.calc_ut(
                jd_ut,
                body,
                sidereal=True,
                ayanamsa=ayanamsa,
                true_node=bool(true_node),
            )
            positions[body] = coord
            lon_map[body] = coord.longitude_deg
            cap_lon_map[body.capitalize()] = coord.longitude_deg
            speed_map[body] = coord.longitude_speed_deg_per_day
            cap_speed_map[body.capitalize()] = coord.longitude_speed_deg_per_day
            retro_map[body.capitalize()] = coord.is_retrograde

        houses = self.houses_ut(
            jd_ut,
            latitude_deg,
            longitude_deg,
            system="whole_sign",
            ayanamsa=ayanamsa,
        )
        asc_deg = houses.ascendant_deg

        vedic_analysis = compute_vedic_chart_analysis(
            planet_longitudes=cap_lon_map,
            lagna_lon_deg=asc_deg,
            jd_ut=jd_ut,
            ayanamsa_deg=ayan_deg,
            ayanamsa_system=ayanamsa,
            planet_speeds_deg_per_day=cap_speed_map,
            ce_year=ce_year,
        )

        kp_sublords: dict[str, KpPositionLords] = {
            body: kp_coordinate_lords(pos.longitude_deg)
            for body, pos in positions.items()
        }
        kp_sublords["ascendant"] = kp_coordinate_lords(asc_deg)

        classical_yogas = evaluate_classical_yogas(lon_map, asc_deg)
        jaimini_karakamsa = compute_karakamsa_analysis(asc_deg, cap_lon_map)
        jaimini_ayurdaya = compute_jaimini_ayurdaya(asc_deg, cap_lon_map)

        bhrigu_bindu = compute_bhrigu_bindu(
            positions["moon"].longitude_deg,
            positions["rahu"].longitude_deg,
            transit_longitudes=lon_map,
        )
        khara_points = compute_khara_points(asc_deg, label="lagna")

        boundary_margins: dict[str, BoundarySensitivityEnvelope] = {}
        for body, pos in positions.items():
            eff_speed = abs(pos.longitude_speed_deg_per_day)
            if eff_speed <= 1e-9:
                eff_speed = 0.0529539
            boundary_margins[body] = compute_boundary_sensitivity(
                pos.longitude_deg,
                eff_speed,
                is_ascendant=False,
            )
        boundary_margins["ascendant"] = compute_boundary_sensitivity(
            asc_deg,
            360.0,
            is_ascendant=True,
        )

        ai_fact_sheet = compile_ai_fact_sheet(
            lon_map,
            asc_deg,
            planet_speeds_deg_per_day=speed_map,
            birth_jd_ut=jd_ut,
            latitude_deg=float(latitude_deg),
            max_bytes=3000,
        )

        north_svg: SvgChartArtifact | None = None
        south_svg: SvgChartArtifact | None = None
        if include_svg:
            north_svg = render_north_indian_svg(
                cap_lon_map,
                asc_deg,
                theme=svg_theme,
                retrograde_planets=retro_map,
            )
            south_svg = render_south_indian_svg(
                cap_lon_map,
                asc_deg,
                theme=svg_theme,
                retrograde_planets=retro_map,
            )

        bundle_receipt_payload = {
            "schema": "ephemeris-oss.adapter.complete-kundali-bundle.v1",
            "version": __version__,
            "jd_ut": round(jd_ut, 9),
            "latitude_deg": round(float(latitude_deg), 8),
            "longitude_deg": round(float(longitude_deg), 8),
            "ayanamsa_system": str(ayanamsa).lower(),
            "ayanamsa_deg": round(ayan_deg, 9),
            "position_receipts": {b: p.receipt_sha256 for b, p in positions.items()},
            "houses_receipt": houses.receipt_sha256,
            "vedic_analysis_receipt": vedic_analysis.receipt_sha256,
            "kp_sublords_receipts": {b: k.receipt_sha256 for b, k in kp_sublords.items()},
            "classical_yogas_receipt": classical_yogas.receipt_sha256,
            "jaimini_karakamsa_atmakaraka": jaimini_karakamsa.atmakaraka_planet,
            "jaimini_karakamsa_sign": jaimini_karakamsa.karakamsa_sign,
            "jaimini_ayurdaya_category": jaimini_ayurdaya.final_category,
            "bhrigu_bindu_receipt": bhrigu_bindu.receipt_sha256,
            "khara_points_receipt": khara_points.receipt_sha256,
            "boundary_margin_receipts": {b: m.receipt_sha256 for b, m in boundary_margins.items()},
            "ai_fact_sheet_receipt": ai_fact_sheet.receipt_sha256,
            "north_indian_svg_receipt": north_svg.receipt_sha256 if north_svg is not None else None,
            "south_indian_svg_receipt": south_svg.receipt_sha256 if south_svg is not None else None,
        }
        bundle_receipt_sha256 = canonical_hash(bundle_receipt_payload)

        return CompleteKundaliBundle(
            jd_ut=jd_ut,
            latitude_deg=float(latitude_deg),
            longitude_deg=float(longitude_deg),
            ayanamsa_system=str(ayanamsa).lower(),
            ayanamsa_deg=ayan_deg,
            positions=positions,
            houses=houses,
            vedic_analysis=vedic_analysis,
            kp_sublords=kp_sublords,
            classical_yogas=classical_yogas,
            jaimini_karakamsa=jaimini_karakamsa,
            jaimini_ayurdaya=jaimini_ayurdaya,
            bhrigu_bindu=bhrigu_bindu,
            khara_points=khara_points,
            boundary_margins=boundary_margins,
            ai_fact_sheet=ai_fact_sheet,
            north_indian_svg=north_svg,
            south_indian_svg=south_svg,
            bundle_receipt_sha256=bundle_receipt_sha256,
        )

    def houses_ex(
        self,
        jd_ut: float,
        lat: float,
        lon: float,
        hsys: str | bytes = b"P",
        flags: int = 0,
        *,
        tt_jd: float | None = None,
    ) -> tuple[tuple[float, ...], tuple[float, ...]]:
        """Sidecar-compatible house cusps and angles ``(cusps_12, ascmc_10)``.

        Supports ``P`` (Placidus), ``E`` (Equal), ``W`` (Whole Sign), and
        ``O`` (Porphyry). Fails closed with :class:`EphemerisError` (a
        :class:`ValueError` subclass) on unsupported house system codes.
        """
        hsys_code = (
            hsys.decode("ascii", errors="replace")
            if isinstance(hsys, (bytes, bytearray))
            else str(hsys)
        ).strip().upper()
        system_map = {
            "P": "placidus",
            "PLACIDUS": "placidus",
            "E": "equal_house",
            "EQUAL": "equal_house",
            "EQUAL_HOUSE": "equal_house",
            "W": "whole_sign",
            "WHOLE": "whole_sign",
            "WHOLE_SIGN": "whole_sign",
            "O": "porphyry",
            "PORPHYRY": "porphyry",
        }
        if hsys_code not in system_map:
            raise EphemerisError(f"Unsupported house system: {hsys_code!r}")

        ayan_mode = "lahiri" if (int(flags) & FLG_SIDEREAL) else None
        res = self.houses_ut(
            jd_ut,
            lat,
            lon,
            system=system_map[hsys_code],
            ayanamsa=ayan_mode,
            tt_jd=tt_jd,
        )
        jd_val = self._coerce_jd_ut(jd_ut)
        jd_tt = self._jd_ut_to_jd_tt(jd_val) if tt_jd is None else float(tt_jd)
        if not math.isfinite(jd_tt):
            raise EphemerisError("tt_jd must be finite")
        angles = house_angles(
            tt_jd=jd_tt,
            ut1_jd=jd_val,
            longitude_deg=float(lon),
            latitude_deg=float(lat),
        )
        ascmc = (
            res.ascendant_deg,
            res.mc_deg,
            angles.local_apparent_sidereal_deg,
            res.vertex_deg,
            math.nan,
            math.nan,
            math.nan,
            math.nan,
            math.nan,
            math.nan,
        )
        return res.cusps_deg, ascmc

    def rise_trans(
        self,
        jd_ut: float,
        body: str | int,
        event_flag: int = CALC_RISE,
        geopos: tuple[float, float, float] = (0.0, 0.0, 0.0),
        pressure: float = 1013.25,
        temp: float = 15.0,
    ) -> tuple[int, tuple[float, ...]]:
        """Compute true latitude-and-declination-sensitive rise or set JD UT."""
        _ = (pressure, temp)
        jd_val = self._coerce_jd_ut(jd_ut)
        body_key = _resolve_body_name(body)
        if int(event_flag) not in (CALC_RISE, CALC_SET):
            raise EphemerisError(
                f"Unsupported rise_trans event_flag {event_flag!r}; expected CALC_RISE (1) or CALC_SET (2)"
            )
        if len(geopos) < 2:
            raise EphemerisError("geopos must be a (longitude_deg, latitude_deg[, altitude_m]) tuple")
        lon_deg = float(geopos[0])
        lat_deg = float(geopos[1])
        if not math.isfinite(lat_deg) or not -90.0 < lat_deg < 90.0:
            raise EphemerisError("Observer latitude must be finite and within (-90, 90)")
        if not math.isfinite(lon_deg) or not -180.0 <= lon_deg <= 180.0:
            raise EphemerisError("Observer longitude must be finite and within [-180, 180]")

        def _trop_lon_lat(t_jd: float) -> tuple[float, float]:
            pos = self.calc_ut(t_jd, body_key, sidereal=False)
            return pos.longitude_deg, pos.latitude_deg

        event_jd = _solve_spherical_rise_set_jd(
            jd_start=jd_val,
            body_key=body_key,
            event_flag=int(event_flag),
            lon_deg=lon_deg,
            lat_deg=lat_deg,
            tropical_lon_lat_fn=_trop_lon_lat,
        )
        return 0, (float(event_jd),)

    def solcross_ut(
        self,
        target_lon: float,
        jd_start: float,
        flags: int = 0,
    ) -> float:
        """Compute the Julian Date UT when the Sun reaches ``target_lon`` at or after ``jd_start``."""
        target = float(target_lon) % 360.0
        cur_jd = self._coerce_jd_ut(jd_start)
        sidereal = bool(int(flags) & FLG_SIDEREAL)
        for _ in range(40):
            res = self.calc_ut(cur_jd, "sun", sidereal=sidereal)
            lon = res.longitude_deg % 360.0
            speed = res.longitude_speed_deg_per_day or 0.9856
            diff = (lon - target + 180.0) % 360.0 - 180.0
            if abs(diff) < 1e-7:
                return float(cur_jd)
            cur_jd -= diff / speed
        return float(cur_jd)

    def sol_eclipse_when_glob(
        self,
        jd_ut: float,
        flags: int = 0,
        iflag: int = 0,
    ) -> tuple[int, tuple[float, ...]]:
        """Find the next global solar eclipse at or after ``jd_ut`` via our Besselian solver."""
        _ = (flags, iflag)
        jd_val = self._coerce_jd_ut(jd_ut)
        jd_tt = self._jd_ut_to_jd_tt(jd_val)
        delta_days = jd_tt - jd_val
        eclipses = find_solar_eclipses(jd_tt, jd_tt + 400.0)
        for ecl in eclipses:
            max_ut = float(ecl.greatest_jd_tt - delta_days)
            if max_ut >= jd_val - 1e-6:
                code_map = {
                    "total": ECL_TOTAL,
                    "annular": ECL_ANNULAR,
                    "hybrid": ECL_ANNULAR_TOTAL,
                    "partial": ECL_PARTIAL,
                }
                ret_flag = code_map.get(ecl.classification, ECL_PARTIAL)
                half_span = 0.11
                return ret_flag, (
                    max_ut,
                    max_ut - half_span,
                    max_ut + half_span,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                )
        raise EphemerisError(f"No solar eclipse found within 400 days after JD {jd_val}")

    def lun_eclipse_when(
        self,
        jd_ut: float,
        flags: int = 0,
        iflag: int = 0,
    ) -> tuple[int, tuple[float, ...]]:
        """Find the next global lunar eclipse at or after ``jd_ut`` via our shadow-cone solver."""
        _ = (flags, iflag)
        jd_val = self._coerce_jd_ut(jd_ut)
        jd_tt = self._jd_ut_to_jd_tt(jd_val)
        delta_days = jd_tt - jd_val
        eclipses = find_lunar_eclipses(jd_tt, jd_tt + 400.0)
        for ecl in eclipses:
            max_ut = float(ecl.greatest_jd_tt - delta_days)
            if max_ut >= jd_val - 1e-6:
                code_map = {
                    "total": ECL_TOTAL,
                    "partial": ECL_PARTIAL,
                    "penumbral": ECL_PENUMBRAL,
                }
                ret_flag = code_map.get(ecl.classification, ECL_PENUMBRAL)
                p1_ut = float(ecl.p1_jd_tt - delta_days) if ecl.p1_jd_tt is not None else 0.0
                p4_ut = float(ecl.p4_jd_tt - delta_days) if ecl.p4_jd_tt is not None else 0.0
                u1_ut = float(ecl.u1_jd_tt - delta_days) if ecl.u1_jd_tt is not None else 0.0
                u4_ut = float(ecl.u4_jd_tt - delta_days) if ecl.u4_jd_tt is not None else 0.0
                u2_ut = float(ecl.u2_jd_tt - delta_days) if ecl.u2_jd_tt is not None else 0.0
                u3_ut = float(ecl.u3_jd_tt - delta_days) if ecl.u3_jd_tt is not None else 0.0
                return ret_flag, (
                    max_ut,
                    p1_ut,
                    p4_ut,
                    u1_ut,
                    u4_ut,
                    u2_ut,
                    u3_ut,
                    0.0,
                )
        raise EphemerisError(f"No lunar eclipse found within 400 days after JD {jd_val}")


def _solve_spherical_rise_set_jd(
    *,
    jd_start: float,
    body_key: str,
    event_flag: int,
    lon_deg: float,
    lat_deg: float,
    tropical_lon_lat_fn: Callable[[float], tuple[float, float]],
) -> float:
    """Solve rise or set UT Julian Date using spherical hour-angle geometry and equation of time."""
    deg_to_rad = math.pi / 180.0
    if body_key == "sun":
        h0_deg = -0.8333333333333334
    elif body_key == "moon":
        h0_deg = 0.125
    else:
        h0_deg = -0.5666666666666667
    sin_h0 = math.sin(h0_deg * deg_to_rad)
    sin_phi = math.sin(lat_deg * deg_to_rad)
    cos_phi = math.cos(lat_deg * deg_to_rad)
    if abs(cos_phi) < 1e-12:
        raise EphemerisError("Rise/set is undefined at exact geographic poles")

    base_noon_ut = math.floor(jd_start - 0.5) + 0.5 - (lon_deg / 360.0)

    def _ra_dec_h0_at(t_jd: float) -> tuple[float, float, float]:
        T = (t_jd - J2000_JD) / 36525.0
        eps_deg = 23.43929111 - (46.8150 * T + 0.00059 * T * T - 0.001813 * T * T * T) / 3600.0
        eps_rad = eps_deg * deg_to_rad
        lam_deg, beta_deg = tropical_lon_lat_fn(t_jd)
        lam_rad = lam_deg * deg_to_rad
        beta_rad = beta_deg * deg_to_rad

        sin_dec = math.sin(beta_rad) * math.cos(eps_rad) + math.cos(beta_rad) * math.sin(eps_rad) * math.sin(lam_rad)
        sin_dec = max(-1.0, min(1.0, sin_dec))
        dec_rad = math.asin(sin_dec)
        cos_dec = math.cos(dec_rad)
        if abs(cos_dec) < 1e-12:
            raise EphemerisError("Body is at celestial pole; rise/set undefined")

        y = math.sin(lam_rad) * math.cos(eps_rad) - math.tan(beta_rad) * math.sin(eps_rad)
        x = math.cos(lam_rad)
        ra_deg = math.degrees(math.atan2(y, x)) % 360.0

        cos_H0 = (sin_h0 - sin_phi * sin_dec) / (cos_phi * cos_dec)
        if cos_H0 < -1.0 or cos_H0 > 1.0:
            raise EphemerisError(
                f"Body {body_key!r} is circumpolar at latitude {lat_deg} deg on JD {t_jd:.2f}"
            )
        H0_deg = math.degrees(math.acos(cos_H0))
        return ra_deg, math.degrees(dec_rad), H0_deg

    def _gmst_deg(t_jd: float) -> float:
        T = (t_jd - J2000_JD) / 36525.0
        return (
            280.46061837
            + 360.98564736629 * (t_jd - J2000_JD)
            + 0.000387933 * T * T
            - (T * T * T) / 38710000.0
        ) % 360.0

    for day_offset in (-1, 0, 1, 2):
        noon_cand = base_noon_ut + float(day_offset)
        ra_deg, _dec_deg, H0_deg = _ra_dec_h0_at(noon_cand)
        target_ha = -H0_deg if event_flag == CALC_RISE else H0_deg
        lst_noon = (_gmst_deg(noon_cand) + lon_deg) % 360.0
        ha_noon = (lst_noon - ra_deg + 540.0) % 360.0 - 180.0
        t_est = noon_cand + ((target_ha - ha_noon + 540.0) % 360.0 - 180.0) / 360.98564736629

        for _ in range(4):
            ra_deg, _dec_deg, H0_deg = _ra_dec_h0_at(t_est)
            target_ha = -H0_deg if event_flag == CALC_RISE else H0_deg
            lst_est = (_gmst_deg(t_est) + lon_deg) % 360.0
            ha_est = (lst_est - ra_deg + 540.0) % 360.0 - 180.0
            delta_ha = (target_ha - ha_est + 540.0) % 360.0 - 180.0
            t_est += delta_ha / 360.98564736629
            if abs(delta_ha) < 1e-6:
                break

        if t_est >= jd_start - 1e-7:
            return float(t_est)

    raise EphemerisError(f"Unable to converge rise/set for {body_key!r} after JD {jd_start}")


# ---------------------------------------------------------------------------
# Pure-Python Analytical Fallback Provider (QA-SEC Hardened)
# ---------------------------------------------------------------------------

_ANALYTICAL_DEG = math.pi / 180.0
_ANALYTICAL_AYANAMSA_J2000 = 23.853
_ANALYTICAL_AYANAMSA_RATE_DEG_PER_YEAR = 50.2388 / 3600.0

_ANALYTICAL_ELEMENTS: Mapping[str, tuple[tuple[float, float], ...]] = {
    "Mercury": (
        (0.38709927, 0.00000037),
        (0.20563593, 0.00001906),
        (7.00497902, -0.00594749),
        (252.25032350, 149472.67411175),
        (77.45779628, 0.16047689),
        (48.33076593, -0.12534081),
    ),
    "Venus": (
        (0.72333566, 0.00000390),
        (0.00677672, -0.00004107),
        (3.39467605, -0.00078890),
        (181.97909950, 58517.81538729),
        (131.60246718, 0.00268329),
        (76.67984255, -0.27769418),
    ),
    "Earth": (
        (1.00000261, 0.00000562),
        (0.01671123, -0.00004392),
        (-0.00001531, -0.01294668),
        (100.46457166, 35999.37244981),
        (102.93768193, 0.32327364),
        (0.0, 0.0),
    ),
    "Mars": (
        (1.52371034, 0.00001847),
        (0.09339410, 0.00007882),
        (1.84969142, -0.00813131),
        (-4.55343205, 19140.30268499),
        (-23.94362959, 0.44441088),
        (49.55953891, -0.29257343),
    ),
    "Jupiter": (
        (5.20288700, -0.00011607),
        (0.04838624, -0.00013253),
        (1.30439695, -0.00183714),
        (34.39644051, 3034.74612775),
        (14.72847983, 0.21252668),
        (100.47390909, 0.20469106),
    ),
    "Saturn": (
        (9.53667594, -0.00125060),
        (0.05386179, -0.00050991),
        (2.48599187, 0.00193609),
        (49.95424423, 1222.49362201),
        (92.59887831, -0.41897216),
        (113.66242448, -0.28867794),
    ),
    "Uranus": (
        (19.18916464, -0.00196176),
        (0.04725744, -0.00004397),
        (0.77263783, -0.00242939),
        (313.23810451, 428.48202785),
        (170.95427630, 0.40805281),
        (74.01692503, 0.04240589),
    ),
    "Neptune": (
        (30.06992276, 0.00026291),
        (0.00859048, 0.00005105),
        (1.77004347, 0.00035372),
        (-55.12002969, 218.45945325),
        (44.96476227, -0.32241464),
        (131.78422574, -0.00508664),
    ),
    "Pluto": (
        (39.48211675, -0.00031596),
        (0.24882730, 0.00005170),
        (17.14001206, 0.00004818),
        (238.92903833, 145.20780515),
        (224.06891629, -0.04062942),
        (110.30393684, -0.01183482),
    ),
}

_ANALYTICAL_AYANAMSA_OFFSETS_DEG: Mapping[str, float] = {
    "lahiri": 0.0,
    "raman": -1.445,
    "kp": -0.100,
    "krishnamurti": -0.100,
    "kp_vp291": -0.100,
    "yukteshwar": -1.411,
    "fagan_bradley": 0.884,
    "true_citra": 0.0,
    "pushya": 0.0,
    "tropical": 0.0,
}

_ANALYTICAL_INT_AYANAMSA_MODES: Mapping[int, str] = {
    0: "fagan_bradley",
    1: "lahiri",
    3: "raman",
    5: "kp",
    7: "yukteshwar",
    27: "true_citra",
    29: "pushya",
    45: "kp_vp291",
}

_ANALYTICAL_INT_BODY_MAP: Mapping[int, tuple[str, bool]] = {
    0: ("Sun", False),
    1: ("Moon", False),
    2: ("Mercury", False),
    3: ("Venus", False),
    4: ("Mars", False),
    5: ("Jupiter", False),
    6: ("Saturn", False),
    7: ("Uranus", False),
    8: ("Neptune", False),
    9: ("Pluto", False),
    10: ("Rahu", False),
    11: ("Rahu", True),  # Oscillating true lunar node = 11
    100: ("Rahu", True),
}

_ANALYTICAL_STR_BODY_MAP: Mapping[str, tuple[str, bool]] = {
    "sun": ("Sun", False),
    "moon": ("Moon", False),
    "mercury": ("Mercury", False),
    "venus": ("Venus", False),
    "mars": ("Mars", False),
    "jupiter": ("Jupiter", False),
    "saturn": ("Saturn", False),
    "uranus": ("Uranus", False),
    "neptune": ("Neptune", False),
    "pluto": ("Pluto", False),
    "rahu": ("Rahu", False),
    "mean_node": ("Rahu", False),
    "mean node": ("Rahu", False),
    "true_node": ("Rahu", True),
    "true node": ("Rahu", True),
    "true_rahu": ("Rahu", True),
    "true rahu": ("Rahu", True),
    "ketu": ("Ketu", False),
    "south_node": ("Ketu", False),
    "south node": ("Ketu", False),
}


def _analytical_ayanamsa(jd: float) -> float:
    years = (jd - J2000_JD) / 365.25
    return _ANALYTICAL_AYANAMSA_J2000 + _ANALYTICAL_AYANAMSA_RATE_DEG_PER_YEAR * years


def _analytical_kepler_e(m_rad: float, ecc: float) -> float:
    e_anom = m_rad if ecc < 0.8 else math.pi
    for _ in range(12):
        delta = (e_anom - ecc * math.sin(e_anom) - m_rad) / (1.0 - ecc * math.cos(e_anom))
        e_anom -= delta
        if abs(delta) < 1e-10:
            break
    return e_anom


def _analytical_heliocentric_xyz(name: str, t_centuries: float) -> tuple[float, float, float]:
    (a0, ad), (e0, ed), (i0, id_rate), (l0, ld), (w0, wd), (o0, od) = _ANALYTICAL_ELEMENTS[name]
    a = a0 + ad * t_centuries
    e = e0 + ed * t_centuries
    inc = (i0 + id_rate * t_centuries) * _ANALYTICAL_DEG
    mean_l = l0 + ld * t_centuries
    varpi = w0 + wd * t_centuries
    omega_node = (o0 + od * t_centuries) * _ANALYTICAL_DEG
    omega_arg = (varpi - (o0 + od * t_centuries)) * _ANALYTICAL_DEG
    mean_anom = ((mean_l - varpi + 180.0) % 360.0 - 180.0) * _ANALYTICAL_DEG
    ecc_anom = _analytical_kepler_e(mean_anom, e)
    xp = a * (math.cos(ecc_anom) - e)
    yp = a * math.sqrt(max(0.0, 1.0 - e * e)) * math.sin(ecc_anom)
    co, so = math.cos(omega_arg), math.sin(omega_arg)
    c_node, s_node = math.cos(omega_node), math.sin(omega_node)
    ci, si = math.cos(inc), math.sin(inc)
    x = (co * c_node - so * s_node * ci) * xp + (-so * c_node - co * s_node * ci) * yp
    y = (co * s_node + so * c_node * ci) * xp + (-so * s_node + co * c_node * ci) * yp
    z = (so * si) * xp + (co * si) * yp
    return x, y, z


def _analytical_geocentric_sidereal_lon(name: str, jd: float) -> float:
    t_cent = (jd - J2000_JD) / 36525.0
    ex, ey, _ez = _analytical_heliocentric_xyz("Earth", t_cent)
    if name == "Sun":
        gx, gy = -ex, -ey
    else:
        px, py, _pz = _analytical_heliocentric_xyz(name, t_cent)
        gx, gy = px - ex, py - ey
    lam_j2000 = math.degrees(math.atan2(gy, gx)) % 360.0
    return (lam_j2000 - _ANALYTICAL_AYANAMSA_J2000) % 360.0


def _analytical_moon_sidereal_lon(jd: float) -> float:
    t_cent = (jd - J2000_JD) / 36525.0
    lp = 218.3164477 + 481267.88123421 * t_cent
    d = 297.8501921 + 445267.1114034 * t_cent
    m = 357.5291092 + 35999.0502909 * t_cent
    mp = 134.9633964 + 477198.8675055 * t_cent
    f = 93.2720950 + 483202.0175233 * t_cent
    lam = (
        lp
        + 6.288774 * math.sin(mp * _ANALYTICAL_DEG)
        + 1.274027 * math.sin((2.0 * d - mp) * _ANALYTICAL_DEG)
        + 0.658314 * math.sin(2.0 * d * _ANALYTICAL_DEG)
        + 0.213618 * math.sin(2.0 * mp * _ANALYTICAL_DEG)
        - 0.185116 * math.sin(m * _ANALYTICAL_DEG)
        - 0.114332 * math.sin(2.0 * f * _ANALYTICAL_DEG)
        + 0.058793 * math.sin((2.0 * d - 2.0 * mp) * _ANALYTICAL_DEG)
        + 0.057066 * math.sin((2.0 * d - m - mp) * _ANALYTICAL_DEG)
        + 0.053322 * math.sin((2.0 * d + mp) * _ANALYTICAL_DEG)
        + 0.045758 * math.sin((2.0 * d - m) * _ANALYTICAL_DEG)
    )
    return (lam - _analytical_ayanamsa(jd)) % 360.0


def _analytical_rahu_sidereal_lon(jd: float, *, true_node: bool = False) -> float:
    t_cent = (jd - J2000_JD) / 36525.0
    node = (
        125.04452
        - 1934.136261 * t_cent
        + 0.0020708 * t_cent * t_cent
        + (t_cent * t_cent * t_cent) / 450000.0
    )
    if true_node:
        d = 297.8501921 + 445267.1114034 * t_cent
        m = 357.5291092 + 35999.0502909 * t_cent
        mp = 134.9633964 + 477198.8675055 * t_cent
        f = 93.2720950 + 483202.0175233 * t_cent
        node += (
            -1.4979 * math.sin(2.0 * (d - f) * _ANALYTICAL_DEG)
            - 0.1500 * math.sin(m * _ANALYTICAL_DEG)
            - 0.1226 * math.sin(2.0 * d * _ANALYTICAL_DEG)
            + 0.1176 * math.sin(2.0 * f * _ANALYTICAL_DEG)
            - 0.0801 * math.sin(2.0 * (mp - f) * _ANALYTICAL_DEG)
        )
    return (node - _analytical_ayanamsa(jd)) % 360.0


class AnalyticalEphemerisProvider:
    """Clean-room pure-Python Keplerian + Meeus analytical provider.

    Remedies all QA-SEC findings for downstream sidecars:
    - Unknown integer or string body identifiers raise :class:`ValueError` (never default to Sun).
    - ``houses_ex`` computes distinct Placidus (``P``), Equal (``E``), Whole Sign (``W``),
      and Porphyry (``O``) cusps via :func:`house_layout`, and raises :class:`ValueError`
      on unsupported house system codes (``K, S, C, R``, etc.).
    - ``rise_trans`` computes true latitude-and-declination-dependent rise/set times
      and raises :class:`ValueError` in polar circumpolar zones.
    - ``sol_eclipse_when_glob`` and ``lun_eclipse_when`` fail closed with
      :class:`NotImplementedError` by default unless ``enable_besselian_eclipses=True``.
    """

    name: str = "alternative"

    def __init__(self, *, enable_besselian_eclipses: bool = False) -> None:
        self._ayanamsa_mode: str = "lahiri"
        self._topo_coords: tuple[float, float, float] | None = None
        self._enable_besselian_eclipses: bool = bool(enable_besselian_eclipses)

    def set_ayanamsa(self, mode: str | int = "lahiri") -> None:
        if isinstance(mode, int) and not isinstance(mode, bool):
            if mode not in _ANALYTICAL_INT_AYANAMSA_MODES:
                raise EphemerisError(f"Unsupported integer ayanamsa mode: {mode!r}")
            self._ayanamsa_mode = _ANALYTICAL_INT_AYANAMSA_MODES[mode]
            return
        key = str(mode).strip().lower().replace("-", "_")
        if key not in _ANALYTICAL_AYANAMSA_OFFSETS_DEG:
            raise EphemerisError(f"Unsupported ayanamsa mode: {mode!r}")
        self._ayanamsa_mode = key

    def get_ayanamsa_ut(self, jd: float, mode: str | int | None = None) -> float:
        if mode is not None:
            self.set_ayanamsa(mode)
        if self._ayanamsa_mode == "tropical":
            return 0.0
        offset = _ANALYTICAL_AYANAMSA_OFFSETS_DEG.get(self._ayanamsa_mode, 0.0)
        return float(_analytical_ayanamsa(float(jd)) + offset)

    def set_topo(self, longitude: float, latitude: float, altitude_m: float = 0.0) -> None:
        self._topo_coords = (float(longitude), float(latitude), float(altitude_m))

    def clear_topo(self) -> None:
        self._topo_coords = None

    def _resolve_body_name(self, body: int | str) -> tuple[str, bool]:
        if isinstance(body, int) and not isinstance(body, bool):
            if body in _ANALYTICAL_INT_BODY_MAP:
                return _ANALYTICAL_INT_BODY_MAP[body]
            raise EphemerisError(
                f"Unsupported integer body ID for analytical provider: {body!r}"
            )
        if isinstance(body, str):
            clean = body.strip().lower()
            if clean in _ANALYTICAL_STR_BODY_MAP:
                return _ANALYTICAL_STR_BODY_MAP[clean]
        raise EphemerisError(
            f"Unsupported astronomical body for analytical provider: {body!r}"
        )

    def _sidereal_longitude_for(self, name: str, jd: float, *, true_node: bool = False) -> float:
        if name == "Moon":
            return _analytical_moon_sidereal_lon(jd)
        if name == "Rahu":
            return _analytical_rahu_sidereal_lon(jd, true_node=true_node)
        if name == "Ketu":
            return (_analytical_rahu_sidereal_lon(jd, true_node=true_node) + 180.0) % 360.0
        if name == "Sun" or name in _ANALYTICAL_ELEMENTS:
            return _analytical_geocentric_sidereal_lon(name, jd)
        raise EphemerisError(f"Unsupported analytical body: {name!r}")

    def calc_ut(
        self,
        jd: float,
        body: int | str,
        flags: int = 0,
    ) -> tuple[tuple[float, float, float, float, float, float], int]:
        jd_val = float(jd)
        if not math.isfinite(jd_val):
            raise EphemerisError("jd must be finite")
        body_name, is_true_node = self._resolve_body_name(body)
        mode_offset = _ANALYTICAL_AYANAMSA_OFFSETS_DEG.get(self._ayanamsa_mode, 0.0)

        def _lon(j: float) -> float:
            sid = (self._sidereal_longitude_for(body_name, j, true_node=is_true_node) - mode_offset) % 360.0
            if int(flags) & FLG_SIDEREAL:
                return sid
            return (sid + self.get_ayanamsa_ut(j)) % 360.0

        lon = _lon(jd_val)
        l_before = _lon(jd_val - 0.5)
        l_after = _lon(jd_val + 0.5)
        speed = ((l_after - l_before + 540.0) % 360.0) - 180.0
        return (lon, 0.0, 1.0, speed, 0.0, 0.0), int(flags | FLG_SWIEPH)

    def houses_ex(
        self,
        jd: float,
        lat: float,
        lon: float,
        hsys: str | bytes = b"P",
        flags: int = 0,
    ) -> tuple[tuple[float, ...], tuple[float, ...]]:
        hsys_str = (
            hsys.decode("ascii", errors="replace")
            if isinstance(hsys, (bytes, bytearray))
            else str(hsys)
        ).strip().upper()
        system_map = {
            "W": "whole_sign",
            "P": "placidus",
            "E": "equal_house",
            "O": "porphyry",
        }
        if hsys_str not in system_map:
            raise EphemerisError(
                f"Unsupported house system for analytical provider: {hsys_str!r}; supported: P, E, W, O"
            )
        lat_f = float(lat)
        lon_f = float(lon)
        if not math.isfinite(lat_f) or not -90.0 < lat_f < 90.0:
            raise EphemerisError("Latitude must be finite and within (-90, 90)")
        if not math.isfinite(lon_f) or not -180.0 <= lon_f <= 180.0:
            raise EphemerisError("Longitude must be finite and within [-180, 180]")

        jd_val = float(jd)
        t_cent = (jd_val - J2000_JD) / 36525.0
        gmst = (
            280.46061837
            + 360.98564736629 * (jd_val - J2000_JD)
            + 0.000387933 * t_cent * t_cent
            - (t_cent * t_cent * t_cent) / 38710000.0
        ) % 360.0
        lst = (gmst + lon_f) % 360.0
        eps = 23.43929111 - (46.8150 * t_cent + 0.00059 * t_cent * t_cent - 0.001813 * t_cent * t_cent * t_cent) / 3600.0
        asc_trop, mc_trop = ascendant_midheaven_from_sidereal(lst, lat_f, eps)
        offset = self.get_ayanamsa_ut(jd_val) if (int(flags) & FLG_SIDEREAL) else 0.0
        asc = (asc_trop - offset) % 360.0
        mc = (mc_trop - offset) % 360.0

        canon_sys = system_map[hsys_str]
        if canon_sys in ("whole_sign", "equal_house"):
            layout = house_layout(canon_sys, ascendant_deg=asc, midheaven_deg=mc)
            cusps = tuple(float(c) for c in layout.cusps_deg)
        else:
            layout = house_layout(
                canon_sys,
                ascendant_deg=asc_trop,
                midheaven_deg=mc_trop,
                local_apparent_sidereal_deg=lst,
                latitude_deg=lat_f,
                true_obliquity_deg=eps,
            )
            cusps = tuple(normalize_degrees(float(c) - offset) for c in layout.cusps_deg)

        ascmc = (asc, mc, lst, (asc + 180.0) % 360.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        return cusps, ascmc

    def rise_trans(
        self,
        jd: float,
        body: int | str,
        event_flag: int,
        geopos: tuple[float, float, float],
        pressure: float = 1013.25,
        temp: float = 15.0,
    ) -> tuple[int, tuple[float, ...]]:
        _ = (pressure, temp)
        jd_val = float(jd)
        if not math.isfinite(jd_val):
            raise EphemerisError("jd must be finite")
        body_name, _is_true = self._resolve_body_name(body)
        if int(event_flag) not in (CALC_RISE, CALC_SET):
            raise EphemerisError(
                f"Unsupported rise_trans event_flag {event_flag!r}; expected CALC_RISE (1) or CALC_SET (2)"
            )
        if len(geopos) < 2:
            raise EphemerisError("geopos must be (longitude_deg, latitude_deg[, altitude_m])")
        lon_deg = float(geopos[0])
        lat_deg = float(geopos[1])
        if not math.isfinite(lat_deg) or not -90.0 < lat_deg < 90.0:
            raise EphemerisError("Observer latitude must be finite and within (-90, 90)")
        if not math.isfinite(lon_deg) or not -180.0 <= lon_deg <= 180.0:
            raise EphemerisError("Observer longitude must be finite and within [-180, 180]")

        def _trop_lon_lat(t_jd: float) -> tuple[float, float]:
            res, _ = self.calc_ut(t_jd, body_name, flags=0)
            return float(res[0]), float(res[1])

        event_jd = _solve_spherical_rise_set_jd(
            jd_start=jd_val,
            body_key=body_name.lower(),
            event_flag=int(event_flag),
            lon_deg=lon_deg,
            lat_deg=lat_deg,
            tropical_lon_lat_fn=_trop_lon_lat,
        )
        return 0, (float(event_jd),)

    def solcross_ut(
        self,
        target_lon: float,
        jd_start: float,
        flags: int = 0,
    ) -> float:
        target = float(target_lon) % 360.0
        cur_jd = float(jd_start)
        for _ in range(40):
            res, _ = self.calc_ut(cur_jd, "Sun", flags)
            lon = res[0] % 360.0
            speed = res[3] or 0.9856
            diff = (lon - target + 180.0) % 360.0 - 180.0
            if abs(diff) < 1e-7:
                return float(cur_jd)
            cur_jd -= diff / speed
        return float(cur_jd)

    def sol_eclipse_when_glob(
        self,
        jd: float,
        flags: int = 0,
        iflag: int = 0,
    ) -> tuple[int, tuple[float, ...]]:
        _ = (flags, iflag)
        if not self._enable_besselian_eclipses:
            raise NotImplementedError(
                "Global solar eclipse search is not available on the Keplerian analytical fallback; "
                "use EphemerisAdapter or pass enable_besselian_eclipses=True"
            )
        jd_val = float(jd)
        eclipses = find_solar_eclipses(jd_val, jd_val + 400.0)
        for ecl in eclipses:
            if ecl.greatest_jd_tt >= jd_val - 1e-6:
                code_map = {
                    "total": ECL_TOTAL,
                    "annular": ECL_ANNULAR,
                    "hybrid": ECL_ANNULAR_TOTAL,
                    "partial": ECL_PARTIAL,
                }
                ret_flag = code_map.get(ecl.classification, ECL_PARTIAL)
                max_jd = float(ecl.greatest_jd_tt)
                return ret_flag, (max_jd, max_jd - 0.11, max_jd + 0.11, 0.0, 0.0, 0.0, 0.0, 0.0)
        raise EphemerisError(f"No solar eclipse found within 400 days after JD {jd_val}")

    def lun_eclipse_when(
        self,
        jd: float,
        flags: int = 0,
        iflag: int = 0,
    ) -> tuple[int, tuple[float, ...]]:
        _ = (flags, iflag)
        if not self._enable_besselian_eclipses:
            raise NotImplementedError(
                "Global lunar eclipse search is not available on the Keplerian analytical fallback; "
                "use EphemerisAdapter or pass enable_besselian_eclipses=True"
            )
        jd_val = float(jd)
        eclipses = find_lunar_eclipses(jd_val, jd_val + 400.0)
        for ecl in eclipses:
            if ecl.greatest_jd_tt >= jd_val - 1e-6:
                code_map = {
                    "total": ECL_TOTAL,
                    "partial": ECL_PARTIAL,
                    "penumbral": ECL_PENUMBRAL,
                }
                ret_flag = code_map.get(ecl.classification, ECL_PENUMBRAL)
                max_jd = float(ecl.greatest_jd_tt)
                return ret_flag, (
                    max_jd,
                    float(ecl.p1_jd_tt or 0.0),
                    float(ecl.p4_jd_tt or 0.0),
                    float(ecl.u1_jd_tt or 0.0),
                    float(ecl.u4_jd_tt or 0.0),
                    float(ecl.u2_jd_tt or 0.0),
                    float(ecl.u3_jd_tt or 0.0),
                    0.0,
                )
        raise EphemerisError(f"No lunar eclipse found within 400 days after JD {jd_val}")

    def get_version(self) -> str:
        return f"ephemeris-oss {__version__}-analytical (Apache-2.0 clean-room)"

    def get_planet_positions(
        self,
        dt: datetime,
        location: GeoCoords | None = None,
        planets: Sequence[str] | None = None,
    ) -> dict[str, PlanetPosition]:
        """Sidereal positions at UTC datetime dt matching IEphemerisProvider."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        if location is not None:
            self.set_topo(location.longitude, location.latitude, getattr(location, "altitude_m", 0.0))
        y, m, d = dt.year, dt.month, dt.day
        hour_ut = (
            float(dt.hour)
            + float(dt.minute) / 60.0
            + (float(dt.second) + float(dt.microsecond) / 1_000_000.0) / 3600.0
        )
        if m <= 2:
            y -= 1
            m += 12
        a = y // 100
        b = 2 - a + (a // 4)
        jd = math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + b - 1524.5 + hour_ut / 24.0

        candidates = (
            list(planets)
            if planets is not None
            else ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
        )
        result: dict[str, PlanetPosition] = {}
        for p in candidates:
            body_key = str(p).strip().lower()
            canonical_name = body_key.capitalize() if body_key != "true_node" else "True Node"
            coords, _ = self.calc_ut(jd, body_key, flags=FLG_SIDEREAL)
            lon = coords[0] % 360.0
            speed = coords[3]
            retrograde = speed < 0.0
            sign_num, sign_name, deg_in_sign = sign_from_longitude(lon)
            nak = nakshatra_from_longitude(lon)
            result[canonical_name] = PlanetPosition(
                name=canonical_name,
                longitude=lon,
                sign=sign_name,
                sign_num=sign_num,
                degree_in_sign=deg_in_sign,
                retrograde=retrograde,
                speed=speed,
                nakshatra=nak,
            )
        return result


def normalize_ephemeris_source(
    source: str | None = None,
    *,
    env: Mapping[str, str] | None = None,
    manifest_validator: Callable[[str], Any] | None = None,
    default_source: str = "primary",
) -> str:
    """Validate and normalize an ephemeris provider source with fail-closed manifest checks.

    Guarantees:
    1. When unconfigured (``EPHEMERIS_SOURCE`` omitted and ``source`` is ``None``),
       returns ``default_source``.
    2. If ``EPHEMERIS_RELEASE_MANIFEST`` or a ``*_DE440_KERNEL`` path is supplied
       in the environment (even when ``EPHEMERIS_SOURCE`` is omitted), validates the
       supplied path(s) and raises :class:`EphemerisError` (:class:`ValueError`) if
       missing or invalid rather than silently falling back to ``"alternative"``.
    """
    fallback_primary = str(default_source).strip().lower()
    environ = os.environ if env is None else env
    explicit_env = environ.get("EPHEMERIS_SOURCE")
    configured = (explicit_env or fallback_primary).strip().lower()
    raw = (source if source is not None else configured).strip().lower()

    manifest = environ.get("EPHEMERIS_RELEASE_MANIFEST")
    kernel_env = environ.get("EPHEMERIS_DE440_KERNEL") or next(
        (val for key, val in environ.items() if key.upper().endswith("_DE440_KERNEL")),
        None,
    )

    def _validate_manifest_and_kernel(require_manifest: bool) -> None:
        if require_manifest and not manifest:
            raise EphemerisError("EPHEMERIS_SOURCE=JPL requires an ephemeris release manifest")
        if manifest:
            manifest_path = Path(manifest)
            if not manifest_path.is_file():
                raise EphemerisError(f"ephemeris release manifest unavailable: {manifest_path}")
            if manifest_validator is not None:
                manifest_validator(str(manifest_path))
        if kernel_env:
            kernel_path = Path(kernel_env)
            if not kernel_path.is_file():
                raise EphemerisError(f"ephemeris DE440 kernel file unavailable: {kernel_path}")

    # Fail closed if caller or environment supplied a release manifest or kernel path
    # even when EPHEMERIS_SOURCE was omitted.
    if source is None and explicit_env is None and (manifest or kernel_env):
        if not manifest or not kernel_env:
            raise EphemerisError(
                "Both EPHEMERIS_RELEASE_MANIFEST and DE440 kernel path must be valid files when supplied"
            )
        _validate_manifest_and_kernel(require_manifest=True)

    if raw == fallback_primary:
        return fallback_primary
    if raw in ("alternative", "analytical", "alt"):
        return "alternative"
    if raw in ("dark", "jpl"):
        if source is None and configured == "dark":
            raise EphemerisError("EPHEMERIS_SOURCE=DARK is not a releasable primary; use JPL")
        if configured != "jpl":
            return "alternative" if configured in ("alternative", "analytical", "alt") else fallback_primary
        _validate_manifest_and_kernel(require_manifest=True)
        return "jpl"
    return fallback_primary


__all__ = [
    "AU_KM",
    "AnalyticalEphemerisProvider",
    "BODY_CODE_MAP",
    "CALC_RISE",
    "CALC_SET",
    "CompleteKundaliBundle",
    "ECL_ANNULAR",
    "ECL_ANNULAR_TOTAL",
    "ECL_PARTIAL",
    "ECL_PENUMBRAL",
    "ECL_TOTAL",
    "EphemerisAdapter",
    "FLG_EQUATORIAL",
    "FLG_SIDEREAL",
    "FLG_SPEED",
    "FLG_SWIEPH",
    "FLG_TOPOCTR",
    "GeoCoords",
    "HouseSystemResult",
    "JUPITER",
    "KETU",
    "MARS",
    "MEAN_NODE",
    "MERCURY",
    "MOON",
    "NAKSHATRAS_27",
    "NAKSHATRA_ARC",
    "NEPTUNE",
    "NakshatraInfo",
    "PLUTO",
    "PlanetCoordinateResult",
    "PlanetPosition",
    "RAHU",
    "SATURN",
    "SIGNS_12",
    "SOUTH_NODE",
    "SUN",
    "TRUE_NODE",
    "URANUS",
    "VEDIC_NINE_GRAHAS",
    "VENUS",
    "nakshatra_from_longitude",
    "normalize_ephemeris_source",
    "sign_from_longitude",
]
