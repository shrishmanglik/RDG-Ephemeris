"""Unit and mathematical invariant tests for the Regional Indian Almanac layer (Stage 2)."""

from __future__ import annotations

import pytest

from ephemeris_oss import EphemerisAdapter
from ephemeris_oss.almanac import (
    BENGALI_SOLAR_MONTHS,
    LUNAR_MASA_NAMES,
    MALAYALAM_SOLAR_MONTHS,
    ODIA_SOLAR_MONTHS,
    TAMIL_SOLAR_MONTHS,
    compute_eclipse_window_summary,
    compute_lunar_month_amanta_purnimanta,
    compute_regional_panchang,
    compute_regional_solar_calendar,
)


def test_regional_solar_month_catalogs_have_12_entries_each() -> None:
    assert len(LUNAR_MASA_NAMES) == 12
    assert len(TAMIL_SOLAR_MONTHS) == 12
    assert len(MALAYALAM_SOLAR_MONTHS) == 12
    assert len(BENGALI_SOLAR_MONTHS) == 12
    assert len(ODIA_SOLAR_MONTHS) == 12
    assert TAMIL_SOLAR_MONTHS[0] == "Chithirai"
    assert MALAYALAM_SOLAR_MONTHS[4] == "Chingam"
    assert BENGALI_SOLAR_MONTHS[0] == "Boishakh"


def test_amanta_vs_purnimanta_shukla_and_krishna_paksha_rules() -> None:
    # Scan 30 consecutive days to cover both Shukla Paksha (1..15) and Krishna Paksha (16..30)
    base_jd = 2461300.5
    shukla_seen = False
    krishna_seen = False
    for offset in range(30):
        lm = compute_lunar_month_amanta_purnimanta(base_jd + offset)
        assert 0 <= lm.amanta_index <= 11
        assert 0 <= lm.purnimanta_index <= 11
        assert lm.next_amavasya_jd_ut > lm.prev_amavasya_jd_ut
        if lm.paksha == "Shukla":
            shukla_seen = True
            # In Shukla Paksha, Amanta and Purnimanta month names agree
            assert lm.purnimanta_index == lm.amanta_index
            assert lm.purnimanta_name == lm.amanta_name
        else:
            krishna_seen = True
            # In Krishna Paksha, Purnimanta is 1 month ahead of Amanta
            assert lm.purnimanta_index == (lm.amanta_index + 1) % 12
    assert shukla_seen and krishna_seen


def test_regional_solar_calendar_eras_and_months() -> None:
    # Mesha 10 deg in 2026 CE (post-Mesha Sankranti, April 2026)
    cal_mesha = compute_regional_solar_calendar(10.0, 2026)
    assert cal_mesha.surya_rashi_index == 0
    assert cal_mesha.sanskrit_saura_masa == "Mesha"
    assert cal_mesha.tamil_month == "Chithirai"
    assert cal_mesha.malayalam_month == "Medam"
    assert cal_mesha.bengali_month == "Boishakh"
    assert cal_mesha.odia_month == "Baisakha"
    assert cal_mesha.solar_day_of_month == 11
    assert cal_mesha.shaka_samvat_year == 1948
    assert cal_mesha.vikram_samvat_year == 2083
    assert cal_mesha.kali_yuga_year == 5127
    assert cal_mesha.bangabda_era_year == 1433
    assert cal_mesha.kollam_era_year == 1201

    # Simha 5 deg in 2026 CE (Chingam, Kollam Era increments to 1202)
    cal_simha = compute_regional_solar_calendar(125.0, 2026)
    assert cal_simha.surya_rashi_index == 4
    assert cal_simha.malayalam_month == "Chingam"
    assert cal_simha.kollam_era_year == 1202

    # Makara 5 deg in Jan 2026 CE (pre-Mesha Sankranti)
    cal_makara = compute_regional_solar_calendar(275.0, 2026)
    assert cal_makara.surya_rashi_index == 9
    assert cal_makara.tamil_month == "Thai"
    assert cal_makara.shaka_samvat_year == 1947
    assert cal_makara.vikram_samvat_year == 2082


def test_eclipse_window_detection_around_feb_2026_eclipse() -> None:
    # Feb 17, 2026 annular solar eclipse and Mar 3, 2026 total lunar eclipse
    jd_feb_2026 = EphemerisAdapter.julday(2026, 2, 20, 12.0)
    win = compute_eclipse_window_summary(
        jd_feb_2026,
        latitude_deg=28.6139,
        longitude_deg=77.2090,
        window_days=16.0,
    )
    assert win.has_eclipse_within_window is True
    assert win.nearest_solar_eclipse is not None
    assert win.nearest_lunar_eclipse is not None
    assert "local_visible" in win.nearest_solar_eclipse
    assert "local_visible" in win.nearest_lunar_eclipse


def test_complete_regional_panchang_with_compact_adapter_and_receipt() -> None:
    jd = EphemerisAdapter.julday(2026, 10, 6, 6.0)
    with EphemerisAdapter(kernels="compact") as adapter:
        rep1 = compute_regional_panchang(jd, 28.6139, 77.2090, adapter=adapter)
        rep2 = compute_regional_panchang(jd, 28.6139, 77.2090, adapter=adapter)
    assert len(rep1.receipt_sha256) == 64
    assert rep1.receipt_sha256 == rep2.receipt_sha256
    assert rep1.sidereal_ayana in ("Uttarayana", "Dakshinayana")
    assert rep1.tropical_ayana in ("Uttarayana", "Dakshinayana")
    d = rep1.to_dict()
    assert d["receipt_sha256"] == rep1.receipt_sha256
    assert "lunar_month" in d and "solar_calendar" in d

    with pytest.raises(ValueError):
        compute_regional_panchang(jd, 95.0, 77.2090)
