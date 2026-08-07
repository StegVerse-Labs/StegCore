#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "ecosystem_management/child_mode_authority_runtime.v0.1.json"
HANDOFF = ROOT / "docs/CHILD_MODE_AUTHORITY_RUNTIME_MIRROR_HANDOFF.md"
RECEIPT = ROOT / "docs/stegverse_admissibility_receipt_v1.md"
REPORT = ROOT / "brain_reports/child_mode_authority_runtime_report.json"

REQUIRED_DENY = {
    "UNKNOWN_PERSON_DM",
    "PUBLIC_DISCOVERY",
    "ENGAGEMENT_RECOMMENDER",
    "BEHAVIORAL_AD_PROFILE",
    "PRECISE_LOCATION_DISCLOSURE",
    "NORMAL_MODE_REQUEST_BY_INELIGIBLE_USER",
}
REQUIRED_ALLOW = {"KNOWN_CONTACT_MESSAGE", "APPROVED_COLLABORATION", "REPORT_BLOCK"}
REQUIRED_DATA = {
    "contacts",
    "photos_videos_files",
    "precise_background_location",
    "microphone_camera_derived_nonessential",
    "clipboard",
    "browsing_application_activity",
    "advertising_identifiers",
    "cross_app_cross_service_identifiers",
    "behavioral_profiles_inferred_interests",
    "nonessential_telemetry",
}
REQUIRED_RECEIPT_EXTENSIONS = {
    "subject_reference",
    "jurisdiction",
    "age_eligibility_evidence_reference",
    "device_account_state_reference",
    "guardian_known_contact_evidence_reference",
    "requested_capability_or_data_class",
    "purpose",
    "recipient",
    "retention_window",
    "released_amount",
    "pilot_authority_reference",
}


def fail(failures: list[str]) -> int:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({"status": "FAIL", "failures": failures}, indent=2) + "\n", encoding="utf-8")
    print("CHILD_MODE_AUTHORITY_RUNTIME=FAIL")
    for item in failures:
        print(f"- {item}")
    return 1


