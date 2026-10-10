"""Replay the preserved independent scorer against the installed package source.

The scorer is supplied explicitly and hashed. Its provider factory is replaced
with this package's provider; reference calculations and thresholds stay intact.
No reference data are downloaded during replay.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import os
import sys
from contextlib import contextmanager
from pathlib import Path

from ephemeris_oss import Engine


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scorer", type=Path, required=True)
    parser.add_argument("--kernel", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--horizons-dir", type=Path, required=True)
    args = parser.parse_args()
    scorer_path = args.scorer.resolve()
    spec = importlib.util.spec_from_file_location("independent_accuracy_scorer", scorer_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("independent scorer cannot be loaded")
    scorer = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = scorer
    spec.loader.exec_module(scorer)

    @contextmanager
    def package_provider(kernel: Path):
        with Engine.load(kernels={"DE440": kernel}, eop=None) as engine:
            yield engine._provider

    def package_source_digest():
        root = Path(__file__).resolve().parents[3] / "src"
        files = {}
        digest = hashlib.sha256()
        for path in sorted(root.rglob("*.py")):
            name = path.relative_to(root).as_posix()
            raw = path.read_bytes()
            files[name] = hashlib.sha256(raw).hexdigest()
            digest.update(name.encode() + b"\0" + raw)
        return {"sha256": digest.hexdigest(), "files": files,
                "scorer_sha256": hashlib.sha256(scorer_path.read_bytes()).hexdigest(),
                "adapter_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}

    scorer.provider = package_provider
    scorer.engine_source_digest = package_source_digest
    os.environ["E2_FETCH_HORIZONS"] = "0"
    return scorer.main(["--kernel", str(args.kernel), "--output", str(args.output),
                        "--horizons-dir", str(args.horizons_dir)])


if __name__ == "__main__":
    raise SystemExit(main())
