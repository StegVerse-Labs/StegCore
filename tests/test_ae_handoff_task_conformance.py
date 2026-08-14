from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools import verify_ae_handoff_task_conformance as verifier


class AEHandoffTaskConformanceTests(unittest.TestCase):
    def test_repository_contract_is_conformant(self):
        report = verifier.verify()
        self.assertTrue(report["valid"], report["findings"])
        self.assertEqual(report["temporal_counts"]["recently_completed"], 1)
        self.assertEqual(report["temporal_counts"]["current"], 1)
        self.assertEqual(report["temporal_counts"]["future"], 1)
        self.assertGreaterEqual(report["capability_count"], 3)

    def _isolated_contract(self):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / "ecosystem_management").mkdir()
        (root / "management").mkdir()
        (root / "docs").mkdir()
        (root / "brain_reports").mkdir()
        return temp, root

    def test_future_task_without_capability_binding_fails_closed(self):
        temp, root = self._isolated_contract()
        self.addCleanup(temp.cleanup)
        manifest = {
            "canonical_issue": "#x",
            "canonical_admissibility_runtime": "stegcore.steggate.evaluate_admissibility",
            "credential_authority": "TV/TVC",
            "github_token_runtime_authority": "NONE",
            "rules": {
                "completed_task_requires_evidence_for_claimed_phase": True,
                "current_task_requires_owner_and_continuation": True,
                "future_task_requires_capability_binding_before_activation": True,
                "activated_requires_integration_and_activation_proof": True,
                "blocked_admissible_requires_continuation_owner": True,
                "structural_verification_may_widen_authority": False,
                "handoff_registry_projection_must_match": True,
                "legacy_unclassified_tasks_are_conformant": False,
            },
            "tasks": [
                {
                    "task_id": "FUTURE-X",
                    "temporal_class": "future",
                    "relationship": "develops_capability",
                    "capability_id": "missing",
                    "claimed_phase": "DECLARED",
                    "target_phase": "STANDING",
                    "owner": "repo",
                    "handoff_ref": "docs/task.md",
                    "evidence_refs": [],
                    "blockers": ["NOT_STARTED"],
                    "continuation_owner": "repo#1",
                    "activation_claimed": False,
                },
                {
                    "task_id": "CURRENT-X",
                    "temporal_class": "current",
                    "relationship": "integrates_capability",
                    "capability_id": "missing",
                    "claimed_phase": "DECLARED",
                    "target_phase": "STANDING",
                    "owner": "repo",
                    "handoff_ref": "docs/task.md",
                    "evidence_refs": [],
                    "blockers": ["WAITING"],
                    "continuation_owner": "repo#1",
                    "activation_claimed": False,
                },
                {
                    "task_id": "DONE-X",
                    "temporal_class": "recently_completed",
                    "relationship": "validates_capability",
                    "capability_id": "missing",
                    "claimed_phase": "DECLARED",
                    "target_phase": "DECLARED",
                    "owner": "repo",
                    "handoff_ref": "docs/task.md",
                    "evidence_refs": ["receipt"],
                    "blockers": [],
                    "continuation_owner": "repo#1",
                    "activation_claimed": False,
                },
            ],
            "legacy_policy": {
                "records_without_ae_binding": "MIGRATION_REQUIRED",
                "records_may_continue_existing_authority_while_migrating": False,
                "future_activation_from_legacy_record": False,
            },
        }
        (root / "ecosystem_management/ae_task_conformance.v1.json").write_text(json.dumps(manifest))
        (root / "management/admissible-existence-capability-registry.json").write_text(json.dumps({"entries": []}))
        (root / "ecosystem_management/task_registry.yml").write_text(
            "admissible_existence_conformance:\n  manifest: ecosystem_management/ae_task_conformance.v1.json\n  verifier: tools/verify_ae_handoff_task_conformance.py\n"
        )
        (root / "docs/STEGVERSE_ECOSYSTEM_MANAGEMENT_MIRROR_HANDOFF.md").write_text(
            "## Admissible-Existence conformance gate\n"
            "ecosystem_management/ae_task_conformance.v1.json\n"
            "tools/verify_ae_handoff_task_conformance.py\n"
            "recently completed current future\n"
        )
        (root / "docs/task.md").write_text("task")
        with mock.patch.object(verifier, "ROOT", root), \
             mock.patch.object(verifier, "MANIFEST_PATH", root / "ecosystem_management/ae_task_conformance.v1.json"), \
             mock.patch.object(verifier, "CAPABILITY_REGISTRY_PATH", root / "management/admissible-existence-capability-registry.json"), \
             mock.patch.object(verifier, "TASK_REGISTRY_PATH", root / "ecosystem_management/task_registry.yml"), \
             mock.patch.object(verifier, "HANDOFF_PATH", root / "docs/STEGVERSE_ECOSYSTEM_MANAGEMENT_MIRROR_HANDOFF.md"):
            report = verifier.verify()
        self.assertFalse(report["valid"])
        self.assertIn("capability_binding_missing", {item["code"] for item in report["findings"]})

    def test_activated_registry_entry_without_activation_proof_fails(self):
        temp, root = self._isolated_contract()
        self.addCleanup(temp.cleanup)
        declaration = {
            "artifact_type": "stegcore.capability_existence_declaration",
            "schema_version": "1.0",
            "capability_id": "cap-x",
            "capability_version": "1",
            "owner_repository": "repo",
            "purpose": "x",
            "dependencies": [],
            "authority": {"credential_authority": "TV/TVC", "github_token_runtime_authority": False, "may": [], "may_not": []},
            "evidence_refs": [],
            "metadata": {},
        }
        entry = {
            "declaration": declaration,
            "existence_hash": verifier.sha256_json(declaration),
            "phase": "ACTIVATED",
            "evidence": {"standing_evidence_refs": ["s"], "admissibility_evidence_refs": ["a"], "integration_evidence_refs": [], "activation_proof_ref": None, "blockers": [], "continuation_owner": "repo"},
        }
        (root / "ecosystem_management/ae_task_conformance.v1.json").write_text(json.dumps({
            "canonical_admissibility_runtime": "stegcore.steggate.evaluate_admissibility",
            "credential_authority": "TV/TVC",
            "github_token_runtime_authority": "NONE",
            "rules": {
                "completed_task_requires_evidence_for_claimed_phase": True,
                "current_task_requires_owner_and_continuation": True,
                "future_task_requires_capability_binding_before_activation": True,
                "activated_requires_integration_and_activation_proof": True,
                "blocked_admissible_requires_continuation_owner": True,
                "structural_verification_may_widen_authority": False,
                "handoff_registry_projection_must_match": True,
                "legacy_unclassified_tasks_are_conformant": False,
            },
            "tasks": [],
            "legacy_policy": {"records_without_ae_binding": "MIGRATION_REQUIRED", "records_may_continue_existing_authority_while_migrating": False, "future_activation_from_legacy_record": False},
        }))
        (root / "management/admissible-existence-capability-registry.json").write_text(json.dumps({"entries": [entry]}))
        (root / "ecosystem_management/task_registry.yml").write_text("admissible_existence_conformance:\n ecosystem_management/ae_task_conformance.v1.json\n tools/verify_ae_handoff_task_conformance.py\n")
        (root / "docs/STEGVERSE_ECOSYSTEM_MANAGEMENT_MIRROR_HANDOFF.md").write_text("## Admissible-Existence conformance gate\necosystem_management/ae_task_conformance.v1.json\ntools/verify_ae_handoff_task_conformance.py\nrecently completed current future\n")
        with mock.patch.object(verifier, "ROOT", root), \
             mock.patch.object(verifier, "MANIFEST_PATH", root / "ecosystem_management/ae_task_conformance.v1.json"), \
             mock.patch.object(verifier, "CAPABILITY_REGISTRY_PATH", root / "management/admissible-existence-capability-registry.json"), \
             mock.patch.object(verifier, "TASK_REGISTRY_PATH", root / "ecosystem_management/task_registry.yml"), \
             mock.patch.object(verifier, "HANDOFF_PATH", root / "docs/STEGVERSE_ECOSYSTEM_MANAGEMENT_MIRROR_HANDOFF.md"):
            report = verifier.verify()
        codes = {item["code"] for item in report["findings"]}
        self.assertIn("activated_integration_evidence_missing", codes)
        self.assertIn("activated_activation_proof_missing", codes)


if __name__ == "__main__":
    unittest.main()
