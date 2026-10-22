# StegCore / StegGate

StegCore is the canonical StegVerse commit-time governance runtime. **StegGate** is its portable product surface for evaluating one proposed consequential transition before execution.

Current portable product version: **0.3.0**.

## What it does

StegGate accepts a structured commitment candidate plus current judgment, signal/state, execution, capability, continuity, and approval evidence. It evaluates that request through the canonical StegCore admissibility chain and returns exactly one disposition:

```text
ALLOW | DENY | REVIEW | FAIL_CLOSED
```

The product boundary is intentionally narrow:

```text
candidate
  -> stegcore.three_layer.evaluate_three_layer
  -> stegcore.steggate.evaluate_admissibility
  -> disposition + reasons + complete predicate matrix + hashes
```

For routes that declare fresh SPE standing as required, canonical execution also re-verifies the bound SDK/SPE/interlock evidence before commit coherence or consequence invocation. Missing, stale, DENY, tampered, or mismatched required standing fails closed before the bounded executor can run.

Execution-boundary predicates preserve the distinction between **unknown** and **affirmatively false**. An unestablished applicable predicate remains `UNKNOWN` and produces `FAIL_CLOSED / execution.probe_required` until evidence or a governed probe establishes it; it is never coerced into a stale/false finding. An explicitly observed `False` predicate still follows its applicable DENY rule. This preserves fail-closed governance without converting absence of evidence into evidence of invalidity.

Interfaces may adapt input or presentation, but they must not implement a separate policy or admissibility engine.

StegCore does **not** mint continuity receipts, establish identity truth, grant provider authority, execute arbitrary external actions, publish content, or become durable evidence custody.

## Present-tense runtime enforcement conversion

The active `PA-001-ECOSYSTEM-RUNTIME-ENFORCEMENT-001` workstream is converting the already validated permission/admissibility invariant into explicit commit-time runtime enforcement. The governing rule is that **authority and time are state variables**: consequence-bearing execution must be decided from reconstructed commit-time state rather than presumed continuity of proposal-time approval.

The current source conversion centralizes one reusable present-state evaluator in `stegcore.commit_governance` and applies it to both `GovernedRuntime` and the canonical `governed_steggate_execute()` path. Before consequence invocation, the runtime now requires current authority state, authority-to-target binding, authority temporal validity, and current evidence state. Explicitly stale, expired, revoked, or mismatched state is a `DENY`; materially missing or indeterminate required state is `FAIL_CLOSED`. The exact authority state, target, evaluation instant, present-state checks, complete commit-state object, and commit-state hash are receipt-bound.

This source contract does not by itself prove resident runtime activation or ecosystem-wide enforcement. Current coordination, exact validation state, resident-proof requirements, and propagation gates are recorded in `docs/PA001_ECOSYSTEM_RUNTIME_ENFORCEMENT_MIRROR_HANDOFF.md`.

## Structured authority-basis resolution for evaluator tests

StegCore now exposes a bounded, non-authorizing authority-basis resolver for evaluator and interoperability tests:

```python
from stegcore.authority_basis import resolve_authority_basis
```

The resolver consumes a frozen set of caller-supplied authority and delegation assertions, explicit completeness declarations for those assertion sets, plus one exact candidate `action`, `target`, `scope`, actor identity, and evaluation instant. It derives only whether the represented basis establishes current actor authority and, when required, current delegation. A role label such as `board_member` or `junior_operator` is preserved as context but is never interpreted as authority.

```text
role label != authority
structured authority assertion != issued authority
authority-basis resolution != credential verification
evaluator resolution != TV/TVC authority issuance
incomplete/unestablished basis -> FAIL_CLOSED
complete basis with no current candidate-covering authority/delegation -> DENY
matching current scoped basis -> ALLOW as a currentness fact for downstream StegGate evaluation
```

This surface exists to prevent SDK or external-framework tests from hand-authoring `actor_authority_current` / `delegation_current` booleans while also avoiding a second authority plane. It does not define organizational role policy, mint authority, verify TVC credentials, or replace Interlock/InTr transition governance. Production credential and scoped-authority issuance remain separate TV/TVC responsibilities.

Canonical continuation and scope are recorded in `docs/SDK_AUTHORITY_BASIS_RESOLUTION_MIRROR_HANDOFF.md`.

## Exact fresh commit binding reference control

