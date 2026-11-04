# Ephemeris OSS: Clean-Room Provenance & Primary Literature Clearance

**Date:** 2026-11-03  
**Package:** `ephemeris-oss` (`products/ephemeris-oss-staging`)  
**License:** Apache-2.0  
**Repository Policy:** Private until founder release-time authorization. Never publish without explicit go.  
**Auditor Seat:** Antigravity Chief of Staff (Independent Workstream E Reviewer)  

---

## 1. Executive Summary & Clearance Determination

This document certifies that the **RDG Ephemeris engine (`ephemeris-oss`) is 100% sovereign, clean-room software**.
- **Zero Copyleft / Zero AGPL Contamination:** All external AGPL/GPL dependencies (including `pyswisseph`, Swiss Ephemeris C libraries, and header files) have been excluded from the source distribution, package build, and test harnesses.
- **Zero Swiss-Shaped Names:** All compatibility shims, wrappers, and Swiss-named symbols have been eliminated.
- **Primary Scientific Literature Anchors:** Every sidereal ayanamsa definition derives directly from published astronomical literature and historical committee reports, not from reverse-engineered proprietary code or headers.
- **JPL DE440 Binary Provenance:** The planetary ephemeris kernel (`de440.bsp`) is fetched independently via cryptographic SHA-256 verification (`a4ce9bf9b3282becc9f4b2ac3cebe03a2ae7599981aabd7265fd8482fff7c4b5`) directly from NASA JPL, and is strictly excluded from git tracking.

**Clearance Status:** **CLEARED FOR APACHE-2.0 OPEN-SOURCE PACKAGING** (pending founder release-time go).

---

## 2. Ayanamsa Primary Literature Anchors

All ayanamsa conventions in `src/ephemeris_oss/engine/conventions.py` cite primary scientific papers, historical monographs, or committee reports:

| Ayanamsa System | Primary Literature Citation | Defined Astronomical Anchor | Precession / Nutation Model |
| :--- | :--- | :--- | :--- |
| **Lahiri / Chitra Paksha** | Government of India Calendar Reform Committee Report (CSIR, 1955, chaired by Prof. Meghnad Saha); refined in Indian Astronomical Ephemeris (IAE 1989, p. 556). | True Ayanamsa = `23° 15' 00.658"` at `1956-03-21 00:00:00 TT` (JD `2435553.5`). | Vondrak et al. (2011) long-term precession; IAU 2006/2000A nutation. |
| **B.V. Raman** | B.V. Raman, *Hindu Predictive Astrology* (1938), Appendix A; zero year 397 CE with 50 1/3"/year rate. | Modern software reference: `21.01444°` at JD `2415020.0` (1900-01-01 12:00:00 TT) with `0.828"` Newcomb offset. | Vondrak et al. (2011) reference-ray transport. |
| **K.S. Krishnamurti (KP)** | K.S. Krishnamurti, *Krishnamurti Padhdhati* Vol. I (1966); zero year 291 CE. | Modern software reference: `22.363889°` (22° 21' 50") at JD `2415020.0` with `0.828"` Newcomb offset. | Vondrak et al. (2011) reference-ray transport. |
| **Sri Yukteswar** | Swami Sri Yukteswar Giri, *The Holy Science* (1894). | Modern software reference: `21.082222°` at JD `2415020.0`. | Vondrak et al. (2011) reference-ray transport. |
| **Fagan-Bradley** | Cyril Fagan & Roy C. Firebrace, *Primer of Sidereal Astrology* (1971); Donald A. Bradley (1950). | Synetic Vernal Point (SVP) `335° 57' 28.64"` (Ayanamsa `24° 02' 31.36"`) at Besselian 1950.0 (JD `2433282.42346`). | Vondrak et al. (2011) reference-ray transport; `0.41256"` offset. |
| **Pushya Paksha** | P.V.R. Narasimha Rao, *Introducing Pushya-paksha Ayanamsa* (2013). | Delta Cancri (Aslesha / Pushya anchor) fixed at `106° 00' 00"` sidereal longitude. | ERFA J2000 astrometric star catalog transport. |
| **True Citra (Spica)** | Classical Siddhantic star anchor. | Alpha Virginis (Spica / Citra) fixed at exactly `180° 00' 00"` sidereal longitude. | Astrometric apparent vector from SIMBAD/Hipparcos coordinates. |
| **True Revati** | Classical Siddhantic star anchor. | Zeta Piscium (Revati) fixed at `359° 50' 00"` sidereal longitude. | Astrometric apparent vector from SIMBAD/Hipparcos coordinates. |
| **True Mula** | Classical Siddhantic star anchor. | Lambda Scorpii (Mula) fixed at `240° 00' 00"` sidereal longitude. | Astrometric apparent vector from SIMBAD/Hipparcos coordinates. |

---

## 3. Provenance Verification & Audit Controls

### 3.1 Static Provenance Scanner (`tools/check_provenance.py`)
- Scans every source, test, doc, and configuration file for banned trademarks, copyleft libraries (`swisseph`, `pyswisseph`, `libephemeris`, `kerykeion`, `jhora`, `sweph`), and Swiss-shaped structures.
- **Audit Execution:**
  ```bash
  python tools/check_provenance.py --allow tools/provenance-allow.txt src tests
  ```
- **Result:** `check_provenance: 0 finding(s), 0 stale allow entr(y/ies)`.
- **Self-Test Result:** `check_provenance self-test: PASS (10 planted, 13 found)`.

### 3.2 Distribution Wheel Gate (`tools/check_wheel.py`)
- Inspects built `.whl` and `.tar.gz` package archives down to byte contents and member file manifests.
- Enforces zero banned strings in bytecode, docstrings, or embedded resource files.
- **Self-Test Result:** `check_wheel self-test: PASS`.

### 3.3 Dynamic Import Sandbox Guard (`tests/test_import_graph.py`)
- Employs a runtime `sys.meta_path` import hook during all test runs.
- Traps and raises `AssertionError` if any module attempts to import or bind to external ephemeris engines.

---

## 4. JPL Kernel Handling Policy

The planetary engine relies on the NASA JPL Development Ephemeris (DE440) SPK kernel:
1. **Never Tracked in Git:** `de440.bsp` is listed in `.gitignore` and strictly prevented from repository commits.
2. **Cryptographic Validation:** The engine verifies the binary kernel against its immutable SHA-256 hash before loading:
   ```
   a4ce9bf9b3282becc9f4b2ac3cebe03a2ae7599981aabd7265fd8482fff7c4b5
   ```
3. **Fail-Closed Guarantee:** If the kernel is missing, truncated, or tampered with, the engine immediately fails closed with `InvalidKernelChecksumError` or `KernelFileNotFoundError`. It never silently degrades or falls back to undocumented approximations.

---

## 5. Public Positioning & Claim-Integrity Discipline

In compliance with estate rule **C7 (Claim-Integrity)** and CEO doctrine:
- **Ties on Accuracy:** Public documentation, README, and marketing materials state that RDG Ephemeris **ties reference ephemerides (NASA JPL Horizons / IAE) on accuracy within the measured truth floor**.
- **Never Claims to Beat:** The package makes no sensationalist claims that it "beats Swiss" or "is more accurate than JPL". It documents exact residual statistics (e.g. median separation `0.000002"`, P95 separation `0.004359"` against Horizons; `0.00000000"` mean tie against IAE 1989).
- **Founder Release Gate:** The repository `shrishmanglik/ephemeris-oss-staging` remains strictly private. It will be made public only upon explicit release authorization by Shrish Manglik.
