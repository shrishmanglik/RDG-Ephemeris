# Public deterministic interface

`Engine` owns kernel verification, explicit time/frame conventions, numerical
calculation and source-bound receipts. Callers need not assemble providers.

```python
from ephemeris_oss import Engine

with Engine.load(kernels="auto", eop=None) as engine:
    result = engine.positions_tt(2451545.0, bodies=("sun", "moon"))
    print(result.value["moon"]["longitude_deg"])
    print(result.receipt)
```

For remote epochs, supply both dynamical time scales and request the mean
ecliptic explicitly. The verified DE441 parts must cover every required state,
including light-time emission instants:

```python
result = engine.positions_tt(
    jd_tt=-1_000_000.0, bodies=("sun", "moon"),
    jd_tdb=-1_000_000.0, mean_equinox=True,
)
```

The equal TT/TDB values above illustrate the interface; callers who need precise
timing must supply their actual conversion. A one-second consistency guard
rejects unrelated epochs, but does not certify a supplied subsecond conversion.
Outside TT years 1600..2400 the API refuses omitted TDB and true-ecliptic output.
Mean frames use long-term precession across the declared DE441 interval. UTC,
UT1, Earth orientation, stellar propagation and physical-model accuracy have
separate validity and evidence requirements. Neither data coverage nor reader
agreement establishes a universal apparent-position precision bound.

`positions()` accepts a timezone-aware UTC datetime in the documented validity
window. `ayanamsa()`, `houses()`, `nodes()` and `rise_set()` use their documented
input types and return a Result with value and receipt. Observer/Earth-orientation
inputs are explicit. Undefined geometry stays an Undefined value with a reason.
No model may supply missing numerical facts.
