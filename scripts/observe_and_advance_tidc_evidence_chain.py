#!/usr/bin/env python3
"""Observe the TIDC evidence chain and emit the next executable task set.

This script never treats a missing upstream artifact as a reason to stop all work.
It distinguishes blocked dependency tasks from parallel-ready development tasks.
"""
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SITE_REPO = "StegVerse-Labs/Site"
STECORE_REPO = "StegVerse-Labs/StegCore"
RETURN_PREFIX = "data/tidc/blinded-coding/returns/"
RESULT_PREFIX = "data/tidc/blinded-coding/results/"
REQUIRED_SITE_PATHS = [
    "data/tidc/blinded-coding/BCP-2026-07-27-01.md",
    "scripts/validate_tidc_blinded_return.py",
    "scripts/create_tidc_blinded_return_receipt.py",
    "scripts/compare_tidc_blinded_coding.py",
    "docs/TIDC_BLINDED_CODING_ADJUDICATION_PROTOCOL.md",
    ".github/workflows/check-tidc-research.yml",
]
PARALLEL_TASKS = [
    {
        "id": "TIDC-PAR-001",
        "owner_repo": "StegVerse-Labs/Site",
        "location": "data/tidc/source-expansion/",
        "task": "Expand primary-source records for the ten seed events without recoding them.",
    },
    {
        "id": "TIDC-PAR-002",
        "owner_repo": "StegVerse-Labs/Site",
        "location": "data/tidc/negative-controls/",
        "task": "Build negative-control and placebo-event records under non-confirmatory posture.",
    },
    {
        "id": "TIDC-PAR-003",
        "owner_repo": "StegVerse-Labs/Site",
        "location": "data/tidc/tranche-02/",
        "task": "Prepare the next event tranche and split aggregate events while preserving tranche 01.",
    },
    {
        "id": "TIDC-PAR-004",
        "owner_repo": "StegVerse-Labs/StegCore",
        "location": "brain_reports/tidc_evidence_chain_observation.json",
        "task": "Continuously observe Site evidence state and emit next executable tasks.",
    },
]


def api(path: str, token: str | None) -> Any:
    request = urllib.request.Request(f"https://api.github.com{path}")
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise


def list_directory(repo: str, path: str, token: str | None) -> list[dict[str, Any]]:
    value = api(f"/repos/{repo}/contents/{path}", token)
    return value if isinstance(value, list) else []


def path_exists(repo: str, path: str, token: str | None) -> bool:
    return api(f"/repos/{repo}/contents/{path}", token) is not None


def observe(token: str | None) -> dict[str, Any]:
    missing_required = [path for path in REQUIRED_SITE_PATHS if not path_exists(SITE_REPO, path, token)]
    returns = [item for item in list_directory(SITE_REPO, RETURN_PREFIX.rstrip("/"), token) if item.get("name", "").endswith(".json")]
    results = [item for item in list_directory(SITE_REPO, RESULT_PREFIX.rstrip("/"), token) if item.get("type") == "file"]

    return_present = bool(returns)
    receipt_present = any("receipt" in item.get("name", "") for item in results)
    comparison_json_present = any("comparison" in item.get("name", "") and item.get("name", "").endswith(".json") for item in results)
    comparison_md_present = any("comparison" in item.get("name", "") and item.get("name", "").endswith(".md") for item in results)
    adjudication_present = any("adjudication" in item.get("name", "") for item in results)

    chain = [
        ("SITE_CONTRACT_READY", not missing_required),
        ("RETURN_PRESERVED", return_present),
        ("RECEIPT_PRESERVED", receipt_present),
        ("COMPARISON_JSON_PRESERVED", comparison_json_present),
        ("COMPARISON_MD_PRESERVED", comparison_md_present),
        ("ADJUDICATION_RECORDS_PRESENT", adjudication_present),
    ]
    first_incomplete = next((name for name, complete in chain if not complete), None)

    executable: list[dict[str, Any]] = []
    if missing_required:
        executable.append({
            "id": "TIDC-RECOVER-001",
            "owner_repo": SITE_REPO,
            "location": missing_required,
            "task": "Restore missing Site evidence-chain contract files.",
        })
    elif return_present and not receipt_present:
        executable.append({
            "id": "TIDC-ADV-001",
            "owner_repo": SITE_REPO,
            "location": "scripts/create_tidc_blinded_return_receipt.py",
            "task": "Validate the preserved return and generate its integrity receipt.",
        })
    elif receipt_present and not (comparison_json_present and comparison_md_present):
        executable.append({
            "id": "TIDC-ADV-002",
            "owner_repo": SITE_REPO,
            "location": "scripts/compare_tidc_blinded_coding.py",
            "task": "Generate and preserve JSON and Markdown comparison results.",
        })
    elif comparison_json_present and comparison_md_present and not adjudication_present:
        executable.append({
            "id": "TIDC-ADV-003",
            "owner_repo": SITE_REPO,
            "location": "data/tidc/blinded-coding/results/",
            "task": "Create one governed adjudication status record for every disagreement.",
        })

    # These tasks remain executable regardless of the current serial dependency.
    executable.extend(PARALLEL_TASKS)

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return {
        "schema": "stegverse.stegcore.tidc_evidence_chain_observation.v0.1",
        "observed_at": now,
        "source_repo": SITE_REPO,
        "management_repo": STECORE_REPO,
        "serial_chain": [{"state": name, "complete": complete} for name, complete in chain],
        "first_incomplete_state": first_incomplete,
        "missing_required_paths": missing_required,
        "return_files": [item.get("path") for item in returns],
        "result_files": [item.get("path") for item in results],
        "development_halted": False,
        "halt_prevention_rule": "A blocked serial dependency cannot suppress unrelated or preparatory executable tasks.",
        "next_executable_tasks": executable,
        "archive_ready": all(complete for _, complete in chain),
        "authority_effect": "NONE",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("brain_reports/tidc_evidence_chain_observation.json"))
    args = parser.parse_args()
    report = observe(os.environ.get("GITHUB_TOKEN"))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("TIDC_EVIDENCE_CHAIN_OBSERVED")
    print(f"first_incomplete={report['first_incomplete_state']}")
    print(f"next_tasks={len(report['next_executable_tasks'])}")
    print("development_halted=false")


if __name__ == "__main__":
    main()
