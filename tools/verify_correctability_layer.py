#!/usr/bin/env python3
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "correctability"
REPORT = ROOT / "brain_reports" / "correctability_layer_report.json"
CASES = FIXTURES / "v2" / "cases.json"
COMPENSATION_CASES = FIXTURES / "v2" / "compensation_cases.json"
AUTHORITIES = FIXTURES / "authority_records.json"
ALLOWED = {"pause", "deny", "revoke", "quarantine", "rollback", "redirect", "supersede", "compensate", "escalate"}
COMPENSATION_RESULTS = {"COMPLETE", "PARTIAL", "FAILED", "IMPOSSIBLE"}


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def evaluate(record: dict, authorities: dict) -> dict:
    required = {
        "correction_id", "transition_id", "subject_identity", "authority_reference",
        "intervention", "requested_scope", "detected_at", "authorization_latency_ms",
        "intervention_latency_ms", "irreversible_at", "pathway_reachable",
        "intervention_enforceable", "evidence_references"
    }
    predicates = {}
    errors = []
    missing = sorted(required - set(record))
    predicates["required_fields_present"] = not missing
    if missing:
        errors.append(f"missing_required:{','.join(missing)}")
        return {"decision": "DENY", "predicates": predicates, "errors": errors}

    authority = authorities.get(record["authority_reference"])
    predicates["authority_resolved"] = authority is not None
    if authority is None:
        errors.append("authority_unresolved")
        return {"decision": "DENY", "predicates": predicates, "errors": errors}

    detected = parse_time(record["detected_at"])
    irreversible = parse_time(record["irreversible_at"])
    completion = detected + timedelta(milliseconds=record["authorization_latency_ms"] + record["intervention_latency_ms"])

    predicates["subject_matches"] = authority["subject_identity"] == record["subject_identity"]
    predicates["authority_active"] = authority["revocation_state"] == "active"
    predicates["authority_time_valid"] = parse_time(authority["not_before"]) <= detected <= parse_time(authority["not_after"])
    predicates["intervention_globally_allowed"] = record["intervention"] in ALLOWED
    predicates["intervention_authorized"] = record["intervention"] in authority.get("allowed_interventions", [])
    predicates["scope_authorized"] = set(record["requested_scope"]).issubset(set(authority.get("scope", [])))
    predicates["pathway_reachable"] = record["pathway_reachable"] is True
    predicates["intervention_enforceable"] = record["intervention_enforceable"] is True
    predicates["evidence_present"] = bool(record["evidence_references"])
    predicates["before_irreversible_boundary"] = completion < irreversible

    compensation = record.get("compensation")
    compensation_mode = record["intervention"] == "compensate" and completion >= irreversible
    if compensation_mode:
        predicates["compensation_receipt_present"] = isinstance(compensation, dict)
        if isinstance(compensation, dict):
            required_comp = {"receipt_id", "compensation_type", "executed_at", "result", "residual_effects", "evidence_references"}
            predicates["compensation_fields_present"] = required_comp.issubset(compensation)
            predicates["compensation_result_valid"] = compensation.get("result") in COMPENSATION_RESULTS
            predicates["compensation_evidence_present"] = bool(compensation.get("evidence_references"))
            predicates["residual_effects_recorded"] = isinstance(compensation.get("residual_effects"), list)
        else:
            predicates["compensation_fields_present"] = False
            predicates["compensation_result_valid"] = False
            predicates["compensation_evidence_present"] = False
            predicates["residual_effects_recorded"] = False

    ignored_for_compensation = {"before_irreversible_boundary"} if compensation_mode else set()
    for name, value in predicates.items():
        if not value and name not in ignored_for_compensation:
            errors.append(name)

    if compensation_mode and not errors:
        result = compensation["result"]
        decision = "COMPENSATE" if result in {"COMPLETE", "PARTIAL"} else "DENY"
        if result in {"FAILED", "IMPOSSIBLE"}:
            errors.append(f"compensation_{result.lower()}")
    else:
        decision = "ADMIT" if not errors else "DENY"

    return {
        "decision": decision,
        "predicates": predicates,
        "errors": errors,
        "completion_at": completion.isoformat(),
        "irreversible_at": irreversible.isoformat(),
        "resolved_authority_id": authority["authority_id"],
        "mode": "post_irreversibility_compensation" if compensation_mode else "timely_correction",
        "compensation": compensation if compensation_mode else None,
    }


def main() -> int:
    authorities = json.loads(AUTHORITIES.read_text())
    case_specs = json.loads(CASES.read_text()) + json.loads(COMPENSATION_CASES.read_text())
    results = []
    all_passed = True
    for case in case_specs:
        result = evaluate(case["record"], authorities)
        passed = result["decision"] == case["expected"]
        all_passed = all_passed and passed
        results.append({"name": case["name"], "expected": case["expected"], "passed": passed, "result": result})

    report = {
        "layer": "governed_correctability",
        "state": "COMPLETE" if all_passed else "FAILED",
        "status": "pass" if all_passed else "fail",
        "verification_command": "python tools/verify_correctability_layer.py",
        "inputs": [str(CASES.relative_to(ROOT)), str(COMPENSATION_CASES.relative_to(ROOT)), str(AUTHORITIES.relative_to(ROOT))],
        "fixture_count": len(results),
        "passed_count": sum(1 for item in results if item["passed"]),
        "next_executable_task": "inspect-hosted-correctability-workflow" if all_passed else "repair-failing-correctability-case",
        "next_task_location": ".github/workflows/correctability-layer.yml" if all_passed else "tests/fixtures/correctability/v2/",
        "cases": results,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
