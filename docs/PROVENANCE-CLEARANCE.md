# Clean-Room Provenance, License, and Dependency Clearance

**Package:** `ephemeris-oss` (RDG Ephemeris Engine)
**Version:** `0.1.0`
**License:** Apache License, Version 2.0 (`Apache-2.0`)
**Status:** Verified Clean-Room Implementation (12/12 Standalone Library Contract Checks PASS; Downstream App Journeys HELD/UNKNOWN)

---

## 1. Executive Summary

`ephemeris-oss` is a clean-room astronomical and Vedic astrological calculation engine built from first principles directly on public-domain planetary ephemerides and open-standard astronomical reduction routines:
- **Zero Copyleft Contamination:** All restrictive copyleft third-party ephemeris libraries, C extensions, and binary data tables have been excluded from the runtime, test suite, and build pipeline.
- **Zero Legacy Symbol Leakage:** All legacy compatibility shims and third-party function signatures have been eliminated in favor of our native first-principles API (`Engine`, `EphemerisAdapter`, `JplErfaAstronomyProvider`).
- **Zero Internal Estate Identifier Leakage:** Verified by `tools/check_internal_ids.py` across `src/`, `tests/`, `docs/`, `tools/`, and `web/`.
- **Deterministic Provenance Receipts:** Every calculation produces a canonical SHA-256 receipt binding the exact kernel SHA-256, Earth Orientation Parameters version, time-scale policy, ayanamsa model, and coordinate frame.

---

## 2. Clean-Room Mathematical & Data Sources

Every algorithm in `src/ephemeris_oss/` and `rust/ephemeris-core/` traces directly to primary published astronomical and classical Jyotish literature:

| Subsystem | Primary Published Source | Implementation Module | License / Status |
| :--- | :--- | :--- | :--- |
| **Barycentric Planetary & Lunar States** | NASA / Caltech JPL Development Ephemeris (`DE440` / `DE441`, Park et al. 2021, *AJ* 161:105) | `src/ephemeris_oss/engine/numerical_provider.py`, `src/ephemeris_oss/compact_kernel.py` | Public release by JPL/Caltech; credited in `NOTICE` |
| **SPK DAF Binary Segment Reader** | NASA NAIF SPK Required Reading & `jplephem` (Brandon Rhodes) | `src/ephemeris_oss/engine/spk_reader.py`, `jplephem >= 2.21` | MIT License (`jplephem`) |
| **Precession, Nutation & Time Scales (IAU 2006/2000A)** | IAU SOFA / Liberfa (`PyERFA`, IERS Conventions 2010 Technical Note 36) | `src/ephemeris_oss/engine/apparent.py`, `pyerfa >= 2.0.1` | BSD 3-Clause License (`PyERFA` / `Liberfa`) |
| **Earth Orientation Parameters & Historical Delta-T** | IERS Bulletin A (`finals2000A.all`); Espenak & Meeus (2006) NASA/TP-2006-214141 five-millennium polynomial | `src/ephemeris_oss/engine/earth_orientation.py` | Public domain / IERS open data |
| **Mean & Osculating Lunar Nodes** | Meeus, *Astronomical Algorithms* (2nd ed., 1998, Ch. 47 eq. 47.7); orbital angular momentum plane $\mathbf{h} = \mathbf{r} \times \mathbf{v}$ | `src/ephemeris_oss/engine/conventions.py` | Clean-room mathematical derivation |
| **Ayanamsa Models (Lahiri, True Citra, Raman, KP, Yukteshwar, Fagan-Bradley)** | *Report of the Calendar Reform Committee* (Govt. of India, 1955); *Indian Astronomical Ephemeris* (1989, p. 556); Hipparcos Catalog (ESA SP-1200, Spica HIP 65474) | `src/ephemeris_oss/engine/conventions.py`, `src/ephemeris_oss/engine/stellar_anchors.py` | Clean-room mathematical derivation |
| **Horizon Rise/Set/Transit & Optical Refraction** | Illinois bracketed secant-bisection solver; ERFA `eraRefco` + Saemundsson (*Sky & Telescope* 72, 70, 1986) | `src/ephemeris_oss/engine/events.py` | Clean-room mathematical derivation |
| **Solar & Lunar Eclipse Besselian & Shadow Solvers** | Besselian fundamental-plane geometry & conical Earth-shadow contact root-finding; forward syzygy search | `src/ephemeris_oss/engine/eclipses.py`, `src/ephemeris_oss/engine/eclipse_search.py` | Clean-room mathematical derivation |
| **Parashari, Jaimini, Nadi, Tajika, Compatibility & Siddhanta** | *Brihat Parashara Hora Shastra* (BPHS); *Jaimini Sutras*; *Surya Siddhanta*; *Vedanga Jyotisha* | `src/ephemeris_oss/jyotish*.py`, `src/ephemeris_oss/almanac/` | Clean-room mathematical derivation |

---

## 3. Automated Release Gate Verification

Four automated release gates enforce clean-room integrity before any wheel or source distribution is built:

1. **Provenance Scanner (`python tools/check_provenance.py --allow tools/provenance-allow.txt src tests docs tools web`)**
   - Scans every source, test, documentation, tool, and web SDK file for prohibited third-party ephemeris identifiers, copyleft markers, and binary file extensions.
   - Enforces that every line in `tools/provenance-allow.txt` is actively matched (zero stale allowlist entries).

2. **Internal Identifier Scanner (`python tools/check_internal_ids.py src tests docs tools web`)**
   - Ensures zero internal workspace paths, private product identifiers, or internal order references appear anywhere in the public repository.

3. **Claim-Integrity Rule Engine (`python tools/check_claims.py`)**
   - Verifies that every numerical accuracy metric in `docs/ACCURACY.md`, `README.md`, and `docs/benchmark-portal/index.html` matches `docs/claims.yaml` verbatim and contains zero unverified superlatives.

4. **Wheel & Source Archive Inspector (`python tools/check_wheel.py` & `python tools/verify_release.py`)**
   - Inspects built `.whl` and `.tar.gz` archives to ensure `LICENSE` and `NOTICE` are present and zero raw `.bsp` kernels, `.sqlite` databases, or internal evidence directories are packaged.

---

## 4. Runtime Dependency Audit

| Dependency | Version Constraint | License | Purpose |
| :--- | :--- | :--- | :--- |
| `numpy` | `>= 1.26` | BSD 3-Clause | Vectorized array arithmetic and rotation matrices |
| `pyerfa` | `>= 2.0.1` | BSD 3-Clause | IAU 2006/2000A precession, nutation, Earth rotation, and time scales |
| `jplephem` | `>= 2.21` | MIT | NASA JPL SPK DAF binary Chebyshev segment evaluation |

All three runtime dependencies use permissive open-source licenses (BSD 3-Clause and MIT) fully compatible with Apache-2.0 commercial and open-source distribution.
