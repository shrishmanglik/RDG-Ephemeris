"""Command line: ``ephemeris-oss kernels``, ``chart``, ``jyotish``, ``eclipses``, ``fact-sheet``, ``bench``."""

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
            b: float(place.get("longitude_speed_deg_per_day", 0.0))
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
            b: float(place.get("longitude_speed_deg_per_day", 0.0))
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

    ec = commands.add_parser("eclipses", help="find solar and lunar eclipses in a date window")
    ec.add_argument("--start", required=True, help="ISO 8601 start instant with offset")
    ec.add_argument("--end", required=True, help="ISO 8601 end instant with offset")
    ec.add_argument("--lat", type=float, help="optional observer latitude for local circumstances")
    ec.add_argument("--lon", type=float, help="optional observer longitude for local circumstances")
    ec.add_argument("--json", action="store_true")

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
        if args.command == "eclipses":
            return _eclipses(args)
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
