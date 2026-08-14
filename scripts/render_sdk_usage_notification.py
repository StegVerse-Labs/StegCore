#!/usr/bin/env python3
from __future__ import annotations

"""Validate and render a disclosure-safe SDK usage GitHub notification.

Input is a JSON document on stdin using `stegcore.sdk_usage_notification.v1`.
The renderer is intentionally allowlist-based so repository_dispatch cannot turn
GitHub issue comments into a payload, secret, or authority-bearing side channel.
"""

import json
import sys
from typing import Any


CHOICES = ("000", "00", "0", "1", "2")
KNOWN_LABELS = {
    "0": "Submit data for governance",
    "1": "Replay a previously governed run",
    "2": "Reconstruct a previously governed run",
}
EVENT_KEYS = {
    "event_id",
    "invocation_id",
    "occurred_at",
    "choice_code",
    "choice_label",
    "phase",
    "manifest_receipt_id",
    "transaction_id",
    "canonical_runtime_identity",
    "source",
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
}


def _require_exact_keys(value: dict[str, Any], allowed: set[str], name: str) -> None:
    extras = set(value) - allowed
    if extras:
        raise ValueError(f"{name} contains unsupported fields: {sorted(extras)}")


def _nonnegative_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def _safe_text(value: Any, field: str, *, required: bool = False) -> str | None:
    if value is None:
        if required:
            raise ValueError(f"{field} is required")
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    if len(value) > 512:
        raise ValueError(f"{field} exceeds notification length limit")
    return value.strip()


