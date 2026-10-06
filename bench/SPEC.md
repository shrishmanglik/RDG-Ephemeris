# Benchmark method (v0, draft)

The benchmark answers one question per row: how far is an engine's output from the JPL truth, measured so that any
reader can rerun it and get the same bytes. Nothing in `bench/` ships in the wheel or is imported by the package.

## Truth

- **T1, JPL Horizons.** The vectors API (`https://ssd.jpl.nasa.gov/api/horizons.api`), `EPHEM_TYPE=VECTORS`,
  `CENTER='500@399'` (geocentre), `REF_PLANE=FRAME`, `REF_SYSTEM=ICRF`, `OUT_UNITS=AU-D`, `CSV_FORMAT=YES`,
  `TIME_TYPE=TDB`, `TLIST_TYPE=JD`, `TLIST` = exact JD TDB values written with 9 decimals. `VEC_CORR` is `NONE`
  (geometric), `LT` (astrometric) or `LT+S` (apparent direction). The echoed epoch of every row is recorded and
  must equal the requested JD to the printed precision, or the response is VOID. Raw responses are committed under
  `bench/data/horizons/` named by their SHA-256, with a manifest (`manifest.json`) listing request URL, retrieval
  time, sha256 and the DE version Horizons reports. At most 1 request per second; at most 300 instants per stratum set.
- **T2, raw kernel.** Skyfield (MIT) reading the same DE440/DE441 file through jplephem: an independent reader of the
  kernel. It is the full-sample truth.
- **Truth floor** = P99 of the angular separation |T1 - T2| over the T1 subsample, per mode. Any engine error below
  the floor is reported as a tie with truth, never as a value.

## Samples

Seeded (`seed` recorded in every result), strata = body x era x mode.
- Bodies: sun, moon, mercury, venus, mars, jupiter, saturn, uranus, neptune, pluto (NAIF 10, 301, 199, 299, 4..9;
  outer planets as system barycentres, the engine's documented choice).
- Eras: `E1` 1900-2026 (births), `E2` 2026-2040 (transits), `E3` 1550-1899, `E4` 2041-2649 (both DE440). DE441 eras
  (before 1550, after 2649) are added only when DE441 is provisioned.
- Modes: `geometric`, `astrometric`, `apparent`.
- Sample file: JSON Lines, one object per row: `{"id", "body", "era", "mode", "jd_tdb"}`; `jd_tdb` as a decimal string
  with 9 decimals so every engine and Horizons receive the identical instant. The sample file's SHA-256 is part of
  every scorecard.

## Engines and their outputs

Every engine returns, per sample id, a geocentric unit direction in ICRF (x, y, z) for the requested mode, plus the
distance in au where the engine provides it. Engines that only emit ecliptic-of-date angles are converted to ICRF by
the harness with one documented ERFA rotation (IAU 2006/2000A, `pnm06a` then `ecm06` inverse), the same code for
every such engine, and the conversion's own round-trip error is reported.

Copyleft engines (pyswisseph, libephemeris) run only as separate processes from `bench/comparators/<name>/` in their
own virtual environments, reading the sample file and writing a results file. The harness never imports them.

## Statistics

Per stratum and engine: n, median, P95, max of (a) angular separation in arcseconds and (b) the maximum of the
longitude and latitude component differences on the ecliptic of date (the statistic the earlier internal scorecard
used), each with a bootstrap 95% interval (seeded, 2,000 resamples, percentile method). Both statistics are always
shown, because they differ by up to a factor of about the square root of two and cannot be compared across rows.

## Controls (each must fire every run, or the run is VOID)

- +1" added to our Moon makes the fidelity row FAIL.
- One altered byte in a committed Horizons response makes the run VOID (hash mismatch).
- Swiss against Swiss gives exactly 0.
- A missing kernel gives VOID, never a skipped pass.
- Two scorecard runs are byte-identical; timings live only in `speed-*.json`.

## Speed (separate file, never in the scorecard)

Interleaved A/B rounds, an A/A control that must land in 0.9 to 1.1, the machine and Python stated, the heavy slot
held throughout.
