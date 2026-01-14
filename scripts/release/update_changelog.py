#!/usr/bin/env python3
"""
Update CHANGELOG.md by moving items from [Unreleased] into a new version section.

Workflow-friendly: pass version and a short summary.

Usage:
  python scripts/release/update_changelog.py 0.1.1 "Emergency governance v0.1 specs"
"""

from __future__ import annotations
import sys
from pathlib import Path
from datetime import date

CHANGELOG = Path("CHANGELOG.md")

def die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)

def main() -> None:
    if len(sys.argv) < 3:
        die("Usage: update_changelog.py <version> <summary text>")

    version = sys.argv[1].strip()
    summary = " ".join(sys.argv[2:]).strip()

    if not CHANGELOG.exists():
        die("CHANGELOG.md not found at repo root.")

    text = CHANGELOG.read_text(encoding="utf-8")

    marker = "## [Unreleased]"
    idx = text.find(marker)
    if idx == -1:
        die("CHANGELOG.md missing '## [Unreleased]' section.")

    # Insert a new version section right after Unreleased block header line
    # We keep Unreleased in place, but we also add a release entry below it.
    insert_after = idx + len(marker)

    new_section = (
        f"\n\n---\n\n"
        f"## [{version}] - {date.today().isoformat()}\n\n"
        f"### Added\n"
        f"- {summary}\n"
    )

    updated = text[:insert_after] + new_section + text[insert_after:]
    CHANGELOG.write_text(updated, encoding="utf-8")
    print(f"Updated CHANGELOG.md with version {version}")

if __name__ == "__main__":
    main()
