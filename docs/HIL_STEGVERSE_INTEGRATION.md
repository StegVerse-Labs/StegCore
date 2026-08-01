# Humans as the Interoperability Layer — StegVerse Integration

Status: ACTIVE BUILD
Updated: 2026-08-01

## Decision

The HIL lifecycle is a StegVerse ecosystem capability, not a disconnected Site experiment.

StegCore owns the ecosystem-level transition contract that binds:

1. participant-facing intake and lifecycle projection in `StegVerse-Labs/Site`;
2. exact-byte custody, reconstruction, and private-review handoff in `StegVerse-Labs/TVC`;
3. validation-only Master Record assembly in `master-records/orchestration`;
4. later publication and downstream projection only after separate authority is granted.

## Current authoritative tasks

- `StegVerse-Labs/Site#81` — hosted receiver, durable storage, readiness, controlled browser submission, restart persistence.
- `StegVerse-Labs/TVC#8` — exact-byte lifecycle handoff, authenticated private review, negative tests.
- `master-records/orchestration#13` — validation-only HIL Master Record candidate contract.
- `StegVerse-Labs/Site#67` — participant-visible lifecycle projection and activation checks.

## Canonical transition sequence

```text
PARTICIPANT_RECORD_CREATED
→ RECEIVED_BY_STEGVERSE
→ EXACT_BYTES_VERIFIED
→ RECONSTRUCTED_HASH_VERIFIED
→ QUEUED_FOR_PRIVATE_REVIEW
→ ACCEPT_PRIVATE | QUARANTINE | REJECT
→ MASTER_RECORD_CANDIDATE_VALIDATED
→ PUBLICATION_DECISION_PENDING | PUBLICATION_AUTHORIZED | PUBLICATION_DENIED
→ RELEASE_PENDING | RELEASE_AUTHORIZED | RELEASE_DENIED
```

No state may be skipped. No lower layer may grant authority owned by a later layer.

## Current evidence anchor

```text
submission_id: HIL-20260731-GPT56-001
response_sha256: 1442c8407e6de8c66d1aa6d5180779a4c58cb449a46338bc9dae07e5ddf99285
TVC receipt: HIL-TVC-1442c8407e6de8c6
TVC state: RECONSTRUCTED_HASH_VERIFIED
publication_authorized: false
release_authorized: false
```

## StegCore activation responsibilities

StegCore must:

1. validate monotonic HIL state progression;
2. reject contradictory receipts or authority flags;
3. require exact identity continuity across Site, TVC, and Master Records;
4. preserve participant consent separately from review, publication, and release decisions;
5. expose the current lifecycle state without claiming unavailable custody or authority;
6. emit an activation decision only when all required upstream receipts validate.

## Current activation posture

```text
StegVerse ecosystem integration: STARTED
StegCore transition contract: DEFINED
hosted receiver activation: PENDING
private-review lifecycle: BUILDING
Master Record candidate validation: BUILDING
participant lifecycle projection: BUILDING
publication authority: NOT GRANTED
release authority: NOT GRANTED
```

## Completion condition

This layer becomes activatable only when:

- Site #81 proves hosted durable custody and restart persistence;
- TVC #8 emits a valid write-once private-review lifecycle receipt;
- Master Records #13 validates the same evidence identities;
- Site #67 projects the same lifecycle without contradiction;
- StegCore validates the complete transition chain.
