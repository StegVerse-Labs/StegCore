"""StegVerse legacy LLM adapter compatibility surface.

This module retains prompt classification and historical Triad candidate shaping,
but it is no longer an admissibility authority. The previous adapter-local inline
evaluator could mint ALLOW when the external validator was unavailable; that path
is intentionally removed.

Consequential evaluation now requires an explicit canonical
``stegcore.AdmissibilityRequest`` and traverses the same manifested transaction,
ingestion, StegGate, commit-coherence, return-ingestion path used by ordinary
StegVerse governed runtimes.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Optional
import uuid

from stegcore.steggate import AdmissibilityRequest
from stegcore.transaction_lifecycle import (
    ManifestedTransactionResult,
    TransactionLedger,
    run_manifested_transaction,
)


def make_triad_candidate(
    prompt: str,
    user_id: str,
    entity_subject_id: str,
    action_intent: str,
    action_class: str,
    gcat_state: dict,
    bcat_params: dict,
    ecat_entity: dict,
    icat_params: dict,
    pe_observations: list,
    iw_budget: float = 1.0,
    context: dict | None = None,
) -> dict:
    """Build a non-authoritative historical Triad-shaped candidate.

    This helper exists for compatibility, audit, and input shaping only. Its
    output must not be treated as an executable authorization or StegGate result.
    """

    candidate_id = f"CAND-{uuid.uuid4().hex[:8].upper()}"
    return {
        "candidate_id": candidate_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "prompt_hash": hashlib.sha256(prompt.encode()).hexdigest(),
        "user_id": user_id,
        "entity_subject_id": entity_subject_id,
        "action_intent": action_intent,
        "action_class": action_class,
        "context": context or {},
        "gcat": {
            "state": gcat_state,
            "params": {
                "governance_threshold": bcat_params.get("governance_threshold", 0.5),
                "control_threshold": bcat_params.get("control_threshold", 0.5),
                "autonomy_threshold": bcat_params.get("autonomy_threshold", 0.5),
                "trust_threshold": bcat_params.get("trust_threshold", 0.5),
            },
        },
        "bcat": {"state": gcat_state, "params": bcat_params},
        "ecat": {
            "entity": ecat_entity,
            "params": {
                "stress_threshold": ecat_entity.get("stress_threshold", 0.7),
                "coherence_floor": ecat_entity.get("coherence_floor", 0.3),
                "manipulation_limit": ecat_entity.get("manipulation_limit", 0.2),
            },
        },
        "icat": {"entity": ecat_entity, "params": icat_params},
        "pe": {
            "observations": pe_observations,
            "params": {"existence_threshold": 0.6, "min_observations": 1},
        },
        "iw": {
            "inference_window": {
                "start": datetime.now(timezone.utc).isoformat(),
                "depth": len(pe_observations),
                "coherent": True,
            },
            "params": {"coherence_threshold": 0.5, "depth_minimum": 1},
            "budget": iw_budget,
        },
        "admissibility_authority": False,
        "canonical_runtime_required": True,
    }


ACTION_SCOPE_MAP = {
    "observe": ("ALLOW_OBSERVE", 0.3, 0.3, 0.3, 0.3),
    "queue": ("ALLOW_QUEUE", 0.4, 0.4, 0.4, 0.4),
    "route": ("ALLOW_ROUTE", 0.45, 0.45, 0.45, 0.45),
    "vault_write": ("ALLOW_VAULT_WRITE", 0.5, 0.5, 0.5, 0.5),
    "vault_read": ("ALLOW_VAULT_READ", 0.35, 0.35, 0.35, 0.35),
    "install": ("ALLOW_INSTALL", 0.6, 0.6, 0.6, 0.6),
    "confirm": ("ALLOW_CONFIRM", 0.65, 0.65, 0.65, 0.65),
    "promote": ("ALLOW_PROMOTE", 0.7, 0.7, 0.7, 0.7),
    "finco": ("ALLOW_FINCO_TRANSITION", 0.75, 0.75, 0.75, 0.75),
    "consent_grant": ("ALLOW_CONSENT_GRANT", 0.7, 0.7, 0.7, 0.7),
    "repair": ("ALLOW_REPAIR_CANDIDATE", 0.55, 0.55, 0.55, 0.55),
    "quarantine": ("ALLOW_QUARANTINE", 0.5, 0.5, 0.5, 0.5),
}


def classify_action(action_intent: str, activation_tier: str = "assist") -> dict:
    """Classify intent for candidate shaping; classification is not authority."""

    intent_lower = action_intent.lower()
    if any(word in intent_lower for word in ["read", "check", "look", "view", "get", "list", "show"]):
        action_class = "vault_read" if "vault" in intent_lower else "observe"
    elif any(word in intent_lower for word in ["write", "save", "store", "update", "remember"]):
        action_class = "vault_write"
    elif any(word in intent_lower for word in ["install", "deploy", "bootstrap"]):
        action_class = "install"
    elif any(word in intent_lower for word in ["pay", "transfer", "token", "coin", "finco"]):
        action_class = "finco"
    elif any(word in intent_lower for word in ["consent", "allow", "permit", "grant"]):
        action_class = "consent_grant"
    elif any(word in intent_lower for word in ["promote", "release", "publish"]):
        action_class = "promote"
    elif any(word in intent_lower for word in ["repair", "fix", "heal", "patch"]):
        action_class = "repair"
    elif any(word in intent_lower for word in ["queue", "schedule", "plan"]):
        action_class = "queue"
    else:
        action_class = "observe"

    if activation_tier == "observe":
        action_class = "observe"

    scope, governance, control, autonomy, trust = ACTION_SCOPE_MAP.get(
        action_class, ACTION_SCOPE_MAP["observe"]
    )
    return {
        "action_class": action_class,
        "required_scope": scope,
        "thresholds": {
            "governance": governance,
            "control": control,
            "autonomy": autonomy,
            "trust": trust,
        },
        "admissibility_authority": False,
    }


def default_gcat_state(activation_tier: str, user_trust_score: float = 0.7) -> dict:
    tier_caps = {
        "observe": {"governance": 0.4, "control": 0.4, "autonomy": 0.2, "trust": user_trust_score},
        "assist": {"governance": 0.6, "control": 0.6, "autonomy": 0.5, "trust": user_trust_score},
        "stegclaw": {"governance": 0.8, "control": 0.8, "autonomy": 0.75, "trust": user_trust_score},
    }
    return tier_caps.get(activation_tier, tier_caps["assist"])


def default_ecat_entity(stress_level: float = 0.2, coherence: float = 0.8) -> dict:
    return {
        "stress": stress_level,
        "coherence": coherence,
        "manipulation_detected": False,
        "inference_collapse": False,
        "stress_threshold": 0.7,
        "coherence_floor": 0.3,
        "manipulation_limit": 0.2,
    }


class LLMAdapter:
    """Compatibility adapter that cannot independently mint admissibility."""

    def __init__(
        self,
        triad_validator_path: str | None = None,
        receipts_path: str = "./llm_adapter_receipts.jsonl",
        candidates_path: str = "./llm_adapter_candidates/",
        transaction_ledger_path: str | None = None,
    ) -> None:
        # ``triad_validator_path`` is retained for API compatibility only. The
        # adapter does not delegate execution authority to a parallel validator.
        self.triad_validator_path = triad_validator_path
        self.receipts_path = Path(receipts_path)
        self.candidates_dir = Path(candidates_path)
        self.candidates_dir.mkdir(parents=True, exist_ok=True)
        self.transaction_ledger = TransactionLedger(transaction_ledger_path)

    def _emit_receipt(self, receipt: dict) -> None:
        self.receipts_path.parent.mkdir(parents=True, exist_ok=True)
        with self.receipts_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(receipt, sort_keys=True) + "\n")

    def _make_legacy_receipt(
        self,
        candidate_id: str,
        *,
        actor: str,
        action_intent: str,
    ) -> dict:
        return {
            "schema": "stegverse_llm_adapter_receipt.v2",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "engine": "llm-adapter-compatibility",
            "input_ref": candidate_id,
            "actor_or_source": actor,
            "decision": "FAIL_CLOSED",
            "reason": "canonical_admissibility_request_required",
            "hashes": {"candidate_hash": hashlib.sha256(candidate_id.encode()).hexdigest()},
            "unknowns": [action_intent],
            "next_route": "canonical_manifested_steggate_required",
            "admissibility_authority": False,
            "parallel_evaluator_used": False,
        }

    def evaluate_action(
        self,
        prompt: str,
        user_id: str,
        entity_subject_id: str,
        action_intent: str,
        activation_tier: str = "assist",
        user_trust_score: float = 0.7,
        stress_level: float = 0.2,
        coherence: float = 0.8,
        pe_observations: list | None = None,
        context: dict | None = None,
    ) -> dict:
        """Shape legacy input but fail closed until a canonical request exists.

        Historical callers may continue to call this method, but it can no
        longer produce ALLOW/DENY as an independent policy engine. Use
        :meth:`evaluate_manifested_action` for consequential evaluation.
        """

        classification = classify_action(action_intent, activation_tier)
        thresholds = classification["thresholds"]
        candidate = make_triad_candidate(
            prompt=prompt,
            user_id=user_id,
            entity_subject_id=entity_subject_id,
            action_intent=action_intent,
            action_class=classification["action_class"],
            gcat_state=default_gcat_state(activation_tier, user_trust_score),
            bcat_params=thresholds,
            ecat_entity=default_ecat_entity(stress_level, coherence),
            icat_params={"coherence_threshold": 0.5, "depth_minimum": 1},
            pe_observations=pe_observations or [{"type": "user_session", "confidence": 0.8}],
            context=context,
        )
        candidate_path = self.candidates_dir / f"{candidate['candidate_id']}.json"
        candidate_path.write_text(json.dumps(candidate, indent=2, sort_keys=True), encoding="utf-8")

        receipt = self._make_legacy_receipt(
            candidate["candidate_id"],
            actor=entity_subject_id,
            action_intent=action_intent,
        )
        self._emit_receipt(receipt)
        return {
            "candidate_id": candidate["candidate_id"],
            "action_class": classification["action_class"],
            "decision": "FAIL_CLOSED",
            "reason": "canonical_admissibility_request_required",
            "next_route": "canonical_manifested_steggate_required",
            "receipt": receipt,
        }

    def evaluate_manifested_action(
        self,
        request: AdmissibilityRequest,
        executor: Callable[[], Any],
        *,
        prompt: str,
        entity_subject_id: str,
        processing_capability: str,
        route_id: str,
        source: str = "llm-adapter",
        metadata: Optional[Mapping[str, Any]] = None,
        declared_execution_context: Optional[Mapping[str, Any]] = None,
        capability_surface: Optional[Mapping[str, Any]] = None,
        authority_resolution: Optional[Mapping[str, Any]] = None,
    ) -> ManifestedTransactionResult:
        """Run an explicit canonical request through the ordinary ecosystem path."""

        return run_manifested_transaction(
            request,
            executor,
            input_data={
                "prompt_hash": hashlib.sha256(prompt.encode()).hexdigest(),
                "prompt": prompt,
            },
            source=source,
            subject=entity_subject_id,
            ledger=self.transaction_ledger,
            processing_capability=processing_capability,
            route_id=route_id,
            metadata={
                "adapter": "legacy-llm-adapter-compatibility",
                "parallel_evaluator_used": False,
                **dict(metadata or {}),
            },
            declared_execution_context=declared_execution_context,
            capability_surface=capability_surface,
            authority_resolution=authority_resolution,
        )


if __name__ == "__main__":
    adapter = LLMAdapter()
    result = adapter.evaluate_action(
        prompt="Read my genealogy records",
        user_id="user_001",
        entity_subject_id="steg:agent/personal:demo",
        action_intent="observe",
        activation_tier="assist",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
