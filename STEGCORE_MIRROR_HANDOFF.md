# StegCore Mirror Handoff

## Source of truth

```text
Organization: StegVerse-Labs
Repository: StegCore
Branch: main
Completed functional goal: STEGGATE-FULL-FUNCTIONAL-ACTIVATION-001 / issue #68 CLOSED
Current integration goal: STEGGATE-HEARTBEAT-CREDENTIAL-INTEGRATION-001 / issue #75
Originating session goal: make StegGate actually functional while preserving the complete admissibility matrix and decision/execution/observation state as reconstructable reality
Canonical StegGate owner: StegVerse-Labs/StegCore
Current goal state: COMPLETE / 6 OF 6 ACCEPTANCE GROUPS SATISFIED
Session state: ACTIVE_FOR_ADJACENT_STABLE_RENDEZVOUS_RECONCILIATION
Conversation archive allowed: NO
```

Read this handoff, `management/steggate-heartbeat-credential-integration.json`, `data/steggate-live-activation-receipt.json`, `management/steggate-full-functional-activation.json`, Site issue #24/state, TV infrastructure-credential task, TVC infrastructure-credential task, and issue #75 before changing this workstream. Live repository/workflow evidence supersedes older chat summaries.

## Canonical StegGate authority chain

```text
Governance policy/evidence
  -> src/stegcore/three_layer.py:evaluate_three_layer
  -> src/stegcore/steggate.py:evaluate_admissibility
  -> complete admissibility matrix / ALLOW|DENY|REVIEW|FAIL_CLOSED
  -> src/stegcore/steggate_runtime.py:governed_steggate_execute
  -> src/stegcore/commit_governance.py:coherence_gate
  -> bounded consequence callback only after ALLOW + coherence ALLOW
  -> execution observation/reconciliation
  -> Continuity/reconstruction consumers
```

`decision.py` remains an intentionally minimal compatibility interface. Do not create a competing evaluator.

## Functional StegGate activation — COMPLETE

Issue #68 is closed. Canonical activation is persisted on `main` through merged PR #74 / merge commit `1d26a21354917a74b40a6c8f1101d91e8d2c44c0`.

Canonical receipt:

```text
data/steggate-live-activation-receipt.json
state: COMPLETE
deployment_source: heartbeat_ephemeral_micronode
observed_at: 2026-08-09T09:14:06.578269Z
observation_digest: sha256:4159d510a8c8e2d941f8c5efb8355f95ce651c328b41e22abb8be7e97b799506
receipt_digest: sha256:8fa34d07283a48e5aacf71f8f11242371de5e997b61f16b055e403c10a07df13
```

The accepted public execution proved `/health`, exact ALLOW/DENY/REVIEW/FAIL_CLOSED `/v1/self-test`, and deterministic complete-matrix `/v1/evaluate`. Persistent Render hosting and the named `stegverse.org/api/steggate` route are not prerequisites for functional StegGate activation.

## Portable / ephemeral topology — COMPLETE

`src/stegcore/portable_steggate.py` is the first-class governed-package topology. A receiver may instantiate a short-lived StegGate micro-node from the governed package/runtime profile, evaluate the canonical chain locally, invoke consequence only after ALLOW + coherence ALLOW, emit reconstructable evidence, and terminate. Networking is optional.

Hosted evidence remains run `31286273932`, job `93175594894`, artifact `9029913625`, digest `sha256:fd7b9a27eb18d6e4a061e7e7b507cceb6d6b10bef649e2198c08841a9e25e054`.

A real Ecosystem Chat consumer remains validated in `StegVerse-org/LLM-adapter`; do not duplicate that consumer authority lane.

## Heartbeat-native scheduling integration — COMPLETE

StegGate no longer has a normative wall-clock scheduler. Its public-runtime workflow accepts `repository_dispatch: stegverse-heartbeat`; manual dispatch is diagnostic only. The canonical organization heartbeat additionally has a stronger zero-extra-credential carrier: `.github` invokes StegCore's reusable heartbeat micro-node workflow directly with the exact heartbeat ID and epoch.

Authoritative surfaces:

```text
StegVerse-Labs/.github/.github/workflows/steggate-heartbeat-integration.yml
StegVerse-Labs/StegCore/.github/workflows/steggate-heartbeat-worker-reusable.yml
StegVerse-Labs/StegCore/.github/workflows/steggate-fallback-public-runtime.yml
```

Hosted proof:

```text
workflow run: 31306010854
canonical heartbeat job: 93226408727 SUCCESS
StegGate micro-node job: 93226429725 SUCCESS
heartbeat epoch: 4
heartbeat artifact: 9035958447
heartbeat artifact digest: sha256:4b71b5600ad2b1b7ccd580568b66145f811deaf389b0825f5b700bf4828631f6
micro-node artifact: 9035963753
micro-node artifact digest: sha256:b496a848c0f2561e1eb3b3dcdc33502f3019252995fa83cbe81e1c13c32651ba
```

