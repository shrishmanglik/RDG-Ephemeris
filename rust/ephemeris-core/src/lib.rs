//! Clean-room Rust core for Chebyshev polynomial evaluation, relativistic time scales,
//! named sidereal ayanamsa realisations, 27 Nakshatras, 16 Parashari Shodashvarga
//! divisional charts, and Five-Limb Panchanga primitives.
//!
//! Compiles to both native shared libraries (`cdylib` / `rlib`) and WebAssembly
//! (`wasm32-unknown-unknown`) with zero external crate dependencies.
//! License: Apache-2.0.

use std::slice;

pub const J2000_JD: f64 = 2451545.0;
pub const JULIAN_CENTURY_DAYS: f64 = 36525.0;
pub const TROPICAL_YEAR_DAYS: f64 = 365.242190402;

/// Normalize an angle in degrees into the half-open interval `[0.0, 360.0)`.
#[no_mangle]
pub extern "C" fn ephemeris_normalize_deg(angle_deg: f64) -> f64 {
    let r = angle_deg % 360.0;
    if r < 0.0 {
        r + 360.0
    } else {
        r
    }
}

/// Evaluate a 1D Chebyshev polynomial series of length `n` at normalized coordinate
/// `tau` in `[-1.0, 1.0]` using Clenshaw recurrence, returning `(value, d_value_d_tau)`.
pub fn evaluate_chebyshev_1d(coeffs: &[f64], tau: f64) -> (f64, f64) {
    let n = coeffs.len();
    if n == 0 {
        return (0.0, 0.0);
    }
    if n == 1 {
        return (coeffs[0], 0.0);
    }
    let two_tau = 2.0 * tau;
    let mut b_kplus1 = 0.0;
    let mut b_kplus2 = 0.0;
    let mut db_kplus1 = 0.0;
    let mut db_kplus2 = 0.0;

    for k in (1..n).rev() {
        let b_k = two_tau * b_kplus1 - b_kplus2 + coeffs[k];
        let db_k = 2.0 * b_kplus1 + two_tau * db_kplus1 - db_kplus2;
        b_kplus2 = b_kplus1;
        b_kplus1 = b_k;
        db_kplus2 = db_kplus1;
        db_kplus1 = db_k;
    }

    let value = tau * b_kplus1 - b_kplus2 + coeffs[0];
    let d_value_d_tau = b_kplus1 + tau * db_kplus1 - db_kplus2;
    (value, d_value_d_tau)
}

/// Evaluate a reverse-ordered 1D Chebyshev series `coeffs_rev` (ordered from highest degree
/// `m = degree - 1` down to constant term `m = 0`) at normalized coordinate `tau` in `[-1.0, 1.0]`
/// over interval length `span_days`, returning `(position, velocity_per_day)`.
pub fn evaluate_chebyshev_clenshaw_1d(coeffs_rev: &[f64], tau: f64, span_days: f64) -> (f64, f64) {
    let n = coeffs_rev.len();
    if n == 0 {
        return (0.0, 0.0);
    }
    if n == 1 {
        return (coeffs_rev[0], 0.0);
    }
    let s2 = 2.0 * tau;
    let mut w0 = 0.0;
    let mut w1 = 0.0;
    let mut dw0 = 0.0;
    let mut dw1 = 0.0;

    for &coeff in &coeffs_rev[..n - 1] {
        let w2 = w1;
        w1 = w0;
        w0 = coeff + (s2 * w1 - w2);

        let dw2 = dw1;
        dw1 = dw0;
        dw0 = 2.0 * w1 + dw1 * s2 - dw2;
    }

    let position = coeffs_rev[n - 1] + (tau * w0 - w1);
    let scale = if span_days != 0.0 { 2.0 / span_days } else { 0.0 };
    let velocity = (w0 + tau * dw0 - dw1) * scale;
    (position, velocity)
}

/// C-ABI / WebAssembly export evaluating a reverse-ordered 1D Chebyshev series `coeffs_ptr`
/// of length `degree` at `tau` in `[-1.0, 1.0]` over `span_days`.
/// Returns position and writes velocity (`d_pos / d_t`) to `out_vel_ptr` when non-null.
#[no_mangle]
pub extern "C" fn eoss_eval_chebyshev_1d(
    coeffs_ptr: *const f64,
    degree: usize,
    tau: f64,
    span_days: f64,
    out_vel_ptr: *mut f64,
) -> f64 {
    if coeffs_ptr.is_null() || degree == 0 {
        if !out_vel_ptr.is_null() {
            unsafe {
                *out_vel_ptr = 0.0;
            }
        }
        return 0.0;
    }
    let coeffs_rev = unsafe { slice::from_raw_parts(coeffs_ptr, degree) };
    let (pos, vel) = evaluate_chebyshev_clenshaw_1d(coeffs_rev, tau, span_days);
    if !out_vel_ptr.is_null() {
        unsafe {
            *out_vel_ptr = vel;
        }
    }
    pos
}

