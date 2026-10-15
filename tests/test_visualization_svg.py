"""Tests for pure-Python SVG Kundali and Chakra renderers (`ephemeris_oss.visualization`)."""

from __future__ import annotations

import xml.etree.ElementTree as ET
import pytest

from ephemeris_oss.visualization import (
    SOUTH_INDIAN_SIGN_CELLS,
    SUPPORTED_THEMES,
    SvgChartArtifact,
    render_circular_wheel_svg,
    render_east_indian_svg,
    render_north_indian_svg,
    render_sarvatobhadra_svg,
    render_south_indian_svg,
)

SVG_NS = "{http://www.w3.org/2000/svg}"

SAMPLE_LONGITUDES: dict[str, float] = {
    "Sun": 12.5,        # Aries 12 deg 30 min
    "Moon": 45.25,      # Taurus 15 deg 15 min
    "Mars": 102.0,      # Cancer 12 deg 00 min
    "Mercury": 8.2,     # Aries 08 deg 12 min
    "Jupiter": 132.5,   # Leo 12 deg 30 min
    "Venus": 350.0,     # Pisces 20 deg 00 min
    "Saturn": 195.0,    # Libra 15 deg 00 min
    "Rahu": 72.0,       # Gemini 12 deg 00 min
    "Ketu": 252.0,      # Sagittarius 12 deg 00 min
}

SAMPLE_ASCENDANT_DEG = 105.5  # Cancer (sign index 3, sign number 4) 15 deg 30 min


def _assert_valid_svg(artifact: SvgChartArtifact) -> ET.Element:
    assert isinstance(artifact, SvgChartArtifact)
    assert artifact.svg.startswith('<svg xmlns="http://www.w3.org/2000/svg"')
    assert artifact.svg.endswith("</svg>")
    assert len(artifact.receipt_sha256) == 64
    root = ET.fromstring(artifact.svg)
    assert root.tag == f"{SVG_NS}svg"
    assert root.attrib["viewBox"] == f"0 0 {artifact.width} {artifact.height}"
    assert int(root.attrib["width"]) == artifact.width
    assert int(root.attrib["height"]) == artifact.height
    return root


@pytest.mark.parametrize("theme", SUPPORTED_THEMES)
def test_north_indian_svg_valid_xml_and_themes(theme: str) -> None:
    artifact = render_north_indian_svg(
        SAMPLE_LONGITUDES,
        SAMPLE_ASCENDANT_DEG,
        varga="D1",
        title="Natal Rasi Kundali",
        theme=theme,
        retrograde_planets={"Saturn", "Rahu", "Ketu"},
        combust_planets={"Mercury"},
    )
    root = _assert_valid_svg(artifact)
    assert artifact.chart_style == "north_indian"
    assert artifact.varga == "D1"
    assert artifact.theme == theme
    assert root.attrib["data-theme"] == theme
    assert "Su 12\u00b030'" in artifact.svg
    assert "Sa(R) 15\u00b000'" in artifact.svg
    assert "Me(C) 08\u00b012'" in artifact.svg


def test_north_indian_house_sign_counter_clockwise_rotation() -> None:
    # Cancer Ascendant (sign_index = 3 -> sign number 4 in House 1)
    artifact = render_north_indian_svg(SAMPLE_LONGITUDES, 105.5, varga="D1")
    root = _assert_valid_svg(artifact)
    house_Group = root.find(f".//{SVG_NS}g[@id='house-signs']")
    assert house_Group is not None
    sign_by_house: dict[int, int] = {}
    for elem in house_Group.findall(f"{SVG_NS}text"):
        h_num = int(elem.attrib["data-house"])
        s_num = int(elem.attrib["data-sign"])
        assert elem.text == str(s_num)
        sign_by_house[h_num] = s_num

    assert len(sign_by_house) == 12
    assert sign_by_house[1] == 4   # Cancer in House 1
    assert sign_by_house[2] == 5   # Leo in House 2
    assert sign_by_house[4] == 7   # Libra in House 4
    assert sign_by_house[7] == 10  # Capricorn in House 7
    assert sign_by_house[10] == 1  # Aries in House 10
    assert sign_by_house[12] == 3  # Gemini in House 12


@pytest.mark.parametrize("varga", ["D1", "D2", "D3", "D9", "D10", "D12", "D60"])
def test_north_indian_across_divisional_charts(varga: str) -> None:
    artifact = render_north_indian_svg(
        SAMPLE_LONGITUDES,
        SAMPLE_ASCENDANT_DEG,
        varga=varga,
        title=f"North Indian {varga}",
        theme="obsidian",
    )
    root = _assert_valid_svg(artifact)
    assert artifact.varga == varga
    assert root.attrib["data-varga"] == varga
    planet_group = root.find(f".//{SVG_NS}g[@id='house-planets']")
    assert planet_group is not None
    rendered_planets = {el.attrib["data-planet"] for el in planet_group.findall(f"{SVG_NS}text")}
    assert rendered_planets == set(SAMPLE_LONGITUDES.keys())


