"""Tests for deterministic AI fact-sheet compiler (< 3 KB) and astrological hallucination verifier."""

from __future__ import annotations

import json

from ephemeris_oss.fact_sheet import (
    AIFactSheet,
    HallucinationAudit,
    SCHEMA_VERSION,
    compile_ai_fact_sheet,
    verify_ai_interpretation,
)


SAMPLE_LONGITUDES = {
    "sun": 12.5,       # Aries (0), house 1, Ashwini (0)
    "moon": 45.0,      # Taurus (1), house 2, Rohini (3)
    "mars": 280.0,     # Capricorn (9), house 10, Uttara Ashadha (20)
    "mercury": 15.0,   # Aries (0), house 1, Bharani (1)
    "jupiter": 95.0,   # Cancer (3), house 4, Pushya (7)
    "venus": 350.0,    # Pisces (11), house 12, Revati (26)
    "saturn": 195.0,   # Libra (6), house 7, Swati (14)
    "rahu": 60.0,      # Gemini (2), house 3, Mrigashira (4)
    "ketu": 240.0,     # Sagittarius (8), house 9, Moola (18)
}

SAMPLE_SPEEDS = {
    "sun": 0.9856,
    "moon": 13.176,
    "mars": 0.52,
    "mercury": -0.65,  # Retrograde
    "jupiter": 0.12,
    "venus": 1.15,
    "saturn": -0.04,   # Retrograde
    "rahu": -0.053,
    "ketu": -0.053,
}


def test_compile_ai_fact_sheet_under_3kb_and_receipted() -> None:
    sheet = compile_ai_fact_sheet(
        SAMPLE_LONGITUDES,
        ascendant_lon_deg=5.0,  # Aries Ascendant
        planet_speeds_deg_per_day=SAMPLE_SPEEDS,
        birth_jd_ut=2451545.0,
        query_jd_ut=2461000.0,
        sunrise_jd_ut=2451544.75,
        sunset_jd_ut=2451545.25,
        latitude_deg=28.6139,
    )
    assert isinstance(sheet, AIFactSheet)
    assert sheet.schema_version == SCHEMA_VERSION
    assert sheet.byte_length <= 3000
    assert sheet.byte_length == len(sheet.json_str.encode("utf-8"))
    assert len(sheet.receipt_sha256) == 64

    parsed = json.loads(sheet.json_str)
    assert parsed["ascendant"]["sign"] == "Aries"
    assert parsed["bodies"]["sun"]["sign"] == "Aries"
    assert parsed["bodies"]["sun"]["house"] == 1
    assert parsed["bodies"]["moon"]["sign"] == "Taurus"
    assert parsed["bodies"]["moon"]["nakshatra"] == "Rohini"
    assert parsed["bodies"]["mercury"]["retro"] is True
    assert parsed["bodies"]["saturn"]["retro"] is True
    assert parsed["bodies"]["jupiter"]["retro"] is False
    assert "panchanga" in parsed
    assert "dasha" in parsed
    assert "shadbala_rupas" in parsed


def test_compile_ai_fact_sheet_determinism() -> None:
    s1 = compile_ai_fact_sheet(
        SAMPLE_LONGITUDES,
        ascendant_lon_deg=5.0,
        planet_speeds_deg_per_day=SAMPLE_SPEEDS,
        birth_jd_ut=2451545.0,
    )
    s2 = compile_ai_fact_sheet(
        dict(reversed(list(SAMPLE_LONGITUDES.items()))),
        ascendant_lon_deg=5.0,
        planet_speeds_deg_per_day=SAMPLE_SPEEDS,
        birth_jd_ut=2451545.0,
    )
    assert s1.receipt_sha256 == s2.receipt_sha256
    assert s1.json_str == s2.json_str


def test_compile_ai_fact_sheet_borderline_detection() -> None:
    borderline_lons = dict(SAMPLE_LONGITUDES)
    borderline_lons["sun"] = 29.95  # 3 arcminutes from Taurus boundary
    sheet = compile_ai_fact_sheet(borderline_lons, ascendant_lon_deg=0.05)
    warn_bodies = {w["body"] for w in sheet.payload["borderline_warnings"]}
    assert "sun" in warn_bodies
    assert "ascendant" in warn_bodies


