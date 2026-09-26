"""Private-owner pre-release cross-package source test, without distribution.

Runs inside native StegCore Actions: the native checkout already has authorized
access to PRIVATE StegCore. Installs only the public pinned SDK draft source.
The customer authority verifier is an EXPLICIT TEST FIXTURE, not an issuer
or proof of actual customer authorization. No real external consequence.
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from stegverse.customer_local_governance import (
    CustomerLocalRouteRefused, execute_local_manifest, execute_manifest,
)
from stegverse.route_resolution import (
    CUSTOMER_LOCAL_GOVERNANCE_ROUTE_ID, PUBLISHED_ROUTES,
)
from stegcore import __version__
from stegcore.steggate_runtime import governed_steggate_execute

SDK_ROOT = Path(os.environ["STEGCORE_TEST_LOCAL_SDK_ROOT"])


def source_manifest():
    fixture = SDK_ROOT / "inspection/examples/external-framework-generic-manifest.json"
    manifest = json.loads(fixture.read_text(encoding="utf-8"))
    route = PUBLISHED_ROUTES[CUSTOMER_LOCAL_GOVERNANCE_ROUTE_ID]
    manifest["processing"] = {
        "capability": "governance",
        "route_id": CUSTOMER_LOCAL_GOVERNANCE_ROUTE_ID,
    }
    manifest["extensions"]["stegverse_route"] = {
        key: route[key] for key in (
            "route_id", "lane_class", "routing_surface", "containment",
            "sandbox_required", "external_consequence_enabled",
        )
    }
    manifest.pop("completion", None)
    return manifest


def TEST_FIXTURE_verifier(evidence, *, target):
    if evidence.get("fixture_approved") is not True:
        raise ValueError("unapproved test fixture")
    return {
        "status": "approved",
        "target_binding": target,
        "authority_ref": "FIXTURE_ONLY_NOT_CUSTOMER_CREDENTIAL",
        "basis_invalidated_by_action": False,
        "valid_from": "2026-01-01T00:00:00+00:00",
        "valid_until": "2027-01-01T00:00:00+00:00",
    }


class RealStegCorePlusLocalSDKSource(unittest.TestCase):
    def test_source_packages_import_actual_canonical_runtime(self):
        self.assertEqual(__version__, "0.3.0")
        self.assertTrue(callable(governed_steggate_execute))

    def test_real_canonical_allow_commits_once_and_retains_test_evidence(self):
        with tempfile.TemporaryDirectory() as work:
            root = Path(work)
            target = root / "bounded-fixture"
            target.write_text("before", encoding="utf-8")
            events = []
            def record_precommit(observation):
                events.append(("PRE_COMMIT", observation))
                (root / "precommit.json").write_text(
                    json.dumps(observation, sort_keys=True), encoding="utf-8")
            def bounded_executor():
                self.assertTrue((root / "precommit.json").is_file())
                self.assertEqual(target.read_text(encoding="utf-8"), "before")
                target.write_text("after", encoding="utf-8")
                events.append(("EXECUTOR", "test-only"))
                return {"test_file_written": True}
            def record_result(result):
                events.append(("RESULT", result))
                (root / "result.json").write_text(
                    json.dumps(result, sort_keys=True), encoding="utf-8")
            result = execute_local_manifest(
                source_manifest(),
                authority_evidence={"fixture_approved": True},
                authority_verifier=TEST_FIXTURE_verifier,
                precommit_recorder=record_precommit,
                executor=bounded_executor,
                result_recorder=record_result,
            )
            self.assertEqual(result["status"], "executed", result)
            self.assertEqual(result["disposition"], "ALLOW")
            self.assertEqual(target.read_text(encoding="utf-8"), "after")
            self.assertEqual([x[0] for x in events],
                             ["PRE_COMMIT", "EXECUTOR", "RESULT"])
            reread = json.loads((root / "result.json").read_text(encoding="utf-8"))
            self.assertEqual(reread["decision_state_hash"], result["decision_state_hash"])
            self.assertEqual(reread["authority_boundary"],
                             "CUSTOMER_LOCAL_NOT_STEGVERSE_MASTER_RECORDS")

    def test_real_canonical_non_allow_cannot_mutate_test_file(self):
        manifest = source_manifest()
        manifest["extensions"]["stegverse_governance_request"]["execution"]["policy_current"] = False
        modified = []
        result = execute_local_manifest(
            manifest,
            authority_evidence={"fixture_approved": True},
            authority_verifier=TEST_FIXTURE_verifier,
            precommit_recorder=lambda value: modified.append("precommit"),
            executor=lambda: modified.append("FORBIDDEN_MUTATION"),
            result_recorder=lambda value: modified.append("result"),
        )
        self.assertEqual(result["status"], "refused")
        self.assertEqual(result["disposition"], "DENY")
        self.assertEqual(modified, ["result"])

    def test_real_precommit_checkpoint_failure_remains_non_allow(self):
        # Actual canonical StegCore initially admits; the customer writer
        # then refuses, so the bounded executor MUST remain unreachable.
        mutations = []
        results = []
        def custody_unavailable(observation):
            raise OSError("customer offline checkpoint is unavailable")
        result = execute_local_manifest(
            source_manifest(),
            authority_evidence={"fixture_approved": True},
            authority_verifier=TEST_FIXTURE_verifier,
            precommit_recorder=custody_unavailable,
            executor=lambda: mutations.append("FORBIDDEN"),
            result_recorder=lambda row: results.append(row),
        )
        self.assertEqual(result["status"], "refused")
        self.assertEqual(result["canonical_admissibility_disposition"], "ALLOW")
        self.assertEqual(result["disposition"], "FAIL_CLOSED")
        self.assertEqual(result["local_execution_reason"], "precommit_observer_failed")
        self.assertFalse(result["executor_invoked"])
        self.assertTrue(result["canonical_coherence_receipt"]["pre_execution_observer_failed"])
        self.assertEqual(mutations, [])
        self.assertEqual(len(results), 1)

    def test_unverified_customer_authority_fails_before_canonical_executor(self):
        touched = []
        with self.assertRaisesRegex(CustomerLocalRouteRefused, "AUTHORITY_VERIFICATION_FAILED"):
            execute_local_manifest(
                source_manifest(), authority_evidence={"fixture_approved": False},
                authority_verifier=TEST_FIXTURE_verifier,
                precommit_recorder=lambda value: touched.append("precommit"),
                executor=lambda: touched.append("not permitted"),
                result_recorder=lambda value: touched.append("result"),
            )
        self.assertFalse(touched)

    def test_manifest_only_entrypoint_cannot_contact_remote_intr(self):
        with patch("urllib.request.urlopen", side_effect=AssertionError("network")):
            with self.assertRaisesRegex(CustomerLocalRouteRefused, "HOST_BINDINGS_REQUIRED"):
                execute_manifest(source_manifest())


if __name__ == "__main__":
    unittest.main()
