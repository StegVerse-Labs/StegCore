# External Evaluator Privacy Mirror Handoff

## Authority

```text
goal_id: EXTERNAL-EVALUATOR-PRIVACY-001
repository: StegVerse-Labs/StegCore
branch: fix/external-evaluator-privacy
parent_handoffs: docs/SDK_STEGGATE_EXPERIMENT_REFERENCE_MIRROR_HANDOFF.md, docs/TRANSACTION_CONTINUITY_MIRROR_HANDOFF.md
state: INSTALLED_PENDING_VALIDATION
```

## Rule

Public repository records must use neutral role identifiers for external evaluators unless the named individual has explicitly agreed to public attribution.

The rule applies to filenames, workflow names, test subjects, manifest subjects, receipt metadata, PR titles/bodies, evaluator handoffs, examples, and durable public inspection records.

External identity is not runtime authority and must not be required for submission, replay, reconstruction, or custody resolution.

## Public inspection entry point

A public PR may provide a visible, durable inspection record, but untrusted PR code must never become the evaluator implementation or runtime authority.

Safe shape:

```text
untrusted PR supplies bounded declarative case data
-> trusted base-repository workflow validates schema
-> trusted pinned evaluator/runtime processes the case
-> governed receipts are emitted
-> public check/run records the observation
```

Prohibited shape:

```text
untrusted PR code
-> executed as evaluator/runtime
```

Fork PRs must not receive secrets, write authority, TV/TVC credentials, or Master Records custody authority. Public records are observations only until separately admitted into canonical custody.

## Remaining work

1. remove personal evaluator identifiers from current public files and active PR surfaces;
2. replace the person-specific frozen-case harness with a neutral external-inspection harness;
3. ensure the PR-triggered lane consumes only bounded declarative data and trusted base code;
4. validate no public source file on the active branch contains the removed personal identifier;
5. preserve the distinction between public inspection evidence and canonical Master Records custody.
