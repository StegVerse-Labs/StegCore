from stegcore.manifold_governance import PopulationTransition, govern_manifold_action, plan_manifold
from stegcore.steggate import (
    AdmissibilityRequest,
    ApprovalState,
    Candidate,
    CapabilityState,
    ContinuityState,
    ExecutionState,
    JudgmentState,
    SignalState,
)


def allowed_request(*, target: str, value: int = 1) -> AdmissibilityRequest:
    return AdmissibilityRequest(
        candidate=Candidate(
            actor_class="system",
            action="write_record",
            target=target,
            scope="manifold-test",
            parameters={"value": value},
        ),
        judgment=JudgmentState(
            refusal_available=True,
            operator_recoverability="available",
            workload_state="supported",
            time_pressure="normal",
            isolation_state="supported",
            evidence_refs=["judgment:e1"],
        ),
        signal=SignalState(
            admitted_signal_refs=["signal:s1"],
            transformations=["test:v1"],
            missing_inputs=[],
            uncertainty_state="bounded",
            reference_state_hash="state:1",
            expected_reference_state_hash="state:1",
            reconstruction_available=True,
            transformation_provenance_complete=True,
        ),
        execution=ExecutionState(
            actor_authority_current=True,
            policy_current=True,
            delegation_current=True,
            evidence_current=True,
            affected_entity_conditions_represented=True,
            recoverability_profile="recoverable",
            validity_window_open=True,
            policy_ref="policy:p1",
            delegation_ref="delegation:d1",
            evidence_refs=["execution:e1"],
        ),
        capability=CapabilityState(allowed=True),
        continuity=ContinuityState(
            required=True,
            previous_receipt_verified=True,
            previous_receipt_hash="receipt:r0",
        ),
        approval=ApprovalState(required=False),
        permission_present=False,
    )


def test_equivalent_population_permutations_have_same_plan_hash():
    a = PopulationTransition(
        transition_id="T-A",
        base_manifold_hash="M0",
        request=allowed_request(target="record:a"),
    )
    b = PopulationTransition(
        transition_id="T-B",
        base_manifold_hash="M0",
        request=allowed_request(target="record:b"),
        depends_on=("T-A",),
    )
    forward = plan_manifold([a, b])
    reverse = plan_manifold([b, a])
    assert forward.state == "READY"
    assert reverse.state == "READY"
    assert forward.ordered_transition_ids == ("T-A", "T-B")
    assert forward.plan_hash == reverse.plan_hash
    assert forward.eligible_transition_ids == ("T-A", "T-B")


def test_mixed_base_manifold_fails_closed_before_canonical_evaluation():
    result = plan_manifold([
        PopulationTransition("T-A", "M0", allowed_request(target="record:a")),
        PopulationTransition("T-B", "M1", allowed_request(target="record:b")),
    ])
    assert result.state == "FAIL_CLOSED"
    assert result.reasons == ("MIXED_OR_STALE_BASE_MANIFOLD",)
    assert result.commit_performed is False
    assert result.standings == ()


def test_dependency_cycle_fails_closed():
    result = plan_manifold([
        PopulationTransition("T-A", "M0", allowed_request(target="record:a"), depends_on=("T-B",)),
        PopulationTransition("T-B", "M0", allowed_request(target="record:b"), depends_on=("T-A",)),
    ])
    assert result.state == "FAIL_CLOSED"
    assert result.reasons == ("DEPENDENCY_CYCLE",)
    assert result.eligible_transition_ids == ()


def test_canonical_deny_is_preserved_and_never_promoted_by_population_observations():
    denied = allowed_request(target="record:denied")
    denied.execution.policy_current = False
    result = plan_manifold([
        PopulationTransition(
            "T-DENY",
            "M0",
            denied,
            observations={
                "coherence": 1.0,
                "gradient_relation": "reinforcing",
                "classifier_confidence": 0.999,
            },
        )
    ])
    standing = result.standings[0]
    assert standing.disposition == "DENY"
    assert standing.derived_observations_authoritative is False
    assert result.derived_observations_authoritative is False
    assert result.eligible_transition_ids == ()
    assert result.commit_performed is False
    assert result.authority_effect == "NONE_PLANNING_ONLY"


def test_two_allowed_conflicting_transitions_require_resolution_not_implicit_choice():
    result = plan_manifold([
        PopulationTransition(
            "T-A",
            "M0",
            allowed_request(target="record:a"),
            conflicts_with=("T-B",),
        ),
        PopulationTransition(
            "T-B",
            "M0",
            allowed_request(target="record:b"),
            conflicts_with=("T-A",),
        ),
    ])
    assert result.state == "REVIEW_REQUIRED"
    assert result.conflict_pairs == (("T-A", "T-B"),)
    assert result.eligible_transition_ids == ()
    assert any(reason.startswith("ALLOW_CONFLICT_REQUIRES_RESOLUTION") for reason in result.reasons)
    assert result.commit_performed is False


