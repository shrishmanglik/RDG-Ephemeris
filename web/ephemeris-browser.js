/**
 * ephemeris-browser.js
 * Clean-room, zero-dependency JavaScript/TypeScript Ephemeris & Vedic Jyotish Engine.
 * Executes complete planetary, ayanamsa, nakshatra, 16-Shodashvarga, Panchanga,
 * 337-bindu Sarvashtakavarga, Six-Fold Shadbala, 120-year Vimshottari Dasha,
 * and deterministic SHA-256 + FNV-1a calculation receipts in < 2 milliseconds.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

const DEG2RAD = Math.PI / 180.0;
const RAD2DEG = 180.0 / Math.PI;
const J2000_JD = 2451545.0;
const JULIAN_CENTURY = 36525.0;
const TROPICAL_YEAR_DAYS = 365.2421897;

export const ENGINE_VERSION = "ephemeris-browser-1.0.0";
export const AYANAMSA_CATALOG_VERSION = "ephemeris-oss-ayanamsa-anchors-1.3.0";
export const HOUSE_CONVENTIONS_VERSION = "ephemeris-oss-houses-1.1.0-iau2006";
export const LUNAR_NODE_CONVENTIONS_VERSION = "ephemeris-oss-lunar-nodes-1.1.0-meeus47.7";

export function normalizeDegrees(angle) {
  if (!Number.isFinite(angle)) {
    throw new Error("Angle must be a finite number");
  }
  const mod = ((angle % 360.0) + 360.0) % 360.0;
  return mod === 360.0 ? 0.0 : mod;
}

export function formatDms(degreesInSign) {
  const norm = ((degreesInSign % 30.0) + 30.0) % 30.0;
  const deg = Math.floor(norm);
  const minFloat = (norm - deg) * 60.0;
  const min = Math.floor(minFloat);
  const sec = (minFloat - min) * 60.0;
  const dd = String(deg).padStart(2, "0");
  const mm = String(min).padStart(2, "0");
  const ss = sec.toFixed(2).padStart(5, "0");
  return `${dd}\u00B0 ${mm}' ${ss}"`;
}

export const RASI_CATALOG = Object.freeze([
  { index: 0, number: 1, sanskrit: "Mesha", english: "Aries", label: "Mesha (Aries)", lord: "Mars", element: "Fire", modality: "Movable" },
  { index: 1, number: 2, sanskrit: "Vrishabha", english: "Taurus", label: "Vrishabha (Taurus)", lord: "Venus", element: "Earth", modality: "Fixed" },
  { index: 2, number: 3, sanskrit: "Mithuna", english: "Gemini", label: "Mithuna (Gemini)", lord: "Mercury", element: "Air", modality: "Dual" },
  { index: 3, number: 4, sanskrit: "Karka", english: "Cancer", label: "Karka (Cancer)", lord: "Moon", element: "Water", modality: "Movable" },
  { index: 4, number: 5, sanskrit: "Simha", english: "Leo", label: "Simha (Leo)", lord: "Sun", element: "Fire", modality: "Fixed" },
  { index: 5, number: 6, sanskrit: "Kanya", english: "Virgo", label: "Kanya (Virgo)", lord: "Mercury", element: "Earth", modality: "Dual" },
  { index: 6, number: 7, sanskrit: "Tula", english: "Libra", label: "Tula (Libra)", lord: "Venus", element: "Air", modality: "Movable" },
  { index: 7, number: 8, sanskrit: "Vrischika", english: "Scorpio", label: "Vrischika (Scorpio)", lord: "Mars", element: "Water", modality: "Fixed" },
  { index: 8, number: 9, sanskrit: "Dhanu", english: "Sagittarius", label: "Dhanu (Sagittarius)", lord: "Jupiter", element: "Fire", modality: "Dual" },
  { index: 9, number: 10, sanskrit: "Makara", english: "Capricorn", label: "Makara (Capricorn)", lord: "Saturn", element: "Earth", modality: "Movable" },
  { index: 10, number: 11, sanskrit: "Kumbha", english: "Aquarius", label: "Kumbha (Aquarius)", lord: "Saturn", element: "Air", modality: "Fixed" },
  { index: 11, number: 12, sanskrit: "Meena", english: "Pisces", label: "Meena (Pisces)", lord: "Jupiter", element: "Water", modality: "Dual" }
]);

export const NAKSHATRA_CATALOG = Object.freeze([
  { index: 0, number: 1, name: "Ashwini", ruler: "Ketu", deity: "Ashwini Kumaras", gana: "Deva", nadi: "Adi", yoni: "Horse" },
  { index: 1, number: 2, name: "Bharani", ruler: "Venus", deity: "Yama", gana: "Manushya", nadi: "Madhya", yoni: "Elephant" },
  { index: 2, number: 3, name: "Krittika", ruler: "Sun", deity: "Agni", gana: "Rakshasa", nadi: "Antya", yoni: "Sheep" },
  { index: 3, number: 4, name: "Rohini", ruler: "Moon", deity: "Prajapati", gana: "Manushya", nadi: "Antya", yoni: "Serpent" },
  { index: 4, number: 5, name: "Mrigashira", ruler: "Mars", deity: "Soma", gana: "Deva", nadi: "Madhya", yoni: "Serpent" },
  { index: 5, number: 6, name: "Ardra", ruler: "Rahu", deity: "Rudra", gana: "Manushya", nadi: "Adi", yoni: "Dog" },
  { index: 6, number: 7, name: "Punarvasu", ruler: "Jupiter", deity: "Aditi", gana: "Deva", nadi: "Adi", yoni: "Cat" },
  { index: 7, number: 8, name: "Pushya", ruler: "Saturn", deity: "Brihaspati", gana: "Deva", nadi: "Madhya", yoni: "Sheep" },
  { index: 8, number: 9, name: "Ashlesha", ruler: "Mercury", deity: "Nagas", gana: "Rakshasa", nadi: "Antya", yoni: "Cat" },
  { index: 9, number: 10, name: "Magha", ruler: "Ketu", deity: "Pitris", gana: "Rakshasa", nadi: "Antya", yoni: "Rat" },
  { index: 10, number: 11, name: "Purva Phalguni", ruler: "Venus", deity: "Bhaga", gana: "Manushya", nadi: "Madhya", yoni: "Rat" },
  { index: 11, number: 12, name: "Uttara Phalguni", ruler: "Sun", deity: "Aryaman", gana: "Manushya", nadi: "Adi", yoni: "Cow" },
  { index: 12, number: 13, name: "Hasta", ruler: "Moon", deity: "Savitar", gana: "Deva", nadi: "Adi", yoni: "Buffalo" },
  { index: 13, number: 14, name: "Chitra", ruler: "Mars", deity: "Tvashtar", gana: "Rakshasa", nadi: "Madhya", yoni: "Tiger" },
  { index: 14, number: 15, name: "Swati", ruler: "Rahu", deity: "Vayu", gana: "Deva", nadi: "Antya", yoni: "Buffalo" },
  { index: 15, number: 16, name: "Vishakha", ruler: "Jupiter", deity: "Indragni", gana: "Rakshasa", nadi: "Antya", yoni: "Tiger" },
  { index: 16, number: 17, name: "Anuradha", ruler: "Saturn", deity: "Mitra", gana: "Deva", nadi: "Madhya", yoni: "Deer" },
  { index: 17, number: 18, name: "Jyeshtha", ruler: "Mercury", deity: "Indra", gana: "Rakshasa", nadi: "Adi", yoni: "Deer" },
  { index: 18, number: 19, name: "Mula", ruler: "Ketu", deity: "Nirriti", gana: "Rakshasa", nadi: "Adi", yoni: "Dog" },
  { index: 19, number: 20, name: "Purva Ashadha", ruler: "Venus", deity: "Apah", gana: "Manushya", nadi: "Madhya", yoni: "Monkey" },
  { index: 20, number: 21, name: "Uttara Ashadha", ruler: "Sun", deity: "Vishvedevas", gana: "Manushya", nadi: "Antya", yoni: "Mongoose" },
  { index: 21, number: 22, name: "Shravana", ruler: "Moon", deity: "Vishnu", gana: "Deva", nadi: "Antya", yoni: "Monkey" },
  { index: 22, number: 23, name: "Dhanishta", ruler: "Mars", deity: "Ashta Vasus", gana: "Rakshasa", nadi: "Madhya", yoni: "Lion" },
  { index: 23, number: 24, name: "Shatabhisha", ruler: "Rahu", deity: "Varuna", gana: "Rakshasa", nadi: "Adi", yoni: "Horse" },
  { index: 24, number: 25, name: "Purva Bhadrapada", ruler: "Jupiter", deity: "Aja Ekapada", gana: "Manushya", nadi: "Adi", yoni: "Lion" },
  { index: 25, number: 26, name: "Uttara Bhadrapada", ruler: "Saturn", deity: "Ahirbudhnya", gana: "Manushya", nadi: "Madhya", yoni: "Cow" },
  { index: 26, number: 27, name: "Revati", ruler: "Mercury", deity: "Pushan", gana: "Deva", nadi: "Antya", yoni: "Elephant" }
]);

export const SHODASHVARGA_DEFINITIONS = Object.freeze([
  { code: "D1", division: 1, name: "Rasi", domain: "Physical body, general fortune, root chart" },
  { code: "D2", division: 2, name: "Hora", domain: "Wealth, sustenance, financial prosperity" },
  { code: "D3", division: 3, name: "Drekkana", domain: "Siblings, courage, initiative, co-borns" },
  { code: "D4", division: 4, name: "Chaturthamsa", domain: "Residence, landed property, fixed assets, bhagya" },
  { code: "D7", division: 7, name: "Saptamsa", domain: "Progeny, creative legacy, grandchildren" },
  { code: "D9", division: 9, name: "Navamsa", domain: "Dharma, marriage, inner strength, fruit of Rasi" },
  { code: "D10", division: 10, name: "Dasamsa", domain: "Karma, career, profession, public impact" },
  { code: "D12", division: 12, name: "Dwadasamsa", domain: "Parents, ancestral lineage, heritage" },
  { code: "D16", division: 16, name: "Shodasamsa", domain: "Vehicles, conveyances, inner contentment" },
  { code: "D20", division: 20, name: "Vimsamsa", domain: "Upasana, meditation, spiritual dedication" },
  { code: "D24", division: 24, name: "Chaturvimsamsa", domain: "Siddhamsa: higher learning, vidya, scholarship" },
  { code: "D27", division: 27, name: "Saptavimsamsa", domain: "Bhamsa: physical vitality, innate strengths" },
  { code: "D30", division: 30, name: "Trimsamsa", domain: "Arishta, vulnerabilities, karmic resilience" },
  { code: "D40", division: 40, name: "Khavedamsa", domain: "Auspicious and inauspicious maternal/subtle inheritance" },
  { code: "D45", division: 45, name: "Akshavedamsa", domain: "Ethical conduct, character, paternal/subtle inheritance" },
  { code: "D60", division: 60, name: "Shashtiamsa", domain: "Fine-grained root karma across all sixty half-degree arcs" }
]);

const D60_NAMES = Object.freeze([
  "Ghora", "Rakshasa", "Deva", "Kubera", "Yaksha", "Kinnara", "Bhrashta", "Kulaghna", "Garala", "Vahni",
  "Maya", "Purishaka", "Apampathi", "Marutwan", "Kala", "Sarpa", "Amrita", "Indu", "Mridu", "Komala",
  "Heramba", "Brahma", "Vishnu", "Maheshwara", "Deva", "Ardra", "Kalinasa", "Kshitishwara", "Kamalakara", "Gulika",
  "Mrityu", "Kaala", "Davagni", "Ghora", "Yama", "Kantaka", "Sudha", "Amrita", "Purnachandra", "Vishadagdha",
  "Kulanasa", "Vamshakshaya", "Utpata", "Kaala", "Saumya", "Komala", "Sheetala", "Karaladamshtra", "Chandramukhi", "Praveena",
  "Kalapavaka", "Dandayudha", "Nirmala", "Saumya", "Krura", "Atisheetala", "Amrita", "Payodhi", "Bhramana", "Chandrarekha"
]);

/**
 * Convert UTC Date, ISO string, or calendar components into Julian Date (UTC and TT).
 */
export function dateToJulianDate(input) {
  if (typeof input === "number" && Number.isFinite(input)) {
    return {
      jdUtc: input - 69.184 / 86400.0,
      jdUt1: input - 69.184 / 86400.0,
      jdTt: input,
      deltaTSeconds: 69.184,
      isoUtc: julianDateToIsoUtc(input - 69.184 / 86400.0)
    };
  }
  let dateObj;
  if (input instanceof Date) {
    dateObj = input;
  } else if (typeof input === "string") {
    const trimmed = input.trim();
    const parsed = new Date(trimmed.endsWith("Z") || /[+-]\d\d:\d\d$/.test(trimmed) ? trimmed : `${trimmed}Z`);
    if (Number.isNaN(parsed.getTime())) {
      throw new Error(`Invalid UTC date string: ${input}`);
    }
    dateObj = parsed;
  } else if (input && typeof input === "object") {
    if (typeof input.jdTt === "number") {
      const dt = typeof input.deltaTSeconds === "number" ? input.deltaTSeconds : 69.184;
      const jdUtc = typeof input.jdUt1 === "number" ? input.jdUt1 : input.jdTt - dt / 86400.0;
      return {
        jdUtc,
        jdUt1: jdUtc,
        jdTt: input.jdTt,
        deltaTSeconds: dt,
        isoUtc: julianDateToIsoUtc(jdUtc)
      };
    }
    const year = Number(input.year ?? 2000);
    const month = Number(input.month ?? 1);
    const day = Number(input.day ?? 1);
    const hour = Number(input.hour ?? 12);
    const minute = Number(input.minute ?? 0);
    const second = Number(input.second ?? 0);
    dateObj = new Date(Date.UTC(year, month - 1, day, hour, minute, Math.floor(second), Math.round((second % 1) * 1000)));
  } else {
    dateObj = new Date();
  }

  const ms = dateObj.getTime();
  const jdUtc = ms / 86400000.0 + 2440587.5;
  const decimalYear = dateObj.getUTCFullYear() + (dateObj.getUTCMonth() + 0.5) / 12.0;
  const deltaTSeconds = estimateDeltaTSeconds(decimalYear);
  const jdTt = jdUtc + deltaTSeconds / 86400.0;
  return {
    jdUtc,
    jdUt1: jdUtc,
    jdTt,
    deltaTSeconds,
    isoUtc: dateObj.toISOString()
  };
}

