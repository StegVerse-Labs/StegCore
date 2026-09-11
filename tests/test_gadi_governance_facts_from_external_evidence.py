from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from scripts.materialize_gadi_governance_facts_from_external_evidence import (
    GADIExternalEvidenceFactsError,
    GADI_ACTION,
    GADI_POLICY,
    GADI_SCOPE,
    GADI_TARGET,
    resolved_facts_from_external_evidence,
)

FIXTURE = Path("contracts/governance_external_evidence_snapshot/docs/examples/interop/external_evidence_valid.json")


def envelope() -> dict:
    value = json.loads(FIXTURE.read_text(encoding="utf-8"))
    value["subject"]["target_ref"] = GADI_TARGET
    candidate = value["commitment_candidate"]
    candidate["target_ref"] = GADI_TARGET
    candidate["scope"] = GADI_SCOPE
    candidate["action"] = GADI_ACTION
    candidate["policy_ref"] = GADI_POLICY
    return value


def test_valid_current_external_evidence_projects_exact_three_layer_facts():
    result = resolved_facts_from_external_evidence(envelope())
    facts = result["resolved_governance_facts"]
    assert result["state"] == "RESOLVED_GOVERNANCE_FACTS_PROJECTED"
    assert set(facts) == {"judgment_conditions", "signal_admission", "execution_boundary"}
    assert facts["execution_boundary"]["policy_ref"] == GADI_POLICY
    assert facts["execution_boundary"]["actor_authority_current"] is True
    assert facts["execution_boundary"]["policy_current"] is True
    assert facts["execution_boundary"]["delegation_current"] is True
    assert facts["execution_boundary"]["evidence_current"] is True
    assert facts["signal_admission"]["reference_state_hash"] == facts["signal_admission"]["expected_reference_state_hash"]
    assert result["external_evidence_envelope_created"] is False
    assert result["resolved_governance_facts_invented"] is False
    assert result["intr_transport_performed"] is False
    assert result["gadi_admission_created"] is False
    assert result["runtime_binding_created"] is False
    assert result["claim_or_fence_minted"] is False
    assert result["execution_authority_granted"] is False
    assert result["authority_effect"] == "NONE_FACT_PROJECTION_ONLY"


def test_stale_envelope_is_rejected_as_fact_source():
    value = envelope()
    value["freshness"]["is_current"] = False
    with pytest.raises(GADIExternalEvidenceFactsError, match="evidence.stale"):
        resolved_facts_from_external_evidence(value)


def test_unauthorized_provider_is_rejected_as_fact_source():
    value = envelope()
    value["authorization"]["provider_authorized"] = False
    with pytest.raises(GADIExternalEvidenceFactsError, match="provider_unauthorized"):
        resolved_facts_from_external_evidence(value)


def test_provider_cannot_claim_execution_authority():
    value = envelope()
    value["commitment_candidate"]["evidence_provider_execution_authority"] = True
    with pytest.raises(GADIExternalEvidenceFactsError, match="provider authority forbidden"):
        resolved_facts_from_external_evidence(value)


def test_wrong_gadi_policy_is_rejected_before_projection():
    value = envelope()
    value["commitment_candidate"]["policy_ref"] = "policy:wrong"
    with pytest.raises(GADIExternalEvidenceFactsError, match="policy mismatch"):
        resolved_facts_from_external_evidence(value)


def test_wrong_gadi_target_is_rejected_before_projection():
    value = envelope()
    value["commitment_candidate"]["target_ref"] = "other-system"
    with pytest.raises(GADIExternalEvidenceFactsError, match="target mismatch"):
        resolved_facts_from_external_evidence(value)


def test_valid_but_reference_drift_may_project_denial_facts_without_authority():
    value = envelope()
    value["commitment_candidate"]["reference_state_hash"] = "sha256:state-drifted"
    result = resolved_facts_from_external_evidence(value)
    assert result["external_evidence_decision"] in {"DENY", "FAIL-CLOSED"}
    assert result["resolved_governance_facts"]["signal_admission"]["reference_state_hash"] == "sha256:state-drifted"
    assert result["execution_authority_granted"] is False
