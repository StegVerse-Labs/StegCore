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
parent_handoff: STEGCORE_MIRROR_HANDOFF.md
credential_authority: TV/TVC
non_TV_TVC_secret_or_token_allowed: false
archive_ready: false
```

This scoped handoff owns credential-clean validation transport semantics only. It does not own canonical StegGate policy, issue #70 four-app runtime binding, runtime activation, release/tag authority, wallet authority, or TV/TVC credential custody.

## Historical completion before privatization

Issue #93 and PR #102 completed the original public-repository validation objective. Five core validation gates were converted away from `actions/checkout`, GitHub-generated checkout credentials, `GH_TOKEN`, PATs, and other NON-TV/TVC credential paths. Historical branch head `591ee20af4699d1d8c4c761bdb7fc801d1c5c176` produced five credential-clean hosted validation passes while StegCore was public:

```text
StegCore Tests: 31819521795 SUCCESS
Runtime Validation: 31819521778 SUCCESS
BCAT Gate: 31819521809 SUCCESS
Test Readiness: 31819521770 SUCCESS
001/002 Baseline: 31819521765 SUCCESS
```

Those passes remain valid historical evidence for the public-source configuration. They are not evidence that anonymous fetch works after repository privatization.

## Visibility transition

StegCore is now private. The prior anonymous-source premise is therefore no longer valid.

The first private-repository failure mode was transport-only: credential absence assertions passed, then anonymous `git fetch` could not materialize the private source. Such runs are neither product-code PASS nor product-code failure.

No response to privatization may silently restore `GITHUB_TOKEN`, `GH_TOKEN`, a PAT, provider credential, or any other NON-TV/TVC secret/token to StegCore validation.

## Applied noise/fanout repair on main

Commit:

```text
3b10620843a650224e18a7aac1e402b684becbf2
ci: stop legacy anonymous validation fanout on private StegCore
```

applied the bounded private-repository transition to six legacy public-anonymous workflows:

```text
.github/workflows/bcat-gate.yml
.github/workflows/portable-release-candidate.yml
.github/workflows/runtime-tests.yml
.github/workflows/stegcore-tests.yml
.github/workflows/stegverse-001-002-validator.yml
.github/workflows/test-readiness.yml
```

The automatic `pull_request` fanout that could not validate private source was removed from those public-anonymous paths, and their remaining public-mode jobs are guarded with `github.event.repository.private == false`.

This repair intentionally produces no replacement PASS and introduces no credential path. It stops known-invalid anonymous-private-source runs while preserving the credential boundary.

## Canonical private-source validation continuation

PR #141 installs the StegVerse-native private-source validation path without exposing repository credentials to StegCore:

```text
scripts/run_private_source_validation_via_tvc.py
scripts/run_sovereign_validation.py
tasks/STEGCORE-SOVEREIGN-PRIVATE-SOURCE-VALIDATION-003.json
.github/workflows/sovereign-private-source-validation.yml  # optional bridge only
```

The canonical bridge emits a bounded non-secret `MATERIALIZE_SOURCE_ARCHIVE` warrant to TVC, waits for a sanitized TVC receipt, verifies exact source identity, then runs the sovereign validator against the materialized source. `GITHUB_TOKEN`, `GH_TOKEN`, `GITHUB_PAT`, and `TVC_EPHEMERAL_GITHUB_TOKEN` remain forbidden in the StegCore validation process.

Current exact PR #141 head at this reconciliation:

```text
c8cfe486632415c91e3fe2a39f7aac3d82af33e9
```

The required sovereign receipt remains unobserved. PR #141 must not merge solely because obsolete hosted checks are absent/skipped or because source files are complete.

## Upstream machine-owned dependency

The current private-source path depends on the existing TVC repository-operation broker and its StegVerse-controlled validation carrier:

```text
StegVerse-Labs/TVC PR #20
TVC-GITHUB-REPOSITORY-OPERATION-BROKER-001
expected PR #20 head: 6209396bc9846ec5f301b24d3b6f0207e571af1d

StegVerse-Labs/.github
handoffs/SHWP-TVC-REPOSITORY-BROKER-VALIDATION-001.json
workers/tvc_repository_broker_validation_worker.py
receipt target:
receipts/tvc-repository-broker-validation/SHWP-TVC-REPOSITORY-BROKER-VALIDATION-001.json
```

The worker is bound for validation-only execution and grants no credential or merge authority. The required carrier receipt has not yet been observed. Durable handoff, `HANDOFF_READY`, machine ownership, or source completion do not satisfy the release condition.

The machine-observable upstream release condition is:

```text
1. exact clean TVC PR #20 source is locally materialized on a StegVerse-controlled carrier;
2. python tools/task_dispatcher.py tvc.github_repository_operation_broker.verify executes;
3. dispatcher status=ok and nested result.result=PASS;
4. consumer_credential_used=false;
5. tvc_github_credential_used=false;
6. non_tv_tvc_secret_or_token_used=false;
7. protected_value_disclosure=false;
8. the carrier receipt records COMPLETED for exact PR #20 head;
9. TVC PR #20 is canonically admitted;
10. StegCore exact PR #141 source is materialized and sovereign validation executes against its then-current exact head.
```

## Separate generalized private-source-read capability

TVC main also carries `TVC-PRIVATE-SOURCE-READ-001` / `tvc.private-source-read.v1` for generalized exact private repository reads. That capability is currently `BLOCKED_DEPENDENCY_MACHINE_OWNED` and is not a completed substitute for the PR #20 broker path. No generic GitHub credential substitution is authorized.

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
original issue #93: CLOSED COMPLETED
original PR #102: MERGED
legacy anonymous private-source failure fanout repair on main: APPLIED @ 3b10620843a650224e18a7aac1e402b684becbf2
NON-TV/TVC credential substitution: NONE AUTHORIZED
private-source sovereign implementation in PR #141: SOURCE COMPLETE
TVC PR #20 broker validation carrier receipt: NOT OBSERVED
TVC PR #20 canonical admission: NOT COMPLETE
StegCore PR #141 exact-head sovereign validation receipt: NOT OBSERVED
StegCore PR #141 merge: NOT COMPLETE
write-side evidence continuation #101: REMAINS DEPENDENT ON TV/TVC TRANSPORT
```

## Archive condition

Do not archive this workstream while the required private-source validation chain remains machine-owned, blocked, unvalidated, unreleased, or not activated. Historical public-source success and the applied fanout repair do not satisfy private-source activation.

Current status:

```text
DO NOT ARCHIVE THIS SESSION — REQUIRED EXECUTION REMAINS IN AN ACTIVE DEPENDENCY LANE.
```
