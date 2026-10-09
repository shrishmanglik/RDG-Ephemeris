"""Positions derived from JPL kernels, with explicit conventions and calculation receipts.

Start with :meth:`Engine.load`; everything else hangs off the engine::

    from ephemeris_oss import Engine
    with Engine.load() as eng:
        result = eng.positions(instant, bodies=("sun", "moon"), ayanamsa="lahiri")
        result.value["moon"]["longitude_deg"], result.receipt

Undefined geometry (Placidus inside the polar circle, a body that never rises)
is returned as :class:`Undefined` with a reason. It is never an exception and
never a silent switch to another system.
"""

from __future__ import annotations

from ._api import EarthOrientation, Engine, EphemerisError, Houses, Result, Undefined
from ._version import __version__

__all__ = [
    "EarthOrientation",
    "Engine",
    "EphemerisError",
    "Houses",
    "Result",
    "Undefined",
    "__version__",
]
