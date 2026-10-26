"""The long-term *convention* contract, distinct from stellar accuracy."""
import math

import erfa
import pytest

from ephemeris_oss.engine.contracts import AstronomyDataUnavailable
from ephemeris_oss.engine.civil_time import CalendarSystem, calendar_jd
from ephemeris_oss.engine.earth_orientation import estimate_delta_t
from ephemeris_oss.engine.conventions import (
    AYANAMSA_CATALOG, ayanamsa_degrees, mean_lunar_node_longitude_degrees,
)


ADDITIONS = {
    "lahiri_icrc", "lahiri_1940", "kp_senthilathiban", "sassanian",
    "true_revati", "true_mula", "aldebaran", "galactic_center_sagittarius",
    "galactic_center_capricorn", "dhruva_middle_mula",
    "galactic_equator_iau1958", "galactic_equator_modern", "ardra_galactic_plane",
    "suryasiddhanta_equinox", "suryasiddhanta_mean_sun", "aryabhata_equinox",
    "aryabhata_mean_sun", "aryabhata_522", "suryasiddhanta_revati",
    "suryasiddhanta_citra",
}
ENDPOINTS = (-3100015.5, 8000016.5)


def test_distinct_conventions_have_explicit_realizations():
    assert ADDITIONS <= AYANAMSA_CATALOG.keys()
    assert len(AYANAMSA_CATALOG) >= 27
    for key in ADDITIONS:
        definition = AYANAMSA_CATALOG[key]
        assert definition.key == key
        assert definition.source_reference
        assert definition.precession_model.startswith("Vondrak2011")
    for key in ("suryasiddhanta_equinox", "suryasiddhanta_mean_sun",
                "aryabhata_equinox", "aryabhata_mean_sun", "aryabhata_522",
                "suryasiddhanta_revati", "suryasiddhanta_citra"):
        assert "modern realization" in AYANAMSA_CATALOG[key].original_author_ambiguity


@pytest.mark.parametrize("jd", [*ENDPOINTS, 2451545.])
def test_all_convention_operations_accept_complete_jpl_coordinate_range(jd):
    assert ADDITIONS <= AYANAMSA_CATALOG.keys()
    for definition in AYANAMSA_CATALOG.values():
        kwargs = ({"anchor_tropical_longitude_deg": 203.84}
                  if definition.model in {"star_anchor", "polar_anchor"} else {})
        value = ayanamsa_degrees(jd, definition.key, **kwargs)
        assert math.isfinite(value) and 0 <= value < 360


def test_long_term_reference_ray_is_independently_constructed_from_poles():
    # Construct a date equinox with the pole cross product rather than ltp().
    jd = ENDPOINTS[0]
    reference = AYANAMSA_CATALOG["kp_senthilathiban"]
    epoch = 2000. + (jd - 2451545.) / 365.25
    equator, ecliptic = erfa.ltpequ(epoch), erfa.ltpecl(epoch)
    equinox = erfa.pxp(equator, ecliptic)
    equinox = equinox / erfa.pm(equinox)
    ref_epoch = 2000. + (reference.reference_jd_tt - 2451545.) / 365.25
    vector = erfa.ltp(ref_epoch) @ equinox
    obliquity = math.acos(float(erfa.pdp(erfa.ltpequ(ref_epoch), erfa.ltpecl(ref_epoch))))
    lon = math.degrees(math.atan2(vector[1]*math.cos(obliquity)
                                 + vector[2]*math.sin(obliquity), vector[0]))
    expected = (reference.reference_offset_deg - lon) % 360.
    assert ayanamsa_degrees(jd, reference.key) == pytest.approx(expected, abs=1e-11)


def test_long_term_ayanamsa_does_not_extend_short_term_lunar_polynomial():
    assert math.isfinite(ayanamsa_degrees(ENDPOINTS[0], "lahiri"))
    with pytest.raises(AstronomyDataUnavailable):
        mean_lunar_node_longitude_degrees(ENDPOINTS[0])
    for jd in (ENDPOINTS[0] - 1., ENDPOINTS[1] + 1., math.nan):
        with pytest.raises(AstronomyDataUnavailable):
            ayanamsa_degrees(jd, "lahiri")


def test_stellar_and_polar_inputs_are_required_not_synthesized():
    assert ADDITIONS <= AYANAMSA_CATALOG.keys()
    for definition in AYANAMSA_CATALOG.values():
        if definition.model in {"star_anchor", "polar_anchor"}:
            with pytest.raises(AstronomyDataUnavailable, match="anchor"):
                ayanamsa_degrees(2451545., definition.key)
            with pytest.raises(AstronomyDataUnavailable, match="finite"):
                ayanamsa_degrees(2451545., definition.key,
                                 anchor_tropical_longitude_deg=math.nan)


@pytest.mark.parametrize("key,year,seconds", [
    ("suryasiddhanta_equinox", 499, 7*3600+30*60+31.57),
    ("aryabhata_equinox", 499, 6*3600+56*60+55.57),
    ("aryabhata_522", 522, 5*3600+46*60+44.),
])
def test_historical_realizations_keep_ut1_to_tt_policy_explicit(key, year, seconds):
    start = calendar_jd(year, 1, 1, calendar=CalendarSystem.JULIAN)
    end = calendar_jd(year+1, 1, 1, calendar=CalendarSystem.JULIAN)
    ut1 = calendar_jd(year, 3, 21, seconds/86400., calendar=CalendarSystem.JULIAN)
    delta_t = estimate_delta_t(year+(ut1-start)/(end-start))
    definition = AYANAMSA_CATALOG[key]
    assert definition.reference_jd_tt == pytest.approx(ut1+delta_t.seconds/86400., abs=1e-10)
    assert "UT1" in definition.source_reference
    assert "Espenak/Meeus" in definition.source_reference
    assert definition.reference_offset_deg == 0.
    assert ayanamsa_degrees(definition.reference_jd_tt, key) == pytest.approx(0., abs=1e-10)
