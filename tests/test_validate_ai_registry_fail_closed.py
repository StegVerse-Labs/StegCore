"""StegCore_hooks AI registry validator must fail closed on missing inputs."""
import importlib.util
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


# Schema validation uses the vendored stdlib-only structural validator, so jsonschema is
# never needed. PyYAML (for ethics/ai_classes.yaml) is not a declared StegCore dependency;
# without it the validator fails closed at AI_REGISTRY_VALIDATOR_DEPENDENCIES_PRESENT.
HAVE_YAML = importlib.util.find_spec("yaml") is not None


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


    def _with_inputs(self, tmp):
        if not HAVE_YAML:
            self.skipTest("PyYAML not installed in this environment")
        root = pathlib.Path(tmp)
        (root / "registry").mkdir()
        (root / "registry" / "ai_entity_schema.json").write_text("{}")
        (root / "ethics").mkdir()
        (root / "ethics" / "ai_classes.yaml").write_text("transitions:\n  prohibited: []\n")
        return root

    def test_missing_entities_directory_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._with_inputs(tmp)
            result = _run(tmp)
            self._assert_fail_closed(result, "AI_REGISTRY_ENTITIES_PRESENT")

    def test_empty_entities_directory_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            (self._with_inputs(tmp) / "registry" / "entities").mkdir()
            result = _run(tmp)
            self._assert_fail_closed(result, "AI_REGISTRY_ENTITIES_PRESENT")

    def test_malformed_entity_history_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._with_inputs(tmp)
            entities = root / "registry" / "entities"
            entities.mkdir()
            (entities / "bad.json").write_text(json.dumps({
                "class_history": [{"from": "alpha"}],
                "acknowledgements": ["present"],
            }))
            result = _run(tmp)
            self._assert_fail_closed(result, "AI_REGISTRY_ENTITY_INPUT_VALID")
            self.assertNotIn("Traceback", result.stderr)

    def test_non_object_entity_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._with_inputs(tmp)
            entities = root / "registry" / "entities"
            entities.mkdir()
            (entities / "array.json").write_text("[]")
            result = _run(tmp)
            self._assert_fail_closed(result, "AI_REGISTRY_ENTITY_INPUT_VALID")
            self.assertNotIn("Traceback", result.stderr)

    def test_malformed_prohibited_policy_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._with_inputs(tmp)
            (root / "ethics" / "ai_classes.yaml").write_text(
                "transitions:\\n  prohibited: not-an-array\\n".replace("\\n", "\n")
            )
            result = _run(tmp)
            self._assert_fail_closed(result, "AI_REGISTRY_POLICY_INPUTS_VALID")
            self.assertNotIn("Traceback", result.stderr)

    def test_missing_yaml_fails_closed_without_traceback(self):
        if HAVE_YAML:
            self.skipTest("PyYAML installed; the missing-dependency path is not reachable")
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "registry").mkdir()
            (root / "registry" / "ai_entity_schema.json").write_text("{}")
            (root / "ethics").mkdir()
            (root / "ethics" / "ai_classes.yaml").write_text("transitions: {}\n")
            result = _run(tmp)
            self._assert_fail_closed(result, "AI_REGISTRY_VALIDATOR_DEPENDENCIES_PRESENT")

    def test_unsupported_schema_keyword_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._with_inputs(tmp)
            (root / "registry" / "ai_entity_schema.json").write_text(json.dumps({"patternProperties": {}}))
            (root / "registry" / "entities").mkdir()
            (root / "registry" / "entities" / "a.json").write_text(json.dumps({"acknowledgements": ["x"]}))
            result = _run(tmp)
            self._assert_fail_closed(result, "AI_REGISTRY_POLICY_INPUTS_VALID")
            self.assertNotIn("Traceback", result.stderr)

    def test_entity_schema_violation_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._with_inputs(tmp)
            (root / "registry" / "ai_entity_schema.json").write_text(json.dumps({"required": ["id"]}))
            (root / "registry" / "entities").mkdir()
            (root / "registry" / "entities" / "a.json").write_text(json.dumps({"acknowledgements": ["x"]}))
            result = _run(tmp)
            self._assert_fail_closed(result, "AI_REGISTRY_ENTITY_SCHEMA_VALID")
            self.assertIn("/id:REQUIRED", result.stdout)


if __name__ == "__main__":
    unittest.main()
