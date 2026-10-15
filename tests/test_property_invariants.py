"""Deterministic Monte Carlo Property-Based Mathematical Invariant Suite.

Verifies fundamental astronomical and Vedic Jyotish invariants across hundreds of
seeded epochs (1800-2100 CE) and geographic coordinates so edge-case regressions
are impossible.
"""

from __future__ import annotations

import math
import random

from ephemeris_oss.adapter import EphemerisAdapter, VEDIC_NINE_GRAHAS
from ephemeris_oss.jyotish.ashtakavarga import compute_ashtakavarga
from ephemeris_oss.jyotish.dasha import compute_vimshottari_dasha
from ephemeris_oss.jyotish.nakshatra import nakshatra_position
from ephemeris_oss.jyotish.vargas import SHODASHVARGA_KEYS, compute_shodashvarga
from ephemeris_oss.jyotish_advanced.koota import evaluate_ashtakoota
from ephemeris_oss.jyotish_advanced.kp import kp_coordinate_lords


def test_property_julday_revjul_bijection_100_random_instants() -> None:
    rng = random.Random(20261015)
    for _ in range(100):
        jd = rng.uniform(2378497.0, 2488069.0)  # 1800..2100 CE
        y, m, d, h = EphemerisAdapter.revjul(jd)
        jd_back = EphemerisAdapter.julday(y, m, d, h)
        assert math.isclose(jd, jd_back, abs_tol=1e-7)


def test_property_planetary_and_varga_invariants_across_50_charts() -> None:
    rng = random.Random(31415926)
    with EphemerisAdapter(kernels="compact") as adapter:
        for _ in range(50):
            jd = rng.uniform(2415020.5, 2488069.0)
            lat = rng.uniform(-60.0, 60.0)
            lon = rng.uniform(-180.0, 180.0)

            positions = {
                body.capitalize(): adapter.calc_ut(jd, body, sidereal=True).longitude_deg
                for body in VEDIC_NINE_GRAHAS
            }
            # 1. Rahu-Ketu exact 180-degree opposition
            assert math.isclose(
                (positions["Rahu"] + 180.0) % 360.0,
                positions["Ketu"],
                abs_tol=1e-9,
            )

            # 2. All 16 Shodashavarga signs in 0..11
            for body_lon in positions.values():
                vargas = compute_shodashvarga(body_lon)
                assert set(vargas.keys()) == set(SHODASHVARGA_KEYS)
                for v_pos in vargas.values():
                    assert 0 <= v_pos.sign_index <= 11

                # 3. Nakshatra index in 0..26 and pada in 1..4
                nak = nakshatra_position(body_lon)
                assert 0 <= nak.index <= 26
                assert 1 <= nak.pada <= 4

                # 4. KP Sub-lord number in 1..249
                kp = kp_coordinate_lords(body_lon)
                assert 1 <= kp.horary_number_249 <= 249

            # 5. Houses cusp count and finite bounds
            houses = adapter.houses_ut(jd, lat, lon, system="placidus")
            assert len(houses.cusps_deg) == 12
            assert all(0.0 <= c < 360.0 for c in houses.cusps_deg)

            # 6. Sarvashtakavarga grand total invariant == 337 bindus
            av = compute_ashtakavarga(positions, houses.ascendant_deg)
            assert av.sarvashtakavarga_7_total == 337

            # 7. Vimshottari Mahadasha 9-lord progression and positive span invariant
            dasha_timeline = compute_vimshottari_dasha(positions["Moon"], jd)
            mahadashas = dasha_timeline.mahadashas
            assert len(mahadashas) == 9
            assert mahadashas[-1].end_jd > mahadashas[0].start_jd


def test_property_ashtakoota_bounds_and_determinism_100_pairs() -> None:
    rng = random.Random(27182818)
    for _ in range(100):
        lon_a = rng.uniform(0.0, 360.0 - 1e-9)
        lon_b = rng.uniform(0.0, 360.0 - 1e-9)
        rep1 = evaluate_ashtakoota(lon_a, lon_b)
        rep2 = evaluate_ashtakoota(lon_a, lon_b)
        assert 0.0 <= rep1.total_raw_points <= 36.0
        assert rep1.receipt_sha256 == rep2.receipt_sha256
