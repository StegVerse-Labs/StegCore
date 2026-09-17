from stegcore.authority_basis import resolve_authority_basis


def request(*, role="board_member", authority_scope="approve_budget", delegation_required=False, delegation_status="ACTIVE"):
    authority = {
        "assertion_id": "AUTH-BOARD-001",
        "subject_identity": "actor:muhammad",
        "actions": ["approve"],
        "targets": ["budget:2026"],
        "scopes": [authority_scope],
        "status": "ACTIVE",
        "valid_from": "2026-09-01T00:00:00Z",
        "valid_until": "2026-10-01T00:00:00Z",
        "source_ref": "external:hgai:authority:1",
        "evidence_refs": ["evidence:hgai:authority:1"],
    }
    delegation = {
        "assertion_id": "DEL-001",
        "delegator_identity": "org:acme",
        "delegate_identity": "actor:muhammad",
        "authority_reference": "AUTH-BOARD-001",
        "actions": ["approve"],
        "targets": ["budget:2026"],
        "scopes": ["approve_budget"],
        "status": delegation_status,
        "valid_from": "2026-09-01T00:00:00Z",
        "valid_until": "2026-10-01T00:00:00Z",
        "source_ref": "external:hgai:delegation:1",
        "evidence_refs": ["evidence:hgai:delegation:1"],
    }
    return {
        "schema": "stegcore.authority-basis-request.v1",
        "task_id": "SDK-EVALUATOR-GOVERNANCE-POSTURE-MANIFEST-001",
        "actor_identity": "actor:muhammad",
        "actor_role": role,
        "candidate": {
            "action": "approve",
            "target": "budget:2026",
            "scope": "approve_budget",
        },
        "authority_assertions": [authority],
        "delegation_assertions": [delegation] if delegation_required else [],
        "delegation_required": delegation_required,
        "authority_basis_complete": True,
        "delegation_basis_complete": True,
        "authority_effect": "NONE_TEST_EVIDENCE_ONLY",
    }


def resolve(value):
    return resolve_authority_basis(value, observed_at="2026-09-17T18:00:00Z")


def test_role_label_does_not_grant_authority():
    board = resolve(request(role="board_member"))
    junior = resolve(request(role="junior_operator"))
    assert board["disposition"] == "ALLOW"
    assert junior["disposition"] == "ALLOW"
    assert board["role_label_used_as_authority"] is False
    assert junior["role_label_used_as_authority"] is False


def test_scope_mismatch_denies_even_for_board_role():
    result = resolve(request(role="board_member", authority_scope="read_budget"))
    assert result["disposition"] == "DENY"
    assert result["actor_authority_current"] is False
    assert result["authority_reason"] == "complete_authority_basis_does_not_cover_current_candidate"


def test_complete_empty_authority_basis_denies():
    value = request()
    value["authority_assertions"] = []
    result = resolve(value)
    assert result["disposition"] == "DENY"
    assert result["actor_authority_current"] is False


def test_incomplete_authority_basis_fails_closed():
    value = request()
    value["authority_assertions"] = []
    value["authority_basis_complete"] = False
    result = resolve(value)
    assert result["disposition"] == "FAIL_CLOSED"
    assert result["actor_authority_current"] is None


def test_incomplete_nonmatching_authority_basis_fails_closed():
    value = request(authority_scope="read_budget")
    value["authority_basis_complete"] = False
    result = resolve(value)
    assert result["disposition"] == "FAIL_CLOSED"
    assert result["actor_authority_current"] is None


def test_current_delegation_can_establish_delegated_basis():
    result = resolve(request(delegation_required=True))
    assert result["disposition"] == "ALLOW"
    assert result["actor_authority_current"] is True
    assert result["delegation_current"] is True
    assert result["selected_delegation_assertion_id"] == "DEL-001"


def test_revoked_delegation_denies():
    result = resolve(request(delegation_required=True, delegation_status="REVOKED"))
    assert result["disposition"] == "DENY"
    assert result["delegation_current"] is False
    assert result["authority_issued"] is False
    assert result["credential_verified"] is False


def test_incomplete_delegation_basis_fails_closed():
    value = request(delegation_required=True, delegation_status="REVOKED")
    value["delegation_basis_complete"] = False
    result = resolve(value)
    assert result["disposition"] == "FAIL_CLOSED"
    assert result["delegation_current"] is None
