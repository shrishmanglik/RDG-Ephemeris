import json
from types import SimpleNamespace
import pytest
from ephemeris_oss import cli

class EngineFixture:
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def positions_tt(self, instant, bodies):
        return SimpleNamespace(value={body: {"longitude_deg": instant % 360, "latitude_deg": 0.0} for body in bodies}, receipt={"kernel_sha256": "fixture-only", "time_scale": "TT"})

def test_benchmark_cli_reports_repeated_matched_tt_workload(monkeypatch, capsys):
    monkeypatch.setattr(cli.Engine, "load", lambda **kw: EngineFixture())
    assert cli.main(["bench", "--samples", "2", "--rounds", "2"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["schema"] == "ephemeris-researcher-benchmark-v1"
    assert len(report["rounds"]) == 2
    assert report["samples"] == 2
    assert report["bodies"] == ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"]
    assert report["output_equivalence"] is True
    assert report["production_qualification"] is False

def test_benchmark_refuses_bad_workload_before_computing(monkeypatch):
    def refuse(**kw): raise AssertionError("engine must not load")
    monkeypatch.setattr(cli.Engine, "load", refuse)
    with pytest.raises(SystemExit): cli.main(["bench", "--samples", "0"])

def test_benchmark_blocks_inconsistent_scalar_and_batched_output(monkeypatch, capsys):
    class BadEngine(EngineFixture):
        def positions_tt(self, instant, bodies):
            result = super().positions_tt(instant, bodies)
            if len(bodies) == 1:
                result.value[bodies[0]]["longitude_deg"] += 1
            return result
    monkeypatch.setattr(cli.Engine, "load", lambda **kw: BadEngine())
    assert cli.main(["bench", "--samples", "2"]) == 2
    assert "differ" in capsys.readouterr().err
