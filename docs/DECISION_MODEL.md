# StegCore Decision Model (v0.1)

This document defines the **decision interface** for StegCore.

StegCore answers a single question:

> Is this action permitted right now — and if so, under what constraints?

StegCore does not verify continuity or identity. It consumes verified continuity
output (e.g., from StegID) as an input.

---

## Inputs

### 1) VerifiedReceipt
A verified continuity record produced by an external system (e.g., StegID).

StegCore does not define receipt format or verification logic.
It assumes verification has already succeeded.

Minimum conceptual expectations:
- stable identifier
- verification status = OK
- optional linkage to prior receipt(s)

### 2) Actor Class
One of:
- `human`
- `ai`
- `system`

Actor class provides **context**, not identity.

### 3) Action Intent
A structured request describing what is being attempted.

Recommended fields:
- `action` — stable identifier (e.g., `repo.push`, `policy.change`)
- `target` — resource or scope affected
- `parameters` — optional structured data
- `requested_at` — timestamp
- `urgency` — normal | elevated | emergency (optional)

### 4) Policy Context
A reference to one or more **policy shapes** (defined separately).
In v0.1 this is descriptive, not executable.

---

## Output

StegCore returns a **Decision** object:

- `decision` — `allow` | `deny` | `defer`
- `reason_code` — stable, machine-readable string
- `reason_detail` — optional structured metadata
- `constraints` — optional list of constraints to satisfy

---

## Decision Semantics

### allow
The action is permitted immediately.

### deny
The action is not permitted under current policy context.

### defer
The action is not permitted yet and must satisfy one or more constraints
(quorum, time-lock, guardian review, etc.).

---

## Reason Codes (initial set)

Reason codes are stable and never re-used with different meanings.

### Continuity
- `receipt.missing`
- `receipt.invalid`
- `receipt.insufficient`

### Actor / intent
- `actor.class_missing`
- `intent.missing`
- `intent.unknown`
- `intent.parameter_violation`

### Governance
- `requires.quorum`
- `requires.guardian`
- `requires.veto_window`
- `requires.time_lock`
- `requires.escalation`

### Safety
- `risk.too_high`
- `system.degraded`

---

## Notes

This document defines **interface and meaning**, not enforcement.

If implementation and documentation diverge, **this document wins**.
