"""T1 truth: geocentric ICRF vectors from the JPL Horizons API, stored by hash.

Contract: ``bench/SPEC.md`` section Truth, T1. Standard library only, so it runs on any
Python 3.9+ without a virtual environment.

What the Horizons API documentation says, read 2026-10-06 from
https://ssd-api.jpl.nasa.gov/doc/horizons.html:

- ``TLIST`` accepts "up to 10,000" discrete output times, as JD, MJD or calendar dates;
  ``TLIST_TYPE`` ('JD', 'MJD', 'CAL') overrides the magnitude-based type guess. Values in a
  GET URL are URL-encoded (space %20, quote %27).
- ``VEC_TABLE`` 1 is position only, 2 adds velocity. This fetcher uses **1**: the benchmark
  scores directions and distances, so velocity would only enlarge every committed response.
- ``VEC_CORR`` is 'NONE' (geometric), 'LT' (light-time corrected) or 'LT+S' (light time plus
  stellar aberration).

What ``LT+S`` vectors do not contain: gravitational light deflection. Every stored LT+S response
says so in its own footer ("corrected for Newtonian down-leg (receive) light-time displacement
and relativistic stellar aberration"), and the Horizons manual
(https://ssd.jpl.nasa.gov/horizons/manual.html, read 2026-10-06) lists the vector-table
corrections as "LT+S (light-time & stellar aberration)", while its observer-table quantities
name "the gravitational deflection of light" separately. So ``LT+S`` truth scores the
benchmark mode ``apparent-aberrated`` only; the mode ``apparent`` (with deflection) has no
Horizons vector equivalent and is scored against T2 alone (``bench/SPEC.md``).
- ``REF_SYSTEM`` 'ICRF' or 'B1950'; ``OUT_UNITS`` 'KM-S', 'AU-D' or 'KM-D'; ``CSV_FORMAT``
  'YES' or 'NO'; ``TIME_TYPE`` 'UT', 'TT' or 'TDB'.
- The JSON reply carries ``signature`` {``version``, ``source``} and ``result`` (the text
  ephemeris). No rate limit or URL length limit is documented.

The documented TLIST ceiling is 10,000, but every request here is a GET whose URL grows by
about 24 characters per epoch, so requests are cut at ``CHUNK`` = 100 epochs (about 2.5 kB of
query string). That is a choice made for URL hygiene, not a Horizons limit. SPEC caps a stratum
set at 300 instants, so a full set is three requests.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from decimal import Decimal
from pathlib import Path

API_URL = "https://ssd.jpl.nasa.gov/api/horizons.api"
USER_AGENT = (
    "ephemeris-bench-truth/0.1 (+benchmark T1 truth fetcher; Python urllib; "
    "at most 1 request per second)"
)
CHUNK = 100
MIN_INTERVAL_S = 1.0
VEC_CORRS = ("NONE", "LT", "LT+S")
# ``apparent`` (with deflection) is absent on purpose: no VEC_CORR value deflects light.
MODE_TO_VEC_CORR = {"geometric": "NONE", "astrometric": "LT", "apparent-aberrated": "LT+S"}
# An echoed epoch may differ from the request by at most this many units of its last printed digit.
ECHO_TOLERANCE_UNITS = 1
BODY_TO_NAIF = {
    "sun": 10, "moon": 301, "mercury": 199, "venus": 299, "mars": 4,
    "jupiter": 5, "saturn": 6, "uranus": 7, "neptune": 8, "pluto": 9,
}
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DIR = REPO_ROOT / "bench" / "data" / "horizons"

_JD_RE = re.compile(r"^\d{7}\.\d{9}$")
_SOURCE_RE = re.compile(r"^Target body name:.*\{source:\s*([^}]+?)\s*\}", re.MULTILINE)
_last_request = None  # time.monotonic() of the previous network request, or None


class VoidRun(Exception):
    """The stored truth cannot be trusted; the run that reads it is VOID."""


class HorizonsError(Exception):
    """Horizons answered, but not with an ephemeris."""


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_request(body_naif_id: int, jd_tdb_strings: list[str], vec_corr: str) -> str:
    """Return the GET URL for one body, one correction and up to ``CHUNK`` JD TDB epochs.

    The JD strings go into TLIST byte for byte; they must carry exactly 9 decimals so that
    every engine and Horizons receive the identical instant.
    """
    if vec_corr not in VEC_CORRS:
        raise ValueError(f"vec_corr must be one of {VEC_CORRS}, got {vec_corr!r}")
    if not jd_tdb_strings:
        raise ValueError("no epochs")
    if len(jd_tdb_strings) > CHUNK:
        raise ValueError(f"{len(jd_tdb_strings)} epochs exceeds the chunk of {CHUNK}")
    for jd in jd_tdb_strings:
        if not _JD_RE.match(jd):
            raise ValueError(f"JD must be written with 9 decimals: {jd!r}")
    params = [
        ("format", "json"),
        ("COMMAND", f"'{int(body_naif_id)}'"),
        ("OBJ_DATA", "'NO'"),
        ("MAKE_EPHEM", "'YES'"),
        ("EPHEM_TYPE", "'VECTORS'"),
        ("CENTER", "'500@399'"),
        ("REF_PLANE", "'FRAME'"),
        ("REF_SYSTEM", "'ICRF'"),
        ("OUT_UNITS", "'AU-D'"),
        ("CSV_FORMAT", "'YES'"),
        ("VEC_TABLE", "'1'"),
        ("VEC_LABELS", "'NO'"),
        ("VEC_CORR", f"'{vec_corr}'"),
        ("TIME_TYPE", "'TDB'"),
        ("TLIST_TYPE", "'JD'"),
        ("TLIST", " ".join(f"'{jd}'" for jd in jd_tdb_strings)),
    ]
    return API_URL + "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote, safe="")


def tlist_values(url: str) -> list[str]:
    """The JD strings a request URL actually carries, decoded back out of TLIST."""
    q = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
    return re.findall(r"'([^']+)'", q["TLIST"][0])


def _result_text(response: bytes) -> str:
    doc = json.loads(response.decode("utf-8"))
    if "error" in doc:
        raise HorizonsError(doc["error"])
    return doc["result"]


def parse(response: bytes) -> list[dict]:
    """Rows of the CSV block between $$SOE and $$EOE: echoed JD exactly as printed, x, y, z (au)."""
    text = _result_text(response)
    if "$$SOE" not in text or "$$EOE" not in text:
        raise HorizonsError(text.strip()[-2000:])
    block = text.split("$$SOE", 1)[1].split("$$EOE", 1)[0]
    rows = []
    for line in block.strip().splitlines():
        cells = [c.strip() for c in line.split(",")]
        rows.append({
            "jd_tdb_echoed": cells[0],
            "x": float(cells[2]),
            "y": float(cells[3]),
            "z": float(cells[4]),
        })
    return rows


def ephemeris_source(response: bytes) -> str:
    """The planetary ephemeris Horizons names on its Target body line, e.g. ``DE441``."""
    m = _SOURCE_RE.search(_result_text(response))
    return m.group(1) if m else ""


def echo_offset_units(echoed: str, requested: str) -> int:
    """Signed offset of the echo from the request, in units of the echo's last printed digit.

    Horizons reads each TLIST value as a binary double and prints it back with 9 decimals, so
    an echo can land one unit (1e-9 day, 86.4 us) from the request. The offset is recorded,
    never applied: every engine and the truth row keep the requested JD.
    """
    decimals = len(echoed.split(".")[1]) if "." in echoed else 0
    quantum = Decimal(1).scaleb(-decimals)
    return int((Decimal(echoed) - Decimal(requested).quantize(quantum)) / quantum)


def _match_echoes(rows: list[dict], requested: list[str], label: str) -> dict[str, dict]:
    """Pair each requested JD with its echoed row, or raise VoidRun.

    Horizons prints a TLIST ephemeris in ascending time order, not request order (observed
    on the first pilot request, 2026-10-06), so rows are paired by value: both sides sorted
    by instant, then each pair must agree within ``ECHO_TOLERANCE_UNITS`` of the last printed
    digit. Each paired row carries its ``echo_offset_units``.
    """
    if len(rows) != len(requested):
        raise VoidRun(f"{label}: {len(rows)} rows for {len(requested)} requested epochs")
    by_time = sorted(rows, key=lambda r: Decimal(r["jd_tdb_echoed"]))
    paired: dict[str, dict] = {}
    for row, jd in zip(by_time, sorted(requested, key=Decimal)):
        offset = echo_offset_units(row["jd_tdb_echoed"], jd)
        if abs(offset) > ECHO_TOLERANCE_UNITS:
            raise VoidRun(f"{label}: echo {row['jd_tdb_echoed']} != requested {jd} ({offset:+d} units)")
        paired[jd] = dict(row, echo_offset_units=offset)
    return paired


def _load_manifest(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"entries": []}


def _write_manifest(path: Path, manifest: dict) -> None:
    path.write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def _throttle() -> None:
    global _last_request
    if _last_request is not None:
        wait = MIN_INTERVAL_S - (time.monotonic() - _last_request)
        if wait > 0:
            time.sleep(wait)
    _last_request = time.monotonic()


def fetch(url: str, out_dir: Path = DEFAULT_DIR) -> dict:
    """GET ``url`` once ever: store the raw body by SHA-256 and record it in the manifest.

    A URL already in the manifest is returned from the manifest without a request.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / "manifest.json"
    manifest = _load_manifest(manifest_path)
    for entry in manifest["entries"]:
        if entry["url"] == url:
            return entry
    _throttle()
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as resp:
        raw = resp.read()
    retrieved = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rows = parse(raw)  # raises HorizonsError before anything is stored
    requested = tlist_values(url)
    if len(rows) != len(requested):
        raise HorizonsError(f"asked for {len(requested)} epochs, got {len(rows)} rows")
    sha = sha256_hex(raw)
    (out_dir / f"{sha}.json").write_bytes(raw)
    doc = json.loads(raw.decode("utf-8"))
    q = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
    entry = {
        "url": url,
        "body": int(q["COMMAND"][0].strip("'")),
        "vec_corr": q["VEC_CORR"][0].strip("'"),
        "n_epochs": len(requested),
        "jd_tdb_requested": requested,
        "retrieved_utc": retrieved,
        "sha256": sha,
        "horizons_signature_version": doc.get("signature", {}).get("version", ""),
        "horizons_signature_source": doc.get("signature", {}).get("source", ""),
        "ephemeris_source": ephemeris_source(raw),
    }
    manifest["entries"].append(entry)
    _write_manifest(manifest_path, manifest)
    return entry


