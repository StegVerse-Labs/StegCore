# StegCore Proof-Anchor Invariant Matrix

## Purpose

This matrix evaluates the proof-anchor invariants declared in `docs/STEGCORE_PROOF_ANCHOR_MIRROR_HANDOFF.md` against current repository evidence.

It is a bounded hardening artifact. It does not create execution, release, deployment, token, continuity-receipt, or cross-repository mutation authority.

## Classification Vocabulary

- `implemented_and_testable` — executable behavior exists and repository tests or validators exercise it.
- `implemented_partial` — executable behavior exists, but one or more hostile-assumption cases remain untested or incompletely bound.
- `documented_only` — the invariant is stated but not mechanically demonstrated.
- `absent` — no sufficient repository evidence was located.

## Invariant Evidence Matrix

| ID | Proof-anchor invariant | Classification | Current evidence | Material gap / next durable task |
| --- | --- | --- | --- | --- |
| PA-01 | Governance precedes execution. | `implemented_and_testable` | `src/stegcore/runtime.py` calls `decide(request)` before the injected executor and refuses execution unless the decision is `allow`; `src/stegcore/three_layer.py` evaluates judgment, signal admission, and execution admissibility in restrictive order. | Add a hostile-assumption test proving the executor is never invoked for every `DENY` and `FAIL-CLOSED` path produced by the three-layer evaluator. |
| PA-02 | Identity and credentials do not alone confer authority. | `implemented_partial` | `src/stegcore/decision.py` treats actor class as context and requires an already-verified receipt plus action intent; `src/stegcore/three_layer.py` separately requires current actor authority, policy, delegation, evidence, and validity window. | Add a fixture where valid identity/receipt inputs are present but delegation or policy is stale, and assert deterministic refusal. |
| PA-03 | Authority is evaluated against explicit policy, delegation, evidence, scope, validity, and recoverability constraints. | `implemented_and_testable` | `ExecutionBoundary` requires current authority, policy, delegation, evidence, affected-entity representation, recoverability profile, validity window, policy reference, delegation reference, and evidence references. | Preserve this field set as a versioned contract and add schema validation if no authoritative schema already binds it. |
| PA-04 | Missing, conflicting, stale, or ambiguous required inputs fail closed. | `implemented_and_testable` | `evaluate_three_layer()` returns `DENY` or `FAIL-CLOSED` for missing admitted signals, missing inputs, material/unknown uncertainty, unreconstructable state, missing or discontinuous reference-state hashes, stale authority/policy/delegation/evidence, closed validity window, missing affected-entity conditions, and unknown recoverability. | Add one consolidated hostile-input parameterized test covering all fail-closed branches and confirming stable reason codes. |
| PA-05 | Decisions are bound to explicit versions, epochs, state references, and canonical inputs rather than an implicitly trusted “now” or “latest.” | `implemented_partial` | Three-layer receipts bind a canonical request hash, policy reference, delegation reference, current and expected reference-state hashes, evidence references, issue time, and receipt hash. | Add explicit policy/delegation version or immutable artifact hashes where references may resolve mutably; add a caller-supplied decision epoch or validity-basis identifier so replay verification does not depend only on wall-clock `issued_at`. |
| PA-06 | A third party with repository read access and declared inputs can reproduce or independently verify the decision. | `implemented_partial` | Evaluation is deterministic over declared request fields; canonical hashing is local and dependency-light; runtime and Governance fixture workflows provide repeatable validation. | Remove remaining verifier dependence on mutable external retrieval by preserving/exporting the exact fixture inputs and rule versions in a self-contained proof packet or content-addressed manifest. |
| PA-07 | StegCore evaluates declared authority; it does not fetch authority from mutable external services. | `implemented_and_testable` | `src/stegcore/three_layer.py` requires callers to supply already-resolved policy, authority, evidence, and state-integrity facts; `src/stegcore/runtime.py` accepts injected authority resolution and does not perform authority discovery. | Add a static or unit guard test that rejects introduction of network authority lookups in the evaluator path, or document the prohibited dependency surface in an executable dependency policy. |
| PA-08 | Governance changes are at least as constrained and reviewable as the governed actions they affect. | `documented_only` | Constitutional and boundary handoffs describe review constraints, and runtime validation is automated. Current repository evidence reviewed for this matrix does not independently prove quorum, immutable scope-version binding, or a machine-enforced authority-expansion declaration for all governance-semantic changes. | Install or verify a PR gate that classifies changes to decision semantics, policy shapes, authority boundaries, failure behavior, schemas, and canonicalization as constitutional; require a machine-readable invariant diff and human review. |
| PA-09 | Downstream modules consume StegCore decisions but receive no implicit override, callback, or negotiation authority. | `implemented_partial` | Runtime invokes a caller-supplied executor only after approval and returns immutable observations; downstream dispatch records explicitly preserve destination authority boundaries and non-claims. | Add a downstream enforcement contract and test proving no callback result, executor response, health signal, or provider status can mutate the issued decision or convert refusal into execution. |
| PA-10 | Human-readable reasons remain available alongside machine-readable results. | `implemented_and_testable` | Decision and three-layer results include stable `reason_code` values and human-readable `detail` text in findings; runtime observations preserve the decision object. | Add schema/compatibility tests to prevent removal or semantic reuse of existing reason codes and finding detail fields. |

