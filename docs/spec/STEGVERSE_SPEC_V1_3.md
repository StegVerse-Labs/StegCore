# StegVerse Specification v1.3 — Consolidated Staging Draft

**Status:** conceptual research specification; not production authority, formal verification, or peer-reviewed proof.

## 1. Purpose

StegVerse defines a control-plane architecture for consequence-bearing autonomous systems. Its central claim is architectural rather than behavioral: authority, consent, admissibility, execution, and reconstructability should be enforced and evidenced by infrastructure rather than assumed from model intent.

## 2. Architecture

```text
Human Authority
      |
      v
Control Plane
  identity, policy, delegation, consent
      |
      v
Decision Surface
  pre-execution admissibility evaluation
      |
      v
Data Plane
  agents, models, automation
      |
      v
Execution Layer
  APIs, tools, infrastructure, physical effects
      |
      v
Audit / Replay
  receipts, state evidence, reconstruction, compensation
```

No data-plane action may bypass the decision surface and directly acquire execution standing.

## 3. State Model

Let the evaluated system state be:

```text
s = (A, P, I, C, E, R)
```

where:

- `A` is the accredited authority and delegation state;
- `P` is the applicable policy state and version;
- `I` is the identity and actor-binding state;
- `C` is the relevant operational context;
- `E` is the execution environment and reachable effect surface;
- `R` is the recoverability and evidence state.

A proposed action is `a`.

## 4. Decision Surface

The decision function is:

```text
D(a, s) -> {ALLOW, DENY, FAIL_CLOSED}
```

An `ALLOW` result is a commitment candidate, not proof that execution occurred or remained admissible at commit time.

The decision receipt should bind at least:

```text
transition_id
action
actor_identity
actor_authority
scope
policy_reference
policy_version
delegation_reference
consent_reference
evidence_references
execution_context
validity_window
recoverability_profile
decision
reason_codes
state_digest
receipt_digest
```

## 5. State Transition

Execution is represented by a partial transition function:

```text
T(s, a) -> s_next
```

`T` is defined only when all of the following hold:

1. `D(a, s) = ALLOW`;
2. the decision remains valid at commit time;
3. actor, policy, delegation, evidence, and execution context have not materially drifted;
4. the required execution authority is present;
5. the action remains within its validity window and scope.

If any condition fails, execution must not proceed under the earlier decision receipt.

## 6. Allowed-Action Set

Let:

```text
Omega(s) = {a | a is admissible in state s}
```

Then:

```text
a may become an execution candidate only if a in Omega(s)
```

Membership in `Omega(s)` is necessary but not sufficient for a global safety claim. It establishes local admissibility under the represented state and assumptions.

## 7. Core Invariants

### I1 — Authority binding

Every consequence-bearing action must be traceable to accredited, scoped, and revocable authority.

### I2 — Mandatory pre-commit evaluation

No consequence-bearing action may execute without a decision-surface evaluation.

### I3 — Commit-time validity

An earlier `ALLOW` does not survive material drift in policy, identity, delegation, evidence, scope, context, validity, or recoverability.

### I4 — Fail-closed uncertainty

When required evaluation inputs cannot be validated, the system returns `FAIL_CLOSED` or `DENY` and does not execute.

### I5 — No silent mutation

Changes to authority, policy, identity, delegation, evidence state, or execution standing must produce durable evidence.

### I6 — Receipt completeness

Each evaluation and execution attempt must emit enough canonical evidence to distinguish proposal, admission, commitment, execution, failure, and compensation.

### I7 — Replay qualification

Replay claims require the historical action, canonical state inputs, policy and delegation versions, evaluator version, and deterministic or explicitly bounded nondeterministic behavior.

### I8 — Recoverability qualification

Rollback must not be claimed where effects are irreversible. Such systems require compensating-action, containment, or remediation semantics.

### I9 — Separation of authority and operation

Data-plane capability does not create control-plane authority.

### I10 — Human-authority degradation

A boundary is not admissible merely because it can be maintained while the operator is fully coherent. The system must state how authority, consent, recovery, and safe degradation behave as operator capacity changes.

### I11 — Correctability viability

A governed system must preserve a machine-observable correction pathway while consequential execution remains alterable. Corrective authority, scope, reachability, enforceability, evidence, and timing must be independently evaluated rather than asserted by the correction request.

