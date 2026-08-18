# StegCore No-Non-TV/TVC Validation Credential Mirror Handoff

## Source of truth

```text
organization: StegVerse-Labs
repository: StegCore
branch: main
goal_id: STEGCORE-NO-NON-TVTVC-VALIDATION-CREDENTIALS-001
historical_issue: #93 (CLOSED COMPLETED)
historical_pull_request: #102 (MERGED)
private_source_followup_pull_request: #141
private_source_followup_task: tasks/STEGCORE-SOVEREIGN-PRIVATE-SOURCE-VALIDATION-003.json
upstream_tvc_pull_request: #79
superseded_upstream_tvc_pull_request: #20
parent_handoff: STEGCORE_MIRROR_HANDOFF.md
credential_authority: TV/TVC
non_TV_TVC_secret_or_token_allowed: false
archive_ready: false
```

This scoped handoff owns credential-clean validation transport semantics only. It does not own canonical StegGate policy, unrelated runtime activation, wallet authority, or TV/TVC credential custody.

## Historical completion before privatization

Issue #93 and PR #102 completed the original public-repository validation objective. Historical head `591ee20af4699d1d8c4c761bdb7fc801d1c5c176` produced five credential-clean validation passes while StegCore was public. Those remain historical evidence only; they do not prove anonymous fetch after privatization.

## Visibility transition and fanout repair

StegCore is private. Anonymous private-source fetch is therefore not a valid transport. A run that passes credential-absence assertions and then fails anonymous source fetch is neither product PASS nor product-code failure.

No response to privatization may silently restore `GITHUB_TOKEN`, `GH_TOKEN`, a PAT, provider credential, or other NON-TV/TVC token to the authoritative StegCore validation path.

Main commit `3b10620843a650224e18a7aac1e402b684becbf2` removed automatic pull-request fanout from the six legacy public-anonymous workflows and guarded their retained public-mode execution. That change removes known-invalid private-source noise; it is not replacement validation.

## Canonical private-source continuation

PR #141 installs:

```text
scripts/run_private_source_validation_via_tvc.py
scripts/run_sovereign_validation.py
tasks/STEGCORE-SOVEREIGN-PRIVATE-SOURCE-VALIDATION-003.json
.github/workflows/sovereign-private-source-validation.yml  # optional bridge only
```

The canonical bridge emits a bounded non-secret `MATERIALIZE_SOURCE_ARCHIVE` warrant to TVC, waits for a sanitized TVC receipt, verifies exact source identity, and then executes the sovereign validator. `GITHUB_TOKEN`, `GH_TOKEN`, `GITHUB_PAT`, and `TVC_EPHEMERAL_GITHUB_TOKEN` remain forbidden in the StegCore validation process.

PR #141 remains live and its exact source identity must be resolved at execution start. Source completeness, mergeability, skipped/absent hosted checks, or upstream readiness are not PASS.

## Upstream machine-owned dependency

Legacy TVC PR #20 is closed unmerged as structurally superseded. The canonical broker repair/admission path is now:

```text
StegVerse-Labs/TVC PR #79
TVC-GITHUB-REPOSITORY-OPERATION-BROKER-001
exact current governed-validation head: 50d84499e255f8c54814c79f6c9060853c62dae4

StegVerse-Labs/.github
handoffs/SHWP-TVC-REPOSITORY-BROKER-VALIDATION-001.json
workers/tvc_repository_broker_validation_worker.py
control/worker-registry.d/tvc-repository-broker-validation-001.json
receipt target:
receipts/tvc-repository-broker-validation/SHWP-TVC-REPOSITORY-BROKER-VALIDATION-001.json
```

PR #79 re-materializes the bounded broker implementation onto current private main. It remains draft and must not merge from source completeness. The `.github` validation carrier is pinned to the exact current PR #79 head and remains validation-only.

## Machine-observable upstream release condition

All are required:

```text
1. exact clean TVC PR #79 source at 50d84499e255f8c54814c79f6c9060853c62dae4 is locally present on a StegVerse-controlled carrier;
2. python tools/task_dispatcher.py tvc.github_repository_operation_broker.verify executes;
3. dispatcher status=ok and nested result.result=PASS;
4. consumer_credential_used=false;
5. tvc_github_credential_used=false;
6. non_tv_tvc_secret_or_token_used=false;
7. protected_value_disclosure=false;
8. carrier receipt records COMPLETED for that exact PR #79 head;
9. TVC repository integration authority canonically admits PR #79;
10. StegCore PR #141 exact source is re-resolved/materialized;
11. StegCore sovereign validator runs against that exact then-current PR #141 head;
12. all required StegCore validation commands PASS and the retained receipt records that exact head.
```

`HANDOFF_READY`, machine ownership, assignment, available worker, source complete, hosted workflow PASS, or release-ready are nonterminal.

## StegCore validation commands after materialization

```text
python3 -m pytest -q tests/test_manifest_capability_context.py
python3 -m pytest -q tests/test_transaction_lifecycle.py tests/test_manifest_receipts.py tests/test_manifest_receipt_provider.py
python3 -m pytest -q
python3 scripts/verify_product_consistency.py
```

The sovereign receipt must also prove exact source-head identity and `non_tv_tvc_secret_or_token_used=false` with no GitHub-token requirement.

## Current observed runtime state

At the latest direct observation in `.github`:

```text
carrier: ACTIVE epoch 31 / generation 31
worker runtime: CARRIER_REFERENCE_ONLY_NO_TASK_EXECUTION
fragment-aware engine_v13 source repair: installed
TVC broker assignment packet after repair: NOT OBSERVED
TVC broker worker binding/invocation: NOT OBSERVED
TVC broker validation receipt: NOT OBSERVED
```

Carrier continuity does not satisfy task-capable worker runtime proof.

## Completion inventory

```text
historical #93/#102 public credential-clean implementation: COMPLETE
legacy anonymous-private-source fanout repair: APPLIED
NON-TV/TVC credential substitution: NONE AUTHORIZED
private-source sovereign implementation in PR #141: SOURCE COMPLETE
TVC PR #79 broker source/control delta: COMPLETE SOURCE / NOT VALIDATED
TVC PR #79 governed validation receipt: NOT OBSERVED
TVC PR #79 canonical admission: NOT COMPLETE
StegCore PR #141 sovereign validation receipt: NOT OBSERVED
StegCore PR #141 merge: NOT COMPLETE
write-side evidence continuation #101: REMAINS DEPENDENT ON TV/TVC TRANSPORT
```

## Archive condition

Do not archive while required private-source validation, TVC admission, StegCore sovereign validation, downstream integration/release, runtime proof, or activation remains incomplete.

```text
DO NOT ARCHIVE THIS SESSION — REQUIRED EXECUTION REMAINS IN AN ACTIVE DEPENDENCY LANE.
```
