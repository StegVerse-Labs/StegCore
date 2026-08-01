# StegVerse RTG–TT Operational Layer Handoff

## Repository

`StegVerse-Labs/StegCore`

## State determination

The canonical AE/RTG/TT implementation exists outside StegVerse core, and a Site projection is being built. Before this branch, StegCore had no operational layer that could register, verify, coordinate, and hand off the capability across StegVerse.

**Current state:** `BUILDING`

## Purpose

This layer coordinates the `rtg-tt-v0.1` boundary across StegVerse. It binds canonical source commits, verifies authority remains false, and routes exact downstream work.

It does not own RTG geometry, TT allocation, AE formal interpretation, or Validation Factory procedure.

## Canonical sources

- `Data-Continuation/RTG-Tests@2fd7099bb3b6d2d7aa8ce7d72f7f71f6dfd4566a`
- `Admissible-Existence/TT@19720bae935ef9881ce5b239e0b66423fcd8bfab`
- `Admissible-Existence/ae-validation-factory@5ca6ac0442809c5902f9765d2f865e5fa03d9c60`
- factory report `sha256:a11eea46242f3df6faa64c2c4174779abea08be9ca7ea93342317cdbcdf7aa56`

## Result mapping

```text
RESOLUTION_SATISFIED -> ALLOW
FAIL_CLOSED          -> DENY
QUARANTINE           -> DEFER
```

These are bounded TT results. They do not independently authorize commitment or execution.

## Coordinated work

- StegCore implementation: issue `#38`
- AE public index: `Admissible-Existence/AE#5`
- Site projection: `StegVerse-Labs/Site#125`
- Admissibility projection: `StegVerse-Labs/admissibility-wiki#51`
- Guardian projection: `StegVerse-002/stegguardian-wiki#10`
- Publication projection: `GCAT-BCAT-Engine/Publisher#20`

## Verification

```bash
python tools/verify_rtg_tt_operational_layer.py
```

Expected report:

`brain_reports/rtg_tt_operational_layer_report.json`

## Activation condition

The StegVerse operational layer may change from `BUILDING` to `ACTIVE` only after:

1. the StegCore verifier and workflow pass;
2. the source commit bindings remain exact;
3. all authority flags remain false;
4. Site PR #125 is merged and verified on `main`;
5. downstream consumers remain dependency-bound and preserve semantics;
6. an activation receipt records the exact verified state.

## Non-overlap

This work does not claim the active StegFin chain, Site HIL upload paths, AE formalism ownership, TT allocation ownership, or downstream publication ownership.

## Archive readiness

The issue, state file, task-registry entry, verifier, workflow report, this handoff, and downstream issue references preserve enough state for a new session to continue without conversation context.
