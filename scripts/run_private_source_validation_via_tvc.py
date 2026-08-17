#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import subprocess
import time
import uuid

FORBIDDEN_ENV = (
    "GITHUB_TOKEN",
    "GH_TOKEN",
    "GITHUB_PAT",
    "TVC_EPHEMERAL_GITHUB_TOKEN",
)


def now() -> datetime:
    return datetime.now(timezone.utc)


def iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def default_spool() -> Path:
    override = os.environ.get("STEGVERSE_FORMALISM_TVC_SPOOL_ROOT", "").strip()
    return Path(override or "~/.stegverse/transport/formalism-tvc-repository").expanduser().resolve()


def validate_head(value: str) -> str:
    value = value.strip().lower()
    if len(value) != 40 or any(ch not in "0123456789abcdef" for ch in value):
        raise SystemExit("EXPECTED_HEAD_INVALID")
    return value


def validate_receipt(path: Path, expected_head: str, destination: Path) -> None:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["credential_authority"] == "TV/TVC"
    assert value["consumer_credential_present"] is False
    assert value["credential_value_exposed"] is False
    assert value["non_tv_tvc_secret_or_token_used"] is False
    result = value["result"]
    assert result["status"] == "MATERIALIZED"
    assert result["repository"] == "StegVerse-Labs/StegCore"
    assert result["commit_sha"].lower() == expected_head
    assert Path(result["destination"]).resolve() == destination.resolve()
    archive_hash = result["archive_sha256"]
    assert isinstance(archive_hash, str) and len(archive_hash) == 64


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Request exact private StegCore source from TVC and run credential-free sovereign validation."
    )
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--source-ref", required=True)
    parser.add_argument("--spool-root")
    parser.add_argument("--materialization-root", default="/var/lib/stegverse/source")
    parser.add_argument("--timeout-seconds", type=int, default=360)
    parser.add_argument("--receipt-out", default="validation/sovereign-validation.latest.json")
    args = parser.parse_args()

    for name in FORBIDDEN_ENV:
        if os.environ.get(name):
            raise SystemExit(f"forbidden credential environment variable present: {name}")

    expected_head = validate_head(args.expected_head)
    source_ref = args.source_ref.strip()
    if not source_ref or source_ref.startswith("-") or ".." in source_ref:
        raise SystemExit("SOURCE_REF_INVALID")

    spool = Path(args.spool_root).expanduser().resolve() if args.spool_root else default_spool()
    materialization_root = Path(args.materialization_root).expanduser().resolve()
    destination = materialization_root / "StegVerse-Labs" / "StegCore" / expected_head
    operation_id = f"stegcore-private-source-{expected_head[:16]}-{uuid.uuid4().hex[:12]}"
    outbox = spool / "outbox"
    inbox = spool / "inbox"
    outbox.mkdir(parents=True, exist_ok=True)
    inbox.mkdir(parents=True, exist_ok=True)
    request_path = outbox / f"{operation_id}.json"
    receipt_path = inbox / f"{operation_id}.json"

    issued = now()
    warrant = {
        "schema": "stegverse.tvc-github-repository-operation-warrant/v0.1",
        "operation_id": operation_id,
        "operation_class": "MATERIALIZE_SOURCE_ARCHIVE",
        "repository": "StegVerse-Labs/StegCore",
        "base_ref": source_ref,
        "expected_base_sha": expected_head,
        "destination_identity": str(destination),
        "maximum_total_bytes": 50_000_000,
        "credential_authority": "TV/TVC",
        "consumer_credential_present": False,
        "secret_values_present": False,
        "single_use": True,
        "issued_at": iso(issued),
        "expires_at": iso(issued + timedelta(minutes=15)),
        "nonce": uuid.uuid4().hex,
        "authorization_ref": f"tvc://spool/stegcore-private-source/{operation_id}",
    }
    request_path.write_text(json.dumps(warrant, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"TVC_SOURCE_MATERIALIZATION_REQUEST={request_path}")
    print("consumer_credential_present=false")
    print("credential_authority=TV/TVC")

    deadline = time.monotonic() + max(1, args.timeout_seconds)
    while not receipt_path.is_file() and time.monotonic() < deadline:
        time.sleep(1)
    if not receipt_path.is_file():
        print(f"TVC_SOURCE_MATERIALIZATION_PENDING={request_path}")
        return 2

    validate_receipt(receipt_path, expected_head, destination)
    if not (destination / "pyproject.toml").is_file() or not (destination / "src/stegcore").is_dir():
        raise SystemExit("MATERIALIZED_SOURCE_INCOMPLETE")

    command = [
        "python3",
        str(destination / "scripts/run_sovereign_validation.py"),
        "--source-root",
        str(destination),
        "--expected-head",
        expected_head,
        "--materialization-receipt",
        str(receipt_path),
        "--receipt-out",
        args.receipt_out,
    ]
    completed = subprocess.run(command, cwd=destination)
    print(f"SOVEREIGN_VALIDATION_EXIT_CODE={completed.returncode}")
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
