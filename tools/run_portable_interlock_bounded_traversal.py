from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from stegcore.steggate import AdmissibilityRequest
from stegcore.steggate_runtime import governed_steggate_execute

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE = ROOT / "fixtures" / "portable_interlock_bounded_traversal.v1.json"
DEFAULT_REQUEST = ROOT / "examples" / "steggate_allow_request.json"


def _hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def build_execution_context(bundle: dict[str, Any]) -> dict[str, Any]:
    ingress = bundle["interlock_transition"]
    if _hash(ingress) != bundle["ingress_interlock_hash"]:
        raise ValueError("ingress interlock hash mismatch")
    connection = ingress["connection"]
    return {
        "standing_required": True,
        "standing_evidence": {
            "required": True,
            "expected_interlock": {
                "package_id": ingress["package_id"],
                "transition_id": ingress["transition_id"],
                "run_id": ingress["run_id"],
                "participant_id": connection["participant_id"],
                "ingress_interlock_hash": bundle["ingress_interlock_hash"],
            },
            "spe_envelope": copy.deepcopy(bundle["spe_envelope"]),
            "spe_receipt": copy.deepcopy(bundle["spe_receipt"]),
            "steggate_bridge": copy.deepcopy(bundle["steggate_bridge"]),
        },
    }


def run_traversal(bundle_path: Path = DEFAULT_FIXTURE, request_path: Path = DEFAULT_REQUEST) -> dict[str, Any]:
    bundle = load_json(bundle_path)
    request = AdmissibilityRequest.model_validate(load_json(request_path))
    execution_context = build_execution_context(bundle)
    state = {"written": False, "count": 0}

    def executor() -> dict[str, Any]:
        state["written"] = True
        state["count"] += 1
        return {"record": "bounded-write", "count": state["count"]}

    observation = governed_steggate_execute(
        request,
        executor,
        declared_execution_context=execution_context,
        capability_surface={
            "actions_exposed": [request.candidate.action],
            "execution_mode": "manual",
            "requires_governed_commit": True,
        },
        authority_resolution={
            "status": "approved",
            "basis_invalidated_by_action": False,
            "authority_ref": "portable-interlock-test-authority",
            "target_binding": request.candidate.target,
            "valid_from": "2026-01-01T00:00:00+00:00",
            "valid_until": "2027-01-01T00:00:00+00:00",
        },
    )
    standing_rows = [row for row in observation.evaluation.matrix if row.predicate == "standing.spe_binding"]
    checks = {
        "sdk_source_pinned": len(str(bundle.get("sdk_source_commit", ""))) == 40,
        "ingress_hash_verified": _hash(bundle["interlock_transition"]) == bundle["ingress_interlock_hash"],
        "standing_binding_pass": len(standing_rows) == 1 and standing_rows[0].state == "PASS",
        "admissibility_allow": observation.evaluation.disposition == "ALLOW",
        "present_state_allow": bool(observation.coherence_receipt)
        and all((observation.coherence_receipt.get("present_state_checks") or {}).values()),
        "coherence_allow": bool(observation.coherence_receipt) and observation.coherence_receipt.get("decision") == "ALLOW",
        "executor_invoked_once": observation.executor_invoked is True and state["count"] == 1,
        "bounded_consequence_observed": observation.status == "executed" and state["written"] is True,
    }
    return {
        "schema": "stegverse.portable-interlock-bounded-traversal-evidence.v1",
        "sdk_source_commit": bundle["sdk_source_commit"],
        "ingress_interlock_hash": bundle["ingress_interlock_hash"],
        "package_id": bundle["interlock_transition"]["package_id"],
        "transition_id": bundle["interlock_transition"]["transition_id"],
        "run_id": bundle["interlock_transition"]["run_id"],
        "participant_id": bundle["interlock_transition"]["connection"]["participant_id"],
        "checks": checks,
        "proof_state": "PASS" if all(checks.values()) else "FAIL",
        "execution": {
            "status": observation.status,
            "executor_invoked": observation.executor_invoked,
            "pre_state_hash": observation.pre_state_hash,
            "post_state_hash": observation.post_state_hash,
            "decision_state_hash": observation.evaluation.decision_state_hash,
            "coherence_receipt": observation.coherence_receipt,
            "result": observation.result,
        },
        "next_boundary": "SDK_INTERLOCK_RETURN_ASSEMBLY",
        "master_records_organization_record_claimed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--request", type=Path, default=DEFAULT_REQUEST)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    evidence = run_traversal(args.fixture, args.request)
    rendered = json.dumps(evidence, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if evidence["proof_state"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
