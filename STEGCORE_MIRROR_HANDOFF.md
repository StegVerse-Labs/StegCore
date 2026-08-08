# StegCore Mirror Handoff

## Source of truth

```text
Organization: StegVerse-Labs
Repository: StegCore
Canonical branch: main
Primary goal: STEGGATE-LIVE-FUNCTIONAL-ACTIVATION
Canonical task owner: issue #68
State: IMPLEMENTED_AND_REPOSITORY_VALIDATED / HOST_DEPLOYMENT_BLOCKED
```

Read this file before changing StegCore runtime decisions, adapters, receipt bindings, live-service activation, deployment, or downstream verification. Live Git state, workflow runs/jobs, committed evidence, issues, and Render observations supersede chat history.

## Active goal

Make canonical StegGate directly usable as a live service with complete admissibility-matrix outcomes rather than stopping at library/tag readiness.

## Architectural invariants

1. `src/stegcore/runtime.py#governed_execute` remains the production mutation boundary.
2. Transport never creates authority; mutation remains unreachable until admissibility and commit coherence permit it.
3. StegCore consumes already-verified continuity references and does not verify signatures or mint Continuity receipts.
4. ALLOW, DENY, REVIEW, FAIL_CLOSED, coherence denial, execution failure, non-execution, observation, and reconciliation remain reconstructable.
5. Decision reality, execution reality, and observed reality remain distinct.
6. Live evaluation is not arbitrary remote mutation authority.

## Completed prior chain

Governed runtime adapters, decision-state reconstruction, evidence persistence, downstream reconciliation, Governance freshness, independent release-policy evaluation, authorized annotated tag `v0.1.0`, and post-tag awareness were completed before this goal. Issues #21, #23, #37, and #64 are closed for that chain.

## Live service implementation — INSTALLED

Canonical issue: `StegVerse-Labs/StegCore#68`.

Installed on `main`:

```text
src/stegcore/steggate.py
src/stegcore/service.py
tests/test_steggate_service.py
pyproject.toml
docs/STEGGATE_LIVE_SERVICE.md
```

The service exposes:

```text
GET /health
GET /v1/capabilities
GET /v1/self-test
POST /v1/evaluate
```

The evaluator returns a complete predicate matrix and preserves four dispositions: `ALLOW`, `DENY`, `REVIEW`, `FAIL_CLOSED`. Critical unknown evidence fails closed. Human approval is candidate-hash bound. Candidate and decision-state hashes are deterministic canonical SHA-256 values. No arbitrary remote mutation endpoint is exposed.

## Repository validation

Head `7cc4feb5311a3453e7f60e38109a37c9538a795b` completed StegCore Tests successfully in run `31266956563` and Test Readiness successfully in run `31266956537`. A packaging hardening follow-up was committed at `522b10ebbe2ebca1dec1a93366fcecf42d231047` so setuptools discovers only the canonical `src/stegcore` package for hosted installation.

## Hosted activation — BLOCKED BY MACHINE-OBSERVED RENDER QUOTA

A canonical Render service was actually created in the confirmed workspace:

```text
service: steggate-core
service id: srv-d9rlic2jobas73do1q6g
origin: https://steggate-core.onrender.com
repo: StegVerse-Labs/StegCore
branch: main
auto-deploy: yes
plan: free
region: oregon
```

Initial deploy:

```text
deploy id: dep-d9rlicajobas73do1qjg
status: build_failed
cause: workspace has run out of build pipeline minutes for the current billing period
```

Render's own build log states that builds are canceled until workspace build-pipeline capacity is restored. This is not a StegGate source/test failure and must not be represented as live activation.

## Claim and collision control

```text
task: STEGGATE-LIVE-FUNCTIONAL-ACTIVATION
owner: StegVerse-Labs/StegCore#68
role: implementation + validation + deployment activation
claim state: BLOCKED
claim release condition: hosted /health and /v1/self-test observed successfully
collision boundary: do not create a competing canonical StegGate service or replace the completed runtime adapter chain
```

Legacy Render services `steggate-api` and `steggate-api-tp4t` remain owned by `StegGhost/entity-sandbox-runner`; they are not evidence that canonical StegCore is deployed.

## Exact next executable action

When Render build-pipeline capacity becomes machine-observably available, the existing `steggate-core` service auto-deploys the current `main` commit. Then:

1. inspect the deploy to `live`;
2. observe `/health`;
3. observe `/v1/self-test` and require ALLOW/DENY/REVIEW/FAIL_CLOSED all PASS;
4. exercise one `/v1/evaluate` request and retain the complete matrix plus hashes;
5. update issue #68 and this handoff with the deploy id and observations;
6. only then classify canonical live StegGate evaluation as activated.

## Cross-repository dependencies

Ara decision-state interop remains canonical at `StegVerse-Labs/ara-admissibility-interop/ARA_ADMISSIBILITY_INTEROP_MIRROR_HANDOFF.md`.
Continuity preservation remains canonical at `StegVerse-Labs/Continuity/STEGGATE_CONTINUITY_MIRROR_HANDOFF.md`.
Governance remains policy authority; StegCore remains runtime authority.

## Archive condition

NOT SATISFIED for this active goal. The source implementation and repository validation are installed, but canonical hosted runtime observation is blocked by the Render workspace build-minute exhaustion. The session retains a distinct activation/observation role until issue #68's release condition is satisfied.