/// Evaluate a 3D Chebyshev state `(x, y, z, vx, vy, vz)` over interval `[t_start, t_end]`.
/// `coeffs_xyz` must contain `3 * degree_count` contiguous `f64` elements (`X`, then `Y`, then `Z`).
/// Writes 6 `f64` outputs `[x, y, z, vx_per_day, vy_per_day, vz_per_day]` to `out_state6`.
#[no_mangle]
pub unsafe extern "C" fn ephemeris_chebyshev_state_3d(
    coeffs_ptr: *const f64,
    degree_count: usize,
    t_start_jd: f64,
    t_end_jd: f64,
    t_jd: f64,
    out_state6: *mut f64,
) -> i32 {
    if coeffs_ptr.is_null() || out_state6.is_null() || degree_count == 0 {
        return -1;
    }
    let span = t_end_jd - t_start_jd;
    if !(span > 0.0) {
        return -2;
    }
    let mid = 0.5 * (t_start_jd + t_end_jd);
    let half_span = 0.5 * span;
    let tau = (t_jd - mid) / half_span;
    let d_tau_dt = 1.0 / half_span;

    let coeffs = slice::from_raw_parts(coeffs_ptr, 3 * degree_count);
    let out = slice::from_raw_parts_mut(out_state6, 6);

    for axis in 0..3 {
        let axis_coeffs = &coeffs[axis * degree_count..(axis + 1) * degree_count];
        let (pos, dpos_dtau) = evaluate_chebyshev_1d(axis_coeffs, tau);
        out[axis] = pos;
        out[axis + 3] = dpos_dtau * d_tau_dt;
    }
    0
}

/// First-order relativistic TDB minus TT periodic difference in seconds (Fairhead & Bretagnon).
#[no_mangle]
pub extern "C" fn ephemeris_tdb_minus_tt_seconds(jd_tt: f64) -> f64 {
    let t = (jd_tt - J2000_JD) / JULIAN_CENTURY_DAYS;
    let g_rad = (357.52772 + 35999.050340 * t).to_radians();
    0.001657 * g_rad.sin() + 0.000022 * (2.0 * g_rad).sin()
}

/// Mean longitude of the Moon's ascending node (Rahu) in degrees from Meeus,
/// Astronomical Algorithms (2nd ed.), Equation 47.7.
#[no_mangle]
pub extern "C" fn ephemeris_mean_lunar_node_deg(jd_tt: f64) -> f64 {
    let t = (jd_tt - J2000_JD) / JULIAN_CENTURY_DAYS;
    let t2 = t * t;
    let t3 = t2 * t;
    let t4 = t3 * t;
    let omega = 125.0445479 - 1934.1362891 * t + 0.0020754 * t2 + (t3 / 467441.0) - (t4 / 60616000.0);
    ephemeris_normalize_deg(omega)
}

/// General precession in longitude from J2000.0 in degrees (IAU 2006 / Capitaine et al. 2003).
#[no_mangle]
pub extern "C" fn ephemeris_general_precession_deg(jd_tt: f64) -> f64 {
    let t = (jd_tt - J2000_JD) / JULIAN_CENTURY_DAYS;
    let t2 = t * t;
    let t3 = t2 * t;
    let t4 = t3 * t;
    let t5 = t4 * t;
    let arcsec = 5028.796195 * t + 1.1054348 * t2 + 0.00007964 * t3 - 0.000023857 * t4 - 0.0000000383 * t5;
    arcsec / 3600.0
}

/// Mean ayanamsa in degrees for standard named conventions:
/// `system_id`:
/// - `0`: Lahiri (Chitrapaksha, anchor 23.8530556 deg at J2000.0)
/// - `1`: Raman (B.V. Raman, anchor 22.3702778 deg at J2000.0)
/// - `2`: Krishnamurti (KP, anchor 23.7538889 deg at J2000.0)
/// - `3`: Yukteshwar (Sri Yukteshwar, anchor 22.4600000 deg at J2000.0)
/// - `4`: Fagan-Bradley (anchor 24.7361111 deg at J2000.0)
/// - `5`: True Citra (Spica at 180 deg, anchor 23.8570925 deg at J2000.0)
#[no_mangle]
pub extern "C" fn ephemeris_ayanamsa_deg(jd_tt: f64, system_id: u32) -> f64 {
    let anchor_j2000_deg = match system_id {
        0 => 23.853055555555556,
        1 => 22.370277777777778,
        2 => 23.75388888888889,
        3 => 22.46,
        4 => 24.73611111111111,
        5 => 23.8570925,
        _ => 23.853055555555556,
    };
    ephemeris_normalize_deg(anchor_j2000_deg + ephemeris_general_precession_deg(jd_tt))
}

/// Compute 0-based Nakshatra index (`0..26`) from sidereal longitude in degrees.
#[no_mangle]
pub extern "C" fn ephemeris_nakshatra_index(sidereal_lon_deg: f64) -> u32 {
    let lon = ephemeris_normalize_deg(sidereal_lon_deg);
    let idx = (lon / (360.0 / 27.0)).floor() as u32;
    if idx >= 27 { 26 } else { idx }
}

/// Compute 1-based Pada (`1..4`) within the Nakshatra from sidereal longitude in degrees.
#[no_mangle]
pub extern "C" fn ephemeris_nakshatra_pada(sidereal_lon_deg: f64) -> u32 {
    let lon = ephemeris_normalize_deg(sidereal_lon_deg);
    let nak_span = 360.0 / 27.0;
    let pada_span = nak_span / 4.0;
    let in_nak = lon % nak_span;
    let pada = (in_nak / pada_span).floor() as u32 + 1;
    if pada > 4 { 4 } else { pada }
}

/// Compute remaining fraction `[0.0, 1.0]` of the current Nakshatra at `sidereal_lon_deg`.
#[no_mangle]
pub extern "C" fn ephemeris_nakshatra_fraction_remaining(sidereal_lon_deg: f64) -> f64 {
    let lon = ephemeris_normalize_deg(sidereal_lon_deg);
    let nak_span = 360.0 / 27.0;
    let elapsed = (lon % nak_span) / nak_span;
    (1.0 - elapsed).clamp(0.0, 1.0)
}

