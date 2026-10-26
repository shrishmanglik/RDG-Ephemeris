"""Generated long-term ayanamsa catalogs must remain byte-for-byte current."""

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "tools" / "generate_ayanamsa_catalog.py"


def _run_generator(rust_output: Path, js_output: Path, *, check: bool):
    command = [
        sys.executable,
        str(GENERATOR),
        "--rust-output",
        str(rust_output),
        "--js-output",
        str(js_output),
    ]
    if check:
        command.append("--check")
    return subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)


def test_check_accepts_current_bytes_and_rejects_one_byte_mutant(tmp_path):
    rust_output = tmp_path / "ayanamsa_catalog.rs"
    js_output = tmp_path / "ayanamsa-catalog.js"

    generated = _run_generator(rust_output, js_output, check=False)
    assert generated.returncode == 0, generated.stderr

    current = _run_generator(rust_output, js_output, check=True)
    assert current.returncode == 0, current.stderr
    assert "Convention data checked" in current.stdout

    mutant = bytearray(js_output.read_bytes())
    mutant[0] ^= 1
    js_output.write_bytes(mutant)

    stale = _run_generator(rust_output, js_output, check=True)
    assert stale.returncode != 0
    assert "Stale generated convention data" in stale.stderr
    assert js_output.name in stale.stderr
