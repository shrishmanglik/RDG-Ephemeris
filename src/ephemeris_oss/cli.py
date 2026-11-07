"""Command line: ``ephemeris-oss kernels``, ``chart``, ``jyotish``, ``eclipses``, ``fact-sheet``, ``svg``, ``bench``."""

from __future__ import annotations

import argparse
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any

from . import kernels
from ._api import Engine, EphemerisError, Houses, Undefined
from .engine.eclipses import (
    find_lunar_eclipses,
    find_solar_eclipses,
    lunar_eclipse_local_visibility,
    solar_eclipse_local_circumstances,
)
from .fact_sheet import compile_ai_fact_sheet
from .jyotish.dasha import jd_to_iso_utc
from .visualization import (
    render_circular_wheel_svg,
    render_east_indian_svg,
    render_north_indian_svg,
    render_south_indian_svg,
)

BODIES = (
    "sun",
    "moon",
    "mercury",
    "venus",
    "mars",
    "jupiter",
    "saturn",
    "uranus",
    "neptune",
    "pluto",
)
JYOTISH_BODIES = ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "rahu", "ketu")


def _instant(text: str) -> datetime:
    value = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if value.tzinfo is None:
        raise SystemExit("--at / --start / --end needs a UTC offset, for example 2026-10-06T12:00:00Z")
    return value.astimezone(timezone.utc)


def _datetime_to_jd(dt: datetime) -> float:
    return dt.timestamp() / 86400.0 + 2440587.5


def _jsonable(value: Any) -> Any:
    if isinstance(value, (Houses, Undefined)):
        return {"type": type(value).__name__, **value.__dict__}
    if is_dataclass(value) and not isinstance(value, type):
        return _jsonable(asdict(value))
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _kernels(args: argparse.Namespace) -> int:
    directory = Path(args.cache) if args.cache else None
    if args.action == "fetch":
        identifiers = ("DE440", "DE441-PART1", "DE441-PART2") if args.all else ("DE440",)
        kernels.fetch(identifiers, directory=directory)
        if args.eop:
            kernels.fetch_eop(directory=directory)
    status = kernels.verify(directory)
    for identifier, state in status.items():
        print(f"{identifier}: {state}")
    return 1 if args.verify and status.get("DE440") != "verified" else 0


def _chart(args: argparse.Namespace) -> int:
    t = _instant(args.at)
    kernel_mode = "compact" if getattr(args, "compact", False) else "auto"
    with Engine.load(kernels=kernel_mode, cache_dir=args.cache) as eng:
        positions = eng.positions(t, bodies=BODIES, ayanamsa=args.ayanamsa)
        payload: dict[str, Any] = {
            "at": t.isoformat(),
            "ayanamsa": args.ayanamsa,
            "positions": {
                body: {
                    "longitude_deg": place["longitude_deg"],
                    "latitude_deg": place.get("latitude_deg"),
                }
                for body, place in positions.value.items()
            },
            "receipt": positions.receipt,
            "receipt_sha256": positions.receipt_sha256,
        }
        if args.lat is not None and args.lon is not None:
            try:
                houses = eng.houses(t, args.lat, args.lon, system=args.houses, ayanamsa=args.ayanamsa)
                payload["houses"] = _jsonable(houses.value)
            except (EphemerisError, ValueError) as error:
                payload["houses"] = {"type": "Unavailable", "reason": str(error)}
    if args.json:
        json.dump(_jsonable(payload), sys.stdout, indent=2, sort_keys=True, default=str)
        print()
    else:
        for body, place in payload["positions"].items():
            print(f"{body:8s} {place['longitude_deg']:12.6f}")
    return 0


