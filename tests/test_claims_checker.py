"""Tests for the Claim-Integrity Rule Engine, Browser Ephemeris Engine, and Benchmark Observatory."""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from ephemeris_oss.engine.conventions import ayanamsa_degrees, mean_lunar_node_longitude_degrees

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_tool_module(name: str, rel_path: str):
    path = REPO_ROOT / rel_path
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


check_claims = _load_tool_module("check_claims", "tools/check_claims.py")
check_internal_ids = _load_tool_module("check_internal_ids", "tools/check_internal_ids.py")
check_provenance = _load_tool_module("check_provenance", "tools/check_provenance.py")


def test_check_claims_self_test_passes() -> None:
    assert check_claims.self_test() == 0


def test_claims_manifest_matches_accuracy_and_readme() -> None:
    findings = check_claims.verify_manifest_against_docs(REPO_ROOT)
    assert findings == [], f"Unexpected claim findings: {findings}"


def test_claims_checker_catches_planted_mismatch_and_hyperbole(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir(parents=True, exist_ok=True)
    acc = (REPO_ROOT / "docs" / "ACCURACY.md").read_text(encoding="utf-8")
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    claims = (REPO_ROOT / "docs" / "claims.yaml").read_text(encoding="utf-8")

    (tmp_path / "docs" / "claims.yaml").write_text(claims, encoding="utf-8")
    (tmp_path / "docs" / "ACCURACY.md").write_text(
        acc.replace("3.80815838e-06", "9.99999999e-06", 1),
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text(
        readme + "\nWe are the best in the world and beats any ephemeris.\n",
        encoding="utf-8",
    )

    findings = check_claims.verify_manifest_against_docs(tmp_path)
    assert any("GRAHA_ROW_MISMATCH" in f for f in findings)
    assert any("BANNED_HYPERBOLE" in f for f in findings)


def test_deliverable_files_exist_and_pass_provenance_and_internal_id_gates() -> None:
    required_files = [
        REPO_ROOT / "docs" / "claims.yaml",
        REPO_ROOT / "tools" / "check_claims.py",
        REPO_ROOT / "web" / "ephemeris-browser.js",
        REPO_ROOT / "web" / "ephemeris-browser.d.ts",
        REPO_ROOT / "docs" / "benchmark-portal" / "index.html",
    ]
    for path in required_files:
        assert path.is_file(), f"Missing required deliverable: {path}"
        content = path.read_text(encoding="utf-8")
        assert "\u2014" not in content, f"Em dash found in {path}"

    for target in (REPO_ROOT / "web", REPO_ROOT / "docs", REPO_ROOT / "tools"):
        id_hits = check_internal_ids.scan(target)
        assert id_hits == [], f"Internal ID findings in {target}: {id_hits}"

    allow = check_provenance.load_allow(REPO_ROOT / "tools" / "provenance-allow.txt")
    for target in (REPO_ROOT / "web", REPO_ROOT / "docs", REPO_ROOT / "tools"):
        prov_findings, _ = check_provenance.scan(target, allow)
        assert prov_findings == [], f"Provenance findings in {target}: {prov_findings}"


def test_generated_manifest_refuses_any_swiss_filenames(tmp_path):
    metadata = tmp_path / "ephemeris_oss.egg-info" / "SOURCES.txt"
    metadata.parent.mkdir()
    metadata.write_text("src/other_swisseph.py\n", encoding="utf-8")
    findings, _ = check_provenance.scan(tmp_path, {})
    assert any(item.rule == "SOURCE" for item in findings)


def test_benchmark_portal_contains_verified_ledger_and_shodashvarga_workbench() -> None:
    portal_html = (REPO_ROOT / "docs" / "benchmark-portal" / "index.html").read_text(encoding="utf-8")
    manifest = check_claims.load_claims_manifest(REPO_ROOT / "docs" / "claims.yaml")

    for graha in manifest["physical_grahas"]:
        assert graha["target_label"] in portal_html
        assert graha["horizons_p95_arcsec"] in portal_html
        assert graha["horizons_worst_arcsec"] in portal_html
        assert graha["de440_worst_arcsec"] in portal_html

    for varga in ("D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"):
        assert varga in portal_html


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js runtime not installed")
def test_browser_ephemeris_engine_parity_and_sub_2ms_execution() -> None:
    script = """
    import('./web/ephemeris-browser.js').then((m) => {
      const c1 = m.computeChart({
        jdTt: 2451545.0,
        latitudeDeg: 28.6139,
        longitudeDeg: 77.2090,
        ayanamsa: 'lahiri',
        nodeMode: 'mean'
      });
      const c2 = m.computeChart({
        jdTt: 2451545.0,
        latitudeDeg: 28.6139,
        longitudeDeg: 77.2090,
        ayanamsa: 'lahiri',
        nodeMode: 'mean'
      });
      const c3 = m.computeChart({
        jdTt: 2451546.0,
        latitudeDeg: 28.6139,
        longitudeDeg: 77.2090,
        ayanamsa: 'raman',
        nodeMode: 'true'
      });
      const timings = [];
      for (let i = 0; i < 15; i++) {
        timings.push(m.computeChart({ jdTt: 2451545.0 + i }).executionTimeMs);
      }
      timings.sort((a, b) => a - b);
      const medianMs = timings[Math.floor(timings.length / 2)];
      console.log(JSON.stringify({
        medianMs,
        sarvaTotal: c1.ashtakavarga.totalBindus,
        vargaCodes: Object.keys(c1.shodashvarga),
        grahaIds: Object.keys(c1.grahas),
        shadbalaIds: Object.keys(c1.shadbala),
        mahaCount: c1.vimshottari.mahadashas.length,
        mahaTotalYears: c1.vimshottari.mahadashas.reduce((s, x) => s + x.totalYears, 0),
        receipt1: c1.receipt.sha256,
        receipt2: c2.receipt.sha256,
        receipt3: c3.receipt.sha256,
        ayanamsasJ2000: {
          lahiri: m.computeAyanamsa(2451545.0, 'lahiri'),
          raman: m.computeAyanamsa(2451545.0, 'raman'),
          krishnamurti: m.computeAyanamsa(2451545.0, 'krishnamurti'),
          true_citra: m.computeAyanamsa(2451545.0, 'true_citra')
        },
        meanNodeJ2000: m.computeMeanLunarNode(2451545.0),
        panchangaKeys: Object.keys(c1.panchanga)
      }));
    });
    """
    proc = subprocess.run(
        ["node", "-e", script],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    payload = json.loads(proc.stdout.strip())

    assert payload["medianMs"] < 2.0, f"Expected sub-2ms execution, got {payload['medianMs']} ms"
    assert payload["sarvaTotal"] == 337
    assert len(payload["vargaCodes"]) == 16
    assert set(payload["grahaIds"]) == {
        "sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"
    }
    assert set(payload["shadbalaIds"]) == {
        "sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"
    }
    assert payload["mahaCount"] == 9
    assert payload["mahaTotalYears"] == 120
    assert payload["receipt1"] == payload["receipt2"]
    assert payload["receipt1"] != payload["receipt3"]
    assert set(payload["panchangaKeys"]) == {"tithi", "vara", "nakshatra", "yoga", "karana"}

    # Verify exact parity with Python conventions.py at J2000.0
    assert abs(payload["ayanamsasJ2000"]["lahiri"] - ayanamsa_degrees(2451545.0, "lahiri")) < 1e-6
    assert abs(payload["ayanamsasJ2000"]["raman"] - ayanamsa_degrees(2451545.0, "raman")) < 1e-6
    assert abs(payload["ayanamsasJ2000"]["krishnamurti"] - ayanamsa_degrees(2451545.0, "kp")) < 1e-6
    assert abs(payload["meanNodeJ2000"] - mean_lunar_node_longitude_degrees(2451545.0)) < 1e-9
