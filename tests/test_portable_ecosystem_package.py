import importlib.util
import json
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools" / "build_portable_ecosystem_package.py"

spec = importlib.util.spec_from_file_location("portable_package_builder", BUILDER)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def read_receipt_from_zip(path: Path) -> dict:
    with zipfile.ZipFile(path) as zf:
        return json.loads(zf.read("PACKAGE_RECEIPT.json"))


def read_receipt_from_tar_gz(path: Path) -> dict:
    with tarfile.open(path, "r:gz") as tf:
        member = tf.getmember("PACKAGE_RECEIPT.json")
        handle = tf.extractfile(member)
        assert handle is not None
        return json.loads(handle.read())


def assert_single_host_sovereignty(receipt: dict) -> None:
    contract = receipt["single_host_sovereignty"]
    assert contract["physical_host_topology"] == "ONE_SOVEREIGN_PHYSICAL_HOST"
    assert contract["additional_physical_machine_required"] is False
    assert contract["third_party_machine_required"] is False
    assert contract["third_party_process_host_required"] is False
    assert contract["third_party_scheduler_required"] is False
    assert contract["third_party_state_host_required"] is False
    assert contract["third_party_control_plane_executor_required"] is False
    assert contract["third_party_platform_availability_may_block_local_operation"] is False
    assert contract["independent_validation_mechanism"] == "SAME_HOST_ISOLATED_LOGICAL_BOUNDARIES"
    assert contract["local_governance_replay_reconstruction_survive_third_party_absence"] is True
    assert contract["credential_authority"] == "TV/TVC"
    assert contract["non_tv_tvc_secret_or_token_allowed"] is False
    assert receipt["physical_additional_machine_required"] is False
    assert receipt["third_party_runtime_infrastructure_required"] is False


def test_s_package_is_sdk_distributable_in_both_required_formats_without_node_membership_claim(tmp_path):
    archives, receipt = module.build_package_set("S", tmp_path)
    assert set(archives) == {"zip", "tar.gz"}
    assert all(path.exists() for path in archives.values())
    assert receipt["channel"] == "SDK_EARLY_ACCESS"
    assert receipt["deployment_class"] == "S"
    assert receipt["required_archive_formats"] == ["zip", "tar.gz"]
    assert receipt["node_membership_claim"] is False
    assert receipt["requires_provider_account"] is False
    assert receipt["requires_non_tv_tvc_secret"] is False
    assert_single_host_sovereignty(receipt)
    assert len(receipt["artifacts"]["zip"]["sha256"]) == 64
    assert len(receipt["artifacts"]["tar.gz"]["sha256"]) == 64
    zip_receipt = read_receipt_from_zip(archives["zip"])
    tar_receipt = read_receipt_from_tar_gz(archives["tar.gz"])
    assert zip_receipt == tar_receipt
    assert zip_receipt["deployment_class"] == "S"
    assert_single_host_sovereignty(zip_receipt)


def test_ns_package_never_self_accredits_node_membership_in_either_format(tmp_path):
    archives, receipt = module.build_package_set("NS", tmp_path)
    assert receipt["deployment_class"] == "NS"
    assert receipt["node_membership_claim"] is False
    assert receipt["node_membership_activation_required"] is True
    assert_single_host_sovereignty(receipt)
    with zipfile.ZipFile(archives["zip"]) as zf:
        names = set(zf.namelist())
        assert "micro_ecosystem/node_sovereign_profile.v1.json" in names
        assert "docs/STEGVERSE_NODE_SOVEREIGN_DEFINITION.md" in names
    with tarfile.open(archives["tar.gz"], "r:gz") as tf:
        names = set(tf.getnames())
        assert "micro_ecosystem/node_sovereign_profile.v1.json" in names
        assert "docs/STEGVERSE_NODE_SOVEREIGN_DEFINITION.md" in names


def test_builder_fails_closed_if_single_host_contract_is_weakened(tmp_path, monkeypatch):
    original = module.load_micro_manifest
    manifest = original()
    manifest["single_host_sovereignty"]["third_party_process_host_required"] = True
    monkeypatch.setattr(module, "MICRO_MANIFEST", tmp_path / "manifest.json")
    module.MICRO_MANIFEST.write_text(json.dumps(manifest), encoding="utf-8")
    try:
        module.build_package_set("S", tmp_path / "dist")
        assert False, "weakened sovereignty contract must fail closed"
    except ValueError as exc:
        assert "prohibited sovereignty dependency" in str(exc)


def test_both_archive_formats_are_byte_deterministic_for_same_source(tmp_path):
    first, receipt_a = module.build_package_set("S", tmp_path / "a")
    second, receipt_b = module.build_package_set("S", tmp_path / "b")
    for archive_format in ("zip", "tar.gz"):
        assert first[archive_format].read_bytes() == second[archive_format].read_bytes()
        assert receipt_a["artifacts"][archive_format]["sha256"] == receipt_b["artifacts"][archive_format]["sha256"]
    assert receipt_a["payload_sha256"] == receipt_b["payload_sha256"]


def test_backward_compatible_build_package_returns_zip_and_dual_artifact_receipt(tmp_path):
    archive, receipt = module.build_package("S", tmp_path)
    assert archive.suffix == ".zip"
    assert receipt["archive_sha256"] == receipt["artifacts"]["zip"]["sha256"]
    assert (tmp_path / archive.name.replace(".zip", ".tar.gz")).is_file()
