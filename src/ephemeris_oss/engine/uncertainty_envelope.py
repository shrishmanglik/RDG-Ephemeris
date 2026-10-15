"""Scientific Ephemeris Uncertainty & Birth-Time Boundary Margin Calculator.

Implements the Published Uncertainty & Boundary Sensitivity Envelope for
high-precision astronomical and jyotisha computations, grounded in:
- NASA JPL DE440 / DE441 (*Folkner et al.* / *Park et al.*, AJ 161:105, 2021)
- IAU SOFA / IERS Earth Orientation Parameters (`finals2000A.all`, 1962-2026)
- Espenak & Meeus (*Five Millennium Canon of Solar Eclipses*, NASA TP-2006-214141)
  piecewise historical Delta-T uncertainty model.

Decomposes 95% positional uncertainty (`total_uncertainty_arcsec`) into:
1. `ephemeris_model_spread_arcsec`: Secular numerical integration spread between
   DE440/DE441/INPOP21a (`0.0005"` near J2000 growing quadratically as `0.002" * T^2`
   for planets/Sun, or `0.015"` base for the Moon).
2. `compact_fit_residual_arcsec`: `0.0` when `kernel_mode == "de440"`, or the
   measured Chebyshev polynomial fit ceiling (`0.00060"` Sun, `0.01418"` Moon,
   `0.00182"` inner planets, `0.00026"` outer planets) when `kernel_mode == "compact"`.
3. `delta_t_propagated_arcsec`: Outside the IERS observed window (`< 1962` or `> 2026`),
   propagates Espenak-Meeus Delta-T uncertainty into ecliptic longitude via
   `|lambda_dot_body| * sigma_DeltaT / 86400`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final, Iterator, Mapping

from .earth_orientation import estimate_delta_t
from .receipt import canonical_hash

J2000_JD_TT: Final[float] = 2451545.0
JULIAN_CENTURY_DAYS: Final[float] = 36525.0
TROPICAL_YEAR_DAYS: Final[float] = 365.2425
SECONDS_PER_DAY: Final[float] = 86400.0
ARCSEC_PER_DEG: Final[float] = 3600.0

IERS_OBSERVED_START_YEAR: Final[float] = 1962.0
IERS_OBSERVED_END_YEAR: Final[float] = 2026.0

# Compact Chebyshev fit residual ceilings (in arcseconds) against full JPL DE440
COMPACT_RESIDUAL_CEILINGS_ARCSEC: Final[Mapping[str, float]] = {
    "sun": 0.00060,
    "moon": 0.01418,
    "mercury": 0.00182,
    "venus": 0.00182,
    "mars": 0.00182,
    "rahu": 0.00182,
    "ketu": 0.00182,
    "jupiter": 0.00026,
    "saturn": 0.00026,
    "uranus": 0.00026,
    "neptune": 0.00026,
    "pluto": 0.00026,
}

# Canonical mean daily angular speeds |d(lambda)/dt| in degrees/day for Delta-T propagation
MEAN_DAILY_SPEED_DEG_PER_DAY: Final[Mapping[str, float]] = {
    "sun": 0.98564736,
    "moon": 13.17639648,
    "mercury": 1.3833,
    "venus": 1.2000,
    "mars": 0.5240,
    "jupiter": 0.0831,
    "saturn": 0.0335,
    "rahu": 0.0529539,
    "ketu": 0.0529539,
    "uranus": 0.0117,
    "neptune": 0.0060,
    "pluto": 0.0040,
    "ascendant": 360.0,
    "lagna": 360.0,
}

# Classical divisional and nakshatra boundary spans in degrees
BOUNDARY_STEPS_DEG: Final[tuple[tuple[str, float], ...]] = (
    ("D1", 30.0),                # 30 deg 00 min (Rasi)
    ("Nakshatra", 360.0 / 27.0), # 13 deg 20 min (800 arcmin)
    ("Pada", 360.0 / 108.0),     # 3 deg 20 min (200 arcmin)
    ("D9", 30.0 / 9.0),          # 3 deg 20 min (Navamsa)
    ("D10", 3.0),                # 3 deg 00 min (Dasamsa)
    ("D60", 0.5),                # 0 deg 30 min (Shashtiamsa)
)


@dataclass(frozen=True)
class PositionUncertaintyEnvelope:
    """Decomposed 95% positional uncertainty budget in arcseconds with SHA-256 receipt."""

    jd_tt: float
    body: str
    kernel_mode: str
    utc_year: float
    julian_centuries_from_j2000: float
    ephemeris_model_spread_arcsec: float
    compact_fit_residual_arcsec: float
    delta_t_uncertainty_seconds: float
    delta_t_propagated_arcsec: float
    quadrature_uncertainty_arcsec: float
    total_uncertainty_arcsec: float
    confidence_level: float
    iers_observed_window: bool
    receipt_sha256: str


@dataclass(frozen=True)
class BoundaryMarginEntry:
    """Angular and birth-time margin to the nearest boundary of a single division."""

    division: str
    step_deg: float
    current_index: int
    distance_to_lower_arcsec: float
    distance_to_upper_arcsec: float
    margin_arcsec: float
    birth_time_margin_seconds: float
    nearest_direction: str
    is_cuspal_borderline: bool


@dataclass(frozen=True)
class BoundarySensitivityEnvelope:
    """Complete boundary sensitivity envelope across D1, Nakshatra, Pada, D9, D10, and D60."""

    sidereal_lon_deg: float
    daily_speed_deg_per_day: float
    is_ascendant: bool
    d1: BoundaryMarginEntry
    nakshatra: BoundaryMarginEntry
    pada: BoundaryMarginEntry
    d9: BoundaryMarginEntry
    d10: BoundaryMarginEntry
    d60: BoundaryMarginEntry
    boundaries: Mapping[str, BoundaryMarginEntry]
    nearest_boundary_name: str
    margin_arcsec: float
    birth_time_margin_seconds: float
    borderline_divisions: tuple[str, ...]
    is_cuspal_borderline: bool
    cuspal_threshold_seconds: float
    receipt_sha256: str

    def __getitem__(self, division: str) -> BoundaryMarginEntry:
        return self.boundaries[division]

    def __contains__(self, division: object) -> bool:
        return division in self.boundaries

    def __iter__(self) -> Iterator[ str]:
        return iter(self.boundaries)


def _normalize_body_key(body: str) -> str:
    b = str(body).strip().lower()
    aliases = {
        "10": "sun",
        "301": "moon",
        "199": "mercury",
        "1": "mercury",
        "299": "venus",
        "2": "venus",
        "4": "mars",
        "5": "jupiter",
        "6": "saturn",
        "7": "uranus",
        "8": "neptune",
        "9": "pluto",
        "mean_node": "rahu",
        "true_node": "rahu",
    }
    return aliases.get(b, b)


def compute_position_uncertainty(
    jd_tt: float,
    body: str,
    kernel_mode: str = "de440",
    utc_year: float | None = None,
    *,
    daily_speed_deg_per_day: float | None = None,
) -> PositionUncertaintyEnvelope:
    """Compute the 95% angular position uncertainty envelope (in arcseconds) for `body` at `jd_tt`.

    Decomposes `total_uncertainty_arcsec` into:
    1. `ephemeris_model_spread_arcsec`: Secular numerical integration spread between
       DE440/DE441/INPOP21a models (`0.0005" + 0.002" * T^2` for planets/Sun, or
       `0.015" + 0.002" * T^2` for the Moon).
    2. `compact_fit_residual_arcsec`: `0.0` when `kernel_mode == "de440"`, or the
       measured compact Chebyshev ceiling (`0.00060"` Sun, `0.01418"` Moon,
       `0.00182"` inner planets, `0.00026"` outer planets) when `kernel_mode == "compact"`.
    3. `delta_t_propagated_arcsec`: Outside the IERS observed window (`< 1962` or `> 2026`),
       propagates Espenak-Meeus `sigma_DeltaT(Y)` into ecliptic longitude via
       `|lambda_dot_body| * sigma_DeltaT / 86400`.
    """
    jd_val = float(jd_tt)
    if not math.isfinite(jd_val):
        raise ValueError("jd_tt must be finite")

    body_key = _normalize_body_key(body)
    if body_key not in MEAN_DAILY_SPEED_DEG_PER_DAY:
        raise ValueError(f"Unsupported astronomical body {body!r}")

    mode_norm = str(kernel_mode).strip().lower()
    if mode_norm in ("de440", "de441", "bsp", "full"):
        canonical_mode = "de440"
    elif mode_norm in ("compact", "compact-chebyshev-de440", "compact_de440"):
        canonical_mode = "compact"
    else:
        raise ValueError(f"Unsupported kernel_mode {kernel_mode!r}; expected 'de440' or 'compact'")

    t_centuries = (jd_val - J2000_JD_TT) / JULIAN_CENTURY_DAYS
    base_spread = 0.015 if body_key == "moon" else 0.0005
    ephemeris_spread = base_spread + 0.002 * (t_centuries ** 2)

    if canonical_mode == "de440":
        compact_residual = 0.0
    else:
        compact_residual = float(COMPACT_RESIDUAL_CEILINGS_ARCSEC.get(body_key, 0.00182))

    if utc_year is not None:
        eff_year = float(utc_year)
    else:
        eff_year = 2000.0 + (jd_val - J2000_JD_TT) / TROPICAL_YEAR_DAYS

    in_iers_window = IERS_OBSERVED_START_YEAR <= eff_year <= IERS_OBSERVED_END_YEAR
    if in_iers_window:
        sigma_dt_sec = 0.0
        dt_prop_arcsec = 0.0
    else:
        clamped_year = min(max(eff_year, -1999.0), 3000.0)
        dt_est = estimate_delta_t(clamped_year)
        sigma_dt_sec = float(dt_est.uncertainty_seconds or 0.0)
        speed_deg = (
            abs(float(daily_speed_deg_per_day))
            if daily_speed_deg_per_day is not None
            else MEAN_DAILY_SPEED_DEG_PER_DAY[body_key]
        )
        lambda_dot_arcsec_per_day = speed_deg * ARCSEC_PER_DEG
        dt_prop_arcsec = (lambda_dot_arcsec_per_day * sigma_dt_sec) / SECONDS_PER_DAY

    quad_arcsec = math.sqrt(
        ephemeris_spread ** 2 + compact_residual ** 2 + dt_prop_arcsec ** 2
    )
    total_arcsec = ephemeris_spread + compact_residual + dt_prop_arcsec

    receipt_payload = {
        "schema": "position-uncertainty-envelope-v1",
        "jd_tt": round(jd_val, 9),
        "body": body_key,
        "kernel_mode": canonical_mode,
        "utc_year": round(eff_year, 6),
        "ephemeris_model_spread_arcsec": round(ephemeris_spread, 9),
        "compact_fit_residual_arcsec": round(compact_residual, 9),
        "delta_t_propagated_arcsec": round(dt_prop_arcsec, 9),
        "total_uncertainty_arcsec": round(total_arcsec, 9),
    }

    return PositionUncertaintyEnvelope(
        jd_tt=jd_val,
        body=body_key,
        kernel_mode=canonical_mode,
        utc_year=eff_year,
        julian_centuries_from_j2000=t_centuries,
        ephemeris_model_spread_arcsec=ephemeris_spread,
        compact_fit_residual_arcsec=compact_residual,
        delta_t_uncertainty_seconds=sigma_dt_sec,
        delta_t_propagated_arcsec=dt_prop_arcsec,
        quadrature_uncertainty_arcsec=quad_arcsec,
        total_uncertainty_arcsec=total_arcsec,
        confidence_level=0.95,
        iers_observed_window=in_iers_window,
        receipt_sha256=canonical_hash(receipt_payload),
    )


def compute_boundary_sensitivity(
    sidereal_lon_deg: float,
    daily_speed_deg_per_day: float = 1.0,
    is_ascendant: bool = False,
    *,
    cuspal_threshold_seconds: float = 60.0,
) -> BoundarySensitivityEnvelope:
    """Compute angular margin (in arcseconds) and birth-time margin (in seconds)
    to the nearest boundary of `D1`, `Nakshatra`, `Pada`, `D9`, `D10`, and `D60`.

    - When `is_ascendant=True` and `daily_speed_deg_per_day == 1.0`, the diurnal
      horizon rotation rate of `360.0` deg/day (`15.0` arcsec/sec) is used automatically.
    - Flags `is_cuspal_borderline=True` whenever `birth_time_margin_seconds < cuspal_threshold_seconds`
      (default `60.0` seconds), accompanied by a deterministic `receipt_sha256`.
    """
    if not math.isfinite(sidereal_lon_deg):
        raise ValueError("sidereal_lon_deg must be finite")

    lon = float(sidereal_lon_deg) % 360.0
    if lon < 0.0 or lon >= 360.0:
        lon = 0.0

    if is_ascendant and daily_speed_deg_per_day == 1.0:
        eff_speed_deg_per_day = 360.0
    else:
        eff_speed_deg_per_day = abs(float(daily_speed_deg_per_day))

    if not math.isfinite(eff_speed_deg_per_day) or eff_speed_deg_per_day <= 0.0:
        raise ValueError("daily_speed_deg_per_day must be finite and positive")

    speed_arcsec_per_sec = (eff_speed_deg_per_day * ARCSEC_PER_DEG) / SECONDS_PER_DAY
    threshold_sec = float(cuspal_threshold_seconds)

    entries: dict[str, BoundaryMarginEntry] = {}
    for div_name, step_deg in BOUNDARY_STEPS_DEG:
        total_cells = int(round(360.0 / step_deg))
        scaled = lon / step_deg
        idx = min(max(int(math.floor(scaled + 1e-15)), 0), total_cells - 1)
        offset_deg = lon - idx * step_deg
        if offset_deg < 0.0:
            offset_deg = 0.0
        elif offset_deg > step_deg:
            offset_deg = step_deg

        lower_deg = offset_deg
        upper_deg = step_deg - offset_deg
        lower_arcsec = lower_deg * ARCSEC_PER_DEG
        upper_arcsec = upper_deg * ARCSEC_PER_DEG

        if lower_arcsec <= upper_arcsec:
            margin_arcsec = lower_arcsec
            nearest_dir = "lower"
        else:
            margin_arcsec = upper_arcsec
            nearest_dir = "upper"

        time_margin_sec = margin_arcsec / speed_arcsec_per_sec
        borderline = bool(time_margin_sec < threshold_sec)

        entries[div_name] = BoundaryMarginEntry(
            division=div_name,
            step_deg=step_deg,
            current_index=idx,
            distance_to_lower_arcsec=lower_arcsec,
            distance_to_upper_arcsec=upper_arcsec,
            margin_arcsec=margin_arcsec,
            birth_time_margin_seconds=time_margin_sec,
            nearest_direction=nearest_dir,
            is_cuspal_borderline=borderline,
        )

    tightest_entry = min(entries.values(), key=lambda item: (item.birth_time_margin_seconds, item.step_deg))
    borderline_divs = tuple(
        div_name for div_name, _ in BOUNDARY_STEPS_DEG if entries[div_name].is_cuspal_borderline
    )
    overall_borderline = len(borderline_divs) > 0

    receipt_payload = {
        "schema": "boundary-sensitivity-envelope-v1",
        "sidereal_lon_deg": round(lon, 9),
        "daily_speed_deg_per_day": round(eff_speed_deg_per_day, 9),
        "is_ascendant": bool(is_ascendant),
        "cuspal_threshold_seconds": round(threshold_sec, 6),
        "nearest_boundary_name": tightest_entry.division,
        "margin_arcsec": round(tightest_entry.margin_arcsec, 6),
        "birth_time_margin_seconds": round(tightest_entry.birth_time_margin_seconds, 6),
        "is_cuspal_borderline": overall_borderline,
        "borderline_divisions": list(borderline_divs),
    }

    return BoundarySensitivityEnvelope(
        sidereal_lon_deg=lon,
        daily_speed_deg_per_day=eff_speed_deg_per_day,
        is_ascendant=bool(is_ascendant),
        d1=entries["D1"],
        nakshatra=entries["Nakshatra"],
        pada=entries["Pada"],
        d9=entries["D9"],
        d10=entries["D10"],
        d60=entries["D60"],
        boundaries=entries,
        nearest_boundary_name=tightest_entry.division,
        margin_arcsec=tightest_entry.margin_arcsec,
        birth_time_margin_seconds=tightest_entry.birth_time_margin_seconds,
        borderline_divisions=borderline_divs,
        is_cuspal_borderline=overall_borderline,
        cuspal_threshold_seconds=threshold_sec,
        receipt_sha256=canonical_hash(receipt_payload),
    )


__all__ = [
    "BOUNDARY_STEPS_DEG",
    "BoundaryMarginEntry",
    "BoundarySensitivityEnvelope",
    "COMPACT_RESIDUAL_CEILINGS_ARCSEC",
    "IERS_OBSERVED_END_YEAR",
    "IERS_OBSERVED_START_YEAR",
    "MEAN_DAILY_SPEED_DEG_PER_DAY",
    "PositionUncertaintyEnvelope",
    "compute_boundary_sensitivity",
    "compute_position_uncertainty",
]
