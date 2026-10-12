import tempfile
import unittest
from pathlib import Path

from stegcore.manifest_receipts import ManifestReceiptRegistry, manifest_receipt_id_for
from stegcore.transaction_lifecycle import ManifestedTransactionResult, ReplayDescriptor, TransactionManifest, TransitionReceipt


class ManifestReceiptRegistryTests(unittest.TestCase):
    def make_result(self):
        manifest = TransactionManifest(
            transaction_id="TX-1",
            created_at="2026-08-12T19:00:00Z",
            source="test",
            subject="case",
            processing_capability="governance",
            route_id="stegverse.route.canonical-governed.v1",
            input_hash="a" * 64,
            candidate_hash="b" * 64,
            request_hash="c" * 64,
            manifest_hash="d" * 64,
        )
        receipts = [
            TransitionReceipt(
                transaction_id="TX-1", sequence=0, observed_at="2026-08-12T19:00:01Z",
                stage="ingestion", state="MANIFEST_ADMITTED", processor="test",
                receipt_hash="e" * 64,
            ),
            TransitionReceipt(
                transaction_id="TX-1", sequence=1, observed_at="2026-08-12T19:00:02Z",
                stage="steggate", state="ALLOW", processor="test",
                previous_receipt_hash="e" * 64, receipt_hash="f" * 64,
            ),
        ]
        replay = ReplayDescriptor(
            transaction_id="TX-1", manifest_hash=manifest.manifest_hash,
            request_hash=manifest.request_hash,
            canonical_runtime_identity=f"{manifest.processing_capability}@{manifest.route_id}",
            receipt_chain_head="f" * 64, receipt_count=2,
            expected_disposition="ALLOW", expected_executor_invoked=False,
        )
        return ManifestedTransactionResult(
            transaction_id="TX-1", manifest=manifest, receipts=receipts,
            execution_observation={"evaluation": {"disposition": "ALLOW"}},
            replay=replay, chain_verified=True,
        )

    def test_register_resolve_and_reload_exact_run(self):
        result = self.make_result()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest_receipts.jsonl"
            registry = ManifestReceiptRegistry(path)
            record = registry.register(result)
            self.assertEqual(record.manifest_receipt_id, manifest_receipt_id_for(result))
            self.assertFalse(record.locator_grants_authority)
            loaded = ManifestReceiptRegistry(path)
            self.assertEqual(loaded.resolve(record.manifest_receipt_id).record_hash, record.record_hash)

    def test_reconstruction_never_reexecutes_consequence(self):
        registry = ManifestReceiptRegistry()
        record = registry.register(self.make_result())
        reconstruction = registry.reconstruct(record.manifest_receipt_id)
        self.assertFalse(reconstruction.consequence_reexecuted)
        self.assertEqual(reconstruction.persisted_evidence[0]["evidence_class"], "NATIVELY_PERSISTED")

    def test_replay_links_original_and_requires_no_consequence(self):
        registry = ManifestReceiptRegistry()
        record = registry.register(self.make_result())
        replay = registry.replay(record.manifest_receipt_id, lambda evidence: {
            "governance_state": "ALLOW",
            "manifest_hash": evidence["manifest"]["manifest_hash"],
            "input_hash": evidence["manifest"]["input_hash"],
            "consequence_executed": False,
        })
        self.assertEqual(replay.original_manifest_receipt_id, record.manifest_receipt_id)
        self.assertTrue(replay.deterministic_disposition_match)
        self.assertFalse(replay.consequence_reexecuted)

        with self.assertRaises(ValueError):
            registry.replay(record.manifest_receipt_id, lambda _evidence: {"governance_state": "ALLOW", "consequence_executed": True})

    def test_unknown_id_fails_closed(self):
        with self.assertRaises(KeyError):
            ManifestReceiptRegistry().resolve("MR-DOESNOTEXIST")


if __name__ == "__main__":
    unittest.main()
