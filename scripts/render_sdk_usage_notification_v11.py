#!/usr/bin/env python3
from __future__ import annotations

"""Validate and render SDK usage notification schema v1.1.

v1.1 distinguishes a governance-menu selection from an actual governed
operation. This prevents option 1/2 guidance views from being reported as
replay/reconstruction runs. The renderer is allowlist-only and rejects payload
or authority-bearing fields.
"""

import json
import sys
from typing import Any


CHOICES = ("000", "00", "0", "1", "2")
LABELS = {
    "000": "Demo test sequence without user-supplied manifest",
    "00": "User-defined run parameters",
    "0": "Submit data for governance",
    "1": "Replay previously run set",
    "2": "Reconstruct previously run set",
}
EVENT_KEYS = {
    "event_id",
    "invocation_id",
    "occurred_at",
    "choice_code",
    "choice_label",
    "phase",
    "activity_kind",
    "canonical_runtime_identity",
    "source",
    "manifest_receipt_id",
    "transaction_id",
    "receipt_chain_head",
    "consequence_reexecuted",
}
USAGE_KEYS = {
    "artifact_type",
    "schema_version",
    "generated_at",
    "observed_since",
    "historical_coverage",
    "lifetime_all_menu_invocations",
    "trailing_30_day_all_menu_invocations",
    "lifetime_core_governed_invocations",
    "trailing_30_day_core_governed_invocations",
    "choices",
    "payload_disclosed",
    "observation_grants_authority",
}
CHOICE_KEYS = {
    "choice_code",
    "choice_label",
    "lifetime_invocations",
    "trailing_30_day_invocations",
    "percent_of_total",
    "last_used_at",
    "unique_runtime_identities",
    "completed",
    "failed",
    "cancelled",
    "in_progress",
    "menu_selections",
    "governed_operations",
}


def _exact_keys(value: dict[str, Any], allowed: set[str], name: str) -> None:
    extras = set(value) - allowed
    missing = allowed - set(value)
    if extras:
        raise ValueError(f"{name} contains unsupported fields: {sorted(extras)}")
    if missing:
        raise ValueError(f"{name} is missing required fields: {sorted(missing)}")


