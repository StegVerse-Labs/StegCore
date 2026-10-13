"""Bounded SVG source adapter to the *installed* native StegCore evaluator.

Governance's G0-G6/A0-A8 schema remains owned by Governance. This adapter
records stage references only; it does not re-evaluate stage vectors or
authenticate external receipts. Native evaluation is not sovereign execution.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
import time
from typing import Any

from stegcore.three_layer import ThreeLayerRequest, evaluate_three_layer

GOVERNANCE_SCHEMA = "StegVerse-Labs/Governance/schemas/admissibility_stage_vector.schema.json"
GOVERNANCE_STAGES = tuple(f"A{i}" for i in range(9))


def evaluate_native_source(request: ThreeLayerRequest, *, governance_stage_vector: dict | None = None) -> dict[str, Any]:
    """Evaluate one typed request using the original native three-layer function."""
    if not isinstance(request, ThreeLayerRequest):
        return {"disposition": "FAIL_CLOSED", "reason": "INVALID_NATIVE_REQUEST",
                "evidence_class": "SOURCE_ONLY", "authority_effect": "NONE"}
    start = time.perf_counter_ns()
    result = evaluate_three_layer(request)
    elapsed_ns = time.perf_counter_ns() - start
    # Validate the pinned exact Governance schema, not just the A0-A8 labels.
    stage_status = "NOT_PROVIDED"
    stage_errors = []
    if governance_stage_vector is not None:
        schema_path = Path(__file__).parent / "schemas/governance_admissibility_stage_vector.schema.json"
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
            validator = Draft202012Validator(schema)
            stage_errors = sorted(e.message for e in validator.iter_errors(governance_stage_vector))
            stage_status = "INVALID" if stage_errors else "SCHEMA_VALID_SOURCE_ONLY"
        except (OSError, ValueError, TypeError, SchemaError) as exc:
            stage_errors = [f"GOVERNANCE_SCHEMA_UNAVAILABLE_OR_INVALID:{type(exc).__name__}"]
            stage_status = "INVALID"
        if not stage_errors and governance_stage_vector["aggregate_disposition"] not in (
            result.decision.replace("-", "_"), "UNKNOWN"
        ):
            stage_status = "INVALID"
            stage_errors.append("AGGREGATE_DISPOSITION_CONFLICTS_WITH_NATIVE_EVALUATION")
    # Schema validation is source conformance only, never authenticated custody.
    # The native evaluator uses FAIL-CLOSED, whereas source benchmark uses FAIL_CLOSED.
    disposition = "FAIL_CLOSED" if stage_status == "INVALID" else result.decision.replace("-", "_")
    return {
        "schema": "stegverse.svg.native-source-observation/v0.1",
        "evidence_class": "SOURCE_ONLY",
        "authority_effect": "NONE",
        "native_evaluator": "stegcore.three_layer.evaluate_three_layer",
        "native_disposition": result.decision,
        "disposition": disposition,
        "reason": "INVALID_GOVERNANCE_STAGE_VECTOR" if stage_status == "INVALID" else result.reason_code,
        "governance_validation_errors": stage_errors,
        "request_hash": result.request_hash,
        "native_receipt_hash": result.receipt.get("receipt_hash"),
        "native_continuity_receipt_minted": result.receipt.get("continuity_receipt_minted"),
        "governance_schema_ref": GOVERNANCE_SCHEMA,
        "governance_stage_vector_status": stage_status,
        "governance_stage_vector_sha256": (
            sha256(json.dumps(governance_stage_vector, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            if stage_status == "SCHEMA_VALID_SOURCE_ONLY" else None
        ),
        "native_evaluator_elapsed_ns": elapsed_ns,
        "authentic_consequence_observed": False,
        "original_master_records_reconstruction_observed": False,
    }
