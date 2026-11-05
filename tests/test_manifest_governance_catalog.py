"""Conformance suite for the MANIFEST-GOVERNANCE-001 catalog code.

Each test exercises one catalog type (or one sandbox-evaluation
question) against the semantics of MANIFEST_GOVERNANCE__SANDBOX_
EVALUATION__01. The Type 3 tests are the conformance exercise the
sandbox evaluation conditioned FINAL REVIEW entry on, in the code
form the owner's M2 determination (2026-11-05) specifies: one
in-scope read admitted, one out-of-scope read refused.
"""

import hashlib

from stegcore.manifest_governance_catalog import (
    ALLOW,
    DENY,
    FAIL_CLOSED,
    ITEMIZED,
    VERIFIED,
    VERIFIED_BOUNDED,
    CLAIM_FIRST,
    CLAIM_SECOND_VERIFIER,
    eval_cited_evidence,
    eval_claim_before_work,
    eval_custody_refusal,
    eval_packet_digest_binding,
    eval_participation_metering,
    eval_projection_scope_election,
    eval_readable_twin,
    eval_resource_allowlist,
    eval_return_path_binding,
    eval_stage_binding,
    evaluate_manifest,
    sha256_hex,
)


def item(id_, data: bytes):
    return {"id": id_, "locator": f"mem://{id_}", "size": len(data),
            "sha256": hashlib.sha256(data).hexdigest(), "bytes": data}


def assert_grammar(d):
    assert not d.is_allow
    assert d.grammar_complete(), f"incomplete grammar: {d}"


# ---------------------------------------------------------------- Type 1
def test_t1_digest_match_allows():
    ds = eval_packet_digest_binding([item("a", b"alpha")])
    assert ds[0].outcome == ALLOW


def test_t1_digest_mismatch_fail_closed():
    bad = item("a", b"alpha")
    bad["bytes"] = b"alpha-rendition"
    ds = eval_packet_digest_binding([bad])
    assert ds[0].outcome == FAIL_CLOSED
    assert ds[0].failure_code == "BYTE_IDENTITY_MISMATCH"
    assert_grammar(ds[0])


# ---------------------------------------------------------------- Type 2
def test_t2_recompute_match_and_verified_language():
    r = eval_cited_evidence([{"id": "c1", "sha256": sha256_hex(b"x"), "bytes": b"x"}])
    assert r.dispositions[0].outcome == ALLOW
    assert r.verification_language == VERIFIED
    assert r.reported == []


def test_t2_mismatch_denies():
    r = eval_cited_evidence([{"id": "c1", "sha256": sha256_hex(b"x"), "bytes": b"y"}])
    assert r.dispositions[0].outcome == DENY
    assert r.dispositions[0].failure_code == "CITED_EVIDENCE_DIGEST_MISMATCH"
    assert_grammar(r.dispositions[0])


def test_t2_unreachable_is_reported_and_caps_language_q2():
    r = eval_cited_evidence([
        {"id": "c1", "sha256": sha256_hex(b"x"), "bytes": b"x"},
        {"id": "c2", "sha256": "ab" * 32, "bytes": None},
    ])
    assert r.reported == ["c2"]
    assert r.verification_language == VERIFIED_BOUNDED
    assert all(d.is_allow for d in r.dispositions)  # never silently failed


# ---------------------------------------------------------------- Type 3
ALLOWLIST = [
    {"tier": "folder", "id": "folder-inbox"},
    {"tier": "file", "id": "file-named"},
    {"tier": "digest", "id": sha256_hex(b"pinned-bytes")},
]


def test_t3_in_scope_reads_allowed_all_tiers():
    reads = [
        {"id": "f1", "folder_id": "folder-inbox", "sha256": None},
        {"id": "file-named", "folder_id": None, "sha256": None},
        {"id": "anything", "folder_id": None, "sha256": sha256_hex(b"pinned-bytes")},
    ]
    ds = eval_resource_allowlist(ALLOWLIST, reads)
    assert all(d.outcome == ALLOW for d in ds)