def test_compile_ai_fact_sheet_strict_compaction_budget() -> None:
    sheet = compile_ai_fact_sheet(
        SAMPLE_LONGITUDES,
        ascendant_lon_deg=5.0,
        planet_speeds_deg_per_day=SAMPLE_SPEEDS,
        birth_jd_ut=2451545.0,
        max_bytes=1600,
    )
    assert sheet.byte_length <= 1600


def test_verify_ai_interpretation_passes_accurate_reading() -> None:
    sheet = compile_ai_fact_sheet(
        SAMPLE_LONGITUDES,
        ascendant_lon_deg=5.0,
        planet_speeds_deg_per_day=SAMPLE_SPEEDS,
        birth_jd_ut=2451545.0,
        query_jd_ut=2451545.5,
    )
    active_md = sheet.payload["dasha"]["mahadasha"]
    accurate_text = (
        f"With Aries Ascendant, Sun is in Aries in the 1st house and Moon is in Taurus "
        f"in the second house. Moon is placed in Rohini Nakshatra. Jupiter sits in Cancer "
        f"in the 4th house while Saturn is in Libra in the seventh bhava. "
        f"Retrograde Mercury and retrograde Saturn add depth, while Jupiter is direct. "
        f"The native is in {active_md.title()} Mahadasha."
    )
    audit = verify_ai_interpretation(accurate_text, sheet)
    assert isinstance(audit, HallucinationAudit)
    assert audit.passed is True
    assert len(audit.contradictions) == 0
    assert audit.total_claims_checked >= 9
    assert len(audit.receipt_sha256) == 64


def test_verify_ai_interpretation_catches_sign_and_house_hallucinations() -> None:
    sheet = compile_ai_fact_sheet(
        SAMPLE_LONGITUDES,
        ascendant_lon_deg=5.0,
        planet_speeds_deg_per_day=SAMPLE_SPEEDS,
    )
    hallucinated_text = (
        "With Libra Ascendant, Sun is in Leo in the 5th house, and Moon is in Scorpio "
        "in the eighth house."
    )
    audit = verify_ai_interpretation(hallucinated_text, sheet)
    assert audit.passed is False
    assert len(audit.contradictions) == 5
    categories = [c.category for c in audit.contradictions]
    assert categories.count("d1_sign") == 3
    assert categories.count("house") == 2
    assert any("Sun is in Aries, not Leo." in (c.correction or "") for c in audit.contradictions)


def test_verify_ai_interpretation_catches_nakshatra_and_motion_hallucinations() -> None:
    sheet = compile_ai_fact_sheet(
        SAMPLE_LONGITUDES,
        ascendant_lon_deg=5.0,
        planet_speeds_deg_per_day=SAMPLE_SPEEDS,
    )
    hallucinated_text = (
        "Moon is in Ashwini Nakshatra while Jupiter is retrograde and Saturn is direct."
    )
    audit = verify_ai_interpretation(hallucinated_text, sheet)
    assert audit.passed is False
    assert len(audit.contradictions) == 3
    cats = {c.category for c in audit.contradictions}
    assert cats == {"nakshatra", "motion"}


def test_verify_ai_interpretation_checks_d9_navamsa_and_dasha_claims() -> None:
    sheet = compile_ai_fact_sheet(
        SAMPLE_LONGITUDES,
        ascendant_lon_deg=5.0,
        planet_speeds_deg_per_day=SAMPLE_SPEEDS,
        birth_jd_ut=2451545.0,
        query_jd_ut=2451545.5,
    )
    sun_d9 = sheet.payload["bodies"]["sun"]["d9_sign"]
    # Sun at 12.5 deg Aries is in 4th Navamsa -> Cancer
    assert sun_d9 == "Cancer"

    text_ok = f"Sun is placed in {sun_d9} in D9 Navamsa."
    audit_ok = verify_ai_interpretation(text_ok, sheet)
    assert audit_ok.passed is True
    assert len(audit_ok.verified_claims) == 1
    assert audit_ok.verified_claims[0].category == "d9_sign"

    text_bad = "Sun is placed in Capricorn in Navamsa and the native runs Ketu Mahadasha."
    audit_bad = verify_ai_interpretation(text_bad, sheet)
    assert audit_bad.passed is False
    assert len(audit_bad.contradictions) == 2
