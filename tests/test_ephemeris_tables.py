"""Unit tests for Pillar 17: Tabular Ephemeris Grid Generator and Ingress/Synodic Aspect Scanner."""

from __future__ import annotations

import csv
import io
import math
import pytest

from ephemeris_oss import AnalyticalEphemerisProvider, EphemerisAdapter
from ephemeris_oss.adapter import FLG_SIDEREAL
from ephemeris_oss.almanac import (
    BodyTableCell,
    DEFAULT_ASPECT_ANGLES,
    DEFAULT_TABLE_BODIES,
    EphemerisTable,
    EphemerisTableRow,
    MAX_EPHEMERIS_TABLE_ROWS,
    PlanetaryIngressEvent,
    SynodicAspectEvent,
    TransitTimelineReport,
    format_dms,
    generate_ephemeris_table,
    scan_ingresses_and_aspects,
)
from ephemeris_oss.jyotish.nakshatra import NAKSHATRA_SPAN_DEG, RASI_NAMES


# ---------------------------------------------------------------------------
# 1. format_dms tests
# ---------------------------------------------------------------------------


def test_format_dms_exact_reference_without_sign() -> None:
    deg = 14.0 + 23.0 / 60.0 + 11.4 / 3600.0
    assert format_dms(deg, include_sign=False) == "14d 23m 11.4s"


def test_format_dms_exact_reference_with_sign() -> None:
    deg = 14.0 + 23.0 / 60.0 + 11.4 / 3600.0
    assert format_dms(deg, include_sign=True) == "Mesha 14d 23m 11.4s"
    assert format_dms(30.0 + deg, include_sign=True) == "Vrishabha 14d 23m 11.4s"


def test_format_dms_all_twelve_rashis() -> None:
    offset = 5.0 + 12.0 / 60.0 + 34.5 / 3600.0
    for idx, rashi_name in enumerate(RASI_NAMES):
        lon = idx * 30.0 + offset
        assert format_dms(lon, include_sign=True) == f"{rashi_name} 05d 12m 34.5s"


def test_format_dms_normalizes_negative_and_multi_turn_angles() -> None:
    deg = 14.0 + 23.0 / 60.0 + 11.4 / 3600.0
    assert format_dms(deg + 360.0, include_sign=True) == "Mesha 14d 23m 11.4s"
    assert format_dms(deg - 360.0, include_sign=False) == "14d 23m 11.4s"


def test_format_dms_handles_arcsecond_rollover_cleanly() -> None:
    # 29d 59m 59.99s should roll cleanly to 30d 00m 00.0s (or Vrishabha 00d 00m 00.0s)
    near_boundary = 30.0 - (0.01 / 3600.0)
    assert format_dms(near_boundary, include_sign=False) == "30d 00m 00.0s"
    assert format_dms(near_boundary, include_sign=True) == "Vrishabha 00d 00m 00.0s"


def test_format_dms_rejects_non_finite_values() -> None:
    for bad in (math.nan, math.inf, -math.inf):
        with pytest.raises(ValueError):
            format_dms(bad)


# ---------------------------------------------------------------------------
# 2. generate_ephemeris_table tests
# ---------------------------------------------------------------------------


def test_generate_ephemeris_table_default_bodies_and_structure() -> None:
    start_jd = 2461041.5  # 2026-01-01 00:00 UT
    table = generate_ephemeris_table(start_jd, start_jd + 4.0, step_days=1.0)
    assert isinstance(table, EphemerisTable)
    assert table.bodies == DEFAULT_TABLE_BODIES
    assert len(table.rows) == 5
    assert len(table.receipt_sha256) == 64

    first_row = table.rows[0]
    assert isinstance(first_row, EphemerisTableRow)
    assert math.isclose(first_row.jd_ut, start_jd, abs_tol=1e-8)
    assert first_row.iso_utc == "2026-01-01T00:00:00Z"
    assert 23.0 < first_row.ayanamsa_deg < 25.0

    for body in DEFAULT_TABLE_BODIES:
        cell = first_row.bodies[body]
        assert isinstance(cell, BodyTableCell)
        assert 0.0 <= cell.longitude_deg < 360.0
        assert 0 <= cell.rashi_index <= 11
        assert cell.rashi_name == RASI_NAMES[cell.rashi_index]
        assert 0 <= cell.nakshatra_index <= 26
        assert 1 <= cell.pada <= 4
        assert cell.motion_code in ("D", "R", "S")
        # Verify both attribute and mapping access work
        assert cell["longitude_deg"] == cell.longitude_deg
        assert cell["rashi_name"] == cell.rashi_name
        assert first_row[body].longitude_deg == cell.longitude_deg
        assert first_row.bodies[body.lower()].longitude_deg == cell.longitude_deg