def _jyotish(args: argparse.Namespace) -> int:
    t = _instant(args.at)
    jd_ut = _datetime_to_jd(t)
    kernel_mode = "compact" if getattr(args, "compact", False) else "auto"
    with Engine.load(kernels=kernel_mode, cache_dir=args.cache) as eng:
        positions = eng.positions(t, bodies=JYOTISH_BODIES, ayanamsa=args.ayanamsa)
        houses = eng.houses(t, args.lat, args.lon, system="whole_sign", ayanamsa=args.ayanamsa)
        asc_lon = (
            float(houses.value.ascendant_deg)
            if isinstance(houses.value, Houses)
            else 0.0
        )
        lons = {b: float(place["longitude_deg"]) for b, place in positions.value.items()}
        speeds = {
            b: float(place["speed_deg_per_day"])
            for b, place in positions.value.items()
        }
        sheet = compile_ai_fact_sheet(
            lons,
            asc_lon,
            planet_speeds_deg_per_day=speeds,
            birth_jd_ut=jd_ut,
            query_jd_ut=jd_ut,
            latitude_deg=args.lat,
        )
    if args.json:
        json.dump(sheet.payload, sys.stdout, indent=2, sort_keys=True)
        print()
    else:
        asc = sheet.payload["ascendant"]
        print(f"Ascendant: {asc['sign']} {asc['deg_in_sign']:.2f} deg ({asc['nakshatra']} Pada {asc['pada']}, D9 {asc['d9_sign']})")
        for body, info in sheet.payload["bodies"].items():
            retro_tag = " (R)" if info.get("retro") else ""
            print(
                f"{body:8s} {info['sign']:11s} {info['deg']:5.2f} deg | H{info['house']:02d} | "
                f"{info['nakshatra']} P{info['pada']} | D9 {info['d9_sign']}{retro_tag}"
            )
        if "dasha" in sheet.payload:
            d = sheet.payload["dasha"]
            print(f"Active Vimshottari: {d.get('mahadasha')}-{d.get('antardasha')}-{d.get('pratyantardasha')}")
        print(f"Receipt SHA-256: {sheet.receipt_sha256}")
    return 0


def _fact_sheet(args: argparse.Namespace) -> int:
    t = _instant(args.at)
    jd_ut = _datetime_to_jd(t)
    kernel_mode = "compact" if getattr(args, "compact", False) else "auto"
    with Engine.load(kernels=kernel_mode, cache_dir=args.cache) as eng:
        positions = eng.positions(t, bodies=JYOTISH_BODIES, ayanamsa=args.ayanamsa)
        houses = eng.houses(t, args.lat, args.lon, system="whole_sign", ayanamsa=args.ayanamsa)
        asc_lon = (
            float(houses.value.ascendant_deg)
            if isinstance(houses.value, Houses)
            else 0.0
        )
        lons = {b: float(place["longitude_deg"]) for b, place in positions.value.items()}
        speeds = {
            b: float(place["speed_deg_per_day"])
            for b, place in positions.value.items()
        }
        sheet = compile_ai_fact_sheet(
            lons,
            asc_lon,
            planet_speeds_deg_per_day=speeds,
            birth_jd_ut=jd_ut,
            query_jd_ut=jd_ut,
            latitude_deg=args.lat,
            max_bytes=args.max_bytes,
        )
    print(sheet.json_str)
    return 0


def _svg(args: argparse.Namespace) -> int:
    t = _instant(args.at)
    kernel_mode = "compact" if getattr(args, "compact", False) else "auto"
    with Engine.load(kernels=kernel_mode, cache_dir=args.cache) as eng:
        positions = eng.positions(t, bodies=JYOTISH_BODIES, ayanamsa=args.ayanamsa)
        houses = eng.houses(t, args.lat, args.lon, system="whole_sign", ayanamsa=args.ayanamsa)
        asc_lon = (
            float(houses.value.ascendant_deg)
            if isinstance(houses.value, Houses)
            else 0.0
        )
        lons = {b: float(place["longitude_deg"]) for b, place in positions.value.items()}
        retros = {
            b
            for b, place in positions.value.items()
            if b not in ("sun", "moon") and float(place["speed_deg_per_day"]) < 0.0
        }
    if args.style == "north_indian":
        artifact = render_north_indian_svg(
            lons, asc_lon, varga=args.varga, theme=args.theme, retrograde_planets=retros
        )
    elif args.style == "south_indian":
        artifact = render_south_indian_svg(
            lons, asc_lon, varga=args.varga, theme=args.theme, retrograde_planets=retros
        )
    elif args.style == "east_indian":
        artifact = render_east_indian_svg(
            lons, asc_lon, varga=args.varga, theme=args.theme, retrograde_planets=retros
        )
    else:
        artifact = render_circular_wheel_svg(
            lons, asc_lon, theme=args.theme, retrograde_planets=retros
        )
    if args.out:
        Path(args.out).write_text(artifact.svg, encoding="utf-8")
    else:
        print(artifact.svg)
    return 0


