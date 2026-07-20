from stegcore.ephemeral_backend import evaluate_ephemeral_backend_report


def passing_report():
    return {
        "report_hash": "abc",
        "manual_action_required": False,
        "network_access_used": False,
        "provider_credentials_used": False,
        "production_state_used": False,
        "production_mutation_allowed": False,
        "execution_authority": False,
        "traffic_cutover_authority": False,
        "cancellation_authority": False,
        "provider_retirement_authority": False,
        "continuity_receipt_minted": False,
        "results": [{
            "provider_id": "github",
            "state": "PASS_EPHEMERAL_BACKEND",
            "manual_action_required": False,
            "network_access_used": False,
            "provider_credentials_used": False,
            "production_state_used": False,
            "production_mutation_allowed": False,
            "execution_authority": False,
            "traffic_cutover_authority": False,
            "cancellation_authority": False,
            "provider_retirement_authority": False,
            "continuity_receipt_minted": False,
            "checks": {
                "health_check_passed": True,
                "import_hash_equivalent": True,
                "export_hash_equivalent": True,
                "mutation_detected": True,
                "rollback_hash_equivalent": True,
                "network_access_used": False,
                "provider_credentials_used": False,
                "production_state_used": False,
            },
        }],
    }


def test_allows_only_isolated_evidence():
    decision = evaluate_ephemeral_backend_report(passing_report())
    assert decision["outcome"] == "ALLOW_ISOLATED_EVIDENCE_ONLY"
    assert decision["production_mutation_allowed"] is False
    assert decision["continuity_receipt_minted"] is False


def test_denies_hidden_authority():
    report = passing_report()
    report["results"][0]["traffic_cutover_authority"] = True
    decision = evaluate_ephemeral_backend_report(report)
    assert decision["outcome"] == "DENY_EPHEMERAL_EVIDENCE"
    assert any("traffic_cutover_authority" in value for value in decision["blockers"])


def test_denies_failed_rollback():
    report = passing_report()
    report["results"][0]["checks"]["rollback_hash_equivalent"] = False
    decision = evaluate_ephemeral_backend_report(report)
    assert decision["outcome"] == "DENY_EPHEMERAL_EVIDENCE"
    assert any("rollback_hash_equivalent" in value for value in decision["blockers"])
