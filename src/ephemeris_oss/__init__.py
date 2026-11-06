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
    api_server,
    compact_kernel,
    fact_sheet,
    impossible_astrology,
    jyotish,
    jyotish_advanced,
    jyotish_jaimini,
    jyotish_nadi,
    jyotish_rectification,
    jyotish_siddhanta,
    jyotish_transit,
    mcp_server,
    rust_bridge,
    visualization,
)
from ._api import EarthOrientation, Engine, EphemerisError, Houses, Result, Undefined
from ._version import __version__
from .adapter import (
    AnalyticalEphemerisProvider,
    CompleteKundaliBundle,
    EphemerisAdapter,
    GeoCoords,
    HouseSystemResult,
    NakshatraInfo,
    PlanetCoordinateResult,
    PlanetPosition,
    nakshatra_from_longitude,
    normalize_ephemeris_source,
    sign_from_longitude,
)
from .almanac import (
    RegionalPanchangReport,
    compute_lunar_month_amanta_purnimanta,
    compute_regional_panchang,
    compute_regional_solar_calendar,
)
from .api_server import build_openapi_spec, dispatch_api_request
from .engine import phenomena, uncertainty_envelope
from .fact_sheet import AIFactSheet, HallucinationAudit, compile_ai_fact_sheet, verify_ai_interpretation
from .impossible_astrology import (
    MultiCenturyPhenomenaReport,
    PersonalizedAstroFingerprintReport,
    SiddhantaDriftAnalysisReport,
    SubsecondShodashvargaCuspReport,
    VargaBoundaryMargin,
    analyze_siddhanta_vs_jpl_de440_drift,
    compute_personalized_astro_fingerprint,
    rectify_birth_time_bayesian,
    scan_multi_century_rare_phenomena,
    solve_subsecond_shodashvarga_cusp_transitions,
)
from .jyotish import VedicChartAnalysis, compute_vedic_chart_analysis
from .mcp_server import execute_mcp_tool
from .rust_bridge import evaluate_chebyshev_clenshaw_3d

__all__ = [
    "AIFactSheet",
    "AnalyticalEphemerisProvider",
    "CompleteKundaliBundle",
    "EarthOrientation",
    "Engine",
    "EphemerisAdapter",
    "EphemerisError",
    "GeoCoords",
    "HallucinationAudit",
    "HouseSystemResult",
    "Houses",
    "MultiCenturyPhenomenaReport",
    "NakshatraInfo",
    "PersonalizedAstroFingerprintReport",
    "PlanetCoordinateResult",
    "PlanetPosition",
    "RegionalPanchangReport",
    "Result",
    "SiddhantaDriftAnalysisReport",
    "SubsecondShodashvargaCuspReport",
    "Undefined",
    "VargaBoundaryMargin",
    "VedicChartAnalysis",
    "__version__",
    "adapter",
    "almanac",
    "analyze_siddhanta_vs_jpl_de440_drift",
    "api_server",
    "build_openapi_spec",
    "compact_kernel",
    "compile_ai_fact_sheet",
    "compute_lunar_month_amanta_purnimanta",
    "compute_personalized_astro_fingerprint",
    "compute_regional_panchang",
    "compute_regional_solar_calendar",
    "compute_vedic_chart_analysis",
    "dispatch_api_request",
    "evaluate_chebyshev_clenshaw_3d",
    "execute_mcp_tool",
    "fact_sheet",
    "impossible_astrology",
    "jyotish",
    "jyotish_advanced",
    "jyotish_jaimini",
    "jyotish_nadi",
    "jyotish_rectification",
    "jyotish_siddhanta",
    "jyotish_transit",
    "mcp_server",
    "nakshatra_from_longitude",
    "normalize_ephemeris_source",
    "phenomena",
    "rectify_birth_time_bayesian",
    "rust_bridge",
    "scan_multi_century_rare_phenomena",
    "sign_from_longitude",
    "solve_subsecond_shodashvarga_cusp_transitions",
    "uncertainty_envelope",
    "verify_ai_interpretation",
    "visualization",
]
