from __future__ import annotations

import json

import pytest

from bench.harness import samples as S
from bench.harness import scorecard as C


def test_format_rounds_to_picoarcsec_and_sorts_keys():
    text = C.render({"b": 0.1234567890123456, "a": [1.0, {"d": 2, "c": 3e-14}]})
    assert text == b'{"a":[1.0,{"c":0.0,"d":2}],"b":0.123456789012}\n'


def test_render_rejects_non_finite():
    with pytest.raises(ValueError):
        C.render({"x": float("nan")})


def test_missing_kernel_is_void(tmp_path):
    samples = tmp_path / "s.jsonl"
    S.write_samples(S.make_samples(1, 1, ["sun"], ["E1"], ["geometric"]), samples)
    out = tmp_path / "card.json"
    code = C.main(["--samples", str(samples), "--kernel", str(tmp_path / "nope.bsp"), "--out", str(out)])
    assert code == C.EXIT_VOID
    assert json.loads(out.read_text())["verdict"] == "VOID"


def test_wrong_kernel_hash_is_void(tmp_path):
    samples = tmp_path / "s.jsonl"
    S.write_samples(S.make_samples(1, 1, ["sun"], ["E1"], ["geometric"]), samples)
    fake = tmp_path / "de440.bsp"
    fake.write_bytes(b"not a kernel")
    out = tmp_path / "card.json"
    code = C.main(["--samples", str(samples), "--kernel", str(fake), "--out", str(out)])
    assert code == C.EXIT_VOID
    card = json.loads(out.read_text())
    assert "sha256" in card["void_reason"]


def test_unknown_engine_is_an_error(tmp_path, kernel_path):
    samples = tmp_path / "s.jsonl"
    S.write_samples(S.make_samples(1, 1, ["sun"], ["E1"], ["geometric"]), samples)
    with pytest.raises(SystemExit):
        C.main(["--samples", str(samples), "--kernel", str(kernel_path), "--out", str(tmp_path / "o"),
                "--engines", "ours,nonesuch"])


@pytest.fixture(scope="module")
def thirty_row_card(tmp_path_factory, kernel_path):
    base = tmp_path_factory.mktemp("card")
    rows = S.make_samples(30, 1, list(S.BODIES), ["E1"], list(S.MODES))
    assert len(rows) == 30
    samples = base / "s.jsonl"
    S.write_samples(rows, samples)
    outs = []
    for name in ("a.json", "b.json"):
        out = base / name
        assert C.main(["--samples", str(samples), "--kernel", str(kernel_path), "--out", str(out)]) == C.EXIT_PASS
        outs.append(out)
    return samples, outs


def test_two_runs_are_byte_identical(thirty_row_card):
    _, (a, b) = thirty_row_card
    assert a.read_bytes() == b.read_bytes()


def test_card_contents(thirty_row_card, kernel_path):
    samples, (a, _) = thirty_row_card
    raw = a.read_text(encoding="utf-8")
    card = json.loads(raw)
    assert card["sample_sha256"] == S.sample_sha256(samples)
    assert card["kernel_sha256"] == C.DE440_SHA256
    assert card["package_version"]
    assert card["verdict"] == "PASS"
    assert card["truth"] == "t2"
    strata = card["engines"]["ours"]["strata"]
    assert len(strata) == 30
    first = strata[sorted(strata)[0]]
    for stat in ("separation_arcsec", "ecliptic_max_component_arcsec"):
        assert set(first[stat]) >= {"n", "median", "p95", "max", "ci95"}
    assert set(card["engines"]["ours"]["by_mode"]) == {"geometric", "astrometric", "apparent"}
    for forbidden in ("time", "date", "host", "platform", "python_version"):
        assert forbidden not in card
    assert str(kernel_path.parent) not in raw


def test_floor_turns_small_values_into_ties(tmp_path, thirty_row_card, kernel_path):
    samples, _ = thirty_row_card
    floor = tmp_path / "floor.json"
    floor.write_text(json.dumps({"geometric": 1.0, "astrometric": 1.0, "apparent": 1.0}))
    out = tmp_path / "card.json"
    assert C.main(["--samples", str(samples), "--kernel", str(kernel_path), "--out", str(out),
                   "--truth-floor", str(floor)]) == C.EXIT_PASS
    card = json.loads(out.read_text())
    geometric = card["engines"]["ours"]["by_mode"]["geometric"]["separation_arcsec"]
    assert geometric["median"] == {"tie_with_truth": True}
    assert geometric["n"] == 10
