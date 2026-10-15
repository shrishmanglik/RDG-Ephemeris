"""Clean-room Kerala Prashna Marga Sphutas, 11 Classical Upagrahas, and Horary Arudha Engine.

Mathematical formulations follow *Prashna Marga*, *Brihat Parashara Hora Shastra*,
*Uttara Kalamrita*, and *Phaladeepika*:
- 11 Classical Upagrahas (Sub-Planets):
  - 5 Solar Mathematical Upagrahas (Dhoomadi Group): Dhuma, Vyatipata, Parivesha,
    Indrachapa (Kodanda), and Upaketu (Sikhi).
  - 6 Time-Division Upagrahas (Kalavela Group): Gulika (and Mandi), Kala, Mrityu,
    Ardhaprahara, Yamaghantaka, and ochcha, dividing daytime or nighttime into
    8 equal octants ruled from the weekday lord (Day) or 5th lord from weekday lord (Night).
- Kerala Prashna Sphutas (*Prashna Marga*):
  - Trisphuta, Chatusphuta, Panchasphuta
  - Prana Sphuta, Deha Sphuta, Mrityu Sphuta
  - Tithi Sphuta, Kshetra Sphuta (female fertility), and Beeja Sphuta (male virility).
- Horary Sign Classifications & Arudha:
  - Udaya mode: Shirshodaya (Gemini, Leo, Virgo, Libra, Scorpio, Aquarius),
    Prishtodaya (Aries, Taurus, Cancer, Sagittarius, Capricorn), Ubhayodaya (Pisces).
  - Substance category: Dhatu (Mineral - Movable signs), Moola (Plant - Fixed signs),
    Jeeva (Living - Dual signs).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Final, Mapping

from .._version import __version__
from ..engine.receipt import canonical_hash
from ..jyotish.nakshatra import NakshatraPosition, RASI_NAMES, nakshatra_position, normalize_degrees
from ..jyotish.panchanga import compute_vara

# 5 Solar Mathematical Upagrahas (Dhoomadi group)
SOLAR_UPAGRAHA_NAMES: Final[tuple[str, ...]] = (
    "Dhuma",
    "Vyatipata",
    "Parivesha",
    "Indrachapa",
    "Upaketu",
)

# 6 Time-Division Upagrahas (Kalavela group) and their planetary weekday indices (0=Sun..6=Sat)
KALAVELA_UPAGRAHA_NAMES: Final[tuple[str, ...]] = (
    "Gulika",
    "Kala",
    "Mrityu",
    "Ardhaprahara",
    "Yamaghantaka",
    "ochcha",
)

KALAVELA_RULER_VARA_INDEX: Final[Mapping[str, tuple[int, str]]] = {
    "Gulika": (6, "Saturn"),
    "Kala": (0, "Sun"),
    "Mrityu": (2, "Mars"),
    "Ardhaprahara": (3, "Mercury"),
    "Yamaghantaka": (4, "Jupiter"),
    "ochcha": (5, "Venus"),
}

UPAGRAHA_11_NAMES: Final[tuple[str, ...]] = SOLAR_UPAGRAHA_NAMES + KALAVELA_UPAGRAHA_NAMES

# Sign rising classifications (0-based sign indices 0..11)
SHIRSHODAYA_SIGNS: Final[frozenset[int]] = frozenset({2, 4, 5, 6, 7, 10})  # Gemini, Leo, Virgo, Libra, Scorpio, Aquarius
PRISHTODAYA_SIGNS: Final[frozenset[int]] = frozenset({0, 1, 3, 8, 9})      # Aries, Taurus, Cancer, Sagittarius, Capricorn
UBHAYODAYA_SIGNS: Final[frozenset[int]] = frozenset({11})                  # Pisces

# Dhatu (Mineral / Movable), Moola (Plant / Fixed), Jeeva (Living / Dual) sign indices (0..11)
DHATU_SIGNS: Final[frozenset[int]] = frozenset({0, 3, 6, 9})
MOOLA_SIGNS: Final[frozenset[int]] = frozenset({1, 4, 7, 10})
JEEVA_SIGNS: Final[frozenset[int]] = frozenset({2, 5, 8, 11})

SIDEREAL_ROTATION_DEG_PER_DAY: Final[float] = 360.98564736629


@dataclass(frozen=True)
class SolarUpagrahaPoint:
    """One mathematical Solar Upagraha (Dhoomadi group)."""

    name: str
    alias: str
    longitude_deg: float
    sign_index: int
    sign_name: str
    degree_in_sign: float
    nakshatra: NakshatraPosition


@dataclass(frozen=True)
class KalavelaUpagrahaPoint:
    """One time-division Upagraha (Kalavela group) with transition JD and sidereal longitude."""

    name: str
    ruling_planet: str
    is_daytime: bool
    octant_number: int
    start_jd: float
    mid_jd: float
    end_jd: float
    transition_jd: float
    longitude_deg: float
    sign_index: int
    sign_name: str
    degree_in_sign: float
    nakshatra: NakshatraPosition


@dataclass(frozen=True)
class UpagrahaSet:
    """Complete set of 11 classical Upagrahas (5 Solar + 6 Kalavela, plus Mandi alias)."""

    dhuma: SolarUpagrahaPoint
    vyatipata: SolarUpagrahaPoint
    parivesha: SolarUpagrahaPoint
    indrachapa: SolarUpagrahaPoint
    upaketu: SolarUpagrahaPoint
    gulika: KalavelaUpagrahaPoint
    mandi: KalavelaUpagrahaPoint
    kala: KalavelaUpagrahaPoint
    mrityu: KalavelaUpagrahaPoint
    ardhaprahara: KalavelaUpagrahaPoint
    yamaghantaka: KalavelaUpagrahaPoint
    ochcha: KalavelaUpagrahaPoint
    solar_upagrahas: Mapping[str, SolarUpagrahaPoint]
    kalavela_upagrahas: Mapping[str, KalavelaUpagrahaPoint]
    all_11_longitudes: Mapping[str, float]


@dataclass(frozen=True)
class SphutaPoint:
    """Computed longitude, sign, and nakshatra of a Prashna Sphuta."""

    name: str
    longitude_deg: float
    sign_index: int
    sign_name: str
    degree_in_sign: float
    nakshatra: NakshatraPosition


@dataclass(frozen=True)
class PrashnaSphutaSet:
    """Complete Kerala *Prashna Marga* Sphuta suite."""

    trisphuta: SphutaPoint
    chatusphuta: SphutaPoint
    panchasphuta: SphutaPoint
    prana_sphuta: SphutaPoint
    deha_sphuta: SphutaPoint
    mrityu_sphuta: SphutaPoint
    tithi_sphuta: SphutaPoint
    kshetra_sphuta: SphutaPoint
    beeja_sphuta: SphutaPoint
    vitality_conjunction_warning: bool


@dataclass(frozen=True)
class PrashnaSignClassification:
    """Horary classification of a zodiacal sign (Udaya mode, Dhatu/Moola/Jeeva, mobility)."""

    sign_index: int
    sign_number: int
    sign_name: str
    udaya_type: str
    substance_type: str
    mobility_type: str
    is_shirshodaya: bool
    is_prishtodaya: bool
    is_ubhayodaya: bool
    is_dhatu: bool
    is_moola: bool
    is_jeeva: bool


@dataclass(frozen=True)
class PrashnaArudhaResult:
    """Horary Arudha and Chatra Rasi derived from a query seed number (1..108) and Sun/Lagna."""

    seed_number: int
    arudha_sign_index: int
    arudha_sign_name: str
    arudha_longitude_deg: float
    udaya_lagna_sign_index: int
    udaya_lagna_sign_name: str
    veethya_sign_index: int
    chatra_sign_index: int
    chatra_sign_name: str
    arudha_classification: PrashnaSignClassification


@dataclass(frozen=True)
class PrashnaAnalysis:
    """Full Kerala Prashna Marga horary analysis with deterministic SHA-256 receipt."""

    jd_ut: float
    is_daytime: bool
    vara_index: int
    vara_name: str
    upagrahas: UpagrahaSet
    sphutas: PrashnaSphutaSet
    lagna_classification: PrashnaSignClassification
    moon_classification: PrashnaSignClassification
    arudha: PrashnaArudhaResult
    receipt: Mapping[str, Any]
    receipt_sha256: str


def _make_solar_point(name: str, alias: str, lon_deg: float) -> SolarUpagrahaPoint:
    lon = normalize_degrees(lon_deg)
    s_idx = min(int(lon // 30.0), 11)
    deg_in = lon - s_idx * 30.0
    return SolarUpagrahaPoint(
        name=name,
        alias=alias,
        longitude_deg=lon,
        sign_index=s_idx,
        sign_name=RASI_NAMES[s_idx],
        degree_in_sign=deg_in,
        nakshatra=nakshatra_position(lon),
    )


def compute_solar_upagrahas(sun_lon_deg: float) -> Mapping[str, SolarUpagrahaPoint]:
    """Compute the 5 mathematical Solar Upagrahas (Dhoomadi group) from sidereal solar longitude.

    Formulas (*Brihat Parashara Hora Shastra*):
    1. `Dhuma` = `(sun_lon_deg + 133 deg 20 min) % 360`
    2. `Vyatipata` = `(360 - Dhuma) % 360`
    3. `Parivesha` = `(Vyatipata + 180) % 360`
    4. `Indrachapa` (`Kodanda`) = `(360 - Parivesha) % 360`
    5. `Upaketu` (`Sikhi`) = `(Indrachapa + 16 deg 40 min) % 360` = `(sun_lon_deg - 30) % 360`
    """
    s_lon = normalize_degrees(sun_lon_deg)
    dhuma_lon = normalize_degrees(s_lon + (133.0 + 20.0 / 60.0))
    vyatipata_lon = normalize_degrees(360.0 - dhuma_lon)
    parivesha_lon = normalize_degrees(vyatipata_lon + 180.0)
    indrachapa_lon = normalize_degrees(360.0 - parivesha_lon)
    upaketu_lon = normalize_degrees(indrachapa_lon + (16.0 + 40.0 / 60.0))

    return {
        "Dhuma": _make_solar_point("Dhuma", "Dhuma", dhuma_lon),
        "Vyatipata": _make_solar_point("Vyatipata", "Vyatipata", vyatipata_lon),
        "Parivesha": _make_solar_point("Parivesha", "Parivesha", parivesha_lon),
        "Indrachapa": _make_solar_point("Indrachapa", "Kodanda", indrachapa_lon),
        "Upaketu": _make_solar_point("Upaketu", "Sikhi", upaketu_lon),
    }


def compute_kalavela_upagrahas(
    sunrise_jd: float,
    sunset_jd: float,
    *,
    next_sunrise_jd: float | None = None,
    is_daytime: bool = True,
    vara_index: int | None = None,
    reference_jd: float | None = None,
    reference_lagna_deg: float = 0.0,
    ascendant_fn: Callable[[float], float] | None = None,
) -> Mapping[str, KalavelaUpagrahaPoint]:
    """Compute the 6 Time-Division Upagrahas (Kalavela group: `Gulika`, `Kala`, `Mrityu`,
    `Ardhaprahara`, `Yamaghantaka`, `ochcha`, plus `Mandi`).

    Divides daytime (`sunrise_jd` to `sunset_jd`) or nighttime (`sunset_jd` to `next_sunrise_jd`)
    into 8 equal parts.
    - Daytime: Part 1 starts with the weekday lord (`vara_index`), proceeding in weekday order
      through Part 7; Part 8 is lordless.
    - Nighttime: Part 1 starts with the 5th lord from the weekday lord (`(vara_index + 4) % 7`),
      proceeding in weekday order through Part 7; Part 8 is lordless.
    """
    if sunset_jd <= sunrise_jd:
        raise ValueError("sunset_jd must be greater than sunrise_jd")
    next_sr = float(next_sunrise_jd) if next_sunrise_jd is not None else (float(sunrise_jd) + 1.0)
    if next_sr <= sunset_jd:
        raise ValueError("next_sunrise_jd must be greater than sunset_jd")

    vara = compute_vara(sunrise_jd, sunrise_jd_ut=sunrise_jd, vara_index=vara_index)
    w_idx = vara.index

    if is_daytime:
        span_start = float(sunrise_jd)
        octant_step = (float(sunset_jd) - float(sunrise_jd)) / 8.0
        first_lord_idx = w_idx
    else:
        span_start = float(sunset_jd)
        octant_step = (next_sr - float(sunset_jd)) / 8.0
        first_lord_idx = (w_idx + 4) % 7

    ref_jd = float(reference_jd) if reference_jd is not None else float(sunrise_jd)
    ref_lagna = normalize_degrees(reference_lagna_deg)

    def _resolve_lon(target_jd: float) -> float:
        if ascendant_fn is not None:
            return normalize_degrees(ascendant_fn(target_jd))
        return normalize_degrees(ref_lagna + (target_jd - ref_jd) * SIDEREAL_ROTATION_DEG_PER_DAY)

    out: dict[str, KalavelaUpagrahaPoint] = {}
    for name in KALAVELA_UPAGRAHA_NAMES:
        planet_idx, planet_name = KALAVELA_RULER_VARA_INDEX[name]
        octant_1based = ((planet_idx - first_lord_idx) % 7) + 1
        s_jd = span_start + (octant_1based - 1) * octant_step
        e_jd = span_start + octant_1based * octant_step
        m_jd = 0.5 * (s_jd + e_jd)
        # Classical *Brihat Parashara Hora Shastra* cusp rises at the start of the planet's octant
        t_jd = s_jd
        lon = _resolve_lon(t_jd)
        s_idx = min(int(lon // 30.0), 11)
        deg_in = lon - s_idx * 30.0
        out[name] = KalavelaUpagrahaPoint(
            name=name,
            ruling_planet=planet_name,
            is_daytime=bool(is_daytime),
            octant_number=octant_1based,
            start_jd=s_jd,
            mid_jd=m_jd,
            end_jd=e_jd,
            transition_jd=t_jd,
            longitude_deg=lon,
            sign_index=s_idx,
            sign_name=RASI_NAMES[s_idx],
            degree_in_sign=deg_in,
            nakshatra=nakshatra_position(lon),
        )

    # Provide Mandi (Saturn's Kalavela at mid-octant or start-octant; linked to Saturn's octant)
    gul = out["Gulika"]
    mandi_lon = _resolve_lon(gul.mid_jd)
    m_s_idx = min(int(mandi_lon // 30.0), 11)
    out["Mandi"] = KalavelaUpagrahaPoint(
        name="Mandi",
        ruling_planet="Saturn",
        is_daytime=gul.is_daytime,
        octant_number=gul.octant_number,
        start_jd=gul.start_jd,
        mid_jd=gul.mid_jd,
        end_jd=gul.end_jd,
        transition_jd=gul.mid_jd,
        longitude_deg=mandi_lon,
        sign_index=m_s_idx,
        sign_name=RASI_NAMES[m_s_idx],
        degree_in_sign=mandi_lon - m_s_idx * 30.0,
        nakshatra=nakshatra_position(mandi_lon),
    )
    return out


def compute_11_upagrahas(
    sun_lon_deg: float,
    sunrise_jd: float,
    sunset_jd: float,
    *,
    jd_ut: float | None = None,
    next_sunrise_jd: float | None = None,
    vara_index: int | None = None,
    lagna_lon_deg: float = 0.0,
    ascendant_fn: Callable[[float], float] | None = None,
) -> UpagrahaSet:
    """Compute all 11 classical Upagrahas (5 Solar + 6 Kalavela, plus Mandi)."""
    q_jd = float(jd_ut) if jd_ut is not None else float(sunrise_jd)
    is_day = float(sunrise_jd) <= q_jd < float(sunset_jd)

    solar = compute_solar_upagrahas(sun_lon_deg)
    kalavela = compute_kalavela_upagrahas(
        sunrise_jd,
        sunset_jd,
        next_sunrise_jd=next_sunrise_jd,
        is_daytime=is_day,
        vara_index=vara_index,
        reference_jd=q_jd,
        reference_lagna_deg=lagna_lon_deg,
        ascendant_fn=ascendant_fn,
    )

    all_11: dict[str, float] = {k: solar[k].longitude_deg for k in SOLAR_UPAGRAHA_NAMES}
    for k in KALAVELA_UPAGRAHA_NAMES:
        all_11[k] = kalavela[k].longitude_deg

    return UpagrahaSet(
        dhuma=solar["Dhuma"],
        vyatipata=solar["Vyatipata"],
        parivesha=solar["Parivesha"],
        indrachapa=solar["Indrachapa"],
        upaketu=solar["Upaketu"],
        gulika=kalavela["Gulika"],
        mandi=kalavela["Mandi"],
        kala=kalavela["Kala"],
        mrityu=kalavela["Mrityu"],
        ardhaprahara=kalavela["Ardhaprahara"],
        yamaghantaka=kalavela["Yamaghantaka"],
        ochcha=kalavela["ochcha"],
        solar_upagrahas=solar,
        kalavela_upagrahas=kalavela,
        all_11_longitudes=all_11,
    )


def _make_sphuta(name: str, lon_deg: float) -> SphutaPoint:
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


def compute_prashna_sphutas(
    lagna_deg: float,
    sun_deg: float,
    moon_deg: float,
    gulika_deg: float,
    *,
    rahu_deg: float = 0.0,
    mars_deg: float = 0.0,
    jupiter_deg: float = 0.0,
    venus_deg: float = 0.0,
) -> PrashnaSphutaSet:
    """Compute the classical *Prashna Marga* Sphutas:
    - `Trisphuta` = `(lagna_deg + moon_deg + gulika_deg) % 360`
    - `Chatusphuta` = `(trisphuta + sun_deg) % 360`
    - `Panchasphuta` = `(chatusphuta + rahu_deg) % 360`
    - `Prana Sphuta` = `(5.0 * lagna_deg + gulika_deg) % 360`
    - `Deha Sphuta` = `(8.0 * moon_deg + gulika_deg) % 360`
    - `Mrityu Sphuta` = `(7.0 * gulika_deg + sun_deg) % 360`
    - `Tithi Sphuta` = `(lagna_deg + moon_deg - sun_deg) % 360`
    - `Kshetra Sphuta` (female fertility) = `(moon_deg + mars_deg + jupiter_deg) % 360`
    - `Beeja Sphuta` (male virility) = `(sun_deg + venus_deg + jupiter_deg) % 360`
    """
    l_deg = normalize_degrees(lagna_deg)
    s_deg = normalize_degrees(sun_deg)
    m_deg = normalize_degrees(moon_deg)
    g_deg = normalize_degrees(gulika_deg)
    r_deg = normalize_degrees(rahu_deg)
    ma_deg = normalize_degrees(mars_deg)
    ju_deg = normalize_degrees(jupiter_deg)
    ve_deg = normalize_degrees(venus_deg)

    tri_lon = normalize_degrees(l_deg + m_deg + g_deg)
    chatu_lon = normalize_degrees(tri_lon + s_deg)
    pancha_lon = normalize_degrees(chatu_lon + r_deg)

    prana_lon = normalize_degrees(5.0 * l_deg + g_deg)
    deha_lon = normalize_degrees(8.0 * m_deg + g_deg)
    mrityu_lon = normalize_degrees(7.0 * g_deg + s_deg)

    tithi_lon = normalize_degrees(l_deg + (m_deg - s_deg))
    kshetra_lon = normalize_degrees(m_deg + ma_deg + ju_deg)
    beeja_lon = normalize_degrees(s_deg + ve_deg + ju_deg)

    prana_pt = _make_sphuta("Prana Sphuta", prana_lon)
    deha_pt = _make_sphuta("Deha Sphuta", deha_lon)
    mrityu_pt = _make_sphuta("Mrityu Sphuta", mrityu_lon)

    # Warning if Mrityu Sphuta shares the same nakshatra as Prana or Deha Sphuta
    vitality_warn = (
        mrityu_pt.nakshatra.index == prana_pt.nakshatra.index
        or mrityu_pt.nakshatra.index == deha_pt.nakshatra.index
    )

    return PrashnaSphutaSet(
        trisphuta=_make_sphuta("Trisphuta", tri_lon),
        chatusphuta=_make_sphuta("Chatusphuta", chatu_lon),
        panchasphuta=_make_sphuta("Panchasphuta", pancha_lon),
        prana_sphuta=prana_pt,
        deha_sphuta=deha_pt,
        mrityu_sphuta=mrityu_pt,
        tithi_sphuta=_make_sphuta("Tithi Sphuta", tithi_lon),
        kshetra_sphuta=_make_sphuta("Kshetra Sphuta", kshetra_lon),
        beeja_sphuta=_make_sphuta("Beeja Sphuta", beeja_lon),
        vitality_conjunction_warning=vitality_warn,
    )


def classify_prashna_sign(sign_index: int) -> PrashnaSignClassification:
    """Classify a 0-based zodiacal sign (`0..11`, Mesha..Meena) by its Udaya rising mode
    (`Shirshodaya`, `Prishtodaya`, `Ubhayodaya`), substance (`Dhatu`, `Moola`, `Jeeva`),
    and mobility (`Chara`, `Sthira`, `Dwiswabhava`).
    """
    if not 0 <= int(sign_index) <= 11:
        raise ValueError("sign_index must be in 0..11")
    idx = int(sign_index)

    is_shirsha = idx in SHIRSHODAYA_SIGNS
    is_prishta = idx in PRISHTODAYA_SIGNS
    is_ubhaya = idx in UBHAYODAYA_SIGNS
    if is_shirsha:
        udaya = "Shirshodaya"
    elif is_prishta:
        udaya = "Prishtodaya"
    else:
        udaya = "Ubhayodaya"

    is_dhatu = idx in DHATU_SIGNS
    is_moola = idx in MOOLA_SIGNS
    is_jeeva = idx in JEEVA_SIGNS
    if is_dhatu:
        substance = "Dhatu"
        mobility = "Chara (Movable)"
    elif is_moola:
        substance = "Moola"
        mobility = "Sthira (Fixed)"
    else:
        substance = "Jeeva"
        mobility = "Dwiswabhava (Dual)"

    return PrashnaSignClassification(
        sign_index=idx,
        sign_number=idx + 1,
        sign_name=RASI_NAMES[idx],
        udaya_type=udaya,
        substance_type=substance,
        mobility_type=mobility,
        is_shirshodaya=is_shirsha,
        is_prishtodaya=is_prishta,
        is_ubhayodaya=is_ubhaya,
        is_dhatu=is_dhatu,
        is_moola=is_moola,
        is_jeeva=is_jeeva,
    )


def compute_prashna_arudha(
    seed_number: int,
    lagna_lon_deg: float,
    sun_lon_deg: float,
) -> PrashnaArudhaResult:
    """Compute the Kerala *Prashna Marga* Horary Arudha Lagna and Chatra Rasi from a seed number `1..108`.

    - In the 108-Ashtamangala/Navamsa horary system, `seed_number` in `1..108` maps to
      `(seed_number - 1) % 12` as the Arudha Rasi (`0..11`).
    - The Sun's sign determines the Veethya (solar street) sign (`Mesha..Meena`), and
      counting from the Veethya or Udaya Lagna to the Arudha Lagna yields the Chatra
      (umbrella/royal canopy) Rasi.
    """
    if not 1 <= int(seed_number) <= 108:
        raise ValueError("seed_number must be in 1..108")
    seed = int(seed_number)
    arudha_sign = (seed - 1) % 12
    pada_in_sign = ((seed - 1) // 12) % 9
    arudha_lon = arudha_sign * 30.0 + (pada_in_sign + 0.5) * (30.0 / 9.0)

    udaya_sign = min(int(normalize_degrees(lagna_lon_deg) // 30.0), 11)
    sun_sign = min(int(normalize_degrees(sun_lon_deg) // 30.0), 11)

    # Classical Veethya anchor (*Prashna Marga*): Mesha(0) for Sun in Taurus..Leo,
    # Mithuna(2) for Sun in Virgo..Sagittarius, Vrishabha(1) for Sun in Capricorn..Aries
    if sun_sign in (1, 2, 3, 4):
        veethya = 0
    elif sun_sign in (5, 6, 7, 8):
        veethya = 2
    else:
        veethya = 1

    offset_from_udaya = (arudha_sign - udaya_sign) % 12
    chatra_sign = (veethya + offset_from_udaya) % 12

    return PrashnaArudhaResult(
        seed_number=seed,
        arudha_sign_index=arudha_sign,
        arudha_sign_name=RASI_NAMES[arudha_sign],
        arudha_longitude_deg=arudha_lon,
        udaya_lagna_sign_index=udaya_sign,
        udaya_lagna_sign_name=RASI_NAMES[udaya_sign],
        veethya_sign_index=veethya,
        chatra_sign_index=chatra_sign,
        chatra_sign_name=RASI_NAMES[chatra_sign],
        arudha_classification=classify_prashna_sign(arudha_sign),
    )


def compute_prashna_analysis(
    planet_longitudes: Mapping[str, float],
    lagna_lon_deg: float,
    *,
    jd_ut: float = 2451545.0,
    sunrise_jd: float = 2451544.75,
    sunset_jd: float = 2451545.25,
    next_sunrise_jd: float | None = None,
    vara_index: int | None = None,
    seed_number: int = 1,
    ascendant_fn: Callable[[float], float] | None = None,
) -> PrashnaAnalysis:
    """Compute a complete Kerala *Prashna Marga* analysis (11 Upagrahas, 9 Sphutas, Sign
    Classifications, and Horary Arudha) with an auditable SHA-256 receipt.
    """
    norm_lons = {k.strip().capitalize(): normalize_degrees(v) for k, v in planet_longitudes.items()}
    for req in ("Sun", "Moon", "Mars", "Jupiter", "Venus"):
        if req not in norm_lons:
            raise ValueError(f"Missing required planet {req!r} in planet_longitudes")
    rahu_lon = norm_lons.get("Rahu", 0.0)
    l_lon = normalize_degrees(lagna_lon_deg)

    vara = compute_vara(jd_ut, sunrise_jd_ut=sunrise_jd, vara_index=vara_index)
    is_day = float(sunrise_jd) <= float(jd_ut) < float(sunset_jd)

    upagrahas = compute_11_upagrahas(
        norm_lons["Sun"],
        sunrise_jd,
        sunset_jd,
        jd_ut=jd_ut,
        next_sunrise_jd=next_sunrise_jd,
        vara_index=vara.index,
        lagna_lon_deg=l_lon,
        ascendant_fn=ascendant_fn,
    )

    sphutas = compute_prashna_sphutas(
        lagna_deg=l_lon,
        sun_deg=norm_lons["Sun"],
        moon_deg=norm_lons["Moon"],
        gulika_deg=upagrahas.gulika.longitude_deg,
        rahu_deg=rahu_lon,
        mars_deg=norm_lons["Mars"],
        jupiter_deg=norm_lons["Jupiter"],
        venus_deg=norm_lons["Venus"],
    )

    lagna_sign = min(int(l_lon // 30.0), 11)
    moon_sign = min(int(norm_lons["Moon"] // 30.0), 11)
    lagna_cls = classify_prashna_sign(lagna_sign)
    moon_cls = classify_prashna_sign(moon_sign)
    arudha = compute_prashna_arudha(seed_number, l_lon, norm_lons["Sun"])

    receipt = {
        "module": "ephemeris_oss.jyotish_transit.prashna",
        "version": __version__,
        "jd_ut": float(jd_ut),
        "is_daytime": is_day,
        "vara": vara.english_name,
        "upagraha_longitudes": {k: round(v, 8) for k, v in upagrahas.all_11_longitudes.items()},
        "trisphuta_deg": round(sphutas.trisphuta.longitude_deg, 8),
        "chatusphuta_deg": round(sphutas.chatusphuta.longitude_deg, 8),
        "panchasphuta_deg": round(sphutas.panchasphuta.longitude_deg, 8),
        "prana_sphuta_deg": round(sphutas.prana_sphuta.longitude_deg, 8),
        "deha_sphuta_deg": round(sphutas.deha_sphuta.longitude_deg, 8),
        "mrityu_sphuta_deg": round(sphutas.mrityu_sphuta.longitude_deg, 8),
        "arudha_sign": arudha.arudha_sign_name,
        "chatra_sign": arudha.chatra_sign_name,
    }
    receipt_sha256 = canonical_hash(receipt)

    return PrashnaAnalysis(
        jd_ut=float(jd_ut),
        is_daytime=is_day,
        vara_index=vara.index,
        vara_name=vara.english_name,
        upagrahas=upagrahas,
        sphutas=sphutas,
        lagna_classification=lagna_cls,
        moon_classification=moon_cls,
        arudha=arudha,
        receipt=receipt,
        receipt_sha256=receipt_sha256,
    )


__all__ = [
    "DHATU_SIGNS",
    "JEEVA_SIGNS",
    "KALAVELA_RULER_VARA_INDEX",
    "KALAVELA_UPAGRAHA_NAMES",
    "KalavelaUpagrahaPoint",
    "MOOLA_SIGNS",
    "PRISHTODAYA_SIGNS",
    "PrashnaAnalysis",
    "PrashnaArudhaResult",
    "PrashnaSignClassification",
    "PrashnaSphutaSet",
    "SHIRSHODAYA_SIGNS",
    "SIDEREAL_ROTATION_DEG_PER_DAY",
    "SOLAR_UPAGRAHA_NAMES",
    "SolarUpagrahaPoint",
    "SphutaPoint",
    "UBHAYODAYA_SIGNS",
    "UPAGRAHA_11_NAMES",
    "UpagrahaSet",
    "classify_prashna_sign",
    "compute_11_upagrahas",
    "compute_kalavela_upagrahas",
    "compute_prashna_analysis",
    "compute_prashna_arudha",
    "compute_prashna_sphutas",
    "compute_solar_upagrahas",
]
