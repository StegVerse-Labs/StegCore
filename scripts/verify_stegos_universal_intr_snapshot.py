#!/usr/bin/env python3
from __future__ import annotations

from hashlib import sha1
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "contracts/stegos_universal_intr_snapshot"


def git_blob_sha(raw: bytes) -> str:
    return sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def main() -> int:
    try:
        manifest = json.loads((SNAP / "manifest.json").read_text(encoding="utf-8"))
        if manifest.get("schema") != "stegcore.stegos-universal-intr-snapshot-manifest.v1":
            raise ValueError("snapshot manifest schema")
        if manifest.get("stegos_source_commit") != "500a9f07ae6fb6ec73ee41dc9842e55412425695":
            raise ValueError("unexpected StegOS source commit")
        if manifest.get("authority_effect") != "NONE_SNAPSHOT_ONLY":
            raise ValueError("snapshot authority effect")
        if manifest.get("stegos_authority_transferred") is not False:
            raise ValueError("snapshot cannot transfer StegOS authority")
        for entry in manifest.get("source_files", []):
            path = ROOT / entry["snapshot_path"]
            if git_blob_sha(path.read_bytes()) != entry["source_blob_sha"]:
                raise ValueError(f"snapshot blob mismatch: {path}")
        registry = json.loads(
            (SNAP / "specs/universal-intr-connector-profiles.v1.json").read_text(encoding="utf-8")
        )
        profile = next(
            p for p in registry["profiles"]
            if p["profile_id"] == "governance-external-action"
        )
        if profile["payload_schema"] != "stegverse.governance-connector.request/v1":
            raise ValueError("governance request payload schema binding")
        if profile["operations"] != ["GOVERN_ACTION"]:
            raise ValueError("governance operation binding")
        if profile["authorization_required"] is not True:
            raise ValueError("governance transport must require authorization")
        if profile["authority_effect"] != "NONE":
            raise ValueError("governance transport profile cannot grant authority")
    except Exception as exc:
        print(f"STEGOS_UNIVERSAL_INTR_SNAPSHOT: FAIL: {exc}")
        return 1
    print("STEGOS_UNIVERSAL_INTR_SNAPSHOT: PASS")
    print("stegos_commit=500a9f07ae6fb6ec73ee41dc9842e55412425695")
    print("profile=governance-external-action")
    print("authority_effect=NONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
