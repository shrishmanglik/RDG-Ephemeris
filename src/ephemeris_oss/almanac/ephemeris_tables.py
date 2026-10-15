"""Tabular Ephemeris Grid Generator and High-Precision Ingress / Synodic Aspect Scanner.

Generates classic *Indian Ephemeris* style tabular sidereal coordinate grids at configurable
time steps (with CSV and Markdown export) and scans date intervals for exact Rashi (sign)
ingresses, Nakshatra ingresses, and synodic planetary aspects using guarded secant-bisection
root refinement.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
import io
import math
from typing import Any, Iterator, Mapping, Sequence

from .._version import __version__
from ..adapter import AnalyticalEphemerisProvider, EphemerisAdapter, FLG_SIDEREAL
from ..engine.receipt import canonical_hash
from ..jyotish.nakshatra import (
    NAKSHATRA_NAMES,
    NAKSHATRA_SPAN_DEG,
    RASI_NAMES as RASHI_NAMES,
    nakshatra_position,
)

DEFAULT_TABLE_BODIES: tuple[str, ...] = (
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
    "Rahu",
    "Ketu",
)

DEFAULT_ASPECT_ANGLES: tuple[float, ...] = (0.0, 60.0, 90.0, 120.0, 180.0)

STATIONARY_SPEED_THRESHOLD_DEG_PER_DAY: float = 0.005
MAX_EPHEMERIS_TABLE_ROWS: int = 400
MAX_STEP_DAYS: float = 30.0

_CANONICAL_BODY_LABELS: Mapping[str, str] = {
    "sun": "Sun",
    "surya": "Sun",
    "ravi": "Sun",
    "moon": "Moon",
    "chandra": "Moon",
    "soma": "Moon",
    "mars": "Mars",
    "mangala": "Mars",
    "kuja": "Mars",
    "mercury": "Mercury",
    "budha": "Mercury",
    "jupiter": "Jupiter",
    "guru": "Jupiter",
    "brihaspati": "Jupiter",
    "venus": "Venus",
    "shukra": "Venus",
    "saturn": "Saturn",
    "shani": "Saturn",
    "uranus": "Uranus",
    "neptune": "Neptune",
    "pluto": "Pluto",
    "rahu": "Rahu",
    "mean_node": "Rahu",
    "true_node": "Rahu",
    "north_node": "Rahu",
    "ketu": "Ketu",
    "south_node": "Ketu",
}

_ASPECT_NAMES: Mapping[float, str] = {
    0.0: "Conjunction",
    30.0: "Semi-Sextile",
    45.0: "Semi-Square",
    60.0: "Sextile",
    72.0: "Quintile",
    90.0: "Square",
    120.0: "Trine",
    135.0: "Sesquiquadrate",
    150.0: "Quincunx",
    180.0: "Opposition",
    210.0: "Quincunx (210)",
    240.0: "Trine (240)",
    270.0: "Square (270)",
    300.0: "Sextile (300)",
}


def _normalize_body_label(body: str) -> str:
    if not isinstance(body, str) or not body.strip():
        raise ValueError(f"body name must be a non-empty string; got {body!r}")
    key = body.strip().lower().replace(" ", "_")
    if key not in _CANONICAL_BODY_LABELS:
        raise ValueError(f"unsupported body name {body!r}")
    return _CANONICAL_BODY_LABELS[key]


def _jd_ut_to_iso_utc(jd_ut: float) -> str:
    year, month, day, hour_ut = EphemerisAdapter.revjul(jd_ut)
    total_sec = int(round(hour_ut * 3600.0))
    if total_sec >= 86400:
        year, month, day, _ = EphemerisAdapter.revjul(jd_ut + 0.5 / 86400.0)
        total_sec = 0
    hh = total_sec // 3600
    rem = total_sec % 3600
    mm = rem // 60
    ss = rem % 60
    return f"{year:04d}-{month:02d}-{day:02d}T{hh:02d}:{mm:02d}:{ss:02d}Z"


def format_dms(degrees: float, include_sign: bool = False) -> str:
    """Format an ecliptic longitude in ``[0, 360)`` as exact DMS.

    Parameters
    ----------
    degrees:
        Angle in decimal degrees (normalized modulo 360).
    include_sign:
        When ``True``, prefixes the Sanskrit Rashi name and formats the degree
        within the 30-degree sign (e.g. ``"Mesha 14d 23m 11.4s"``). When ``False``,
        formats the normalized angle directly (e.g. ``"14d 23m 11.4s"``).
    """
    val = float(degrees)
    if not math.isfinite(val):
        raise ValueError(f"degrees must be finite; got {degrees!r}")
    lon = val % 360.0
    total_tenths = int(round(lon * 36000.0)) % (360 * 36000)

    if include_sign:
        sign_tenths = 30 * 36000
        rashi_idx = (total_tenths // sign_tenths) % 12
        rem_tenths = total_tenths % sign_tenths
        deg = rem_tenths // 36000
        rem_tenths %= 36000
        minutes = rem_tenths // 600
        seconds = (rem_tenths % 600) / 10.0
        return f"{RASHI_NAMES[rashi_idx]} {deg:02d}d {minutes:02d}m {seconds:04.1f}s"

    deg = total_tenths // 36000
    rem_tenths = total_tenths % 36000
    minutes = rem_tenths // 600
    seconds = (rem_tenths % 600) / 10.0
    return f"{deg:02d}d {minutes:02d}m {seconds:04.1f}s"


@dataclass(frozen=True)
class BodyTableCell:
    """Per-body tabular ephemeris entry for a single epoch row."""

    body: str
    longitude_deg: float
    speed_deg_per_day: float
    is_retrograde: bool
    motion_code: str
    rashi_index: int
    rashi_name: str
    dms_in_rashi: str
    nakshatra_index: int
    nakshatra_name: str
    pada: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "body": self.body,
            "longitude_deg": self.longitude_deg,
            "speed_deg_per_day": self.speed_deg_per_day,
            "is_retrograde": self.is_retrograde,
            "motion_code": self.motion_code,
            "rashi_index": self.rashi_index,
            "rashi_name": self.rashi_name,
            "dms_in_rashi": self.dms_in_rashi,
            "nakshatra_index": self.nakshatra_index,
            "nakshatra_name": self.nakshatra_name,
            "pada": self.pada,
        }

    def __getitem__(self, key: str) -> Any:
        data = self.to_dict()
        if key in data:
            return data[key]
        raise KeyError(key)

    def get(self, key: str, default: Any = None) -> Any:
        return self.to_dict().get(key, default)

    def keys(self) -> Iterator[str]:
        return iter(self.to_dict().keys())

    def items(self) -> Iterator[tuple[str, Any]]:
        return iter(self.to_dict().items())

    def values(self) -> Iterator[Any]:
        return iter(self.to_dict().values())

    def __contains__(self, key: object) -> bool:
        return key in self.to_dict()


class _CaseInsensitiveBodyMap(dict[str, BodyTableCell]):
    """Dictionary of body cells supporting both canonical TitleCase and lowercase keys."""

    def __getitem__(self, key: str) -> BodyTableCell:
        if super().__contains__(key):
            return super().__getitem__(key)
        try:
            norm = _normalize_body_label(key)
        except ValueError as exc:
            raise KeyError(key) from exc
        if super().__contains__(norm):
            return super().__getitem__(norm)
        raise KeyError(key)

    def __contains__(self, key: object) -> bool:
        if super().__contains__(key):
            return True
        if isinstance(key, str):
            try:
                norm = _normalize_body_label(key)
            except ValueError:
                return False
            return super().__contains__(norm)
        return False

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default


@dataclass(frozen=True)
class EphemerisTableRow:
    """Single timestamp row of a tabular sidereal ephemeris grid."""

    jd_ut: float
    iso_utc: str
    ayanamsa_deg: float
    bodies: Mapping[str, BodyTableCell]

    @property
    def positions(self) -> Mapping[str, BodyTableCell]:
        return self.bodies

    def __getitem__(self, key: str) -> Any:
        if key in ("jd_ut", "iso_utc", "ayanamsa_deg", "bodies"):
            return getattr(self, key)
        return self.bodies[key]

    def to_dict(self) -> dict[str, Any]:
        return {
            "jd_ut": self.jd_ut,
            "iso_utc": self.iso_utc,
            "ayanamsa_deg": self.ayanamsa_deg,
            "bodies": {name: cell.to_dict() for name, cell in self.bodies.items()},
        }


@dataclass(frozen=True)
class EphemerisTable:
    """Complete tabular ephemeris grid with CSV/Markdown serializers and SHA-256 receipt."""

    start_jd_ut: float
    end_jd_ut: float
    step_days: float
    bodies: tuple[str, ...]
    rows: tuple[EphemerisTableRow, ...]
    receipt: Mapping[str, Any]
    receipt_sha256: str

    def to_csv(self) -> str:
        """Serialize the tabular ephemeris grid to RFC-4180 CSV text."""
        buf = io.StringIO()
        writer = csv.writer(buf, lineterminator="\n")
        header: list[str] = ["jd_ut", "iso_utc", "ayanamsa_deg"]
        for body in self.bodies:
            header.extend(
                [
                    f"{body}_longitude_deg",
                    f"{body}_speed_deg_per_day",
                    f"{body}_is_retrograde",
                    f"{body}_motion_code",
                    f"{body}_rashi_index",
                    f"{body}_rashi_name",
                    f"{body}_dms_in_rashi",
                    f"{body}_nakshatra_index",
                    f"{body}_nakshatra_name",
                    f"{body}_pada",
                ]
            )
        writer.writerow(header)
        for row in self.rows:
            line: list[Any] = [
                f"{row.jd_ut:.8f}",
                row.iso_utc,
                f"{row.ayanamsa_deg:.6f}",
            ]
            for body in self.bodies:
                cell = row.bodies[body]
                line.extend(
                    [
                        f"{cell.longitude_deg:.6f}",
                        f"{cell.speed_deg_per_day:.6f}",
                        str(cell.is_retrograde),
                        cell.motion_code,
                        cell.rashi_index,
                        cell.rashi_name,
                        cell.dms_in_rashi,
                        cell.nakshatra_index,
                        cell.nakshatra_name,
                        cell.pada,
                    ]
                )
            writer.writerow(line)
        return buf.getvalue()

    def to_markdown(self) -> str:
        """Render the tabular ephemeris grid as a GitHub-Flavored Markdown table."""
        headers = ["JD (UT)", "UTC", "Ayanamsa"] + list(self.bodies)
        sep = ["---", "---", "---"] + ["---" for _ in self.bodies]
        lines = [
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join(sep) + " |",
        ]
        for row in self.rows:
            cols = [
                f"{row.jd_ut:.5f}",
                row.iso_utc,
                f"{row.ayanamsa_deg:.4f}d",
            ]
            for body in self.bodies:
                cell = row.bodies[body]
                cols.append(
                    f"{cell.rashi_name} {cell.dms_in_rashi} ({cell.motion_code}, {cell.nakshatra_name} P{cell.pada})"
                )
            lines.append("| " + " | ".join(cols) + " |")
        return "\n".join(lines) + "\n"

    def to_dict(self) -> dict[str, Any]:
        return {
            "start_jd_ut": self.start_jd_ut,
            "end_jd_ut": self.end_jd_ut,
            "step_days": self.step_days,
            "bodies": list(self.bodies),
            "rows": [row.to_dict() for row in self.rows],
            "receipt": dict(self.receipt),
            "receipt_sha256": self.receipt_sha256,
        }


@dataclass(frozen=True)
class PlanetaryIngressEvent:
    """Refined Rashi or Nakshatra ingress event on a transit timeline."""

    jd_ut: float
    iso_utc: str
    body: str
    ingress_type: str
    from_index: int
    to_index: int
    from_name: str
    to_name: str
    boundary_longitude_deg: float
    longitude_deg: float
    speed_deg_per_day: float
    is_retrograde: bool

    @property
    def event_type(self) -> str:
        return f"{self.ingress_type}_ingress"

    @property
    def from_rashi(self) -> str:
        return self.from_name

    @property
    def to_rashi(self) -> str:
        return self.to_name

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "jd_ut": self.jd_ut,
            "iso_utc": self.iso_utc,
            "body": self.body,
            "ingress_type": self.ingress_type,
            "from_index": self.from_index,
            "to_index": self.to_index,
            "from_name": self.from_name,
            "to_name": self.to_name,
            "boundary_longitude_deg": self.boundary_longitude_deg,
            "longitude_deg": self.longitude_deg,
            "speed_deg_per_day": self.speed_deg_per_day,
            "is_retrograde": self.is_retrograde,
        }


@dataclass(frozen=True)
class SynodicAspectEvent:
    """Refined exact synodic planetary aspect event on a transit timeline."""

    jd_ut: float
    iso_utc: str
    body_a: str
    body_b: str
    aspect_angle_deg: float
    aspect_name: str
    longitude_a_deg: float
    longitude_b_deg: float
    separation_deg: float
    relative_speed_deg_per_day: float

    @property
    def event_type(self) -> str:
        return "synodic_aspect"

    @property
    def aspect_angle(self) -> float:
        return self.aspect_angle_deg

    @property
    def lon_a(self) -> float:
        return self.longitude_a_deg

    @property
    def lon_b(self) -> float:
        return self.longitude_b_deg

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "jd_ut": self.jd_ut,
            "iso_utc": self.iso_utc,
            "body_a": self.body_a,
            "body_b": self.body_b,
            "aspect_angle_deg": self.aspect_angle_deg,
            "aspect_name": self.aspect_name,
            "longitude_a_deg": self.longitude_a_deg,
            "longitude_b_deg": self.longitude_b_deg,
            "separation_deg": self.separation_deg,
            "relative_speed_deg_per_day": self.relative_speed_deg_per_day,
        }


@dataclass(frozen=True)
class TransitTimelineReport:
    """Chronological report of planetary ingresses and synodic aspects with SHA-256 receipt."""

    start_jd_ut: float
    end_jd_ut: float
    bodies: tuple[str, ...]
    aspect_angles: tuple[float, ...]
    include_nakshatra_ingresses: bool
    ingresses: tuple[PlanetaryIngressEvent, ...]
    rashi_ingresses: tuple[PlanetaryIngressEvent, ...]
    nakshatra_ingresses: tuple[PlanetaryIngressEvent, ...]
    aspects: tuple[SynodicAspectEvent, ...]
    events: tuple[PlanetaryIngressEvent | SynodicAspectEvent, ...]
    receipt: Mapping[str, Any]
    receipt_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "start_jd_ut": self.start_jd_ut,
            "end_jd_ut": self.end_jd_ut,
            "bodies": list(self.bodies),
            "aspect_angles": list(self.aspect_angles),
            "include_nakshatra_ingresses": self.include_nakshatra_ingresses,
            "ingresses": [item.to_dict() for item in self.ingresses],
            "rashi_ingresses": [item.to_dict() for item in self.rashi_ingresses],
            "nakshatra_ingresses": [item.to_dict() for item in self.nakshatra_ingresses],
            "aspects": [item.to_dict() for item in self.aspects],
            "events": [item.to_dict() for item in self.events],
            "receipt": dict(self.receipt),
            "receipt_sha256": self.receipt_sha256,
        }


def _make_evaluator(
    adapter: EphemerisAdapter | AnalyticalEphemerisProvider | None,
):
    analytical = AnalyticalEphemerisProvider()
    cache: dict[tuple[str, float], tuple[float, float, bool]] = {}

    def eval_body(jd_ut: float, body_label: str) -> tuple[float, float, bool]:
        key = (body_label, float(jd_ut))
        if key in cache:
            return cache[key]
        if adapter is None:
            coords, _ = analytical.calc_ut(jd_ut, body_label, flags=FLG_SIDEREAL)
            lon = float(coords[0]) % 360.0
            spd = float(coords[3])
            retro = False if body_label in ("Sun", "Moon") else (True if body_label in ("Rahu", "Ketu") else bool(spd < 0.0))
        elif isinstance(adapter, AnalyticalEphemerisProvider):
            coords, _ = adapter.calc_ut(jd_ut, body_label, flags=FLG_SIDEREAL)
            lon = float(coords[0]) % 360.0
            spd = float(coords[3])
            retro = False if body_label in ("Sun", "Moon") else (True if body_label in ("Rahu", "Ketu") else bool(spd < 0.0))
        else:
            pos = adapter.calc_ut(jd_ut, body_label.lower(), sidereal=True)
            lon = float(pos.longitude_deg) % 360.0
            spd = float(pos.longitude_speed_deg_per_day)
            retro = bool(pos.is_retrograde)
        res = (lon, spd, retro)
        cache[key] = res
        return res

    def eval_ayanamsa(jd_ut: float) -> float:
        if adapter is None:
            return float(analytical.get_ayanamsa_ut(jd_ut))
        return float(adapter.get_ayanamsa_ut(jd_ut))

    return eval_body, eval_ayanamsa


def _motion_code_for(body_label: str, speed_deg_per_day: float, is_retrograde: bool) -> str:
    if body_label not in ("Sun", "Moon") and abs(speed_deg_per_day) < STATIONARY_SPEED_THRESHOLD_DEG_PER_DAY:
        return "S"
    if is_retrograde or (body_label not in ("Sun", "Moon") and speed_deg_per_day < 0.0):
        return "R"
    return "D"


def generate_ephemeris_table(
    start_jd_ut: float,
    end_jd_ut: float,
    step_days: float = 1.0,
    *,
    bodies: Sequence[str] = DEFAULT_TABLE_BODIES,
    adapter: EphemerisAdapter | AnalyticalEphemerisProvider | None = None,
) -> EphemerisTable:
    """Generate a complete *Indian Ephemeris* style tabular sidereal grid."""
    start_val = float(start_jd_ut)
    end_val = float(end_jd_ut)
    step_val = float(step_days)

    if not math.isfinite(start_val) or not math.isfinite(end_val):
        raise ValueError("start_jd_ut and end_jd_ut must be finite Julian Dates")
    if end_val < start_val:
        raise ValueError(f"end_jd_ut ({end_val}) must be >= start_jd_ut ({start_val})")
    if not math.isfinite(step_val) or step_val <= 0.0 or step_val > MAX_STEP_DAYS:
        raise ValueError(f"step_days must be in (0, {MAX_STEP_DAYS}]; got {step_days!r}")
    if not bodies:
        raise ValueError("bodies must contain at least one planetary body")

    canonical_bodies: list[str] = []
    seen: set[str] = set()
    for b in bodies:
        label = _normalize_body_label(b)
        if label not in seen:
            canonical_bodies.append(label)
            seen.add(label)
    body_tuple = tuple(canonical_bodies)

    span = end_val - start_val
    num_rows = int(math.floor((span + 1e-9 * step_val) / step_val)) + 1
    if num_rows > MAX_EPHEMERIS_TABLE_ROWS:
        raise ValueError(
            f"Requested grid requires {num_rows} rows, exceeding maximum {MAX_EPHEMERIS_TABLE_ROWS} rows per call"
        )

    eval_body, eval_ayanamsa = _make_evaluator(adapter)
    rows: list[EphemerisTableRow] = []

    for idx in range(num_rows):
        jd = start_val + idx * step_val
        if jd > end_val and idx > 0:
            jd = end_val
        iso_utc = _jd_ut_to_iso_utc(jd)
        ayan_deg = eval_ayanamsa(jd)

        cell_map = _CaseInsensitiveBodyMap()
        for body_label in body_tuple:
            lon, spd, retro = eval_body(jd, body_label)
            m_code = _motion_code_for(body_label, spd, retro)
            rashi_idx = int(lon // 30.0) % 12
            rashi_name = RASHI_NAMES[rashi_idx]
            dms_str = format_dms(lon % 30.0, include_sign=False)
            nak = nakshatra_position(lon)

            cell_map[body_label] = BodyTableCell(
                body=body_label,
                longitude_deg=round(lon, 8),
                speed_deg_per_day=round(spd, 8),
                is_retrograde=retro,
                motion_code=m_code,
                rashi_index=rashi_idx,
                rashi_name=rashi_name,
                dms_in_rashi=dms_str,
                nakshatra_index=nak.index,
                nakshatra_name=nak.name,
                pada=nak.pada,
            )

        rows.append(
            EphemerisTableRow(
                jd_ut=round(jd, 8),
                iso_utc=iso_utc,
                ayanamsa_deg=round(ayan_deg, 8),
                bodies=cell_map,
            )
        )

    receipt_payload: dict[str, Any] = {
        "schema": "ephemeris-oss.almanac.ephemeris_table.v1",
        "version": __version__,
        "start_jd_ut": round(start_val, 8),
        "end_jd_ut": round(end_val, 8),
        "step_days": round(step_val, 8),
        "bodies": list(body_tuple),
        "row_count": len(rows),
        "first_row_jd_ut": rows[0].jd_ut,
        "last_row_jd_ut": rows[-1].jd_ut,
        "sample_longitudes": {
            b: [rows[0].bodies[b].longitude_deg, rows[-1].bodies[b].longitude_deg]
            for b in body_tuple
        },
    }
    return EphemerisTable(
        start_jd_ut=start_val,
        end_jd_ut=end_val,
        step_days=step_val,
        bodies=body_tuple,
        rows=tuple(rows),
        receipt=receipt_payload,
        receipt_sha256=canonical_hash(receipt_payload),
    )


def _signed_angle_diff(angle_deg: float, target_deg: float) -> float:
    """Return signed angular residual ``angle_deg - target_deg`` in ``[-180, 180)``."""
    return ((angle_deg - target_deg + 180.0) % 360.0) - 180.0


def _refine_angle_crossing(
    fn_angle,
    t_left: float,
    t_right: float,
    target_deg: float,
    *,
    tol_days: float = 2e-8,
) -> float:
    """Refine root of ``fn_angle(t) == target_deg (mod 360)`` via guarded secant-bisection.

    Returns an 8-decimal rounded Julian Date ``jd_ut`` within ``< 1e-6`` days of the root
    such that ``fn_angle(jd_ut)`` sits strictly on the ``[2e-7, 5e-5)`` degree side above
    ``target_deg``, preventing floating-point modulo wraparound to ``29.999999`` or ``359.999999``.
    """
    a = float(t_left)
    b = float(t_right)
    fa = _signed_angle_diff(fn_angle(a), target_deg)
    fb = _signed_angle_diff(fn_angle(b), target_deg)

    for _ in range(40):
        if abs(b - a) <= tol_days:
            break
        if abs(fb - fa) > 1e-12:
            sec = b - fb * (b - a) / (fb - fa)
            margin = 0.05 * (b - a)
            if (a + margin) < sec < (b - margin):
                mid = sec
            else:
                mid = 0.5 * (a + b)
        else:
            mid = 0.5 * (a + b)

        fmid = _signed_angle_diff(fn_angle(mid), target_deg)
        if (fa <= 0.0 <= fmid) or (fa >= 0.0 >= fmid):
            b = mid
            fb = fmid
        else:
            a = mid
            fa = fmid

    t_pos = a if fa >= 0.0 else b
    step_dir = 1.0 if fb >= fa else -1.0
    base_jd = round(t_pos, 8)
    for k in range(0, 50):
        cand_jd = round(base_jd + step_dir * k * 1e-8, 8)
        diff = _signed_angle_diff(fn_angle(cand_jd), target_deg)
        if diff >= 1.5e-7:
            return cand_jd
    return round(t_pos + step_dir * 5e-7, 8)



def scan_ingresses_and_aspects(
    start_jd_ut: float,
    end_jd_ut: float,
    *,
    bodies: Sequence[str] = DEFAULT_TABLE_BODIES,
    aspect_angles: Sequence[float] = DEFAULT_ASPECT_ANGLES,
    include_nakshatra_ingresses: bool = False,
    adapter: EphemerisAdapter | AnalyticalEphemerisProvider | None = None,
) -> TransitTimelineReport:
    """Scan ``[start_jd_ut, end_jd_ut]`` for exact Rashi/Nakshatra ingresses and synodic aspects."""
    start_val = float(start_jd_ut)
    end_val = float(end_jd_ut)
    if not math.isfinite(start_val) or not math.isfinite(end_val):
        raise ValueError("start_jd_ut and end_jd_ut must be finite Julian Dates")
    if end_val <= start_val:
        raise ValueError(f"end_jd_ut ({end_val}) must be strictly greater than start_jd_ut ({start_val})")
    if end_val - start_val > 400.0:
        raise ValueError("scan_ingresses_and_aspects span cannot exceed 400 days per call")
    if not bodies:
        raise ValueError("bodies must contain at least one planetary body")

    canonical_bodies: list[str] = []
    seen_bodies: set[str] = set()
    for b in bodies:
        label = _normalize_body_label(b)
        if label not in seen_bodies:
            canonical_bodies.append(label)
            seen_bodies.add(label)
    body_tuple = tuple(canonical_bodies)

    clean_angles: list[float] = []
    seen_angles: set[float] = set()
    for ang in aspect_angles:
        ang_f = float(ang)
        if not math.isfinite(ang_f):
            raise ValueError(f"aspect_angle must be finite; got {ang!r}")
        norm_ang = round(ang_f % 360.0, 8)
        if norm_ang not in seen_angles:
            clean_angles.append(norm_ang)
            seen_angles.add(norm_ang)
    angle_tuple = tuple(clean_angles)

    eval_body, _ = _make_evaluator(adapter)

    # Coarse grid at 0.25-day intervals (6 hours) guarantees Moon moves ~3.3 deg (< 1/4 Nakshatra)
    coarse_step = 0.25
    num_coarse = max(2, int(math.ceil((end_val - start_val) / coarse_step)) + 1)
    t_grid: list[float] = [
        min(end_val, start_val + i * ((end_val - start_val) / (num_coarse - 1)))
        for i in range(num_coarse)
    ]

    # Pre-evaluate coarse longitudes for each requested body
    coarse_lons: dict[str, list[float]] = {
        b: [eval_body(t, b)[0] for t in t_grid]
        for b in body_tuple
    }

    rashi_events: list[PlanetaryIngressEvent] = []
    nakshatra_events: list[PlanetaryIngressEvent] = []

    for body_label in body_tuple:
        lons = coarse_lons[body_label]
        fn_lon = lambda t, b=body_label: eval_body(t, b)[0]

        for idx in range(num_coarse - 1):
            t0 = t_grid[idx]
            t1 = t_grid[idx + 1]
            lon0 = lons[idx]
            lon1 = lons[idx + 1]

            # 1. Rashi ingress check
            r0 = int(lon0 // 30.0) % 12
            r1 = int(lon1 // 30.0) % 12
            if r0 != r1:
                delta_lon = _signed_angle_diff(lon1, lon0)
                if delta_lon >= 0.0:
                    boundary_deg = float((r1 * 30) % 360)
                else:
                    boundary_deg = float((r0 * 30) % 360)

                t_ing = _refine_angle_crossing(fn_lon, t0, t1, boundary_deg)
                lon_ing, spd_ing, retro_ing = eval_body(t_ing, body_label)
                if rashi_events and rashi_events[-1].body == body_label and abs(rashi_events[-1].jd_ut - t_ing) < 1e-4:
                    continue
                rashi_events.append(
                    PlanetaryIngressEvent(
                        jd_ut=round(t_ing, 8),
                        iso_utc=_jd_ut_to_iso_utc(t_ing),
                        body=body_label,
                        ingress_type="rashi",
                        from_index=r0,
                        to_index=r1,
                        from_name=RASHI_NAMES[r0],
                        to_name=RASHI_NAMES[r1],
                        boundary_longitude_deg=round(boundary_deg, 8),
                        longitude_deg=round(lon_ing, 8),
                        speed_deg_per_day=round(spd_ing, 8),
                        is_retrograde=retro_ing,
                    )
                )

            # 2. Optional Nakshatra ingress check
            if include_nakshatra_ingresses:
                n0 = min(int(lon0 / NAKSHATRA_SPAN_DEG), 26)
                n1 = min(int(lon1 / NAKSHATRA_SPAN_DEG), 26)
                if n0 != n1:
                    delta_lon = _signed_angle_diff(lon1, lon0)
                    if delta_lon >= 0.0:
                        boundary_deg = (n1 * NAKSHATRA_SPAN_DEG) % 360.0
                    else:
                        boundary_deg = (n0 * NAKSHATRA_SPAN_DEG) % 360.0

                    t_nak = _refine_angle_crossing(fn_lon, t0, t1, boundary_deg)
                    lon_nak, spd_nak, retro_nak = eval_body(t_nak, body_label)
                    if (
                        nakshatra_events
                        and nakshatra_events[-1].body == body_label
                        and abs(nakshatra_events[-1].jd_ut - t_nak) < 1e-4
                    ):
                        continue
                    nakshatra_events.append(
                        PlanetaryIngressEvent(
                            jd_ut=round(t_nak, 8),
                            iso_utc=_jd_ut_to_iso_utc(t_nak),
                            body=body_label,
                            ingress_type="nakshatra",
                            from_index=n0,
                            to_index=n1,
                            from_name=NAKSHATRA_NAMES[n0],
                            to_name=NAKSHATRA_NAMES[n1],
                            boundary_longitude_deg=round(boundary_deg, 8),
                            longitude_deg=round(lon_nak, 8),
                            speed_deg_per_day=round(spd_nak, 8),
                            is_retrograde=retro_nak,
                        )
                    )

    # 3. Synodic planetary aspects among ordered pairs (body_a, body_b)
    aspect_events: list[SynodicAspectEvent] = []
    num_bodies = len(body_tuple)

    for i in range(num_bodies):
        body_a = body_tuple[i]
        lons_a = coarse_lons[body_a]
        for j in range(i + 1, num_bodies):
            body_b = body_tuple[j]
            if {body_a, body_b} == {"Rahu", "Ketu"}:
                # Rahu and Ketu are fixed 180 deg apart with zero relative speed
                continue
            lons_b = coarse_lons[body_b]
            fn_sep = lambda t, ba=body_a, bb=body_b: (eval_body(t, ba)[0] - eval_body(t, bb)[0]) % 360.0

            for idx in range(num_coarse - 1):
                t0 = t_grid[idx]
                t1 = t_grid[idx + 1]
                sep0 = (lons_a[idx] - lons_b[idx]) % 360.0
                sep1 = (lons_a[idx + 1] - lons_b[idx + 1]) % 360.0

                for target_ang in angle_tuple:
                    d0 = _signed_angle_diff(sep0, target_ang)
                    d1 = _signed_angle_diff(sep1, target_ang)
                    if abs(d0) < 90.0 and abs(d1) < 90.0 and abs(d1 - d0) > 1e-9:
                        if (d0 <= 0.0 <= d1) or (d0 >= 0.0 >= d1):
                            t_asp = _refine_angle_crossing(fn_sep, t0, t1, target_ang)
                            la, sa, _ = eval_body(t_asp, body_a)
                            lb, sb, _ = eval_body(t_asp, body_b)
                            sep_exact = (la - lb) % 360.0
                            if (
                                aspect_events
                                and aspect_events[-1].body_a == body_a
                                and aspect_events[-1].body_b == body_b
                                and aspect_events[-1].aspect_angle_deg == target_ang
                                and abs(aspect_events[-1].jd_ut - t_asp) < 1e-3
                            ):
                                continue
                            asp_name = _ASPECT_NAMES.get(target_ang, f"{target_ang:g} deg")
                            aspect_events.append(
                                SynodicAspectEvent(
                                    jd_ut=round(t_asp, 8),
                                    iso_utc=_jd_ut_to_iso_utc(t_asp),
                                    body_a=body_a,
                                    body_b=body_b,
                                    aspect_angle_deg=target_ang,
                                    aspect_name=asp_name,
                                    longitude_a_deg=round(la, 8),
                                    longitude_b_deg=round(lb, 8),
                                    separation_deg=round(sep_exact, 8),
                                    relative_speed_deg_per_day=round(sa - sb, 8),
                                )
                            )

    rashi_events.sort(key=lambda e: (e.jd_ut, e.body, e.ingress_type))
    nakshatra_events.sort(key=lambda e: (e.jd_ut, e.body, e.ingress_type))
    all_ingresses = sorted(
        rashi_events + nakshatra_events,
        key=lambda e: (e.jd_ut, e.body, e.ingress_type),
    )
    aspect_events.sort(key=lambda e: (e.jd_ut, e.body_a, e.body_b, e.aspect_angle_deg))
    combined_events: list[PlanetaryIngressEvent | SynodicAspectEvent] = sorted(
        [*all_ingresses, *aspect_events],
        key=lambda e: e.jd_ut,
    )

    receipt_payload: dict[str, Any] = {
        "schema": "ephemeris-oss.almanac.transit_timeline.v1",
        "version": __version__,
        "start_jd_ut": round(start_val, 8),
        "end_jd_ut": round(end_val, 8),
        "bodies": list(body_tuple),
        "aspect_angles": list(angle_tuple),
        "include_nakshatra_ingresses": bool(include_nakshatra_ingresses),
        "rashi_ingress_count": len(rashi_events),
        "nakshatra_ingress_count": len(nakshatra_events),
        "aspect_count": len(aspect_events),
        "events_digest": [
            {
                "jd_ut": ev.jd_ut,
                "type": ev.event_type,
            }
            for ev in combined_events
        ],
    }

    return TransitTimelineReport(
        start_jd_ut=start_val,
        end_jd_ut=end_val,
        bodies=body_tuple,
        aspect_angles=angle_tuple,
        include_nakshatra_ingresses=bool(include_nakshatra_ingresses),
        ingresses=tuple(all_ingresses),
        rashi_ingresses=tuple(rashi_events),
        nakshatra_ingresses=tuple(nakshatra_events),
        aspects=tuple(aspect_events),
        events=tuple(combined_events),
        receipt=receipt_payload,
        receipt_sha256=canonical_hash(receipt_payload),
    )


__all__ = [
    "BodyTableCell",
    "DEFAULT_ASPECT_ANGLES",
    "DEFAULT_TABLE_BODIES",
    "EphemerisTable",
    "EphemerisTableRow",
    "MAX_EPHEMERIS_TABLE_ROWS",
    "MAX_STEP_DAYS",
    "PlanetaryIngressEvent",
    "STATIONARY_SPEED_THRESHOLD_DEG_PER_DAY",
    "SynodicAspectEvent",
    "TransitTimelineReport",
    "format_dms",
    "generate_ephemeris_table",
    "scan_ingresses_and_aspects",
]
