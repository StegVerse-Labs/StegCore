# StegCore Mirror Handoff

## Source of truth

```text
organization: StegVerse-Labs
repository: StegCore
branch: main
canonical StegGate owner: StegVerse-Labs/StegCore
portable product version: 0.2.0
canonical runtime identity: stegverse:steggate:canonical:three-layer:v1
canonical admissibility runtime: stegcore.three_layer.evaluate_three_layer
```

Live repository/workflow evidence supersedes chat summaries. This file is the canonical continuation source for current StegCore runtime, portable-product, benchmark, release, and cross-application integration work.

## Current goals

```text
STEGGATE-FULL-FUNCTIONAL-ACTIVATION-001 / issue #68: COMPLETE
STEGGATE-HEARTBEAT-CREDENTIAL-INTEGRATION-001 / issue #75: COMPLETE
STEGGATE-PORTABLE-PRODUCT-CONSISTENCY-001: COMPLETE + HOSTED VALIDATED
ADMITTEDCODE-PERFORMANCE-BENCHMARK-001: COMPLETE + HOSTED VALIDATED
STEGGATE-TUNNEL-CONTINUITY-HARDENING: MACHINE-OWNED CONTINUATION
STEGGATE-FOUR-APP-RUNTIME-BINDING-001 / issue #70: ACTIVE
```

The active #70 claim remains `current-session-common-runtime-binding / CLAIMED_FOR_IMPLEMENTATION`. Do not create per-application StegGate evaluators, bind policy identity to a transport URL, or modify HIL paths owned by a separate Site claim.

## Canonical authority chain

```text
Governance policy/evidence
  -> src/stegcore/three_layer.py:evaluate_three_layer
  -> src/stegcore/steggate.py:evaluate_admissibility
  -> ALLOW | DENY | REVIEW | FAIL_CLOSED
  -> src/stegcore/steggate_runtime.py:governed_steggate_execute
  -> src/stegcore/commit_governance.py:coherence_gate
  -> bounded consequence only after ALLOW + coherence ALLOW
  -> observation / reconciliation
```

Transport discovery, heartbeat cadence, leases, UI state, CLI state, provider state, benchmark state, and application integration do not grant policy or execution authority.

## Portable product boundary — 0.2.0

Supported current-product surfaces:

```text
Python: stegcore.AdmissibilityRequest + stegcore.evaluate_admissibility
CLI:    steggate identity | self-test | evaluate | serve
HTTP:   /health | /v1/runtime-identity | /v1/capabilities | /v1/self-test | /v1/evaluate
```

All supported surfaces terminate in the same canonical evaluation composition.

Current product documentation and machine checks:

```text
README.md
docs/STEGGATE_PORTABLE_PRODUCT.md
docs/STEGGATE_RUNTIME_IDENTITY_CONTRACT.md
docs/ADMITTEDCODE_PERFORMANCE.md
CHANGELOG.md
VERSION
pyproject.toml
src/stegcore/version.py
scripts/verify_product_consistency.py
tests/test_product_consistency.py
```

Historical receipt/schema/review/constitutional versions remain independent provenance domains and are not rewritten to match product version `0.2.0`.

## AdmittedCode performance benchmark — COMPLETE + HOSTED VALIDATED

Installed canonical performance surfaces:

```text
benchmarks/admittedcode-performance-policy.json
tools/run_admittedcode_benchmarks.py
tests/test_admittedcode_performance.py
docs/ADMITTEDCODE_PERFORMANCE.md
.github/workflows/admittedcode-performance.yml
.github/workflows/release-bump.yml
```

The benchmark emits a versioned JSON receipt:

```text
schema: stegverse.admittedcode.performance-receipt.v1
default path: artifacts/admittedcode-performance-receipt.json
```

Measured dimensions:

```text
decision correctness
false ALLOW / false DENY
four-disposition correctness
FAIL_CLOSED integrity
candidate/approval hash binding
reason-code presence
predicate-matrix completeness
canonical receipt-hash presence
deterministic stable-semantic replay
Python / service / CLI semantic equivalence
runtime identity consistency
p50 / p95 / p99 / max core latency
CPU time per evaluation
Python traced memory and process max-RSS observation
bounded-concurrency throughput + correctness under load
CLI cold-start identity and self-test time
governance-composition overhead versus canonical three-layer evaluator
optional live HTTP round-trip latency via --url
four-application integration progress
manual developer-experience fields for install-to-first-ALLOW and failed-request diagnosis time
```

Release-blocking benchmark invariants:

```text
false_allow_rate = 0
four_disposition_correctness_rate = 1.0
fail_closed_integrity_rate = 1.0
candidate_binding_integrity_rate = 1.0
deterministic_semantic_replay_rate = 1.0
cross_interface_equivalence_rate = 1.0
runtime_identity_consistency_rate = 1.0
parallel_evaluator_escape_count = 0
matrix_completeness_rate = 1.0
reason_code_presence_rate = 1.0
```

Initial latency guardrails are recorded but non-blocking until enough historical receipts exist for a defensible regression policy.

Determinism rule: `decision_state_hash` and canonical three-layer receipt hash are time-bound provenance. They are required to exist but are not required to repeat across independent evaluations. Semantic replay compares the stable material decision surface, including disposition, candidate hash, reasons, canonical request hash, authority-boundary fields, and predicate matrix semantics.

Hosted validation:

