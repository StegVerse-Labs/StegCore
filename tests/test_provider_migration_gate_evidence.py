from copy import deepcopy

from stegcore.provider_migration_gate_evidence import (
    REQUIRED_GATES,
    evaluate_provider_migration_gate_evidence,
)


def _sha(char: str) -> str:
    return char * 64


def _report():
    gates = []
    for index, gate in enumerate(REQUIRED_GATES):
        if index == 0:
            gates.append({
                "gate": gate,
                "verification_state": "EVIDENCE_VERIFIED",
                "evidence_hash": _sha("a"),
                "evidence_refs": ["reports/provider-inventory-results.json"],
            })
        else:
            gates.append({
                "gate": gate,
                "verification_state": "BLOCKED_MISSING_EVIDENCE",
                "evidence_hash": None,
                "evidence_refs": [],
            })

    import hashlib, json
    canonical = lambda value: json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    provider = {
        "provider_id": "github",
        "gates": gates,
        "gate_set_hash": hashlib.sha256(canonical(gates)).hexdigest(),
    }
    providers = [provider]
    return {
        "schema": "stegverse.governance.provider_migration_gate_evidence.v1",
        "providers": providers,
        "registry_hash": hashlib.sha256(canonical(providers)).hexdigest(),
        "manual_action_required": False,
        "production_mutation_allowed": False,
        "execution_authority": False,
        "traffic_cutover_authority": False,
        "cancellation_authority": False,
        "provider_retirement_authority": False,
        "continuity_receipt_minted": False,
    }


def test_allows_valid_registry_as_evidence_only():
    result = evaluate_provider_migration_gate_evidence(_report())
    assert result["decision"] == "ALLOW_EVIDENCE_REGISTRY_ONLY"
    assert result["verified_gate_count"] == 1
    assert result["blocked_gate_count"] == 7
    assert result["provider_retirement_authority"] is False


def test_denies_verified_gate_without_hash():
    report = _report()
    report["providers"][0]["gates"][0]["evidence_hash"] = None
    result = evaluate_provider_migration_gate_evidence(report)
    assert result["decision"] == "DENY"
    assert any("invalid_verified_hash" in reason for reason in result["reasons"])


def test_denies_gate_order_change():
    report = _report()
    report["providers"][0]["gates"].reverse()
    result = evaluate_provider_migration_gate_evidence(report)
    assert result["decision"] == "DENY"
    assert any("gate_order_or_coverage_mismatch" in reason for reason in result["reasons"])


def test_denies_hidden_retirement_authority():
    report = _report()
    report["nested"] = {"provider_retirement_authority": True}
    result = evaluate_provider_migration_gate_evidence(report)
    assert result["decision"] == "DENY"
    assert "forbidden_authority_present" in result["reasons"]


def test_denies_registry_hash_mismatch():
    report = _report()
    report["registry_hash"] = _sha("b")
    result = evaluate_provider_migration_gate_evidence(report)
    assert result["decision"] == "DENY"
    assert "registry_hash_mismatch" in result["reasons"]