def verify(manifest_path: Path) -> int:
    """Recheck every stored response against the manifest; raise VoidRun on any mismatch.

    Returns the number of responses verified; ``verify_report`` also lists the echo offsets.
    """
    return verify_report(manifest_path)["responses"]


def verify_report(manifest_path: Path) -> dict:
    """Check the SHA-256 of each stored file and every echoed JD; raise VoidRun on a mismatch.

    An echo within ``ECHO_TOLERANCE_UNITS`` of the request passes and is listed under
    ``echo_offsets`` (sorted by response and requested JD); anything further is VOID.
    """
    manifest_path = Path(manifest_path)
    store = manifest_path.parent
    manifest = _load_manifest(manifest_path)
    offsets = []
    for entry in manifest["entries"]:
        path = store / f"{entry['sha256']}.json"
        if not path.exists():
            raise VoidRun(f"missing response {path.name}")
        raw = path.read_bytes()
        actual = sha256_hex(raw)
        if actual != entry["sha256"]:
            raise VoidRun(f"sha256 mismatch for {path.name}: file hashes to {actual}")
        paired = _match_echoes(parse(raw), entry["jd_tdb_requested"], path.name)
        for jd, row in paired.items():
            if row["echo_offset_units"]:
                offsets.append({"sha256": entry["sha256"], "jd_tdb_requested": jd,
                                "jd_tdb_echoed": row["jd_tdb_echoed"],
                                "offset_units": row["echo_offset_units"]})
    offsets.sort(key=lambda o: (o["sha256"], Decimal(o["jd_tdb_requested"])))
    return {"responses": len(manifest["entries"]), "echo_offsets": offsets}