def test_t3_out_of_scope_read_denied():
    reads = [{"id": "secret", "folder_id": "folder-other", "sha256": sha256_hex(b"nope")}]
    ds = eval_resource_allowlist(ALLOWLIST, reads)
    assert ds[0].outcome == DENY
    assert ds[0].failure_code == "RESOURCE_OUTSIDE_ALLOWLIST"
    assert_grammar(ds[0])


# ---------------------------------------------------------------- Type 4
def test_t4_default_submitter_only_allows_anyone_with_link():
    d = eval_projection_scope_election(
        {"scope": "SUBMITTER_ONLY", "named": ["sub@example"]},
        {"anyone_with_link": True, "named": ["sub@example"]},
    )
    assert d.outcome == ALLOW


def test_t4_named_only_breached_by_link_grant():
    d = eval_projection_scope_election(
        {"scope": "NAMED_ONLY", "named": ["a@example"], "elected_before_run": True},
        {"anyone_with_link": True, "named": ["a@example"]},
    )
    assert d.outcome == FAIL_CLOSED
    assert d.failure_code == "PROJECTION_SCOPE_MISMATCH"
    assert_grammar(d)


def test_t4_named_only_must_precede_run():
    d = eval_projection_scope_election(
        {"scope": "NAMED_ONLY", "named": ["a@example"], "elected_before_run": False},
        {"anyone_with_link": False, "named": ["a@example"]},
    )
    assert d.outcome == FAIL_CLOSED


# ---------------------------------------------------------------- Type 5
EGRESS = {"receipt": "rcpt-1", "committed_result_digest": "dg-1"}


def test_t5_same_path_and_declaration_allow():
    d = eval_return_path_binding(
        "inbox/", {}, EGRESS,
        {"path": "inbox/", "declared_receipt": "rcpt-1", "result_digest": "dg-1"},
    )
    assert d.outcome == ALLOW


def test_t5_named_deviation_honored():
    d = eval_return_path_binding(
        "inbox/", {"return_address": "_AI/ClaudeCode"}, EGRESS,
        {"path": "_AI/ClaudeCode", "declared_receipt": "rcpt-1", "result_digest": "dg-1"},
    )
    assert d.outcome == ALLOW


def test_t5_wrong_path_and_declaration_mismatch():
    d = eval_return_path_binding(
        "inbox/", {}, EGRESS,
        {"path": "elsewhere/", "declared_receipt": "rcpt-1", "result_digest": "dg-1"},
    )
    assert d.outcome == FAIL_CLOSED and d.failure_code == "RETURN_PATH_MISMATCH"
    d = eval_return_path_binding(
        "inbox/", {}, EGRESS,
        {"path": "inbox/", "declared_receipt": "rcpt-OTHER", "result_digest": "dg-1"},
    )
    assert d.outcome == FAIL_CLOSED and d.failure_code == "RETURN_DECLARATION_MISMATCH"
    assert_grammar(d)


# ---------------------------------------------------------------- Type 6
def test_t6_twin_identical_allows_and_mismatch_closes():
    ok = eval_readable_twin([{"id": "r", "bytes": b"body", "twin_bytes": b"body"}])
    assert ok[0].outcome == ALLOW
    bad = eval_readable_twin([{"id": "r", "bytes": b"body", "twin_bytes": b"body "}])
    assert bad[0].outcome == FAIL_CLOSED
    assert bad[0].failure_code == "READABLE_TWIN_MISMATCH"


# ---------------------------------------------------------------- Type 7
def test_t7_governance_only_single_stage():
    assert eval_stage_binding("GOVERNANCE_ONLY", ["EXECUTE"]).outcome == ALLOW


def test_t7_staged_prefix_allows_out_of_order_closes():
    assert eval_stage_binding("STAGED", ["PROPOSAL", "SANDBOX EVALUATION"]).outcome == ALLOW
    d = eval_stage_binding("STAGED", ["PROPOSAL", "FREEZE"])
    assert d.outcome == FAIL_CLOSED
    assert d.failure_code == "STAGE_ORDER_VIOLATION"
    assert_grammar(d)