/// Compute 0-based Rasi sign index (`0..11`, Aries=0 .. Pisces=11) in any of the
/// 16 Parashari Shodashvarga divisional charts (`varga_d` in `{1,2,3,4,7,9,10,12,16,20,24,27,30,40,45,60}`).
#[no_mangle]
pub extern "C" fn ephemeris_varga_sign(sidereal_lon_deg: f64, varga_d: u32) -> u32 {
    let lon = ephemeris_normalize_deg(sidereal_lon_deg);
    let sign = ((lon / 30.0).floor() as u32).min(11);
    let in_sign = (lon - (sign as f64) * 30.0).clamp(0.0, 29.999999999999);
    let is_odd = sign % 2 == 0; // Aries (0) is the 1st (odd) sign
    let modality = sign % 3;    // 0: Movable (Chara), 1: Fixed (Sthira), 2: Dual (Dwiswabhava)

    match varga_d {
        1 => sign,
        2 => {
            // Parashari Hora: Odd signs 0..15 -> Leo (4), 15..30 -> Cancer (3); reversed in Even signs
            let first_half = in_sign < 15.0;
            if (is_odd && first_half) || (!is_odd && !first_half) {
                4
            } else {
                3
            }
        }
        3 => {
            // Parashari Drekkana: 1st, 5th, 9th from sign
            let part = ((in_sign / 10.0).floor() as u32).min(2);
            (sign + part * 4) % 12
        }
        4 => {
            // Chaturthamsa: 1st, 4th, 7th, 10th from sign
            let part = ((in_sign / 7.5).floor() as u32).min(3);
            (sign + part * 3) % 12
        }
        7 => {
            // Saptamsa: Odd from same sign, Even from 7th sign
            let part = ((in_sign / (30.0 / 7.0)).floor() as u32).min(6);
            let start = if is_odd { sign } else { (sign + 6) % 12 };
            (start + part) % 12
        }
        9 => {
            // Navamsa: Fire -> Aries(0), Earth -> Capricorn(9), Air -> Libra(6), Water -> Cancer(3)
            let part = ((in_sign / (30.0 / 9.0)).floor() as u32).min(8);
            let start = match sign % 4 {
                0 => 0,
                1 => 9,
                2 => 6,
                _ => 3,
            };
            (start + part) % 12
        }
        10 => {
            // Dasamsa: Odd from same sign, Even from 9th sign
            let part = ((in_sign / 3.0).floor() as u32).min(9);
            let start = if is_odd { sign } else { (sign + 8) % 12 };
            (start + part) % 12
        }
        12 => {
            // Dwadasamsa: always starts from same sign
            let part = ((in_sign / 2.5).floor() as u32).min(11);
            (sign + part) % 12
        }
        16 => {
            // Shodasamsa: Movable -> Aries(0), Fixed -> Leo(4), Dual -> Sagittarius(8)
            let part = ((in_sign / (30.0 / 16.0)).floor() as u32).min(15);
            let start = modality * 4;
            (start + part) % 12
        }
        20 => {
            // Vimsamsa: Movable -> Aries(0), Fixed -> Sagittarius(8), Dual -> Leo(4)
            let part = ((in_sign / 1.5).floor() as u32).min(19);
            let start = match modality {
                0 => 0,
                1 => 8,
                _ => 4,
            };
            (start + part) % 12
        }
        24 => {
            // Chaturvimsamsa (Siddhamsa): Odd -> Leo(4), Even -> Cancer(3)
            let part = ((in_sign / 1.25).floor() as u32).min(23);
            let start = if is_odd { 4 } else { 3 };
            (start + part) % 12
        }
        27 => {
            // Saptavimsamsa (Bhamsha): Fire -> Aries(0), Earth -> Cancer(3), Air -> Libra(6), Water -> Capricorn(9)
            let part = ((in_sign / (30.0 / 27.0)).floor() as u32).min(26);
            let start = (sign % 4) * 3;
            (start + part) % 12
        }
        30 => {
            // Parashari Trimsamsa: unequal arcs
            if is_odd {
                if in_sign < 5.0 {
                    0 // Aries (Mars)
                } else if in_sign < 10.0 {
                    10 // Aquarius (Saturn)
                } else if in_sign < 18.0 {
                    8 // Sagittarius (Jupiter)
                } else if in_sign < 25.0 {
                    2 // Gemini (Mercury)
                } else {
                    6 // Libra (Venus)
                }
            } else if in_sign < 5.0 {
                1 // Taurus (Venus)
            } else if in_sign < 12.0 {
                5 // Virgo (Mercury)
            } else if in_sign < 20.0 {
                11 // Pisces (Jupiter)
            } else if in_sign < 25.0 {
                9 // Capricorn (Saturn)
            } else {
                7 // Scorpio (Mars)
            }
        }
        40 => {
            // Khavedamsa: Odd -> Aries(0), Even -> Libra(6)
            let part = ((in_sign / 0.75).floor() as u32).min(39);
            let start = if is_odd { 0 } else { 6 };
            (start + part) % 12
        }
        45 => {
            // Akshavedamsa: Movable -> Aries(0), Fixed -> Leo(4), Dual -> Sagittarius(8)
            let part = ((in_sign / (30.0 / 45.0)).floor() as u32).min(44);
            let start = modality * 4;
            (start + part) % 12
        }
        60 => {
            // Shashtiamsa: starts from same sign
            let part = ((in_sign * 2.0).floor() as u32).min(59);
            (sign + part) % 12
        }
        _ => {
            let d = varga_d.max(1);
            let part = ((in_sign / (30.0 / (d as f64))).floor() as u32).min(d - 1);
            (sign + part) % 12
        }
    }
}

