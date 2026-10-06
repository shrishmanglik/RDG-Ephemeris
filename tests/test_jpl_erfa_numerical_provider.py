from __future__ import annotations

import hashlib
import os
from datetime import date, datetime, timezone
from pathlib import Path

import erfa
import numpy as np
import pytest

from ephemeris_oss.engine import (
    AstronomyDataUnavailable,
    CalculationSettings,
    EarthOrientationParameters,
    JplErfaAstronomyProvider,
    KernelArtifact,
    KernelRegistry,
    Observer,
    UtcCalendarInstant,
)
from ephemeris_oss.engine.numerical_provider import J2000_JD, _SpkGraph


SETTINGS = CalculationSettings(
    frame="ICRF",
    zodiac_mode="tropical",
    ayanamsa=None,
    node_mode="mean",
)


class FakeSegment:
    def __init__(
        self,
        center: int,
        target: int,
        position: tuple[float, float, float],
        *,
        start_jd: float = 2400000.0,
        end_jd: float = 2500000.0,
    ) -> None:
        self.center = center
        self.target = target
        self.start_jd = start_jd
        self.end_jd = end_jd
        self.position = np.asarray(position, dtype=np.float64)

    def compute_and_differentiate(self, _tdb1: float, _tdb2: float) -> tuple[np.ndarray, np.ndarray]:
        return self.position, self.position * 0.01


class FakeKernel:
    def __init__(self, segments: list[FakeSegment]) -> None:
        self.segments = segments


def provider_for_kernel(path: Path, **kwargs: object) -> JplErfaAstronomyProvider:
    checksum = hashlib.sha256(path.read_bytes()).hexdigest()
    return JplErfaAstronomyProvider(
        kernel_registry=KernelRegistry({"DE440": KernelArtifact("DE440", path, checksum)}),
        leap_seconds_version="erfa-2026-01",
        earth_orientation_version="test-eop-1",
        time_scale_version="test-explicit-utc-window-1",
        tdb_minus_tt_version="sofa-iauDtdb-2021-05-12",
        time_scale_valid_from_utc=date(1960, 1, 1),
        time_scale_valid_through_utc=date(2026, 12, 31),
        ayanamsa_data_version="not-used",
        **kwargs,
    )


def provider_for_real_kernels(**kwargs: object) -> JplErfaAstronomyProvider:
    artifacts = {}
    for identifier, variable in (
        ("DE440", "EPHEMERIS_OSS_DE440_KERNEL"),
        ("DE441-PART1", "EPHEMERIS_OSS_DE441_PART1_KERNEL"),
        ("DE441-PART2", "EPHEMERIS_OSS_DE441_PART2_KERNEL"),
    ):
        configured = os.getenv(variable)
        if configured is None:
            continue
        path = Path(configured)
        artifacts[identifier] = KernelArtifact(
            identifier, path, hashlib.sha256(path.read_bytes()).hexdigest()
        )
    return JplErfaAstronomyProvider(
        kernel_registry=KernelRegistry(artifacts),
        leap_seconds_version="erfa-2026-01",
        earth_orientation_version="not-used-geometric",
        time_scale_version="test-explicit-utc-window-1",
        tdb_minus_tt_version="sofa-iauDtdb-2021-05-12",
        time_scale_valid_from_utc=date(1960, 1, 1),
        time_scale_valid_through_utc=date(2026, 12, 31),
        ayanamsa_data_version="not-used",
        **kwargs,
    )


def test_spk_graph_composes_and_reverses_segments() -> None:
    graph = _SpkGraph(
        FakeKernel(
            [
                FakeSegment(0, 3, (10.0, 20.0, 30.0)),
                FakeSegment(3, 399, (1.0, 2.0, 3.0)),
                FakeSegment(0, 10, (100.0, 200.0, 300.0)),
            ]
        )
    )
    earth, velocity = graph.state(399, (J2000_JD, 0.0))
    assert earth == pytest.approx((11.0, 22.0, 33.0))
    assert velocity == pytest.approx((0.11, 0.22, 0.33))


def test_spk_graph_fails_closed_outside_segment_coverage() -> None:
    graph = _SpkGraph(FakeKernel([FakeSegment(0, 10, (1.0, 2.0, 3.0))]))
    with pytest.raises(AstronomyDataUnavailable, match="no active SSB path"):
        graph.state(10, (2600000.0, 0.0))


