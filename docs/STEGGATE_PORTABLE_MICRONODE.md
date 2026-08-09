# StegGate Portable / Ephemeral Micro-Node Topology

Status: implementation candidate installed on `main`; governed by `STEGCORE_MIRROR_HANDOFF.md` and issue #68.

## Principle

A governed transition and the StegGate boundary required to admit it may travel as one transportable execution object. Persistent HTTP hosting is therefore one topology, not an architectural prerequisite.

The package does **not** acquire trust by carrying arbitrary executable bytes. Instead it carries:

- the canonical `AdmissibilityRequest` for the transition;
- the StegGate portable profile;
- the expected reconciled-runtime profile and runtime fingerprint;
- declared execution/coherence context;
- package identity and canonical package hash;
- optional expiry.

The receiving environment instantiates a short-lived micro-node from a locally installed, known StegCore runtime. The node verifies package integrity and runtime identity before invoking the canonical chain:

```text
GovernedTransitionPackage
        ↓ integrity/profile/runtime binding
three_layer.evaluate_three_layer
        ↓
steggate.evaluate_admissibility
        ↓ complete decision-state matrix
steggate_runtime.governed_steggate_execute
        ↓ independent commit coherence
injected consequence callback (only after ALLOW + coherence ALLOW)
        ↓
PortableMicroNodeReceipt
        ↓
node terminates
```

## Runtime surfaces

Implementation: `src/stegcore/portable_steggate.py`

Public Python API:

- `runtime_fingerprint()`
- `create_governed_package(...)`
- `evaluate_governed_package(package)`
- `execute_governed_package(package, executor)`

Profiles:

- portable node: `steggate.portable-micronode.v1`
- reconciled runtime: `stegcore.reconciled-three-layer.v1`

The runtime fingerprint is calculated over the canonical implementation components used to cross the consequence boundary:

- `three_layer.py`
- `steggate.py`
- `steggate_runtime.py`
- `commit_governance.py`

A receiver that cannot reproduce the package's required runtime fingerprint fails closed. Package-hash mismatch and invalid/expired package validity also fail closed before the consequence callback is reachable.

## Lifecycle

```text
TRANSPORTED
   ↓
INSTANTIATED (new `SGMU-*` identity)
   ↓
PACKAGE + RUNTIME BINDING VERIFIED
   ↓
EVALUATED
   ↓
ALLOW / DENY / REVIEW / FAIL_CLOSED
   ↓ if ALLOW and execute topology requested
COMMIT COHERENCE
   ↓ if independently ALLOW
CONSEQUENCE
   ↓
EXECUTED / REFUSED / FAILED / FAIL_CLOSED
   ↓
RECEIPT EMITTED
   ↓
TERMINATED
```

Each instantiation has a fresh micro-node instance identifier. Identity of the node instance is evidence, not authority. Authority remains in the package's evaluated policy/evidence/delegation surfaces and the independent commit-coherence boundary.

## Portability semantics

JSON serialization/deserialization of `GovernedTransitionPackage` is part of the tested contract. A package can therefore be transported between compliant environments and instantiated locally without a resident StegGate HTTP service.

This topology is suitable for:

- local/device execution;
- agent/provider-side execution;
- serverless jobs;
- batch transitions;
- offline or intermittently connected environments when required artifacts are locally reconstructable;
- resident services that prefer per-transition isolation.

Networking is optional. If the consequence target is locally callable, the micro-node requires no public ingress and no tunnel. A tunnel/rendezvous layer is only an availability/transport mechanism when a remote caller must reach a resident or remote micro-node.

## Reconstruction

The emitted `stegcore.portable_micronode_receipt` preserves:

- package identity/hash;
- ephemeral node instance identity;
- runtime profile/fingerprint;
- complete admissibility evaluation when available;
- full governed execution observation when execution is attempted;
- fail-closed reason when instantiation cannot safely proceed;
- instantiation and termination timestamps;
- canonical receipt hash.

This makes node birth, governance decision, consequence/non-consequence, and node termination part of the reconstructable transition history.

## Non-authorities

Portable execution does not grant:

- arbitrary remote code execution;
- publication authority;
- provider credential authority;
- payment/transaction authority;
- Continuity receipt-minting authority;
- deployment authority;
- policy authorship.

The package is transportable governance state plus a required implementation identity. The consequence callback remains environment-provided and unreachable unless canonical StegGate and commit coherence both permit it.

## Validation

`tests/test_portable_steggate.py` proves:

1. JSON transport followed by fresh micro-node evaluation;
2. ALLOW + coherence ALLOW executes and binds the decision-state hash;
3. runtime fingerprint mismatch fails closed before execution;
4. package tampering fails closed before execution;
5. canonical DENY never invokes the executor.

The portable topology becomes activated only when these tests pass through hosted repository validation and the result is reflected in the canonical handoff/task inventory.
