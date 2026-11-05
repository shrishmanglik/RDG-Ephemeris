# Internal Role-Based AI/VCOS Domain Analysis Report (`ephemeris-oss`)

**Date:** `2026-11-05`  
**Provenance & Scope Disclosure (Internal AI Role Analysis, Not an External Human Expert Cohort):**  
This document records an **internal role-based AI/VCOS domain analysis** conducted inside the authoring workflow using three automated AI agent role personas (`4dc841fe-b60e-4d5c-9c09-fda77e6deb80`, `fcd7ebe5-45c7-4578-8045-a6030b865b2f`, and `ba2b4190-19db-4979-a557-01031f253bb4`). **It is not an external human expert cohort, does not represent independent third-party practitioner, developer, or academic endorsement, and does not substitute for independent engineering review or external community testing:**
1. **Track 1 (AI Persona `jyotish-lineage-expert-tester`, Session `4dc841fe-b60e-4d5c-9c09-fda77e6deb80`) - Traditional Jyotish & Siddhanta/Panchanga Domain Checklist**
2. **Track 2 (AI Persona `astrology-saas-api-developer-tester`, Session `fcd7ebe5-45c7-4578-8045-a6030b865b2f`) - Commercial Astrology Software, SaaS & API Integration Checklist**
3. **Track 3 (AI Persona `ephemeris-astronomy-researcher-tester`, Session `ba2b4190-19db-4979-a557-01031f253bb4`) - Fundamental Astronomy & Ephemeris Benchmark Checklist**

Every checklist item identified by the three internal AI analysis tracks was resolved in code or documented transparently in [`ROADMAP-AND-LIMITATIONS.md`](ROADMAP-AND-LIMITATIONS.md), [`JYOTISH-CAPABILITIES-AND-CONVENTIONS.md`](JYOTISH-CAPABILITIES-AND-CONVENTIONS.md), and [`TRADEMARK-AND-COMMERCIAL-BOUNDARY.md`](TRADEMARK-AND-COMMERCIAL-BOUNDARY.md).

---

## 1. Track 1 Checklist Findings & Resolutions (Traditional Jyotish Domain Persona)

| Finding | Assessment | Resolution Enacted |
|---|---|---|
| **1.1 Mean vs. True (*Spashta*) Rahu/Ketu in `calc_ut` & `compute_complete_kundali_bundle`** | Calling `adapter.calc_ut(jd_ut, "true_node")` previously aliased `"true_node"` to `"rahu"` and returned the Mean Lunar Node (Meeus Eq. 47.7), whereas `calc_tt` computed the True (osculating) Lunar Node ($\mathbf{k} \times (\mathbf{r} \times \mathbf{v})$). | Updated `EphemerisAdapter.calc_ut()` and `compute_complete_kundali_bundle()` (plus MCP and REST tools) to support `true_node: bool = False` and direct `"true_node"` / `"true_rahu"` / `"true_ketu"` / `"osculating_node"` queries using the osculating Earth-Moon orbital angular momentum plane inside `1550-2306 CE` (with coverage-aware one-sided derivative fallback near the `1550` and `2306` endpoints) and Meeus periodic nodal terms outside that window, while keeping Mean Rahu/Ketu as the default. |
| **1.2 Accurate Yoga & Ashtakavarga Naming (`86 Yogas` vs `337 Bindus`)** | `README.md` previously summarized `"337 Yogas"`, conflating the conserved `337-bindu` *Sarvashtakavarga* total (`48+49+39+54+56+52+39 = 337`) with the Yoga engine (`70` classical *Parashari* Yogas + `16` *Tajika* Yogas). | Updated `README.md` and [`JYOTISH-CAPABILITIES-AND-CONVENTIONS.md`](JYOTISH-CAPABILITIES-AND-CONVENTIONS.md) to state **`86 Classical & Tajika Yogas, 337-Bindu Ashtakavarga`**. |
| **1.3 Dasha Inventory & *Kalachakra Dasha* Roadmap** | `docs/ARCHITECTURE-AND-MATHEMATICAL-REFERENCE.md` mentioned *Kalachakra Dasha*, whereas the 8 implemented Dashas are *Vimshottari, Ashtottari, Yogini, Chara, Sthira, Shoola, Mandooka, and Tajika Mudda*. | Updated [`ARCHITECTURE-AND-MATHEMATICAL-REFERENCE.md`](ARCHITECTURE-AND-MATHEMATICAL-REFERENCE.md) to list the exact 8 implemented Dasha systems and placed *Kalachakra Dasha* on the [`ROADMAP-AND-LIMITATIONS.md`](ROADMAP-AND-LIMITATIONS.md) roadmap. |
| **1.4 Lineage Convention Transparency** | Practitioners need clear documentation of default *Parampara* settings (`365.2425` solar vs `360.0` *Savana* Dasha years, `7` vs `8` Jaimini *Chara Karakas*, Venus exemption in *Graha Yuddha*, and sunrise-anchored *Udaya Panchanga*). | Authored [`JYOTISH-CAPABILITIES-AND-CONVENTIONS.md`](JYOTISH-CAPABILITIES-AND-CONVENTIONS.md) documenting all 21 Ayanamshas, 8 House systems, Mean vs True Nodes, and configurable *Parampara* parameters. |