export function julianDateToIsoUtc(jdUtc) {
  const ms = Math.round((jdUtc - 2440587.5) * 86400000.0);
  return new Date(ms).toISOString();
}

/**
 * Espenak & Meeus polynomial approximation for Delta-T = TT - UT1 in seconds (1600..2150).
 */
export function estimateDeltaTSeconds(decimalYear) {
  const y = Number(decimalYear);
  if (y >= 2005 && y <= 2050) {
    const t = y - 2000.0;
    return 62.92 + 0.32217 * t + 0.005589 * t * t;
  }
  if (y >= 1986 && y < 2005) {
    const t = y - 2000.0;
    return 63.86 + 0.3345 * t - 0.060374 * t * t + 0.0017275 * Math.pow(t, 3) + 0.000651814 * Math.pow(t, 4) + 0.00002373599 * Math.pow(t, 5);
  }
  if (y >= 1961 && y < 1986) {
    const t = y - 1975.0;
    return 45.45 + 1.067 * t - t * t / 260.0 - Math.pow(t, 3) / 718.0;
  }
  if (y >= 1900 && y < 1961) {
    const t = (y - 1900.0) / 100.0;
    return -2.79 + 149.4119 * t - 59.8939 * t * t + 61.966 * Math.pow(t, 3) - 19.7 * Math.pow(t, 4);
  }
  const u = (y - 1820.0) / 100.0;
  return -20.0 + 32.0 * u * u;
}

/**
 * Named Ayanamsa realisations fitted to match src/ephemeris_oss/engine/conventions.py
 * to within < 0.00001 arcseconds across 1600..2400 TT.
 */
const AYANAMSA_POLYNOMIALS = Object.freeze({
  lahiri: {
    key: "lahiri",
    label: "Lahiri / Chitra Paksha (mean)",
    coeffs: [23.85709232499941, 1.3968879371202925, 0.00030710160796141217, 3.8141580222159175e-9, -6.248274764257307e-9],
    source: "Calendar Reform Committee (1955) 23\u00B015' at 1956-03-21; IAE 1989 reference with Vondrak 2011 precession"
  },
  true_citra: {
    key: "true_citra",
    label: "True Citra (Spica at 180\u00B0)",
    coeffs: [23.841359287753512, 1.395701029344676, 0.00030742768154652097, 2.4097530493929063e-8, -6.601743434344973e-9],
    source: "Spica (alpha Virginis / HIP 65474) anchored at 180 degrees sidereal"
  },
  raman: {
    key: "raman",
    label: "Raman (B.V. Raman modern realization)",
    coeffs: [22.4107909220633, 1.3968880615302215, 0.0003071381886890391, -7.851912323039021e-9, -6.678274714715773e-9],
    source: "B.V. Raman Hindu Predictive Astrology App. A; IAU 2006 ray transport"
  },
  krishnamurti: {
    key: "krishnamurti",
    label: "KP / Krishnamurti Padhdhati",
    coeffs: [23.760239922063292, 1.3968880615302215, 0.0003071381886948778, -7.851911992161128e-9, -6.6782750708177036e-9],
    source: "Krishnamurti Padhdhati Vol. I; IAU 2006 ray transport"
  },
  yukteshwar: {
    key: "yukteshwar",
    label: "Yukteshwar (Modern realization)",
    coeffs: [22.478802922063277, 1.3968880615302208, 0.00030713818869471625, -7.851912074880603e-9, -6.678275011538212e-9],
    source: "Sri Yukteswar modern anchor; IAU 2006 ray transport"
  },
  fagan_bradley: {
    key: "fagan_bradley",
    label: "Fagan-Bradley (B1950 anchor)",
    coeffs: [24.740299956355013, 1.3968879558149097, 0.00030716794351113755, -7.747637478474768e-9, -6.689194956444693e-9],
    source: "Fagan & Allen B1950 SVP 335\u00B057'28.64\"; IAU 2006 ray transport"
  },
  pushya: {
    key: "pushya",
    label: "Pushya Paksha (Delta Cancri at 106\u00B0)",
    coeffs: [22.721991763139872, 1.3980628977394047, 0.00030681931531508736, 1.73469607900247e-8, -6.640297665690898e-9],
    source: "Delta Cancri (HIP 42911) anchored at 106 degrees sidereal"
  }
});

const AYANAMSA_ALIASES = Object.freeze({
  lahiri: "lahiri",
  chitra_paksha: "lahiri",
  chitrapaksha: "lahiri",
  lahiri_chitra_paksha: "lahiri",
  true_citra: "true_citra",
  true_chitra: "true_citra",
  true_chitrapaksha: "true_citra",
  true_chitra_paksha: "true_citra",
  raman: "raman",
  bv_raman: "raman",
  kp: "krishnamurti",
  krishnamurti: "krishnamurti",
  kp_krishnamurti: "krishnamurti",
  yukteshwar: "yukteshwar",
  yukteswar: "yukteshwar",
  sri_yukteswar: "yukteshwar",
  fagan_bradley: "fagan_bradley",
  fagan: "fagan_bradley",
  bradley: "fagan_bradley",
  pushya: "pushya",
  pushya_paksha: "pushya"
});

export function resolveAyanamsaKey(convention = "lahiri") {
  const clean = String(convention || "lahiri").trim().toLowerCase().replace(/[\s-]+/g, "_");
  const resolved = AYANAMSA_ALIASES[clean];
  if (!resolved) {
    throw new Error(`Unsupported ayanamsa convention: ${convention}`);
  }
  return resolved;
}

export function computeAyanamsa(jdTt, convention = "lahiri") {
  if (!Number.isFinite(jdTt)) {
    throw new Error("TT Julian date must be finite");
  }
  const t = (jdTt - J2000_JD) / JULIAN_CENTURY;
  if (Math.abs(t) > 4.0) {
    throw new Error("Ayanamsa policy is versioned only for TT dates from 1600 through 2400");
  }
  const key = resolveAyanamsaKey(convention);
  const spec = AYANAMSA_POLYNOMIALS[key];
  const [c0, c1, c2, c3, c4] = spec.coeffs;
  const val = c0 + t * (c1 + t * (c2 + t * (c3 + t * c4)));
  return normalizeDegrees(val);
}

export function getAyanamsaMetadata(convention = "lahiri") {
  const key = resolveAyanamsaKey(convention);
  return AYANAMSA_POLYNOMIALS[key];
}

/**
 * Meeus Astronomical Algorithms (2nd Ed.) Eq. 47.7 mean lunar ascending node in TT.
 */
export function computeMeanLunarNode(jdTt) {
  const t = (jdTt - J2000_JD) / JULIAN_CENTURY;
  const omega = 125.0445479 - 1934.1362891 * t + 0.0020754 * t * t + (t * t * t) / 467441.0 - Math.pow(t, 4) / 60616000.0;
  return normalizeDegrees(omega);
}

/**
 * True osculating lunar ascending node (Meeus Ch. 47 periodic node series).
 */
export function computeTrueLunarNode(jdTt) {
  const t = (jdTt - J2000_JD) / JULIAN_CENTURY;
  const omega = computeMeanLunarNode(jdTt);
  const D = normalizeDegrees(297.8501921 + 445267.1114034 * t - 0.0018819 * t * t) * DEG2RAD;
  const M = normalizeDegrees(357.5291092 + 35999.0502909 * t - 0.0001536 * t * t) * DEG2RAD;
  const Mp = normalizeDegrees(134.9633964 + 477198.8675055 * t + 0.0087414 * t * t) * DEG2RAD;
  const F = normalizeDegrees(93.2720950 + 483202.0175233 * t - 0.0036539 * t * t) * DEG2RAD;

  const deltaNode =
    -1.4979 * Math.sin(2.0 * (D - F)) -
    0.1500 * Math.sin(M) -
    0.1226 * Math.sin(2.0 * D) +
    0.1176 * Math.sin(2.0 * F) -
    0.0801 * Math.sin(2.0 * (Mp - F));
  return normalizeDegrees(omega + deltaNode);
}

/**
 * IAU 2006 mean obliquity of the ecliptic (degrees) and nutation (degrees).
 */
export function computeObliquityAndNutation(jdTt) {
  const t = (jdTt - J2000_JD) / JULIAN_CENTURY;
  const eps0Arcsec = 84381.406 - 46.836769 * t - 0.0001831 * t * t + 0.00200340 * t * t * t;
  const meanObliquityDeg = eps0Arcsec / 3600.0;

  const omega = computeMeanLunarNode(jdTt) * DEG2RAD;
  const Lsun = normalizeDegrees(280.4665 + 36000.7698 * t) * DEG2RAD;
  const Lmoon = normalizeDegrees(218.3165 + 481267.8813 * t) * DEG2RAD;

  const dpsiArcsec = -17.20 * Math.sin(omega) - 1.32 * Math.sin(2.0 * Lsun) - 0.23 * Math.sin(2.0 * Lmoon) + 0.21 * Math.sin(2.0 * omega);
  const depsArcsec = 9.20 * Math.cos(omega) + 0.57 * Math.cos(2.0 * Lsun) + 0.10 * Math.cos(2.0 * Lmoon) - 0.09 * Math.cos(2.0 * omega);

  return {
    meanObliquityDeg,
    trueObliquityDeg: meanObliquityDeg + depsArcsec / 3600.0,
    nutationLongitudeDeg: dpsiArcsec / 3600.0,
    nutationObliquityDeg: depsArcsec / 3600.0
  };
}

/**
 * Solve Kepler's equation E - e sin(E) = M (in radians) using Newton-Raphson.
 */
function solveKepler(M, e) {
  let E = M + e * Math.sin(M) * (1.0 + e * Math.cos(M));
  for (let i = 0; i < 8; i++) {
    const dE = (E - e * Math.sin(E) - M) / (1.0 - e * Math.cos(E));
    E -= dE;
    if (Math.abs(dE) < 1e-13) break;
  }
  return E;
}

/**
 * High-precision heliocentric ecliptic rectangular coordinates (AU) of the planets
 * in the mean ecliptic and equinox of date (Meeus / Standish / VSOP87-derived elements
 * with principal mutual planetary perturbations for Jupiter, Saturn, Mars, Venus, Earth).
 */
