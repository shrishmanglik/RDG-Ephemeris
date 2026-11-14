import importlib.util
import io
from pathlib import Path
import tarfile
import zipfile

spec=importlib.util.spec_from_file_location("release_gate", Path(__file__).parents[1]/"tools/verify_release.py")
gate=importlib.util.module_from_spec(spec); spec.loader.exec_module(gate)

def test_release_gate_clean_and_private_control(tmp_path):
    def build(name, files):
        p=tmp_path/name
        with zipfile.ZipFile(p,"w") as z:
            for key,value in files.items():z.writestr(key,value)
        return p
    def build_sdist(name, files):
        p=tmp_path/name
        with tarfile.open(p,"w:gz") as t:
            for key,value in files.items():
                raw=value.encode("utf-8") if isinstance(value,str) else value
                info=tarfile.TarInfo(name=key); info.size=len(raw)
                t.addfile(info, io.BytesIO(raw))
        return p
    clean_meta="Metadata-Version: 2.1\nName: pkg\nRequires-Dist: jplephem>=2.21\nRequires-Dist: pytest>=8; extra == \"test\"\n"
    clean={"pkg/__init__.py":"VALUE=1", "pkg.dist-info/METADATA":clean_meta, "pkg.dist-info/licenses/LICENSE":"Apache-2.0", "pkg.dist-info/licenses/NOTICE":"Copyright owner"}
    clean_sdist={"pkg-0.0/pkg/__init__.py":"VALUE=1", "pkg-0.0/PKG-INFO":clean_meta, "pkg-0.0/LICENSE":"Apache-2.0", "pkg-0.0/NOTICE":"Copyright owner"}
    bad_specs=(
        'Requires-Dist: skyfield==1.55; extra == "test"',
        'Requires-Dist: ephem==4.2.1; extra == "test"',
        "Requires-Dist: ephem==4.2.1",
        'Requires-Dist: pyephem==4.2.1; extra == "test"',
    )
    for _ in range(2):
        assert gate.inspect(build("clean.whl",clean)) == []
        assert gate.inspect(build_sdist("clean.tar.gz",clean_sdist)) == []
        assert gate.inspect(build("private.whl",{**clean,"evidence/internal.txt":"private"}))
        assert gate.inspect(build("kernel.whl",{**clean,"pkg/input.bsp":"data"}))
        assert gate.inspect(build("identifier.whl",{**clean,"pkg/doc.txt":"the-last-" + "product"}))
        for idx, spec_line in enumerate(bad_specs):
            bad_meta=f"Metadata-Version: 2.1\nName: pkg\nRequires-Dist: jplephem>=2.21\n{spec_line}\n"
            assert gate.inspect(build(f"comparator_meta_{idx}.whl",{**clean,"pkg.dist-info/METADATA":bad_meta})), f"wheel gate missed {spec_line}"
            assert gate.inspect(build_sdist(f"comparator_meta_{idx}.tar.gz",{**clean_sdist,"pkg-0.0/PKG-INFO":bad_meta})), f"sdist gate missed {spec_line}"
