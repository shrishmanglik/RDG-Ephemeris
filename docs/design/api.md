# ephemeris_oss public interface (P1 draft, scratch)

Deep module: `Engine` hides kernel discovery, SHA-256 verification, DE440/DE441 split by date, EOP parsing,
time-scale policy, IAU 2006 frame chains and the provider constructor's eight version strings.

```python
from ephemeris_oss import Engine, Undefined, Instant

eng = Engine.load(kernels="auto", eop="auto", cache_dir=None)   # "auto": user cache, fetched by `kernels fetch --verify`
                                                                  # or an explicit Path / mapping id->Path
r = eng.positions(t, bodies=("sun", "moon"), frame="ecliptic-of-date", apparent=True, observer=None)
r.values["moon"].longitude_deg ; r.receipt                       # Result[T]: values + receipt
eng.ayanamsa(t, system="lahiri", mode="mean")                    # -> Result[float]
eng.houses(t, lat, lon, system="placidus")                       # -> Result[Houses | Undefined]
eng.nodes(t, kind="mean")                                        # -> Result[float]
eng.rise_set(date, place, body="sun", event="rise")              # -> Result[RiseSet | Undefined]
ephemeris_oss.time.from_civil(...), ephemeris_oss.time.delta_t(...)
```

Errors: `EphemerisError` (bad input, missing kernel). Undefined geometry is a value (`Undefined(reason)`), never an
exception and never a silent fallback system.

Hidden: provider construction, kernel registry, EOP resolver, version strings, receipts' hashing.
Deletion test: without `Engine` every caller rebuilds the 8-argument provider and the registry; deep.
Seam test: no second implementation; no abstract base added.
Eclipse functions: not exported (internal until R7).
