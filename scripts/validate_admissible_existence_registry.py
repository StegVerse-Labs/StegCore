from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

DEFAULT_REGISTRY = Path("management/admissible-existence-capability-registry.json")
PHASES_REQUIRING_STANDING = {"STANDING", "ADMISSIBLE", "ACTIVATED", "SUSPENDED", "SUPERSEDED", "TERMINATED"}
PHASES_REQUIRING_ADMISSIBILITY = {"ADMISSIBLE", "ACTIVATED", "SUSPENDED", "SUPERSEDED", "TERMINATED"}
PHASES_REQUIRING_ACTIVATION = {"ACTIVATED", "SUSPENDED", "SUPERSEDED"}


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validate_registry(data: dict[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    seen_hashes: set[str] = set()
    entries = data.get("entries") or []

    for entry in entries:
        declaration = entry.get("declaration") or {}
        capability_id = str(declaration.get("capability_id") or "")
        existence_hash = str(entry.get("existence_hash") or "")
        expected_hash = canonical_sha256(declaration)
        phase = entry.get("phase")
        evidence = entry.get("evidence") or {}
        authority = declaration.get("authority") or {}

        def add(code: str, detail: str) -> None:
            findings.append({"capability_id": capability_id, "code": code, "detail": detail})

        if not capability_id:
            add("capability_id_missing", "capability_id is required")
        elif capability_id in seen_ids:
            add("duplicate_capability_id", "capability_id must be unique")
        seen_ids.add(capability_id)

        if existence_hash in seen_hashes:
            add("duplicate_existence_hash", "existence_hash must be unique")
        seen_hashes.add(existence_hash)

        if existence_hash != expected_hash:
            add("existence_hash_mismatch", f"expected {expected_hash}")

        if authority.get("credential_authority") != "TV/TVC":
            add("credential_authority_mismatch", "credential authority must be TV/TVC")
        if authority.get("github_token_runtime_authority") is not False:
            add("github_token_runtime_authority", "GitHub token runtime authority must be false")

        if phase in PHASES_REQUIRING_STANDING and not evidence.get("standing_evidence_refs"):
            add("standing_evidence_missing", "phase requires standing evidence")
        if phase in PHASES_REQUIRING_ADMISSIBILITY and not evidence.get("admissibility_evidence_refs"):
            add("admissibility_evidence_missing", "phase requires admissibility evidence")
        if phase in PHASES_REQUIRING_ACTIVATION:
            if not evidence.get("integration_evidence_refs"):
                add("integration_evidence_missing", "activated lineage requires integration evidence")
            if not evidence.get("activation_proof_ref"):
                add("activation_proof_missing", "activated lineage requires an activation proof")
        if phase == "ACTIVATED" and evidence.get("blockers"):
            add("activated_with_open_blockers", "ACTIVATED cannot retain unresolved activation blockers")
        if phase == "ADMISSIBLE" and evidence.get("blockers") and not evidence.get("continuation_owner"):
            add("blocked_admissible_without_owner", "blocked ADMISSIBLE capability requires a continuation owner")

    return {
        "artifact_type": "stegcore.capability_existence_registry_validation",
        "schema_version": "1.0",
        "valid": not findings,
        "entry_count": len(entries),
        "findings": findings,
        "credential_authority": "TV/TVC",
        "github_token_runtime_authority": "NONE",
        "runtime_dependencies_required": [],
    }


def main() -> int:
    data = json.loads(DEFAULT_REGISTRY.read_text(encoding="utf-8"))
    result = validate_registry(data)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
