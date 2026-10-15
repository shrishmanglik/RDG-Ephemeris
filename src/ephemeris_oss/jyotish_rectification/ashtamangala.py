"""Clean-room Kerala Ashtamangala Prashna, Trisphuta, and Nimitta Engine.

Mathematical formulations follow *Prashna Marga* (Chapters 5, 6, 8) and *Brihat
Parashara Hora Shastra*:
- Ashtamangala Cowrie Remainder Mapping (`1..8` when 108 cowrie shells are divided
  into three heaps for Past [`Bhuta`], Present [`Vartamana`], and Future [`Bhavishya`]):
  - `1`: Sun (East / Purva)
  - `2`: Mars (South-East / Agneya)
  - `3`: Jupiter (South / Dakshina)
  - `4`: Mercury (South-West / Nairritya)
  - `5`: Venus (West / Paschima)
  - `6`: Saturn (North-West / Vayavya)
  - `7`: Moon (North / Uttara)
  - `8`: Rahu (North-East / Ishanya)
- Three-digit Ashtamangala figure (`100 * a + 10 * b + c`), total sum `a + b + c`,
  and parity classification (`Oja` [odd, auspicious dynamic momentum] vs `Yugma`
  [even, steady or obstructed]).
- `Nikshepa Rasi` (`(a + b + c - 1) % 12`), `Chinta Graha` (ruler of the center pile),
  and `Ashtamangala Arudha Sign` (`(a * 10 + b) % 12`).
- Integration with `Trisphuta` (`(lagna_lon_deg + moon_lon_deg + gulika_lon_deg) % 360.0`)
  and `Mrityu Sphuta` (`(7.0 * gulika_lon_deg + sun_lon_deg) % 360.0`), with a
  deterministic SHA-256 calculation receipt.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final, Mapping

from .._version import __version__
from ..engine.receipt import canonical_hash
from ..jyotish.nakshatra import NakshatraPosition, RASI_NAMES, nakshatra_position, normalize_degrees
from ..jyotish.vargas import RASI_LORDS
from ..jyotish_transit.prashna import SphutaPoint

TOTAL_ASHTAMANGALA_SHELLS: Final[int] = 108


@dataclass(frozen=True)
class AshtamangalaGrahaSpec:
    """Classical *Prashna Marga* Ch. 5 mapping of an Ashtamangala remainder (`1..8`)."""

    digit: int
    graha: str
    sanskrit_graha: str
    direction: str
    sanskrit_direction: str
    is_oja: bool
    is_benefic: bool


ASHTAMANGALA_GRAHA_CATALOG: Final[tuple[AshtamangalaGrahaSpec, ...]] = (
    AshtamangalaGrahaSpec(1, "Sun", "Surya", "East", "Purva", True, False),
    AshtamangalaGrahaSpec(2, "Mars", "Kuja", "South-East", "Agneya", False, False),
    AshtamangalaGrahaSpec(3, "Jupiter", "Guru", "South", "Dakshina", True, True),
    AshtamangalaGrahaSpec(4, "Mercury", "Budha", "South-West", "Nairritya", False, True),
    AshtamangalaGrahaSpec(5, "Venus", "Shukra", "West", "Paschima", True, True),
    AshtamangalaGrahaSpec(6, "Saturn", "Shani", "North-West", "Vayavya", False, False),
    AshtamangalaGrahaSpec(7, "Moon", "Chandra", "North", "Uttara", True, True),
    AshtamangalaGrahaSpec(8, "Rahu", "Rahu", "North-East", "Ishanya", False, False),
)

ASHTAMANGALA_GRAHA_BY_DIGIT: Final[Mapping[int, AshtamangalaGrahaSpec]] = {
    spec.digit: spec for spec in ASHTAMANGALA_GRAHA_CATALOG
}

ASHTAMANGALA_GRAHA_NAMES: Final[Mapping[int, str]] = {
    spec.digit: spec.graha for spec in ASHTAMANGALA_GRAHA_CATALOG
}

ASHTAMANGALA_DIRECTIONS: Final[Mapping[int, str]] = {
    spec.digit: spec.direction for spec in ASHTAMANGALA_GRAHA_CATALOG
}


@dataclass(frozen=True)
class AshtamangalaPileState:
    """Evaluated state of one of the three Ashtamangala cowrie heaps (Past, Present, Future)."""

    pile_position: str
    temporal_domain: str
    sanskrit_tense: str
    digit: int
    graha: str
    sanskrit_graha: str
    direction: str
    sanskrit_direction: str
    parity: str
    is_oja: bool
    is_benefic_graha: bool


@dataclass(frozen=True)
class AshtamangalaPrashnaResult:
    """Complete Kerala *Prashna Marga* Ashtamangala Prashna & Sphuta analysis."""

    left_pile: int
    center_pile: int
    right_pile: int
    ashtamangala_number: int
    total_sum: int
    is_odd_sum: bool
    parity_classification: str
    oja_pile_count: int
    yugma_pile_count: int
    past_pile: AshtamangalaPileState
    present_pile: AshtamangalaPileState
    future_pile: AshtamangalaPileState
    bhuta_graha: str
    chinta_graha: str
    bhavishya_graha: str
    chinta_direction: str
    chinta_is_benefic: bool
    nikshepa_rasi: int
    nikshepa_rasi_name: str
    nikshepa_rasi_lord: str
    ashtamangala_arudha_sign: int
    ashtamangala_arudha_sign_name: str
    ashtamangala_arudha_lord: str
    trisphuta_lon_deg: float
    trisphuta_sign_index: int
    trisphuta_sign_name: str
    trisphuta_nakshatra: NakshatraPosition
    trisphuta: SphutaPoint
    mrityu_sphuta_lon_deg: float
    mrityu_sphuta_sign_index: int
    mrityu_sphuta_sign_name: str
    mrityu_sphuta_nakshatra: NakshatraPosition
    mrityu_sphuta: SphutaPoint
    mrityu_afflicts_trisphuta: bool
    mrityu_afflicts_arudha: bool
    nimitta_verdict: str
    receipt: Mapping[str, Any]
    receipt_sha256: str


def _validate_pile_digit(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer in 1..8, got {value!r}")
    if not 1 <= value <= 8:
        raise ValueError(f"{name} must be in 1..8, got {value}")
    return value


def normalize_cowrie_heap(raw_count: int) -> int:
    """Reduce a positive cowrie shell heap count modulo 8 into `1..8` (where 0 mod 8 becomes 8)."""
    if isinstance(raw_count, bool) or not isinstance(raw_count, int) or raw_count < 1:
        raise ValueError(f"raw_count must be a positive integer >= 1, got {raw_count!r}")
    return ((raw_count - 1) % 8) + 1


def divide_108_cowries(left_raw: int, center_raw: int, right_raw: int) -> tuple[int, int, int]:
    """Validate a three-heap partition of 108 cowrie shells and return `(left_pile, center_pile, right_pile)` in `1..8`."""
    for label, val in (("left_raw", left_raw), ("center_raw", center_raw), ("right_raw", right_raw)):
        if isinstance(val, bool) or not isinstance(val, int) or val < 1:
            raise ValueError(f"{label} must be a positive integer >= 1, got {val!r}")
    if left_raw + center_raw + right_raw != TOTAL_ASHTAMANGALA_SHELLS:
        raise ValueError(
            f"The three cowrie heaps must sum to {TOTAL_ASHTAMANGALA_SHELLS}, got "
            f"{left_raw} + {center_raw} + {right_raw} = {left_raw + center_raw + right_raw}"
        )
    return (
        normalize_cowrie_heap(left_raw),
        normalize_cowrie_heap(center_raw),
        normalize_cowrie_heap(right_raw),
    )


def _build_pile_state(
    pile_position: str,
    temporal_domain: str,
    sanskrit_tense: str,
    digit: int,
) -> AshtamangalaPileState:
    spec = ASHTAMANGALA_GRAHA_BY_DIGIT[digit]
    return AshtamangalaPileState(
        pile_position=pile_position,
        temporal_domain=temporal_domain,
        sanskrit_tense=sanskrit_tense,
        digit=digit,
        graha=spec.graha,
        sanskrit_graha=spec.sanskrit_graha,
        direction=spec.direction,
        sanskrit_direction=spec.sanskrit_direction,
        parity="Oja" if spec.is_oja else "Yugma",
        is_oja=spec.is_oja,
        is_benefic_graha=spec.is_benefic,
    )


def _build_sphuta_point(name: str, lon_deg: float) -> SphutaPoint:
    lon = normalize_degrees(lon_deg)
    s_idx = min(int(lon // 30.0), 11)
    return SphutaPoint(
        name=name,
        longitude_deg=lon,
        sign_index=s_idx,
        sign_name=RASI_NAMES[s_idx],
        degree_in_sign=lon - s_idx * 30.0,
        nakshatra=nakshatra_position(lon),
    )


def compute_ashtamangala_prashna(
    left_pile: int,
    center_pile: int,
    right_pile: int,
    *,
    lagna_lon_deg: float = 0.0,
    sun_lon_deg: float = 0.0,
    moon_lon_deg: float = 0.0,
    gulika_lon_deg: float = 0.0,
) -> AshtamangalaPrashnaResult:
    """Compute a Kerala *Prashna Marga* (Chapter 5) Ashtamangala Prashna reading.

    Parameters
    ----------
    left_pile : int
        Remainder (`1..8`) of the left cowrie heap representing Past (`Bhuta`).
    center_pile : int
        Remainder (`1..8`) of the center cowrie heap representing Present (`Vartamana`).
    right_pile : int
        Remainder (`1..8`) of the right cowrie heap representing Future (`Bhavishya`).
    lagna_lon_deg, sun_lon_deg, moon_lon_deg, gulika_lon_deg : float
        Sidereal longitudes in degrees (`0..360`) for Trisphuta and Mrityu Sphuta integration.
    """
    a = _validate_pile_digit(left_pile, "left_pile")
    b = _validate_pile_digit(center_pile, "center_pile")
    c = _validate_pile_digit(right_pile, "right_pile")

    ashtamangala_num = 100 * a + 10 * b + c
    total_sum = a + b + c
    is_odd_sum = (total_sum % 2) == 1
    parity_cls = "Oja" if is_odd_sum else "Yugma"

    past_state = _build_pile_state("left", "Past", "Bhuta", a)
    present_state = _build_pile_state("center", "Present", "Vartamana", b)
    future_state = _build_pile_state("right", "Future", "Bhavishya", c)

    oja_count = sum(1 for st in (past_state, present_state, future_state) if st.is_oja)
    yugma_count = 3 - oja_count

    nikshepa_rasi = (total_sum - 1) % 12
    nikshepa_name = RASI_NAMES[nikshepa_rasi]
    nikshepa_lord = RASI_LORDS[nikshepa_rasi]

    arudha_sign = (a * 10 + b) % 12
    arudha_name = RASI_NAMES[arudha_sign]
    arudha_lord = RASI_LORDS[arudha_sign]

    l_lon = normalize_degrees(lagna_lon_deg)
    s_lon = normalize_degrees(sun_lon_deg)
    m_lon = normalize_degrees(moon_lon_deg)
    g_lon = normalize_degrees(gulika_lon_deg)

    trisphuta_lon = normalize_degrees(l_lon + m_lon + g_lon)
    mrityu_lon = normalize_degrees(7.0 * g_lon + s_lon)

    trisphuta_pt = _build_sphuta_point("Trisphuta", trisphuta_lon)
    mrityu_pt = _build_sphuta_point("Mrityu Sphuta", mrityu_lon)

    mrityu_afflicts_tri = (
        mrityu_pt.sign_index == trisphuta_pt.sign_index
        or mrityu_pt.nakshatra.index == trisphuta_pt.nakshatra.index
    )
    mrityu_afflicts_arudha = mrityu_pt.sign_index == arudha_sign

    if is_odd_sum and present_state.is_benefic_graha and not mrityu_afflicts_tri:
        verdict = "Shubha (Auspicious Oja momentum with benefic Chinta Graha)"
    elif is_odd_sum and not mrityu_afflicts_tri:
        verdict = "Madhyama-Shubha (Dynamic Oja total with mixed planetary intensity)"
    elif present_state.is_benefic_graha and not mrityu_afflicts_tri:
        verdict = "Madhyama (Steady Yugma total supported by benefic Chinta Graha)"
    else:
        verdict = "Krichhra (Obstructed Yugma or Mrityu Sphuta affliction requiring remedial care)"

    receipt = {
        "module": "ephemeris_oss.jyotish_rectification.ashtamangala",
        "version": __version__,
        "left_pile": a,
        "center_pile": b,
        "right_pile": c,
        "ashtamangala_number": ashtamangala_num,
        "total_sum": total_sum,
        "parity_classification": parity_cls,
        "bhuta_graha": past_state.graha,
        "chinta_graha": present_state.graha,
        "bhavishya_graha": future_state.graha,
        "chinta_direction": present_state.direction,
        "nikshepa_rasi": nikshepa_rasi,
        "nikshepa_rasi_name": nikshepa_name,
        "ashtamangala_arudha_sign": arudha_sign,
        "ashtamangala_arudha_sign_name": arudha_name,
        "trisphuta_lon_deg": round(trisphuta_lon, 8),
        "mrityu_sphuta_lon_deg": round(mrityu_lon, 8),
    }
    receipt_sha256 = canonical_hash(receipt)

    return AshtamangalaPrashnaResult(
        left_pile=a,
        center_pile=b,
        right_pile=c,
        ashtamangala_number=ashtamangala_num,
        total_sum=total_sum,
        is_odd_sum=is_odd_sum,
        parity_classification=parity_cls,
        oja_pile_count=oja_count,
        yugma_pile_count=yugma_count,
        past_pile=past_state,
        present_pile=present_state,
        future_pile=future_state,
        bhuta_graha=past_state.graha,
        chinta_graha=present_state.graha,
        bhavishya_graha=future_state.graha,
        chinta_direction=present_state.direction,
        chinta_is_benefic=present_state.is_benefic_graha,
        nikshepa_rasi=nikshepa_rasi,
        nikshepa_rasi_name=nikshepa_name,
        nikshepa_rasi_lord=nikshepa_lord,
        ashtamangala_arudha_sign=arudha_sign,
        ashtamangala_arudha_sign_name=arudha_name,
        ashtamangala_arudha_lord=arudha_lord,
        trisphuta_lon_deg=trisphuta_lon,
        trisphuta_sign_index=trisphuta_pt.sign_index,
        trisphuta_sign_name=trisphuta_pt.sign_name,
        trisphuta_nakshatra=trisphuta_pt.nakshatra,
        trisphuta=trisphuta_pt,
        mrityu_sphuta_lon_deg=mrityu_lon,
        mrityu_sphuta_sign_index=mrityu_pt.sign_index,
        mrityu_sphuta_sign_name=mrityu_pt.sign_name,
        mrityu_sphuta_nakshatra=mrityu_pt.nakshatra,
        mrityu_sphuta=mrityu_pt,
        mrityu_afflicts_trisphuta=mrityu_afflicts_tri,
        mrityu_afflicts_arudha=mrityu_afflicts_arudha,
        nimitta_verdict=verdict,
        receipt=receipt,
        receipt_sha256=receipt_sha256,
    )


__all__ = [
    "ASHTAMANGALA_DIRECTIONS",
    "ASHTAMANGALA_GRAHA_BY_DIGIT",
    "ASHTAMANGALA_GRAHA_CATALOG",
    "ASHTAMANGALA_GRAHA_NAMES",
    "AshtamangalaGrahaSpec",
    "AshtamangalaPileState",
    "AshtamangalaPrashnaResult",
    "TOTAL_ASHTAMANGALA_SHELLS",
    "compute_ashtamangala_prashna",
    "divide_108_cowries",
    "normalize_cowrie_heap",
]
