# StegCore No-Non-TV/TVC Validation Credential Mirror Handoff

## Source of truth

```text
organization: StegVerse-Labs
repository: StegCore
branch: fix/no-non-tvtvc-validation-credentials-001
goal_id: STEGCORE-NO-NON-TVTVC-VALIDATION-CREDENTIALS-001
issue: #93
parent_handoff: STEGCORE_MIRROR_HANDOFF.md
credential_authority: TV/TVC
non_TV_TVC_secret_or_token_allowed: false
archive_ready: false
```

This scoped handoff supplements the root StegCore handoff. It owns only credential-clean validation infrastructure and does not overlap issue #70 four-app runtime binding, canonical StegGate semantics, runtime activation, release/tag authority, or TV/TVC credential transport.

## Originating requirement

The strict session requirement is not merely that StegCore runtime code avoid credentials; validation itself must not use GitHub's automatically issued checkout token, `GH_TOKEN`, a PAT, provider credentials, wallet material, or any other NON-TV/TVC secret/token. StegCore is public, so validation source can be fetched anonymously.

## Active claim

```text
task_id: STEGCORE-NO-NON-TVTVC-VALIDATION-CREDENTIALS-001
claimant: current ChatGPT formalism/manifold continuation session
role: CLAIMED_FOR_IMPLEMENTATION
claimed_at: 2026-08-14T11:20:00-05:00
expires_at: 2026-08-14T14:20:00-05:00
release: target validation workflows are credential-clean, hosted validation passes, changes merge, and any removed write-side persistence is transferred to TV/TVC-owned transport
```

## Scope

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

## Validation contract

All five product-validation gates must:

- use `permissions: {}`;
- use no `uses:` action requiring GitHub credential transport;
- fetch the public repository anonymously with `git` over HTTPS;
- never reference `github.token`, `secrets.*`, `GITHUB_TOKEN`, `GH_TOKEN`, `GITHUB_PAT`, or `TVC_EPHEMERAL_GITHUB_TOKEN` as a credential source;
- explicitly fail if credential-bearing environment variables are present in the test process;
- use the runner's local Python rather than `actions/setup-python`;
- retain their existing validation commands/semantics.

`runtime-tests.yml` currently also performs write-side evidence PR and issue reconciliation using `GH_TOKEN=${{ github.token }}`. Those write operations cannot remain under the strict credential rule. This task preserves read-only validation and moves durable write-side continuation to the TV/TVC repository-operation transport rather than replacing it with another token.

## Authority boundary

This task may change only validation transport and credential assertions. It may not change canonical StegGate policy, test expectations, product semantics, release/tag workflows, deployment, provider operations, wallet behavior, signing/broadcast, or TV/TVC credential custody.

## Validation commands

```text
python scripts/validate_no_non_tvtvc_validation_credentials.py
python -m unittest -q tests.test_no_non_tvtvc_validation_credentials
pytest -q
```

## Integration obligation

If write-side validation evidence persistence remains required after credential-clean validation, it must be executed through TV/TVC-owned bounded repository operations after `StegVerse-Labs/TVC#20` is canonically validated/admitted. No GitHub-generated credential may be reintroduced as a shortcut.

## Archive condition

This scoped claim may be released after merge and durable transfer of any remaining write-side evidence persistence. The broader session remains non-archive-ready while trade activation, TVC broker activation, resident source generation, first-cohort reconciliation, generalized owner-mutation runtime proof, or full recursive re-observation remain incomplete/untransferred.
