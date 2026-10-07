from __future__ import annotations

"""Manifested transaction continuity for SDK and ecosystem test/runtime paths.

The manifest declares provenance and routing intent; it never grants execution
or policy authority. Every consequential decision still traverses the canonical
StegGate evaluator and commit-coherence boundary.

This module adds the continuity envelope around that existing authority path:

    SDK/input -> manifest -> ingestion -> canonical StegGate -> observation
    -> return ingestion -> discover/reconstruct/replay descriptor

Receipts are hash chained so the complete trajectory can be independently
verified without rewriting historical states.
"""

from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Optional
import uuid

from pydantic import BaseModel, Field

from .steggate import AdmissibilityRequest, canonical_sha256
from .steggate_runtime import StegGateExecutionObservation, governed_steggate_execute


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _jsonable(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json", exclude_none=False)
    if is_dataclass(value):
        return {key: _jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


class TransactionManifest(BaseModel):
    """SDK-admitted identity and declared itinerary for one transaction."""

    artifact_type: str = "stegcore.transaction_manifest"
    schema_version: str = "1.0"
    transaction_id: str
    created_at: str
    source: str
    subject: str
    processing_capability: str
    route_id: str
    input_hash: str
    candidate_hash: str
    request_hash: str
    manifest_grants_authority: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
    manifest_hash: str


class TransitionReceipt(BaseModel):
    """One immutable state transition in a transaction trajectory."""

    artifact_type: str = "stegcore.transaction_transition_receipt"
    schema_version: str = "1.0"
    transaction_id: str
    sequence: int
    observed_at: str
    stage: str
    state: str
    processor: str
    previous_receipt_hash: Optional[str] = None
    input_state_hash: Optional[str] = None
    output_state_hash: Optional[str] = None
    decision_ref: Optional[str] = None
    route_from: Optional[str] = None
    route_to: Optional[str] = None
    details: dict[str, Any] = Field(default_factory=dict)
    receipt_hash: str


class ReplayDescriptor(BaseModel):
    artifact_type: str = "stegcore.transaction_replay_descriptor"
    schema_version: str = "1.0"
    transaction_id: str
    manifest_hash: str
    request_hash: str
    canonical_runtime_identity: str
    receipt_chain_head: str
    receipt_count: int
    expected_disposition: str
    expected_executor_invoked: bool


class ManifestedTransactionResult(BaseModel):
    artifact_type: str = "stegcore.manifested_transaction_result"
    schema_version: str = "1.0"
    transaction_id: str
    manifest: TransactionManifest
    receipts: list[TransitionReceipt]
    execution_observation: dict[str, Any]
    replay: ReplayDescriptor
    chain_verified: bool


class TransactionLedger:
    """Append-only transaction receipt index with optional JSONL persistence."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path is not None else None
        self._receipts: dict[str, list[TransitionReceipt]] = {}
        if self.path is not None and self.path.exists():
            self._load()

    def _load(self) -> None:
        assert self.path is not None
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            receipt = TransitionReceipt.model_validate_json(line)
            self._receipts.setdefault(receipt.transaction_id, []).append(receipt)

    def append(self, receipt: TransitionReceipt) -> None:
        chain = self._receipts.setdefault(receipt.transaction_id, [])
        if chain:
            expected_previous = chain[-1].receipt_hash
            if receipt.previous_receipt_hash != expected_previous:
                raise ValueError("transaction receipt chain discontinuity")
        elif receipt.previous_receipt_hash is not None:
            raise ValueError("first receipt cannot reference an unknown predecessor")
        chain.append(receipt)
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(receipt.model_dump_json() + "\n")

    def discover(self, transaction_id: str) -> list[TransitionReceipt]:
        """Return the discoverable ordered trajectory for a transaction."""
        return list(self._receipts.get(transaction_id, ()))

    def verify_chain(self, transaction_id: str) -> bool:
        chain = self.discover(transaction_id)
        previous: Optional[str] = None
        for expected_sequence, receipt in enumerate(chain):
            if receipt.sequence != expected_sequence:
                return False
            if receipt.previous_receipt_hash != previous:
                return False
            body = receipt.model_dump(mode="json", exclude={"receipt_hash"})
            if canonical_sha256(body) != receipt.receipt_hash:
                return False
            previous = receipt.receipt_hash
        return bool(chain)

    def reconstruct(self, transaction_id: str) -> dict[str, Any]:
        chain = self.discover(transaction_id)
        return {
            "transaction_id": transaction_id,
            "chain_verified": self.verify_chain(transaction_id),
            "states": [
                {
                    "sequence": item.sequence,
                    "stage": item.stage,
                    "state": item.state,
                    "processor": item.processor,
                    "input_state_hash": item.input_state_hash,
                    "output_state_hash": item.output_state_hash,
                    "decision_ref": item.decision_ref,
                    "receipt_hash": item.receipt_hash,
                }
                for item in chain
            ],
        }


def manifest_transaction(
    request: AdmissibilityRequest,
    input_data: Any,
    *,
    source: str,
    subject: str,
    processing_capability: str,
    route_id: str,
    metadata: Optional[Mapping[str, Any]] = None,
    transaction_id: Optional[str] = None,
) -> TransactionManifest:
    """Validate SDK intake and create a non-authoritative routing manifest."""

    if not isinstance(processing_capability, str) or not processing_capability.strip():
        raise ValueError("manifest processing_capability required")
    if not isinstance(route_id, str) or not route_id.strip():
        raise ValueError("manifest route_id required")

    request_body = request.model_dump(mode="json", exclude_none=False)
    candidate_body = request.candidate.model_dump(mode="json", exclude_none=True)
    body = {
        "artifact_type": "stegcore.transaction_manifest",
        "schema_version": "1.0",
        "transaction_id": transaction_id or f"TX-{uuid.uuid4().hex.upper()}",
        "created_at": _now(),
        "source": source,
        "subject": subject,
        "processing_capability": processing_capability,
        "route_id": route_id,
        "input_hash": canonical_sha256(_jsonable(input_data)),
        "candidate_hash": canonical_sha256(candidate_body),
        "request_hash": canonical_sha256(request_body),
        "manifest_grants_authority": False,
        "metadata": dict(metadata or {}),
    }
    return TransactionManifest(**body, manifest_hash=canonical_sha256(body))


def _make_receipt(
    *,
    transaction_id: str,
    sequence: int,
    stage: str,
    state: str,
    processor: str,
    previous_receipt_hash: Optional[str],
    input_state_hash: Optional[str] = None,
    output_state_hash: Optional[str] = None,
    decision_ref: Optional[str] = None,
    route_from: Optional[str] = None,
    route_to: Optional[str] = None,
    details: Optional[Mapping[str, Any]] = None,
) -> TransitionReceipt:
    body = {
        "artifact_type": "stegcore.transaction_transition_receipt",
        "schema_version": "1.0",
        "transaction_id": transaction_id,
        "sequence": sequence,
        "observed_at": _now(),
        "stage": stage,
        "state": state,
        "processor": processor,
        "previous_receipt_hash": previous_receipt_hash,
        "input_state_hash": input_state_hash,
        "output_state_hash": output_state_hash,
        "decision_ref": decision_ref,
        "route_from": route_from,
        "route_to": route_to,
        "details": dict(details or {}),
    }
    return TransitionReceipt(**body, receipt_hash=canonical_sha256(body))


def run_manifested_transaction(
    request: AdmissibilityRequest,
    executor: Callable[[], Any],
    *,
    input_data: Any,
    source: str,
    subject: str,
    ledger: Optional[TransactionLedger] = None,
    processing_capability: str,
    route_id: str,
    metadata: Optional[Mapping[str, Any]] = None,
    transaction_id: Optional[str] = None,
    declared_execution_context: Optional[Mapping[str, Any]] = None,
    capability_surface: Optional[Mapping[str, Any]] = None,
    authority_resolution: Optional[Mapping[str, Any]] = None,
    pre_execution_observer: Optional[Callable[[Mapping[str, Any]], Any]] = None,
) -> ManifestedTransactionResult:
    """Run one ordinary manifested transaction through canonical StegGate.

    ``transaction_id`` may be supplied by an already-established ecosystem route
    manifest so ingestion/CGE, StegCore, return ingestion, and downstream custody
    preserve one transaction identity. Supplying the identifier grants no authority.
    """

    ledger = ledger or TransactionLedger()
    manifest = manifest_transaction(
        request,
        input_data,
        source=source,
        subject=subject,
        processing_capability=processing_capability,
        route_id=route_id,
        metadata=metadata,
        transaction_id=transaction_id,
    )

    admitted = _make_receipt(
        transaction_id=manifest.transaction_id,
        sequence=0,
        stage="ingestion",
        state="MANIFEST_ADMITTED",
        processor="stegcore.transaction_lifecycle",
        previous_receipt_hash=None,
        input_state_hash=manifest.input_hash,
        output_state_hash=manifest.manifest_hash,
        route_from="intr",
        route_to=manifest.route_id,
        details={"manifest_hash": manifest.manifest_hash, "request_hash": manifest.request_hash, "processing_capability": manifest.processing_capability, "route_id": manifest.route_id},
    )
    ledger.append(admitted)

    observation: StegGateExecutionObservation[Any] = governed_steggate_execute(
        request,
        executor,
        declared_execution_context=declared_execution_context,
        capability_surface=capability_surface,
        authority_resolution=authority_resolution,
        pre_execution_observer=pre_execution_observer,
    )
    evaluation = observation.evaluation

    governed = _make_receipt(
        transaction_id=manifest.transaction_id,
        sequence=1,
        stage="steggate",
        state=evaluation.disposition,
        processor="stegcore.steggate_runtime.governed_steggate_execute",
        previous_receipt_hash=admitted.receipt_hash,
        input_state_hash=observation.pre_state_hash,
        output_state_hash=observation.post_state_hash,
        decision_ref=evaluation.decision_state_hash,
        route_from=manifest.route_id,
        route_to="return_ingestion",
        details={
            "candidate_hash": evaluation.candidate_hash,
            "canonical_three_layer_receipt_hash": evaluation.canonical_three_layer_receipt_hash,
            "executor_invoked": observation.executor_invoked,
            "execution_status": observation.status,
        },
    )
    ledger.append(governed)

    returned = _make_receipt(
        transaction_id=manifest.transaction_id,
        sequence=2,
        stage="return_ingestion",
        state="RESULT_INGESTED",
        processor="stegcore.transaction_lifecycle",
        previous_receipt_hash=governed.receipt_hash,
        input_state_hash=observation.post_state_hash,
        output_state_hash=canonical_sha256(_jsonable(observation)),
        decision_ref=evaluation.decision_state_hash,
        route_from="steggate",
        route_to="sdk_output",
        details={"execution_status": observation.status},
    )
    ledger.append(returned)

    receipts = ledger.discover(manifest.transaction_id)
    replay = ReplayDescriptor(
        transaction_id=manifest.transaction_id,
        manifest_hash=manifest.manifest_hash,
        request_hash=manifest.request_hash,
        canonical_runtime_identity=f"{manifest.processing_capability}@{manifest.route_id}",
        receipt_chain_head=receipts[-1].receipt_hash,
        receipt_count=len(receipts),
        expected_disposition=evaluation.disposition,
        expected_executor_invoked=observation.executor_invoked,
    )

    return ManifestedTransactionResult(
        transaction_id=manifest.transaction_id,
        manifest=manifest,
        receipts=receipts,
        execution_observation=_jsonable(observation),
        replay=replay,
        chain_verified=ledger.verify_chain(manifest.transaction_id),
    )
