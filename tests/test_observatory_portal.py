"""Tests for the Stage 4 Interactive 18-Pillar HTML Observatory & Benchmark Portal."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WEB_OBSERVATORY_HTML = REPO_ROOT / "web" / "observatory" / "index.html"
BENCHMARK_PORTAL_HTML = REPO_ROOT / "docs" / "benchmark-portal" / "index.html"
PLAYGROUND_HTML = REPO_ROOT / "docs" / "playground" / "index.html"
CLAIMS_YAML = REPO_ROOT / "docs" / "claims.yaml"


def _load_observatory_html() -> str:
    return WEB_OBSERVATORY_HTML.read_text(encoding="utf-8")


def _load_portal_html() -> str:
    return BENCHMARK_PORTAL_HTML.read_text(encoding="utf-8")


def _load_claims() -> dict:
    return json.loads(CLAIMS_YAML.read_text(encoding="utf-8"))


def test_observatory_and_portal_files_exist_and_are_complete_html5() -> None:
    for path in (WEB_OBSERVATORY_HTML, BENCHMARK_PORTAL_HTML):
        assert path.is_file(), f"Missing HTML file: {path}"
        content = path.read_text(encoding="utf-8")
        assert content.startswith("<!DOCTYPE html>")
        assert '<html lang="en">' in content
        assert content.rstrip().endswith("</html>")
        assert len(content) > 100_000


def test_module_imports_and_parity_between_observatory_and_portal() -> None:
    obs = _load_observatory_html()
    portal = _load_portal_html()
    assert '<script type="module" src="../ephemeris-browser.js"></script>' in obs
    assert '<script type="module" src="../../web/ephemeris-browser.js"></script>' in portal
    assert obs.replace("../ephemeris-browser.js", "../../web/ephemeris-browser.js") == portal


def test_zero_em_dashes_in_observatory_and_portal() -> None:
    em_dash = "\u2014"
    for path in (WEB_OBSERVATORY_HTML, BENCHMARK_PORTAL_HTML):
        content = path.read_text(encoding="utf-8")
        assert em_dash not in content, f"Found forbidden em dash in {path}"


def test_zero_forbidden_claims_or_provenance_tokens() -> None:
    claims = _load_claims()
    forbidden_phrases = claims.get("banned_hyperbole_phrases", [])
    for path in (WEB_OBSERVATORY_HTML, BENCHMARK_PORTAL_HTML):
        lower = path.read_text(encoding="utf-8").lower()
        for phrase in forbidden_phrases:
            assert phrase.lower() not in lower, f"Forbidden phrase {phrase!r} in {path}"


def test_all_seven_scientific_instrument_panels_present() -> None:
    obs = _load_observatory_html()
    for panel_idx in range(1, 8):
        assert f'id="panel{panel_idx}"' in obs, f"Missing panel{panel_idx}"
        assert f'data-tab="panel{panel_idx}"' in obs, f"Missing tab button for panel{panel_idx}"
    assert "18-Pillar" in obs


def test_panel1_five_style_svg_chart_workbench_and_sha256_receipt() -> None:
    obs = _load_observatory_html()
    for container_id in (
        "svgMountNorth",
        "svgMountSouth",
        "svgMountEast",
        "svgMountWheel",
        "svgMountSbc",
        "receiptInspector",
        "headerLatencyBadge",
        "panchangaGrid",
        "grahaTableBody",
    ):
        assert container_id in obs, f"Missing Panel 1 element {container_id}"
    for style_label in (
        "North Indian Diamond",
        "South Indian 4x4 Grid",
        "East Indian 3x3 Surya Chakra",
        "360-Degree Zodiac/Nakshatra Wheel",
        "81-Cell 9x9 Sarvatobhadra Chakra",
    ):
        assert style_label in obs


def test_panel2_de440_and_horizons_residuals_match_claims_yaml() -> None:
    obs = _load_observatory_html()
    claims = _load_claims()
    for body_cfg in claims["physical_grahas"]:
        assert body_cfg["target_label"] in obs
        assert str(body_cfg["horizons_p95_arcsec"]) in obs
        assert str(body_cfg["horizons_worst_arcsec"]) in obs
        assert str(body_cfg["de440_worst_arcsec"]) in obs
    assert "3,612" in obs
    assert "2,100" in obs
    assert "1.84 MB" in obs
    assert "de440_compact.bin.zlib" in obs


def test_panel2_lunar_node_replay_and_researcher_benchmark_metrics() -> None:
    obs = _load_observatory_html()
    claims = _load_claims()
    ln = claims["lunar_nodes"]
    for val in (
        ln["mean_rahu_median_arcsec"],
        ln["mean_rahu_max_arcsec"],
        ln["true_rahu_typical_arcsec"],
        ln["true_rahu_worst_arcsec"],
        ln["antipode_residual_arcsec"],
        ln["legacy_mean_rahu_worst_arcsec"],
    ):
        assert str(val) in obs
    for metric_token in (
        "5.9635", "7.6404", "3.2652", "5.9134", "0.987681",
        "5.6203", "10.4830", "3.1937", "6.8014", "0.995893",
    ):
        assert metric_token in obs


def test_panel3_twenty_parashari_vargas_and_shashtiamsa_deities() -> None:
    obs = _load_observatory_html()
    varga_codes = [
        "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10",
        "D11", "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60",
    ]
    for code in varga_codes:
        assert f'code: "{code}"' in obs, f"Missing Varga definition for {code}"
    assert "D60_NAMES" in obs
    assert "vargaPillGrid" in obs
    assert "vargaDetailTableBody" in obs


def test_panel3_five_level_vimshottari_shadbala_and_337_ashtakavarga() -> None:
    obs = _load_observatory_html()
    for token in (
        "computeVimshottariDasha",
        "pratyantaraLord",
        "sookshmaLord",
        "pranaLord",
        "computeShadbala",
        "shadbalaTableBody",
        "computeAshtakavarga",
        "bhinnaMatrixBody",
        "337",
    ):
        assert token in obs


def test_panel4_kp_249_sub_lords_varshphal_ashtakoota_and_70_yogas() -> None:
    obs = _load_observatory_html()
    for token in (
        "computeKpSubLords",
        "kpTableBody",
        "evaluate70YogasSummary",
        "yogasTableBody",
        "varshphalSummaryBox",
        "sahamsTableBody",
        "Punya Saham",
        "ashtakootaTableBody",
        "36.0 Gunas",
    ):
        assert token in obs


def test_panel5_jaimini_karakas_arudha_padas_bhrigu_and_rectification() -> None:
    obs = _load_observatory_html()
    for token in (
        "jaiminiKarakasBody",
        "arudhaPadasGrid",
        "bnnSummaryBox",
        "bnnCircuitsBody",
        "rectificationCurveSvg",
        "rectificationTableBody",
        "sensitivityTableBody",
        "Atmakaraka",
        "Bhrigu Bindu",
        "Kunda (81x)",
    ):
        assert token in obs


def test_panel6_besselian_eclipses_drik_panchang_and_surya_siddhanta() -> None:
    obs = _load_observatory_html()
    for token in (
        "almanacSummaryGrid",
        "muhurtaTableBody",
        "eclipseCatalogBody",
        "siddhantaTableBody",
        "Amanta",
        "Purnimanta",
        "Ahargana",
        "Manda",
    ):
        assert token in obs


def test_panel7_ai_fact_sheet_and_hallucination_firewall_playground() -> None:
    obs = _load_observatory_html()
    for token in (
        "ephemeris-oss.fact-sheet.v1",
        "compileAiFactSheetJs",
        "verifyAiReadingJs",
        "HALLUCINATED_SIGN",
        "HALLUCINATED_HOUSE",
        "HALLUCINATED_LAGNA",
        "HALLUCINATED_DASHA",
        "factSheetJsonBox",
        "firewallResultsContainer",
        "3,072",
    ):
        assert token in obs


def test_playground_theme_switcher_and_attribution_badge() -> None:
    expected_badge = "Engineered by The AGI Studio & V" + "edic Astro Studio"
    for path in (WEB_OBSERVATORY_HTML, BENCHMARK_PORTAL_HTML, PLAYGROUND_HTML):
        assert path.is_file(), f"Missing HTML file: {path}"
        html = path.read_text(encoding="utf-8")
        assert 'data-testid="canvas-theme-switcher"' in html
        assert "44px" in html
        for theme_id in ("void", "paper", "contrast", "daltonic"):
            assert f'data-theme="{theme_id}"' in html or f'data-theme-option="{theme_id}"' in html
        for hex_token in ("#0A0A0E", "#FAF5EE", "#C84B31", "#000000", "#FFE600", "#06162E", "#56B4E9", "#D55E00"):
            assert hex_token in html.upper(), f"Missing theme token {hex_token} in {path}"
        assert expected_badge in html
        assert "\u2014" not in html
    assert PLAYGROUND_HTML.read_text(encoding="utf-8") == BENCHMARK_PORTAL_HTML.read_text(encoding="utf-8")


def test_speedup_calculator_and_mcp_config_copy_across_all_html_surfaces() -> None:
    for path in (WEB_OBSERVATORY_HTML, BENCHMARK_PORTAL_HTML, PLAYGROUND_HTML):
        html = path.read_text(encoding="utf-8")
        assert 'data-testid="ephemeris-speedup-calculator"' in html
        assert 'data-testid="copy-mcp-config-btn"' in html
        for batch_size in ("100", "1000", "10000"):
            assert f'data-batch-size="{batch_size}"' in html
        for token in (
            "agi-ephemeris",
            "12.50x",
            "15.07x",
            "0.001 arcsec",
            "Apache-2.0",
            "mcpServers",
            "ephemeris-oss-mcp",
        ):
            assert token in html, f"Missing speedup/MCP token {token!r} in {path}"
        assert "\u2014" not in html


def test_license_savings_calculator_and_apache_attribution_copy_across_all_html_surfaces() -> None:
    for path in (WEB_OBSERVATORY_HTML, BENCHMARK_PORTAL_HTML, PLAYGROUND_HTML):
        html = path.read_text(encoding="utf-8")
        assert 'data-testid="ephemeris-license-savings-calculator"' in html
        assert 'data-testid="copy-apache-attribution-btn"' in html
        for tier_id in ("indie", "saas", "fleet"):
            assert f'data-license-tier="{tier_id}"' in html
        for token in (
            "Indie Astrology App",
            "Multi-Surface SaaS + Mobile App",
            "Enterprise Research &amp; Autonomous Fleet",
            "$0 royalties forever",
            "Apache-2.0 permissive commercial freedom",
            "0.001 arcsec JPL DE440 precision",
        ):
            assert token in html, f"Missing license/attribution token {token!r} in {path}"
        assert "\u2014" not in html


def test_ayanamsa_precision_inspector_and_python_quickstart_copy_across_all_html_surfaces() -> None:
    for path in (WEB_OBSERVATORY_HTML, BENCHMARK_PORTAL_HTML, PLAYGROUND_HTML):
        html = path.read_text(encoding="utf-8")
        assert 'data-testid="ayanamsa-precision-inspector"' in html
        assert 'data-testid="copy-python-quickstart-btn"' in html
        for mode_id in ("lahiri", "krishnamurti", "raman"):
            assert f'data-ayanamsa-mode="{mode_id}"' in html
        for token in (
            "Lahiri (Chitrapaksha)",
            "Krishnamurti (KP)",
            "Raman",
            "Copied Python Quickstart",
            "compute_complete_kundali_bundle",
        ):
            assert token in html, f"Missing ayanamsa/quickstart token {token!r} in {path}"
        assert "\u2014" not in html




