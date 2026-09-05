# TEMPORAL_GOVERNED_ANALYSIS_MIRROR_HANDOFF.md

Status: SOURCE_IMPLEMENTED_VALIDATION_IN_PROGRESS
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

All eight source artifacts are present on PR #184. Source-complete remains unclaimed until the dedicated TGA validation workflow succeeds and the PR is merged.

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
- `StegVerse-Labs/StegIndex`: capability/predicate registration for TGA-001; tracking issue #28;
- `StegVerse-Labs/Site`: governed discovery/playback UI and temporal source references;
- `GCAT-BCAT-Engine/Publisher`: governed publication projection;
- `admissibility-wiki`: explanatory projection;
- `stegguardian-wiki`: governance/contestability projection.

The media/event ingestion adapter must remain separate from media custody and must preserve source identity, exact temporal windows, provenance, and representational uncertainty.

## Validation lane

Dedicated workflow:
- `.github/workflows/temporal-governed-analysis.yml`

TGA-required checks:
1. package install succeeds;
2. evaluator compiles;
3. focused TGA tests pass;
4. analysis-only authority and non-ground-truth assertions remain present.

Observed run `33983989348` proved:
- package install: PASS;
- evaluator compile: PASS;
- focused TGA tests: PASS (`6 passed`);
- repo-wide regression step: FAIL due five pre-existing portable-release/version-coherence tests.

The repo-wide failures are not caused by TGA and are canonical to the existing portable artifact/version lane: `docs/STEGVERSE_MICRO_ECOSYSTEM_MIRROR_HANDOFF.md` names StegCore PR #137 as the active artifact-transport claimant and forbids competing artifact/publication implementation. Main currently has `VERSION=0.3.0` and `pyproject.toml version=0.3.0` while `tests/test_product_consistency.py` still asserts `0.2.0` and portable-release manifest validation likewise observes source-version mismatch.

Commit `1987ee0380bf4ee333bda5ce6711024f8525a6a5` therefore narrows the dedicated TGA workflow to TGA-owned validation only and explicitly records the unrelated repository regression boundary rather than modifying PR #137-owned files.

## Current continuation

pull_request: #184
source_state: IMPLEMENTED_ON_FEATURE_BRANCH
focused_validation_state: PASS_OBSERVED_RUN_33983989348_PRE_PATCH
current_validation_state: DEDICATED_WORKFLOW_RERUN_REQUIRED_AFTER_1987ee0
repo_wide_regression_state: PREEXISTING_VERSION_COHERENCE_FAILURE_OWNED_BY_PR_137
merge_state: OPEN
stegindex_registration_issue: StegVerse-Labs/StegIndex#28
next_action: observe the post-1987ee0 dedicated TGA workflow; if successful and repository merge requirements allow, merge PR #184; then execute StegIndex #28 registration and open the governed media/event ingestion integration lane.
manual_execution_allowed: true
runtime_activation_claim: NONE
authority_effect: NONE_ANALYSIS_ONLY
thread_archive_ready: false
