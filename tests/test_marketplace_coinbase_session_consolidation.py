from scripts.validate_marketplace_coinbase_session_consolidation import validate


def test_session_consolidation_is_archive_safe() -> None:
    receipt = validate()
    assert receipt["state"] == "COMPLETE", receipt["findings"]
    assert receipt["requirements_transferred"] == receipt["requirements_required"] == 8
    assert receipt["claims_recorded"] == receipt["claims_required"] == 6
    assert receipt["canonical_tasks_recorded"] == receipt["canonical_tasks_required"] == 6
    assert receipt["unique_execution_responsibility_remaining"] is False
    assert receipt["deleting_session_impairs_execution"] is False
    assert receipt["publication_authority"] == "NOT_GRANTED"
    assert receipt["release_authority"] == "NOT_GRANTED"
    assert receipt["execution_authority"] == "NOT_GRANTED"
    assert receipt["live_authority"] == "NOT_GRANTED"
    assert receipt["receipt_digest"].startswith("sha256:")