The Universal Governance sovereign reference runner additionally exercises an exact consequence-time binding over `state_version`, `state_hash`, `policy_epoch`, `policy_hash`, `evidence_bundle_hash`, and a single-use `execution_binding_id`. The reusable predicate is `stegcore.fresh_commit_binding`; it is deliberately a state-binding check, not a policy engine or authority source.

The bounded experiment first captures an authorization-aligned V0 binding, then performs a separately retained material state transition before any consequence. Both the canonical route and an alternate consequence-capable route must reject the stale V0 state without invoking the executor. A newly derived V1 binding may proceed through the existing Governance + StegGate consequence path exactly once; replay is denied after its execution binding is consumed. The alternate route reaches the same bounded consequence primitive but cannot supply the canonical commit-boundary permit.

This source experiment strengthens the reference-boundary proof only. GitHub Actions validation does **not** establish resident WorkerCoordinator claim/fence, sovereign resident execution, a Master Records organization record of an authentic resident instance, or real external-system ENFORCED activation. Those predicates remain separately evidence-gated under `SHWP-UNIVERSAL-GOVERNANCE-ENFORCED-REFERENCE-001`.

## GADI defensive reasoning surface

StegCore also contains the bounded reasoning surface for `GADI-001` (Governed Autonomous Defensive Intervention). This layer can correlate manifested external autonomous-system observations, preserve uncertainty and semantic qualifiers, classify threat state, compare declared defensive capabilities using least-destructive-effective semantics, and construct `DEFENSIVE_INTERVENTION_REQUEST` candidates.

This reasoning layer is **not execution authority and is not a parallel evaluator**. A threat assessment or intervention candidate cannot itself cause an external consequence. Every consequential defensive transition must still pass the canonical `stegcore.steggate.evaluate_admissibility` / InTr governance path and separately bind to a pre-authorized capability.

Semantic-integrity evidence is preserved as part of threat reasoning. Qualified statements such as `may`, `might`, `possible`, or `likely` must not silently become stronger assertions during correlation. Material semantic drift can contribute evidence to a threat assessment, but it never independently authorizes intervention.

Current bounded implementation and continuation state are recorded in `docs/GADI_STEGCORE_MIRROR_HANDOFF.md`.

## Install

Python 3.11+ is required.

The public PyPI distribution is **`stegverse-stegcore`** while the Python import/module namespace remains **`stegcore`**:

```bash
python -m pip install stegverse-stegcore
```

For editable development from a repository checkout:

```bash
python -m pip install -e .
```

Either installation exposes the `stegcore` Python API and the `steggate` CLI.

## Fastest verification

```bash
steggate identity
steggate self-test
```

`self-test` deterministically exercises ALLOW, DENY, REVIEW, and FAIL_CLOSED against the same canonical runtime used by the HTTP service.

## Evaluate a candidate

```bash
steggate evaluate examples/steggate_allow_request.json
```

The result contains the disposition, reason codes, candidate hash, canonical three-layer request/receipt hashes, decision-state hash, and complete predicate matrix.

## Run the HTTP service

```bash
steggate serve --host 127.0.0.1 --port 8000
```

Equivalent direct launch:

```bash
uvicorn stegcore.service:app --host 127.0.0.1 --port 8000
```

Canonical endpoints:

```text
GET  /health
GET  /v1/runtime-identity
GET  /v1/capabilities
GET  /v1/self-test
POST /v1/evaluate
GET  /docs
```

The runtime identity is transport-independent:

```text
contract_version: stegverse.steggate.runtime-identity.v1
runtime_identity: stegverse:steggate:canonical:three-layer:v1
canonical_owner: StegVerse-Labs/StegCore
canonical_admissibility_runtime: stegcore.three_layer.evaluate_three_layer
```

A host URL, tunnel, heartbeat, lease, UI, CLI, SDK, or application integration is never policy authority.

## Python API

```python
from stegcore import AdmissibilityRequest, evaluate_admissibility

request = AdmissibilityRequest.model_validate(payload)
result = evaluate_admissibility(request)
print(result.disposition)
```

The Python API, CLI, and HTTP service all terminate in the same canonical evaluation composition.

## Performance and benchmark tracking

Run the canonical AdmittedCode benchmark suite with:

```bash
python tools/run_admittedcode_benchmarks.py
```

