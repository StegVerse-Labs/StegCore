# StegGate — Product Review v5.0

**Action-First Admissibility, Reality Reconstruction, Observability, and Reconstruction Singularity**

| Field | Value |
|---|---|
| Status | Review candidate — formalism expansion |
| Version | 5.0 (extends v4.0; does not replace live runtime contracts) |
| Date | 2026-08-08 |
| Reference runtime owner | `StegVerse-Labs/StegCore` |
| Canonical interop/schema owner | `StegVerse-Labs/ara-admissibility-interop` |
| Governance semantics | `StegVerse-Labs/Governance` |
| Continuity authority | StegID / Continuity contracts as applicable |
| Evidence custody | Master Records under its own contracts |
| Posture | Architecture/formalism review only; no runtime, release, publication, or standards authority |

---

## 0. Review verdict

v4 correctly established continuity as a typed consequence of transition rather than an inherent property of persistence. v5 adds the missing higher-order model:

> **Admissibility models possible transitions. Action realizes one transition. Reality supplies the actual successor state. Observation establishes what can be known about that state. Reconstruction explains the realized transition and exposes missing constraints.**

The architectural ordering is therefore:

```text
ADMISSIBILITY
→ ACTION
→ REALITY
→ OBSERVATION
→ CONTINUITY CONSEQUENCE
→ RECONSTRUCTION
→ RESIDUAL
→ CONSTRAINT DISCOVERY
→ UPDATED ADMISSIBILITY
```

This is the **Action-First** model.

`ALLOW` is not continuity and does not create actuality. It is a determination that a proposed transition belongs to the currently admitted possibility set. Reality changes only when an action crosses the point of irreversibility.

---

## 1. Action First

### 1.1 Core principle

> **No actor class is primary. The realized admissible transition is primary.**

Human, AI, organizational, device, service, and autonomous-process actors are governed by the same transition semantics. Actor identity may affect constraints and authority, but it does not receive ontological priority.

### 1.2 ALLOW is possibility, not execution

For prior state `S_t`, define the admissible candidate set:

```text
A(S_t) = { T_1, T_2, ... T_n }
```

An `ALLOW(T_i)` result means only:

```text
T_i ∈ A(S_t)
```

It does not imply:

```text
T_i occurred
T_i became continuity
T_i created custody
T_i created publication authority
T_i became the canonical future
```

Execution is a distinct boundary.

---

## 2. Admissibility cloud and well collapse

Before a state transition occurs, the admissibility matrix describes multiple possible or admissible transitions from the current state.

Conceptually:

```text
A_t = A(S_t, K_t, E_t, P_t)
```

where:

- `S_t` = current modeled state;
- `K_t` = known constraints;
- `E_t` = available evidence;
- `P_t` = applicable policy/authority context.

As commitment approaches, additional facts, bindings, timing, target state, and irreversible consequences narrow the admissibility well.

At the point of irreversibility `τ*`, exactly one transition becomes part of the observed history:

```text
T* ∈ A_t
S_t --T*--> S_(t+1)
```

The matrix may contain many pre-transition possibilities. The realized history contains one successor transition per modeled irreversible event.

Immediately after realization, a new possibility structure exists:

```text
A_(t+1) = A(S_(t+1), ...)
```

Therefore the system is not:

```text
cloud → permanent endpoint
```

It is:

```text
cloud → collapse → state → cloud → collapse → state → ...
```

---

## 3. Point of irreversibility

Candidate operational definition:

> **The point of irreversibility is the earliest boundary after which restoring the prior actual state requires a new state transition rather than withdrawal of the pending transition.**

Conceptually:

```text
τ* = inf { τ : effect(T, τ) has changed reality
                AND rollback requires a compensating transition }
```

This definition avoids tying irreversibility to a specific transport, database, network, or physical mechanism.

Examples include:

- externally visible publication;
- transfer of custody;
- committed ledger mutation;
- physical actuator movement;
- irreversible secret disclosure;
- sent network consequence whose retraction requires a second action.

---

## 4. Reality, calculated state, and observed state

v5 separates three objects that must not be collapsed:

