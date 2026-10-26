"""Exercise the native file reader and actual WebAssembly execution, not export strings."""
from __future__ import annotations

import hashlib
import ctypes
import json
import math
import os
from pathlib import Path
import struct
import subprocess
import sys

import numpy as np
import pytest
from jplephem.spk import SPK

from ephemeris_oss.rust_bridge import read_spk_state

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / 'rust/ephemeris-core/target/release' / (
    'ephemeris_core.dll' if sys.platform == 'win32' else
    'libephemeris_core.dylib' if sys.platform == 'darwin' else 'libephemeris_core.so')


def _fixture(midpoint: float = 0., radius: float = 10.) -> bytes:
    data = bytearray(4096)
    data[:8] = b'DAF/SPK '
    struct.pack_into('<ii', data, 8, 2, 6)
    struct.pack_into('<iii', data, 76, 2, 2, 400)
    data[88:96] = b'LTL-IEEE'
    struct.pack_into('<ddd', data, 1024, 0., 0., 1.)
    struct.pack_into('<ddiiiiii', data, 1048, midpoint-radius, midpoint+radius, 301, 0, 1, 2, 385, 399)
    struct.pack_into('<15d', data, 3072, midpoint, radius, 10., 2., 3., 20., 0., 0., -5., 0., 0., midpoint-radius, 2*radius, 11., 1.)
    return bytes(data)


def test_native_file_sdk_reads_real_bytes_and_fails_closed(tmp_path):
    assert LIBRARY.is_file(), 'Build the declared native Rust input before this suite'
    path = tmp_path / 'polynomial.bsp'
    path.write_bytes(_fixture())
    assert read_spk_state(path, 301, 0, 5., library_path=LIBRARY) == (9.5, 20., -5., .8, 0., 0.)
    assert read_spk_state(path, 0, 301, 5., library_path=LIBRARY) == (-9.5, -20., 5., -.8, 0., 0.)
    with pytest.raises(ValueError, match='coverage'):
        read_spk_state(path, 301, 0, 11., library_path=LIBRARY)
    for target in (True, 2**31, .5):
        with pytest.raises(ValueError, match='32-bit'):
            read_spk_state(path, target, 0, 0., library_path=LIBRARY)
    with pytest.raises(ValueError, match='finite'):
        read_spk_state(path, 301, 0, math.inf, library_path=LIBRARY)
    path.write_bytes(b'not a kernel')
    with pytest.raises(ValueError, match='invalid'):
        read_spk_state(path, 301, 0, 0., library_path=LIBRARY)


def test_sparse_native_protocol_validates_framing_and_requests_missing_bytes():
    library = ctypes.CDLL(str(LIBRARY))
    function = library.ephemeris_spk_sparse_state
    function.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int32,
                         ctypes.c_int32, ctypes.c_double, ctypes.POINTER(ctypes.c_double)]
    function.restype = ctypes.c_int32

    def run(data):
        buffer = ctypes.create_string_buffer(data)
        output = (ctypes.c_double * 6)()
        return function(buffer, len(data), 301, 0, 5., output), tuple(output)

    status, request = run(struct.pack('<QI', 4096, 0))
    assert status == 100
    assert request[0] == 0. and 0. < request[1] <= 4096.
    complete = struct.pack('<QI', 4096, 1)+struct.pack('<QI', 0, 4096)+_fixture()
    for _ in range(2):
        status, state = run(complete)
        assert status == 0
        assert state == (9.5, 20., -5., .8, 0., 0.)
    for malformed in (
        b'bad', struct.pack('<QI', 2**53, 0), struct.pack('<QI', 4096, 0)+b'x',
        struct.pack('<QI', 4096, 1)+struct.pack('<QI', 0, 0),
        struct.pack('<QI', 4096, 1)+struct.pack('<QI', 4095, 2)+b'xx',
        struct.pack('<QI', 4096, 2)+struct.pack('<QI', 0, 2)+b'ab'
        +struct.pack('<QI', 1, 2)+b'cd',
    ):
        assert run(malformed)[0] not in (0, 100)