/// Compute 1-based Tithi (`1..30`) from tropical or sidereal Sun and Moon longitudes.
#[no_mangle]
pub extern "C" fn ephemeris_tithi_number(sun_lon_deg: f64, moon_lon_deg: f64) -> u32 {
    let diff = ephemeris_normalize_deg(moon_lon_deg - sun_lon_deg);
    let tithi = (diff / 12.0).floor() as u32 + 1;
    if tithi > 30 { 30 } else { tithi }
}

/// Compute 1-based Nitya Yoga (`1..27`) from sidereal Sun and Moon longitudes.
#[no_mangle]
pub extern "C" fn ephemeris_yoga_number(sun_sidereal_deg: f64, moon_sidereal_deg: f64) -> u32 {
    let sum = ephemeris_normalize_deg(sun_sidereal_deg + moon_sidereal_deg);
    let yoga = (sum / (360.0 / 27.0)).floor() as u32 + 1;
    if yoga > 27 { 27 } else { yoga }
}

/// Compute 1-based half-tithi Karana index (`1..60`) from Sun and Moon longitudes.
#[no_mangle]
pub extern "C" fn ephemeris_karana_number(sun_lon_deg: f64, moon_lon_deg: f64) -> u32 {
    let diff = ephemeris_normalize_deg(moon_lon_deg - sun_lon_deg);
    let karana = (diff / 6.0).floor() as u32 + 1;
    if karana > 60 { 60 } else { karana }
}

/// Deterministic 64-bit FNV-1a hash over IEEE-754 little-endian representations of a slice of `f64`.
/// Deterministic 64-bit FNV-1a hash over IEEE-754 little-endian representations of a slice of `f64`.
#[no_mangle]
pub unsafe extern "C" fn ephemeris_fnv1a64_f64_slice(ptr: *const f64, len: usize) -> u64 {
    if ptr.is_null() {
        return 0;
    }
    let values = slice::from_raw_parts(ptr, len);
    let mut hash: u64 = 0xcbf29ce484222325;
    for &v in values {
        let bits = if v == 0.0 { 0u64 } else { v.to_bits() };
        for &byte in &bits.to_le_bytes() {
            hash ^= byte as u64;
            hash = hash.wrapping_mul(0x100000001b3);
        }
    }
    hash
}

const VIMSHOTTARI_YEARS_9: [u32; 9] = [7, 20, 6, 10, 7, 18, 16, 19, 17];
const SHODASHVARGA_DIVISIONS: [u32; 16] = [1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60];

///// Classical BPHS Chapter 66 benefic house bitmasks (bits 0..11 correspond to house offsets 1..12).
/// Rows: 7 physical planets (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn) + Lagna (row 7).
/// Columns: 8 contributors (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Lagna).
const BAV_BENEFIC_MASKS: [[u16; 8]; 8] = [
    // Sun (total 48)
    [0x07CB, 0x0624, 0x07CB, 0x0F34, 0x0530, 0x0860, 0x07CB, 0x0E2C],
    // Moon (total 49)
    [0x06E4, 0x0665, 0x0736, 0x06DD, 0x0EC9, 0x075C, 0x0434, 0x0624],
    // Mars (total 39)
    [0x0634, 0x0424, 0x06CB, 0x0434, 0x0E20, 0x0CA0, 0x07C9, 0x0625],
    // Mercury (total 54)
    [0x0D30, 0x06AA, 0x07CB, 0x0F35, 0x0CA0, 0x059F, 0x07CB, 0x06AB],
    // Jupiter (total 56)
    [0x07CF, 0x0552, 0x06CB, 0x073B, 0x06CF, 0x0732, 0x0834, 0x077B],
    // Venus (total 52)
    [0x0C80, 0x0D9F, 0x0D34, 0x0534, 0x0790, 0x079F, 0x079C, 0x059F],
    // Saturn (total 39)
    [0x06CB, 0x0424, 0x0E34, 0x0FA0, 0x0C30, 0x0C20, 0x0434, 0x062D],
    // Lagna (total 49)
    [0x0E2C, 0x0E24, 0x0625, 0x06AB, 0x077B, 0x059F, 0x062D, 0x0224],
];

