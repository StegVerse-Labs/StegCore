# Legacy Release Admissibility Mirror Handoff

Repository: `StegVerse-Labs/StegCore`
Parent handoff: `STEGCORE_MIRROR_HANDOFF.md`
Goal: `STEGCORE-LEGACY-RELEASE-001`
State: `SOURCE_IMPLEMENTED_PENDING_HOSTED_VALIDATION`
Upstream: `StegVerse-Labs/Continuity/docs/LEGACY_CONTINUITY_MIRROR_HANDOFF.md`
Authority effect: NONE
Activation effect: false

## Purpose

Adapt verified legacy-continuity facts into the existing canonical StegCore three-layer admissibility runtime. This work MUST NOT create a second evaluator.

Canonical evaluator remains:

`stegcore.three_layer.evaluate_three_layer`

## Implemented surfaces

- `src/stegcore/legacy_release.py`
- `tests/test_legacy_release.py`
- `schemas/legacy-release-admissibility.schema.json`

## Required predicates

A disclosure/release candidate is eligible for canonical evaluation only when the request represents:

- participant-authored policy current;
- verified recipient identity;
- recipient participation qualification when configured;
- verified trigger evidence;
- TV/TVC authorization current;
- current state/reference hash continuity;
- affected-recipient conditions represented;
- reconstructable evidence basis;
- explicit recoverability classification;
- open validity window.

Missing or ambiguous facts fail closed before consequence.

## Consequence boundary

The adapter returns only an admissibility result and legacy transition receipt. It does not:

- disclose a KV payload;
- notify a recipient;
- move StegCoin or StegToken;
- determine death;
- mint identity or TVC authorization;
- bypass legal/estate requirements;
- execute external delivery.

`ALLOW` means only that the represented transition is admissible under the represented current state and policy. Downstream consequence still requires the appropriate authorized executor.

## Remaining integration

1. TVC produces current legacy-release authorization receipt.
2. Continuity binds StegID recipient and participation evidence into the adapter request.
3. KV consumes only the resulting permitted disclosure stage.
4. StegFin independently evaluates economic consequences.
5. Site renders status without creating authority.
