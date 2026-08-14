from __future__ import annotations

import unittest
from pathlib import Path

from scripts.validate_no_non_tvtvc_validation_credentials import ROOT, TARGETS, validate_text


class NoNonTvTvcValidationCredentialTests(unittest.TestCase):
    def test_all_target_workflows_are_credential_clean(self):
        failures = []
        for path in TARGETS:
            failures.extend(validate_text(path, path.read_text(encoding="utf-8")))
        self.assertEqual(failures, [])

    def test_validator_rejects_github_action_and_token_context(self):
        sample = """permissions: {}\n- name: Anonymous public repository fetch\n- name: Assert credential-clean validation environment\nuses: actions/checkout@v4\nenv:\n  GH_TOKEN: ${{ github.token }}\nhttps://github.com/${GITHUB_REPOSITORY}.git\ncredential.helper=\nhttp.extraheader=\n"""
        errors = validate_text(Path("sample.yml"), sample)
        self.assertTrue(any("uses:" in item for item in errors))
        self.assertTrue(any("github.token" in item for item in errors))

    def test_target_inventory_is_explicit(self):
        expected = {
            ".github/workflows/stegcore-tests.yml",
            ".github/workflows/runtime-tests.yml",
            ".github/workflows/bcat-gate.yml",
            ".github/workflows/test-readiness.yml",
            ".github/workflows/stegverse-001-002-validator.yml",
        }
        actual = {str(path.relative_to(ROOT)) for path in TARGETS}
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
