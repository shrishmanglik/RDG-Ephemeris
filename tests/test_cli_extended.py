"""Tests for expanded CLI subcommands (jyotish, fact-sheet, eclipses, svg) and top-level exports."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
import pytest

import ephemeris_oss
from ephemeris_oss.cli import main


def test_top_level_exports_complete() -> None:
    expected = {
        "AIFactSheet",
        "AnalyticalEphemerisProvider",
        "CompleteKundaliBundle",
        "EarthOrientation",
        "Engine",
        "EphemerisAdapter",
        "EphemerisError",
        "HallucinationAudit",
        "HouseSystemResult",
        "Houses",
        "PlanetCoordinateResult",
        "Result",
        "Undefined",
        "VedicChartAnalysis",
        "adapter",
        "almanac",
        "compact_kernel",
        "compile_ai_fact_sheet",
        "compute_vedic_chart_analysis",
        "fact_sheet",
        "jyotish",
        "jyotish_advanced",
        "jyotish_jaimini",
        "jyotish_nadi",
        "jyotish_rectification",
        "jyotish_siddhanta",
        "jyotish_transit",
        "normalize_ephemeris_source",
        "phenomena",
        "rust_bridge",
        "uncertainty_envelope",
        "verify_ai_interpretation",
        "visualization",
    }
    assert expected.issubset(set(ephemeris_oss.__all__))
    for name in expected:
        assert hasattr(ephemeris_oss, name)


def test_cli_jyotish_json_compact(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(
        [
            "jyotish",
            "--at",
            "2026-10-06T12:00:00Z",
            "--lat",
            "28.6139",
            "--lon",
            "77.2090",
            "--compact",
            "--json",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["schema_version"] == "ephemeris-oss.fact-sheet.v1"
    assert "ascendant" in payload
    assert "sun" in payload["bodies"]
    assert "moon" in payload["bodies"]
    assert "rahu" in payload["bodies"]
    assert "ketu" in payload["bodies"]
    assert len(payload["receipt_sha256"]) == 64


def test_cli_jyotish_human_readable_compact(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(
        [
            "jyotish",
            "--at",
            "2026-10-06T12:00:00Z",
            "--lat",
            "28.6139",
            "--lon",
            "77.2090",
            "--compact",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "Ascendant:" in out
    assert "Receipt SHA-256:" in out


def test_cli_fact_sheet_compact_under_3kb(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(
        [
            "fact-sheet",
            "--at",
            "2026-10-06T12:00:00Z",
            "--lat",
            "28.6139",
            "--lon",
            "77.2090",
            "--compact",
            "--max-bytes",
            "2800",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out.strip()
    assert len(out.encode("utf-8")) <= 2800
    parsed = json.loads(out)
    assert parsed["schema_version"] == "ephemeris-oss.fact-sheet.v1"


def test_cli_svg_renders_valid_xml(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(
        [
            "svg",
            "--at",
            "2026-10-06T12:00:00Z",
            "--lat",
            "28.6139",
            "--lon",
            "77.2090",
            "--style",
            "north_indian",
            "--varga",
            "D9",
            "--compact",
        ]
    )
    assert rc == 0
    svg_text = capsys.readouterr().out.strip()
    root = ET.fromstring(svg_text)
    assert root.tag.endswith("svg")
    assert root.attrib["data-varga"] == "D9"


def test_cli_eclipses_json(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(
        [
            "eclipses",
            "--start",
            "2024-03-01T00:00:00Z",
            "--end",
            "2024-05-01T00:00:00Z",
            "--lat",
            "32.7767",
            "--lon",
            "-96.7970",
            "--json",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert len(payload["solar_eclipses"]) == 1
    assert payload["solar_eclipses"][0]["classification"] == "total"
    assert payload["solar_eclipses"][0]["local_circumstances"]["classification"] == "total"
    assert len(payload["lunar_eclipses"]) == 1
    assert payload["lunar_eclipses"][0]["classification"] == "penumbral"


def test_cli_panchang_siddhanta_and_table(capsys: pytest.CaptureFixture[str]) -> None:
    rc_p = main(["panchang", "--year", "2026", "--month", "1", "--json"])
    assert rc_p == 0
    p_payload = json.loads(capsys.readouterr().out)
    assert p_payload["year"] == 2026
    assert len(p_payload["days"]) == 31

    rc_s = main(["siddhanta", "--at", "2026-01-01T00:00:00Z", "--json"])
    assert rc_s == 0
    s_payload = json.loads(capsys.readouterr().out)
    assert "positions" in s_payload
    assert len(s_payload["receipt_sha256"]) == 64

    rc_t = main(
        [
            "table",
            "--start",
            "2026-01-01T00:00:00Z",
            "--end",
            "2026-01-03T00:00:00Z",
            "--step-days",
            "1.0",
            "--format",
            "csv",
        ]
    )
    assert rc_t == 0
    csv_out = capsys.readouterr().out
    assert "jd_ut,iso_utc" in csv_out
