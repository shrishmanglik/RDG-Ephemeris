"""Pure-Python, zero-dependency publication-grade SVG Kundali and Chakra renderer.

Generates deterministic, standards-compliant SVG charts for Vedic and positional
astronomy applications:
- North Indian Diamond Kundali (`render_north_indian_svg`) across D1..D144 vargas.
- South Indian Fixed-Sign 4x4 Kundali (`render_south_indian_svg`) with double-slash
  Ascendant marker and central panchang/varga summary panel.
- East Indian 3x3 Surya Chakra (`render_east_indian_svg`) with diagonally split
  corner cells progressing counter-clockwise from Aries at top-center.
- Concentric Sidereal Zodiac & 27-Nakshatra Wheel (`render_circular_wheel_svg`)
  with 108 pada ticks, 12 Rasi sectors, 12 Bhava cusps, collision-resolved planet
  markers, and geometric/Parashari aspect chords.
- 81-Cell (9x9) Sarvatobhadra Chakra (`render_sarvatobhadra_svg`) with color-coded
  Vowel, Nakshatra, Consonant, Rasi, and Tithi rings plus active transit Vedha rays.
"""

from __future__ import annotations

import html
import math
from dataclasses import dataclass
from typing import Any, Final, Iterable, Mapping

from .._version import __version__
from ..engine.receipt import canonical_hash
from ..jyotish.nakshatra import (
    NAKSHATRA_CATALOG,
    NAKSHATRA_SPAN_DEG,
    PADA_SPAN_DEG,
    RASI_NAMES,
    abhijit_position,
    nakshatra_position,
    normalize_degrees,
)
from ..jyotish.vargas import RASI_LORDS, varga_sign
from ..jyotish_transit.chakras import (
    NATURAL_BENEFICS,
    SARVATOBHADRA_28_NAKSHATRAS,
    SarvatobhadraCell,
    build_sarvatobhadra_grid,
    compute_sarvatobhadra_vedha,
)

SUPPORTED_THEMES: Final[tuple[str, ...]] = ("obsidian", "parchment")

PLANET_CODES: Final[Mapping[str, str]] = {
    "Sun": "Su",
    "Moon": "Mo",
    "Mars": "Ma",
    "Mercury": "Me",
    "Jupiter": "Ju",
    "Venus": "Ve",
    "Saturn": "Sa",
    "Rahu": "Ra",
    "Ketu": "Ke",
    "Uranus": "Ur",
    "Neptune": "Ne",
    "Pluto": "Pl",
    "Ascendant": "As",
    "Lagna": "As",
}

CANONICAL_PLANET_ORDER: Final[tuple[str, ...]] = (
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
    "Rahu",
    "Ketu",
)

RASI_ENGLISH_SHORT: Final[tuple[str, ...]] = (
    "Ari",
    "Tau",
    "Gem",
    "Can",
    "Leo",
    "Vir",
    "Lib",
    "Sco",
    "Sag",
    "Cap",
    "Aqu",
    "Pis",
)


@dataclass(frozen=True)
class ThemePalette:
    """Color palette for sacred-geometry SVG chart rendering."""

    name: str
    bg_primary: str
    bg_secondary: str
    bg_panel: str
    stroke_outer: str
    stroke_primary: str
    stroke_secondary: str
    stroke_muted: str
    text_title: str
    text_subtitle: str
    text_primary: str
    text_muted: str
    sign_numeral: str
    asc_accent: str
    benefic_color: str
    malefic_color: str
    retrograde_color: str
    combust_color: str
    aspect_conjunction: str
    aspect_trine: str
    aspect_sextile: str
    aspect_square: str
    aspect_opposition: str
    sbc_vowel_fill: str
    sbc_nakshatra_fill: str
    sbc_consonant_fill: str
    sbc_rasi_fill: str
    sbc_tithi_fill: str
    sbc_janma_fill: str
    sbc_janma_stroke: str


THEME_PALETTES: Final[Mapping[str, ThemePalette]] = {
    "obsidian": ThemePalette(
        name="obsidian",
        bg_primary="#090D16",
        bg_secondary="#0F172A",
        bg_panel="#131C31",
        stroke_outer="#D4AF37",
        stroke_primary="#C59B27",
        stroke_secondary="#475569",
        stroke_muted="#1E293B",
        text_title="#F8FAFC",
        text_subtitle="#CBD5E1",
        text_primary="#F1F5F9",
        text_muted="#94A3B8",
        sign_numeral="#F59E0B",
        asc_accent="#38BDF8",
        benefic_color="#34D399",
        malefic_color="#F87171",
        retrograde_color="#38BDF8",
        combust_color="#FB923C",
        aspect_conjunction="#FBBF24",
        aspect_trine="#34D399",
        aspect_sextile="#38BDF8",
        aspect_square="#F87171",
        aspect_opposition="#C084FC",
        sbc_vowel_fill="#1E1B4B",
        sbc_nakshatra_fill="#0F172A",
        sbc_consonant_fill="#111827",
        sbc_rasi_fill="#172554",
        sbc_tithi_fill="#31102F",
        sbc_janma_fill="#422006",
        sbc_janma_stroke="#F59E0B",
    ),
    "parchment": ThemePalette(
        name="parchment",
        bg_primary="#FCF9F2",
        bg_secondary="#F4EFE4",
        bg_panel="#EFE7D6",
        stroke_outer="#8B4513",
        stroke_primary="#A0522D",
        stroke_secondary="#A89F91",
        stroke_muted="#D6CFC2",
        text_title="#1C1917",
        text_subtitle="#57534E",
        text_primary="#292524",
        text_muted="#78716C",
        sign_numeral="#B45309",
        asc_accent="#0369A1",
        benefic_color="#15803D",
        malefic_color="#B91C1C",
        retrograde_color="#1D4ED8",
        combust_color="#C2410C",
        aspect_conjunction="#B45309",
        aspect_trine="#15803D",
        aspect_sextile="#0369A1",
        aspect_square="#B91C1C",
        aspect_opposition="#6D28D9",
        sbc_vowel_fill="#F3E8FF",
        sbc_nakshatra_fill="#F5EFE6",
        sbc_consonant_fill="#FAF7F0",
        sbc_rasi_fill="#E0F2FE",
        sbc_tithi_fill="#FCE7F3",
        sbc_janma_fill="#FEF3C7",
        sbc_janma_stroke="#D97706",
    ),
}


