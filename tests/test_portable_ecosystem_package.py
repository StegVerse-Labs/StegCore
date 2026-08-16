import importlib.util
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools" / "build_portable_ecosystem_package.py"

spec = importlib.util.spec_from_file_location("portable_package_builder", BUILDER)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def test_s_package_is_sdk_distributable_without_node_membership_claim(tmp_path):
    archive, receipt = module.build_package("S", tmp_path)
    assert archive.exists()
    assert receipt["channel"] == "SDK_EARLY_ACCESS"
    assert receipt["deployment_class"] == "S"
    assert receipt["node_membership_claim"] is False
    assert receipt["requires_provider_account"] is False
    assert receipt["requires_non_tv_tvc_secret"] is False
    assert len(receipt["archive_sha256"]) == 64
    with zipfile.ZipFile(archive) as zf:
        names = set(zf.namelist())
        assert "PACKAGE_RECEIPT.json" in names
        package_receipt = json.loads(zf.read("PACKAGE_RECEIPT.json"))
        assert package_receipt["deployment_class"] == "S"


def test_ns_package_never_self_accredits_node_membership(tmp_path):
    archive, receipt = module.build_package("NS", tmp_path)
    assert archive.exists()
    assert receipt["deployment_class"] == "NS"
    assert receipt["node_membership_claim"] is False
    assert receipt["node_membership_activation_required"] is True
    with zipfile.ZipFile(archive) as zf:
        names = set(zf.namelist())
        assert "micro_ecosystem/node_sovereign_profile.v1.json" in names
        assert "docs/STEGVERSE_NODE_SOVEREIGN_DEFINITION.md" in names


def test_package_builder_is_byte_deterministic_for_same_source(tmp_path):
    first, receipt_a = module.build_package("S", tmp_path / "a")
    second, receipt_b = module.build_package("S", tmp_path / "b")
    assert first.read_bytes() == second.read_bytes()
    assert receipt_a["archive_sha256"] == receipt_b["archive_sha256"]
    assert receipt_a["payload_sha256"] == receipt_b["payload_sha256"]
