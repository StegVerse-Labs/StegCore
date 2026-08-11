#!/usr/bin/env python3
"""Promote the current Unreleased changelog body into one versioned section.

Usage:
  python scripts/release/update_changelog.py 0.2.1 "Short release summary"
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
import re
import sys

CHANGELOG = Path("CHANGELOG.md")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


def die(message: str, code: int = 1) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def main() -> None:
    if len(sys.argv) < 3:
        die("usage: update_changelog.py <version> <summary text>")

    version = sys.argv[1].strip()
    summary = " ".join(sys.argv[2:]).strip()
    if not SEMVER_RE.fullmatch(version):
        die(f"invalid semver: {version}")
    if not summary:
        die("release summary must not be empty")
    if not CHANGELOG.exists():
        die("CHANGELOG.md not found at repository root")

    text = CHANGELOG.read_text(encoding="utf-8")
    if f"## [{version}]" in text:
        die(f"CHANGELOG.md already contains version {version}")

    marker = "## [Unreleased]"
    start = text.find(marker)
    if start == -1:
        die("CHANGELOG.md missing '## [Unreleased]' section")

    body_start = start + len(marker)
    next_heading = text.find("\n## [", body_start)
    if next_heading == -1:
        next_heading = len(text)

    unreleased_body = text[body_start:next_heading].strip()
    release_body = unreleased_body if unreleased_body else "### Changed\n- No categorized unreleased entries were recorded."
    release_body += f"\n\n### Release summary\n- {summary}"

    replacement = (
        "## [Unreleased]\n\n"
        f"## [{version}] - {date.today().isoformat()}\n\n"
        f"{release_body}\n"
    )
    updated = text[:start] + replacement + text[next_heading:]
    CHANGELOG.write_text(updated, encoding="utf-8")
    print(f"Promoted Unreleased changelog entries to {version}")


if __name__ == "__main__":
    main()
