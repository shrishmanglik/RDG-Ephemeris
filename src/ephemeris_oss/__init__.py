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

from . import (
    adapter,
    almanac,
    compact_kernel,
    fact_sheet,
    jyotish,
    jyotish_advanced,
    jyotish_jaimini,
    jyotish_nadi,
    jyotish_rectification,
    jyotish_siddhanta,
    jyotish_transit,
    rust_bridge,
    visualization,
)
from ._api import EarthOrientation, Engine, EphemerisError, Houses, Result, Undefined
from ._version import __version__
from .adapter import (
    AnalyticalEphemerisProvider,
    CompleteKundaliBundle,
    EphemerisAdapter,
    HouseSystemResult,
    PlanetCoordinateResult,
    normalize_ephemeris_source,
)
from .engine import phenomena, uncertainty_envelope
from .fact_sheet import AIFactSheet, HallucinationAudit, compile_ai_fact_sheet, verify_ai_interpretation
from .jyotish import VedicChartAnalysis, compute_vedic_chart_analysis

__all__ = [
    "AIFactSheet",
    "AnalyticalEphemerisProvider",
    "CompleteKundaliBundle",
    "EarthOrientation",
    "Engine",
    "EphemerisAdapter",
    "EphemerisError",
    "HallucinationAudit",
    "HouseSystemResult",
    "Houses",
    "PlanetCoordinateResult",
    "Result",
    "Undefined",
    "VedicChartAnalysis",
    "__version__",
    "adapter",
    "almanac",
    "compact_kernel",
    "compile_ai_fact_sheet",
    "compute_vedic_chart_analysis",
    "fact_sheet",
    "jyotish",
    "jyotish_advanced",
    "jyotish_jaimini",
    "jyotish_nadi",
    "jyotish_rectification",
    "jyotish_siddhanta",
    "jyotish_transit",
    "normalize_ephemeris_source",
    "phenomena",
    "rust_bridge",
    "uncertainty_envelope",
    "verify_ai_interpretation",
    "visualization",
]
