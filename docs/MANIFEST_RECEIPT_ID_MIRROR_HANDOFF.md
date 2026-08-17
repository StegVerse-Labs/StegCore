# Manifest Receipt ID Mirror Handoff

## Canonical authority

```text
goal_id: STEGCORE-MANIFEST-RECEIPT-ID-001
adjacent_goal_id: STEGCORE-AE-MANIFEST-CAPABILITY-CONTEXT-002
repository: StegVerse-Labs/StegCore
branch: feat/ae-manifest-capability-context-v1
parent_handoff: docs/TRANSACTION_CONTINUITY_MIRROR_HANDOFF.md
canonical_issue: #85
pull_request: #141
validation_task: tasks/STEGCORE-AE-MANIFEST-CAPABILITY-CONTEXT-VALIDATION-002V.json
credential_authority: TV/TVC
github_token_runtime_authority: NONE
non_tv_tvc_secret_or_token_required: false
render_required: false
```

Live repository state, current Admissible-Existence handoffs, Master Records sovereign custody evidence, issue #85, PR #141, and this handoff supersede older hosted-transport assumptions.

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

The local model/runtime goal is already `COMPLETE_RELEASED` under `StegVerse-002/micro-node-runtime/docs/SOVEREIGN_LOCAL_MODEL_RUNTIME_MIRROR_HANDOFF.md`; live activation remains MACHINE_OWNED by resident v12 heartbeat -> TVC -> LLM-adapter -> Master Records and MUST NOT be duplicated here.

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

Master Records has provider-neutral/local exact-run, route, replay-operation, reconstruction-operation, and portable custody. Retained sovereign validation contains T0/T1-A/T1-B exact-run records and replay/reconstruction chains with `third_party_host_required=false`.

```text
third-party hosted transport: OPTIONAL
Render: NOT REQUIRED / NOT AUTHORITY
sovereign evaluator validation: AVAILABLE
persistent replication / backup automation: general hardening, not bounded evaluator prerequisite
```

Do not recreate a hosted-service dependency in StegCore.

## AE capability-context integration

Admissible-Existence is canonically implemented by `src/stegcore/admissible_existence.py`, `src/stegcore/capability_registry.py`, the machine-readable registry, and `docs/ADMISSIBLE_EXISTENCE_CAPABILITY_MODEL_MIRROR_HANDOFF.md`.

PR #141 adds only the transaction-owned observation layer:

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

## Claim and collision state

```text
task_id: STEGCORE-AE-MANIFEST-CAPABILITY-CONTEXT-002
implementation_state: INSTALLED_ON_PR_141_UNVALIDATED
validation_state: BLOCKED_CREDENTIAL_CLEAN_SOURCE_MATERIALIZATION
session_role: DISTINCT_IMPLEMENTATION_AND_VALIDATION_SUPPORT
claim_created_at: 2026-08-17T12:22:00-05:00
branch: feat/ae-manifest-capability-context-v1
release_condition: actual focused/regression validation executes without NON-TV/TVC credentials; PASS permits PR merge, issue/handoff reconciliation, and claim release
collision_boundaries: no AE policy rewrite; no duplicate SES runner; no duplicate local model/runtime/heartbeat; no duplicate receipt/custody authority; no NON-TV/TVC credentials/tokens
```

No competing open StegCore PR for this exact capability-context/manifest-receipt scope was found before claiming PR #141.

## Validation evidence — blocked before test execution

Credential-clean PR workflows were directly inspected. They did start, but all six failed before source/test execution at the same source-materialization step:

```text
StegCore Tests: 32050514065 FAILURE_PRE_TEST
Validate StegCore Runtime: 32050514043 FAILURE_PRE_TEST
Test Readiness: 32050514015 FAILURE_PRE_TEST
Validate StegVerse 001 002 Baseline: 32050514026 FAILURE_PRE_TEST
BCAT Gate: 32050514070 FAILURE_PRE_TEST
Portable Release Candidate build-only: 32050514007 FAILURE_PRE_TEST
common failing step: Anonymous public repository fetch
```