def test_generate_ephemeris_table_motion_codes_direct_retrograde_stationary() -> None:
    start_jd = 2461041.5
    table = generate_ephemeris_table(start_jd, start_jd + 2.0, step_days=1.0)
    row = table.rows[0]
    assert row.bodies["Sun"].motion_code == "D"
    assert row.bodies["Sun"].is_retrograde is False
    assert row.bodies["Moon"].motion_code == "D"
    assert row.bodies["Moon"].is_retrograde is False
    assert row.bodies["Rahu"].motion_code == "R"
    assert row.bodies["Rahu"].is_retrograde is True
    assert row.bodies["Ketu"].motion_code == "R"
    assert row.bodies["Ketu"].is_retrograde is True


def test_generate_ephemeris_table_detects_stationary_planet_motion_code() -> None:
    # Scan Saturn around a stationary point so |speed| < 0.005 triggers motion_code == "S"
    # First locate a Saturn station via coarse speed sign change in 2026
    provider = AnalyticalEphemerisProvider()
    jd0 = 2461041.5
    station_jd = None
    prev_spd = provider.calc_ut(jd0, "Saturn", flags=FLG_SIDEREAL)[0][3]
    for day in range(1, 365):
        cur_jd = jd0 + day
        spd = provider.calc_ut(cur_jd, "Saturn", flags=FLG_SIDEREAL)[0][3]
        if prev_spd * spd <= 0.0:
            # Bisect for |speed| < 0.001
            a, b = cur_jd - 1.0, float(cur_jd)
            for _ in range(20):
                m = 0.5 * (a + b)
                sm = provider.calc_ut(m, "Saturn", flags=FLG_SIDEREAL)[0][3]
                if prev_spd * sm <= 0.0:
                    b = m
                else:
                    a = m
            station_jd = 0.5 * (a + b)
            break
        prev_spd = spd

    assert station_jd is not None
    table = generate_ephemeris_table(station_jd, station_jd, step_days=1.0, bodies=("Saturn",))
    saturn_cell = table.rows[0].bodies["Saturn"]
    assert abs(saturn_cell.speed_deg_per_day) < 0.005
    assert saturn_cell.motion_code == "S"


def test_generate_ephemeris_table_csv_serialization() -> None:
    start_jd = 2461041.5
    table = generate_ephemeris_table(
        start_jd,
        start_jd + 3.0,
        step_days=1.0,
        bodies=("Sun", "Moon", "Mars"),
    )
    csv_text = table.to_csv()
    reader = list(csv.reader(io.StringIO(csv_text)))
    assert len(reader) == 5  # 1 header + 4 rows
    header = reader[0]
    assert header[:3] == ["jd_ut", "iso_utc", "ayanamsa_deg"]
    assert "Sun_longitude_deg" in header
    assert "Moon_nakshatra_name" in header
    assert "Mars_dms_in_rashi" in header


def test_generate_ephemeris_table_markdown_serialization() -> None:
    start_jd = 2461041.5
    table = generate_ephemeris_table(
        start_jd,
        start_jd + 2.0,
        step_days=1.0,
        bodies=("Sun", "Moon"),
    )
    md = table.to_markdown()
    lines = [line for line in md.strip().splitlines() if line.strip()]
    assert len(lines) == 5  # header + separator + 3 data rows
    assert lines[0].startswith("| JD (UT) | UTC | Ayanamsa | Sun | Moon |")
    assert lines[1].startswith("| --- |")
    assert "2026-01-01T00:00:00Z" in lines[2]


def test_generate_ephemeris_table_with_ephemeris_adapter() -> None:
    start_jd = 2461041.5
    with EphemerisAdapter(kernels="compact") as adapter:
        table = generate_ephemeris_table(
            start_jd,
            start_jd + 2.0,
            step_days=1.0,
            bodies=("Sun", "Moon", "Jupiter"),
            adapter=adapter,
        )
        assert len(table.rows) == 3
        sun_lon = table.rows[0].bodies["Sun"].longitude_deg
        direct_sun = adapter.calc_ut(start_jd, "sun", sidereal=True).longitude_deg
        assert math.isclose(sun_lon, direct_sun, abs_tol=1e-6)


def test_generate_ephemeris_table_sanskrit_aliases_and_deduplication() -> None:
    start_jd = 2461041.5
    table = generate_ephemeris_table(
        start_jd,
        start_jd + 1.0,
        step_days=1.0,
        bodies=("Surya", "sun", "Chandra", "Mangala"),
    )
    assert table.bodies == ("Sun", "Moon", "Mars")


