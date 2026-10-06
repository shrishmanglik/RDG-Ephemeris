"""No copyleft module may be importable from the package.

Every module under ``ephemeris_oss`` is imported in a fresh interpreter whose
import system refuses the copyleft comparators. If any package module reaches
one, the import fails and so does this test. The planted case proves the
guard is live: a module that imports ``swisseph`` must be caught.
"""

from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
COPYLEFT = ("swisseph", "pyswisseph", "libephemeris", "kerykeion", "jhora", "sweph")

PROBE = textwrap.dedent(
    """
    import importlib, pkgutil, sys
    BLOCKED = {blocked!r}

    class Refuse:
        def find_spec(self, name, path=None, target=None):
            if name.split(".")[0] in BLOCKED:
                raise ImportError("copyleft module refused: " + name)
            return None

    sys.meta_path.insert(0, Refuse())
    sys.path.insert(0, {src!r})
    import {package} as root
    names = [root.__name__] + [m.name for m in pkgutil.walk_packages(root.__path__, root.__name__ + ".")]
    for name in names:
        importlib.import_module(name)
    leaked = sorted(m for m in sys.modules if m.split(".")[0] in BLOCKED)
    assert not leaked, leaked
    print(len(names))
    """
)


def _probe(src: Path, package: str) -> subprocess.CompletedProcess[str]:
    code = PROBE.format(blocked=COPYLEFT, src=str(src), package=package)
    return subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=120)


def test_every_package_module_imports_without_any_copyleft_module() -> None:
    result = _probe(SRC, "ephemeris_oss")
    assert result.returncode == 0, result.stderr
    assert int(result.stdout.strip()) >= 10


def test_guard_catches_a_planted_copyleft_import(tmp_path: Path) -> None:
    planted = tmp_path / "planted_pkg"
    planted.mkdir()
    (planted / "__init__.py").write_text("", encoding="utf-8")
    (planted / "leak.py").write_text("import swisseph\n", encoding="utf-8")
    result = _probe(tmp_path, "planted_pkg")
    assert result.returncode != 0
    assert "copyleft module refused: swisseph" in result.stderr
