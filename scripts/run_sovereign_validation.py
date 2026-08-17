#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

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


def discover_source(explicit: str | None) -> Path:
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
            Path("/srv/stegverse/repos/StegVerse-Labs/StegCore"),
            Path("/opt/stegverse/repos/StegVerse-Labs/StegCore"),
        ]
    )
    for candidate in candidates:
        if (candidate / ".git").exists() and (candidate / "pyproject.toml").exists():
            try:
                remote = git(candidate, "config", "--get", "remote.origin.url")
            except subprocess.CalledProcessError:
                remote = ""
            if "StegCore" in remote or (candidate / "src/stegcore").exists():
                return candidate.resolve()
    raise RuntimeError("SOVEREIGN_SOURCE_NOT_MATERIALIZED")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root")
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--receipt-out", default="validation/sovereign-validation.latest.json")
    args = parser.parse_args()

    for name in FORBIDDEN_ENV:
        if os.environ.get(name):
            raise SystemExit(f"forbidden credential environment variable present: {name}")

    root = discover_source(args.source_root)
    actual_head = git(root, "rev-parse", "HEAD")
    if actual_head != args.expected_head:
        raise SystemExit(f"SOURCE_IDENTITY_MISMATCH expected={args.expected_head} actual={actual_head}")

    dirty = git(root, "status", "--porcelain")
    if dirty:
        raise SystemExit("SOURCE_WORKTREE_NOT_CLEAN")

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
        "source_head": actual_head,
        "expected_head": args.expected_head,
        "credential_authority": "TV/TVC",
        "non_tv_tvc_secret_or_token_used": False,
        "github_token_required": False,
        "render_required": False,
        "source_materialization": "PREEXISTING_STEGVERSE_CONTROLLED_LOCAL_SOURCE",
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
