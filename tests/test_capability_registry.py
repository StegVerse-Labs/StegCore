from pathlib import Path

from stegcore.capability_registry import (
    CapabilityExistenceRegistry,
    load_capability_registry,
    validate_capability_registry,
)


REGISTRY = Path("management/admissible-existence-capability-registry.json")


def test_canonical_registry_validates():
    registry = load_capability_registry(REGISTRY)
    result = validate_capability_registry(registry)
    assert result.valid is True
    assert result.entry_count >= 2
    assert result.findings == []


def test_local_model_is_not_falsely_marked_activated():
    registry = load_capability_registry(REGISTRY)
    entry = next(
        item
        for item in registry.entries
        if item.declaration.capability_id == "stegverse:capability:sovereign-local-model:v1"
    )
    assert entry.phase == "ADMISSIBLE"
    assert entry.evidence.activation_proof_ref is None
    assert entry.evidence.blockers
    assert entry.evidence.continuation_owner


def test_activated_phase_requires_activation_evidence():
    registry = load_capability_registry(REGISTRY)
    data = registry.model_dump(mode="json")
    data["entries"][1]["phase"] = "ACTIVATED"
    data["entries"][1]["evidence"]["blockers"] = []
    invalid = CapabilityExistenceRegistry.model_validate(data)
    result = validate_capability_registry(invalid)
    codes = {finding.code for finding in result.findings}
    assert "integration_evidence_missing" in codes
    assert "activation_proof_missing" in codes


def test_registry_hashes_are_bound_to_declarations():
    registry = load_capability_registry(REGISTRY)
    data = registry.model_dump(mode="json")
    data["entries"][0]["existence_hash"] = "0" * 64
    invalid = CapabilityExistenceRegistry.model_validate(data)
    result = validate_capability_registry(invalid)
    assert any(finding.code == "existence_hash_mismatch" for finding in result.findings)
