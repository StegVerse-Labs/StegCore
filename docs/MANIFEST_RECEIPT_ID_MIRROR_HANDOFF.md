# Manifest Receipt ID Mirror Handoff

## Canonical authority

```text
goal_id: STEGCORE-MANIFEST-RECEIPT-ID-001
adjacent_goal_id: STEGCORE-AE-MANIFEST-CAPABILITY-CONTEXT-002
repository: StegVerse-Labs/StegCore
branch: feat/ae-manifest-capability-context-v1
parent_handoff: docs/TRANSACTION_CONTINUITY_MIRROR_HANDOFF.md
canonical_issue: #85
credential_authority: TV/TVC
github_token_runtime_authority: NONE
non_tv_tvc_secret_or_token_required: false
render_required: false
```

Live repository state, current Admissible-Existence handoffs, Master Records sovereign custody evidence, issue #85, and this handoff supersede older hosted-transport assumptions.

## Originating session goals preserved

```text
1 ordinary SDK 000 / 00 / 0 / 1 / 2 governed navigation
2 exact-run manifest_receipt_id in every ordinary returned packet
3 immutable replay/reconstruction without consequence re-execution
4 full canonical custody before caller return projection
5 000 self-describing governed demo and manifest labels
6 external LLM/direct-machine manifest interoperability
7 T0 / T1-A / T1-B evaluator sequence using ordinary packets
8 reconcile newest Admissible-Existence capability lifecycle with manifested runs
9 no NON-TV/TVC secret/token authority
10 no duplicate local runtime/model, SES construction, custody, or evaluator authority
```

The local model/runtime goal is already `COMPLETE_RELEASED` under `StegVerse-002/micro-node-runtime/docs/SOVEREIGN_LOCAL_MODEL_RUNTIME_MIRROR_HANDOFF.md`; live activation remains MACHINE_OWNED by the resident v12 heartbeat -> TVC -> LLM-adapter -> Master Records chain and MUST NOT be duplicated here.

Transition-native executable construction has converged into `StegVerse-Labs/TVC/docs/SES_GENESIS_MIRROR_HANDOFF.md`; StegCore retains only post-hoc evaluation through `tasks/TRANSITION-NATIVE-AI-CROSS-LANE-EVALUATION-002.json` and MUST NOT build a second SES runner.

StegFin is trade-ready at the USER_ONLY pre-sign boundary under `StegVerse-Labs/stegfin-governance/docs/STEGFIN_MIRROR_HANDOFF.md`; this work gains no signing/broadcast authority.

## Existing exact-run implementation

```text
src/stegcore/transaction_lifecycle.py
src/stegcore/manifest_receipts.py
src/stegcore/manifest_receipt_provider.py
tests/test_transaction_lifecycle.py
tests/test_manifest_receipts.py
tests/test_manifest_receipt_provider.py
```

A canonical `MR-<SHA256>` locator resolves one immutable run. The locator grants no authority. Registration, exact evidence-package resolution, non-mutating replay, and reconstruction without consequence re-execution are installed.

## Master Records sovereign custody reconciliation

The previous hosted-transport proof assumption is superseded for the bounded evaluator lane by:

```text
master-records/orchestration/MANIFEST_RECEIPT_CUSTODY_MIRROR_HANDOFF.md
implementation_state: COMPLETE_SOVEREIGN_PATH_INSTALLED
activation_state: SOVEREIGN_VALIDATION_AVAILABLE
```

Master Records now has provider-neutral/local exact-run, route, replay-operation, reconstruction-operation, and portable custody. Retained sovereign validation already contains T0/T1-A/T1-B exact-run records and replay/reconstruction chains with `third_party_host_required=false`.

```text
third-party hosted transport: OPTIONAL
Render: NOT REQUIRED / NOT AUTHORITY
sovereign evaluator validation: AVAILABLE
persistent replication / backup automation: general hardening, not bounded evaluator prerequisite
```

Do not recreate a hosted-service dependency in StegCore.

## AE capability-context integration

Admissible-Existence is canonically implemented by `src/stegcore/admissible_existence.py`, `src/stegcore/capability_registry.py`, the machine-readable registry, and `docs/ADMISSIBLE_EXISTENCE_CAPABILITY_MODEL_MIRROR_HANDOFF.md`.

This branch adds only the transaction-owned observation layer:

```text
src/stegcore/manifest_capability_context.py
src/stegcore/transaction_lifecycle.py
src/stegcore/manifest_receipts.py
tests/test_manifest_capability_context.py
```

Contract:

```text
caller may request capability_id + optional required_phase
-> actual lifecycle state resolves from canonical AE registry
-> caller phase claims are non-authoritative
-> unknown capability fails closed
-> unmet required phase fails closed before executor invocation
-> existence_hash / phase / evidence / blocker / continuation owner are retained
-> capability_context_hash binds ingestion, StegGate, return-ingestion, replay descriptor
-> exact-run evidence package retains capability_context
-> reconstruction preserves original-run capability state and never substitutes current state
-> resolution grants authority: false
```