def main() -> int:
    failures: list[str] = []
    for path in (STATE, HANDOFF, RECEIPT):
        if not path.is_file():
            failures.append(f"missing {path.relative_to(ROOT)}")
    if failures:
        return fail(failures)

    state = json.loads(STATE.read_text(encoding="utf-8"))
    handoff = HANDOFF.read_text(encoding="utf-8")
    receipt = RECEIPT.read_text(encoding="utf-8")

    if state.get("goal_id") != "STEGCORE-CHILD-MODE-AUTHORITY-RUNTIME-001":
        failures.append("goal_id mismatch")
    if state.get("repository") != "StegVerse-Labs/StegCore":
        failures.append("repository mismatch")
    if state.get("authority_effect") is not False:
        failures.append("authority_effect must remain false")
    if state.get("pilot_activation") is not False:
        failures.append("pilot_activation must remain false until lawful authorization exists")

    baseline = state.get("baseline", {})
    expected_baseline = {
        "optional_data_harvesting": "DENY_BY_DEFAULT",
        "undeclared_data_egress": "NONE",
        "normal_mode_bypass": "DENY",
        "child_ui_consent_harvesting_authority": False,
        "mandatory_age_floor_overridable": False,
        "fail_closed": True,
    }
    for key, expected in expected_baseline.items():
        if baseline.get(key) != expected:
            failures.append(f"baseline {key} must equal {expected!r}")

    vectors = state.get("decision_vectors", [])
    denied = {v.get("request") for v in vectors if v.get("expected") == "DENY"}
    allowed = {v.get("request") for v in vectors if v.get("expected") == "ALLOW"}
    if not REQUIRED_DENY.issubset(denied):
        failures.append(f"missing required DENY vectors: {sorted(REQUIRED_DENY - denied)}")
    if not REQUIRED_ALLOW.issubset(allowed):
        failures.append(f"missing required ALLOW vectors: {sorted(REQUIRED_ALLOW - allowed)}")

    data = state.get("data_authority", {})
    if data.get("default") != "DENY":
        failures.append("data authority default must be DENY")
    protected = set(data.get("protected_classes", []))
    if not REQUIRED_DATA.issubset(protected):
        failures.append(f"missing protected data classes: {sorted(REQUIRED_DATA - protected)}")
    scope_fields = set(data.get("authorization_scope_fields", []))
    for field in ("data_class", "purpose", "recipient", "retention_window", "authority_reference"):
        if field not in scope_fields:
            failures.append(f"missing authorization scope field: {field}")

    mapping = state.get("receipt_mapping", {})
    if mapping.get("canonical_receipt_reference") != "docs/stegverse_admissibility_receipt_v1.md":
        failures.append("canonical receipt reference mismatch")
    if mapping.get("receipt_creates_authority") is not False:
        failures.append("receipt must not create authority")
    extensions = set(mapping.get("required_child_mode_extensions", []))
    if not REQUIRED_RECEIPT_EXTENSIONS.issubset(extensions):
        failures.append(f"missing receipt extensions: {sorted(REQUIRED_RECEIPT_EXTENSIONS - extensions)}")

    pilot = state.get("pilot", {})
    if pilot.get("requires_lawful_regulator_authority") is not True:
        failures.append("pilot must require lawful/regulator authority")
    if pilot.get("self_exemption_allowed") is not False:
        failures.append("self exemption must remain false")
    if set(pilot.get("evidence_layers", [])) != {"ELIGIBILITY", "CAPABILITY", "DATA_EGRESS", "BOUNDARY_CHANGE", "OUTCOME_INCIDENT"}:
        failures.append("pilot evidence layers incomplete")

    consolidation = state.get("session_consolidation", {})
    if consolidation.get("source_goals_transferred") != consolidation.get("source_goals_total"):
        failures.append("source session goals not fully transferred")
    if consolidation.get("unique_chat_only_requirements_remaining") != 0:
        failures.append("chat-only requirements remain")
    if consolidation.get("originating_chat_archive_dependency") is not False:
        failures.append("originating chat must not remain an execution dependency")

    handoff_markers = (
        "MERGED INTO: StegVerse-Labs/StegCore/docs/CHILD_MODE_AUTHORITY_RUNTIME_MIRROR_HANDOFF.md",
        "OPTIONAL_DATA_HARVESTING=DENY_BY_DEFAULT",
        "NORMAL_MODE_BYPASS=DENY",
        "UNDECLARED_DATA_EGRESS=NONE",
        "AUTHORITY_GRANTED=false",
    )
    for marker in handoff_markers:
        if marker not in handoff:
            failures.append(f"handoff missing marker: {marker}")

    receipt_markers = ("stegverse.admissibility_receipt.v1", "scope", "canonicalization", "decision.fingerprint")
    for marker in receipt_markers:
        if marker not in receipt:
            failures.append(f"canonical receipt document missing marker: {marker}")

    if failures:
        return fail(failures)

    report = {
        "status": "PASS",
        "goal_id": state["goal_id"],
        "repository": state["repository"],
        "authority_granted": False,
        "pilot_activation": False,
        "optional_data_harvesting": "DENY_BY_DEFAULT",
        "normal_mode_bypass": "DENY",
        "undeclared_data_egress": "NONE",
        "fail_closed": True,
        "decision_vectors": len(vectors),
        "protected_data_classes": len(protected),
        "source_goals_transferred": consolidation.get("source_goals_transferred"),
        "source_goals_total": consolidation.get("source_goals_total"),
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("CHILD_MODE_AUTHORITY_RUNTIME=PASS")
    print("OPTIONAL_DATA_HARVESTING=DENY_BY_DEFAULT")
    print("NORMAL_MODE_BYPASS=DENY")
    print("UNDECLARED_DATA_EGRESS=NONE")
    print("FAIL_CLOSED=true")
    print("AUTHORITY_GRANTED=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
