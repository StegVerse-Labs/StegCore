from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from stegcore.service import runtime_identity, self_test
from stegcore.steggate import AdmissibilityRequest, evaluate_admissibility

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "micro_ecosystem" / "manifest.json"
DEFAULT_REQUEST = ROOT / "examples" / "steggate_allow_request.json"
EXPECTED_RUNTIME_IDENTITY = "stegverse:steggate:canonical:three-layer:v1"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def run_proof(manifest_path: Path, request_path: Path) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    request_payload = load_json(request_path)
    identity = runtime_identity()
    matrix_proof = self_test()
    request = AdmissibilityRequest.model_validate(request_payload)
    result = evaluate_admissibility(request).model_dump(mode="json")

    checks = {
        "manifest_schema": manifest.get("schema") == "stegverse.micro-ecosystem.manifest.v1",
        "runtime_identity_match": identity.get("runtime_identity") == EXPECTED_RUNTIME_IDENTITY == manifest.get("canonical_runtime_identity"),
        "canonical_owner_match": identity.get("canonical_owner") == manifest.get("canonical_owner"),
        "canonical_runtime_match": identity.get("canonical_admissibility_runtime") == manifest.get("canonical_admissibility_runtime"),
        "self_test_pass": matrix_proof.get("state") == "PASS",
        "canonical_three_layer_bound": matrix_proof.get("canonical_three_layer_bound") is True,
        "fixture_disposition_allow": result.get("disposition") == "ALLOW",
        "no_execution_authority": identity.get("execution_authority") is False,
        "no_continuity_minting_authority": identity.get("continuity_receipt_minting_authority") is False,
        "no_external_host_required": manifest.get("authority_boundaries", {}).get("requires_external_host") is False,
        "no_provider_account_required": manifest.get("authority_boundaries", {}).get("requires_provider_account") is False,
        "no_non_tv_tvc_secret_required": manifest.get("authority_boundaries", {}).get("requires_non_tv_tvc_secret") is False,
    }

    receipt = {
        "schema": "stegverse.micro-ecosystem.proof-receipt.v1",
        "micro_ecosystem_id": manifest.get("micro_ecosystem_id"),
        "product_version": manifest.get("product_version"),
        "manifest_sha256": sha256_json(manifest),
        "request_sha256": sha256_json(request_payload),
        "result_sha256": sha256_json(result),
        "runtime_identity": identity,
        "self_test": matrix_proof,
        "evaluation": result,
        "checks": checks,
        "proof_state": "PASS" if all(checks.values()) else "FAIL",
        "external_side_effect": False,
        "execution_authority": False,
        "continuity_receipt_minted": False,
    }
    return receipt


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the portable StegVerse StegGate/AdmittedCode micro-ecosystem proof.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--request", type=Path, default=DEFAULT_REQUEST)
    parser.add_argument("--output", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    receipt = run_proof(args.manifest, args.request)
    rendered = json.dumps(receipt, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if receipt["proof_state"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
