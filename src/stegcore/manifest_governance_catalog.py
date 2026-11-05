"""MANIFEST-GOVERNANCE-001 constraint-type catalog, as executable code.

Implements the ten constraint types of the manifest governance catalog
(PROPOSAL 01) with the semantics settled by SANDBOX EVALUATION 01,
including its four carried questions:

- Q1: per-item dispositions under one governed read; a single item's
  FAIL_CLOSED grades the whole only when the manifest binds the items
  jointly, or the failed predicate is packet-level.
- Q2: a REPORTED cited element caps the run's verification language at
  VERIFIED-BOUNDED, is named in the result, and states what evidence
  would raise it. A REPORTED element never silently passes or fails.
- Q3: allowlist entries come in three tiers (folder, file, digest),
  manifest-declared, mixed allowed; mid-run amendment is a new
  manifest (not modeled here: an amended allowlist is a new input).
- Q4: participation metering enforces FAIL_CLOSED at claim when the
  seat's count reaches the filed limit (PARTICIPATION_LIMIT_REACHED);
  reset semantics are UNBOUND (cumulative) as filed.

Every non-ALLOW disposition carries the six-field grammar:
failure_code, failed_predicate, required_evidence_or_repair,
retry_entrypoint, owning_existing_goal, next_attempt.

This module is the FINAL REVIEW candidate for the catalog. Under the
owner's M2 determination (2026-11-05), the tagged release of this
code is the catalog's FREEZE: rules established in code, frozen by
version. The module is stdlib-only and holds no authority of its own;
it computes dispositions over supplied evidence and nothing else.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Sequence

CATALOG_ID = "MANIFEST-GOVERNANCE-001"
CATALOG_VERSION = "0.1.0"  # pre-freeze candidate; the freeze tag sets 1.0.0
OWNING_GOAL = "StegVerse product revenue launch (goal_f74ab505b022)"

ALLOW = "ALLOW"
DENY = "DENY"
FAIL_CLOSED = "FAIL_CLOSED"

VERIFIED = "VERIFIED"
VERIFIED_BOUNDED = "VERIFIED-BOUNDED"

PIPELINE_STAGES = [
    "PROPOSAL",
    "SANDBOX EVALUATION",
    "FINAL REVIEW",
    "FREEZE",
    "EXECUTE",
]


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class Disposition:
    """One governed read. Non-ALLOW carries the six-field grammar."""

    constraint_type: str
    outcome: str  # ALLOW | DENY | FAIL_CLOSED
    scope: str = "packet"  # "packet" or "item:<id>"
    failure_code: Optional[str] = None
    failed_predicate: Optional[str] = None
    required_evidence_or_repair: Optional[str] = None
    retry_entrypoint: Optional[str] = None
    owning_existing_goal: str = OWNING_GOAL
    next_attempt: Optional[str] = None
    notes: list = field(default_factory=list)

    @property
    def is_allow(self) -> bool:
        return self.outcome == ALLOW

    def grammar_complete(self) -> bool:
        if self.is_allow:
            return True
        return all(
            [
                self.failure_code,
                self.failed_predicate,
                self.required_evidence_or_repair,
                self.retry_entrypoint,
                self.owning_existing_goal,
                self.next_attempt,
            ]
        )


def _breach(
    constraint_type: str,
    outcome: str,
    scope: str,
    failure_code: str,
    failed_predicate: str,
    repair: str,
    retry: str,
    next_attempt: str,
    notes: Optional[list] = None,
) -> Disposition:
    return Disposition(
        constraint_type=constraint_type,
        outcome=outcome,
        scope=scope,
        failure_code=failure_code,
        failed_predicate=failed_predicate,
        required_evidence_or_repair=repair,
        retry_entrypoint=retry,
        next_attempt=next_attempt,
        notes=notes or [],
    )


def _allow(constraint_type: str, scope: str = "packet", notes: Optional[list] = None) -> Disposition:
    return Disposition(constraint_type=constraint_type, outcome=ALLOW, scope=scope, notes=notes or [])


# ---------------------------------------------------------------- Type 1
def eval_packet_digest_binding(items: Sequence[Mapping[str, Any]]) -> list[Disposition]:
    """Each item: {id, locator, size, sha256, bytes}. Receiver recompute.

    Breach (digest or size mismatch) = FAIL_CLOSED / BYTE_IDENTITY_MISMATCH
    for that item. Packet-level scope: the manifest's own digest binding
    is the ingress predicate (Q1(b)).
    """
    out = []
    for it in items:
        data = it["bytes"]
        ok = len(data) == it["size"] and sha256_hex(data) == it["sha256"]
        if ok:
            out.append(_allow("PACKET_DIGEST_BINDING", scope=f"item:{it['id']}"))
        else:
            out.append(
                _breach(
                    "PACKET_DIGEST_BINDING",
                    FAIL_CLOSED,
                    "packet",
                    "BYTE_IDENTITY_MISMATCH",
                    f"recomputed digest/size of item {it['id']} at {it['locator']} "
                    "equals the manifest's declared sha256 and size",
                    "the file itself, byte-identical, from its storage of record "
                    "(the raw hash is the criterion; rendition-producing hops are the hazard)",
                    "resubmission of the item under the same manifest",
                    "on the conforming bytes arriving",
                )
            )
    return out


# ---------------------------------------------------------------- Type 2
@dataclass
class CitedEvidenceResult:
    dispositions: list
    reported: list  # element ids graded REPORTED (unreachable, named)
    verification_language: str  # VERIFIED or VERIFIED_BOUNDED (Q2 cap)


def eval_cited_evidence(citations: Sequence[Mapping[str, Any]]) -> CitedEvidenceResult:
    """Each citation: {id, sha256, bytes|None}.

    bytes None = unreachable from the receiver's surface: graded
    REPORTED and named, never silently passed or failed; the run's
    verification language caps at VERIFIED-BOUNDED (Q2).
    A recomputed mismatch = DENY of that claim.
    """
    dispositions, reported = [], []
    for c in citations:
        if c.get("bytes") is None:
            reported.append(c["id"])
            dispositions.append(
                _allow(
                    "CITED_EVIDENCE_BYTE_IDENTITY",
                    scope=f"item:{c['id']}",
                    notes=[
                        "REPORTED: element unreachable from the receiver's surface; "
                        "graded, named, not recomputed. Raised to recomputed by a "
                        "reachable locator or the element's bytes."
                    ],
                )
            )
        elif sha256_hex(c["bytes"]) == c["sha256"]:
            dispositions.append(_allow("CITED_EVIDENCE_BYTE_IDENTITY", scope=f"item:{c['id']}"))
        else:
            dispositions.append(
                _breach(
                    "CITED_EVIDENCE_BYTE_IDENTITY",
                    DENY,
                    f"item:{c['id']}",
                    "CITED_EVIDENCE_DIGEST_MISMATCH",
                    f"cited element {c['id']} recomputes to its cited digest",
                    "the element's bytes as cited, or a corrected citation",
                    "resubmission with the conforming citation",
                    "on the corrected citation",
                )
            )
    language = VERIFIED_BOUNDED if reported else VERIFIED
    return CitedEvidenceResult(dispositions, reported, language)


# ---------------------------------------------------------------- Type 3
def eval_resource_allowlist(
    allowlist: Sequence[Mapping[str, Any]], reads: Sequence[Mapping[str, Any]]
) -> list[Disposition]:
    """Allowlist entries: {tier: folder|file|digest, id}.

    A folder entry admits reads of files under that folder id; a file
    entry admits exactly that file id; a digest entry admits exactly
    the bytes that recompute to it. Tiers may mix (Q3). A read is
    {id, folder_id|None, sha256|None}. A read outside the allowlist =
    DENY / RESOURCE_OUTSIDE_ALLOWLIST.
    """
    folder_ids = {e["id"] for e in allowlist if e["tier"] == "folder"}
    file_ids = {e["id"] for e in allowlist if e["tier"] == "file"}
    digests = {e["id"] for e in allowlist if e["tier"] == "digest"}
    out = []
    for r in reads:
        admitted = (
            r["id"] in file_ids
            or (r.get("folder_id") is not None and r["folder_id"] in folder_ids)
            or (r.get("sha256") is not None and r["sha256"] in digests)
        )
        if admitted:
            out.append(_allow("RESOURCE_ALLOWLIST", scope=f"item:{r['id']}"))
        else:
            out.append(
                _breach(
                    "RESOURCE_ALLOWLIST",
                    DENY,
                    f"item:{r['id']}",
                    "RESOURCE_OUTSIDE_ALLOWLIST",
                    f"read of {r['id']} is inside the manifest's declared allowlist",
                    "a new manifest whose allowlist names the resource "
                    "(mid-run amendment is a new manifest, Q3)",
                    "resubmission under the amended manifest",
                    "on the amended manifest",
                )
            )
    return out


# ---------------------------------------------------------------- Type 4
def eval_projection_scope_election(
    election: Mapping[str, Any], egress_grant: Mapping[str, Any]
) -> Disposition:
    """Election: {scope: SUBMITTER_ONLY|NAMED_ONLY, named: [...],
    elected_before_run: bool}. SUBMITTER_ONLY is the default and means
    addressing/delivery scope (anyone-with-link reader plus the named
    submitter), NOT recipient-only readability. A NAMED_ONLY election
    must precede the run. Egress grant: {anyone_with_link: bool,
    named: [...]}. A return projected outside the elected scope =
    FAIL_CLOSED / PROJECTION_SCOPE_MISMATCH.
    """
    scope = election.get("scope", "SUBMITTER_ONLY")
    if scope == "NAMED_ONLY":
        if not election.get("elected_before_run", False):
            return _breach(
                "PROJECTION_SCOPE_ELECTION",
                FAIL_CLOSED,
                "packet",
                "PROJECTION_SCOPE_MISMATCH",
                "a named-only election precedes the run",
                "the election recorded before the run's ingress",
                "a new run under a timely election",
                "on the new run",
            )
        named = set(election.get("named", []))
        if egress_grant.get("anyone_with_link") or not set(egress_grant.get("named", [])) <= named:
            return _breach(
                "PROJECTION_SCOPE_ELECTION",
                FAIL_CLOSED,
                "packet",
                "PROJECTION_SCOPE_MISMATCH",
                "the return is projected only to the elected named recipients",
                "egress grant metadata confined to the elected named set",
                "re-projection of the return within the elected scope",
                "on the corrected egress",
            )
    return _allow("PROJECTION_SCOPE_ELECTION")


# ---------------------------------------------------------------- Type 5
def eval_return_path_binding(
    arrival_path: str,
    manifest: Mapping[str, Any],
    egress: Mapping[str, Any],
    returned: Mapping[str, Any],
) -> Disposition:
    """The governed return travels back along the arrival path unless
    the manifest names a different return address (a submitter
    deviation, honored as stated). The return declares, at its top,
    the same receipt recorded for the egress; the egress commits the
    run's terminal RESULT digest (canonical commitment form).
    """
    expected_path = manifest.get("return_address") or arrival_path
    if returned["path"] != expected_path:
        return _breach(
            "RETURN_PATH_BINDING",
            FAIL_CLOSED,
            "packet",
            "RETURN_PATH_MISMATCH",
            "the governed return travels the arrival path, or the "
            "manifest-named return address as stated",
            "the return filed at the bound path",
            "re-projection of the return at the bound path",
            "on the corrected return",
        )
    if returned["declared_receipt"] != egress["receipt"]:
        return _breach(
            "RETURN_PATH_BINDING",
            FAIL_CLOSED,
            "packet",
            "RETURN_DECLARATION_MISMATCH",
            "the return declares at its top the same receipt recorded "
            "for the egress (one receipt: handoff proof, declaration "
            "anchor, retrieval key)",
            "a return whose declared receipt is the egress receipt",
            "re-projection of the return with the egress receipt declared",
            "on the corrected return",
        )
    if egress["committed_result_digest"] != returned["result_digest"]:
        return _breach(
            "RETURN_PATH_BINDING",
            FAIL_CLOSED,
            "packet",
            "RETURN_COMMITMENT_MISMATCH",
            "the egress commits the run's terminal RESULT digest and "
            "the return is that result",
            "the terminal result bytes the egress committed",
            "re-projection of the committed result",
            "on the corrected return",
        )
    return _allow("RETURN_PATH_BINDING")


# ---------------------------------------------------------------- Type 6
def eval_readable_twin(files: Sequence[Mapping[str, Any]]) -> list[Disposition]:
    """Each submitter-facing file: {id, bytes, twin_bytes}. The twin
    must be byte-identical at filing; the raw hash is the criterion.
    """
    out = []
    for f in files:
        if sha256_hex(f["bytes"]) == sha256_hex(f["twin_bytes"]):
            out.append(_allow("READABLE_TWIN", scope=f"item:{f['id']}"))
        else:
            out.append(
                _breach(
                    "READABLE_TWIN",
                    FAIL_CLOSED,
                    f"item:{f['id']}",
                    "READABLE_TWIN_MISMATCH",
                    f"the .txt twin of {f['id']} is byte-identical to the filed file",
                    "a twin generated from the filed bytes themselves, "
                    "not from a rendition",
                    "re-filing of the twin from the filed bytes",
                    "on the corrected twin",
                )
            )
    return out


# ---------------------------------------------------------------- Type 7
def eval_stage_binding(intent: str, performed_stages: Sequence[str]) -> Disposition:
    """intent: GOVERNANCE_ONLY (EXECUTE single-stage) or STAGED (the
    five-stage pipeline in order). Stage states are computed from
    lineage evidence by the caller; this evaluator checks the order
    conformance of the performed sequence. Work performed out of
    stage order = FAIL_CLOSED / STAGE_ORDER_VIOLATION.
    """
    if intent == "GOVERNANCE_ONLY":
        required = ["EXECUTE"]
    else:
        required = PIPELINE_STAGES
    performed = list(performed_stages)
    if performed == required[: len(performed)] and len(performed) >= 1:
        return _allow("STAGE_BINDING")
    return _breach(
        "STAGE_BINDING",
        FAIL_CLOSED,
        "packet",
        "STAGE_ORDER_VIOLATION",
        "performed stages are a prefix of the manifest's required "
        "stage order, computed from lineage evidence",
        "the lineage's computed stage states, in order",
        "the stage the order names next",
        "on the next in-order stage",
    )


# ---------------------------------------------------------------- Type 8
@dataclass
class MeteringResult:
    disposition: Disposition
    new_count: Optional[int]  # count after claim; None when not claimed


def eval_participation_metering(
    participation_class: str, seat_count: int, limit: int
) -> MeteringResult:
    """Metering is read at claim. The native class (registered healthy
    node) is exempt. For the EXTERNAL class, count = limit at claim
    closes the submission FAIL_CLOSED / PARTICIPATION_LIMIT_REACHED
    (Q4: the submission is fully identified and its predicate is
    capacity; HOLD is reserved for arrivals whose identity cannot be
    established, and reset semantics are UNBOUND, so a held item
    would be a stuck dependency). Charging: NONE IN FORCE.
    """
    if participation_class == "native":
        return MeteringResult(_allow("PARTICIPATION_METERING"), seat_count)
    if seat_count >= limit:
        return MeteringResult(
            _breach(
                "PARTICIPATION_METERING",
                FAIL_CLOSED,
                "packet",
                "PARTICIPATION_LIMIT_REACHED",
                "the seat's counted lineages are below the filed limit at claim",
                "a filed reset binding, or a filed amendment raising the limit",
                "resubmission after either binding lands",
                "on the binding",
            ),
            None,
        )
    return MeteringResult(_allow("PARTICIPATION_METERING"), seat_count + 1)


# ---------------------------------------------------------------- Type 9
def eval_custody_refusal(manifest_terms: Mapping[str, Any]) -> Disposition:
    """A manifest that requests credential custody by the ecosystem,
    or collection of user data, fails the predicate by construction
    (zero credentials; zero collection). Breach = DENY /
    CUSTODY_OR_COLLECTION_REQUESTED.
    """
    if manifest_terms.get("requests_credential_custody") or manifest_terms.get(
        "requests_user_data_collection"
    ):
        return _breach(
            "CUSTODY_REFUSAL",
            DENY,
            "packet",
            "CUSTODY_OR_COLLECTION_REQUESTED",
            "the manifest requests neither credential custody by the "
            "ecosystem nor collection of user data",
            "a manifest whose terms keep custody with the principal "
            "(data held in a principal's own KV is held, not collected)",
            "resubmission under conforming terms",
            "on the conforming manifest",
        )
    return _allow("CUSTODY_REFUSAL")


# ---------------------------------------------------------------- Type 10
CLAIM_FIRST = "FIRST_CLAIM"
CLAIM_SECOND_VERIFIER = "SECOND_ARRIVAL_VERIFIER"


@dataclass
class ClaimResult:
    disposition: Disposition
    role: Optional[str]  # CLAIM_FIRST | CLAIM_SECOND_VERIFIER | None


def eval_claim_before_work(claim: Mapping[str, Any]) -> ClaimResult:
    """claim: {claimed_at: int|None, ingress_at: int|None,
    already_claimed: bool}. A submission is claimed in the queue
    before work; the claim is the assignment. A second arrival at
    the same work is the verifier, never a second execution
    (single-claim rule). Work without a preceding claim =
    FAIL_CLOSED / WORK_WITHOUT_CLAIM.
    """
    if claim.get("already_claimed"):
        return ClaimResult(_allow("CLAIM_BEFORE_WORK"), CLAIM_SECOND_VERIFIER)
    claimed_at, ingress_at = claim.get("claimed_at"), claim.get("ingress_at")
    if claimed_at is not None and ingress_at is not None and claimed_at <= ingress_at:
        return ClaimResult(_allow("CLAIM_BEFORE_WORK"), CLAIM_FIRST)
    return ClaimResult(
        _breach(
            "CLAIM_BEFORE_WORK",
            FAIL_CLOSED,
            "packet",
            "WORK_WITHOUT_CLAIM",
            "the queue claim entry precedes the run's ingress receipt",
            "a claim entry in the manifold queue before work begins",
            "claim in the queue, then the run",
            "on the claim",
        ),
        None,
    )


# ------------------------------------------------------------- whole read
@dataclass
class CatalogResult:
    dispositions: list
    overall: str  # ALLOW | FAIL_CLOSED | ITEMIZED (Q1)
    verification_language: str
    reported: list

    def failed_items(self) -> list:
        return [d for d in self.dispositions if not d.is_allow]


ITEMIZED = "ITEMIZED"


def overall_read(
    dispositions: Sequence[Disposition], joint_binding: bool
) -> str:
    """Q1: a FAIL_CLOSED grades the whole only when the manifest binds
    the items jointly or the failed predicate is packet-level (packet
    scope). Otherwise there is no scalar grade for the whole: the
    overall read is the itemized set (ITEMIZED), each failed item
    named with its six fields, ALLOW items standing independently.
    """
    fails = [d for d in dispositions if d.outcome == FAIL_CLOSED]
    if any(d.scope == "packet" for d in fails) or (joint_binding and fails):
        return FAIL_CLOSED
    if any(not d.is_allow for d in dispositions):
        return ITEMIZED
    return ALLOW


def evaluate_manifest(manifest: Mapping[str, Any], evidence: Mapping[str, Any]) -> CatalogResult:
    """Evaluate a manifest against supplied evidence under all ten
    types. `manifest` and `evidence` are plain mappings; see each
    evaluator for its input shape. Types whose inputs are absent are
    not evaluated (absence is the caller's statement, recorded in
    notes by the caller, never silently passed here).
    """
    dispositions: list[Disposition] = []
    reported: list[str] = []
    language = VERIFIED

    if "packet_items" in evidence:
        dispositions += eval_packet_digest_binding(evidence["packet_items"])
    if "citations" in evidence:
        cited = eval_cited_evidence(evidence["citations"])
        dispositions += cited.dispositions
        reported = cited.reported
        language = cited.verification_language
    if "allowlist" in manifest and "reads" in evidence:
        dispositions += eval_resource_allowlist(manifest["allowlist"], evidence["reads"])
    if "projection_election" in manifest and "egress_grant" in evidence:
        dispositions.append(
            eval_projection_scope_election(manifest["projection_election"], evidence["egress_grant"])
        )
    if {"arrival_path", "egress", "returned"} <= set(evidence):
        dispositions.append(
            eval_return_path_binding(
                evidence["arrival_path"], manifest, evidence["egress"], evidence["returned"]
            )
        )
    if "filed_files" in evidence:
        dispositions += eval_readable_twin(evidence["filed_files"])
    if "stage_intent" in manifest and "performed_stages" in evidence:
        dispositions.append(eval_stage_binding(manifest["stage_intent"], evidence["performed_stages"]))
    if "participation" in manifest:
        p = manifest["participation"]
        dispositions.append(
            eval_participation_metering(p["class"], p["seat_count"], p["limit"]).disposition
        )
    if "terms" in manifest:
        dispositions.append(eval_custody_refusal(manifest["terms"]))
    if "claim" in evidence:
        dispositions.append(eval_claim_before_work(evidence["claim"]).disposition)

    overall = overall_read(dispositions, bool(manifest.get("joint_binding", False)))
    return CatalogResult(dispositions, overall, language, reported)
