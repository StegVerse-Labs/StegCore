# StegCore No-Non-TV/TVC Validation Credential Mirror Handoff

## Canonical authority

```text
organization: StegVerse-Labs
repository: StegCore
goal_id: STEGCORE-NO-NON-TVTVC-VALIDATION-CREDENTIALS-001
original_issue: #93 CLOSED_COMPLETE_FOR_PUBLIC_REPOSITORY_MODE
current_private_source_task: tasks/STEGCORE-SOVEREIGN-PRIVATE-SOURCE-VALIDATION-003.json
current_ae_validation_task: tasks/STEGCORE-AE-MANIFEST-CAPABILITY-CONTEXT-VALIDATION-002V.json
current_ae_pull_request: #141
credential_authority: TV/TVC
non_TV_TVC_secret_or_token_allowed: false
render_required: false
```

This handoff owns credential-clean validation transport only. It does not grant StegGate, release, merge, provider, wallet, signing, broadcast, or runtime authority.

## Historical public-source mode

Issue #93 / PR #102 correctly removed GitHub checkout-token use while StegCore was public. Five hosted validation workflows used `permissions: {}`, no `uses:` actions, explicit credential absence checks, and anonymous public `git fetch`. Historical runs 31819521795, 31819521778, 31819521809, 31819521770, and 31819521765 passed that mode.

That evidence remains valid for the repository state observed at the time. It is not evidence that anonymous fetch remains possible now.

## Visibility transition / supersession

Current repository inspection reports:

```text
StegVerse-Labs/StegCore visibility: private
```

Therefore the sentence "StegCore is public, so validation source is fetched anonymously" is superseded. Anonymous GitHub-hosted fetch is no longer a valid source-materialization mechanism for current private StegCore validation.

Observed PR #141 hosted runs correctly passed the no-credential environment check, then failed before code-test execution at `Anonymous public repository fetch`. No implementation PASS or code-test failure may be inferred from those runs.

## Canonical private-source validation path

Private-source validation now uses a StegVerse-controlled local source boundary:

```text
TV/TVC-owned repository source materialization
-> exact private StegCore commit materialized locally
-> credential value remains inside TV/TVC transport
-> validation process receives no repository credential
-> scripts/run_sovereign_validation.py verifies exact HEAD + clean worktree
-> focused AE tests
-> transaction/receipt regressions
-> full pytest
-> product-consistency verifier
-> validation/sovereign-validation.latest.json
```

Installed on PR #141:

```text
scripts/run_sovereign_validation.py
.github/workflows/sovereign-private-source-validation.yml
tasks/STEGCORE-SOVEREIGN-PRIVATE-SOURCE-VALIDATION-003.json
```

The sovereign runner refuses `GITHUB_TOKEN`, `GH_TOKEN`, `GITHUB_PAT`, and `TVC_EPHEMERAL_GITHUB_TOKEN` in the validation process. It performs no network source fetch and accepts only an already materialized exact source HEAD with a clean worktree.

## TVC source-materialization owner

Do not create a StegCore credential path. The existing canonical implementation is:

```text
StegVerse-Labs/TVC PR #20
TVC-GITHUB-REPOSITORY-OPERATION-BROKER-001
operation: MATERIALIZE_SOURCE_ARCHIVE
policy materialization root: /var/lib/stegverse/source
allowed repository: StegVerse-Labs/StegCore
credential authority: TV/TVC
consumer credential allowed: false
```

TVC PR #20 explicitly implements safe source-archive materialization using the TVC-managed ephemeral GitHub credential without exposing the credential to the consumer/validator. Until that broker is admitted/released on its canonical TVC lane, current private-source validation is `BLOCKED_ON_CANONICAL_TVC_SOURCE_MATERIALIZATION_RELEASE`, not blocked on a missing StegCore test implementation.

## Authority and collision boundaries

```text
no Render
no GitHub-generated checkout token in StegCore validation
no GH_TOKEN / PAT / provider / wallet credential in validation
no direct private-repository fetch credential in StegCore
no weakening tests to obtain a green workflow
no duplicate repository-operation broker outside TVC
GitHub-hosted validation: optional validation infrastructure only, never runtime/control-plane authority
```

## Current validation command

On a StegVerse-controlled node with exact source already materialized:

```text
python3 scripts/run_sovereign_validation.py \
  --source-root <EXACT_LOCAL_STEGCORE_ROOT> \
  --expected-head <EXACT_PR_HEAD> \
  --receipt-out validation/sovereign-validation.latest.json
```

The runner itself executes:

```text
python3 -m pytest -q tests/test_manifest_capability_context.py
python3 -m pytest -q tests/test_transaction_lifecycle.py tests/test_manifest_receipts.py tests/test_manifest_receipt_provider.py
python3 -m pytest -q
python3 scripts/verify_product_consistency.py
```

## Durable continuation

```text
StegVerse-Labs/StegCore#141
-> tasks/STEGCORE-SOVEREIGN-PRIVATE-SOURCE-VALIDATION-003.json
-> StegVerse-Labs/TVC#20 source materialization authority
-> exact local validation receipt
-> PR #141 merge only after PASS
-> issue #85 / SDK #16 / LLM-adapter #139 continuation
```

The old public-anonymous validation mode is historical fallback only if repository visibility is deliberately public again. It is not the current canonical path.