---

## 2. Track 2 Checklist Findings & Resolutions (Commercial Astrology SaaS & API Developer Persona)

| Finding | Assessment | Resolution Enacted |
|---|---|---|
| **2.1 `NOTICE` Alignment with Embedded `1550-2306 CE` Chebyshev Kernels & Trademark Reservation** | `NOTICE` needed to distinguish between the bundled compressed Chebyshev polynomial derivative tables (`data/*.zlib`, `1550-2306 CE`) and optional on-demand raw NASA NAIF `.bsp` files, and needed explicit `Apache-2.0 Section 6` trademark reservation. | Updated [`NOTICE`](../NOTICE) and authored [`TRADEMARK-AND-COMMERCIAL-BOUNDARY.md`](TRADEMARK-AND-COMMERCIAL-BOUNDARY.md) reserving `RDG`, `Raj Dulari Gupta`, `RDG-Ephemeris`, `Jyotish Studio`, `Jyotish Gurukul`, `The AGI Studio`, and `The Million Dollar AI Studio Ltd.` while confirming royalty-free `Apache-2.0` commercial code licensing. |
| **2.2 Complete Runtime Dependency Table in `PROVENANCE-CLEARANCE.md`** | `tzdata >= 2024.1` (`Apache-2.0`) was listed in `pyproject.toml` and `NOTICE` but omitted from the table in `docs/PROVENANCE-CLEARANCE.md`. | Added `tzdata >= 2024.1` (`Apache-2.0`) to [`PROVENANCE-CLEARANCE.md`](PROVENANCE-CLEARANCE.md). |
| **2.3 OpenAPI 3.1 `responses` Blocks, HTTP Body Size Limit & Adapter Reuse** | Strict OpenAPI code generators require `responses` objects on every route; `do_POST` needed a `1 MB` payload cap (`HTTP 413`); `execute_mcp_tool` instantiated `EphemerisAdapter()` on every call. | Added `_get_responses()` and `_post_responses()` (`200`, `400`, `413`) to `build_openapi_spec()`, added `MAX_REQUEST_BODY_BYTES = 1_048_576` (`HTTP 413`) in `api_server.py`, and cached `_get_default_adapter()` in `mcp_server.py`. |

---

## 3. Track 3 Checklist Findings & Resolutions (Fundamental Astronomy & Ephemeris Researcher Persona)

| Finding | Assessment | Resolution Enacted |
|---|---|---|
| **3.1 Three Precision Regimes & Pre-1600 Nutation Boundary** | Researchers need a single table contrasting `1800-2100 CE` (`<= 0.018191"` embedded Chebyshev vs full DE440; `<= 0.000717"` in the full-kernel `docs/ACCURACY.md` table), `1550-2306 CE` embedded wings (`<= 0.018191"` vs DE440, with `mean_equinox=True` prior to `1600 CE`), provisioned `de441.bsp` (`-13200 to +17191`), and the unverified offline analytical fallback outside `1550-2306 CE`. | Documented all three precision regimes and scope boundaries in [`ROADMAP-AND-LIMITATIONS.md`](ROADMAP-AND-LIMITATIONS.md) Section 1 and [`README.md`](../README.md). |
| **3.2 Full DE440 vs. Live Embedded Chebyshev Horizons DE441 Footnote** | `docs/ACCURACY.md` reports full DE440 vs Horizons DE441 (`Moon worst 0.025351"`), while `evidence/horizons-iae-benchmark.json` reports live embedded Chebyshev vs Horizons DE441 (`Moon worst 0.036858"`). | Documented both figures and their exact methodological difference in [`README.md`](../README.md) and [`ROADMAP-AND-LIMITATIONS.md`](ROADMAP-AND-LIMITATIONS.md). |
| **3.3 System Barycentres (`NAIF 4/5/6`) & Ancient $\Delta T$ Geophysical Uncertainty** | Researchers value explicit quantification of the Jupiter/Saturn barycentre-to-physical-centre offset (`~0.15"-0.45"`) and the multi-hour geophysical $\Delta T$ uncertainty in `3102 BCE`. | Documented both physical boundaries in [`ROADMAP-AND-LIMITATIONS.md`](ROADMAP-AND-LIMITATIONS.md) Section 2. |
