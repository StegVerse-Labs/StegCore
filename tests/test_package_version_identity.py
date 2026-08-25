from pathlib import Path
import tomllib


def test_release_candidate_is_distinct_from_frozen_0_2_identity():
    root = Path(__file__).resolve().parents[1]
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert project["name"] == "stegcore"
    assert project["version"] == "0.3.0"
    assert project["version"] != "0.2.0"


def test_0_3_candidate_contains_standing_and_interlock_sources():
    root = Path(__file__).resolve().parents[1]
    assert (root / "src" / "stegcore" / "standing_binding.py").is_file()
    assert (root / "src" / "stegcore" / "steggate_runtime.py").is_file()
    assert (root / "tests" / "test_spe_standing_binding.py").is_file()