def test_generate_ephemeris_table_receipt_determinism() -> None:
    start_jd = 2461041.5
    t1 = generate_ephemeris_table(start_jd, start_jd + 5.0, step_days=1.0)
    t2 = generate_ephemeris_table(start_jd, start_jd + 5.0, step_days=1.0)
    assert t1.receipt_sha256 == t2.receipt_sha256
    assert t1.to_dict() == t2.to_dict()


def test_generate_ephemeris_table_validation_errors() -> None:
    jd = 2461041.5
    with pytest.raises(ValueError):
        generate_ephemeris_table(jd + 5.0, jd, step_days=1.0)
    with pytest.raises(ValueError):
        generate_ephemeris_table(jd, jd + 5.0, step_days=0.0)
    with pytest.raises(ValueError):
        generate_ephemeris_table(jd, jd + 5.0, step_days=-1.0)
    with pytest.raises(ValueError):
        generate_ephemeris_table(jd, jd + 60.0, step_days=31.0)
    with pytest.raises(ValueError):
        generate_ephemeris_table(jd, jd + float(MAX_EPHEMERIS_TABLE_ROWS + 5), step_days=1.0)
    with pytest.raises(ValueError):
        generate_ephemeris_table(jd, jd + 2.0, bodies=())
    with pytest.raises(ValueError):
        generate_ephemeris_table(jd, jd + 2.0, bodies=("NotAPlanet",))
    with pytest.raises(ValueError):
        generate_ephemeris_table(math.nan, jd + 2.0)


# ---------------------------------------------------------------------------
# 3. scan_ingresses_and_aspects tests
# ---------------------------------------------------------------------------


def test_scan_rashi_ingresses_root_finding_accuracy() -> None:
    start_jd = 2461041.5  # 2026-01-01
    end_jd = start_jd + 35.0
    report = scan_ingresses_and_aspects(
        start_jd,
        end_jd,
        bodies=("Sun", "Moon", "Mars", "Mercury", "Venus"),
        aspect_angles=(),
        include_nakshatra_ingresses=False,
    )
    assert isinstance(report, TransitTimelineReport)
    assert len(report.rashi_ingresses) >= 14  # Moon crosses ~15 rashis in 35 days, plus Sun/inner planets
    assert len(report.nakshatra_ingresses) == 0

    provider = AnalyticalEphemerisProvider()
    for ev in report.rashi_ingresses:
        assert isinstance(ev, PlanetaryIngressEvent)
        assert ev.ingress_type == "rashi"
        assert start_jd <= ev.jd_ut <= end_jd
        assert ev.from_index != ev.to_index
        assert ev.from_name == RASI_NAMES[ev.from_index]
        assert ev.to_name == RASI_NAMES[ev.to_index]

        coords, _ = provider.calc_ut(ev.jd_ut, ev.body, flags=FLG_SIDEREAL)
        lon = float(coords[0]) % 360.0
        rem = lon % 30.0
        boundary_dist = min(rem, 30.0 - rem)
        assert boundary_dist < 1e-4
        assert (ev.longitude_deg % 30.0) < 1e-4


def test_scan_nakshatra_ingresses_root_finding_accuracy() -> None:
    start_jd = 2461041.5
    end_jd = start_jd + 15.0
    report = scan_ingresses_and_aspects(
        start_jd,
        end_jd,
        bodies=("Sun", "Moon"),
        aspect_angles=(),
        include_nakshatra_ingresses=True,
    )
    assert len(report.nakshatra_ingresses) >= 12  # Moon crosses ~1 nakshatra per day

    provider = AnalyticalEphemerisProvider()
    for ev in report.nakshatra_ingresses:
        assert ev.ingress_type == "nakshatra"
        assert 0 <= ev.from_index <= 26
        assert 0 <= ev.to_index <= 26
        coords, _ = provider.calc_ut(ev.jd_ut, ev.body, flags=FLG_SIDEREAL)
        lon = float(coords[0]) % 360.0
        rem = lon % NAKSHATRA_SPAN_DEG
        boundary_dist = min(rem, NAKSHATRA_SPAN_DEG - rem)
        assert boundary_dist < 1e-4
        assert (ev.longitude_deg % NAKSHATRA_SPAN_DEG) < 1e-4


