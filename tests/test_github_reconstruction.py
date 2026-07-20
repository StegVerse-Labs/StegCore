from stegcore.github_reconstruction import evaluate_github_reconstruction


def valid_report():
    return {
        "scope": "default_branch_snapshot_only",
        "history_complete": False,
        "temporary_source_destroyed": True,
        "source_content_retained": False,
        "source_content_uploaded": False,
        "manual_action_required": False,
        "production_mutation_allowed": False,
        "execution_authority": False,
        "traffic_cutover_authority": False,
        "cancellation_authority": False,
        "provider_retirement_authority": False,
        "continuity_receipt_minted": False,
        "records": [{
            "repository": "StegVerse-Labs/example",
            "state": "PASS_DEFAULT_BRANCH_RECONSTRUCTION",
            "source_commit": "abc",
            "source_tree": "def",
            "source_tree_listing_hash": "1",
            "archive_sha256": "2",
            "reconstructed_manifest_hash": "3",
            "reconstructed_file_count": 1,
            "record_hash": "4",
            "temporary_source_destroyed": True,
            "source_content_retained": False,
            "source_content_uploaded": False,
            "manual_action_required": False,
            "production_mutation_allowed": False,
            "execution_authority": False,
            "traffic_cutover_authority": False,
            "cancellation_authority": False,
            "provider_retirement_authority": False,
            "continuity_receipt_minted": False,
        }],
    }


def test_allows_valid_bounded_reconstruction_evidence():
    result = evaluate_github_reconstruction(valid_report())
    assert result["decision"] == "ALLOW_RECONSTRUCTION_EVIDENCE_ONLY"
    assert result["passed_repository_count"] == 1
    assert result["execution_authority"] is False


def test_denies_cleanup_failure():
    report = valid_report()
    report["records"][0]["temporary_source_destroyed"] = False
    result = evaluate_github_reconstruction(report)
    assert result["decision"] == "DENY_RECONSTRUCTION_EVIDENCE"
    assert any("cleanup_not_proven" in blocker for blocker in result["blockers"])


def test_denies_hidden_authority():
    report = valid_report()
    report["records"][0]["traffic_cutover_authority"] = True
    result = evaluate_github_reconstruction(report)
    assert result["decision"] == "DENY_RECONSTRUCTION_EVIDENCE"
    assert any("traffic_cutover_authority" in blocker for blocker in result["blockers"])


def test_denies_empty_pass_record():
    report = valid_report()
    report["records"][0]["reconstructed_file_count"] = 0
    result = evaluate_github_reconstruction(report)
    assert result["decision"] == "DENY_RECONSTRUCTION_EVIDENCE"