def test_north_indian_stellium_non_overlapping_coordinates() -> None:
    # Place all 9 planets in the same sign to stress-test multi-column house stacking
    stellium = {p: 10.0 + idx * 1.5 for idx, p in enumerate(SAMPLE_LONGITUDES)}
    artifact = render_north_indian_svg(stellium, 15.0, varga="D1")
    root = _assert_valid_svg(artifact)
    planet_group = root.find(f".//{SVG_NS}g[@id='house-planets']")
    assert planet_group is not None
    coords = {
        (float(el.attrib["x"]), float(el.attrib["y"]))
        for el in planet_group.findall(f"{SVG_NS}text")
    }
    assert len(coords) == 9


@pytest.mark.parametrize("theme", SUPPORTED_THEMES)
@pytest.mark.parametrize("varga", ["D1", "D9", "D10", "D60"])
def test_south_indian_svg_valid_xml_themes_and_vargas(theme: str, varga: str) -> None:
    artifact = render_south_indian_svg(
        SAMPLE_LONGITUDES,
        SAMPLE_ASCENDANT_DEG,
        varga=varga,
        title=f"South Indian {varga}",
        theme=theme,
        retrograde_planets=["Saturn"],
        combust_planets=["Mercury"],
    )
    root = _assert_valid_svg(artifact)
    assert artifact.chart_style == "south_indian"
    assert artifact.varga == varga
    assert artifact.theme == theme
    # Verify all 12 perimeter sign cells and double diagonal Ascendant marker
    sign_rects = root.findall(f".//{SVG_NS}rect[@data-sign]")
    assert len(sign_rects) == 12
    slash1 = root.find(f".//{SVG_NS}line[@data-marker='ascendant-slash-1']")
    slash2 = root.find(f".//{SVG_NS}line[@data-marker='ascendant-slash-2']")
    assert slash1 is not None
    assert slash2 is not None


def test_south_indian_fixed_sign_grid_layout() -> None:
    assert SOUTH_INDIAN_SIGN_CELLS[11] == (0, 0)  # Pisces at top-left
    assert SOUTH_INDIAN_SIGN_CELLS[0] == (0, 1)   # Aries at (0, 1)
    assert SOUTH_INDIAN_SIGN_CELLS[1] == (0, 2)   # Taurus at (0, 2)
    assert SOUTH_INDIAN_SIGN_CELLS[2] == (0, 3)   # Gemini at top-right
    assert SOUTH_INDIAN_SIGN_CELLS[5] == (3, 3)   # Virgo at bottom-right
    assert SOUTH_INDIAN_SIGN_CELLS[8] == (3, 0)   # Sagittarius at bottom-left


@pytest.mark.parametrize("theme", SUPPORTED_THEMES)
@pytest.mark.parametrize("varga", ["D1", "D9", "D10", "D60"])
def test_east_indian_svg_valid_xml_themes_and_vargas(theme: str, varga: str) -> None:
    artifact = render_east_indian_svg(
        SAMPLE_LONGITUDES,
        SAMPLE_ASCENDANT_DEG,
        varga=varga,
        title=f"East Indian {varga}",
        theme=theme,
        retrograde_planets={"Saturn": True, "Mars": False},
        combust_planets={"Mercury": True},
    )
    root = _assert_valid_svg(artifact)
    assert artifact.chart_style == "east_indian"
    assert artifact.varga == varga
    assert artifact.theme == theme
    group = root.find(f".//{SVG_NS}g[@id='east-indian-signs-and-planets']")
    assert group is not None
    sign_headers = [
        el for el in group.findall(f"{SVG_NS}text") if "data-planet" not in el.attrib
    ]
    assert len(sign_headers) == 12
    planet_texts = [
        el for el in group.findall(f"{SVG_NS}text") if "data-planet" in el.attrib
    ]
    assert len(planet_texts) == len(SAMPLE_LONGITUDES)


@pytest.mark.parametrize("theme", SUPPORTED_THEMES)
@pytest.mark.parametrize("show_aspects", [True, False])
def test_circular_wheel_svg_rings_and_aspects(theme: str, show_aspects: bool) -> None:
    artifact = render_circular_wheel_svg(
        SAMPLE_LONGITUDES,
        SAMPLE_ASCENDANT_DEG,
        title="27-Nakshatra Sidereal Wheel",
        theme=theme,
        retrograde_planets={"Saturn"},
        show_aspects=show_aspects,
        width=640,
        height=640,
    )
    root = _assert_valid_svg(artifact)
    assert artifact.chart_style == "circular_wheel"
    assert artifact.width == 640
    assert artifact.height == 640

    # Verify 27 Nakshatra sectors
    nak_ring = root.find(f".//{SVG_NS}g[@id='nakshatra-ring']")
    assert nak_ring is not None
    nak_ticks = nak_ring.findall(f"{SVG_NS}line[@data-nakshatra-index]")
    assert len(nak_ticks) == 27

    # Verify 12 Rasi sectors
    rasi_ring = root.find(f".//{SVG_NS}g[@id='rasi-ring']")
    assert rasi_ring is not None
    rasi_ticks = rasi_ring.findall(f"{SVG_NS}line[@data-rasi-index]")
    assert len(rasi_ticks) == 12

    # Verify 12 Bhava house cusps
    bhava_ring = root.find(f".//{SVG_NS}g[@id='bhava-ring']")
    assert bhava_ring is not None
    cusp_lines = bhava_ring.findall(f"{SVG_NS}line[@data-house-cusp]")
    assert len(cusp_lines) == 12

    # Verify aspect chords group presence matches show_aspects
    aspect_group = root.find(f".//{SVG_NS}g[@id='aspect-chords']")
    if show_aspects:
        assert aspect_group is not None
        assert len(aspect_group.findall(f"{SVG_NS}line")) >= 1
    else:
        assert aspect_group is None


