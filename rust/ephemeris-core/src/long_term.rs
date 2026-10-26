//! Optional long-term sidereal-convention evaluator.
//!
//! The catalog is generated from the Python definition home.  This module owns
//! only the numerical operations over those definitions.  Long-term precession
//! and ecliptic matrices are supplied by the permissively licensed `sofars`
//! implementation of IAU SOFA-derived computations; see the crate's
//! `THIRD_PARTY_NOTICES.md`.

use crate::ayanamsa_catalog::DEFINITIONS;
use sofars::coords::ltecm;
use sofars::pnp::{ltp, ltpecl, ltpequ};

const J2000_JD: f64 = 2_451_545.0;
const JULIAN_YEAR_DAYS: f64 = 365.25;
const MIN_DE441_JD_TT: f64 = -3_100_015.5;
const MAX_DE441_JD_TT: f64 = 8_000_016.5;

fn normalize_degrees(value: f64) -> f64 {
    let normalized = value % 360.0;
    if normalized < 0.0 {
        normalized + 360.0
    } else if normalized == 0.0 {
        0.0
    } else {
        normalized
    }
}

fn julian_epoch(jd_tt: f64) -> f64 {
    2000.0 + (jd_tt - J2000_JD) / JULIAN_YEAR_DAYS
}

fn dot(left: [f64; 3], right: [f64; 3]) -> f64 {
    left[0] * right[0] + left[1] * right[1] + left[2] * right[2]
}

fn cross(left: [f64; 3], right: [f64; 3]) -> [f64; 3] {
    [
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    ]
}

fn normalize_vector(vector: [f64; 3]) -> Option<[f64; 3]> {
    let magnitude = dot(vector, vector).sqrt();
    if !magnitude.is_finite() || magnitude <= f64::EPSILON {
        return None;
    }
    Some([
        vector[0] / magnitude,
        vector[1] / magnitude,
        vector[2] / magnitude,
    ])
}

fn matrix_vector(matrix: [[f64; 3]; 3], vector: [f64; 3]) -> [f64; 3] {
    [
        dot(matrix[0], vector),
        dot(matrix[1], vector),
        dot(matrix[2], vector),
    ]
}

fn transpose_matrix_vector(matrix: [[f64; 3]; 3], vector: [f64; 3]) -> [f64; 3] {
    [
        matrix[0][0] * vector[0]
            + matrix[1][0] * vector[1]
            + matrix[2][0] * vector[2],
        matrix[0][1] * vector[0]
            + matrix[1][1] * vector[1]
            + matrix[2][1] * vector[2],
        matrix[0][2] * vector[0]
            + matrix[1][2] * vector[1]
            + matrix[2][2] * vector[2],
    ]
}

fn fixed_ray_ayanamsa(
    jd_tt: f64,
    reference_jd_tt: f64,
    reference_offset_deg: f64,
    reference_equinox_displacement_arcsec: f64,
) -> f64 {
    let corrected_offset =
        reference_offset_deg - reference_equinox_displacement_arcsec / 3600.0;
    if jd_tt == reference_jd_tt {
        return normalize_degrees(corrected_offset);
    }

    let reference_epoch = julian_epoch(reference_jd_tt);
    let date_epoch = julian_epoch(jd_tt);
    let reference_precession = ltp(reference_epoch);
    let date_precession = ltp(date_epoch);

    // Express the date equinox first in J2000 and then on the reference
    // epoch's mean equator and equinox.
    let equinox_j2000 =
        transpose_matrix_vector(date_precession, [1.0, 0.0, 0.0]);
    let equinox_reference = matrix_vector(reference_precession, equinox_j2000);

    let equator_pole = ltpequ(reference_epoch);
    let ecliptic_pole = ltpecl(reference_epoch);
    let cosine_obliquity = dot(equator_pole, ecliptic_pole).clamp(-1.0, 1.0);
    let obliquity = cosine_obliquity.acos();
    let reference_longitude = (equinox_reference[1] * obliquity.cos()
        + equinox_reference[2] * obliquity.sin())
    .atan2(equinox_reference[0])
    .to_degrees();

    normalize_degrees(corrected_offset - reference_longitude)
}

