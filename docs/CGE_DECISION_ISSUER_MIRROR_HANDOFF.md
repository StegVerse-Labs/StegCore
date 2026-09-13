# CGE Decision Issuer Mirror Handoff

Updated: 2026-09-13
Repository: `StegVerse-Labs/StegCore`
Architecture decision source: `StegVerse-Labs/Governance:evidence/cge-decision-issuer-architecture/latest.json`
Canonical gap: `MR.GAP.CGE_DECISION_ISSUER.001`

## Ownership

StegCore owns CGE/admissibility decision issuance because the canonical StegGate + three-layer evaluator already owns admissibility judgment. This does not move canonical state-transition execution into StegCore.

```text
CGE decision issuer: StegVerse-Labs/StegCore
closure custody/reconstruction: Master Records
transition executor: Interlock/InTr
credential/provider/grant authority: TV/TVC
Governance: architecture/policy coordination, not runtime issuer
GitHub: source/validation only
```

## Installed source

- `src/stegcore/cge_decision_issuer.py`
- `scripts/issue_cge_service_decision.py`
- `tests/test_cge_decision_issuer.py`

The issuer accepts one exact TVC service route, matching authentic authority evidence, and one complete canonical StegGate `AdmissibilityRequest` assembled from current evidence. It validates the authority-evidence hash and route identity, evaluates through `stegcore.steggate.evaluate_admissibility`, and emits:

1. Master Records `authority_context_receipt.v0.1` compatible receipt;
2. Master Records `commit_time_admissibility_receipt.v0.1` compatible receipt;
3. externally consumable `stegverse.cge_admissibility_decision/1.0.0` bound to the route + authority evidence;
4. full StegCore evaluation evidence.

## Decision mapping

```text
StegCore ALLOW       -> TVC admissibility ADMIT -> CGE_REVIEW_ACCEPTED
StegCore DENY        -> TVC admissibility DENY  -> CGE_REVIEW_DENIED
StegCore REVIEW      -> TVC admissibility DEFER -> CGE_REVIEW_DEFERRED
StegCore FAIL_CLOSED -> TVC admissibility DEFER -> CGE_REVIEW_BLOCKED
```

Only `ALLOW` carries execution scope. The CGE decision itself never grants TVC execution authority; TVC must separately bind the decision, issue its own bounded single-use grant, and authorize the exact operation.

## Separation invariant

```text
issuer executes transition: false
issuer mutates canonical state: false
issuer issues TVC grant: false
issuer performs provider operation: false
issuer performs relay transport: false
master_records_custody_required: true
transition_executor: Interlock/InTr
```

Missing, stale, invalid, or unknown authority/policy/evidence state fails closed through the canonical StegGate evaluator or issuer preflight.

## Runtime continuation

For sovereign control-plane source transport:

```text
content-addressed stegverse.control-plane package
-> TVC service route
-> authentic TV/TVC authority evidence
-> canonical StegGate request assembled from current route/binding/package/continuity evidence
-> this CGE issuer
-> TVC bind_service_admissibility.py
-> TVC bounded relay authorization entrypoint
-> existing WorkerCoordinator / StegOS sovereign relay transport
-> far-side /intr/source-package materialization
```

Source validation does not prove a live CGE decision or transport execution.
