# Neural Micro-Node Governance Mirror Handoff

Status: ACTIVE SPECIFICATION — implementation not claimed
Date: 2026-08-08
Repository: `StegVerse-Labs/StegCore`

## Governing source

This continuation inherits the portable/ephemeral micro-node topology and the network-governance review. It does not alter their authority boundaries.

Authoritative predecessors:

- `docs/STEGGATE_NETWORK_GOVERNANCE_MIRROR_HANDOFF.md`
- `docs/STEGGATE_PORTABLE_MICRONODE.md`
- `docs/STEGGATE_PRODUCT_REVIEW_V4.md`

## Goal

Define how StegVerse least-stable micro-node transport can address a bounded neural receiver while preserving the distinction between observed neural evidence, interpreted state, authorization, admissibility, and consequence.

The BCI, sensor, stimulator, decoder, encoder, or other interface is transport/translation infrastructure. It is not automatically the receiver and it is not automatically an authority.

The receiver is the specifically addressed downstream neural micro-node: a bounded neural region, ensemble, pathway, or other experimentally supportable functional target for the transition.

## Core transport statement

```text
source micro-node
  -> payload candidate + transition requirements
  -> transport / neural interface
  -> addressed neural micro-node
  -> receiver observation/signature
  -> bounded admissibility translation
  -> transition-relative evidence
  -> ALLOW | DENY | REVIEW | FAIL_CLOSED
  -> consequence or non-consequence
  -> receipt
```

The receiver signature is not itself a governance decision. The signature is translated into only the admissibility evidence required by the particular proposed transition.

## Receiver-relative admissibility

Let `N_d` be the addressed destination neural micro-node, `sigma(N_d,t)` an observation/signature at observation time `t`, `P` the payload candidate, and `R_T` the requirements for transition `T`.

```text
A_T = translate(sigma(N_d,t), P, R_T)
decision = evaluate(P, R_T, A_T)
```

`A_T` is deliberately bounded. It MUST NOT be interpreted as a complete representation of the receiver, person, cognition, mental state, intent, or identity.

The same payload directed to different micro-nodes can require different admissibility packages:

```text
P -> N1 requires R1
P -> N2 requires R2
P -> N3 requires R3
```

Likewise, the same neural signature can produce different admissibility evidence for different proposed transitions because admissibility is transition-relative.

## Required distinctions

A conforming neural adapter MUST preserve these non-equivalences:

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

No decoder confidence score can collapse these boundaries.

## Minimal ephemeral governance packet

A neural micro-node packet SHOULD contain no more governance state than necessary to evaluate the addressed transition. Candidate fields:

```json
{
  "profile": "steggate.neural-micronode.v0",
  "transition_id": "...",
  "source": {"micro_node_id": "..."},
  "destination": {
    "receiver_class": "neural_micro_node",
    "receiver_locator": "adapter-defined-bounded-target",
    "locator_profile": "..."
  },
  "payload": {
    "candidate_hash": "...",
    "semantic_profile": "..."
  },
  "requirements": {
    "required_assertions": [],
    "prohibited_assertions": [],
    "freshness_ms": 0,
    "minimum_observation_quality": "..."
  },
  "translation": {
    "adapter_profile": "...",
    "model_or_mapping_id": "...",
    "calibration_ref": "..."
  },
  "expiry": "..."
}
```

The `receiver_locator` is adapter-defined because current neuroscience does not justify pretending that a universal neural addressing scheme exists.

## Inbound neural transition

For machine/external -> neural transport:

1. Construct payload candidate.
2. Identify the bounded destination supported by the adapter.
3. Derive the minimum receiver-state predicates required for this transition.
4. Observe the destination through the interface.
5. Translate the observation into bounded transition-relative evidence.
6. Fail closed if addressability, calibration, freshness, evidence quality, or required predicates cannot be established.
7. Admit or refuse the transition.
8. If admitted, permit the adapter to perform only the consequence class explicitly authorized by the packet.
9. Observe consequence when technically possible.
10. Emit a receipt and terminate the ephemeral governance instance.

