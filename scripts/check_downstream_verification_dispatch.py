#!/usr/bin/env python3
"""Validate the bounded cross-repository verification dispatch."""
from __future__ import annotations

import argparse
import json
import pathlib

EXPECTED = {
    "StegVerse-Labs/Site": (14, "docs/SITE_MIRROR_HANDOFF.md"),
    "GCAT-BCAT-Engine/Publisher": (4, "PUBLISHER_MIRROR_HANDOFF.md"),
    "StegVerse-Labs/admissibility-wiki": (19, "docs/ADMISSIBILITY_WIKI_MIRROR_HANDOFF.md"),
    "StegVerse-002/stegguardian-wiki": (4, "STEGGUARDIAN_WIKI_MIRROR_HANDOFF.md"),
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=pathlib.Path)
    args = parser.parse_args()

    try:
        data = json.loads(args.path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Invalid dispatch: {exc}")
        return 1

    errors: list[str] = []
    if not isinstance(data, dict):
        return 1
    if data.get("artifact_type") != "stegcore.downstream_verification_dispatch":
        errors.append("artifact_type is invalid")
    if data.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    if data.get("state") != "queued_not_completed":
        errors.append("state must remain queued_not_completed")

    authority = data.get("authority_boundary")
    if not isinstance(authority, dict):
        errors.append("authority_boundary must be an object")
    else:
        for key in (
            "deployment_authority_granted",
            "execution_authority_granted",
            "release_authority_granted",
            "cross_repository_mutation_authority_granted",
        ):
            if authority.get(key) is not False:
                errors.append(f"authority_boundary.{key} must be false")

    destinations = data.get("destinations")
    observed: dict[str, tuple[int, str]] = {}
    if not isinstance(destinations, list):
        errors.append("destinations must be a list")
    else:
        for item in destinations:
            if not isinstance(item, dict):
                errors.append("destination entries must be objects")
                continue
            repo = item.get("repository")
            number = item.get("issue_number")
            handoff = item.get("handoff")
            if isinstance(repo, str) and isinstance(number, int) and isinstance(handoff, str):
                observed[repo] = (number, handoff)
            if item.get("required") is not True:
                errors.append(f"{repo}: required must be true")
            if item.get("state") != "queued":
                errors.append(f"{repo}: state must be queued")
            expected_url = f"https://github.com/{repo}/issues/{number}"
            if item.get("issue_url") != expected_url:
                errors.append(f"{repo}: issue_url must be {expected_url}")
            if not isinstance(item.get("scope"), str) or not item.get("scope", "").strip():
                errors.append(f"{repo}: scope is required")
        if observed != EXPECTED:
            errors.append("destination repository, issue, or handoff mapping is incorrect")

    if errors:
        print("Downstream verification dispatch check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Downstream verification dispatch check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
