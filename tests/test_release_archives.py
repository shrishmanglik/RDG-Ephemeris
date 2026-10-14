import importlib.util
from pathlib import Path
import zipfile

spec=importlib.util.spec_from_file_location("release_gate", Path(__file__).parents[1]/"tools/verify_release.py")
gate=importlib.util.module_from_spec(spec); spec.loader.exec_module(gate)

def test_release_gate_clean_and_private_control(tmp_path):
    def build(name, files):
        p=tmp_path/name
        with zipfile.ZipFile(p,"w") as z:
            for key,value in files.items():z.writestr(key,value)
        return p
    clean={"pkg/__init__.py":"VALUE=1", "pkg.dist-info/licenses/LICENSE":"Apache-2.0", "pkg.dist-info/licenses/NOTICE":"Copyright owner"}
    for _ in range(2):
        assert gate.inspect(build("clean.whl",clean)) == []
        assert gate.inspect(build("private.whl",{**clean,"evidence/internal.txt":"private"}))
        assert gate.inspect(build("kernel.whl",{**clean,"pkg/input.bsp":"data"}))
        assert gate.inspect(build("identifier.whl",{**clean,"pkg/doc.txt":"the-last-" + "product"}))
