from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timedelta, timezone

import erfa
import pytest

from ephemeris_oss.engine.contracts import AstronomyDataUnavailable
from ephemeris_oss.engine.earth_orientation import (
    EopQuality,
    EopRecord,
    IersFinals2000A,
    UtcCalendarInstant,
    estimate_delta_t,
    parse_finals2000a_line,
)


LEAP_INSERTION_DATES = (
    date(1972, 6, 30),
    date(1972, 12, 31),
    date(1973, 12, 31),
    date(1974, 12, 31),
    date(1975, 12, 31),
    date(1976, 12, 31),
    date(1977, 12, 31),
    date(1978, 12, 31),
    date(1979, 12, 31),
    date(1981, 6, 30),
    date(1982, 6, 30),
    date(1983, 6, 30),
    date(1985, 6, 30),
    date(1987, 12, 31),
    date(1989, 12, 31),
    date(1990, 12, 31),
    date(1992, 6, 30),
    date(1993, 6, 30),
    date(1994, 6, 30),
    date(1995, 12, 31),
    date(1997, 6, 30),
    date(1998, 12, 31),
    date(2005, 12, 31),
    date(2008, 12, 31),
    date(2012, 6, 30),
    date(2015, 6, 30),
    date(2016, 12, 31),
)


def _put(line: list[str], start: int, end: int, value: str) -> None:
    width = end - start + 1
    line[start - 1 : end] = list(value.rjust(width))


def _line(
    mjd: float,
    *,
    x: float,
    y: float,
    dut1: float,
    flag: str = "I",
    bx: float | None = None,
    by: float | None = None,
    but1: float | None = None,
) -> str:
    line = [" "] * 187
    _put(line, 8, 15, f"{mjd:8.2f}")
    _put(line, 19, 27, f"{x:9.6f}")
    _put(line, 38, 46, f"{y:9.6f}")
    _put(line, 58, 58, flag)
    _put(line, 59, 68, f"{dut1:10.7f}")
    _put(line, 98, 106, f"{0.111:9.3f}")
    _put(line, 117, 125, f"{-0.222:9.3f}")
    if bx is not None and by is not None and but1 is not None:
        _put(line, 135, 144, f"{bx:10.6f}")
        _put(line, 145, 154, f"{by:10.6f}")
        _put(line, 155, 165, f"{but1:11.7f}")
        _put(line, 166, 175, f"{0.333:10.3f}")
        _put(line, 176, 185, f"{-0.444:10.3f}")
    return "".join(line)


def test_parser_prefers_bulletin_b_final_values() -> None:
    record = parse_finals2000a_line(
        _line(60000.0, x=0.1, y=0.2, dut1=0.3, bx=0.4, by=0.5, but1=0.6)
    )
    assert record is not None
    assert record.quality is EopQuality.FINAL
    assert record.xp_arcsec == pytest.approx(0.4)
    assert record.yp_arcsec == pytest.approx(0.5)
    assert record.dut1_seconds == pytest.approx(0.6)
    assert record.dx_mas == pytest.approx(0.333)
    assert record.dy_mas == pytest.approx(-0.444)


def test_parser_marks_bulletin_a_prediction() -> None:
    record = parse_finals2000a_line(_line(60000.0, x=0.1, y=0.2, dut1=0.3, flag="P"))
    assert record is not None
    assert record.quality is EopQuality.PREDICTED


def test_snapshot_interpolates_and_exposes_provenance(tmp_path) -> None:
    content = "\n".join(
        [
            _line(59946.0, x=0.10, y=0.20, dut1=-0.10, bx=0.11, by=0.21, but1=-0.11),
            _line(59947.0, x=0.30, y=0.40, dut1=-0.30, bx=0.31, by=0.41, but1=-0.31),
        ]
    )
    path = tmp_path / "finals2000A.all"
    path.write_text(content, encoding="ascii")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    snapshot = IersFinals2000A.from_file(
        path, expected_sha256=digest, version="iers-test-2023-01-02"
    )

    resolved = snapshot.resolve(datetime(2023, 1, 2, 12, tzinfo=timezone.utc))

    assert resolved.xp_arcsec == pytest.approx(0.21, abs=1e-12)
    assert resolved.yp_arcsec == pytest.approx(0.31, abs=1e-12)
    assert resolved.dut1_seconds == pytest.approx(-0.21, abs=1e-12)
    assert resolved.quality is EopQuality.FINAL
    assert resolved.version == "iers-test-2023-01-02"
    assert resolved.source_sha256 == digest
    assert resolved.lower_mjd == 59946.0
    assert resolved.upper_mjd == 59947.0


