# Execution Orchestrator Mirror Handoff

## Repository and owner

- Repository: `StegVerse-Labs/StegCore`
- Controller issue: `StegVerse-Labs/StegCore#42`
- Core module: `src/stegcore/execution_orchestrator.py`
- Runner: `scripts/run_execution_orchestrator.py`
- Task graph: `data/execution-orchestrator-tasks.json`
- Runtime state: `data/execution-orchestrator-state.json`
- Workflow: `.github/workflows/execution-orchestrator.yml`

## Purpose

Convert unfinished StegVerse work into governed execution states with exact locations, observers, resolvers, successors, and retry policies. Generic `PENDING` is prohibited.

## States

- `RUNNABLE`
- `WAITING_FOR_EVIDENCE`
- `WAITING_FOR_AUTHORITY`
- `OBSERVATION_BLOCKED`
- `RESOLVING`
- `COMPLETE`
- `DENIED`

Observation failure is not task failure. Waiting work does not halt independent admissible branches. Every task record must name its repository, issue, workflow, evidence path, stop condition, dependencies, resolver, successor, and retry policy.

## Initial graph

1. `MC-01-CRYPTO-ACCESSIBILITY`
   - Repository: `StegVerse-Labs/crypto-bot`
   - Issue: `StegVerse-Labs/crypto-bot#7`
   - Workflow: `.github/workflows/first-accessibility-mark.yml`
   - Evidence: `data/first-accessibility-mark-status.json`

2. `MC-02-MARKETPLACE-COLLECTION`
   - Repository: `GCAT-BCAT-Engine/Marketplace`
   - Issue: `GCAT-BCAT-Engine/Marketplace#1`
   - Workflow: `.github/workflows/import-marketplace-coinbase-settlements.yml`
   - Evidence: `data/marketplace-coinbase-outbound-collection-status.json`

3. `MC-03-PUBLISHER-VERIFY`
   - Repository: `GCAT-BCAT-Engine/Publisher`
   - Issue: `GCAT-BCAT-Engine/Publisher#19`
   - Workflow: `.github/workflows/collect-marketplace-coinbase-release-evidence.yml`
   - Evidence: `data/marketplace-coinbase-release-evidence-status.json`

4. `MC-04-SITE-PROJECTION`
   - Repository: `StegVerse-Labs/Site`
   - Issue: `StegVerse-Labs/Site#131`
   - Workflow: `.github/workflows/import-marketplace-coinbase-accessibility.yml`
   - Evidence: `data/marketplace-coinbase-accessibility-status.json`

## Continuation rule

`development_halt` is always false for evidence waiting, observation repair, retries, or independent work. A task may stop only its dependent branch. The scheduler continues every independent admissible branch.

## Authority boundary

The orchestrator schedules and observes work. It does not grant execution, publication, release, custody, withdrawal, financial, or live Coinbase authority. All authority flags remain false unless a separate verified authority process grants them.

## Current decision

`EXECUTION_ORCHESTRATOR_BUILT_AND_ACTIVATED_INITIAL_GRAPH_RUNNING`