## 8. Trajectory Model

A trajectory is:

```text
tau = (s_0, a_0, s_1, a_1, ..., s_n)
```

with:

```text
s_(k+1) = T(s_k, a_k)
```

A locally admissible trajectory requires:

```text
for every k:
  a_k in Omega(s_k)
  D(a_k, s_k) = ALLOW
  commit_time_valid(a_k, s_k) = true
```

This does not alone prove that every reached state is safe. A separate safe-state definition and inductive or barrier-style argument are required.

## 9. Stability and Risk Framing

Let `V(s)` be a candidate risk, divergence, or boundary-tension measure.

A proposed monotonic condition is:

```text
V(s_next) <= V(s)
```

This is a design objective or proof obligation, not a theorem until:

- `V` is well-defined;
- its domain and assumptions are explicit;
- admissible disturbances are modeled;
- the transition relation is specified;
- the claimed stability property is proven or empirically bounded.

StegVerse therefore uses the term **stability-constrained autonomy** cautiously: autonomy should remain within admissible authority and should not produce unbounded divergence from recoverable, governable states.

## 10. GCAT-Style Trajectory Qualification

A governance-constrained autonomy trajectory is a trajectory for which:

1. each action is locally admissible;
2. each commitment remains valid at execution time;
3. authority and delegation remain reconstructable;
4. evidence continuity is maintained;
5. divergence and recoverability obligations remain within declared bounds.

This combines static admissibility with dynamic continuation requirements.

## 11. Correctability and Compensation

Correctability is distinct from admissibility, reconstructability, replayability, recoverability, rollback, and compensation.

- **Admissibility** determines whether an action may proceed under the represented state.
- **Reconstructability** determines whether the basis and authority state can later be independently recovered.
- **Replayability** determines whether evaluation can be rerun under declared historical inputs.
- **Recoverability** describes the available path toward an acceptable post-failure state.
- **Rollback** reverses a transition only where the effect surface is actually reversible.
- **Correctability** is the continued operational ability of legitimate authority to alter, stop, redirect, or supersede execution before irreversible consequence.
- **Compensation** is a separately authorized post-consequence action that remediates, contains, restores, counteracts, or records harm after timely correction is no longer possible.

A correction request `c` is viable only when:

```text
corrective_authority_valid(c)
scope_authorized(c)
pathway_reachable(c)
intervention_enforceable(c)
evidence_present(c)
completion_time(c) < irreversible_time(c)
```

with:

```text
completion_time(c) = detected_at(c)
                   + authorization_latency(c)
                   + intervention_latency(c)
```

The governed correction decision is:

```text
C(c, s) -> {ADMIT, DENY, FAIL_CLOSED}
```

A late request must not be mislabeled as a successful correction. Where the requested intervention is `compensate` and the irreversible boundary has already been reached, the system evaluates a compensation receipt instead. The receipt result is one of:

```text
COMPLETE
PARTIAL
FAILED
IMPOSSIBLE
```

`PARTIAL`, `FAILED`, and `IMPOSSIBLE` require explicit residual-effect records. `FAILED` and `IMPOSSIBLE` do not establish successful remediation. Compensation never retroactively makes the original execution admissible or timely correctable.

The permitted correction vocabulary is:

```text
pause
deny
revoke
quarantine
rollback
redirect
supersede
compensate
escalate
```

These values constrain repository-level conformance and do not themselves grant runtime authority.

## 12. Threat Model

The baseline adversary may attempt to:

- spoof an actor or authority;
- reuse an expired or out-of-scope delegation;
- change policy after evaluation but before execution;
- substitute stale or incomplete evidence;
- bypass the decision surface;
- mutate execution context;
- suppress or fork receipts;
- induce replay divergence;
- exploit degraded human authority;
- coordinate multiple entities whose local actions produce unsafe coupled behavior;
- submit a late compensation attempt as if it were timely correction;
- assert local authority booleans instead of resolving canonical authority records.

No universal prevention guarantee is claimed. Each implementation must declare trust roots, cryptographic assumptions, failure domains, and monitored bypass surfaces.

## 13. Failure Classes