def _midnight_mjd(value: date) -> float:
    base, offset = erfa.cal2jd(value.year, value.month, value.day)
    return float(base + offset - 2_400_000.5)


@pytest.mark.parametrize("insertion_date", LEAP_INSERTION_DATES)
def test_dut1_interpolation_is_continuous_across_every_leap_second(
    insertion_date: date,
) -> None:
    next_date = insertion_date + timedelta(days=1)
    before_dat = float(
        erfa.dat(insertion_date.year, insertion_date.month, insertion_date.day, 0.0)
    )
    after_dat = float(erfa.dat(next_date.year, next_date.month, next_date.day, 0.0))
    assert after_dat - before_dat == pytest.approx(1.0, abs=0.0)

    continuous_ut1_tai = -before_dat - 0.4
    snapshot = IersFinals2000A(
        (
            EopRecord(
                _midnight_mjd(insertion_date),
                continuous_ut1_tai + before_dat,
                0.1,
                0.2,
                0.0,
                0.0,
                EopQuality.FINAL,
            ),
            EopRecord(
                _midnight_mjd(next_date),
                continuous_ut1_tai + after_dat,
                0.1,
                0.2,
                0.0,
                0.0,
                EopQuality.FINAL,
            ),
        ),
        version="leap-regression",
        source_sha256="0" * 64,
    )

    before_samples = (
        UtcCalendarInstant(*insertion_date.timetuple()[:3], 0, 0, 0.0),
        UtcCalendarInstant(*insertion_date.timetuple()[:3], 12, 0, 0.0),
        UtcCalendarInstant(*insertion_date.timetuple()[:3], 23, 59, 59.999999),
        UtcCalendarInstant(*insertion_date.timetuple()[:3], 23, 59, 60.0),
    )
    for instant in before_samples:
        assert snapshot.resolve(instant).dut1_seconds == pytest.approx(-0.4, abs=1e-12)

    immediately_after = UtcCalendarInstant(*next_date.timetuple()[:3], 0, 0, 0.0)
    assert snapshot.resolve(immediately_after).dut1_seconds == pytest.approx(0.6, abs=1e-12)


def test_recorded_2016_boundary_does_not_interpolate_discontinuous_dut1() -> None:
    snapshot = IersFinals2000A(
        (
            EopRecord(57753.0, -0.4077600, 0.1, 0.2, 0.0, 0.0, EopQuality.FINAL),
            EopRecord(57754.0, 0.5912975, 0.1, 0.2, 0.0, 0.0, EopQuality.FINAL),
        ),
        version="iers-2016-regression",
        source_sha256="1" * 64,
    )

    midpoint = snapshot.resolve(
        UtcCalendarInstant(2016, 12, 31, 12, 0, 0.0)
    ).dut1_seconds
    assert midpoint == pytest.approx(-0.408231, abs=2e-6)
    assert midpoint < -0.4


def test_utc_calendar_instant_rejects_sixty_seconds_on_non_leap_day() -> None:
    with pytest.raises(ValueError, match="invalid UTC"):
        UtcCalendarInstant(2016, 12, 30, 23, 59, 60.0)


def test_explicit_leap_second_maps_to_one_si_second_in_tai() -> None:
    before = UtcCalendarInstant(2016, 12, 31, 23, 59, 59.0)
    leap = UtcCalendarInstant(2016, 12, 31, 23, 59, 60.0)
    after = UtcCalendarInstant(2017, 1, 1, 0, 0, 0.0)

    def tai_parts(instant: UtcCalendarInstant) -> tuple[float, float]:
        return tuple(float(value) for value in erfa.utctai(*instant.utc_jd()))

    before_tai = tai_parts(before)
    leap_tai = tai_parts(leap)
    after_tai = tai_parts(after)
    first_step = sum(a - b for a, b in zip(leap_tai, before_tai, strict=True))
    second_step = sum(a - b for a, b in zip(after_tai, leap_tai, strict=True))
    assert first_step * 86_400.0 == pytest.approx(1.0, abs=1e-9)
    assert second_step * 86_400.0 == pytest.approx(1.0, abs=1e-9)
    assert leap.isoformat() == "2016-12-31T23:59:60Z"