def test_spk_graph_vector_batch_honors_later_overlapping_segment_priority() -> None:
    graph = _SpkGraph(
        FakeKernel(
            [
                FakeSegment(0, 10, (1.0, 0.0, 0.0)),
                FakeSegment(
                    0,
                    10,
                    (9.0, 0.0, 0.0),
                    start_jd=2451546.0,
                    end_jd=2451548.0,
                ),
            ]
        )
    )
    samples = np.asarray((2451545.5, 2451546.5))

    positions, velocities = graph.state_many(10, samples)

    np.testing.assert_allclose(positions[0], (1.0, 9.0), atol=0.0, rtol=0.0)
    np.testing.assert_allclose(velocities[0], (0.01, 0.09), atol=0.0, rtol=0.0)


def test_utc_tt_tdb_conversion_and_round_trip() -> None:
    kernel = Path(__file__)
    provider = provider_for_kernel(kernel)
    instant = datetime(2000, 1, 1, 12, tzinfo=timezone.utc)
    scales = provider.utc_time_scales(instant)
    assert scales.utc_jd == pytest.approx(2451545.0, abs=1e-12)
    assert (scales.tt_jd - scales.utc_jd) * 86400.0 == pytest.approx(64.184, abs=3e-5)
    assert abs((scales.tdb_jd - scales.tt_jd) * 86400.0) < 0.002


def test_provider_contract_preserves_explicit_utc_leap_second() -> None:
    provider = provider_for_kernel(Path(__file__))
    leap = UtcCalendarInstant(2016, 12, 31, 23, 59, 60.0)

    scales = provider.utc_time_scales(leap)
    restored = provider.reverse_julian_day(julian_day=leap.utc_jd())

    assert provider.julian_day(instant_utc=leap) == pytest.approx(scales.utc_jd, abs=0.0)
    assert isinstance(restored, UtcCalendarInstant)
    assert restored.second == pytest.approx(60.0, abs=5e-7)
    assert restored.isoformat() == "2016-12-31T23:59:60Z"


def test_provider_computes_versioned_stellar_anchor_ayanamsas() -> None:
    provider = provider_for_kernel(Path(__file__))
    instant = datetime(2000, 1, 1, 12, tzinfo=timezone.utc)

    citra = provider.ayanamsa(instant_utc=instant, convention="true_citra")
    pushya = provider.ayanamsa(instant_utc=instant, convention="pushya")

    # Exact API behavior snapshots for the newly specified apparent-place policy.
    # Independent physical/definition fidelity is measured in the R3 reference grid.
    assert citra == pytest.approx(23.840018015395685, abs=1e-12)
    assert pushya == pytest.approx(22.727091052222818, abs=1e-12)
    assert citra != pushya


def test_pre_utc_time_scale_conversion_fails_closed() -> None:
    provider = provider_for_kernel(Path(__file__))
    with pytest.raises(AstronomyDataUnavailable, match="validity window"):
        provider.utc_time_scales(datetime(1900, 1, 1, 12, tzinfo=timezone.utc))


def test_future_utc_beyond_versioned_policy_fails_closed() -> None:
    provider = provider_for_kernel(Path(__file__))
    with pytest.raises(AstronomyDataUnavailable, match="validity window"):
        provider.utc_time_scales(datetime(2027, 1, 1, tzinfo=timezone.utc))


@pytest.mark.parametrize("year", [1900, 2027])
def test_reverse_julian_day_enforces_versioned_utc_window(year: int) -> None:
    provider = provider_for_kernel(Path(__file__))
    jd1, jd2 = erfa.cal2jd(year, 1, 1)
    with pytest.raises(AstronomyDataUnavailable, match="validity window"):
        provider.reverse_julian_day(julian_day=float(jd1 + jd2))


@pytest.mark.parametrize("frame", ["GCRS", "ICRF/J2000", "ICRS"])
def test_ambiguous_frame_aliases_fail_closed(frame: str) -> None:
    provider = provider_for_kernel(Path(__file__))
    with pytest.raises(AstronomyDataUnavailable, match="unsupported coordinate frame"):
        provider.coordinate_transform(
            vector=(1.0, 0.0, 0.0),
            source_frame="ICRF",
            target_frame=frame,
            instant_utc=datetime(2000, 1, 1, 12, tzinfo=timezone.utc),
            observer=None,
            settings=SETTINGS,
        )


def test_provider_celestial_matrix_matches_sofa_canonical_vector() -> None:
    expected = np.asarray(
        [
            [0.9999952427708701137, -0.002829062057663042347, -0.001229163741100017629],
            [0.003084546876908653562, 0.9174891871550392514, 0.3977487611849338124],
            [0.000002488512951527405928, -0.3977506604161195467, 0.9174935488232863071],
        ]
    )
    actual = JplErfaAstronomyProvider._celestial_matrix(
        "ECLIPTIC_OF_DATE", (2456165.5, 0.401182685)
    )
    np.testing.assert_allclose(actual, expected, atol=2e-15, rtol=0.0)


