"""Tests for expanded CLI subcommands (jyotish, fact-sheet, eclipses) and top-level exports."""

from __future__ import annotations

import json
import pytest

import ephemeris_oss
from ephemeris_oss.cli import main


def test_top_level_exports_complete() -> None:
    expected = {
        "AIFactSheet",
        "EarthOrientation",
        "Engine",
        "EphemerisError",
        "HallucinationAudit",
        "Houses",
        "Result",
        "Undefined",
        "VedicChartAnalysis",
        "compact_kernel",
        "compile_ai_fact_sheet",
        "compute_vedic_chart_analysis",
        "eclipses",
        "fact_sheet",
        "jyotish",
        "jyotish_advanced",
        "jyotish_jaimini",
        "jyotish_transit",
        "phenomena",
        "rust_bridge",
        "uncertainty_envelope",
        "verify_ai_interpretation",
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