def test_snapshot_fails_closed_for_checksum_prediction_gap_and_extrapolation(tmp_path) -> None:
    path = tmp_path / "finals2000A.all"
    path.write_text(
        "\n".join(
            [
                _line(59945.0, x=0.1, y=0.2, dut1=-0.1, flag="I"),
                _line(59946.0, x=0.2, y=0.3, dut1=-0.2, flag="P"),
                _line(59949.0, x=0.3, y=0.4, dut1=-0.3, flag="P"),
            ]
        ),
        encoding="ascii",
    )
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    with pytest.raises(AstronomyDataUnavailable, match="checksum mismatch"):
        IersFinals2000A.from_file(path, expected_sha256="0" * 64, version="bad")

    snapshot = IersFinals2000A.from_file(path, expected_sha256=digest, version="test")
    with pytest.raises(AstronomyDataUnavailable, match="predicted"):
        snapshot.resolve(datetime(2023, 1, 1, 12, tzinfo=timezone.utc))
    with pytest.raises(AstronomyDataUnavailable, match="outside"):
        snapshot.resolve(datetime(2022, 12, 31, tzinfo=timezone.utc))

    predictions = IersFinals2000A.from_file(
        path, expected_sha256=digest, version="test", allow_predictions=True
    )
    with pytest.raises(AstronomyDataUnavailable, match="gap"):
        predictions.resolve(datetime(2023, 1, 3, tzinfo=timezone.utc))


@pytest.mark.parametrize(
    ("year", "expected", "tolerance"),
    [
        (1600.0, 120.0, 1e-9),
        (1700.0, 8.83, 1e-9),
        (1800.0, 13.72, 1e-9),
        (1900.0, -2.79, 1e-9),
        (2000.0, 63.86, 1e-9),
        (2050.0, 93.0, 1e-9),
    ],
)
def test_delta_t_piecewise_boundary_values(year: float, expected: float, tolerance: float) -> None:
    estimate = estimate_delta_t(year)
    assert estimate.seconds == pytest.approx(expected, abs=tolerance)
    assert estimate.uncertainty_seconds is not None


def test_delta_t_policy_rejects_unbounded_epoch() -> None:
    with pytest.raises(AstronomyDataUnavailable, match="-1999..3000"):
        estimate_delta_t(4000.0)


def test_release_root_loads_only_checksum_bound_active_generation(tmp_path) -> None:
    payload = (
        "\n".join(
            _line(60_000.0 + index, x=0.1, y=0.2, dut1=0.3)
            for index in range(10_000)
        )
        + "\n"
    ).encode()
    digest = hashlib.sha256(payload).hexdigest()
    generation = tmp_path / "releases" / digest
    generation.mkdir(parents=True)
    (generation / "finals2000A.all").write_bytes(payload)
    (generation / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "iers-eop-manifest-v2",
                "retrieved_at_utc": "2026-07-22T00:00:00+00:00",
                "sha256": digest,
                "byte_count": len(payload),
                "record_count": 10_000,
                "first_mjd_utc": 60_000.0,
                "last_mjd_utc": 69_999.0,
                "latest_non_predicted_mjd_utc": 69_999.0,
                "quality_counts": {"observed": 10_000},
            }
        )
    )
    (tmp_path / "active.json").write_text(
        json.dumps(
            {
                "schema_version": "iers-eop-active-pointer-v1",
                "generation_sha256": digest,
                "payload": f"releases/{digest}/finals2000A.all",
                "manifest": f"releases/{digest}/manifest.json",
            }
        )
    )

    snapshot = IersFinals2000A.from_release_root(tmp_path)

    assert snapshot.source_sha256 == digest
    assert snapshot.version == "iers-finals2000a@2026-07-22T00:00:00+00:00"


def test_release_root_rejects_noncanonical_pointer_path(tmp_path) -> None:
    digest = "a" * 64
    (tmp_path / "active.json").write_text(
        json.dumps(
            {
                "schema_version": "iers-eop-active-pointer-v1",
                "generation_sha256": digest,
                "payload": "../outside",
                "manifest": f"releases/{digest}/manifest.json",
            }
        )
    )

    with pytest.raises(AstronomyDataUnavailable, match="paths are not canonical"):
        IersFinals2000A.from_release_root(tmp_path)
