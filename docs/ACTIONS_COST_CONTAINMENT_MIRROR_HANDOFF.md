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

Necessary recurring behavior belongs to StegVerse-controlled workers; GitHub is retained only for bounded source-change validation and explicit diagnostics.

## Completed containment batch 2

Merged by PR #127 at merge commit `f410a6d2a71f19742f1110c5c5eeff5404a8f821`.

Recurring schedules were removed from:

- `.github/workflows/stegva-bootstrap-verify.yml`
- `.github/workflows/coordinate-hil-lifecycle.yml`
- `.github/workflows/external-evidence-interop.yml`
- `.github/workflows/runtime-tests.yml`
- `.github/workflows/validate-marketplace-coinbase-session-consolidation.yml`

Source-change/manual validation remains where useful. Operational recurrence is a StegVerse-worker responsibility. No NON-TV/TVC secret/token was added.

## Completed workflow-surface minimization batch 1

Merged by PR #129 at merge commit `8e2f451d49b1ca14bc4ea8678b4dd5aaa8de14fd`.

Two dedicated validation workflows were consolidated into the credential-clean `runtime-tests.yml` dispatcher:

- `.github/workflows/check-tidc-evidence-chain-management.yml` -> `runtime-tests.yml`
- `.github/workflows/criterion-contestability-validate.yml` -> `runtime-tests.yml`

Post-merge GitHub Actions observation reported `total_count: 49`.

The consolidation exposed a stale TIDC v0.1 validator. PR #130 repaired it to current v0.2 semantics; final validation run `31864882005` passed and PR #130 merged at `e1bf1a35fe42c0c43e2143887d27fcc9544f303e`.

## Workflow-surface minimization batch 2 — implementation pending hosted validation

Branch: `chore/workflow-surface-minimization-002`.

Two additional bounded validation surfaces are consolidated into the existing credential-clean `runtime-tests.yml` dispatcher:

- `.github/workflows/governed-runtime-adapters.yml` -> `runtime-tests.yml`
  - preserves Python compilation of `runtime.py` / `runtime_adapters.py`;
  - preserves governed adapter conformance/reconciliation tests and runtime commit-coherence test;
  - preserves the static no-direct-`executor()` bypass assertion.
- `.github/workflows/originating-choice-validate.yml` -> `runtime-tests.yml`
  - preserves canonical originating-choice schema validation, fail-closed self-tests, consumer routing and consumer self-tests;
  - generates the same four deterministic receipt JSON files ephemerally and prints their SHA-256 values;
  - adds `tools/**`, `spec/**`, and originating-choice example paths to stable dispatcher triggers.

The stable dispatcher remains `permissions: {}`, rejects exposed GitHub/GH/PAT/TVC-ephemeral credential variables, acquires repository source anonymously, and grants no production/runtime authority. No NON-TV/TVC secret or token is introduced.

Classification: both standalone files are `CONSOLIDATE_INTO_STABLE_DISPATCHER`, not capability eliminations.

Expected post-merge workflow count: `47`, subject to direct API observation after all final-head validations pass.

Release conditions for batch 2:

1. exact PR diff contains only stable-dispatcher consolidation, the two standalone workflow deletions, and this handoff update;
2. `runtime-tests.yml` passes on the final PR head;
3. adapter and originating-choice validation steps are observed PASS inside the stable dispatcher;
4. no NON-TV/TVC credential path or GitHub production authority is introduced;
5. merge completes and direct Actions API reports workflow count `47`;
6. issue #128 receives the merge/run/count evidence.

## Current quantitative state

- workflow surfaces at audit start: 51
- current workflow files on canonical `main`: 49
- recurring schedules removed in containment batches: 12
- workflow files consolidated/eliminated on `main`: 2
- workflow surfaces explicitly classified/remediated on `main`: 14/51
- batch 2 proposed additional consolidations: 2
- expected after batch 2 merge: current workflow files 47; classified/remediated 16/51; remaining classification denominator 35/51