The transaction layer receipts the observation/reference; AE itself still mints no transaction continuity receipt.

## Active claim / collision boundary

```text
task_id: STEGCORE-AE-MANIFEST-CAPABILITY-CONTEXT-002
originating_goal: reconcile newest AE implementation with manifest receipt/replay/reconstruction development
claim_state: CLAIMED_FOR_IMPLEMENTATION
claimant: this session / distinct StegCore integration lane
claim_created_at: 2026-08-17T12:22:00-05:00
branch: feat/ae-manifest-capability-context-v1
files: src/stegcore/manifest_capability_context.py; src/stegcore/transaction_lifecycle.py; src/stegcore/manifest_receipts.py; tests/test_manifest_capability_context.py; this handoff
collision_boundaries: no AE policy rewrite; no duplicate SES runner; no duplicate local model/runtime/heartbeat; no duplicate receipt/custody authority; no NON-TV/TVC credentials/tokens
release_condition: applicable tests/workflows pass, PR merges, issue #85 is reconciled, claim is released/transferred
expected_evidence: PR workflow runs/jobs/logs plus merged commit or explicit blocked validation record
next_after_release: SDK/LLM-adapter may expose generated capability_context without asserting lifecycle state themselves
```

No competing open StegCore PR for this exact capability-context/manifest-receipt scope was found before claiming the branch.

## Full custody before caller projection

```text
canonical manifested transaction
-> canonical governance/state transitions
-> generated AE capability context when applicable
-> complete exact-run result + receipt chain
-> canonical manifest_receipt_id
-> retain full canonical evidence package in Master Records
-> apply return_projection / manifest_labels
-> return permitted packet INCLUDING manifest_receipt_id
```

`return_projection` and `manifest_labels` remain caller-facing controls only. Neither may alter exact-run identity, capability state, governance, or Master Records custody.

## Evaluator continuity

The ordinary T0/T1-A/T1-B packets must each carry their own `manifest_receipt_id`. A convenience index may repeat those IDs but is navigation, not new evidence. Capability context is additive and must not rewrite frozen T0/T1 semantics or create a bespoke evaluator path.

## Validation commands

```text
pytest -q tests/test_manifest_capability_context.py
pytest -q tests/test_transaction_lifecycle.py tests/test_manifest_receipts.py tests/test_manifest_receipt_provider.py
pytest -q
python scripts/verify_product_consistency.py
```

GitHub-hosted validation may remain only as credential-clean source validation; it is not production/runtime/control-plane authority.

## Scoped execution inventory

Denominator for `STEGCORE-AE-MANIFEST-CAPABILITY-CONTEXT-002`: 8 required deliverables.

```text
1 canonical AE-context resolver: INSTALLED_BRANCH
2 transaction receipt/result binding: INSTALLED_BRANCH
3 exact-run evidence/reconstruction preservation: INSTALLED_BRANCH
4 focused fail-closed/preservation tests: INSTALLED_BRANCH_UNVALIDATED
5 regression/repository validation: PENDING_PR_WORKFLOW
6 issue #85 + handoff reconciliation: HANDOFF_UPDATED / ISSUE_PENDING
7 merge to main + claim release: PENDING
8 SDK/LLM-adapter consumer transfer: PENDING_AFTER_MERGE
```

Developed-file denominator: 5 required branch files, 5 present; scaffolding/stubs 0; missing 0.

Validation denominator: 4 gates: focused tests; manifest/transaction regressions; applicable repository CI; post-merge source-of-truth verification. Current: 0/4 until executions are inspected.

Integration denominator: 4 gates: AE registry -> transaction context; transaction context -> exact-run receipt/reconstruction; main merge/issue reconciliation; SDK+LLM-adapter transfer. Current: 2/4 source-integrated on branch.

## Machine-owned / merged adjacent work

```text
SOVEREIGN-LOCAL-MODEL-001: COMPLETE_RELEASED; live activation MACHINE_OWNED
TVC SES construction: MERGED INTO StegVerse-Labs/TVC/docs/SES_GENESIS_MIRROR_HANDOFF.md
TRANSITION-NATIVE-AI-CROSS-LANE-EVALUATION-002: MACHINE_OWNED/BLOCKED_ON_TVC_BUNDLE
StegFin pre-sign trade-ready goal: COMPLETE_ACTIVATED; USER_ONLY sign/broadcast
SDK-INGRESS-RUNTIME-BINDING-006: CLAIMED_FOR_INTEGRATION; DO NOT COMPETE
SDK authority-boundary sovereign run: MACHINE_OWNED; DO NOT COMPETE
Master Records sovereign exact-run custody: COMPLETE_SOVEREIGN_PATH_INSTALLED
```

## Archive condition

This session is not archive-safe while this branch claim is active. It becomes consolidation-eligible after the branch is validated/merged or durably transferred as a blocked canonical claim, issue #85 and this handoff identify continuation state, and the SDK/LLM-adapter consumer requirement is transferred without duplicate execution.
