/**
 * ephemeris-browser.d.ts
 * TypeScript declarations for the zero-dependency Browser Ephemeris & Vedic Jyotish Engine.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

export type AyanamsaConvention =
  | "lahiri"
  | "true_citra"
  | "raman"
  | "krishnamurti"
  | "kp"
  | "yukteshwar"
  | "fagan_bradley"
  | "pushya";

export type NodeMode = "mean" | "true";

export type GrahaId =
  | "sun"
  | "moon"
  | "mars"
  | "mercury"
  | "jupiter"
  | "venus"
  | "saturn"
  | "rahu"
  | "ketu";

export type PhysicalGrahaId =
  | "sun"
  | "moon"
  | "mars"
  | "mercury"
  | "jupiter"
  | "venus"
  | "saturn";

export type ShodashvargaCode =
  | "D1"
  | "D2"
  | "D3"
  | "D4"
  | "D7"
  | "D9"
  | "D10"
  | "D12"
  | "D16"
  | "D20"
  | "D24"
  | "D27"
  | "D30"
  | "D40"
  | "D45"
  | "D60";

export interface RasiMetadata {
  readonly index: number;
  readonly number: number;
  readonly sanskrit: string;
  readonly english: string;
  readonly label: string;
  readonly lord: string;
  readonly element: "Fire" | "Earth" | "Air" | "Water";
  readonly modality: "Movable" | "Fixed" | "Dual";
}

export interface NakshatraMetadata {
  readonly index: number;
  readonly number: number;
  readonly name: string;
  readonly ruler: string;
  readonly deity: string;
  readonly gana: "Deva" | "Manushya" | "Rakshasa";
  readonly nadi: "Adi" | "Madhya" | "Antya";
  readonly yoni: string;
}

export interface NakshatraPosition extends NakshatraMetadata {
  readonly pada: 1 | 2 | 3 | 4;
  readonly globalPadaNumber: number;
  readonly navamsaRasiIndex: number;
  readonly navamsaRasiName: string;
  readonly degreesInNakshatra: number;
  readonly percentElapsed: number;
  readonly fractionRemaining: number;
}

export interface ShodashvargaDefinition {
  readonly code: ShodashvargaCode;
  readonly division: number;
  readonly name: string;
  readonly domain: string;
}

export interface JulianDateInfo {
  readonly jdUtc: number;
  readonly jdUt1: number;
  readonly jdTt: number;
  readonly deltaTSeconds: number;
  readonly isoUtc: string;
}

export interface GrahaPosition {
  readonly id: GrahaId;
  readonly name: string;
  readonly sanskritName: string;
  readonly symbol: string;
  readonly tropicalLongitudeDeg: number;
  readonly siderealLongitudeDeg: number;
  readonly latitudeDeg: number;
  readonly speedDegPerDay: number;
  readonly isRetrograde: boolean;
  readonly rasiIndex: number;
  readonly rasiNumber: number;
  readonly rasiSanskrit: string;
  readonly rasiName: string;
  readonly rasiLord: string;
  readonly degreeInRasi: number;
  readonly dmsInRasi: string;
  readonly nakshatra: NakshatraPosition;
  readonly meanSiderealLongitudeDeg?: number;
  readonly trueSiderealLongitudeDeg?: number;
  readonly nodeMode?: NodeMode;
}

export interface AscendantAndHousesResult {
  readonly gmstDeg: number;
  readonly gastDeg: number;
  readonly localApparentSiderealDeg: number;
  readonly trueObliquityDeg: number;
  readonly tropicalAscendantDeg: number;
  readonly tropicalMidheavenDeg: number;
  readonly siderealAscendantDeg: number;
  readonly siderealMidheavenDeg: number;
  readonly lagnaRasiIndex: number;
  readonly lagnaRasiName: string;
  readonly lagnaDegreeInRasi: number;
  readonly lagnaDms: string;
  readonly lagnaNakshatra: NakshatraPosition;
  readonly wholeSignCusps: readonly number[];
}

export interface VargaPlacement {
  readonly id: GrahaId;
  readonly name: string;
  readonly symbol: string;
  readonly rasiIndex: number;
  readonly rasiSanskrit: string;
  readonly rasiName: string;
  readonly rasiLord: string;
  readonly houseNumber: number;
  readonly shashtiamsaDeity?: string;
}

export interface VargaSignBucket {
  readonly rasiIndex: number;
  readonly rasiName: string;
  readonly houseNumber: number;
  readonly occupants: readonly string[];
}

export interface VargaChart {
  readonly code: ShodashvargaCode;
  readonly division: number;
  readonly name: string;
  readonly domain: string;
  readonly lagnaRasiIndex: number;
  readonly lagnaRasiName: string;
  readonly placements: Readonly<Record<GrahaId, VargaPlacement>>;
  readonly signs: readonly VargaSignBucket[];
}

export interface PanchangaResult {
  readonly tithi: {
    readonly number: number;
    readonly name: string;
    readonly paksha: "Shukla Paksha" | "Krishna Paksha";
    readonly percentElapsed: number;
  };
  readonly vara: {
    readonly index: number;
    readonly sanskrit: string;
    readonly english: string;
    readonly lord: string;
  };
  readonly nakshatra: NakshatraPosition;
  readonly yoga: {
    readonly number: number;
    readonly name: string;
    readonly percentElapsed: number;
  };
  readonly karana: {
    readonly number: number;
    readonly name: string;
    readonly isFixed: boolean;
  };
}

export interface AshtakavargaResult {
  readonly bhinna: Readonly<
    Record<
      PhysicalGrahaId,
      {
        readonly bindusBySign: readonly number[];
        readonly total: number;
      }
    >
  >;
  readonly sarvaBySign: readonly number[];
  readonly signSummaries: readonly {
    readonly rasiIndex: number;
    readonly rasiSanskrit: string;
    readonly rasiName: string;
    readonly houseNumber: number;
    readonly bindus: number;
  }[];
  readonly totalBindus: 337;
}

export interface ShadbalaPlanetSummary {
  readonly id: PhysicalGrahaId;
  readonly name: string;
  readonly sthanaBala: number;
  readonly digBala: number;
  readonly kalaBala: number;
  readonly cheshtaBala: number;
  readonly naisargikaBala: number;
  readonly drikBala: number;
  readonly totalVirupas: number;
  readonly totalRupas: number;
  readonly minimumRequiredRupas: number;
  readonly ratio: number;
  readonly status: "Strong" | "Sufficient" | "Below Threshold";
}

export interface AntardashaPeriod {
  readonly lord: string;
  readonly durationYears: number;
  readonly startJd: number;
  readonly endJd: number;
  readonly startDateIso: string;
  readonly endDateIso: string;
}

export interface MahadashaPeriod {
  readonly lord: string;
  readonly totalYears: number;
  readonly balanceYearsAtBirth: number;
  readonly startJd: number;
  readonly endJd: number;
  readonly startDateIso: string;
  readonly endDateIso: string;
  readonly antardashas: readonly AntardashaPeriod[];
}

export interface VimshottariDashaResult {
  readonly birthNakshatra: string;
  readonly birthPada: 1 | 2 | 3 | 4;
  readonly openingLord: string;
  readonly balanceYearsAtBirth: number;
  readonly mahadashas: readonly MahadashaPeriod[];
}

export interface CalculationReceipt {
  readonly engineVersion: string;
  readonly ayanamsaVersion: string;
  readonly houseVersion: string;
  readonly lunarNodeVersion: string;
  readonly canonicalPayload: string;
  readonly fnv1a64: string;
  readonly sha256: string;
}

export interface ChartInputOptions {
  readonly datetime?: string | Date | { year: number; month: number; day: number; hour?: number; minute?: number; second?: number };
  readonly jdTt?: number;
  readonly latitudeDeg?: number;
  readonly longitudeDeg?: number;
  readonly ayanamsa?: AyanamsaConvention | string;
  readonly nodeMode?: NodeMode;
}

export interface CompleteChartResult {
  readonly time: JulianDateInfo;
  readonly observer: {
    readonly latitudeDeg: number;
    readonly longitudeDeg: number;
  };
  readonly ayanamsa: {
    readonly key: string;
    readonly label: string;
    readonly degrees: number;
    readonly dms: string;
  };
  readonly houses: AscendantAndHousesResult;
  readonly grahas: Readonly<Record<GrahaId, GrahaPosition>>;
  readonly shodashvarga: Readonly<Record<ShodashvargaCode, VargaChart>>;
  readonly panchanga: PanchangaResult;
  readonly ashtakavarga: AshtakavargaResult;
  readonly shadbala: Readonly<Record<PhysicalGrahaId, ShadbalaPlanetSummary>>;
  readonly vimshottari: VimshottariDashaResult;
  readonly receipt: CalculationReceipt;
  readonly executionTimeMs: number;
}

export const ENGINE_VERSION: string;
export const AYANAMSA_CATALOG_VERSION: string;
export const HOUSE_CONVENTIONS_VERSION: string;
export const LUNAR_NODE_CONVENTIONS_VERSION: string;
export const RASI_CATALOG: readonly RasiMetadata[];
export const NAKSHATRA_CATALOG: readonly NakshatraMetadata[];
export const SHODASHVARGA_DEFINITIONS: readonly ShodashvargaDefinition[];

export function normalizeDegrees(angle: number): number;
export function formatDms(degreesInSign: number): string;
export function dateToJulianDate(input?: string | number | Date | Record<string, unknown>): JulianDateInfo;
export function julianDateToIsoUtc(jdUtc: number): string;
export function estimateDeltaTSeconds(decimalYear: number): number;
export function resolveAyanamsaKey(convention?: AyanamsaConvention | string): string;
export function computeAyanamsa(jdTt: number, convention?: AyanamsaConvention | string): number;
export function computeMeanLunarNode(jdTt: number): number;
export function computeTrueLunarNode(jdTt: number): number;
export function computeNakshatra(siderealLongitudeDeg: number): NakshatraPosition;
export function computePlanets(
  jdTt: number,
  options?: { ayanamsa?: AyanamsaConvention | string; nodeMode?: NodeMode }
): {
  ayanamsaKey: string;
  ayanamsaDeg: number;
  nodeMode: NodeMode;
  grahas: Record<GrahaId, GrahaPosition>;
};
export function computeAscendantAndHouses(
  jdTt: number,
  jdUt1: number,
  latitudeDeg: number,
  longitudeDeg: number,
  ayanamsa?: AyanamsaConvention | string
): AscendantAndHousesResult;
export function computeVargaRasiIndex(siderealLongitudeDeg: number, vargaCode: ShodashvargaCode | string): number;
export function computeShodashvarga(
  siderealAscendantDeg: number,
  grahasMap: Record<GrahaId, GrahaPosition>
): Record<ShodashvargaCode, VargaChart>;
export function computePanchanga(jdUtc: number, sunSiderealDeg: number, moonSiderealDeg: number): PanchangaResult;
export function computeAshtakavarga(lagnaRasiIndex: number, grahasMap: Record<GrahaId, GrahaPosition>): AshtakavargaResult;
export function computeShadbala(
  siderealAscendantDeg: number,
  grahasMap: Record<GrahaId, GrahaPosition>,
  shodashvarga: Record<ShodashvargaCode, VargaChart>
): Record<PhysicalGrahaId, ShadbalaPlanetSummary>;
export function jdToYmdString(jdUtc: number): string;
export function computeVimshottariDasha(jdUtc: number, moonSiderealDeg: number): VimshottariDashaResult;
export interface ClientKundaliBenchmarkResult {
  readonly iterations: number;
  readonly medianMs: number;
  readonly p95Ms: number;
  readonly sub2msQualified: boolean;
  readonly sampleReceiptSha256: string;
}

export interface BatchNatalRequestInput {
  readonly jdUtc: number;
  readonly jdTt?: number;
  readonly deltaTSec?: number;
  readonly latDeg: number;
  readonly lonDeg: number;
  readonly altM?: number;
  readonly elevM?: number;
  readonly ayanamsaId?: number;
  readonly houseSystemId?: number;
  readonly nodeMode?: number;
}

export interface FullKundaliZeroCopyView {
  readonly planetLonSidereal: Float64Array;
  readonly planetLatEcliptic: Float64Array;
  readonly planetLat: Float64Array;
  readonly planetSpeedLon: Float64Array;
  readonly houseCuspsSidereal: Float64Array;
  readonly vargaRashiMatrix: Uint8Array;
  readonly ashtakavargaBav: Uint8Array;
  readonly ashtakavargaSav: Uint8Array;
  readonly savAlignmentPad: Uint8Array;
  readonly dashaMahadashaStartJd: Float64Array;
  readonly dashaAntardashaStartJd: Float64Array;
  readonly polarStatusFlag: number;
  readonly byteLength: 1416;
}

export function sha256Hex(asciiString: string): string;
export function fnv1a64Hex(str: string): string;
export function computeReceipt(requestPayload: Record<string, unknown>, numericSummary: Record<string, unknown>): CalculationReceipt;
export function computeChart(options?: ChartInputOptions): CompleteChartResult;
export function evaluateChebyshevSegment3D(
  coeffsRevX: ArrayLike<number>,
  coeffsRevY: ArrayLike<number>,
  coeffsRevZ: ArrayLike<number>,
  jdTdb: number,
  startJd: number,
  spanDays: number
): [number, number, number, number, number, number];
export function benchmarkClientKundali(iterations?: number): ClientKundaliBenchmarkResult;
export function isWasmArenaInitialized(): boolean;
export function initEphemerisWasm(kernelBytes?: Uint8Array | ArrayBuffer | string): Promise<void>;
export function computeFullChartZeroCopy(request: BatchNatalRequestInput): FullKundaliZeroCopyView;

export const EphemerisBrowser: {
  readonly ENGINE_VERSION: string;
  readonly AYANAMSA_CATALOG_VERSION: string;
  readonly HOUSE_CONVENTIONS_VERSION: string;
  readonly LUNAR_NODE_CONVENTIONS_VERSION: string;
  readonly RASI_CATALOG: readonly RasiMetadata[];
  readonly NAKSHATRA_CATALOG: readonly NakshatraMetadata[];
  readonly SHODASHVARGA_DEFINITIONS: readonly ShodashvargaDefinition[];
  readonly normalizeDegrees: typeof normalizeDegrees;
  readonly formatDms: typeof formatDms;
  readonly dateToJulianDate: typeof dateToJulianDate;
  readonly julianDateToIsoUtc: typeof julianDateToIsoUtc;
  readonly estimateDeltaTSeconds: typeof estimateDeltaTSeconds;
  readonly resolveAyanamsaKey: typeof resolveAyanamsaKey;
  readonly computeAyanamsa: typeof computeAyanamsa;
  readonly computeMeanLunarNode: typeof computeMeanLunarNode;
  readonly computeTrueLunarNode: typeof computeTrueLunarNode;
  readonly computeNakshatra: typeof computeNakshatra;
  readonly computePlanets: typeof computePlanets;
  readonly computeAscendantAndHouses: typeof computeAscendantAndHouses;
  readonly computeVargaRasiIndex: typeof computeVargaRasiIndex;
  readonly computeShodashvarga: typeof computeShodashvarga;
  readonly computePanchanga: typeof computePanchanga;
  readonly computeAshtakavarga: typeof computeAshtakavarga;
  readonly computeShadbala: typeof computeShadbala;
  readonly jdToYmdString: typeof jdToYmdString;
  readonly computeVimshottariDasha: typeof computeVimshottariDasha;
  readonly sha256Hex: typeof sha256Hex;
  readonly fnv1a64Hex: typeof fnv1a64Hex;
  readonly computeReceipt: typeof computeReceipt;
  readonly computeChart: typeof computeChart;
  readonly evaluateChebyshevSegment3D: typeof evaluateChebyshevSegment3D;
  readonly benchmarkClientKundali: typeof benchmarkClientKundali;
  readonly isWasmArenaInitialized: typeof isWasmArenaInitialized;
  readonly initEphemerisWasm: typeof initEphemerisWasm;
  readonly computeFullChartZeroCopy: typeof computeFullChartZeroCopy;
};

export default EphemerisBrowser;
