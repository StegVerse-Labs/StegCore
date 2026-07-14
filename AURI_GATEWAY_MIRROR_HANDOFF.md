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
evidence/auri-gateway-verification.json
```

## Verified invariants

- actor identity must be `stegverse:auri`;
- activation level is constrained to `AURI-L1`;
- Auri execution authority and final consequence authority remain false;
- verified continuity evidence is required;
- missing policy or delegation denies consequential candidates;
- policy shapes may defer through the existing StegCore decision interface;
- candidate hash at evaluation must equal the hash at the commit boundary;
- mismatch denies with no execution;
- every result emits a machine-readable, hash-addressed decision receipt;
- no manual task is required for verification.

## Status

```text
COMPLETE
```

## Verification

```text
python scripts/verify_auri_gateway.py
```

Evidence:

```text
evidence/auri-gateway-verification.json
```

## Result

AURI-004 provides deterministic allow, deny, and defer handling, commit-time equality enforcement, and no-execution decision receipts. It does not verify or mint continuity receipts.

## Manual blockers

```text
None.
```

## Next integration candidate

```text
AURI-005 — StegVerse-Labs/Continuity Auri receipt governance
```

## Archive readiness

AURI-004 is durably complete through implementation, tests, verifier, evidence, and this handoff. No originating conversation context is required to continue.
