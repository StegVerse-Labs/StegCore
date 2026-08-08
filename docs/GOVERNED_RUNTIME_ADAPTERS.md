# Governed Runtime Adapter Contract

Status: implementation candidate under `StegVerse-Labs/StegCore#21`.

## Rule

Every supported mutation-entry path — UI, API, human, AI, agent, batch, workflow, or replay — must normalize into the same governed adapter request and call `src/stegcore/runtime.py#governed_execute`. Transport, caller type, provider reachability, or possession of a credential reference does not create execution authority.

## Binding requirements

Before the runtime boundary is entered, the adapter fail-closes unless the supplied execution binding preserves the admitted:

- candidate ID and canonical candidate hash;
- credential ID, hash, and subject binding;
- authority reference;
- capability action set without broadening;
- governed-commit requirement;
- admitted parameter bounds;
- prior verified receipt-chain pointer.

A binding failure emits an explicit `FAIL_CLOSED` decision-state record and never invokes the mutation callback.

## Runtime requirements

After binding succeeds, the adapter calls only `governed_execute()` and preserves:

- ALLOW, DENY, REVIEW, and adapter-level FAIL_CLOSED as distinct outcomes;
- coherence denial as a distinct commit-coherence phase;
- explicit executor invocation state;
- commit and observation states;
- candidate, credential, authority, capability, and receipt-pointer bindings;
- StegCore pre/post runtime hashes and coherence receipt hash where available.

StegCore consumes already-verified receipt and credential references. This adapter does not verify signatures and does not mint Continuity receipts.

## HTTP/API rule

`execute_http()` is a bounded transport shim only. It accepts only the `api` adapter kind and delegates to the same adapter/runtime path. There is no direct executor invocation in the HTTP shim or generic adapter implementation.

## Conformance

`tests/test_governed_runtime_adapters.py` covers API, agent, batch, and workflow equivalence; exact-bound ALLOW; candidate mismatch; credential mismatch; unexposed action; parameter bound failure; capability broadening; REVIEW; admissibility DENY; coherence DENY; receipt-pointer mismatch; and HTTP kind mismatch.

Hosted validation is owned by `.github/workflows/governed-runtime-adapters.yml`.
