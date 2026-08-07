from stegcore.criterion_contestability import evaluate_criterion_contestability


def base_candidate(**overrides):
    candidate = {
        "consequence_bearing": True,
        "trajectory_ids": ["trajectory-a", "trajectory-b"],
        "selected_criterion_id": "criterion-1",
        "criterion_provenance_bound": True,
        "criterion_contestable_at_commit": True,
        "criterion_authority_current": True,
        "relation_governed": True,
        "authority_current": True,
        "continuity_current": True,
        "governing_conditions_current": True,
        "consequence_attributable": True,
        "consequence_reconstructable": True,
        "consent_or_standing_required": False,
        "consent_or_standing_current": None,
    }
    candidate.update(overrides)
    return candidate


def test_parallel_visible_but_unbound_provenance_denies():
    result = evaluate_criterion_contestability(
        base_candidate(criterion_provenance_bound=False)
    )
    assert result["decision"] == "DENY"
    assert result["trajectory_parallelity_preserved"] is True
    assert result["synthetic_consensus_used"] is False
    assert "criterion_provenance_unbound" in result["reasons"]


def test_contestability_disabled_before_consequence_denies():
    result = evaluate_criterion_contestability(
        base_candidate(criterion_contestable_at_commit=False)
    )
    assert result["decision"] == "DENY"
    assert "criterion_not_contestable_at_commit" in result["reasons"]


def test_contestable_but_stale_criterion_authority_denies():
    result = evaluate_criterion_contestability(
        base_candidate(criterion_authority_current=False)
    )
    assert result["decision"] == "DENY"
    assert result["contestability_used_as_admissibility"] is False
    assert "criterion_authority_not_current" in result["reasons"]


def test_contestable_but_required_consent_missing_denies():
    result = evaluate_criterion_contestability(
        base_candidate(
            consent_or_standing_required=True,
            consent_or_standing_current=False,
        )
    )
    assert result["decision"] == "DENY"
    assert "consent_or_standing_not_current" in result["reasons"]


def test_parallel_contest_with_unresolved_authority_defers_not_consensus():
    result = evaluate_criterion_contestability(
        base_candidate(criterion_authority_current=None)
    )
    assert result["decision"] == "DEFER"
    assert result["admissible"] is False
    assert result["synthetic_consensus_used"] is False
    assert "unresolved:criterion_authority_current" in result["reasons"]


def test_all_current_allows_without_conveying_execution_authority():
    result = evaluate_criterion_contestability(base_candidate())
    assert result["decision"] == "ALLOW"
    assert result["admissible"] is True
    assert result["orientation_used_as_authority"] is False
    assert result["execution_authority_conferred"] is False


def test_orientation_only_can_proceed_but_is_not_execution_authority():
    result = evaluate_criterion_contestability(
        base_candidate(
            consequence_bearing=False,
            criterion_provenance_bound=None,
            criterion_contestable_at_commit=None,
            criterion_authority_current=None,
            relation_governed=None,
            authority_current=None,
            continuity_current=None,
            governing_conditions_current=None,
            consequence_attributable=None,
            consequence_reconstructable=None,
        )
    )
    assert result["decision"] == "ALLOW"
    assert result["admissible"] is True
    assert result["execution_authority_conferred"] is False
    assert result["reasons"] == ["orientation_or_coordination_only"]