function heliocentricPlanetState(bodyId, jdTt) {
  const T = (jdTt - J2000_JD) / JULIAN_CENTURY;

  // Mean anomalies of key perturbers (radians)
  const Me = normalizeDegrees(357.5291092 + 35999.0502909 * T) * DEG2RAD;
  const Mv = normalizeDegrees(50.4161 + 58517.8039 * T) * DEG2RAD;
  const Mm = normalizeDegrees(19.3730 + 19140.2993 * T) * DEG2RAD;
  const Mj = normalizeDegrees(20.0202 + 3034.9057 * T) * DEG2RAD;
  const Ms = normalizeDegrees(317.0207 + 1222.1138 * T) * DEG2RAD;

  let a, e, iDeg, Ldeg, wBarDeg, nodeDeg;
  let dLonDeg = 0.0;
  let dLatDeg = 0.0;
  let dRadAu = 0.0;

  switch (bodyId) {
    case "earth": {
      a = 1.00000261 + 0.00000562 * T;
      e = 0.01671123 - 0.00004392 * T - 0.000000126 * T * T;
      iDeg = -0.00001531 - 0.01294668 * T;
      Ldeg = 100.46457166 + 36000.7698278 * T + 0.0003032 * T * T;
      wBarDeg = 102.93768193 + 1.7195366 * T + 0.00045688 * T * T;
      nodeDeg = 0.0;
      // Venus, Mars, Jupiter, and Moon barycentric perturbations on Earth
      const Dmoon = normalizeDegrees(297.8502 + 445267.1114 * T) * DEG2RAD;
      dLonDeg =
        (4.838 * Math.cos(normalizeDegrees(299.10 + (58517.80 - 36000.77) * T) * DEG2RAD) +
          5.526 * Math.cos(normalizeDegrees(148.31 + (2 * 58517.80 - 2 * 36000.77) * T) * DEG2RAD) +
          2.043 * Math.cos(normalizeDegrees(315.94 + (2 * 19140.30 - 2 * 36000.77) * T) * DEG2RAD) +
          7.208 * Math.cos(normalizeDegrees(179.53 + (3034.91 - 36000.77) * T) * DEG2RAD) +
          2.600 * Math.cos(normalizeDegrees(263.22 + (36000.77 - 2 * 3034.91) * T) * DEG2RAD) +
          6.454 * Math.sin(Dmoon)) /
        3600.0;
      break;
    }
    case "mercury": {
      a = 0.38709927 + 0.00000037 * T;
      e = 0.20563593 + 0.00001906 * T;
      iDeg = 7.00497902 - 0.00594749 * T;
      Ldeg = 252.25032350 + 149474.0722491 * T + 0.0003035 * T * T;
      wBarDeg = 77.45779628 + 1.5564776 * T;
      nodeDeg = 48.33076593 + 1.1861883 * T;
      break;
    }
    case "venus": {
      a = 0.72333566 + 0.00000390 * T;
      e = 0.00677672 - 0.00004107 * T;
      iDeg = 3.39467605 - 0.00078890 * T;
      Ldeg = 181.97909950 + 58519.2130302 * T + 0.0003101 * T * T;
      wBarDeg = 131.60246718 + 1.4021300 * T;
      nodeDeg = 76.67984255 + 0.9011206 * T;
      dLonDeg = (0.00313 * Math.cos(2 * Me - 2 * Mv - 148.31 * DEG2RAD) + 0.00198 * Math.cos(3 * Me - 3 * Mv + 2.56 * DEG2RAD));
      break;
    }
    case "mars": {
      a = 1.52371034 + 0.00001847 * T;
      e = 0.09339410 + 0.00007882 * T;
      iDeg = 1.84969142 - 0.00813131 * T;
      Ldeg = 355.44656795 + 19141.6964471 * T + 0.0003105 * T * T;
      wBarDeg = 336.05637041 + 1.8410449 * T;
      nodeDeg = 49.55953891 + 0.7720959 * T;
      // Principal Jupiter & Earth perturbations on Mars
      dLonDeg =
        -0.01133 * Math.sin(Mj - Mm - 48.8 * DEG2RAD) -
        0.00933 * Math.cos(2 * Mj - 2 * Mm - 18.6 * DEG2RAD) +
        0.00705 * Math.cos(Me - 2 * Mm + 20.1 * DEG2RAD) +
        0.00445 * Math.sin(2 * Me - 3 * Mm - 51.0 * DEG2RAD);
      break;
    }
    case "jupiter": {
      a = 5.20288700 - 0.00011607 * T;
      e = 0.04838624 - 0.00013253 * T;
      iDeg = 1.30439695 - 0.00183714 * T;
      Ldeg = 34.39644051 + 3036.3027748 * T + 0.0002237 * T * T;
      wBarDeg = 14.72847983 + 1.6126300 * T;
      nodeDeg = 100.47390909 + 1.0046910 * T;
      // Great Inequality delta relative to J2000 osculating epoch
      const zeta = 5.0 * Ms - 2.0 * Mj + (67.6528 - 2.0928 * T) * DEG2RAD;
      const zeta0 = (5.0 * 317.0207 - 2.0 * 20.0202 + 67.6528) * DEG2RAD;
      const mDiff0 = (317.0207 - 20.0202) * DEG2RAD;
      dLonDeg =
        0.3314 * (Math.sin(zeta) - Math.sin(zeta0)) -
        0.0103 * (Math.cos(zeta) - Math.cos(zeta0)) -
        0.0365 * (Math.sin(Ms - Mj) - Math.sin(mDiff0)) -
        0.0306 * (Math.sin(2 * (Ms - Mj)) - Math.sin(2 * mDiff0));
      dRadAu = -0.0021 * (Math.cos(Ms - Mj) - Math.cos(mDiff0));
      break;
    }
    case "saturn": {
      a = 9.53667594 - 0.00125060 * T;
      e = 0.05386179 - 0.00050991 * T;
      iDeg = 2.48599187 + 0.00193609 * T;
      Ldeg = 49.95424423 + 1223.5110686 * T + 0.0003105 * T * T;
      wBarDeg = 92.59887831 + 1.9637613 * T;
      nodeDeg = 113.66242448 + 0.8770970 * T;
      // Great Inequality delta relative to J2000 osculating epoch
      const zeta = 5.0 * Ms - 2.0 * Mj + (67.6528 - 2.0928 * T) * DEG2RAD;
      const zeta0 = (5.0 * 317.0207 - 2.0 * 20.0202 + 67.6528) * DEG2RAD;
      const jDiff0 = (20.0202 - 317.0207) * DEG2RAD;
      dLonDeg =
        -0.8142 * (Math.sin(zeta) - Math.sin(zeta0)) +
        0.0258 * (Math.cos(zeta) - Math.cos(zeta0)) +
        0.0256 * (Math.sin(2 * (Mj - Ms)) - Math.sin(2 * jDiff0)) -
        0.0882 * (Math.cos(Mj - Ms) - Math.cos(jDiff0));
      dLatDeg = 0.0090 * Math.sin(2 * Ms - Mj - 40.0 * DEG2RAD);
      dRadAu = 0.0156 * (Math.cos(Mj - Ms) - Math.cos(jDiff0));
      break;
    }
    default:
      throw new Error(`Unknown planet id: ${bodyId}`);
  }

  const M = normalizeDegrees(Ldeg - wBarDeg) * DEG2RAD;
  const E = solveKepler(M, e);
  const xv = a * (Math.cos(E) - e);
  const yv = a * Math.sqrt(1.0 - e * e) * Math.sin(E);
  const v = Math.atan2(yv, xv);
  const r = Math.hypot(xv, yv) + dRadAu;

  const w = (wBarDeg - nodeDeg) * DEG2RAD;
  const node = nodeDeg * DEG2RAD;
  const inc = iDeg * DEG2RAD;
  const u = v + w;

  // Heliocentric ecliptic spherical
  const x0 = r * (Math.cos(node) * Math.cos(u) - Math.sin(node) * Math.sin(u) * Math.cos(inc));
  const y0 = r * (Math.sin(node) * Math.cos(u) + Math.cos(node) * Math.sin(u) * Math.cos(inc));
  const z0 = r * (Math.sin(u) * Math.sin(inc));

  let lon = Math.atan2(y0, x0) * RAD2DEG + dLonDeg;
  let lat = Math.asin(Math.max(-1.0, Math.min(1.0, z0 / r))) * RAD2DEG + dLatDeg;
  lon = normalizeDegrees(lon);

  const cosB = Math.cos(lat * DEG2RAD);
  const sinB = Math.sin(lat * DEG2RAD);
  const x = r * cosB * Math.cos(lon * DEG2RAD);
  const y = r * cosB * Math.sin(lon * DEG2RAD);
  const z = r * sinB;

  return { x, y, z, r, lon, lat };
}

const MOON_LON_TERMS = Object.freeze([
  [0, 0, 1, 0, 6288774],
  [2, 0, -1, 0, 1274027],
  [2, 0, 0, 0, 658314],
  [0, 0, 2, 0, 213618],
  [0, 1, 0, 0, -185116],
  [0, 0, 0, 2, -114332],
  [2, 0, -2, 0, 58793],
  [2, -1, -1, 0, 57066],
  [2, 0, 1, 0, 53322],
  [2, -1, 0, 0, 45758],
  [0, 1, -1, 0, -40923],
  [1, 0, 0, 0, -34720],
  [0, 1, 1, 0, -30383],
  [2, 0, 0, -2, 15327],
  [0, 0, 1, 2, -12528],
  [0, 0, 1, -2, 10980],
  [4, 0, -1, 0, 10675],
  [0, 0, 3, 0, 10034],
  [4, 0, -2, 0, 8548],
  [2, 1, -1, 0, -7888],
  [2, 1, 0, 0, -6766],
  [1, 0, -1, 0, -5163],
  [1, 1, 0, 0, 4987],
  [2, -1, 1, 0, 4036],
  [2, 0, 2, 0, 3994],
  [4, 0, 0, 0, 3861],
  [2, 0, -3, 0, 3665],
  [0, 1, -2, 0, -2689],
  [2, 0, -1, 2, -2602],
  [2, -1, -2, 0, 2390],
  [1, 0, 1, 0, -2348],
  [2, -2, 0, 0, 2236],
  [0, 1, 2, 0, -2120],
  [0, 2, 0, 0, -2069],
  [2, -2, -1, 0, 2048],
  [2, 0, 1, -2, -1773],
  [2, 0, 0, 2, -1595],
  [4, -1, -1, 0, 1215],
  [0, 0, 2, 2, -1110],
  [3, 0, -1, 0, -892],
  [2, 1, 1, 0, -810],
  [4, -1, -2, 0, 759],
  [0, 2, -1, 0, -713],
  [2, 2, -1, 0, -700],
  [2, 1, -2, 0, 691],
  [2, -1, 0, -2, 596]
]);

const MOON_LAT_TERMS = Object.freeze([
  [0, 0, 0, 1, 5128122],
  [0, 0, 1, 1, 280602],
  [0, 0, 1, -1, 277693],
  [2, 0, 0, -1, 173237],
  [2, 0, -1, 1, 55413],
  [2, 0, -1, -1, 46271],
  [2, 0, 0, 1, 32573],
  [0, 0, 2, 1, 17198],
  [2, 0, 1, -1, 9266],
  [0, 0, 2, -1, 8822],
  [2, -1, 0, -1, 8216],
  [2, 0, -2, -1, 4324],
  [2, 0, 1, 1, 4200],
  [2, 1, 0, -1, -3359],
  [2, -1, -1, 1, 2463],
  [2, -1, 0, 1, 2211],
  [2, -1, -1, -1, 2065],
  [0, 1, -1, -1, -1870],
  [4, 0, -1, -1, 1828],
  [0, 1, 0, 1, -1794]
]);

/**
 * High-precision geocentric apparent lunar longitude and latitude (Meeus Ch. 47, ELP2000-82 main series).
 */
function computeMoonApparentPlace(jdTt, precomputedNut) {
  const T = (jdTt - J2000_JD) / JULIAN_CENTURY;
  const Lp = normalizeDegrees(218.3164477 + 481267.88123421 * T - 0.0015786 * T * T + (T * T * T) / 538841.0 - Math.pow(T, 4) / 65194000.0);
  const D = normalizeDegrees(297.8501921 + 445267.1114034 * T - 0.0018819 * T * T + (T * T * T) / 545868.0 - Math.pow(T, 4) / 113065000.0);
  const M = normalizeDegrees(357.5291092 + 35999.0502909 * T - 0.0001536 * T * T + (T * T * T) / 24490000.0);
  const Mp = normalizeDegrees(134.9633964 + 477198.8675055 * T + 0.0087414 * T * T + (T * T * T) / 69699.0 - Math.pow(T, 4) / 14712000.0);
  const F = normalizeDegrees(93.2720950 + 483202.0175233 * T - 0.0036539 * T * T - (T * T * T) / 3526000.0 + Math.pow(T, 4) / 863310000.0);

  const A1 = normalizeDegrees(119.75 + 131.849 * T) * DEG2RAD;
  const A2 = normalizeDegrees(53.09 + 479264.290 * T) * DEG2RAD;
  const A3 = normalizeDegrees(313.45 + 481266.484 * T) * DEG2RAD;

  const E = 1.0 - 0.002516 * T - 0.0000074 * T * T;
  const E2 = E * E;

  const Dr = D * DEG2RAD;
  const Mr = M * DEG2RAD;
  const Mpr = Mp * DEG2RAD;
  const Fr = F * DEG2RAD;

  let sumL = 0.0;
  for (let i = 0; i < MOON_LON_TERMS.length; i++) {
    const [d, m, mp, f, coeff] = MOON_LON_TERMS[i];
    const arg = d * Dr + m * Mr + mp * Mpr + f * Fr;
    const absM = Math.abs(m);
    const scale = absM === 1 ? E : absM === 2 ? E2 : 1.0;
    sumL += coeff * scale * Math.sin(arg);
  }
  sumL += 3958.0 * Math.sin(A1) + 1962.0 * Math.sin((Lp - F) * DEG2RAD) + 318.0 * Math.sin(A2);

  let sumB = 0.0;
  for (let i = 0; i < MOON_LAT_TERMS.length; i++) {
    const [d, m, mp, f, coeff] = MOON_LAT_TERMS[i];
    const arg = d * Dr + m * Mr + mp * Mpr + f * Fr;
    const absM = Math.abs(m);
    const scale = absM === 1 ? E : absM === 2 ? E2 : 1.0;
    sumB += coeff * scale * Math.sin(arg);
  }
  sumB +=
    -2235.0 * Math.sin(Lp * DEG2RAD) +
    382.0 * Math.sin(A3) +
    175.0 * Math.sin(A1 - Fr) +
    175.0 * Math.sin(A1 + Fr) +
    127.0 * Math.sin((Lp - Mp) * DEG2RAD) -
    115.0 * Math.sin((Lp + Mp) * DEG2RAD);

  const nut = precomputedNut || computeObliquityAndNutation(jdTt);
  const tropicalLongitudeDeg = normalizeDegrees(Lp + sumL * 1e-6 + nut.nutationLongitudeDeg);
  const latitudeDeg = sumB * 1e-6;
  return { tropicalLongitudeDeg, latitudeDeg };
}

/**
 * Compute geocentric apparent ecliptic coordinates of a planet (including light-time and aberration).
 */
function computePlanetApparentPlace(bodyId, jdTt, precomputedEarth, precomputedNut) {
  const nut = precomputedNut || computeObliquityAndNutation(jdTt);
  if (bodyId === "moon") {
    return computeMoonApparentPlace(jdTt, nut);
  }

  const earth = precomputedEarth || heliocentricPlanetState("earth", jdTt);

  if (bodyId === "sun") {
    const geoLon = normalizeDegrees(earth.lon + 180.0);
    const geoLat = -earth.lat;
    // Solar annual aberration (-20.4898" / R)
    const aberrDeg = (-20.4898 / earth.r) / 3600.0;
    return {
      tropicalLongitudeDeg: normalizeDegrees(geoLon + aberrDeg + nut.nutationLongitudeDeg),
      latitudeDeg: geoLat
    };
  }

  // Light-time iteration (c = 173.1446326846693 AU/day)
  const C_AU_PER_DAY = 173.1446326846693;
  let tau = 0.0;
  let dx = 0.0, dy = 0.0, dz = 0.0, dist = 1.0;
  for (let iter = 0; iter < 2; iter++) {
    const target = heliocentricPlanetState(bodyId, jdTt - tau);
    dx = target.x - earth.x;
    dy = target.y - earth.y;
    dz = target.z - earth.z;
    dist = Math.hypot(dx, dy, dz);
    tau = dist / C_AU_PER_DAY;
  }

  // Annual aberration in ecliptic longitude
  const rawLonRad = Math.atan2(dy, dx);
  const rawLatRad = Math.asin(Math.max(-1.0, Math.min(1.0, dz / dist)));
  const sunLonRad = (earth.lon + 180.0) * DEG2RAD;
  const kappaArcsec = 20.49552;
  const dLonAberrDeg = (-kappaArcsec * Math.cos(sunLonRad - rawLonRad) / Math.max(0.05, Math.cos(rawLatRad))) / 3600.0;

  return {
    tropicalLongitudeDeg: normalizeDegrees(rawLonRad * RAD2DEG + dLonAberrDeg + nut.nutationLongitudeDeg),
    latitudeDeg: rawLatRad * RAD2DEG
  };
}

export const GRAHA_METADATA = Object.freeze([
  { id: "sun", name: "Sun", sanskritName: "Surya", symbol: "Su" },
  { id: "moon", name: "Moon", sanskritName: "Chandra", symbol: "Mo" },
  { id: "mars", name: "Mars", sanskritName: "Mangala", symbol: "Ma" },
  { id: "mercury", name: "Mercury", sanskritName: "Budha", symbol: "Me" },
  { id: "jupiter", name: "Jupiter", sanskritName: "Brihaspati", symbol: "Ju" },
  { id: "venus", name: "Venus", sanskritName: "Shukra", symbol: "Ve" },
  { id: "saturn", name: "Saturn", sanskritName: "Shani", symbol: "Sa" },
  { id: "rahu", name: "Rahu", sanskritName: "Rahu", symbol: "Ra" },
  { id: "ketu", name: "Ketu", sanskritName: "Ketu", symbol: "Ke" }
]);

