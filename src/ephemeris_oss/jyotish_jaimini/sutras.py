"""Clean-room Jaimini Upadesha Sutras mathematical engine.

Mathematical formulations follow *Jaimini Upadesha Sutras* (Chapters 1-4) and
*Brihat Parashara Hora Shastra* (Chapters 28-35, 44):
- Rashi Drishti (`j_rashi_drishti`): Sign-based mutual aspect matrix across Movable
  (Chara), Fixed (Sthira), and Dual (Dwiswabhava) signs with adjacent-sign exclusion.
- Argala & Virodhargala (`compute_argala_matrix`): Primary Argala (`2nd`, `4th`, `11th`)
  and Virodhargala obstructions (`12th`, `10th`, `3rd`), Secondary Argala (`5th` vs `9th`),
  Malefic `3rd-house Vipareeta Argala` (3+ natural malefics), and reverse counting for
  Ketu-dominated signs.
- Karakamsa, Swamsa & Jaimini Devatas (`compute_karakamsa_analysis`): Chara Karakas
  (`AK`, `AmK`, `BK`, `MK`, `PK`, `GK`, `DK`), `Karakamsa` (D9 sign of `AK`), `Swamsa`
  (D9 Lagna), `Ishta Devata` (12th from Karakamsa), `Palana Devata` (6th from `AmK` in D9),
  and `Dharma Devata` (9th from Karakamsa).
- Three-Pairs Jaimini Longevity (`compute_jaimini_ayurdaya`): `Lagna + Moon`,
  `Lagna + Hora Lagna`, and `Lagna + 8th/Saturn` modality synthesis into `Alpayu`
  (0-33y), `Madhyayu` (33-66y), and `Purnayu` (66-100y), with `Kakshya Vriddhi` /
  `Kakshya Hrasa` adjustments and `Brahma`, `Rudra`, and `Maheshwara` identification.
- Additional Jaimini Rasi Dashas: `Sthira Dasha` (`7/8/9` years = `96` years total),
  `Shoola Dasha` (`9` years per sign = `108` years total), and `Mandooka Dasha`
  frog-jump progression (`96` years total).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Iterator, Mapping, Sequence, overload

from ..jyotish.dasha import (
    LEVEL_NAMES,
    SAVYA_SIGNS,
    SOLAR_YEAR_DAYS,
    CharaKarakaEntry,
    DashaPeriod,
    DashaTimeline,
    compute_chara_karakas,
    jd_to_iso_utc,
)
from ..jyotish.nakshatra import RASI_NAMES, normalize_degrees
from ..jyotish.vargas import (
    DEBILITATION_SIGNS,
    EXALTATION_SIGNS,
    RASI_LORDS,
    hora_lagna,
    resolve_jaimini_sign_lord,
    varga_sign,
)

MOVABLE_SIGNS: Final[frozenset[int]] = frozenset({0, 3, 6, 9})
FIXED_SIGNS: Final[frozenset[int]] = frozenset({1, 4, 7, 10})
DUAL_SIGNS: Final[frozenset[int]] = frozenset({2, 5, 8, 11})

MODALITY_NAMES: Final[tuple[str, str, str]] = ("Movable", "Fixed", "Dual")

# Adjacent Movable <-> Fixed pairs that do NOT aspect each other under Jaimini Rashi Drishti
ADJACENT_MOVABLE_FIXED_PAIRS: Final[frozenset[frozenset[int]]] = frozenset(
    {
        frozenset({0, 1}),   # Mesha (Aries) <-> Vrishabha (Taurus)
        frozenset({3, 4}),   # Karka (Cancer) <-> Simha (Leo)
        frozenset({6, 7}),   # Tula (Libra) <-> Vrishchika (Scorpio)
        frozenset({9, 10}),  # Makara (Capricorn) <-> Kumbha (Aquarius)
    }
)

# Precomputed canonical Jaimini Rashi Drishti aspect table for signs 0..11
RASHI_DRISHTI_TABLE: Final[tuple[tuple[int, int, int], ...]] = (
    (4, 7, 10),   # 0 Mesha (Movable) -> Simha, Vrishchika, Kumbha (excludes 1 Vrishabha)
    (3, 6, 9),    # 1 Vrishabha (Fixed) -> Karka, Tula, Makara (excludes 0 Mesha)
    (5, 8, 11),   # 2 Mithuna (Dual) -> Kanya, Dhanu, Meena
    (1, 7, 10),   # 3 Karka (Movable) -> Vrishabha, Vrishchika, Kumbha (excludes 4 Simha)
    (0, 6, 9),    # 4 Simha (Fixed) -> Mesha, Tula, Makara (excludes 3 Karka)
    (2, 8, 11),   # 5 Kanya (Dual) -> Mithuna, Dhanu, Meena
    (1, 4, 10),   # 6 Tula (Movable) -> Vrishabha, Simha, Kumbha (excludes 7 Vrishchika)
    (0, 3, 9),    # 7 Vrishchika (Fixed) -> Mesha, Karka, Makara (excludes 6 Tula)
    (2, 5, 11),   # 8 Dhanu (Dual) -> Mithuna, Kanya, Meena
    (1, 4, 7),    # 9 Makara (Movable) -> Vrishabha, Simha, Vrishchika (excludes 10 Kumbha)
    (0, 3, 6),    # 10 Kumbha (Fixed) -> Mesha, Karka, Tula (excludes 9 Makara)
    (2, 5, 8),    # 11 Meena (Dual) -> Mithuna, Kanya, Dhanu
)

NATURAL_MALEFICS: Final[frozenset[str]] = frozenset({"Sun", "Mars", "Saturn", "Rahu", "Ketu"})
NATURAL_BENEFICS: Final[frozenset[str]] = frozenset({"Jupiter", "Venus", "Mercury", "Moon"})

JAIMINI_DEITY_MAP: Final[Mapping[str, str]] = {
    "Sun": "Shiva",
    "Moon": "Gauri",
    "Mars": "Skanda",
    "Mercury": "Vishnu",
    "Jupiter": "Sada Shiva",
    "Venus": "Lakshmi",
    "Saturn": "Narayana",
    "Rahu": "Durga",
    "Ketu": "Ganesha",
}

AYURDAYA_TIERS: Final[tuple[str, str, str]] = ("Alpayu", "Madhyayu", "Purnayu")
AYURDAYA_RANGES_YEARS: Final[Mapping[str, tuple[float, float]]] = {
    "Alpayu": (0.0, 33.0),
    "Madhyayu": (33.0, 66.0),
    "Purnayu": (66.0, 100.0),
}

STHIRA_MODALITY_YEARS: Final[tuple[float, float, float]] = (7.0, 8.0, 9.0)


@dataclass(frozen=True)
class RashiDrishtiEntry:
    """Jaimini Rashi Drishti (sign aspect) descriptor for a single sign (`0..11`).

    Behaves both as a structured dataclass and as a sequence of the 3 aspected
    sign indices (`tuple(entry) == entry.aspected_signs`, `target in entry`).
    """

    sign_index: int
    sign_name: str
    modality: str
    aspected_signs: tuple[int, int, int]
    aspected_sign_names: tuple[str, str, str]
    occupants: tuple[str, ...] = ()
    aspected_by_planets: tuple[str, ...] = ()

    def aspects(self, target_sign: int) -> bool:
        """Return True if this sign aspects `target_sign` under Jaimini Rashi Drishti."""
        return (int(target_sign) % 12) in self.aspected_signs

    def __contains__(self, item: object) -> bool:
        if isinstance(item, int):
            return (item % 12) in self.aspected_signs
        if isinstance(item, str):
            return item in self.aspected_sign_names
        return False

    def __iter__(self) -> Iterator[int]:
        return iter(self.aspected_signs)

    def __len__(self) -> int:
        return len(self.aspected_signs)

    def __getitem__(self, index: int) -> int:
        return self.aspected_signs[index]


@dataclass(frozen=True)
class ArgalaPairEvaluation:
    """Single Argala vs Virodhargala house pair evaluation for a reference sign."""

    name: str
    argala_house_offset: int
    virodha_house_offset: int
    argala_sign: int
    argala_sign_name: str
    virodha_sign: int
    virodha_sign_name: str
    argala_planets: tuple[str, ...]
    virodha_planets: tuple[str, ...]
    argala_strength_deg: float
    virodha_strength_deg: float
    status: str
    net_active: bool


@dataclass(frozen=True)
class SignArgalaSummary:
    """Complete Argala and Virodhargala analysis for a single sign (`0..11`)."""

    sign_index: int
    sign_name: str
    occupants: tuple[str, ...]
    is_ketu_reversed: bool
    direction_step: int
    dhana_2nd_vs_12th: ArgalaPairEvaluation
    sukha_4th_vs_10th: ArgalaPairEvaluation
    labha_11th_vs_3rd: ArgalaPairEvaluation
    putra_5th_vs_9th: ArgalaPairEvaluation
    third_house_sign: int
    third_house_malefics: tuple[str, ...]
    has_vipareeta_argala_3rd: bool
    active_argala_houses: tuple[str, ...]


@dataclass(frozen=True)
class ArgalaMatrix:
    """12-sign Jaimini Argala & Virodhargala matrix."""

    signs: tuple[SignArgalaSummary, ...]
    by_sign: Mapping[int, SignArgalaSummary]

    def __getitem__(self, sign_index: int) -> SignArgalaSummary:
        return self.signs[int(sign_index) % 12]

    def __iter__(self) -> Iterator[SignArgalaSummary]:
        return iter(self.signs)

    def __len__(self) -> int:
        return len(self.signs)


@dataclass(frozen=True)
class DevataIndicator:
    """Jaimini Devata indicator derived from Karakamsa or Amatyakaraka in D9."""

    role: str
    house_from_reference: int
    reference_name: str
    sign_index: int
    sign_name: str
    sign_lord: str
    occupants_in_d9: tuple[str, ...]
    governing_planet: str
    deity_name: str


@dataclass(frozen=True)
class KarakamsaAnalysis:
    """Complete Karakamsa, Swamsa, Chara Karaka, and Jaimini Devata synthesis."""

    scheme: str
    chara_karakas: tuple[CharaKarakaEntry, ...]
    karakas_by_code: Mapping[str, CharaKarakaEntry]
    atmakaraka_planet: str
    amatyakaraka_planet: str
    darakaraka_planet: str
    karakamsa_sign: int
    karakamsa_sign_name: str
    swamsa_sign: int
    swamsa_sign_name: str
    d9_planet_signs: Mapping[str, int]
    ishta_devata: DevataIndicator
    palana_devata: DevataIndicator
    dharma_devata: DevataIndicator


@dataclass(frozen=True)
class AyurdayaPairResult:
    """Longevity evaluation for one classical Jaimini pair."""

    pair_name: str
    factor_a_name: str
    factor_a_sign: int
    factor_a_sign_name: str
    factor_a_modality: str
    factor_b_name: str
    factor_b_sign: int
    factor_b_sign_name: str
    factor_b_modality: str
    category: str
    span_years: tuple[float, float]


@dataclass(frozen=True)
class JaiminiAyurdayaResult:
    """Three-Pairs Jaimini Longevity (`Ayurdaya`) synthesis with Kakshya rules and Tri-Grahas."""

    pair_1_lagna_moon: AyurdayaPairResult
    pair_2_lagna_hora_lagna: AyurdayaPairResult
    pair_3_lagna_eighth_or_saturn: AyurdayaPairResult
    pairs: tuple[AyurdayaPairResult, AyurdayaPairResult, AyurdayaPairResult]
    base_category: str
    tie_breaker_used: bool
    kakshya_type: str
    kakshya_shift: int
    kakshya_reason: str
    final_category: str
    estimated_Range_years: tuple[float, float]
    brahma_graha: str
    rudra_graha: str
    maheshwara_graha: str

    @property
    def estimated_range_years(self) -> tuple[float, float]:
        """Lowercase-normalized alias for `estimated_Range_years`."""
        return self.estimated_Range_years


def sign_modality(sign_index: int) -> str:
    """Return `'Movable'`, `'Fixed'`, or `'Dual'` for a sign index (`0..11`)."""
    return MODALITY_NAMES[(int(sign_index) % 12) % 3]


def _effective_degree_in_sign(planet: str, lon_deg: float) -> float:
    """Return Jaimini effective degree within sign (`30 - deg` for Rahu/Ketu, `deg` otherwise)."""
    norm = normalize_degrees(lon_deg)
    deg_in_sign = norm - (min(int(norm // 30.0), 11) * 30.0)
    if planet.strip().capitalize() in ("Rahu", "Ketu"):
        return 30.0 - deg_in_sign
    return deg_in_sign


def _normalize_planet_map(planet_longitudes: Mapping[str, float] | None) -> dict[str, float]:
    if not planet_longitudes:
        return {}
    return {k.strip().capitalize(): normalize_degrees(v) for k, v in planet_longitudes.items()}


def _occupants_by_sign(norm_lons: Mapping[str, float]) -> dict[int, tuple[str, ...]]:
    buckets: dict[int, list[tuple[float, str]]] = {i: [] for i in range(12)}
    for planet, lon in norm_lons.items():
        s_idx = min(int(lon // 30.0), 11)
        buckets[s_idx].append((_effective_degree_in_sign(planet, lon), planet))
    out: dict[int, tuple[str, ...]] = {}
    for s_idx, items in buckets.items():
        items.sort(key=lambda item: (-item[0], item[1]))
        out[s_idx] = tuple(p for _, p in items)
    return out


@overload
def j_rashi_drishti(
    sign_a: int,
    sign_b: int,
    *,
    planet_longitudes: Mapping[str, float] | None = None,
) -> bool: ...


@overload
def j_rashi_drishti(
    sign_a: int,
    sign_b: None = None,
    *,
    planet_longitudes: Mapping[str, float] | None = None,
) -> RashiDrishtiEntry: ...


@overload
def j_rashi_drishti(
    sign_a: None = None,
    sign_b: None = None,
    *,
    planet_longitudes: Mapping[str, float] | None = None,
) -> tuple[RashiDrishtiEntry, ...]: ...


def j_rashi_drishti(
    sign_a: int | None = None,
    sign_b: int | None = None,
    *,
    planet_longitudes: Mapping[str, float] | None = None,
) -> bool | RashiDrishtiEntry | tuple[RashiDrishtiEntry, ...]:
    """Evaluate Jaimini Rashi Drishti (sign aspects) per *Jaimini Upadesha Sutras* 1.1.25-28.

    - Movable signs (`0, 3, 6, 9`) aspect all Fixed signs (`1, 4, 7, 10`) except the
      immediately adjacent Fixed sign (`0<->1`, `3<->4`, `6<->7`, `9<->10`).
    - Fixed signs (`1, 4, 7, 10`) aspect all Movable signs (`0, 3, 6, 9`) except the
      immediately adjacent Movable sign.
    - Dual signs (`2, 5, 8, 11`) mutually aspect the other three Dual signs.

    Usage:
    - `j_rashi_drishti(sign_a, sign_b)` -> returns `bool` (`True` iff `sign_a` aspects `sign_b`).
    - `j_rashi_drishti(sign_a)` -> returns `RashiDrishtiEntry` for `sign_a` (which also supports
      iteration and `in` membership checks over its 3 aspected sign indices).
    - `j_rashi_drishti()` -> returns `tuple[RashiDrishtiEntry, ...]` for all 12 signs `0..11`.
    """
    if sign_a is not None and sign_b is not None:
        sa = int(sign_a) % 12
        sb = int(sign_b) % 12
        return sb in RASHI_DRISHTI_TABLE[sa]

    norm_lons = _normalize_planet_map(planet_longitudes)
    occ = _occupants_by_sign(norm_lons)

    def _build_entry(s_idx: int) -> RashiDrishtiEntry:
        s = int(s_idx) % 12
        aspected = RASHI_DRISHTI_TABLE[s]
        aspecting_planets: list[str] = []
        for other_sign in aspected:
            aspecting_planets.extend(occ.get(other_sign, ()))
        return RashiDrishtiEntry(
            sign_index=s,
            sign_name=RASI_NAMES[s],
            modality=sign_modality(s),
            aspected_signs=aspected,
            aspected_sign_names=(
                RASI_NAMES[aspected[0]],
                RASI_NAMES[aspected[1]],
                RASI_NAMES[aspected[2]],
            ),
            occupants=occ.get(s, ()),
            aspected_by_planets=tuple(aspecting_planets),
        )

    if sign_a is not None:
        return _build_entry(sign_a)

    return tuple(_build_entry(i) for i in range(12))


def _evaluate_argala_pair(
    *,
    name: str,
    ref_sign: int,
    argala_offset: int,
    virodha_offset: int,
    direction_step: int,
    occ_by_sign: Mapping[int, tuple[str, ...]],
    norm_lons: Mapping[str, float],
) -> ArgalaPairEvaluation:
    arg_sign = (ref_sign + direction_step * argala_offset) % 12
    vir_sign = (ref_sign + direction_step * virodha_offset) % 12
    arg_planets = occ_by_sign.get(arg_sign, ())
    vir_planets = occ_by_sign.get(vir_sign, ())

    arg_deg = max((_effective_degree_in_sign(p, norm_lons[p]) for p in arg_planets), default=0.0)
    vir_deg = max((_effective_degree_in_sign(p, norm_lons[p]) for p in vir_planets), default=0.0)

    n_arg = len(arg_planets)
    n_vir = len(vir_planets)

    if n_arg == 0:
        status = "None"
        net_active = False
    elif n_vir == 0:
        status = "Unobstructed"
        net_active = True
    elif n_arg > n_vir:
        status = "Predominant"
        net_active = True
    elif n_arg < n_vir:
        status = "Obstructed"
        net_active = False
    else:
        if arg_deg >= vir_deg:
            status = "Predominant_By_Degree"
            net_active = True
        else:
            status = "Obstructed_By_Degree"
            net_active = False

    return ArgalaPairEvaluation(
        name=name,
        argala_house_offset=argala_offset + 1,
        virodha_house_offset=virodha_offset + 1,
        argala_sign=arg_sign,
        argala_sign_name=RASI_NAMES[arg_sign],
        virodha_sign=vir_sign,
        virodha_sign_name=RASI_NAMES[vir_sign],
        argala_planets=arg_planets,
        virodha_planets=vir_planets,
        argala_strength_deg=round(arg_deg, 6),
        virodha_strength_deg=round(vir_deg, 6),
        status=status,
        net_active=net_active,
    )


def compute_argala_matrix(
    planet_longitudes: Mapping[str, float],
    *,
    reverse_for_ketu: bool = True,
) -> ArgalaMatrix:
    """Compute Jaimini Argala and Virodhargala across all 12 signs (`0..11`).

    Evaluates for every sign:
    - Primary Argala from `2nd` (Dhana) obstructed by `12th`
    - Primary Argala from `4th` (Sukha) obstructed by `10th`
    - Primary Argala from `11th` (Labha) obstructed by `3rd`
    - Secondary Argala from `5th` (Putra) obstructed by `9th`
    - Special Malefic `3rd-house Vipareeta Argala` when 3 or more natural malefics
      (`Sun`, `Mars`, `Saturn`, `Rahu`, `Ketu`) occupy the 3rd house from the sign.
    - Reverse (anti-zodiacal) house counting for a Ketu-dominated sign when
      `reverse_for_ketu=True` (*Jaimini Upadesha Sutras* 1.1.9).
    """
    norm_lons = _normalize_planet_map(planet_longitudes)
    occ_by_sign = _occupants_by_sign(norm_lons)

    summaries: list[SignArgalaSummary] = []
    by_sign: dict[int, SignArgalaSummary] = {}

    for s_idx in range(12):
        occupants = occ_by_sign.get(s_idx, ())
        # Ketu dominates a sign if Ketu occupies the sign and is the highest-ranking occupant
        # (since occ_by_sign is sorted descending by effective degree in sign, occupants[0] == "Ketu")
        ketu_dominated = bool(reverse_for_ketu and occupants and occupants[0] == "Ketu")
        step = -1 if ketu_dominated else 1

        dhana = _evaluate_argala_pair(
            name="Dhana (2nd vs 12th)",
            ref_sign=s_idx,
            argala_offset=1,
            virodha_offset=11,
            direction_step=step,
            occ_by_sign=occ_by_sign,
            norm_lons=norm_lons,
        )
        sukha = _evaluate_argala_pair(
            name="Sukha (4th vs 10th)",
            ref_sign=s_idx,
            argala_offset=3,
            virodha_offset=9,
            direction_step=step,
            occ_by_sign=occ_by_sign,
            norm_lons=norm_lons,
        )
        labha = _evaluate_argala_pair(
            name="Labha (11th vs 3rd)",
            ref_sign=s_idx,
            argala_offset=10,
            virodha_offset=2,
            direction_step=step,
            occ_by_sign=occ_by_sign,
            norm_lons=norm_lons,
        )
        putra = _evaluate_argala_pair(
            name="Putra (5th vs 9th)",
            ref_sign=s_idx,
            argala_offset=4,
            virodha_offset=8,
            direction_step=step,
            occ_by_sign=occ_by_sign,
            norm_lons=norm_lons,
        )

        third_sign = (s_idx + step * 2) % 12
        third_occ = occ_by_sign.get(third_sign, ())
        third_malefics = tuple(p for p in third_occ if p in NATURAL_MALEFICS)
        has_vipareeta_3rd = len(third_malefics) >= 3

        active_houses: list[str] = []
        if dhana.net_active:
            active_houses.append("2nd")
        if sukha.net_active:
            active_houses.append("4th")
        if labha.net_active:
            active_houses.append("11th")
        if putra.net_active:
            active_houses.append("5th")
        if has_vipareeta_3rd:
            active_houses.append("3rd_Vipareeta")

        summary = SignArgalaSummary(
            sign_index=s_idx,
            sign_name=RASI_NAMES[s_idx],
            occupants=occupants,
            is_ketu_reversed=ketu_dominated,
            direction_step=step,
            dhana_2nd_vs_12th=dhana,
            sukha_4th_vs_10th=sukha,
            labha_11th_vs_3rd=labha,
            putra_5th_vs_9th=putra,
            third_house_sign=third_sign,
            third_house_malefics=third_malefics,
            has_vipareeta_argala_3rd=has_vipareeta_3rd,
            active_argala_houses=tuple(active_houses),
        )
        summaries.append(summary)
        by_sign[s_idx] = summary

    return ArgalaMatrix(signs=tuple(summaries), by_sign=by_sign)


def compute_karakamsa_analysis(
    lagna_lon_deg: float,
    planet_longitudes: Mapping[str, float],
    *,
    scheme: str = "7",
) -> KarakamsaAnalysis:
    """Compute Karakamsa, Swamsa, Chara Karakas (`AK`..`DK`), and Jaimini Devatas.

    - `Karakamsa`: D9 Navamsa sign of `Atmakaraka` (`AK`).
    - `Swamsa`: D9 Navamsa sign of `Janma Lagna`.
    - `Ishta Devata`: 12th sign from `Karakamsa` in D9 (strongest occupant in D9 by
      Chara Karaka degree if occupied, else its Jaimini sign lord).
    - `Palana Devata`: 6th sign from `Amatyakaraka` (`AmK`) in D9.
    - `Dharma Devata`: 9th sign from `Karakamsa` in D9.
    """
    norm_lons = _normalize_planet_map(planet_longitudes)
    karakas = compute_chara_karakas(norm_lons, scheme=scheme)
    by_code = {entry.code: entry for entry in karakas}

    ak = by_code["AK"]
    amk = by_code["AmK"]
    dk = by_code["DK"]

    d9_signs: dict[str, int] = {}
    for planet, lon in norm_lons.items():
        d9_signs[planet] = varga_sign(lon, "D9").sign_index

    d9_occ_buckets: dict[int, list[tuple[float, str]]] = {i: [] for i in range(12)}
    for planet, d9_s in d9_signs.items():
        d9_occ_buckets[d9_s].append((_effective_degree_in_sign(planet, norm_lons[planet]), planet))

    d9_occ: dict[int, tuple[str, ...]] = {}
    for s_idx, items in d9_occ_buckets.items():
        items.sort(key=lambda item: (-item[0], item[1]))
        d9_occ[s_idx] = tuple(p for _, p in items)

    karakamsa_sign = d9_signs[ak.planet]
    swamsa_sign = varga_sign(normalize_degrees(lagna_lon_deg), "D9").sign_index
    amk_d9_sign = d9_signs[amk.planet]

    def _build_devata(role: str, house_num: int, ref_name: str, ref_sign: int) -> DevataIndicator:
        target_sign = (ref_sign + house_num - 1) % 12
        occupants = d9_occ.get(target_sign, ())
        lord = resolve_jaimini_sign_lord(target_sign, norm_lons)
        gov = occupants[0] if occupants else lord
        return DevataIndicator(
            role=role,
            house_from_reference=house_num,
            reference_name=ref_name,
            sign_index=target_sign,
            sign_name=RASI_NAMES[target_sign],
            sign_lord=lord,
            occupants_in_d9=occupants,
            governing_planet=gov,
            deity_name=JAIMINI_DEITY_MAP.get(gov, "Paramatma"),
        )

    ishta = _build_devata("Ishta Devata", 12, "Karakamsa", karakamsa_sign)
    palana = _build_devata("Palana Devata", 6, "Amatyakaraka D9", amk_d9_sign)
    dharma = _build_devata("Dharma Devata", 9, "Karakamsa", karakamsa_sign)

    return KarakamsaAnalysis(
        scheme=str(scheme).strip(),
        chara_karakas=karakas,
        karakas_by_code=by_code,
        atmakaraka_planet=ak.planet,
        amatyakaraka_planet=amk.planet,
        darakaraka_planet=dk.planet,
        karakamsa_sign=karakamsa_sign,
        karakamsa_sign_name=RASI_NAMES[karakamsa_sign],
        swamsa_sign=swamsa_sign,
        swamsa_sign_name=RASI_NAMES[swamsa_sign],
        d9_planet_signs=d9_signs,
        ishta_devata=ishta,
        palana_devata=palana,
        dharma_devata=dharma,
    )


def classify_modality_pair_longevity(sign_a: int, sign_b: int) -> str:
    """Classify a sign pair into `'Purnayu'`, `'Madhyayu'`, or `'Alpayu'` per Jaimini Sutras 2.1.

    Classical modality table:
    - `Movable + Movable` (`0, 0`) OR `Fixed + Dual` (`1, 2` / `2, 1`) -> `'Purnayu'` (66-100 years)
    - `Fixed + Fixed` (`1, 1`) OR `Movable + Dual` (`0, 2` / `2, 0`) -> `'Alpayu'` (0-33 years)
    - `Dual + Dual` (`2, 2`) OR `Movable + Fixed` (`0, 1` / `1, 0`) -> `'Madhyayu'` (33-66 years)
    """
    ma = (int(sign_a) % 12) % 3
    mb = (int(sign_b) % 12) % 3
    pair = (min(ma, mb), max(ma, mb))
    if pair in ((0, 0), (1, 2)):
        return "Purnayu"
    if pair in ((1, 1), (0, 2)):
        return "Alpayu"
    return "Madhyayu"


def _planet_jaimini_strength_key(planet: str, norm_lons: Mapping[str, float]) -> tuple[int, int, float]:
    """Return `(conjunction_count, dignity_rank, effective_degree)` for Jaimini planet strength comparison."""
    p = planet.strip().capitalize()
    if p not in norm_lons:
        return (0, 0, 0.0)
    lon = norm_lons[p]
    s_idx = min(int(lon // 30.0), 11)
    conj = sum(1 for other_p, other_lon in norm_lons.items() if other_p != p and min(int(other_lon // 30.0), 11) == s_idx)
    dignity = 0
    if EXALTATION_SIGNS.get(p) == s_idx:
        dignity = 2
    elif RASI_LORDS[s_idx] == p:
        dignity = 1
    elif DEBILITATION_SIGNS.get(p) == s_idx:
        dignity = -1
    return (conj, dignity, _effective_degree_in_sign(p, lon))


def stronger_sign_jaimini(
    sign_a: int,
    sign_b: int,
    planet_longitudes: Mapping[str, float] | None = None,
) -> int:
    """Return the stronger of two signs (`sign_a` vs `sign_b`) under Jaimini Sutras 1.1 / 2.3 rules.

    Hierarchy:
    1. Sign occupied by more planets in D1.
    2. Sign with higher sum of exalted/own-sign planet dignities.
    3. Sign whose Jaimini lord has stronger placement (`_planet_jaimini_strength_key`).
    4. Natural modality strength (`Dual [2] > Fixed [1] > Movable [0]`).
    """
    sa = int(sign_a) % 12
    sb = int(sign_b) % 12
    if sa == sb:
        return sa
    norm_lons = _normalize_planet_map(planet_longitudes)
    occ = _occupants_by_sign(norm_lons)

    occ_a = occ.get(sa, ())
    occ_b = occ.get(sb, ())
    if len(occ_a) != len(occ_b):
        return sa if len(occ_a) > len(occ_b) else sb

    def _dignity_sum(s_idx: int, planets: Sequence[str]) -> int:
        total = 0
        for p in planets:
            if EXALTATION_SIGNS.get(p) == s_idx:
                total += 2
            elif RASI_LORDS[s_idx] == p:
                total += 1
        return total

    dig_a = _dignity_sum(sa, occ_a)
    dig_b = _dignity_sum(sb, occ_b)
    if dig_a != dig_b:
        return sa if dig_a > dig_b else sb

    lord_a = resolve_jaimini_sign_lord(sa, norm_lons) if norm_lons else RASI_LORDS[sa]
    lord_b = resolve_jaimini_sign_lord(sb, norm_lons) if norm_lons else RASI_LORDS[sb]
    key_a = _planet_jaimini_strength_key(lord_a, norm_lons)
    key_b = _planet_jaimini_strength_key(lord_b, norm_lons)
    if key_a != key_b:
        return sa if key_a > key_b else sb

    mod_a = sa % 3
    mod_b = sb % 3
    if mod_a != mod_b:
        return sa if mod_a > mod_b else sb

    return sa


def compute_jaimini_ayurdaya(
    lagna_lon_deg: float | None = None,
    planet_longitudes: Mapping[str, float] | None = None,
    *,
    hora_lagna_lon_deg: float | None = None,
    hours_since_sunrise: float = 0.0,
    lagna_sign: int | None = None,
    moon_sign: int | None = None,
    hora_lagna_sign: int | None = None,
    eighth_or_saturn_sign: int | None = None,
    apply_kakshya_adjustment: bool = True,
) -> JaiminiAyurdayaResult:
    """Compute Three-Pairs Jaimini Longevity (`Ayurdaya`) per *Jaimini Upadesha Sutras* Ch. 2 Pada 1.

    Evaluates the three classical longevity pairs:
    1. `Lagna Sign` + `Moon Sign`
    2. `Lagna Sign` + `Hora Lagna Sign`
    3. `Lagna Sign` + `8th House (or Saturn) Sign`

    Resolves majority or 3-way split, evaluates `Kakshya Vriddhi` (Jupiter/Venus on Lagna or
    Atmakaraka elevates one tier) and `Kakshya Hrasa` (unrelieved malefic affliction reduces
    one tier), and identifies `Brahma`, `Rudra`, and `Maheshwara` grahas.
    """
    norm_lons = _normalize_planet_map(planet_longitudes)

    if lagna_sign is None:
        if lagna_lon_deg is None:
            raise ValueError("Either lagna_lon_deg or lagna_sign must be provided")
        l_sign = min(int(normalize_degrees(lagna_lon_deg) // 30.0), 11)
    else:
        l_sign = int(lagna_sign) % 12

    if moon_sign is None:
        if "Moon" not in norm_lons:
            raise ValueError("Either moon_sign or planet_longitudes['Moon'] must be provided")
        m_sign = min(int(norm_lons["Moon"] // 30.0), 11)
    else:
        m_sign = int(moon_sign) % 12

    if hora_lagna_sign is None:
        if hora_lagna_lon_deg is not None:
            hl_sign = min(int(normalize_degrees(hora_lagna_lon_deg) // 30.0), 11)
        elif "Sun" in norm_lons:
            hl_deg = hora_lagna(norm_lons["Sun"], hours_since_sunrise)
            hl_sign = min(int(hl_deg // 30.0), 11)
        else:
            hl_sign = l_sign
    else:
        hl_sign = int(hora_lagna_sign) % 12

    if eighth_or_saturn_sign is None:
        if "Saturn" in norm_lons:
            s8_sign = min(int(norm_lons["Saturn"] // 30.0), 11)
            pair3_b_label = "Saturn Sign"
        else:
            s8_sign = (l_sign + 7) % 12
            pair3_b_label = "8th House Sign"
    else:
        s8_sign = int(eighth_or_saturn_sign) % 12
        pair3_b_label = "8th/Saturn Sign"

    def _build_pair(name: str, fa_name: str, sa: int, fb_name: str, sb: int) -> AyurdayaPairResult:
        cat = classify_modality_pair_longevity(sa, sb)
        return AyurdayaPairResult(
            pair_name=name,
            factor_a_name=fa_name,
            factor_a_sign=sa,
            factor_a_sign_name=RASI_NAMES[sa],
            factor_a_modality=sign_modality(sa),
            factor_b_name=fb_name,
            factor_b_sign=sb,
            factor_b_sign_name=RASI_NAMES[sb],
            factor_b_modality=sign_modality(sb),
            category=cat,
            span_years=AYURDAYA_RANGES_YEARS[cat],
        )

    p1 = _build_pair("Pair 1 (Lagna + Moon)", "Lagna", l_sign, "Moon", m_sign)
    p2 = _build_pair("Pair 2 (Lagna + Hora Lagna)", "Lagna", l_sign, "Hora Lagna", hl_sign)
    p3 = _build_pair("Pair 3 (Lagna + 8th/Saturn)", "Lagna", l_sign, pair3_b_label, s8_sign)

    cats = (p1.category, p2.category, p3.category)
    if cats[0] == cats[1] or cats[0] == cats[2]:
        base_cat = cats[0]
        tie_used = False
    elif cats[1] == cats[2]:
        base_cat = cats[1]
        tie_used = False
    else:
        # Classical 3-way split (one Alpayu, one Madhyayu, one Purnayu):
        # Jaimini Sutras 2.1.10 resolves via the Lagna + Hora Lagna pair
        base_cat = p2.category
        tie_used = True

    # Determine Atmakaraka if full 7-planet longitudes are present
    seven_planets = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
    has_all_seven = all(p in norm_lons for p in seven_planets)
    ak_planet = "Sun"
    ak_sign = l_sign
    if has_all_seven:
        karakas = compute_chara_karakas(norm_lons, scheme="7")
        ak_planet = karakas[0].planet
        ak_sign = karakas[0].sign_index

    occ = _occupants_by_sign(norm_lons)
    lagna_occ = set(occ.get(l_sign, ()))
    ak_occ = set(occ.get(ak_sign, ()))
    combined_lagna_ak = lagna_occ | ak_occ

    kakshya_shift = 0
    kakshya_type = "None"
    kakshya_reason = "No Kakshya shift triggered"

    if apply_kakshya_adjustment and norm_lons:
        has_jup_or_ven = bool({"Jupiter", "Venus"} & combined_lagna_ak)
        malefics_on_lagna_ak = ({"Saturn", "Mars", "Rahu", "Ketu"} & combined_lagna_ak) - {ak_planet}
        if has_jup_or_ven:
            kakshya_shift = 1
            kakshya_type = "Kakshya Vriddhi"
            benefics_found = sorted({"Jupiter", "Venus"} & combined_lagna_ak)
            kakshya_reason = f"{'/'.join(benefics_found)} occupying Lagna or Atmakaraka sign elevates longevity by one tier"
        elif len(malefics_on_lagna_ak) >= 2:
            kakshya_shift = -1
            kakshya_type = "Kakshya Hrasa"
            kakshya_reason = "Multiple natural malefics afflicting Lagna/Atmakaraka without Jupiter/Venus relief reduces longevity by one tier"

    base_idx = AYURDAYA_TIERS.index(base_cat)
    final_idx = min(max(base_idx + kakshya_shift, 0), 2)
    final_cat = AYURDAYA_TIERS[final_idx]

    # Identify Rudra, Maheshwara, and Brahma grahas
    lord_8th_from_lagna = resolve_jaimini_sign_lord((l_sign + 7) % 12, norm_lons) if norm_lons else RASI_LORDS[(l_sign + 7) % 12]
    lord_8th_from_7th = resolve_jaimini_sign_lord((l_sign + 1) % 12, norm_lons) if norm_lons else RASI_LORDS[(l_sign + 1) % 12]
    if _planet_jaimini_strength_key(lord_8th_from_lagna, norm_lons) >= _planet_jaimini_strength_key(lord_8th_from_7th, norm_lons):
        rudra_graha = lord_8th_from_lagna
    else:
        rudra_graha = lord_8th_from_7th

    maheshwara_graha = resolve_jaimini_sign_lord((ak_sign + 7) % 12, norm_lons) if norm_lons else RASI_LORDS[(ak_sign + 7) % 12]

    stronger_l_or_7 = stronger_sign_jaimini(l_sign, (l_sign + 6) % 12, norm_lons)
    brahma_candidates: list[str] = []
    for ref_s in (stronger_l_or_7, l_sign, (l_sign + 6) % 12):
        for offset in (5, 7, 11):  # 6th, 8th, 12th houses
            c_lord = resolve_jaimini_sign_lord((ref_s + offset) % 12, norm_lons) if norm_lons else RASI_LORDS[(ref_s + offset) % 12]
            if c_lord not in brahma_candidates:
                brahma_candidates.append(c_lord)

    filtered_brahma = [p for p in brahma_candidates if p not in (rudra_graha, maheshwara_graha, "Rahu", "Ketu")]
    if not filtered_brahma:
        filtered_brahma = brahma_candidates or ["Jupiter"]
    filtered_brahma.sort(key=lambda p: _planet_jaimini_strength_key(p, norm_lons), reverse=True)
    brahma_graha = filtered_brahma[0]

    return JaiminiAyurdayaResult(
        pair_1_lagna_moon=p1,
        pair_2_lagna_hora_lagna=p2,
        pair_3_lagna_eighth_or_saturn=p3,
        pairs=(p1, p2, p3),
        base_category=base_cat,
        tie_breaker_used=tie_used,
        kakshya_type=kakshya_type,
        kakshya_shift=kakshya_shift,
        kakshya_reason=kakshya_reason,
        final_category=final_cat,
        estimated_Range_years=AYURDAYA_RANGES_YEARS[final_cat],
        brahma_graha=brahma_graha,
        rudra_graha=rudra_graha,
        maheshwara_graha=maheshwara_graha,
    )


def _subdivide_rasi_equal(
    *,
    system: str,
    parent_chain: tuple[str, ...],
    parent_sign_idx: int,
    parent_start_jd: float,
    parent_end_jd: float,
    direction_step: int,
    year_days: float,
    current_level: int,
    max_level: int,
) -> tuple[DashaPeriod, ...]:
    """Subdivide a Jaimini Rasi Dasha period into 12 equal sign sub-periods."""
    span_days = parent_end_jd - parent_start_jd
    sub_days = span_days / 12.0
    cursor_jd = parent_start_jd
    out: list[DashaPeriod] = []

    for i in range(12):
        s_idx = (parent_sign_idx + direction_step * i) % 12
        s_name = RASI_NAMES[s_idx]
        s_jd = cursor_jd
        e_jd = parent_end_jd if i == 11 else (cursor_jd + sub_days)
        cursor_jd = e_jd
        chain = parent_chain + (s_name,)

        children: tuple[DashaPeriod, ...] = ()
        if current_level < max_level:
            sub_step = 1 if s_idx in SAVYA_SIGNS else -1
            children = _subdivide_rasi_equal(
                system=system,
                parent_chain=chain,
                parent_sign_idx=s_idx,
                parent_start_jd=s_jd,
                parent_end_jd=e_jd,
                direction_step=sub_step,
                year_days=year_days,
                current_level=current_level + 1,
                max_level=max_level,
            )

        dur_days = e_jd - s_jd
        out.append(
            DashaPeriod(
                system=system,
                level=current_level,
                level_name=LEVEL_NAMES[current_level - 1],
                lord=s_name,
                lords_chain=chain,
                start_jd=s_jd,
                end_jd=e_jd,
                start_iso_utc=jd_to_iso_utc(s_jd),
                end_iso_utc=jd_to_iso_utc(e_jd),
                duration_days=dur_days,
                duration_years=dur_days / year_days,
                associated_planet=RASI_LORDS[s_idx],
                sub_periods=children,
            )
        )
    return tuple(out)


def compute_sthira_dasha(
    lagna_lon_deg: float,
    planet_longitudes: Mapping[str, float] | None = None,
    birth_jd: float = 2451545.0,
    *,
    start_from_brahma: bool = True,
    start_sign: int | None = None,
    year_days: float = SOLAR_YEAR_DAYS,
    max_level: int = 2,
) -> DashaTimeline:
    """Compute Jaimini Sthira Dasha (`7` years Movable, `8` years Fixed, `9` years Dual = `96` years total).

    Starts from the sign occupied by `Brahma` graha (when `start_from_brahma=True` and
    `planet_longitudes` are provided) or from the stronger of `Lagna` and `7th` house.
    """
    if not 1 <= max_level <= 5:
        raise ValueError("max_level must be between 1 and 5")

    norm_lons = _normalize_planet_map(planet_longitudes)
    l_sign = min(int(normalize_degrees(lagna_lon_deg) // 30.0), 11)

    if start_sign is not None:
        opening_sign = int(start_sign) % 12
    elif start_from_brahma and "Moon" in norm_lons:
        ayur = compute_jaimini_ayurdaya(lagna_lon_deg, norm_lons)
        if ayur.brahma_graha in norm_lons:
            opening_sign = min(int(norm_lons[ayur.brahma_graha] // 30.0), 11)
        else:
            opening_sign = stronger_sign_jaimini(l_sign, (l_sign + 6) % 12, norm_lons)
    else:
        opening_sign = stronger_sign_jaimini(l_sign, (l_sign + 6) % 12, norm_lons)

    # Odd signs (Aries=0, Gemini=2, ...) progress zodiacally (+1); even signs progress anti-zodiacally (-1)
    step = 1 if (opening_sign % 2 == 0) else -1

    cursor_jd = float(birth_jd)
    mahadashas: list[DashaPeriod] = []
    first_years = 0.0

    for i in range(12):
        s_idx = (opening_sign + step * i) % 12
        s_name = RASI_NAMES[s_idx]
        yrs = STHIRA_MODALITY_YEARS[s_idx % 3]
        if i == 0:
            first_years = yrs

        span_days = yrs * year_days
        s_jd = cursor_jd
        e_jd = cursor_jd + span_days
        cursor_jd = e_jd
        lord = resolve_jaimini_sign_lord(s_idx, norm_lons) if norm_lons else RASI_LORDS[s_idx]

        children: tuple[DashaPeriod, ...] = ()
        if max_level > 1:
            children = _subdivide_rasi_equal(
                system="Sthira",
                parent_chain=(s_name,),
                parent_sign_idx=s_idx,
                parent_start_jd=s_jd,
                parent_end_jd=e_jd,
                direction_step=1 if (s_idx % 2 == 0) else -1,
                year_days=year_days,
                current_level=2,
                max_level=max_level,
            )

        mahadashas.append(
            DashaPeriod(
                system="Sthira",
                level=1,
                level_name="Mahadasha",
                lord=s_name,
                lords_chain=(s_name,),
                start_jd=s_jd,
                end_jd=e_jd,
                start_iso_utc=jd_to_iso_utc(s_jd),
                end_iso_utc=jd_to_iso_utc(e_jd),
                duration_days=span_days,
                duration_years=yrs,
                associated_planet=lord,
                sub_periods=children,
            )
        )

    return DashaTimeline(
        system="Sthira",
        birth_jd=float(birth_jd),
        birth_iso_utc=jd_to_iso_utc(birth_jd),
        year_days=year_days,
        opening_lord=RASI_NAMES[opening_sign],
        birth_balance_years=first_years,
        birth_balance_days=first_years * year_days,
        mahadashas=tuple(mahadashas),
    )


def compute_shoola_dasha(
    lagna_lon_deg: float,
    planet_longitudes: Mapping[str, float] | None = None,
    birth_jd: float = 2451545.0,
    *,
    start_sign: int | None = None,
    year_days: float = SOLAR_YEAR_DAYS,
    max_level: int = 2,
) -> DashaTimeline:
    """Compute Jaimini Shoola Dasha (`9` years per sign = `108` years total cycle).

    Starts from the stronger of `Lagna` or `7th` house and progresses continuously.
    """
    if not 1 <= max_level <= 5:
        raise ValueError("max_level must be between 1 and 5")

    norm_lons = _normalize_planet_map(planet_longitudes)
    l_sign = min(int(normalize_degrees(lagna_lon_deg) // 30.0), 11)
    opening_sign = int(start_sign) % 12 if start_sign is not None else stronger_sign_jaimini(l_sign, (l_sign + 6) % 12, norm_lons)
    step = 1 if (opening_sign % 2 == 0) else -1

    cursor_jd = float(birth_jd)
    mahadashas: list[DashaPeriod] = []
    yrs = 9.0
    span_days = yrs * year_days

    for i in range(12):
        s_idx = (opening_sign + step * i) % 12
        s_name = RASI_NAMES[s_idx]
        s_jd = cursor_jd
        e_jd = cursor_jd + span_days
        cursor_jd = e_jd
        lord = resolve_jaimini_sign_lord(s_idx, norm_lons) if norm_lons else RASI_LORDS[s_idx]

        children: tuple[DashaPeriod, ...] = ()
        if max_level > 1:
            children = _subdivide_rasi_equal(
                system="Shoola",
                parent_chain=(s_name,),
                parent_sign_idx=s_idx,
                parent_start_jd=s_jd,
                parent_end_jd=e_jd,
                direction_step=1 if (s_idx % 2 == 0) else -1,
                year_days=year_days,
                current_level=2,
                max_level=max_level,
            )

        mahadashas.append(
            DashaPeriod(
                system="Shoola",
                level=1,
                level_name="Mahadasha",
                lord=s_name,
                lords_chain=(s_name,),
                start_jd=s_jd,
                end_jd=e_jd,
                start_iso_utc=jd_to_iso_utc(s_jd),
                end_iso_utc=jd_to_iso_utc(e_jd),
                duration_days=span_days,
                duration_years=yrs,
                associated_planet=lord,
                sub_periods=children,
            )
        )

    return DashaTimeline(
        system="Shoola",
        birth_jd=float(birth_jd),
        birth_iso_utc=jd_to_iso_utc(birth_jd),
        year_days=year_days,
        opening_lord=RASI_NAMES[opening_sign],
        birth_balance_years=yrs,
        birth_balance_days=span_days,
        mahadashas=tuple(mahadashas),
    )


MANDOOKA_JUMP_OFFSETS: Final[tuple[int, ...]] = (0, 2, 4, 6, 8, 10, 1, 3, 5, 7, 9, 11)


def compute_mandooka_dasha(
    lagna_lon_deg: float,
    planet_longitudes: Mapping[str, float] | None = None,
    birth_jd: float = 2451545.0,
    *,
    start_sign: int | None = None,
    year_days: float = SOLAR_YEAR_DAYS,
    max_level: int = 2,
) -> DashaTimeline:
    """Compute Jaimini Mandooka Dasha (frog-jump progression jumping by 3 signs inclusive:
    `1st -> 3rd -> 5th -> 7th -> 9th -> 11th`, then `2nd -> 4th -> 6th -> 8th -> 10th -> 12th`).

    Starts from the stronger of `Lagna` or `7th` house, with modality durations
    (`7` years Movable, `8` years Fixed, `9` years Dual = `96` years total cycle).
    """
    if not 1 <= max_level <= 5:
        raise ValueError("max_level must be between 1 and 5")

    norm_lons = _normalize_planet_map(planet_longitudes)
    l_sign = min(int(normalize_degrees(lagna_lon_deg) // 30.0), 11)
    opening_sign = int(start_sign) % 12 if start_sign is not None else stronger_sign_jaimini(l_sign, (l_sign + 6) % 12, norm_lons)
    step = 1 if (opening_sign % 2 == 0) else -1

    cursor_jd = float(birth_jd)
    mahadashas: list[DashaPeriod] = []
    first_years = 0.0

    for i, offset in enumerate(MANDOOKA_JUMP_OFFSETS):
        s_idx = (opening_sign + step * offset) % 12
        s_name = RASI_NAMES[s_idx]
        yrs = STHIRA_MODALITY_YEARS[s_idx % 3]
        if i == 0:
            first_years = yrs

        span_days = yrs * year_days
        s_jd = cursor_jd
        e_jd = cursor_jd + span_days
        cursor_jd = e_jd
        lord = resolve_jaimini_sign_lord(s_idx, norm_lons) if norm_lons else RASI_LORDS[s_idx]

        children: tuple[DashaPeriod, ...] = ()
        if max_level > 1:
            children = _subdivide_rasi_equal(
                system="Mandooka",
                parent_chain=(s_name,),
                parent_sign_idx=s_idx,
                parent_start_jd=s_jd,
                parent_end_jd=e_jd,
                direction_step=1 if (s_idx % 2 == 0) else -1,
                year_days=year_days,
                current_level=2,
                max_level=max_level,
            )

        mahadashas.append(
            DashaPeriod(
                system="Mandooka",
                level=1,
                level_name="Mahadasha",
                lord=s_name,
                lords_chain=(s_name,),
                start_jd=s_jd,
                end_jd=e_jd,
                start_iso_utc=jd_to_iso_utc(s_jd),
                end_iso_utc=jd_to_iso_utc(e_jd),
                duration_days=span_days,
                duration_years=yrs,
                associated_planet=lord,
                sub_periods=children,
            )
        )

    return DashaTimeline(
        system="Mandooka",
        birth_jd=float(birth_jd),
        birth_iso_utc=jd_to_iso_utc(birth_jd),
        year_days=year_days,
        opening_lord=RASI_NAMES[opening_sign],
        birth_balance_years=first_years,
        birth_balance_days=first_years * year_days,
        mahadashas=tuple(mahadashas),
    )


__all__ = [
    "ADJACENT_MOVABLE_FIXED_PAIRS",
    "AYURDAYA_RANGES_YEARS",
    "AYURDAYA_TIERS",
    "ArgalaMatrix",
    "ArgalaPairEvaluation",
    "AyurdayaPairResult",
    "DUAL_SIGNS",
    "DevataIndicator",
    "FIXED_SIGNS",
    "JAIMINI_DEITY_MAP",
    "JaiminiAyurdayaResult",
    "KarakamsaAnalysis",
    "MANDOOKA_JUMP_OFFSETS",
    "MODALITY_NAMES",
    "MOVABLE_SIGNS",
    "RASHI_DRISHTI_TABLE",
    "RashiDrishtiEntry",
    "STHIRA_MODALITY_YEARS",
    "SignArgalaSummary",
    "classify_modality_pair_longevity",
    "compute_argala_matrix",
    "compute_jaimini_ayurdaya",
    "compute_karakamsa_analysis",
    "compute_mandooka_dasha",
    "compute_shoola_dasha",
    "compute_sthira_dasha",
    "j_rashi_drishti",
    "sign_modality",
    "stronger_sign_jaimini",
]
