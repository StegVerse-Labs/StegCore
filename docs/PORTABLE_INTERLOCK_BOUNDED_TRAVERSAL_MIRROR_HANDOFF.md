# Portable Interlock Bounded Traversal Mirror Handoff

## Goal

`STEGCORE-PORTABLE-INTERLOCK-BOUNDED-TRAVERSAL-147`

Issue: `StegVerse-Labs/StegCore#147`

Prove that a frozen public-SDK interlock/reference-participant bundle can be consumed by the canonical StegCore standing binding and traverse the real `governed_steggate_execute` path through admissibility, commit coherence, and one bounded consequence invocation.

## Source boundary

- SDK source commit pinned in fixture: `9368804802ba8b5e5899a9da6c8325d811c268de`
- StegCore base for this slice: `26b18204b135a213231d160b718e47ca6ab46f28`
- canonical runtime: `stegverse:steggate:canonical:three-layer:v1`
- canonical consequence boundary: `src/stegcore/steggate_runtime.py:governed_steggate_execute`

The frozen fixture is evidence input only. StegCore does not reimplement the SDK interlock, SPE, or participant receipt issuer.

## Added surfaces

- `fixtures/portable_interlock_bounded_traversal.v1.json`
- `tools/run_portable_interlock_bounded_traversal.py`
- `tests/test_portable_interlock_bounded_traversal.py`
- `docs/PORTABLE_INTERLOCK_BOUNDED_TRAVERSAL_MIRROR_HANDOFF.md`

## Required proof

The runner must:

1. recompute the exact `stegverse.interlock-transition.v1` hash;
2. bind package / transition / run / participant identity;
3. pass the SDK->SPE envelope, SPE receipt, and SDK->StegGate bridge into the canonical StegCore standing verifier;
4. receive `standing.spe_binding = PASS`;
5. receive canonical admissibility `ALLOW`;
6. receive commit-coherence `ALLOW`;
7. invoke the bounded in-memory consequence exactly once;
8. retain deterministic pre-state, post-state, decision-state, and coherence receipt hashes;
9. stop at `SDK_INTERLOCK_RETURN_ASSEMBLY` without claiming a return receipt or a Master Records organization record.

Negative coverage must prove tampered ingress state, tampered SPE receipt, and mismatched participant identity fail closed before consequence invocation.

## Collision boundary

This slice does not modify any file owned by open StegCore PR #141. It does not create or replace transaction-lifecycle receipts, manifested transaction reconstruction, Master Records organization records, or SDK reciprocal-return semantics.

## Authority boundary

SDK authority: NONE. SPE execution authority: NONE. No Master Records organization record is claimed. The bounded executor is reachable only after canonical StegGate ALLOW plus commit-coherence ALLOW.

## Completion boundary

Source presence is not completion. Merge only after exact-head repository validation executes the positive traversal and negative/tamper cases. Full portable-governance activation remains open until the governed result is assembled into the SDK reciprocal return, bound into a participant successor receipt, recorded as a Master Records organization record and reconstructed from it, and independently verified in POST_RETURN mode.
