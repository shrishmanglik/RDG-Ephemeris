use ephemeris_core::spk::{SpkError, SpkKernel, State};
use std::io::Cursor;

fn integer(buf: &mut [u8], offset: usize, n: i32, big: bool) {
    buf[offset..offset + 4].copy_from_slice(&if big {
        n.to_be_bytes()
    } else {
        n.to_le_bytes()
    });
}

fn number(buf: &mut [u8], offset: usize, n: f64, big: bool) {
    buf[offset..offset + 8].copy_from_slice(&if big {
        n.to_be_bytes()
    } else {
        n.to_le_bytes()
    });
}

// Two independently written exact polynomials, with two records each. In the
// first interval x = 10 + 2*tau + 3*(2*tau^2-1), y = 20, z = -5.
fn fixture(big: bool, data_type: i32) -> Vec<u8> {
    let mut buf = vec![0u8; 4096];
    buf[..8].copy_from_slice(b"DAF/SPK ");
    integer(&mut buf, 8, 2, big);
    integer(&mut buf, 12, 6, big);
    integer(&mut buf, 76, 2, big);
    integer(&mut buf, 80, 2, big);
    buf[88..96].copy_from_slice(if big { b"BIG-IEEE" } else { b"LTL-IEEE" });
    let components = if data_type == 3 { 6 } else { 3 };
    let size = 2 + 3 * components;
    let start = 385;
    let end = start + 2 * size + 4 - 1;
    integer(&mut buf, 84, end + 1, big);
    number(&mut buf, 1024, 0., big);
    number(&mut buf, 1032, 0., big);
    number(&mut buf, 1040, 1., big);
    number(&mut buf, 1048, -10., big);
    number(&mut buf, 1056, 30., big);
    for (i, n) in [301, 0, 1, data_type, start, end].iter().enumerate() {
        integer(&mut buf, 1064 + i * 4, *n, big);
    }
    for interval in 0..2 {
        let offset = 3072 + interval * size as usize * 8;
        number(&mut buf, offset, interval as f64 * 20., big);
        number(&mut buf, offset + 8, 10., big);
        for (i, n) in [10., 2., 3., 20., 0., 0., -5., 0., 0.].iter().enumerate() {
            number(&mut buf, offset + 16 + i * 8, *n, big);
        }
        if data_type == 3 {
            for (i, n) in [7., 0., 0., 8., 0., 0., 9., 0., 0.].iter().enumerate() {
                number(&mut buf, offset + 88 + i * 8, *n, big);
            }
        }
    }
    let trailer = 3072 + 2 * size as usize * 8;
    for (i, n) in [-10., 20., size as f64, 2.].iter().enumerate() {
        number(&mut buf, trailer + i * 8, *n, big);
    }
    buf
}

fn fixture_with_comment(big: bool) -> Vec<u8> {
    let original = fixture(big, 2);
    let mut data = vec![0u8; 5120];
    data[..1024].copy_from_slice(&original[..1024]);
    data[2048..3072].copy_from_slice(&original[1024..2048]);
    data[4096..5120].copy_from_slice(&original[3072..4096]);
    integer(&mut data, 76, 3, big);
    integer(&mut data, 80, 3, big);
    integer(&mut data, 84, 539, big);
    integer(&mut data, 2104, 513, big);
    integer(&mut data, 2108, 538, big);
    data
}

#[test]
fn comment_records_are_not_arrays_and_valid_comments_remain_supported() {
    for big in [false, true] {
        let valid = fixture_with_comment(big);
        let mut k = SpkKernel::open(Cursor::new(valid.clone())).unwrap();
        assert_eq!(k.state(301, 0, 5.).unwrap().position_km, [9.5, 20., -5.]);
        let mut invalid = valid;
        let coefficients = invalid[4096..4304].to_vec();
        invalid[1024..1232].copy_from_slice(&coefficients);
        integer(&mut invalid, 2104, 129, big);
        integer(&mut invalid, 2108, 154, big);
        assert!(SpkKernel::open(Cursor::new(invalid)).is_err());
        let mut invalid = fixture_with_comment(big);
        integer(&mut invalid, 84, 400, big);
        assert!(SpkKernel::open(Cursor::new(invalid)).is_err());
    }
}

#[test]
fn shifted_midpoint_or_radius_cannot_change_the_record_time_scale() {
    for big in [false, true] {
        for (offset, value) in [(3072, 1.), (3080, 11.)] {
            let mut data = fixture(big, 2);
            number(&mut data, offset, value, big);
            let mut k = SpkKernel::open(Cursor::new(data)).unwrap();
            assert!(matches!(k.state(301, 0, 5.), Err(SpkError::Invalid(_))));
        }
    }
}

#[test]
fn relative_state_ignores_an_unsupported_edge_above_the_common_ancestor() {
    for big in [false, true] {
        let original = fixture(big, 2);
        let mut data = original.clone();
        data.resize(6144, 0);
        integer(&mut data, 84, 667, big);
        number(&mut data, 1040, 3., big);
        for (item, (target, center, frame)) in
            [(301, 3, 1), (399, 3, 1), (3, 0, 2)].iter().enumerate()
        {
            let offset = 1048 + item * 40;
            number(&mut data, offset, -10., big);
            number(&mut data, offset + 8, 30., big);
            let start = 385 + item as i32 * 128;
            for (i, n) in [*target, *center, *frame, 2, start, start + 25]
                .iter()
                .enumerate()
            {
                integer(&mut data, offset + 16 + i * 4, *n, big);
            }
            data[3072 + item * 1024..3280 + item * 1024].copy_from_slice(&original[3072..3280]);
        }
        number(&mut data, 4112, 1., big);
        number(&mut data, 4136, 4., big);
        number(&mut data, 4160, -2., big);
        let mut k = SpkKernel::open(Cursor::new(data)).unwrap();
        assert_eq!(
            k.state(301, 399, 5.).unwrap(),
            State {
                position_km: [9., 16., -3.],
                velocity_km_s: [0.; 3]
            }
        );
        assert_eq!(k.state(399, 301, 5.).unwrap().position_km, [-9., -16., 3.]);
        assert!(matches!(k.state(301, 0, 5.), Err(SpkError::Unsupported(_))));
    }
}

