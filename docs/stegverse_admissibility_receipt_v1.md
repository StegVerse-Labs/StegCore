# StegVerse Admissibility Receipt — v1

Canonical, ecosystem-wide receipt. One envelope that the existing emitters
(TVC, StegCore, StegCGE, StegDB) map into, plus the fields required to survive
independent, legal, and adversarial scrutiny. This is the artifact every
AdmittedCode product ships per release.

## Design rules

1. A receipt claims **only what was evaluated**. The `scope` block is mandatory
   and states both what is asserted and what is NOT. A receipt without an honest
   scope is invalid.
1. A receipt is **independently re-verifiable**: it carries the recompute anchor
   (`verification.replay_hash` / `merkle_root`) and the exact
   `canonicalization` method, so any implementation in any language can confirm
   it. This is what makes it device/OS/language-agnostic.
1. **Authority and enforcement are distinct and bound**: the enforcement block
   carries the `decision_fingerprint` it acted on, so the two halves cannot be
   spliced.
1. The evaluating **engines are pinned** with name, version, and hash, so the
   evaluation itself is reproducible against the same logic later.
1. Platform-bound or hybrid receipts must identify their platform dependencies.
   A receipt may be valid for execution without being fully portable.

## Required envelope

```json
{
  "schema": "stegverse.admissibility_receipt.v1",
  "receipt_id": "sha256:<hash of all fields below except receipt_id>",
  "timestamp_utc": "2026-06-11T00:00:00Z",

  "entity": "AdmittedCode",
  "repo": "admittedcode/repo-guard",
  "release": "v1.0.0",
  "stage": "publish",
  "actor": "ci/release",
  "declared_action": "publish_product_release",

  "input": { "path": ".", "sha256": "sha256:..." },
  "manifest": { "path": "repo-guard.json", "sha256": "sha256:..." },

  "transition": {
    "transition_class": "B?-...",
    "transition_cell": "...",
    "authority_class": "...",
    "state_effect": "...",
    "binding_level": "..."
  },

  "authority_evidence": {
    "tvc_policy_hash": "sha256:...",
    "tv_receipt_refs": [],
    "formalism_refs": []
  },

  "decision": {
    "engine": "StegCore",
    "engine_version": "x.y.z",
    "engine_hash": "sha256:...",
    "decision": "ALLOW",
    "reason_code": "OK",
    "basis": "validated against declared policy; no forbidden patterns; structure conforms",
    "fingerprint": "sha256:<hash over the decision inputs+verdict>"
  },

  "enforcement": {
    "manager": "StegCGE",
    "manager_version": "x.y.z",
    "manager_hash": "sha256:...",
    "route": "ALLOW",
    "enacted_decision_fingerprint": "sha256:<MUST equal decision.fingerprint>",
    "portability_class": "hybrid",
    "platform_dependencies": [],
    "fail_closed_reason": ""
  },

  "verification": {
    "state_hash": "sha256:<CGE hash_state>",
    "replay_hash": "sha256:<final_state_hash from CGE replay_chain>",
    "merkle_root": "sha256:<optional when CGE exposes a Merkle root>",
    "reverification_possible": true,
    "reverify_command": "python -m stegcge.replay --receipt <this_file> --repo <path>"
  },

  "canonicalization": {
    "method": "stegverse.jcs.v1",
    "hash": "sha256",
    "notes": "UTF-8; keys byte-sorted; integers only in hashed numerics; LF; no insignificant whitespace"
  },

  "scope": {
    "asserts": [
      "The product conforms to its declared manifest under GCAT/BCAT evaluation at this release.",
      "The decision is reproducible from committed policy + this receipt."
    ],
    "does_not_assert": [
      "Security, vulnerability-freedom, or penetration resistance.",
      "Regulatory/legal compliance (e.g. PCI, HIPAA, GDPR).",
      "Fitness for any particular purpose.",
      "Correctness of the product's runtime behavior beyond declared policy."
    ]
  },

  "outputs": [],
  "previous_receipt_hash": "sha256:..."
}
```

## Required validation checks

A v1 verifier must fail closed unless all of the following hold:

1. `receipt_id` equals the SHA-256 hash of the canonicalized receipt with
   `receipt_id` removed.
1. `enforcement.enacted_decision_fingerprint` equals `decision.fingerprint`.
1. `scope.asserts` and `scope.does_not_assert` are both present and non-empty.
1. `canonicalization.method` and `canonicalization.hash` are present.
1. `decision.engine`, `decision.engine_version`, and `decision.engine_hash` are present.
1. `enforcement.manager`, `enforcement.manager_version`, and
   `enforcement.manager_hash` are present.
1. `verification.replay_hash` is present when `verification.reverification_possible` is true.
1. `enforcement.portability_class` is one of `portable`, `platform_bound`, or `hybrid`.
1. `platform_dependencies` is non-empty when `portability_class` is `platform_bound` or `hybrid`, unless the manager supplies a reason for no platform dependency.

## Field-mapping from existing emitters

| v1 field | TVC secret-read | StegCore | StegCGE | StegDB cleanup |
|---|---|---|---|---|
| `decision.decision` | `admissible` (bool → `ALLOW`/`DENY`) | `decision` | `route` | n/a (action) |
| `decision.reason_code` | `reasons[0]` | `reason_code` | — | `detection` |
| `decision.fingerprint` | `decision_id` | derive | — | — |
| `authority_evidence.tvc_policy_hash` | `policy_hash` | — | — | — |
| `verification.replay_hash` | — | — | `final_state_hash` | — |
| `verification.merkle_root` | — | — | `build_merkle_tree` root | — |
| `previous_receipt_hash` | — | — | `parent_hash` | chainlog |
| `timestamp_utc` | `ts` | — | — | `ts` |
| `scope` | new | new | new | new |
| `canonicalization` | new | new | new | new |

Two fields (`scope`, `canonicalization`) are new to all emitters. They are the
additions that make the receipt survive legal and cross-implementation scrutiny.

## The five gaps this closes

1. `verification.{merkle_root,replay_hash,reverify_command}` gives independent
   scrutiny something concrete to recompute.
1. `canonicalization` pins the bytes-to-hash method so any language can reproduce it.
1. `scope` states what the receipt does and does not prove.
1. `decision.engine_version/hash` and `enforcement.manager_version/hash` pin the
   evaluating logic so the evaluation is reproducible.
1. `enforcement.enacted_decision_fingerprint` binds enforcement to the specific
   decision it enacted.
