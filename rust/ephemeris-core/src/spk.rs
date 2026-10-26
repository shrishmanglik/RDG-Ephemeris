//! JPL SPK Type 2/3 reader. Public formats: NAIF DAF and SPK Required Reading.
use std::collections::BTreeSet;
use std::io::{Read, Seek, SeekFrom};

const RECORD_BYTES: u64 = 1024;
const MAX_RECORD_WORDS: usize = 65536;

#[derive(Debug)]
pub enum SpkError {
    Io(std::io::Error),
    Invalid(&'static str),
    Unsupported(&'static str),
    Coverage,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct State {
    pub position_km: [f64; 3],
    pub velocity_km_s: [f64; 3],
}

impl State {
    fn zero() -> Self {
        Self {
            position_km: [0.; 3],
            velocity_km_s: [0.; 3],
        }
    }
    fn add(self, other: Self, sign: f64) -> Result<Self, SpkError> {
        let mut result = self;
        for axis in 0..3 {
            result.position_km[axis] += sign * other.position_km[axis];
            result.velocity_km_s[axis] += sign * other.velocity_km_s[axis];
        }
        if result
            .position_km
            .iter()
            .chain(result.velocity_km_s.iter())
            .all(|v| v.is_finite())
        {
            Ok(result)
        } else {
            Err(SpkError::Invalid("nonfinite state"))
        }
    }
}

#[derive(Clone, Copy)]
enum Endian {
    Little,
    Big,
}

impl Endian {
    fn integer(self, bytes: &[u8]) -> i32 {
        let mut b = [0u8; 4];
        b.copy_from_slice(&bytes[..4]);
        match self {
            Self::Little => i32::from_le_bytes(b),
            Self::Big => i32::from_be_bytes(b),
        }
    }
    fn number(self, bytes: &[u8]) -> f64 {
        let mut b = [0u8; 8];
        b.copy_from_slice(&bytes[..8]);
        match self {
            Self::Little => f64::from_le_bytes(b),
            Self::Big => f64::from_be_bytes(b),
        }
    }
}

#[derive(Clone, Debug)]
pub struct Segment {
    pub start_tdb_seconds: f64,
    pub end_tdb_seconds: f64,
    pub target: i32,
    pub center: i32,
    pub frame: i32,
    pub data_type: i32,
    start_word: u64,
    end_word: u64,
}

pub struct SpkKernel<R> {
    reader: R,
    endian: Endian,
    segments: Vec<Segment>,
}

impl From<std::io::Error> for SpkError {
    fn from(value: std::io::Error) -> Self {
        Self::Io(value)
    }
}

fn index(value: f64) -> Result<usize, SpkError> {
    if !value.is_finite() || value < 0. || value.fract() != 0. || value >= usize::MAX as f64 {
        Err(SpkError::Invalid("nonintegral or out-of-range index"))
    } else {
        Ok(value as usize)
    }
}

fn positive(value: i32) -> Result<u64, SpkError> {
    if value <= 0 {
        Err(SpkError::Invalid("nonpositive address"))
    } else {
        Ok(value as u64)
    }
}

fn read_at<R: Read + Seek>(reader: &mut R, offset: u64, bytes: &mut [u8]) -> Result<(), SpkError> {
    reader.seek(SeekFrom::Start(offset))?;
    reader.read_exact(bytes)?;
    Ok(())
}

impl<R: Read + Seek> SpkKernel<R> {
    /// Read the directory only; coefficients stay in the caller-owned seekable
    /// input. Native files therefore do not require a multi-gigabyte allocation.
    pub fn open(mut reader: R) -> Result<Self, SpkError> {
        let length = reader.seek(SeekFrom::End(0))?;
        if length < RECORD_BYTES || length % RECORD_BYTES != 0 {
            return Err(SpkError::Invalid("DAF record length"));
        }
        let mut header = [0u8; 1024];
        read_at(&mut reader, 0, &mut header)?;
        if &header[..8] != b"DAF/SPK " {
            return Err(SpkError::Unsupported("not a DAF/SPK file"));
        }
        let endian = match &header[88..96] {
            b"LTL-IEEE" => Endian::Little,
            b"BIG-IEEE" => Endian::Big,
            _ => return Err(SpkError::Unsupported("DAF binary format")),
        };
        if endian.integer(&header[8..]) != 2 || endian.integer(&header[12..]) != 6 {
            return Err(SpkError::Invalid("SPK descriptor dimensions"));
        }
        let mut next = positive(endian.integer(&header[76..]))?;
        let first_summary = next;
        let last = positive(endian.integer(&header[80..]))?;
        let free = positive(endian.integer(&header[84..]))?;
        if free > length / 8 + 1 || free <= (first_summary + 1) * 128 {
            return Err(SpkError::Invalid("free address outside allocated data"));
        }
        let mut seen = BTreeSet::new();
        let mut previous = 0;
        let mut segments = Vec::new();
        while next != 0 {
            if next < 2 || next >= length / RECORD_BYTES || !seen.insert(next) {
                return Err(SpkError::Invalid("summary chain bounds or cycle"));
            }
            let mut record = [0u8; 1024];
            read_at(&mut reader, (next - 1) * RECORD_BYTES, &mut record)?;
            if index(endian.number(&record[8..]))? as u64 != previous {
                return Err(SpkError::Invalid("summary back pointer"));
            }
            let count = index(endian.number(&record[16..]))?;
            if count > (1024 - 24) / 40 {
                return Err(SpkError::Invalid("summary count"));
            }
            for item in 0..count {
                let offset = 24 + item * 40;
                let descriptor = &record[offset..offset + 40];
                let start_word = positive(endian.integer(&descriptor[32..]))?;
                let end_word = positive(endian.integer(&descriptor[36..]))?;
                let start = endian.number(descriptor);
                let end = endian.number(&descriptor[8..]);
                if !start.is_finite()
                    || !end.is_finite()
                    || start > end
                    || start_word < (first_summary - 1) * 128 + 1
                    || start_word > end_word
                    || end_word >= free
                {
                    return Err(SpkError::Invalid("segment descriptor bounds"));
                }
                segments.push(Segment {
                    start_tdb_seconds: start,
                    end_tdb_seconds: end,
                    target: endian.integer(&descriptor[16..]),
                    center: endian.integer(&descriptor[20..]),
                    frame: endian.integer(&descriptor[24..]),
                    data_type: endian.integer(&descriptor[28..]),
                    start_word,
                    end_word,
                });
            }
            previous = next;
            next = index(endian.number(&record))? as u64;
        }
        if previous != last {
            return Err(SpkError::Invalid("final summary pointer"));
        }
        for segment in &segments {
            for summary in &seen {
                let first = (summary - 1) * 128 + 1;
                let end = (summary + 1) * 128;
                if segment.start_word <= end && segment.end_word >= first {
                    return Err(SpkError::Invalid("segment overlaps directory"));
                }
            }
        }
        Ok(Self {
            reader,
            endian,
            segments,
        })
    }

    pub fn segments(&self) -> &[Segment] {
        &self.segments
    }

    /// Geometric J2000 state, km and km/s, at TDB seconds from J2000.
    /// This does not apply light time, aberration, TT conversion or refraction.
    pub fn state(&mut self, target: i32, center: i32, tdb_seconds: f64) -> Result<State, SpkError> {
        if !tdb_seconds.is_finite() {
            return Err(SpkError::Invalid("nonfinite epoch"));
        }
        if target == center {
            return Ok(State::zero());
        }
        let (target_path, target_error) = self.path(target, tdb_seconds, Some(center));
        if let Some((_, state)) = target_path.iter().find(|(body, _)| *body == center) {
            return Ok(*state);
        }
        let (center_path, center_error) = self.path(center, tdb_seconds, None);
        for (ancestor, state) in target_path {
            if let Some((_, center_state)) = center_path.iter().find(|(body, _)| *body == ancestor)
            {
                return state.add(*center_state, -1.);
            }
        }
        Err(target_error.or(center_error).unwrap_or(SpkError::Coverage))
    }

    fn path(
        &mut self,
        mut body: i32,
        epoch: f64,
        stop: Option<i32>,
    ) -> (Vec<(i32, State)>, Option<SpkError>) {
        let mut path = vec![(body, State::zero())];
        let mut seen = BTreeSet::new();
        let mut accumulated = State::zero();
        while body != 0 && Some(body) != stop {
            if !seen.insert(body) {
                return (path, Some(SpkError::Invalid("body center cycle")));
            }
            // Later segments have NAIF priority; an unsupported selected segment
            // must never silently fall through to an earlier representation.
            let selected = self
                .segments
                .iter()
                .rev()
                .find(|s| {
                    s.target == body && epoch >= s.start_tdb_seconds && epoch <= s.end_tdb_seconds
                })
                .cloned();
            let Some(segment) = selected else {
                break;
            };
            // Keep usable prefixes when an irrelevant edge above the common
            // ancestor cannot be evaluated. Only an unresolved request needs
            // that terminal error; a relative state uses no higher edge.
            accumulated = match self
                .evaluate(&segment, epoch)
                .and_then(|state| accumulated.add(state, 1.))
            {
                Ok(state) => state,
                Err(error) => return (path, Some(error)),
            };
            body = segment.center;
            path.push((body, accumulated));
        }
        (path, None)
    }

    fn evaluate(&mut self, segment: &Segment, epoch: f64) -> Result<State, SpkError> {
        if segment.frame != 1 {
            return Err(SpkError::Unsupported("only J2000 frame is supported"));
        }
        let components = match segment.data_type {
            2 => 3,
            3 => 6,
            _ => return Err(SpkError::Unsupported("SPK segment type")),
        };
        if segment.end_word - segment.start_word + 1 < 4 {
            return Err(SpkError::Invalid("missing segment trailer"));
        }
        let mut tail = [0u8; 32];
        read_at(&mut self.reader, (segment.end_word - 4) * 8, &mut tail)?;
        let init = self.endian.number(&tail);
        let interval = self.endian.number(&tail[8..]);
        let size = index(self.endian.number(&tail[16..]))?;
        let count = index(self.endian.number(&tail[24..]))?;
        if !init.is_finite()
            || !interval.is_finite()
            || interval <= 0.
            || size < 2 + components
            || size > MAX_RECORD_WORDS
            || (size - 2) % components != 0
            || count == 0
        {
            return Err(SpkError::Invalid("Chebyshev trailer"));
        }
        let words = (size as u64)
            .checked_mul(count as u64)
            .and_then(|v| v.checked_add(4));
        if words != Some(segment.end_word - segment.start_word + 1) {
            return Err(SpkError::Invalid("segment record count"));
        }
        let end = init + interval * count as f64;
        if !end.is_finite()
            || epoch < init
            || epoch > end
            || segment.start_tdb_seconds < init
            || segment.end_tdb_seconds > end
        {
            return Err(SpkError::Invalid("descriptor outside coefficient coverage"));
        }
        let record = index(((epoch - init) / interval).floor())?.min(count - 1);
        let offset = (segment.start_word - 1 + record as u64 * size as u64) * 8;
        let mut bytes = vec![0u8; size * 8];
        read_at(&mut self.reader, offset, &mut bytes)?;
        let midpoint = self.endian.number(&bytes);
        let radius = self.endian.number(&bytes[8..]);
        if !midpoint.is_finite() || !radius.is_finite() || radius <= 0. {
            return Err(SpkError::Invalid("record time normalization"));
        }
        // DAF chooses the record using INIT/INTLEN. Its stored normalization
        // must describe that same interval, within floating-point rounding.
        let expected_midpoint = init + (record as f64 + 0.5) * interval;
        let expected_radius = interval / 2.;
        let midpoint_tolerance = 4. * f64::EPSILON * expected_midpoint.abs().max(interval).max(1.);
        let radius_tolerance = 4. * f64::EPSILON * expected_radius.abs().max(1.);
        if (midpoint - expected_midpoint).abs() > midpoint_tolerance
            || (radius - expected_radius).abs() > radius_tolerance
        {
            return Err(SpkError::Invalid("record interval disagrees with trailer"));
        }
        let tau = (epoch - midpoint) / radius;
        if !tau.is_finite() || !(-1. ..=1.).contains(&tau) {
            return Err(SpkError::Invalid("epoch outside selected record"));
        }
        let degree = (size - 2) / components;
        let mut state = State::zero();
        for component in 0..components {
            let mut coefficients = Vec::with_capacity(degree);
            for item in 0..degree {
                let coefficient = self
                    .endian
                    .number(&bytes[(2 + component * degree + item) * 8..]);
                if !coefficient.is_finite() {
                    return Err(SpkError::Invalid("nonfinite coefficient"));
                }
                coefficients.push(coefficient);
            }
            let (value, derivative) = crate::evaluate_chebyshev_1d(&coefficients, tau);
            if component < 3 {
                state.position_km[component] = value;
                if components == 3 {
                    state.velocity_km_s[component] = derivative / radius;
                }
            } else {
                state.velocity_km_s[component - 3] = value;
            }
        }
        state.add(State::zero(), 1.)
    }
}

fn status(error: SpkError) -> i32 {
    match error {
        SpkError::Invalid(_) => 1,
        SpkError::Unsupported(_) => 2,
        SpkError::Coverage => 3,
        SpkError::Io(_) => 4,
    }
}

/// Allocate initialized bytes for a WASM caller. Null means allocation refused.
#[no_mangle]
pub extern "C" fn ephemeris_spk_buffer_new(length: usize) -> *mut u8 {
    let mut buffer = Vec::new();
    if length == 0 || buffer.try_reserve_exact(length).is_err() {
        return std::ptr::null_mut();
    }
    buffer.resize(length, 0u8);
    Box::into_raw(buffer.into_boxed_slice()) as *mut u8
}

/// # Safety
/// Pointer and length must be the live allocation returned by buffer_new;
/// release exactly once, with its original length.
#[no_mangle]
pub unsafe extern "C" fn ephemeris_spk_buffer_free(pointer: *mut u8, length: usize) {
    if !pointer.is_null() {
        drop(Box::from_raw(std::ptr::slice_from_raw_parts_mut(
            pointer, length,
        )));
    }
}

/// # Safety
/// Input must point to length readable bytes; output to six writable doubles.
/// Invalid inputs return 1; unsupported format/frame 2; missing coverage 3;
/// IO error 4. Output is left unchanged on error.
#[no_mangle]
pub unsafe extern "C" fn ephemeris_spk_state(
    pointer: *const u8,
    length: usize,
    target: i32,
    center: i32,
    tdb_seconds: f64,
    output: *mut f64,
) -> i32 {
    if pointer.is_null() || output.is_null() || length == 0 {
        return 1;
    }
    let bytes = std::slice::from_raw_parts(pointer, length);
    match SpkKernel::open(std::io::Cursor::new(bytes))
        .and_then(|mut k| k.state(target, center, tdb_seconds))
    {
        Ok(state) => {
            for axis in 0..3 {
                *output.add(axis) = state.position_km[axis];
                *output.add(axis + 3) = state.velocity_km_s[axis];
            }
            0
        }
        Err(error) => status(error),
    }
}

/// Native streaming entry point. The caller verifies the kernel hash with the
/// asset registry; no coefficients or bulk kernel bytes are copied into Python.
/// # Safety
/// Path must point to path_length UTF-8 bytes, output to six writable doubles.
#[cfg(not(target_arch = "wasm32"))]
#[no_mangle]
pub unsafe extern "C" fn ephemeris_spk_file_state(
    path: *const u8,
    path_length: usize,
    target: i32,
    center: i32,
    tdb_seconds: f64,
    output: *mut f64,
) -> i32 {
    if path.is_null() || output.is_null() || path_length == 0 {
        return 1;
    }
    let Ok(path) = std::str::from_utf8(std::slice::from_raw_parts(path, path_length)) else {
        return 1;
    };
    let result = std::fs::File::open(path)
        .map_err(SpkError::from)
        .and_then(SpkKernel::open)
        .and_then(|mut k| k.state(target, center, tdb_seconds));
    match result {
        Ok(state) => {
            for axis in 0..3 {
                *output.add(axis) = state.position_km[axis];
                *output.add(axis + 3) = state.velocity_km_s[axis];
            }
            0
        }
        Err(error) => status(error),
    }
}
