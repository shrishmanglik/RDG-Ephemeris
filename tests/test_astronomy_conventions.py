from __future__ import annotations

import math

import erfa
import pytest

from ephemeris_oss.engine.contracts import AstronomyDataUnavailable
from ephemeris_oss.engine.conventions import (
    AYANAMSA_CATALOG,
    AYANAMSA_CATALOG_VERSION,
    HOUSE_CONVENTIONS_VERSION,
    J2000_TT_JD,
    LUNAR_NODE_CONVENTIONS_VERSION,
    ascendant_midheaven_from_sidereal,
    ayanamsa_degrees,
    general_precession_longitude_degrees,
    house_angles,
    house_layout,
    mean_lunar_node_longitude_degrees,
    normalize_degrees,
    osculating_lunar_node_longitude_degrees,
    tropical_to_sidereal,
)


def _angular_difference(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0)




def test_lahiri_is_derived_from_the_published_iae_anchor_not_calibrated():
    definition = AYANAMSA_CATALOG["lahiri"]
    assert "Calibrated" not in definition.source_reference
    assert definition.reference_jd_tt == 2435553.5
    assert "1989" in definition.source_reference




def test_catalog_is_versioned_complete_and_has_explicit_sources() -> None:
    assert AYANAMSA_CATALOG_VERSION == "ephemeris-oss-ayanamsa-anchors-1.3.0"
    assert HOUSE_CONVENTIONS_VERSION == "ephemeris-oss-houses-1.1.0-iau2006"
    assert LUNAR_NODE_CONVENTIONS_VERSION == "ephemeris-oss-lunar-nodes-1.0.0"
    assert set(AYANAMSA_CATALOG) == {
        "lahiri",
        "raman",
        "kp",
        "yukteshwar",
        "fagan_bradley",
        "true_citra",
        "pushya",
    }
    assert all(definition.source_reference for definition in AYANAMSA_CATALOG.values())


@pytest.mark.parametrize("convention,jd,expected", [
    ("lahiri",J2000_TT_JD,23.85709235), ("chitra paksha",J2000_TT_JD,23.85709235),
    ("raman",2415020.,21.01444-.828/3600),
    ("kp",2415020.,22.363889-.828/3600),
    ("krishnamurti",2415020.,22.363889-.828/3600),
    ("yukteshwar",2415020.,21.082222),
    ("fagan-bradley",2433282.42346,24+2/60+31.36/3600-.41256/3600),
])
def test_mean_ayanamsa_anchors_are_exact_at_their_defining_epoch(convention,jd,expected):
    # Modern realizations retain exact published defining epochs; J2000 is no
    # longer falsely treated as their defining epoch. Independent grid tests
    # verify transport separately. Lahiri's J2000 value is a rounded reference.
    tolerance = .0005/3600 if convention in {"lahiri","chitra paksha"} else 1e-12
    assert ayanamsa_degrees(jd,convention) == pytest.approx(expected,abs=tolerance)


def test_lahiri_1956_mean_and_true_are_paired_with_the_frozen_reference() -> None:
    jd = 2435553.5
    mean = ayanamsa_degrees(jd, "lahiri")
    true = ayanamsa_degrees(jd, "lahiri", true=True)
    assert abs(mean - (23 + 14 / 60 + 44.019 / 3600)) * 3600 < .002
    assert abs(true - (23 + 15 / 60 + .796 / 3600)) * 3600 < .002


def test_reference_ecliptic_transport_is_not_the_j2000_scalar_precession() -> None:
    future = J2000_TT_JD + 36525.0
    delta = general_precession_longitude_degrees(future)
    assert delta == pytest.approx(math.degrees(erfa.p06e(J2000_TT_JD, 36525.0)[12]))
    lahiri_delta = ayanamsa_degrees(future, "lahiri") - ayanamsa_degrees(J2000_TT_JD, "lahiri")
    raman_delta = ayanamsa_degrees(future, "raman") - ayanamsa_degrees(J2000_TT_JD, "raman")
    assert lahiri_delta != pytest.approx(delta, abs=1e-12)
    assert raman_delta != pytest.approx(delta, abs=1e-12)


def test_star_anchored_ayanamsas_require_date_specific_stellar_longitude() -> None:
    with pytest.raises(AstronomyDataUnavailable, match="anchor-star"):
        ayanamsa_degrees(J2000_TT_JD, "true_citra")
    with pytest.raises(AstronomyDataUnavailable, match="anchor-star"):
        ayanamsa_degrees(J2000_TT_JD, "pushya")
    assert ayanamsa_degrees(
        J2000_TT_JD, "true_citra", anchor_tropical_longitude_deg=203.84
    ) == pytest.approx(23.84)
    assert ayanamsa_degrees(
        J2000_TT_JD, "pushya_paksha", anchor_tropical_longitude_deg=128.7219777778
    ) == pytest.approx(22.7219777778)