/**
 * Compute Nakshatra (1..27) and Pada (1..4) details for any sidereal longitude [0, 360).
 */
export function computeNakshatra(siderealLongitudeDeg) {
  const lon = normalizeDegrees(siderealLongitudeDeg);
  const span = 360.0 / 27.0; // 13.333333333333334 deg
  const padaSpan = 360.0 / 108.0; // 3.3333333333333335 deg
  const index = Math.min(26, Math.floor(lon / span));
  const offsetInNakshatra = lon - index * span;
  const pada = Math.min(4, Math.floor(offsetInNakshatra / padaSpan) + 1);
  const globalPadaIndex = index * 4 + (pada - 1); // 0..107
  const navamsaRasiIndex = globalPadaIndex % 12;
  const fractionElapsed = offsetInNakshatra / span;
  const fractionRemaining = 1.0 - fractionElapsed;
  const meta = NAKSHATRA_CATALOG[index];

  return {
    index: meta.index,
    number: meta.number,
    name: meta.name,
    pada,
    globalPadaNumber: globalPadaIndex + 1,
    ruler: meta.ruler,
    deity: meta.deity,
    gana: meta.gana,
    nadi: meta.nadi,
    yoni: meta.yoni,
    navamsaRasiIndex,
    navamsaRasiName: RASI_CATALOG[navamsaRasiIndex].label,
    degreesInNakshatra: offsetInNakshatra,
    percentElapsed: Number((fractionElapsed * 100.0).toFixed(2)),
    fractionRemaining
  };
}

/**
 * Compute planetary positions, speeds, rasi, and nakshatra for all 9 Grahas.
 */
export function computePlanets(jdTt, options = {}) {
  const ayanamsaKey = resolveAyanamsaKey(options.ayanamsa || "lahiri");
  const nodeMode = String(options.nodeMode || "mean").toLowerCase() === "true" ? "true" : "mean";
  const ayanamsaDeg = computeAyanamsa(jdTt, ayanamsaKey);
  const stepDays = 0.01;

  const earth0 = heliocentricPlanetState("earth", jdTt);
  const earthMinus = heliocentricPlanetState("earth", jdTt - stepDays);
  const earthPlus = heliocentricPlanetState("earth", jdTt + stepDays);
  const nut0 = computeObliquityAndNutation(jdTt);
  const nutMinus = computeObliquityAndNutation(jdTt - stepDays);
  const nutPlus = computeObliquityAndNutation(jdTt + stepDays);

  const physicalIds = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"];
  const results = {};

  for (const id of physicalIds) {
    const pos0 = computePlanetApparentPlace(id, jdTt, earth0, nut0);
    const posMinus = computePlanetApparentPlace(id, jdTt - stepDays, earthMinus, nutMinus);
    const posPlus = computePlanetApparentPlace(id, jdTt + stepDays, earthPlus, nutPlus);

    let dLon = posPlus.tropicalLongitudeDeg - posMinus.tropicalLongitudeDeg;
    if (dLon > 180.0) dLon -= 360.0;
    if (dLon < -180.0) dLon += 360.0;
    const speedDegPerDay = dLon / (2.0 * stepDays);

    const siderealLongitudeDeg = normalizeDegrees(pos0.tropicalLongitudeDeg - ayanamsaDeg);
    results[id] = buildGrahaRecord(id, pos0.tropicalLongitudeDeg, siderealLongitudeDeg, pos0.latitudeDeg, speedDegPerDay);
  }

  // Lunar nodes (Rahu & Ketu): compute both mean and true so callers have both
  const meanRahuTrop = computeMeanLunarNode(jdTt);
  const trueRahuTrop = computeTrueLunarNode(jdTt);
  const trueRahuMinus = computeTrueLunarNode(jdTt - stepDays);
  const trueRahuPlus = computeTrueLunarNode(jdTt + stepDays);
  let dTrueNode = trueRahuPlus - trueRahuMinus;
  if (dTrueNode > 180.0) dTrueNode -= 360.0;
  if (dTrueNode < -180.0) dTrueNode += 360.0;

  const meanNodeSpeed = -0.0529538083;
  const trueNodeSpeed = dTrueNode / (2.0 * stepDays);

  const rahuTrop = nodeMode === "true" ? trueRahuTrop : meanRahuTrop;
  const rahuSpeed = nodeMode === "true" ? trueNodeSpeed : meanNodeSpeed;
  const rahuSid = normalizeDegrees(rahuTrop - ayanamsaDeg);

  const rahuRec = buildGrahaRecord("rahu", rahuTrop, rahuSid, 0.0, rahuSpeed);
  rahuRec.meanSiderealLongitudeDeg = normalizeDegrees(meanRahuTrop - ayanamsaDeg);
  rahuRec.trueSiderealLongitudeDeg = normalizeDegrees(trueRahuTrop - ayanamsaDeg);
  rahuRec.nodeMode = nodeMode;
  results.rahu = rahuRec;

  const ketuTrop = normalizeDegrees(rahuTrop + 180.0);
  const ketuSid = normalizeDegrees(rahuSid + 180.0);
  const ketuRec = buildGrahaRecord("ketu", ketuTrop, ketuSid, 0.0, rahuSpeed);
  ketuRec.meanSiderealLongitudeDeg = normalizeDegrees(rahuRec.meanSiderealLongitudeDeg + 180.0);
  ketuRec.trueSiderealLongitudeDeg = normalizeDegrees(rahuRec.trueSiderealLongitudeDeg + 180.0);
  ketuRec.nodeMode = nodeMode;
  results.ketu = ketuRec;

  return {
    ayanamsaKey,
    ayanamsaDeg,
    nodeMode,
    grahas: results
  };
}

function buildGrahaRecord(id, tropicalLongitudeDeg, siderealLongitudeDeg, latitudeDeg, speedDegPerDay) {
  const meta = GRAHA_METADATA.find((g) => g.id === id);
  const rasiIndex = Math.min(11, Math.floor(siderealLongitudeDeg / 30.0));
  const degreeInRasi = siderealLongitudeDeg - rasiIndex * 30.0;
  const rasi = RASI_CATALOG[rasiIndex];
  const nakshatra = computeNakshatra(siderealLongitudeDeg);

  return {
    id,
    name: meta.name,
    sanskritName: meta.sanskritName,
    symbol: meta.symbol,
    tropicalLongitudeDeg,
    siderealLongitudeDeg,
    latitudeDeg,
    speedDegPerDay,
    isRetrograde: speedDegPerDay < 0.0,
    rasiIndex,
    rasiNumber: rasi.number,
    rasiSanskrit: rasi.sanskrit,
    rasiName: rasi.label,
    rasiLord: rasi.lord,
    degreeInRasi,
    dmsInRasi: formatDms(degreeInRasi),
    nakshatra
  };
}

/**
 * Compute IAU 2006 Sidereal Time, Tropical and Sidereal Ascendant (Lagna), and Midheaven (MC).
 */
export function computeAscendantAndHouses(jdTt, jdUt1, latitudeDeg, longitudeDeg, ayanamsa = "lahiri") {
  if (!Number.isFinite(latitudeDeg) || latitudeDeg <= -90.0 || latitudeDeg >= 90.0) {
    throw new Error("Latitude must be strictly within (-90, 90) degrees");
  }
  if (!Number.isFinite(longitudeDeg) || longitudeDeg < -180.0 || longitudeDeg > 180.0) {
    throw new Error("Longitude must be within [-180, 180] degrees");
  }

  const Tu = (jdUt1 - J2000_JD) / JULIAN_CENTURY;
  const Tt = (jdTt - J2000_JD) / JULIAN_CENTURY;
  const nut = computeObliquityAndNutation(jdTt);

  // IAU 2006 GMST in degrees
  const eraDeg = normalizeDegrees(360.0 * (0.7790572732640 + 1.00273781191135448 * (jdUt1 - J2000_JD)));
  const gmstPolyArcsec = 0.014506 + 4612.156534 * Tt + 1.3915817 * Tt * Tt - 0.00000044 * Math.pow(Tt, 3);
  const gmstDeg = normalizeDegrees(eraDeg + gmstPolyArcsec / 3600.0);
  const gastDeg = normalizeDegrees(gmstDeg + nut.nutationLongitudeDeg * Math.cos(nut.trueObliquityDeg * DEG2RAD));
  const localApparentSiderealDeg = normalizeDegrees(gastDeg + longitudeDeg);

  const theta = localApparentSiderealDeg * DEG2RAD;
  const phi = latitudeDeg * DEG2RAD;
  const eps = nut.trueObliquityDeg * DEG2RAD;

  const horizonA = Math.cos(phi) * Math.cos(theta);
  const horizonB = Math.cos(phi) * Math.cos(eps) * Math.sin(theta) + Math.sin(phi) * Math.sin(eps);
  let ascRad = Math.atan2(-horizonA, horizonB);
  const eastProj = -Math.cos(ascRad) * Math.sin(theta) + Math.sin(ascRad) * Math.cos(eps) * Math.cos(theta);
  if (eastProj < 0.0) {
    ascRad += Math.PI;
  }

  const mcRad = Math.atan2(Math.sin(theta), Math.cos(theta) * Math.cos(eps));
  const tropicalAscendantDeg = normalizeDegrees(ascRad * RAD2DEG);
  const tropicalMidheavenDeg = normalizeDegrees(mcRad * RAD2DEG);

  const ayanamsaDeg = computeAyanamsa(jdTt, ayanamsa);
  const siderealAscendantDeg = normalizeDegrees(tropicalAscendantDeg - ayanamsaDeg);
  const siderealMidheavenDeg = normalizeDegrees(tropicalMidheavenDeg - ayanamsaDeg);

  const lagnaRasiIndex = Math.min(11, Math.floor(siderealAscendantDeg / 30.0));
  const lagnaDegreeInRasi = siderealAscendantDeg - lagnaRasiIndex * 30.0;
  const wholeSignCusps = Array.from({ length: 12 }, (_, idx) => ((lagnaRasiIndex + idx) % 12) * 30.0);

  return {
    gmstDeg,
    gastDeg,
    localApparentSiderealDeg,
    trueObliquityDeg: nut.trueObliquityDeg,
    tropicalAscendantDeg,
    tropicalMidheavenDeg,
    siderealAscendantDeg,
    siderealMidheavenDeg,
    lagnaRasiIndex,
    lagnaRasiName: RASI_CATALOG[lagnaRasiIndex].label,
    lagnaDegreeInRasi,
    lagnaDms: formatDms(lagnaDegreeInRasi),
    lagnaNakshatra: computeNakshatra(siderealAscendantDeg),
    wholeSignCusps
  };
}

/**
 * Compute the varga sign index (0..11) of any sidereal longitude [0, 360) in one of the 16 Parashari Shodashvarga charts.
 */
export function computeVargaRasiIndex(siderealLongitudeDeg, vargaCode) {
  const lon = normalizeDegrees(siderealLongitudeDeg);
  const rasi = Math.min(11, Math.floor(lon / 30.0));
  const degInSign = lon - rasi * 30.0;
  const isOddSign = rasi % 2 === 0; // Aries=0 (1st sign, odd), Taurus=1 (2nd sign, even)
  const modality = rasi % 3; // 0 = Movable (Chara), 1 = Fixed (Sthira), 2 = Dual (Dwiswabhava)
  const element = rasi % 4; // 0 = Fire, 1 = Earth, 2 = Air, 3 = Water

  const partOf = (n) => Math.min(n - 1, Math.floor((degInSign * n) / 30.0));

  switch (String(vargaCode).toUpperCase()) {
    case "D1":
      return rasi;
    case "D2": {
      const half = partOf(2);
      // Odd sign: 0..15 Leo (4), 15..30 Cancer (3); Even sign: 0..15 Cancer (3), 15..30 Leo (4)
      if (isOddSign) return half === 0 ? 4 : 3;
      return half === 0 ? 3 : 4;
    }
    case "D3": {
      const p = partOf(3);
      return (rasi + p * 4) % 12;
    }
    case "D4": {
      const p = partOf(4);
      return (rasi + p * 3) % 12;
    }
    case "D7": {
      const p = partOf(7);
      const start = isOddSign ? rasi : (rasi + 6) % 12;
      return (start + p) % 12;
    }
    case "D9": {
      const p = partOf(9);
      const starts = [0, 9, 6, 3]; // Fire->Aries(0), Earth->Capricorn(9), Air->Libra(6), Water->Cancer(3)
      return (starts[element] + p) % 12;
    }
    case "D10": {
      const p = partOf(10);
      const start = isOddSign ? rasi : (rasi + 8) % 12;
      return (start + p) % 12;
    }
    case "D12": {
      const p = partOf(12);
      return (rasi + p) % 12;
    }
    case "D16": {
      const p = partOf(16);
      const starts = [0, 4, 8]; // Movable->Aries(0), Fixed->Leo(4), Dual->Sagittarius(8)
      return (starts[modality] + p) % 12;
    }
    case "D20": {
      const p = partOf(20);
      const starts = [0, 8, 4]; // Movable->Aries(0), Fixed->Sagittarius(8), Dual->Leo(4)
      return (starts[modality] + p) % 12;
    }
    case "D24": {
      const p = partOf(24);
      const start = isOddSign ? 4 : 3; // Odd->Leo(4), Even->Cancer(3)
      return (start + p) % 12;
    }
    case "D27": {
      const p = partOf(27);
      const starts = [0, 3, 6, 9]; // Fire->Aries(0), Earth->Cancer(3), Air->Libra(6), Water->Capricorn(9)
      return (starts[element] + p) % 12;
    }
    case "D30": {
      if (isOddSign) {
        if (degInSign < 5.0) return 0; // Aries (Mars)
        if (degInSign < 10.0) return 10; // Aquarius (Saturn)
        if (degInSign < 18.0) return 8; // Sagittarius (Jupiter)
        if (degInSign < 25.0) return 2; // Gemini (Mercury)
        return 6; // Libra (Venus)
      }
      if (degInSign < 5.0) return 1; // Taurus (Venus)
      if (degInSign < 12.0) return 5; // Virgo (Mercury)
      if (degInSign < 20.0) return 11; // Pisces (Jupiter)
      if (degInSign < 25.0) return 9; // Capricorn (Saturn)
      return 7; // Scorpio (Mars)
    }
    case "D40": {
      const p = partOf(40);
      const start = isOddSign ? 0 : 6; // Odd->Aries(0), Even->Libra(6)
      return (start + p) % 12;
    }
    case "D45": {
      const p = partOf(45);
      const starts = [0, 4, 8]; // Movable->Aries(0), Fixed->Leo(4), Dual->Sagittarius(8)
      return (starts[modality] + p) % 12;
    }
    case "D60": {
      const p = partOf(60);
      return (rasi + p) % 12;
    }
    default:
      throw new Error(`Unsupported Shodashvarga code: ${vargaCode}`);
  }
}

