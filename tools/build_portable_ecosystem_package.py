from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import shutil
import subprocess
import tarfile
import tempfile
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "sdk" / "portable_package_catalog.v1.json"
MICRO_MANIFEST = ROOT / "micro_ecosystem" / "manifest.json"
DEPLOYMENT_CLASSES = ("S", "NS")
ARCHIVE_FORMATS = ("zip", "tar.gz")
FIXED_MTIME = 0


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def load_catalog() -> dict[str, Any]:
    value = json.loads(CATALOG.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("portable package catalog must be an object")
    return value


def load_micro_manifest() -> dict[str, Any]:
    value = json.loads(MICRO_MANIFEST.read_text(encoding="utf-8"))
    contract = value.get("single_host_sovereignty")
    if not isinstance(contract, dict):
        raise ValueError("micro ecosystem manifest lacks single_host_sovereignty contract")
    required_false = (
        "additional_physical_machine_required", "third_party_machine_required",
        "third_party_process_host_required", "third_party_scheduler_required",
        "third_party_state_host_required", "third_party_control_plane_executor_required",
        "third_party_platform_availability_may_block_local_operation",
        "non_tv_tvc_secret_or_token_allowed",
    )
    if contract.get("physical_host_topology") != "ONE_SOVEREIGN_PHYSICAL_HOST":
        raise ValueError("portable ecosystem must declare ONE_SOVEREIGN_PHYSICAL_HOST")
    if contract.get("independent_validation_mechanism") != "SAME_HOST_ISOLATED_LOGICAL_BOUNDARIES":
        raise ValueError("portable ecosystem must use same-host logical isolation")
    if contract.get("credential_authority") != "TV/TVC":
        raise ValueError("portable ecosystem credential authority must remain TV/TVC")
    if any(contract.get(name) is not False for name in required_false):
        raise ValueError("portable ecosystem declares a prohibited sovereignty dependency")
    if contract.get("local_governance_replay_reconstruction_survive_third_party_absence") is not True:
        raise ValueError("portable ecosystem must remain locally operable without third-party runtime infrastructure")
    return value


def iter_payload_files(required_paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for rel in required_paths:
        source = ROOT / rel
        if not source.exists():
            raise FileNotFoundError(rel)
        if source.is_dir():
            files.extend(sorted(path for path in source.rglob("*") if path.is_file() and "__pycache__" not in path.parts))
        else:
            files.append(source)
    return sorted(set(files), key=lambda p: p.relative_to(ROOT).as_posix())


def validate_no_secret_material(files: list[Path]) -> None:
    prohibited_names = {".env", ".env.local", "id_rsa", "id_ed25519"}
    prohibited_suffixes = {".pem", ".key", ".p12", ".pfx"}
    for path in files:
        if path.name in prohibited_names or path.suffix.lower() in prohibited_suffixes:
            raise ValueError(f"prohibited secret-bearing file in package payload: {path.relative_to(ROOT)}")


def _stage_payload(stage: Path, files: list[Path], manifest: dict[str, Any]) -> None:
    for path in files:
        rel = path.relative_to(ROOT)
        target = stage / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    (stage / "PACKAGE_RECEIPT.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_zip(stage: Path, archive: Path) -> None:
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(stage.rglob("*"), key=lambda p: p.relative_to(stage).as_posix()):
            if not path.is_file():
                continue
            info = zipfile.ZipInfo(path.relative_to(stage).as_posix())
            info.date_time = (1980, 1, 1, 0, 0, 0)
            info.external_attr = (0o644 & 0xFFFF) << 16
            info.create_system = 3
            zf.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED)


def _write_tar_gz(stage: Path, archive: Path) -> None:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w", format=tarfile.PAX_FORMAT) as tf:
        for path in sorted(stage.rglob("*"), key=lambda p: p.relative_to(stage).as_posix()):
            if not path.is_file():
                continue
            data = path.read_bytes()
            info = tarfile.TarInfo(path.relative_to(stage).as_posix())
            info.size = len(data); info.mode = 0o644; info.mtime = FIXED_MTIME
            info.uid = 0; info.gid = 0; info.uname = ""; info.gname = ""
            tf.addfile(info, io.BytesIO(data))
    with archive.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=FIXED_MTIME) as gz:
            gz.write(buffer.getvalue())


def build_package_set(deployment_class: str, output_dir: Path) -> tuple[dict[str, Path], dict[str, Any]]:
    if deployment_class not in DEPLOYMENT_CLASSES:
        raise ValueError(f"unsupported deployment class: {deployment_class}")
    catalog = load_catalog()
    micro_manifest = load_micro_manifest()
    sovereignty = micro_manifest["single_host_sovereignty"]
    package = catalog["packages"][deployment_class]
    files = iter_payload_files(catalog["required_payload_paths"])
    validate_no_secret_material(files)
    manifest = {
        "schema": "stegverse.sdk.portable-package-receipt.v2",
        "catalog_schema": catalog["schema"], "channel": catalog["channel"],
        "package_id": package["package_id"], "deployment_class": deployment_class,
        "source_commit": git_commit(), "required_archive_formats": list(ARCHIVE_FORMATS),
        "archive_format_authority_effect": "NONE",
        "node_membership_claim": package.get("node_membership_claim", False),
        "node_membership_activation_required": package.get("node_membership_activation_required", False),
        "files": [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha256_file(path), "size": path.stat().st_size} for path in files],
        "requires_provider_account": False, "requires_non_tv_tvc_secret": False,
        "single_host_sovereignty": sovereignty,
        "physical_additional_machine_required": False,
        "third_party_runtime_infrastructure_required": False,
    }
    manifest["payload_sha256"] = hashlib.sha256(canonical_json_bytes(manifest["files"])).hexdigest()
    output_dir.mkdir(parents=True, exist_ok=True)
    archives = {"zip": output_dir / f"{package['package_id']}.zip", "tar.gz": output_dir / f"{package['package_id']}.tar.gz"}
    with tempfile.TemporaryDirectory() as tmp:
        stage = Path(tmp) / package["package_id"]; stage.mkdir(parents=True)
        _stage_payload(stage, files, manifest); _write_zip(stage, archives["zip"]); _write_tar_gz(stage, archives["tar.gz"])
    receipt = {**manifest, "artifacts": {fmt: {"path": archive.name, "sha256": sha256_file(archive), "size": archive.stat().st_size} for fmt, archive in archives.items()}}
    return archives, receipt


def build_package(deployment_class: str, output_dir: Path) -> tuple[Path, dict[str, Any]]:
    archives, receipt = build_package_set(deployment_class, output_dir)
    compatibility_receipt = dict(receipt); compatibility_receipt["archive_sha256"] = receipt["artifacts"]["zip"]["sha256"]
    return archives["zip"], compatibility_receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Build deterministic ZIP and TAR.GZ StegVerse SDK portable ecosystem packages.")
    parser.add_argument("--deployment-class", choices=DEPLOYMENT_CLASSES, required=True)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist" / "sdk")
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    archives, receipt = build_package_set(args.deployment_class, args.output_dir)
    rendered = json.dumps(receipt, indent=2, sort_keys=True)
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True); args.receipt.write_text(rendered + "\n", encoding="utf-8")
    print(json.dumps({"archives": {key: str(value) for key, value in archives.items()}, "receipt": receipt}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