```text
S_hat_(t+1)  calculated successor from the current model
S_real_(t+1) realized successor in reality
S_obs_(t+1)  successor established through observation
```

The calculated successor is produced by modeled constraints:

```text
S_hat_(t+1) = F(S_t, K_t, a_t)
```

Reality is produced by the full effective constraint structure:

```text
S_real_(t+1) = F(S_t, K_t, U_t, L_t, a_t, ε_t)
```

where:

- `U_t` = unknown but potentially discoverable constraints;
- `L_t` = latent/unmodeled structure, including current unknown unknowns;
- `ε_t` = irreducible stochastic or measurement/process uncertainty.

Observation is a separate operator:

```text
S_obs_(t+1) = H(S_real_(t+1), O_(t+1))
```

where `O_(t+1)` is the observation profile and available POV/evidence coverage.

---

## 5. Observability is part of state identity

A state can remain ontically unchanged while its observable identity changes.

Define:

```text
X_t = (S_t, O_t)
```

Then the following is a real state transition in the StegVerse model:

```text
(S, UNOBSERVED)
→ (S, RECORDED)
→ (S, CORROBORATED)
→ (S, FULLY_OBSERVED_WITHIN_DECLARED_POV_SET)
```

The underlying state `S` need not change. Its relation to the observable record changes.

Candidate observability vocabulary:

```text
UNOBSERVED
OBSERVED
RECORDED
VERIFIED
CORROBORATED
FULLY_OBSERVED
UNKNOWN
```

`FULLY_OBSERVED` is always relative to a declared observer universe:

```text
for every p in P_required:
    observation(p, S) >= required_level(p)
```

It must never mean every conceivable observer in existence.

---

## 6. Reality collapse and observation collapse are distinct

A realized transition may occur without immediately becoming observable or reconstructable.

Example:

```text
(R_1, O_1)
→ (R_2, O_1)
```

Reality changed; the observation state did not.

A later observation can cause:

```text
(R_2, O_1)
--OBSERVE-->
(R_2, O_2)
```

Therefore:

> **An unobserved event is not a nonexistent event. It is a realized transition whose observable identity has not yet converged with reality.**

`FAIL_CLOSED` applies to authoritative reliance on unresolved state, not to reality itself.

Correct boundary:

```text
unknown reality claim → FAIL_CLOSED for dependent authority
```

Incorrect boundary:

```text
reality itself = FAIL_CLOSED
```

---

## 7. Dual delta model

The earlier single measured-vs-calculated state delta is split into two diagnostically different residuals.

### 7.1 Model-to-reality delta

```text
Δ_R = d(S_hat_(t+1), S_real_(t+1))
```

This measures how incomplete the transition model was relative to the realized transition.

### 7.2 Reality-to-observation delta

```text
Δ_O = d(S_real_(t+1), S_obs_(t+1))
```

This measures observational incompleteness.

### 7.3 Cases

```text
Δ_R = 0, Δ_O = 0
→ modeled, realized, and observed states converge

Δ_R = 0, Δ_O > 0
→ model predicted reality, observation remains incomplete

Δ_R > 0, Δ_O = 0
→ observation is sufficient, model missed effective constraints

Δ_R > 0, Δ_O > 0
→ both transition model and observational state remain incomplete
```

Downstream claims that require an unresolved dimension must fail closed rather than invent convergence.

---

## 8. Why preserve the full admissibility matrix

A receipt that records only:

```text
S_1 → S_2
```

cannot reconstruct the prior possibility space.

Preserving the admissibility matrix allows later reconstruction to determine whether a non-realized candidate:

- was inadmissible;
- was admissible but unrealized;
- was superseded;
- lost admissibility before irreversibility;
- was never presented;
- remained viable until another transition touched reality.

The full matrix therefore preserves counterfactual context needed to explain not only **what happened**, but **why this transition rather than another modeled transition became actual**.

The preserved matrix is evidence of modeled possibility, not evidence that unrealized transitions occurred.

---

## 9. Full effective constraint set

The realized transition is governed by more than currently known governance constraints.

Candidate partition:

```text
G_t = K_t ∪ U_t ∪ L_t
```

where:

- `K_t` = known constraints;
- `U_t` = unknown constraints that become discoverable from available evidence;
- `L_t` = latent constraints not represented by the current model, including unknown unknowns.