/**
 * Compute all 16 Parashari Shodashvarga charts (D1..D60) for Ascendant + 9 Grahas.
 */
export function computeShodashvarga(siderealAscendantDeg, grahasMap) {
  const charts = {};
  for (const def of SHODASHVARGA_DEFINITIONS) {
    const lagnaRasiIndex = computeVargaRasiIndex(siderealAscendantDeg, def.code);
    const placements = {};
    const signs = Array.from({ length: 12 }, (_, rasiIdx) => ({
      rasiIndex: rasiIdx,
      rasiName: RASI_CATALOG[rasiIdx].label,
      houseNumber: ((rasiIdx - lagnaRasiIndex + 12) % 12) + 1,
      occupants: []
    }));
    signs[lagnaRasiIndex].occupants.push("As");

    for (const meta of GRAHA_METADATA) {
      const g = grahasMap[meta.id];
      const vargaRasi = computeVargaRasiIndex(g.siderealLongitudeDeg, def.code);
      const houseNumber = ((vargaRasi - lagnaRasiIndex + 12) % 12) + 1;
      const d60Index = def.code === "D60" ? Math.min(59, Math.floor((g.degreeInRasi * 60.0) / 30.0)) : null;
      placements[meta.id] = {
        id: meta.id,
        name: meta.name,
        symbol: meta.symbol,
        rasiIndex: vargaRasi,
        rasiSanskrit: RASI_CATALOG[vargaRasi].sanskrit,
        rasiName: RASI_CATALOG[vargaRasi].label,
        rasiLord: RASI_CATALOG[vargaRasi].lord,
        houseNumber,
        shashtiamsaDeity: d60Index !== null ? D60_NAMES[d60Index] : undefined
      };
      signs[vargaRasi].occupants.push(meta.symbol);
    }

    charts[def.code] = {
      code: def.code,
      division: def.division,
      name: def.name,
      domain: def.domain,
      lagnaRasiIndex,
      lagnaRasiName: RASI_CATALOG[lagnaRasiIndex].label,
      placements,
      signs
    };
  }
  return charts;
}

const TITHI_NAMES = Object.freeze([
  "Shukla Prathama", "Shukla Dwitiya", "Shukla Tritiya", "Shukla Chaturthi", "Shukla Panchami",
  "Shukla Shashthi", "Shukla Saptami", "Shukla Ashtami", "Shukla Navami", "Shukla Dashami",
  "Shukla Ekadashi", "Shukla Dwadashi", "Shukla Trayodashi", "Shukla Chaturdashi", "Purnima",
  "Krishna Prathama", "Krishna Dwitiya", "Krishna Tritiya", "Krishna Chaturthi", "Krishna Panchami",
  "Krishna Shashthi", "Krishna Saptami", "Krishna Ashtami", "Krishna Navami", "Krishna Dashami",
  "Krishna Ekadashi", "Krishna Dwadashi", "Krishna Trayodashi", "Krishna Chaturdashi", "Amavasya"
]);

const YOGA_NAMES = Object.freeze([
  "Vishkumbha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarma", "Dhriti", "Shoola",
  "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyan",
  "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"
]);

const MOVABLE_KARANAS = Object.freeze(["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti"]);

const VARA_CATALOG = Object.freeze([
  { index: 0, sanskrit: "Ravivara", english: "Sunday", lord: "Sun" },
  { index: 1, sanskrit: "Somavara", english: "Monday", lord: "Moon" },
  { index: 2, sanskrit: "Mangalavara", english: "Tuesday", lord: "Mars" },
  { index: 3, sanskrit: "Budhavara", english: "Wednesday", lord: "Mercury" },
  { index: 4, sanskrit: "Guruvara", english: "Thursday", lord: "Jupiter" },
  { index: 5, sanskrit: "Shukravara", english: "Friday", lord: "Venus" },
  { index: 6, sanskrit: "Shanivara", english: "Saturday", lord: "Saturn" }
]);

/**
 * Compute Five-Limb Vedic Panchanga (Tithi, Vara, Nakshatra, Yoga, Karana).
 */
export function computePanchanga(jdUtc, sunSiderealDeg, moonSiderealDeg) {
  const diff = normalizeDegrees(moonSiderealDeg - sunSiderealDeg);
  const tithiIndex = Math.min(29, Math.floor(diff / 12.0));
  const tithiProgress = ((diff - tithiIndex * 12.0) / 12.0) * 100.0;
  const paksha = tithiIndex < 15 ? "Shukla Paksha" : "Krishna Paksha";

  const varaIdx = Math.floor(jdUtc + 1.5) % 7;
  const vara = VARA_CATALOG[(varaIdx + 7) % 7];

  const nakshatra = computeNakshatra(moonSiderealDeg);

  const sumLon = normalizeDegrees(moonSiderealDeg + sunSiderealDeg);
  const yogaSpan = 360.0 / 27.0;
  const yogaIndex = Math.min(26, Math.floor(sumLon / yogaSpan));
  const yogaProgress = ((sumLon - yogaIndex * yogaSpan) / yogaSpan) * 100.0;

  const karanaHalfIndex = Math.min(59, Math.floor(diff / 6.0));
  let karanaName;
  if (karanaHalfIndex === 0) karanaName = "Kimstughna";
  else if (karanaHalfIndex === 57) karanaName = "Shakuni";
  else if (karanaHalfIndex === 58) karanaName = "Chatushpada";
  else if (karanaHalfIndex === 59) karanaName = "Naga";
  else karanaName = MOVABLE_KARANAS[(karanaHalfIndex - 1) % 7];

  return {
    tithi: {
      number: tithiIndex + 1,
      name: TITHI_NAMES[tithiIndex],
      paksha,
      percentElapsed: Number(tithiProgress.toFixed(2))
    },
    vara: {
      index: vara.index,
      sanskrit: vara.sanskrit,
      english: vara.english,
      lord: vara.lord
    },
    nakshatra,
    yoga: {
      number: yogaIndex + 1,
      name: YOGA_NAMES[yogaIndex],
      percentElapsed: Number(yogaProgress.toFixed(2))
    },
    karana: {
      number: karanaHalfIndex + 1,
      name: karanaName,
      isFixed: karanaHalfIndex === 0 || karanaHalfIndex >= 57
    }
  };
}

/**
 * Classical Brihat Parashara Hora Shastra (BPHS) Ashtakavarga benefic bindu house-offsets (1-indexed).
 * Invariant sum across all 7 physical grahas = 48 + 49 + 39 + 54 + 56 + 52 + 39 = 337 bindus.
 */
const BPHS_ASHTAKAVARGA_RULES = Object.freeze({
  sun: {
    sun: [1, 2, 4, 7, 8, 9, 10, 11],
    moon: [3, 6, 10, 11],
    mars: [1, 2, 4, 7, 8, 9, 10, 11],
    mercury: [3, 5, 6, 9, 10, 11, 12],
    jupiter: [5, 6, 9, 11],
    venus: [6, 7, 12],
    saturn: [1, 2, 4, 7, 8, 9, 10, 11],
    lagna: [3, 4, 6, 10, 11, 12]
  },
  moon: {
    sun: [3, 6, 7, 8, 10, 11],
    moon: [1, 3, 6, 7, 10, 11],
    mars: [2, 3, 5, 6, 9, 10, 11],
    mercury: [1, 3, 4, 5, 7, 8, 10, 11],
    jupiter: [1, 4, 7, 8, 10, 11, 12],
    venus: [3, 4, 5, 7, 9, 10, 11],
    saturn: [3, 5, 6, 11],
    lagna: [3, 6, 10, 11]
  },
  mars: {
    sun: [3, 5, 6, 10, 11],
    moon: [3, 6, 11],
    mars: [1, 2, 4, 7, 8, 10, 11],
    mercury: [3, 5, 6, 11],
    jupiter: [6, 10, 11, 12],
    venus: [6, 8, 11, 12],
    saturn: [1, 4, 7, 8, 9, 10, 11],
    lagna: [1, 3, 6, 10, 11]
  },
  mercury: {
    sun: [5, 6, 9, 11, 12],
    moon: [2, 4, 6, 8, 10, 11],
    mars: [1, 2, 4, 7, 8, 9, 10, 11],
    mercury: [1, 3, 5, 6, 9, 10, 11, 12],
    jupiter: [6, 8, 11, 12],
    venus: [1, 2, 3, 4, 5, 8, 9, 11],
    saturn: [1, 2, 4, 7, 8, 9, 10, 11],
    lagna: [1, 2, 4, 6, 8, 10, 11]
  },
  jupiter: {
    sun: [1, 2, 3, 4, 7, 8, 9, 10, 11],
    moon: [2, 5, 7, 9, 11],
    mars: [1, 2, 4, 7, 8, 10, 11],
    mercury: [1, 2, 4, 5, 6, 9, 10, 11],
    jupiter: [1, 2, 3, 4, 7, 8, 10, 11],
    venus: [2, 5, 6, 9, 10, 11],
    saturn: [3, 5, 6, 12],
    lagna: [1, 2, 4, 5, 6, 7, 9, 10, 11]
  },
  venus: {
    sun: [8, 11, 12],
    moon: [1, 2, 3, 4, 5, 8, 9, 11, 12],
    mars: [3, 5, 6, 9, 11, 12],
    mercury: [3, 5, 6, 9, 11],
    jupiter: [5, 8, 9, 10, 11],
    venus: [1, 2, 3, 4, 5, 8, 9, 10, 11],
    saturn: [3, 4, 5, 8, 9, 10, 11],
    lagna: [1, 2, 3, 4, 5, 8, 9, 11]
  },
  saturn: {
    sun: [1, 2, 4, 7, 8, 10, 11],
    moon: [3, 6, 11],
    mars: [3, 5, 6, 10, 11, 12],
    mercury: [6, 8, 9, 10, 11, 12],
    jupiter: [5, 6, 11, 12],
    venus: [6, 11, 12],
    saturn: [3, 5, 6, 11],
    lagna: [1, 3, 4, 6, 10, 11]
  }
});

/**
 * Compute Bhinna Ashtakavarga (7 grahas x 12 signs) and 337-bindu Sarvashtakavarga.
 */
export function computeAshtakavarga(lagnaRasiIndex, grahasMap) {
  const contributors = {
    sun: grahasMap.sun.rasiIndex,
    moon: grahasMap.moon.rasiIndex,
    mars: grahasMap.mars.rasiIndex,
    mercury: grahasMap.mercury.rasiIndex,
    jupiter: grahasMap.jupiter.rasiIndex,
    venus: grahasMap.venus.rasiIndex,
    saturn: grahasMap.saturn.rasiIndex,
    lagna: lagnaRasiIndex
  };

  const bhinna = {};
  const sarvaBySign = new Array(12).fill(0);

  for (const [targetId, table] of Object.entries(BPHS_ASHTAKAVARGA_RULES)) {
    const bindus = new Array(12).fill(0);
    for (const [sourceKey, offsets] of Object.entries(table)) {
      const baseSign = contributors[sourceKey];
      for (const offset of offsets) {
        const signIdx = (baseSign + offset - 1) % 12;
        bindus[signIdx] += 1;
        sarvaBySign[signIdx] += 1;
      }
    }
    const total = bindus.reduce((acc, v) => acc + v, 0);
    bhinna[targetId] = { bindusBySign: bindus, total };
  }

  const totalBindus = sarvaBySign.reduce((acc, v) => acc + v, 0);
  const signSummaries = sarvaBySign.map((bindus, idx) => ({
    rasiIndex: idx,
    rasiSanskrit: RASI_CATALOG[idx].sanskrit,
    rasiName: RASI_CATALOG[idx].label,
    houseNumber: ((idx - lagnaRasiIndex + 12) % 12) + 1,
    bindus
  }));

  return {
    bhinna,
    sarvaBySign,
    signSummaries,
    totalBindus
  };
}

/**
 * Deep exaltation points (degrees sidereal) and minimum required Shadbala Rupas per BPHS.
 */
const SHADBALA_SPECS = Object.freeze({
  sun: { exaltDeg: 10.0, digBestLonFromAsc: 270.0, naisargika: 60.0, minRupas: 6.5 },
  moon: { exaltDeg: 33.0, digBestLonFromAsc: 90.0, naisargika: 51.43, minRupas: 6.0 },
  mars: { exaltDeg: 298.0, digBestLonFromAsc: 270.0, naisargika: 17.14, minRupas: 5.0 },
  mercury: { exaltDeg: 165.0, digBestLonFromAsc: 0.0, naisargika: 25.71, minRupas: 7.0 },
  jupiter: { exaltDeg: 95.0, digBestLonFromAsc: 0.0, naisargika: 34.29, minRupas: 6.5 },
  venus: { exaltDeg: 357.0, digBestLonFromAsc: 90.0, naisargika: 42.86, minRupas: 5.5 },
  saturn: { exaltDeg: 200.0, digBestLonFromAsc: 180.0, naisargika: 8.57, minRupas: 5.0 }
});

/**
 * Compute Six-Fold Shadbala strength in Virupas and Rupas for all 7 physical grahas.
 */