@pytest.mark.parametrize("theme", SUPPORTED_THEMES)
def test_sarvatobhadra_svg_81_cells_and_vedha_rays(theme: str) -> None:
    artifact = render_sarvatobhadra_svg(
        janma_nakshatra_index=3,  # Rohini
        transit_longitudes=SAMPLE_LONGITUDES,
        title="Sarvatobhadra 9x9 Transit Chakra",
        theme=theme,
        width=720,
        height=720,
    )
    root = _assert_valid_svg(artifact)
    assert artifact.chart_style == "sarvatobhadra_chakra"
    assert artifact.varga == "SBC-9x9"
    assert artifact.theme == theme

    cells_group = root.find(f".//{SVG_NS}g[@id='sarvatobhadra-cells']")
    assert cells_group is not None
    cell_rects = cells_group.findall(f"{SVG_NS}rect")
    assert len(cell_rects) == 81

    # Count cell types: 16 Vowel, 28 Nakshatra, 20 Consonant, 12 Rasi, 5 Tithi
    counts: dict[str, int] = {}
    for rect in cell_rects:
        ctype = rect.attrib["data-cell-type"]
        counts[ctype] = counts.get(ctype, 0) + 1
    assert counts == {
        "Vowel": 16,
        "Nakshatra": 28,
        "Consonant": 20,
        "Rasi": 12,
        "Tithi": 5,
    }

    # Verify active Vedha rays are drawn when transit_longitudes are provided
    vedha_group = root.find(f".//{SVG_NS}g[@id='sarvatobhadra-vedha-rays']")
    assert vedha_group is not None
    vedha_lines = vedha_group.findall(f"{SVG_NS}line")
    assert len(vedha_lines) == len(SAMPLE_LONGITUDES) * 3


def test_sarvatobhadra_svg_without_transits_omits_vedha_group() -> None:
    artifact = render_sarvatobhadra_svg(janma_nakshatra_index=0, transit_longitudes=None)
    root = _assert_valid_svg(artifact)
    vedha_group = root.find(f".//{SVG_NS}g[@id='sarvatobhadra-vedha-rays']")
    assert vedha_group is None


def test_deterministic_receipt_sha256_and_input_sensitivity() -> None:
    a1 = render_north_indian_svg(SAMPLE_LONGITUDES, SAMPLE_ASCENDANT_DEG, varga="D9", theme="obsidian")
    a2 = render_north_indian_svg(dict(reversed(list(SAMPLE_LONGITUDES.items()))), SAMPLE_ASCENDANT_DEG, varga="D9", theme="obsidian")
    assert a1.receipt_sha256 == a2.receipt_sha256
    assert a1.svg == a2.svg

    # Changing varga, theme, or longitude changes the receipt_sha256
    a_d10 = render_north_indian_svg(SAMPLE_LONGITUDES, SAMPLE_ASCENDANT_DEG, varga="D10", theme="obsidian")
    a_parchment = render_north_indian_svg(SAMPLE_LONGITUDES, SAMPLE_ASCENDANT_DEG, varga="D9", theme="parchment")
    modified_lons = dict(SAMPLE_LONGITUDES, Sun=14.0)
    a_mod = render_north_indian_svg(modified_lons, SAMPLE_ASCENDANT_DEG, varga="D9", theme="obsidian")

    assert len({a1.receipt_sha256, a_d10.receipt_sha256, a_parchment.receipt_sha256, a_mod.receipt_sha256}) == 4
    assert a1.to_dict()["receipt_sha256"] == a1.receipt_sha256


def test_combined_retrograde_and_combust_badge() -> None:
    artifact = render_south_indian_svg(
        {"Mercury": 21.5},
        ascendant_lon_deg=0.0,
        retrograde_planets={"Me"},
        combust_planets={"Mercury"},
    )
    _assert_valid_svg(artifact)
    assert "Me(R,C) 21\u00b030'" in artifact.svg


def test_validation_errors_on_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="Unsupported theme"):
        render_north_indian_svg(SAMPLE_LONGITUDES, 0.0, theme="neon")

    with pytest.raises(ValueError, match="width and height"):
        render_south_indian_svg(SAMPLE_LONGITUDES, 0.0, width=120, height=120)

    with pytest.raises(ValueError, match="Unsupported varga"):
        render_east_indian_svg(SAMPLE_LONGITUDES, 0.0, varga="D999")

    with pytest.raises(ValueError, match="janma_nakshatra_index"):
        render_sarvatobhadra_svg(janma_nakshatra_index=40)
