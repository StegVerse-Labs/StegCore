# Neural End-to-End Validation Plan

Goal: `STEGCORE-NEURAL-ENDTOEND-002`

## Validation classes

1. **Static composition** — required canonical calls and non-activation boundaries exist.
2. **Deterministic physical model** — READ/WRITE channel eligibility fails closed on unresolved targets, invalid calibration, envelope violations, weak channel evidence, and weak observation evidence.
3. **Full governance integration** — neural evidence and physical eligibility are admitted only as evidence references; canonical StegGate and commit coherence remain authoritative.
4. **Hosted execution** — GitHub Actions runs predecessor and end-to-end tests and records inspectable job/log evidence.

## Required positive proof

A positive fixture may execute only a `software_model_only` consequence after:

```text
candidate hash exact
AND neural boundary ALLOW
AND physical channel ELIGIBLE
AND canonical StegGate ALLOW
AND commit coherence ALLOW
```

The receipt must include neural decision hash, physical decision hash, StegGate decision-state hash, and commit receipt hash.

## Required negative proofs

At minimum:

- candidate mismatch -> fail closed before consequence;
- neural decoder assertion cannot become authorization;
- physical intensity outside adapter-declared normalized envelope -> fail closed;
- canonical policy denial -> consequence unreachable;
- commit coherence denial -> consequence unreachable;
- missing commit authority -> consequence unreachable;
- weak READ observation -> fail closed.

## Activation boundary

Passing this plan validates the **software governance and physical-channel abstraction only**. It does not validate a human neural target, hardware adapter, stimulation waveform, biological dosage, semantic encoding, semantic decoding, or medical safety.
