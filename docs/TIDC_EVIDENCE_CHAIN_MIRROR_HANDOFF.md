# TIDC Evidence-Chain Ecosystem Mirror Handoff

## Target

```text
source_repo: StegVerse-Labs/Site
management_repo: StegVerse-Labs/StegCore
layer: blinded second-coding evidence chain
```

## Determination

The Site-level TIDC blinded-return layer and the StegCore management layer are built and activated. The prior management posture incorrectly allowed one missing serial artifact to appear as an external blocker capable of halting development.

That posture is superseded.

There are no unowned external tasks in this layer. Every task must have an owner repository, a concrete location, an observable completion condition, and either an active or conditionally executable state.

## Active observer and advancement layer

```text
observer_script: scripts/observe_and_advance_tidc_evidence_chain.py
observer_workflow: .github/workflows/observe-and-advance-tidc-evidence-chain.yml
observation_receipt: brain_reports/tidc_evidence_chain_observation.json
cadence: hourly and workflow_dispatch
registry: ecosystem_management/tidc_evidence_chain_registry.json
```

The observer inspects the authoritative `StegVerse-Labs/Site` evidence-chain paths, identifies the first incomplete serial state, and emits the next executable tasks with their owner repositories and exact locations.

## Non-halting rule

```text
missing serial-chain artifact
!=
permission to stop unrelated or preparatory development
```

A waiting serial state cannot suppress:

- primary-source expansion in `StegVerse-Labs/Site/data/tidc/source-expansion/`;
- negative controls in `StegVerse-Labs/Site/data/tidc/negative-controls/`;
- tranche 02 preparation in `StegVerse-Labs/Site/data/tidc/tranche-02/`;
- observer and verification hardening in `StegVerse-Labs/StegCore/scripts/` and `.github/workflows/`;
- downstream verification preparation in `StegVerse-Labs/StegCore/ecosystem_management/`.

## Authoritative Site records

```text
Site issue: #126
activation_commit: 32f2e2111c5d49678659960a7a7ad1784c6a432f
packet: data/tidc/blinded-coding/BCP-2026-07-27-01.md
workflow: .github/workflows/check-tidc-research.yml
return_validator: scripts/validate_tidc_blinded_return.py
receipt_generator: scripts/create_tidc_blinded_return_receipt.py
comparison_engine: scripts/compare_tidc_blinded_coding.py
adjudication_protocol: docs/TIDC_BLINDED_CODING_ADJUDICATION_PROTOCOL.md
```

## State machine

```text
SITE_LAYER_BUILT
-> SITE_LAYER_ACTIVATED
-> OBSERVER_ACTIVE
-> RETURN_PRESERVED
-> STRUCTURAL_VALIDATION_PASSED
-> RECEIPT_GENERATED
-> COMPARISON_GENERATED
-> DISAGREEMENTS_RECORDED
-> ADJUDICATION_STATUSES_ASSIGNED
-> RELEASE_2_ACTIVE
-> DOWNSTREAM_MIRRORS_VERIFIED
-> ARCHIVE_READY
```

Current state:

```text
SITE_LAYER_ACTIVATED
STEGCORE_MANAGEMENT_ACTIVATED
OBSERVER_ACTIVE
PARALLEL_ADVANCEMENT_ACTIVE
DEVELOPMENT_HALTED=false
```

## Completion criteria

The ecosystem layer is operationally complete when:

1. the serial evidence state is observed automatically;
2. no missing serial artifact halts parallel development;
3. any produced return is preserved without repair;
4. Site CI validates it;
5. receipt and comparison artifacts are preserved;
6. every disagreement has a recorded status;
7. Release 2 is advanced only under the declared boundary;
8. downstream public mirrors are checked;
9. an archive-readiness receipt is committed.

## Authority boundary

StegCore may observe, route, verify, and advance tasks. It may not invent evidence, adjudicate research classifications by management fiat, convert AI coding into human replication, or promote a research note into proof.

## Archive rule

Archive readiness is determined from the committed observation and completion receipts, not from an idle-status label. Do not announce archive readiness until the serial chain and downstream checks are complete.
