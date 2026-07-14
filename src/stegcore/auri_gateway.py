from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Any, Literal, Mapping

from .decision import (
    ActionIntent,
    DecisionRequest,
    PolicyContext,
    VerifiedReceiptEnvelope,
    decide,
)

GatewayDecision = Literal["allow", "deny", "defer"]


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256(payload).hexdigest()


@dataclass(frozen=True)
class AuriGatewayResult:
    decision: GatewayDecision
    reason_code: str
    candidate_sha256: str
    execution_performed: bool
    receipt: dict[str, Any]


def evaluate_auri_candidate(
    candidate: Mapping[str, Any],
    *,
    verified_receipt: VerifiedReceiptEnvelope | None,
    policy_shapes: list[str] | None = None,
    commit_candidate_sha256: str | None = None,
) -> AuriGatewayResult:
    candidate_dict = dict(candidate)
    candidate_hash = canonical_sha256(candidate_dict)

    def result(decision: GatewayDecision, reason: str) -> AuriGatewayResult:
        body = {
            "schema_version": "1.0.0",
            "receipt_type": "stegcore_auri_decision",
            "actor_entity_id": candidate_dict.get("prepared_by"),
            "activation_level": candidate_dict.get("activation_level", "AURI-L1"),
            "candidate_id": candidate_dict.get("candidate_id"),
            "candidate_sha256": candidate_hash,
            "decision": decision,
            "reason_code": reason,
            "execution_performed": False,
        }
        receipt = {**body, "receipt_sha256": canonical_sha256(body)}
        return AuriGatewayResult(decision, reason, candidate_hash, False, receipt)

    if candidate_dict.get("prepared_by") != "stegverse:auri":
        return result("deny", "auri.actor.invalid")

    posture = candidate_dict.get("auri_posture")
    if not isinstance(posture, Mapping):
        return result("deny", "auri.posture.missing")
    if posture.get("execution_authority") is not False:
        return result("deny", "auri.execution_authority.forbidden")
    if posture.get("final_consequence_authority") is not False:
        return result("deny", "auri.final_authority.forbidden")
    if posture.get("requires_external_admissibility") is not True:
        return result("deny", "auri.external_admissibility.required")

    consequential = bool(candidate_dict.get("execution_context", {}).get("consequential"))
    if consequential and not candidate_dict.get("policy_ref"):
        return result("deny", "policy.missing")
    if consequential and not candidate_dict.get("delegation_ref"):
        return result("deny", "delegation.missing")

    if commit_candidate_sha256 is not None and commit_candidate_sha256 != candidate_hash:
        return result("deny", "commit.candidate_hash_mismatch")

    decision_result = decide(
        DecisionRequest(
            verified_receipt=verified_receipt,
            actor_class="ai",
            intent=ActionIntent(
                action=str(candidate_dict.get("action", "")),
                target=str(candidate_dict.get("target", "")),
                parameters={"candidate_sha256": candidate_hash},
            ),
            policy=PolicyContext(shapes=list(policy_shapes or []), scope=str(candidate_dict.get("scope", ""))),
        )
    )
    return result(decision_result.decision, decision_result.reason_code)
