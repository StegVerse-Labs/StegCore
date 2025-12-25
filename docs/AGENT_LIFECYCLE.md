# StegVerse Agent Lifecycle (v0.1)

This document describes how actions flow through StegVerse systems,
from intent to execution, under verifiable continuity and constraint.

It defines **boundaries**, not implementation.

---

## High-Level Flow

1. Actor forms intent
2. Continuity is verified (StegID)
3. Decision is requested (StegCore)
4. Constraints are evaluated
5. Action is executed, deferred, or denied
6. New signals are emitted (state / receipt)

Each step is isolated by design.

---

## 1) Actor Forms Intent

An actor (human, AI, or system) constructs an **Action Intent**.

The intent is a structured description of what is being requested.
It does **not** grant permission.

Typical fields:
- `action`
- `target`
- `parameters`
- `requested_at`
- `urgency`

The actor may be local, remote, automated, or interactive.

---

## 2) Continuity Is Verified (StegID)

Before any permission decision, the actor must produce
**verified continuity evidence**.

This is handled by **StegID**, not StegCore.

StegID responsibilities:
- mint continuity receipts
- verify receipt chains
- expose verification results

StegCore assumptions:
- receipts presented to it are already verified
- verification semantics are external and opaque

StegCore does **not**:
- mint receipts
- verify signatures
- interpret identity

---

## 3) Decision Is Requested (StegCore)

The actor submits a **Decision Request** to StegCore containing:

- VerifiedReceipt (from StegID)
- Actor class (human / ai / system)
- Action intent
- Policy context (references to policy shapes)

StegCore evaluates the request against its decision model.

This is the **sole responsibility** of StegCore.

---

## 4) Constraints Are Applied

StegCore returns one of three outcomes:

### allow
The action may proceed immediately.

### deny
The action may not proceed.

### defer
The action may proceed only after constraints are satisfied.

Constraints may include:
- quorum approval
- guardian review
- veto window
- time-lock delay
- escalation

StegCore does not enforce constraints directly.
It declares them.

---

## 5) Action Execution

If permitted, the action is executed by the calling system or agent.

Execution occurs **outside** StegCore.

StegCore:
- does not perform actions
- does not retry actions
- does not roll back actions

This separation ensures StegCore remains deterministic
and audit-friendly.

---

## 6) Signals and Continuity Emission

After execution (or failure), systems may emit new signals:

- updated node state (internal audit signals)
- new continuity receipts (via StegID)
- external logs or metrics

StegCore may record internal state/audit signals
(e.g., node health, degraded state),
but continuity truth remains with StegID.

---

## Failure Paths

### Receipt Failure
If continuity verification fails:
- decision request is rejected
- no permission evaluation occurs

### Decision Denial
If StegCore returns `deny`:
- action does not execute
- denial reason is returned

### Decision Deferral
If StegCore returns `defer`:
- constraints must be satisfied
- no execution until resolved

---

## Why This Matters

This lifecycle prevents:
- silent privilege escalation
- irreversible automation errors
- agents acting outside authority

It enables:
- accountability
- recoverability
- constrained autonomy

---

## Stability

This lifecycle is intended to remain valid
even as implementations evolve.

If code and this document diverge,
**this document wins**.
