import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DownstreamVerificationReconciliationTests(unittest.TestCase):
    def test_canonical_receipts_promote_only_downstream_gate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "release-readiness.json"
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/reconcile_downstream_verification.py"),
                    "--runtime-evidence", str(ROOT / "evidence/runtime-validation.json"),
                    "--dispatch", str(ROOT / "evidence/downstream-verification-dispatch.json"),
                    "--receipts", str(ROOT / "evidence/downstream-verification-receipts.json"),
                    "--output", str(output),
                ],
                cwd=ROOT,
                check=True,
            )
            readiness = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(readiness["schema_version"], "1.1")
            self.assertEqual(readiness["state"], "downstream_verified_release_blocked")
            self.assertEqual(readiness["gates"]["downstream_verification"], "pass")
            self.assertEqual(readiness["gates"]["governance_freshness"], "pending")
            self.assertEqual(readiness["gates"]["independent_release_policy"], "pending")
            self.assertFalse(readiness["release_permitted"])
            self.assertFalse(readiness["tag_permitted"])
            self.assertEqual(len(readiness["downstream_gates"]), 4)
            self.assertTrue(all(row["status"] == "pass" for row in readiness["downstream_gates"]))

    def test_missing_required_receipt_fails_closed(self):
        receipts = json.loads((ROOT / "evidence/downstream-verification-receipts.json").read_text(encoding="utf-8"))
        receipts["verifications"] = receipts["verifications"][:-1]
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            receipts_path = temp / "receipts.json"
            output = temp / "readiness.json"
            receipts_path.write_text(json.dumps(receipts), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/reconcile_downstream_verification.py"),
                    "--runtime-evidence", str(ROOT / "evidence/runtime-validation.json"),
                    "--dispatch", str(ROOT / "evidence/downstream-verification-dispatch.json"),
                    "--receipts", str(receipts_path),
                    "--output", str(output),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertFalse(output.exists())

    def test_source_hash_mismatch_fails_closed(self):
        receipts = json.loads((ROOT / "evidence/downstream-verification-receipts.json").read_text(encoding="utf-8"))
        receipts["source_runtime_evidence_hash"] = "0" * 64
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            receipts_path = temp / "receipts.json"
            output = temp / "readiness.json"
            receipts_path.write_text(json.dumps(receipts), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/reconcile_downstream_verification.py"),
                    "--runtime-evidence", str(ROOT / "evidence/runtime-validation.json"),
                    "--dispatch", str(ROOT / "evidence/downstream-verification-dispatch.json"),
                    "--receipts", str(receipts_path),
                    "--output", str(output),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
