# Action-First Runtime Observation

StegCore exposes a bounded runtime producer for the Action-First reconstruction record defined by the pinned interop schema in `StegVerse-Labs/ara-admissibility-interop`.

The producer consumes an existing `AdapterObservation` and caller-supplied reconstruction inputs. It preserves three distinct identities: calculated state, realized state, and observed state. It separately records the model→reality residual and the reality→observation residual, binds the preserved admissibility-matrix reference and action candidate, records the point of irreversibility, and carries observer coverage, constraint candidates, reconstruction posture, continuity consequence, and viability horizon.

This API is observational. It does not alter `governed_execute()`, admit an action, create execution authority, turn an ALLOW decision into continuity, promote a latent constraint into Governance truth, verify signatures, mint Continuity receipts, or claim an empirical Reconstruction Singularity.

Canonical semantic source:

```text
repository: StegVerse-Labs/ara-admissibility-interop
commit: d48b2734c2fdb8018271e2413a0d786f6cc5e479
schema: schemas/action-first-reconstruction.v1.json
blob: c49f70190ad313e2c849564c411080cd3c7a610f
schema_version: stegverse.action-first-reconstruction.v1
```

## Runtime boundary

`build_action_first_record()` requires the action-candidate reference to bind to the runtime decision candidate. A runtime decision that did not invoke the executor cannot claim that its consequence crossed the irreversibility boundary. Residuals marked `UNKNOWN` or `NOT_COMPUTABLE` cannot carry invented numeric values. The runtime can record `NONE`, `CANDIDATE`, or `TESTABLE` constraint-promotion posture; `PROMOTED` is refused because Governance owns the promotion decision.

An unobserved realized transition remains representable: the realized state may retain its state identity while the observed state remains `UNOBSERVED` with a non-computable observation residual. This preserves the distinction between reality and the system's ability to establish reality.
