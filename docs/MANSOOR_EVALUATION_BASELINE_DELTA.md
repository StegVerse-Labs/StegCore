# Mansoor Evaluation Baseline Delta

## Frozen evaluation reference

```text
product: AdmittedCode / StegGate 0.2.0
baseline commit: 5d86d7999199b9403a05320710c4d1bb95527327
evaluation branch: eval/mansoor-admittedcode-0.2.0-2026-08-11
canonical runtime identity: stegverse:steggate:canonical:three-layer:v1
canonical evaluator: stegcore.three_layer.evaluate_three_layer
```

The evaluation reference is immutable. Later `main` development does not retroactively alter what Mansoor reviewed.

## Post-freeze development finding

After the evaluation baseline was frozen, development re-identified an intended but incompletely canonicalized SDK/LLM-adapter capability: an incoming test/runtime transaction should be manifested, admitted through ingestion, routed through the ordinary canonical StegGate boundary, re-ingested on return, and exposed as a discoverable/replayable/reconstructable transaction trajectory.

The historical `core/llm_adapter.py` already documented candidate persistence for replay/audit, receipt emission, and routing to ingestion/quarantine/review. The later canonical StegGate runtime strengthened evaluation and execution boundaries but did not yet preserve the complete manifested transaction lifecycle around that evaluator.

## Decision

Development will correct the gap without mutating the frozen 0.2.0 evaluation branch.

This is not conditioned on reviewer agreement. Evaluation independence controls evidence preservation and attribution, not development authority.

## Compatibility boundary

The intended forward path is additive:

```text
manifest / ingestion / transaction discovery
  -> existing AdmissibilityRequest
  -> existing canonical StegGate semantics
  -> existing governed execution + commit coherence
  -> return ingestion / replay / reconstruction envelope
```

The following remain protected unless explicitly versioned forward:

- canonical runtime identity;
- canonical evaluator authority;
- candidate-hash semantics;
- ALLOW / DENY / REVIEW / FAIL_CLOSED precedence;
- commit-coherence requirement;
- rule that transport, SDK, UI, manifest, and application state are not policy authority.

Any change to those semantics is contract-affecting and must version forward rather than being represented as a correction to Mansoor's frozen reference.

## Reviewer attribution rule

If Mansoor independently identifies the same missing transaction-envelope/discoverability/replay/reconstruction problem, his finding remains an independent evaluation result. It must not be downgraded because development discovered or corrected the issue after the baseline freeze.

If his finding differs from the forward correction, retain both the review observation and the implementation decision as separate evidence.

## Timeline rule

Future evaluation records should be able to answer:

1. what exact build the reviewer observed;
2. what finding the reviewer made;
3. when development independently discovered the same or related condition;
4. what subsequent implementation changed;
5. whether replay reproduces the original finding against the frozen build;
6. whether the corrected build changes the resulting trajectory.

That timeline is the basis for preventing a moving-goalpost interpretation while allowing development to continue.
