#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
from datetime import datetime, timezone
from typing import Any

FORBIDDEN_ENV = (
    "GITHUB_TOKEN",
    "GH_TOKEN",
    "GITHUB_PAT",
    "TVC_EPHEMERAL_GITHUB_TOKEN",
)

DEFAULT_COMMANDS = (
    "python3 -m pytest -q tests/test_manifest_capability_context.py",
    "python3 -m pytest -q tests/test_transaction_lifecycle.py tests/test_manifest_receipts.py tests/test_manifest_receipt_provider.py",
    "python3 -m pytest -q",
    "python3 scripts/verify_product_consistency.py",
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit("MATERIALIZATION_RECEIPT_NOT_OBJECT")
    return value


def validate_materialization_receipt(path: Path, root: Path, expected_head: str) -> dict[str, Any]:
    receipt = load_json(path)
    if receipt.get("credential_authority") != "TV/TVC":
        raise SystemExit("MATERIALIZATION_CREDENTIAL_AUTHORITY_INVALID")
    if receipt.get("consumer_credential_present") is not False:
        raise SystemExit("MATERIALIZATION_CONSUMER_CREDENTIAL_PRESENT")
    if receipt.get("credential_value_exposed") is not False:
        raise SystemExit("MATERIALIZATION_CREDENTIAL_VALUE_EXPOSED")
    if receipt.get("non_tv_tvc_secret_or_token_used") is not False:
        raise SystemExit("MATERIALIZATION_NON_TV_TVC_SECRET_USED")
    result = receipt.get("result")
    if not isinstance(result, dict) or result.get("status") != "MATERIALIZED":
        raise SystemExit("MATERIALIZATION_RESULT_INVALID")
    if result.get("repository") != "StegVerse-Labs/StegCore":
        raise SystemExit("MATERIALIZATION_REPOSITORY_MISMATCH")
    if result.get("commit_sha") != expected_head:
        raise SystemExit("MATERIALIZATION_SOURCE_IDENTITY_MISMATCH")
    destination = Path(str(result.get("destination") or "")).expanduser().resolve()
    if destination != root.resolve():
        raise SystemExit("MATERIALIZATION_DESTINATION_MISMATCH")
    archive_sha = result.get("archive_sha256")
    if not isinstance(archive_sha, str) or len(archive_sha) != 64:
        raise SystemExit("MATERIALIZATION_ARCHIVE_HASH_INVALID")
    return receipt


def discover_source(explicit: str | None, expected_head: str, materialization_receipt: str | None) -> tuple[Path, str, dict[str, Any] | None]:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit).expanduser())
    env_root = os.environ.get("STEGVERSE_STEGCORE_SOURCE_ROOT")
    if env_root:
        candidates.append(Path(env_root).expanduser())
    candidates.extend(
        [
            Path.cwd(),
            Path.home() / ".stegverse" / "repos" / "StegVerse-Labs" / "StegCore",
            Path("/var/lib/stegverse/source/StegVerse-Labs/StegCore") / expected_head,
            Path("/srv/stegverse/repos/StegVerse-Labs/StegCore"),
            Path("/opt/stegverse/repos/StegVerse-Labs/StegCore"),
        ]
    )

    receipt_path = Path(materialization_receipt).expanduser().resolve() if materialization_receipt else None
    for candidate in candidates:
        candidate = candidate.resolve()
        if not (candidate / "pyproject.toml").exists() or not (candidate / "src/stegcore").exists():
            continue

        if (candidate / ".git").exists():
            actual_head = git(candidate, "rev-parse", "HEAD")
            if actual_head != expected_head:
                continue
            dirty = git(candidate, "status", "--porcelain")
            if dirty:
                raise SystemExit("SOURCE_WORKTREE_NOT_CLEAN")
            return candidate, "STEGVERSE_CONTROLLED_GIT_WORKTREE", None

        if receipt_path and receipt_path.is_file():
            receipt = validate_materialization_receipt(receipt_path, candidate, expected_head)
            return candidate, "TVC_MATERIALIZED_SOURCE_ARCHIVE", receipt

    raise SystemExit("SOVEREIGN_SOURCE_NOT_MATERIALIZED")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root")
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--materialization-receipt")
    parser.add_argument("--receipt-out", default="validation/sovereign-validation.latest.json")
    args = parser.parse_args()

    for name in FORBIDDEN_ENV:
        if os.environ.get(name):
            raise SystemExit(f"forbidden credential environment variable present: {name}")

    root, source_mode, materialization = discover_source(
        args.source_root,
        args.expected_head,
        args.materialization_receipt,
    )

    results: list[dict[str, object]] = []
    overall = "PASS"
    for command in DEFAULT_COMMANDS:
        proc = subprocess.run(command, cwd=root, shell=True, text=True, capture_output=True)
        combined = (proc.stdout or "") + (proc.stderr or "")
        results.append(
            {
                "command": command,
                "exit_code": proc.returncode,
                "output_sha256": sha256_text(combined),
                "output_tail": combined[-12000:],
            }
        )
        if proc.returncode != 0:
            overall = "FAIL"
            break

    receipt = {
        "schema": "stegcore.sovereign-validation/v1",
        "created_at": now(),
        "repository": "StegVerse-Labs/StegCore",
        "source_root": str(root),
        "source_head": args.expected_head,
        "expected_head": args.expected_head,
        "credential_authority": "TV/TVC",
        "non_tv_tvc_secret_or_token_used": False,
        "github_token_required": False,
        "render_required": False,
        "source_materialization": source_mode,
        "materialization_receipt_hash": (
            sha256_text(json.dumps(materialization, sort_keys=True, separators=(",", ":")))
            if materialization is not None
            else None
        ),
        "validation_result": overall,
        "commands": results,
    }
    receipt["receipt_sha256"] = sha256_text(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    out = root / args.receipt_out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