def _group(samples: list[dict], max_per_set: int) -> dict[tuple[str, str], list[dict]]:
    groups: dict[tuple[str, str], list[dict]] = {}
    for row in samples:
        key = (row["body"], row["mode"])
        bucket = groups.setdefault(key, [])
        if len(bucket) < max_per_set:
            bucket.append(row)
    return groups


def build_truth(samples_path: Path, max_per_set: int, out_dir: Path = DEFAULT_DIR) -> Path:
    raw_samples = Path(samples_path).read_bytes()
    sample_sha = sha256_hex(raw_samples)
    samples = [json.loads(line) for line in raw_samples.decode("utf-8").splitlines() if line.strip()]
    truth: dict[str, dict] = {}
    for (body, mode), rows in _group(samples, max_per_set).items():
        if mode not in MODE_TO_VEC_CORR:
            continue  # ``apparent`` has no Horizons vector equivalent; T2 alone scores it
        naif, vec_corr = BODY_TO_NAIF[body], MODE_TO_VEC_CORR[mode]
        for i in range(0, len(rows), CHUNK):
            chunk = rows[i:i + CHUNK]
            entry = fetch(build_request(naif, [r["jd_tdb"] for r in chunk], vec_corr), out_dir)
            parsed = parse((Path(out_dir) / f"{entry['sha256']}.json").read_bytes())
            paired = _match_echoes(parsed, [r["jd_tdb"] for r in chunk], entry["sha256"])
            for sample in chunk:
                got = paired[sample["jd_tdb"]]
                truth[sample["id"]] = {
                    "id": sample["id"], "x": got["x"], "y": got["y"], "z": got["z"],
                    "jd_echoed": got["jd_tdb_echoed"], "response_sha256": entry["sha256"],
                    "echo_offset_units": got["echo_offset_units"],
                }
    verify(Path(out_dir) / "manifest.json")
    out = Path(out_dir) / f"t1-{sample_sha[:12]}.jsonl"
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        for row in samples:
            if row["id"] in truth:
                fh.write(json.dumps(truth[row["id"]], sort_keys=True) + "\n")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--samples", required=True, type=Path, help="sample JSON Lines file")
    ap.add_argument("--max-per-set", type=int, default=300, help="instants per (body, mode) set")
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_DIR)
    args = ap.parse_args(argv)
    out = build_truth(args.samples, args.max_per_set, args.out_dir)
    n = sum(1 for _ in out.open(encoding="utf-8"))
    print(f"wrote {n} truth rows to {out.relative_to(REPO_ROOT) if out.is_relative_to(REPO_ROOT) else out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