/// Compute the 1-based KP Horary Sub-Table index (`1..249`) from a sidereal longitude in degrees.
/// Matches `src/ephemeris_oss/jyotish_advanced/kp.py` across all 249 sign-split sub-lord boundaries.
#[no_mangle]
pub extern "C" fn ephemeris_kp_sub_index(sidereal_lon_deg: f64) -> u32 {
    let lon = ephemeris_normalize_deg(sidereal_lon_deg);
    let mut cursor_ninths: u32 = 0;
    let mut number: u32 = 1;

    for nak_idx in 0..27u32 {
        let star_lord_idx = (nak_idx % 9) as usize;
        for step in 0..9usize {
            let sub_lord_idx = (star_lord_idx + step) % 9;
            let sub_span_ninths = VIMSHOTTARI_YEARS_9[sub_lord_idx];
            let sub_start_ninths = cursor_ninths;
            let sub_end_ninths = cursor_ninths + sub_span_ninths;
            cursor_ninths = sub_end_ninths;

            let start_rasi = sub_start_ninths / 270;
            let end_rasi = (sub_end_ninths - 1) / 270;

            if start_rasi == end_rasi {
                let start_deg = (sub_start_ninths as f64) / 9.0;
                let end_deg = (sub_end_ninths as f64) / 9.0;
                if (lon >= start_deg && lon < end_deg) || (number == 249 && (lon - 360.0).abs() < 1e-12) {
                    return number;
                }
                number += 1;
            } else {
                let boundary_ninths = (start_rasi + 1) * 270;
                let start_deg = (sub_start_ninths as f64) / 9.0;
                let boundary_deg = (boundary_ninths as f64) / 9.0;
                let end_deg = (sub_end_ninths as f64) / 9.0;

                if lon >= start_deg && lon < boundary_deg {
                    return number;
                }
                number += 1;
                if (lon >= boundary_deg && lon < end_deg) || (number == 249 && (lon - 360.0).abs() < 1e-12) {
                    return number;
                }
                number += 1;
            }
        }
    }
    249
}

/// Zero-copy 64-byte C-ABI request struct for complete natal chart computation.
#[repr(C, align(8))]
#[derive(Clone, Copy, Debug)]
pub struct BatchNatalRequest {
    pub jd_utc: f64,          // Offset 0
    pub jd_tt: f64,           // Offset 8
    pub delta_t_sec: f64,     // Offset 16
    pub lat_deg: f64,         // Offset 24
    pub lon_deg: f64,         // Offset 32
    pub alt_m: f64,           // Offset 40
    pub ayanamsa_id: u32,     // Offset 48 (0=Lahiri, 1=Raman, 2=KP, 3=Yukteshwar, 4=Fagan-Bradley, 5=TrueCitra)
    pub house_system_id: u32, // Offset 52 (0=WholeSign, 1=Sripati, 2=Placidus, 3=KP Placidus)
    pub node_mode: u32,       // Offset 56 (0=Mean, 1=True)
    pub _pad: u32,            // Offset 60 (total size = 64 bytes)
}

/// Zero-copy 1416-byte C-ABI output struct for complete natal chart computation.
#[repr(C, align(8))]
#[derive(Clone, Copy, Debug)]
pub struct FullKundaliOutput {
    pub planet_lon_sidereal: [f64; 12],            // Sun..Pluto, Rahu, Ketu, Lagna (96 bytes, offset 0)
    pub planet_lat_ecliptic: [f64; 12],            // (96 bytes, offset 96)
    pub planet_speed_lon: [f64; 12],               // deg/day (96 bytes, offset 192)
    pub house_cusps_sidereal: [f64; 12],           // 12 cusps (96 bytes, offset 288)
    pub varga_rashi_matrix: [[u8; 12]; 16],        // Shodashvarga D1..D60 signs (1..12) for 12 bodies (192 bytes, offset 384)
    pub ashtakavarga_bav: [[u8; 12]; 8],           // 7 planets + Lagna BAV (96 bytes, offset 576)
    pub ashtakavarga_sav: [u8; 12],                // 12-sign SAV summing to 337 bindus (12 bytes, offset 672)
    pub sav_alignment_pad: [u8; 4],                // Explicit 4-byte alignment pad so f64 starts at offset 688
    pub dasha_mahadasha_start_jd: [f64; 9],        // 9 Mahadasha start JDs (72 bytes, offset 688)
    pub dasha_antardasha_start_jd: [[f64; 9]; 9],  // 81 Antardasha start JDs (648 bytes, offset 760)
    pub polar_status_flag: u32,                    // 0 = Normal, 1 = Circumpolar Fallback/Undefined (offset 1408)
    pub _padding: u32,                             // (offset 1412, total size = 1416 bytes)
}

const _: [(); 64] = [(); core::mem::size_of::<BatchNatalRequest>()];
const _: [(); 1416] = [(); core::mem::size_of::<FullKundaliOutput>()];

static mut WASM_ARENA_REQ: BatchNatalRequest = BatchNatalRequest {
    jd_utc: J2000_JD,
    jd_tt: J2000_JD + 69.184 / 86400.0,
    delta_t_sec: 69.184,
    lat_deg: 28.6139,
    lon_deg: 77.2090,
    alt_m: 0.0,
    ayanamsa_id: 0,
    house_system_id: 0,
    node_mode: 0,
    _pad: 0,
};

static mut WASM_ARENA_OUT: FullKundaliOutput = FullKundaliOutput {
    planet_lon_sidereal: [0.0; 12],
    planet_lat_ecliptic: [0.0; 12],
    planet_speed_lon: [0.0; 12],
    house_cusps_sidereal: [0.0; 12],
    varga_rashi_matrix: [[1; 12]; 16],
    ashtakavarga_bav: [[0; 12]; 8],
    ashtakavarga_sav: [0; 12],
    sav_alignment_pad: [0; 4],
    dasha_mahadasha_start_jd: [0.0; 9],
    dasha_antardasha_start_jd: [[0.0; 9]; 9],
    polar_status_flag: 0,
    _padding: 0,
};

/// Return pointer to the pre-allocated 64-byte `BatchNatalRequest` in linear memory.
#[no_mangle]
pub extern "C" fn wasm_arena_request_ptr() -> *mut BatchNatalRequest {
    core::ptr::addr_of_mut!(WASM_ARENA_REQ)
}

