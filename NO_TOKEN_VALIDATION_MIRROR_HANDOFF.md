# StegCore No-Non-TV/TVC Validation Credential Mirror Handoff

## Source of truth

```text
organization: StegVerse-Labs
repository: StegCore
branch: fix/no-non-tvtvc-validation-credentials-001
goal_id: STEGCORE-NO-NON-TVTVC-VALIDATION-CREDENTIALS-001
issue: #93
pull_request: #102
parent_handoff: STEGCORE_MIRROR_HANDOFF.md
credential_authority: TV/TVC
non_TV_TVC_secret_or_token_allowed: false
archive_ready: false
```

This scoped handoff supplements the root StegCore handoff. It owns only credential-clean validation infrastructure and does not overlap issue #70 four-app runtime binding, canonical StegGate semantics, runtime activation, release/tag authority, or TV/TVC credential transport.

## Originating requirement

The strict session requirement is not merely that StegCore runtime code avoid credentials; validation itself must not use GitHub's automatically issued checkout token, `GH_TOKEN`, a PAT, provider credentials, wallet material, or any other NON-TV/TVC secret/token. StegCore is public, so validation source is fetched anonymously.

## Active claim

```text
task_id: STEGCORE-NO-NON-TVTVC-VALIDATION-CREDENTIALS-001
claimant: current ChatGPT formalism/manifold continuation session
role: CLAIMED_FOR_IMPLEMENTATION
claimed_at: 2026-08-14T11:20:00-05:00
expires_at: 2026-08-14T14:20:00-05:00
release: PR #102 merges after final-head credential-clean validation and write-side evidence persistence remains durably assigned to #101 / TV/TVC transport
```

## Installed scope

```text
NO_TOKEN_VALIDATION_MIRROR_HANDOFF.md
management/no-non-tvtvc-validation-credentials-claim.json
scripts/validate_no_non_tvtvc_validation_credentials.py
tests/test_no_non_tvtvc_validation_credentials.py
.github/workflows/stegcore-tests.yml
.github/workflows/runtime-tests.yml
.github/workflows/bcat-gate.yml
.github/workflows/test-readiness.yml
.github/workflows/stegverse-001-002-validator.yml
```

All five product validation workflows now use `permissions: {}`, contain no `uses:` actions, fetch the public repository anonymously with `git -c credential.helper= -c http.extraheader=`, use the runner's local `python3`, and explicitly fail if `GITHUB_TOKEN`, `GH_TOKEN`, `GITHUB_PAT`, or `TVC_EPHEMERAL_GITHUB_TOKEN` is present in the validation process environment.

The runtime gate no longer pushes evidence branches, creates/merges PRs, or reconciles issues using `GH_TOKEN=${{ github.token }}`. Durable write-side validation evidence continuation is separately recorded as StegCore #101 and must use the TV/TVC repository-operation transport after TVC #20 is canonically validated/admitted.

## Hosted validation evidence

Final functional branch head `591ee20af4699d1d8c4c761bdb7fc801d1c5c176` produced five credential-clean validation passes:

```text
StegCore Tests - No Non-TV/TVC Credential Authority
run: 31819521795 SUCCESS

Validate StegCore Runtime - No Non-TV/TVC Credential Authority
run: 31819521778 SUCCESS

BCAT Gate - No Non-TV/TVC Credential Authority
run: 31819521809 SUCCESS

Test Readiness - No Non-TV/TVC Credential Authority
run: 31819521770 SUCCESS

Validate StegVerse 001 002 Baseline - No Non-TV/TVC Credential Authority
run: 31819521765 SUCCESS
```

Each run reached and passed the explicit credential-environment assertion and anonymous source-fetch step. No project validation step consumed a GitHub/PAT/TVC credential. GitHub platform metadata may still describe its internal runner token context; this task's boundary is that no repository validation step receives, references, exports, or uses that credential.

The first attempted credential-clean runs exposed a toolchain-path bug in the branch's Python 3.11 locator. The branch repaired that by using the runner's preinstalled `python3`; credential assertions and anonymous fetch had already passed in the failed attempts. No validator or product test was weakened.

## Authority boundary

This task changes only validation transport and credential assertions. It does not change canonical StegGate policy, test expectations, product semantics, release/tag workflows, deployment, provider operations, wallet behavior, signing/broadcast, or TV/TVC credential custody.

## Validation commands

```text
python3 scripts/validate_no_non_tvtvc_validation_credentials.py
python3 -m unittest -q tests.test_no_non_tvtvc_validation_credentials
python3 -m pytest -q
```

## Cross-repository continuation

```text
credential-clean read-only validation: PR #102
write-side runtime validation evidence persistence: StegVerse-Labs/StegCore#101
transport dependency: StegVerse-Labs/TVC#19/#20
credential authority: TV/TVC
```

#101 is a real integration dependency, not an unspecified future task. Its release condition requires a passing credential-clean runtime validation to generate exact evidence content, TVC to apply that bounded content to an admitted evidence branch/open the persistence PR without exposing a credential to StegCore, and issue projection to be either separately admitted through TV/TVC or superseded by durable task/receipt state.

## Completion inventory

```text
required developed files: 9/9
scaffolding/stubs: 0
missing required files: 0
credential-clean hosted validation gates: 5/5 PASS
canonical merge: PENDING PR #102
issue/claim closure: PENDING merge
write-side evidence continuation: TRANSFERRED TO #101, execution pending TVC #20
```

## Archive condition

This scoped claim may be released after PR #102 merges and #93 is closed. The broader session remains non-archive-ready while trade activation, TVC broker activation, resident source generation, first-cohort reconciliation, generalized owner-mutation runtime proof, full recursive re-observation, or the TV/TVC-backed evidence-persistence continuation remain incomplete/untransferred to proven active executors.
