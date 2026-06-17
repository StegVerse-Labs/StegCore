# StegCore 001/002 Repo-Aligned Adapter

Generated: 2026-06-17

## Assumptions

Active repo: `StegVerse-Labs/StegCore`.

Verification found that StegCore uses `src/stegcore/` for package code and `docs/` as the authoritative specification surface.

This build step therefore places the 001/002 adapter under:

```text
src/stegcore/adapters/
```

instead of the earlier top-level experimental path.

## Done Definition

This build step is complete when:

1. `src/stegcore/adapters/` exists.
2. StegVerse-001 continuity records can be evaluated.
3. StegVerse-002 master-record ingestion records can be evaluated.
4. Public raw StegVerse-002 ingestion is denied.
5. The tests pass through `PYTHONPATH=src python -m unittest discover -s tests`.
6. The workflow validates the adapter without secrets.

## Scope

This is a repo-alignment layer.

It does not replace StegCore's existing `decision.py`.

It adds an adapter for the 001/002 activation baseline that can later be connected into the existing `DecisionRequest` / `DecisionResult` interface.

## Boundary Rules

Continuity is not approval.

Execution is not admissibility.

Visibility is not governance.

Discovery is not execution authority.

Reviewer is not override authority.

A refusal must bind consequence unless explicit override authority exists.

## Leading-Dot Path Note

The workflow path is displayed as:

```text
github/workflows/validate-001-002-adapter.yml
```

The leading dot is intentionally omitted in this document. In the repo, place it at:

```text
.github/workflows/validate-001-002-adapter.yml
```
