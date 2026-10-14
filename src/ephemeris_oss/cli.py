"""Command line: ``ephemeris-oss kernels fetch --verify``, ``chart --json``, ``bench``."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import kernels
from ._api import Engine, EphemerisError, Houses, Undefined

BODIES = ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto")


def _instant(text: str) -> datetime:
    value = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if value.tzinfo is None:
        raise SystemExit("--at needs a UTC offset, for example 2026-10-06T12:00:00Z")
    return value.astimezone(timezone.utc)


def _jsonable(value: Any) -> Any:
    if isinstance(value, (Houses, Undefined)):
        return {"type": type(value).__name__, **value.__dict__}
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
    with Engine.load(cache_dir=args.cache) as eng:
        positions = eng.positions(t, bodies=BODIES, ayanamsa=args.ayanamsa)
        payload: dict[str, Any] = {
            "at": t.isoformat(),
            "ayanamsa": args.ayanamsa,
            "positions": {body: {"longitude_deg": place["longitude_deg"], "latitude_deg": place.get("latitude_deg")}
                          for body, place in positions.value.items()},
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
    c.add_argument("--json", action="store_true")

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