It emits `artifacts/admittedcode-performance-receipt.json` and measures correctness, false-ALLOW/false-DENY behavior, FAIL_CLOSED integrity, candidate binding, deterministic semantic replay, cross-interface equivalence, p50/p95/p99 latency, throughput under bounded concurrency, CPU/memory observations, cold start, governance overhead, runtime identity consistency, and four-application integration progress.

A live deployment can be measured separately with:

```bash
python tools/run_admittedcode_benchmarks.py --url https://<steggate-host>
```

Release-blocking benchmark policy is in `benchmarks/admittedcode-performance-policy.json`. False ALLOW, disposition correctness, FAIL_CLOSED integrity, candidate binding, semantic replay, interface equivalence, runtime identity, matrix/reason completeness, and parallel-evaluator escape checks are fail-closed release measures. Hosted receipts are produced by `.github/workflows/admittedcode-performance.yml`.

See `docs/ADMITTEDCODE_PERFORMANCE.md` for the measurement contract and interpretation rules.

## Runtime authority chain

```text
Governance policy/evidence
  -> structured authority/delegation basis resolution when supplied
  -> stegcore.three_layer.evaluate_three_layer
  -> stegcore.steggate.evaluate_admissibility
  -> ALLOW | DENY | REVIEW | FAIL_CLOSED
  -> shared present-state check: authority + target + time + evidence
  -> exact fresh commit binding when required: state + policy + evidence + single-use execution binding
  -> governed commit-coherence boundary
  -> consequence execution, when separately authorized
  -> observation / reconciliation
```

`ALLOW` is admissibility, not proof that execution occurred. A consequence is still unreachable until the present state and commit-coherence gates pass. `FAIL_CLOSED` applies when required authority, target/time binding, evidence, or declared fresh-binding state cannot be established safely.

## Canonical documentation map

Read current-state documents before historical review material:

- `STEGCORE_MIRROR_HANDOFF.md` — live repository source of truth, active claims, validation, and continuation.
- `docs/PA001_ECOSYSTEM_RUNTIME_ENFORCEMENT_MIRROR_HANDOFF.md` — active conversion from the PA-001 semantic invariant to commit-time and ecosystem runtime enforcement.
- `docs/SDK_AUTHORITY_BASIS_RESOLUTION_MIRROR_HANDOFF.md` — non-authorizing structured authority/delegation basis resolution used by SDK evaluator integration without creating a duplicate authority plane.
- `docs/UNIVERSAL_GOVERNANCE_REFERENCE_RUNNER_MIRROR_HANDOFF.md` — bounded two-route Universal Governance reference runner and fresh-binding proof contract.
- `docs/GADI_STEGCORE_MIRROR_HANDOFF.md` — bounded GADI threat-reasoning implementation and continuation.
- `docs/STEGCORE_UNKNOWN_PROBE_SEMANTICS_MIRROR_HANDOFF.md` — UNKNOWN-versus-false governance semantics and frozen-v0.4 longitudinal regression evidence.
- `docs/STEGGATE_PORTABLE_PRODUCT.md` — supported portable product surface and compatibility rules.
- `docs/STEGGATE_RUNTIME_IDENTITY_CONTRACT.md` — transport-independent runtime identity contract.
- `docs/ADMITTEDCODE_PERFORMANCE.md` — canonical performance, benchmark, and release-measurement contract.
- `docs/STEGGATE_PRODUCT_REVIEW_V4.md` — network-governance architecture that the live runtime follows.
- `docs/STEGGATE_PRODUCT_REVIEW_V5.md` — formalism/research expansion; **not** a replacement for live runtime contracts.
- `management/steggate-four-app-runtime-binding.json` — current cross-application integration state.

Historical receipts, review documents, activation artifacts, and schema-versioned files remain evidence of their own point in time. Their embedded versions must not be interpreted as the current package/service version unless they explicitly say so.

## Current product status