```text
F1 decision_input_unavailable
F2 identity_or_authority_unverified
F3 delegation_invalid_or_expired
F4 policy_or_context_drift
F5 evidence_stale_or_incomplete
F6 decision_surface_bypass
F7 execution_receipt_missing
F8 replay_divergence
F9 irreversible_effect_without_compensation
F10 authority_degradation_unhandled
F11 multi_entity_coupling_violation
F12 purpose_inverting_boundary
F13 correction_pathway_unreachable
F14 correction_intervention_unenforceable
F15 correction_after_irreversibility
F16 compensation_failed_or_impossible
```

A purpose-inverting boundary is a boundary whose maintenance prevents convergence toward the system's declared legitimate purpose.

## 14. Proposition and Proof-Obligation Framing

### P1 — Local admissibility enforcement

If every execution path is mediated by the decision surface and bypass is excluded by implementation evidence, then actions outside `Omega(s)` are prevented from executing through the governed path.

**Proof obligation:** enumerate and test all execution paths and bypass surfaces.

### P2 — Decision reconstructability

If receipts preserve canonical action, state, policy, delegation, evaluator, and evidence references, then a third party can reconstruct the basis of the decision.

**Proof obligation:** demonstrate independent reconstruction from canonical artifacts rather than asserted values.

### P3 — Drift-sensitive denial

If commit-time validation compares the current authority, policy, delegation, evidence, and context with the admitted state, then material drift can cause deterministic denial.

**Proof obligation:** define material drift and test each drift class.

### P4 — Safe-state preservation

If the initial state is in a defined safe set, each admitted transition preserves that set, and the transition relation is complete for the governed path, then reachable governed states remain in the safe set.

**Proof obligation:** define the safe set and prove transition preservation. This draft does not supply that proof.

### P5 — Timely correctability

If a canonical corrective authority is valid, the intervention is scoped, reachable and enforceable, required evidence is available, and completion precedes the irreversible boundary, then the governed path may admit the correction.

**Proof obligation:** independently resolve authority, enumerate correction paths, measure or bound latencies, and test every irreversible-boundary case.

## 15. Required Conformance Artifacts

A conforming implementation should publish machine-readable schemas and tests for:

```text
state_snapshot
action_request
authority_record
delegation_record
policy_record
decision_receipt
commit_time_check
execution_receipt
correction_request
compensation_receipt
replay_result
drift_event
```

Minimum tests:

1. valid action -> `ALLOW`;
2. invalid authority -> `DENY`;
3. missing evidence -> `FAIL_CLOSED`;
4. policy drift before commit -> `DENY`;
5. identity mutation before commit -> `DENY`;
6. expired delegation -> `DENY`;
7. bypass attempt -> blocked and evidenced;
8. replay under original state -> matching result;
9. replay under changed state -> explicit divergence;
10. irreversible effect -> compensation semantics, not false rollback claim;
11. valid timely correction -> `ADMIT`;
12. late ordinary correction -> `DENY`;
13. authorized post-irreversibility partial compensation -> `COMPENSATE` with residual effects;
14. impossible compensation -> `DENY` with `compensation_impossible` evidence.

## 16. Non-Claims

This specification does not claim:

- that human authority is always legitimate;
- that cryptographic identity proves consent;
- that local admissibility guarantees global safety;
- that replay proves correctness;
- that visibility equals governance;
- that approval equals continuity;
- that execution equals admissibility;
- that compensation makes an earlier action admissible;
- that a late correction request was timely;
- that the candidate stability measure is a proven Lyapunov function;
- that current StegVerse runtime implementations satisfy this specification.

## 17. Migration Target

This staged document should be split in `StegVerse-Labs/stegverse-spec` into:

```text
README.md
SPEC.md
INVARIANTS.md
STATE_AND_TRANSITIONS.md
DECISION_SURFACES.md
IDENTITY_AUTHORITY_AND_DELEGATION.md
AUDIT_REPLAY_AND_RECOVERY.md
CORRECTABILITY_AND_COMPENSATION.md
TRAJECTORY_AND_STABILITY.md
THREAT_MODEL.md
FAILURE_MODES.md
CONFORMANCE.md
schemas/
tests/
docs/STEGVERSE_SPEC_MIRROR_HANDOFF.md
```
