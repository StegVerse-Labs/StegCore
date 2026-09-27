"""Bounded SVG source adapter to the *installed* native StegCore evaluator.

Governance's G0-G6/A0-A8 schema remains owned by Governance. This adapter
records stage references only; it does not re-evaluate stage vectors or
authenticate external receipts. Native evaluation is not sovereign execution.
"""
from __future__ import annotations
from dataclasses import asdict
from hashlib import sha256
import json
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
    # Never convert an unverified stage vector into original Governance evidence.
    stage_status = "NOT_PROVIDED"
    if governance_stage_vector is not None:
        if not isinstance(governance_stage_vector, dict):
            stage_status = "INVALID"
        elif (governance_stage_vector.get("schema_version") == "1.0.0"
              and isinstance(governance_stage_vector.get("stages"), list)
              and [s.get("stage") for s in governance_stage_vector["stages"] if isinstance(s, dict)]
              == list(GOVERNANCE_STAGES)
              and len(governance_stage_vector["stages"]) == 9):
            stage_status = "SHAPE_ONLY_UNVALIDATED"
        else:
            stage_status = "INVALID"
    # The native evaluator uses FAIL-CLOSED, whereas source benchmark uses FAIL_CLOSED.
    disposition = result.decision.replace("-", "_")
    return {
        "schema": "stegverse.svg.native-source-observation/v0.1",
        "evidence_class": "SOURCE_ONLY",
        "authority_effect": "NONE",
        "native_evaluator": "stegcore.three_layer.evaluate_three_layer",
        "native_disposition": result.decision,
        "disposition": disposition,
        "reason": result.reason_code,
        "request_hash": result.request_hash,
        "native_receipt_hash": result.receipt.get("receipt_hash"),
        "native_continuity_receipt_minted": result.receipt.get("continuity_receipt_minted"),
        "governance_schema_ref": GOVERNANCE_SCHEMA,
        "governance_stage_vector_status": stage_status,
        "governance_stage_vector_sha256": (
            sha256(json.dumps(governance_stage_vector, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            if stage_status == "SHAPE_ONLY_UNVALIDATED" else None
        ),
        "native_evaluator_elapsed_ns": elapsed_ns,
        "authentic_consequence_observed": False,
        "original_master_records_reconstruction_observed": False,
    }