## Outbound neural transition

For neural -> machine/external transport, observed neural activity is never directly elevated to execution authority:

```text
neural observation
 -> candidate reconstruction
 -> reconstruction provenance
 -> bounded interpretation
 -> proposed payload
 -> destination requirements
 -> authorization/admissibility
 -> commit-time check
 -> consequence
```

The decoder is therefore a candidate generator/evidence producer, not an authority source merely because its reconstruction confidence is high.

## Translation provenance

Because a learned decoder can introduce priors not present in the observed signal, every translated assertion SHOULD preserve:

- observation reference/hash;
- adapter identity/profile;
- decoder/model/mapping identity;
- calibration reference;
- confidence or uncertainty where meaningful;
- observation timestamp and freshness;
- transformation chain;
- assertion scope;
- explicit statement of what is not established.

A translated assertion MUST NOT silently upgrade `correlated_with`, `predicted_as`, or `classified_as` into `intended_by`, `authorized_by`, or `consented_to_by`.

## Commit boundary

Neural transport does not eliminate the commit boundary. It creates additional pre-commit evidence boundaries.

For consequential outbound action, the minimum chain is:

```text
observation -> reconstruction -> candidate -> authorization -> admissibility -> commit coherence -> consequence
```

For consequential inbound stimulation or delivery, the minimum chain is:

```text
candidate -> destination resolution -> receiver evidence -> admissibility -> consequence -> observation
```

## Fail-closed classes

At minimum:

- `DESTINATION_UNRESOLVED`
- `DESTINATION_AMBIGUOUS`
- `ADAPTER_UNATTESTED`
- `CALIBRATION_MISSING`
- `CALIBRATION_STALE`
- `OBSERVATION_QUALITY_INSUFFICIENT`
- `RECEIVER_EVIDENCE_STALE`
- `TRANSLATION_PROVENANCE_INCOMPLETE`
- `REQUIRED_ASSERTION_UNRESOLVED`
- `PROHIBITED_STATE_PRESENT`
- `CANDIDATE_BINDING_FAILED`
- `AUTHORIZATION_UNESTABLISHED`
- `COMMIT_COHERENCE_FAILED`

## Privacy/minimization rule

Raw neural observations SHOULD remain local to the neural adapter whenever the transition can be governed using derived bounded assertions. Transport the minimum assertion set, commitments, hashes, and provenance necessary for verification rather than raw neural data by default.

This follows least-stable micro-node construction: minimize capability, lifetime, retained state, and disclosure together.

## Safety / scientific boundary

This specification does not claim that present neurotechnology can reliably address arbitrary neural ensembles, infer complete mental states, establish subjective meaning, or safely write arbitrary information to a selected neural network. Those are empirical capabilities that adapters must independently establish.

The protocol defines how governance behaves if and only if a bounded observation/consequence interface is supportable. Unknown biological semantics, ambiguous targeting, or insufficient evidence are fail-closed conditions, not values to be guessed by StegGate.

## Implementation targets

Destination: `StegVerse-Labs/StegCore`

Needed next:

1. `schemas/neural-micronode-packet.schema.json`
2. `src/stegcore/neural_micronode.py` adapter-neutral evaluator
3. `tests/test_neural_micronode.py`
4. fixtures for positive, stale, ambiguous-destination, decoder-prior/provenance, and unauthorized-outbound cases
5. integration with `portable_steggate.py` without granting the adapter policy authorship or execution authority
6. hosted validation and receipt

Potential later schema/interop destination: `StegVerse-Labs/ara-admissibility-interop`, only after its live handoff admits the work.

## Completion state

```text
specification: INSTALLED
schema: NOT_STARTED
runtime: NOT_STARTED
tests: NOT_STARTED
hosted_validation: NOT_STARTED
interop_propagation: NOT_STARTED
release: NOT_READY
```

This handoff is the current task source of truth for the neural micro-node continuation until merged into a broader canonical handoff.