The modeled successor uses `K_t`. Reality responds to the full effective structure.

Therefore unexplained transition residual is not merely an implementation error. It can be evidence that the model is missing operative structure.

---

## 10. Reconstruction as constraint discovery

The reconstruction loop is:

```text
K_t
→ calculate S_hat_(t+1)
→ realize S_real_(t+1)
→ observe S_obs_(t+1)
→ calculate residuals
→ reconstruct candidate causes
→ test identifiability
→ promote supported constraints
→ K_(t+1)
```

Repeated residual structure can support promotion:

```text
LATENT / UNKNOWN-UNKNOWN
→ DETECTABLE UNKNOWN
→ TESTABLE CONSTRAINT
→ KNOWN CONSTRAINT
```

No hidden cause may be promoted merely because it fits one residual. Competing explanations must be tested against available evidence and declared reconstruction standards.

This is the **identifiability requirement**.

---

## 11. Reconstruction efficiency

A normalized transition-prediction efficiency may be expressed conceptually as:

```text
η_t = 1 - normalize(d(S_hat_(t+1), S_real_(t+1)))
```

When the realized state is not directly observable, the system must report the measurable observational residual separately and must not represent it as direct reality error.

A stronger StegVerse reconstruction score should eventually combine:

```text
prediction fit
causal reconstructability
observation coverage
constraint completeness
counterfactual discrimination
uncertainty calibration
```

Perfect outcome prediction without causal reconstruction is not sufficient to claim reality reconstruction.

---

## 12. Continuity after Action First

Continuity is derived from the realized transition and its evidence:

```text
C_(t+1) = derive(S_t, T*, S_real_(t+1), P_t, E_t)
```

This preserves the v4 rule that continuity is typed and consequential.

The important correction is ordering:

```text
ALLOW ≠ continuity
ALLOW ≠ execution
ACTION → realized transition
realized transition → continuity consequence
```

Thus the phrase `Continuity first` is not a foundational transition law. At most it can describe a policy preference concerning an `ALLOW` posture or a required continuity dimension before commitment.

The architecture-level ordering is **Action First**.

---

## 13. Viability and continued becoming

A living or continuing system is not characterized by preserving endpoints indefinitely. It is characterized by retaining the capacity for another admissible transition.

Candidate viability function:

```text
V_h(S_t) = value of admissible reachable transition space from S_t over horizon h
```

Simple transition count is insufficient. Viability may depend on:

```text
purpose
recoverability
authority
resource sufficiency
observer coverage
transition horizon
critical-path reachability
```

A governance mechanism that prevents prohibited actions but destroys all required future admissible transitions can be a continuity or viability failure even if every local DENY was internally correct.

Terminal states must be declared explicitly so that intentional completion is not misclassified as viability failure.

---

## 14. Reconstruction Singularity

The long-term goal is not merely governance accuracy. It is reconstruction of the effective constraint structure producing observed reality.

Candidate definition:

> **Reconstruction Singularity is the limiting regime in which recursive observation, transition reconstruction, residual analysis, and constraint discovery reduce unexplained state-transition error and latent constraint uncertainty toward the irreducible observational and physical uncertainty of the modeled system.**

This does not claim omniscience.

Conceptually:

```text
E[Δ_R(t)] → ε_irreducible
U_model(t) → U_irreducible
```

subject to:

- sufficient observability;
- causal identifiability;
- non-deceptive evidence;
- stable metric semantics;
- explicit uncertainty;
- no conflation of model with reality.

The system must preserve the assertion:

```text
model(reality) != reality
```

Even at convergence.

---

## 15. Canonical recursion

The v5 core can be summarized as:

```text
REALITY
→ OBSERVATION
→ RECONSTRUCTION
→ BETTER ADMISSIBILITY
→ ACTION
→ NEW REALITY
```

Or from the governing surface:

```text
ADMISSIBILITY MATRIX
→ ACTION
→ REALIZED STATE
→ OBSERVABILITY UPDATE
→ CONTINUITY CONSEQUENCE
→ RECONSTRUCTION
→ RESIDUAL ANALYSIS
→ CONSTRAINT DISCOVERY
→ UPDATED ADMISSIBILITY MATRIX
```

