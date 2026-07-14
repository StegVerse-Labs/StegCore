# Three-Layer Admissibility Runtime

## Source of truth

The governing policy and fixture contract originates in `StegVerse-Labs/Governance`:

- `docs/governance/judgment_signal_execution_architecture.md`
- `docs/examples/GDR_SCHEMA_MAPPING.md`
- negative GDR fixtures under `docs/examples/fixtures/`

StegCore owns only deterministic runtime decision behavior for this contract.

## Runtime implementation

- Module: `src/stegcore/three_layer.py`
- Tests: `tests/test_three_layer.py`
- Workflow: `.github/workflows/runtime-tests.yml`

The evaluator processes three layers in restrictive order:

1. judgment conditions;
2. signal admission and reference-state integrity;
3. execution-boundary currency and recoverability.

## Results

The runtime returns one of:

- `ALLOW`
- `DENY`
- `FAIL-CLOSED`

These uppercase execution results remain separate from lowercase Governance Decision Record values.

## Deterministic rules

The evaluator denies when:

- meaningful refusal is unavailable;
- operator authority cannot be recovered;
- declared workload or time pressure materially degrades judgment;
- no canonical signals are admitted;
- material inputs are missing or uncertainty is unresolved;
- state construction or transformations cannot be reconstructed;
- actor authority, policy, delegation, evidence, or validity windows are stale;
- affected-entity conditions are absent.

The evaluator fails closed when:

- current or expected reference-state hashes are absent;
- the current reference-state hash differs from the authorized reference-state hash;
- execution recoverability is unknown.

It allows only when every required judgment, signal-state, and execution condition passes.

## Receipt boundary

The result includes a deterministic evidence receipt containing:

- request hash;
- policy and delegation references;
- judgment evidence references;
- admitted signal references;
- execution evidence references;
- current and expected reference-state hashes;
- findings and result;
- receipt hash.

The receipt explicitly records `continuity_receipt_minted: false`.

StegCore does not verify, mint, replace, or assert authority over Continuity receipts.

## Automated acceptance tests

The runtime test suite proves:

- condition-degraded judgment produces `DENY`;
- unreconstructable signal admission produces `DENY`;
- a shifted reference state produces `FAIL-CLOSED` even when policy and authority pass;
- a valid positive control produces `ALLOW`;
- replay with a changed reference state changes the result;
- an unreconstructable state can never produce `ALLOW`.

The workflow runs automatically on relevant pushes and pull requests. Manual dispatch exists only as an optional recovery route.

## Authority status

This implementation is test-backed runtime behavior, not production deployment authority. Production authority requires passing automation evidence plus any repository-specific release and deployment gates.
