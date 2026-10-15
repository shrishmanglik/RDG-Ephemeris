"""Contract and accuracy tests for the self-contained compact Chebyshev DE440 kernel."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np
import pytest

from ephemeris_oss import EarthOrientation, Engine, EphemerisError, cli
from ephemeris_oss.compact_kernel import (
    COMPACT_KERNEL_ID,
    COMPACT_KERNEL_MODE,
    COMPACT_KERNEL_PATH,
    COMPACT_KERNEL_SHA256,
    REQUIRED_SEGMENT_PAIRS,
    CompactChebyshevKernel,
)
from ephemeris_oss.engine.contracts import AstronomyDataUnavailable
from ephemeris_oss.engine.numerical_provider import J2000_JD, _SpkGraph
from ephemeris_oss.engine.receipt import canonical_hash

DE440 = os.getenv("EPHEMERIS_OSS_DE440_KERNEL")
needs_de440 = pytest.mark.skipif(not DE440, reason="real DE440 kernel not supplied")
ZERO_EOP = EarthOrientation(dut1_seconds=0.0, xp_arcsec=0.0, yp_arcsec=0.0, version="test-zero")
CLASSICAL_BODIES = ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn")
ALL_BODIES = ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto")


def _angular_diff_arcsec(lon_a: float, lon_b: float) -> float:
    diff_deg = abs((lon_a - lon_b + 180.0) % 360.0 - 180.0)
    return diff_deg * 3600.0


def test_compact_kernel_data_file_exists_is_under_size_budget_and_matches_pinned_sha256() -> None:
    assert COMPACT_KERNEL_PATH.is_file(), f"missing compact kernel data file at {COMPACT_KERNEL_PATH}"
    size_bytes = COMPACT_KERNEL_PATH.stat().st_size
    assert 100_000 < size_bytes < 3_500_000, f"compact kernel size {size_bytes} outside budget"
    actual_sha256 = hashlib.sha256(COMPACT_KERNEL_PATH.read_bytes()).hexdigest()
    assert actual_sha256 == COMPACT_KERNEL_SHA256


def test_compact_kernel_segments_cover_all_required_naif_pairs() -> None:
    with CompactChebyshevKernel.open() as kernel:
        pairs = {(int(seg.center), int(seg.target)) for seg in kernel.segments}
        assert set(REQUIRED_SEGMENT_PAIRS) <= pairs
        for seg in kernel.segments:
            assert seg.start_jd <= 2378496.5  # 1800-01-01
            assert seg.end_jd >= 2488434.5    # 2101-01-01


def test_compact_kernel_scalar_and_vector_evaluations_match_across_graph() -> None:
    with CompactChebyshevKernel.open() as kernel:
        graph = _SpkGraph(kernel)  # type: ignore[arg-type]
        jds = np.asarray([2415020.5, 2433282.5, 2451545.0, 2461319.0, 2480765.5], dtype=np.float64)
        for target in (10, 301, 399, 199, 299, 4, 5, 6, 7, 8, 9):
            pos_vec, vel_vec = graph.state_many(target, jds)
            scalars = [graph.state(target, (J2000_JD, float(jd - J2000_JD))) for jd in jds]
            np.testing.assert_allclose(pos_vec.T, [s[0] for s in scalars], atol=1e-9, rtol=0.0)
            np.testing.assert_allclose(vel_vec.T, [s[1] for s in scalars], atol=1e-9, rtol=0.0)


def test_compact_kernel_fails_closed_outside_covered_epoch_window() -> None:
    with Engine.load(kernels="compact", eop=None) as eng:
        with pytest.raises(EphemerisError):
            eng.positions_tt(2200000.0, bodies=("sun",))


def test_compact_kernel_refuses_corrupted_or_tampered_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bad_file = tmp_path / "bad_compact.bin.zlib"
    bad_file.write_bytes(b"not-a-valid-compact-kernel")
    with pytest.raises(AstronomyDataUnavailable, match="magic header"):
        CompactChebyshevKernel.open(bad_file)

    import ephemeris_oss.compact_kernel as ck_mod

    monkeypatch.setattr(ck_mod, "COMPACT_KERNEL_PATH", bad_file)
    with pytest.raises(EphemerisError, match="SHA-256 mismatch"):
        Engine.load(kernels="compact", eop=None)


def test_engine_load_compact_positions_tt_works_with_empty_cache_and_records_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("EPHEMERIS_OSS_CACHE", str(tmp_path))
    with Engine.load(kernels="compact", eop=None, cache_dir=tmp_path) as eng:
        first = eng.positions_tt(2451545.0, bodies=CLASSICAL_BODIES)
        second = eng.positions_tt(2451545.0, bodies=CLASSICAL_BODIES)

    assert list(tmp_path.iterdir()) == []
    assert set(first.value) == set(CLASSICAL_BODIES)
    assert first.value == second.value
    assert first.receipt == second.receipt
    assert first.receipt_sha256 == second.receipt_sha256
    assert first.receipt["kernel_mode"] == COMPACT_KERNEL_MODE
    assert first.receipt["kernel_sha256"] == COMPACT_KERNEL_SHA256
    assert first.receipt_sha256 == canonical_hash(first.receipt)


def test_engine_load_compact_supports_utc_positions_houses_nodes_and_rise_set_offline(
    tmp_path: Path,
) -> None:
    instant = datetime(2026, 10, 6, 12, 0, 0, tzinfo=timezone.utc)
    with Engine.load(kernels="compact", eop=ZERO_EOP, cache_dir=tmp_path) as eng:
        pos = eng.positions(instant, bodies=ALL_BODIES, ayanamsa="lahiri")
        houses = eng.houses(instant, lat=43.6532, lon=-79.3832, system="placidus", ayanamsa="lahiri")
        mean_node = eng.nodes(instant, kind="mean", ayanamsa="lahiri")
        true_node = eng.nodes(instant, kind="true", ayanamsa="lahiri")
        sunrise = eng.rise_set(date(2026, 10, 6), lat=43.6532, lon=-79.3832, body="sun", event="rise")
        batch = eng._provider.geocentric_states_for_bodies_at_tdb_jds(
            bodies=("Sun", "Moon", "Mars"),
            tdb_jds=(2451545.0, 2461319.0),
            kernel_year=2026,
        )

    assert set(pos.value) == set(ALL_BODIES)
    assert pos.receipt["kernel_identifier"] == COMPACT_KERNEL_ID
    assert pos.receipt["kernel_mode"] == COMPACT_KERNEL_MODE
    assert pos.receipt["kernel_sha256"] == COMPACT_KERNEL_SHA256
    assert houses.receipt["kernel_mode"] == COMPACT_KERNEL_MODE
    assert houses.receipt["kernel_sha256"] == COMPACT_KERNEL_SHA256
    assert 0.0 <= mean_node.value < 360.0
    assert 0.0 <= true_node.value < 360.0
    assert mean_node.value != true_node.value
    assert sunrise.value["outcome"] == "events"
    assert set(batch) == {"Sun", "Moon", "Mars"}


def test_cli_chart_compact_flag_runs_offline_and_outputs_json(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rc = cli.main(
        [
            "--cache",
            str(tmp_path),
            "chart",
            "--compact",
            "--at",
            "2026-10-06T12:00:00Z",
            "--ayanamsa",
            "lahiri",
            "--json",
        ]
    )
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ayanamsa"] == "lahiri"
    assert set(payload["positions"]) == set(ALL_BODIES)
    assert payload["receipt"]["kernel_mode"] == COMPACT_KERNEL_MODE
    assert payload["receipt"]["kernel_sha256"] == COMPACT_KERNEL_SHA256
    assert len(payload["receipt_sha256"]) == 64


@needs_de440
def test_compact_kernel_matches_full_de440_to_sub_arcsecond_across_1800_to_2100() -> None:
    assert DE440 is not None
    # Sample epochs from 1800-01-01 (2378496.5) through 2100-01-01 (2488069.5)
    sampled_epochs = np.linspace(2378500.0, 2488060.0, 35)
    max_lon_err_arcsec = 0.0
    max_lat_err_arcsec = 0.0

    with Engine.load(kernels="compact", eop=ZERO_EOP) as compact_eng, Engine.load(
        kernels={"DE440": Path(DE440)}, eop=ZERO_EOP
    ) as de440_eng:
        for jd_tt in sampled_epochs:
            comp_tt = compact_eng.positions_tt(float(jd_tt), bodies=CLASSICAL_BODIES).value
            ref_tt = de440_eng.positions_tt(float(jd_tt), bodies=CLASSICAL_BODIES).value
            for body in CLASSICAL_BODIES:
                lon_err = _angular_diff_arcsec(
                    comp_tt[body]["longitude_deg"], ref_tt[body]["longitude_deg"]
                )
                lat_err = abs(comp_tt[body]["latitude_deg"] - ref_tt[body]["latitude_deg"]) * 3600.0
                max_lon_err_arcsec = max(max_lon_err_arcsec, lon_err)
                max_lat_err_arcsec = max(max_lat_err_arcsec, lat_err)
                assert lon_err < 0.05, f"{body} at JD {jd_tt}: lon_err={lon_err:.4f} arcsec"
                assert lat_err < 0.05, f"{body} at JD {jd_tt}: lat_err={lat_err:.4f} arcsec"

        # Also check all 10 bodies (including Uranus, Neptune, Pluto) and true node at UTC instants
        for year in (1965, 1985, 2000, 2015, 2026):
            instant = datetime(year, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
            comp_pos = compact_eng.positions(instant, bodies=ALL_BODIES, ayanamsa="lahiri").value
            ref_pos = de440_eng.positions(instant, bodies=ALL_BODIES, ayanamsa="lahiri").value
            for body in ALL_BODIES:
                lon_err = _angular_diff_arcsec(
                    comp_pos[body]["longitude_deg"], ref_pos[body]["longitude_deg"]
                )
                lat_err = abs(comp_pos[body]["latitude_deg"] - ref_pos[body]["latitude_deg"]) * 3600.0
                assert lon_err < 0.05, f"{body} in {year}: lon_err={lon_err:.4f} arcsec"
                assert lat_err < 0.05, f"{body} in {year}: lat_err={lat_err:.4f} arcsec"

            comp_true_node = compact_eng.nodes(instant, kind="true", ayanamsa="lahiri").value
            ref_true_node = de440_eng.nodes(instant, kind="true", ayanamsa="lahiri").value
            node_err = _angular_diff_arcsec(comp_true_node, ref_true_node)
            assert node_err < 0.5, f"true node in {year}: node_err={node_err:.4f} arcsec"
