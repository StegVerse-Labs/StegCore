# SDK Usage Observability Mirror Handoff

## Authority

```text
goal_id: STEGCORE-SDK-USAGE-OBSERVABILITY-001
repository: StegVerse-Labs/StegCore
branch: feat/sdk-usage-observability
parent_handoff: STEGCORE_MIRROR_HANDOFF.md
issue: #117
pull_request: #118
implementation_state: INSTALLED_UNWIRED
validation_state: HOSTED_TESTS_PASS
release_state: NOT_RELEASED
```

## Goal

Install an observation-only SDK operation ledger and GitHub notification projection for the canonical SDK menu choices `000`, `00`, `0`, `1`, and `2`.

The observer answers, without consulting Master Records for routine activity visibility:

- which SDK choice was invoked;
- whether the invocation started, completed, failed, or was cancelled;
- lifetime observed count for each choice;
- trailing 30-day count for each choice;
- each choice's share of all observed SDK invocations;
- last-used timestamp;
- unique canonical runtime identities;
- completed/failed/cancelled/in-progress breakdown;
- core governed-operation aggregate for `0 + 1 + 2`;
- all-menu aggregate for `000 + 00 + 0 + 1 + 2`.

Lifecycle rows do not inflate usage: STARTED + one terminal event count as one invocation.

## Non-authority boundary

This telemetry is not Master Records, is not an evaluator, and grants no policy, execution, replay, reconstruction, or disclosure authority.

Mandatory invariants:

```text
payload_disclosed: false
observation_grants_authority: false
notification_grants_authority: false
master_records_remains_canonical_custody: true
github_remains_notification_projection_only: true
```

No SDK payload, policy body, secret, token, credential, or authority-bearing material may be persisted in the operation ledger or projected to GitHub.

## Historical-count boundary

`since inception` may only be claimed when the canonical ledger contains provenance-supported historical observations reaching inception. Otherwise notifications say `observed since <earliest event timestamp>` and do not infer unrecorded historical usage.

Historical backfill is permitted only from deterministic, inspectable evidence that identifies an actual SDK invocation and its time. Guessed or reconstructed counts are prohibited.

## Choice semantics

Known canonical semantics:

```text
0 = submit data for governance
1 = replay a previously governed run
2 = reconstruct a previously governed run
```

`000` and `00` are counted independently but their labels remain observational until resolved from the canonical SDK entry implementation. Telemetry does not invent semantics for them.

## Installed surfaces

```text
src/stegcore/sdk_operation_events.py
src/stegcore/__init__.py
scripts/render_sdk_usage_notification.py
tests/test_sdk_operation_events.py
tests/test_sdk_usage_notification.py
.github/workflows/sdk-usage-notification.yml
docs/SDK_USAGE_OBSERVABILITY_MIRROR_HANDOFF.md
StegVerse-Labs/StegCore#117  # canonical human-visible notification thread
StegVerse-Labs/StegCore#118  # implementation PR
```

`SDKOperationEventLedger` provides an append-only JSONL-capable lifecycle ledger with deterministic event hashes/IDs, immutable invocation identity, replay/reconstruct receipt-locator requirements, reconstruct no-consequence-reexecution enforcement, five-choice usage aggregation, and a disclosure-safe notification projection.

The notification renderer uses an explicit field allowlist. Unknown fields, payload projection, authority projection, incomplete five-choice census data, invalid counts, and reconstruct consequence-reexecution claims fail closed.

## GitHub projection

A TV/TVC-authorized bridge may issue a GitHub `repository_dispatch` event of type:

```text
stegverse_sdk_usage_event
```

with the disclosure-safe `stegcore.sdk_usage_notification.v1` projection as `client_payload`.

`.github/workflows/sdk-usage-notification.yml` validates the implementation/tests, validates and renders the payload, retains the rendered notification as a workflow artifact, and posts it to issue #117. Normal GitHub issue subscription/watching can then provide GitHub email notification.

The workflow introduces no non-TV/TVC credential. External dispatch authority remains TV/TVC-managed. Repository-native issue posting uses only GitHub's workflow-scoped `GITHUB_TOKEN`.

## Existing observer correction

StegCore already contains `.github/workflows/steggate-live-observer.yml`. That workflow is the canonical service-health/activation observer. It is not the SDK menu-usage observer and is intentionally not repurposed; this goal remains a separate non-authority usage projection.

## Hosted validation evidence

PR #118 head `926206cfa14f88e1d2ec8e8ff08615cc04778a7f` recorded:

```text
SDK Usage Notification / validate: PASS
bcat-check: PASS
repository smoke checks: PASS
repository tests: PASS
```

The PR notification job is correctly skipped on `pull_request`; it runs only for `repository_dispatch` after the workflow exists on the default branch.

## Completion requirements

```text
[done] append-only five-choice operation event model installed
[done] deterministic event integrity verification installed
[done] invocation lifecycle deduplication installed
[done] lifetime + trailing-30-day aggregation installed
[done] last-used + percent-of-total + unique-runtime aggregation installed
[done] status breakdown installed
[done] observed-since semantics installed
[done] GitHub repository_dispatch projection installed
[done] GitHub projection rejects payload/authority-bearing fields
[done] GitHub issue comment renderer includes current event + five-choice usage census
[done] tests pass on hosted CI
[pending] merge #118 to default branch
[pending] identify canonical SDK menu entry source for `000` and `00`
[pending] wire all five actual menu invocations to `SDKOperationEventLedger`
[pending] wire TV/TVC bridge to dispatch the safe projection
[pending] execute first real dispatch and verify issue #117 notification/artifact
[pending] determine whether provenance-supported pre-install history can be backfilled
[pending] update parent handoff after merge/activation-state reconciliation
```

## Activation boundary

The StegCore observer contract is implemented and hosted-test validated, but the goal is not activated yet. Full activation requires the canonical SDK entry surface to call the ledger for every actual `000`, `00`, `0`, `1`, and `2` invocation, and the TV/TVC notification bridge to dispatch the disclosure-safe event projection after recording.

Until that source wiring and one real end-to-end dispatch are directly verified, report `INSTALLED_UNWIRED`, not COMPLETE or ACTIVATED.

## Remaining destination ownership

```text
StegVerse-Labs/StegCore
  -> merge #118 after branch protection remains green
  -> locate and bind canonical SDK entry to the installed ledger
  -> preserve issue #117 as notification-only observation surface

TV/TVC
  -> own external GitHub repository_dispatch credential/authorization
  -> send only `stegcore.sdk_usage_notification.v1` client_payload

Master Records
  -> remains canonical exact-run/evidence custody; no telemetry authority moves to GitHub
```
