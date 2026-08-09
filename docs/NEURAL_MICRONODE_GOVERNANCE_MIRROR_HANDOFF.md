# Neural Micro-Node Governance Mirror Handoff

Status: ACTIVE — IMPLEMENTED, HOSTED VALIDATION MACHINE-OWNED
Date: 2026-08-08
Repository: `StegVerse-Labs/StegCore`
Branch: `main`
Goal: `STEGCORE-NEURAL-MICRONODE-001`
Canonical issue: `#71`

## Governing source and collision control

This continuation inherits the portable/ephemeral micro-node topology and network-governance review without altering their authority boundaries. `docs/STEGCORE_MIRROR_HANDOFF.md` was read before runtime mutation; its external-evidence collision boundary does not include this lane's files. Portable integration is deliberately deferred until its separate lane admits mutation.

Authoritative predecessors:
- `docs/STEGCORE_MIRROR_HANDOFF.md`
- `docs/STEGGATE_NETWORK_GOVERNANCE_MIRROR_HANDOFF.md`
- `docs/STEGGATE_PORTABLE_MICRONODE.md`
- `docs/STEGGATE_PRODUCT_REVIEW_V4.md`

## Active claim

```text
task_id: STEGCORE-NEURAL-MICRONODE-001
originating_goal: govern minimal ephemeral transport to/from a specifically addressed downstream neural micro-node
implementation_claim: COMPLETE_ON_MAIN
validation_claim: MACHINE_OWNED
validation_lane: .github/workflows/neural-micronode.yml
claim_created: 2026-08-09T02:08:28Z
claim_release_condition: hosted workflow passes and run/job evidence is recorded here and in issue #71
collision_boundary:
  - docs/NEURAL_MICRONODE_GOVERNANCE_MIRROR_HANDOFF.md
  - schemas/neural-micronode-packet.schema.json
  - src/stegcore/neural_micronode.py
  - tests/test_neural_micronode.py
  - .github/workflows/neural-micronode.yml
  - data/neural-micronode-session-inventory.json
next_task_after_release: portable integration review through its canonical issue/handoff; interop propagation only through destination handoff
```

## Goal and receiver model

The BCI, sensor, stimulator, decoder, encoder, or other interface is transport/translation infrastructure. It is not automatically the receiver and it is not automatically an authority. The receiver is the specifically addressed downstream neural micro-node: a bounded neural region, ensemble, pathway, or other experimentally supportable functional target for the transition.

```text
source micro-node
 -> payload candidate + transition requirements
 -> transport / neural interface
 -> addressed neural micro-node
 -> receiver observation/signature
 -> bounded admissibility translation
 -> transition-relative evidence
 -> ALLOW | DENY | REVIEW | FAIL_CLOSED
 -> separately governed consequence or non-consequence
 -> receipt
```

Let `N_d` be the addressed destination, `sigma(N_d,t)` an observation/signature, `P` the candidate, and `R_T` transition requirements:

```text
A_T = translate(sigma(N_d,t), P, R_T)
decision = evaluate(P, R_T, A_T)
```

`A_T` is deliberately bounded and MUST NOT be interpreted as a complete representation of the receiver, person, cognition, mental state, intent, or identity. The same payload can require different evidence at different destinations, and the same observation can support different bounded assertions for different transitions.

## Non-equivalences

```text
neural activity != thought
thought != intended meaning
intended meaning != instruction
instruction != authorization
authorization != admissibility
admissibility != execution
observation != receiver state in full
receiver signature != authority
translation confidence != authority
transport success != admissibility
```

No decoder confidence score collapses these boundaries.

## Installed implementation

```text
docs/NEURAL_MICRONODE_GOVERNANCE_MIRROR_HANDOFF.md
schemas/neural-micronode-packet.schema.json
src/stegcore/neural_micronode.py
tests/test_neural_micronode.py
.github/workflows/neural-micronode.yml
data/neural-micronode-session-inventory.json
```

Commits:

```text
997fea00f658ce6fe6c2200ba65afb1431087bc9 initial handoff
ddb74ae2020eeb13f547c56f63abaaa140155eaf packet schema
a450f71e46a7463f6da18a1744b99fe1d646de19 adapter-neutral evaluator
d095a684e9808c03a1b7fa3f95e5daf66037ed3f focused tests
cdd5c7165d603d3dfa8a08effc369baea532fed9 hosted validation workflow
761088027856ba856e4e5d96e45b85caafa84c35 session execution inventory
```

The evaluator verifies destination resolution/ambiguity, adapter attestation, calibration presence/validity, translation identity, freshness, observation quality, required/prohibited assertions and provenance. It explicitly rejects attempts to elevate decoder assertions named `intended_by`, `authorized_by`, `consented_to_by`, or `execution_authority` into authority.

ALLOW from this module means only that the bounded neural receiver-evidence boundary is satisfied. It does not execute a consequence or manufacture higher-level authority.

## Inbound / outbound chains

Inbound:
```text
candidate -> destination resolution -> receiver evidence -> admissibility -> separately authorized consequence -> observation
```