def test_seekable_wasm_reuses_reader_with_bounded_async_ranges(tmp_path):
    path = tmp_path / 'seekable.bsp'
    path.write_bytes(_fixture())
    script = '''
import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const sdk=await import(pathToFileURL(process.argv[1]));
await sdk.initEphemerisWasm(new Uint8Array(fs.readFileSync(process.argv[2])));
const bytes=new Uint8Array(fs.readFileSync(process.argv[3]));
const reads=[];
const source={size:bytes.length,async read(offset,length){
  reads.push([offset,length]); await Promise.resolve(); return bytes.slice(offset,offset+length);
}};
for(let repeat=0;repeat<2;repeat++) {
  const [a,b]=await Promise.all([sdk.readSpkStateSeekable(source,301,0,5),
                                 sdk.readSpkStateSeekable(source,301,0,-5)]);
  assert.deepEqual(a,[9.5,20,-5,.8,0,0]);
  assert.deepEqual(b,[7.5,20,-5,-.4,0,0]);
}
assert.ok(reads.length>1 && reads.every(([o,n])=>n<bytes.length));
await assert.rejects(sdk.readSpkStateSeekable(source,301,0,11),/status 3/);
await assert.rejects(sdk.readSpkStateSeekable(source,301,0,5,{maxRequests:1}),/request|limit/i);
await assert.rejects(sdk.readSpkStateSeekable(source,301,0,5,{maxCacheBytes:16}),/cache|limit/i);
await assert.rejects(sdk.readSpkStateSeekable({size:4096,async read(o,n){return bytes.slice(o,o+n-1);}},
                                          301,0,5),/short|length/i);
await assert.rejects(sdk.readSpkStateSeekable({size:NaN,read:source.read},301,0,5),/size|integer/i);
console.log('Seekable WASM ranges, concurrency, repeats and refusal controls passed');
'''
    result = subprocess.run(['node', '--input-type=module', '-e', script,
                             str(ROOT/'web/ephemeris-browser.js'),
                             str(ROOT/'rust/ephemeris-core/wasm/ephemeris_spk.wasm'), str(path)],
                            cwd=ROOT, capture_output=True, text=True, check=True)
    assert 'Seekable WASM' in result.stdout


def test_actual_wasm_sdk_executes_reader_and_preserves_math_module_size(tmp_path):
    path = tmp_path / 'polynomial.bsp'
    path.write_bytes(_fixture())
    math_module = ROOT/'rust/ephemeris-core/wasm/ephemeris_core.wasm'
    reader_module = ROOT/'rust/ephemeris-core/wasm/ephemeris_spk.wasm'
    assert math_module.stat().st_size < 65536
    assert reader_module.is_file(), 'Build the spk-reader WASM feature before this suite'
    script = '''
import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const sdk=await import(pathToFileURL(process.argv[1]));
const kernel=new Uint8Array(fs.readFileSync(process.argv[3]));
assert.throws(()=>sdk.readSpkState(kernel,301,0,5),/Initialize/);
await sdk.initEphemerisWasm(new Uint8Array(fs.readFileSync(process.argv[2])));
for(let i=0;i<2;i++) {
  assert.deepEqual(sdk.readSpkState(kernel,301,0,5),[9.5,20,-5,.8,0,0]);
  assert.throws(()=>sdk.readSpkState(kernel,301,0,11),/status 3/);
  assert.throws(()=>sdk.readSpkState(kernel,2**32,0,0),/32-bit/);
  assert.throws(()=>sdk.readSpkState(kernel,301,0,NaN),/finite/);
}
console.log('Actual WASM SDK execution and repeat controls passed');
'''
    result = subprocess.run(['node','--input-type=module','-e',script,
                             str(ROOT/'web/ephemeris-browser.js'),str(reader_module),str(path)],
                            cwd=ROOT,capture_output=True,text=True,check=True)
    assert 'Actual WASM SDK execution' in result.stdout