#[test]
fn reads_type_two_real_binary_polynomial_and_analytic_velocity() {
    for big in [false, true] {
        let mut kernel = SpkKernel::open(Cursor::new(fixture(big, 2))).unwrap();
        let state = kernel
            .state(301, 0, 5.)
            .expect("Type 2 segment must be evaluated");
        assert_eq!(
            state,
            State {
                position_km: [9.5, 20., -5.],
                velocity_km_s: [0.8, 0., 0.]
            }
        );
    }
}

#[test]
fn type_three_uses_supplied_velocity_and_inclusive_final_epoch() {
    for big in [false, true] {
        let mut k = SpkKernel::open(Cursor::new(fixture(big, 3))).unwrap();
        assert_eq!(k.state(301, 0, 5.).unwrap().velocity_km_s, [7., 8., 9.]);
        assert_eq!(k.state(301, 0, 30.).unwrap().position_km, [15., 20., -5.]);
        assert!(matches!(k.state(301, 0, 30.0001), Err(SpkError::Coverage)));
        assert!(matches!(k.state(301, 0, -10.0001), Err(SpkError::Coverage)));
        assert_eq!(k.state(0, 301, 5.).unwrap().velocity_km_s, [-7., -8., -9.]);
    }
}

#[test]
fn record_boundary_uses_later_record_and_zero_self_is_finite_only() {
    let mut k = SpkKernel::open(Cursor::new(fixture(false, 2))).unwrap();
    assert_eq!(k.state(301, 0, 10.).unwrap().position_km, [11., 20., -5.]);
    assert_eq!(k.state(301, 301, 0.).unwrap().position_km, [0.; 3]);
    assert!(matches!(
        k.state(301, 301, f64::NAN),
        Err(SpkError::Invalid(_))
    ));
}

#[test]
fn rejects_truncation_cycle_and_directory_overlap() {
    let mut data = fixture(false, 2);
    data.pop();
    assert!(SpkKernel::open(Cursor::new(data)).is_err());
    let mut data = fixture(false, 2);
    number(&mut data, 1024, 2., false);
    assert!(SpkKernel::open(Cursor::new(data)).is_err());
    let mut data = fixture(false, 2);
    integer(&mut data, 1080, 129, false);
    assert!(SpkKernel::open(Cursor::new(data)).is_err());
}

#[test]
fn refuses_unsupported_frame_type_and_bad_coefficients_without_fallback() {
    for (offset, value) in [(1072, 2), (1076, 17)] {
        let mut data = fixture(false, 2);
        integer(&mut data, offset, value, false);
        let mut k = SpkKernel::open(Cursor::new(data)).unwrap();
        assert!(matches!(k.state(301, 0, 5.), Err(SpkError::Unsupported(_))));
    }
    let mut data = fixture(false, 2);
    number(&mut data, 3088, f64::NAN, false);
    let mut k = SpkKernel::open(Cursor::new(data)).unwrap();
    assert!(matches!(k.state(301, 0, 5.), Err(SpkError::Invalid(_))));
}

#[test]
fn malformed_trailer_radius_and_summary_counts_fail_closed() {
    for (offset, value) in [
        (3248, 3.),
        (3256, 0.),
        (3264, 11.5),
        (3272, 2.5),
        (3080, 0.),
    ] {
        let mut data = fixture(false, 2);
        number(&mut data, offset, value, false);
        let mut k = SpkKernel::open(Cursor::new(data)).unwrap();
        assert!(k.state(301, 0, 5.).is_err(), "offset {offset}");
    }
    for value in [26., f64::NAN, 0.5] {
        let mut data = fixture(false, 2);
        number(&mut data, 1040, value, false);
        assert!(SpkKernel::open(Cursor::new(data)).is_err());
    }
}

#[test]
fn direct_relative_segment_does_not_require_solar_system_root() {
    let mut data = fixture(false, 2);
    integer(&mut data, 1068, 3, false);
    let mut k = SpkKernel::open(Cursor::new(data)).unwrap();
    assert_eq!(k.state(301, 3, 5.).unwrap().position_km, [9.5, 20., -5.]);
    assert!(matches!(k.state(301, 0, 5.), Err(SpkError::Coverage)));
}

#[test]
fn ffi_leaves_output_untouched_on_error() {
    let data = fixture(false, 2);
    let mut output = [999.; 6];
    let status = unsafe {
        ephemeris_core::spk::ephemeris_spk_state(
            data.as_ptr(),
            data.len(),
            301,
            0,
            50.,
            output.as_mut_ptr(),
        )
    };
    assert_eq!(status, 3);
    assert_eq!(output, [999.; 6]);
    let status = unsafe {
        ephemeris_core::spk::ephemeris_spk_state(
            data.as_ptr(),
            data.len(),
            301,
            0,
            5.,
            output.as_mut_ptr(),
        )
    };
    assert_eq!(status, 0);
    assert_eq!(output, [9.5, 20., -5., 0.8, 0., 0.]);
}
