# StegCore Mirror Handoff

## Source of truth

```text
organization: StegVerse-Labs
repository: StegCore
branch: main
canonical StegGate owner: StegVerse-Labs/StegCore
portable product source version: 0.3.0
successor release state: SOURCE_VALIDATED_MERGED / v0.3.0 NOT YET RELEASED
canonical runtime identity: stegverse:steggate:canonical:three-layer:v1
canonical admissibility runtime: stegcore.three_layer.evaluate_three_layer
```

Live repository/workflow evidence supersedes chat summaries. This file is the canonical continuation source for current StegCore runtime, portable-product, benchmark, release, reviewer-readiness, and cross-application integration work.

## 2026-08-26 successor 0.3 reconciliation

The current portable-product source line is 0.3.0. Exact successor release coordinates and validation are canonical in `docs/STEGCORE_0_3_RELEASE_CANDIDATE_MIRROR_HANDOFF.md`:

```text
source parent: ef38410505b0ef3e84148892b1d6e3cdef20f300
release commit: 58445bb14642c1889cf9802666c15bd48c6d2e39
target tag: v0.3.0
exact source validation: 32911552882 SUCCESS
canonical source reconciliation merge: 788a55b8e616b53fdc593fd56a10e9d7f5625f51
release authority: TV/TVC
release state: NOT RELEASED
```

The 0.2.0 benchmark/baseline sections retained below are historical/provisional evidence domains and are not a claim that 0.2.0 remains the current source-product identity. StegCore PR #141 remains a separate active capability-context lane.

## Current goals

