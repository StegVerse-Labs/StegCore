from stegcore.successor_harness import evaluate_successor_harness


def base_report():
    return {
        "report_hash": "a" * 64,
        "manual_action_required": False,
        "production_mutation_allowed": False,
        "traffic_cutover_authority": False,
        "cancellation_authority": False,
        "provider_retirement_authority": False,
        "execution_authority": False,
        "results": [
            {
                "provider_id": "render",
                "state": "PASS_NON_PRODUCTION_HARNESS",
                "manual_action_required": False,
                "production_mutation_allowed": False,
                "traffic_cutover_authority": False,
                "cancellation_authority": False,
                "provider_retirement_authority": False,
                "execution_authority": False,
            }
        ],
    }


def test_allows_non_production_evidence_only():
    receipt = evaluate_successor_harness(base_report())
    assert receipt["decision"] == "ALLOW_NON_PRODUCTION_EVIDENCE_ONLY"
    assert receipt["production_authority"] is False
    assert receipt["receipt_minting_authority"] is False


def test_blocks_incomplete_provider():
    report = base_report()
    report["results"][0]["state"] = "BLOCKED_PREREQUISITES"
    receipt = evaluate_successor_harness(report)
    assert receipt["decision"] == "DENY"
    assert receipt["blocked_providers"] == ["render"]


def test_rejects_hidden_authority():
    report = base_report()
    report["results"][0]["traffic_cutover_authority"] = True
    receipt = evaluate_successor_harness(report)
    assert receipt["decision"] == "DENY"
    assert any("traffic_cutover_authority" in reason for reason in receipt["reason_codes"])


def test_receipt_is_deterministic():
    report = base_report()
    assert evaluate_successor_harness(report) == evaluate_successor_harness(report)
