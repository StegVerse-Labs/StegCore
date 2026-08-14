#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / ".github/workflows/stegcore-tests.yml",
    ROOT / ".github/workflows/runtime-tests.yml",
    ROOT / ".github/workflows/bcat-gate.yml",
    ROOT / ".github/workflows/test-readiness.yml",
    ROOT / ".github/workflows/stegverse-001-002-validator.yml",
]

FORBIDDEN = (
    "uses:",
    "${{ github.token }}",
    "${{github.token}}",
    "secrets.",
    "persist-credentials:",
    "Authorization:",
    "AUTHORIZATION:",
)


def validate_text(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    if "permissions: {}" not in text:
        errors.append(f"{path.name}: permissions must be empty")
    if "Anonymous public repository fetch" not in text:
        errors.append(f"{path.name}: anonymous fetch step missing")
    if "Assert credential-clean validation environment" not in text:
        errors.append(f"{path.name}: credential absence assertion missing")
    for marker in FORBIDDEN:
        if marker in text:
            errors.append(f"{path.name}: forbidden credential/action marker: {marker}")
    if "https://github.com/${GITHUB_REPOSITORY}.git" not in text:
        errors.append(f"{path.name}: anonymous origin URL missing")
    if "credential.helper=" not in text or "http.extraheader=" not in text:
        errors.append(f"{path.name}: anonymous git credential/header suppression missing")
    return errors


def main() -> int:
    errors: list[str] = []
    for path in TARGETS:
        if not path.is_file():
            errors.append(f"missing target workflow: {path.relative_to(ROOT)}")
            continue
        errors.extend(validate_text(path, path.read_text(encoding="utf-8")))
    if errors:
        print("STEGCORE_NO_NON_TVTVC_VALIDATION_CREDENTIALS=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("STEGCORE_NO_NON_TVTVC_VALIDATION_CREDENTIALS=PASS")
    print(f"validated_workflows={len(TARGETS)}")
    print("credential_authority=TV/TVC")
    print("non_tv_tvc_secret_or_token_allowed=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
