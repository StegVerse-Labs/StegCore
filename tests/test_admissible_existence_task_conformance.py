from pathlib import Path

from scripts.verify_admissible_existence_task_conformance import verify


ROOT = Path(__file__).resolve().parents[1]


def test_canonical_handoff_and_fixture_registry_pass(tmp_path):
    registry = tmp_path / "registry.json"
    registry.write_text(
        '''{
  "artifact_type": "stegverse_worker_task_registry",
  "schema_version": "2.0",
  "workers": [
    {
      "task_id": "worker-current-1",
      "worker_id": "worker-current-1",
      "task_horizon": "current",
      "state": "ACTIVE",
      "ae_phase": "ADMISSIBLE",
      "owner": "StegVerse-Labs/example",
      "collision_boundary": "example files only",
      "next_executable_action": "run the bounded implementation task",
      "expected_evidence": ["merged commit", "validation receipt"],
      "evidence_refs": ["issue #1", "validator"],
      "admissibility_evidence_refs": ["validator"],
      "activation_proof_ref": null,
      "continuation_owner": "StegVerse-Labs/example"
    }
  ]
}\n''',
        encoding="utf-8",
    )
    receipt = verify(
        ROOT / "management/admissible-existence-task-conformance-handoff.json",
        registry,
        ROOT / "management/admissible-existence-task-conformance-policy.json",
    )
    assert receipt["status"] == "PASS", receipt["errors"]
    assert receipt["activation_inferred"] is False
    assert receipt["github_token_runtime_authority"] is False


def test_activated_worker_without_activation_proof_fails_closed(tmp_path):
    registry = tmp_path / "registry.json"
    registry.write_text(
        '''{
  "artifact_type": "stegverse_worker_task_registry",
  "schema_version": "2.0",
  "workers": [
    {
      "task_id": "worker-bad-1",
      "worker_id": "worker-bad-1",
      "task_horizon": "recently_completed",
      "state": "COMPLETE",
      "ae_phase": "ACTIVATED",
      "owner": "StegVerse-Labs/example",
      "collision_boundary": "example files only",
      "next_executable_action": "none",
      "expected_evidence": ["activation receipt"],
      "evidence_refs": ["merged commit"],
      "activation_proof_ref": null,
      "continuation_owner": "StegVerse-Labs/example"
    }
  ]
}\n''',
        encoding="utf-8",
    )
    receipt = verify(
        ROOT / "management/admissible-existence-task-conformance-handoff.json",
        registry,
        ROOT / "management/admissible-existence-task-conformance-policy.json",
    )
    assert receipt["status"] == "FAIL_CLOSED"
    assert any("activation_proof_required" in error or "missing:activation_proof_ref" in error for error in receipt["errors"])


def test_future_terminal_worker_fails_closed(tmp_path):
    registry = tmp_path / "registry.json"
    registry.write_text(
        '''{
  "artifact_type": "stegverse_worker_task_registry",
  "schema_version": "2.0",
  "workers": [
    {
      "task_id": "worker-future-1",
      "worker_id": "worker-future-1",
      "task_horizon": "future",
      "state": "COMPLETE",
      "ae_phase": "STANDING",
      "owner": "StegVerse-Labs/example",
      "collision_boundary": "example files only",
      "next_executable_action": "implement later",
      "expected_evidence": ["future evidence"],
      "evidence_refs": ["declaration"],
      "standing_evidence_refs": ["declaration"],
      "activation_proof_ref": null,
      "continuation_owner": "StegVerse-Labs/example"
    }
  ]
}\n''',
        encoding="utf-8",
    )
    receipt = verify(
        ROOT / "management/admissible-existence-task-conformance-handoff.json",
        registry,
        ROOT / "management/admissible-existence-task-conformance-policy.json",
    )
    assert receipt["status"] == "FAIL_CLOSED"
    assert any("future_task_cannot_be_terminal" in error for error in receipt["errors"])
