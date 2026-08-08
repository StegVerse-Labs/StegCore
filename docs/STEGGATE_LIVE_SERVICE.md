# StegGate Live Service

## Purpose

`stegcore.service:app` exposes the canonical StegGate admissibility matrix as an HTTP service.

The service is a decision boundary, not an authority amplifier. It evaluates a proposed candidate against evidence, authority, policy, capability, continuity, and approval state and preserves the complete matrix that produced the terminal disposition.

## Endpoints

```text
GET  /
GET  /health
GET  /v1/capabilities
POST /v1/evaluate
GET  /v1/self-test
```

`POST /v1/evaluate` returns one of:

```text
ALLOW
DENY
REVIEW
FAIL_CLOSED
```

Every response contains the canonical candidate hash, every material matrix predicate, reasons, evaluation time, and a canonical decision-state hash.

## Matrix semantics

Known invalidity or prohibition produces `DENY`. Missing critical evidence produces `FAIL_CLOSED`. A required but not-yet-supplied human approval produces `REVIEW`. `ALLOW` is reachable only when every required material predicate passes.

Human approval is candidate-hash bound. Approval for one candidate cannot be reused after a candidate mutation.

## Execution boundary

The live service intentionally does not expose an arbitrary external mutation endpoint. A returned `ALLOW` means the candidate passed this admissibility evaluation. It does not itself mint a Continuity receipt or grant the caller permission to invent a new external side effect.

Existing `GovernedRuntime` adapters remain the in-process execution boundary for callers that already possess an authorized executor binding. A future remote execution adapter must bind an explicit action registry/allowlist and its own authority contract rather than accepting arbitrary URLs or code from the network.

## Deployment

Canonical Render contract: `render.steggate.yaml`.

Build:

```bash
pip install --upgrade pip && pip install -e .
```

Start:

```bash
uvicorn stegcore.service:app --host 0.0.0.0 --port $PORT
```

Health gate: `/health`.

The deployment is considered functionally active only after repository tests pass, the Render deploy is live, `/health` reports `healthy`, and `/v1/self-test` reports `PASS` for ALLOW, DENY, REVIEW, and FAIL_CLOSED.
