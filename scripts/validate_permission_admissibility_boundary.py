#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "permission-admissibility-boundary.v1.json"

REQUIRED_TRUE = (
    "authority_current",
    "continuity_current",
    "governing_conditions_current",
    "consequence_attributable",
    "consequence_reconstructable",
)


def evaluate_case(case_input):
    if not isinstance(case_input.get("consequence_bearing"), bool):
        return {"decision": "DEFER", "admissible": False, "execution_authority": False}

    if not case_input["consequence_bearing"]:
        return {"decision": "ALLOW", "admissible": True, "execution_authority": False}

    required_values = [case_input.get(name) for name in REQUIRED_TRUE]
    if case_input.get("consent_or_standing_required") is True:
        required_values.append(case_input.get("consent_or_standing_current"))

    if any(value is None for value in required_values):
        return {"decision": "DEFER", "admissible": False, "execution_authority": False}

    if all(value is True for value in required_values):
        return {"decision": "ALLOW", "admissible": True, "execution_authority": False}

    return {"decision": "DENY", "admissible": False, "execution_authority": False}


def validate_contract(contract):
    errors = []
    if contract.get("contract_id") != "PA-001":
        errors.append("contract_id must be PA-001")
    if contract.get("execution_authority") is not False:
        errors.append("contract must never grant execution authority")
    if contract.get("fail_closed") is not True:
        errors.append("contract must fail closed")

    required = set(contract.get("required_predicates_for_consequence_bearing_transition", []))
    missing = set(REQUIRED_TRUE) - required
    if missing:
        errors.append(f"missing required predicates: {sorted(missing)}")

    cases = contract.get("cases")
    if not isinstance(cases, list) or len(cases) < 6:
        errors.append("at least six semantic cases are required")
        return errors

    ids = set()
    for case in cases:
        case_id = case.get("id")
        if not case_id or case_id in ids:
            errors.append(f"invalid or duplicate case id: {case_id!r}")
            continue
        ids.add(case_id)
        actual = evaluate_case(case.get("input", {}))
        expected = case.get("expected", {})
        for key, expected_value in expected.items():
            if actual.get(key) != expected_value:
                errors.append(
                    f"{case_id}: {key} expected {expected_value!r}, got {actual.get(key)!r}"
                )

    permission_present_denied = any(
        c.get("input", {}).get("permission_present") is True
        and c.get("expected", {}).get("admissible") is False
        for c in cases
    )
    no_permission_allowed = any(
        c.get("input", {}).get("permission_present") is False
        and c.get("input", {}).get("consequence_bearing") is True
        and c.get("expected", {}).get("admissible") is True
        for c in cases
    )
    if not permission_present_denied:
        errors.append("must prove permission-present can still be inadmissible")
    if not no_permission_allowed:
        errors.append("must prove permission absence does not itself imply inadmissibility")

    return errors


def main():
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    errors = validate_contract(contract)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print("PERMISSION_ADMISSIBILITY_BOUNDARY=PASS")
    print(f"cases={len(contract['cases'])}")


if __name__ == "__main__":
    main()
