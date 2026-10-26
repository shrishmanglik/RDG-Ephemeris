"""Execute the optional native and browser convention core, not a JS mock."""
import ctypes
import json
import math
from pathlib import Path
import subprocess
import sys

import pytest

from ephemeris_oss.engine.conventions import AYANAMSA_CATALOG, ayanamsa_degrees

ROOT = Path(__file__).resolve().parents[1]


def test_native_and_optional_wasm_execute_identical_named_conventions(tmp_path):
    assert len(AYANAMSA_CATALOG) >= 27
    name = ("ephemeris_core.dll" if sys.platform == "win32" else
            "libephemeris_core.dylib" if sys.platform == "darwin" else "libephemeris_core.so")
    library = ctypes.CDLL(str(ROOT / "rust/ephemeris-core/target/release" / name))
    function = library.ephemeris_ayanamsa_v2
    function.argtypes = [ctypes.c_double, ctypes.c_uint32, ctypes.c_double]
    function.restype = ctypes.c_double
    cases = []
    for system, (key, definition) in enumerate(AYANAMSA_CATALOG.items()):
        for jd in (-3100015.5, 2300000., 2451545., 2600000., 8000016.5):
            kwargs = ({"anchor_tropical_longitude_deg": 203.84}
                      if definition.model in {"star_anchor", "polar_anchor"} else {})
            expected = ayanamsa_degrees(jd, key, **kwargs)
            anchor = kwargs.get("anchor_tropical_longitude_deg", math.nan)
            actual = function(jd, system, anchor)
            assert abs((actual - expected + 180.) % 360. - 180.) < 1e-10
            cases.append({"key": key, "jd": jd, "anchor": None if math.isnan(anchor) else anchor,
                          "expected": expected})
    assert math.isnan(function(2451545., 999999, math.nan))
    assert math.isnan(function(-3100016.5, 0, math.nan))
    assert math.isnan(function(2451545., 5, math.nan))
    fixture = tmp_path / "cases.json"
    fixture.write_text(json.dumps(cases), encoding="utf-8")
    script = tmp_path / "conventions.mjs"
    script.write_text("""
import fs from 'node:fs';
const sdk = await import(process.argv[2]);
await sdk.initEphemerisWasm(new Uint8Array(fs.readFileSync(process.argv[3])));
const cases = JSON.parse(fs.readFileSync(process.argv[4], 'utf8'));
for (let repeat=0; repeat<2; repeat++) {
  for (const c of cases) {
    const actual = sdk.computeAyanamsaLongTerm(c.jd, c.key,
      {anchorTropicalLongitudeDeg: c.anchor ?? undefined});
    const delta = ((actual-c.expected+540)%360)-180;
    if (!Number.isFinite(actual) || Math.abs(delta)>1e-10) throw new Error(JSON.stringify(c));
  }
}
for (const [jd,key,options] of [[2451545,'invented',{}],[-3100016.5,'lahiri',{}],
                               [2451545,'true_citra',{}]]) {
  let refused=false;
  try { sdk.computeAyanamsaLongTerm(jd,key,options); } catch { refused=true; }
  if (!refused) throw new Error('Invalid input was accepted');
}
console.log(JSON.stringify({cases:cases.length, repeats:2}));
""", encoding="utf-8")
    result = subprocess.run(["node", str(script), (ROOT / "web/ephemeris-browser.js").as_uri(),
                             str(ROOT / "rust/ephemeris-core/wasm/ephemeris_spk.wasm"),
                             str(fixture)], capture_output=True, text=True, check=True)
    assert json.loads(result.stdout) == {"cases": len(cases), "repeats": 2}