The canonical StegGate runtime, HTTP service, runtime identity contract, four-disposition self-test, initial live activation, portable-product consistency lane, AdmittedCode performance benchmark lane, standing/interlock fail-closed consequence binding, and UNKNOWN-preserving probe-required execution semantics are implemented. GADI threat reasoning is being integrated as a bounded proposal-generation surface that preserves the same authority boundary; it does not replace or bypass canonical admission. Current integration work is proving complete successor release/custody/POST_RETURN behavior through the same runtime rather than creating per-application decision semantics. The PA-001 ecosystem-enforcement conversion has now installed shared source-level present-state enforcement across the direct governed runtime and canonical StegGate consequence path. The Universal Governance reference lane additionally carries a source-level V0→V1 fresh-binding and alternate-route negative-control experiment; exact-head CI, authentic resident execution, same-execution reconstruction, destination custody for authentic resident evidence, and ecosystem-wide propagation remain separate proof gates. See `STEGCORE_MIRROR_HANDOFF.md`, `docs/STEGCORE_UNKNOWN_PROBE_SEMANTICS_MIRROR_HANDOFF.md`, `docs/GADI_STEGCORE_MIRROR_HANDOFF.md`, `docs/UNIVERSAL_GOVERNANCE_REFERENCE_RUNNER_MIRROR_HANDOFF.md`, and `docs/PA001_ECOSYSTEM_RUNTIME_ENFORCEMENT_MIRROR_HANDOFF.md` for exact machine-owned state.

## Development verification

```bash
pytest -q
python scripts/verify_product_consistency.py
python tools/run_admittedcode_benchmarks.py --iterations 25 --replay-iterations 10 --throughput-requests 50 --concurrency 1,5
```

The consistency verifier fails when current package/service/CLI documentation drifts from the portable product version or canonical runtime identity. The benchmark exits non-zero when a release-blocking performance invariant fails.

## Legacy substrate

StegCore also contains earlier node-state, registry, orchestration, research, historical release, and ecosystem-management surfaces. They remain available for compatibility and provenance but are not the primary StegGate product entry point. Current product behavior is defined by the canonical files above.


## Host-provider independence

Current StegGate endpoint discovery is bounded to the StegVerse-owned stable rendezvous and fails closed when that endpoint is unavailable or not canonically bound. No third-party persistent host, tunnel, provider registry, or fallback runtime is selected by current discovery.


## Repository hygiene baseline — 2026-09-21

StegCore adopts canonical hygiene goal `HYGIENE-CAUSAL-ROOTS-001` through a read-only in-repository caller because the central anonymous bulk census cannot access this private repository. The pre-adoption census observed 138 branches. Classification produces evidence only and has no branch-deletion, runtime, release, or governance authority. See `docs/REPOSITORY_HYGIENE_ADOPTION_MIRROR_HANDOFF.md`.

## SVG synthetic governance-cycle trace benchmark (source candidate)

Run `python -m benchmarks.svg_governance_cycle --iterations 1000` and `python -m unittest discover -s tests -p test_svg_governance_cycle.py`. This is synthetic trace bookkeeping only; it is not native Governance/InTr admission, authorized consequence or Master Records reconstruction. Central admission request: StegVerse-Labs/.github#2757; native StegCore source benchmark ownership does not allocate a central SVG Goal Task ID or COSV.

## SVG native three-layer source adapter

`benchmarks/svg_native_source_adapter.py` binds the SVG source-only trace work to the installed `stegcore.three_layer.evaluate_three_layer` callable. `python -m unittest discover -s tests -p test_svg_native_source_adapter.py -v` checks native ALLOW, DENY and FAIL-CLOSED, malformed requests, and Governance A0–A8 stage-reference shape. Shape checking is **not** validation against Governance's authoritative JSON Schema; native evaluator receipts are **not** original InTr execution, Master Records organization records, or authorized consequences. Central issue: StegVerse-Labs/.github#2757; do not infer SVG admission or COSV from this source PR.

## Licensing candidate (not an operative grant)

A dual-license decision candidate and nonbinding commercial terms outline are under review in `docs/licensing/`. No root LICENSE has been adopted by this candidate, and public repository access alone grants no additional rights. See `docs/licensing/DUAL_LICENSE_DECISION_CANDIDATE.md` and `docs/licensing/LICENSING_MIRROR_HANDOFF.md`.

## Provider-free StegGate declaration (2026-10-22)

For enterprise eradication goal `ENTERPRISE-HOST-PROVIDER-ERADICATION-001` / COSV `40000100100000` (StegHealth #83), the proposed workflow repair disables third-party fallback selection. It does not grant resident runtime authority or establish sovereign observation, exact-head CI, independent review, provider shutdown, or protected merge. No replacement provider is authorized.
