"""64th Navamsa, 22nd Drekkana (Khara), 85th Dwadashamsa, and Mrityu Bhaga Vulnerability Engine.

Implements classical vulnerability (*Chhidra* / *Khara*) and fatal degree (*Mrityu Bhaga*)
diagnostics from Varahamihira's *Brihat Jataka* (Chapter 27, *Drekkana Swarupa*),
Mantreswara's *Phaladeepika* (Chapters 3 and 13), Vaidyanatha Dikshita's *Jataka Parijata*
(Chapters 1 and 5), and *Brihat Parashara Hora Shastra*:
1. **22nd Drekkana (Khara Drekkana)**:
   - Absolute Drekkana index ``0..35`` is ``int((reference_lon_deg % 360.0) / 10.0)``.
   - The 22nd Drekkana index is ``(drekkana_index + 21) % 36``, which always falls in the
     8th sign from the reference sign and the 8th sign from the reference D3 sign.
   - Catalogs all 36 Drekkanas with their Parashari 1st/5th/9th lord and classical
     *Drekkana Swarupa* classification (``Sarpa``, ``Pakshi``, ``Chatushpada``, ``Ayudha``,
     ``Pasha``, ``Nigada``, ``Krura``, ``Saumya``).
2. **64th Navamsa (Khara Navamsa)**:
   - Absolute Navamsa index ``0..107`` is ``int((reference_lon_deg % 360.0) / (10.0 / 3.0))``.
   - The 64th Navamsa index is ``(navamsa_index + 63) % 108``, whose D9 sign is always the
     4th sign from the reference's D9 sign and whose D1 span lies in the 8th sign from the
     reference's D1 sign.
3. **85th Dwadashamsa (Khara Dwadashamsa)**:
   - Absolute Dwadashamsa index ``0..143`` is ``int((reference_lon_deg % 360.0) / 2.5)``.
   - The 85th Dwadashamsa index is ``(d12_index + 84) % 144``.
4. **Mrityu Bhaga (Fatal Degree) Detector**:
   - Evaluates all 9 grahas and Lagna against the canonical *Phaladeepika* / *Jataka Parijata*
     Mrityu Bhaga degree table across the 12 signs and flags proximity within 1.0 degree.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Final, Mapping

from ..engine.receipt import canonical_hash
from ..jyotish.nakshatra import RASI_NAMES
from ..jyotish.vargas import RASI_LORDS

DREKKANA_SWARUPA_CATEGORIES: Final[frozenset[str]] = frozenset(
    {
        "Sarpa",
        "Pakshi",
        "Chatushpada",
        "Ayudha",
        "Pasha",
        "Nigada",
        "Krura",
        "Saumya",
    }
)


@dataclass(frozen=True)
class DrekkanaSwarupaEntry:
    """Classical Brihat Jataka Ch. 27 / Phaladeepika attributes for one of the 36 Drekkanas."""

    drekkana_index: int
    sign_index: int
    sign_name: str
    decanate_number: int
    degree_span_in_sign: tuple[float, float]
    d3_sign_index: int
    d3_sign_name: str
    ruling_planet: str
    swarupa: str
    secondary_tags: tuple[str, ...]
    description: str


def _make_drekkana_entry(
    idx: int,
    swarupa: str,
    secondary_tags: tuple[str, ...],
    description: str,
) -> DrekkanaSwarupaEntry:
    sign_idx = idx // 3
    dec_idx = idx % 3
    start_deg = float(dec_idx * 10)
    end_deg = float((dec_idx + 1) * 10)
    d3_sign = (sign_idx + dec_idx * 4) % 12
    lord = RASI_LORDS[d3_sign].lower()
    return DrekkanaSwarupaEntry(
        drekkana_index=idx,
        sign_index=sign_idx,
        sign_name=RASI_NAMES[sign_idx],
        decanate_number=dec_idx + 1,
        degree_span_in_sign=(start_deg, end_deg),
        d3_sign_index=d3_sign,
        d3_sign_name=RASI_NAMES[d3_sign],
        ruling_planet=lord,
        swarupa=swarupa,
        secondary_tags=secondary_tags,
        description=description,
    )


# Canonical 36 Drekkana Swarupa table per Varahamihira's Brihat Jataka Ch. 27 & Phaladeepika.
DREKKANA_SWARUPA_CATALOG: Final[tuple[DrekkanaSwarupaEntry, ...]] = (
    # 0 Mesha (Aries)
    _make_drekkana_entry(0, "Ayudha", ("Ayudha", "Krura"), "Fierce man in white cloth holding a raised battle-axe"),
    _make_drekkana_entry(1, "Chatushpada", ("Chatushpada", "Saumya"), "Horse-faced woman wearing red garments with a pot of jewels"),
    _make_drekkana_entry(2, "Krura", ("Krura", "Ayudha"), "Fierce man skilled in arts holding an uplifted staff"),
    # 1 Vrishabha (Taurus)
    _make_drekkana_entry(3, "Saumya", ("Saumya",), "Woman with curled hair carrying a water vessel desiring food and ornaments"),
    _make_drekkana_entry(4, "Chatushpada", ("Chatushpada", "Saumya"), "Man skilled in agriculture and cattle with a ram-like neck"),
    _make_drekkana_entry(5, "Chatushpada", ("Chatushpada", "Krura"), "Elephant-bodied figure with white tusks and tawny eyes thinking of deer"),
    # 2 Mithuna (Gemini)
    _make_drekkana_entry(6, "Saumya", ("Saumya",), "Graceful woman fond of needlework and ornaments"),
    _make_drekkana_entry(7, "Pakshi", ("Pakshi", "Ayudha"), "Eagle-faced warrior in a flower garden holding bow and arrows"),
    _make_drekkana_entry(8, "Ayudha", ("Ayudha", "Saumya"), "Man adorned with jewels holding bow, quiver, mail, and lute"),
    # 3 Karka (Cancer)
    _make_drekkana_entry(9, "Chatushpada", ("Chatushpada", "Saumya"), "Figure holding leaves, roots, and fruits with elephant body and horse neck"),
    _make_drekkana_entry(10, "Sarpa", ("Sarpa", "Krura"), "Youthful woman in forest with a lotus on head and a serpent"),
    _make_drekkana_entry(11, "Sarpa", ("Sarpa", "Krura"), "Man coiled by a serpent setting out on a boat across the ocean for gems"),
    # 4 Simha (Leo)
    _make_drekkana_entry(12, "Pakshi", ("Pakshi", "Chatushpada", "Krura"), "Vulture and jackal atop a Shalmali tree"),
    _make_drekkana_entry(13, "Chatushpada", ("Chatushpada", "Ayudha"), "Horse-shaped figure wearing a white floral garland holding a bow"),
    _make_drekkana_entry(14, "Ayudha", ("Ayudha", "Chatushpada", "Krura"), "Bear-faced figure with ape-like deeds holding a club and bow"),
    # 5 Kanya (Virgo)
    _make_drekkana_entry(15, "Saumya", ("Saumya",), "Maiden carrying a jar filled with blooming flowers"),
    _make_drekkana_entry(16, "Saumya", ("Saumya",), "Accountant holding a stylus calculating income and expenditure"),
    _make_drekkana_entry(17, "Saumya", ("Saumya",), "Tall golden woman holding a pot and sacrificial ladle heading to a temple"),
    # 6 Tula (Libra)
    _make_drekkana_entry(18, "Saumya", ("Saumya",), "Merchant seated in a market holding scales and weights"),
    _make_drekkana_entry(19, "Pakshi", ("Pakshi", "Krura"), "Vulture-faced figure hungry and thirsty thinking of wife and children"),
    _make_drekkana_entry(20, "Chatushpada", ("Chatushpada", "Ayudha"), "Horse-faced figure with golden quiver and armor frightening animals in woods"),
    # 7 Vrishchika (Scorpio)
    _make_drekkana_entry(21, "Sarpa", ("Sarpa", "Krura"), "Woman without garments coming from the sea with feet bound by serpents"),
    _make_drekkana_entry(22, "Sarpa", ("Sarpa", "Pasha"), "Woman desiring comfort with body encircled by serpents"),
    _make_drekkana_entry(23, "Chatushpada", ("Chatushpada", "Krura"), "Lion with broad face resembling a tortoise guarding a sandalwood forest"),
    # 8 Dhanu (Sagittarius)
    _make_drekkana_entry(24, "Ayudha", ("Ayudha", "Chatushpada"), "Centaur with human face and horse body holding a long bow at a hermitage"),
    _make_drekkana_entry(25, "Saumya", ("Saumya",), "Graceful woman seated on a throne picking gems from the ocean"),
    _make_drekkana_entry(26, "Ayudha", ("Ayudha", "Saumya"), "Bearded man of golden hue seated on a throne holding a staff"),
    # 9 Makara (Capricorn)
    _make_drekkana_entry(27, "Nigada", ("Nigada", "Pasha", "Krura"), "Hairy fierce man like a crocodile holding iron fetters and nose-rope"),
    _make_drekkana_entry(28, "Krura", ("Krura", "Saumya"), "Woman skilled in arts with lotus eyes wearing iron ear-ornaments"),
    _make_drekkana_entry(29, "Ayudha", ("Ayudha", "Chatushpada"), "Kinnara-bodied figure with blanket, quiver, bow, and armor"),
    # 10 Kumbha (Aquarius)
    _make_drekkana_entry(30, "Pakshi", ("Pakshi", "Krura"), "Vulture-faced figure anxious over oil, wine, water, and pots"),
    _make_drekkana_entry(31, "Pasha", ("Pasha", "Krura"), "Woman in a burnt wagon in a forest carrying iron pots bound by cords"),
    _make_drekkana_entry(32, "Krura", ("Krura", "Saumya"), "Dark man with hairy ears wearing a bark crown carrying pots of iron and resin"),
    # 11 Meena (Pisces)
    _make_drekkana_entry(33, "Saumya", ("Saumya",), "Man carrying sacrificial vessels, pearls, and gems crossing the sea in a boat"),
    _make_drekkana_entry(34, "Saumya", ("Saumya",), "Bright-faced woman steering a bannered ship to the coast"),
    _make_drekkana_entry(35, "Sarpa", ("Sarpa", "Pasha", "Krura"), "Man coiled by a serpent in a forest pit crying from thieves and fire"),
)

# Canonical Mrityu Bhaga (fatal degree within each sign 0..11) per Phaladeepika Ch. 13 & Jataka Parijata.
MRITYU_BHAGA_DEGREE_TABLE: Final[Mapping[str, tuple[float, ...]]] = {
    "sun": (20.0, 9.0, 12.0, 6.0, 8.0, 24.0, 16.0, 17.0, 22.0, 2.0, 3.0, 23.0),
    "moon": (26.0, 12.0, 13.0, 25.0, 24.0, 11.0, 26.0, 14.0, 13.0, 25.0, 5.0, 12.0),
    "mars": (19.0, 28.0, 25.0, 23.0, 29.0, 28.0, 14.0, 21.0, 2.0, 15.0, 11.0, 6.0),
    "mercury": (15.0, 14.0, 13.0, 12.0, 8.0, 18.0, 20.0, 10.0, 21.0, 22.0, 7.0, 5.0),
    "jupiter": (19.0, 29.0, 12.0, 27.0, 6.0, 4.0, 13.0, 10.0, 17.0, 11.0, 15.0, 28.0),
    "venus": (28.0, 15.0, 11.0, 17.0, 10.0, 13.0, 4.0, 6.0, 27.0, 12.0, 29.0, 19.0),
    "saturn": (10.0, 4.0, 7.0, 9.0, 12.0, 16.0, 3.0, 18.0, 28.0, 14.0, 13.0, 15.0),
    "rahu": (14.0, 13.0, 12.0, 11.0, 24.0, 23.0, 22.0, 21.0, 10.0, 20.0, 18.0, 8.0),
    "ketu": (8.0, 18.0, 20.0, 10.0, 21.0, 22.0, 23.0, 24.0, 11.0, 12.0, 13.0, 14.0),
    "lagna": (1.0, 9.0, 22.0, 22.0, 25.0, 2.0, 4.0, 23.0, 18.0, 20.0, 24.0, 10.0),
}


def _norm360(lon_deg: float) -> float:
    val = float(lon_deg)
    if not math.isfinite(val):
        raise ValueError("longitude must be a finite float")
    return val % 360.0


@dataclass(frozen=True)
class KharaDrekkanaInfo:
    """Details of the 22nd Drekkana (Khara Drekkana) from a reference longitude."""

    reference_drekkana_index: int
    khara_drekkana_index: int
    sign_index: int
    sign_name: str
    decanate_number: int
    degree_span: tuple[float, float]
    ecliptic_degree_span: tuple[float, float]
    d3_sign_index: int
    d3_sign_name: str
    ruling_planet: str
    swarupa: str
    secondary_tags: tuple[str, ...]
    description: str


@dataclass(frozen=True)
class KharaNavamsaInfo:
    """Details of the 64th Navamsa (Khara Navamsa) from a reference longitude."""

    reference_navamsa_index: int
    reference_d9_sign_index: int
    reference_d9_sign_name: str
    khara_navamsa_index: int
    d9_sign_index: int
    d9_sign_name: str
    ruling_planet: str
    d1_sign_index: int
    d1_sign_name: str
    degree_span: tuple[float, float]
    ecliptic_degree_span: tuple[float, float]

    @property
    def khara_lord(self) -> str:
        return self.ruling_planet


@dataclass(frozen=True)
class KharaDwadashamsaInfo:
    """Details of the 85th Dwadashamsa (Khara Dwadashamsa) from a reference longitude."""

    reference_d12_index: int
    reference_d12_sign_index: int
    reference_d12_sign_name: str
    khara_d12_index: int
    d12_sign_index: int
    d12_sign_name: str
    ruling_planet: str
    d1_sign_index: int
    d1_sign_name: str
    degree_span: tuple[float, float]
    ecliptic_degree_span: tuple[float, float]


@dataclass(frozen=True)
class KharaPointsReport:
    """Combined 22nd Drekkana, 64th Navamsa, and 85th Dwadashamsa vulnerability report."""

    label: str
    reference_lon_deg: float
    reference_sign_index: int
    reference_sign_name: str
    reference_degree_in_sign: float
    drekkana_22nd: KharaDrekkanaInfo
    navamsa_64th: KharaNavamsaInfo
    dwadashamsa_85th: KharaDwadashamsaInfo
    receipt_sha256: str

    @property
    def khara_drekkana(self) -> KharaDrekkanaInfo:
        return self.drekkana_22nd

    @property
    def khara_navamsa(self) -> KharaNavamsaInfo:
        return self.navamsa_64th

    @property
    def khara_dwadashamsa(self) -> KharaDwadashamsaInfo:
        return self.dwadashamsa_85th


@dataclass(frozen=True)
class MrityuBhagaEntry:
    """Mrityu Bhaga (fatal degree) diagnostic for a single planet or Lagna."""

    point: str
    longitude_deg: float
    sign_index: int
    sign_name: str
    degree_in_sign: float
    mrityu_bhaga_deg: float
    distance_deg: float
    orb_deg: float
    is_in_mrityu_bhaga: bool


@dataclass(frozen=True)
class MrityuBhagaReport:
    """Complete Mrityu Bhaga vulnerability report across planets and Lagna."""

    entries: Mapping[str, MrityuBhagaEntry]
    afflicted_points: tuple[str, ...]
    orb_deg: float
    receipt_sha256: str

    def __getitem__(self, key: str) -> MrityuBhagaEntry:
        norm_key = str(key).strip().lower()
        if norm_key == "ascendant":
            norm_key = "lagna"
        return self.entries[norm_key]


def compute_khara_points(
    reference_lon_deg: float,
    label: str = "lagna",
) -> KharaPointsReport:
    """Compute the 22nd Drekkana, 64th Navamsa, and 85th Dwadashamsa from ``reference_lon_deg``.

    Parameters
    ----------
    reference_lon_deg:
        Sidereal longitude of the reference point (e.g. Lagna, Moon, or Sun) in degrees.
    label:
        Identifier for the reference point (default ``"lagna"``).
    """
    ref_lon = _norm360(reference_lon_deg)
    ref_sign = int(ref_lon // 30.0) % 12
    ref_deg_in_sign = ref_lon % 30.0

    # 1. 22nd Drekkana (Khara Drekkana)
    ref_drekkana_idx = int(ref_lon / 10.0) % 36
    khara_drekkana_idx = (ref_drekkana_idx + 21) % 36
    cat_entry = DREKKANA_SWARUPA_CATALOG[khara_drekkana_idx]
    d3_ecliptic_start = float(khara_drekkana_idx * 10)
    d3_ecliptic_end = float((khara_drekkana_idx + 1) * 10)

    drekkana_22nd = KharaDrekkanaInfo(
        reference_drekkana_index=ref_drekkana_idx,
        khara_drekkana_index=khara_drekkana_idx,
        sign_index=cat_entry.sign_index,
        sign_name=cat_entry.sign_name,
        decanate_number=cat_entry.decanate_number,
        degree_span=cat_entry.degree_span_in_sign,
        ecliptic_degree_span=(d3_ecliptic_start, d3_ecliptic_end),
        d3_sign_index=cat_entry.d3_sign_index,
        d3_sign_name=cat_entry.d3_sign_name,
        ruling_planet=cat_entry.ruling_planet,
        swarupa=cat_entry.swarupa,
        secondary_tags=cat_entry.secondary_tags,
        description=cat_entry.description,
    )

    # 2. 64th Navamsa (Khara Navamsa)
    navamsa_span = 10.0 / 3.0
    ref_navamsa_idx = int(ref_lon / navamsa_span) % 108
    ref_d9_sign = ref_navamsa_idx % 12
    khara_navamsa_idx = (ref_navamsa_idx + 63) % 108
    khara_d9_sign = khara_navamsa_idx % 12
    khara_d9_lord = RASI_LORDS[khara_d9_sign].lower()

    khara_nav_d1_sign = khara_navamsa_idx // 9
    khara_nav_sub = khara_navamsa_idx % 9
    nav_start_in_sign = khara_nav_sub * navamsa_span
    nav_end_in_sign = (khara_nav_sub + 1) * navamsa_span
    nav_ecliptic_start = khara_navamsa_idx * navamsa_span
    nav_ecliptic_end = (khara_navamsa_idx + 1) * navamsa_span

    navamsa_64th = KharaNavamsaInfo(
        reference_navamsa_index=ref_navamsa_idx,
        reference_d9_sign_index=ref_d9_sign,
        reference_d9_sign_name=RASI_NAMES[ref_d9_sign],
        khara_navamsa_index=khara_navamsa_idx,
        d9_sign_index=khara_d9_sign,
        d9_sign_name=RASI_NAMES[khara_d9_sign],
        ruling_planet=khara_d9_lord,
        d1_sign_index=khara_nav_d1_sign,
        d1_sign_name=RASI_NAMES[khara_nav_d1_sign],
        degree_span=(nav_start_in_sign, nav_end_in_sign),
        ecliptic_degree_span=(nav_ecliptic_start, nav_ecliptic_end),
    )

    # 3. 85th Dwadashamsa (Khara Dwadashamsa)
    d12_span = 2.5
    ref_d12_idx = int(ref_lon / d12_span) % 144
    ref_d12_sub = ref_d12_idx % 12
    ref_d12_sign = (ref_sign + ref_d12_sub) % 12

    khara_d12_idx = (ref_d12_idx + 84) % 144
    khara_d12_d1_sign = khara_d12_idx // 12
    khara_d12_sub = khara_d12_idx % 12
    khara_d12_sign = (khara_d12_d1_sign + khara_d12_sub) % 12
    khara_d12_lord = RASI_LORDS[khara_d12_sign].lower()

    d12_start_in_sign = khara_d12_sub * d12_span
    d12_end_in_sign = (khara_d12_sub + 1) * d12_span
    d12_ecliptic_start = khara_d12_idx * d12_span
    d12_ecliptic_end = (khara_d12_idx + 1) * d12_span

    dwadashamsa_85th = KharaDwadashamsaInfo(
        reference_d12_index=ref_d12_idx,
        reference_d12_sign_index=ref_d12_sign,
        reference_d12_sign_name=RASI_NAMES[ref_d12_sign],
        khara_d12_index=khara_d12_idx,
        d12_sign_index=khara_d12_sign,
        d12_sign_name=RASI_NAMES[khara_d12_sign],
        ruling_planet=khara_d12_lord,
        d1_sign_index=khara_d12_d1_sign,
        d1_sign_name=RASI_NAMES[khara_d12_d1_sign],
        degree_span=(d12_start_in_sign, d12_end_in_sign),
        ecliptic_degree_span=(d12_ecliptic_start, d12_ecliptic_end),
    )

    clean_label = str(label).strip() or "lagna"
    receipt = canonical_hash(
        {
            "engine": "khara_points",
            "label": clean_label,
            "reference_lon_deg": round(ref_lon, 9),
            "khara_drekkana_index": khara_drekkana_idx,
            "khara_drekkana_swarupa": drekkana_22nd.swarupa,
            "khara_navamsa_index": khara_navamsa_idx,
            "khara_navamsa_d9_sign": khara_d9_sign,
            "khara_d12_index": khara_d12_idx,
            "khara_d12_sign": khara_d12_sign,
        }
    )

    return KharaPointsReport(
        label=clean_label,
        reference_lon_deg=ref_lon,
        reference_sign_index=ref_sign,
        reference_sign_name=RASI_NAMES[ref_sign],
        reference_degree_in_sign=ref_deg_in_sign,
        drekkana_22nd=drekkana_22nd,
        navamsa_64th=navamsa_64th,
        dwadashamsa_85th=dwadashamsa_85th,
        receipt_sha256=receipt,
    )


def evaluate_mrityu_bhaga(
    planet_longitudes: Mapping[str, float],
    lagna_lon_deg: float | None = None,
    orb_deg: float = 1.0,
) -> MrityuBhagaReport:
    """Evaluate Mrityu Bhaga (fatal degree) proximity for all supplied planets and Lagna.

    Parameters
    ----------
    planet_longitudes:
        Mapping of planet names (``sun``, ``moon``, ``mars``, ``mercury``, ``jupiter``,
        ``venus``, ``saturn``, ``rahu``, ``ketu``, and optionally ``lagna``) to sidereal
        longitudes in degrees ``[0, 360)``.
    lagna_lon_deg:
        Optional sidereal longitude of Lagna (Ascendant) in degrees ``[0, 360)``.
    orb_deg:
        Maximum distance in degrees within the sign to flag ``is_in_mrityu_bhaga=True``.
        Defaults to ``1.0`` degree.
    """
    max_orb = float(orb_deg)
    if not math.isfinite(max_orb) or max_orb < 0.0:
        raise ValueError("orb_deg must be a non-negative finite float")

    combined: dict[str, float] = {}
    for raw_name, raw_lon in planet_longitudes.items():
        p_name = str(raw_name).strip().lower()
        if p_name == "ascendant":
            p_name = "lagna"
        if p_name not in MRITYU_BHAGA_DEGREE_TABLE:
            raise ValueError(f"unsupported Mrityu Bhaga point: {raw_name!r}")
        combined[p_name] = _norm360(raw_lon)

    if lagna_lon_deg is not None:
        combined["lagna"] = _norm360(lagna_lon_deg)

    if not combined:
        raise ValueError("at least one planet or lagna longitude must be provided")

    canonical_order = ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu", "lagna")
    ordered_keys = [k for k in canonical_order if k in combined]

    entries: dict[str, MrityuBhagaEntry] = {}
    afflicted: list[str] = []

    for point in ordered_keys:
        lon = combined[point]
        sign_idx = int(lon // 30.0) % 12
        deg_in_sign = lon % 30.0
        fatal_deg = MRITYU_BHAGA_DEGREE_TABLE[point][sign_idx]
        dist = abs(deg_in_sign - fatal_deg)
        in_mb = dist <= max_orb
        if in_mb:
            afflicted.append(point)
        entries[point] = MrityuBhagaEntry(
            point=point,
            longitude_deg=lon,
            sign_index=sign_idx,
            sign_name=RASI_NAMES[sign_idx],
            degree_in_sign=deg_in_sign,
            mrityu_bhaga_deg=fatal_deg,
            distance_deg=dist,
            orb_deg=max_orb,
            is_in_mrityu_bhaga=in_mb,
        )

    receipt = canonical_hash(
        {
            "engine": "mrityu_bhaga",
            "orb_deg": round(max_orb, 9),
            "points": {
                k: {
                    "lon_deg": round(v.longitude_deg, 9),
                    "sign_index": v.sign_index,
                    "mrityu_bhaga_deg": v.mrityu_bhaga_deg,
                    "distance_deg": round(v.distance_deg, 9),
                    "is_in_mrityu_bhaga": v.is_in_mrityu_bhaga,
                }
                for k, v in entries.items()
            },
        }
    )

    return MrityuBhagaReport(
        entries=entries,
        afflicted_points=tuple(afflicted),
        orb_deg=max_orb,
        receipt_sha256=receipt,
    )


__all__ = [
    "DREKKANA_SWARUPA_CATALOG",
    "DREKKANA_SWARUPA_CATEGORIES",
    "DrekkanaSwarupaEntry",
    "KharaDrekkanaInfo",
    "KharaDwadashamsaInfo",
    "KharaNavamsaInfo",
    "KharaPointsReport",
    "MRITYU_BHAGA_DEGREE_TABLE",
    "MrityuBhagaEntry",
    "MrityuBhagaReport",
    "compute_khara_points",
    "evaluate_mrityu_bhaga",
]
