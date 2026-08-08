# Action-First Runtime Mirror Handoff

## Active goal

```text
goal_id: STEGCORE-ACTION-FIRST-RUNTIME-001
originating_goal: activate Action-First reconstruction v1 as a bounded StegCore runtime observation producer
repository: StegVerse-Labs/StegCore
branch: feat/action-first-runtime-observation
canonical_owner: issue #65
claim_state: CLAIMED_FOR_IMPLEMENTATION
```

Read `STEGCORE_MIRROR_HANDOFF.md`, this handoff, issue #65, `management/action-first-runtime-task.json`, and the pinned ara schema before changing this lane. Live main state and hosted workflow evidence supersede chat claims.

## Semantic source

```text
StegVerse-Labs/ara-admissibility-interop
d48b2734c2fdb8018271e2413a0d786f6cc5e479
schemas/action-first-reconstruction.v1.json
blob c49f70190ad313e2c849564c411080cd3c7a610f
```

The runtime consumes this semantic contract; it does not duplicate ownership of the interop schema.

## Runtime producer

`src/stegcore/action_first_reconstruction.py` provides `build_action_first_record()`. It consumes an already-produced StegCore `AdapterObservation` plus explicit reconstruction inputs and emits the Action-First v1 record shape.

Implemented boundaries:

- exact action-candidate binding to the runtime decision;
- calculated, realized, and observed state remain distinct;
- model→reality and reality→observation residuals remain distinct;
- unknown residuals cannot invent numeric values;
- unobserved realized transitions remain representable;
- a non-executed runtime decision cannot claim its consequence crossed irreversibility;
- committed execution requires a bounded realized-state identity;
- StegCore records latent/unknown constraint candidates but refuses `PROMOTED` posture;
- `governed_execute()` is not modified;
- Continuity consequence is carried as an externally established value and defaults to `UNKNOWN`;
- no receipt, deployment, publication, standards, or causal-truth authority is created.

## Required files

```text
src/stegcore/action_first_reconstruction.py
tests/test_action_first_reconstruction_runtime.py
docs/ACTION_FIRST_RUNTIME.md
management/action-first-runtime-task.json
docs/ACTION_FIRST_RUNTIME_MIRROR_HANDOFF.md
.github/workflows/action-first-runtime.yml
```

## Validation

The dedicated workflow must prove:

```text
focused Action-First runtime tests: PASS
validator/module compile: PASS
full existing StegCore test suite: PASS through repository-required checks
runtime authority boundary unchanged
```

Hosted evidence must be recorded here after the PR becomes green. Do not infer activation from file presence.

## Integration obligation

After merge to StegCore main, update the ara `ACTION_FIRST_RECONSTRUCTION_MIRROR_HANDOFF.md` on its canonical PR #1 branch so `runtime_activation` points to the exact StegCore merge and hosted evidence. That update is evidence/ownership propagation only and must not claim ara release or publication authority.

## Release condition

The implementation claim is released after:

1. PR is hosted-green and merged to main;
2. current-main StegCore tests remain green;
3. issue #65 records exact merge/workflow evidence;
4. ara Action-First handoff records the runtime producer evidence.

No chat session is required after those durable records exist.