def test_ayanamsa_and_sidereal_conversion_fail_closed_and_wrap() -> None:
    with pytest.raises(AstronomyDataUnavailable, match="unsupported ayanamsa"):
        ayanamsa_degrees(J2000_TT_JD, "invented")
    with pytest.raises(AstronomyDataUnavailable, match="1600 through 2400"):
        ayanamsa_degrees(J2000_TT_JD + 4.01 * 36525.0, "lahiri")
    assert tropical_to_sidereal(1.0, J2000_TT_JD, "lahiri") == pytest.approx(337.14290765)
    assert normalize_degrees(-0.0) == 0.0
    with pytest.raises(AstronomyDataUnavailable, match="finite"):
        normalize_degrees(float("nan"))


def test_mean_lunar_node_matches_polynomial_anchor_and_regresses() -> None:
    at_epoch = mean_lunar_node_longitude_degrees(J2000_TT_JD)
    ten_days_later = mean_lunar_node_longitude_degrees(J2000_TT_JD + 10.0)
    assert at_epoch == pytest.approx(125.04455501, abs=1e-12)
    signed_motion = (ten_days_later - at_epoch + 180.0) % 360.0 - 180.0
    assert signed_motion < 0.0


def test_osculating_lunar_node_comes_from_state_vector_plane() -> None:
    inclination = math.radians(5.0)
    longitude = osculating_lunar_node_longitude_degrees(
        (1.0, 0.0, 0.0),
        (0.0, math.cos(inclination), math.sin(inclination)),
    )
    assert longitude == pytest.approx(0.0, abs=1e-12)

    rotated = osculating_lunar_node_longitude_degrees(
        (0.0, 1.0, 0.0),
        (-math.cos(inclination), 0.0, math.sin(inclination)),
    )
    assert rotated == pytest.approx(90.0, abs=1e-12)


def test_osculating_lunar_node_fails_closed_for_degenerate_state() -> None:
    with pytest.raises(AstronomyDataUnavailable, match="singular"):
        osculating_lunar_node_longitude_degrees((1.0, 0.0, 0.0), (0.0, 1.0, 0.0))
    with pytest.raises(AstronomyDataUnavailable, match="3 values"):
        osculating_lunar_node_longitude_degrees((1.0, 0.0), (0.0, 1.0, 0.0))


def test_equatorial_sidereal_cardinal_angles_are_exact() -> None:
    ascendant, midheaven = ascendant_midheaven_from_sidereal(0.0, 0.0, 23.4)
    assert ascendant == pytest.approx(90.0, abs=1e-12)
    assert midheaven == pytest.approx(0.0, abs=1e-12)

    ascendant, midheaven = ascendant_midheaven_from_sidereal(90.0, 0.0, 23.4)
    assert ascendant == pytest.approx(180.0, abs=1e-12)
    assert midheaven == pytest.approx(90.0, abs=1e-12)


def test_house_angles_are_iau_derived_and_longitude_is_east_positive() -> None:
    tt_jd = 2459580.5
    ut1_jd = 2459580.499998
    greenwich = house_angles(
        tt_jd=tt_jd,
        ut1_jd=ut1_jd,
        longitude_deg=0.0,
        latitude_deg=28.6139,
    )
    east = house_angles(
        tt_jd=tt_jd,
        ut1_jd=ut1_jd,
        longitude_deg=77.2090,
        latitude_deg=28.6139,
    )
    tt = (J2000_TT_JD, tt_jd - J2000_TT_JD)
    ut1 = (J2000_TT_JD, ut1_jd - J2000_TT_JD)
    assert greenwich.earth_rotation_angle_deg == pytest.approx(
        math.degrees(erfa.era00(*ut1)) % 360.0
    )
    assert greenwich.gmst_deg == pytest.approx(math.degrees(erfa.gmst06(*ut1, *tt)) % 360.0)
    assert greenwich.gast_deg == pytest.approx(math.degrees(erfa.gst06a(*ut1, *tt)) % 360.0)
    assert (
        _angular_difference(
            east.local_apparent_sidereal_deg,
            greenwich.local_apparent_sidereal_deg + 77.2090,
        )
        < 1e-12
    )


def test_house_angles_fail_closed_at_geographic_poles() -> None:
    with pytest.raises(AstronomyDataUnavailable, match="geographic poles"):
        ascendant_midheaven_from_sidereal(0.0, 90.0, 23.4)