```text
STEGGATE-FULL-FUNCTIONAL-ACTIVATION-001 / issue #68: COMPLETE
STEGGATE-HEARTBEAT-CREDENTIAL-INTEGRATION-001 / issue #75: COMPLETE
STEGGATE-PORTABLE-PRODUCT-CONSISTENCY-001: COMPLETE + HOSTED VALIDATED
ADMITTEDCODE-PERFORMANCE-BENCHMARK-001: COMPLETE + HOSTED VALIDATED
ADMITTEDCODE-PRE-REVIEW-HARDENING-001: COMPLETE + HOSTED VALIDATED
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

Transport discovery, heartbeat cadence, leases, UI/CLI state, provider state, benchmark state, and application integration do not grant policy or execution authority.

## Portable product boundary — 0.2.0

Supported current-product surfaces:

```text
Python: stegcore.AdmissibilityRequest + stegcore.evaluate_admissibility
CLI:    steggate identity | self-test | evaluate | serve
HTTP:   /health | /v1/runtime-identity | /v1/capabilities | /v1/self-test | /v1/evaluate
```

All supported surfaces terminate in the same canonical evaluation composition.

Canonical current-product documentation and machine checks:

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

## AdmittedCode performance and pre-review hardening — COMPLETE + HOSTED VALIDATED

Installed measurement and review-readiness surfaces:

```text
benchmarks/admittedcode-performance-policy.json
benchmarks/admittedcode-baseline-v0.2.0.json
benchmarks/admittedcode-stranger-observation-template.json
tools/run_admittedcode_benchmarks.py
tools/compare_admittedcode_baseline.py
tools/run_admittedcode_onboarding_rehearsal.py
tests/test_admittedcode_performance.py
docs/ADMITTEDCODE_PERFORMANCE.md
.github/workflows/admittedcode-performance.yml
.github/workflows/release-bump.yml
```

The benchmark receipt schema is `stegverse.admittedcode.performance-receipt.v1`. It measures correctness, false ALLOW/DENY, four-disposition behavior, FAIL_CLOSED integrity, candidate/approval binding, reason/matrix completeness, canonical receipt-hash presence, stable-semantic replay, Python/service/CLI equivalence, runtime identity, latency percentiles, CPU/memory observations, bounded-concurrency throughput with correctness, cold start, governance composition overhead, optional HTTP round-trip performance, four-app integration progress, and explicitly separate human usability fields.

Release-blocking invariants remain:

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

`decision_state_hash` and canonical three-layer receipt hash are time-bound provenance. They must exist but are excluded from stable semantic replay equality.

### Provisional hosted baseline

`benchmarks/admittedcode-baseline-v0.2.0.json` now retains three successful comparable hosted samples:

```text
run 31507071754 / artifact 9107472044
run 31507106362 / artifact 9107494384
run 31508213959 / artifact 9107938760
```

Observed envelope:

```text
core p95 latency:          0.773312 .. 1.142945 ms
governance p95 overhead:   0.131866 .. 0.225686 ms
throughput c=1:            2948.276 .. 4752.710 req/s
throughput c=10:           2765.099 .. 4615.006 req/s
throughput c=50:           2635.831 .. 4467.080 req/s
identity cold start:       254.511 .. 394.152 ms
self-test cold start:      254.632 .. 381.578 ms
```

The timing/throughput baseline is intentionally provisional. Promotion toward release-blocking performance thresholds requires at least 10 comparable successful receipts across at least 3 distinct commits or release candidates. Security/correctness invariants remain release blocking independently.

### HTTP-path proof

The hosted workflow now starts the packaged StegGate HTTP service locally and benchmarks the actual `/v1/evaluate` path after validating `/health` and `/v1/runtime-identity`.

First retained HTTP observation:

```text
run: 31508213959
artifact: 9107938760
localhost HTTP p95: 1.861632 ms
HTTP correctness: 1.0
runtime identity consistent: true
canonical runtime consistent: true
```

This is packaged HTTP-path evidence, not a public-Internet transport claim. Historical tunnel URLs must not be treated as current endpoints.

### Newcomer mechanical proof and human-observer boundary

The hosted workflow now executes `tools/run_admittedcode_onboarding_rehearsal.py` in a fresh temporary virtual environment. Run `31508213959` completed the full mechanical path in `9972.057 ms`, including environment creation, local package install, canonical identity resolution, first ALLOW, and an induced stale-policy DENY with reason evidence.

This is deliberately **not** a human usability score. The two human targets remain:

```text
unfamiliar-human install -> first ALLOW: <= 5 minutes
unfamiliar-human deliberate-failure diagnosis: <= 15 minutes
```

Canonical observation form:

```text
benchmarks/admittedcode-stranger-observation-template.json
status: UNMEASURED
```

Do not fabricate, estimate, or substitute CI/onboarding rehearsal timing for these human observations. They can only be completed by an actual unfamiliar operator. A reviewer should perform this blind measurement before receiving a detailed implementation walkthrough if the measurement is intended to remain independent.

## Release integration

The portable-product release workflow now:

```text
1. aligns VERSION + pyproject.toml + src/stegcore/version.py;
2. updates CHANGELOG.md;
3. runs product consistency verification;
4. installs the release candidate;
5. runs AdmittedCode benchmark contract tests;
6. starts and validates the candidate HTTP service;
7. runs release-blocking correctness/performance checks through the HTTP-capable benchmark lane;
8. compares the compatible hosted regression baseline;
9. retains performance + regression evidence;
10. only then creates/pushes a release branch and opens the release PR.
```

Performance regression bands remain warning-only while provisional; canonical identity incompatibility and correctness/security failures fail closed.

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

Issue #68 remains complete. Historical activation evidence is retained at `data/steggate-live-activation-receipt.json`; it is not a continuously rewritten health record. Canonical transport continuity remains machine-owned under the StegVerse-Labs `.github` durable runtime activation handoff/worker registry. Persistent Render authority remains `NONE` for this boundary.

## Four-app canonical runtime integration — ACTIVE

Canonical state remains:

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
  -> accumulate comparable benchmark receipts to >=10 before considering performance-band promotion
  -> collect unfamiliar-human usability evidence from an actual reviewer/operator; never fabricate it
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
python tools/run_admittedcode_onboarding_rehearsal.py
python tools/compare_admittedcode_baseline.py artifacts/admittedcode-performance-receipt.json
```

## Completion

```text
functional StegGate runtime: 100%
portable product consistency implementation: 100%
portable product consistency hosted validation: 100%
runtime identity core contract: 100%
AdmittedCode benchmark implementation: 100%
AdmittedCode benchmark hosted validation: 100%
hosted local HTTP performance path: 100%
provisional baseline/regression machinery: 100%
automated clean-environment onboarding rehearsal: 100%
human unfamiliar-operator measurement: UNMEASURED BY DESIGN
release-candidate benchmark/regression gate: INSTALLED
current portable-product/benchmark files developed: 100%
scaffolding/stubs in current portable StegGate/benchmark path: 0
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
StegVerse-Labs/StegCore/benchmarks/admittedcode-baseline-v0.2.0.json
StegVerse-Labs/StegCore/benchmarks/admittedcode-stranger-observation-template.json
StegVerse-Labs/StegCore/management/steggate-four-app-runtime-binding.json
StegVerse-Labs/.github/handoffs/SHWP-DURABLE-RUNTIME-ACTIVATION.json
```

All executable pre-review performance, baseline, HTTP-path, release-gate, and mechanical-onboarding hardening is installed and durably transferred. The only intentionally uncompleted performance item is an unfamiliar-human observation that cannot be validly self-generated by the implementation session.
