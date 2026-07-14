# StegVerse Specification Mirror Handoff

## Purpose

This file preserves the public-introduction and specification work developed for the proposed `StegVerse-Labs/stegverse` and `StegVerse-Labs/stegverse-spec` repositories. It is the durable continuation source until those repositories exist and receive the canonical files.

## Current Goal

```text
Goal: establish a canonical StegVerse public introduction and specification repository
Intended introduction repository: StegVerse-Labs/stegverse
Intended specification repository: StegVerse-Labs/stegverse-spec
Current durable staging repository: StegVerse-Labs/StegCore
Current owner: ecosystem-managed continuation
Mutation scope: preserve, review, refine, and later migrate the staged specification
```

## Decisions Preserved

1. The GitHub account `StegVerse` is the public identity layer.
2. `StegVerse/StegVerse` is the intended GitHub profile README repository.
3. `StegVerse-Labs/stegverse` is the intended ecosystem introduction/front-door repository.
4. `StegVerse-Labs/stegverse-spec` is the intended protocol and formal-specification repository.
5. The preferred public description is:

> StegVerse explores how autonomous systems can operate within enforceable trust boundaries where authority, consent, and rollback exist as properties of the infrastructure itself.

6. The visual architecture separates a governance control plane from an execution data plane and includes Human Authority, Control Plane, Decision Surface, Data Plane, Execution Layer, and Audit/Replay.
7. Public materials must remain safe, serious, lightly styled, and must not overclaim mathematical proof, production authority, or validated safety guarantees.

## Version Lineage

```text
v1.0: architecture, governance model, decision surfaces, identity, audit and replay
v1.1: definitions, formal invariants, theorem-style framing, conceptual diagram
v1.2: state transitions, constraint set, adversarial model, failure modes
v1.3: trajectory constraints, stability framing, GCAT-style bounded autonomy
```

## Qualification of Claims

The v1.1-v1.3 materials are conceptual research scaffolding. They are not peer reviewed, mechanically verified, mathematically complete, or evidence of production safety. In particular:

- `V(s_next) <= V(s)` is a proposed Lyapunov-like framing, not a proven Lyapunov function.
- membership in an allowed-action set does not by itself prove all future states remain safe;
- replayability requires sufficient canonical state capture and deterministic evaluation;
- rollback may require compensating actions where physical or external effects are irreversible;
- adversarial guarantees must be stated relative to explicit threat assumptions.

## Durable Staged Artifact

The current consolidated specification is staged at:

```text
docs/spec/STEGVERSE_SPEC_V1_3.md
```

That file is the recoverable source for migration into the intended `stegverse-spec` repository.

## Remaining Work

1. Create `StegVerse-Labs/stegverse` and install the public introduction README and architecture brochure assets.
2. Create `StegVerse-Labs/stegverse-spec` and split the consolidated staged specification into canonical files.
3. Add schemas for state, action request, decision receipt, execution receipt, and replay result.
4. Add executable conformance tests for mandatory evaluation, fail-closed behavior, policy/version binding, and replay divergence.
5. Replace theorem labels with propositions or proof obligations until proofs exist.
6. Add explicit safety-set, recoverability, authority-degradation, and coupled multi-entity boundary definitions.
7. Verify downstream terminology against StegCore, Data-Continuation, master-records, BCAT-GCAT-Engine/Publisher, admissibility-wiki, and stegguardian-wiki before release tagging.

## Known Blockers

```text
- The intended introduction and specification repositories have not been verified as created.
- Binary brochure/PDF assets are not committed by this handoff.
- The specification currently lacks executable schemas and conformance tests.
- Formal guarantees remain proof obligations rather than established theorems.
```

## Permitted Continuation Scope

A successor may:

- refine the staged specification;
- add schemas, examples, validators, and tests;
- create migration-ready file splits;
- migrate content into the intended repositories once they exist;
- update this handoff with commit SHAs and validation evidence.

A successor must not claim production authority, formal verification, complete safety, or peer-reviewed results without new evidence.

## Archival State

```text
thread_archive_ready: true
archive_reason: the session decisions, artifact lineage, intended destinations, caveats, blockers, remaining work, ownership, and permitted continuation scope are now repository-resident.
```
