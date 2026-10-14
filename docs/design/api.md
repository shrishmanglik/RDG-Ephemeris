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

`positions()` accepts a timezone-aware UTC datetime in the documented validity
window. `ayanamsa()`, `houses()`, `nodes()` and `rise_set()` use their documented
input types and return a Result with value and receipt. Observer/Earth-orientation
inputs are explicit. Undefined geometry stays an Undefined value with a reason.
No model may supply missing numerical facts.