def test_iau_2006_transform_matches_erfa_and_round_trips(tmp_path: Path) -> None:
    # Kernel bytes are never opened by coordinate_transform.
    kernel = tmp_path / "unused.bsp"
    kernel.write_bytes(b"unused")
    provider = provider_for_kernel(kernel)
    instant = datetime(2026, 7, 21, 12, tzinfo=timezone.utc)
    vector = np.asarray((1.0, 2.0, 3.0))
    times = provider.utc_time_scales(instant)
    expected = erfa.ecm06(*times.tt) @ vector
    actual = provider.coordinate_transform(
        vector=vector,
        source_frame="ICRF",
        target_frame="ECLIPTIC_OF_DATE",
        instant_utc=instant,
        observer=None,
        settings=SETTINGS,
    )
    assert actual == pytest.approx(expected, abs=2e-15)
    recovered = provider.coordinate_transform(
        vector=actual,
        source_frame="ECLIPTIC_OF_DATE",
        target_frame="ICRF",
        instant_utc=instant,
        observer=None,
        settings=SETTINGS,
    )
    assert recovered == pytest.approx(vector, abs=2e-14)


def test_itrs_transform_requires_eop_and_uses_iau_2006(tmp_path: Path) -> None:
    kernel = tmp_path / "unused.bsp"
    kernel.write_bytes(b"unused")
    instant = datetime(2026, 7, 21, 12, tzinfo=timezone.utc)
    without_eop = provider_for_kernel(kernel)
    with pytest.raises(AstronomyDataUnavailable, match="Earth-orientation"):
        without_eop.coordinate_transform(
            vector=(1.0, 0.0, 0.0),
            source_frame="ICRF",
            target_frame="ITRS",
            instant_utc=instant,
            observer=None,
            settings=SETTINGS,
        )

    eop = EarthOrientationParameters(dut1_seconds=0.123, xp_arcsec=0.05, yp_arcsec=0.10)
    provider = provider_for_kernel(kernel, earth_orientation_resolver=lambda _: eop)
    scales = provider.utc_time_scales(instant)
    ut1 = erfa.utcut1(*scales.utc, eop.dut1_seconds)
    expected = erfa.c2t06a(
        *scales.tt, *ut1, eop.xp_arcsec * erfa.DAS2R, eop.yp_arcsec * erfa.DAS2R
    ) @ np.asarray((1.0, 0.0, 0.0))
    actual = provider.coordinate_transform(
        vector=(1.0, 0.0, 0.0),
        source_frame="ICRF",
        target_frame="ITRS",
        instant_utc=instant,
        observer=None,
        settings=SETTINGS,
    )
    assert actual == pytest.approx(expected, abs=2e-15)


def test_planet_positions_fail_closed_for_sidereal_non_ecliptic_frame(tmp_path: Path) -> None:
    kernel = tmp_path / "unused.bsp"
    kernel.write_bytes(b"unused")
    provider = provider_for_kernel(kernel)
    sidereal = CalculationSettings("ICRF", "sidereal", "lahiri", "true")
    with pytest.raises(AstronomyDataUnavailable, match="ecliptic frame"):
        provider.planet_positions(
            instant_utc=datetime(2026, 7, 21, tzinfo=timezone.utc),
            bodies=("Sun",),
            observer=None,
            settings=sidereal,
        )


def test_vector_request_fails_closed_when_it_crosses_kernel_boundary(tmp_path: Path) -> None:
    first = tmp_path / "de440.bsp"
    second = tmp_path / "de441.bsp"
    first.write_bytes(b"de440")
    second.write_bytes(b"de441")
    provider = JplErfaAstronomyProvider(
        kernel_registry=KernelRegistry(
            {
                "DE440": KernelArtifact(
                    "DE440", first, hashlib.sha256(first.read_bytes()).hexdigest()
                ),
                "DE441": KernelArtifact(
                    "DE441", second, hashlib.sha256(second.read_bytes()).hexdigest()
                ),
            }
        ),
        leap_seconds_version="test",
        earth_orientation_version="test",
        time_scale_version="test",
        tdb_minus_tt_version="test",
        time_scale_valid_from_utc=date(1960, 1, 1),
        time_scale_valid_through_utc=date(2026, 12, 31),
        ayanamsa_data_version="test",
    )

    with pytest.raises(AstronomyDataUnavailable, match="spans multiple kernels"):
        provider.geocentric_states_at_tdb_jds(
            body="Sun",
            tdb_jds=(2688976.49, 2688976.51),
            kernel_year=2650,
        )


