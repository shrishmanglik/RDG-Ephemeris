"""Tests for the T1 Horizons truth fetcher.

The parse test reads a real response committed under ``bench/data/horizons/``; it
is skipped only when no response has been fetched yet, and says so.
"""

from __future__ import annotations

import json
import shutil
import sys
import urllib.parse
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bench.truth import horizons  # noqa: E402

DATA_DIR = REPO_ROOT / "bench" / "data" / "horizons"


def _query(url: str) -> dict[str, list[str]]:
    return urllib.parse.parse_qs(urllib.parse.urlsplit(url).query, keep_blank_values=True)


def test_request_builder_emits_exactly_the_jd_strings_given():
    jds = ["2451545.000000000", "2415020.512345678", "2466154.499999999"]
    url = horizons.build_request(301, jds, "LT+S")
    assert url.startswith("https://ssd.jpl.nasa.gov/api/horizons.api?")
    q = _query(url)
    assert q["TLIST"] == ["'2451545.000000000' '2415020.512345678' '2466154.499999999'"]
    assert horizons.tlist_values(url) == jds
    assert q["COMMAND"] == ["'301'"]
    assert q["VEC_CORR"] == ["'LT+S'"]
    assert q["CENTER"] == ["'500@399'"]
    assert q["TIME_TYPE"] == ["'TDB'"]
    assert q["TLIST_TYPE"] == ["'JD'"]
    assert q["VEC_TABLE"] == ["'1'"]
    assert q["REF_SYSTEM"] == ["'ICRF'"]
    assert q["REF_PLANE"] == ["'FRAME'"]
    assert q["OUT_UNITS"] == ["'AU-D'"]
    assert q["CSV_FORMAT"] == ["'YES'"]
    assert q["format"] == ["json"]


def test_request_builder_refuses_bad_input():
    with pytest.raises(ValueError):
        horizons.build_request(301, ["2451545.0"], "NONE")  # not 9 decimals
    with pytest.raises(ValueError):
        horizons.build_request(301, ["2451545.000000000"], "XX")
    with pytest.raises(ValueError):
        horizons.build_request(301, [], "NONE")
    with pytest.raises(ValueError):
        horizons.build_request(301, ["2451545.000000000"] * (horizons.CHUNK + 1), "NONE")


SYNTHETIC = {
    "signature": {"version": "1.2", "source": "NASA/JPL Horizons API"},
    "result": (
        "Target body name: Moon (301)                      {source: DE441}\n"
        "Center body name: Earth (399)                     {source: DE441}\n"
        "$$SOE\n"
        "2451545.000000000, A.D. 2000-Jan-01 12:00:00.0000, -1.0E-03, 2.0E-03, 3.0E-04,\n"
        "2451546.500000000, A.D. 2000-Jan-03 00:00:00.0000, -1.5E-03, 1.0E-03, 2.0E-04,\n"
        "$$EOE\n"
    ),
}


def test_parse_synthetic_rows():
    rows = horizons.parse(json.dumps(SYNTHETIC).encode())
    assert [r["jd_tdb_echoed"] for r in rows] == ["2451545.000000000", "2451546.500000000"]
    assert rows[0]["x"] == -1.0e-3 and rows[0]["y"] == 2.0e-3 and rows[0]["z"] == 3.0e-4
    assert horizons.ephemeris_source(json.dumps(SYNTHETIC).encode()) == "DE441"


def _tmp_store(tmp_path: Path) -> Path:
    raw = json.dumps(SYNTHETIC).encode()
    sha = horizons.sha256_hex(raw)
    (tmp_path / f"{sha}.json").write_bytes(raw)
    manifest = {
        "entries": [
            {
                "url": horizons.build_request(301, ["2451545.000000000", "2451546.500000000"], "NONE"),
                "body": 301,
                "vec_corr": "NONE",
                "n_epochs": 2,
                "jd_tdb_requested": ["2451545.000000000", "2451546.500000000"],
                "sha256": sha,
            }
        ]
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return tmp_path


def test_verify_passes_on_clean_store(tmp_path):
    store = _tmp_store(tmp_path)
    assert horizons.verify(store / "manifest.json") == 1


def test_verify_catches_one_altered_byte(tmp_path):
    store = _tmp_store(tmp_path)
    target = next(p for p in store.glob("*.json") if p.name != "manifest.json")
    data = bytearray(target.read_bytes())
    data[len(data) // 2] ^= 0x01
    target.write_bytes(bytes(data))
    with pytest.raises(horizons.VoidRun, match="sha256 mismatch"):
        horizons.verify(store / "manifest.json")


def test_verify_catches_echo_mismatch(tmp_path):
    store = _tmp_store(tmp_path)
    m = json.loads((store / "manifest.json").read_text(encoding="utf-8"))
    m["entries"][0]["jd_tdb_requested"][1] = "2451546.500000001"
    (store / "manifest.json").write_text(json.dumps(m), encoding="utf-8")
    with pytest.raises(horizons.VoidRun, match="echo"):
        horizons.verify(store / "manifest.json")


def _real_responses() -> list[Path]:
    if not (DATA_DIR / "manifest.json").exists():
        return []
    m = json.loads((DATA_DIR / "manifest.json").read_text(encoding="utf-8"))
    return [DATA_DIR / f"{e['sha256']}.json" for e in m["entries"]]


def test_parse_saved_real_response():
    files = _real_responses()
    if not files:
        pytest.skip("no Horizons response fetched yet")
    raw = files[0].read_bytes()
    rows = horizons.parse(raw)
    assert rows, "a real response parsed to zero rows"
    for r in rows:
        assert len(r["jd_tdb_echoed"].split(".")[1]) == 9
        dist = (r["x"] ** 2 + r["y"] ** 2 + r["z"] ** 2) ** 0.5
        assert 1e-3 < dist < 3.0  # moon, sun and mars all sit in this geocentric range, au
    assert horizons.ephemeris_source(raw).startswith("DE4")


def test_verify_real_store_and_its_copy_with_one_flipped_byte(tmp_path):
    files = _real_responses()
    if not files:
        pytest.skip("no Horizons response fetched yet")
    assert horizons.verify(DATA_DIR / "manifest.json") == len(files)
    for f in files:
        shutil.copy(f, tmp_path / f.name)
    shutil.copy(DATA_DIR / "manifest.json", tmp_path / "manifest.json")
    victim = tmp_path / files[0].name
    data = bytearray(victim.read_bytes())
    data[100] ^= 0x20
    victim.write_bytes(bytes(data))
    with pytest.raises(horizons.VoidRun):
        horizons.verify(tmp_path / "manifest.json")


def test_verify_pairs_echoes_by_value_not_position(tmp_path):
    # Horizons prints TLIST rows in ascending time, whatever order they were requested in.
    store = _tmp_store(tmp_path)
    m = json.loads((store / "manifest.json").read_text(encoding="utf-8"))
    m["entries"][0]["jd_tdb_requested"].reverse()
    (store / "manifest.json").write_text(json.dumps(m), encoding="utf-8")
    assert horizons.verify(store / "manifest.json") == 1
