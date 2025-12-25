# Policy Shapes (v0.1)

Policy shapes define **how decisions are constrained**, not what the rules are.

They are structural primitives that remain stable over time.

---

## Quorum

Requires multiple approvals before an action may proceed.

Common attributes:
- approval threshold
- eligible approvers
- scope
- expiration

Typical outcome:
- `defer` + `requires.quorum`

---

## Guardian

Assigns review authority to a designated guardian role.

Common attributes:
- guardian set
- review mode (approve / challenge / block)
- audit requirements

Typical outcome:
- `defer` + `requires.guardian`

---

## Veto

Allows designated actors to block an action during a defined window.

Common attributes:
- veto set
- veto window duration
- effect of veto (deny / escalate)

Typical outcome:
- `defer` + `requires.veto_window`

---

## Time-lock

Enforces a delay before an action may execute.

Common attributes:
- delay duration
- cancellation authority
- justification

Typical outcome:
- `defer` + `requires.time_lock`

---

## Escalation

Routes a decision to a higher authority or broader context.

Common attributes:
- escalation levels
- triggers
- resolution modes

Typical outcome:
- `defer` + `requires.escalation`

---

## Composition

Shapes may be composed:
- quorum + time-lock
- guardian + veto
- veto → escalation

---

## Stability Principle

Policy shapes should change rarely.
Rules may evolve; shapes should not.
