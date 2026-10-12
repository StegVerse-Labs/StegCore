from __future__ import annotations

import pytest

from scripts.release.bump_version import bump


def test_release_bump_kinds_advance():
    assert bump("0.3.0", "patch") == "0.3.1"
    assert bump("0.3.0", "minor") == "0.4.0"
    assert bump("0.3.0", "major") == "1.0.0"


def test_explicit_successor_rejects_same_or_lower_without_mutating_repository(tmp_path, monkeypatch):
    from scripts.release import bump_version
    monkeypatch.chdir(tmp_path)
    (tmp_path / "VERSION").write_text("0.3.0\n")
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "stegcore"\nversion = "0.3.0"\n')
    source = tmp_path / "src/stegcore/version.py"
    source.parent.mkdir(parents=True)
    source.write_text('__version__ = "0.3.0"\n')
    monkeypatch.setattr("sys.argv", ["bump_version.py", "0.3.0"])
    with pytest.raises(SystemExit):
        bump_version.main()
    monkeypatch.setattr("sys.argv", ["bump_version.py", "0.2.9"])
    with pytest.raises(SystemExit):
        bump_version.main()
    assert (tmp_path / "VERSION").read_text() == "0.3.0\n"
    assert source.read_text() == '__version__ = "0.3.0"\n'