StegCore Tests job `95448498397` proved the credential-clean check first:

```text
credential_authority=TV/TVC
consumer_credential_present=false
```

The anonymous private-source fetch then failed:

```text
fatal: could not read Username for 'https://github.com': No such device or address
```

Therefore no code test executed. This is neither PASS nor evidence of a code-test failure. It MUST NOT be bypassed by `GITHUB_TOKEN`, `GH_TOKEN`, PAT, or any NON-TV/TVC credential.

Durable continuation is installed at:

```text
tasks/STEGCORE-AE-MANIFEST-CAPABILITY-CONTEXT-VALIDATION-002V.json
state: BLOCKED_CREDENTIAL_CLEAN_SOURCE_MATERIALIZATION
machine trigger: current PR #141 head can be materialized on a StegVerse-controlled validation host without a NON-TV/TVC credential, or the canonical repository owner installs a credential-clean private-source materialization mechanism
```

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

## Cross-repository consumer transfer

The post-merge consumer requirement has been durably transferred without taking over active claims:

```text
StegVerse-org/StegVerse-SDK issue #16 comment 5318211381
  consume/project generated capability_context after StegCore #141 validation/merge;
  do not create a parallel AE resolver;
  preserve existing SDK-INGRESS-RUNTIME-BINDING-006 ownership.

StegVerse-org/LLM-adapter issue #139 comment 5318212356
  pass through generated capability_context after StegCore #141 validation/merge;
  do not trust provider/model lifecycle claims or create a parallel AE resolver.

StegVerse-Labs/StegCore issue #85 comment 5318209841
  records PR #141, sovereign custody reconciliation, validation blocker, and release condition.
```

## Validation commands

```text
pytest -q tests/test_manifest_capability_context.py
pytest -q tests/test_transaction_lifecycle.py tests/test_manifest_receipts.py tests/test_manifest_receipt_provider.py
pytest -q
python scripts/verify_product_consistency.py
```

GitHub-hosted validation may remain only where credential-clean and technically possible; it is not production/runtime/control-plane authority.

## Scoped execution inventory

Denominator for `STEGCORE-AE-MANIFEST-CAPABILITY-CONTEXT-002`: 8 required deliverables.

```text
1 canonical AE-context resolver: INSTALLED_PR_141
2 transaction receipt/result binding: INSTALLED_PR_141
3 exact-run evidence/reconstruction preservation: INSTALLED_PR_141
4 focused fail-closed/preservation tests: INSTALLED_PR_141_UNEXECUTED
5 regression/repository validation: BLOCKED_PRE_TEST_WITH_DURABLE_OBSERVER
6 issue #85 + handoff reconciliation: COMPLETE_FOR_CURRENT_STATE
7 merge to main + claim release: PENDING_VALIDATION
8 SDK/LLM-adapter consumer requirement transfer: COMPLETE_BLOCKED_ON_PR_141
```

Task completion: 6/8 = 75%. Developed-file denominator: 6 required branch files (resolver, transaction integration, manifest receipt integration, focused tests, handoff, validation task), 6 present; scaffolding/stubs 0; missing 0.

Validation denominator: 4 gates: focused tests; manifest/transaction regressions; applicable repository validation; post-merge source-of-truth verification. Current actual validation: 0/4. Hosted runners were inspected but failed before test execution.

Integration denominator: 4 gates: AE registry -> transaction context; transaction context -> exact-run receipt/reconstruction; main merge/issue final reconciliation; SDK+LLM-adapter implementation after dependency release. Current: 2/4 actual source integrations complete; downstream requirements transferred but not counted as integrated code.

Session-consolidation denominator: 10 originating/adjacent goals listed above. All 10/10 have durable canonical owners/records; current session still retains the distinct PR #141 validation/merge support role until release or explicit transfer of that execution role.

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

This session is not archive-safe while it retains the distinct PR #141 validation/merge support role. Release condition: credential-clean source materialization causes actual tests to execute; if PASS, merge PR #141, reconcile issue #85/main handoff, and release the claim; if FAIL, persist exact diagnostics and transfer correction ownership. No other session goal remains only in chat.