`StegVerse-Labs/.github/control/heartbeat-state.json` durably advanced from epoch 3 to epoch 4. That canonical heartbeat directly drove the reusable StegCore micro-node through full public StegGate acceptance.

The original issue #75 wording requiring a cross-repository `repository_dispatch` from `.github` is superseded for the canonical `.github -> StegCore` path by the direct reusable-workflow carrier. This is a narrowing, not an authority expansion: it preserves the one-heartbeat scheduler and removes an unnecessary PAT/App-token dependency. StegCore still accepts `repository_dispatch` for compatible external heartbeat carriers.

## TV/TVC governed infrastructure credentials — COMPLETE CONTRACT / FAIL-CLOSED VALUE ABSENCE

### TV

Canonical task: `StegVerse-Labs/TV/tasks/TV-INFRA-CREDENTIAL-PACKAGING-001.json`.

TV packages only credential references and no-secret usage metadata for:

```text
GITHUB_CROSS_REPO_DISPATCH
CLOUDFLARE_API_TOKEN
CLOUDFLARE_ACCOUNT_ID
```

It never stores raw values. Hosted validation is green; current task state is COMPLETE / RELEASED.

### TVC

Canonical task: `StegVerse-Labs/TVC/tasks/TVC-INFRA-CREDENTIAL-AUTHORITY-001.json`.

TVC exact-bound secret-reference authority is hosted-green for heartbeat dispatch and Site Cloudflare rendezvous use. Validation run `31305690694`, job `93225596181`, artifact `9035862288`, digest `sha256:a6ff49884bd4199f7b6f4ff8999d860d4517b547a4fd495118ccc59c00070562` proved allow/deny scope/binding semantics and `credentials_recorded=false`.

TVC publishes the no-secret consumer contract at `contracts/infrastructure-credential-consumer-authority.v1.json`. Site imports the pinned contract; TVC does not transport secret values.

## Stable StegVerse rendezvous — ADJACENT HARDENING / BLOCKED ON VALUE PRESENCE

Owner: `StegVerse-Labs/Site#24`.

The Site rendezvous workflow now has no cron scheduler. It accepts `stegverse-heartbeat`, diagnostic manual dispatch, and bounded configuration pushes. It validates the pinned TVC authority contract before checking the execution environment for Cloudflare values.

Run `31305845192`, job `93225990737`, proved:

```text
pinned TVC authority import: PASS
credential reference authority: admissible
CLOUDFLARE_API_TOKEN value present: NO
CLOUDFLARE_ACCOUNT_ID value present: NO
deployment: SKIPPED
state: FAIL_CLOSED_CREDENTIAL_ABSENT
artifact: 9035908600
artifact digest: sha256:fe1be4cbdb0cd0a87542fe1ee40b2a1dad561c9355b5647cbfdd187c331c2af8
```

This is not a StegGate functional blocker. It is stable-routing hardening. Release condition: both referenced Cloudflare values become available in the Site execution environment; then the heartbeat-triggered workflow may deploy and validate `https://stegverse.org/api/steggate`. TV/TVC cannot manufacture absent credential values.

## Current execution inventory

Authoritative current-goal inventory: `management/steggate-heartbeat-credential-integration.json`.

```text
HBI-01 heartbeat-only StegCore trigger surface                         COMPLETE
HBI-02 canonical heartbeat -> public StegGate micro-node proof         COMPLETE
HBI-03 TV infrastructure credential-reference packaging                COMPLETE
HBI-04 TVC exact-bound no-secret authority                              COMPLETE
HBI-05 Site TVC-consumer integration + credential-absence fail-close    COMPLETE
HBI-06 handoff/inventory/scheduler reconciliation                       COMPLETE
```

Current integration goal: `6/6 = 100%`.

## Collision controls

- `.github#12` owns the single StegVerse heartbeat.
- Heartbeat cadence/epoch does not grant execution authority.
- StegCore owns StegGate evaluation/runtime; Site must not copy StegGate policy logic.
- TV owns credential-reference packaging/usage evidence, not secret values.
- TVC owns secret-reference read authority, not secret values or StegGate admissibility.
- Site #24 owns stable endpoint publication/discovery.
- LLM-adapter #18 remains the real-provider/custody owner for Ecosystem Chat.
- Render remains optional hosting, not architectural authority.

## Next integration goal candidate

Because `STEGGATE-HEARTBEAT-CREDENTIAL-INTEGRATION-001` is complete, the directly related candidate is stable rendezvous hardening under existing canonical owner `StegVerse-Labs/Site#24`.

Do not create a competing StegCore implementation lane. The current state there is `BLOCKED_CREDENTIAL_VALUES_ABSENT`, with a machine-observable release condition already installed. This session retains only reconciliation/support responsibility until the adjacent Site handoff/task state reflects the heartbeat/TVC changes.

## Completeness

```text
functional StegGate goal: 100%
heartbeat/credential integration goal: 100%
developed current-goal files: 13/13
scaffolding/stubs: 0
validation groups: 6/6
integration groups: 6/6
session consolidation for current goal: 5/6
archive readiness: NO — adjacent stable-rendezvous state still needs final durable reconciliation
```