def _eclipses(args: argparse.Namespace) -> int:
    t_start = _instant(args.start)
    t_end = _instant(args.end)
    jd_start = _datetime_to_jd(t_start)
    jd_end = _datetime_to_jd(t_end)
    solar_list = find_solar_eclipses(jd_start, jd_end)
    lunar_list = find_lunar_eclipses(jd_start, jd_end)

    solar_out: list[dict[str, Any]] = []
    for s in solar_list:
        entry = _jsonable(s)
        entry["greatest_iso_utc"] = jd_to_iso_utc(s.greatest_jd_tt)
        if args.lat is not None and args.lon is not None:
            local = solar_eclipse_local_circumstances(s, args.lat, args.lon)
            entry["local_circumstances"] = _jsonable(local)
        solar_out.append(entry)

    lunar_out: list[dict[str, Any]] = []
    for l_ecl in lunar_list:
        entry = _jsonable(l_ecl)
        entry["greatest_iso_utc"] = jd_to_iso_utc(l_ecl.greatest_jd_tt)
        if args.lat is not None and args.lon is not None:
            local_vis = lunar_eclipse_local_visibility(l_ecl, args.lat, args.lon)
            entry["local_visibility"] = _jsonable(local_vis)
        lunar_out.append(entry)

    payload = {
        "start": t_start.isoformat(),
        "end": t_end.isoformat(),
        "solar_eclipses": solar_out,
        "lunar_eclipses": lunar_out,
    }
    if args.json:
        json.dump(payload, sys.stdout, indent=2, sort_keys=True, default=str)
        print()
    else:
        for s in solar_list:
            print(f"SOLAR {s.classification:8s} | {jd_to_iso_utc(s.greatest_jd_tt)} | gamma={s.gamma:+.4f} | mag={s.max_magnitude:.4f}")
        for l_ecl in lunar_list:
            print(f"LUNAR {l_ecl.classification:9s} | {jd_to_iso_utc(l_ecl.greatest_jd_tt)} | gamma={l_ecl.gamma:+.4f} | umag={l_ecl.umbral_magnitude:.4f}")
    return 0


def _panchang(args: argparse.Namespace) -> int:
    from .almanac import generate_monthly_panchang

    sheet = generate_monthly_panchang(
        args.year,
        args.month,
        latitude_deg=args.lat,
        longitude_deg=args.lon,
        tz_offset_hours=args.tz_offset,
    )
    if args.json:
        json.dump(_jsonable(sheet), sys.stdout, indent=2, sort_keys=True, default=str)
        print()
    else:
        for d in sheet.days:
            vrata_str = f" | {', '.join(d.vratas)}" if d.vratas else ""
            print(
                f"{d.civil_date} ({d.vara_name:11s}) | Tithi {d.tithi_number:02d} {d.tithi_name:18s} | "
                f"{d.nakshatra_name:16s}{vrata_str}"
            )
    return 0