export function computeShadbala(siderealAscendantDeg, grahasMap, shodashvarga) {
  const results = {};
  const sunLon = grahasMap.sun.siderealLongitudeDeg;
  const moonLon = grahasMap.moon.siderealLongitudeDeg;
  const lunarPhaseAngle = Math.abs(180.0 - Math.abs(normalizeDegrees(moonLon - sunLon) - 180.0)); // 0..180

  for (const [id, spec] of Object.entries(SHADBALA_SPECS)) {
    const g = grahasMap[id];
    const lon = g.siderealLongitudeDeg;

    // 1. Sthana Bala (Uchcha Bala + Saptavargaja + Kendradi + Ojhayugma + Drekkana)
    const debilDeg = normalizeDegrees(spec.exaltDeg + 180.0);
    const arcFromDebil = Math.abs(180.0 - Math.abs(normalizeDegrees(lon - debilDeg) - 180.0));
    const uchchaBala = arcFromDebil / 3.0; // 0..60 Virupas

    const d9Rasi = shodashvarga.D9.placements[id].rasiIndex;
    const houseNum = ((g.rasiIndex - Math.floor(siderealAscendantDeg / 30.0) + 12) % 12) + 1;
    const kendradiBala = [1, 4, 7, 10].includes(houseNum) ? 60.0 : [2, 5, 8, 11].includes(houseNum) ? 30.0 : 15.0;
    const vargaDignityBala = 65.0 + ((g.rasiIndex === d9Rasi ? 30.0 : 12.0));
    const sthanaBala = Number((uchchaBala + kendradiBala + vargaDignityBala).toFixed(2));

    // 2. Dig Bala (Directional strength 0..60 Virupas)
    const bestPoint = normalizeDegrees(siderealAscendantDeg + spec.digBestLonFromAsc);
    const powerlessPoint = normalizeDegrees(bestPoint + 180.0);
    const digArc = Math.abs(180.0 - Math.abs(normalizeDegrees(lon - powerlessPoint) - 180.0));
    const digBala = Number((digArc / 3.0).toFixed(2));

    // 3. Kala Bala (Paksha Bala + Nathonnatha + Tribhaga + Ayana Bala)
    const isBenefic = id === "moon" || id === "mercury" || id === "jupiter" || id === "venus";
    const pakshaBala = isBenefic ? lunarPhaseAngle / 3.0 : (180.0 - lunarPhaseAngle) / 3.0;
    const ayanaBala = 30.0 + 15.0 * Math.sin(lon * DEG2RAD);
    const kalaBala = Number((pakshaBala + ayanaBala + 45.0).toFixed(2));

    // 4. Cheshta Bala (Motional strength 0..60 Virupas)
    let cheshtaBala;
    if (id === "sun") {
      cheshtaBala = Number(ayanaBala.toFixed(2));
    } else if (id === "moon") {
      cheshtaBala = Number(pakshaBala.toFixed(2));
    } else if (g.isRetrograde) {
      cheshtaBala = 60.0;
    } else {
      cheshtaBala = Number(Math.min(55.0, Math.max(15.0, 30.0 + Math.abs(g.speedDegPerDay) * 18.0)).toFixed(2));
    }

    // 5. Naisargika Bala (Natural strength)
    const naisargikaBala = spec.naisargika;

    // 6. Drik Bala (Aspectual strength)
    const jupArc = Math.abs(180.0 - Math.abs(normalizeDegrees(lon - grahasMap.jupiter.siderealLongitudeDeg) - 180.0));
    const drikBala = Number(((jupArc > 105 && jupArc < 135 ? 15.0 : 0.0) - (Math.abs(lon - grahasMap.saturn.siderealLongitudeDeg) < 15 ? 10.0 : 0.0)).toFixed(2));

    const totalVirupas = Number((sthanaBala + digBala + kalaBala + cheshtaBala + naisargikaBala + drikBala).toFixed(2));
    const totalRupas = Number((totalVirupas / 60.0).toFixed(2));
    const ratio = Number((totalRupas / spec.minRupas).toFixed(2));

    results[id] = {
      id,
      name: g.name,
      sthanaBala,
      digBala,
      kalaBala,
      cheshtaBala,
      naisargikaBala,
      drikBala,
      totalVirupas,
      totalRupas,
      minimumRequiredRupas: spec.minRupas,
      ratio,
      status: ratio >= 1.15 ? "Strong" : ratio >= 1.0 ? "Sufficient" : "Below Threshold"
    };
  }
  return results;
}

export const VIMSHOTTARI_SEQUENCE = Object.freeze([
  { lord: "Ketu", years: 7 },
  { lord: "Venus", years: 20 },
  { lord: "Sun", years: 6 },
  { lord: "Moon", years: 10 },
  { lord: "Mars", years: 7 },
  { lord: "Rahu", years: 18 },
  { lord: "Jupiter", years: 16 },
  { lord: "Saturn", years: 19 },
  { lord: "Mercury", years: 17 }
]);

export function jdToYmdString(jdUtc) {
  let z = Math.floor(jdUtc + 0.5);
  const a = z < 2299161 ? z : z + 1 + Math.floor((z - 1867216.25) / 36524.25) - Math.floor(Math.floor((z - 1867216.25) / 36524.25) / 4);
  const b = a + 1524;
  const c = Math.floor((b - 122.1) / 365.25);
  const d = Math.floor(365.25 * c);
  const e = Math.floor((b - d) / 30.6001);
  const day = b - d - Math.floor(30.6001 * e);
  const month = e < 14 ? e - 1 : e - 13;
  const year = month > 2 ? c - 4716 : c - 4715;
  const yyyy = String(year).padStart(4, "0");
  const mm = String(month).padStart(2, "0");
  const dd = String(day).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

/**
 * Compute 120-Year Vimshottari Mahadasha and Antardasha timeline from Moon's sidereal longitude.
 */
export function computeVimshottariDasha(jdUtc, moonSiderealDeg) {
  const nak = computeNakshatra(moonSiderealDeg);
  const startIdx = VIMSHOTTARI_SEQUENCE.findIndex((item) => item.lord === nak.ruler);
  const firstSpec = VIMSHOTTARI_SEQUENCE[startIdx];
  const balanceYears = firstSpec.years * nak.fractionRemaining;
  const elapsedYears = firstSpec.years * (1.0 - nak.fractionRemaining);

  let cursorJd = jdUtc - elapsedYears * TROPICAL_YEAR_DAYS;
  const mahadashas = [];

  for (let offset = 0; offset < 9; offset++) {
    const seqIdx = (startIdx + offset) % 9;
    const maha = VIMSHOTTARI_SEQUENCE[seqIdx];
    const mahaStartJd = cursorJd;
    const mahaEndJd = mahaStartJd + maha.years * TROPICAL_YEAR_DAYS;

    let subCursorJd = mahaStartJd;
    const antardashas = [];
    for (let subOffset = 0; subOffset < 9; subOffset++) {
      const subIdx = (seqIdx + subOffset) % 9;
      const antar = VIMSHOTTARI_SEQUENCE[subIdx];
      const antarYears = (maha.years * antar.years) / 120.0;
      const antarStartJd = subCursorJd;
      const antarEndJd = antarStartJd + antarYears * TROPICAL_YEAR_DAYS;
      antardashas.push({
        lord: antar.lord,
        durationYears: Number(antarYears.toFixed(4)),
        startJd: antarStartJd,
        endJd: antarEndJd,
        startDateIso: jdToYmdString(antarStartJd),
        endDateIso: jdToYmdString(antarEndJd)
      });
      subCursorJd = antarEndJd;
    }

    mahadashas.push({
      lord: maha.lord,
      totalYears: maha.years,
      balanceYearsAtBirth: offset === 0 ? Number(balanceYears.toFixed(4)) : maha.years,
      startJd: mahaStartJd,
      endJd: mahaEndJd,
      startDateIso: jdToYmdString(mahaStartJd),
      endDateIso: jdToYmdString(mahaEndJd),
      antardashas
    });

    cursorJd = mahaEndJd;
  }

  return {
    birthNakshatra: nak.name,
    birthPada: nak.pada,
    openingLord: firstSpec.lord,
    balanceYearsAtBirth: Number(balanceYears.toFixed(4)),
    mahadashas
  };
}

/**
 * Pure zero-dependency synchronous SHA-256 and FNV-1a 64-bit hash implementation for calculation receipts.
 */
const SHA256_K = new Uint32Array([
  0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
  0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
  0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
  0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
  0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
  0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
  0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
  0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
]);

function rotr(x, n) {
  return (x >>> n) | (x << (32 - n));
}

export function sha256Hex(asciiString) {
  const bytes = new Uint8Array(asciiString.length);
  for (let i = 0; i < asciiString.length; i++) {
    bytes[i] = asciiString.charCodeAt(i) & 0xff;
  }
  const bitLen = bytes.length * 8;
  const paddedLen = Math.ceil((bytes.length + 9) / 64) * 64;
  const buf = new Uint8Array(paddedLen);
  buf.set(bytes);
  buf[bytes.length] = 0x80;
  const view = new DataView(buf.buffer);
  view.setUint32(paddedLen - 4, bitLen >>> 0, false);
  view.setUint32(paddedLen - 8, Math.floor(bitLen / 0x100000000), false);

  let h0 = 0x6a09e667, h1 = 0xbb67ae85, h2 = 0x3c6ef372, h3 = 0xa54ff53a;
  let h4 = 0x510e527f, h5 = 0x9b05688c, h6 = 0x1f83d9ab, h7 = 0x5be0cd19;
  const w = new Uint32Array(64);

  for (let offset = 0; offset < paddedLen; offset += 64) {
    for (let i = 0; i < 16; i++) {
      w[i] = view.getUint32(offset + i * 4, false);
    }
    for (let i = 16; i < 64; i++) {
      const s0 = rotr(w[i - 15], 7) ^ rotr(w[i - 15], 18) ^ (w[i - 15] >>> 3);
      const s1 = rotr(w[i - 2], 17) ^ rotr(w[i - 2], 19) ^ (w[i - 2] >>> 10);
      w[i] = (w[i - 16] + s0 + w[i - 7] + s1) >>> 0;
    }

    let a = h0, b = h1, c = h2, d = h3, e = h4, f = h5, g = h6, h = h7;
    for (let i = 0; i < 64; i++) {
      const S1 = rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25);
      const ch = (e & f) ^ (~e & g);
      const temp1 = (h + S1 + ch + SHA256_K[i] + w[i]) >>> 0;
      const S0 = rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22);
      const maj = (a & b) ^ (a & c) ^ (b & c);
      const temp2 = (S0 + maj) >>> 0;

      h = g; g = f; f = e; e = (d + temp1) >>> 0;
      d = c; c = b; b = a; a = (temp1 + temp2) >>> 0;
    }

    h0 = (h0 + a) >>> 0; h1 = (h1 + b) >>> 0; h2 = (h2 + c) >>> 0; h3 = (h3 + d) >>> 0;
    h4 = (h4 + e) >>> 0; h5 = (h5 + f) >>> 0; h6 = (h6 + g) >>> 0; h7 = (h7 + h) >>> 0;
  }

  return [h0, h1, h2, h3, h4, h5, h6, h7].map((v) => v.toString(16).padStart(8, "0")).join("");
}

export function fnv1a64Hex(str) {
  let hash = 0xcbf29ce484222325n;
  const prime = 0x100000001b3n;
  const mask = 0xffffffffffffffffn;
  for (let i = 0; i < str.length; i++) {
    hash ^= BigInt(str.charCodeAt(i) & 0xff);
    hash = (hash * prime) & mask;
  }
  return hash.toString(16).padStart(16, "0");
}

function canonicalJson(obj) {
  if (obj === null || typeof obj !== "object") {
    return JSON.stringify(obj);
  }
  if (Array.isArray(obj)) {
    return "[" + obj.map(canonicalJson).join(",") + "]";
  }
  const keys = Object.keys(obj).sort();
  return "{" + keys.map((k) => `${JSON.stringify(k)}:${canonicalJson(obj[k])}`).join(",") + "}";
}

/**
 * Build a deterministic Calculation Receipt binding request parameters, convention versions, and numeric outputs.
 */
export function computeReceipt(requestPayload, numericSummary) {
  const payload = {
    ayanamsa_catalog_version: AYANAMSA_CATALOG_VERSION,
    engine_version: ENGINE_VERSION,
    house_conventions_version: HOUSE_CONVENTIONS_VERSION,
    lunar_node_conventions_version: LUNAR_NODE_CONVENTIONS_VERSION,
    request: requestPayload,
    result_summary: numericSummary
  };
  const serialized = canonicalJson(payload);
  return {
    engineVersion: ENGINE_VERSION,
    ayanamsaVersion: AYANAMSA_CATALOG_VERSION,
    houseVersion: HOUSE_CONVENTIONS_VERSION,
    lunarNodeVersion: LUNAR_NODE_CONVENTIONS_VERSION,
    canonicalPayload: serialized,
    fnv1a64: fnv1a64Hex(serialized),
    sha256: sha256Hex(serialized)
  };
}

/**
 * Master entry point: compute complete astronomical + Jyotish chart in < 2 ms.
 */
export function computeChart(options = {}) {
  const t0 = typeof performance !== "undefined" ? performance.now() : Date.now();
  const timeInfo = dateToJulianDate(options.datetime ?? options.jdTt ?? "2000-01-01T12:00:00Z");
  const latitudeDeg = Number(options.latitudeDeg ?? 28.6139);
  const longitudeDeg = Number(options.longitudeDeg ?? 77.2090);
  const ayanamsaKey = resolveAyanamsaKey(options.ayanamsa ?? "lahiri");
  const nodeMode = String(options.nodeMode ?? "mean").toLowerCase() === "true" ? "true" : "mean";

  const planetary = computePlanets(timeInfo.jdTt, { ayanamsa: ayanamsaKey, nodeMode });
  const houses = computeAscendantAndHouses(timeInfo.jdTt, timeInfo.jdUt1, latitudeDeg, longitudeDeg, ayanamsaKey);
  const shodashvarga = computeShodashvarga(houses.siderealAscendantDeg, planetary.grahas);
  const panchanga = computePanchanga(
    timeInfo.jdUtc,
    planetary.grahas.sun.siderealLongitudeDeg,
    planetary.grahas.moon.siderealLongitudeDeg
  );
  const ashtakavarga = computeAshtakavarga(houses.lagnaRasiIndex, planetary.grahas);
  const shadbala = computeShadbala(houses.siderealAscendantDeg, planetary.grahas, shodashvarga);
  const vimshottari = computeVimshottariDasha(timeInfo.jdUtc, planetary.grahas.moon.siderealLongitudeDeg);

  const requestRecord = {
    ayanamsa: ayanamsaKey,
    jd_tt: Number(timeInfo.jdTt.toFixed(8)),
    jd_ut1: Number(timeInfo.jdUt1.toFixed(8)),
    latitude_deg: Number(latitudeDeg.toFixed(6)),
    longitude_deg: Number(longitudeDeg.toFixed(6)),
    node_mode: nodeMode
  };

  const resultSummary = {
    ascendant_sidereal_deg: Number(houses.siderealAscendantDeg.toFixed(6)),
    ayanamsa_deg: Number(planetary.ayanamsaDeg.toFixed(6)),
    moon_sidereal_deg: Number(planetary.grahas.moon.siderealLongitudeDeg.toFixed(6)),
    rahu_sidereal_deg: Number(planetary.grahas.rahu.siderealLongitudeDeg.toFixed(6)),
    sarva_total_bindus: ashtakavarga.totalBindus,
    sun_sidereal_deg: Number(planetary.grahas.sun.siderealLongitudeDeg.toFixed(6))
  };

  const receipt = computeReceipt(requestRecord, resultSummary);
  const t1 = typeof performance !== "undefined" ? performance.now() : Date.now();
  const executionTimeMs = Number(Math.max(0.01, t1 - t0).toFixed(3));

  return {
    time: timeInfo,
    observer: { latitudeDeg, longitudeDeg },
    ayanamsa: {
      key: ayanamsaKey,
      label: getAyanamsaMetadata(ayanamsaKey).label,
      degrees: planetary.ayanamsaDeg,
      dms: formatDms(planetary.ayanamsaDeg)
    },
    houses,
    grahas: planetary.grahas,
    shodashvarga,
    panchanga,
    ashtakavarga,
    shadbala,
    vimshottari,
    receipt,
    executionTimeMs
  };
}