@pytest.mark.skipif(not os.getenv("EPHEMERIS_OSS_DE440_KERNEL"), reason="real DE440 kernel not supplied")
def test_real_de440_j2000_sun_matches_horizons_reference() -> None:
    kernel = Path(os.environ["EPHEMERIS_OSS_DE440_KERNEL"])
    with provider_for_kernel(kernel) as provider:
        state = provider.geocentric_state_at_tdb_jd(
            body="Sun", tdb_jd=2451545.0, kernel_year=2000
        )
    horizons_km = (26499033.67743050, -132757417.3383451, -57556718.47054072)
    assert state.position_km == pytest.approx(horizons_km, abs=1e-4)


@pytest.mark.skipif(not os.getenv("EPHEMERIS_OSS_DE440_KERNEL"), reason="real DE440 kernel not supplied")
def test_planet_positions_accepts_explicit_leap_second_through_provider_contract() -> None:
    leap = UtcCalendarInstant(2016, 12, 31, 23, 59, 60.0)
    with provider_for_real_kernels() as provider:
        result = provider.planet_positions(
            instant_utc=leap,
            bodies=("Sun",),
            observer=None,
            settings=SETTINGS,
        )
        before = provider.planet_positions(
            instant_utc=UtcCalendarInstant(2016, 12, 31, 23, 59, 59.0),
            bodies=("Sun",),
            observer=None,
            settings=SETTINGS,
        )

    assert result["positions"]["Sun"]["position_type"] == "geometric_geocentric"
    assert result["calculation_receipt_sha256"] != before["calculation_receipt_sha256"]
    assert result["time_scales_jd"]["tdb"] > before["time_scales_jd"]["tdb"]


@pytest.mark.skipif(not os.getenv("EPHEMERIS_OSS_DE440_KERNEL"), reason="real DE440 kernel not supplied")
def test_vectorized_de440_matches_scalar_evaluation() -> None:
    kernel = Path(os.environ["EPHEMERIS_OSS_DE440_KERNEL"])
    jds = np.asarray((2451545.0, 2460000.5, 2488069.5))
    with provider_for_kernel(kernel) as provider:
        positions, velocities, metadata = provider.geocentric_states_at_tdb_jds(
            body="Jupiter_Barycenter", tdb_jds=jds, kernel_year=2000
        )
        scalar = [
            provider.geocentric_state_at_tdb_jd(
                body="Jupiter_Barycenter", tdb_jd=float(jd), kernel_year=2000
            )
            for jd in jds
        ]
    np.testing.assert_allclose(positions.T, [state.position_km for state in scalar], atol=1e-8)
    np.testing.assert_allclose(velocities.T, [state.velocity_km_per_day for state in scalar], atol=1e-8)
    assert metadata["target_naif_id"] == 5


@pytest.mark.skipif(not os.getenv("EPHEMERIS_OSS_DE440_KERNEL"), reason="real DE440 kernel not supplied")
def test_true_node_uses_rotating_ecliptic_state_and_keeps_ketu_opposed() -> None:
    instant = datetime(2026, 7, 21, 12, tzinfo=timezone.utc)
    true_settings = CalculationSettings(
        "ECLIPTIC_OF_DATE", "tropical", None, "true"
    )
    mean_settings = CalculationSettings(
        "ECLIPTIC_OF_DATE", "tropical", None, "mean"
    )
    with provider_for_real_kernels() as provider:
        true_nodes = provider.planet_positions(
            instant_utc=instant,
            bodies=("Rahu", "Ketu"),
            observer=None,
            settings=true_settings,
        )["positions"]
        mean_rahu = provider.planet_positions(
            instant_utc=instant,
            bodies=("Rahu",),
            observer=None,
            settings=mean_settings,
        )["positions"]["Rahu"]["longitude_deg"]

    true_rahu = true_nodes["Rahu"]["longitude_deg"]
    true_ketu = true_nodes["Ketu"]["longitude_deg"]
    assert (true_ketu - true_rahu) % 360.0 == pytest.approx(180.0, abs=1e-12)
    assert abs((true_rahu - mean_rahu + 180.0) % 360.0 - 180.0) > 0.01
    assert true_nodes["Rahu"]["position_type"] == "osculating_lunar_node_axis"


