# Actions Cost Containment Mirror Handoff

## Goal

- Goal ID: `STEGCORE-ACTIONS-COST-CONTAINMENT-001`
- Repository: `StegVerse-Labs/StegCore`
- Canonical branch: `main`
- Coordination: `StegVerse-Labs/.github#164`
- Workflow minimization policy: `StegVerse-Labs/.github#167`
- Repository issues: `StegVerse-Labs/StegCore#125`, `StegVerse-Labs/StegCore#128`
- Governing invariant: production/continuity execution must remain `StegVerse -> StegVerse -> StegVerse`; GitHub Actions is not a required production carrier.
- Credential invariant: no NON-TV/TVC secret or token may be introduced; production/control-plane credential authority remains TV/TVC.
- Preferred GitHub workflow surface: minimum technically necessary; `0/1/2` preferred, `>2` only by evidence-backed standalone exception.

## Completed containment batch 1

Merged by PR #126 at merge commit `42ac77b7b1e12d72b9a6e9763c150c317573354e`.

Recurring GitHub-hosted schedules were removed while explicit/manual or repository-event validation paths were preserved for:

- `.github/workflows/execution-orchestrator.yml`
- `.github/workflows/rtg-tt-task-observer.yml`
- `.github/workflows/steggate-live-observer.yml`
- `.github/workflows/steggate-session-continuity.yml`
- `.github/workflows/observe-correctability-site-admission.yml`
- `.github/workflows/personal-data-control-session-consolidation.yml`
- `.github/workflows/observe-and-advance-tidc-evidence-chain.yml`

The recurring responsibility of these operational observers/orchestrators is not a GitHub production dependency. Necessary recurring behavior belongs to StegVerse-controlled workers; GitHub is retained for bounded source-change validation and explicit diagnostics.

## Completed containment batch 2

Merged by PR #127 at merge commit `f410a6d2a71f19742f1110c5c5eeff5404a8f821`.

The following five additional recurring schedules were removed while preserving push, pull-request, or explicit/manual validation paths as applicable:

- `.github/workflows/stegva-bootstrap-verify.yml` — daily bootstrap/session verification is redundant with source-change/manual validation; `KEEP_GITHUB_VALIDATION` for event/manual use, recurring trigger eliminated.
- `.github/workflows/coordinate-hil-lifecycle.yml` — periodic lifecycle observation/coordination is operational work; recurring ownership is `TRANSFER_TO_STEGVERSE_WORKER`, GitHub retained for source-change/manual validation.
- `.github/workflows/external-evidence-interop.yml` — daily full-suite revalidation of a pinned snapshot is unnecessary; `KEEP_GITHUB_VALIDATION` for source-change/manual use, recurring trigger eliminated.
- `.github/workflows/runtime-tests.yml` — daily full runtime validation is unnecessary because source changes already trigger the validation and production authority is none; `KEEP_GITHUB_VALIDATION` for source-change/manual use, recurring trigger eliminated.
- `.github/workflows/validate-marketplace-coinbase-session-consolidation.yml` — periodic consolidation receipt generation is operational/reconciliation work; recurring ownership is `TRANSFER_TO_STEGVERSE_WORKER`, GitHub retained for source-change/manual validation.

No NON-TV/TVC secret/token was added by this batch.

## Completed workflow-surface minimization batch 1

Merged by PR #129 at merge commit `8e2f451d49b1ca14bc4ea8678b4dd5aaa8de14fd`.

This batch begins reducing workflow *file count*, not merely cron frequency. Two dedicated validation workflows were consolidated into the existing credential-clean `runtime-tests.yml` dispatcher:

- `.github/workflows/check-tidc-evidence-chain-management.yml` -> `runtime-tests.yml`
  - preserves `scripts/check_tidc_evidence_chain_management.py` compile + deterministic validation;
  - removes the separate 3-version runner matrix, including unsupported Python 3.9 (`pyproject.toml` requires Python >=3.11).
- `.github/workflows/criterion-contestability-validate.yml` -> `runtime-tests.yml`
  - preserves `scripts/validate_criterion_contestability_boundary.py` and the full runtime test suite that already includes `tests/test_criterion_contestability.py`.

