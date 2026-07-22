# StegCore Recreation Gate Mirror Handoff

## Purpose

This is the authoritative continuation record for the StegCore integration of `SV-CONTINUITY-109` from `StegVerse-Labs/Continuity`.

It does not supersede the StegVA handoff or the private boundary-review handoff. It establishes a separate neutral-named workstream for recreation-gate admissibility.

## Current Goal

```text
Goal: Map 109% recreatable continuity evidence into fail-closed StegCore admissibility.
Repository: StegVerse-Labs/StegCore
Source repository: StegVerse-Labs/Continuity
Protocol: SV-CONTINUITY-109
Activation state: executable_candidate
```

## Built Files

```text
docs/STEGCORE_RECREATION_GATE_MIRROR_HANDOFF.md
schemas/recreation-gate-request.schema.json
schemas/recreation-gate-receipt.schema.json
examples/recreation-gate.allow.json
examples/recreation-gate.block-unresolved-divergence.json
examples/recreation-gate.block-stale-authority.json
scripts/evaluate_recreation_gate.py
.github/workflows/validate-recreation-gate.yml
```

## Required Inputs

```text
trusted_pre_state_hash
recreated_state_hash
candidate_state_hash
recreation_complete
recovery_proof_complete
verification_margin_complete
external_exposures_complete
divergence_detected
divergence_resolution_status
authority_current
consent_current
policy_current
unresolved_conditions_evaluated
continuity_receipt_ref
recovery_receipt_ref
divergence_report_ref
```

## Fail-Closed Rule

The gate returns `BLOCK` when any required proof is absent or false, trusted and recreated state hashes differ, exposure completeness is false, current authority/consent/policy is not established, unresolved conditions were not evaluated, or divergence remains unresolved.

External AI output is never authoritative merely because it was returned to a governed node.

## Executable Proof Path

```text
Continuity recreation evidence
→ request schema validation
→ hash equality check
→ recreation and recovery proof checks
→ external exposure completeness check
→ divergence resolution check
→ authority, consent, and policy freshness checks
→ unresolved-condition evaluation check
→ StegCore ALLOW or BLOCK receipt
```

The workflow proves:

- complete evidence produces `ALLOW`;
- unresolved divergence produces `BLOCK`;
- stale authority produces `BLOCK`;
- request and receipt schemas validate on Python 3.11 and 3.12.

## Build Queue

```text
SC-RG-001 COMPLETE: repository-local mirror handoff
SC-RG-002 COMPLETE: recreation-gate request schema
SC-RG-003 COMPLETE: admissibility receipt schema
SC-RG-004 COMPLETE: ALLOW example
SC-RG-005 COMPLETE: BLOCK examples
SC-RG-006 COMPLETE: fail-closed validator
SC-RG-007 COMPLETE: workflow validation harness
SC-RG-008 PENDING: durable Continuity-to-StegCore transfer receipt
SC-RG-009 PENDING: workflow success evidence and release candidate
```

## Definition of Done

The integration is complete when a machine-readable request can be validated, evaluated fail-closed, and converted into a StegCore admissibility receipt without chat memory or cooperation from an ungoverned external entity, and the cross-repository transfer is durably receipted.

## Next Actions

1. Add a Continuity-to-StegCore transfer receipt naming exact source and destination artifacts.
2. Confirm workflow success.
3. Update the Continuity mirror handoff to mark StegCore integration complete.
4. Prepare release and destination verification tasks for Site, Publisher, admissibility-wiki, and stegguardian-wiki.

## Non-Claims

This workstream does not claim third-party certification, external endorsement, or compatibility with any third-party standard.

## Progress Snapshot

```text
StegVerse-Labs - 66% complete
StegCore - 92% fully developed files vs scaffolding and stubs
StegCore recreation gate - 88% complete TO GOAL ACTIVATION
Delta: request/receipt schemas, ALLOW and BLOCK examples, fail-closed evaluator, and cross-version workflow are built. Transfer receipt and successful workflow evidence remain.
Thread archive state: READY after repository artifacts preserve the task.
```
