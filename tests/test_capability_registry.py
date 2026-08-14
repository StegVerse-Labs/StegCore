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
    assert result.entry_count >= 8
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
    assert entry.evidence.blockers == ["CONTROL_PLANE_LOCAL_MODEL_ROUTE_ACTIVATION_PROOF_NOT_YET_OBSERVED"]
    assert entry.evidence.continuation_owner


def test_formalism_source_generation_is_declared_and_non_authorizing():
    registry = load_capability_registry(REGISTRY)
    entries = {item.declaration.capability_id: item for item in registry.entries}
    entry = entries["stegverse:capability:formalism-source-generation:v1"]
    assert entry.phase == "DECLARED"
    assert entry.existence_hash == "5d6c4976e69fa958ddacc417195a9c8604a79931fbe0689a3e469e34064690ca"
    assert entry.declaration.owner_repository == "StegVerse-Labs/.github"
    assert entry.declaration.dependencies == [
        "stegverse:capability:steggate:canonical:v1",
        "stegverse:capability:sovereign-local-model:v1",
    ]
    assert entry.declaration.authority.credential_authority == "TV/TVC"
    assert entry.declaration.authority.github_token_runtime_authority is False
    assert "credential_authority" in entry.declaration.authority.may_not
    assert "repository_transport_authority" in entry.declaration.authority.may_not
    assert entry.evidence.activation_proof_ref is None
    assert entry.evidence.integration_evidence_refs == []
    assert "SOVEREIGN_LOCAL_MODEL_LIVE_ACTIVATION_NOT_YET_OBSERVED" in entry.evidence.blockers
    assert entry.evidence.continuation_owner


def test_heartbeat_carrier_is_separate_non_authorizing_capability():
    registry = load_capability_registry(REGISTRY)
    entries = {item.declaration.capability_id: item for item in registry.entries}
    carrier = entries["stegverse:capability:heartbeat-carrier:v1"]
    control = entries["stegverse:capability:worker-control-plane:v1"]
    communication = entries["stegverse:capability:manifest-communication:v1"]
    custody = entries["stegverse:capability:master-records-terminal-custody:v1"]

    assert carrier.phase == "DECLARED"
    assert carrier.declaration.metadata["canonical_role"] == "carrier_synchronization_only"
    assert carrier.declaration.metadata["frequency_rule"] == "gate_passband_derived"
    assert "route_execution" in carrier.declaration.authority.may_not
    assert "task_dispatch" in carrier.declaration.authority.may_not
    assert "master_records_custody" in carrier.declaration.authority.may_not

    assert control.declaration.capability_id != carrier.declaration.capability_id
    assert communication.declaration.capability_id != carrier.declaration.capability_id
    assert custody.declaration.capability_id != carrier.declaration.capability_id
    assert control.declaration.metadata["heartbeat_relationship"] == "observes_synchronization_continuity_only"
    assert communication.declaration.metadata["communication_object"] == "manifest+expiration_wrapper+data"
    assert custody.declaration.metadata["transition_table_eol"] == "master_records"
    assert custody.declaration.dependencies == ["stegverse:capability:manifest-communication:v1"]


def test_all_new_capability_boundaries_preserve_tvtvc_authority():
    registry = load_capability_registry(REGISTRY)
    ids = {
        "stegverse:capability:heartbeat-carrier:v1",
        "stegverse:capability:worker-control-plane:v1",
        "stegverse:capability:manifest-communication:v1",
        "stegverse:capability:master-records-terminal-custody:v1",
        "stegverse:capability:formalism-source-generation:v1",
    }
    for entry in registry.entries:
        if entry.declaration.capability_id in ids:
            assert entry.declaration.authority.credential_authority == "TV/TVC"
            assert entry.declaration.authority.github_token_runtime_authority is False


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