@pytest.mark.skipif(not os.getenv("EPHEMERIS_OSS_DE440_KERNEL"), reason="real DE440 kernel not supplied")
def test_solar_upper_limb_altitude_adds_dynamic_semidiameter() -> None:
    instant = datetime(2026, 7, 21, 12, tzinfo=timezone.utc)
    observer = Observer(latitude_deg=0.0, longitude_deg=0.0, altitude_m=0.0)
    eop = EarthOrientationParameters(dut1_seconds=0.0, xp_arcsec=0.0, yp_arcsec=0.0)
    with provider_for_real_kernels(earth_orientation_resolver=lambda _: eop) as provider:
        jd = provider.julian_day(instant_utc=instant)
        center = provider._apparent_altitude(
            jd_utc=jd,
            observer=observer,
            body="sun",
            settings=SETTINGS,
            atmosphere=None,
        )
        upper_limb = provider._apparent_altitude(
            jd_utc=jd,
            observer=observer,
            body="sun",
            settings=SETTINGS,
            atmosphere=None,
            upper_limb_radius_km=695_700.0,
        )

    assert 0.25 < upper_limb - center < 0.28


@pytest.mark.skipif(
    not all(
        os.getenv(name)
        for name in (
            "EPHEMERIS_OSS_DE440_KERNEL",
            "EPHEMERIS_OSS_DE441_PART1_KERNEL",
            "EPHEMERIS_OSS_DE441_PART2_KERNEL",
        )
    ),
    reason="real DE440 and split DE441 kernels not supplied",
)
@pytest.mark.parametrize(
    ("year", "tdb_jd", "expected"),
    [
        (
            1000,
            2086303.0,
            (62496557.56539194, -122073890.0207863, -53250206.44343915),
        ),
        (
            5000,
            3547273.0,
            (-77353074.31798324, -116383220.5251144, -49439064.97166838),
        ),
    ],
)
def test_real_split_de441_sun_matches_horizons_reference(
    year: int, tdb_jd: float, expected: tuple[float, float, float]
) -> None:
    with provider_for_real_kernels() as provider:
        state = provider.geocentric_state_at_tdb_jd(
            body="Sun", tdb_jd=tdb_jd, kernel_year=year
        )
    assert state.position_km == pytest.approx(expected, abs=1e-4)
    assert state.kernel_identifier == ("DE441-PART1" if year < 1550 else "DE441-PART2")


@pytest.mark.skipif(
    not all(
        os.getenv(name)
        for name in (
            "EPHEMERIS_OSS_DE440_KERNEL",
            "EPHEMERIS_OSS_DE441_PART1_KERNEL",
            "EPHEMERIS_OSS_DE441_PART2_KERNEL",
        )
    ),
    reason="real DE440 and split DE441 kernels not supplied",
)
def test_de441_covers_epoch_after_exact_de440_end() -> None:
    with provider_for_real_kernels() as provider:
        state = provider.geocentric_state_at_tdb_jd(
            body="Sun", tdb_jd=2689100.0, kernel_year=2650
        )

    assert state.kernel_identifier == "DE441-PART2"
    assert all(np.isfinite(state.position_km))


@pytest.mark.skipif(
    not all(
        os.getenv(name)
        for name in (
            "EPHEMERIS_OSS_DE440_KERNEL",
            "EPHEMERIS_OSS_DE441_PART1_KERNEL",
            "EPHEMERIS_OSS_DE441_PART2_KERNEL",
        )
    ),
    reason="real DE440 and split DE441 kernels not supplied",
)
def test_multi_body_vectorized_matches_scalar_for_each_kernel() -> None:
    cases = ((1000, 2086303.0), (2000, 2451545.0), (5000, 3547273.0))
    with provider_for_real_kernels() as provider:
        for year, jd in cases:
            actual = provider.geocentric_states_for_bodies_at_tdb_jds(
                bodies=("Sun", "Moon", "Jupiter_Barycenter"),
                tdb_jds=(jd, jd + 10.0),
                kernel_year=year,
            )
            for body in ("Sun", "Moon", "Jupiter_Barycenter"):
                scalar = [
                    provider.geocentric_state_at_tdb_jd(
                        body=body, tdb_jd=sample_jd, kernel_year=year
                    )
                    for sample_jd in (jd, jd + 10.0)
                ]
                display = "Jupiter Barycenter" if body == "Jupiter_Barycenter" else body.capitalize()
                positions, velocities, _metadata = actual[display]
                np.testing.assert_allclose(
                    positions.T, [state.position_km for state in scalar], atol=1e-8
                )
                np.testing.assert_allclose(
                    velocities.T,
                    [state.velocity_km_per_day for state in scalar],
                    atol=1e-8,
                )
