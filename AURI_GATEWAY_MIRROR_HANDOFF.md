# Auri StegCore Gateway Mirror Handoff

## Target

```text
Organization: StegVerse-Labs
Repository: StegCore
Task: AURI-004
Purpose: externally evaluate AURI-L1 advisory candidates without granting Auri execution authority
```

## Source of truth

This file is the authoritative sub-handoff for AURI-004. The ecosystem-level source remains `StegVerse-Labs/StegTalk/AURI_MIRROR_HANDOFF.md`.

## Boundary

Auri may submit advisory candidates and explain results. StegCore evaluates already-verified continuity evidence and policy posture. Neither this gateway nor Auri verifies or mints continuity receipts. AURI-L1 never executes consequence.

## Deliverables

```text
src/stegcore/auri_gateway.py
tests/test_auri_gateway.py
scripts/verify_auri_gateway.py
```

## Required invariants

- actor identity must be `stegverse:auri`;
- activation level must be `AURI-L1`;
- Auri execution authority must be false;
- verified continuity evidence is required;
- missing policy or delegation denies consequential candidates;
- policy shapes may defer through the existing StegCore decision interface;
- candidate hash at evaluation must equal the hash at commit boundary;
- mismatch denies with no execution;
- every result emits a machine-readable decision receipt;
- no manual task is required for verification.

## Status

```text
IN PROGRESS
```

## Current claim

```text
AURI-004 — gateway implementation and verifier
```

## Manual blockers

```text
None.
```

## Next integration candidate

```text
AURI-005 — Continuity / StegID Auri receipt governance
```

## Archive readiness

This handoff and committed verification evidence are sufficient to continue AURI-004 without access to the originating conversation.