def _text(value: Any, field: str, *, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    if len(value) > 512:
        raise ValueError(f"{field} exceeds notification length limit")
    return value.strip()


def _count(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def validate_projection(data: dict[str, Any]) -> dict[str, Any]:
    _exact_keys(
        data,
        {
            "schema_version",
            "event",
            "usage",
            "payload_disclosed",
            "notification_grants_authority",
        },
        "projection",
    )
    if data["schema_version"] != "stegcore.sdk_usage_notification.v1.1":
        raise ValueError("unsupported SDK usage notification schema")
    if data["payload_disclosed"] is not False:
        raise ValueError("notification projection must assert payload_disclosed=false")
    if data["notification_grants_authority"] is not False:
        raise ValueError("notification projection must assert notification_grants_authority=false")

    event = data["event"]
    usage = data["usage"]
    if not isinstance(event, dict) or not isinstance(usage, dict):
        raise ValueError("event and usage must be objects")
    _exact_keys(event, EVENT_KEYS, "event")
    _exact_keys(usage, USAGE_KEYS, "usage")

    code = _text(event["choice_code"], "event.choice_code")
    if code not in CHOICES:
        raise ValueError("event.choice_code is not canonical")
    if event["choice_label"] != LABELS[code]:
        raise ValueError("event.choice_label does not match canonical SDK semantics")
    if event["phase"] not in {"STARTED", "COMPLETED", "FAILED", "CANCELLED"}:
        raise ValueError("event.phase is unsupported")
    kind = event["activity_kind"]
    if kind not in {"MENU_SELECTION", "GOVERNED_OPERATION"}:
        raise ValueError("event.activity_kind is unsupported")
    for field in ("event_id", "invocation_id", "occurred_at", "canonical_runtime_identity", "source"):
        _text(event[field], f"event.{field}")
    for field in ("manifest_receipt_id", "transaction_id", "receipt_chain_head"):
        _text(event[field], f"event.{field}", optional=True)
    reexecuted = event["consequence_reexecuted"]
    if reexecuted is not None and not isinstance(reexecuted, bool):
        raise ValueError("event.consequence_reexecuted must be boolean or null")
    if kind == "GOVERNED_OPERATION" and code in {"1", "2"} and not event["manifest_receipt_id"]:
        raise ValueError("governed replay/reconstruct event requires manifest_receipt_id")
    if code == "2" and reexecuted is True:
        raise ValueError("reconstruct event cannot claim consequence re-execution")

    if usage["artifact_type"] != "stegverse.sdk_usage_summary" or usage["schema_version"] != "1.1":
        raise ValueError("usage summary schema mismatch")
    if usage["payload_disclosed"] is not False or usage["observation_grants_authority"] is not False:
        raise ValueError("usage summary cannot disclose payload or grant authority")
    coverage = usage["historical_coverage"]
    if coverage not in {"OBSERVED_ONLY", "PROVENANCE_BACKFILLED_TO_INCEPTION"}:
        raise ValueError("unsupported historical coverage")
    if coverage == "OBSERVED_ONLY" and not usage["observed_since"]:
        raise ValueError("OBSERVED_ONLY requires observed_since")
    for field in (
        "lifetime_all_menu_invocations",
        "trailing_30_day_all_menu_invocations",
        "lifetime_core_governed_invocations",
        "trailing_30_day_core_governed_invocations",
    ):
        _count(usage[field], f"usage.{field}")

    rows = usage["choices"]
    if not isinstance(rows, list) or len(rows) != 5:
        raise ValueError("usage.choices must contain exactly five rows")
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("usage choice must be an object")
        _exact_keys(row, CHOICE_KEYS, "usage choice")
        row_code = row["choice_code"]
        if row_code not in CHOICES or row_code in seen:
            raise ValueError("usage choices must contain each canonical choice exactly once")
        seen.add(row_code)
        if row["choice_label"] != LABELS[row_code]:
            raise ValueError("usage choice label does not match canonical SDK semantics")
        for field in (
            "lifetime_invocations",
            "trailing_30_day_invocations",
            "unique_runtime_identities",
            "completed",
            "failed",
            "cancelled",
            "in_progress",
            "menu_selections",
            "governed_operations",
        ):
            _count(row[field], f"usage.{row_code}.{field}")
        if row["menu_selections"] + row["governed_operations"] != row["lifetime_invocations"]:
            raise ValueError("usage activity-kind counts must reconcile to lifetime count")
        percent = row["percent_of_total"]
        if isinstance(percent, bool) or not isinstance(percent, (int, float)) or not 0 <= percent <= 100:
            raise ValueError("usage percent_of_total must be within 0..100")
        _text(row["last_used_at"], f"usage.{row_code}.last_used_at", optional=True)
    return data


def _display(value: Any) -> str:
    if value is None:
        return "—"
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_markdown(data: dict[str, Any]) -> str:
    validate_projection(data)
    event = data["event"]
    usage = data["usage"]
    code = event["choice_code"]
    coverage = (
        "**Historical coverage:** provenance-backed to SDK telemetry inception"
        if usage["historical_coverage"] == "PROVENANCE_BACKFILLED_TO_INCEPTION"
        else f"**Observed since:** `{usage['observed_since']}`"
    )
    lines = [
        f"## SDK activity — `{code}` {LABELS[code]}",
        "",
        f"- **Activity:** `{event['activity_kind']}`",
        f"- **Phase:** `{event['phase']}`",
        f"- **Occurred:** `{event['occurred_at']}`",
        f"- **Runtime:** `{event['canonical_runtime_identity']}`",
        f"- **Source:** `{event['source']}`",
    ]
    if event["manifest_receipt_id"]:
        lines.append(f"- **Manifest receipt:** `{event['manifest_receipt_id']}`")
    if event["transaction_id"]:
        lines.append(f"- **Transaction:** `{event['transaction_id']}`")
    if event["receipt_chain_head"]:
        lines.append(f"- **Receipt-chain head:** `{event['receipt_chain_head']}`")
    if event["consequence_reexecuted"] is not None:
        lines.append(f"- **Consequence re-executed:** `{str(event['consequence_reexecuted']).lower()}`")

    lines.extend([
        "",
        coverage,
        "",
        "| Choice | Meaning | Lifetime | Last 30d | Menu | Governed ops | Share | Last used | Runtimes |",
        "|---|---|---:|---:|---:|---:|---:|---|---:|",
    ])
    by_code = {row["choice_code"]: row for row in usage["choices"]}
    for row_code in CHOICES:
        row = by_code[row_code]
        lines.append(
            "| `{}` | {} | {} | {} | {} | {} | {:.2f}% | {} | {} |".format(
                row_code,
                LABELS[row_code],
                row["lifetime_invocations"],
                row["trailing_30_day_invocations"],
                row["menu_selections"],
                row["governed_operations"],
                float(row["percent_of_total"]),
                _display(row["last_used_at"]),
                row["unique_runtime_identities"],
            )
        )
    lines.extend([
        "",
        f"**Core choices (`0+1+2`):** {usage['lifetime_core_governed_invocations']} lifetime observed / {usage['trailing_30_day_core_governed_invocations']} last 30d",
        f"**All SDK choice activity:** {usage['lifetime_all_menu_invocations']} lifetime observed / {usage['trailing_30_day_all_menu_invocations']} last 30d",
        "",
        "_Observation only. Menu selection is not proof a governed operation occurred. GitHub is not canonical custody and this notification grants no authority._",
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    try:
        value = json.load(sys.stdin)
        if not isinstance(value, dict):
            raise ValueError("projection must be a JSON object")
        sys.stdout.write(render_markdown(value))
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"invalid SDK usage notification: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