def test_atomic_bundle_with_denied_member_is_not_commit_eligible():
    denied = allowed_request(target="record:b")
    denied.execution.actor_authority_current = False
    result = plan_manifold([
        PopulationTransition(
            "T-A",
            "M0",
            allowed_request(target="record:a"),
            bundle_id="B-1",
        ),
        PopulationTransition(
            "T-B",
            "M0",
            denied,
            bundle_id="B-1",
        ),
    ])
    assert len(result.bundles) == 1
    bundle = result.bundles[0]
    assert bundle.bundle_id == "B-1"
    assert bundle.disposition == "DENY"
    assert bundle.eligible_for_commit is False
    assert result.eligible_transition_ids == ()


def test_dependency_on_review_stays_review_required_and_planner_never_executes():
    review = allowed_request(target="record:review")
    review.approval.required = True
    result = plan_manifold([
        PopulationTransition("T-REVIEW", "M0", review),
        PopulationTransition(
            "T-DEPENDENT",
            "M0",
            allowed_request(target="record:dependent"),
            depends_on=("T-REVIEW",),
        ),
    ])
    assert result.state == "REVIEW_REQUIRED"
    assert any(row.disposition == "REVIEW" for row in result.standings)
    assert "T-DEPENDENT" not in result.eligible_transition_ids
    assert result.commit_performed is False
    assert result.continuity_receipt_minted is False
    assert result.canonical_evaluator == "stegcore.steggate.evaluate_admissibility"
    assert result.canonical_evaluator_unchanged is True


def test_unknown_dependency_reference_fails_closed():
    result = plan_manifold([
        PopulationTransition(
            "T-A",
            "M0",
            allowed_request(target="record:a"),
            depends_on=("T-MISSING",),
        )
    ])
    assert result.state == "FAIL_CLOSED"
    assert result.reasons[0].startswith("UNKNOWN_DEPENDENCY_REFERENCE:T-A:T-MISSING")

def test_governed_manifold_action_allows_independent_machine_speed_paths_while_review_holds_boundary():
    review = allowed_request(target="record:protected")
    review.approval.required = True
    action = govern_manifold_action(
        [
            PopulationTransition("T-A", "M0", allowed_request(target="record:a")),
            PopulationTransition(
                "T-B",
                "M0",
                allowed_request(target="record:b"),
                depends_on=("T-A",),
            ),
            PopulationTransition("T-REVIEW", "M0", review),
            PopulationTransition(
                "T-AFTER-REVIEW",
                "M0",
                allowed_request(target="record:after-review"),
                depends_on=("T-REVIEW",),
            ),
        ],
        authority_boundary_refs=("authority:human-review", "policy:manifold-v1"),
    )

    assert action.state == "REVIEWABLE"
    assert action.continue_transition_ids == ("T-A", "T-B")
    assert action.review_transition_ids == ("T-REVIEW",)
    assert action.held_transition_ids == ("T-AFTER-REVIEW",)
    assert action.denied_transition_ids == ()
    assert action.fail_closed_transition_ids == ()
    assert action.external_execution_performed is False
    assert action.continuity_receipt_minted is False
    assert action.human_review_timing_is_authority is False
    assert action.wall_clock_is_governance_authority is False
    assert action.heartbeat_is_governance_authority is False
    assert action.machine_speed_internal_transitions_may_continue is True
    assert action.protected_boundary_crossing_requires_external_authority is True

    projection = action.reviewable_projection
    assert projection["governance_invariants"]["linear_transition_path_required"] is False
    assert projection["governance_invariants"]["manifold_reviewable_as_projection"] is True
    assert projection["governance_invariants"]["machine_speed_internal_transitions_may_continue_inside_existing_authority"] is True
    assert projection["governance_invariants"]["protected_boundary_crossing_requires_external_authority"] is True
    assert projection["authority_boundary_refs"] == ["authority:human-review", "policy:manifold-v1"]


def test_governed_manifold_action_preserves_deny_and_never_advances_failed_population():
    denied = allowed_request(target="record:denied")
    denied.execution.policy_current = False
    action = govern_manifold_action(
        [
            PopulationTransition("T-ALLOW", "M0", allowed_request(target="record:allow")),
            PopulationTransition("T-DENY", "M0", denied),
        ]
    )
    assert action.state == "CONTINUE"
    assert action.continue_transition_ids == ("T-ALLOW",)
    assert action.denied_transition_ids == ("T-DENY",)
    assert action.external_execution_performed is False

    failed = govern_manifold_action(
        [
            PopulationTransition("T-X", "M0", allowed_request(target="record:x"), depends_on=("T-Y",)),
        ]
    )
    assert failed.state == "FAIL_CLOSED"
    assert failed.continue_transition_ids == ()
    assert failed.external_execution_performed is False

