"""Clean-room Ashtakavarga Kakshya (8-Fold Transit Timing), Sarvatobhadra 9x9 Chakra, and Kota Chakra Engine.

Mathematical formulations follow *Brihat Parashara Hora Shastra*, *Phaladeepika*,
*Narapati Jayacharya Sarvatobhadra*, and *Uttara Kalamrita*:
- Prastara Ashtakavarga and Kakshya Transit Timing:
  - Every 30-degree sign is subdivided into 8 equal Kakshyas of 3 deg 45 min (3.75 deg)
    ruled in invariable order of orbital period:
    `0: Saturn, 1: Jupiter, 2: Mars, 3: Sun, 4: Venus, 5: Mercury, 6: Moon, 7: Lagna`.
  - Evaluates whether a transiting planet at any sidereal longitude is traversing a
    bindu-bearing (benefic) or bindu-less (barren) Kakshya.
- Sarvatobhadra Chakra (9x9 = 81-Cell Vedic Transit Grid):
  - 28 Nakshatras (including Abhijit) along the outer perimeter (7 per cardinal side),
    16 Vowels (Svaras) along the two main diagonals, 20 Consonants (Aksharas) in the
    second ring, 12 Rasis in the third ring, and 5 Tithi groups (Nanda, Bhadra, Jaya,
    Rikta, Purna) in the central cross (28 + 16 + 20 + 12 + 5 = 81 cells).
  - 3-Way Sarvatobhadra Vedha (Front, Left, Right rays) with directional motion rules
    and natal Janma Nakshatra / Rasi / Tithi / Akshara affliction and benefic checks.
- Kota Chakra (28-Nakshatra Fortress Protection & Vulnerability Grid):
  - Partitions the 28 Nakshatras from natal Janma Nakshatra into the 4 concentric
    fortress zones (`Stambha` 4, `Madhya` 8, `Prakaara` 8, `Bahya` 8) and into
    `Pravesha` (diagonal entry/vulnerability) vs `Nirgamana` (cardinal exit/relief) paths,
    with `Kota Swami` and `Kota Paala` identification.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final, Mapping

from .._version import __version__
from ..engine.receipt import canonical_hash
from ..jyotish.ashtakavarga import (
    ASHTAKAVARGA_CONTRIBUTORS,
    BAV_BENEFIC_HOUSES,
    compute_ashtakavarga,
)
from ..jyotish.nakshatra import RASI_NAMES, abhijit_position, nakshatra_position, normalize_degrees
from ..jyotish.panchanga import TITHI_GROUPS
from ..jyotish.shadbala import SEVEN_GRAHAS
from ..jyotish.vargas import RASI_LORDS

# Invariable Kakshya lord order (0..7) for each 3 deg 45 min (3.75 deg) segment of a sign
KAKSHYA_LORDS: Final[tuple[str, ...]] = (
    "Saturn",
    "Jupiter",
    "Mars",
    "Sun",
    "Venus",
    "Mercury",
    "Moon",
    "Lagna",
)
KAKSHYA_SPAN_DEG: Final[float] = 30.0 / 8.0  # 3.75 degrees (3 deg 45 min)

# 28 Nakshatras in canonical order (including Abhijit at index 21 between Uttara Ashadha and Shravana)
SARVATOBHADRA_28_NAKSHATRAS: Final[tuple[str, ...]] = (
    "Ashwini",
    "Bharani",
    "Krittika",
    "Rohini",
    "Mrigashirsha",
    "Ardra",
    "Punarvasu",
    "Pushya",
    "Ashlesha",
    "Magha",
    "Purva Phalguni",
    "Uttara Phalguni",
    "Hasta",
    "Chitra",
    "Swati",
    "Vishakha",
    "Anuradha",
    "Jyeshtha",
    "Mula",
    "Purva Ashadha",
    "Uttara Ashadha",
    "Abhijit",
    "Shravana",
    "Dhanishta",
    "Shatabhisha",
    "Purva Bhadrapada",
    "Uttara Bhadrapada",
    "Revati",
)

# 16 Sanskrit Vowels (Svaras) placed on the 4 concentric diagonal rings (TL, TR, BR, BL)
SARVATOBHADRA_16_VOWELS: Final[tuple[tuple[int, int, str], ...]] = (
    # Outer corners (ring 0)
    (0, 0, "a"),
    (0, 8, "aa"),
    (8, 8, "i"),
    (8, 0, "ii"),
    # Ring 1 diagonals
    (1, 1, "u"),
    (1, 7, "uu"),
    (7, 7, "ri"),
    (7, 1, "rii"),
    # Ring 2 diagonals
    (2, 2, "li"),
    (2, 6, "lii"),
    (6, 6, "e"),
    (6, 2, "ai"),
    # Ring 3 diagonals
    (3, 3, "o"),
    (3, 5, "au"),
    (5, 5, "am"),
    (5, 3, "ah"),
)

# 20 Consonants (Aksharas) placed along the non-diagonal cells of Ring 1 (5 per side)
SARVATOBHADRA_20_CONSONANTS: Final[tuple[tuple[int, int, str], ...]] = (
    # East (row 1, cols 2..6)
    (1, 2, "g"),
    (1, 3, "s"),
    (1, 4, "d"),
    (1, 5, "ch"),
    (1, 6, "l"),
    # South (col 7, rows 2..6)
    (2, 7, "u_c"),
    (3, 7, "m"),
    (4, 7, "t"),
    (5, 7, "p"),
    (6, 7, "r"),
    # West (row 7, cols 6..2)
    (7, 6, "n"),
    (7, 5, "dh"),
    (7, 4, "bh"),
    (7, 3, "y"),
    (7, 2, "j"),
    # North (col 1, rows 6..2)
    (6, 1, "kh"),
    (5, 1, "gh"),
    (4, 1, "v"),
    (3, 1, "sh"),
    (2, 1, "k"),
)

# 12 Rasis placed along the non-diagonal cells of Ring 2 (3 per side)
SARVATOBHADRA_12_RASIS: Final[tuple[tuple[int, int, str, int], ...]] = (
    # East (row 2, cols 3..5)
    (2, 3, "Mesha", 0),
    (2, 4, "Vrishabha", 1),
    (2, 5, "Mithuna", 2),
    # South (col 6, rows 3..5)
    (3, 6, "Karka", 3),
    (4, 6, "Simha", 4),
    (5, 6, "Kanya", 5),
    # West (row 6, cols 5..3)
    (6, 5, "Tula", 6),
    (6, 4, "Vrishchika", 7),
    (6, 3, "Dhanu", 8),
    # North (col 2, rows 5..3)
    (5, 2, "Makara", 9),
    (4, 2, "Kumbha", 10),
    (3, 2, "Meena", 11),
)

# 5 Tithi groups in the central 3x3 cross
SARVATOBHADRA_5_TITHIS: Final[tuple[tuple[int, int, str], ...]] = (
    (3, 4, "Nanda"),
    (4, 5, "Bhadra"),
    (5, 4, "Jaya"),
    (4, 3, "Rikta"),
    (4, 4, "Purna"),
)

NATURAL_MALEFICS: Final[frozenset[str]] = frozenset({"Sun", "Mars", "Saturn", "Rahu", "Ketu"})
NATURAL_BENEFICS: Final[frozenset[str]] = frozenset({"Jupiter", "Venus", "Mercury", "Moon"})

# Kota Chakra zone counts (1-based offset 1..28 from natal Janma Nakshatra)
# In each of the 4 fortress quadrants of 7 stars:
# - Offset 1 -> Stambha (Inner Pillar, 4 stars total: 1, 8, 15, 22)
# - Offsets 2, 5 -> Madhya (Middle Court, 8 stars total: 2, 5, 9, 12, 16, 19, 23, 26)
# - Offsets 3, 6 -> Prakaara (Boundary Wall, 8 stars total: 3, 6, 10, 13, 17, 20, 24, 27)
# - Offsets 4, 7 -> Bahya (Outer Trench, 8 stars total: 4, 7, 11, 14, 18, 21, 25, 28)
# In each quadrant of 7 stars, offsets 1, 2, 3 are Pravesha (diagonal entry paths) and
# offsets 4, 5, 6, 7 are Nirgamana (cardinal exit paths).
KOTA_STAMBHA_OFFSETS: Final[frozenset[int]] = frozenset({1, 8, 15, 22})
KOTA_MADHYA_OFFSETS: Final[frozenset[int]] = frozenset({2, 5, 9, 12, 16, 19, 23, 26})
KOTA_PRAKAARA_OFFSETS: Final[frozenset[int]] = frozenset({3, 6, 10, 13, 17, 20, 24, 27})
KOTA_BAHYA_OFFSETS: Final[frozenset[int]] = frozenset({4, 7, 11, 14, 18, 21, 25, 28})
KOTA_PRAVESHA_OFFSETS: Final[frozenset[int]] = frozenset({1, 2, 3, 8, 9, 10, 15, 16, 17, 22, 23, 24})
KOTA_NIRGAMANA_OFFSETS: Final[frozenset[int]] = frozenset({
    4, 5, 6, 7, 11, 12, 13, 14, 18, 19, 20, 21, 25, 26, 27, 28,
})


@dataclass(frozen=True)
class PrastaraTable:
    """8-Contributor x 12-Sign Prastara Ashtakavarga table for a single recipient."""

    recipient: str
    kakshya_lords: tuple[str, ...]
    kakshya_grid: tuple[tuple[int, ...], ...]
    contributor_rows: Mapping[str, tuple[int, ...]]
    sign_totals: tuple[int, ...]
    total_bindus: int


@dataclass(frozen=True)
class PrastaraAshtakavargaSet:
    """Complete Prastara Ashtakavarga tables for all 7 planets plus Lagna."""

    tables: Mapping[str, PrastaraTable]
    sarvashtakavarga_7: tuple[int, ...]
    sarvashtakavarga_7_total: int
    receipt: Mapping[str, Any]
    receipt_sha256: str


@dataclass(frozen=True)
class KakshyaTransitEvaluation:
    """Kakshya (3 deg 45 min) transit evaluation for a planet at a sidereal longitude."""

    recipient: str | None
    longitude_deg: float
    sign_index: int
    sign_name: str
    degree_in_sign: float
    kakshya_index: int
    kakshya_number: int
    kakshya_lord: str
    kakshya_start_deg_in_sign: float
    kakshya_end_deg_in_sign: float
    degree_in_kakshya: float
    fraction_elapsed: float
    fraction_remaining: float
    has_bindu: bool | None
    sign_bindus: int | None


@dataclass(frozen=True)
class SarvatobhadraCell:
    """One cell `(row, col)` in the 9x9 Sarvatobhadra Chakra."""

    row: int
    col: int
    cell_type: str
    label: str
    direction: str
    nakshatra_28_index: int | None = None
    rasi_index: int | None = None


@dataclass(frozen=True)
class SarvatobhadraVedhaRays:
    """3-Way Sarvatobhadra Vedha rays cast from a perimeter Nakshatra cell."""

    source_nakshatra: str
    source_nakshatra_28_index: int
    source_row: int
    source_col: int
    direction: str
    front_vedha_nakshatra: str
    left_vedha_nakshatra: str
    right_vedha_nakshatra: str
    front_ray_cells: tuple[SarvatobhadraCell, ...]
    left_ray_cells: tuple[SarvatobhadraCell, ...]
    right_ray_cells: tuple[SarvatobhadraCell, ...]


@dataclass(frozen=True)
class SarvatobhadraPlanetTransit:
    """Sarvatobhadra transit Vedha cast by one planet."""

    planet: str
    longitude_deg: float
    speed_deg_per_day: float
    motion: str
    is_natural_benefic: bool
    nakshatra_28_index: int
    nakshatra_28_name: str
    vedha_rays: SarvatobhadraVedhaRays
    active_vedha_nakshatras: tuple[str, ...]
    active_vedha_rasis: tuple[str, ...]
    active_vedha_tithis: tuple[str, ...]
    active_vedha_vowels: tuple[str, ...]
    active_vedha_consonants: tuple[str, ...]
    aspects_janma_nakshatra: bool
    aspects_janma_rasi: bool
    aspects_janma_tithi: bool
    aspects_nama_akshara: bool


@dataclass(frozen=True)
class SarvatobhadraChakraAnalysis:
    """Complete 9x9 Sarvatobhadra Chakra grid and multi-planet transit Vedha analysis."""

    grid: tuple[tuple[SarvatobhadraCell, ...], ...]
    nakshatra_cells: Mapping[str, SarvatobhadraCell]
    vedha_lookup: Mapping[str, SarvatobhadraVedhaRays]
    janma_nakshatra_28: str
    janma_rasi_name: str
    janma_tithi_group: str | None
    nama_akshara: str | None
    planet_transits: Mapping[str, SarvatobhadraPlanetTransit]
    benefic_vedha_on_janma_nakshatra: tuple[str, ...]
    malefic_vedha_on_janma_nakshatra: tuple[str, ...]
    benefic_vedha_on_janma_rasi: tuple[str, ...]
    malefic_vedha_on_janma_rasi: tuple[str, ...]
    receipt: Mapping[str, Any]
    receipt_sha256: str


@dataclass(frozen=True)
class KotaNakshatraSlot:
    """One of the 28 Nakshatra slots in the Kota Chakra relative to Janma Nakshatra."""

    offset_from_janma: int
    nakshatra_28_index: int
    nakshatra_28_name: str
    zone: str
    path_type: str
    is_pravesha: bool
    is_nirgamana: bool


@dataclass(frozen=True)
class KotaPlanetPlacement:
    """Placement of one transiting planet inside the Kota Chakra fortress."""

    planet: str
    longitude_deg: float
    is_natural_benefic: bool
    nakshatra_28_index: int
    nakshatra_28_name: str
    offset_from_janma: int
    zone: str
    path_type: str
    is_pravesha: bool
    is_nirgamana: bool
    afflicts_stambha: bool


@dataclass(frozen=True)
class KotaChakraAnalysis:
    """Complete Kota Chakra fortress analysis for a native and transit positions."""

    natal_moon_lon_deg: float
    janma_rasi_index: int
    janma_rasi_name: str
    janma_nakshatra_28_index: int
    janma_nakshatra_28_name: str
    kota_swami: str
    kota_paala: str
    slots: tuple[KotaNakshatraSlot, ...]
    zone_nakshatras: Mapping[str, tuple[str, ...]]
    pravesha_nakshatras: tuple[str, ...]
    nirgamana_nakshatras: tuple[str, ...]
    planet_placements: Mapping[str, KotaPlanetPlacement]
    stambha_malefics: tuple[str, ...]
    stambha_benefics: tuple[str, ...]
    pravesha_malefics: tuple[str, ...]
    nirgamana_malefics: tuple[str, ...]
    is_fortress_besieged: bool
    vulnerability_status: str
    receipt: Mapping[str, Any]
    receipt_sha256: str


def prastara_ashtakavarga(
    planet_longitudes: Mapping[str, float],
    lagna_lon_deg: float,
) -> PrastaraAshtakavargaSet:
    """Build the 8-Contributor x 12-Sign Prastara Ashtakavarga tables ordered by Kakshya lord
    (`Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon, Lagna`).
    """
    ashta = compute_ashtakavarga(planet_longitudes, lagna_lon_deg)
    tables: dict[str, PrastaraTable] = {}

    for recipient in ASHTAKAVARGA_CONTRIBUTORS:
        bav = ashta.bhinna_tables[recipient]
        kakshya_rows: list[tuple[int, ...]] = []
        ordered_map: dict[str, tuple[int, ...]] = {}
        for k_lord in KAKSHYA_LORDS:
            row = bav.contributor_matrix[k_lord]
            kakshya_rows.append(row)
            ordered_map[k_lord] = row

        tables[recipient] = PrastaraTable(
            recipient=recipient,
            kakshya_lords=KAKSHYA_LORDS,
            kakshya_grid=tuple(kakshya_rows),
            contributor_rows=ordered_map,
            sign_totals=bav.sign_bindus,
            total_bindus=bav.total_bindus,
        )

    receipt = {
        "module": "ephemeris_oss.jyotish_transit.chakras",
        "version": __version__,
        "sav_7": list(ashta.sarvashtakavarga_7),
        "sav_total": ashta.sarvashtakavarga_7_total,
        "bav_totals": {r: tables[r].total_bindus for r in ASHTAKAVARGA_CONTRIBUTORS},
    }
    return PrastaraAshtakavargaSet(
        tables=tables,
        sarvashtakavarga_7=ashta.sarvashtakavarga_7,
        sarvashtakavarga_7_total=ashta.sarvashtakavarga_7_total,
        receipt=receipt,
        receipt_sha256=canonical_hash(receipt),
    )


def evaluate_kakshya(
    lon_or_recipient: float | str,
    transit_lon_deg: float | None = None,
    *,
    recipient: str | None = None,
    prastara: PrastaraAshtakavargaSet | PrastaraTable | None = None,
    planet_longitudes: Mapping[str, float] | None = None,
    lagna_lon_deg: float | None = None,
) -> KakshyaTransitEvaluation:
    """Evaluate the Ashtakavarga Kakshya (1..8 of 3.75 deg each) at a sidereal longitude.

    Supports calling either as `evaluate_kakshya(transit_lon_deg, recipient="Saturn", prastara=...)`
    or `evaluate_kakshya("Saturn", transit_lon_deg, prastara=...)`.
    """
    if isinstance(lon_or_recipient, str):
        rec_name: str | None = lon_or_recipient.strip().capitalize()
        if transit_lon_deg is None:
            raise ValueError("transit_lon_deg must be provided when first argument is recipient name")
        lon = normalize_degrees(transit_lon_deg)
    else:
        lon = normalize_degrees(lon_or_recipient)
        rec_name = recipient.strip().capitalize() if recipient is not None else None

    sign_idx = min(int(lon // 30.0), 11)
    deg_in_sign = lon - sign_idx * 30.0
    k_idx = min(int(deg_in_sign / KAKSHYA_SPAN_DEG), 7)
    k_num = k_idx + 1
    k_lord = KAKSHYA_LORDS[k_idx]
    k_start = k_idx * KAKSHYA_SPAN_DEG
    k_end = (k_idx + 1) * KAKSHYA_SPAN_DEG
    deg_in_k = max(0.0, min(deg_in_sign - k_start, KAKSHYA_SPAN_DEG))
    frac_elapsed = deg_in_k / KAKSHYA_SPAN_DEG

    if prastara is None and planet_longitudes is not None and lagna_lon_deg is not None:
        prastara = prastara_ashtakavarga(planet_longitudes, lagna_lon_deg)

    has_bindu: bool | None = None
    sign_bindus: int | None = None
    if prastara is not None:
        if isinstance(prastara, PrastaraTable):
            tbl = prastara
            if rec_name is None:
                rec_name = tbl.recipient
        else:
            target_rec = rec_name if rec_name is not None else "Sun"
            if target_rec not in prastara.tables:
                raise ValueError(f"Unknown Prastara recipient {target_rec!r}")
            tbl = prastara.tables[target_rec]
            rec_name = target_rec

        has_bindu = bool(tbl.kakshya_grid[k_idx][sign_idx] == 1)
        sign_bindus = tbl.sign_totals[sign_idx]

    return KakshyaTransitEvaluation(
        recipient=rec_name,
        longitude_deg=lon,
        sign_index=sign_idx,
        sign_name=RASI_NAMES[sign_idx],
        degree_in_sign=deg_in_sign,
        kakshya_index=k_idx,
        kakshya_number=k_num,
        kakshya_lord=k_lord,
        kakshya_start_deg_in_sign=k_start,
        kakshya_end_deg_in_sign=k_end,
        degree_in_kakshya=deg_in_k,
        fraction_elapsed=frac_elapsed,
        fraction_remaining=1.0 - frac_elapsed,
        has_bindu=has_bindu,
        sign_bindus=sign_bindus,
    )


def build_sarvatobhadra_grid() -> tuple[tuple[SarvatobhadraCell, ...], ...]:
    """Construct the canonical 9x9 (81-cell) Sarvatobhadra Chakra grid.

    Cell breakdown (total = 81):
    - 28 Nakshatras (including Abhijit) along the outer perimeter (7 per side)
    - 16 Vowels (Svaras) along the two main diagonals
    - 20 Consonants (Aksharas) along the second ring (`row/col = 1, 7`)
    - 12 Rasis (`Mesha..Meena`) along the third ring (`row/col = 2, 6`)
    - 5 Tithi groups (`Nanda, Bhadra, Jaya, Rikta, Purna`) in the central 3x3 cross
    """
    cells: list[list[SarvatobhadraCell | None]] = [[None for _ in range(9)] for _ in range(9)]

    # 1. Place the 28 Nakshatras along the outer perimeter starting from Krittika (index 2) at (0, 1)
    # East: row=0, cols 1..7 -> indices 2..8 (Krittika..Ashlesha)
    for idx_offset, col in enumerate(range(1, 8)):
        n_idx = 2 + idx_offset
        name = SARVATOBHADRA_28_NAKSHATRAS[n_idx]
        cells[0][col] = SarvatobhadraCell(0, col, "Nakshatra", name, "East", nakshatra_28_index=n_idx)

    # South: col=8, rows 1..7 -> indices 9..15 (Magha..Vishakha)
    for idx_offset, row in enumerate(range(1, 8)):
        n_idx = 9 + idx_offset
        name = SARVATOBHADRA_28_NAKSHATRAS[n_idx]
        cells[row][8] = SarvatobhadraCell(row, 8, "Nakshatra", name, "South", nakshatra_28_index=n_idx)

    # West: row=8, cols 7..1 -> indices 16..22 (Anuradha..Shravana incl. Abhijit at 21)
    for idx_offset, col in enumerate(range(7, 0, -1)):
        n_idx = 16 + idx_offset
        name = SARVATOBHADRA_28_NAKSHATRAS[n_idx]
        cells[8][col] = SarvatobhadraCell(8, col, "Nakshatra", name, "West", nakshatra_28_index=n_idx)

    # North: col=0, rows 7..1 -> indices 23..27 (Dhanishta..Revati) then 0, 1 (Ashwini, Bharani)
    north_indices = (23, 24, 25, 26, 27, 0, 1)
    for n_idx, row in zip(north_indices, range(7, 0, -1)):
        name = SARVATOBHADRA_28_NAKSHATRAS[n_idx]
        cells[row][0] = SarvatobhadraCell(row, 0, "Nakshatra", name, "North", nakshatra_28_index=n_idx)

    # 2. Place the 16 Vowels on the diagonals
    for r, c, vowel in SARVATOBHADRA_16_VOWELS:
        quad = ("NE" if c > 4 else "NW") if r < 4 else ("SE" if c > 4 else "SW")
        cells[r][c] = SarvatobhadraCell(r, c, "Vowel", vowel, quad)

    # 3. Place the 20 Consonants in Ring 1
    for r, c, cons in SARVATOBHADRA_20_CONSONANTS:
        direction = "East" if r == 1 else ("South" if c == 7 else ("West" if r == 7 else "North"))
        cells[r][c] = SarvatobhadraCell(r, c, "Consonant", cons, direction)

    # 4. Place the 12 Rasis in Ring 2
    for r, c, rasi_name, r_idx in SARVATOBHADRA_12_RASIS:
        direction = "East" if r == 2 else ("South" if c == 6 else ("West" if r == 6 else "North"))
        cells[r][c] = SarvatobhadraCell(r, c, "Rasi", rasi_name, direction, rasi_index=r_idx)

    # 5. Place the 5 Tithi groups in the central cross
    tithi_dirs = {(3, 4): "East", (4, 5): "South", (5, 4): "West", (4, 3): "North", (4, 4): "Center"}
    for r, c, t_group in SARVATOBHADRA_5_TITHIS:
        cells[r][c] = SarvatobhadraCell(r, c, "Tithi", t_group, tithi_dirs[(r, c)])

    return tuple(tuple(cell for cell in row if cell is not None) for row in cells)


def _trace_ray(
    grid: tuple[tuple[SarvatobhadraCell, ...], ...],
    start_row: int,
    start_col: int,
    dr: int,
    dc: int,
) -> tuple[SarvatobhadraCell, ...]:
    ray: list[SarvatobhadraCell] = []
    r, c = start_row + dr, start_col + dc
    while 0 <= r <= 8 and 0 <= c <= 8:
        ray.append(grid[r][c])
        r += dr
        c += dc
    return tuple(ray)


def compute_sarvatobhadra_vedha(
    nakshatra_28_name_or_index: str | int,
    *,
    grid: tuple[tuple[SarvatobhadraCell, ...], ...] | None = None,
) -> SarvatobhadraVedhaRays:
    """Compute the 3-way Sarvatobhadra Vedha rays (`front`, `left`, `right`) cast from
    any of the 28 perimeter Nakshatras.
    """
    if grid is None:
        grid = build_sarvatobhadra_grid()

    if isinstance(nakshatra_28_name_or_index, int):
        if not 0 <= nakshatra_28_name_or_index <= 27:
            raise ValueError("nakshatra_28_index must be in 0..27")
        target_name = SARVATOBHADRA_28_NAKSHATRAS[nakshatra_28_name_or_index]
    else:
        target_name = nakshatra_28_name_or_index.strip()
        if target_name not in SARVATOBHADRA_28_NAKSHATRAS:
            raise ValueError(f"Unknown 28-scheme nakshatra {target_name!r}")

    source_cell: SarvatobhadraCell | None = None
    for row in grid:
        for cell in row:
            if cell.cell_type == "Nakshatra" and cell.label == target_name:
                source_cell = cell
                break
        if source_cell is not None:
            break

    assert source_cell is not None and source_cell.nakshatra_28_index is not None
    r, c = source_cell.row, source_cell.col

    # Determine inward Front, Left (forward/counter-clockwise), and Right (backward/clockwise) step vectors
    if r == 0:  # East (top wall, looking South +r)
        front_vec = (1, 0)
        left_vec = (1, 1)
        right_vec = (1, -1)
    elif c == 8:  # South (right wall, looking West -c)
        front_vec = (0, -1)
        left_vec = (1, -1)
        right_vec = (-1, -1)
    elif r == 8:  # West (bottom wall, looking North -r)
        front_vec = (-1, 0)
        left_vec = (-1, -1)
        right_vec = (-1, 1)
    else:  # North (left wall, looking East +c)
        front_vec = (0, 1)
        left_vec = (-1, 1)
        right_vec = (1, 1)

    front_ray = _trace_ray(grid, r, c, front_vec[0], front_vec[1])
    left_ray = _trace_ray(grid, r, c, left_vec[0], left_vec[1])
    right_ray = _trace_ray(grid, r, c, right_vec[0], right_vec[1])

    return SarvatobhadraVedhaRays(
        source_nakshatra=source_cell.label,
        source_nakshatra_28_index=source_cell.nakshatra_28_index,
        source_row=r,
        source_col=c,
        direction=source_cell.direction,
        front_vedha_nakshatra=front_ray[-1].label,
        left_vedha_nakshatra=left_ray[-1].label,
        right_vedha_nakshatra=right_ray[-1].label,
        front_ray_cells=front_ray,
        left_ray_cells=left_ray,
        right_ray_cells=right_ray,
    )


def evaluate_sarvatobhadra_transits(
    natal_moon_lon_deg: float,
    transit_longitudes: Mapping[str, float],
    *,
    planet_speeds_deg_per_day: Mapping[str, float] | None = None,
    janma_tithi_group: str | None = None,
    nama_akshara: str | None = None,
) -> SarvatobhadraChakraAnalysis:
    """Evaluate full 9x9 Sarvatobhadra Chakra transits and 3-way Vedha on natal sensitive points.

    Directional Vedha rule (*Narapati Jayacharya Sarvatobhadra*):
    - Luminaries (`Sun`, `Moon`) cast all three Vedhas (`front`, `left`, `right`).
    - Direct planets (`speed >= 0`) cast `front` and `left` Vedhas.
    - Retrograde planets (`speed < 0`, and default `Rahu`/`Ketu`) cast `front` and `right` Vedhas.
    """
    grid = build_sarvatobhadra_grid()
    nak_cells: dict[str, SarvatobhadraCell] = {}
    vedha_map: dict[str, SarvatobhadraVedhaRays] = {}
    for n_name in SARVATOBHADRA_28_NAKSHATRAS:
        rays = compute_sarvatobhadra_vedha(n_name, grid=grid)
        vedha_map[n_name] = rays
        nak_cells[n_name] = grid[rays.source_row][rays.source_col]

    m_lon = normalize_degrees(natal_moon_lon_deg)
    janma_ab = abhijit_position(m_lon)
    janma_nak_28 = janma_ab.nakshatra_28_name
    janma_rasi_idx = min(int(m_lon // 30.0), 11)
    janma_rasi = RASI_NAMES[janma_rasi_idx]

    speeds = {k.strip().capitalize(): float(v) for k, v in (planet_speeds_deg_per_day or {}).items()}
    norm_transits = {k.strip().capitalize(): normalize_degrees(v) for k, v in transit_longitudes.items()}

    p_transits: dict[str, SarvatobhadraPlanetTransit] = {}
    benefic_on_nak: list[str] = []
    malefic_on_nak: list[str] = []
    benefic_on_rasi: list[str] = []
    malefic_on_rasi: list[str] = []

    for planet, lon in norm_transits.items():
        default_spd = -0.05 if planet in ("Rahu", "Ketu") else 1.0
        spd = speeds.get(planet, default_spd)
        ab_pos = abhijit_position(lon)
        n_name = ab_pos.nakshatra_28_name
        rays = vedha_map[n_name]

        if planet in ("Sun", "Moon"):
            motion = "luminary"
            active_rays = (rays.front_ray_cells, rays.left_ray_cells, rays.right_ray_cells)
        elif spd < 0.0:
            motion = "retrograde"
            active_rays = (rays.front_ray_cells, rays.right_ray_cells)
        else:
            motion = "direct"
            active_rays = (rays.front_ray_cells, rays.left_ray_cells)

        naks_hit: list[str] = []
        rasis_hit: list[str] = []
        tithis_hit: list[str] = []
        vowels_hit: list[str] = []
        cons_hit: list[str] = []

        for ray in active_rays:
            for cell in ray:
                if cell.cell_type == "Nakshatra" and cell.label not in naks_hit:
                    naks_hit.append(cell.label)
                elif cell.cell_type == "Rasi" and cell.label not in rasis_hit:
                    rasis_hit.append(cell.label)
                elif cell.cell_type == "Tithi" and cell.label not in tithis_hit:
                    tithis_hit.append(cell.label)
                elif cell.cell_type == "Vowel" and cell.label not in vowels_hit:
                    vowels_hit.append(cell.label)
                elif cell.cell_type == "Consonant" and cell.label not in cons_hit:
                    cons_hit.append(cell.label)

        is_ben = planet in NATURAL_BENEFICS
        hits_j_nak = (janma_nak_28 in naks_hit) or (n_name == janma_nak_28)
        hits_j_rasi = janma_rasi in rasis_hit
        hits_j_tithi = (janma_tithi_group is not None) and (janma_tithi_group in tithis_hit)
        hits_akshara = (nama_akshara is not None) and (
            nama_akshara in vowels_hit or nama_akshara in cons_hit
        )

        if hits_j_nak:
            if is_ben:
                benefic_on_nak.append(planet)
            else:
                malefic_on_nak.append(planet)
        if hits_j_rasi:
            if is_ben:
                benefic_on_rasi.append(planet)
            else:
                malefic_on_rasi.append(planet)

        p_transits[planet] = SarvatobhadraPlanetTransit(
            planet=planet,
            longitude_deg=lon,
            speed_deg_per_day=spd,
            motion=motion,
            is_natural_benefic=is_ben,
            nakshatra_28_index=ab_pos.nakshatra_28_index,
            nakshatra_28_name=n_name,
            vedha_rays=rays,
            active_vedha_nakshatras=tuple(naks_hit),
            active_vedha_rasis=tuple(rasis_hit),
            active_vedha_tithis=tuple(tithis_hit),
            active_vedha_vowels=tuple(vowels_hit),
            active_vedha_consonants=tuple(cons_hit),
            aspects_janma_nakshatra=hits_j_nak,
            aspects_janma_rasi=hits_j_rasi,
            aspects_janma_tithi=hits_j_tithi,
            aspects_nama_akshara=hits_akshara,
        )

    receipt = {
        "module": "ephemeris_oss.jyotish_transit.chakras",
        "version": __version__,
        "janma_nakshatra_28": janma_nak_28,
        "janma_rasi": janma_rasi,
        "benefic_vedha_on_janma_nakshatra": sorted(benefic_on_nak),
        "malefic_vedha_on_janma_nakshatra": sorted(malefic_on_nak),
        "planet_nakshatras": {p: p_transits[p].nakshatra_28_name for p in sorted(p_transits)},
    }

    return SarvatobhadraChakraAnalysis(
        grid=grid,
        nakshatra_cells=nak_cells,
        vedha_lookup=vedha_map,
        janma_nakshatra_28=janma_nak_28,
        janma_rasi_name=janma_rasi,
        janma_tithi_group=janma_tithi_group,
        nama_akshara=nama_akshara,
        planet_transits=p_transits,
        benefic_vedha_on_janma_nakshatra=tuple(sorted(benefic_on_nak)),
        malefic_vedha_on_janma_nakshatra=tuple(sorted(malefic_on_nak)),
        benefic_vedha_on_janma_rasi=tuple(sorted(benefic_on_rasi)),
        malefic_vedha_on_janma_rasi=tuple(sorted(malefic_on_rasi)),
        receipt=receipt,
        receipt_sha256=canonical_hash(receipt),
    )


def evaluate_kota_chakra(
    natal_moon_lon_deg: float,
    transit_longitudes: Mapping[str, float] | None = None,
) -> KotaChakraAnalysis:
    """Construct the 28-Nakshatra Kota Chakra (fortress vulnerability & protection grid)
    anchored at the native's `Janma Nakshatra` and evaluate transiting planets.

    Concentric zones (total = 28):
    - `Stambha` (Inner Pillar / Citadel): 4 nakshatras (offsets 1, 8, 15, 22)
    - `Madhya` (Middle Court): 8 nakshatras (offsets 2, 5, 9, 12, 16, 19, 23, 26)
    - `Prakaara` (Boundary Wall): 8 nakshatras (offsets 3, 6, 10, 13, 17, 20, 24, 27)
    - `Bahya` (Outer Trench): 8 nakshatras (offsets 4, 7, 11, 14, 18, 21, 25, 28)
    """
    m_lon = normalize_degrees(natal_moon_lon_deg)
    janma_ab = abhijit_position(m_lon)
    j_idx_28 = janma_ab.nakshatra_28_index
    j_name_28 = janma_ab.nakshatra_28_name
    j_rasi_idx = min(int(m_lon // 30.0), 11)
    j_rasi_name = RASI_NAMES[j_rasi_idx]

    kota_swami = RASI_LORDS[j_rasi_idx]
    # Classical Kota Paala: Vimshottari ruler of the Moon's 27-nakshatra position (or strip guard)
    kota_paala = nakshatra_position(m_lon).vimshottari_ruler

    slots: list[KotaNakshatraSlot] = []
    zone_lists: dict[str, list[str]] = {
        "Stambha": [],
        "Madhya": [],
        "Prakaara": [],
        "Bahya": [],
    }
    pravesha_list: list[str] = []
    nirgamana_list: list[str] = []
    slot_by_nak_idx: dict[int, KotaNakshatraSlot] = {}

    for offset in range(1, 29):
        n_idx = (j_idx_28 + offset - 1) % 28
        n_name = SARVATOBHADRA_28_NAKSHATRAS[n_idx]

        if offset in KOTA_STAMBHA_OFFSETS:
            zone = "Stambha"
        elif offset in KOTA_MADHYA_OFFSETS:
            zone = "Madhya"
        elif offset in KOTA_PRAKAARA_OFFSETS:
            zone = "Prakaara"
        else:
            zone = "Bahya"

        is_prav = offset in KOTA_PRAVESHA_OFFSETS
        is_nirg = not is_prav
        path_type = "Pravesha" if is_prav else "Nirgamana"

        slot = KotaNakshatraSlot(
            offset_from_janma=offset,
            nakshatra_28_index=n_idx,
            nakshatra_28_name=n_name,
            zone=zone,
            path_type=path_type,
            is_pravesha=is_prav,
            is_nirgamana=is_nirg,
        )
        slots.append(slot)
        slot_by_nak_idx[n_idx] = slot
        zone_lists[zone].append(n_name)
        if is_prav:
            pravesha_list.append(n_name)
        else:
            nirgamana_list.append(n_name)

    norm_transits = {k.strip().capitalize(): normalize_degrees(v) for k, v in (transit_longitudes or {}).items()}
    placements: dict[str, KotaPlanetPlacement] = {}
    stambha_mal: list[str] = []
    stambha_ben: list[str] = []
    pravesha_mal: list[str] = []
    nirgamana_mal: list[str] = []

    for planet, lon in norm_transits.items():
        ab = abhijit_position(lon)
        slot = slot_by_nak_idx[ab.nakshatra_28_index]
        is_ben = planet in NATURAL_BENEFICS
        afflicts = (not is_ben) and (slot.zone == "Stambha")

        if slot.zone == "Stambha":
            if is_ben:
                stambha_ben.append(planet)
            else:
                stambha_mal.append(planet)
        if not is_ben:
            if slot.is_pravesha:
                pravesha_mal.append(planet)
            else:
                nirgamana_mal.append(planet)

        placements[planet] = KotaPlanetPlacement(
            planet=planet,
            longitude_deg=lon,
            is_natural_benefic=is_ben,
            nakshatra_28_index=ab.nakshatra_28_index,
            nakshatra_28_name=ab.nakshatra_28_name,
            offset_from_janma=slot.offset_from_janma,
            zone=slot.zone,
            path_type=slot.path_type,
            is_pravesha=slot.is_pravesha,
            is_nirgamana=slot.is_nirgamana,
            afflicts_stambha=afflicts,
        )

    # Fortress is besieged if malefics occupy Stambha without benefic protection in Stambha
    besieged = bool(stambha_mal) and not bool(stambha_ben)
    if besieged:
        status = "Kritaghna / Besieged (Malefics in Stambha without benefic guard)"
    elif stambha_mal and stambha_ben:
        status = "Contested (Stambha has both malefic affliction and benefic protection)"
    elif pravesha_mal:
        status = "Guarded Alert (Malefics on Pravesha entry paths, Stambha clear)"
    else:
        status = "Surakshita / Protected (Stambha clear of malefics)"

    receipt = {
        "module": "ephemeris_oss.jyotish_transit.chakras",
        "version": __version__,
        "janma_nakshatra_28": j_name_28,
        "kota_swami": kota_swami,
        "kota_paala": kota_paala,
        "stambha_malefics": sorted(stambha_mal),
        "stambha_benefics": sorted(stambha_ben),
        "is_fortress_besieged": besieged,
    }

    return KotaChakraAnalysis(
        natal_moon_lon_deg=m_lon,
        janma_rasi_index=j_rasi_idx,
        janma_rasi_name=j_rasi_name,
        janma_nakshatra_28_index=j_idx_28,
        janma_nakshatra_28_name=j_name_28,
        kota_swami=kota_swami,
        kota_paala=kota_paala,
        slots=tuple(slots),
        zone_nakshatras={k: tuple(v) for k, v in zone_lists.items()},
        pravesha_nakshatras=tuple(pravesha_list),
        nirgamana_nakshatras=tuple(nirgamana_list),
        planet_placements=placements,
        stambha_malefics=tuple(sorted(stambha_mal)),
        stambha_benefics=tuple(sorted(stambha_ben)),
        pravesha_malefics=tuple(sorted(pravesha_mal)),
        nirgamana_malefics=tuple(sorted(nirgamana_mal)),
        is_fortress_besieged=besieged,
        vulnerability_status=status,
        receipt=receipt,
        receipt_sha256=canonical_hash(receipt),
    )


__all__ = [
    "KAKSHYA_LORDS",
    "KAKSHYA_SPAN_DEG",
    "KOTA_BAHYA_OFFSETS",
    "KOTA_MADHYA_OFFSETS",
    "KOTA_NIRGAMANA_OFFSETS",
    "KOTA_PRAKAARA_OFFSETS",
    "KOTA_PRAVESHA_OFFSETS",
    "KOTA_STAMBHA_OFFSETS",
    "KakshyaTransitEvaluation",
    "KotaChakraAnalysis",
    "KotaNakshatraSlot",
    "KotaPlanetPlacement",
    "NATURAL_BENEFICS",
    "NATURAL_MALEFICS",
    "PrastaraAshtakavargaSet",
    "PrastaraTable",
    "SARVATOBHADRA_12_RASIS",
    "SARVATOBHADRA_16_VOWELS",
    "SARVATOBHADRA_20_CONSONANTS",
    "SARVATOBHADRA_28_NAKSHATRAS",
    "SARVATOBHADRA_5_TITHIS",
    "SarvatobhadraCell",
    "SarvatobhadraChakraAnalysis",
    "SarvatobhadraPlanetTransit",
    "SarvatobhadraVedhaRays",
    "build_sarvatobhadra_grid",
    "compute_sarvatobhadra_vedha",
    "evaluate_kakshya",
    "evaluate_kota_chakra",
    "evaluate_sarvatobhadra_transits",
    "prastara_ashtakavarga",
]