fn galactic_plane_ayanamsa(
    jd_tt: f64,
    sidereal_anchor_deg: f64,
    pole_ra_deg: f64,
    pole_dec_deg: f64,
) -> f64 {
    let (sin_ra, cos_ra) = pole_ra_deg.to_radians().sin_cos();
    let (sin_dec, cos_dec) = pole_dec_deg.to_radians().sin_cos();
    let galactic_pole = [cos_dec * cos_ra, cos_dec * sin_ra, sin_dec];

    let ecliptic_matrix = ltecm(julian_epoch(jd_tt));
    // The third row of an ICRS-to-ecliptic rotation is the ecliptic pole
    // expressed in ICRS.  p x q selects the node that crosses from negative
    // to positive galactic latitude as ecliptic longitude increases.
    let ecliptic_pole = ecliptic_matrix[2];
    let ascending_node = match normalize_vector(cross(galactic_pole, ecliptic_pole)) {
        Some(node) => node,
        None => return f64::NAN,
    };
    let node_ecliptic = matrix_vector(ecliptic_matrix, ascending_node);
    let longitude = node_ecliptic[1].atan2(node_ecliptic[0]).to_degrees();
    normalize_degrees(longitude - sidereal_anchor_deg)
}

/// Evaluate one generated long-term ayanamsa convention.
///
/// `system_id` is the zero-based Python catalog order.  Model 1 entries require
/// the caller to supply the already-computed date-specific ordinary or polar
/// tropical longitude appropriate to that convention.  Refused inputs return
/// NaN so the C and WebAssembly ABI cannot silently substitute an approximation.
#[no_mangle]
pub extern "C" fn ephemeris_ayanamsa_v2(
    jd_tt: f64,
    system_id: u32,
    anchor_longitude_deg: f64,
) -> f64 {
    if !jd_tt.is_finite() || !(MIN_DE441_JD_TT..=MAX_DE441_JD_TT).contains(&jd_tt) {
        return f64::NAN;
    }

    let definition = match DEFINITIONS.get(system_id as usize) {
        Some(definition) => *definition,
        None => return f64::NAN,
    };
    let (
        model,
        reference_jd_tt,
        reference_offset_deg,
        reference_equinox_displacement_arcsec,
        sidereal_anchor_deg,
        galactic_pole_ra_deg,
        galactic_pole_dec_deg,
    ) = definition;

    match model {
        0 if reference_jd_tt.is_finite()
            && reference_offset_deg.is_finite()
            && reference_equinox_displacement_arcsec.is_finite() =>
        {
            fixed_ray_ayanamsa(
                jd_tt,
                reference_jd_tt,
                reference_offset_deg,
                reference_equinox_displacement_arcsec,
            )
        }
        1 if anchor_longitude_deg.is_finite() && sidereal_anchor_deg.is_finite() => {
            normalize_degrees(anchor_longitude_deg - sidereal_anchor_deg)
        }
        2 if sidereal_anchor_deg.is_finite()
            && galactic_pole_ra_deg.is_finite()
            && galactic_pole_dec_deg.is_finite() =>
        {
            galactic_plane_ayanamsa(
                jd_tt,
                sidereal_anchor_deg,
                galactic_pole_ra_deg,
                galactic_pole_dec_deg,
            )
        }
        _ => f64::NAN,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn fixed_ray_returns_corrected_offset_at_defining_epoch() {
        let result = fixed_ray_ayanamsa(2_400_000.5, 2_400_000.5, 23.5, 0.72);
        assert_eq!(result, 23.5 - 0.72 / 3600.0);
    }

    #[test]
    fn fixed_ray_long_term_transport_is_finite_away_from_epoch() {
        let result = fixed_ray_ayanamsa(2_451_545.0, 2_400_000.5, 23.5, 0.0);
        assert!(result.is_finite());
        assert!((0.0..360.0).contains(&result));
    }

    #[test]
    fn node_cross_product_selects_ascending_intersection() {
        let galactic_pole = normalize_vector([0.2, 0.8, 0.5]).unwrap();
        let ecliptic_pole = normalize_vector([0.0, -0.4, 0.9]).unwrap();
        let node = normalize_vector(cross(galactic_pole, ecliptic_pole)).unwrap();
        assert!(dot(cross(ecliptic_pole, node), galactic_pole) > 0.0);
    }
}