def test_scan_synodic_aspects_root_finding_accuracy() -> None:
    start_jd = 2461041.5
    end_jd = start_jd + 30.0
    report = scan_ingresses_and_aspects(
        start_jd,
        end_jd,
        bodies=("Sun", "Moon", "Mars", "Jupiter", "Saturn"),
        aspect_angles=DEFAULT_ASPECT_ANGLES,
    )
    assert len(report.aspects) >= 20

    provider = AnalyticalEphemerisProvider()
    for asp in report.aspects:
        assert isinstance(asp, SynodicAspectEvent)
        assert start_jd <= asp.jd_ut <= end_jd
        assert asp.aspect_angle_deg in DEFAULT_ASPECT_ANGLES

        ca, _ = provider.calc_ut(asp.jd_ut, asp.body_a, flags=FLG_SIDEREAL)
        cb, _ = provider.calc_ut(asp.jd_ut, asp.body_b, flags=FLG_SIDEREAL)
        lon_a = float(ca[0]) % 360.0
        lon_b = float(cb[0]) % 360.0
        sep = (lon_a - lon_b) % 360.0
        assert abs(sep - asp.aspect_angle_deg) < 1e-3
        assert abs(asp.separation_deg - asp.aspect_angle_deg) < 1e-3


def test_scan_ingresses_and_aspects_with_ephemeris_adapter() -> None:
    start_jd = 2461041.5
    end_jd = start_jd + 16.0
    with EphemerisAdapter(kernels="compact") as adapter:
        report = scan_ingresses_and_aspects(
            start_jd,
            end_jd,
            bodies=("Sun", "Moon"),
            aspect_angles=(0.0, 180.0),
            include_nakshatra_ingresses=False,
            adapter=adapter,
        )
        # In 16 days, Sun enters Makara (~Jan 14) and Moon has at least 1 syzygy (0 or 180)
        assert any(ev.body == "Sun" and ev.to_name == "Makara" for ev in report.rashi_ingresses)
        assert len(report.aspects) >= 1

        for ev in report.rashi_ingresses:
            pos = adapter.calc_ut(ev.jd_ut, ev.body.lower(), sidereal=True)
            assert (pos.longitude_deg % 30.0) < 1e-4

        for asp in report.aspects:
            pa = adapter.calc_ut(asp.jd_ut, asp.body_a.lower(), sidereal=True)
            pb = adapter.calc_ut(asp.jd_ut, asp.body_b.lower(), sidereal=True)
            sep = (pa.longitude_deg - pb.longitude_deg) % 360.0
            assert abs(sep - asp.aspect_angle_deg) < 1e-3


def test_scan_chronological_ordering_and_rahu_ketu_exclusion() -> None:
    start_jd = 2461041.5
    end_jd = start_jd + 20.0
    report = scan_ingresses_and_aspects(
        start_jd,
        end_jd,
        bodies=("Sun", "Moon", "Rahu", "Ketu"),
        aspect_angles=(0.0, 180.0),
        include_nakshatra_ingresses=True,
    )
    jds = [ev.jd_ut for ev in report.events]
    assert jds == sorted(jds)
    # Rahu and Ketu never form a spurious relative aspect with each other
    assert not any({a.body_a, a.body_b} == {"Rahu", "Ketu"} for a in report.aspects)


def test_scan_retrograde_node_ingress_detection() -> None:
    # Mean Rahu moves ~ -0.05295 deg/day (1 Nakshatra every ~251.8 days)
    start_jd = 2461041.5
    end_jd = start_jd + 270.0
    report = scan_ingresses_and_aspects(
        start_jd,
        end_jd,
        bodies=("Rahu",),
        aspect_angles=(),
        include_nakshatra_ingresses=True,
    )
    assert len(report.nakshatra_ingresses) >= 1
    rahu_ev = report.nakshatra_ingresses[0]
    assert rahu_ev.is_retrograde is True
    assert rahu_ev.speed_deg_per_day < 0.0
    assert (rahu_ev.longitude_deg % NAKSHATRA_SPAN_DEG) < 1e-4


def test_scan_ingresses_and_aspects_receipt_determinism() -> None:
    start_jd = 2461041.5
    r1 = scan_ingresses_and_aspects(
        start_jd,
        start_jd + 10.0,
        bodies=("Sun", "Moon", "Mars"),
        aspect_angles=(0.0, 90.0, 180.0),
        include_nakshatra_ingresses=True,
    )
    r2 = scan_ingresses_and_aspects(
        start_jd,
        start_jd + 10.0,
        bodies=("Sun", "Moon", "Mars"),
        aspect_angles=(0.0, 90.0, 180.0),
        include_nakshatra_ingresses=True,
    )
    assert r1.receipt_sha256 == r2.receipt_sha256
    assert r1.to_dict() == r2.to_dict()