@dataclass(frozen=True)
class SvgChartArtifact:
    """Deterministic SVG chart artifact with cryptographic receipt hash."""

    svg: str
    chart_style: str
    varga: str
    theme: str
    width: int
    height: int
    receipt_sha256: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dictionary of the SVG artifact."""
        return {
            "svg": self.svg,
            "chart_style": self.chart_style,
            "varga": self.varga,
            "theme": self.theme,
            "width": self.width,
            "height": self.height,
            "receipt_sha256": self.receipt_sha256,
        }


def _resolve_theme(theme: str) -> ThemePalette:
    key = theme.strip().lower()
    if key not in THEME_PALETTES:
        raise ValueError(f"Unsupported theme {theme!r}; choose from {SUPPORTED_THEMES}")
    return THEME_PALETTES[key]


def _validate_dimensions(width: int, height: int) -> tuple[int, int]:
    w = int(width)
    h = int(height)
    if w < 200 or h < 200:
        raise ValueError(f"width and height must be >= 200; got ({w}, {h})")
    return w, h


def _normalize_planet_flag_set(
    flags: Iterable[str] | Mapping[str, bool] | None,
) -> frozenset[str]:
    if flags is None:
        return frozenset()
    if isinstance(flags, Mapping):
        raw_items = [k for k, v in flags.items() if v]
    else:
        raw_items = list(flags)
    normalized: set[str] = set()
    code_to_name = {code.lower(): name for name, code in PLANET_CODES.items()}
    for item in raw_items:
        clean = str(item).strip()
        if not clean:
            continue
        cap = clean.capitalize()
        normalized.add(cap)
        normalized.add(clean.upper())
        if clean.lower() in code_to_name:
            normalized.add(code_to_name[clean.lower()])
        if cap in PLANET_CODES:
            normalized.add(PLANET_CODES[cap])
    return frozenset(normalized)


def _planet_code(planet_name: str) -> str:
    clean = planet_name.strip()
    cap = clean.capitalize()
    if cap in PLANET_CODES:
        return PLANET_CODES[cap]
    return clean[:2].capitalize() if len(clean) >= 2 else clean.upper()


def _format_deg_min(deg_in_sign: float) -> str:
    clamped = max(0.0, min(float(deg_in_sign), 29.999999))
    total_arcmin = int(round(clamped * 60.0))
    if total_arcmin >= 1800:
        total_arcmin = 1799
    deg = total_arcmin // 60
    arcmin = total_arcmin % 60
    return f"{deg:02d}\u00b0{arcmin:02d}'"


def _format_planet_label(
    planet_name: str,
    lon_deg: float,
    retro_set: frozenset[str],
    combust_set: frozenset[str],
    *,
    include_degrees: bool = True,
) -> str:
    code = _planet_code(planet_name)
    cap = planet_name.strip().capitalize()
    is_retro = (cap in retro_set) or (code in retro_set) or (planet_name.strip().upper() in retro_set)
    is_combust = (cap in combust_set) or (code in combust_set) or (planet_name.strip().upper() in combust_set)

    status = ""
    if is_retro and is_combust:
        status = "(R,C)"
    elif is_retro:
        status = "(R)"
    elif is_combust:
        status = "(C)"

    if not include_degrees:
        return f"{code}{status}"

    deg_in_sign = normalize_degrees(lon_deg) % 30.0
    return f"{code}{status} {_format_deg_min(deg_in_sign)}"


def _sorted_planet_items(planet_longitudes: Mapping[str, float]) -> list[tuple[str, float]]:
    order_Index = {name: idx for idx, name in enumerate(CANONICAL_PLANET_ORDER)}

    def _sort_key(item: tuple[str, float]) -> tuple[int, str]:
        cap = item[0].strip().capitalize()
        return (order_Index.get(cap, 999), cap)

    return sorted(
        ((str(k).strip(), normalize_degrees(float(v))) for k, v in planet_longitudes.items()),
        key=_sort_key,
    )


def _planet_color(
    planet_name: str,
    palette: ThemePalette,
    retro_set: frozenset[str],
    combust_set: frozenset[str],
) -> str:
    cap = planet_name.strip().capitalize()
    code = _planet_code(planet_name)
    if cap in combust_set or code in combust_set:
        return palette.combust_color
    if cap in retro_set or code in retro_set:
        return palette.retrograde_color
    if cap in NATURAL_BENEFICS:
        return palette.benefic_color
    return palette.text_primary


def _compute_artifact_receipt(
    chart_style: str,
    varga: str,
    theme: str,
    width: int,
    height: int,
    title: str,
    payload: Mapping[str, Any],
) -> str:
    return canonical_hash(
        {
            "module": "ephemeris_oss.visualization.kundali_svg",
            "version": __version__,
            "chart_style": chart_style,
            "varga": varga,
            "theme": theme,
            "width": width,
            "height": height,
            "title": title,
            "payload": payload,
        }
    )


def _xml_text(text: str) -> str:
    return html.escape(str(text), quote=False)


def _xml_attr(text: str) -> str:
    return html.escape(str(text), quote=True)


def _svg_header(
    width: int,
    height: int,
    palette: ThemePalette,
    chart_style: str,
    varga: str,
    title: str,
) -> list[str]:
    esc_title_attr = _xml_attr(title)
    esc_title_text = _xml_text(title)
    esc_style = _xml_attr(chart_style)
    esc_varga = _xml_attr(varga)
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" '
        f'data-chart-style="{esc_style}" data-varga="{esc_varga}" data-theme="{palette.name}" '
        f'role="img" aria-label="{esc_title_attr}">',
        f"  <title>{esc_title_text}</title>",
        "  <defs>",
        f'    <linearGradient id="bg-grad-{palette.name}" x1="0%" y1="0%" x2="100%" y2="100%">',
        f'      <stop offset="0%" stop-color="{palette.bg_primary}"/>',
        f'      <stop offset="100%" stop-color="{palette.bg_secondary}"/>',
        "    </linearGradient>",
        "  </defs>",
        f'  <rect x="0" y="0" width="{width}" height="{height}" fill="url(#bg-grad-{palette.name})" rx="8"/>',
        f'  <rect x="4" y="4" width="{width - 8}" height="{height - 8}" fill="none" '
        f'stroke="{palette.stroke_outer}" stroke-width="1.2" stroke-opacity="0.55" rx="6"/>',
    ]


def render_north_indian_svg(
    planet_longitudes: Mapping[str, float],
    ascendant_lon_deg: float,
    *,
    varga: str = "D1",
    title: str = "Rasi Chart (D1)",
    theme: str = "obsidian",
    retrograde_planets: Iterable[str] | Mapping[str, bool] | None = None,
    combust_planets: Iterable[str] | Mapping[str, bool] | None = None,
    width: int = 600,
    height: int = 600,
) -> SvgChartArtifact:
    """Render a traditional North Indian diamond Kundali SVG for D1 or any Varga (D1..D144)."""
    w, h = _validate_dimensions(width, height)
    palette = _resolve_theme(theme)
    varga_code = varga.strip().upper()
    retro_set = _normalize_planet_flag_set(retrograde_planets)
    combust_set = _normalize_planet_flag_set(combust_planets)

    asc_lon = normalize_degrees(ascendant_lon_deg)
    asc_varga = varga_sign(asc_lon, varga_code)
    asc_sign_idx = asc_varga.sign_index
    asc_nak = nakshatra_position(asc_lon)

    sorted_planets = _sorted_planet_items(planet_longitudes)
    house_planets: dict[int, list[tuple[str, str, str]]] = {bhava: [] for bhava in range(1, 13)}
    planet_sign_receipt: dict[str, int] = {}

    for p_name, p_lon in sorted_planets:
        vp = varga_sign(p_lon, varga_code)
        planet_sign_receipt[p_name] = vp.sign_index
        bhava_num = ((vp.sign_index - asc_sign_idx) % 12) + 1
        label = _format_planet_label(p_name, p_lon, retro_set, combust_set, include_degrees=True)
        color = _planet_color(p_name, palette, retro_set, combust_set)
        house_planets[bhava_num].append((p_name, label, color))

    # Chart square geometry
    header_h = 54.0
    footer_h = 26.0
    avail_w = w - 48.0
    avail_h = h - header_h - footer_h - 16.0
    side = min(avail_w, avail_h)
    x0 = (w - side) / 2.0
    y0 = header_h + (avail_h - side) / 2.0
    x1 = x0 + side
    y1 = y0 + side
    cx = x0 + side * 0.5
    cy = y0 + side * 0.5
    q1x = x0 + side * 0.25
    q3x = x0 + side * 0.75
    q1y = y0 + side * 0.25
    q3y = y0 + side * 0.75

    lines = _svg_header(w, h, palette, "north_indian", varga_code, title)

    # Title and subtitle banner
    esc_title = _xml_text(title)
    subtitle = (
        f"Varga: {varga_code} | Lagna: {RASI_NAMES[asc_sign_idx]} {_format_deg_min(asc_lon % 30.0)} "
        f"({asc_nak.name} Pada {asc_nak.pada})"
    )
    lines.append(
        f'  <text x="{w / 2.0:.1f}" y="26" text-anchor="middle" fill="{palette.text_title}" '
        f'font-family="Georgia, serif" font-size="16" font-weight="bold">{esc_title}</text>'
    )
    lines.append(
        f'  <text x="{w / 2.0:.1f}" y="44" text-anchor="middle" fill="{palette.text_subtitle}" '
        f'font-family="monospace" font-size="11">{_xml_text(subtitle)}</text>'
    )

    # Outer square, midpoint diamond, and 2 main diagonals
    lines.append('  <g id="kundali-geometry">')
    lines.append(
        f'    <rect x="{x0:.2f}" y="{y0:.2f}" width="{side:.2f}" height="{side:.2f}" '
        f'fill="{palette.bg_panel}" stroke="{palette.stroke_outer}" stroke-width="2.2"/>'
    )
    lines.append(
        f'    <polygon points="{cx:.2f},{y0:.2f} {x1:.2f},{cy:.2f} {cx:.2f},{y1:.2f} {x0:.2f},{cy:.2f}" '
        f'fill="none" stroke="{palette.stroke_primary}" stroke-width="1.8"/>'
    )
    lines.append(
        f'    <line x1="{x0:.2f}" y1="{y0:.2f}" x2="{x1:.2f}" y2="{y1:.2f}" '
        f'stroke="{palette.stroke_primary}" stroke-width="1.5"/>'
    )
    lines.append(
        f'    <line x1="{x1:.2f}" y1="{y0:.2f}" x2="{x0:.2f}" y2="{y1:.2f}" '
        f'stroke="{palette.stroke_primary}" stroke-width="1.5"/>'
    )
    lines.append("  </g>")

    # Sign numeral anchor coordinates (1..12 counter-clockwise)
    sign_anchors: dict[int, tuple[float, float]] = {
        1: (cx, cy - side * 0.06),
        2: (q1x, q1y - side * 0.05),
        3: (q1x - side * 0.06, q1y + side * 0.01),
        4: (cx - side * 0.06, cy + side * 0.01),
        5: (q1x - side * 0.06, q3y + side * 0.01),
        6: (q1x, q3y + side * 0.07),
        7: (cx, cy + side * 0.08),
        8: (q3x, q3y + side * 0.07),
        9: (q3x + side * 0.06, q3y + side * 0.01),
        10: (cx + side * 0.06, cy + side * 0.01),
        11: (q3x + side * 0.06, q1y + side * 0.01),
        12: (q3x, q1y - side * 0.05),
    }

    # Planet text box centroids for each of the 12 houses
    planet_centroids: dict[int, tuple[float, float]] = {
        1: (cx, y0 + side * 0.24),
        2: (x0 + side * 0.25, y0 + side * 0.09),
        3: (x0 + side * 0.09, y0 + side * 0.25),
        4: (x0 + side * 0.24, cy),
        5: (x0 + side * 0.09, y0 + side * 0.75),
        6: (x0 + side * 0.25, y0 + side * 0.91),
        7: (cx, y0 + side * 0.76),
        8: (x0 + side * 0.75, y0 + side * 0.91),
        9: (x0 + side * 0.91, y0 + side * 0.75),
        10: (x0 + side * 0.76, cy),
        11: (x0 + side * 0.91, y0 + side * 0.25),
        12: (x0 + side * 0.75, y0 + side * 0.09),
    }

    # Render Sign Numbers (1..12) in each house
    lines.append('  <g id="house-signs" font-family="monospace" font-size="11" font-weight="bold">')
    for bhava in range(1, 13):
        sign_num = ((asc_sign_idx + bhava - 1) % 12) + 1
        sx, sy = sign_anchors[bhava]
        lines.append(
            f'    <text x="{sx:.2f}" y="{sy:.2f}" text-anchor="middle" '
            f'data-house="{bhava}" data-sign="{sign_num}" fill="{palette.sign_numeral}">{sign_num}</text>'
        )
    lines.append("  </g>")

    # Lagna label in House 1
    lines.append(
        f'  <text x="{cx:.2f}" y="{y0 + side * 0.08:.2f}" text-anchor="middle" '
        f'font-family="monospace" font-size="10" font-weight="bold" fill="{palette.asc_accent}">'
        f"As {_format_deg_min(asc_lon % 30.0)}</text>"
    )

    # Render Planets inside each house without overlapping
    lines.append('  <g id="house-planets" font-family="monospace">')
    for bhava in range(1, 13):
        p_list = house_planets[bhava]
        if not p_list:
            continue
        px, py = planet_centroids[bhava]
        count = len(p_list)
        is_diamond = bhava in (1, 4, 7, 10)
        if count <= 3 and is_diamond:
            font_sz = 10.5
            line_step = 13.0
            start_y = py - ((count - 1) * line_step) / 2.0
            for idx, (p_name, p_label, p_color) in enumerate(p_list):
                yy = start_y + idx * line_step
                lines.append(
                    f'    <text x="{px:.2f}" y="{yy:.2f}" text-anchor="middle" '
                    f'font-size="{font_sz:.1f}" font-weight="600" data-planet="{_xml_attr(p_name)}" '
                    f'data-house="{bhava}" fill="{p_color}">{_xml_text(p_label)}</text>'
                )
        else:
            # 2-column compact layout for triangular houses or high-occupancy houses
            font_sz = 8.5 if count > 4 else 9.2
            col_offset = side * 0.062 if is_diamond else side * 0.048
            row_step = 10.5 if count <= 4 else 9.0
            num_rows = (count + 1) // 2
            start_y = py - ((num_rows - 1) * row_step) / 2.0
            for idx, (p_name, p_label, p_color) in enumerate(p_list):
                row_i = idx // 2
                col_i = idx % 2
                if count == 1:
                    xx = px
                elif idx == count - 1 and count % 2 == 1:
                    xx = px
                else:
                    xx = px - col_offset if col_i == 0 else px + col_offset
                yy = start_y + row_i * row_step
                lines.append(
                    f'    <text x="{xx:.2f}" y="{yy:.2f}" text-anchor="middle" '
                    f'font-size="{font_sz:.1f}" font-weight="600" data-planet="{_xml_attr(p_name)}" '
                    f'data-house="{bhava}" fill="{p_color}">{_xml_text(p_label)}</text>'
                )
    lines.append("  </g>")

    receipt_sha = _compute_artifact_receipt(
        chart_style="north_indian",
        varga=varga_code,
        theme=palette.name,
        width=w,
        height=h,
        title=title,
        payload={
            "ascendant_lon_deg": round(asc_lon, 8),
            "asc_sign_index": asc_sign_idx,
            "planet_longitudes": {k: round(v, 8) for k, v in sorted_planets},
            "planet_varga_signs": planet_sign_receipt,
            "retrograde": sorted(retro_set),
            "combust": sorted(combust_set),
        },
    )
    lines.append(
        f'  <text x="{w / 2.0:.1f}" y="{h - 10:.1f}" text-anchor="middle" '
        f'font-family="monospace" font-size="9" fill="{palette.text_muted}">'
        f"North Indian {varga_code} | SHA256: {receipt_sha[:16]}</text>"
    )
    lines.append("</svg>")
    svg_text = "\n".join(lines)
    return SvgChartArtifact(
        svg=svg_text,
        chart_style="north_indian",
        varga=varga_code,
        theme=palette.name,
        width=w,
        height=h,
        receipt_sha256=receipt_sha,
    )


# Fixed 4x4 grid coordinates for the 12 signs (0=Aries .. 11=Pisces) in South Indian layout
SOUTH_INDIAN_SIGN_CELLS: Final[Mapping[int, tuple[int, int]]] = {
    11: (0, 0),  # Pisces (Meena) top-left
    0: (0, 1),   # Aries (Mesha)
    1: (0, 2),   # Taurus (Vrishabha)
    2: (0, 3),   # Gemini (Mithuna)
    3: (1, 3),   # Cancer (Karka)
    4: (2, 3),   # Leo (Simha)
    5: (3, 3),   # Virgo (Kanya)
    6: (3, 2),   # Libra (Tula)
    7: (3, 1),   # Scorpio (Vrishchika)
    8: (3, 0),   # Sagittarius (Dhanu)
    9: (2, 0),   # Capricorn (Makara)
    10: (1, 0),  # Aquarius (Kumbha)
}


def render_south_indian_svg(
    planet_longitudes: Mapping[str, float],
    ascendant_lon_deg: float,
    *,
    varga: str = "D1",
    title: str = "South Indian Kundali",
    theme: str = "obsidian",
    retrograde_planets: Iterable[str] | Mapping[str, bool] | None = None,
    combust_planets: Iterable[str] | Mapping[str, bool] | None = None,
    width: int = 600,
    height: int = 600,
) -> SvgChartArtifact:
    """Render a traditional 4x4 South Indian fixed-sign Kundali SVG."""
    w, h = _validate_dimensions(width, height)
    palette = _resolve_theme(theme)
    varga_code = varga.strip().upper()
    retro_set = _normalize_planet_flag_set(retrograde_planets)
    combust_set = _normalize_planet_flag_set(combust_planets)

    asc_lon = normalize_degrees(ascendant_lon_deg)
    asc_varga = varga_sign(asc_lon, varga_code)
    asc_sign_idx = asc_varga.sign_index
    asc_nak = nakshatra_position(asc_lon)

    sorted_planets = _sorted_planet_items(planet_longitudes)
    sign_planets: dict[int, list[tuple[str, str, str]]] = {s: [] for s in range(12)}
    planet_sign_receipt: dict[str, int] = {}

    for p_name, p_lon in sorted_planets:
        vp = varga_sign(p_lon, varga_code)
        planet_sign_receipt[p_name] = vp.sign_index
        label = _format_planet_label(p_name, p_lon, retro_set, combust_set, include_degrees=True)
        color = _planet_color(p_name, palette, retro_set, combust_set)
        sign_planets[vp.sign_index].append((p_name, label, color))

    pad_top = 42.0
    pad_bottom = 26.0
    avail_w = w - 48.0
    avail_h = h - pad_top - pad_bottom - 12.0
    side = min(avail_w, avail_h)
    x0 = (w - side) / 2.0
    y0 = pad_top + (avail_h - side) / 2.0
    cell_s = side / 4.0

    lines = _svg_header(w, h, palette, "south_indian", varga_code, title)
    lines.append(
        f'  <text x="{w / 2.0:.1f}" y="28" text-anchor="middle" fill="{palette.text_title}" '
        f'font-family="Georgia, serif" font-size="16" font-weight="bold">{_xml_text(title)}</text>'
    )

    lines.append('  <g id="south-indian-grid">')
    # Outer 4x4 frame
    lines.append(
        f'    <rect x="{x0:.2f}" y="{y0:.2f}" width="{side:.2f}" height="{side:.2f}" '
        f'fill="{palette.bg_panel}" stroke="{palette.stroke_outer}" stroke-width="2.2"/>'
    )

    # Render each of the 12 perimeter sign cells
    for sign_idx, (r, c) in SOUTH_INDIAN_SIGN_CELLS.items():
        cx0 = x0 + c * cell_s
        cy0 = y0 + r * cell_s
        bhava_num = ((sign_idx - asc_sign_idx) % 12) + 1
        lines.append(
            f'    <rect x="{cx0:.2f}" y="{cy0:.2f}" width="{cell_s:.2f}" height="{cell_s:.2f}" '
            f'fill="none" stroke="{palette.stroke_primary}" stroke-width="1.4" '
            f'data-sign="{sign_idx + 1}" data-rasi="{RASI_NAMES[sign_idx]}" data-house="{bhava_num}"/>'
        )
        # Sign label in top-left of cell and house number in top-right
        lines.append(
            f'    <text x="{cx0 + 6:.2f}" y="{cy0 + 14:.2f}" font-family="monospace" '
            f'font-size="9.5" font-weight="bold" fill="{palette.sign_numeral}">'
            f"{sign_idx + 1}:{RASI_NAMES[sign_idx][:3]}</text>"
        )
        lines.append(
            f'    <text x="{cx0 + cell_s - 6:.2f}" y="{cy0 + 14:.2f}" text-anchor="end" '
            f'font-family="monospace" font-size="9" fill="{palette.text_muted}">H{bhava_num}</text>'
        )

        # Traditional double diagonal slash in the Ascendant sign cell
        if sign_idx == asc_sign_idx:
            slash1_end = 22.0
            slash2_end = 28.0
            lines.append(
                f'    <line x1="{cx0:.2f}" y1="{cy0 + slash1_end:.2f}" '
                f'x2="{cx0 + slash1_end:.2f}" y2="{cy0:.2f}" '
                f'stroke="{palette.asc_accent}" stroke-width="2.0" data-marker="ascendant-slash-1"/>'
            )
            lines.append(
                f'    <line x1="{cx0:.2f}" y1="{cy0 + slash2_end:.2f}" '
                f'x2="{cx0 + slash2_end:.2f}" y2="{cy0:.2f}" '
                f'stroke="{palette.asc_accent}" stroke-width="2.0" data-marker="ascendant-slash-2"/>'
            )
            lines.append(
                f'    <text x="{cx0 + cell_s * 0.5:.2f}" y="{cy0 + 26:.2f}" text-anchor="middle" '
                f'font-family="monospace" font-size="9.5" font-weight="bold" fill="{palette.asc_accent}">'
                f"Asc {_format_deg_min(asc_lon % 30.0)}</text>"
            )

        # Render planets inside this sign cell
        p_list = sign_planets[sign_idx]
        if p_list:
            top_offset = 38.0 if sign_idx == asc_sign_idx else 28.0
            avail_cell_h = cell_s - top_offset - 6.0
            count = len(p_list)
            if count <= 4:
                step_y = min(14.5, avail_cell_h / max(count, 1))
                for idx, (p_name, p_label, p_color) in enumerate(p_list):
                    py = cy0 + top_offset + idx * step_y + 8.0
                    lines.append(
                        f'    <text x="{cx0 + cell_s * 0.5:.2f}" y="{py:.2f}" text-anchor="middle" '
                        f'font-family="monospace" font-size="9.8" font-weight="600" '
                        f'data-planet="{_xml_attr(p_name)}" fill="{p_color}">{_xml_text(p_label)}</text>'
                    )
            else:
                num_rows = (count + 1) // 2
                step_y = min(12.5, avail_cell_h / max(num_rows, 1))
                for idx, (p_name, p_label, p_color) in enumerate(p_list):
                    r_i = idx // 2
                    c_i = idx % 2
                    px = cx0 + (cell_s * 0.27 if c_i == 0 else cell_s * 0.73)
                    py = cy0 + top_offset + r_i * step_y + 7.0
                    lines.append(
                        f'    <text x="{px:.2f}" y="{py:.2f}" text-anchor="middle" '
                        f'font-family="monospace" font-size="8.2" font-weight="600" '
                        f'data-planet="{_xml_attr(p_name)}" fill="{p_color}">{_xml_text(p_label)}</text>'
                    )

    # 2x2 Center summary panel
    center_x = x0 + cell_s
    center_y = y0 + cell_s
    center_s = cell_s * 2.0
    lines.append(
        f'    <rect x="{center_x:.2f}" y="{center_y:.2f}" width="{center_s:.2f}" height="{center_s:.2f}" '
        f'fill="{palette.bg_primary}" stroke="{palette.stroke_outer}" stroke-width="1.8"/>'
    )
    mid_x = center_x + center_s * 0.5
    mid_y = center_y + center_s * 0.5
    lines.append(
        f'    <text x="{mid_x:.2f}" y="{mid_y - 36:.2f}" text-anchor="middle" '
        f'font-family="Georgia, serif" font-size="14" font-weight="bold" fill="{palette.text_title}">'
        f"{_xml_text(title)}</text>"
    )
    lines.append(
        f'    <text x="{mid_x:.2f}" y="{mid_y - 14:.2f}" text-anchor="middle" '
        f'font-family="monospace" font-size="11.5" font-weight="bold" fill="{palette.sign_numeral}">'
        f"Divisional Chart: {_xml_text(varga_code)}</text>"
    )
    lines.append(
        f'    <text x="{mid_x:.2f}" y="{mid_y + 10:.2f}" text-anchor="middle" '
        f'font-family="monospace" font-size="10.5" fill="{palette.asc_accent}">'
        f"Lagna: {RASI_NAMES[asc_sign_idx]} {_format_deg_min(asc_lon % 30.0)}</text>"
    )
    lines.append(
        f'    <text x="{mid_x:.2f}" y="{mid_y + 30:.2f}" text-anchor="middle" '
        f'font-family="monospace" font-size="10" fill="{palette.text_subtitle}">'
        f"Nakshatra: {asc_nak.name} (Pada {asc_nak.pada})</text>"
    )
    lines.append(
        f'    <text x="{mid_x:.2f}" y="{mid_y + 48:.2f}" text-anchor="middle" '
        f'font-family="monospace" font-size="9.5" fill="{palette.text_muted}">'
        f"Lord: {RASI_LORDS[asc_sign_idx]}</text>"
    )
    lines.append("  </g>")

    receipt_sha = _compute_artifact_receipt(
        chart_style="south_indian",
        varga=varga_code,
        theme=palette.name,
        width=w,
        height=h,
        title=title,
        payload={
            "ascendant_lon_deg": round(asc_lon, 8),
            "asc_sign_index": asc_sign_idx,
            "planet_longitudes": {k: round(v, 8) for k, v in sorted_planets},
            "planet_varga_signs": planet_sign_receipt,
            "retrograde": sorted(retro_set),
            "combust": sorted(combust_set),
        },
    )
    lines.append(
        f'  <text x="{w / 2.0:.1f}" y="{h - 10:.1f}" text-anchor="middle" '
        f'font-family="monospace" font-size="9" fill="{palette.text_muted}">'
        f"South Indian {varga_code} | SHA256: {receipt_sha[:16]}</text>"
    )
    lines.append("</svg>")
    return SvgChartArtifact(
        svg="\n".join(lines),
        chart_style="south_indian",
        varga=varga_code,
        theme=palette.name,
        width=w,
        height=h,
        receipt_sha256=receipt_sha,
    )


def render_east_indian_svg(
    planet_longitudes: Mapping[str, float],
    ascendant_lon_deg: float,
    *,
    varga: str = "D1",
    title: str = "East Indian Surya Chakra",
    theme: str = "obsidian",
    retrograde_planets: Iterable[str] | Mapping[str, bool] | None = None,
    combust_planets: Iterable[str] | Mapping[str, bool] | None = None,
    width: int = 600,
    height: int = 600,
) -> SvgChartArtifact:
    """Render a traditional 3x3 East Indian (Bengali/Odia/Maithili) Surya Chakra SVG.

    Aries sits in the top-center cell `(0,1)` and signs progress counter-clockwise,
    with the four corner cells split diagonally radiating from the central square.
    """
    w, h = _validate_dimensions(width, height)
    palette = _resolve_theme(theme)
    varga_code = varga.strip().upper()
    retro_set = _normalize_planet_flag_set(retrograde_planets)
    combust_set = _normalize_planet_flag_set(combust_planets)

    asc_lon = normalize_degrees(ascendant_lon_deg)
    asc_varga = varga_sign(asc_lon, varga_code)
    asc_sign_idx = asc_varga.sign_index
    asc_nak = nakshatra_position(asc_lon)

    sorted_planets = _sorted_planet_items(planet_longitudes)
    sign_planets: dict[int, list[tuple[str, str, str]]] = {s: [] for s in range(12)}
    planet_sign_receipt: dict[str, int] = {}

    for p_name, p_lon in sorted_planets:
        vp = varga_sign(p_lon, varga_code)
        planet_sign_receipt[p_name] = vp.sign_index
        label = _format_planet_label(p_name, p_lon, retro_set, combust_set, include_degrees=True)
        color = _planet_color(p_name, palette, retro_set, combust_set)
        sign_planets[vp.sign_index].append((p_name, label, color))

    pad_top = 42.0
    pad_bottom = 26.0
    avail_w = w - 48.0
    avail_h = h - pad_top - pad_bottom - 12.0
    side = min(avail_w, avail_h)
    x0 = (w - side) / 2.0
    y0 = pad_top + (avail_h - side) / 2.0
    x1 = x0 + side
    y1 = y0 + side
    c_len = side / 3.0
    gx1 = x0 + c_len
    gx2 = x0 + 2.0 * c_len
    gy1 = y0 + c_len
    gy2 = y0 + 2.0 * c_len

    lines = _svg_header(w, h, palette, "east_indian", varga_code, title)
    lines.append(
        f'  <text x="{w / 2.0:.1f}" y="28" text-anchor="middle" fill="{palette.text_title}" '
        f'font-family="Georgia, serif" font-size="16" font-weight="bold">{_xml_text(title)}</text>'
    )

    lines.append('  <g id="east-indian-grid">')
    # Outer square
    lines.append(
        f'    <rect x="{x0:.2f}" y="{y0:.2f}" width="{side:.2f}" height="{side:.2f}" '
        f'fill="{palette.bg_panel}" stroke="{palette.stroke_outer}" stroke-width="2.2"/>'
    )
    # 3x3 grid lines
    lines.append(
        f'    <line x1="{gx1:.2f}" y1="{y0:.2f}" x2="{gx1:.2f}" y2="{y1:.2f}" '
        f'stroke="{palette.stroke_primary}" stroke-width="1.6"/>'
    )
    lines.append(
        f'    <line x1="{gx2:.2f}" y1="{y0:.2f}" x2="{gx2:.2f}" y2="{y1:.2f}" '
        f'stroke="{palette.stroke_primary}" stroke-width="1.6"/>'
    )
    lines.append(
        f'    <line x1="{x0:.2f}" y1="{gy1:.2f}" x2="{x1:.2f}" y2="{gy1:.2f}" '
        f'stroke="{palette.stroke_primary}" stroke-width="1.6"/>'
    )
    lines.append(
        f'    <line x1="{x0:.2f}" y1="{gy2:.2f}" x2="{x1:.2f}" y2="{gy2:.2f}" '
        f'stroke="{palette.stroke_primary}" stroke-width="1.6"/>'
    )
    # 4 corner diagonals radiating from the central square corners to the outer corners
    # Top-left corner (Taurus / Gemini)
    lines.append(
        f'    <line x1="{x0:.2f}" y1="{y0:.2f}" x2="{gx1:.2f}" y2="{gy1:.2f}" '
        f'stroke="{palette.stroke_primary}" stroke-width="1.6"/>'
    )
    # Bottom-left corner (Leo / Virgo)
    lines.append(
        f'    <line x1="{gx1:.2f}" y1="{gy2:.2f}" x2="{x0:.2f}" y2="{y1:.2f}" '
        f'stroke="{palette.stroke_primary}" stroke-width="1.6"/>'
    )
    # Bottom-right corner (Scorpio / Sagittarius)
    lines.append(
        f'    <line x1="{gx2:.2f}" y1="{gy2:.2f}" x2="{x1:.2f}" y2="{y1:.2f}" '
        f'stroke="{palette.stroke_primary}" stroke-width="1.6"/>'
    )
    # Top-right corner (Aquarius / Pisces)
    lines.append(
        f'    <line x1="{gx2:.2f}" y1="{gy1:.2f}" x2="{x1:.2f}" y2="{y0:.2f}" '
        f'stroke="{palette.stroke_primary}" stroke-width="1.6"/>'
    )

    # Central square (1,1) summary panel
    lines.append(
        f'    <rect x="{gx1:.2f}" y="{gy1:.2f}" width="{c_len:.2f}" height="{c_len:.2f}" '
        f'fill="{palette.bg_primary}" stroke="{palette.stroke_outer}" stroke-width="1.8"/>'
    )
    mid_x = gx1 + c_len * 0.5
    mid_y = gy1 + c_len * 0.5
    lines.append(
        f'    <text x="{mid_x:.2f}" y="{mid_y - 24:.2f}" text-anchor="middle" '
        f'font-family="Georgia, serif" font-size="12.5" font-weight="bold" fill="{palette.text_title}">'
        f"Surya Chakra ({_xml_text(varga_code)})</text>"
    )
    lines.append(
        f'    <text x="{mid_x:.2f}" y="{mid_y - 4:.2f}" text-anchor="middle" '
        f'font-family="monospace" font-size="10" fill="{palette.asc_accent}">'
        f"Lagna: {RASI_NAMES[asc_sign_idx]}</text>"
    )
    lines.append(
        f'    <text x="{mid_x:.2f}" y="{mid_y + 12:.2f}" text-anchor="middle" '
        f'font-family="monospace" font-size="9.5" fill="{palette.text_subtitle}">'
        f"{_format_deg_min(asc_lon % 30.0)} | {asc_nak.name[:10]}</text>"
    )
    lines.append(
        f'    <text x="{mid_x:.2f}" y="{mid_y + 28:.2f}" text-anchor="middle" '
        f'font-family="monospace" font-size="9" fill="{palette.text_muted}">'
        f"Pada {asc_nak.pada}</text>"
    )
    lines.append("  </g>")

    # Sign header anchor & planet centroid for each of the 12 counter-clockwise East Indian signs
    sign_header_pos: dict[int, tuple[float, float]] = {
        0: (gx1 + c_len * 0.5, y0 + 14.0),                     # Aries (top-center)
        1: (x0 + c_len * 0.68, y0 + 14.0),                     # Taurus (top-left upper-right triangle)
        2: (x0 + c_len * 0.28, y0 + c_len * 0.52),             # Gemini (top-left lower-left triangle)
        3: (x0 + c_len * 0.5, gy1 + 14.0),                     # Cancer (middle-left)
        4: (x0 + c_len * 0.28, gy2 + 14.0),                    # Leo (bottom-left upper-left triangle)
        5: (x0 + c_len * 0.68, y1 - c_len * 0.36),             # Virgo (bottom-left lower-right triangle)
        6: (gx1 + c_len * 0.5, gy2 + 14.0),                    # Libra (bottom-center)
        7: (gx2 + c_len * 0.32, y1 - c_len * 0.36),            # Scorpio (bottom-right lower-left triangle)
        8: (gx2 + c_len * 0.72, gy2 + 14.0),                   # Sagittarius (bottom-right upper-right triangle)
        9: (gx2 + c_len * 0.5, gy1 + 14.0),                    # Capricorn (middle-right)
        10: (gx2 + c_len * 0.72, y0 + c_len * 0.52),           # Aquarius (top-right lower-right triangle)
        11: (gx2 + c_len * 0.32, y0 + 14.0),                   # Pisces (top-right upper-left triangle)
    }

    sign_planet_centroids: dict[int, tuple[float, float]] = {
        0: (gx1 + c_len * 0.5, y0 + c_len * 0.55),
        1: (x0 + c_len * 0.68, y0 + c_len * 0.34),
        2: (x0 + c_len * 0.30, y0 + c_len * 0.74),
        3: (x0 + c_len * 0.5, gy1 + c_len * 0.55),
        4: (x0 + c_len * 0.30, gy2 + c_len * 0.34),
        5: (x0 + c_len * 0.68, gy2 + c_len * 0.80),
        6: (gx1 + c_len * 0.5, gy2 + c_len * 0.55),
        7: (gx2 + c_len * 0.32, gy2 + c_len * 0.80),
        8: (gx2 + c_len * 0.70, gy2 + c_len * 0.34),
        9: (gx2 + c_len * 0.5, gy1 + c_len * 0.55),
        10: (gx2 + c_len * 0.70, y0 + c_len * 0.74),
        11: (gx2 + c_len * 0.32, y0 + c_len * 0.34),
    }

    lines.append('  <g id="east-indian-signs-and-planets" font-family="monospace">')
    for sign_idx in range(12):
        hx, hy = sign_header_pos[sign_idx]
        is_asc = sign_idx == asc_sign_idx
        hdr_text = f"{sign_idx + 1}:{RASI_NAMES[sign_idx][:3]}" + (" [Asc]" if is_asc else "")
        hdr_color = palette.asc_accent if is_asc else palette.sign_numeral
        lines.append(
            f'    <text x="{hx:.2f}" y="{hy:.2f}" text-anchor="middle" '
            f'font-size="9" font-weight="bold" data-sign="{sign_idx + 1}" fill="{hdr_color}">'
            f"{_xml_text(hdr_text)}</text>"
        )

        p_list = sign_planets[sign_idx]
        if not p_list:
            continue
        px, py = sign_planet_centroids[sign_idx]
        count = len(p_list)
        is_cardinal_box = sign_idx in (0, 3, 6, 9)
        step_y = 12.0 if is_cardinal_box else 10.0
        font_sz = 9.2 if is_cardinal_box else 8.2
        start_y = py - ((count - 1) * step_y) / 2.0
        for idx, (p_name, p_label, p_color) in enumerate(p_list):
            yy = start_y + idx * step_y
            lines.append(
                f'    <text x="{px:.2f}" y="{yy:.2f}" text-anchor="middle" '
                f'font-size="{font_sz:.1f}" font-weight="600" data-planet="{_xml_attr(p_name)}" '
                f'data-sign="{sign_idx + 1}" fill="{p_color}">{_xml_text(p_label)}</text>'
            )
    lines.append("  </g>")

    receipt_sha = _compute_artifact_receipt(
        chart_style="east_indian",
        varga=varga_code,
        theme=palette.name,
        width=w,
        height=h,
        title=title,
        payload={
            "ascendant_lon_deg": round(asc_lon, 8),
            "asc_sign_index": asc_sign_idx,
            "planet_longitudes": {k: round(v, 8) for k, v in sorted_planets},
            "planet_varga_signs": planet_sign_receipt,
            "retrograde": sorted(retro_set),
            "combust": sorted(combust_set),
        },
    )
    lines.append(
        f'  <text x="{w / 2.0:.1f}" y="{h - 10:.1f}" text-anchor="middle" '
        f'font-family="monospace" font-size="9" fill="{palette.text_muted}">'
        f"East Indian {varga_code} | SHA256: {receipt_sha[:16]}</text>"
    )
    lines.append("</svg>")
    return SvgChartArtifact(
        svg="\n".join(lines),
        chart_style="east_indian",
        varga=varga_code,
        theme=palette.name,
        width=w,
        height=h,
        receipt_sha256=receipt_sha,
    )


def _lon_to_wheel_xy(
    cx: float,
    cy: float,
    radius: float,
    sidereal_lon_deg: float,
    ascendant_lon_deg: float,
) -> tuple[float, float]:
    """Convert sidereal longitude to `(x, y)` on a wheel where `ascendant_lon_deg`
    is anchored at the 9-o'clock left horizon (`180 deg` screen angle) and longitudes
    advance counter-clockwise.
    """
    rel_deg = normalize_degrees(sidereal_lon_deg - ascendant_lon_deg)
    # Screen coordinates: 180 deg is left (cx - r, cy); counter-clockwise means increasing y-down angle
    # Wait: in SVG (+x right, +y down), (cx + r*cos(theta), cy + r*sin(theta)) goes clockwise as theta increases.
    # For counter-clockwise progression from left horizon (theta = pi), we subtract rel_deg:
    theta = math.radians(180.0 - rel_deg)
    return cx + radius * math.cos(theta), cy + radius * math.sin(theta)


def _resolve_wheel_label_angles(
    sorted_planets: list[tuple[str, float]],
    min_sep_deg: float = 6.5,
) -> dict[str, float]:
    """Spread closely conjunct planet label longitudes so radial text never collides."""
    if not sorted_planets:
        return {}
    items = sorted(sorted_planets, key=lambda item: item[1])
    n = len(items)
    angles = [lon for _, lon in items]
    for _ in range(12):
        changed = False
        for i in range(n):
            j = (i + 1) % n
            diff = (angles[j] - angles[i]) % 360.0
            if diff < min_sep_deg and (n * min_sep_deg < 360.0):
                push = (min_sep_deg - diff) * 0.5
                angles[i] = normalize_degrees(angles[i] - push)
                angles[j] = normalize_degrees(angles[j] + push)
                changed = True
        if not changed:
            break
    return {items[i][0]: angles[i] for i in range(n)}


def _classify_aspect(lon_a: float, lon_b: float) -> tuple[str, float] | None:
    """Classify geometric aspect between two ecliptic longitudes within standard orbs."""
    sep = abs(normalize_degrees(lon_a) - normalize_degrees(lon_b))
    if sep > 180.0:
        sep = 360.0 - sep
    targets = (
        ("conjunction", 0.0, 8.0),
        ("opposition", 180.0, 8.0),
        ("trine", 120.0, 7.0),
        ("square", 90.0, 7.0),
        ("sextile", 60.0, 5.5),
    )
    for name, exact, orb in targets:
        if abs(sep - exact) <= orb:
            return name, round(abs(sep - exact), 3)
    return None


def render_circular_wheel_svg(
    planet_longitudes: Mapping[str, float],
    ascendant_lon_deg: float,
    *,
    title: str = "Sidereal Zodiac & 27-Nakshatra Wheel",
    theme: str = "obsidian",
    retrograde_planets: Iterable[str] | Mapping[str, bool] | None = None,
    show_aspects: bool = True,
    width: int = 640,
    height: int = 640,
) -> SvgChartArtifact:
    """Render a concentric scientific/astrological circular wheel SVG with:
    - Outer ring: 27 Nakshatra sectors (13 deg 20 min each) + 108 pada ticks.
    - Middle ring: 12 Rasi sectors (30 deg each) + 5-degree ticks.
    - Inner ring: 12 Bhava house cusps anchored to `ascendant_lon_deg`.
    - Planet radial markers with collision-resolved degree labels and central aspect chords.
    """
    w, h = _validate_dimensions(width, height)
    palette = _resolve_theme(theme)
    retro_set = _normalize_planet_flag_set(retrograde_planets)
    asc_lon = normalize_degrees(ascendant_lon_deg)
    sorted_planets = _sorted_planet_items(planet_longitudes)

    cx = w * 0.5
    cy = h * 0.5 + 14.0
    max_r = min(w, h - 68.0) * 0.46
    r_nak_outer = max_r
    r_nak_inner = max_r * 0.84
    r_rasi_inner = max_r * 0.68
    r_house_inner = max_r * 0.54
    r_planet_track = max_r * 0.44
    r_chord = max_r * 0.34

    lines = _svg_header(w, h, palette, "circular_wheel", "D1", title)
    lines.append(
        f'  <text x="{cx:.1f}" y="26" text-anchor="middle" fill="{palette.text_title}" '
        f'font-family="Georgia, serif" font-size="16" font-weight="bold">{_xml_text(title)}</text>'
    )
    asc_sign_idx = min(int(asc_lon // 30.0), 11)
    asc_nak = nakshatra_position(asc_lon)
    lines.append(
        f'  <text x="{cx:.1f}" y="44" text-anchor="middle" fill="{palette.text_subtitle}" '
        f'font-family="monospace" font-size="11">'
        f"Ascendant: {RASI_NAMES[asc_sign_idx]} {_format_deg_min(asc_lon % 30.0)} | "
        f"{asc_nak.name} Pada {asc_nak.pada}</text>"
    )

    # Concentric ring circles
    lines.append('  <g id="wheel-rings">')
    lines.append(
        f'    <circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r_nak_outer:.2f}" '
        f'fill="{palette.bg_panel}" stroke="{palette.stroke_outer}" stroke-width="2.0"/>'
    )
    lines.append(
        f'    <circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r_nak_inner:.2f}" '
        f'fill="none" stroke="{palette.stroke_primary}" stroke-width="1.5"/>'
    )
    lines.append(
        f'    <circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r_rasi_inner:.2f}" '
        f'fill="none" stroke="{palette.stroke_primary}" stroke-width="1.5"/>'
    )
    lines.append(
        f'    <circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r_house_inner:.2f}" '
        f'fill="{palette.bg_primary}" stroke="{palette.stroke_secondary}" stroke-width="1.2"/>'
    )
    lines.append(
        f'    <circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r_chord:.2f}" '
        f'fill="none" stroke="{palette.stroke_muted}" stroke-width="1.0" stroke-dasharray="3,3"/>'
    )
    lines.append("  </g>")

    # 1. Outer Ring: 27 Nakshatras and 108 Pada ticks
    lines.append('  <g id="nakshatra-ring" font-family="monospace" font-size="7.8">')
    for nak_meta in NAKSHATRA_CATALOG:
        start_deg = nak_meta.index * NAKSHATRA_SPAN_DEG
        mid_deg = start_deg + 0.5 * NAKSHATRA_SPAN_DEG
        x_out, y_out = _lon_to_wheel_xy(cx, cy, r_nak_outer, start_deg, asc_lon)
        x_in, y_in = _lon_to_wheel_xy(cx, cy, r_nak_inner, start_deg, asc_lon)
        lines.append(
            f'    <line x1="{x_in:.2f}" y1="{y_in:.2f}" x2="{x_out:.2f}" y2="{y_out:.2f}" '
            f'stroke="{palette.stroke_primary}" stroke-width="1.1" data-nakshatra-index="{nak_meta.index}"/>'
        )
        # 4 Pada sub-ticks per Nakshatra
        for p_idx in range(1, 4):
            p_deg = start_deg + p_idx * PADA_SPAN_DEG
            px_out, py_out = _lon_to_wheel_xy(cx, cy, r_nak_inner + (r_nak_outer - r_nak_inner) * 0.28, p_deg, asc_lon)
            px_in, py_in = _lon_to_wheel_xy(cx, cy, r_nak_inner, p_deg, asc_lon)
            lines.append(
                f'    <line x1="{px_in:.2f}" y1="{py_in:.2f}" x2="{px_out:.2f}" y2="{py_out:.2f}" '
                f'stroke="{palette.stroke_secondary}" stroke-width="0.7"/>'
            )
        # Nakshatra short label at midpoint
        lx, ly = _lon_to_wheel_xy(cx, cy, (r_nak_outer + r_nak_inner) * 0.5, mid_deg, asc_lon)
        short_nak = nak_meta.name[:6]
        lines.append(
            f'    <text x="{lx:.2f}" y="{ly + 2.5:.2f}" text-anchor="middle" '
            f'data-nakshatra="{_xml_attr(nak_meta.name)}" fill="{palette.text_subtitle}">'
            f"{_xml_text(short_nak)}</text>"
        )
    lines.append("  </g>")

    # 2. Middle Ring: 12 Rasi sectors (30 deg each) + 5-degree ticks
    lines.append('  <g id="rasi-ring" font-family="monospace" font-size="9.5" font-weight="bold">')
    for rasi_idx in range(12):
        start_deg = rasi_idx * 30.0
        mid_deg = start_deg + 15.0
        rx_out, ry_out = _lon_to_wheel_xy(cx, cy, r_nak_inner, start_deg, asc_lon)
        rx_in, ry_in = _lon_to_wheel_xy(cx, cy, r_rasi_inner, start_deg, asc_lon)
        lines.append(
            f'    <line x1="{rx_in:.2f}" y1="{ry_in:.2f}" x2="{rx_out:.2f}" y2="{ry_out:.2f}" '
            f'stroke="{palette.stroke_outer}" stroke-width="1.5" data-rasi-index="{rasi_idx}"/>'
        )
        for step in range(5, 30, 5):
            t_deg = start_deg + step
            tick_h = 0.26 if step % 10 == 0 else 0.15
            tx_out, ty_out = _lon_to_wheel_xy(
                cx, cy, r_rasi_inner + (r_nak_inner - r_rasi_inner) * tick_h, t_deg, asc_lon
            )
            tx_in, ty_in = _lon_to_wheel_xy(cx, cy, r_rasi_inner, t_deg, asc_lon)
            lines.append(
                f'    <line x1="{tx_in:.2f}" y1="{ty_in:.2f}" x2="{tx_out:.2f}" y2="{ty_out:.2f}" '
                f'stroke="{palette.stroke_secondary}" stroke-width="0.7"/>'
            )
        rlx, rly = _lon_to_wheel_xy(cx, cy, (r_nak_inner + r_rasi_inner) * 0.5, mid_deg, asc_lon)
        rasi_label = f"{rasi_idx + 1}:{RASI_NAMES[rasi_idx][:3]}"
        lines.append(
            f'    <text x="{rlx:.2f}" y="{rly + 3.0:.2f}" text-anchor="middle" '
            f'data-rasi="{RASI_NAMES[rasi_idx]}" fill="{palette.sign_numeral}">{rasi_label}</text>'
        )
    lines.append("  </g>")

    # 3. Inner Ring: 12 Equal Bhava house cusps anchored to Ascendant
    lines.append('  <g id="bhava-ring" font-family="monospace" font-size="8.8">')
    for h_idx in range(12):
        cusp_deg = normalize_degrees(asc_lon + h_idx * 30.0)
        mid_deg = normalize_degrees(cusp_deg + 15.0)
        hx_out, hy_out = _lon_to_wheel_xy(cx, cy, r_rasi_inner, cusp_deg, asc_lon)
        hx_in, hy_in = _lon_to_wheel_xy(cx, cy, r_house_inner, cusp_deg, asc_lon)
        stroke_col = palette.asc_accent if h_idx == 0 else palette.stroke_secondary
        stroke_w = "2.0" if h_idx in (0, 3, 6, 9) else "1.0"
        lines.append(
            f'    <line x1="{hx_in:.2f}" y1="{hy_in:.2f}" x2="{hx_out:.2f}" y2="{hy_out:.2f}" '
            f'stroke="{stroke_col}" stroke-width="{stroke_w}" data-house-cusp="{h_idx + 1}"/>'
        )
        hlx, hly = _lon_to_wheel_xy(cx, cy, (r_rasi_inner + r_house_inner) * 0.5, mid_deg, asc_lon)
        lines.append(
            f'    <text x="{hlx:.2f}" y="{hly + 3.0:.2f}" text-anchor="middle" '
            f'fill="{palette.text_muted}" data-house="{h_idx + 1}">H{h_idx + 1}</text>'
        )
    # Ascendant horizon arrow marker on left axis
    ax_out, ay_out = _lon_to_wheel_xy(cx, cy, r_rasi_inner + 4.0, asc_lon, asc_lon)
    ax_in, ay_in = _lon_to_wheel_xy(cx, cy, r_chord, asc_lon, asc_lon)
    lines.append(
        f'    <line x1="{ax_in:.2f}" y1="{ay_in:.2f}" x2="{ax_out:.2f}" y2="{ay_out:.2f}" '
        f'stroke="{palette.asc_accent}" stroke-width="1.8" stroke-dasharray="4,2" data-marker="ascendant-axis"/>'
    )
    lines.append("  </g>")

    # 4. Central Aspect Chords
    aspect_pairs: list[tuple[str, str, str, float]] = []
    if show_aspects and len(sorted_planets) >= 2:
        aspect_colors = {
            "conjunction": palette.aspect_conjunction,
            "trine": palette.aspect_trine,
            "sextile": palette.aspect_sextile,
            "square": palette.aspect_square,
            "opposition": palette.aspect_opposition,
        }
        lines.append('  <g id="aspect-chords">')
        for i in range(len(sorted_planets)):
            p1, lon1 = sorted_planets[i]
            x1_c, y1_c = _lon_to_wheel_xy(cx, cy, r_chord, lon1, asc_lon)
            for j in range(i + 1, len(sorted_planets)):
                p2, lon2 = sorted_planets[j]
                asp = _classify_aspect(lon1, lon2)
                if asp is None:
                    continue
                asp_type, orb_val = asp
                aspect_pairs.append((p1, p2, asp_type, orb_val))
                x2_c, y2_c = _lon_to_wheel_xy(cx, cy, r_chord, lon2, asc_lon)
                col = aspect_colors.get(asp_type, palette.stroke_secondary)
                dash = ' stroke-dasharray="4,3"' if asp_type in ("square", "sextile") else ""
                lines.append(
                    f'    <line x1="{x1_c:.2f}" y1="{y1_c:.2f}" x2="{x2_c:.2f}" y2="{y2_c:.2f}" '
                    f'stroke="{col}" stroke-width="1.2" stroke-opacity="0.78"{dash} '
                    f'data-aspect="{asp_type}" data-planets="{_xml_attr(p1)}-{_xml_attr(p2)}"/>'
                )
        lines.append("  </g>")

    # 5. Planet Radial Markers and Collision-Resolved Degree Labels
    label_angles = _resolve_wheel_label_angles(sorted_planets, min_sep_deg=7.5)
    lines.append('  <g id="wheel-planets" font-family="monospace">')
    for p_name, p_lon in sorted_planets:
        tx_Ring, ty_ring = _lon_to_wheel_xy(cx, cy, r_house_inner, p_lon, asc_lon)
        cx_dot, cy_dot = _lon_to_wheel_xy(cx, cy, r_chord, p_lon, asc_lon)
        disp_lon = label_angles.get(p_name, p_lon)
        lx, ly = _lon_to_wheel_xy(cx, cy, r_planet_track, disp_lon, asc_lon)
        p_col = _planet_color(p_name, palette, retro_set, frozenset())
        p_label = _format_planet_label(p_name, p_lon, retro_set, frozenset(), include_degrees=True)

        lines.append(
            f'    <line x1="{cx_dot:.2f}" y1="{cy_dot:.2f}" x2="{lx:.2f}" y2="{ly:.2f}" '
            f'stroke="{p_col}" stroke-width="0.9" stroke-opacity="0.65"/>'
        )
        lines.append(
            f'    <circle cx="{tx_Ring:.2f}" cy="{ty_ring:.2f}" r="2.8" fill="{p_col}"/>'
        )
        lines.append(
            f'    <circle cx="{cx_dot:.2f}" cy="{cy_dot:.2f}" r="2.4" fill="{p_col}"/>'
        )
        lines.append(
            f'    <text x="{lx:.2f}" y="{ly + 3.0:.2f}" text-anchor="middle" '
            f'font-size="8.6" font-weight="bold" data-planet="{_xml_attr(p_name)}" fill="{p_col}">'
            f"{_xml_text(p_label)}</text>"
        )
    lines.append("  </g>")

    receipt_sha = _compute_artifact_receipt(
        chart_style="circular_wheel",
        varga="D1",
        theme=palette.name,
        width=w,
        height=h,
        title=title,
        payload={
            "ascendant_lon_deg": round(asc_lon, 8),
            "planet_longitudes": {k: round(v, 8) for k, v in sorted_planets},
            "retrograde": sorted(retro_set),
            "show_aspects": bool(show_aspects),
            "aspects": aspect_pairs,
        },
    )
    lines.append(
        f'  <text x="{cx:.1f}" y="{h - 10:.1f}" text-anchor="middle" '
        f'font-family="monospace" font-size="9" fill="{palette.text_muted}">'
        f"27-Nakshatra &amp; Sidereal Wheel | SHA256: {receipt_sha[:16]}</text>"
    )
    lines.append("</svg>")
    return SvgChartArtifact(
        svg="\n".join(lines),
        chart_style="circular_wheel",
        varga="D1",
        theme=palette.name,
        width=w,
        height=h,
        receipt_sha256=receipt_sha,
    )


def _resolve_janma_nakshatra_28_name(janma_nakshatra_index: int) -> str:
    idx = int(janma_nakshatra_index)
    if 0 <= idx < 27:
        return NAKSHATRA_CATALOG[idx].name
    if idx == 27:
        return SARVATOBHADRA_28_NAKSHATRAS[21]  # Abhijit when 27 is passed explicitly
    raise ValueError(f"janma_nakshatra_index must be in 0..27; got {janma_nakshatra_index}")


def render_sarvatobhadra_svg(
    janma_nakshatra_index: int = 0,
    transit_longitudes: Mapping[str, float] | None = None,
    *,
    title: str = "Sarvatobhadra 9x9 Chakra",
    theme: str = "obsidian",
    width: int = 720,
    height: int = 720,
) -> SvgChartArtifact:
    """Render the 81-cell (9x9) Sarvatobhadra Chakra SVG with active transit Vedha rays."""
    w, h = _validate_dimensions(width, height)
    palette = _resolve_theme(theme)
    janma_nak_name = _resolve_janma_nakshatra_28_name(janma_nakshatra_index)
    grid = build_sarvatobhadra_grid()

    sorted_transits = _sorted_planet_items(transit_longitudes or {})
    cell_transits: dict[tuple[int, int], list[str]] = {}
    vedha_lines_data: list[tuple[str, tuple[int, int], tuple[int, int], str, bool]] = []

    # Map nakshatra name -> cell
    nak_cell_map: dict[str, SarvatobhadraCell] = {}
    for row in grid:
        for cell in row:
            if cell.cell_type == "Nakshatra":
                nak_cell_map[cell.label] = cell

    for p_name, p_lon in sorted_transits:
        ab_pos = abhijit_position(p_lon)
        n_name = ab_pos.nakshatra_28_name
        src_cell = nak_cell_map[n_name]
        p_code = _planet_code(p_name)
        cell_transits.setdefault((src_cell.row, src_cell.col), []).append(p_code)

        rays = compute_sarvatobhadra_vedha(n_name, grid=grid)
        is_ben = p_name.strip().capitalize() in NATURAL_BENEFICS
        for ray_dir, ray_cells in (
            ("front", rays.front_ray_cells),
            ("left", rays.left_ray_cells),
            ("right", rays.right_ray_cells),
        ):
            if ray_cells:
                end_cell = ray_cells[-1]
                vedha_lines_data.append(
                    (
                        p_name,
                        (src_cell.row, src_cell.col),
                        (end_cell.row, end_cell.col),
                        ray_dir,
                        is_ben,
                    )
                )

    pad_top = 56.0
    pad_bottom = 32.0
    avail_w = w - 48.0
    avail_h = h - pad_top - pad_bottom - 12.0
    side = min(avail_w, avail_h)
    x0 = (w - side) / 2.0
    y0 = pad_top + (avail_h - side) / 2.0
    cell_s = side / 9.0

    lines = _svg_header(w, h, palette, "sarvatobhadra_chakra", "SBC-9x9", title)
    lines.append(
        f'  <text x="{w / 2.0:.1f}" y="26" text-anchor="middle" fill="{palette.text_title}" '
        f'font-family="Georgia, serif" font-size="16" font-weight="bold">{_xml_text(title)}</text>'
    )
    lines.append(
        f'  <text x="{w / 2.0:.1f}" y="44" text-anchor="middle" fill="{palette.text_subtitle}" '
        f'font-family="monospace" font-size="11">'
        f"Janma Nakshatra: {_xml_text(janma_nak_name)} | 81-Cell Sacred Vedha Grid</text>"
    )

    cell_fill_map = {
        "Vowel": palette.sbc_vowel_fill,
        "Nakshatra": palette.sbc_nakshatra_fill,
        "Consonant": palette.sbc_consonant_fill,
        "Rasi": palette.sbc_rasi_fill,
        "Tithi": palette.sbc_tithi_fill,
    }

    # 1. Render all 81 cells
    lines.append('  <g id="sarvatobhadra-cells" font-family="monospace">')
    for row in grid:
        for cell in row:
            cx0 = x0 + cell.col * cell_s
            cy0 = y0 + cell.row * cell_s
            is_janma = cell.cell_type == "Nakshatra" and cell.label == janma_nak_name
            fill_col = palette.sbc_janma_fill if is_janma else cell_fill_map.get(cell.cell_type, palette.bg_panel)
            stroke_col = palette.sbc_janma_stroke if is_janma else palette.stroke_primary
            stroke_w = "2.2" if is_janma else "1.0"

            lines.append(
                f'    <rect x="{cx0:.2f}" y="{cy0:.2f}" width="{cell_s:.2f}" height="{cell_s:.2f}" '
                f'fill="{fill_col}" stroke="{stroke_col}" stroke-width="{stroke_w}" '
                f'data-row="{cell.row}" data-col="{cell.col}" data-cell-type="{cell.cell_type}" '
                f'data-label="{_xml_attr(cell.label)}"/>'
            )

            short_lbl = cell.label[:7] if cell.cell_type in ("Nakshatra", "Rasi") else cell.label
            lbl_color = (
                palette.sign_numeral
                if cell.cell_type in ("Vowel", "Tithi")
                else (palette.asc_accent if is_janma else palette.text_primary)
            )
            font_sz = "8.2" if cell.cell_type == "Nakshatra" else "9.0"
            lines.append(
                f'    <text x="{cx0 + cell_s * 0.5:.2f}" y="{cy0 + cell_s * 0.42:.2f}" '
                f'text-anchor="middle" font-size="{font_sz}" font-weight="bold" fill="{lbl_color}">'
                f"{_xml_text(short_lbl)}</text>"
            )
            lines.append(
                f'    <text x="{cx0 + cell_s * 0.5:.2f}" y="{cy0 + cell_s * 0.64:.2f}" '
                f'text-anchor="middle" font-size="6.8" fill="{palette.text_muted}">'
                f"{cell.cell_type[:3].upper()}</text>"
            )

            occupants = cell_transits.get((cell.row, cell.col))
            if occupants:
                occ_str = ",".join(occupants)
                lines.append(
                    f'    <text x="{cx0 + cell_s * 0.5:.2f}" y="{cy0 + cell_s * 0.86:.2f}" '
                    f'text-anchor="middle" font-size="8.5" font-weight="bold" '
                    f'data-transit-occupants="{_xml_attr(occ_str)}" fill="{palette.asc_accent}">'
                    f"[{_xml_text(occ_str)}]</text>"
                )
    lines.append("  </g>")

    # 2. Render active Vedha rays across the 9x9 grid when transit_longitudes are provided
    if vedha_lines_data:
        lines.append('  <g id="sarvatobhadra-vedha-rays">')
        for p_name, (r1, c1), (r2, c2), ray_dir, is_ben in vedha_lines_data:
            x1_ray = x0 + (c1 + 0.5) * cell_s
            y1_ray = y0 + (r1 + 0.5) * cell_s
            x2_ray = x0 + (c2 + 0.5) * cell_s
            y2_ray = y0 + (r2 + 0.5) * cell_s
            ray_col = palette.benefic_color if is_ben else palette.malefic_color
            dash = "" if ray_dir == "front" else ' stroke-dasharray="5,3"'
            lines.append(
                f'    <line class="vedha-ray" x1="{x1_ray:.2f}" y1="{y1_ray:.2f}" '
                f'x2="{x2_ray:.2f}" y2="{y2_ray:.2f}" stroke="{ray_col}" '
                f'stroke-width="1.4" stroke-opacity="0.72"{dash} '
                f'data-planet="{_xml_attr(p_name)}" data-vedha-dir="{ray_dir}"/>'
            )
        lines.append("  </g>")

    receipt_sha = _compute_artifact_receipt(
        chart_style="sarvatobhadra_chakra",
        varga="SBC-9x9",
        theme=palette.name,
        width=w,
        height=h,
        title=title,
        payload={
            "janma_nakshatra_index": int(janma_nakshatra_index),
            "janma_nakshatra_name": janma_nak_name,
            "transit_longitudes": {k: round(v, 8) for k, v in sorted_transits},
            "vedha_count": len(vedha_lines_data),
        },
    )
    lines.append(
        f'  <text x="{w / 2.0:.1f}" y="{h - 10:.1f}" text-anchor="middle" '
        f'font-family="monospace" font-size="9" fill="{palette.text_muted}">'
        f"Sarvatobhadra 9x9 Chakra | SHA256: {receipt_sha[:16]}</text>"
    )
    lines.append("</svg>")
    return SvgChartArtifact(
        svg="\n".join(lines),
        chart_style="sarvatobhadra_chakra",
        varga="SBC-9x9",
        theme=palette.name,
        width=w,
        height=h,
        receipt_sha256=receipt_sha,
    )


__all__ = [
    "SOUTH_INDIAN_SIGN_CELLS",
    "SUPPORTED_THEMES",
    "SvgChartArtifact",
    "ThemePalette",
    "render_circular_wheel_svg",
    "render_east_indian_svg",
    "render_north_indian_svg",
    "render_sarvatobhadra_svg",
    "render_south_indian_svg",
]
