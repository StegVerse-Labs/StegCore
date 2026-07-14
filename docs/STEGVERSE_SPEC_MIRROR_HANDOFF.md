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
Mutation scope: preserve, review, refine, validate, and later migrate the staged specification
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
v1.3-conformance-1: machine-readable core schemas plus dependency-free checks and tests
```

## Qualification of Claims

The v1.1-v1.3 materials are conceptual research scaffolding. They are not peer reviewed, mechanically verified, mathematically complete, or evidence of production safety. In particular:

- `V(s_next) <= V(s)` is a proposed Lyapunov-like framing, not a proven Lyapunov function.
- membership in an allowed-action set does not by itself prove all future states remain safe;
- replayability requires sufficient canonical state capture and deterministic evaluation;
- rollback may require compensating actions where physical or external effects are irreversible;
- adversarial guarantees must be stated relative to explicit threat assumptions;
- the current checker validates selected repository-local conformance rules, not full JSON Schema or formal specification correctness.

## Durable Staged Artifacts

```text
docs/spec/STEGVERSE_SPEC_V1_3.md
docs/spec/schemas/state_snapshot.schema.json
docs/spec/schemas/action_request.schema.json
docs/spec/schemas/decision_receipt.schema.json
docs/spec/schemas/execution_receipt.schema.json
docs/spec/schemas/replay_result.schema.json
scripts/check_stegverse_spec_conformance.py
tests/test_stegverse_spec_conformance.py
```

The consolidated specification remains the recoverable source for migration into the intended `stegverse-spec` repository. The schemas, checker, and tests are staging artifacts for the first executable conformance layer.

## Implemented Conformance Surface

The current staged checker covers:

```text
- required action-request evidence and scope;
- decision value and receipt completeness;
- policy-version drift at commit time;
- state-digest drift at commit time;
- invalid commit-time state blocking execution;
- replay match/divergence consistency;
- fail-closed treatment of missing required evidence.
```

Run locally from the repository root:

```text
python -m unittest tests/test_stegverse_spec_conformance.py
python scripts/check_stegverse_spec_conformance.py action PATH_TO_ACTION_REQUEST.json
python scripts/check_stegverse_spec_conformance.py decision PATH_TO_DECISION_RECEIPT.json
python scripts/check_stegverse_spec_conformance.py execution PATH_TO_EXECUTION_RECEIPT.json
python scripts/check_stegverse_spec_conformance.py replay PATH_TO_REPLAY_RESULT.json
```

No passing runtime output is claimed by this handoff until an authorized runner records it.

## Commit Evidence

```text
handoff_initial: 008dc8b8308c3cd0a7836134c3643a1b684790e9
consolidated_spec: 675fc1f7b5e4c49c6e94105827bbba80de55d6b6
state_snapshot_schema: 63bc5822dc4d19b926318fab184e308ae8bdd089
action_request_schema: 1778d5281eca215c84216d35240c8e190ff0641b
decision_receipt_schema: 71d83d01d9a8339012e39470fc12fe38a447a36a
execution_receipt_schema: aecae23aa413ce61123f08be0d18f542fee1d9d3
replay_result_schema: 9200798af286a66dc017e6ce5982551bdc79844f
conformance_checker: a5bd1fe07260b8a41c049780166284f625174534
conformance_tests: 2e3685ea50ecaab313bebbf17f96d8741f4dbeb7
```

## Remaining Work

1. Create `StegVerse-Labs/stegverse` and install the public introduction README and architecture brochure assets.
2. Create `StegVerse-Labs/stegverse-spec` and split the consolidated staged specification into canonical files.
3. Add schemas for authority record, delegation record, policy record, commit-time check, compensation receipt, and drift event.
4. Run and record the repository-local conformance tests in an authorized environment.
5. Extend executable tests for invalid authority, expired delegation, identity mutation, bypass evidence, and irreversible-effect compensation semantics.
6. Replace theorem labels with propositions or proof obligations until proofs exist.
7. Add explicit safety-set, recoverability, authority-degradation, and coupled multi-entity boundary definitions.
8. Verify downstream terminology against StegCore, Data-Continuation, master-records, BCAT-GCAT-Engine/Publisher, admissibility-wiki, and stegguardian-wiki before release tagging.

## Known Blockers

```text
- The intended introduction and specification repositories have not been verified as created.
- Binary brochure/PDF assets are not committed by this handoff.
- The schema set is incomplete relative to the full required artifact list.
- Conformance tests are committed but no authorized execution receipt is yet recorded.
- Formal guarantees remain proof obligations rather than established theorems.
```

## Permitted Continuation Scope

A successor may:

- refine the staged specification;
- add schemas, examples, validators, and tests;
- run and record validation evidence;
- create migration-ready file splits;
- migrate content into the intended repositories once they exist;
- update this handoff with commit SHAs and validation evidence.

A successor must not claim production authority, formal verification, complete safety, peer-reviewed results, or passing tests without recorded execution evidence.

## Release and Downstream Update Rule

When the specification becomes release/tag ready:

1. create the release/tag only after required tests and terminology checks pass;
2. create a follow-up task verifying whether pertinent information must be applied to:
   - `StegVerse-Labs/Site`;
   - `BCAT-GCAT-Engine/Publisher`;
   - `admissibility-wiki`;
   - `stegguardian-wiki`.

## Archival State

```text
thread_archive_ready: true
archive_reason: decisions, artifact lineage, intended destinations, implementation progress, caveats, blockers, remaining work, ownership, permitted continuation scope, and commit evidence are repository-resident.
```

## Progress Snapshot

```text
StegVerse-Labs - 82% complete
StegCore - 72% complete
StegCore - 100% complete TO GOAL ACTIVATION
Fully developed files vs scaffolding and stubs: 68% developed / 32% scaffolding and unvalidated conformance surfaces
Delta: five core schemas, a dependency-free conformance checker, and seven unit tests are now committed; remaining work is schema completion, authorized test execution, target-repository migration, and downstream terminology verification.
```
