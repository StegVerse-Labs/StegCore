# BCAT Publication Roadmap

This document outlines the planned academic publications derived from
StegCore’s doctrine on **Boundary-Conditioned Autonomy and Trust (BCAT)**.

The roadmap reflects a **research program**, not a single paper.

---

## Publication Strategy

BCAT research is intentionally staged:

1. Establish foundational concepts and vocabulary
2. Formalize detection and enforcement mechanisms
3. Apply the framework to real autonomous systems
4. Address governance, accountability, and ethics

Each publication builds on the previous work without overloading scope.

---

## Paper 01 — Foundational

### Working Title
**Phantom Trust: Detecting Semantically Illegitimate Credentials in Automated Systems**

### Purpose
- Define *phantom trust* as a new class of system failure
- Introduce trust continuity as a first-class system property
- Explain why valid authentication and authorization are insufficient
- Establish BCAT as a governing lens for autonomy

### Contribution Type
- Conceptual framework
- Formal definitions
- Taxonomy of phantom credential states
- System-level reasoning without exploits

### Status
Anchor paper — all subsequent publications reference this work.

---

## Paper 02 — Detection & Signals

### Working Theme
**Detecting Trust Continuity Breaks in Autonomous and Automated Systems**

### Purpose
- Identify observable signals of trust degradation
- Formalize continuity breaks, context drift, and temporal anomalies
- Show detection without exploit disclosure or policy violations

### Contribution Type
- Detection models
- Signal taxonomy
- Operational observability

### Dependency
Builds directly on Paper 01 definitions.

---

## Paper 03 — Authority & Governance

### Working Theme
**Continuous Authority and Conditional Legitimacy in Autonomous Systems**

### Purpose
- Separate permission from authority
- Introduce authority decay and revocation without failure
- Explain explainable non-action as a success state
- Address responsibility without intent

### Contribution Type
- Governance model
- Authority lifecycle
- Accountability mechanisms

---

## Paper 04 — Applied Autonomy (Domain-Specific)

### Candidate Domains
- Autonomous vehicles
- AI agents and tool-using systems
- CI/CD automation pipelines
- Robotics and industrial control systems

### Purpose
- Demonstrate how BCAT resolves “almost here” autonomy failures
- Show how operational truth boundaries reduce tail risk
- Translate doctrine into deployable system architecture

### Contribution Type
- Case study
- Applied systems analysis
- Deployment rationale

---

## Optional Extensions

Future publications may address:
- Regulatory and legal implications
- Human–AI collaboration ethics
- Trust boundary specification languages
- Cross-domain autonomy governance

These are intentionally deferred to avoid diluting core contributions.

---

## Guiding Principle

BCAT publications do not aim to prove that autonomous systems are safe.

They aim to show:
> **How and why autonomous systems can be trusted, revoked, and governed
in ways humans can understand and audit.**

That principle governs all publication decisions.