def _siddhanta(args: argparse.Namespace) -> int:
    from .jyotish_siddhanta import surya_siddhanta_true_positions

    t = _instant(args.at)
    jd_ut = _datetime_to_jd(t)
    report = surya_siddhanta_true_positions(jd_ut)
    if args.json:
        json.dump(_jsonable(report), sys.stdout, indent=2, sort_keys=True, default=str)
        print()
    else:
        print(f"Ahargana (Kali Yuga days): {report.ahargana:.4f}")
        for body, pos in report.planets.items():
            print(
                f"{body:8s} | Madhyama={pos.mean_longitude_deg:8.4f} deg | "
                f"Spashta={pos.true_longitude_deg:8.4f} deg ({pos.rasi_name})"
            )
    return 0


def _table(args: argparse.Namespace) -> int:
    from .almanac import generate_ephemeris_table

    t_start = _instant(args.start)
    t_end = _instant(args.end)
    table = generate_ephemeris_table(
        _datetime_to_jd(t_start),
        _datetime_to_jd(t_end),
        step_days=args.step_days,
    )
    if args.format == "csv":
        print(table.to_csv(), end="")
    elif args.format == "json":
        json.dump(_jsonable(table), sys.stdout, indent=2, sort_keys=True, default=str)
        print()
    else:
        print(table.to_markdown())
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ephemeris-oss", description=__doc__)
    parser.add_argument("--cache", default=None, help="data directory (default: user cache)")
    commands = parser.add_subparsers(dest="command", required=True)

    k = commands.add_parser("kernels", help="fetch or verify JPL kernels in the cache")
    k.add_argument("action", choices=("fetch", "status"))
    k.add_argument("--verify", action="store_true", help="exit 1 unless DE440 verifies")
    k.add_argument("--all", action="store_true", help="also DE441 (about 3.3 GB) for dates outside 1550-2649")
    k.add_argument("--eop", action="store_true", help="also the IERS finals2000A Earth-orientation file")

    c = commands.add_parser("chart", help="positions (and houses with --lat/--lon) at one instant")
    c.add_argument("--at", required=True, help="ISO 8601 instant with offset, e.g. 2026-10-06T12:00:00Z")
    c.add_argument("--lat", type=float)
    c.add_argument("--lon", type=float)
    c.add_argument("--houses", default="placidus")
    c.add_argument("--ayanamsa", default=None, help="e.g. lahiri; omit for tropical")
    c.add_argument("--compact", action="store_true", help="use the embedded compact Chebyshev DE440 kernel")
    c.add_argument("--json", action="store_true")

    j = commands.add_parser("jyotish", help="compute full Vedic Jyotish chart summary at one instant")
    j.add_argument("--at", required=True, help="ISO 8601 instant with offset, e.g. 2026-10-06T12:00:00Z")
    j.add_argument("--lat", type=float, default=28.6139, help="observer latitude in degrees")
    j.add_argument("--lon", type=float, default=77.2090, help="observer longitude in degrees")
    j.add_argument("--ayanamsa", default="lahiri", help="sidereal ayanamsa convention (default: lahiri)")
    j.add_argument("--compact", action="store_true", help="use the embedded compact Chebyshev DE440 kernel")
    j.add_argument("--json", action="store_true")

    fs = commands.add_parser("fact-sheet", help="emit deterministic <3KB JSON AI fact sheet")
    fs.add_argument("--at", required=True, help="ISO 8601 instant with offset")
    fs.add_argument("--lat", type=float, default=28.6139)
    fs.add_argument("--lon", type=float, default=77.2090)
    fs.add_argument("--ayanamsa", default="lahiri")
    fs.add_argument("--compact", action="store_true", help="use the embedded compact Chebyshev DE440 kernel")
    fs.add_argument("--max-bytes", type=int, default=3000)

    sv = commands.add_parser("svg", help="render publication-grade Kundali SVG chart")
    sv.add_argument("--at", required=True, help="ISO 8601 instant with offset")
    sv.add_argument("--lat", type=float, default=28.6139)
    sv.add_argument("--lon", type=float, default=77.2090)
    sv.add_argument("--ayanamsa", default="lahiri")
    sv.add_argument(
        "--style",
        choices=("north_indian", "south_indian", "east_indian", "wheel"),
        default="north_indian",
    )
    sv.add_argument("--varga", default="D1")
    sv.add_argument("--theme", choices=("obsidian", "parchment"), default="obsidian")
    sv.add_argument("--compact", action="store_true")
    sv.add_argument("--out", default=None, help="optional output .svg file path")

    ec = commands.add_parser("eclipses", help="find solar and lunar eclipses in a date window")
    ec.add_argument("--start", required=True, help="ISO 8601 start instant with offset")
    ec.add_argument("--end", required=True, help="ISO 8601 end instant with offset")
    ec.add_argument("--lat", type=float, help="optional observer latitude for local circumstances")
    ec.add_argument("--lon", type=float, help="optional observer longitude for local circumstances")
    ec.add_argument("--json", action="store_true")

    pc = commands.add_parser("panchang", help="generate monthly sunrise-anchored Drik Panchang calendar")
    pc.add_argument("--year", type=int, required=True)
    pc.add_argument("--month", type=int, required=True)
    pc.add_argument("--lat", type=float, default=28.6139)
    pc.add_argument("--lon", type=float, default=77.2090)
    pc.add_argument("--tz-offset", type=float, default=5.5)
    pc.add_argument("--json", action="store_true")

    sd = commands.add_parser("siddhanta", help="compute classical Surya Siddhanta epicyclic planetary positions")
    sd.add_argument("--at", required=True, help="ISO 8601 instant with offset")
    sd.add_argument("--json", action="store_true")

    tb = commands.add_parser("table", help="generate tabular ephemeris grid in markdown, csv, or json")
    tb.add_argument("--start", required=True, help="ISO 8601 start instant with offset")
    tb.add_argument("--end", required=True, help="ISO 8601 end instant with offset")
    tb.add_argument("--step-days", type=float, default=1.0)
    tb.add_argument("--format", choices=("markdown", "csv", "json"), default="markdown")

    he = commands.add_parser(
        "human-ephemeris",
        help="generate Human-Readable Classical Ephemeris & Jyotish Academy Manual Calculation Compendium",
    )
    he.add_argument("--year", type=int, required=True, help="Calendar year (e.g. 2026)")
    he.add_argument("--month", type=int, default=11, help="Calendar month 1..12 (default: 11)")
    he.add_argument("--lat", type=float, default=28.6139, help="Observer latitude in degrees")
    he.add_argument("--lon", type=float, default=77.2090, help="Observer longitude in degrees")
    he.add_argument("--tz-offset", type=float, default=5.5, help="Timezone offset in hours from UTC (default: 5.5 IST)")
    he.add_argument("--ayanamsa", default="lahiri", help="Sidereal ayanamsa mode (default: lahiri)")
    he.add_argument("--format", choices=("markdown", "html", "json"), default="markdown")
    he.add_argument("--out", default=None, help="Optional file path to save the compendium")

    mc = commands.add_parser("mcp", help="start built-in Model Context Protocol (MCP) JSON-RPC 2.0 server over stdio")
    mc.add_argument("--dump-tools", action="store_true", help="print MCP tool schemas as JSON and exit")

    sv_api = commands.add_parser("serve", help="start built-in HTTP REST JSON API server with OpenAPI 3.1")
    sv_api.add_argument("--host", default="127.0.0.1", help="bind host (default: 127.0.0.1)")
    sv_api.add_argument("--port", type=int, default=8765, help="bind port (default: 8765)")
    sv_api.add_argument("--dump-openapi", action="store_true", help="print OpenAPI 3.1 JSON and exit")

    imp = commands.add_parser("impossible", help="run sub-second varga cusp, Bayesian birth rectification, personalized fingerprint, and Siddhanta drift solvers")
    imp.add_argument("--at", required=True, help="ISO 8601 instant with offset")
    imp.add_argument("--lat", type=float, default=28.6139)
    imp.add_argument("--lon", type=float, default=77.2090)
    imp.add_argument("--ayanamsa", default="lahiri")
    imp.add_argument("--window-minutes", type=float, default=15.0)
    imp.add_argument("--step-seconds", type=float, default=15.0)

    fp = commands.add_parser("fingerprint", help="compute personalized 16-Varga harmonic phase, clock-confidence decay, and Kaksha transit resonance")
    fp.add_argument("--at", default=None, help="natal ISO 8601 instant with offset")
    fp.add_argument("--jd", type=float, default=None, help="natal Julian Date (UT)")
    fp.add_argument("--query-at", default=None, help="optional transit ISO 8601 instant with offset")
    fp.add_argument("--query-jd", type=float, default=None, help="optional transit Julian Date (UT)")
    fp.add_argument("--lat", type=float, default=28.6139)
    fp.add_argument("--lon", type=float, default=77.2090)
    fp.add_argument("--uncertainty-seconds", "--uncertainty-sec", dest="uncertainty_seconds", type=float, default=60.0)
    fp.add_argument("--ayanamsa", default="lahiri")
    fp.add_argument("--true-node", action="store_true")
    fp.add_argument("--compact", action="store_true")
    fp.add_argument("--json", action="store_true")

    b = commands.add_parser("bench", help="measure public TT body batching")
    b.add_argument("--kernel", help="explicit DE440 file; otherwise use the verified package cache")
    b.add_argument("--samples", type=int, choices=range(2, 257), default=32)
    b.add_argument("--rounds", type=int, choices=range(2, 9), default=2)
    args = parser.parse_args(argv)
    try:
        if args.command == "kernels":
            return _kernels(args)
        if args.command == "chart":
            return _chart(args)
        if args.command == "jyotish":
            return _jyotish(args)
        if args.command == "fact-sheet":
            return _fact_sheet(args)
        if args.command == "svg":
            return _svg(args)
        if args.command == "eclipses":
            return _eclipses(args)
        if args.command == "panchang":
            return _panchang(args)
        if args.command == "siddhanta":
            return _siddhanta(args)
        if args.command == "table":
            return _table(args)
        if args.command == "human-ephemeris":
            from .almanac import generate_human_manual_ephemeris_compendium

            comp = generate_human_manual_ephemeris_compendium(
                args.year,
                args.month,
                latitude_deg=args.lat,
                longitude_deg=args.lon,
                tz_offset_hours=args.tz_offset,
                ayanamsa=args.ayanamsa,
            )
            if args.format == "html":
                rendered = comp.to_html()
            elif args.format == "json":
                rendered = json.dumps(comp.to_dict(), indent=2, sort_keys=True) + "\n"
            else:
                rendered = comp.to_markdown()
            if args.out:
                out_path = Path(args.out)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(rendered, encoding="utf-8", newline="\n")
            else:
                print(rendered, end="")
            return 0
        if args.command == "mcp":
            from .mcp_server import main as mcp_main

            return mcp_main(["--dump-tools"] if args.dump_tools else [])
        if args.command == "serve":
            from .api_server import main as api_main

            api_argv = ["--host", str(args.host), "--port", str(args.port)]
            if args.dump_openapi:
                api_argv.append("--dump-openapi")
            return api_main(api_argv)
        if args.command == "impossible":
            from .impossible_astrology import (
                analyze_siddhanta_vs_jpl_de440_drift,
                compute_personalized_astro_fingerprint,
                rectify_birth_time_bayesian,
                solve_subsecond_shodashvarga_cusp_transitions,
            )

            t = _instant(args.at)
            jd_ut = _datetime_to_jd(t)
            cusps = solve_subsecond_shodashvarga_cusp_transitions(
                jd_ut,
                args.lat,
                args.lon,
                ayanamsa=args.ayanamsa,
            )
            rect = rectify_birth_time_bayesian(
                jd_ut,
                args.lat,
                args.lon,
                window_minutes=args.window_minutes,
                step_seconds=args.step_seconds,
                ayanamsa=args.ayanamsa,
            )
            drift = analyze_siddhanta_vs_jpl_de440_drift(jd_ut, ayanamsa=args.ayanamsa)
            fp_res = compute_personalized_astro_fingerprint(
                jd_ut,
                args.lat,
                args.lon,
                ayanamsa=args.ayanamsa,
            )
            payload = {
                "at": t.isoformat(),
                "jd_ut": jd_ut,
                "most_sensitive_varga": cusps.most_sensitive_varga,
                "minimum_ascendant_cusp_margin_seconds": cusps.minimum_ascendant_cusp_margin_seconds,
                "rectified_jd_ut": rect.rectified_jd_ut,
                "rectified_offset_seconds": rect.offset_seconds,
                "best_rectification_score": rect.best_candidate.total_score,
                "siddhanta_mean_abs_delta_deg": drift.mean_abs_delta_deg,
                "siddhanta_max_abs_delta_deg": drift.max_abs_delta_deg,
                "fingerprint_id_sha256": fp_res.fingerprint_id_sha256,
                "overall_clock_confidence_score": fp_res.overall_clock_confidence_score,
                "overall_personal_transit_resonance_score": fp_res.overall_personal_transit_resonance_score,
                "receipts": {
                    "cusps_sha256": cusps.receipt_sha256,
                    "rectification_sha256": rect.receipt_sha256,
                    "siddhanta_drift_sha256": drift.receipt_sha256,
                    "fingerprint_sha256": fp_res.receipt_sha256,
                },
            }
            json.dump(_jsonable(payload), sys.stdout, indent=2, sort_keys=True, default=str)
            print()
            return 0
        if args.command == "fingerprint":
            from .impossible_astrology import compute_personalized_astro_fingerprint

            if args.jd is not None:
                jd_ut = float(args.jd)
            elif args.at is not None:
                jd_ut = _datetime_to_jd(_instant(args.at))
            else:
                raise ValueError("either --at or --jd is required for fingerprint")

            if args.query_jd is not None:
                q_jd = float(args.query_jd)
            elif args.query_at is not None:
                q_jd = _datetime_to_jd(_instant(args.query_at))
            else:
                q_jd = None

            fp_res = compute_personalized_astro_fingerprint(
                jd_ut,
                args.lat,
                args.lon,
                query_jd_ut=q_jd,
                birth_time_uncertainty_seconds=args.uncertainty_seconds,
                ayanamsa=args.ayanamsa,
                true_node=bool(args.true_node),
            )
            if args.json:
                json.dump(_jsonable(fp_res), sys.stdout, indent=2, sort_keys=True, default=str)
                print()
            else:
                print(f"Fingerprint ID (SHA-256): {fp_res.fingerprint_id_sha256}")
                print(
                    f"Atmakaraka: {fp_res.atmakaraka_planet} | Amatyakaraka: {fp_res.amatyakaraka_planet} | "
                    f"Dominant Vimshopaka: {fp_res.dominant_vimshopaka_planet} | Dominant Digbala: {fp_res.dominant_digbala_planet}"
                )
                print(
                    f"Clock Confidence ({fp_res.birth_time_uncertainty_seconds:.1f}s uncertainty): "
                    f"{fp_res.overall_clock_confidence_score:.4f} | Personal Transit Resonance: "
                    f"{fp_res.overall_personal_transit_resonance_score:.2f}/100"
                )
                print(f"Receipt SHA-256: {fp_res.receipt_sha256}")
            return 0
        from .researcher_benchmark import measure

        configured = {"DE440": Path(args.kernel)} if args.kernel else "auto"
        with Engine.load(kernels=configured, cache_dir=args.cache, eop=None) as engine:
            json.dump(measure(engine, samples=args.samples, rounds=args.rounds), sys.stdout, indent=2)
        print()
        return 0
    except (EphemerisError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
