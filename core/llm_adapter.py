"""
StegVerse LLM Adapter v1.0
Converts user prompts into Triad candidate vectors.
Routes outputs through sandbox or ingestion.
Prevents LLM responses from becoming trusted state without Triad validation.
Integrates with existing triad_validator.py in GCAT-BCAT-Engine/workflows.
"""

import json
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Optional
from pathlib import Path

# ── Triad candidate vector schema ───────────────────────────────────────────
# Matches GCAT-BCAT-Engine/workflows/triad_validator.py candidate format

def make_triad_candidate(
    prompt: str,
    user_id: str,
    entity_subject_id: str,
    action_intent: str,
    action_class: str,       # observe|queue|route|install|confirm|promote|vault_write|finco
    gcat_state: dict,
    bcat_params: dict,
    ecat_entity: dict,
    icat_params: dict,
    pe_observations: list,
    iw_budget: float = 1.0,
    context: dict = None,
) -> dict:
    """
    Build a Triad candidate vector from user context.
    This is the bridge between a natural language request and the formal gate.
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
        # GCAT sub-object
        "gcat": {
            "state": gcat_state,
            "params": {
                "governance_threshold": bcat_params.get("governance_threshold", 0.5),
                "control_threshold":    bcat_params.get("control_threshold", 0.5),
                "autonomy_threshold":   bcat_params.get("autonomy_threshold", 0.5),
                "trust_threshold":      bcat_params.get("trust_threshold", 0.5),
            }
        },
        # BCAT sub-object
        "bcat": {
            "state": gcat_state,  # BCAT uses same state vector, different params
            "params": bcat_params,
        },
        # ECAT sub-object
        "ecat": {
            "entity": ecat_entity,
            "params": {
                "stress_threshold":   ecat_entity.get("stress_threshold", 0.7),
                "coherence_floor":    ecat_entity.get("coherence_floor", 0.3),
                "manipulation_limit": ecat_entity.get("manipulation_limit", 0.2),
            }
        },
        # ICAT sub-object
        "icat": {
            "entity": ecat_entity,
            "params": icat_params,
        },
        # PE sub-object
        "pe": {
            "observations": pe_observations,
            "params": {
                "existence_threshold": 0.6,
                "min_observations": 1,
            }
        },
        # IW sub-object
        "iw": {
            "inference_window": {
                "start": datetime.now(timezone.utc).isoformat(),
                "depth": len(pe_observations),
                "coherent": True,
            },
            "params": {"coherence_threshold": 0.5, "depth_minimum": 1},
            "budget": iw_budget,
        }
    }


# ── Action classifier ────────────────────────────────────────────────────────

ACTION_SCOPE_MAP = {
    "observe":        ("ALLOW_OBSERVE",        0.3, 0.3, 0.3, 0.3),
    "queue":          ("ALLOW_QUEUE",           0.4, 0.4, 0.4, 0.4),
    "route":          ("ALLOW_ROUTE",           0.45, 0.45, 0.45, 0.45),
    "vault_write":    ("ALLOW_VAULT_WRITE",     0.5, 0.5, 0.5, 0.5),
    "vault_read":     ("ALLOW_VAULT_READ",      0.35, 0.35, 0.35, 0.35),
    "install":        ("ALLOW_INSTALL",         0.6, 0.6, 0.6, 0.6),
    "confirm":        ("ALLOW_CONFIRM",         0.65, 0.65, 0.65, 0.65),
    "promote":        ("ALLOW_PROMOTE",         0.7, 0.7, 0.7, 0.7),
    "finco":          ("ALLOW_FINCO_TRANSITION", 0.75, 0.75, 0.75, 0.75),
    "consent_grant":  ("ALLOW_CONSENT_GRANT",   0.7, 0.7, 0.7, 0.7),
    "repair":         ("ALLOW_REPAIR_CANDIDATE", 0.55, 0.55, 0.55, 0.55),
    "quarantine":     ("ALLOW_QUARANTINE",      0.5, 0.5, 0.5, 0.5),
}

def classify_action(action_intent: str, activation_tier: str = "assist") -> dict:
    """
    Map a natural language action intent to an action class and threshold requirements.
    Conservative by default — higher-consequence actions require higher thresholds.
    """
    intent_lower = action_intent.lower()

    if any(w in intent_lower for w in ["read", "check", "look", "view", "get", "list", "show"]):
        action_class = "vault_read" if "vault" in intent_lower else "observe"
    elif any(w in intent_lower for w in ["write", "save", "store", "update", "remember"]):
        action_class = "vault_write"
    elif any(w in intent_lower for w in ["install", "deploy", "bootstrap"]):
        action_class = "install"
    elif any(w in intent_lower for w in ["pay", "transfer", "token", "coin", "finco"]):
        action_class = "finco"
    elif any(w in intent_lower for w in ["consent", "allow", "permit", "grant"]):
        action_class = "consent_grant"
    elif any(w in intent_lower for w in ["promote", "release", "publish"]):
        action_class = "promote"
    elif any(w in intent_lower for w in ["repair", "fix", "heal", "patch"]):
        action_class = "repair"
    elif any(w in intent_lower for w in ["queue", "schedule", "plan"]):
        action_class = "queue"
    else:
        action_class = "observe"  # default conservative

    # StegClaw tier can attempt higher-consequence actions
    if activation_tier == "observe":
        action_class = "observe"  # lock to observe

    scope, g, c, a, t = ACTION_SCOPE_MAP.get(action_class, ACTION_SCOPE_MAP["observe"])
    return {
        "action_class": action_class,
        "required_scope": scope,
        "thresholds": {"governance": g, "control": c, "autonomy": a, "trust": t},
    }


# ── Default state vectors by tier ────────────────────────────────────────────

def default_gcat_state(activation_tier: str, user_trust_score: float = 0.7) -> dict:
    """
    Build a default GCAT state vector from user context.
    In production: derive from user's actual governance posture.
    """
    tier_caps = {
        "observe":  {"governance": 0.4, "control": 0.4, "autonomy": 0.2, "trust": user_trust_score},
        "assist":   {"governance": 0.6, "control": 0.6, "autonomy": 0.5, "trust": user_trust_score},
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


# ── LLM Adapter ──────────────────────────────────────────────────────────────

class LLMAdapter:
    """
    Bridges user/LLM prompts to the Triad gate.
    Every proposed action is evaluated before it can commit.
    Receipts are emitted for all decisions.
    """

    def __init__(
        self,
        triad_validator_path: str = None,
        receipts_path: str = "./llm_adapter_receipts.jsonl",
        candidates_path: str = "./llm_adapter_candidates/",
    ):
        self.receipts_path = Path(receipts_path)
        self.candidates_dir = Path(candidates_path)
        self.candidates_dir.mkdir(parents=True, exist_ok=True)

        # Try to import the existing triad_validator
        self._triad_available = False
        if triad_validator_path:
            import sys
            sys.path.insert(0, triad_validator_path)
            try:
                from triad_validator import TriadValidator
                self._triad = TriadValidator()
                self._triad_available = True
            except ImportError:
                pass

    def _emit_receipt(self, receipt: dict):
        with open(self.receipts_path, "a") as f:
            f.write(json.dumps(receipt) + "\n")

    def _make_receipt(self, candidate_id: str, decision: str, reason: str,
                      actor: str, next_route: str, unknowns: list = None) -> dict:
        return {
            "schema": "stegverse_llm_adapter_receipt.v1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "engine": "llm-adapter",
            "input_ref": candidate_id,
            "actor_or_source": actor,
            "decision": decision,
            "reason": reason,
            "hashes": {"candidate_hash": hashlib.sha256(candidate_id.encode()).hexdigest()},
            "unknowns": unknowns or [],
            "next_route": next_route,
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
        pe_observations: list = None,
        context: dict = None,
    ) -> dict:
        """
        Main entry point. Takes a prompt and user context, returns ALLOW/DENY/FAIL_CLOSED.
        This is what the personal entity calls before executing any action.
        """
        # 1. Classify the action
        classification = classify_action(action_intent, activation_tier)
        action_class   = classification["action_class"]
        thresholds     = classification["thresholds"]

        # 2. Build Triad candidate vector
        gcat_state = default_gcat_state(activation_tier, user_trust_score)
        ecat_entity = default_ecat_entity(stress_level, coherence)

        candidate = make_triad_candidate(
            prompt=prompt,
            user_id=user_id,
            entity_subject_id=entity_subject_id,
            action_intent=action_intent,
            action_class=action_class,
            gcat_state=gcat_state,
            bcat_params=thresholds,
            ecat_entity=ecat_entity,
            icat_params={"coherence_threshold": 0.5, "depth_minimum": 1},
            pe_observations=pe_observations or [{"type": "user_session", "confidence": 0.8}],
            context=context,
        )

        # 3. Save candidate vector (for replay and audit)
        cand_file = self.candidates_dir / f"{candidate['candidate_id']}.json"
        with open(cand_file, "w") as f:
            json.dump(candidate, f, indent=2)

        # 4. Run Triad validator if available
        if self._triad_available:
            try:
                triad_result = self._triad.validate(candidate)
                decision = triad_result.get("decision", "FAIL_CLOSED")
                reason   = triad_result.get("reason", "Triad evaluation complete.")
            except Exception as e:
                decision = "FAIL_CLOSED"
                reason   = f"Triad validation error: {e}"
        else:
            # Inline evaluation when triad_validator not available
            decision, reason = self._inline_evaluate(candidate, gcat_state, thresholds)

        # 5. Determine next route
        next_route = {
            "ALLOW": "vault_write" if "vault" in action_class else "ingestion",
            "DENY":  "quarantine",
            "FAIL_CLOSED": "quarantine",
            "REVIEW_REQUIRED": "review",
        }.get(decision, "quarantine")

        # 6. Emit receipt
        receipt = self._make_receipt(
            candidate["candidate_id"], decision, reason,
            entity_subject_id, next_route,
            unknowns=[] if decision == "ALLOW" else [action_intent]
        )
        self._emit_receipt(receipt)

        return {
            "candidate_id": candidate["candidate_id"],
            "action_class": action_class,
            "decision": decision,
            "reason": reason,
            "next_route": next_route,
            "receipt": receipt,
        }

    def _inline_evaluate(self, candidate: dict, gcat_state: dict, thresholds: dict) -> tuple:
        """
        Inline Triad evaluation when external validator not available.
        Simplified but structurally correct.
        """
        issues = []

        # GCAT check
        for dim, threshold in thresholds.items():
            actual = gcat_state.get(dim, 0)
            if actual < threshold:
                issues.append(f"GCAT/{dim.upper()}: {actual:.2f} < {threshold:.2f}")

        # ECAT check
        ecat = candidate.get("ecat", {}).get("entity", {})
        if ecat.get("stress", 0) > ecat.get("stress_threshold", 0.7):
            issues.append("ECAT: stress exceeds threshold")
        if ecat.get("coherence", 1) < ecat.get("coherence_floor", 0.3):
            issues.append("ECAT: coherence below floor")
        if ecat.get("manipulation_detected"):
            issues.append("ECAT: manipulation signal detected")

        # PE check
        pe_obs = candidate.get("pe", {}).get("observations", [])
        if not pe_obs:
            issues.append("PE: no observations — existence unverified")
        else:
            avg_conf = sum(o.get("confidence", 0) for o in pe_obs) / len(pe_obs)
            if avg_conf < 0.6:
                issues.append(f"PE: mean confidence {avg_conf:.2f} below 0.6 threshold")

        if issues:
            return "FAIL_CLOSED", "Gate failures: " + "; ".join(issues)

        return "ALLOW", f"All gates passed for action class '{candidate.get('action_class')}'."


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    adapter = LLMAdapter()

    # Demo evaluation
    results = []
    test_cases = [
        ("Read my genealogy records", "assist",   "observe"),
        ("Save my session context",   "assist",   "vault_write"),
        ("Deploy Core-Lite",          "assist",   "install"),
        ("Transfer 100 StegCoin",     "stegclaw", "finco"),
        ("Transfer 100 StegCoin",     "observe",  "finco"),  # should fail
    ]

    for prompt, tier, intent in test_cases:
        r = adapter.evaluate_action(
            prompt=prompt,
            user_id="user_001",
            entity_subject_id="steg:agent/personal:demo",
            action_intent=intent,
            activation_tier=tier,
        )
        results.append({
            "prompt": prompt,
            "tier": tier,
            "decision": r["decision"],
            "action_class": r["action_class"],
        })
        print(f"[{r['decision']:<12}] {prompt!r} (tier={tier})")

    print(f"\n{sum(1 for r in results if r['decision'] == 'ALLOW')}/{len(results)} ALLOW")