```text
workflow: AdmittedCode Performance
run: 31507071754
head: 59ad67d6432f223387232fa05cc71dabf780ac74
conclusion: SUCCESS
artifact: 9107472044
artifact digest: sha256:dfd1610c1093e0dbeaf220dd981c85e7ce8241256f1cfdfc039db4f3199fafa2

workflow: AdmittedCode Performance
run: 31507106362
head: b40bcbcb6649ed943acbcbd032aa89c93f6f6a0f
conclusion: SUCCESS
artifact: 9107494384
artifact digest: sha256:fbf052e8a9fcda7279137742d5faac04b206889566979d6d5334a7e244285e80
```

The first workflow attempt failed because it incorrectly treated the time-bound canonical receipt hash as stable replay material. That defect was corrected; later hosted runs prove the corrected contract. Do not regress to comparing time-bound receipt/state hashes as semantic equivalence.

## Release integration

The portable-product release bump now:

```text
1. updates VERSION + pyproject.toml + src/stegcore/version.py;
2. updates CHANGELOG.md;
3. runs product consistency verification;
4. installs the release candidate;
5. runs AdmittedCode benchmark contract tests;
6. runs the release-blocking benchmark suite;
7. uploads the release-candidate performance receipt;
8. only then creates/pushes the release branch and opens the release PR.
```

A release-candidate benchmark failure therefore prevents the release PR from being opened.

## Runtime identity contract — COMPLETE

```text
GET /v1/runtime-identity
contract_version: stegverse.steggate.runtime-identity.v1
runtime_identity: stegverse:steggate:canonical:three-layer:v1
canonical_owner: StegVerse-Labs/StegCore
canonical_admissibility_runtime: stegcore.three_layer.evaluate_three_layer
transport_identity_authoritative: false
```

Portable product version and runtime identity contract version are distinct compatibility domains.

## Functional activation and transport

Issue #68 remains complete. Historical activation evidence:

```text
data/steggate-live-activation-receipt.json
state: COMPLETE
deployment_source: heartbeat_ephemeral_micronode
observed_at: 2026-08-09T09:14:06.578269Z
```

Canonical transport remains heartbeat-owned zero-credential public transport. Persistent Render authority is `NONE`. Lease/reconstruction continuation remains machine-owned under:

```text
StegVerse-Labs/.github/handoffs/SHWP-DURABLE-RUNTIME-ACTIVATION.json
StegVerse-Labs/.github/control/worker-registry.json#SHWP-DURABLE-RUNTIME-ACTIVATION
```

## Four-app canonical runtime integration — ACTIVE

Canonical state:

```text
management/steggate-four-app-runtime-binding.json
core contract: COMPLETE
applications CI-bound or stronger: 3/4
applications public-direct: 0/4
Ecosystem Chat: CI_BOUND_PUBLIC_EVIDENCE_PENDING
VACC: CI_BOUND_PUBLIC_EVIDENCE_PENDING
Math Solver: CI_BOUND_PUBLIC_EVIDENCE_PENDING
HIL: PENDING_DIRECT_EVIDENCE
```

Issue #70 remains open until each named application retains direct evidence that its governed path consumed the canonical runtime identity and traversed canonical StegGate semantics.

## Remaining work and owners

```text
StegVerse-Labs/StegCore
  -> continue issue #70 without parallel evaluators
  -> accumulate benchmark receipts across releases before making latency guardrails release-blocking
  -> do not cut a runtime product tag until applicable release authority and release gates are satisfied

StegVerse-Labs/Site + named consumer owners
  -> direct public/runtime evidence for Ecosystem Chat, VACC, Math Solver, HIL

StegVerse-Labs/.github
  -> sovereign carrier restart/reconstruction and lease lifecycle under canonical worker ownership

Future governed runtime release propagation/reconciliation:
  -> StegVerse-Labs/Site
  -> GCAT-BCAT-Engine/Publisher
  -> StegVerse-Labs/admissibility-wiki
  -> StegVerse-002/stegguardian-wiki
```

## Validation commands

```bash
pytest -q
python scripts/verify_product_consistency.py
steggate self-test
steggate evaluate examples/steggate_allow_request.json
python tools/run_admittedcode_benchmarks.py
python tools/run_admittedcode_benchmarks.py --url https://<live-steggate-host>
```

## Completion

```text
functional StegGate runtime: 100%
portable product consistency implementation: 100%
portable product consistency hosted validation: 100%
runtime identity core contract: 100%
AdmittedCode benchmark implementation: 100%
AdmittedCode benchmark hosted validation: 100%
release-candidate benchmark gate: INSTALLED
current portable-product files developed: 100%
scaffolding/stubs in current portable StegGate path: 0
four-app CI-or-stronger binding: 3/4
four-app public-direct evidence: 0/4
parent four-app goal: NOT COMPLETE
```

## Canonical continuation

```text
StegVerse-Labs/StegCore#70
StegVerse-Labs/Site#239
StegVerse-Labs/StegCore/STEGCORE_MIRROR_HANDOFF.md
StegVerse-Labs/StegCore/docs/STEGGATE_PORTABLE_PRODUCT.md
StegVerse-Labs/StegCore/docs/ADMITTEDCODE_PERFORMANCE.md
StegVerse-Labs/StegCore/benchmarks/admittedcode-performance-policy.json
StegVerse-Labs/StegCore/management/steggate-four-app-runtime-binding.json
StegVerse-Labs/.github/handoffs/SHWP-DURABLE-RUNTIME-ACTIVATION.json
```

The performance/benchmark-tracking goal is installed, hosted-validated, release-integrated, and durably transferred. No unique chat state is required to continue it.
