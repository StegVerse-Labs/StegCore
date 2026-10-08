# Cross-Framework Current-Basis Native Derivation Mirror Handoff

Updated: 2026-08-29
Repository: `StegVerse-Labs/StegCore`
Issue: #161
Branch: `feat/current-basis-neutral-derivation-161`
Parent handoff: `STEGCORE_MIRROR_HANDOFF.md`

## Goal

Provide the StegVerse-native derivation surface for the exact frozen cross-framework current-basis v0.4 test without changing the frozen common artifact and without creating a second evaluator.

Frozen external/common identity:

```text
test_id: cross-framework-current-basis-001
vector_schema: stegverse.cross-framework-current-basis-vector.v0.4
manifest_sha256: 07a08496c21b31f70f6f45ef731aa5f6b2522a6fc8f67f2d0a4c2b6fceda7a3f
manifest_git_blob_sha1: 59d818a15fc7be732c97dae7d2174d8cfe9a7bab
SDK lane: StegVerse-org/StegVerse-SDK#94
```

## Governing test semantics

Absent explicitly supplied prior-state data, S0 is the declared initial testing state. No historical receipt is required to establish S0.

The common v0.4 artifact freezes neutral S1 observed-input facts. StegCore must independently derive its native request fields. Material policy change alone MUST NOT be converted into an input assertion that the policy is invalid or non-current. A native currentness field for which the frozen facts do not establish currentness remains unknown/unestablished in the derived StegCore request.

The S0->S1 transition receipt is post-observation evidence. This derivation/evaluation surface does not pre-mint it.

## Authority boundary

```text
canonical evaluator: stegcore.steggate.evaluate_admissibility
parallel evaluator: PROHIBITED
SDK-local disposition logic: PROHIBITED
external consequence: NONE
credential authority: TV/TVC
GitHub runtime authority: NONE
Master Records organization record: separate downstream runtime step
```

## Implementation target

```text
src/stegcore/current_basis.py
tests/test_current_basis.py
```

The module maps the frozen neutral vector into `AdmissibilityRequest`, preserving unknown native currentness as unestablished values, then calls the existing canonical `evaluate_admissibility`. It returns the native request and canonical evaluation as observable architecture evidence; it does not reinterpret the disposition.

## Completion gates

```text
specialized handoff: CREATED
native derivation source: PENDING
focused deterministic tests: PENDING
hosted source validation: PENDING
merge to main: PENDING
SDK thin-client integration: PENDING
authentic independent run: NOT OBSERVED
S1 transition receipt: NOT PRESENT / correctly post-observation
Master Records organization record/reconstruction: NOT PRESENT
cross-framework comparison: NOT PERFORMED
```
