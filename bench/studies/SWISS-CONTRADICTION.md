# Study: the two Swiss accuracy measurements that disagree by 10x

Two earlier internal measurements of Swiss Ephemeris accuracy against JPL gave a P95 of 0.105" and 0.0091". This
study measures four candidate causes separately on one sample: (a) the truth (T1, JPL Horizons, against T2,
Skyfield reading DE440), (b) the quantity (geometric against apparent), (c) the statistic (angular separation against
the larger ecliptic-of-date component) and (d) the Swiss data files (the 2014 DE431-based `sepl_18`/`semo_18`
against the 2026 DE441-based set).

Reproduce with `python -m bench.studies.swiss_contradiction` (arguments in the script's docstring). Every number
below is quoted from `bench/data/studies/swiss-contradiction-result.json`; two runs produced byte-identical files
(sha256 `ceaa879dd7407a32b6fdde44a8cf4e708851f2beeb9b5a9efe2878fa5db57cfd`).

## Sample and setup

- Seed 20261006; 10 bodies x 30 instants, uniform in JD TDB over [2415020.5, 2466520.5) (1900-01-01 up to
  2041-01-01), the same 30 instants in both modes: 600 rows. Sample sha256
  `0cb45358868db0ac907f6c7ec0703d1054e0de55ae645a8e0fe7a32161f7689e`.
- T1: 20 Horizons responses (one per body and mode), Horizons names `DE441`; `NONE` for geometric, `LT+S` for apparent.
- T2 and our engine through `bench/harness/engines.py` on the pinned DE440 kernel.
- Swiss 2.10.03 through `bench/comparators/swiss/run_swiss.py`, four configurations (status below).
- Bootstrap: 2,000 seeded resamples, percentile method, seed per row derived from 20261006 and the row key.
- Truth floor (P99 of the T1 to T2 separation): **geometric 0.001604174312"**, **apparent 0.12972274635"**. Any value
  below its mode's floor is written as "tie".

## Engine status

| configuration | exit | status |
|---|---|---|
| ours | n/a | OK |
| swiss-swieph-2014 (2014 files) | 0 | OK, 600 rows |
| swiss-swieph-2026 (2026 files) | 0 | OK, 600 rows |
| swiss-jpl-de440 (`--ephemeris jpl` on the DE440 `.bsp`) | 2 | **VOID**: "sun-S1-geometric-00000 fell back from the requested ephemeris (retflags 138868)" |
| swiss-moshier | 0 | OK, 600 rows |

The JPL configuration is VOID: Swiss did not use the DE440 kernel for the first row and fell back, which the runner
treats as VOID. The runner reports the fallback flags only; it does not print Swiss's own error string, so the
reason Swiss could not use the file is not recorded here.

## Table (arcsec)

| engine | truth | mode | statistic | n | median | P95 | P95 95% CI | max |
|---|---|---|---|---|---|---|---|---|
| ours | T1 | geometric | separation | 300 | tie | tie | [tie, tie] | 0.002788 |
| ours | T1 | geometric | ecliptic_max_component | 300 | tie | tie | [tie, tie] | 0.002786 |
| ours | T1 | apparent | separation | 300 | tie | tie | [tie, tie] | 0.157566 |
| ours | T1 | apparent | ecliptic_max_component | 300 | tie | tie | [tie, tie] | 0.153524 |
| ours | T2 | geometric | separation | 300 | tie | tie | [tie, tie] | tie |
| ours | T2 | geometric | ecliptic_max_component | 300 | tie | tie | [tie, tie] | tie |
| ours | T2 | apparent | separation | 300 | tie | tie | [tie, tie] | tie |
| ours | T2 | apparent | ecliptic_max_component | 300 | tie | tie | [tie, tie] | tie |
| swiss-swieph-2014 | T1 | geometric | separation | 300 | tie | 0.067800 | [0.038226, 0.077190] | 0.188743 |
| swiss-swieph-2014 | T1 | geometric | ecliptic_max_component | 300 | tie | 0.068006 | [0.037462, 0.076880] | 0.188732 |
| swiss-swieph-2014 | T1 | apparent | separation | 300 | tie | tie | [tie, tie] | 0.188990 |
| swiss-swieph-2014 | T1 | apparent | ecliptic_max_component | 300 | tie | tie | [tie, tie] | 0.188980 |
| swiss-swieph-2014 | T2 | geometric | separation | 300 | tie | 0.067800 | [0.038321, 0.077190] | 0.188743 |
| swiss-swieph-2014 | T2 | geometric | ecliptic_max_component | 300 | tie | 0.068006 | [0.037118, 0.076880] | 0.188732 |
| swiss-swieph-2014 | T2 | apparent | separation | 300 | tie | tie | [tie, tie] | 0.188743 |
| swiss-swieph-2014 | T2 | apparent | ecliptic_max_component | 300 | tie | tie | [tie, tie] | 0.188732 |
| swiss-swieph-2026 | T1 | geometric | separation | 300 | tie | tie | [tie, tie] | 0.005768 |
| swiss-swieph-2026 | T1 | geometric | ecliptic_max_component | 300 | tie | tie | [tie, tie] | 0.005608 |
| swiss-swieph-2026 | T1 | apparent | separation | 300 | tie | tie | [tie, tie] | 0.157438 |
| swiss-swieph-2026 | T1 | apparent | ecliptic_max_component | 300 | tie | tie | [tie, tie] | 0.153390 |
| swiss-swieph-2026 | T2 | geometric | separation | 300 | tie | tie | [tie, 0.001698] | 0.005768 |
| swiss-swieph-2026 | T2 | geometric | ecliptic_max_component | 300 | tie | tie | [tie, 0.001732] | 0.005608 |
| swiss-swieph-2026 | T2 | apparent | separation | 300 | tie | tie | [tie, tie] | tie |
| swiss-swieph-2026 | T2 | apparent | ecliptic_max_component | 300 | tie | tie | [tie, tie] | tie |
| swiss-moshier | T1 | geometric | separation | 300 | 0.103549 | 0.765949 | [0.598188, 0.979279] | 2.367286 |
| swiss-moshier | T1 | geometric | ecliptic_max_component | 300 | 0.090076 | 0.685881 | [0.574154, 0.840003] | 2.065136 |
| swiss-moshier | T1 | apparent | separation | 300 | tie | 0.765799 | [0.603184, 0.979363] | 2.367523 |
| swiss-moshier | T1 | apparent | ecliptic_max_component | 300 | tie | 0.680542 | [0.535198, 0.918185] | 2.065412 |
| swiss-moshier | T2 | geometric | separation | 300 | 0.103548 | 0.765992 | [0.598562, 0.979437] | 2.366784 |
| swiss-moshier | T2 | geometric | ecliptic_max_component | 300 | 0.090075 | 0.685862 | [0.536123, 0.841741] | 2.064576 |
| swiss-moshier | T2 | apparent | separation | 300 | tie | 0.765999 | [0.598162, 0.977776] | 2.367022 |
| swiss-moshier | T2 | apparent | ecliptic_max_component | 300 | tie | 0.685782 | [0.533738, 0.841013] | 2.064853 |

## What moves Swiss's P95

All comparisons below are geometric unless stated, because the apparent floor (0.12972274635") is larger than every
Swiss P95 in this sample except Moshier's, so the apparent rows cannot separate the data files at all.

1. **(d) Data files: the only factor that moves Swiss's P95 beyond its interval.** Against T2, geometric separation,
   the 2014 files give P95 0.0678" (interval [0.038321, 0.077190]); the 2026 files give "tie", that is below
   0.001604174312", with the interval's upper end at 0.001698". The 2014 P95 is therefore at least about 42 times the
   2026 one (0.067800 / 0.001604). Per body (P95 separation against T2, 2014 files): neptune 0.143054", uranus
   0.079255", pluto 0.069638", jupiter 0.014320", mars 0.003762", moon 0.002334", venus 0.002300"; sun, mercury and
   saturn tie. With the 2026 files every body ties except moon 0.002045" and venus 0.002941".
2. **(a) Truth: no effect at P95.** The 2014 files give P95 0.067800" against both T1 and T2, interval
   [0.038226, 0.077190] against T1 and [0.038321, 0.077190] against T2. T1 and T2 differ geometrically by a median of
   0.000000076" and a P95 of 0.000582" over the sample; the Moon carries almost all of it (Moon P95 0.001777",
   every other body at or below 0.0000011").
3. **(c) Statistic: no material effect.** 2014 files against T2: separation P95 0.067800", ecliptic max-component
   P95 0.068006" (0.3 percent apart, intervals overlapping).
4. **(b) Quantity: the apparent comparison is floored, not better.** In apparent mode every Swiss file
   configuration and our engine tie with truth at median and P95, because T1 and T2 themselves disagree by up to
   0.157566" (P95 0.044346", floor 0.12972274635"). By body, the T1 to T2 apparent P95 is venus 0.091715", uranus
   0.068616", jupiter 0.049866", pluto 0.042152", neptune 0.030338", mars 0.032319", saturn 0.027806", mercury
   0.025511", moon 0.001777", sun 0.00000079". This study does not measure why; the sun being near zero is consistent
   with a difference in gravitational deflection between Horizons `LT+S` vectors and Skyfield's `apparent()`, and that
   is a hypothesis, not a result.
5. **Moshier** is far from both: geometric P95 0.765992" against T2 (interval [0.598562, 0.979437]).

Neither earlier figure is reproduced exactly, because the sample differs. In this sample the 2014 files land at the
same order as the larger figure (P95 0.0678") and the 2026 files below the 0.0016" floor, so the file vintage is the
factor consistent with a 10x gap; truth, statistic and mode do not produce it.

## Swiss with the 2026 files against our engine

At P95 both are ties with truth in every row: geometric and apparent, against T1 and T2, on both statistics. Their
P95 values cannot be ordered; this is a **tie**, not a finding that either is closer to JPL. Beyond P95, against T2
our engine ties at max as well, while Swiss 2026 has a geometric max of 0.005768" (separation) and a P95 interval
upper end of 0.001698", just above the floor.

## Deviations and open items

- **Horizons echo.** 8 of 600 rows (4 instants, each in both modes: moon 00011, neptune 00000, pluto 00023, uranus
  00012) came back with an echoed JD one unit in the 9th decimal away from the request (1e-9 day, 86.4 microseconds).
  `bench/truth/horizons.py` treats any such echo as VOID, and its `verify` over the shared manifest now returns VOID on
  response `9c4bbc6a...`. This study accepts a 1e-9 day echo offset and counts the rows (`horizons_echo` in the
  result); the SPEC rule and the fetcher are unchanged and need a decision.
- **Swiss through DE440** is VOID as above.
- Pluto is the system barycentre in T1, T2 and our engine (NAIF 9); Swiss body 9 is used as the runner defines it.
  This study does not separate that choice from the file effect for Pluto.