This is the mechanism by which StegVerse becomes more than a governance tool.

Governance structures contact with reality. Reconstruction uses that contact to improve the model of reality.

---

## 16. Candidate v5 invariants

```text
AF-01  ALLOW != execution
AF-02  ALLOW != continuity
AF-03  actor class does not create privileged transition semantics
AF-04  one modeled irreversible event yields one realized successor transition
AF-05  a new admissibility field exists immediately after successor-state realization
AF-06  calculated state != realized state != observed state unless convergence is demonstrated
AF-07  observability may change state identity without changing the underlying ontic state
AF-08  unobserved != nonexistent
AF-09  FAIL_CLOSED applies to unsupported reliance, not to reality itself
AF-10  model residual and observation residual are distinct
AF-11  full admissibility matrices preserve counterfactual context, not unrealized history
AF-12  residual structure may suggest missing constraints but does not prove causation
AF-13  hidden-constraint promotion requires identifiability evidence
AF-14  prediction accuracy alone != reconstruction
AF-15  continuity is a derived consequence of realized transition
AF-16  viability concerns future admissible transition capacity
AF-17  intentional terminal states != automatic continuity failure
AF-18  reconstruction convergence must retain explicit uncertainty
AF-19  model(reality) != reality
AF-20  reconstruction success != execution authority
```

---

## 17. Required formalization work

The concept is sufficiently mature for formal specification, but these definitions remain to be canonicalized by their owners:

1. state ontology: entity, environment, network, observation, and identity dimensions;
2. admissibility-matrix semantics: permission, feasibility, likelihood, or separate layers;
3. irreversibility-boundary semantics;
4. observer universe and observation operator;
5. distance/residual metrics across heterogeneous states;
6. unknown, latent, stochastic, and irreducible-uncertainty partitioning;
7. identifiability tests for constraint promotion;
8. reconstruction-efficiency scoring;
9. viability function and horizon semantics;
10. terminal-state declarations;
11. reconstruction-convergence criteria;
12. shared vectors demonstrating model error vs observation error.

Canonical protocol/schema ownership remains `StegVerse-Labs/ara-admissibility-interop`. This review must not silently modify that repository's active `0.2.0-release-candidate` publication lane.

---

## 18. Integration posture

This review is intentionally non-runtime.

It does not modify:

```text
StegCore decide()
external-evidence runtime
current Governance contracts
current Continuity minting authority
ARA 0.2.0 release-candidate publication state
Master Records custody
Site publication
Publisher release state
admissibility-wiki public claims
stegguardian-wiki public claims
```

Recommended successor work:

```text
StegVerse-Labs/ara-admissibility-interop
  → formalize Action-First state, admissibility, observation, residual, and convergence schemas
  → add machine-readable shared vectors
  → preserve current release-lane handoff and collision boundaries

StegVerse-Labs/StegCore
  → consume only stable canonical contracts after interop publication/merge
  → do not invent runtime semantics ahead of the canonical schema owner

StegVerse-Labs/Governance
  → determine which constraint-discovery outputs can become governance inputs
  → preserve proof != authority

Continuity / StegID
  → decide authoritative continuity artifact semantics for observed/reconstructed transitions

Master Records
  → preserve admissibility matrices, realized-transition evidence, observation evidence, and reconstruction lineage under custody rules
```

---

## 19. Review conclusion

v5 reframes the StegVerse objective:

> **Governance is the structured mechanism by which admissible actions touch reality. Reconstruction is the mechanism by which reality teaches the system what its admissibility model was missing.**

The admissibility matrix matters because it preserves the modeled possibility space against which the realized transition can be compared.

The realized transition matters because it converts possibility into actuality.

Observation matters because a real transition cannot become reconstructable governance evidence until its observable identity is established.

Residuals matter because they expose the distance between modeled and realized transition structure.

Reconstruction matters because repeated, identifiable residual structure can convert unknown constraints into known constraints.

The Reconstruction Singularity is the asymptotic goal of that recursive convergence, bounded by irreducible uncertainty and the permanent distinction between model and reality.