The stable runtime validator includes the relevant TIDC registry and criterion contract paths in its push/PR trigger set. No third-party action or credential path was added.

Post-merge GitHub Actions API observation reports `total_count: 49`, confirming the workflow-file count fell from 51 to 49.

Classification: both removed files are `CONSOLIDATE_INTO_STABLE_DISPATCHER`, not capability eliminations.

## Current quantitative state

- workflow surfaces at audit start: 51
- current workflow files: 49
- recurring schedules removed in containment batches: 12
- workflow files consolidated/eliminated in minimization batch 1: 2
- workflow surfaces explicitly classified/remediated: 14/51
- remaining surfaces requiring KEEP_STANDALONE_EXCEPTION / CONSOLIDATE / TRANSFER / ELIMINATE classification: 37

The classification denominator is the 51 workflow surfaces present at audit start. Schedule removal alone does not reduce workflow-file count; consolidation/elimination does.

## Classification states

- `KEEP_GITHUB_VALIDATION`: necessary repository/CI behavior retained during interim containment.
- `KEEP_STANDALONE_EXCEPTION`: workflow must remain standalone because a concrete technical/authority requirement prevents safe consolidation; evidence required.
- `CONSOLIDATE_INTO_STABLE_DISPATCHER`: useful GitHub-bound behavior retained behind the minimum stable workflow doorway.
- `TRANSFER_TO_STEGVERSE_WORKER`: necessary operational work whose recurring execution belongs to a StegVerse-controlled worker/runtime.
- `ELIMINATE`: redundant, superseded, completed, or unnecessary workflow/capability surface.

## Local runtime / formal model convergence

This cost-containment work does not reopen or duplicate the already-complete local-runtime implementation. Organization source of truth records:

- formal local model: `COMPLETE_RELEASED`;
- local runtime discovery/launch/inference/proof: `COMPLETE_RELEASED`;
- descriptive `select a local model/runtime` step: `SUPERSEDED`;
- local-model credential requirement: `NONE`;
- credential authority: `TV/TVC`;
- GitHub token production authority: `NONE`.

Canonical continuation is `StegVerse-Labs/.github/docs/ORG_MIRROR_HANDOFF.md` plus `StegVerse-002/micro-node-runtime/docs/SOVEREIGN_LOCAL_MODEL_RUNTIME_MIRROR_HANDOFF.md`. Remaining live carrier activation is worker-owned and must not be duplicated by this remediation lane.

## Repository hygiene

Open issue/PR/branch cleanup is coordinated by `StegVerse-Labs/.github#165`. Destructive cleanup must preserve active claims, current handoffs, protected/release branches, evaluation snapshots, and evidence references. Exact duplicates and superseded automation artifacts should be closed/removed in bounded batches.

Known completed hygiene in this workstream:

- duplicate issue #30 closed in favor of #29;
- duplicate issue #32 closed in favor of #31.

## Active claims / collision boundary

- cost containment implementation: issue #125 and subsequent bounded remediation branches;
- workflow minimization implementation: issue #128 under organization policy #167;
- live sovereign runtime activation: resident StegVerse workers under `.github` handoff/registry — observation only from this session;
- local model implementation: complete/released — no competing implementation claim permitted;
- TV/TVC credential/route authority: TV/TVC only.

## Validation / release condition

Containment batches 1 and 2 and workflow minimization batch 1 are complete and merged.

Full goal completion requires classification of all 51 audit-start surfaces, reduction to the minimum safe workflow count (preferably <=2), evidence-backed exceptions for any retained standalone workflows above that minimum, and bounded issue/PR/branch reconciliation without deleting active evidence or claims.

## Current state

`ACTIVE_REMEDIATION / CONTAINMENT_BATCHES_1_2_MERGED / WORKFLOW_MINIMIZATION_BATCH_1_MERGED / CURRENT_WORKFLOW_COUNT_49 / FULL_CENSUS_PENDING`

## Session consolidation

The local-model/runtime and trade-readiness requirements are durably transferred to the canonical organization/runtime worker chain. This session retains unique value for repository cost-containment, workflow-surface minimization, and hygiene implementation until those mutations and continuation records are transferred.
