"""Executable documentation integrity and mathematical derivation tests (Pillar 18)."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import math
from pathlib import Path
import pytest

from ephemeris_oss import (
    Engine,
    EphemerisAdapter,
    EphemerisError,
    Undefined,
    cli,
    compile_ai_fact_sheet,
    verify_ai_interpretation,
)
from ephemeris_oss.almanac import (
    generate_ephemeris_table,
    generate_monthly_panchang,
    scan_ingresses_and_aspects,
)
from ephemeris_oss.compact_kernel import COMPACT_KERNEL_SHA256, CompactChebyshevKernel
from ephemeris_oss.engine.conventions import (
    ayanamsa_degrees,
    house_layout,
    mean_lunar_node_longitude_degrees,
)
from ephemeris_oss.jyotish import (
    abhijit_position,
    compute_ashtakavarga,
    compute_panchanga,
    compute_shadbala,
    compute_shodashvarga,
    compute_vimshottari_dasha,
    nakshatra_position,
    resolve_dasha_5_levels,
    varga_sign,
)
from ephemeris_oss.jyotish_siddhanta import (
    KALI_YUGA_EPOCH_JD,
    MAHAYUGA_SAVANA_DAYS,
    compute_vedanga_yuga_state,
    surya_siddhanta_true_positions,
)
from ephemeris_oss.visualization import (
    render_circular_wheel_svg,
    render_east_indian_svg,
    render_north_indian_svg,
    render_south_indian_svg,
)

ROOT = Path(__file__).resolve().parents[1]

SAMPLE_LONS: dict[str, float] = {
    "Sun": 10.5,
    "Moon": 45.2,
    "Mars": 120.8,
    "Mercury": 15.0,
    "Jupiter": 95.4,
    "Venus": 350.1,
    "Saturn": 200.3,
    "Rahu": 150.0,
    "Ketu": 330.0,
}
SAMPLE_LAGNA_DEG: float = 25.0


def test_public_documentation_files_exist_and_have_zero_em_dashes() -> None:
    required_files = (
        ROOT / "README.md",
        ROOT / "docs" / "ACCURACY.md",
        ROOT / "docs" / "ARCHITECTURE-AND-MATHEMATICAL-REFERENCE.md",
        ROOT / "docs" / "claims.yaml",
        ROOT / "docs" / "benchmark-portal" / "index.html",
        ROOT / "web" / "ephemeris-browser.js",
        ROOT / "web" / "ephemeris-browser.d.ts",
    )
    for path in required_files:
        assert path.is_file(), f"Missing required documentation/SDK file: {path}"
        content = path.read_text(encoding="utf-8")
        assert len(content.strip()) > 100
        assert "\u2014" not in content, f"Em dash found in {path}"


def test_architecture_reference_covers_all_required_mathematical_sections() -> None:
    ref_text = (ROOT / "docs" / "ARCHITECTURE-AND-MATHEMATICAL-REFERENCE.md").read_text(
        encoding="utf-8"
    )
    required_headings_and_terms = (
        "Clenshaw",
        "IAU 2006 Precession",
        "IAU 2000A Nutation",
        "Chitrapaksha",
        "True Citra",
        "Krishnamurti",
        "Meeus",
        "Bhava Chalit",
        "Divisional Vargas",
        "337",
        "Sarvashtakavarga",
        "Shadbala",
        "Vimshottari",
        "Panchanga",
        "Surya Siddhanta",
        "AIFactSheet",
    )
    for term in required_headings_and_terms:
        assert term in ref_text, f"Missing documented mathematical concept {term!r}"


def test_documented_chebyshev_compact_kernel_and_clenshaw_recurrence() -> None:
    with CompactChebyshevKernel.open() as kernel:
        assert kernel.sha256 == COMPACT_KERNEL_SHA256
        moon_seg = next(s for s in kernel.segments if (s.center, s.target) == (3, 301))
        pos_km, vel_km_day = moon_seg.compute_and_differentiate(2451545.0, 0.0)
        assert pos_km.shape == (3,)
        assert vel_km_day.shape == (3,)
        assert 350_000.0 < float((pos_km @ pos_km) ** 0.5) < 410_000.0


def test_documented_tt_and_utc_engine_receipt_determinism() -> None:
    with Engine.load(kernels="compact", eop=None) as engine:
        res1 = engine.positions_tt(2451545.0, bodies=("sun", "moon", "mars", "jupiter", "saturn"))
        res2 = engine.positions_tt(2451545.0, bodies=("sun", "moon", "mars", "jupiter", "saturn"))
        assert len(res1.receipt_sha256) == 64
        assert res1.receipt_sha256 == res2.receipt_sha256
        assert 0.0 <= res1.value["moon"]["longitude_deg"] < 360.0


def test_documented_ayanamsa_models_lahiri_raman_kp_yukteshwar_fagan() -> None:
    jd_j2000 = 2451545.0
    lahiri_j2000 = ayanamsa_degrees(jd_j2000, "lahiri")
    raman_j2000 = ayanamsa_degrees(jd_j2000, "raman")
    kp_j2000 = ayanamsa_degrees(jd_j2000, "krishnamurti")
    yukteshwar_j2000 = ayanamsa_degrees(jd_j2000, "yukteshwar")
    fagan_j2000 = ayanamsa_degrees(jd_j2000, "fagan_bradley")
    assert 23.85 < lahiri_j2000 < 23.86
    assert 22.40 < raman_j2000 < 22.42
    assert 23.75 < kp_j2000 < 23.77
    assert 22.0 < yukteshwar_j2000 < 23.0
    assert 24.7 < fagan_j2000 < 24.8


def test_documented_meeus_eq_47_7_mean_node_and_antipode_invariant() -> None:
    jd_j2000 = 2451545.0
    omega_j2000 = mean_lunar_node_longitude_degrees(jd_j2000)
    assert abs(omega_j2000 - 125.0445479) < 1e-7
    ketu_j2000 = (omega_j2000 + 180.0) % 360.0
    assert math.isclose(abs(ketu_j2000 - omega_j2000), 180.0, abs_tol=1e-9)


def test_documented_bhava_chalit_whole_sign_equal_porphyry_placidus_and_polar_guard() -> None:
    ws = house_layout("whole_sign", ascendant_deg=45.0, midheaven_deg=315.0)
    eq = house_layout("equal_house", ascendant_deg=45.0, midheaven_deg=315.0)
    po = house_layout(
        "porphyry",
        ascendant_deg=45.0,
        midheaven_deg=315.0,
        local_apparent_sidereal_deg=10.0,
        latitude_deg=28.6139,
        true_obliquity_deg=23.43929,
    )
    pl = house_layout(
        "placidus",
        ascendant_deg=45.0,
        midheaven_deg=315.0,
        local_apparent_sidereal_deg=10.0,
        latitude_deg=28.6139,
        true_obliquity_deg=23.43929,
    )
    assert ws.cusps_deg[0] == 30.0
    assert eq.cusps_deg[0] == 45.0
    assert len(po.cusps_deg) == 12
    assert len(pl.cusps_deg) == 12

    # Polar circle Placidus fails closed on EphemerisAdapter and returns Undefined on Engine
    with EphemerisAdapter(kernels="compact") as adapter:
        with pytest.raises(EphemerisError):
            adapter.houses_ex(2461041.0, 80.0, 0.0, b"P")

    with Engine.load(kernels="compact") as eng:
        polar_res = eng.houses(
            datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc),
            lat=80.0,
            lon=0.0,
            system="placidus",
        )
        assert isinstance(polar_res.value, Undefined)


def test_documented_nakshatra_27_and_28_abhijit_formulas() -> None:
    nak = nakshatra_position(SAMPLE_LONS["Moon"])
    assert nak.index == int(SAMPLE_LONS["Moon"] // (40.0 / 3.0))
    assert 1 <= nak.pada <= 4
    assert math.isclose(nak.fraction_elapsed + nak.fraction_remaining, 1.0, abs_tol=1e-12)

    abh = abhijit_position(278.0)
    assert abh.in_abhijit is True
    assert abh.nakshatra_28_name == "Abhijit"


def test_documented_divisional_vargas_d1_through_d60_formulas() -> None:
    vargas = compute_shodashvarga(SAMPLE_LONS["Sun"], include_higher=True)
    assert len(vargas) == 23
    assert vargas["D1"].sign_index == 0
    assert vargas["D9"].sign_index == int(10.5 // (10.0 / 3.0)) % 12
    # Parashari D30 odd sign bands: [0..5)->0, [5..10)->10, [10..18)->8, [18..25)->2, [25..30)->6
    assert [varga_sign(d, "D30").sign_index for d in (2.0, 7.0, 14.0, 21.0, 27.0)] == [
        0,
        10,
        8,
        2,
        6,
    ]
    assert varga_sign(0.1, "D60").shashtiamsa_name == "Ghora"


def test_documented_ashtakavarga_337_bindu_conservation_and_shodhana() -> None:
    av = compute_ashtakavarga(SAMPLE_LONS, SAMPLE_LAGNA_DEG)
    expected_totals = {
        "Sun": 48,
        "Moon": 49,
        "Mars": 39,
        "Mercury": 54,
        "Jupiter": 56,
        "Venus": 52,
        "Saturn": 39,
    }
    for body, total in expected_totals.items():
        assert av.bhinna_tables[body].total_bindus == total
    assert av.sarvashtakavarga_7_total == 337


def test_documented_shadbala_six_fold_strength_and_rupas_conversion() -> None:
    shadbala = compute_shadbala(SAMPLE_LONS, SAMPLE_LAGNA_DEG)
    assert len(shadbala.planets) == 7
    for ps in shadbala.planets.values():
        assert ps.total_virupas > 0.0
        assert math.isclose(ps.total_rupas, ps.total_virupas / 60.0, abs_tol=1e-9)


def test_documented_vimshottari_120_year_and_5_level_prana_dasha() -> None:
    dasha = compute_vimshottari_dasha(0.0, birth_jd=2451545.0, max_level=3)
    assert len(dasha.mahadashas) == 9
    assert math.isclose(sum(m.duration_years for m in dasha.mahadashas), 120.0, abs_tol=1e-9)
    levels = resolve_dasha_5_levels(dasha, 2451545.0 + 365.0)
    assert len(levels) == 5
    assert levels[-1].level_name == "Prana"


def test_documented_panchanga_tithi_nakshatra_yoga_karana_vara_formulas() -> None:
    panch = compute_panchanga(
        sun_lon_deg=SAMPLE_LONS["Sun"],
        moon_lon_deg=SAMPLE_LONS["Moon"],
        jd_ut=2461319.5,
    )
    assert 1 <= panch.tithi.number <= 30
    assert 1 <= panch.nakshatra.number <= 27
    assert 1 <= panch.yoga.number <= 27
    assert 1 <= panch.karana.number <= 60


def test_documented_surya_siddhanta_and_vedanga_jyotisha_historical_engines() -> None:
    assert KALI_YUGA_EPOCH_JD == 588465.5
    assert MAHAYUGA_SAVANA_DAYS == 1_577_917_828
    siddhanta = surya_siddhanta_true_positions(2461319.5)
    assert len(siddhanta.receipt_sha256) == 64
    assert set(siddhanta.planets.keys()) == {
        "sun",
        "moon",
        "mars",
        "mercury",
        "jupiter",
        "venus",
        "saturn",
        "rahu",
        "ketu",
    }
    vedanga = compute_vedanga_yuga_state(365.0)
    assert len(vedanga.receipt_sha256) == 64


def test_documented_ai_fact_sheet_3kb_budget_and_hallucination_verifier() -> None:
    lower_lons = {k.lower(): v for k, v in SAMPLE_LONS.items()}
    sheet = compile_ai_fact_sheet(
        lower_lons,
        SAMPLE_LAGNA_DEG,
        birth_jd_ut=2451545.0,
        query_jd_ut=2461319.5,
        latitude_deg=28.6139,
        max_bytes=3000,
    )
    assert len(sheet.json_str.encode("utf-8")) <= 3000
    assert len(sheet.receipt_sha256) == 64
    sun_sign = sheet.payload["bodies"]["sun"]["sign"]
    wrong_sign = "Taurus" if sun_sign != "Taurus" else "Gemini"
    assert verify_ai_interpretation(f"Sun is placed in {sun_sign}.", sheet).passed is True
    assert verify_ai_interpretation(f"Sun is placed in {wrong_sign}.", sheet).passed is False


def test_documented_complete_kundali_bundle_almanac_and_svg_renderers() -> None:
    instant = datetime(2026, 10, 6, 12, 0, tzinfo=timezone.utc)
    with EphemerisAdapter(kernels="compact") as adapter:
        bundle = adapter.compute_complete_kundali_bundle(
            instant,
            latitude_deg=28.6139,
            longitude_deg=77.2090,
            ayanamsa="lahiri",
        )
        assert len(bundle.receipt_sha256) == 64

    panchang = generate_monthly_panchang(2026, 10, latitude_deg=28.6139, longitude_deg=77.2090)
    table = generate_ephemeris_table(2461319.5, 2461322.5, step_days=1.0)
    timeline = scan_ingresses_and_aspects(2461319.5, 2461325.5)
    cap_lons = {k.capitalize(): v.longitude_deg for k, v in bundle.positions.items()}
    for renderer in (
        render_north_indian_svg,
        render_south_indian_svg,
        render_east_indian_svg,
        render_circular_wheel_svg,
    ):
        svg_art = renderer(cap_lons, bundle.houses.ascendant_deg)
        assert "<svg" in svg_art.svg
        assert len(svg_art.receipt_sha256) == 64
    assert len(panchang.receipt_sha256) == 64
    assert len(table.receipt_sha256) == 64
    assert len(timeline.receipt_sha256) == 64


def test_documented_cli_subcommands_execute_cleanly(capsys) -> None:
    rc_chart = cli.main(["chart", "--at", "2026-10-06T12:00:00Z", "--compact", "--json"])
    assert rc_chart == 0
    chart_out = json.loads(capsys.readouterr().out)
    assert len(chart_out["receipt_sha256"]) == 64

    rc_siddhanta = cli.main(["siddhanta", "--at", "2026-10-06T12:00:00Z", "--json"])
    assert rc_siddhanta == 0
    siddhanta_out = json.loads(capsys.readouterr().out)
    assert len(siddhanta_out["receipt_sha256"]) == 64

    rc_table = cli.main(
        [
            "table",
            "--start",
            "2026-10-06T00:00:00Z",
            "--end",
            "2026-10-08T00:00:00Z",
            "--format",
            "json",
        ]
    )
    assert rc_table == 0
    table_out = json.loads(capsys.readouterr().out)
    assert len(table_out["receipt_sha256"]) == 64
