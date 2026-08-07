# Permission–Admissibility Mirror Handoff

## Status

```text
goal_id: PA-001
session_state: ACTIVE — DISTINCT IMPLEMENTATION LANE
repository: StegVerse-Labs/StegCore
branch: main
canonical_owner: StegVerse-Labs/StegCore
implementation_claim: CLAIMED_FOR_IMPLEMENTATION
validation_claim: CLAIMED_FOR_VALIDATION
integration_claim: UNCLAIMED
claim_created: 2026-08-07T14:53:00-05:00
claim_release_condition: contract, validator, tests, CI path, and durable validation evidence are installed; StegCore handoff reconciled; propagation task assigned or completed
```

## Originating session goal

Preserve and implement the distinction surfaced in the session: reducing or eliminating positional permission must never be interpreted as eliminating consequence-bound admissibility. AI or infrastructure may absorb redundant coordination, gatekeeping, recognition, and procedural maintenance, but it must not absorb the standing of a consequence-bearing subject or silently convert successful execution into legitimate authority.

## Active goal

Install a deterministic StegCore invariant that makes `permission` and `admissibility` separate machine-readable concepts and fails closed whenever a consequence-bearing action lacks current evidence of authority, consent/standing where applicable, continuity validity, governing-condition validity, or attributable/reconstructable consequence.

## Authoritative files

- `docs/PERMISSION_ADMISSIBILITY_MIRROR_HANDOFF.md`
- `contracts/permission-admissibility-boundary.v1.json`
- `scripts/validate_permission_admissibility_boundary.py`
- `tests/test_permission_admissibility_boundary.py`
- `.github/workflows/permission-admissibility-validate.yml`
- `evidence/permission-admissibility-validation.json` after hosted or deterministic validation evidence is available
- `STEGCORE_MIRROR_HANDOFF.md` for repository-wide collision and continuation state

## Canonical distinctions

1. **Permission** is an approval or allowance issued by a person, institution, role, policy process, or other authority surface.
2. **Admissibility** is the present-tense determination that a proposed consequence-bearing transition may legitimately cross the commit boundary under the evidence and governing conditions that actually hold now.
3. Permission may be absent because it is unnecessary; that absence does not imply inadmissibility.
4. Permission may be present and the action may still be inadmissible.
5. Successful execution is never evidence by itself that authority or admissibility existed.
6. Contribution without capture requires infrastructure to preserve the standing of the subject carrying the consequence; infrastructure may assist orientation and coordination without acquiring authorship of that subject's trajectory.
7. StegCore evaluates consequence-bound admissibility; it does not create underlying human consent, mint continuity evidence, or grant external legal/financial/deployment authority.

## Required invariant

For a consequence-bearing transition, `admissible=true` is valid only when every required present-tense predicate is true:

- `authority_current`
- `consent_or_standing_current` when the transition affects a subject whose consent/standing is required
- `continuity_current`
- `governing_conditions_current`
- `consequence_attributable`
- `consequence_reconstructable`

`permission_present` is recorded independently and is never sufficient to make `admissible=true`.

A non-consequence-bearing coordination step may omit consequence predicates, but it must not be represented as execution authority.

## Collision assessment

The live `STEGCORE_MIRROR_HANDOFF.md` is repository-canonical. Its historical PR #18 status is stale (PR #18 is merged), but the commit-coherence runtime surface remains authoritative and compatible with this lane. This lane owns only the files named above plus the minimum reconciliation patch to `STEGCORE_MIRROR_HANDOFF.md`. It does not modify `src/stegcore/decision.py`, commit-governance runtime code, Child Mode runtime files, StegGate network-governance review files, custody-chain evidence surfaces, or originating-choice runtime files.

Recent StegGate network-governance review work is complete/transferred and does not claim these paths. No open PR matching permission/admissibility was found before claim creation.

## Task inventory

| Task ID | State | Location | Next executable action |
|---|---|---|---|
| PA-001-HANDOFF | COMPLETE | this file | install contract |
| PA-001-CONTRACT | CLAIMED_FOR_IMPLEMENTATION | `contracts/permission-admissibility-boundary.v1.json` | create deterministic invariant contract |
| PA-001-VALIDATOR | CLAIMED_FOR_IMPLEMENTATION | `scripts/validate_permission_admissibility_boundary.py` | validate positive + negative cases |
| PA-001-TESTS | CLAIMED_FOR_VALIDATION | `tests/test_permission_admissibility_boundary.py` | bind semantic cases |
| PA-001-CI | CLAIMED_FOR_VALIDATION | `.github/workflows/permission-admissibility-validate.yml` | run on push/PR/manual dispatch |
| PA-001-EVIDENCE | BLOCKED | `evidence/permission-admissibility-validation.json` | release condition: successful observed run or deterministic local validation receipt |
| PA-001-STEGCORE-RECONCILE | UNCLAIMED | `STEGCORE_MIRROR_HANDOFF.md` | reconcile stale PR #18 state and record this invariant |
| PA-001-PROPAGATION | UNCLAIMED | future durable task receipt after validation | inspect Site, Publisher, admissibility-wiki, stegguardian-wiki handoffs before propagation |

## Validation commands

```bash
python scripts/validate_permission_admissibility_boundary.py
python -m pytest -q tests/test_permission_admissibility_boundary.py
```

Success markers:

```text
PERMISSION_ADMISSIBILITY_BOUNDARY=PASS
PERMISSION_ADMISSIBILITY_TESTS=PASS
```

## Propagation obligations

After validation, inspect the newest applicable `*_MIRROR_HANDOFF.md` before any mutation in:

- `StegVerse-Labs/Site`
- `GCAT-BCAT-Engine/Publisher`
- `StegVerse-Labs/admissibility-wiki`
- `StegVerse-Labs/stegguardian-wiki`

Do not publish the distinction as a claim that permission is never needed. The public-safe statement is narrower: positional permission and present-tense admissibility are distinct; either may be required depending on the consequence and governing context.

## Archive condition

This session may archive only after all unique requirements above are implemented, validated or durably blocked with a machine-owned release condition, repository handoff state is reconciled, and propagation is either verified or assigned to a durable repository-native task. Chat history must not remain necessary for continuation.

## Current completion

- task completion: 1/8 = 12.5%
- developed files: 1/5 = 20%
- validation: 0/3 = 0%
- integration: 0/1 = 0%
- propagation: 0/4 = 0%
- goal activation: 10%
- session consolidation: 1/3 unique session requirements durably transferred
