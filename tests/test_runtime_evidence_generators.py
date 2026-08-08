import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def canonical_hash(record, excluded_field):
    body = dict(record)
    declared = body.pop(excluded_field)
    computed = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return declared, computed


class RuntimeEvidenceGeneratorTests(unittest.TestCase):
    def test_generators_emit_v11_custody_envelopes_and_reset_release_gates(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            runtime_path = temp / "runtime-validation.json"
            readiness_path = temp / "release-readiness.json"

            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/record_runtime_validation.py"),
                    "--output",
                    str(runtime_path),
                    "--dispatch",
                    str(ROOT / "evidence/downstream-verification-dispatch.json"),
                    "--stegcore-commit",
                    "a" * 40,
                    "--governance-commit",
                    "b" * 40,
                    "--run-id",
                    "123456",
                    "--run-attempt",
                    "1",
                    "--workflow",
                    "Validate StegCore Runtime",
                    "--repository",
                    "StegVerse-Labs/StegCore",
                    "--ref",
                    "refs/heads/main",
                    "--event",
                    "push",
                    "--issue",
                    "22",
                ],
                cwd=ROOT,
                check=True,
            )
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/assess_release_readiness.py"),
                    "--evidence",
                    str(runtime_path),
                    "--output",
                    str(readiness_path),
                ],
                cwd=ROOT,
                check=True,
            )

            runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
            readiness = json.loads(readiness_path.read_text(encoding="utf-8"))

            self.assertEqual(runtime["schema_version"], "1.1")
            self.assertEqual(runtime["record_type"], "runtime_validation_evidence")
            self.assertEqual(runtime["source_repository"], "StegVerse-Labs/StegCore")
            self.assertEqual(runtime["destination_repository"], "StegVerse-Labs/StegCore")
            self.assertEqual(runtime["hash_convention"]["excluded_field"], "evidence_hash")
            self.assertEqual(*canonical_hash(runtime, "evidence_hash"))

            self.assertEqual(readiness["schema_version"], "1.1")
            self.assertEqual(readiness["record_type"], "release_readiness_assessment")
            self.assertEqual(readiness["source_repository"], "StegVerse-Labs/StegCore")
            self.assertEqual(readiness["destination_repository"], "StegVerse-Labs/StegCore")
            self.assertEqual(readiness["hash_convention"]["excluded_field"], "assessment_hash")
            self.assertEqual(*canonical_hash(readiness, "assessment_hash"))
            self.assertEqual(readiness["state"], "validated_not_released")
            self.assertEqual(readiness["gates"]["runtime_validation"], "pass")
            self.assertEqual(readiness["gates"]["governance_freshness"], "pending")
            self.assertEqual(readiness["gates"]["independent_release_policy"], "pending")
            self.assertEqual(readiness["gates"]["downstream_verification"], "pending")
            self.assertFalse(readiness["release_permitted"])
            self.assertFalse(readiness["tag_permitted"])
            self.assertTrue(all(gate["status"] == "pending" for gate in readiness["downstream_gates"]))

    def test_readiness_generator_rejects_tampered_runtime_evidence(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            runtime_path = temp / "runtime-validation.json"
            readiness_path = temp / "release-readiness.json"

            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/record_runtime_validation.py"),
                    "--output",
                    str(runtime_path),
                    "--dispatch",
                    str(ROOT / "evidence/downstream-verification-dispatch.json"),
                    "--stegcore-commit",
                    "c" * 40,
                    "--governance-commit",
                    "d" * 40,
                    "--run-id",
                    "654321",
                    "--run-attempt",
                    "1",
                    "--workflow",
                    "Validate StegCore Runtime",
                    "--repository",
                    "StegVerse-Labs/StegCore",
                    "--ref",
                    "refs/heads/main",
                    "--event",
                    "push",
                ],
                cwd=ROOT,
                check=True,
            )
            runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
            runtime["status"] = "tampered"
            runtime_path.write_text(json.dumps(runtime), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/assess_release_readiness.py"),
                    "--evidence",
                    str(runtime_path),
                    "--output",
                    str(readiness_path),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertFalse(readiness_path.exists())


if __name__ == "__main__":
    unittest.main()
