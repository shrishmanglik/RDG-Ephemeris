"""Build the native reader and both browser modules before repository tests."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CRATE = ROOT / "rust/ephemeris-core"


def main() -> None:
    cargo = shutil.which("cargo")
    if cargo is None:
        raise RuntimeError("Rust cargo is required to build the declared test inputs")
    subprocess.run([sys.executable, str(ROOT / "tools/generate_ayanamsa_catalog.py"), "--check"],
                   cwd=ROOT, check=True)
    command = [cargo, "build", "--release", "--manifest-path", str(CRATE / "Cargo.toml")]
    subprocess.run(command, cwd=ROOT, check=True)
    wasm_command = command + ["--target", "wasm32-unknown-unknown"]
    subprocess.run(wasm_command + ["--no-default-features"], cwd=ROOT, check=True)
    output = CRATE / "target/wasm32-unknown-unknown/release/ephemeris_core.wasm"
    math_bytes = output.read_bytes()
    subprocess.run(wasm_command + ["--features", "spk-reader"], cwd=ROOT, check=True)
    reader_bytes = output.read_bytes()
    if len(math_bytes) >= 65536:
        raise RuntimeError("Math-only WASM exceeds its existing 64 KiB budget")
    if any(data[:8] != b"\0asm\x01\0\0\0" for data in (math_bytes, reader_bytes)):
        raise RuntimeError("Build output is not WebAssembly version 1")
    # Publish neither module until both builds and the existing size gate pass.
    artifacts = {"ephemeris_core.wasm": math_bytes, "ephemeris_spk.wasm": reader_bytes}
    for name, data in artifacts.items():
        (CRATE / "wasm" / name).write_bytes(data)
    library = ("ephemeris_core.dll" if sys.platform == "win32" else
               "libephemeris_core.dylib" if sys.platform == "darwin" else "libephemeris_core.so")
    artifacts["native"] = (CRATE / "target/release" / library).read_bytes()
    print(json.dumps({name: {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
                      for name, data in artifacts.items()}, indent=2))


if __name__ == "__main__":
    main()
