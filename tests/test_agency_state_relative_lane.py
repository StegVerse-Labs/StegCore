from scripts.run_agency_state_relative_lane import run_lane


def test_agency_state_relative_lane_demonstrates_state_relative_validity_and_consequential_agency():
    result = run_lane()

    assert result["result"] == "PASS"
    cases = {case["case_id"]: case for case in result["cases"]}

    assert cases["CASE-1-HISTORICAL-VALIDITY"]["disposition"] == "ALLOW"
    assert cases["CASE-2-STALE-APPLICABILITY"]["disposition"] in {"DENY", "FAIL_CLOSED"}
    assert cases["CASE-3-CONSEQUENTIAL-AGENCY"]["disposition"] == "ALLOW"

    consequence = result["consequence"]
    assert consequence["historical_record"] == "PRESERVED"
    assert consequence["historical_authorization_status"] == "VALID_AS_S0_EVIDENCE"
    assert consequence["present_applicability"] == "REQUIRES_RENEWED_DETERMINATION_AFTER_S0_TO_S1"
    assert consequence["human_direction_effect"] == "MATERIAL_OPERATIVE_PATH_CHANGE"
    assert consequence["final_operational_state"] == "RENEWED_DETERMINATION_REQUIRED"

    assert all(case["canonical_three_layer_receipt_hash"] for case in result["cases"])
    assert all(case["decision_state_hash"] for case in result["cases"])
