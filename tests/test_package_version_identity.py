from pathlib import Path
import tomllib


# Release-candidate identity is intentionally checked alongside canonical standing/interlock tests.
def test_successor_release_candidate_is_exact_0_3_0_identity():
    root = Path(__file__).resolve().parents[1]
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert project["name"] == "stegcore"
    assert project["version"] == "0.3.0"
    assert (root / "VERSION").read_text(encoding="utf-8").strip() == "0.3.0"

    version_ns = {}
    exec((root / "src" / "stegcore" / "version.py").read_text(encoding="utf-8"), version_ns)
    assert version_ns["__version__"] == "0.3.0"


def test_0_3_release_candidate_contains_standing_and_interlock_sources():
    root = Path(__file__).resolve().parents[1]
    assert (root / "src" / "stegcore" / "standing_binding.py").is_file()
    assert (root / "src" / "stegcore" / "steggate_runtime.py").is_file()
    assert (root / "tests" / "test_spe_standing_binding.py").is_file()
    assert (root / "tests" / "test_portable_interlock_bounded_traversal.py").is_file()
