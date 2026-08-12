from __future__ import annotations

import argparse
import json
from pathlib import Path

from stegcore.steggate import AdmissibilityRequest
from stegcore.transaction_lifecycle import TransactionLedger, run_manifested_transaction


ROOT = Path(__file__).resolve().parents[1]


def load_request() -> AdmissibilityRequest:
    payload = json.loads((ROOT / "examples/steggate_allow_request.json").read_text(encoding="utf-8"))
    payload["candidate"]["actor_class"] = "system"
    payload["candidate"]["action"] = "write_record"
    payload["candidate"]["target"] = "vendor-payment"
    payload["candidate"]["scope"] = "evaluation"
    payload["candidate"]["parameters"] = {"amount": 420, "currency": "USD"}
    return AdmissibilityRequest.model_validate(payload)


def capability_surface() -> dict:
    return {
        "actions_exposed": ["write_record"],
        "execution_mode": "manual",
        "requires_governed_commit": True,
    }


def authority_resolution() -> dict:
    return {"status": "approved", "basis_invalidated_by_action": False}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run ordinary manifested transactions through canonical StegGate and retain replay/reconstruction evidence."
    )
    parser.add_argument(
        "--output",
        default="artifacts/manifested-transaction-demo.json",
        help="JSON output bundle",
    )
    parser.add_argument(
        "--ledger",
        default="artifacts/manifested-transaction-ledger.jsonl",
        help="Append-only transition ledger",
    )
    args = parser.parse_args()

    output_path = ROOT / args.output
    ledger_path = ROOT / args.ledger
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    if ledger_path.exists():
        ledger_path.unlink()

    ledger = TransactionLedger(ledger_path)

    t0_request = load_request()
    t0 = run_manifested_transaction(
        t0_request,
        lambda: {"payment": "committed", "amount": 420},
        input_data={"amount": 420, "currency": "USD", "phase": "T0"},
        source="sdk:manifested-boundary-demo",
        subject="evaluation:longitudinal-boundary",
        ledger=ledger,
        metadata={"case": "historically-valid-authorization"},
        capability_surface=capability_surface(),
        authority_resolution=authority_resolution(),
    )

    t1_request = load_request()
    t1_request.execution.policy_current = False
    t1 = run_manifested_transaction(
        t1_request,
        lambda: {"payment": "must-not-execute"},
        input_data={
            "amount": 420,
            "currency": "USD",
            "phase": "T1",
            "policy_current": False,
        },
        source="sdk:manifested-boundary-demo",
        subject="evaluation:longitudinal-boundary",
        ledger=ledger,
        metadata={"case": "current-admissibility-divergence"},
        capability_surface=capability_surface(),
        authority_resolution=authority_resolution(),
    )

    bundle = {
        "artifact_type": "stegcore.manifested_transaction_demo",
        "schema_version": "1.0",
        "canonical_runtime_identity": "stegverse:steggate:canonical:three-layer:v1",
        "canonical_evaluator": "stegcore.three_layer.evaluate_three_layer",
        "cases": {
            "T0": t0.model_dump(mode="json"),
            "T1": t1.model_dump(mode="json"),
        },
        "reconstruction": {
            "T0": ledger.reconstruct(t0.transaction_id),
            "T1": ledger.reconstruct(t1.transaction_id),
        },
        "claims": {
            "t0_historical_allow_preserved": t0.replay.expected_disposition == "ALLOW",
            "t0_executor_invoked": t0.replay.expected_executor_invoked is True,
            "t1_current_execution_refused": t1.replay.expected_disposition == "DENY",
            "t1_executor_not_invoked": t1.replay.expected_executor_invoked is False,
            "both_receipt_chains_verified": t0.chain_verified and t1.chain_verified,
            "demo_specific_evaluator_used": False,
        },
    }

    output_path.write_text(json.dumps(bundle, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(bundle["claims"], indent=2, sort_keys=True))
    print(f"bundle={output_path}")
    print(f"ledger={ledger_path}")

    return 0 if all(
        value is True
        for key, value in bundle["claims"].items()
        if key != "demo_specific_evaluator_used"
    ) and bundle["claims"]["demo_specific_evaluator_used"] is False else 1


if __name__ == "__main__":
    raise SystemExit(main())