def validate_projection(data: dict[str, Any]) -> dict[str, Any]:
    _require_exact_keys(
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
    if data.get("schema_version") != "stegcore.sdk_usage_notification.v1":
        raise ValueError("unsupported SDK usage notification schema")
    if data.get("payload_disclosed") is not False:
        raise ValueError("notification projection must assert payload_disclosed=false")
    if data.get("notification_grants_authority") is not False:
        raise ValueError("notification projection must assert notification_grants_authority=false")

    event = data.get("event")
    usage = data.get("usage")
    if not isinstance(event, dict) or not isinstance(usage, dict):
        raise ValueError("projection event and usage must be objects")
    _require_exact_keys(event, EVENT_KEYS, "event")
    _require_exact_keys(usage, USAGE_KEYS, "usage")

    choice = _safe_text(event.get("choice_code"), "event.choice_code", required=True)
    if choice not in CHOICES:
        raise ValueError("event.choice_code is not a canonical SDK menu choice")
    phase = _safe_text(event.get("phase"), "event.phase", required=True)
    if phase not in {"STARTED", "COMPLETED", "FAILED", "CANCELLED"}:
        raise ValueError("event.phase is unsupported")
    for required in (
        "event_id",
        "invocation_id",
        "occurred_at",
        "canonical_runtime_identity",
        "source",
    ):
        _safe_text(event.get(required), f"event.{required}", required=True)
    for optional in (
        "choice_label",
        "manifest_receipt_id",
        "transaction_id",
        "receipt_chain_head",
    ):
        _safe_text(event.get(optional), f"event.{optional}")
    consequence_reexecuted = event.get("consequence_reexecuted")
    if consequence_reexecuted is not None and not isinstance(consequence_reexecuted, bool):
        raise ValueError("event.consequence_reexecuted must be boolean or null")
    if choice in {"1", "2"} and not event.get("manifest_receipt_id"):
        raise ValueError("replay/reconstruct notification requires manifest_receipt_id")
    if choice == "2" and consequence_reexecuted is True:
        raise ValueError("reconstruct notification cannot claim consequence re-execution")

    if usage.get("payload_disclosed") is not False:
        raise ValueError("usage summary must assert payload_disclosed=false")
    if usage.get("observation_grants_authority") is not False:
        raise ValueError("usage summary must assert observation_grants_authority=false")
    coverage = usage.get("historical_coverage")
    if coverage not in {"OBSERVED_ONLY", "PROVENANCE_BACKFILLED_TO_INCEPTION"}:
        raise ValueError("usage historical_coverage is unsupported")
    if coverage == "OBSERVED_ONLY" and not usage.get("observed_since"):
        raise ValueError("observed-only usage summary requires observed_since")

    for name in (
        "lifetime_all_menu_invocations",
        "trailing_30_day_all_menu_invocations",
        "lifetime_core_governed_invocations",
        "trailing_30_day_core_governed_invocations",
    ):
        _nonnegative_int(usage.get(name), f"usage.{name}")

    rows = usage.get("choices")
    if not isinstance(rows, list) or len(rows) != 5:
        raise ValueError("usage.choices must contain exactly five rows")
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("usage choice row must be an object")
        _require_exact_keys(row, CHOICE_KEYS, "usage choice")
        row_choice = row.get("choice_code")
        if row_choice not in CHOICES or row_choice in seen:
            raise ValueError("usage choices must contain each canonical choice exactly once")
        seen.add(row_choice)
        for name in (
            "lifetime_invocations",
            "trailing_30_day_invocations",
            "unique_runtime_identities",
            "completed",
            "failed",
            "cancelled",
            "in_progress",
        ):
            _nonnegative_int(row.get(name), f"usage.{row_choice}.{name}")
        percent = row.get("percent_of_total")
        if isinstance(percent, bool) or not isinstance(percent, (int, float)) or not 0 <= percent <= 100:
            raise ValueError(f"usage.{row_choice}.percent_of_total must be within 0..100")
        _safe_text(row.get("choice_label"), f"usage.{row_choice}.choice_label")
        _safe_text(row.get("last_used_at"), f"usage.{row_choice}.last_used_at")
    if seen != set(CHOICES):
        raise ValueError("usage choices are incomplete")
    return data


def _display(value: Any) -> str:
    if value is None:
        return "—"
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_markdown(data: dict[str, Any]) -> str:
    data = validate_projection(data)
    event = data["event"]
    usage = data["usage"]
    code = event["choice_code"]
    label = KNOWN_LABELS.get(code) or event.get("choice_label") or "Unresolved menu entry"

    if usage["historical_coverage"] == "PROVENANCE_BACKFILLED_TO_INCEPTION":
        coverage = "**Historical coverage:** provenance-backed to SDK telemetry inception"
    else:
        coverage = f"**Observed since:** `{_display(usage['observed_since'])}`"

    lines = [
        f"## SDK activity — `{code}` {label}",
        "",
        f"- **Phase:** `{event['phase']}`",
        f"- **Occurred:** `{event['occurred_at']}`",
        f"- **Invocation:** `{event['invocation_id']}`",
        f"- **Runtime:** `{event['canonical_runtime_identity']}`",
        f"- **Source:** `{event['source']}`",
    ]
    if event.get("manifest_receipt_id"):
        lines.append(f"- **Manifest receipt:** `{event['manifest_receipt_id']}`")
    if event.get("transaction_id"):
        lines.append(f"- **Transaction:** `{event['transaction_id']}`")
    if event.get("receipt_chain_head"):
        lines.append(f"- **Receipt-chain head:** `{event['receipt_chain_head']}`")
    if event.get("consequence_reexecuted") is not None:
        lines.append(
            f"- **Consequence re-executed:** `{str(event['consequence_reexecuted']).lower()}`"
        )

    lines.extend(
        [
            "",
            coverage,
            "",
            "| Choice | Meaning | Lifetime observed | Last 30d | Share | Last used | Runtimes | Completed / Failed / Cancelled / Active |",
            "|---|---|---:|---:|---:|---|---:|---:|",
        ]
    )
    by_code = {row["choice_code"]: row for row in usage["choices"]}
    for row_code in CHOICES:
        row = by_code[row_code]
        row_label = KNOWN_LABELS.get(row_code) or row.get("choice_label") or "Unresolved"
        lines.append(
            "| `{}` | {} | {} | {} | {:.2f}% | {} | {} | {} / {} / {} / {} |".format(
                row_code,
                _display(row_label),
                row["lifetime_invocations"],
                row["trailing_30_day_invocations"],
                float(row["percent_of_total"]),
                _display(row.get("last_used_at")),
                row["unique_runtime_identities"],
                row["completed"],
                row["failed"],
                row["cancelled"],
                row["in_progress"],
            )
        )

    lines.extend(
        [
            "",
            f"**Core governed operations (`0+1+2`):** {usage['lifetime_core_governed_invocations']} lifetime observed / {usage['trailing_30_day_core_governed_invocations']} last 30d",
            f"**All SDK menu activity:** {usage['lifetime_all_menu_invocations']} lifetime observed / {usage['trailing_30_day_all_menu_invocations']} last 30d",
            "",
            "_Observation only. GitHub is not canonical custody and this notification grants no authority._",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    try:
        raw = json.load(sys.stdin)
        if not isinstance(raw, dict):
            raise ValueError("notification projection must be a JSON object")
        sys.stdout.write(render_markdown(raw))
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"invalid SDK usage notification: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