def test_whole_sign_and_equal_house_boundaries_wrap_exactly() -> None:
    whole = house_layout("whole_sign", ascendant_deg=359.999999, midheaven_deg=270.0)
    assert whole.cusps_deg[0] == 330.0
    assert whole.cusps_deg[-1] == 300.0
    assert whole.centers_deg[0] == 345.0

    equal = house_layout("equal", ascendant_deg=350.0, midheaven_deg=270.0)
    assert equal.cusps_deg[:3] == pytest.approx((350.0, 20.0, 50.0))
    assert equal.cusps_deg[6] == pytest.approx(170.0)


def test_porphyry_trisects_each_quadrant_and_preserves_opposites() -> None:
    layout = house_layout("porphyry", ascendant_deg=100.0, midheaven_deg=20.0)
    assert layout.cusps_deg == pytest.approx(
        (
            100.0,
            133.33333333333334,
            166.66666666666669,
            200.0,
            226.66666666666666,
            253.33333333333334,
            280.0,
            313.3333333333333,
            346.6666666666667,
            20.0,
            46.66666666666667,
            73.33333333333334,
        )
    )
    for index in range(6):
        assert (
            _angular_difference(layout.cusps_deg[index + 6], layout.cusps_deg[index] + 180) < 1e-12
        )


def test_sripati_uses_porphyry_points_as_centres_and_midpoint_boundaries() -> None:
    porphyry = house_layout("porphyry", ascendant_deg=100.0, midheaven_deg=20.0)
    sripati = house_layout("sripati", ascendant_deg=100.0, midheaven_deg=20.0)
    assert sripati.centers_deg == pytest.approx(porphyry.cusps_deg)
    assert sripati.cusps_deg == sripati.boundaries_deg
    for index, boundary in enumerate(sripati.boundaries_deg):
        previous = sripati.centers_deg[(index - 1) % 12]
        current = sripati.centers_deg[index]
        expected = (previous + (current - previous) % 360.0 / 2.0) % 360.0
        assert boundary == pytest.approx(expected)


def test_placidus_semisarc_houses_are_opposed_and_require_inputs() -> None:
    angles = house_angles(
        tt_jd=2451545.0,
        ut1_jd=2451545.0,
        longitude_deg=0.0,
        latitude_deg=28.6139,
    )
    layout = house_layout(
        "placidus",
        ascendant_deg=angles.ascendant_deg,
        midheaven_deg=angles.midheaven_deg,
        local_apparent_sidereal_deg=angles.local_apparent_sidereal_deg,
        latitude_deg=28.6139,
        true_obliquity_deg=angles.true_obliquity_deg,
    )

    assert layout.system == "placidus"
    assert layout.cusps_deg[0] == pytest.approx(angles.ascendant_deg, abs=1e-12)
    assert layout.cusps_deg[9] == pytest.approx(angles.midheaven_deg, abs=1e-12)
    for index in range(6):
        assert (layout.cusps_deg[index + 6] - layout.cusps_deg[index]) % 360.0 == pytest.approx(
            180.0, abs=1e-10
        )

    with pytest.raises(AstronomyDataUnavailable, match="requires"):
        house_layout("placidus", ascendant_deg=100.0, midheaven_deg=20.0)


def test_porphyry_and_unknown_house_systems_fail_closed() -> None:
    with pytest.raises(AstronomyDataUnavailable, match="Porphyry quadrant"):
        house_layout("porphyry", ascendant_deg=0.0, midheaven_deg=180.0)
    with pytest.raises(AstronomyDataUnavailable, match="unsupported house system"):
        house_layout("unknown-system", ascendant_deg=100.0, midheaven_deg=20.0)



@pytest.mark.parametrize("key,jd,offset,shift", [
    ("raman",2415020.,21.01444,.828), ("kp",2415020.,22.363889,.828),
    ("yukteshwar",2415020.,21.082222,0),
    ("fagan_bradley",2433282.42346,24+2/60+31.36/3600,.41256),
])
def test_r3_published_reference_epoch_and_frame_are_exact(key,jd,offset,shift):
    expected=(offset-shift/3600)%360
    assert _angular_difference(ayanamsa_degrees(jd,key),expected)*3600 <= .001


@pytest.mark.parametrize("key", ["raman","kp","yukteshwar"])
def test_r3_modern_realizations_do_not_claim_original_author_fidelity(key):
    definition=AYANAMSA_CATALOG[key]
    assert "realization" in definition.label
    assert definition.original_author_ambiguity
    assert "IAU2006" in definition.precession_model
    assert "aacf962d" not in definition.source_reference
    assert "Swiss-compatible realisation" in definition.source_reference
