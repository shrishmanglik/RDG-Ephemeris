# AI, Model Context Protocol (MCP), REST API, and Plugin Integration Guide

RDG-Ephemeris (`ephemeris-oss`) is designed to be loaded directly into AI assistants, LLM agent frameworks, command-line workflows, backend microservices, and browser applications with zero external data downloads required for dates from `1550 CE` to `2306 CE` (and automatic historical/future coverage from `3102 BCE` to `3000 CE`).

---

## 1. Installation & Quick Start

```bash
# Install from a local checkout or built wheel
pip install .

# Or build and install the standalone wheel
python -m build
pip install dist/ephemeris_oss-*.whl
```

Verify your installation from the terminal:

```bash
ephemeris-oss jyotish --at 2026-10-06T12:00:00Z --lat 28.6139 --lon 77.2090
ephemeris-oss fingerprint --at 2026-10-06T12:00:00Z --lat 28.6139 --lon 77.2090
```

---

## 2. Connect to Claude Desktop, Cursor, Windsurf, or VS Code via MCP

RDG-Ephemeris ships with a zero-dependency **Model Context Protocol (MCP) JSON-RPC 2.0 server** over `stdio` (`rdg-ephemeris-mcp` or `ephemeris-oss mcp`).

Add the following entry to your `claude_desktop_config.json`, `.cursor/mcp.json`, or `.vscode/mcp.json`:

```json
{
  "mcpServers": {
    "rdg-ephemeris": {
      "command": "rdg-ephemeris-mcp",
      "args": []
    }
  }
}
```

### All 9 Built-In MCP Tools Available to Your AI Agent

| Tool Name | Purpose |
|---|---|
| `compute_planetary_positions` | Sidereal & tropical coordinates, speeds, retrograde status, Rasi, and 27-Nakshatra Pada (`3102 BCE` to `3000 CE`, with `true_node` or `mean` Rahu/Ketu). |
| `compute_complete_kundali` | Complete natal chart: 9 Grahas, 12 houses, 16 Shodashvarga charts (`D1` to `D60`), 4 Dasha systems, Shadbala, Ashtakavarga, Panchanga, and classical Yogas. |
| `compute_panchanga` | Regional sunrise-anchored Drik Panchanga (`mode="sunrise"` default or `mode="instantaneous"`), Amanta/Purnimanta lunar months, and solar calendar. |
| `rectify_birth_time_and_varga_cusps` | Sub-second 16-Varga (`D1` to `D60`) cusp transition solver and Bayesian Kunda 81x / Pranapada / Tattwa birth-time rectification. |
| `scan_planetary_wars_and_stations` | Multi-century exact-second scanner for Graha Yuddha (planetary wars with disc-diameter and northern-latitude adjudication), retrograde stations, and combustion. |
| `compare_surya_siddhanta_vs_de440` | Classical *Surya Siddhanta* (`3102 BCE` Kali Yuga epicyclic *Manda* and *Sighra Samskara*) vs modern *Drig-Ganita* angular drift analyzer. |
| `compile_verified_ai_fact_sheet` | Compact (`< 3 KB`), token-disciplined, SHA-256-sealed JSON fact sheet for LLM system prompts. |
| `verify_ai_astrology_text` | Post-generation hallucination auditor that flags any AI sentence contradicting the computed chart. |
| `compute_personalized_astro_fingerprint` | Personalized 16-Varga harmonic phase vector, 16-domain clock-uncertainty confidence decay, continuous topocentric Digbala vector, and 8-Kaksha (`3 deg 45 arcmin`) Ashtakavarga transit resonance. |

Inspect all MCP tool schemas from the command line:

```bash
rdg-ephemeris-mcp --dump-tools
```

---

## 3. Run the HTTP REST JSON API & OpenAPI 3.1 Server

Start the built-in multi-threaded HTTP REST server for web frontends, mobile apps, or custom GPT Actions:

```bash
rdg-ephemeris-api --host 127.0.0.1 --port 8765
# or:
ephemeris-oss serve --host 127.0.0.1 --port 8765
```

### REST Endpoints (`12` Total)

- `GET /health` - Engine status, version, embedded DE440 Chebyshev span (`1550-2306 CE`), and endpoint list.
- `GET /openapi.json` - Full OpenAPI `3.1.0` schema (`200`, `400`, `413` responses) ready to import into Postman, Swagger UI, or OpenAI Custom GPT Actions.
- `GET /v1/tools` - List all 9 tool schemas.
- `POST /v1/positions` - Planetary positions (`jd_ut` or `iso_utc`, `ayanamsa`, `true_node`).
- `POST /v1/kundali` - Complete Kundali bundle (`D1-D60`, Dashas, Shadbala, Ashtakavarga, Yogas).
- `POST /v1/panchanga` - Sunrise-anchored (`mode="sunrise"`) or instantaneous (`mode="instantaneous"`) regional Drik Panchanga.
- `POST /v1/rectify` - Sub-second `D1-D60` cusp transition solver & Bayesian birth-time rectification.
- `POST /v1/phenomena` - Multi-century Graha Yuddha, retrograde station, and solar combustion scanner.
- `POST /v1/siddhanta-diff` - Classical *Surya Siddhanta* vs NASA JPL DE440 drift report.
- `POST /v1/fact-sheet` - Compact `< 3 KB` SHA-256-sealed AI fact sheet.
- `POST /v1/verify-text` - AI astrology text hallucination auditor.
- `POST /v1/fingerprint` - Personalized 16-Varga harmonic phase, clock-confidence decay, and 8-Kaksha Ashtakavarga transit resonance report.

Example `curl` call:

```bash
curl -X POST http://127.0.0.1:8765/v1/fingerprint \
  -H "Content-Type: application/json" \
  -d '{"iso_utc": "1995-08-15T09:30:00Z", "latitude_deg": 28.6139, "longitude_deg": 77.2090, "birth_time_uncertainty_seconds": 45.0}'
```

---

## 4. Python SDK & LLM Function-Calling Integration

```python
from ephemeris_oss import (
    compute_personalized_astro_fingerprint,
    execute_mcp_tool,
    MCP_TOOLS,
)

# 1. Direct Python call for personalized astrology
fp = compute_personalized_astro_fingerprint(
    2461139.0,
    latitude_deg=28.6139,
    longitude_deg=77.2090,
    birth_time_uncertainty_seconds=60.0,
)
print("Fingerprint SHA-256:", fp.fingerprint_id_sha256)
print("Overall Clock Confidence:", fp.overall_clock_confidence_score)
print("Personal Transit Resonance:", fp.overall_personal_transit_resonance_score)

# 2. Dispatch any LLM tool call directly in Python
result = execute_mcp_tool(
    "compute_complete_kundali",
    {"iso_utc": "2026-10-06T12:00:00Z", "latitude_deg": 43.6532, "longitude_deg": -79.3832},
)
print("Receipt SHA-256:", result["receipt_sha256"])
```

---

## 5. Rust Core & Browser ES-Module / WebAssembly Integration

- **Rust Core (`rust/ephemeris-core`):** Pure Rust DAF/SPK Type 2 & Type 3 binary reader and Clenshaw Chebyshev evaluator with zero-copy slicing and `wasm32-unknown-unknown` compatibility.
- **Browser ES-Module (`web/ephemeris-browser.js`):** Zero-dependency browser evaluator for client-side Chebyshev evaluation and interactive chart rendering.
