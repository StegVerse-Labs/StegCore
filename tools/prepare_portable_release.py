from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "sdk" / "portable_release_manifest.v1.json"
PACKAGE_BUILDER = ROOT / "tools" / "build_portable_ecosystem_package.py"
VERSION_RE = re.compile(r'^version\s*=\s*["\']([^"\']+)["\']\s*$', re.MULTILINE)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_version() -> str:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = VERSION_RE.search(text)
    if not match:
        raise ValueError("source_version_not_found")
    return match.group(1)


def source_commit() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def validate_manifest(manifest: dict[str, Any]) -> None:
    if manifest.get("schema") != "stegverse.sdk.portable-release-manifest.v1":
        raise ValueError("unsupported_release_manifest_schema")
    release_version = str(manifest.get("release_version", ""))
    observed_source_version = source_version()
    if release_version != observed_source_version:
        raise ValueError(f"release_source_version_mismatch:{release_version}:{observed_source_version}")
    if manifest.get("source_version") != observed_source_version:
        raise ValueError("declared_source_version_mismatch")
    component_versions = manifest.get("versioned_components")
    if not isinstance(component_versions, dict) or not component_versions:
        raise ValueError("versioned_components_missing")
    bad = sorted(k for k, v in component_versions.items() if str(v) != release_version)
    if bad:
        raise ValueError("component_version_mismatch:" + ",".join(bad))
    if manifest.get("required_archive_formats") != ["zip", "tar.gz"]:
        raise ValueError("dual_archive_formats_required")
    if manifest.get("release_tag") != f"stegverse-portable-v{release_version}":
        raise ValueError("release_tag_version_mismatch")


def build_class(deployment_class: str, output_dir: Path) -> dict[str, Any]:
    receipt_path = output_dir / f"{deployment_class.lower()}-build-receipt.json"
    command = [
        sys.executable,
        str(PACKAGE_BUILDER),
        "--deployment-class",
        deployment_class,
        "--output-dir",
        str(output_dir),
        "--receipt",
        str(receipt_path),
    ]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"package_build_failed:{deployment_class}:{result.stderr[-2000:]}")
    receipt = load_json(receipt_path)
    artifacts = receipt.get("artifacts")
    if not isinstance(artifacts, dict) or set(artifacts) != {"zip", "tar.gz"}:
        raise ValueError(f"dual_artifacts_missing:{deployment_class}")
    return receipt


def prepare_release(output_dir: Path) -> dict[str, Any]:
    manifest = load_json(MANIFEST_PATH)
    validate_manifest(manifest)
    output_dir.mkdir(parents=True, exist_ok=True)
    commit = source_commit()
    built = {deployment_class: build_class(deployment_class, output_dir) for deployment_class in ("S", "NS")}

    assets: list[dict[str, Any]] = []
    for deployment_class, receipt in built.items():
        if receipt.get("source_commit") != commit:
            raise ValueError(f"source_commit_mismatch:{deployment_class}")
        for archive_format, artifact in sorted(receipt["artifacts"].items()):
            path = Path(artifact["path"])
            if not path.is_absolute():
                path = ROOT / path
            if not path.is_file():
                raise FileNotFoundError(path)
            observed = sha256_file(path)
            if observed != artifact["sha256"]:
                raise ValueError(f"archive_hash_mismatch:{path.name}")
            assets.append({
                "deployment_class": deployment_class,
                "archive_format": archive_format,
                "name": path.name,
                "path": str(path),
                "sha256": observed,
                "size": path.stat().st_size,
            })

    assets.sort(key=lambda row: row["name"])
    sums_path = output_dir / "SHA256SUMS"
    sums_path.write_text("".join(f"{row['sha256']}  {row['name']}\n" for row in assets), encoding="utf-8")
    assets.append({
        "deployment_class": None,
        "archive_format": "checksums",
        "name": sums_path.name,
        "path": str(sums_path),
        "sha256": sha256_file(sums_path),
        "size": sums_path.stat().st_size,
    })

    receipt = {
        "schema": "stegverse.sdk.portable-release-candidate-receipt.v1",
        "release_family": manifest["release_family"],
        "release_version": manifest["release_version"],
        "release_tag": manifest["release_tag"],
        "release_name": manifest["release_name"],
        "channel": manifest["channel"],
        "source_commit": commit,
        "versioned_components": manifest["versioned_components"],
        "assets": assets,
        "release_publication_state": "CANDIDATE_NOT_PUBLISHED",
        "publication_authority": "TV/TVC",
        "github_build_is_runtime_authority": False,
        "github_release_is_execution_authority": False,
        "node_membership_granted": False,
    }
    receipt_path = output_dir / "PORTABLE_RELEASE_RECEIPT.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a deterministic StegVerse portable GitHub release candidate.")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist" / "portable-release")
    args = parser.parse_args()
    try:
        receipt = prepare_release(args.output_dir)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print(json.dumps({"state": "FAIL_CLOSED", "error": str(exc)}, indent=2, sort_keys=True))
        return 2
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
