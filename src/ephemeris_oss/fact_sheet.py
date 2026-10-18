"""Deterministic AI fact-sheet compiler (< 3 KB JSON) and astrological hallucination verifier.

In vertical astronomical and astrological AI software, factual calculations must be
100% deterministic. Language models should never compute planetary longitudes, sign
placements, house numbers, nakshatras, or dasha periods directly; instead, they
consume a compact, cryptographically receipted mathematical fact sheet (< 3 KB JSON)
and their natural-language output is audited against that fact sheet before display.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Any, Mapping

from .jyotish import compute_vedic_chart_analysis
from .jyotish.nakshatra import NAKSHATRA_NAMES, nakshatra_position
from .jyotish.vargas import RASI_LORDS, is_vargottama, varga_sign
from .jyotish_advanced.kp import kp_coordinate_lords
from .jyotish_advanced.yogas import evaluate_classical_yogas

SCHEMA_VERSION = "ephemeris-oss.fact-sheet.v1"

ENGLISH_SIGN_NAMES: tuple[str, ...] = (
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

SIGN_ALIASES: dict[str, int] = {
    "aries": 0,
    "mesha": 0,
    "mesh": 0,
    "taurus": 1,
    "vrishabha": 1,
    "vrishabh": 1,
    "gemini": 2,
    "mithuna": 2,
    "mithun": 2,
    "cancer": 3,
    "karka": 3,
    "karkata": 3,
    "kark": 3,
    "leo": 4,
    "simha": 4,
    "singh": 4,
    "virgo": 5,
    "kanya": 5,
    "libra": 6,
    "tula": 6,
    "scorpio": 7,
    "vrishchika": 7,
    "vrischika": 7,
    "sagittarius": 8,
    "dhanu": 8,
    "dhanus": 8,
    "capricorn": 9,
    "makara": 9,
    "makar": 9,
    "aquarius": 10,
    "kumbha": 10,
    "kumbh": 10,
    "pisces": 11,
    "meena": 11,
    "meen": 11,
}

BODY_ALIASES: dict[str, str] = {
    "sun": "sun",
    "surya": "sun",
    "ravi": "sun",
    "moon": "moon",
    "chandra": "moon",
    "soma": "moon",
    "mars": "mars",
    "mangala": "mars",
    "mangal": "mars",
    "kuja": "mars",
    "mercury": "mercury",
    "budha": "mercury",
    "budh": "mercury",
    "jupiter": "jupiter",
    "guru": "jupiter",
    "brihaspati": "jupiter",
    "venus": "venus",
    "shukra": "venus",
    "sukra": "venus",
    "saturn": "saturn",
    "shani": "saturn",
    "sani": "saturn",
    "rahu": "rahu",
    "north node": "rahu",
    "ketu": "ketu",
    "south node": "ketu",
    "ascendant": "ascendant",
    "lagna": "ascendant",
    "asc": "ascendant",
}

NAKSHATRA_ALIASES: dict[str, int] = {}
for _idx, _name in enumerate(NAKSHATRA_NAMES):
    _clean = _name.lower()
    NAKSHATRA_ALIASES[_clean] = _idx
    NAKSHATRA_ALIASES[_clean.replace(" ", "")] = _idx

# Common transliteration aliases for the 27 Nakshatras
NAKSHATRA_ALIASES.update(
    {
        "aswini": 0,
        "krittika": 2,
        "kritika": 2,
        "mrigashirsha": 4,
        "mrigasira": 4,
        "ardra": 5,
        "ardhra": 5,
        "pushyami": 7,
        "aslesha": 8,
        "makha": 9,
        "pubba": 10,
        "uttara": 11,
        "chitta": 13,
        "swathi": 14,
        "visakha": 15,
        "jyestha": 17,
        "mula": 18,
        "poorvashada": 19,
        "uttarashada": 20,
        "sravana": 21,
        "dhanistha": 22,
        "shatabhishak": 23,
        "satabhisha": 23,
        "poorvabhadra": 24,
        "uttarabhadra": 25,
    }
)

ORDINAL_WORDS: dict[str, int] = {
    "first": 1,
    "second": 2,
    "third": 3,
    "fourth": 4,
    "fifth": 5,
    "sixth": 6,
    "seventh": 7,
    "eighth": 8,
    "ninth": 9,
    "tenth": 10,
    "eleventh": 11,
    "twelfth": 12,
}


def _sha256_json(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _boundary_margin_arcmin(lon_deg: float, step_deg: float) -> float:
    rem = (lon_deg % 360.0) % step_deg
    dist_deg = min(rem, step_deg - rem)
    return round(dist_deg * 60.0, 2)


@dataclass(frozen=True)
class AIFactSheet:
    """Compact, cryptographically receipted astrological fact sheet (< 3 KB JSON)."""

    schema_version: str
    payload: dict[str, Any]
    json_str: str
    byte_length: int
    max_bytes: int
    receipt_sha256: str


@dataclass(frozen=True)
class ClaimCheckResult:
    """Verification outcome for a single astrological claim extracted from text."""

    category: str
    subject: str
    matched_text: str
    claimed_value: str
    expected_value: str
    is_valid: bool
    correction: str | None = None


@dataclass(frozen=True)
class HallucinationAudit:
    """Deterministic verification report for an AI-generated astrological reading."""

    passed: bool
    total_claims_checked: int
    verified_claims: tuple[ClaimCheckResult, ...]
    contradictions: tuple[ClaimCheckResult, ...]
    fact_sheet_sha256: str
    receipt_sha256: str


def compile_ai_fact_sheet(
    planet_longitudes: Mapping[str, float],
    ascendant_lon_deg: float,
    *,
    planet_speeds_deg_per_day: Mapping[str, float] | None = None,
    birth_jd_ut: float | None = None,
    query_jd_ut: float | None = None,
    sunrise_jd_ut: float | None = None,
    sunset_jd_ut: float | None = None,
    latitude_deg: float = 0.0,
    max_bytes: int = 3000,
) -> AIFactSheet:
    """Compile a deterministic Vedic astrological fact sheet guaranteed under ``max_bytes``."""
    if max_bytes < 512:
        raise ValueError("max_bytes must be at least 512 bytes")

    norm_lons: dict[str, float] = {
        str(k).strip().lower(): float(v) % 360.0 for k, v in planet_longitudes.items()
    }
    speeds: dict[str, float] = {
        str(k).strip().lower(): float(v)
        for k, v in (planet_speeds_deg_per_day or {}).items()
    }
    asc_lon = float(ascendant_lon_deg) % 360.0
    asc_sign_idx = int(asc_lon // 30.0) % 12
    asc_nak = nakshatra_position(asc_lon)
    asc_d9_idx = varga_sign(asc_lon, "D9").sign_index
    asc_kp = kp_coordinate_lords(asc_lon)

    asc_summary: dict[str, Any] = {
        "lon": round(asc_lon, 4),
        "sign": ENGLISH_SIGN_NAMES[asc_sign_idx],
        "sign_idx": asc_sign_idx,
        "lord": RASI_LORDS[asc_sign_idx].lower(),
        "deg_in_sign": round(asc_lon % 30.0, 4),
        "nakshatra": asc_nak.name,
        "nak_idx": asc_nak.index,
        "pada": asc_nak.pada,
        "d9_sign": ENGLISH_SIGN_NAMES[asc_d9_idx],
        "d9_sign_idx": asc_d9_idx,
        "kp_sub": asc_kp.sub_lord,
    }

    canonical_order = (
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
    ordered_bodies = [b for b in canonical_order if b in norm_lons] + [
        b for b in sorted(norm_lons) if b not in canonical_order
    ]

    bodies_summary: dict[str, dict[str, Any]] = {}
    borderline_warnings: list[dict[str, Any]] = []

    asc_rasi_margin = _boundary_margin_arcmin(asc_lon, 30.0)
    asc_d9_margin = _boundary_margin_arcmin(asc_lon, 10.0 / 3.0)
    if asc_rasi_margin <= 15.0 or asc_d9_margin <= 5.0:
        borderline_warnings.append(
            {
                "body": "ascendant",
                "rasi_margin_arcmin": asc_rasi_margin,
                "d9_margin_arcmin": asc_d9_margin,
            }
        )

    for body in ordered_bodies:
        lon = norm_lons[body]
        sign_idx = int(lon // 30.0) % 12
        house_num = ((sign_idx - asc_sign_idx) % 12) + 1
        nak = nakshatra_position(lon)
        d9_idx = varga_sign(lon, "D9").sign_index
        d10_idx = varga_sign(lon, "D10").sign_index
        kp = kp_coordinate_lords(lon)
        spd = speeds.get(body, -0.05 if body in ("rahu", "ketu") else 0.0)
        is_retro = bool(spd < 0.0) if body not in ("sun", "moon") else False

        bodies_summary[body] = {
            "lon": round(lon, 4),
            "sign": ENGLISH_SIGN_NAMES[sign_idx],
            "sign_idx": sign_idx,
            "house": house_num,
            "deg": round(lon % 30.0, 2),
            "nakshatra": nak.name,
            "nak_idx": nak.index,
            "pada": nak.pada,
            "d9_sign": ENGLISH_SIGN_NAMES[d9_idx],
            "d9_sign_idx": d9_idx,
            "d10_sign": ENGLISH_SIGN_NAMES[d10_idx],
            "vargottama": is_vargottama(lon),
            "retro": is_retro,
            "kp_sub": kp.sub_lord,
        }

        r_margin = _boundary_margin_arcmin(lon, 30.0)
        d9_margin = _boundary_margin_arcmin(lon, 10.0 / 3.0)
        if r_margin <= 15.0 or d9_margin <= 3.0:
            borderline_warnings.append(
                {
                    "body": body,
                    "rasi_margin_arcmin": r_margin,
                    "d9_margin_arcmin": d9_margin,
                }
            )

    yogas_report = evaluate_classical_yogas(norm_lons, asc_lon)
    active_yogas = [
        {"name": y.name, "cat": y.category, "strength": round(y.strength_score, 2)}
        for y in yogas_report.active_yogas[:10]
    ]

    panchanga_summary: dict[str, Any] | None = None
    dasha_summary: dict[str, Any] | None = None
    strength_summary: dict[str, Any] | None = None

    if birth_jd_ut is not None and "sun" in norm_lons and "moon" in norm_lons:
        cap_speeds = {k.capitalize(): v for k, v in speeds.items()} if speeds else None
        analysis = compute_vedic_chart_analysis(
            planet_longitudes=norm_lons,
            lagna_lon_deg=asc_lon,
            jd_ut=birth_jd_ut,
            query_jd=query_jd_ut,
            planet_speeds_deg_per_day=cap_speeds,
            sunrise_jd_ut=sunrise_jd_ut,
            sunset_jd_ut=sunset_jd_ut,
        )
        if analysis.panchanga is not None:
            p = analysis.panchanga
            panchanga_summary = {
                "tithi": p.tithi.name,
                "paksha": p.tithi.paksha,
                "vara": p.vara.english_name,
                "nakshatra": p.nakshatra.name,
                "yoga": p.yoga.name,
                "karana": p.karana.name,
            }
        if analysis.vimshottari_active_5_levels is not None:
            levels = analysis.vimshottari_active_5_levels
            dasha_summary = {
                "mahadasha": levels[0].lord.lower() if len(levels) > 0 else None,
                "antardasha": levels[1].lord.lower() if len(levels) > 1 else None,
                "pratyantardasha": levels[2].lord.lower() if len(levels) > 2 else None,
            }
        if analysis.shadbala is not None:
            strength_summary = {
                b.lower(): round(s.total_rupas, 2)
                for b, s in analysis.shadbala.planets.items()
            }

    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "ascendant": asc_summary,
        "bodies": bodies_summary,
        "active_yogas": active_yogas,
        "borderline_warnings": borderline_warnings,
    }
    if panchanga_summary is not None:
        payload["panchanga"] = panchanga_summary
    if dasha_summary is not None:
        payload["dasha"] = dasha_summary
    if strength_summary is not None:
        payload["shadbala_rupas"] = strength_summary

    # Progressive compaction guard to guarantee final byte_length <= max_bytes
    # Reserve 90 bytes for the trailing "receipt_sha256":"<64-char-hex>" field.
    target_budget = max(400, max_bytes - 90)

    def _cur_size() -> int:
        return len(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"))

    if _cur_size() > target_budget and "active_yogas" in payload:
        payload["active_yogas"] = payload["active_yogas"][:4]
    if _cur_size() > target_budget and "borderline_warnings" in payload:
        payload["borderline_warnings"] = payload["borderline_warnings"][:2]
    if _cur_size() > target_budget:
        for b_info in payload["bodies"].values():
            b_info.pop("d10_sign", None)
            b_info.pop("kp_sub", None)
    if _cur_size() > target_budget:
        payload.pop("active_yogas", None)
        payload.pop("shadbala_rupas", None)
    if _cur_size() > target_budget:
        payload.pop("panchanga", None)
        payload.pop("borderline_warnings", None)
        for b_info in payload["bodies"].values():
            b_info.pop("vargottama", None)
            b_info.pop("lon", None)
            b_info.pop("deg", None)
    if _cur_size() > target_budget:
        payload.pop("dasha", None)
        payload["ascendant"].pop("deg_in_sign", None)
        payload["ascendant"].pop("kp_sub", None)
        for b_info in payload["bodies"].values():
            b_info.pop("pada", None)
            b_info.pop("d9_sign", None)

    receipt = _sha256_json(payload)
    payload["receipt_sha256"] = receipt
    final_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    byte_len = len(final_json.encode("utf-8"))

    return AIFactSheet(
        schema_version=SCHEMA_VERSION,
        payload=payload,
        json_str=final_json,
        byte_length=byte_len,
        max_bytes=max_bytes,
        receipt_sha256=receipt,
    )


_BODY_PATTERN = (
    r"(?P<body>sun|surya|ravi|moon|chandra|soma|mars|mangala|mangal|kuja|"
    r"mercury|budha|budh|jupiter|guru|brihaspati|venus|shukra|sukra|"
    r"saturn|shani|sani|rahu|ketu|ascendant|lagna)"
)
_SIGN_PATTERN = (
    r"(?P<sign>aries|mesha|mesh|taurus|vrishabha|vrishabh|gemini|mithuna|mithun|"
    r"cancer|karka|karkata|kark|leo|simha|singh|virgo|kanya|libra|tula|"
    r"scorpio|vrishchika|vrischika|sagittarius|dhanu|dhanus|capricorn|makara|makar|"
    r"aquarius|kumbha|kumbh|pisces|meena|meen)"
)

_RE_D9_PLACEMENT = re.compile(
    rf"\b{_BODY_PATTERN}\s+(?:is\s+)?(?:placed\s+)?in\s+{_SIGN_PATTERN}\s+(?:in\s+)?(?:navamsa|navamsha|d-?9)\b",
    re.IGNORECASE,
)
_RE_SIGN_PLACEMENT = re.compile(
    rf"\b{_BODY_PATTERN}\s+(?:is\s+)?(?:resides\s+|sits\s+|placed\s+|positioned\s+)?in\s+(?:the\s+sign\s+of\s+)?{_SIGN_PATTERN}(?!\s+(?:in\s+)?(?:navamsa|navamsha|d-?9))\b",
    re.IGNORECASE,
)
_RE_SIGN_LAGNA = re.compile(
    rf"\b{_SIGN_PATTERN}\s+(?:ascendant|lagna)\b",
    re.IGNORECASE,
)
_RE_HOUSE_NUM = re.compile(
    rf"\b{_BODY_PATTERN}\s+[^\.\,\;\n]{{0,35}}?\b(?:in\s+)?(?:the\s+)?(?P<house>1[0-2]|[1-9])(?:st|nd|rd|th)?\s+(?:house|bhava)\b",
    re.IGNORECASE,
)
_RE_HOUSE_WORD = re.compile(
    rf"\b{_BODY_PATTERN}\s+[^\.\,\;\n]{{0,35}}?\b(?:in\s+)?(?:the\s+)?(?P<house_word>first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth)\s+(?:house|bhava)\b",
    re.IGNORECASE,
)
_RE_RETRO_PREFIX = re.compile(
    r"\b(?P<motion>retrograde|direct)\s+(?P<body>mars|mangala|mercury|budha|jupiter|guru|venus|shukra|saturn|shani)\b",
    re.IGNORECASE,
)
_RE_RETRO_SUFFIX = re.compile(
    r"\b(?P<body>mars|mangala|mercury|budha|jupiter|guru|venus|shukra|saturn|shani)\s+is\s+(?P<motion>retrograde|direct|vakri|margi)\b",
    re.IGNORECASE,
)
_RE_DASHA = re.compile(
    r"\b(?P<lord>sun|surya|moon|chandra|mars|mangala|mercury|budha|jupiter|guru|venus|shukra|saturn|shani|rahu|ketu)\s+(?P<level>mahadasha|maha\s+dasha|antardasha|antar\s+dasha|bhukti)\b",
    re.IGNORECASE,
)


def verify_ai_interpretation(
    text: str,
    fact_sheet: AIFactSheet | Mapping[str, Any],
) -> HallucinationAudit:
    """Deterministically audit natural-language astrological text against ``fact_sheet``."""
    payload: Mapping[str, Any] = (
        fact_sheet.payload if isinstance(fact_sheet, AIFactSheet) else fact_sheet
    )
    bodies = payload.get("bodies", {})
    asc = payload.get("ascendant", {})
    dasha = payload.get("dasha", {})
    fact_sha = str(payload.get("receipt_sha256") or _sha256_json(payload))

    checks: list[ClaimCheckResult] = []

    def _subject_data(canonical_body: str) -> Mapping[str, Any] | None:
        if canonical_body == "ascendant":
            return asc
        return bodies.get(canonical_body)

    # 1. Check D9 Navamsa placements first
    d9_spans: list[tuple[int, int]] = []
    for match in _RE_D9_PLACEMENT.finditer(text):
        d9_spans.append(match.span())
        raw_body = match.group("body").lower()
        raw_sign = match.group("sign").lower()
        body_key = BODY_ALIASES[raw_body]
        claimed_idx = SIGN_ALIASES[raw_sign]
        b_data = _subject_data(body_key)
        if not b_data or "d9_sign_idx" not in b_data:
            continue
        actual_idx = int(b_data["d9_sign_idx"])
        expected_name = ENGLISH_SIGN_NAMES[actual_idx]
        claimed_name = ENGLISH_SIGN_NAMES[claimed_idx]
        ok = claimed_idx == actual_idx
        checks.append(
            ClaimCheckResult(
                category="d9_sign",
                subject=body_key,
                matched_text=match.group(0),
                claimed_value=claimed_name,
                expected_value=expected_name,
                is_valid=ok,
                correction=None
                if ok
                else f"{body_key.title()} is in {expected_name} in D9 Navamsa, not {claimed_name}.",
            )
        )

    # 2. Check D1 Sign placements
    for match in _RE_SIGN_PLACEMENT.finditer(text):
        if any(
            not (match.end() <= s_start or match.start() >= s_end)
            for s_start, s_end in d9_spans
        ):
            continue
        raw_body = match.group("body").lower()
        raw_sign = match.group("sign").lower()
        body_key = BODY_ALIASES[raw_body]
        claimed_idx = SIGN_ALIASES[raw_sign]
        b_data = _subject_data(body_key)
        if not b_data or "sign_idx" not in b_data:
            continue
        actual_idx = int(b_data["sign_idx"])
        expected_name = ENGLISH_SIGN_NAMES[actual_idx]
        claimed_name = ENGLISH_SIGN_NAMES[claimed_idx]
        ok = claimed_idx == actual_idx
        checks.append(
            ClaimCheckResult(
                category="d1_sign",
                subject=body_key,
                matched_text=match.group(0),
                claimed_value=claimed_name,
                expected_value=expected_name,
                is_valid=ok,
                correction=None
                if ok
                else f"{body_key.title()} is in {expected_name}, not {claimed_name}.",
            )
        )

    # 2b. Check "<Sign> Ascendant/Lagna"
    for match in _RE_SIGN_LAGNA.finditer(text):
        raw_sign = match.group("sign").lower()
        claimed_idx = SIGN_ALIASES[raw_sign]
        if "sign_idx" in asc:
            actual_idx = int(asc["sign_idx"])
            expected_name = ENGLISH_SIGN_NAMES[actual_idx]
            claimed_name = ENGLISH_SIGN_NAMES[claimed_idx]
            ok = claimed_idx == actual_idx
            checks.append(
                ClaimCheckResult(
                    category="d1_sign",
                    subject="ascendant",
                    matched_text=match.group(0),
                    claimed_value=claimed_name,
                    expected_value=expected_name,
                    is_valid=ok,
                    correction=None
                    if ok
                    else f"Ascendant is {expected_name}, not {claimed_name}.",
                )
            )

    # 3. Check House placements (numeric and ordinal words)
    for match in _RE_HOUSE_NUM.finditer(text):
        body_key = BODY_ALIASES[match.group("body").lower()]
        claimed_house = int(match.group("house"))
        b_data = bodies.get(body_key)
        if not b_data or "house" not in b_data:
            continue
        actual_house = int(b_data["house"])
        ok = claimed_house == actual_house
        checks.append(
            ClaimCheckResult(
                category="house",
                subject=body_key,
                matched_text=match.group(0),
                claimed_value=f"house {claimed_house}",
                expected_value=f"house {actual_house}",
                is_valid=ok,
                correction=None
                if ok
                else f"{body_key.title()} is in house {actual_house}, not house {claimed_house}.",
            )
        )

    for match in _RE_HOUSE_WORD.finditer(text):
        body_key = BODY_ALIASES[match.group("body").lower()]
        claimed_house = ORDINAL_WORDS[match.group("house_word").lower()]
        b_data = bodies.get(body_key)
        if not b_data or "house" not in b_data:
            continue
        actual_house = int(b_data["house"])
        ok = claimed_house == actual_house
        checks.append(
            ClaimCheckResult(
                category="house",
                subject=body_key,
                matched_text=match.group(0),
                claimed_value=f"house {claimed_house}",
                expected_value=f"house {actual_house}",
                is_valid=ok,
                correction=None
                if ok
                else f"{body_key.title()} is in house {actual_house}, not house {claimed_house}.",
            )
        )

    # 4. Check Nakshatra placements
    nak_keys_sorted = sorted(NAKSHATRA_ALIASES.keys(), key=len, reverse=True)
    nak_pattern = "|".join(re.escape(k) for k in nak_keys_sorted)
    re_nak = re.compile(
        rf"\b{_BODY_PATTERN}\s+(?:is\s+|placed\s+|sits\s+)?in\s+(?:the\s+)?(?P<nak>{nak_pattern})(?:\s+nakshatra)?\b",
        re.IGNORECASE,
    )
    for match in re_nak.finditer(text):
        body_key = BODY_ALIASES[match.group("body").lower()]
        nak_idx = NAKSHATRA_ALIASES[match.group("nak").lower()]
        b_data = _subject_data(body_key)
        if not b_data or "nak_idx" not in b_data:
            continue
        actual_nak_idx = int(b_data["nak_idx"])
        claimed_nak = NAKSHATRA_NAMES[nak_idx]
        expected_nak = NAKSHATRA_NAMES[actual_nak_idx]
        ok = nak_idx == actual_nak_idx
        checks.append(
            ClaimCheckResult(
                category="nakshatra",
                subject=body_key,
                matched_text=match.group(0),
                claimed_value=claimed_nak,
                expected_value=expected_nak,
                is_valid=ok,
                correction=None
                if ok
                else f"{body_key.title()} is in {expected_nak} Nakshatra, not {claimed_nak}.",
            )
        )

    # 5. Check Retrograde / Direct claims
    for regex in (_RE_RETRO_PREFIX, _RE_RETRO_SUFFIX):
        for match in regex.finditer(text):
            body_key = BODY_ALIASES[match.group("body").lower()]
            motion_word = match.group("motion").lower()
            claimed_retro = motion_word in ("retrograde", "vakri")
            b_data = bodies.get(body_key)
            if not b_data or "retro" not in b_data:
                continue
            actual_retro = bool(b_data["retro"])
            ok = claimed_retro == actual_retro
            claimed_label = "retrograde" if claimed_retro else "direct"
            expected_label = "retrograde" if actual_retro else "direct"
            checks.append(
                ClaimCheckResult(
                    category="motion",
                    subject=body_key,
                    matched_text=match.group(0),
                    claimed_value=claimed_label,
                    expected_value=expected_label,
                    is_valid=ok,
                    correction=None
                    if ok
                    else f"{body_key.title()} is {expected_label}, not {claimed_label}.",
                )
            )

    # 6. Check Active Mahadasha / Antardasha claims
    if dasha:
        for match in _RE_DASHA.finditer(text):
            claimed_lord = BODY_ALIASES[match.group("lord").lower()]
            level_raw = match.group("level").lower().replace(" ", "")
            is_maha = level_raw == "mahadasha"
            expected_lord = (
                dasha.get("mahadasha") if is_maha else dasha.get("antardasha")
            )
            if not expected_lord:
                continue
            expected_lord_str = str(expected_lord).lower()
            ok = claimed_lord == expected_lord_str
            level_label = "mahadasha" if is_maha else "antardasha"
            checks.append(
                ClaimCheckResult(
                    category=level_label,
                    subject=level_label,
                    matched_text=match.group(0),
                    claimed_value=claimed_lord,
                    expected_value=expected_lord_str,
                    is_valid=ok,
                    correction=None
                    if ok
                    else f"Active {level_label} is {expected_lord_str.title()}, not {claimed_lord.title()}.",
                )
            )

    verified = tuple(c for c in checks if c.is_valid)
    contradictions = tuple(c for c in checks if not c.is_valid)
    passed = len(contradictions) == 0

    audit_payload = {
        "fact_sheet_sha256": fact_sha,
        "passed": passed,
        "total_claims_checked": len(checks),
        "verified": [c.__dict__ for c in verified],
        "contradictions": [c.__dict__ for c in contradictions],
    }

    return HallucinationAudit(
        passed=passed,
        total_claims_checked=len(checks),
        verified_claims=verified,
        contradictions=contradictions,
        fact_sheet_sha256=fact_sha,
        receipt_sha256=_sha256_json(audit_payload),
    )


__all__ = [
    "AIFactSheet",
    "ClaimCheckResult",
    "ENGLISH_SIGN_NAMES",
    "HallucinationAudit",
    "SCHEMA_VERSION",
    "compile_ai_fact_sheet",
    "verify_ai_interpretation",
]
