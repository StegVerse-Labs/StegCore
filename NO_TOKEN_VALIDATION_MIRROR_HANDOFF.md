# StegCore No-Non-TV/TVC Validation Credential Mirror Handoff

## Source of truth

```text
organization: StegVerse-Labs
repository: StegCore
branch: feat/ae-manifest-capability-context-v1
goal_id: STEGCORE-NO-NON-TVTVC-VALIDATION-CREDENTIALS-001
historical_issue: #93 (CLOSED COMPLETED)
historical_pull_request: #102 (MERGED)
private_source_followup_pull_request: #141
private_source_followup_task: tasks/STEGCORE-SOVEREIGN-PRIVATE-SOURCE-VALIDATION-003.json
parent_handoff: STEGCORE_MIRROR_HANDOFF.md
credential_authority: TV/TVC
non_TV_TVC_secret_or_token_allowed: false
archive_ready: false
```

This scoped handoff owns credential-clean validation transport semantics only. It does not own canonical StegGate policy, runtime activation, release/tag authority, wallet authority, or TV/TVC credential custody.

## Historical completion before privatization

Issue #93 and PR #102 completed the original public-repository credential-clean validation objective. Those historical passes remain historical evidence only; they are not evidence that anonymous fetch works after repository privatization.

StegCore is private. No response to privatization may silently restore `GITHUB_TOKEN`, `GH_TOKEN`, a PAT, provider credential, or any other NON-TV/TVC secret/token to StegCore validation.

## Applied private-repository fanout repair

Main commit `3b10620843a650224e18a7aac1e402b684becbf2` stopped six legacy anonymous-private automatic validation paths from producing misleading fanout. That repair introduced no replacement PASS and no credential path.

## Canonical private-source validation continuation

PR #141 installs:

```text
scripts/run_private_source_validation_via_tvc.py
scripts/run_sovereign_validation.py
tasks/STEGCORE-SOVEREIGN-PRIVATE-SOURCE-VALIDATION-003.json
.github/workflows/sovereign-private-source-validation.yml  # optional bridge only
```

The canonical bridge emits a bounded non-secret `MATERIALIZE_SOURCE_ARCHIVE` warrant to TVC, waits for a sanitized TVC receipt, verifies exact source identity, then runs the sovereign validator against the materialized source. `GITHUB_TOKEN`, `GH_TOKEN`, `GITHUB_PAT`, and `TVC_EPHEMERAL_GITHUB_TOKEN` remain forbidden in the StegCore validation process.

PR #141 source identity must be re-resolved from the live PR immediately before materialization and bound to the sovereign validation receipt. Any earlier PR #141 SHA is discovery evidence only after the branch moves.

## Upstream TVC dependency

The canonical repository-operation broker admission target is now:

```text
StegVerse-Labs/TVC PR #92
TVC-GITHUB-REPOSITORY-OPERATION-BROKER-001
expected governed PR #92 head: 4e87ad9f3a859ab3b18241640624abd5e1757002
superseded unmerged PRs: #20, #79

StegVerse-Labs/.github
handoffs/SHWP-TVC-REPOSITORY-BROKER-VALIDATION-001.json
workers/tvc_repository_broker_validation_worker.py
receipt target:
receipts/tvc-repository-broker-validation/SHWP-TVC-REPOSITORY-BROKER-VALIDATION-001.json
```

PR #79 was 122+ commits behind current TVC main and non-mergeable; it was closed without merge. PR #92 carries exactly 16 broker source/control/test files. Governed PASS binds the exact tested PR head plus the complete 16-file `source_bundle_sha256`. Later unrelated movement of TVC `main` does not change that tested source identity; integration must rematerialize the identical digest and perform current-base compatibility review.

Heartbeat progression is not a validation trigger or dependency. The broker validation is a separate task-control/runtime lane. No heartbeat state, carrier epoch, missed observation, or assignment packet authorizes, delays, suppresses, or advances the validation.

The required upstream release condition is:

```text
1. exact clean TVC PR #92 source at 4e87ad9f3a859ab3b18241640624abd5e1757002 is locally materialized on a StegVerse-controlled validation surface;
2. python tools/task_dispatcher.py tvc.github_repository_operation_broker.verify executes;
3. dispatcher status=ok and nested result.result=PASS;
4. consumer_credential_used=false;
5. tvc_github_credential_used=false;
6. non_tv_tvc_secret_or_token_used=false;
7. protected_value_disclosure=false;
8. the retained validation receipt binds that exact PR #92 head, `source_bundle_file_count=16`, and a 64-character `source_bundle_sha256`;
9. if TVC main moved, the identical 16-file digest is rematerialized and current-base compatibility passes; TVC PR #92/broker bundle is then canonically admitted;
10. StegCore exact PR #141 source is re-resolved/materialized and sovereign validation executes against that then-current exact head.
```

## Integration compatibility rule

A sovereign validation PASS is bound to the exact tested PR #141 head. It does not override current-base compatibility. Immediately before merge, repository integration authority must verify that the exact validated head is still admissible against current `main`. If resolving base drift changes any validated source byte or changes the PR head, the resulting head must be re-materialized and revalidated before merge. Moving `main`, mergeability, or a merge preview never substitutes for the exact sovereign PASS.

## Separate generalized private-source-read capability

TVC main also carries `TVC-PRIVATE-SOURCE-READ-001` / `tvc.private-source-read.v1`. It is useful for exact private reads but remains a separate capability and does not satisfy broker admission or StegCore validation merely by existing.

## Validation commands after materialization

PR #141 requires the sovereign validation receipt to cover:

```text
python3 -m pytest -q tests/test_manifest_capability_context.py
python3 -m pytest -q tests/test_transaction_lifecycle.py tests/test_manifest_receipts.py tests/test_manifest_receipt_provider.py
python3 -m pytest -q
python3 scripts/verify_product_consistency.py
```

## Current completion inventory

```text
original #93/#102 credential-clean public validation implementation: COMPLETE
legacy anonymous private-source failure fanout repair: APPLIED
NON-TV/TVC credential substitution: NONE AUTHORIZED
private-source sovereign implementation in PR #141: SOURCE COMPLETE
TVC PR #92 broker validation target: 4e87ad9f3a859ab3b18241640624abd5e1757002
TVC PR #92 governed validation receipt: NOT OBSERVED
TVC PR #92 canonical admission: NOT COMPLETE
StegCore PR #141 exact-head sovereign validation receipt: NOT OBSERVED
StegCore PR #141 merge: NOT COMPLETE
write-side evidence continuation #101: REMAINS DEPENDENT ON TV/TVC TRANSPORT
```

## Continuity and archive semantics

The **StegCore validation project lane remains ACTIVE / BLOCKED** while the required private-source validation chain is machine-owned, blocked, unvalidated, unreleased, not deployed, or not activated. Those states remain nonterminal for the project.

The ChatGPT session is not part of the validation chain. Continuation is durable in this handoff, `tasks/STEGCORE-SOVEREIGN-PRIVATE-SOURCE-VALIDATION-003.json`, PR #141, and the upstream TVC/.github handoffs. After global coordination capture, session archival does not imply validation, merge, release, deployment, activation, or completion.

```text
project_lifecycle: ACTIVE / BLOCKED
chat_session_required: false
```