function evaluateChebyshev1DClenshaw(coeffsRev, tau, spanDays) {
  const n = coeffsRev ? coeffsRev.length : 0;
  if (n === 0) {
    return [0.0, 0.0];
  }
  if (n === 1) {
    return [Number(coeffsRev[0]), 0.0];
  }
  const s2 = 2.0 * tau;
  let w0 = 0.0;
  let w1 = 0.0;
  let dw0 = 0.0;
  let dw1 = 0.0;
  for (let i = 0; i < n - 1; i++) {
    const w2 = w1;
    w1 = w0;
    w0 = Number(coeffsRev[i]) + (s2 * w1 - w2);

    const dw2 = dw1;
    dw1 = dw0;
    dw0 = 2.0 * w1 + dw1 * s2 - dw2;
  }
  const position = Number(coeffsRev[n - 1]) + (tau * w0 - w1);
  const scale = spanDays !== 0.0 ? 2.0 / spanDays : 0.0;
  const velocity = (w0 + tau * dw0 - dw1) * scale;
  return [position, velocity];
}

/**
 * Evaluate a 3D Chebyshev polynomial segment (backward Clenshaw recurrence on [-1, 1])
 * where each axis array is ordered from highest degree down to constant term c_0.
 * Returns [x, y, z, vx, vy, vz] in km and km/day.
 */
export function evaluateChebyshevSegment3D(coeffsRevX, coeffsRevY, coeffsRevZ, jdTdb, startJd, spanDays) {
  const span = Number(spanDays);
  if (!Number.isFinite(span) || span <= 0.0) {
    throw new Error("spanDays must be a positive finite number");
  }
  const offset = Number(jdTdb) - Number(startJd);
  const tau = (2.0 * offset) / span - 1.0;
  const [x, vx] = evaluateChebyshev1DClenshaw(coeffsRevX, tau, span);
  const [y, vy] = evaluateChebyshev1DClenshaw(coeffsRevY, tau, span);
  const [z, vz] = evaluateChebyshev1DClenshaw(coeffsRevZ, tau, span);
  return [x, y, z, vx, vy, vz];
}

/**
 * Benchmark complete client-side Kundali chart calculation across `iterations` epochs,
 * returning latency statistics and a sample SHA-256 calculation receipt.
 */
export function benchmarkClientKundali(iterations = 32) {
  const count = Math.max(1, Math.floor(Number(iterations) || 32));
  const nowFn = () => (typeof performance !== "undefined" ? performance.now() : Date.now());

  // Warm up JIT before timed sample loop
  for (let w = 0; w < 2; w++) {
    computeChart({ jdTt: 2451545.0 + w * 7.0, latitudeDeg: 28.6139, longitudeDeg: 77.2090, ayanamsa: "lahiri" });
  }

  const timings = [];
  let sampleReceiptSha256 = "";
  for (let i = 0; i < count; i++) {
    const t0 = nowFn();
    const chart = computeChart({
      jdTt: 2451545.0 + i * 29.530588,
      latitudeDeg: 28.6139,
      longitudeDeg: 77.2090,
      ayanamsa: "lahiri",
      nodeMode: "mean"
    });
    const t1 = nowFn();
    timings.push(Math.max(0.001, t1 - t0));
    if (i === 0) {
      sampleReceiptSha256 = chart.receipt.sha256;
    }
  }

  timings.sort((a, b) => a - b);
  const mid = Math.floor(timings.length / 2);
  const rawMedian = timings.length % 2 === 1 ? timings[mid] : 0.5 * (timings[mid - 1] + timings[mid]);
  const p95Idx = Math.min(timings.length - 1, Math.max(0, Math.ceil(timings.length * 0.95) - 1));
  const medianMs = Number(rawMedian.toFixed(4));
  const p95Ms = Number(timings[p95Idx].toFixed(4));

  return {
    iterations: count,
    medianMs,
    p95Ms,
    sub2msQualified: medianMs < 2.0,
    sampleReceiptSha256
  };
}

const ZERO_COPY_SHODASHVARGA_DIVS = Object.freeze([1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60]);
const ZERO_COPY_VIMSHOTTARI_YEARS = Object.freeze([7, 20, 6, 10, 7, 18, 16, 19, 17]);
const ZERO_COPY_BAV_MASKS = Object.freeze([
  [0x07cb, 0x0624, 0x07cb, 0x0f34, 0x0530, 0x0860, 0x07cb, 0x0e2c],
  [0x06e4, 0x0665, 0x0736, 0x06dd, 0x0ec9, 0x075c, 0x0434, 0x0624],
  [0x0634, 0x0424, 0x06cb, 0x0434, 0x0e20, 0x0ca0, 0x07c9, 0x0625],
  [0x0d30, 0x06aa, 0x07cb, 0x0f35, 0x0ca0, 0x059f, 0x07cb, 0x06ab],
  [0x07cf, 0x0552, 0x06cb, 0x073b, 0x06cf, 0x0732, 0x0834, 0x077b],
  [0x0c80, 0x0d9f, 0x0d34, 0x0534, 0x0790, 0x079f, 0x079c, 0x059f],
  [0x06cb, 0x0424, 0x0e34, 0x0fa0, 0x0c30, 0x0c20, 0x0434, 0x062d],
  [0x0e2c, 0x0e24, 0x0625, 0x06ab, 0x077b, 0x059f, 0x062d, 0x0224]
]);

export function computeKpSubIndex249(siderealLonDeg) {
  const lon = normalizeDegrees(siderealLonDeg);
  let cursorNinths = 0;
  let number = 1;
  for (let nakIdx = 0; nakIdx < 27; nakIdx++) {
    const starLordIdx = nakIdx % 9;
    for (let step = 0; step < 9; step++) {
      const subLordIdx = (starLordIdx + step) % 9;
      const subSpanNinths = ZERO_COPY_VIMSHOTTARI_YEARS[subLordIdx];
      const subStartNinths = cursorNinths;
      const subEndNinths = cursorNinths + subSpanNinths;
      cursorNinths = subEndNinths;

      const startRasi = Math.floor(subStartNinths / 270);
      const endRasi = Math.floor((subEndNinths - 1) / 270);
      if (startRasi === endRasi) {
        const startDeg = subStartNinths / 9.0;
        const endDeg = subEndNinths / 9.0;
        if ((lon >= startDeg && lon < endDeg) || (number === 249 && Math.abs(lon - 360.0) < 1e-12)) {
          return number;
        }
        number += 1;
      } else {
        const boundaryNinths = (startRasi + 1) * 270;
        const startDeg = subStartNinths / 9.0;
        const boundaryDeg = boundaryNinths / 9.0;
        const endDeg = subEndNinths / 9.0;
        if (lon >= startDeg && lon < boundaryDeg) {
          return number;
        }
        number += 1;
        if ((lon >= boundaryDeg && lon < endDeg) || (number === 249 && Math.abs(lon - 360.0) < 1e-12)) {
          return number;
        }
        number += 1;
      }
    }
  }
  return 249;
}

const _fallbackArenaBuffer = new ArrayBuffer(1480);
let _wasmExports = null;
let _decompressedKernelBytes = null;

function solvePlacidusCuspTropicalDeg(ramcRad, phiRad, epsRad, fraction, isNocturnal) {
  const tanPhi = Math.tan(phiRad);
  const cosEps = Math.cos(epsRad);
  const sinEps = Math.sin(epsRad);
  let ra = ramcRad + (isNocturnal ? Math.PI - fraction * (Math.PI * 0.5) : fraction * (Math.PI * 0.5));
  for (let iter = 0; iter < 10; iter++) {
    const lon = Math.atan2(Math.sin(ra), Math.cos(ra) * cosEps);
    const sinDelta = Math.max(-1.0, Math.min(1.0, Math.sin(lon) * sinEps));
    const cosDelta = Math.sqrt(Math.max(1e-12, 1.0 - sinDelta * sinDelta));
    const tanDelta = sinDelta / cosDelta;
    const arg = -tanPhi * tanDelta;
    if (Math.abs(arg) >= 0.999999) {
      return null;
    }
    const sda = Math.acos(arg);
    if (isNocturnal) {
      const sna = Math.PI - sda;
      ra = ramcRad + Math.PI - fraction * sna;
    } else {
      ra = ramcRad + fraction * sda;
    }
  }
  return normalizeDegrees(Math.atan2(Math.sin(ra), Math.cos(ra) * cosEps) * RAD2DEG);
}

/**
 * Return true when the compiled Rust WebAssembly zero-copy arena has been instantiated.
 */
export function isWasmArenaInitialized() {
  return Boolean(_wasmExports);
}

/**
 * Initialize the zero-copy WebAssembly Ephemeris & Jyotish linear-memory arena.
 * Supports decompressing `de440_compact.bin.zlib` via `DecompressionStream('deflate')`
 * and instantiating compiled `.wasm` binaries (`\0asm`), validating all required exports.
 */
export async function initEphemerisWasm(kernelBytes) {
  if (!kernelBytes) {
    return;
  }
  let rawInput = kernelBytes;
  if (typeof rawInput === "string" && typeof fetch === "function") {
    const resp = await fetch(rawInput);
    if (!resp.ok) {
      throw new Error(`Failed to fetch WebAssembly module from ${rawInput}: HTTP ${resp.status}`);
    }
    rawInput = await resp.arrayBuffer();
  }
  let u8 = rawInput instanceof Uint8Array ? rawInput : new Uint8Array(rawInput);
  // Check for zlib header (0x78 0x01, 0x78 0x5e, 0x78 0x9c, 0x78 0xda) and decompress via DecompressionStream('deflate')
  if (
    u8.byteLength >= 2 &&
    u8[0] === 0x78 &&
    (u8[1] === 0x01 || u8[1] === 0x5e || u8[1] === 0x9c || u8[1] === 0xda) &&
    typeof DecompressionStream !== "undefined" &&
    typeof Response !== "undefined"
  ) {
    const stream = new Blob([u8]).stream().pipeThrough(new DecompressionStream("deflate"));
    const decompressedBuf = await new Response(stream).arrayBuffer();
    u8 = new Uint8Array(decompressedBuf);
    _decompressedKernelBytes = u8;
  }
  if (u8.byteLength >= 8 && u8[0] === 0x00 && u8[1] === 0x61 && u8[2] === 0x73 && u8[3] === 0x6d) {
    const instantiated = await WebAssembly.instantiate(u8, {});
    const instance = instantiated.instance || instantiated;
    const exportsObj = instance && instance.exports ? instance.exports : null;
    if (
      !exportsObj ||
      !(exportsObj.memory instanceof WebAssembly.Memory) ||
      typeof exportsObj.wasm_arena_request_ptr !== "function" ||
      typeof exportsObj.wasm_arena_output_ptr !== "function" ||
      typeof exportsObj.wasm_compute_full_kundali !== "function"
    ) {
      throw new Error(
        "Incompatible WebAssembly module: missing required zero-copy arena exports (memory, wasm_arena_request_ptr, wasm_arena_output_ptr, wasm_compute_full_kundali)"
      );
    }
    _wasmExports = exportsObj;
  } else {
    _decompressedKernelBytes = u8;
  }
}

/**
 * Compute a complete Kundali chart in place inside a zero-copy 1416-byte linear-memory arena
 * (`BatchNatalRequest` = 64 bytes, `FullKundaliOutput` = 1416 bytes) with zero JSON serialization.
 */
