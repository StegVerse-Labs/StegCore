# Criterion Contestability Mirror Handoff

## Source of Truth

This is the goal-specific continuation record for `CCB-001` inside the repository-wide authority of `STEGCORE_MIRROR_HANDOFF.md`. It must not supersede unrelated StegCore workstreams. The adjacent completed `PA-001` permission/admissibility lane is a dependency and semantic predecessor, not a competing implementation.

```text
goal_id: CCB-001
session_state: ACTIVE — UNIQUE WORK REMAINS
repository: StegVerse-Labs/StegCore
branch: main
canonical_owner: StegVerse-Labs/StegCore
implementation_claim: CLAIMED_FOR_IMPLEMENTATION
validation_claim: CLAIMED_FOR_VALIDATION
integration_claim: CLAIMED_FOR_INTEGRATION
claim_created: 2026-08-07T17:05:00-05:00
claim_release_condition: criterion-contestability contract, evaluator, semantic tests, CI validation, deterministic evidence, repository handoff reconciliation, and propagation obligation are complete or durably machine-owned
```

## Originating session goal

Formalize the pre-execution insight that agency begins after an upstream selection has already occurred: a possibility is selected as relevant, a criterion acquires force, and a frame becomes actionable. Preserve trajectory plurality while preventing a relevance criterion, frame, or orientation from silently acquiring consequential authority merely because it precedes planning.

## Canonical distinctions transferred from the session

1. **Orientation is not authority.** An orientation, model frame, or selected criterion cannot authorize execution merely by shaping a plan.
2. **Contestability is not admissibility.** A criterion may be visible, provenance-bound, and contestable while the resulting transition remains inadmissible.
3. **Parallelity is not authorization.** Multiple independent trajectories may remain visible without any of them acquiring execution authority.
4. **Pre-selection must remain contestable.** A criterion that hardens into unchallengeable infrastructure before consequence creates an invisible authority path.
5. **Relation is a governed transition.** Mutual legibility among distinct trajectories is insufficient; a consequence-bearing relation requires the same present-tense admissibility discipline as other commits.
6. **Successful planning or execution is not evidence of legitimate framing.** Downstream coherence cannot repair an inadmissible upstream criterion.
7. **Commit-time validity remains decisive.** Criterion provenance, contestability, delegation/authority, consent or standing when applicable, continuity, and governing conditions must survive to the consequence boundary.

## Convergence assessment

`PA-001` already implements the repository invariant that permission is not admissibility and that current authority/continuity/governing-condition evidence is required for consequence-bearing transitions. `CCB-001` extends rather than duplicates that work by adding the missing upstream predicate family: whether the criterion/frame that shaped the proposed action remained provenance-bound and contestable and whether it ever possessed separately established consequential authority.

`CCB-001` must not modify the completed `contracts/permission-admissibility-boundary.v1.json` or its validator/tests. It composes with that boundary through deterministic test fixtures and explicit authority separation.

## Authoritative target files

```text
docs/CRITERION_CONTESTABILITY_MIRROR_HANDOFF.md
contracts/criterion-contestability-boundary.v1.json
src/stegcore/criterion_contestability.py
tests/test_criterion_contestability.py
.github/workflows/criterion-contestability-validate.yml
evidence/criterion-contestability-validation.json
receipts/criterion-contestability-propagation-task.json
```

## Task inventory

| Task ID | State | Location | Next executable action |
|---|---|---|---|
| CCB-001-HANDOFF | COMPLETE | this file | install contract |
| CCB-001-CONTRACT | CLAIMED_FOR_IMPLEMENTATION | `contracts/criterion-contestability-boundary.v1.json` | install deterministic contract and adversarial cases |
| CCB-001-RUNTIME | CLAIMED_FOR_IMPLEMENTATION | `src/stegcore/criterion_contestability.py` | implement fail-closed evaluator |
| CCB-001-TESTS | CLAIMED_FOR_VALIDATION | `tests/test_criterion_contestability.py` | bind contract cases to runtime |
| CCB-001-CI | CLAIMED_FOR_VALIDATION | `.github/workflows/criterion-contestability-validate.yml` | automate validator/test execution |
| CCB-001-EVIDENCE | BLOCKED | `evidence/criterion-contestability-validation.json` | release condition: successful hosted or deterministic validation evidence |
| CCB-001-INTEGRATION | CLAIMED_FOR_INTEGRATION | PA-001 semantic boundary + CCB runtime composition | prove independent trajectories can still DENY at criterion/admissibility boundary |
| CCB-001-PROPAGATION | UNCLAIMED | `receipts/criterion-contestability-propagation-task.json` | inspect destination handoffs and activate bounded propagation review after validation |

## Required adversarial cases

1. Two or more trajectories remain independent and visible, but the selected criterion has no authoritative provenance: `DENY`.
2. Criterion provenance is known but contestability is disabled before consequence: `DENY`.
3. Criterion is contestable but its authority is stale at commit time: `DENY`.
4. Criterion is contestable and provenance-bound but required consent/standing is absent: `DENY`.
5. One trajectory contests another and no criterion has established consequential authority: `DEFER`, not synthetic consensus.
6. All required criterion and PA-001 predicates are current: `ALLOW`.
7. A non-consequence-bearing orientation/coordination step may proceed without being represented as execution authority.

## Collision boundaries

Do not modify or claim ownership of:

- completed PA-001 implementation files;
- commit-governance runtime files owned by the commit-coherence lane;
- Child Mode authority runtime files;
- StegGate network-governance review files;
- custody/continuity receipt minting or verification authority;
- external legal, financial, deployment, Guardian, or publication authority.

## Validation target

```text
python -m pytest -q tests/test_criterion_contestability.py
```

Hosted validation must record the exact head SHA, job conclusion, semantic case count, and deterministic PASS marker before implementation/validation claims are released.

## Propagation candidates

After validation, inspect and obey each destination's canonical handoff before mutation:

```text
StegVerse-Labs/Site/docs/SITE_MIRROR_HANDOFF.md
GCAT-BCAT-Engine/Publisher/PUBLISHER_MIRROR_HANDOFF.md
StegVerse-Labs/admissibility-wiki/ADMISSIBILITY_WIKI_MIRROR_HANDOFF.md
StegVerse-002/stegguardian-wiki/STEGGUARDIAN_WIKI_MIRROR_HANDOFF.md
```

## Archive condition

The originating conversation is archive-safe only after all seven session distinctions above are either implemented/validated or durably merged into this canonical lane, no active CCB implementation/validation claim remains dependent on chat history, and any downstream propagation is complete or machine-owned with an inspectable release condition.

## Completeness snapshot

```text
task_completion: 1/8
required_developed_files: 1/7
scaffolding_or_stubs: 0
missing_required_files: 6
validation: 0/3
integration: 0/2
session_consolidation: 7/7 requirements transferred
archival_readiness: false
```
