from __future__ import annotations

"""Observation-only SDK operation telemetry.

This module records disclosure-safe SDK menu invocations outside Master Records so
operators can observe usage without turning telemetry into an authority surface.
It stores no SDK payload, policy body, credential, or secret and grants no policy,
execution, replay, reconstruction, or disclosure authority.
"""

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field

from .transaction_lifecycle import canonical_sha256


SDK_CHOICE_CODES: tuple[str, ...] = ("000", "00", "0", "1", "2")
CORE_GOVERNED_CHOICES: tuple[str, ...] = ("0", "1", "2")
CHOICE_LABELS: dict[str, str | None] = {
    "000": None,
    "00": None,
    "0": "submit data for governance",
    "1": "replay a previously governed run",
    "2": "reconstruct a previously governed run",
}
TERMINAL_PHASES = {"COMPLETED", "FAILED", "CANCELLED"}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat()


def _parse_iso(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


class SDKOperationEvent(BaseModel):
    artifact_type: str = "stegcore.sdk_operation_event"
    schema_version: str = "1.0"
    event_id: str
    invocation_id: str
    occurred_at: str
    choice_code: str
    choice_label: str | None = None
    phase: Literal["STARTED", "COMPLETED", "FAILED", "CANCELLED"]
    manifest_receipt_id: str | None = None
    transaction_id: str | None = None
    canonical_runtime_identity: str
    source: str
    receipt_chain_head: str | None = None
    consequence_reexecuted: bool | None = None
    payload_disclosed: bool = False
    observation_grants_authority: bool = False
    event_hash: str


class SDKChoiceUsage(BaseModel):
    choice_code: str
    choice_label: str | None = None
    lifetime_invocations: int = 0
    trailing_30_day_invocations: int = 0
    percent_of_total: float = 0.0
    last_used_at: str | None = None
    unique_runtime_identities: int = 0
    completed: int = 0
    failed: int = 0
    cancelled: int = 0
    in_progress: int = 0


class SDKUsageSummary(BaseModel):
    artifact_type: str = "stegcore.sdk_usage_summary"
    schema_version: str = "1.0"
    generated_at: str
    observed_since: str | None = None
    historical_coverage: Literal["OBSERVED_ONLY", "PROVENANCE_BACKFILLED_TO_INCEPTION"] = (
        "OBSERVED_ONLY"
    )
    lifetime_all_menu_invocations: int = 0
    trailing_30_day_all_menu_invocations: int = 0
    lifetime_core_governed_invocations: int = 0
    trailing_30_day_core_governed_invocations: int = 0
    choices: list[SDKChoiceUsage] = Field(default_factory=list)
    payload_disclosed: bool = False
    observation_grants_authority: bool = False


class SDKOperationEventLedger:
    """Append-only JSONL ledger that counts unique SDK invocations.

    A single invocation can have a STARTED event followed by one terminal event.
    Usage counts are invocation counts, not raw event-row counts, so lifecycle
    transitions cannot inflate the menu usage census.
    """

    def __init__(
        self,
        path: str | Path | None = None,
        *,
        historical_coverage: Literal[
            "OBSERVED_ONLY", "PROVENANCE_BACKFILLED_TO_INCEPTION"
        ] = "OBSERVED_ONLY",
    ) -> None:
        self.path = Path(path) if path is not None else None
        self.historical_coverage = historical_coverage
        self._events: list[SDKOperationEvent] = []
        self._by_event_id: dict[str, SDKOperationEvent] = {}
        self._by_invocation: dict[str, list[SDKOperationEvent]] = {}
        if self.path is not None and self.path.exists():
            self._load()

    @staticmethod
    def _validate_event(event: SDKOperationEvent) -> None:
        if event.choice_code not in SDK_CHOICE_CODES:
            raise ValueError(f"unsupported SDK choice code: {event.choice_code}")
        expected_label = CHOICE_LABELS[event.choice_code]
        if expected_label is not None and event.choice_label != expected_label:
            raise ValueError("known SDK choice label does not match canonical semantics")
        if event.payload_disclosed:
            raise ValueError("SDK operation telemetry cannot persist payload disclosure")
        if event.observation_grants_authority:
            raise ValueError("SDK operation telemetry cannot grant authority")
        body = event.model_dump(mode="json", exclude={"event_id", "event_hash"})
        expected_hash = canonical_sha256(body)
        if event.event_hash != expected_hash:
            raise ValueError("SDK operation event hash mismatch")
        if event.event_id != f"SDK-EVT-{expected_hash.upper()}":
            raise ValueError("SDK operation event ID mismatch")
        if event.choice_code in {"1", "2"} and not event.manifest_receipt_id:
            raise ValueError("replay/reconstruct observations require manifest_receipt_id")
        if event.choice_code == "2" and event.consequence_reexecuted is True:
            raise ValueError("reconstruction telemetry cannot claim consequence re-execution")

    def _append_loaded(self, event: SDKOperationEvent) -> None:
        self._validate_event(event)
        existing = self._by_event_id.get(event.event_id)
        if existing is not None:
            if existing.model_dump(mode="json") != event.model_dump(mode="json"):
                raise ValueError("event identity collision with different immutable content")
            return
        events = self._by_invocation.setdefault(event.invocation_id, [])
        if events:
            first = events[0]
            for field in (
                "choice_code",
                "choice_label",
                "canonical_runtime_identity",
                "source",
                "manifest_receipt_id",
                "transaction_id",
            ):
                old = getattr(first, field)
                new = getattr(event, field)
                if old is not None and new is not None and old != new:
                    raise ValueError(f"invocation identity changed across lifecycle: {field}")
            if first.phase in TERMINAL_PHASES:
                raise ValueError("cannot append an event after terminal invocation state")
            if event.phase == "STARTED":
                raise ValueError("invocation cannot contain multiple STARTED events")
        elif event.phase != "STARTED":
            raise ValueError("terminal SDK event requires a preceding STARTED event")
        self._events.append(event)
        self._by_event_id[event.event_id] = event
        events.append(event)

    def _load(self) -> None:
        assert self.path is not None
        for raw in self.path.read_text(encoding="utf-8").splitlines():
            if not raw.strip():
                continue
            self._append_loaded(SDKOperationEvent.model_validate_json(raw))

    def record(
        self,
        *,
        invocation_id: str,
        choice_code: str,
        phase: Literal["STARTED", "COMPLETED", "FAILED", "CANCELLED"],
        canonical_runtime_identity: str,
        source: str,
        occurred_at: datetime | None = None,
        choice_label: str | None = None,
        manifest_receipt_id: str | None = None,
        transaction_id: str | None = None,
        receipt_chain_head: str | None = None,
        consequence_reexecuted: bool | None = None,
    ) -> SDKOperationEvent:
        if choice_code not in SDK_CHOICE_CODES:
            raise ValueError(f"unsupported SDK choice code: {choice_code}")
        canonical_label = CHOICE_LABELS[choice_code]
        if canonical_label is not None:
            if choice_label is not None and choice_label != canonical_label:
                raise ValueError("known SDK choice label cannot be overridden")
            choice_label = canonical_label
        body = {
            "artifact_type": "stegcore.sdk_operation_event",
            "schema_version": "1.0",
            "invocation_id": invocation_id,
            "occurred_at": _iso(occurred_at or _utc_now()),
            "choice_code": choice_code,
            "choice_label": choice_label,
            "phase": phase,
            "manifest_receipt_id": manifest_receipt_id,
            "transaction_id": transaction_id,
            "canonical_runtime_identity": canonical_runtime_identity,
            "source": source,
            "receipt_chain_head": receipt_chain_head,
            "consequence_reexecuted": consequence_reexecuted,
            "payload_disclosed": False,
            "observation_grants_authority": False,
        }
        event_hash = canonical_sha256(body)
        event = SDKOperationEvent(
            **body,
            event_id=f"SDK-EVT-{event_hash.upper()}",
            event_hash=event_hash,
        )
        self._append_loaded(event)
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(event.model_dump_json() + "\n")
        return event

    def begin(
        self,
        *,
        choice_code: str,
        canonical_runtime_identity: str,
        source: str,
        occurred_at: datetime | None = None,
        choice_label: str | None = None,
        manifest_receipt_id: str | None = None,
        transaction_id: str | None = None,
        invocation_id: str | None = None,
    ) -> SDKOperationEvent:
        return self.record(
            invocation_id=invocation_id or f"SDK-INV-{uuid4()}",
            choice_code=choice_code,
            choice_label=choice_label,
            phase="STARTED",
            canonical_runtime_identity=canonical_runtime_identity,
            source=source,
            occurred_at=occurred_at,
            manifest_receipt_id=manifest_receipt_id,
            transaction_id=transaction_id,
        )

    def finish(
        self,
        invocation_id: str,
        *,
        phase: Literal["COMPLETED", "FAILED", "CANCELLED"],
        occurred_at: datetime | None = None,
        receipt_chain_head: str | None = None,
        consequence_reexecuted: bool | None = None,
    ) -> SDKOperationEvent:
        events = self._by_invocation.get(invocation_id)
        if not events:
            raise KeyError(f"unknown SDK invocation: {invocation_id}")
        first = events[0]
        return self.record(
            invocation_id=invocation_id,
            choice_code=first.choice_code,
            choice_label=first.choice_label,
            phase=phase,
            canonical_runtime_identity=first.canonical_runtime_identity,
            source=first.source,
            occurred_at=occurred_at,
            manifest_receipt_id=first.manifest_receipt_id,
            transaction_id=first.transaction_id,
            receipt_chain_head=receipt_chain_head,
            consequence_reexecuted=consequence_reexecuted,
        )

    def events(self) -> list[SDKOperationEvent]:
        return list(self._events)

    def invocation_events(self, invocation_id: str) -> list[SDKOperationEvent]:
        return list(self._by_invocation.get(invocation_id, []))

    def summary(
        self,
        *,
        now: datetime | None = None,
        trailing_days: int = 30,
    ) -> SDKUsageSummary:
        if trailing_days <= 0:
            raise ValueError("trailing_days must be positive")
        reference = now or _utc_now()
        if reference.tzinfo is None:
            reference = reference.replace(tzinfo=timezone.utc)
        reference = reference.astimezone(timezone.utc)
        cutoff = reference - timedelta(days=trailing_days)

        invocations: list[tuple[SDKOperationEvent, SDKOperationEvent]] = []
        for events in self._by_invocation.values():
            if not events:
                continue
            invocations.append((events[0], events[-1]))

        total = len(invocations)
        trailing_total = sum(1 for first, _ in invocations if _parse_iso(first.occurred_at) >= cutoff)
        observed_since = (
            min((_parse_iso(first.occurred_at) for first, _ in invocations), default=None)
        )

        usage_rows: list[SDKChoiceUsage] = []
        for code in SDK_CHOICE_CODES:
            selected = [(first, last) for first, last in invocations if first.choice_code == code]
            trailing = [
                (first, last)
                for first, last in selected
                if _parse_iso(first.occurred_at) >= cutoff
            ]
            last_used = max(
                (_parse_iso(first.occurred_at) for first, _ in selected),
                default=None,
            )
            phases = [last.phase for _, last in selected]
            usage_rows.append(
                SDKChoiceUsage(
                    choice_code=code,
                    choice_label=CHOICE_LABELS[code],
                    lifetime_invocations=len(selected),
                    trailing_30_day_invocations=len(trailing),
                    percent_of_total=(len(selected) / total * 100.0) if total else 0.0,
                    last_used_at=_iso(last_used) if last_used is not None else None,
                    unique_runtime_identities=len(
                        {first.canonical_runtime_identity for first, _ in selected}
                    ),
                    completed=phases.count("COMPLETED"),
                    failed=phases.count("FAILED"),
                    cancelled=phases.count("CANCELLED"),
                    in_progress=phases.count("STARTED"),
                )
            )

        core = [(first, last) for first, last in invocations if first.choice_code in CORE_GOVERNED_CHOICES]
        trailing_core = [
            (first, last)
            for first, last in core
            if _parse_iso(first.occurred_at) >= cutoff
        ]
        return SDKUsageSummary(
            generated_at=_iso(reference),
            observed_since=_iso(observed_since) if observed_since is not None else None,
            historical_coverage=self.historical_coverage,
            lifetime_all_menu_invocations=total,
            trailing_30_day_all_menu_invocations=trailing_total,
            lifetime_core_governed_invocations=len(core),
            trailing_30_day_core_governed_invocations=len(trailing_core),
            choices=usage_rows,
            payload_disclosed=False,
            observation_grants_authority=False,
        )

    def notification_projection(
        self,
        event: SDKOperationEvent,
        *,
        now: datetime | None = None,
    ) -> dict[str, object]:
        """Return the only fields intended for a GitHub notification projection."""
        self._validate_event(event)
        summary = self.summary(now=now)
        return {
            "schema_version": "stegcore.sdk_usage_notification.v1",
            "event": {
                "event_id": event.event_id,
                "invocation_id": event.invocation_id,
                "occurred_at": event.occurred_at,
                "choice_code": event.choice_code,
                "choice_label": event.choice_label,
                "phase": event.phase,
                "manifest_receipt_id": event.manifest_receipt_id,
                "transaction_id": event.transaction_id,
                "canonical_runtime_identity": event.canonical_runtime_identity,
                "source": event.source,
                "receipt_chain_head": event.receipt_chain_head,
                "consequence_reexecuted": event.consequence_reexecuted,
            },
            "usage": summary.model_dump(mode="json"),
            "payload_disclosed": False,
            "notification_grants_authority": False,
        }
