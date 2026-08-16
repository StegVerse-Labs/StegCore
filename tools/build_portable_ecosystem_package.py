from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "sdk" / "portable_package_catalog.v1.json"
DEPLOYMENT_CLASSES = ("S", "NS")


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
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return None


def load_catalog() -> dict[str, Any]:
    value = json.loads(CATALOG.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("portable package catalog must be an object")
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


def build_package(deployment_class: str, output_dir: Path) -> tuple[Path, dict[str, Any]]:
    if deployment_class not in DEPLOYMENT_CLASSES:
        raise ValueError(f"unsupported deployment class: {deployment_class}")

    catalog = load_catalog()
    package = catalog["packages"][deployment_class]
    files = iter_payload_files(catalog["required_payload_paths"])
    validate_no_secret_material(files)

    manifest = {
        "schema": "stegverse.sdk.portable-package-receipt.v1",
        "catalog_schema": catalog["schema"],
        "channel": catalog["channel"],
        "package_id": package["package_id"],
        "deployment_class": deployment_class,
        "source_commit": git_commit(),
        "node_membership_claim": package.get("node_membership_claim", False),
        "node_membership_activation_required": package.get("node_membership_activation_required", False),
        "files": [
            {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": sha256_file(path),
                "size": path.stat().st_size,
            }
            for path in files
        ],
        "requires_provider_account": False,
        "requires_non_tv_tvc_secret": False,
    }
    manifest["payload_sha256"] = hashlib.sha256(canonical_json_bytes(manifest["files"])).hexdigest()

    output_dir.mkdir(parents=True, exist_ok=True)
    archive = output_dir / f"{package['package_id']}.zip"

    with tempfile.TemporaryDirectory() as tmp:
        stage = Path(tmp) / package["package_id"]
        for path in files:
            rel = path.relative_to(ROOT)
            target = stage / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
        (stage / "PACKAGE_RECEIPT.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for path in sorted(stage.rglob("*")):
                if path.is_file():
                    info = zipfile.ZipInfo(path.relative_to(stage).as_posix())
                    info.date_time = (1980, 1, 1, 0, 0, 0)
                    info.external_attr = (0o644 & 0xFFFF) << 16
                    zf.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED)

    manifest["archive_sha256"] = sha256_file(archive)
    return archive, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a deterministic StegVerse SDK portable ecosystem package.")
    parser.add_argument("--deployment-class", choices=DEPLOYMENT_CLASSES, required=True)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist" / "sdk")
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    archive, receipt = build_package(args.deployment_class, args.output_dir)
    rendered = json.dumps(receipt, indent=2, sort_keys=True)
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(rendered + "\n", encoding="utf-8")
    print(json.dumps({"archive": str(archive), "receipt": receipt}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
