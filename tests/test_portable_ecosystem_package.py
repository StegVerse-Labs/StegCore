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
    assert len(receipt["artifacts"]["zip"]["sha256"]) == 64
    assert len(receipt["artifacts"]["tar.gz"]["sha256"]) == 64

    zip_receipt = read_receipt_from_zip(archives["zip"])
    tar_receipt = read_receipt_from_tar_gz(archives["tar.gz"])
    assert zip_receipt == tar_receipt
    assert zip_receipt["deployment_class"] == "S"


def test_ns_package_never_self_accredits_node_membership_in_either_format(tmp_path):
    archives, receipt = module.build_package_set("NS", tmp_path)
    assert receipt["deployment_class"] == "NS"
    assert receipt["node_membership_claim"] is False
    assert receipt["node_membership_activation_required"] is True

    with zipfile.ZipFile(archives["zip"]) as zf:
        names = set(zf.namelist())
        assert "micro_ecosystem/node_sovereign_profile.v1.json" in names
        assert "docs/STEGVERSE_NODE_SOVEREIGN_DEFINITION.md" in names

    with tarfile.open(archives["tar.gz"], "r:gz") as tf:
        names = set(tf.getnames())
        assert "micro_ecosystem/node_sovereign_profile.v1.json" in names
        assert "docs/STEGVERSE_NODE_SOVEREIGN_DEFINITION.md" in names


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
