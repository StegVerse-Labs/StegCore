from datetime import datetime, timezone

from stegcore.gadi_defense_planner import plan_defensive_intervention


NOW = datetime(2026, 9, 7, 23, 30, tzinfo=timezone.utc)


def _observation(
    *,
    observation_id: str = "obs-1",
    threat_state: str = "ACTIVE",
    confidence: float = 0.90,
    expires_at: str = "2026-09-08T00:30:00Z",
    unknowns: list[str] | None = None,
):
    return {
        "schema": "stegos.autonomous_threat_observation.v1",
        "task_id": "GADI-001",
        "cosv": "10100000100000",
        "observation_id": observation_id,
        "observed_at": "2026-09-07T23:20:00Z",
        "observer_principal_id": "observer-1",
        "acting_subject": {
            "subject_id": "subject-1",
            "subject_type": "GOVERNED_AGENT",
            "binding_state": "BOUND",
        },
        "threat_state": threat_state,
        "evidence_refs": [f"evidence:{observation_id}"],
        "confidence": confidence,
        "uncertainty": {
            "present": bool(unknowns),
            "material_unknowns": unknowns or [],
        },
        "freshness": {
            "observed_at": "2026-09-07T23:20:00Z",
            "expires_at": expires_at,
        },
        "authority_effect": "NONE_OBSERVATION_ONLY",
    }


def _capability(
    capability_id: str,
    action: str,
    *,
    destructiveness: str = "NON_DESTRUCTIVE",
    reversibility: str = "REVERSIBLE",
    target_classes: list[str] | None = None,
):
    return {
        "schema": "stegos.governed_intervention_capability.v1",
        "capability_id": capability_id,
        "owner": "StegVerse-Labs/TVC",
        "credential_authority": "TV/TVC",
        "preauthorization_required": True,
        "control_surface": "controlled-test-surface",
        "reversibility": reversibility,
        "destructiveness": destructiveness,
        "production_eligible": True,
        "simulation_eligible": True,
        "authorization_evidence_ref": "tvc:evidence:1",
        "authority_effect": "NONE_UNTIL_INTR_ADMISSION_AND_RUNTIME_BINDING",
        "scope": {
            "target_classes": target_classes or ["GOVERNED_AGENT"],
            "allowed_actions": [action],
            "forbidden_actions": [],
        },
        "freshness": {
            "issued_at": "2026-09-07T22:00:00Z",
            "expires_at": "2026-09-08T22:00:00Z",
        },
    }


def test_positive_path_selects_least_destructive_effective_candidate():
    capabilities = [
        _capability(
            "cap-isolate",
            "ISOLATE",
            destructiveness="STATE_MUTATING_REVERSIBLE",
        ),
        _capability("cap-rate", "RATE_LIMIT"),
    ]

    result = plan_defensive_intervention(
        [_observation()],
        capabilities,
        governed_principal_id="principal-1",
        now=NOW,
    )

    assert result.state == "PLANNED_PENDING_ADMISSION"
    assert result.threat_state == "ACTIVE"
    assert result.selected_request is not None
    assert result.selected_request["intervention_class"] == "RATE_LIMIT"
    assert result.selected_request["required_capability_id"] == "cap-rate"
    assert result.selected_request["admission"]["state"] == "PENDING"
    assert result.selected_request["model_output_authority"] == "NONE"
    assert result.selected_request["authority_effect"] == "ADMISSION_REQUIRED_BEFORE_ACTUATION"
    assert result.authority_effect == "NONE_PLANNING_ONLY"


def test_material_uncertainty_requires_review_and_preserves_unknowns():
    result = plan_defensive_intervention(
        [_observation(unknowns=["identity-linkage-not-final"])],
        [_capability("cap-rate", "RATE_LIMIT")],
        governed_principal_id="principal-1",
        now=NOW,
    )

    assert result.state == "REVIEW_REQUIRED"
    assert result.selected_request is None
    assert result.uncertainty == ("identity-linkage-not-final",)
    assert result.findings == ("material_uncertainty_requires_review",)


def test_stale_observation_fails_closed():
    result = plan_defensive_intervention(
        [_observation(expires_at="2026-09-07T23:00:00Z")],
        [_capability("cap-rate", "RATE_LIMIT")],
        governed_principal_id="principal-1",
        now=NOW,
    )

    assert result.state == "FAIL_CLOSED"
    assert result.selected_request is None
    assert "stale_or_invalid_observation" in result.findings


def test_over_scoped_or_wrong_target_capability_fails_closed():
    result = plan_defensive_intervention(
        [_observation()],
        [
            _capability(
                "cap-rate-other-target",
                "RATE_LIMIT",
                target_classes=["UNRELATED_THIRD_PARTY_SYSTEM"],
            )
        ],
        governed_principal_id="principal-1",
        now=NOW,
    )

    assert result.state == "FAIL_CLOSED"
    assert result.selected_request is None
    assert result.findings == ("no_in_scope_preauthorized_capability",)


def test_low_confidence_path_does_not_produce_intervention_request():
    result = plan_defensive_intervention(
        [_observation(threat_state="CREDIBLE", confidence=0.40)],
        [_capability("cap-rate", "RATE_LIMIT")],
        governed_principal_id="principal-1",
        now=NOW,
    )

    assert result.state == "REVIEW_REQUIRED"
    assert result.selected_request is None
    assert result.findings == ("credible_threshold_not_met",)


def test_provenance_is_retained_and_request_is_deterministic():
    observations = [
        _observation(observation_id="obs-b"),
        _observation(observation_id="obs-a"),
    ]
    capabilities = [_capability("cap-rate", "RATE_LIMIT")]

    first = plan_defensive_intervention(
        observations,
        capabilities,
        governed_principal_id="principal-1",
        now=NOW,
    )
    second = plan_defensive_intervention(
        list(reversed(observations)),
        capabilities,
        governed_principal_id="principal-1",
        now=NOW,
    )

    assert first.observation_refs == ("obs-a", "obs-b")
    assert first.evidence_refs == ("evidence:obs-a", "evidence:obs-b")
    assert first.selected_request is not None
    assert second.selected_request is not None
    assert first.selected_request["receipt_correlation_id"] == second.selected_request["receipt_correlation_id"]
    assert first.selected_request["request_id"] == second.selected_request["request_id"]
