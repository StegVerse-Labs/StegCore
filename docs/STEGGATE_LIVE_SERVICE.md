# StegGate Live Service

## Purpose

`stegcore.service:app` exposes the reconciled canonical StegGate admissibility matrix as an HTTP service.

The service is a decision boundary, not an authority amplifier. Canonical ALLOW/DENY/FAIL-CLOSED authority remains in StegCore. Evaluation and execution remain distinct.

## Endpoints

```text
GET  /
GET  /health
GET  /v1/capabilities
POST /v1/evaluate
GET  /v1/self-test
```

## Governed consequence boundary

```text
evaluate_three_layer
  -> evaluate_admissibility
  -> governed_steggate_execute
  -> coherence_gate
  -> injected mutation callback
```

The public HTTP service does not expose arbitrary remote mutation.

## Canonical runtime placement

StegGate has no third-party hosting-provider default.

```text
repo: StegVerse-Labs/StegCore
branch: main
runtime_provider_default: NONE
third_party_host_required: false
remote_device_connector_required: false
```

Any live origin must be explicitly supplied by the admitted StegVerse runtime composition and verified by runtime identity. Provider identity or historical deployment metadata cannot select runtime placement or processing semantics.

## Machine-owned live verification

Repository-native observer assets remain:

```text
scripts/observe_steggate_live_service.py
tests/test_steggate_live_observer.py
.github/workflows/steggate-live-observer.yml
```

An authentic live observation must verify `/health`, `/v1/self-test`, and deterministic `/v1/evaluate` behavior. Source tests or historical hosted observations do not establish current runtime activation.

## Completion rule

Functional activation requires an authentic observer receipt on the admitted StegVerse runtime surface. No third-party service object, provider account, or remote-device connector is a completion predicate.