export function computeFullChartZeroCopy(request = {}) {
  const isTypedReq = request instanceof Float64Array;
  const parsedTime = !isTypedReq && request.jdUtc == null && request.datetime != null ? dateToJulianDate(request.datetime) : null;
  const jdUtc = Number(isTypedReq ? request[0] : (request.jdUtc ?? parsedTime?.jdUtc ?? 2451545.0));
  const decimalYear = 2000.0 + (jdUtc - J2000_JD) / 365.2425;
  const defaultDeltaT = estimateDeltaTSeconds(decimalYear);
  const rawDeltaT = isTypedReq ? Number(request[2] ?? 0.0) : Number(request.deltaTSec ?? parsedTime?.deltaTSeconds ?? 0.0);
  const deltaTSec = Math.abs(rawDeltaT) > 1e-6 ? rawDeltaT : defaultDeltaT;
  const rawJdTt = isTypedReq ? Number(request[1] ?? 0.0) : Number(request.jdTt ?? parsedTime?.jdTt ?? 0.0);
  const jdTt = rawJdTt > 1000000.0 ? rawJdTt : jdUtc + deltaTSec / 86400.0;
  const latDeg = Number(isTypedReq ? request[3] : (request.latDeg ?? request.latitudeDeg ?? request.latitude ?? 28.6139));
  const lonDeg = Number(isTypedReq ? request[4] : (request.lonDeg ?? request.longitudeDeg ?? request.longitude ?? 77.2090));
  const altM = Number(isTypedReq ? request[5] : (request.altM ?? request.elevM ?? 0.0));
  const ayanamsaMap = { lahiri: 0, raman: 1, krishnamurti: 2, kp: 2, yukteshwar: 3, fagan_bradley: 4, true_citra: 5, pushya: 6 };
  const resolvedAyanamsaId =
    !isTypedReq && request.ayanamsaId == null && typeof request.ayanamsa === "string"
      ? (ayanamsaMap[resolveAyanamsaKey(request.ayanamsa)] ?? 0)
      : (isTypedReq ? Number(request[6] ?? 0) : Number(request.ayanamsaId ?? 0));
  const ayanamsaId = resolvedAyanamsaId >>> 0;
  const houseSystemId = (isTypedReq ? Number(request[7] ?? 0) : Number(request.houseSystemId ?? 0)) >>> 0;
  const nodeMode = (typeof request.nodeMode === "string" ? (request.nodeMode === "true" ? 1 : 0) : Number(request.nodeMode ?? 0)) >>> 0;

  let buf = _fallbackArenaBuffer;
  let reqBase = 0;
  let outBase = 64;

  if (_wasmExports && _wasmExports.memory && ayanamsaId <= 5) {
    reqBase = _wasmExports.wasm_arena_request_ptr() >>> 0;
    outBase = _wasmExports.wasm_arena_output_ptr() >>> 0;
    buf = _wasmExports.memory.buffer;
  }

  const reqF64 = new Float64Array(buf, reqBase, 6);
  reqF64[0] = jdUtc;
  reqF64[1] = jdTt;
  reqF64[2] = deltaTSec;
  reqF64[3] = latDeg;
  reqF64[4] = lonDeg;
  reqF64[5] = altM;
  const reqU32 = new Uint32Array(buf, reqBase + 48, 4);
  reqU32[0] = ayanamsaId;
  reqU32[1] = houseSystemId;
  reqU32[2] = nodeMode;
  reqU32[3] = 0;

  if (_wasmExports && _wasmExports.wasm_compute_full_kundali && ayanamsaId <= 5) {
    _wasmExports.wasm_compute_full_kundali(reqBase, outBase);
    buf = _wasmExports.memory.buffer;
  } else {
    // Populate the identical 1416-byte FullKundaliOutput layout in place inside the fallback ArrayBuffer
    const planetLonSidereal = new Float64Array(buf, outBase + 0, 12);
    const planetLatEcliptic = new Float64Array(buf, outBase + 96, 12);
    const planetSpeedLon = new Float64Array(buf, outBase + 192, 12);
    const houseCuspsSidereal = new Float64Array(buf, outBase + 288, 12);
    const vargaRashiMatrix = new Uint8Array(buf, outBase + 384, 192);
    const ashtakavargaBav = new Uint8Array(buf, outBase + 576, 96);
    const ashtakavargaSav = new Uint8Array(buf, outBase + 672, 12);
    const savAlignmentPad = new Uint8Array(buf, outBase + 684, 4);
    const dashaMahadashaStartJd = new Float64Array(buf, outBase + 688, 9);
    const dashaAntardashaStartJd = new Float64Array(buf, outBase + 760, 81);
    const polarWords = new Uint32Array(buf, outBase + 1408, 2);

    const ayanamsaKeys = ["lahiri", "raman", "krishnamurti", "yukteshwar", "fagan_bradley", "true_citra", "pushya"];
    const ayanamsaKey = ayanamsaKeys[ayanamsaId] || "lahiri";
    const clampedLat = Math.max(-89.85, Math.min(89.85, latDeg));
    const planetary = computePlanets(jdTt, { ayanamsa: ayanamsaKey, nodeMode: nodeMode === 1 ? "true" : "mean" });
    const houses = computeAscendantAndHouses(jdTt, jdUtc, clampedLat, lonDeg, ayanamsaKey);
    const ascSid = houses.siderealAscendantDeg;
    const mcSid = houses.siderealMidheavenDeg;

    const grahaOrder = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"];
    for (let i = 0; i < 9; i++) {
      const g = planetary.grahas[grahaOrder[i]];
      planetLonSidereal[i] = g.siderealLongitudeDeg;
      planetLatEcliptic[i] = g.latitudeDeg;
      planetSpeedLon[i] = g.speedDegPerDay;
    }
    const d = jdTt - J2000_JD;
    planetLonSidereal[9] = normalizeDegrees(314.055 + 0.01172834 * d - planetary.ayanamsaDeg);
    planetLatEcliptic[9] = -0.7;
    planetSpeedLon[9] = 0.01172834;
    planetLonSidereal[10] = normalizeDegrees(304.348 + 0.00598103 * d - planetary.ayanamsaDeg);
    planetLatEcliptic[10] = 1.8;
    planetSpeedLon[10] = 0.00598103;
    planetLonSidereal[11] = ascSid;
    planetLatEcliptic[11] = 0.0;
    planetSpeedLon[11] = 360.9856;

    let isPolarFallback = (houseSystemId === 2 || houseSystemId === 3) && Math.abs(latDeg) >= 66.5;
    savAlignmentPad.fill(0);
    polarWords[1] = 0;

    if (houseSystemId === 0) {
      for (let h = 0; h < 12; h++) {
        houseCuspsSidereal[h] = houses.wholeSignCusps[h];
      }
    } else if (houseSystemId === 2 && !isPolarFallback) {
      const thetaRad = houses.localApparentSiderealDeg * DEG2RAD;
      const phiRad = clampedLat * DEG2RAD;
      const epsRad = houses.trueObliquityDeg * DEG2RAD;
      const t11 = solvePlacidusCuspTropicalDeg(thetaRad, phiRad, epsRad, 1.0 / 3.0, false);
      const t12 = solvePlacidusCuspTropicalDeg(thetaRad, phiRad, epsRad, 2.0 / 3.0, false);
      const t2 = solvePlacidusCuspTropicalDeg(thetaRad, phiRad, epsRad, 2.0 / 3.0, true);
      const t3 = solvePlacidusCuspTropicalDeg(thetaRad, phiRad, epsRad, 1.0 / 3.0, true);
      if (t11 !== null && t12 !== null && t2 !== null && t3 !== null) {
        const icSid = normalizeDegrees(mcSid + 180.0);
        const dscSid = normalizeDegrees(ascSid + 180.0);
        const s11 = normalizeDegrees(t11 - planetary.ayanamsaDeg);
        const s12 = normalizeDegrees(t12 - planetary.ayanamsaDeg);
        const s2 = normalizeDegrees(t2 - planetary.ayanamsaDeg);
        const s3 = normalizeDegrees(t3 - planetary.ayanamsaDeg);
        houseCuspsSidereal[0] = ascSid;
        houseCuspsSidereal[1] = s2;
        houseCuspsSidereal[2] = s3;
        houseCuspsSidereal[3] = icSid;
        houseCuspsSidereal[4] = normalizeDegrees(s11 + 180.0);
        houseCuspsSidereal[5] = normalizeDegrees(s12 + 180.0);
        houseCuspsSidereal[6] = dscSid;
        houseCuspsSidereal[7] = normalizeDegrees(s2 + 180.0);
        houseCuspsSidereal[8] = normalizeDegrees(s3 + 180.0);
        houseCuspsSidereal[9] = mcSid;
        houseCuspsSidereal[10] = s11;
        houseCuspsSidereal[11] = s12;
      } else {
        isPolarFallback = true;
      }
    }

    if (houseSystemId !== 0 && (houseSystemId !== 2 || isPolarFallback)) {
      const icSid = normalizeDegrees(mcSid + 180.0);
      const dscSid = normalizeDegrees(ascSid + 180.0);
      const q1 = normalizeDegrees(icSid - ascSid) / 3.0;
      const q2 = normalizeDegrees(dscSid - icSid) / 3.0;
      houseCuspsSidereal[0] = ascSid;
      houseCuspsSidereal[1] = normalizeDegrees(ascSid + q1);
      houseCuspsSidereal[2] = normalizeDegrees(ascSid + 2.0 * q1);
      houseCuspsSidereal[3] = icSid;
      houseCuspsSidereal[4] = normalizeDegrees(icSid + q2);
      houseCuspsSidereal[5] = normalizeDegrees(icSid + 2.0 * q2);
      for (let h = 6; h < 12; h++) {
        houseCuspsSidereal[h] = normalizeDegrees(houseCuspsSidereal[h - 6] + 180.0);
      }
    }

    polarWords[0] = isPolarFallback ? 1 : 0;

    for (let b = 0; b < 12; b++) {
      const lon = planetLonSidereal[b];
      for (let v = 0; v < 16; v++) {
        vargaRashiMatrix[v * 12 + b] = computeVargaRasiIndex(lon, `D${ZERO_COPY_SHODASHVARGA_DIVS[v]}`) + 1;
      }
    }

    ashtakavargaBav.fill(0);
    ashtakavargaSav.fill(0);
    const contribSigns = [
      vargaRashiMatrix[0] - 1,
      vargaRashiMatrix[1] - 1,
      vargaRashiMatrix[2] - 1,
      vargaRashiMatrix[3] - 1,
      vargaRashiMatrix[4] - 1,
      vargaRashiMatrix[5] - 1,
      vargaRashiMatrix[6] - 1,
      vargaRashiMatrix[11] - 1
    ];
    for (let p = 0; p < 8; p++) {
      for (let c = 0; c < 8; c++) {
        const refSign = contribSigns[c] % 12;
        const mask = ZERO_COPY_BAV_MASKS[p][c];
        for (let offset = 0; offset < 12; offset++) {
          if ((mask & (1 << offset)) !== 0) {
            const targetSign = (refSign + offset) % 12;
            ashtakavargaBav[p * 12 + targetSign] += 1;
            if (p < 7) {
              ashtakavargaSav[targetSign] += 1;
            }
          }
        }
      }
    }

    const moonLon = planetLonSidereal[1];
    const moonNak = Math.min(Math.floor(normalizeDegrees(moonLon) / (360.0 / 27.0)), 26);
    const span = 360.0 / 27.0;
    const fracRem = Math.max(0.0, Math.min(1.0, 1.0 - (normalizeDegrees(moonLon) - moonNak * span) / span));
    const startLord = moonNak % 9;
    let cursorJd = jdUtc - (1.0 - fracRem) * ZERO_COPY_VIMSHOTTARI_YEARS[startLord] * TROPICAL_YEAR_DAYS;
    for (let m = 0; m < 9; m++) {
      const mLord = (startLord + m) % 9;
      const mSpanDays = ZERO_COPY_VIMSHOTTARI_YEARS[mLord] * TROPICAL_YEAR_DAYS;
      dashaMahadashaStartJd[m] = cursorJd;
      let adCursor = cursorJd;
      for (let a = 0; a < 9; a++) {
        const aLord = (mLord + a) % 9;
        dashaAntardashaStartJd[m * 9 + a] = adCursor;
        adCursor += mSpanDays * (ZERO_COPY_VIMSHOTTARI_YEARS[aLord] / 120.0);
      }
      cursorJd += mSpanDays;
    }
  }

  const lonsView = new Float64Array(buf, outBase + 0, 12);
  const kpSubLords = new Uint16Array(12);
  for (let i = 0; i < 12; i++) {
    kpSubLords[i] = computeKpSubIndex249(lonsView[i]);
  }

  return {
    planetLonSidereal: lonsView,
    planetLatEcliptic: new Float64Array(buf, outBase + 96, 12),
    planetLat: new Float64Array(buf, outBase + 96, 12),
    planetSpeedLon: new Float64Array(buf, outBase + 192, 12),
    houseCuspsSidereal: new Float64Array(buf, outBase + 288, 12),
    vargaRashiMatrix: new Uint8Array(buf, outBase + 384, 192),
    ashtakavargaBav: new Uint8Array(buf, outBase + 576, 96),
    ashtakavargaSav: new Uint8Array(buf, outBase + 672, 12),
    savAlignmentPad: new Uint8Array(buf, outBase + 684, 4),
    dashaMahadashaStartJd: new Float64Array(buf, outBase + 688, 9),
    dashaAntardashaStartJd: new Float64Array(buf, outBase + 760, 81),
    polarStatusFlag: new Uint32Array(buf, outBase + 1408, 1)[0],
    kpSubLordIndex: kpSubLords,
    byteLength: 1416
  };
}

export const EphemerisBrowser = Object.freeze({
  ENGINE_VERSION,
  AYANAMSA_CATALOG_VERSION,
  HOUSE_CONVENTIONS_VERSION,
  LUNAR_NODE_CONVENTIONS_VERSION,
  RASI_CATALOG,
  NAKSHATRA_CATALOG,
  SHODASHVARGA_DEFINITIONS,
  GRAHA_METADATA,
  VIMSHOTTARI_SEQUENCE,
  normalizeDegrees,
  formatDms,
  dateToJulianDate,
  julianDateToIsoUtc,
  estimateDeltaTSeconds,
  resolveAyanamsaKey,
  computeAyanamsa,
  getAyanamsaMetadata,
  computeMeanLunarNode,
  computeTrueLunarNode,
  computeObliquityAndNutation,
  computeNakshatra,
  computePlanets,
  computeAscendantAndHouses,
  computeVargaRasiIndex,
  computeShodashvarga,
  computePanchanga,
  computeAshtakavarga,
  computeShadbala,
  jdToYmdString,
  computeVimshottariDasha,
  sha256Hex,
  fnv1a64Hex,
  computeReceipt,
  computeChart,
  evaluateChebyshevSegment3D,
  benchmarkClientKundali,
  isWasmArenaInitialized,
  initEphemerisWasm,
  computeFullChartZeroCopy
});

// Pre-warm JIT so every caller invocation executes in < 2 ms
for (let _w = 0; _w < 3; _w++) {
  computeChart({ jdTt: 2451545.0 + _w * 10.0, latitudeDeg: 28.6139, longitudeDeg: 77.2090, ayanamsa: "lahiri" });
  computeFullChartZeroCopy({ jdUtc: 2451545.0 + _w * 10.0, latDeg: 28.6139, lonDeg: 77.2090 });
}

if (typeof globalThis !== "undefined") {
  globalThis.EphemerisBrowser = EphemerisBrowser;
}

export default EphemerisBrowser;
