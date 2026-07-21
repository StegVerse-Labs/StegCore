import copy
import hashlib
import json

from stegcore.render_provider_state import evaluate_render_provider_state


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def finalize(report):
    payload = dict(report)
    payload.pop("report_sha256", None)
    report["report_sha256"] = hashlib.sha256(canonical(payload)).hexdigest()
    return report


def base_report():
    return finalize({
        "schema": "stegverse.governance.render_provider_state.v1",
        "provider_id": "render",
        "state": "BLOCKED_PARTIAL_RENDER_STATE",
        "api_state": "BLOCKED_RENDER_API_CREDENTIAL_UNAVAILABLE",
        "repository_configs": [{
            "repository": "StegVerse-Labs/Site",
            "state": "CONFIG_DISCOVERED",
            "config_paths": [{"path": "render.yaml", "content_sha256": "a" * 64, "size_bytes": 10}],
        }],
        "services": [],
        "environment_values_retained": False,
        "deploy_hooks_retained": False,
        "credentials_retained": False,
        "raw_secret_material_retained": False,
        "manual_action_required": False,
        "production_mutation_allowed": False,
        "execution_authority": False,
        "traffic_cutover_authority": False,
        "cancellation_authority": False,
        "provider_retirement_authority": False,
        "continuity_receipt_minted": False,
    })


def test_configuration_only_never_verifies_export():
    result = evaluate_render_provider_state(base_report())
    assert result["decision"] == "ALLOW_RENDER_PROVIDER_EVIDENCE_ONLY"
    assert result["configuration_discovery_verified"] is True
    assert result["authenticated_provider_metadata_verified"] is False
    assert result["export_verified"] is False


def test_authenticated_service_metadata_verifies_export_evidence_only():
    report = base_report()
    report["state"] = "RENDER_STATE_EXPORTED"
    report["api_state"] = "AUTHENTICATED_RENDER_METADATA"
    report["services"] = [{"id": "srv-1", "name": "example", "type": "web_service"}]
    finalize(report)
    result = evaluate_render_provider_state(report)
    assert result["decision"] == "ALLOW_RENDER_PROVIDER_EVIDENCE_ONLY"
    assert result["export_verified"] is True
    assert result["provider_retirement_authority"] is False


def test_hidden_authority_denied():
    report = base_report()
    report["execution_authority"] = True
    finalize(report)
    assert evaluate_render_provider_state(report)["decision"] == "DENY"


def test_invalid_hash_denied():
    report = base_report()
    report["report_sha256"] = "0" * 64
    assert evaluate_render_provider_state(report)["decision"] == "DENY"


def test_export_claim_without_authenticated_services_denied():
    report = base_report()
    report["state"] = "RENDER_STATE_EXPORTED"
    finalize(report)
    result = evaluate_render_provider_state(report)
    assert result["decision"] == "DENY"
