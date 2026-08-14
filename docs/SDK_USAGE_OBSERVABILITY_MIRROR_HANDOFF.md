# SDK Usage Observability Mirror Handoff

## Authority

```text
goal_id: STEGCORE-SDK-USAGE-OBSERVABILITY-001
repository: StegVerse-Labs/StegCore
branch: feat/sdk-usage-observability
parent_handoff: STEGCORE_MIRROR_HANDOFF.md
issue: #117
pull_request: #118
sdk_consumer_repo: StegVerse-org/StegVerse-SDK
sdk_consumer_pull_request: #27
implementation_state: INSTALLED_PARTIALLY_WIRED
validation_state: HOSTED_TESTS_PASS
release_state: NOT_RELEASED
```

## Goal

Provide a non-authoritative GitHub notification projection for SDK activity and its five-choice usage census without moving canonical evidence custody out of Master Records.

## Canonical choice semantics

Resolved directly from `StegVerse-org/StegVerse-SDK/stegverse/governance_navigation.py`:

```text
000 = Demo test sequence without user-supplied manifest
00  = User-defined run parameters
0   = Submit data for governance
1   = Replay previously run set
2   = Reconstruct previously run set
```

The earlier unresolved-label assumption for `000` and `00` is superseded.

## Counting correction

A menu selection is not proof that a governed operation occurred. Schema v1.1 therefore carries:

```text
activity_kind: MENU_SELECTION | GOVERNED_OPERATION
```

The notification census counts all observed uses of each choice while separately reporting `menu_selections` and `governed_operations`. This permits `000` and `00` usefulness to be measured without falsely treating option `1` guidance as a replay run or option `2` guidance as reconstruction.

## Non-authority boundary

```text
payload_disclosed: false
observation_grants_authority: false
notification_grants_authority: false
master_records_remains_canonical_custody: true
github_remains_notification_projection_only: true
```

No SDK payload, policy body, secret, token, credential, or authority-bearing material may enter the GitHub projection.

## Historical-count boundary

`since inception` may only be claimed after provenance-supported history reaches SDK telemetry inception. Otherwise all notifications report:

```text
historical_coverage: OBSERVED_ONLY
observed_since: <earliest retained observation>
```

Guessed historical counts are prohibited.

## Installed StegCore surfaces

```text
src/stegcore/sdk_operation_events.py
src/stegcore/__init__.py
scripts/render_sdk_usage_notification.py                  # v1 compatibility
scripts/render_sdk_usage_notification_v11.py              # canonical SDK v1.1 consumer
tests/test_sdk_operation_events.py
tests/test_sdk_usage_notification.py
tests/test_sdk_usage_notification_v11.py
.github/workflows/sdk-usage-notification.yml
docs/SDK_USAGE_OBSERVABILITY_MIRROR_HANDOFF.md
StegVerse-Labs/StegCore#117                               # notification thread
StegVerse-Labs/StegCore#118                               # implementation PR
```

The v1.1 renderer uses an explicit allowlist, validates the five canonical labels, requires menu/governed counts to reconcile, permits replay/reconstruct menu selections without a receipt locator, requires a `manifest_receipt_id` for actual governed option `1`/`2` events, and rejects reconstruction claims that consequence was re-executed.

## SDK producer state

`StegVerse-org/StegVerse-SDK#27` installs the canonical producer side:

```text
stegverse/sdk_usage_observability.py
stegverse/cli.py
tests/test_sdk_usage_observability.py
tests/test_cli_sdk_usage_observability.py
.github/workflows/sdk-usage-observability.yml
SDK_USAGE_OBSERVABILITY_MIRROR_HANDOFF.md
```

Canonical `stegverse governance --select 000|00|0|1|2` selections are recorded after the existing governance-navigation validator accepts the choice. The SDK writes a local disclosure-safe ledger and notification outbox without holding a GitHub credential.

## GitHub projection

A TV/TVC-authorized bridge may issue:

```text
repository_dispatch type: stegverse_sdk_usage_event
client_payload schema: stegcore.sdk_usage_notification.v1.1
```

`.github/workflows/sdk-usage-notification.yml` selects the v1.1 renderer, preserves the rendered message as a workflow artifact, and comments on issue #117. GitHub's ordinary issue-watch/email behavior can then deliver the notification.

The workflow itself introduces no external credential. Repository-native issue posting uses only the workflow-scoped `GITHUB_TOKEN`; external dispatch authorization remains TV/TVC-owned.

## Existing observer boundary

`.github/workflows/steggate-live-observer.yml` remains the service-health/activation observer. It is not repurposed for SDK menu usage.

## Validation evidence

StegCore PR #118 head `5a85d7ea08ea7b12216d91858a7b484aea681412` recorded PASS for the v1.1 `SDK Usage Notification / validate` check, `bcat-check`, repository smoke checks, and repository tests. `notify` is intentionally skipped for pull-request events and is enabled only for repository-dispatch events after the workflow is present on the default branch.

SDK PR #27 head `4ed7bedaa07163a8ddaf4cc998a127aa2454d470` recorded PASS for `SDK Usage Observability Validation / validate`, including anonymous public-source materialization with no `GITHUB_TOKEN` or `GH_TOKEN` available to the SDK validation job.

These PASS records validate the feature heads identified above. Any subsequent functional code change requires fresh validation before merge.

## Completion requirements

```text
[done] five canonical option labels resolved from SDK source
[done] notification schema distinguishes menu selection from governed operation
[done] five-choice lifetime + trailing-30-day census contract installed
[done] percent / last-used / unique-runtime / status metrics installed
[done] observed-since historical boundary installed
[done] GitHub repository_dispatch projection installed
[done] v1.1 projection rejects payload/authority-bearing fields
[done] canonical SDK navigation producer implemented on SDK PR #27
[done] StegCore PR #118 v1.1 checks PASS
[done] SDK PR #27 hosted validation PASS
[pending] merge both PRs
[pending] wire actual option 0/1/2 governed execution call sites to governed-operation telemetry
[pending] implement TV/TVC outbox -> repository_dispatch bridge
[pending] execute first real end-to-end dispatch and verify issue #117 + email-capable notification surface
[pending] determine whether deterministic pre-install history can be backfilled
[pending] reconcile parent handoffs after merge/activation
```

## Activation boundary

Menu-selection producer wiring exists on the SDK feature branch, and the StegCore consumer/notification projection exists on its feature branch. Full activation still requires merge, actual governed-operation instrumentation for `0/1/2`, TV/TVC dispatch wiring, and one verified real notification.

Until those conditions are inspectably satisfied, do not report COMPLETE or ACTIVATED.

## Remaining destination ownership

```text
StegVerse-org/StegVerse-SDK
  -> merge #27 after final documentation-only validation refresh
  -> record canonical menu selections
  -> wire actual 0/1/2 governed operations to record_governed_operation

StegVerse-Labs/StegCore
  -> merge #118 after final documentation-only validation refresh
  -> receive/validate v1.1 projection
  -> preserve issue #117 as notification-only observation surface

StegVerse-Labs/TV or StegVerse-Labs/TVC
  -> own external GitHub repository_dispatch credential/authorization
  -> consume only the disclosure-safe SDK notification outbox/projection

Master Records
  -> remains canonical exact-run, route, replay, and reconstruction custody
```