def test_native_and_wasm_sdk_accept_the_complete_jpl_time_span(tmp_path):
    """A portable time-coordinate control, distinct from real-kernel accuracy."""
    first = (-3100015.5 - 2451545.) * 86400.
    last = (8000016.5 - 2451545.) * 86400.
    midpoint = (first + last) / 2.
    radius = (last - first) / 2.
    path = tmp_path / 'long-span-polynomial.bsp'
    path.write_bytes(_fixture(midpoint, radius))
    epochs = [first, midpoint-radius/2., midpoint, midpoint+radius/2., last]
    expected = [[11., 20., -5., -10./radius, 0., 0.],
                [7.5, 20., -5., -4./radius, 0., 0.],
                [7., 20., -5., 2./radius, 0., 0.],
                [9.5, 20., -5., 8./radius, 0., 0.],
                [15., 20., -5., 14./radius, 0., 0.]]
    for epoch, state in zip(epochs, expected):
        np.testing.assert_allclose(read_spk_state(path, 301, 0, epoch, library_path=LIBRARY),
                                   state, rtol=0., atol=1e-14)
    script = '''
import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const sdk=await import(pathToFileURL(process.argv[1]));
await sdk.initEphemerisWasm(new Uint8Array(fs.readFileSync(process.argv[2])));
const kernel=new Uint8Array(fs.readFileSync(process.argv[3]));
const {epochs,expected}=JSON.parse(process.argv[4]);
for(let run=0;run<2;run++) for(let i=0;i<epochs.length;i++) {
  const state=sdk.readSpkState(kernel,301,0,epochs[i]);
  state.forEach((v,j)=>assert.ok(Math.abs(v-expected[i][j])<=1e-14));
}
assert.throws(()=>sdk.readSpkState(kernel,301,0,epochs[0]-1),/status 3/);
assert.throws(()=>sdk.readSpkState(kernel,301,0,epochs.at(-1)+1),/status 3/);
'''
    subprocess.run(['node', '--input-type=module', '-e', script,
                    str(ROOT/'web/ephemeris-browser.js'),
                    str(ROOT/'rust/ephemeris-core/wasm/ephemeris_spk.wasm'), str(path),
                    json.dumps({'epochs': epochs, 'expected': expected})],
                   cwd=ROOT, capture_output=True, text=True, check=True)


def test_de440_numerical_reader_agreement_at_edges_and_range_epochs(kernel_path):
    assert LIBRARY.is_file(), 'Build the declared native Rust input before this suite'
    rows=[]
    with SPK.open(str(kernel_path)) as reference:
        for segment in reference.segments:
            if segment.data_type != 2:
                continue
            first=(segment.start_jd-2451545.)*86400.
            last=(segment.end_jd-2451545.)*86400.
            for seconds in np.linspace(first,last,17):
                state=read_spk_state(kernel_path,segment.target,segment.center,float(seconds),library_path=LIBRARY)
                position, velocity_day=segment.compute_and_differentiate(2451545.,float(seconds)/86400.)
                actual=np.asarray(state[:3]); expected=np.asarray(position)
                np.testing.assert_allclose(actual,expected,rtol=0.,atol=2e-6)
                np.testing.assert_allclose(state[3:],velocity_day/86400.,rtol=0.,atol=1e-10)
                angular=None
                if np.linalg.norm(expected)>0.:
                    a=actual/np.linalg.norm(actual); b=expected/np.linalg.norm(expected)
                    angular=math.degrees(math.atan2(float(np.linalg.norm(np.cross(a,b))),float(np.dot(a,b))))*3600.
                    assert angular<.001
                rows.append({'target':segment.target,'center':segment.center,'tdb_seconds':float(seconds),
                             'position_error_km':float(np.max(np.abs(actual-expected))),
                             'angular_residual_arcsec':angular})
        # A geocentric Moon state requires the graph, not just one segment.
        moon=read_spk_state(kernel_path,301,399,0.,library_path=LIBRARY)
        position,velocity=reference[3,301].compute_and_differentiate(2451545.)
        earth,earth_velocity=reference[3,399].compute_and_differentiate(2451545.)
        np.testing.assert_allclose(moon[:3],position-earth,rtol=0.,atol=2e-6)
        np.testing.assert_allclose(moon[3:],(velocity-earth_velocity)/86400.,rtol=0.,atol=1e-10)
    # An explicit output opt-in keeps ordinary test runs from mutating evidence.
    output=os.getenv('EPHEMERIS_SPK_BENCH_OUTPUT')
    if output:
        kernel_hash=hashlib.sha256(Path(kernel_path).read_bytes()).hexdigest()
        Path(output).write_text(json.dumps({'scope':'same-kernel numerical reader agreement; not physical or apparent-place accuracy',
            'kernel_sha256':kernel_hash,'samples':rows,
            'de441_full_range':'NOT_RUN by this DE440 test; use the separate verified-input qualification'},indent=2)+'\n')
