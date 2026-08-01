# Personal Data Control Decision Boundary

StegCore evaluates whether a proposed personal-data transition may cross the consequence-bearing commit boundary. It does not identify people, store personal data, contact controllers, delete data in external systems, or mint continuity receipts.

## Purpose

The decision boundary prevents a request from being treated as completed merely because a user possesses a theoretical right or an upstream component produced a request object.

A transition is admissible only when the proposed next state preserves the requester's authority, keeps denial and appeal reachable, and records what remains unresolved.

## Governed request states

```text
NOT_REQUESTED
RECEIVED
IDENTITY_VERIFICATION_REQUIRED
VERIFIED
PROCESSING_RESTRICTED
INVENTORY_COMPLETE
DELETION_IN_PROGRESS
PROCESSOR_PROPAGATION_PENDING
COMPLETED
PARTIALLY_DENIED
DENIED
APPEAL_OPEN
CHANNEL_FAILED
```

## Decision outcomes

```text
ALLOW  - the proposed transition is coherent and may be committed by an authorized executor
DENY   - the proposed transition would erase authority, overstate completion, or bypass required evidence
DEFER  - the transition remains addressable but lacks required evidence for commitment
```

## Minimum predicates

A transition to `COMPLETED` must prove:

```text
request identity bound
scope inventory complete
eligible local deletion complete
retained-data basis recorded
processor propagation resolved or explicitly bounded
completion receipt reference present
appeal path preserved
```

A missing controller or processor response is represented as `CHANNEL_FAILED` or `PROCESSOR_PROPAGATION_PENDING`. Those states do not halt StegCore development and must not be rewritten as unnamed external tasks.

## Task location contract

Every implementation task for this layer must name:

```text
task id
repository
implementation paths
verification paths
executable validator
completion predicate
status receipt
```

## Authority boundary

```text
StegCore ALLOW != external deletion performed
StegCore DENY != legal adjudication
receipt reference != receipt verification
request state != identity proof
processor pending != development blocker
CI PASS != production activation
```
