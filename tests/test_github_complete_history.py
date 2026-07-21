from stegcore.github_complete_history import evaluate_github_complete_history


def clean_document():
    return {
        "records": [{
            "full_name": "StegVerse-Labs/Governance",
            "state": "PASS_COMPLETE_HISTORY_EXPORT",
            "ref_count": 3,
            "refs_hash": "a" * 64,
            "bundle_ref_count": 3,
            "bundle_refs_hash": "b" * 64,
            "bundle_hash": "c" * 64,
            "object_count": 10,
            "commit_count": 4,
            "adjacent_state": {
                "releases_hash": "d" * 64,
                "tags_hash": "e" * 64,
                "issues_hash": "f" * 64,
                "pull_requests_hash": "1" * 64,
            },
            "record_hash": "2" * 64,
            "source_material_retained": False,
            "bundle_retained": False,
            "secret_material_included": False,
            "manual_action_required": False,
            "production_mutation_allowed": False,
            "execution_authority": False,
            "traffic_cutover_authority": False,
            "cancellation_authority": False,
            "provider_retirement_authority": False,
            "continuity_receipt_minted": False,
        }],
        "source_material_retained": False,
        "bundle_retained": False,
        "secret_material_included": False,
        "manual_action_required": False,
        "production_mutation_allowed": False,
        "execution_authority": False,
        "traffic_cutover_authority": False,
        "cancellation_authority": False,
        "provider_retirement_authority": False,
        "continuity_receipt_minted": False,
    }


def test_allows_complete_history_evidence_only():
    result = evaluate_github_complete_history(clean_document())
    assert result["decision"] == "ALLOW_COMPLETE_HISTORY_EVIDENCE_ONLY"
    assert result["execution_authority"] is False


def test_denies_retained_bundle():
    document = clean_document()
    document["records"][0]["bundle_retained"] = True
    assert evaluate_github_complete_history(document)["decision"] == "DENY"


def test_denies_missing_adjacent_hash():
    document = clean_document()
    document["records"][0]["adjacent_state"].pop("issues_hash")
    assert evaluate_github_complete_history(document)["decision"] == "DENY"


def test_denies_empty_history():
    document = clean_document()
    document["records"][0]["commit_count"] = 0
    assert evaluate_github_complete_history(document)["decision"] == "DENY"


def test_denies_missing_records():
    document = clean_document()
    document.pop("records")
    assert evaluate_github_complete_history(document)["decision"] == "DENY"
