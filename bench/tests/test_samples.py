from __future__ import annotations

from decimal import Decimal

import pytest

from bench.harness import samples as S


def test_same_seed_same_rows_and_bytes(tmp_path):
    a = S.make_samples(7, 3, ["moon", "mars"], ["E1", "E4"], ["geometric", "apparent"])
    b = S.make_samples(7, 3, ["moon", "mars"], ["E1", "E4"], ["geometric", "apparent"])
    assert a == b
    pa, pb = tmp_path / "a.jsonl", tmp_path / "b.jsonl"
    S.write_samples(a, pa)
    S.write_samples(b, pb)
    assert pa.read_bytes() == pb.read_bytes()
    assert S.sample_sha256(pa) == S.sample_sha256(pb)
    assert len(S.sample_sha256(pa)) == 64


def test_different_seed_differs():
    a = S.make_samples(1, 2, ["sun"], ["E1"], ["geometric"])
    b = S.make_samples(2, 2, ["sun"], ["E1"], ["geometric"])
    assert [r["jd_tdb"] for r in a] != [r["jd_tdb"] for r in b]


def test_stratum_draws_do_not_depend_on_other_strata():
    alone = S.make_samples(5, 4, ["moon"], ["E2"], ["astrometric"])
    mixed = S.make_samples(5, 4, ["sun", "moon"], ["E1", "E2"], ["geometric", "astrometric"])
    picked = [r for r in mixed if r["body"] == "moon" and r["era"] == "E2" and r["mode"] == "astrometric"]
    assert alone == picked


def test_row_shape_and_era_bounds():
    rows = S.make_samples(11, 50, list(S.BODIES), list(S.ERAS), list(S.MODES))
    assert len(rows) == 50 * len(S.BODIES) * len(S.ERAS) * len(S.MODES)
    assert len({r["id"] for r in rows}) == len(rows)
    for row in rows:
        assert set(row) == {"id", "body", "era", "mode", "jd_tdb"}
        whole, frac = row["jd_tdb"].split(".")
        assert len(frac) == 9
        start, end = S.ERAS[row["era"]]
        assert Decimal(str(start)) <= Decimal(row["jd_tdb"]) < Decimal(str(end))


def test_era_bounds_are_the_documented_years():
    # 1900-01-01 0h TDB is JD 2415020.5; 2026-01-01 is 2461041.5.
    assert S.ERAS["E1"] == (2415020.5, 2461041.5)
    assert S.ERAS["E3"][1] == S.ERAS["E1"][0]
    assert S.ERAS["E2"][0] == S.ERAS["E1"][1]
    assert S.ERAS["E4"][0] == S.ERAS["E2"][1]


def test_rejects_unknown_names():
    with pytest.raises(ValueError):
        S.make_samples(1, 1, ["vulcan"], ["E1"], ["geometric"])
    with pytest.raises(ValueError):
        S.make_samples(1, 1, ["sun"], ["E9"], ["geometric"])
    with pytest.raises(ValueError):
        S.make_samples(1, 1, ["sun"], ["E1"], ["topocentric"])


def test_read_round_trip(tmp_path):
    rows = S.make_samples(3, 2, ["venus"], ["E3"], ["apparent"])
    path = tmp_path / "s.jsonl"
    S.write_samples(rows, path)
    assert S.read_samples(path) == rows
    assert b"\r\n" not in path.read_bytes()


def test_split_jd_is_exact():
    whole, frac = S.split_jd("2451545.123456789")
    assert whole == 2451545.0
    assert frac == pytest.approx(0.123456789, abs=0)
