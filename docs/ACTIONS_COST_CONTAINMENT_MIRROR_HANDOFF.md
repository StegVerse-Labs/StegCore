# Actions Cost Containment Mirror Handoff

## Goal

- Goal ID: `STEGCORE-ACTIONS-COST-CONTAINMENT-001`
- Repository: `StegVerse-Labs/StegCore`
- Branch: `chore/actions-cost-containment-20260814`
- Coordination: `StegVerse-Labs/.github#164`
- Repository issue: `StegVerse-Labs/StegCore#125`
- Governing invariant: production/continuity execution must remain `StegVerse -> StegVerse -> StegVerse`; GitHub Actions is not a required production carrier.

## First containment batch

The following recurring GitHub-hosted hourly triggers are removed while preserving explicit/manual or repository-event validation paths:

- `.github/workflows/execution-orchestrator.yml`
- `.github/workflows/rtg-tt-task-observer.yml`
- `.github/workflows/steggate-live-observer.yml`
- `.github/workflows/steggate-session-continuity.yml`
- `.github/workflows/observe-correctability-site-admission.yml`
- `.github/workflows/personal-data-control-session-consolidation.yml`
- `.github/workflows/observe-and-advance-tidc-evidence-chain.yml`

These surfaces are classified as either recurring operational observation/advancement or periodic consolidation. Their recurring responsibility is a transfer candidate for StegVerse-controlled workers. GitHub remains available for bounded source-change validation and explicit diagnostics.

## Remaining workflow audit

StegCore currently exposes 51 active workflows. Code search identifies additional cron-bearing workflows that still require necessity classification before mutation, including:

- `stegva-bootstrap-verify.yml`
- `coordinate-hil-lifecycle.yml`
- `external-evidence-interop.yml`
- `validate-marketplace-coinbase-session-consolidation.yml`
- `runtime-tests.yml`
- any other cron-bearing workflow discovered by the repository census

Classification states:

- `KEEP_GITHUB_VALIDATION`: necessary repository/CI behavior; recurring trigger justified only by evidence.
- `TRANSFER_TO_STEGVERSE_WORKER`: necessary operational work, but recurring execution must move to a StegVerse-controlled worker/runtime.
- `ELIMINATE`: redundant, superseded, completed, or unnecessary workflow.

## Repository hygiene

Open issue/PR/branch cleanup is coordinated by `StegVerse-Labs/.github#165`. Destructive cleanup must preserve active claims, current handoffs, protected/release branches, evaluation snapshots, and evidence references. Exact duplicates and superseded automation artifacts should be closed/removed in bounded batches.

## Validation / release condition

This first batch is complete when:

1. the seven workflow changes are reviewed and merged;
2. no removed schedule is required for current StegVerse production continuity;
3. equivalent necessary recurring work is registered as a StegVerse-worker transfer candidate where applicable;
4. the remaining 44 workflow surfaces are classified;
5. stale/duplicate issues, PRs, and branches are reconciled without deleting active work.

## Current state

`ACTIVE_REMEDIATION / FIRST_CONTAINMENT_BATCH_IMPLEMENTED / FULL_CENSUS_PENDING`
