import unittest

from stegcore.manifest_receipt_provider import (
    MasterRecordsManifestReceiptProvider,
    build_master_records_submission,
)
from stegcore.manifest_receipts import ManifestReceiptRecord
from stegcore.steggate import canonical_sha256


class ManifestReceiptProviderTests(unittest.TestCase):
    @staticmethod
    def record():
        body = {
            "artifact_type": "stegcore.manifest_receipt_record",
            "schema_version": "1.0",
            "manifest_receipt_id": "MR-" + "A" * 64,
            "transaction_id": "TX-1",
            "manifest_hash": "b" * 64,
            "receipt_chain_head": "c" * 64,
            "canonical_runtime_identity": "stegverse:steggate:canonical:three-layer:v1",
            "registered_at": "2026-08-12T19:00:00+00:00",
            "result": {},
            "locator_grants_authority": False,
        }
        return ManifestReceiptRecord(**body, record_hash=canonical_sha256(body))

    @classmethod
    def evidence(cls):
        record = cls.record()
        return {
            "manifest_receipt_id": record.manifest_receipt_id,
            "transaction_id": record.transaction_id,
            "manifest": {"manifest_hash": record.manifest_hash},
            "receipts": [],
            "execution_observation": {},
            "replay_descriptor": {},
            "chain_verified": True,
            "receipt_chain_head": record.receipt_chain_head,
            "canonical_runtime_identity": record.canonical_runtime_identity,
            "locator_grants_authority": False,
        }

    def test_submission_promotes_exact_identity_without_authority(self):
        record = self.record()
        request = build_master_records_submission(record, self.evidence())
        self.assertEqual("stegverse.master-records.manifest-receipt-submission.v1", request["schema"])
        self.assertFalse(request["authority_requested"])
        package = request["evidence_package"]
        self.assertEqual(record.manifest_hash, package["manifest_hash"])
        self.assertEqual(record.record_hash, package["record_hash"])
        self.assertFalse(package["locator_grants_authority"])

    def test_provider_retain_verifies_custody_boundary(self):
        record = self.record()
        captured = {}

        def submit(request):
            captured.update(request)
            return {
                "schema": "stegverse.master-records.manifest-receipt-custody-receipt.v1",
                "manifest_receipt_id": record.manifest_receipt_id,
                "transaction_id": record.transaction_id,
                "master_record_sha256": "d" * 64,
                "custody_status": "RECORDED",
                "locator_grants_authority": False,
                "custody_grants_execution_authority": False,
                "custody_grants_admissibility": False,
            }

        provider = MasterRecordsManifestReceiptProvider(
            submit_call=submit,
            evidence_call=lambda receipt_id: {
                "manifest_receipt_id": receipt_id,
                "evidence_package": self.evidence(),
                "locator_grants_authority": False,
            },
            reconstruction_call=lambda receipt_id: {
                "manifest_receipt_id": receipt_id,
                "consequence_reexecuted": False,
                "reconstruction_grants_authority": False,
            },
        )
        response = provider.retain(record, self.evidence())
        self.assertEqual("RECORDED", response["custody_status"])
        self.assertFalse(captured["authority_requested"])

    def test_provider_rejects_authority_escalation(self):
        record = self.record()
        provider = MasterRecordsManifestReceiptProvider(
            submit_call=lambda request: {
                "schema": "stegverse.master-records.manifest-receipt-custody-receipt.v1",
                "manifest_receipt_id": record.manifest_receipt_id,
                "transaction_id": record.transaction_id,
                "custody_status": "RECORDED",
                "locator_grants_authority": True,
                "custody_grants_execution_authority": False,
                "custody_grants_admissibility": False,
            },
            evidence_call=lambda receipt_id: {},
            reconstruction_call=lambda receipt_id: {},
        )
        with self.assertRaises(ValueError):
            provider.retain(record, self.evidence())

    def test_reconstruction_must_not_reexecute_consequence(self):
        record = self.record()
        provider = MasterRecordsManifestReceiptProvider(
            submit_call=lambda request: {},
            evidence_call=lambda receipt_id: {},
            reconstruction_call=lambda receipt_id: {
                "manifest_receipt_id": receipt_id,
                "consequence_reexecuted": True,
                "reconstruction_grants_authority": False,
            },
        )
        with self.assertRaises(ValueError):
            provider.reconstruct(record.manifest_receipt_id)


if __name__ == "__main__":
    unittest.main()