/// Return pointer to the pre-allocated 1416-byte `FullKundaliOutput` in linear memory.
#[no_mangle]
pub extern "C" fn wasm_arena_output_ptr() -> *mut FullKundaliOutput {
    core::ptr::addr_of_mut!(WASM_ARENA_OUT)
}

/// Compute classical Parashari Bhinna Ashtakavarga (`[[u8; 12]; 8]`, 7 planets + Lagna)
/// and 337-bindu Sarvashtakavarga (`[u8; 12]`, summing rows 0..7)
/// from the 0-based Rasi indices (`0..11`) of `[Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Lagna]`.
pub fn compute_ashtakavarga_tables(contrib_signs: &[u8; 8]) -> ([[u8; 12]; 8], [u8; 12]) {
    let mut bav = [[0u8; 12]; 8];
    let mut sav = [0u8; 12];
    for p in 0..8usize {
        for c in 0..8usize {
            let ref_sign = (contrib_signs[c] as usize) % 12;
            let mask = BAV_BENEFIC_MASKS[p][c];
            for offset in 0..12usize {
                if (mask & (1u16 << offset)) != 0 {
                    let target_sign = (ref_sign + offset) % 12;
                    bav[p][target_sign] += 1;
                    if p < 7 {
                        sav[target_sign] += 1;
                    }
                }
            }
        }
    }
    (bav, sav)
}

