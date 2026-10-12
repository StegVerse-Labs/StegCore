"""StegCore_hooks AI registry validator must fail closed on missing inputs."""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = (
    pathlib.Path(__file__).resolve().parents[1]
    / "StegCore_hooks"
    / "policy_checks"
    / "validate_ai_registry.py"
)


def _run(cwd):
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=60,
    )


class ValidateAiRegistryFailClosedTest(unittest.TestCase):
    def _assert_fail_closed(self, result, predicate):
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.returncode, 2)
        payload = json.loads(result.stdout.strip().splitlines()[-1])
        self.assertEqual(payload["disposition"], "FAIL_CLOSED")
        self.assertEqual(payload["failed_predicate"], predicate)
        self.assertEqual(payload["authority_effect"], "NONE")
        self.assertIn("declare an exemption", payload["required_evidence_or_repair"])
        self.assertNotIn("skipping", result.stdout.lower())

    def test_missing_all_inputs_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._assert_fail_closed(_run(tmp), "AI_REGISTRY_SCHEMA_PRESENT")

    def test_missing_ai_classes_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry = pathlib.Path(tmp) / "registry"
            registry.mkdir()
            (registry / "ai_entity_schema.json").write_text("{}")
            self._assert_fail_closed(_run(tmp), "AI_CLASSES_PRESENT")


if __name__ == "__main__":
    unittest.main()
