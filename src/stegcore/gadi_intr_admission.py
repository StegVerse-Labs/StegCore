from __future__ import annotations

"""Project a canonical governance decision into the GADI admission contract.

This module does not evaluate governance, mint InTr transport state, create a runtime
binding, or grant execution authority. It only binds an already-produced canonical
Universal Governance Connector decision to the exact GADI intervention request bytes
and projects that decision into the existing ``Admission`` field.
"""

from hashlib import sha256
import json
from typing import Any, Mapping

from .gadi import Admission, DefensiveInterventionRequest
from .universal_governance_connector import GovernanceConnectorResult

GADI_PROFILE_ID = "gadi.defensive-intervention.v1"
GADI_OPERATION_ID = "admit-defensive-intervention"
GADI_SYSTEM_ID = "stegverse.gadi.defensive-intervention"
GADI_BOUNDARY_ID = "interlock:gadi.defensive-intervention"


class GadiAdmissionProjectionError(ValueError):
    pass


def canonical_request_hash(request: DefensiveInterventionRequest) -> str:
    payload = request.model_dump(mode="json")
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + sha256(raw).hexdigest()


def expected_candidate_ref(request: DefensiveInterventionRequest) -> str:
    return f"gadi-request:{request.request_id}"


def intr_decision_ref(result: GovernanceConnectorResult) -> str:
    return f"intr://governance-decision/{result.receipt_hash}"


def project_governance_decision_to_gadi_admission(
    request: DefensiveInterventionRequest,
    result: GovernanceConnectorResult,
) -> DefensiveInterventionRequest:
    """Return a copy of ``request`` with its admission projected from ``result``.

    ALLOW becomes ADMITTED only when the decision is exactly bound to this GADI
    request and still explicitly carries no execution authority. DENY and
    FAIL-CLOSED become DENIED. Any binding or authority mismatch fails closed by
    raising ``GadiAdmissionProjectionError`` rather than manufacturing admission.
    """

    if request.admission.state != "PENDING" or request.admission.intr_decision_ref is not None:
        raise GadiAdmissionProjectionError("gadi admission projection requires PENDING request")
    if result.profile_id != GADI_PROFILE_ID:
        raise GadiAdmissionProjectionError("gadi governance profile mismatch")
    if result.operation_id != GADI_OPERATION_ID:
        raise GadiAdmissionProjectionError("gadi governance operation mismatch")
    if result.system_id != GADI_SYSTEM_ID or result.boundary_id != GADI_BOUNDARY_ID:
        raise GadiAdmissionProjectionError("gadi governance system/boundary mismatch")
    if result.candidate_ref != expected_candidate_ref(request):
        raise GadiAdmissionProjectionError("gadi governance candidate reference mismatch")
    if result.candidate_hash != canonical_request_hash(request):
        raise GadiAdmissionProjectionError("gadi governance candidate hash mismatch")
    if result.execution_authority_granted is not False:
        raise GadiAdmissionProjectionError("governance decision may not grant GADI execution authority")
    if result.credential_authority != "TV/TVC":
        raise GadiAdmissionProjectionError("GADI credential authority mismatch")
    if result.authority_effect != "NONE":
        raise GadiAdmissionProjectionError("governance decision authority drift")
    if result.continuity_receipt_minted is not False:
        raise GadiAdmissionProjectionError("governance decision may not mint GADI continuity authority")

    decision_ref = intr_decision_ref(result)
    if result.decision == "ALLOW":
        if result.eligible_for_separate_consequence_authorization is not True:
            raise GadiAdmissionProjectionError("ALLOW is not eligible for separate consequence authorization")
        admission = Admission(state="ADMITTED", intr_decision_ref=decision_ref)
    elif result.decision in {"DENY", "FAIL-CLOSED"}:
        admission = Admission(state="DENIED", intr_decision_ref=decision_ref)
    else:
        raise GadiAdmissionProjectionError("unsupported governance decision")

    return request.model_copy(update={"admission": admission})


def projection_receipt(
    original: DefensiveInterventionRequest,
    projected: DefensiveInterventionRequest,
    result: GovernanceConnectorResult,
) -> dict[str, Any]:
    """Describe the projection without claiming transport, runtime, or execution."""
    return {
        "schema": "stegcore.gadi-intr-admission-projection/v1",
        "task_id": "GADI-001",
        "request_id": original.request_id,
        "candidate_ref": expected_candidate_ref(original),
        "candidate_hash": canonical_request_hash(original),
        "governance_profile_id": result.profile_id,
        "governance_operation_id": result.operation_id,
        "governance_decision": result.decision,
        "governance_receipt_hash": result.receipt_hash,
        "admission": projected.admission.model_dump(mode="json"),
        "runtime_binding_minted": False,
        "execution_authority_granted": False,
        "credential_authority": "TV/TVC",
        "authority_effect": "NONE_ADMISSION_PROJECTION_ONLY",
    }


__all__ = [
    "GADI_BOUNDARY_ID",
    "GADI_OPERATION_ID",
    "GADI_PROFILE_ID",
    "GADI_SYSTEM_ID",
    "GadiAdmissionProjectionError",
    "canonical_request_hash",
    "expected_candidate_ref",
    "intr_decision_ref",
    "project_governance_decision_to_gadi_admission",
    "projection_receipt",
]