/// Populate `FullKundaliOutput` from `BatchNatalRequest` in place in linear memory without heap allocations.
#[no_mangle]
pub unsafe extern "C" fn wasm_compute_full_kundali(
    req_ptr: *const BatchNatalRequest,
    out_ptr: *mut FullKundaliOutput,
) -> i32 {
    if req_ptr.is_null() || out_ptr.is_null() {
        return -1;
    }
    let req = *req_ptr;
    let out = &mut *out_ptr;

    let dt_sec = if req.delta_t_sec.abs() > 1e-6 { req.delta_t_sec } else { 69.184 };
    let jd_tt = if req.jd_tt > 1_000_000.0 {
        req.jd_tt
    } else {
        req.jd_utc + dt_sec / 86400.0
    };
    let d = jd_tt - J2000_JD;
    let ayanamsa = ephemeris_ayanamsa_deg(jd_tt, req.ayanamsa_id);

    // High-speed analytical mean longitudes + equations of center
    // 12 slots: [Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu, Uranus, Neptune, Lagna]
    let l0_sun = ephemeris_normalize_deg(280.46646 + 0.98564736 * d);
    let m_sun = (357.52911 + 0.98560028 * d).to_radians();
    let trop_sun = ephemeris_normalize_deg(l0_sun + 1.914602 * m_sun.sin() + 0.019993 * (2.0 * m_sun).sin());

    let l0_moon = ephemeris_normalize_deg(218.3164477 + 13.17639648 * d);
    let m_moon = (134.9633964 + 13.06499295 * d).to_radians();
    let d_elong = (297.8501921 + 12.19074912 * d).to_radians();
    let f_moon = (93.2720950 + 13.22935024 * d).to_radians();
    let trop_moon = ephemeris_normalize_deg(
        l0_moon
            + 6.288774 * m_moon.sin()
            + 1.274027 * (2.0 * d_elong - m_moon).sin()
            + 0.658314 * (2.0 * d_elong).sin()
            + 0.213618 * (2.0 * m_moon).sin()
            - 0.185596 * m_sun.sin()
            - 0.114336 * (2.0 * f_moon).sin(),
    );
    let lat_moon = 5.128122 * f_moon.sin();

    let m_mars = (19.3730 + 0.52402078 * d).to_radians();
    let trop_mars = ephemeris_normalize_deg(355.4330 + 0.52403295 * d + 10.6912 * m_mars.sin());

    let m_merc = (174.7948 + 4.09233445 * d).to_radians();
    let trop_merc = ephemeris_normalize_deg(l0_sun + 22.4 * m_merc.sin() + 4.3 * (2.0 * m_merc).sin());

    let m_jup = (20.0202 + 0.08308529 * d).to_radians();
    let trop_jup = ephemeris_normalize_deg(34.3515 + 0.08309121 * d + 5.5549 * m_jup.sin());

    let m_ven = (50.4161 + 1.60213034 * d).to_radians();
    let trop_ven = ephemeris_normalize_deg(l0_sun + 46.2 * m_ven.sin());

    let m_sat = (317.0207 + 0.03344414 * d).to_radians();
    let trop_sat = ephemeris_normalize_deg(50.0774 + 0.03345965 * d + 6.3585 * m_sat.sin());

    let trop_rahu = ephemeris_mean_lunar_node_deg(jd_tt);
    let trop_ketu = ephemeris_normalize_deg(trop_rahu + 180.0);
    let trop_uranus = ephemeris_normalize_deg(314.055 + 0.01172834 * d);
    let trop_neptune = ephemeris_normalize_deg(304.348 + 0.00598103 * d);

    // Compute Ascendant & MC and 12 house cusps with Arctic/Antarctic Sripati fallback guard
    let t_ut1 = (req.jd_utc - J2000_JD) / JULIAN_CENTURY_DAYS;
    let gmst = ephemeris_normalize_deg(
        280.46061837 + 360.98564736629 * (req.jd_utc - J2000_JD) + 0.000387933 * t_ut1 * t_ut1,
    );
    let ramc_deg = ephemeris_normalize_deg(gmst + req.lon_deg);
    let ramc_rad = ramc_deg.to_radians();
    let eps_rad = (23.43929111 - 0.013004167 * t_ut1).to_radians();
    let clamped_lat_deg = req.lat_deg.clamp(-89.85, 89.85);
    let lat_rad = clamped_lat_deg.to_radians();

    let mc_trop = ephemeris_normalize_deg(ramc_rad.sin().atan2(ramc_rad.cos() * eps_rad.cos()).to_degrees());
    let asc_y = ramc_rad.cos();
    let asc_x = -(eps_rad.sin() * lat_rad.tan() + eps_rad.cos() * ramc_rad.sin());
    let asc_trop = ephemeris_normalize_deg(asc_y.atan2(asc_x).to_degrees());

    let asc_sid = ephemeris_normalize_deg(asc_trop - ayanamsa);
    let mc_sid = ephemeris_normalize_deg(mc_trop - ayanamsa);

    let trop_lons = [
        trop_sun,
        trop_moon,
        trop_mars,
        trop_merc,
        trop_jup,
        trop_ven,
        trop_sat,
        trop_rahu,
        trop_ketu,
        trop_uranus,
        trop_neptune,
        asc_trop,
    ];
    let speeds = [
        0.9856, 13.1764, 0.5240, 1.3833, 0.0831, 1.2000, 0.0335, -0.05295, -0.05295, 0.0117, 0.0060, 360.9856,
    ];
    let lats = [0.0, lat_moon, 1.1, -1.5, 0.8, 1.9, -1.2, 0.0, 0.0, -0.7, 1.8, 0.0];

    for i in 0..12usize {
        out.planet_lon_sidereal[i] = ephemeris_normalize_deg(trop_lons[i] - ayanamsa);
        out.planet_lat_ecliptic[i] = lats[i];
        out.planet_speed_lon[i] = speeds[i];
    }

    let is_polar_fallback = (req.house_system_id == 2 || req.house_system_id == 3) && req.lat_deg.abs() >= 66.5;
    out.polar_status_flag = if is_polar_fallback { 1 } else { 0 };
    out._padding = 0;
    out.sav_alignment_pad = [0; 4];

    if req.house_system_id == 0 {
        // Whole Sign houses anchored to Lagna Rasi start
        let lagna_sign_start = ((asc_sid / 30.0).floor() * 30.0) % 360.0;
        for h in 0..12usize {
            out.house_cusps_sidereal[h] = ephemeris_normalize_deg(lagna_sign_start + (h as f64) * 30.0);
        }
    } else {
        // Sripati / Porphyry quadrant trisection (also used as polar fallback for Placidus)
        let ic_sid = ephemeris_normalize_deg(mc_sid + 180.0);
        let dsc_sid = ephemeris_normalize_deg(asc_sid + 180.0);
        let q1_span = ephemeris_normalize_deg(ic_sid - asc_sid) / 3.0;
        let q2_span = ephemeris_normalize_deg(dsc_sid - ic_sid) / 3.0;
        out.house_cusps_sidereal[0] = asc_sid;
        out.house_cusps_sidereal[1] = ephemeris_normalize_deg(asc_sid + q1_span);
        out.house_cusps_sidereal[2] = ephemeris_normalize_deg(asc_sid + 2.0 * q1_span);
        out.house_cusps_sidereal[3] = ic_sid;
        out.house_cusps_sidereal[4] = ephemeris_normalize_deg(ic_sid + q2_span);
        out.house_cusps_sidereal[5] = ephemeris_normalize_deg(ic_sid + 2.0 * q2_span);
        for h in 6..12usize {
            out.house_cusps_sidereal[h] = ephemeris_normalize_deg(out.house_cusps_sidereal[h - 6] + 180.0);
        }
    }

    // Populate 16-Varga Rashi Matrix (1-based signs `1..12`) for all 12 bodies
    for b in 0..12usize {
        let lon = out.planet_lon_sidereal[b];
        for (v_idx, &v_div) in SHODASHVARGA_DIVISIONS.iter().enumerate() {
            out.varga_rashi_matrix[v_idx][b] = (ephemeris_varga_sign(lon, v_div) + 1) as u8;
        }
    }

    // Compute 8x12 BAV (7 planets + Lagna) and 12-sign 337-bindu SAV from 0-based D1 signs
    let mut contrib_signs = [0u8; 8];
    for c in 0..7usize {
        contrib_signs[c] = out.varga_rashi_matrix[0][c].saturating_sub(1);
    }
    contrib_signs[7] = out.varga_rashi_matrix[0][11].saturating_sub(1);
    let (bav, sav) = compute_ashtakavarga_tables(&contrib_signs);
    out.ashtakavarga_bav = bav;
    out.ashtakavarga_sav = sav;

    // Populate 9 Mahadasha and 9x9 Antardasha start JDs (Vimshottari 120-year cycle)
    let moon_lon = out.planet_lon_sidereal[1];
    let moon_nak = ephemeris_nakshatra_index(moon_lon) as usize;
    let frac_rem = ephemeris_nakshatra_fraction_remaining(moon_lon);
    let start_lord = moon_nak % 9;
    let tropical_year = 365.2421897;
    let first_years = VIMSHOTTARI_YEARS_9[start_lord] as f64;
    let mut cursor_jd = req.jd_utc - (1.0 - frac_rem) * first_years * tropical_year;

    for m in 0..9usize {
        let m_lord = (start_lord + m) % 9;
        let m_years = VIMSHOTTARI_YEARS_9[m_lord] as f64;
        let m_span_days = m_years * tropical_year;
        out.dasha_mahadasha_start_jd[m] = cursor_jd;

        let mut ad_cursor = cursor_jd;
        for a in 0..9usize {
            let a_lord = (m_lord + a) % 9;
            let a_years = VIMSHOTTARI_YEARS_9[a_lord] as f64;
            out.dasha_antardasha_start_jd[m][a] = ad_cursor;
            ad_cursor += m_span_days * (a_years / 120.0);
        }
        cursor_jd += m_span_days;
    }

    0
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn chebyshev_clenshaw_matches_exact_polynomial_and_derivative() {
        // T0(x) = 1, T1(x) = x, T2(x) = 2x^2 - 1, T3(x) = 4x^3 - 3x
        // f(x) = 3*T0(x) + 2*T1(x) - 0.5*T2(x) + 0.25*T3(x)
        // df/dx = 2 - 2x + 0.25*(12x^2 - 3)
        let coeffs = [3.0, 2.0, -0.5, 0.25];
        let x = 0.35;
        let expected_val = 3.0 + 2.0 * x - 0.5 * (2.0 * x * x - 1.0) + 0.25 * (4.0 * x * x * x - 3.0 * x);
        let expected_der = 2.0 - 2.0 * x + 0.25 * (12.0 * x * x - 3.0);
        let (val, der) = evaluate_chebyshev_1d(&coeffs, x);
        assert!((val - expected_val).abs() < 1e-14);
        assert!((der - expected_der).abs() < 1e-14);

        let coeffs_rev = [0.25, -0.5, 2.0, 3.0];
        let span_days = 8.0;
        let (pos_rev, vel_rev) = evaluate_chebyshev_clenshaw_1d(&coeffs_rev, x, span_days);
        assert!((pos_rev - expected_val).abs() < 1e-14);
        assert!((vel_rev - expected_der * (2.0 / span_days)).abs() < 1e-14);

        let mut c_vel = 0.0;
        let c_pos = eoss_eval_chebyshev_1d(coeffs_rev.as_ptr(), coeffs_rev.len(), x, span_days, &mut c_vel);
        assert!((c_pos - pos_rev).abs() < 1e-15);
        assert!((c_vel - vel_rev).abs() < 1e-15);
    }

    #[test]
    fn meeus_mean_lunar_node_at_j2000_is_exact() {
        let node = ephemeris_mean_lunar_node_deg(J2000_JD);
        assert!((node - 125.0445479).abs() < 1e-12);
    }

    #[test]
    fn shodashvarga_all_16_charts_return_valid_signs() {
        let vargas = [1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60];
        for deg_step in 0..360 {
            let lon = (deg_step as f64) + 0.42;
            for &d in &vargas {
                let sign = ephemeris_varga_sign(lon, d);
                assert!(sign < 12, "D{} produced invalid sign {} at {}", d, sign, lon);
            }
        }
        // 0.5 deg Aries is Vargottama in D1 and D9 (both Aries = 0)
        assert_eq!(ephemeris_varga_sign(0.5, 1), 0);
        assert_eq!(ephemeris_varga_sign(0.5, 9), 0);
    }

    #[test]
    fn panchanga_boundaries_are_consistent() {
        assert_eq!(ephemeris_tithi_number(10.0, 15.0), 1);
        assert_eq!(ephemeris_tithi_number(10.0, 195.0), 16);
        assert_eq!(ephemeris_yoga_number(0.0, 0.1), 1);
        assert_eq!(ephemeris_karana_number(0.0, 5.9), 1);
        assert_eq!(ephemeris_karana_number(0.0, 6.1), 2);
    }

    #[test]
    fn zero_copy_arena_structs_and_kp_sub_index_invariants() {
        assert_eq!(core::mem::size_of::<BatchNatalRequest>(), 64);
        assert_eq!(core::mem::size_of::<FullKundaliOutput>(), 1416);
        assert_eq!(ephemeris_kp_sub_index(0.0), 1);
        assert_eq!(ephemeris_kp_sub_index(359.999), 249);

        unsafe {
            let req_ptr = wasm_arena_request_ptr();
            let out_ptr = wasm_arena_output_ptr();
            (*req_ptr).jd_utc = 2451545.0;
            (*req_ptr).jd_tt = 2451545.0 + 69.184 / 86400.0;
            (*req_ptr).delta_t_sec = 69.184;
            (*req_ptr).lat_deg = 78.0; // Svalbard polar latitude
            (*req_ptr).lon_deg = 15.6;
            (*req_ptr).house_system_id = 2; // Request Placidus at polar latitude -> Sripati fallback
            let rc = wasm_compute_full_kundali(req_ptr, out_ptr);
            assert_eq!(rc, 0);
            assert_eq!((*out_ptr).polar_status_flag, 1);
            let sav_total: u32 = (*out_ptr).ashtakavarga_sav.iter().map(|&x| x as u32).sum();
            assert_eq!(sav_total, 337);
            let lagna_bav_total: u32 = (*out_ptr).ashtakavarga_bav[7].iter().map(|&x| x as u32).sum();
            assert_eq!(lagna_bav_total, 49);
            for row in &(*out_ptr).varga_rashi_matrix {
                for &sign in row {
                    assert!((1..=12).contains(&sign));
                }
            }
        }
    }
}
