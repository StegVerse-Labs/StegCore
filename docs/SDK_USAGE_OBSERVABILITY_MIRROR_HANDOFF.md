# SDK Usage Observability Mirror Handoff

## Authority

```text
goal_id: STEGCORE-SDK-USAGE-OBSERVABILITY-001
repository: StegVerse-Labs/StegCore
branch: feat/sdk-usage-observability
parent_handoff: STEGCORE_MIRROR_HANDOFF.md
implementation_state: IN_PROGRESS
release_state: NOT_RELEASED
```

## Goal

Install an observation-only SDK operation ledger and GitHub notification projection for the canonical SDK menu choices `000`, `00`, `0`, `1`, and `2`.

The observer must answer, without consulting Master Records for routine activity visibility:

- which SDK choice was invoked;
- whether the invocation completed, failed, or was cancelled;
- lifetime observed count for each choice;
- trailing 30-day count for each choice;
- each choice's share of all observed SDK invocations;
- last-used timestamp;
- unique canonical runtime identities;
- success/failure/cancel breakdown;
- core governed-operation aggregate for `0 + 1 + 2`;
- all-menu aggregate for `000 + 00 + 0 + 1 + 2`.

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

`since inception` may only be claimed when the canonical ledger contains provenance-supported historical observations reaching inception. Otherwise notifications MUST say `observed since <earliest event timestamp>` and MUST NOT infer unrecorded historical usage.

Historical backfill is permitted only from deterministic, inspectable evidence that identifies an actual SDK invocation and its time. Guessed or reconstructed counts are prohibited.

## Choice semantics

Known canonical semantics:

```text
0 = submit data for governance
1 = replay a previously governed run
2 = reconstruct a previously governed run
```

`000` and `00` MUST be counted independently but their labels remain observational until resolved from the canonical SDK entry implementation. Telemetry must not invent semantics for them.

## GitHub projection

A TV/TVC-authorized bridge may issue a GitHub `repository_dispatch` event containing only the disclosure-safe operation observation and aggregate usage summary. The repository-native workflow validates the projection and posts a comment to a dedicated SDK Usage Activity issue so normal GitHub issue-notification/email behavior can be used.

The workflow itself must require no non-TV/TVC secret or token. `GITHUB_TOKEN` may be used only inside the repository-native workflow for the issue projection; external dispatch credentials remain managed by TV/TVC.

## Planned installed surfaces

```text
src/stegcore/sdk_operation_events.py
tests/test_sdk_operation_events.py
.github/workflows/sdk-usage-notification.yml
docs/SDK_USAGE_OBSERVABILITY_MIRROR_HANDOFF.md
```

## Completion requirements

```text
[ ] append-only five-choice operation event model installed
[ ] deterministic event integrity verification installed
[ ] lifetime + trailing-30-day aggregation installed
[ ] last-used + percent-of-total + unique-runtime aggregation installed
[ ] status breakdown installed
[ ] observed-since semantics installed
[ ] GitHub repository_dispatch projection installed
[ ] GitHub projection rejects payload/authority-bearing fields
[ ] GitHub issue comment renders current event + five-choice usage census
[ ] tests pass on hosted CI
[ ] parent handoff updated with installed state and remaining activation boundary
```

## Activation boundary

This goal is not COMPLETE merely because the ledger classes and workflow exist. Full activation requires the canonical SDK entry surface to call the ledger for every actual `000`, `00`, `0`, `1`, and `2` invocation, and the TV/TVC notification bridge to dispatch the disclosure-safe event projection after recording.

Until that source wiring is directly identified and verified, report `INSTALLED_UNWIRED`, not activated.
