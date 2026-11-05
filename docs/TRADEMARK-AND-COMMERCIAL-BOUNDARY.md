# Trademark Reservation, Copyright Ownership & Open-Core Commercial Boundary

**Package:** `ephemeris-oss` (**RDG-Ephemeris**, in tribute to **Raj Dulari Gupta**)  
**Copyright Owner:** `Copyright (c) 2026 The Million Dollar AI Studio Ltd.`  
**Open-Source License:** Apache License, Version 2.0 (`Apache-2.0`)

---

## 1. Why the Core Ephemeris Is Open-Sourced Under Apache-2.0

For decades, developers building commercial astrology software, mobile applications, or cloud calculation APIs faced a difficult structural trade-off:
- **Copyleft Reciprocity (`GPL v2+ / AGPL v3`):** Free editions of legacy C ephemeris libraries require any developer running the library over a network server, web application, or API to release the complete source code of their entire proprietary application under the same copyleft license.
- **Commercial Seat & API Licensing Contracts:** Avoiding copyleft obligations on legacy ephemeris libraries requires purchasing commercial developer licenses and complying with specific contractual conditions governing commercial API or calculation-service businesses.

**RDG-Ephemeris (`ephemeris-oss`)** solves this cleanly for the global developer and research community:
- The entire core astronomical and Jyotish calculation engine (`src/ephemeris_oss/`, `rust/ephemeris-core/`, `web/`, and the embedded `1550–2306 CE` NASA JPL DE440 Chebyshev polynomial derivative tables) is published under the permissive **Apache License, Version 2.0 (`Apache-2.0`)**.
- Independent developers, solo practitioners, academic researchers, startups, and commercial software companies can embed `ephemeris-oss` inside proprietary desktop apps, mobile apps, closed-source SaaS backends, and internal or commercial APIs **royalty-free**, with **no obligation to open-source their proprietary application code**.

---

## 2. Copyright Retention & Attribution Requirements (`Apache-2.0 Section 4`)

Publishing `ephemeris-oss` under `Apache-2.0` grants a perpetual, non-exclusive copyright and patent license to the public. **The Million Dollar AI Studio Ltd. retains full copyright ownership** in all original source code and derivative polynomial tables it authored.

Under **Section 4 of the Apache License, Version 2.0**, any redistribution of `ephemeris-oss` in source or binary form (including inside commercial software or containers) must:
1. Include a copy of the [`LICENSE`](../LICENSE) file (`Apache-2.0`).
2. Retain all copyright, patent, trademark, and attribution notices from the [`NOTICE`](../NOTICE) file.
3. Cause any modified files to carry prominent notices stating that you changed the files.

---

## 3. Trademark Reservation (`Apache-2.0 Section 6`)

Under **Section 6 of the Apache License, Version 2.0** (*Trademarks*):

> *"This License does not grant permission to use the trade names, trademarks, service marks, or product names of the Licensor, except as required for reasonable and customary use in describing the origin of the Work and reproducing the content of the NOTICE file."*

The following names, marks, and brand identifiers are proprietary trademarks and trade names of **The Million Dollar AI Studio Ltd.** and are **expressly reserved**:
- **RDG™** and **Raj Dulari Gupta™** (in the context of astronomical/astrological software, ephemeris engines, and calculation services)
- **RDG-Ephemeris™**
- **Jyotish Studio™**
- **Jyotish Gurukul™**
- **The AGI Studio™**
- **The Million Dollar AI Studio Ltd.™**

### Permitted Nominative Attribution
You may make truthful, factual statements describing that your software uses or is built on this open-source package, such as:
- *"Powered by the open-source `ephemeris-oss` (RDG-Ephemeris) engine under Apache-2.0."*
- *"Astronomical calculations computed using `ephemeris-oss`."*

### Prohibited Trademark Uses Without Written Permission
Without a separate written trademark license from **The Million Dollar AI Studio Ltd.**, you may **not**:
- Brand, name, or market a third-party application, SaaS product, or commercial API service as an official **"RDG"**, **"Raj Dulari Gupta"**, **"Jyotish Studio"**, **"Jyotish Gurukul"**, or **"The AGI Studio"** product or service.
- Use the reserved trademarks in your company name, product title, domain name, or app-store listing in a manner that implies endorsement, sponsorship, or official affiliation.

---

## 4. Open-Core vs. Proprietary Commercial Boundary

Our business model separates trusted open-source community infrastructure from our proprietary products and managed services:

| Surface | License & Ownership | What It Includes |
|---|---|---|
| **1. Core Ephemeris & Jyotish Calculation Engine (`ephemeris-oss`)** | **Open Source (`Apache-2.0`)** | Planetary positions (`1550–2306 CE` embedded DE440 Chebyshev tables; `3102 BCE–3000 CE` extended span), IAU 2006/2000A & Vondrák-2011 reductions, 21 Ayanamshas, 8 House systems, Mean & True Lunar Nodes, 23 Vargas (`D1..D144`), 8 Dashas, Shadbala, Ashtakavarga, 86 Classical & Tajika Yogas, Regional Drik Panchanga, Birth-Time Rectification, Python SDK, CLI, stdio MCP Server, self-hosted HTTP REST server, and Rust/WASM core. |
| **2. Proprietary Flagship Products (`Jyotish Studio™` & `Jyotish Gurukul™`)** | **Proprietary (`All Rights Reserved`, The Million Dollar AI Studio Ltd.)** | Complete consumer and professional practitioner applications (web and offline desktop editions), interactive consultation workspaces, client almirah and case management, guided astrologer training and certification simulators, and visual design systems. |
| **3. Proprietary Fine-Tuned Domain AI Models & Interpretation Pipelines** | **Proprietary (`All Rights Reserved`, The Million Dollar AI Studio Ltd.)** | Custom-trained and quantized astrological reasoning models, curated consultation corpora, and multi-stage interpretation synthesis workflows. |
| **4. Managed Cloud APIs, Commercial Support & Custom Integrations** | **Proprietary Commercial Services (`The AGI Studio™`)** | Hosted high-availability API endpoints, enterprise SLA support, custom domain integrations, and turnkey consulting software built by The AGI Studio. |
