"""Agreement with Swiss Ephemeris (agreement, never accuracy): houses and the Lahiri realisation.

AGPL-3.0, like the rest of this directory. Run only inside the Swiss comparator's own environment, with
the package installed: ``python -m pytest bench/comparators/swiss``. Nothing in the package imports this.
"""

from __future__ import annotations

import pytest

from ephemeris_oss.engine.conventions import (
    ascendant_midheaven_from_sidereal,
    ayanamsa_degrees,
    house_layout,
)


def _angular_difference(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0)

@pytest.mark.parametrize("system,code", [
    ("whole_sign", b"W"), ("placidus", b"P"), ("equal", b"E"), ("koch", b"K"),
    ("sripati", b"S"), ("campanus", b"C"), ("regiomontanus", b"R"), ("porphyry", b"O"),
])
@pytest.mark.parametrize("armc,latitude,obliquity", [
    (120., 43.65, 23.44), (359.9, -33.8, 23.42), (0.1, 65., 23.46),
    (195., -60., 23.43), (75., 0., 23.45),
])
def test_house_cusps_agree_under_identical_angles(system, code, armc, latitude, obliquity):
    import swisseph as swe
    expected, angles = swe.houses_armc(armc, latitude, obliquity, code)
    asc, mc = ascendant_midheaven_from_sidereal(armc, latitude, obliquity)
    actual = house_layout(system, ascendant_deg=asc, midheaven_deg=mc,
                          local_apparent_sidereal_deg=armc, latitude_deg=latitude,
                          true_obliquity_deg=obliquity)
    assert _angular_difference(asc, angles[0]) * 3600 <= .01
    assert _angular_difference(mc, angles[1]) * 3600 <= .01
    assert max(_angular_difference(a,b)*3600 for a,b in zip(actual.cusps_deg, expected)) <= .01


def test_lahiri_mean_and_true_agree_1900_to_2100():
    import swisseph as swe
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    for year in range(1900, 2101):
        for month in (1, 4, 7, 10):
            jd = swe.julday(year, month, 1, 0.0)
            for true in (False, True):
                flags = swe.FLG_SWIEPH | (0 if true else swe.FLG_NONUT)
                expected = swe.get_ayanamsa_ex(jd, flags)[1]
                actual = ayanamsa_degrees(jd, "lahiri", true=true)
                assert _angular_difference(actual, expected) * 3600 <= .01, (year, month, true, actual, expected)