# ---------------------------------------------------------------- Type 8
def test_t8_external_under_limit_allows_and_increments():
    r = eval_participation_metering("external", 2, 10)
    assert r.disposition.outcome == ALLOW and r.new_count == 3


def test_t8_external_at_limit_fail_closed_q4():
    r = eval_participation_metering("external", 10, 10)
    assert r.disposition.outcome == FAIL_CLOSED
    assert r.disposition.failure_code == "PARTICIPATION_LIMIT_REACHED"
    assert r.new_count is None  # not claimed; count uncorrupted
    assert_grammar(r.disposition)


def test_t8_native_exempt():
    r = eval_participation_metering("native", 999, 10)
    assert r.disposition.outcome == ALLOW and r.new_count == 999


# ---------------------------------------------------------------- Type 9
def test_t9_custody_or_collection_denied():
    for terms in ({"requests_credential_custody": True},
                  {"requests_user_data_collection": True}):
        d = eval_custody_refusal(terms)
        assert d.outcome == DENY
        assert d.failure_code == "CUSTODY_OR_COLLECTION_REQUESTED"
        assert_grammar(d)
    assert eval_custody_refusal({}).outcome == ALLOW


# --------------------------------------------------------------- Type 10
def test_t10_claim_precedes_work_and_second_arrival_verifies():
    r = eval_claim_before_work({"claimed_at": 1, "ingress_at": 2, "already_claimed": False})
    assert r.disposition.outcome == ALLOW and r.role == CLAIM_FIRST
    r = eval_claim_before_work({"claimed_at": None, "ingress_at": 2, "already_claimed": True})
    assert r.disposition.outcome == ALLOW and r.role == CLAIM_SECOND_VERIFIER


def test_t10_work_without_claim_closes():
    r = eval_claim_before_work({"claimed_at": 5, "ingress_at": 2, "already_claimed": False})
    assert r.disposition.outcome == FAIL_CLOSED
    assert r.disposition.failure_code == "WORK_WITHOUT_CLAIM"
    assert_grammar(r.disposition)


# -------------------------------------------------------------------- Q1
def _manifest_with_items(joint):
    good, bad = item("good", b"g"), item("bad", b"b")
    bad["bytes"] = b"b-rendition"
    return {"joint_binding": joint}, {"packet_items": [good, bad]}


def test_q1_item_failure_itemized_without_joint_binding():
    m, ev = _manifest_with_items(False)
    r = evaluate_manifest(m, ev)
    # Type 1's packet scope grades the whole (the manifest's own
    # digest binding is packet-level, Q1(b)); use a per-item type to
    # see ITEMIZED: twin mismatch is item-scoped.
    m2 = {"joint_binding": False}
    ev2 = {"filed_files": [{"id": "ok", "bytes": b"a", "twin_bytes": b"a"},
                            {"id": "bad", "bytes": b"b", "twin_bytes": b"b "}]}
    r2 = evaluate_manifest(m2, ev2)
    assert r2.overall == ITEMIZED
    assert [d.scope for d in r2.failed_items()] == ["item:bad"]
    assert r.overall == FAIL_CLOSED  # packet-level predicate (Q1(b))


def test_q1_joint_binding_grades_whole():
    m = {"joint_binding": True}
    ev = {"filed_files": [{"id": "bad", "bytes": b"b", "twin_bytes": b"b "}]}
    r = evaluate_manifest(m, ev)
    assert r.overall == FAIL_CLOSED


def test_all_non_allow_carry_six_field_grammar():
    m = {"terms": {"requests_credential_custody": True},
         "participation": {"class": "external", "seat_count": 10, "limit": 10},
         "stage_intent": "STAGED"}
    ev = {"performed_stages": ["EXECUTE"],
          "filed_files": [{"id": "x", "bytes": b"a", "twin_bytes": b"z"}]}
    r = evaluate_manifest(m, ev)
    assert r.failed_items()
    assert all(d.grammar_complete() for d in r.failed_items())