Outbound:
```text
neural observation -> candidate reconstruction -> provenance -> bounded interpretation -> proposed payload -> authorization -> admissibility -> commit coherence -> consequence
```

A decoder is a candidate generator/evidence producer, not an authority source merely because reconstruction confidence is high.

## Translation provenance and minimization

Translated assertions preserve observation reference, adapter profile, model/mapping identity, calibration reference, timestamp/freshness, assertion provenance, and bounded scope. A translated assertion MUST NOT silently upgrade `correlated_with`, `predicted_as`, or `classified_as` into intent, consent, authorization, or execution authority.

Raw neural observations SHOULD remain local whenever bounded derived assertions suffice. Transport the minimum assertion set, commitments/hashes, and provenance necessary for verification.

## Fail-closed classes

`DESTINATION_UNRESOLVED`, `DESTINATION_AMBIGUOUS`, `ADAPTER_UNATTESTED`, `CALIBRATION_MISSING`, `CALIBRATION_STALE`, `OBSERVATION_QUALITY_INSUFFICIENT`, `RECEIVER_EVIDENCE_STALE`, `TRANSLATION_PROVENANCE_INCOMPLETE`, `REQUIRED_ASSERTION_UNRESOLVED`, `PROHIBITED_STATE_PRESENT`, `CANDIDATE_BINDING_FAILED`, `AUTHORIZATION_UNESTABLISHED`, `COMMIT_COHERENCE_FAILED`.

## Scientific boundary

This protocol does not claim that present neurotechnology can reliably address arbitrary neural ensembles, infer complete mental states, establish subjective meaning, or safely write arbitrary information to a selected neural network. Those are empirical adapter capabilities. Unknown biological semantics, ambiguous targeting, or insufficient evidence fail closed rather than being guessed by StegGate.

Conduit Intelligence / Naomi Bashkansky discussion is preserved only as a motivating external application surface; Conduit is not a dependency and no claim is made about its implementation.

## Tests and automation

`tests/test_neural_micronode.py` contains seven focused cases: valid bounded evidence, stale evidence, ambiguous destination, decoder/mapping provenance mismatch, forbidden authority upgrade, false required assertion, and prohibited state.

`.github/workflows/neural-micronode.yml` validates JSON Schema Draft 2020-12 syntax, runs focused tests, and checks authority-boundary literals. It triggers on relevant pushes/PRs and manual dispatch.

Hosted run:

```text
run_id: 31289736205
head_sha: cdd5c7165d603d3dfa8a08effc369baea532fed9
job_id: 93184768876
observed_state: QUEUED
conclusion: PENDING
```

The machine-observable release condition is `run 31289736205` (or a corrective successor) reaching successful conclusion with the test/schema job passing. Failure requires preserving logs and a corrective commit; it must not be treated as success.

## Durable execution inventory

`data/neural-micronode-session-inventory.json` preserves nine primary/adjacent goals, ownership, exact destinations, completion/validation states, collision boundaries, and archive condition.

## Cross-repository / adjacent ownership

- Portable integration target: `src/stegcore/portable_steggate.py`; BLOCKED from mutation in this lane until the portable canonical owner/issue admits nonconflicting integration after hosted neural validation.
- Interop schema propagation target: `StegVerse-Labs/ara-admissibility-interop`; destination-owned and only after `docs/ARA_ADMISSIBILITY_INTEROP_MIRROR_HANDOFF.md` admits it.
- Site, Publisher, admissibility-wiki, stegguardian-wiki: no publication claim. Review is required only if/when this becomes a release/public capability rather than an experimental protocol/runtime boundary.
- No deployment or biological adapter is installed or claimed.

## Validation commands

```text
pytest -q tests/test_neural_micronode.py
python - <<'PY'
import json
from jsonschema import Draft202012Validator
with open('schemas/neural-micronode-packet.schema.json') as f:
    Draft202012Validator.check_schema(json.load(f))
PY
```

## Completion assessment

```text
task_completion: 7/9 goals complete or transferred; hosted validation pending; portable integration blocked/transferred
developed_files: 6/6 current-lane required files installed
scaffolding_or_stubs: 0
missing_required_files: 0
validation: 2/3 classes installed/committed; hosted execution pending
integration: 2/3 current-lane boundaries complete; portable integration not yet admitted
propagation: 0/4 publication surfaces, not yet required for experimental lane
session_consolidation: 9/9 goals durably recorded
archive_readiness: false until hosted result/correction is transferred and this session releases validation role
```

## Archive condition

All unique conceptual requirements are durable. This session currently retains a distinct validation-observation role only because the first hosted run is queued. Once successful hosted evidence is recorded—or failure is durably transferred to a machine-owned corrective lane with no unique chat-only information—the session may merge into this handoff and archive.

Canonical continuation:

```text
MERGED INTO: StegVerse-Labs/StegCore/docs/NEURAL_MICRONODE_GOVERNANCE_MIRROR_HANDOFF.md
issue: StegVerse-Labs/StegCore#71
inventory: data/neural-micronode-session-inventory.json
workflow: .github/workflows/neural-micronode.yml
```