def test_scan_ingresses_and_aspects_validation_errors() -> None:
    jd = 2461041.5
    with pytest.raises(ValueError):
        scan_ingresses_and_aspects(jd, jd)
    with pytest.raises(ValueError):
        scan_ingresses_and_aspects(jd + 5.0, jd)
    with pytest.raises(ValueError):
        scan_ingresses_and_aspects(jd, jd + 405.0)
    with pytest.raises(ValueError):
        scan_ingresses_and_aspects(jd, jd + 5.0, bodies=())
    with pytest.raises(ValueError):
        scan_ingresses_and_aspects(jd, jd + 5.0, bodies=("UnknownBody",))
    with pytest.raises(ValueError):
        scan_ingresses_and_aspects(jd, jd + 5.0, aspect_angles=(math.nan,))
    with pytest.raises(ValueError):
        scan_ingresses_and_aspects(math.inf, jd + 5.0)


def test_format_dms_zero_and_boundary_angles() -> None:
    assert format_dms(0.0, include_sign=False) == "00d 00m 00.0s"
    assert format_dms(0.0, include_sign=True) == "Mesha 00d 00m 00.0s"
    assert format_dms(360.0, include_sign=True) == "Mesha 00d 00m 00.0s"
    assert format_dms(180.0, include_sign=True) == "Tula 00d 00m 00.0s"


def test_body_table_cell_dict_methods_and_row_positions_alias() -> None:
    table = generate_ephemeris_table(2461041.5, 2461042.5, step_days=1.0, bodies=("Sun", "Moon"))
    row = table.rows[0]
    assert row.positions is row.bodies
    assert "Sun" in row.bodies
    assert "sun" in row.bodies
    assert "Unknown" not in row.bodies
    assert row.bodies.get("Unknown") is None

    sun_cell = row.bodies["Sun"]
    assert "longitude_deg" in sun_cell
    assert sun_cell.get("rashi_name") == sun_cell.rashi_name
    assert list(sun_cell.keys()) == list(sun_cell.to_dict().keys())
    assert len(list(sun_cell.items())) == 11
    assert len(list(sun_cell.values())) == 11


def test_ephemeris_table_fractional_step_days() -> None:
    start_jd = 2461041.5
    table = generate_ephemeris_table(start_jd, start_jd + 2.0, step_days=0.5, bodies=("Sun", "Moon"))
    assert len(table.rows) == 5
    assert math.isclose(table.rows[1].jd_ut, start_jd + 0.5, abs_tol=1e-8)
    assert table.rows[1].iso_utc == "2026-01-01T12:00:00Z"


def test_planetary_ingress_event_properties_and_to_dict() -> None:
    report = scan_ingresses_and_aspects(
        2461041.5,
        2461046.5,
        bodies=("Moon",),
        aspect_angles=(),
        include_nakshatra_ingresses=True,
    )
    r_ev = report.rashi_ingresses[0]
    assert r_ev.event_type == "rashi_ingress"
    assert r_ev.from_rashi == r_ev.from_name
    assert r_ev.to_rashi == r_ev.to_name
    d = r_ev.to_dict()
    assert d["event_type"] == "rashi_ingress"
    assert d["body"] == "Moon"


def test_synodic_aspect_event_properties_and_to_dict() -> None:
    report = scan_ingresses_and_aspects(
        2461041.5,
        2461056.5,
        bodies=("Sun", "Moon"),
        aspect_angles=(0.0, 60.0, 90.0, 120.0, 180.0),
    )
    asp = report.aspects[0]
    assert asp.event_type == "synodic_aspect"
    assert asp.aspect_angle == asp.aspect_angle_deg
    assert asp.lon_a == asp.longitude_a_deg
    assert asp.lon_b == asp.longitude_b_deg
    d = asp.to_dict()
    assert d["event_type"] == "synodic_aspect"
    assert d["aspect_name"] in ("Conjunction", "Sextile", "Square", "Trine", "Opposition")


def test_scan_custom_aspect_angles_and_deduplication() -> None:
    report = scan_ingresses_and_aspects(
        2461041.5,
        2461050.5,
        bodies=("Sun", "Moon"),
        aspect_angles=(45.0, 135.0, 405.0),  # 405 % 360 == 45.0 deduplicated
    )
    assert report.aspect_angles == (45.0, 135.0)
    assert len(report.aspects) >= 1
    for asp in report.aspects:
        assert asp.aspect_angle_deg in (45.0, 135.0)
        assert asp.aspect_name in ("Semi-Square", "Sesquiquadrate")