Schedule removal alone does not reduce workflow-file count; consolidation/elimination does.

## Classification states

- `KEEP_GITHUB_VALIDATION`: necessary repository/CI behavior retained during interim containment.
- `KEEP_STANDALONE_EXCEPTION`: standalone only with concrete technical/authority evidence.
- `CONSOLIDATE_INTO_STABLE_DISPATCHER`: useful GitHub-bound behavior retained behind the minimum stable workflow doorway.
- `TRANSFER_TO_STEGVERSE_WORKER`: necessary operational work whose recurring execution belongs to a StegVerse-controlled worker/runtime.
- `ELIMINATE`: redundant, superseded, completed, or unnecessary workflow/capability surface.
- `REVIEW_REQUIRED`: ownership/drift prevents safe disposition until the canonical owner reconciles it.

## Local runtime / formal model convergence

Do not reopen or duplicate the released local-runtime implementation:

- formal local model: `COMPLETE_RELEASED`;
- local runtime discovery/launch/inference/proof: `COMPLETE_RELEASED`;
- descriptive `select a local model/runtime` step: `SUPERSEDED`;
- local-model credential requirement: `NONE`;
- credential authority: `TV/TVC`;
- GitHub token production authority: `NONE`.

Canonical continuation is `StegVerse-Labs/.github/docs/ORG_MIRROR_HANDOFF.md` plus `StegVerse-002/micro-node-runtime/docs/SOVEREIGN_LOCAL_MODEL_RUNTIME_MIRROR_HANDOFF.md`. Live carrier activation is worker-owned.

## StegFin convergence

Trade-readiness execution is not owned by this cleanup branch. Canonical continuation remains `StegVerse-Labs/stegfin-governance/docs/STEGFIN_MIRROR_HANDOFF.md` and `STEGFIN-CONTINUITY-CARRIER-007`; manual provider/wallet execution is prohibited, credential authority is TV/TVC, and signing/broadcast remain USER_ONLY.

## Repository hygiene

Issue/PR/branch cleanup is coordinated by `StegVerse-Labs/.github#165`. Destructive cleanup must preserve active claims, current handoffs, protected/release branches, evaluation snapshots, unique commits and evidence references.

Known completed hygiene:

- duplicate issue #30 closed in favor of #29;
- duplicate issue #32 closed in favor of #31.

Open legacy PRs require reconciliation rather than age-based closure. In particular PR #27 contains unique evaluator work but also proposes scheduled GitHub-hosted write workflows, `STEGVERSE_CROSS_REPO_TOKEN || github.token`, and a Render-specific provider-state path that conflict with the current workflow-minimization / TV-TVC-only / no-third-party-production architecture. Preserve useful source implementation while reconciling those carrier/credential assumptions before merge or supersession.

## Active claims / collision boundary

- cost containment: issue #125;
- workflow minimization: issue #128 under organization policy #167;
- workflow minimization batch 2: branch `chore/workflow-surface-minimization-002`, distinct validation-surface integration only;
- live sovereign runtime activation: resident StegVerse workers — observation only here;
- local model: complete/released — no competing implementation claim;
- TV/TVC credential/route authority: TV/TVC only.

## Current state

`ACTIVE_REMEDIATION / BATCH_2_MINIMIZATION_IMPLEMENTED_PENDING_VALIDATION / CANONICAL_MAIN_WORKFLOW_COUNT_49 / FULL_CENSUS_PENDING`

## Next executable action

Validate batch 2 on its final PR head, merge only if the stable dispatcher proves both consolidated capabilities and the credential-clean invariant, directly observe the post-merge workflow count, update issue #128, then classify the next nonoverlapping surfaces. Separately reconcile legacy PR #27 without discarding unique evaluator source.

## Archive condition

The local-model/runtime and trade-readiness requirements are durably transferred to canonical worker chains. This session is not archive-ready while unique workflow minimization and evidence-safe repository hygiene remain executable and untransferred.