## Hostile-Assumption Coverage Status

| Hostile condition | Current posture | Required next evidence |
| --- | --- | --- |
| Founder or maintainer disappearance | `partial` | Self-contained proof packet and offline verification instructions independent of privileged operator knowledge. |
| Hosting, CI, endpoint, or infrastructure loss | `partial` | Local validator path using pinned fixtures and versions without fetching mutable external services. |
| Credential compromise without bounded authority | `partial` | Test proving valid credentials cannot substitute for stale/missing policy, delegation, validity, evidence, or recoverability. |
| Clock skew, stale state, replay, reordering, rule-version substitution | `partial` | Explicit decision epoch/version binding plus replay, reordering, clock-skew, and version-substitution fixtures. |
| Gradual governance capture | `gap` | Machine-enforced constitutional change classification, invariant diff, review gate, and sunset enforcement for emergency or convenience overrides. |
| Missing, contradictory, partial, or unavailable evidence | `covered_partial` | Existing fail-closed branches are strong; add parameterized regression coverage and proof-packet preservation. |
| Downstream pressure to negotiate or override decisions | `partial` | Downstream enforcement contract and mutation-resistance tests. |
| Hostile or divergent forks preserving the name while weakening invariants | `gap` | Signed/versioned invariant manifest, conformance claim rules, and fork identity requirements. |

## Ordered Hardening Queue

1. Add deterministic hostile-assumption tests for identity-without-authority, replay/version substitution, and downstream refusal override.
2. Bind decisions and proof packets to immutable policy/delegation versions or artifact hashes and an explicit decision epoch.
3. Produce a self-contained, content-addressed verification packet usable without GitHub, CI, network retrieval, or privileged credentials.
4. Machine-enforce constitutional change classification and invariant-diff review for governance-semantic changes.
5. Define conformance and fork-identity rules preventing weakened implementations from silently retaining StegCore compliance claims.
6. Select one outward demonstration: reproduce an `ALLOW` baseline and a deterministic `FAIL-CLOSED` mutated-state result from the same exported proof packet on a disconnected verifier.

## Bounded Outward Demonstration Candidate

### Candidate: Offline Replay Discontinuity Proof

The demonstration should package:

- one positive-control three-layer request;
- one mutated request differing only in admitted signals or reference state;
- pinned policy and delegation artifacts or their immutable hashes;
- the evaluator version or source commit;
- expected `ALLOW` and `FAIL-CLOSED` outputs;
- request and receipt hashes;
- a dependency-free verification command.

### Acceptance Criteria

1. The packet verifies without GitHub, network access, hosted endpoints, or privileged credentials.
2. Identical canonical inputs reproduce identical request hashes, decisions, reason codes, and receipt hashes, excluding any explicitly non-deterministic observation timestamp from the signed comparison surface.
3. The positive control produces `ALLOW`.
4. The mutated state produces `FAIL-CLOSED`.
5. The verifier confirms `continuity_receipt_minted: false`.
6. No execution callback is invoked for the `FAIL-CLOSED` case.
7. The result does not claim release, deployment, production readiness, third-party endorsement, or cross-repository authority.

## Current Conclusion

StegCore already implements the core three-layer fail-closed evaluation boundary. The principal proof-anchor gaps are not the basic decision order; they are immutable version/epoch binding, offline proof portability, governance-change enforcement, downstream non-override testing, and fork/conformance identity.
