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

Consolidated into credential-clean `runtime-tests.yml`:

- `.github/workflows/check-tidc-evidence-chain-management.yml`
- `.github/workflows/criterion-contestability-validate.yml`

Post-merge workflow count: `49`.

PR #130 repaired the stale TIDC validator to current v0.2 semantics; final validation run `31864882005` passed and merged at `e1bf1a35fe42c0c43e2143887d27fcc9544f303e`.

## Completed workflow-surface minimization batch 2

Merged by PR #131 at merge commit `a1a5507e578f03b1abc414a9c4ab2e5a516176af`.

Consolidated into `runtime-tests.yml`:

- `.github/workflows/governed-runtime-adapters.yml`
- `.github/workflows/originating-choice-validate.yml`

Final-head `Validate StegCore Runtime - No Non-TV/TVC Credential Authority` run `31872307672` passed both consolidated validation steps plus the credential, runtime, TIDC, criterion, Governance snapshot and downstream verification checks. Companion BCAT / baseline / readiness / core-test workflows also passed. Direct post-merge workflow count: `47`.

## Workflow-surface minimization batch 3 — implementation pending validation

Branch: `chore/workflow-surface-minimization-003`.

Two completed source-validation lanes with released chat/session claims are being consolidated into `runtime-tests.yml`:

- `.github/workflows/permission-admissibility-validate.yml` -> `runtime-tests.yml`
  - canonical goal `PA-001` is implementation/validation released and downstream propagation is machine-owned;
  - preserves `scripts/validate_permission_admissibility_boundary.py` and focused semantic tests;
  - preserves success marker semantics;
  - adds `contracts/permission-admissibility-boundary.v1.json` to stable dispatcher triggers.
- `.github/workflows/correctability-layer.yml` -> `runtime-tests.yml`
  - canonical correctability source implementation and validation are complete/released; remaining Site propagation is machine-owned and separate;
  - preserves `tools/verify_correctability_layer.py` execution;
  - requires `brain_reports/correctability_layer_report.json` to be produced and emits its SHA-256 in the credential-clean job;
  - adds the canonical correctability machine-state/claim JSON files to stable dispatcher triggers.

The source validators are not removed. Only their redundant standalone GitHub workflow doorways are removed. Existing committed evidence and machine-owned propagation records remain authoritative. The correctability admission observer is not modified by this batch.

The stable dispatcher remains `permissions: {}`, rejects exposed GitHub/GH/PAT/TVC-ephemeral credential variables, and acquires repository source anonymously. No NON-TV/TVC secret/token or GitHub production/runtime authority is introduced.

Expected post-merge workflow count: `45`, subject to direct API observation after final-head validation.

Release conditions for batch 3:

1. stable dispatcher directly executes both permission-admissibility and correctability validators;
2. focused permission semantic tests pass;
3. correctability verifier produces the required report and report SHA-256;
4. no NON-TV/TVC credential/token path appears;
5. final PR head validation passes;
6. merge completes and direct Actions API reports workflow count `45`;
7. issue #128 receives run/merge/count evidence.

## Current quantitative state

- workflow surfaces at audit start: 51
- current workflow files on canonical `main`: 47
- recurring schedules removed in containment batches: 12
- workflow files consolidated/eliminated on canonical `main`: 4
- workflow surfaces explicitly classified/remediated on canonical `main`: 16/51 = 31.37%
- batch 3 proposed additional consolidations: 2
- expected after batch 3 merge: current workflow files 45; classified/remediated 18/51 = 35.29%; remaining classification denominator 33/51

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

Trade-readiness execution is not owned by this cleanup lane. Canonical continuation remains `StegVerse-Labs/stegfin-governance/docs/STEGFIN_MIRROR_HANDOFF.md` and `STEGFIN-CONTINUITY-CARRIER-007`; manual provider/wallet execution is prohibited, credential authority is TV/TVC, and signing/broadcast remain USER_ONLY.

## Repository hygiene

Issue/PR/branch cleanup is coordinated by `StegVerse-Labs/.github#165`. Destructive cleanup must preserve active claims, current handoffs, protected/release branches, evaluation snapshots, unique commits and evidence references.

Known completed hygiene:

- duplicate issue #30 closed in favor of #29;
- duplicate issue #32 closed in favor of #31.

Legacy PR #27 retains possible unique evaluator source but its scheduled GitHub write workflows, `STEGVERSE_CROSS_REPO_TOKEN || github.token`, and Render-specific path conflict with current architecture; preserve useful source while reconciling those obsolete carrier/credential assumptions before merge or supersession.

## Active claims / collision boundary

- cost containment: issue #125;
- workflow minimization: issue #128 under organization policy #167;
- batch 3: `chore/workflow-surface-minimization-003`, validation-surface consolidation only;
- permission-admissibility propagation: machine-owned, not taken over by this lane;
- correctability final Site propagation: machine-owned, not taken over by this lane;
- live sovereign runtime activation: resident StegVerse workers — observation only here;
- local model: complete/released — no competing implementation claim;
- TV/TVC credential/route authority: TV/TVC only.

## Current state

`ACTIVE_REMEDIATION / BATCH_3_MINIMIZATION_IMPLEMENTED_PENDING_VALIDATION / CANONICAL_MAIN_WORKFLOW_COUNT_47 / FULL_CENSUS_PENDING`

## Next executable action

Open and validate batch 3 on its final PR head. Merge only if both consolidated validators and the credential-clean invariant pass, then directly observe the post-merge workflow count and update issue #128. Continue the next nonoverlapping classification batch afterward. Separately reconcile legacy PR #27 under evidence-safe hygiene rules.

## Archive condition

The local-model/runtime and trade-readiness requirements are durably transferred to canonical worker chains. This session is not archive-ready while workflow minimization and evidence-safe repository hygiene remain executable and untransferred.
