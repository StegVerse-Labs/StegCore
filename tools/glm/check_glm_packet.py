#!/usr/bin/env python3
"""Validate the StegCore GLM boundary packet."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "glm/org-index.json",
    "glm/layers/transition-admissibility.glm.json",
    "schemas/glm/transition-receipt.schema.json",
    "schemas/glm/authority-class.schema.json",
    "schemas/glm/policy-reference.schema.json",
    "examples/glm/transition-receipt.allow.example.json",
    "examples/glm/transition-receipt.deny.example.json",
    "docs/glm/README.md",
    "docs/glm/STEGVERSE_GLM_BOUNDARY_NOTE.md",
    "docs/glm/STEGVERSE_GLM_VALIDATION_CHECKLIST.md",
    "docs/glm/STEGVERSE_GLM_REVIEW_RUBRIC.md",
    "docs/glm/STEGVERSE_GLM_FEEDBACK_PLAN.md",
    "docs/glm/emanuel-review-note.md",
    "docs/STEGCORE_GLM_MIRROR_HANDOFF.md",
]

POSITIVE_OVERCLAIMS = [
    "this index certifies interoperability",
    "this layer certifies interoperability",
    "automatic authority inheritance is enabled",
    "semantically merged by default",
    "globally valid transition",
]


def fail(message: str) -> int:
    print(f"stegcore glm packet check failed: {message}")
    return 1


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_json(path: str) -> dict:
    with (ROOT / path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    try:
        for file_path in REQUIRED_FILES:
            require((ROOT / file_path).exists(), f"missing required file: {file_path}")

        org_index = load_json("glm/org-index.json")
        layer = load_json("glm/layers/transition-admissibility.glm.json")
        allow_receipt = load_json("examples/glm/transition-receipt.allow.example.json")
        deny_receipt = load_json("examples/glm/transition-receipt.deny.example.json")

        require(org_index.get("index_scope") == "discovery_only", "organization index must be discovery_only")
        composition = org_index.get("composition_posture", {})
        require(composition.get("composition_by_index") is False, "index must not compose layers")
        require(composition.get("authority_inheritance_by_index") is False, "index must not create authority inheritance")
        require(composition.get("semantic_merging_by_index") is False, "index must not create semantic merging")
        require(composition.get("interoperability_certification_by_index") is False, "index must not certify interoperability")

        assertion = layer.get("admissibility_assertion", {})
        require(assertion.get("assertion_scope") == "layer_scoped", "admissibility assertion must be layer scoped")
        require(assertion.get("universal_admissibility_claim") is False, "must reject universal admissibility")
        require(assertion.get("commit_time_bound") is True, "assertion must be commit-time bound")

        layer_composition = layer.get("composition_posture", {})
        require(layer_composition.get("authority_inheritance") is False, "layer must reject authority inheritance")
        require(layer_composition.get("semantic_merging") is False, "layer must reject semantic merging")
        require(layer_composition.get("automatic_interoperability") is False, "layer must reject automatic interoperability")

        require(len(layer.get("observes", [])) >= 5, "layer must list observed conditions")
        require(len(layer.get("assumes_but_does_not_independently_validate", [])) >= 5, "layer must list external assumptions")
        require(len(layer.get("non_claims", [])) >= 5, "layer must list non-claims")
        require("five_question_boundary_model" in layer, "layer must answer five-question model")
        require(len(layer["five_question_boundary_model"].keys()) == 5, "five-question model must have five answers")

        require(allow_receipt.get("admissibility_result") == "ADMIT", "allow example must admit")
        require(deny_receipt.get("admissibility_result") == "DENY", "deny example must deny")
        for receipt_name, receipt in [("allow", allow_receipt), ("deny", deny_receipt)]:
            require(receipt.get("layer_id") == "stegverse-transition-admissibility", f"{receipt_name} receipt layer mismatch")
            require("authority_class" in receipt, f"{receipt_name} receipt missing authority class")
            require("policy_reference" in receipt, f"{receipt_name} receipt missing policy reference")
            require("external_assumptions" in receipt, f"{receipt_name} receipt missing assumptions")
            require("non_claims" in receipt, f"{receipt_name} receipt missing non-claims")

        text_parts = []
        for file_path in REQUIRED_FILES:
            if file_path.endswith((".md", ".py", ".json")):
                text_parts.append((ROOT / file_path).read_text(encoding="utf-8"))
        combined = "\n".join(text_parts).lower()
        for phrase in POSITIVE_OVERCLAIMS:
            require(phrase not in combined, f"positive overclaim present: {phrase}")

    except AssertionError as exc:
        return fail(str(exc))
    except json.JSONDecodeError as exc:
        return fail(f"invalid JSON: {exc}")

    print("valid: StegCore GLM boundary packet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
