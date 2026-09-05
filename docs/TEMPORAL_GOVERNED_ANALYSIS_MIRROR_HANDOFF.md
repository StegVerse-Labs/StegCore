# TEMPORAL_GOVERNED_ANALYSIS_MIRROR_HANDOFF.md

Status: SOURCE_IMPLEMENTED_AWAITING_VALIDATION
Updated: 2026-09-05
Organization: StegVerse-Labs
Repository: StegVerse-Labs/StegCore
Branch: feature/temporal-governed-analysis
Goal ID: TGA-001
Pull request: #184

## Source of truth

This file is the canonical goal-specific continuation record for the Temporal Governed Analysis engine inside StegCore. It supplements `docs/STEGCORE_MIRROR_HANDOFF.md` and does not supersede unrelated StegCore workstreams.

## Mission

Build a generalized engine that binds precise temporal evidence to versioned rule/law/constraint sets and produces reconstructable governed evaluations without equating encoded representation with factual correctness.

Primary demonstration domain: sports temporal media.
Generalized target domains include sports rules, laws, regulations, technical standards, safety procedures, policy, and governed ecosystem transitions.

## Foundational invariants

1. Canonical representation is not canonical reality.
2. Encoding increases precision and machine readability but never implies correctness.
3. Original source evidence remains independently addressable from every compact encoding.
4. Observed reality, contemporaneous adjudication, and projected adjudication are separate truth layers.
5. Rule/law effective time, interpretation time, enforcement profile, and event time remain independently represented.
6. Counterfactual evaluation must never rewrite historical applicability.
7. Unresolved evidence remains `UNRESOLVED`; no forced binary conclusion is permitted.
8. Multiple plausible encodings may coexist when source ambiguity cannot be resolved.
9. Legal analysis carries `adjudicative_authority=NONE` unless an authoritative adjudication source is explicitly bound.
10. No hindsight leakage: decision-time evaluation may use only evidence available at the decision point unless retrospective mode is explicitly requested.

## Canonical object chain

```text
SOURCE REALITY
-> TEMPORAL WINDOW
-> OBSERVATION ENCODING
-> GOVERNING CONTEXT
-> EVALUATION
-> VARIANCE / UNCERTAINTY
-> RECONSTRUCTABLE PROVENANCE
```

## Required uncertainty dimensions

- `source_uncertainty`
- `observation_uncertainty`
- `semantic_mapping_uncertainty`
- `rule_mapping_uncertainty`
- `interpretation_uncertainty`
- `evaluation_uncertainty`

These dimensions must not be collapsed into one generic confidence score.

## Required evaluation states

- SATISFIED
- DENIED
- UNRESOLVED
- NOT_APPLICABLE
- CONTRADICTORY

Legal/domain-specific renderers may additionally expose descriptive states such as:
- ELEMENT_SUPPORTED
- ELEMENT_UNSUPPORTED
- ELEMENT_UNRESOLVED
- DEFENSE_POSSIBLY_APPLICABLE
- ENFORCEMENT_HISTORICALLY_UNCOMMON
- NO_ADJUDICATED_CONCLUSION

## Source-complete target

The initial source build is complete when StegCore contains:

1. generalized temporal-event schema;
2. versioned governing-context/ruleset schema;
3. governed evaluation schema;
4. deterministic evaluator that preserves unresolved states and counterfactual markers;
5. provenance/source binding contract;
6. multi-dimensional uncertainty contract;
7. deterministic tests covering historical and counterfactual projections;
8. at least one bounded sports fixture proving cross-temporal rule projection semantics.

All eight source artifacts are now present on PR #184. Source-complete remains unclaimed until the dedicated validation workflow succeeds and the PR is merged.

## Non-goals for TGA-001 source MVP

- media acquisition or redistribution;
- computer-vision model training;
- asserting legal guilt or liability;
- simulating unknowable downstream alternate histories;
- runtime activation claims;
- replacing governing authorities or official adjudications;
- introducing a new authority plane.

## Authority boundary

This engine evaluates represented evidence against represented constraints. It grants no legal, officiating, enforcement, publication, execution, or adjudicative authority.

`authority_effect = NONE_ANALYSIS_ONLY`

## Installed modules

Destination: `StegVerse-Labs/StegCore`

- `schemas/temporal-event.schema.json`
- `schemas/governing-context.schema.json`
- `schemas/governed-evaluation.schema.json`
- `src/stegcore/temporal_governed_analysis.py`
- `tests/test_temporal_governed_analysis.py`
- `fixtures/temporal-governed-analysis/baseball-third-base-counterfactual.json`
- `.github/workflows/temporal-governed-analysis.yml`

## Remaining integration modules

After validated merge:
- `StegVerse-Labs/StegIndex`: capability/predicate registration for TGA-001;
- `StegVerse-Labs/Site`: governed discovery/playback UI and temporal source references;
- `GCAT-BCAT-Engine/Publisher`: governed publication projection;
- `admissibility-wiki`: explanatory projection;
- `stegguardian-wiki`: governance/contestability projection.

The media/event ingestion adapter must remain separate from media custody and must preserve source identity, exact temporal windows, provenance, and representational uncertainty.

## Validation lane

Dedicated workflow:
- `.github/workflows/temporal-governed-analysis.yml`

Required checks:
1. package install succeeds;
2. evaluator compiles;
3. focused TGA tests pass;
4. complete StegCore regression suite passes;
5. analysis-only authority and non-ground-truth assertions remain present.

The absence of a validation workflow before commit `05955a111f8438e7e5b01e0f6fd5417b08d7c320` was a path-scoping omission and is now source-corrected. No successful validation receipt is claimed until a workflow run is observed.

## Current continuation

pull_request: #184
source_state: IMPLEMENTED_ON_FEATURE_BRANCH
validation_state: WORKFLOW_ADDED_AWAITING_OBSERVED_RUN
merge_state: OPEN_BLOCKED_PENDING_REQUIRED_GATE
next_action: observe the dedicated TGA workflow result; if successful, merge PR #184; then register TGA-001 in StegIndex and open the governed media/event ingestion integration lane.
manual_execution_allowed: true
runtime_activation_claim: NONE
authority_effect: NONE_ANALYSIS_ONLY
thread_archive_ready: false
