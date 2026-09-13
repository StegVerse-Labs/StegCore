#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from stegcore.cge_decision_issuer import issue_service_decision


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"object_required:{path}")
    return value


def write_once(path: Path, value: dict) -> None:
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_text(encoding="utf-8") != rendered:
            raise RuntimeError(f"write_once_collision:{path}")
        return
    temp = path.with_name("." + path.name + ".tmp")
    temp.write_text(rendered, encoding="utf-8")
    os.replace(temp, path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Issue one fail-closed StegCore CGE service decision without executing the transition.")
    parser.add_argument("--route", type=Path, required=True)
    parser.add_argument("--authority-evidence", type=Path, required=True)
    parser.add_argument("--admissibility-request", type=Path, required=True)
    parser.add_argument("--subject-request-ref", required=True)
    parser.add_argument("--repository-state-sha256", required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--ttl-seconds", type=int, default=600)
    args = parser.parse_args()
    try:
        result = issue_service_decision(
            route=load(args.route),
            authority_evidence=load(args.authority_evidence),
            admissibility_request=load(args.admissibility_request),
            subject_request_ref=args.subject_request_ref,
            repository_state_sha256=args.repository_state_sha256,
            ttl_seconds=args.ttl_seconds,
        )
        root = args.output_root.expanduser().resolve()
        decision = result["cge_decision"]
        request_id = decision["request_id"]
        safe_id = "".join(ch if ch.isalnum() or ch in "-_." else "-" for ch in request_id)
        authority_ref = root / f"{safe_id}.authority-context.json"
        commit_ref = root / f"{safe_id}.commit-time-admissibility.json"
        decision_ref = root / f"{safe_id}.cge-decision.json"
        evaluation_ref = root / f"{safe_id}.stegcore-evaluation.json"
        write_once(authority_ref, result["authority_context_receipt"])
        write_once(commit_ref, result["commit_time_admissibility_receipt"])
        write_once(decision_ref, decision)
        write_once(evaluation_ref, result["evaluation"])
        receipt = {
            "schema": "stegcore.cge_decision_issuer_cli_receipt/v1",
            "state": result["state"],
            "request_id": request_id,
            "authority_context_receipt_ref": str(authority_ref),
            "commit_time_admissibility_receipt_ref": str(commit_ref),
            "cge_decision_ref": str(decision_ref),
            "stegcore_evaluation_ref": str(evaluation_ref),
            "execution_performed": False,
            "canonical_state_mutated": False,
            "transition_executor": "Interlock/InTr",
            "master_records_custody_required": True,
            "credential_authority": "TV/TVC",
            "authority_effect": "CGE_DECISION_ISSUED_ONLY"
        }
        write_once(root / f"{safe_id}.issuer-receipt.json", receipt)
        print(json.dumps(receipt, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({
            "schema": "stegcore.cge_decision_issuer_cli_receipt/v1",
            "state": "CGE_REVIEW_BLOCKED",
            "reason": f"{type(exc).__name__}:{exc}",
            "execution_performed": False,
            "canonical_state_mutated": False,
            "authority_effect": "NONE_FAIL_CLOSED"
        }, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
