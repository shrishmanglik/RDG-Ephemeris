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
}
