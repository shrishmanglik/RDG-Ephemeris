"""Clean-room Surya Siddhanta (c. 400-500 CE) Madhyama and Spashta planetary engine.

Implements the classical Indian astronomical treatise *Surya Siddhanta*
(*Madhyamadhikara* Chapter 1 and *Spashtadhikara* Chapter 2):
1. **Kali Yuga Epoch and Ahargana**:
   - Kali Yuga midnight/mean epoch at Ujjain prime meridian (`18 February 3102 BCE
     00:00 Ujjain Mean Time`, Julian Date `JD = 588465.5`).
   - *Ahargana* (`compute_ahargana(jd_ut)`): civil (*Savana*) days elapsed since
     the Kali Yuga epoch (`jd_ut - 588465.5`).
2. **Mahayuga Constants and Bhagana Revolution Counts**:
   - One *Mahayuga* (*Chaturyuga*) spans `4,320,000` sidereal solar years and
     `1,577,917,828` civil *Savana* days (*Surya Siddhanta* 1.29-37).
   - Planetary revolutions (*Bhagana*) per *Mahayuga*:
     * Sun (`sun`): `4,320,000`
     * Moon (`moon`): `57,753,336`
     * Moon Apogee / Candrocca (`moon_apogee`): `488,203`
     * Moon Ascending Node / Rahu (`moon_node`): `-232,238` (retrograde)
     * Mars (`mars`): `2,296,832`
     * Mercury Sighrocca (`mercury_sighrocca`): `17,937,060`
     * Jupiter (`jupiter`): `364,220`
     * Venus Sighrocca (`venus_sighrocca`): `7,022,376`
     * Saturn (`saturn`): `146,568`
3. **Madhyama Graha (Mean Longitudes)**:
   - Linearly evolves each body's mean sidereal longitude from `0.0` deg at the
     Kali Yuga epoch (`Ahargana == 0.0`).
4. **Spashta Graha (True Positions via Manda and Sighra Samskaras)**:
   - *Manda Samskara* (equation of center): uses the body's *Mandocca* (apogee)
     and variable *Manda Paridhi* circumference (360th parts of the deferent
     contracting between even and odd quadrants per *Surya Siddhanta* 2.34-39).
   - *Sighra Samskara* (heliocentric-to-geocentric parallax reduction for the 5
     *Taragrahas* Mars, Mercury, Jupiter, Venus, Saturn): uses variable *Sighra
     Paridhi* circumference, *Bhuja*, *Koti*, and *Sighra Karna* hypotenuse in the
     canonical 4-step half-correction (*Ardha-Phala*) alternation (*Surya Siddhanta*
     2.43-45).
5. **Side-by-Side Modern Comparison**:
   - `compare_siddhanta_with_modern(jd_ut, modern_longitudes)` computes signed
     and absolute angular deltas between *Surya Siddhanta* true positions and
     modern reference longitudes, sealed with a deterministic SHA-256 receipt.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Final, Iterator, Mapping

from ..engine.receipt import canonical_hash
from ..jyotish.nakshatra import NAKSHATRA_NAMES, RASI_NAMES, nakshatra_position

KALI_YUGA_EPOCH_JD: Final[float] = 588465.5
UJJAIN_LONGITUDE_DEG: Final[float] = 75.7683
UJJAIN_LATITUDE_DEG: Final[float] = 23.1765

MAHAYUGA_SOLAR_YEARS: Final[int] = 4_320_000
KALI_YUGA_SOLAR_YEARS: Final[int] = 432_000
MAHAYUGA_SAVANA_DAYS: Final[int] = 1_577_917_828
KALPA_SOLAR_YEARS: Final[int] = 4_320_000_000
KALPA_MAHAYUGAS: Final[int] = 1_000

# Canonical revolution counts (Bhagana) in one Mahayuga (Surya Siddhanta 1.29-34)
MAHAYUGA_BHAGANA: Final[Mapping[str, int]] = {
    "sun": 4_320_000,
    "moon": 57_753_336,
    "moon_apogee": 488_203,
    "moon_node": -232_238,
    "mars": 2_296_832,
    "mercury_sighrocca": 17_937_060,
    "jupiter": 364_220,
    "venus_sighrocca": 7_022_376,
    "saturn": 146_568,
}

# Canonical Mandocca (apogee) revolutions per Kalpa (Surya Siddhanta 1.41-42)
KALPA_MANDOCCA_REVOLUTIONS: Final[Mapping[str, int]] = {
    "sun": 387,
    "mars": 204,
    "mercury": 368,
    "jupiter": 900,
    "venus": 535,
    "saturn": 39,
}

# Canonical Mandocca (apogee) longitudes in degrees at Kali Yuga epoch
# (Surya Siddhanta 1.41-44; elapsed Kalpa years at Kali Yuga = 1,972,944,000)
MANDOCCA_KALI_EPOCH_DEG: Final[Mapping[str, float]] = {
    "sun": 77.0 + 17.0 / 60.0,       # 77 deg 17'
    "mars": 130.0 + 0.0 / 60.0,      # 130 deg 00'
    "mercury": 220.0 + 27.0 / 60.0,  # 220 deg 27'
    "jupiter": 171.0 + 18.0 / 60.0,  # 171 deg 18'
    "venus": 79.0 + 50.0 / 60.0,     # 79 deg 50'
    "saturn": 236.0 + 37.0 / 60.0,   # 236 deg 37'
}

# Variable Manda Paridhi (even-quadrant and odd-quadrant circumferences in 360th parts)
# per Surya Siddhanta 2.34-37
MANDA_PARIDHI_EVEN_ODD_DEG: Final[Mapping[str, tuple[float, float]]] = {
    "sun": (14.0, 13.0 + 40.0 / 60.0),
    "moon": (32.0, 31.0 + 40.0 / 60.0),
    "mars": (75.0, 72.0),
    "mercury": (30.0, 28.0),
    "jupiter": (33.0, 32.0),
    "venus": (12.0, 11.0),
    "saturn": (49.0, 48.0),
}

# Variable Sighra Paridhi (even-quadrant and odd-quadrant circumferences in 360th parts)
# for the 5 Taragrahas per Surya Siddhanta 2.37-38
SIGHRA_PARIDHI_EVEN_ODD_DEG: Final[Mapping[str, tuple[float, float]]] = {
    "mars": (235.0, 232.0),
    "mercury": (133.0, 132.0),
    "jupiter": (70.0, 72.0),
    "venus": (262.0, 260.0),
    "saturn": (39.0, 40.0),
}

TARAGRAHA_BODIES: Final[tuple[str, ...]] = (
    "mars",
    "mercury",
    "jupiter",
    "venus",
    "saturn",
)

SPASHTA_GRAHA_ORDER: Final[tuple[str, ...]] = (
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


def _norm360(angle_deg: float) -> float:
    """Normalize an angle in degrees into [0.0, 360.0)."""
    val = float(angle_deg)
    if not math.isfinite(val):
        raise ValueError(f"Angle must be finite, got {angle_deg!r}")
    out = val % 360.0
    if out < 0.0 or out >= 360.0:
        out = 0.0
    return out


def _signed_delta_deg(target_deg: float, reference_deg: float) -> float:
    """Compute shortest signed angular delta (target - reference) in [-180.0, 180.0)."""
    diff = (_norm360(target_deg) - _norm360(reference_deg) + 180.0) % 360.0 - 180.0
    return diff


@dataclass(frozen=True)
class MandaSamskaraResult:
    """Result of the epicyclic Manda Samskara (equation of center) step."""

    body: str
    mean_longitude_deg: float
    mandocca_deg: float
    kendra_deg: float
    even_paridhi_deg: float
    odd_paridhi_deg: float
    effective_paridhi_deg: float
    bhuja_sin: float
    manda_phala_deg: float
    corrected_longitude_deg: float


@dataclass(frozen=True)
class SighraSamskaraResult:
    """Result of the epicyclic Sighra Samskara (heliocentric-to-geocentric parallax) step."""

    body: str
    planet_longitude_deg: float
    sighrocca_deg: float
    kendra_deg: float
    even_paridhi_deg: float
    odd_paridhi_deg: float
    effective_paridhi_deg: float
    epicycle_radius_ratio: float
    dohphala: float
    kotiphala: float
    sphuta_koti: float
    sighra_karna: float
    sighra_phala_deg: float
    corrected_longitude_deg: float


@dataclass(frozen=True)
class SuryaSiddhantaMeanLongitudes:
    """Madhyama Graha (mean sidereal longitudes) at a given Julian Date and Ahargana."""

    jd_ut: float
    ahargana: float
    longitudes: Mapping[str, float]
    receipt_sha256: str

    def __getitem__(self, key: str) -> float:
        k = key.strip().lower()
        if k in self.longitudes:
            return self.longitudes[k]
        if k == "mercury":
            return self.longitudes["sun"]
        if k == "venus":
            return self.longitudes["sun"]
        if k == "rahu":
            return self.longitudes["moon_node"]
        if k == "ketu":
            return _norm360(self.longitudes["moon_node"] + 180.0)
        raise KeyError(key)

    def __iter__(self) -> Iterator[str]:
        return iter(self.longitudes)

    def __len__(self) -> int:
        return len(self.longitudes)

    def keys(self):
        return self.longitudes.keys()

    def values(self):
        return self.longitudes.values()

    def items(self):
        return self.longitudes.items()

    @property
    def sun(self) -> float:
        return self.longitudes["sun"]

    @property
    def moon(self) -> float:
        return self.longitudes["moon"]

    @property
    def moon_apogee(self) -> float:
        return self.longitudes["moon_apogee"]

    @property
    def moon_node(self) -> float:
        return self.longitudes["moon_node"]

    @property
    def mars(self) -> float:
        return self.longitudes["mars"]

    @property
    def mercury_sighrocca(self) -> float:
        return self.longitudes["mercury_sighrocca"]

    @property
    def jupiter(self) -> float:
        return self.longitudes["jupiter"]

    @property
    def venus_sighrocca(self) -> float:
        return self.longitudes["venus_sighrocca"]

    @property
    def saturn(self) -> float:
        return self.longitudes["saturn"]

    @property
    def mercury(self) -> float:
        return self.longitudes["sun"]

    @property
    def venus(self) -> float:
        return self.longitudes["sun"]

    @property
    def rahu(self) -> float:
        return self.longitudes["moon_node"]

    @property
    def ketu(self) -> float:
        return _norm360(self.longitudes["moon_node"] + 180.0)


@dataclass(frozen=True)
class SpashtaGrahaPosition:
    """True (Spashta) position and epicyclic breakdown for a single Graha."""

    body: str
    mean_longitude_deg: float
    mandocca_deg: float
    manda_kendra_deg: float
    manda_paridhi_deg: float
    manda_phala_deg: float
    manda_spashta_deg: float
    sighrocca_deg: float | None
    sighra_kendra_deg: float | None
    sighra_paridhi_deg: float | None
    sighra_karna: float | None
    sighra_phala_deg: float | None
    true_longitude_deg: float
    rasi_index: int
    rasi_name: str
    degree_in_rasi: float
    nakshatra_index: int
    nakshatra_name: str
    pada: int

    @property
    def longitude_deg(self) -> float:
        return self.true_longitude_deg


@dataclass(frozen=True)
class SuryaSiddhantaTruePositions:
    """Complete Spashta Graha (true planetary positions) report for Surya Siddhanta."""

    jd_ut: float
    ahargana: float
    mean_longitudes: Mapping[str, float]
    true_longitudes: Mapping[str, float]
    planets: Mapping[str, SpashtaGrahaPosition]
    receipt_sha256: str

    def __getitem__(self, key: str) -> float:
        k = key.strip().lower()
        if k in self.true_longitudes:
            return self.true_longitudes[k]
        raise KeyError(key)

    def __iter__(self) -> Iterator[str]:
        return iter(self.true_longitudes)

    def __len__(self) -> int:
        return len(self.true_longitudes)

    def keys(self):
        return self.true_longitudes.keys()

    def values(self):
        return self.true_longitudes.values()

    def items(self):
        return self.true_longitudes.items()

    @property
    def sun(self) -> float:
        return self.true_longitudes["sun"]

    @property
    def moon(self) -> float:
        return self.true_longitudes["moon"]

    @property
    def mars(self) -> float:
        return self.true_longitudes["mars"]

    @property
    def mercury(self) -> float:
        return self.true_longitudes["mercury"]

    @property
    def jupiter(self) -> float:
        return self.true_longitudes["jupiter"]

    @property
    def venus(self) -> float:
        return self.true_longitudes["venus"]

    @property
    def saturn(self) -> float:
        return self.true_longitudes["saturn"]

    @property
    def rahu(self) -> float:
        return self.true_longitudes["rahu"]

    @property
    def ketu(self) -> float:
        return self.true_longitudes["ketu"]


@dataclass(frozen=True)
class PlanetSiddhantaComparison:
    """Per-planet angular comparison between Surya Siddhanta and modern longitudes."""

    body: str
    siddhanta_longitude_deg: float
    modern_longitude_deg: float
    signed_delta_deg: float
    abs_delta_deg: float
    delta_arcminutes: float
    mean_longitude_deg: float
    manda_phala_deg: float
    sighra_phala_deg: float


@dataclass(frozen=True)
class SiddhantaModernComparison:
    """Side-by-side comparison of Surya Siddhanta true longitudes with modern positions."""

    jd_ut: float
    ahargana: float
    comparisons: Mapping[str, PlanetSiddhantaComparison]
    angular_deltas_deg: Mapping[str, float]
    abs_deltas_deg: Mapping[str, float]
    mean_abs_delta_deg: float
    max_abs_delta_deg: float
    receipt_sha256: str


def compute_ahargana(jd_ut: float) -> float:
    """Compute Ahargana (civil Savana days elapsed since the Kali Yuga epoch JD 588465.5)."""
    val = float(jd_ut)
    if not math.isfinite(val):
        raise ValueError(f"jd_ut must be finite, got {jd_ut!r}")
    return val - KALI_YUGA_EPOCH_JD


def compute_mandocca_longitude(body: str, ahargana: float, moon_apogee_deg: float | None = None) -> float:
    """Compute the slow-moving Mandocca (apogee) longitude for a body at a given Ahargana.

    For the Moon, Mandocca is the rapidly moving Candrocca (`moon_apogee`).
    For the Sun and the 5 Taragrahas, Mandocca evolves slowly from its Kali Yuga
    epoch value according to its Kalpa revolution count (*Surya Siddhanta* 1.41-42).
    """
    b = body.strip().lower()
    if b == "moon":
        if moon_apogee_deg is not None:
            return _norm360(moon_apogee_deg)
        revs = (float(ahargana) * MAHAYUGA_BHAGANA["moon_apogee"]) / MAHAYUGA_SAVANA_DAYS
        return _norm360(revs * 360.0)
    if b not in MANDOCCA_KALI_EPOCH_DEG:
        raise ValueError(f"Unknown body for Mandocca calculation: {body!r}")
    kalpa_days = MAHAYUGA_SAVANA_DAYS * KALPA_MAHAYUGAS
    delta_revs = (float(ahargana) * KALPA_MANDOCCA_REVOLUTIONS[b]) / kalpa_days
    return _norm360(MANDOCCA_KALI_EPOCH_DEG[b] + delta_revs * 360.0)


def compute_manda_paridhi(body: str, kendra_deg: float) -> float:
    """Compute the variable Manda Paridhi (epicycle circumference in 360th parts).

    Per *Surya Siddhanta* 2.34-38:
    ``P(kendra) = P_even - (P_even - P_odd) * |sin(kendra)|``.
    """
    b = body.strip().lower()
    if b not in MANDA_PARIDHI_EVEN_ODD_DEG:
        raise ValueError(f"Unknown body for Manda Paridhi: {body!r}")
    p_even, p_odd = MANDA_PARIDHI_EVEN_ODD_DEG[b]
    sin_abs = abs(math.sin(math.radians(_norm360(kendra_deg))))
    return p_even - (p_even - p_odd) * sin_abs


def compute_sighra_paridhi(body: str, kendra_deg: float) -> float:
    """Compute the variable Sighra Paridhi (epicycle circumference in 360th parts).

    Per *Surya Siddhanta* 2.37-38:
    ``S(kendra) = S_even - (S_even - S_odd) * |sin(kendra)|``.
    """
    b = body.strip().lower()
    if b not in SIGHRA_PARIDHI_EVEN_ODD_DEG:
        raise ValueError(f"Unknown Taragraha body for Sighra Paridhi: {body!r}")
    s_even, s_odd = SIGHRA_PARIDHI_EVEN_ODD_DEG[b]
    sin_abs = abs(math.sin(math.radians(_norm360(kendra_deg))))
    return s_even - (s_even - s_odd) * sin_abs


def compute_manda_samskara(
    mean_lon_deg: float,
    mandocca_deg: float,
    body: str,
) -> MandaSamskaraResult:
    """Evaluate the epicyclic Manda Samskara (equation of center) per Surya Siddhanta 2.39-45.

    In *Surya Siddhanta* 2.29 & 2.39:
    - ``kendra = (mandocca_deg - mean_lon_deg) % 360``
    - ``effective_paridhi = P_even - (P_even - P_odd) * |sin(kendra)|``
    - ``sin(manda_phala) = (effective_paridhi / 360.0) * sin(kendra)``
    - When ``kendra`` is in `(0, 180)` (planet between perigee and apogee moving toward
      apogee, or equivalently ``mean_lon - mandocca`` in `(180, 360)`), ``manda_phala > 0``;
      when ``kendra`` is in `(180, 360)` (planet moving from apogee to perigee),
      ``manda_phala < 0``.
    """
    b = body.strip().lower()
    if b not in MANDA_PARIDHI_EVEN_ODD_DEG:
        raise ValueError(f"Unsupported body for Manda Samskara: {body!r}")
    mean_lon = _norm360(mean_lon_deg)
    mandocca = _norm360(mandocca_deg)
    kendra = _norm360(mandocca - mean_lon)
    p_even, p_odd = MANDA_PARIDHI_EVEN_ODD_DEG[b]
    kendra_rad = math.radians(kendra)
    bhuja_sin = math.sin(kendra_rad)
    eff_paridhi = p_even - (p_even - p_odd) * abs(bhuja_sin)
    sin_phala = max(-1.0, min(1.0, (eff_paridhi / 360.0) * bhuja_sin))
    manda_phala = math.degrees(math.asin(sin_phala))
    corrected = _norm360(mean_lon + manda_phala)
    return MandaSamskaraResult(
        body=b,
        mean_longitude_deg=mean_lon,
        mandocca_deg=mandocca,
        kendra_deg=kendra,
        even_paridhi_deg=p_even,
        odd_paridhi_deg=p_odd,
        effective_paridhi_deg=eff_paridhi,
        bhuja_sin=bhuja_sin,
        manda_phala_deg=manda_phala,
        corrected_longitude_deg=corrected,
    )


def compute_sighra_samskara(
    planet_lon_deg: float,
    sighrocca_deg: float,
    body: str,
) -> SighraSamskaraResult:
    """Evaluate the epicyclic Sighra Samskara (parallax reduction) per Surya Siddhanta 2.40-42.

    In *Surya Siddhanta* 2.40-42:
    - ``kendra = (sighrocca_deg - planet_lon_deg) % 360``
    - ``effective_paridhi = S_even - (S_even - S_odd) * |sin(kendra)|``
    - ``r = effective_paridhi / 360.0``
    - ``dohphala = r * sin(kendra)``, ``kotiphala = r * cos(kendra)``
    - ``sphuta_koti = 1.0 + kotiphala``
    - ``sighra_karna = hypot(sphuta_koti, dohphala)``
    - ``sighra_phala = degrees(atan2(dohphala, sphuta_koti))``
    """
    b = body.strip().lower()
    if b not in SIGHRA_PARIDHI_EVEN_ODD_DEG:
        raise ValueError(f"Unsupported Taragraha body for Sighra Samskara: {body!r}")
    p_lon = _norm360(planet_lon_deg)
    s_lon = _norm360(sighrocca_deg)
    kendra = _norm360(s_lon - p_lon)
    s_even, s_odd = SIGHRA_PARIDHI_EVEN_ODD_DEG[b]
    kendra_rad = math.radians(kendra)
    sin_k = math.sin(kendra_rad)
    cos_k = math.cos(kendra_rad)
    eff_paridhi = s_even - (s_even - s_odd) * abs(sin_k)
    r_ratio = eff_paridhi / 360.0
    dohphala = r_ratio * sin_k
    kotiphala = r_ratio * cos_k
    sphuta_koti = 1.0 + kotiphala
    karna = math.hypot(sphuta_koti, dohphala)
    sighra_phala = math.degrees(math.atan2(dohphala, sphuta_koti))
    corrected = _norm360(p_lon + sighra_phala)
    return SighraSamskaraResult(
        body=b,
        planet_longitude_deg=p_lon,
        sighrocca_deg=s_lon,
        kendra_deg=kendra,
        even_paridhi_deg=s_even,
        odd_paridhi_deg=s_odd,
        effective_paridhi_deg=eff_paridhi,
        epicycle_radius_ratio=r_ratio,
        dohphala=dohphala,
        kotiphala=kotiphala,
        sphuta_koti=sphuta_koti,
        sighra_karna=karna,
        sighra_phala_deg=sighra_phala,
        corrected_longitude_deg=corrected,
    )


def surya_siddhanta_mean_longitudes(jd_ut: float) -> SuryaSiddhantaMeanLongitudes:
    """Compute Madhyama Graha (mean sidereal longitudes) at any Julian Date (UT).

    At the Kali Yuga epoch (`JD = 588465.5`, `Ahargana = 0.0`), all bodies have
    mean longitude `0.0` degrees (0 deg Mesha).
    """
    ahargana = compute_ahargana(jd_ut)
    longitudes: dict[str, float] = {}
    for body, bhagana in MAHAYUGA_BHAGANA.items():
        revs = (ahargana * float(bhagana)) / float(MAHAYUGA_SAVANA_DAYS)
        lon = (revs * 360.0) % 360.0
        if lon < 0.0 or lon >= 360.0 or ahargana == 0.0:
            lon = 0.0 if ahargana == 0.0 else (lon % 360.0)
        longitudes[body] = float(lon)

    receipt = canonical_hash(
        {
            "engine": "surya_siddhanta_madhyama_v1",
            "jd_ut": float(jd_ut),
            "ahargana": ahargana,
            "longitudes": {k: round(v, 12) for k, v in longitudes.items()},
        }
    )
    return SuryaSiddhantaMeanLongitudes(
        jd_ut=float(jd_ut),
        ahargana=ahargana,
        longitudes=longitudes,
        receipt_sha256=receipt,
    )


def _build_spashta_position(
    *,
    body: str,
    mean_longitude_deg: float,
    mandocca_deg: float,
    manda_kendra_deg: float,
    manda_paridhi_deg: float,
    manda_phala_deg: float,
    manda_spashta_deg: float,
    sighrocca_deg: float | None,
    sighra_kendra_deg: float | None,
    sighra_paridhi_deg: float | None,
    sighra_karna: float | None,
    sighra_phala_deg: float | None,
    true_longitude_deg: float,
) -> SpashtaGrahaPosition:
    true_lon = _norm360(true_longitude_deg)
    rasi_idx = min(int(true_lon // 30.0), 11)
    deg_in_rasi = true_lon - rasi_idx * 30.0
    nak = nakshatra_position(true_lon)
    return SpashtaGrahaPosition(
        body=body,
        mean_longitude_deg=_norm360(mean_longitude_deg),
        mandocca_deg=_norm360(mandocca_deg),
        manda_kendra_deg=_norm360(manda_kendra_deg),
        manda_paridhi_deg=float(manda_paridhi_deg),
        manda_phala_deg=float(manda_phala_deg),
        manda_spashta_deg=_norm360(manda_spashta_deg),
        sighrocca_deg=_norm360(sighrocca_deg) if sighrocca_deg is not None else None,
        sighra_kendra_deg=_norm360(sighra_kendra_deg) if sighra_kendra_deg is not None else None,
        sighra_paridhi_deg=float(sighra_paridhi_deg) if sighra_paridhi_deg is not None else None,
        sighra_karna=float(sighra_karna) if sighra_karna is not None else None,
        sighra_phala_deg=float(sighra_phala_deg) if sighra_phala_deg is not None else None,
        true_longitude_deg=true_lon,
        rasi_index=rasi_idx,
        rasi_name=RASI_NAMES[rasi_idx],
        degree_in_rasi=deg_in_rasi,
        nakshatra_index=nak.index,
        nakshatra_name=NAKSHATRA_NAMES[nak.index],
        pada=nak.pada,
    )


def surya_siddhanta_true_positions(jd_ut: float) -> SuryaSiddhantaTruePositions:
    """Compute true geocentric sidereal longitudes (Spashta Graha) per Surya Siddhanta Chapter 2.

    - **Sun & Moon**: Single *Manda Samskara* against their respective *Mandocca*.
    - **5 Taragrahas (Mars, Mercury, Jupiter, Venus, Saturn)**: Canonical 4-step
      *Surya Siddhanta* (2.43-45) alternation:
      1. Half *Sighra Phala* applied to the mean planet (`L_1 = L_0 + 0.5 * sighra_1`).
      2. Half *Manda Phala* evaluated at `L_1` and applied (`L_2 = L_1 + 0.5 * manda_1`).
      3. Full *Manda Phala* evaluated at `L_2` and applied to the original mean planet
         to yield the *Manda-spashta* planet (`L_3 = L_0 + manda_2`).
      4. Full *Sighra Phala* evaluated at `L_3` and applied to `L_3` to yield the true
         geocentric *Spashta Graha* (`L_true = L_3 + sighra_2`).
    - **Rahu & Ketu**: Mean lunar ascending node (`moon_node`) and its 180-degree
      opposition (`(moon_node + 180) % 360`).
    """
    madhyama = surya_siddhanta_mean_longitudes(jd_ut)
    ahargana = madhyama.ahargana
    mean_map = dict(madhyama.longitudes)

    planets: dict[str, SpashtaGrahaPosition] = {}
    true_longitudes: dict[str, float] = {}

    # 1. Sun (Surya) and Moon (Chandra): Manda Samskara only
    for luminary in ("sun", "moon"):
        mean_lon = mean_map[luminary]
        mandocca = compute_mandocca_longitude(
            luminary,
            ahargana,
            moon_apogee_deg=mean_map["moon_apogee"],
        )
        manda_res = compute_manda_samskara(mean_lon, mandocca, luminary)
        pos = _build_spashta_position(
            body=luminary,
            mean_longitude_deg=mean_lon,
            mandocca_deg=mandocca,
            manda_kendra_deg=manda_res.kendra_deg,
            manda_paridhi_deg=manda_res.effective_paridhi_deg,
            manda_phala_deg=manda_res.manda_phala_deg,
            manda_spashta_deg=manda_res.corrected_longitude_deg,
            sighrocca_deg=None,
            sighra_kendra_deg=None,
            sighra_paridhi_deg=None,
            sighra_karna=None,
            sighra_phala_deg=None,
            true_longitude_deg=manda_res.corrected_longitude_deg,
        )
        planets[luminary] = pos
        true_longitudes[luminary] = pos.true_longitude_deg

    # 2. Five Taragrahas (Mars, Mercury, Jupiter, Venus, Saturn): 4-step Manda + Sighra
    for body in TARAGRAHA_BODIES:
        if body == "mercury":
            l0 = mean_map["sun"]
            sighrocca = mean_map["mercury_sighrocca"]
        elif body == "venus":
            l0 = mean_map["sun"]
            sighrocca = mean_map["venus_sighrocca"]
        else:
            l0 = mean_map[body]
            sighrocca = mean_map["sun"]

        mandocca = compute_mandocca_longitude(body, ahargana)

        # Step 1: Half Sighra Phala from mean planet L0
        sighra_step1 = compute_sighra_samskara(l0, sighrocca, body)
        l1 = _norm360(l0 + 0.5 * sighra_step1.sighra_phala_deg)

        # Step 2: Half Manda Phala from L1
        manda_step2 = compute_manda_samskara(l1, mandocca, body)
        l2 = _norm360(l1 + 0.5 * manda_step2.manda_phala_deg)

        # Step 3: Full Manda Phala evaluated at L2, applied to original mean planet L0
        manda_step3 = compute_manda_samskara(l2, mandocca, body)
        l3_manda_spashta = _norm360(l0 + manda_step3.manda_phala_deg)

        # Step 4: Full Sighra Phala evaluated at Manda-spashta L3, applied to L3
        sighra_step4 = compute_sighra_samskara(l3_manda_spashta, sighrocca, body)
        l_true = sighra_step4.corrected_longitude_deg

        pos = _build_spashta_position(
            body=body,
            mean_longitude_deg=l0,
            mandocca_deg=mandocca,
            manda_kendra_deg=manda_step3.kendra_deg,
            manda_paridhi_deg=manda_step3.effective_paridhi_deg,
            manda_phala_deg=manda_step3.manda_phala_deg,
            manda_spashta_deg=l3_manda_spashta,
            sighrocca_deg=sighrocca,
            sighra_kendra_deg=sighra_step4.kendra_deg,
            sighra_paridhi_deg=sighra_step4.effective_paridhi_deg,
            sighra_karna=sighra_step4.sighra_karna,
            sighra_phala_deg=sighra_step4.sighra_phala_deg,
            true_longitude_deg=l_true,
        )
        planets[body] = pos
        true_longitudes[body] = pos.true_longitude_deg

    # 3. Lunar Nodes (Rahu and Ketu)
    rahu_lon = mean_map["moon_node"]
    ketu_lon = _norm360(rahu_lon + 180.0)
    for node_name, node_lon in (("rahu", rahu_lon), ("ketu", ketu_lon)):
        pos = _build_spashta_position(
            body=node_name,
            mean_longitude_deg=node_lon,
            mandocca_deg=node_lon,
            manda_kendra_deg=0.0,
            manda_paridhi_deg=0.0,
            manda_phala_deg=0.0,
            manda_spashta_deg=node_lon,
            sighrocca_deg=None,
            sighra_kendra_deg=None,
            sighra_paridhi_deg=None,
            sighra_karna=None,
            sighra_phala_deg=None,
            true_longitude_deg=node_lon,
        )
        planets[node_name] = pos
        true_longitudes[node_name] = pos.true_longitude_deg

    receipt = canonical_hash(
        {
            "engine": "surya_siddhanta_spashta_v1",
            "jd_ut": float(jd_ut),
            "ahargana": ahargana,
            "true_longitudes": {k: round(v, 12) for k, v in true_longitudes.items()},
        }
    )
    return SuryaSiddhantaTruePositions(
        jd_ut=float(jd_ut),
        ahargana=ahargana,
        mean_longitudes=mean_map,
        true_longitudes=true_longitudes,
        planets=planets,
        receipt_sha256=receipt,
    )


def compare_siddhanta_with_modern(
    jd_ut: float,
    modern_longitudes: Mapping[str, float],
) -> SiddhantaModernComparison:
    """Compare Surya Siddhanta Spashta Graha positions with modern sidereal longitudes.

    Parameters
    ----------
    jd_ut:
        Julian Date (UT) of comparison.
    modern_longitudes:
        Mapping of body names (e.g. ``"sun"``, ``"moon"``, ``"mars"``, ...) to modern
        sidereal longitudes in degrees.

    Returns
    -------
    SiddhantaModernComparison
        Per-planet angular deltas, summary statistics, and a deterministic SHA-256 receipt.
    """
    if not modern_longitudes:
        raise ValueError("modern_longitudes must contain at least one planet")

    spashta = surya_siddhanta_true_positions(jd_ut)
    comparisons: dict[str, PlanetSiddhantaComparison] = {}
    angular_deltas: dict[str, float] = {}
    abs_deltas: dict[str, float] = {}

    for raw_key, mod_val in modern_longitudes.items():
        body = raw_key.strip().lower()
        if body == "moon_node":
            body = "rahu"
        if body not in spashta.planets:
            raise ValueError(f"Unsupported planet key in modern_longitudes: {raw_key!r}")

        p_info = spashta.planets[body]
        mod_lon = _norm360(float(mod_val))
        sid_lon = p_info.true_longitude_deg
        signed_delta = _signed_delta_deg(sid_lon, mod_lon)
        abs_delta = abs(signed_delta)

        comparisons[body] = PlanetSiddhantaComparison(
            body=body,
            siddhanta_longitude_deg=sid_lon,
            modern_longitude_deg=mod_lon,
            signed_delta_deg=signed_delta,
            abs_delta_deg=abs_delta,
            delta_arcminutes=signed_delta * 60.0,
            mean_longitude_deg=p_info.mean_longitude_deg,
            manda_phala_deg=p_info.manda_phala_deg,
            sighra_phala_deg=p_info.sighra_phala_deg if p_info.sighra_phala_deg is not None else 0.0,
        )
        angular_deltas[body] = signed_delta
        abs_deltas[body] = abs_delta

    mean_abs = sum(abs_deltas.values()) / float(len(abs_deltas))
    max_abs = max(abs_deltas.values())

    receipt = canonical_hash(
        {
            "engine": "surya_siddhanta_modern_comparison_v1",
            "jd_ut": float(jd_ut),
            "ahargana": spashta.ahargana,
            "angular_deltas_deg": {k: round(v, 12) for k, v in sorted(angular_deltas.items())},
            "mean_abs_delta_deg": round(mean_abs, 12),
            "max_abs_delta_deg": round(max_abs, 12),
        }
    )
    return SiddhantaModernComparison(
        jd_ut=float(jd_ut),
        ahargana=spashta.ahargana,
        comparisons=comparisons,
        angular_deltas_deg=angular_deltas,
        abs_deltas_deg=abs_deltas,
        mean_abs_delta_deg=mean_abs,
        max_abs_delta_deg=max_abs,
        receipt_sha256=receipt,
    )


__all__ = [
    "KALI_YUGA_EPOCH_JD",
    "KALI_YUGA_SOLAR_YEARS",
    "KALPA_MAHAYUGAS",
    "KALPA_MANDOCCA_REVOLUTIONS",
    "KALPA_SOLAR_YEARS",
    "MAHAYUGA_BHAGANA",
    "MAHAYUGA_SAVANA_DAYS",
    "MAHAYUGA_SOLAR_YEARS",
    "MANDOCCA_KALI_EPOCH_DEG",
    "MANDA_PARIDHI_EVEN_ODD_DEG",
    "MandaSamskaraResult",
    "PlanetSiddhantaComparison",
    "SIGHRA_PARIDHI_EVEN_ODD_DEG",
    "SPASHTA_GRAHA_ORDER",
    "SighraSamskaraResult",
    "SiddhantaModernComparison",
    "SpashtaGrahaPosition",
    "SuryaSiddhantaMeanLongitudes",
    "SuryaSiddhantaTruePositions",
    "TARAGRAHA_BODIES",
    "UJJAIN_LATITUDE_DEG",
    "UJJAIN_LONGITUDE_DEG",
    "compare_siddhanta_with_modern",
    "compute_ahargana",
    "compute_manda_paridhi",
    "compute_manda_samskara",
    "compute_mandocca_longitude",
    "compute_sighra_paridhi",
    "compute_sighra_samskara",
    "surya_siddhanta_mean_longitudes",
    "surya_siddhanta_true_positions",
]
