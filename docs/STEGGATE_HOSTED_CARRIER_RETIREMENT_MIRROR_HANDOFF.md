# StegGate Hosted Carrier Retirement Mirror Handoff

Updated: 2026-09-09
Repository: `StegVerse-Labs/StegCore`
Parent handoff: `STEGCORE_MIRROR_HANDOFF.md`
Originating goal: `KV-CONNECTION-REVALIDATION-WORKER-001` / `SITE-497-THIRD-PARTY-DEPENDENCY-ERADICATION`
COSV: `50000000102000`
State: SOURCE_RETIREMENT_IMPLEMENTED / VALIDATION_PENDING / RESIDENT_RUNTIME_OBSERVATION_SEPARATE
Authority effect: NONE

## Finding

The historical `.github/workflows/steggate-heartbeat-worker-reusable.yml` was still acting as a long-running GitHub-hosted StegGate micro-node. It started the canonical service in a hosted runner, downloaded Cloudflare `cloudflared`, created a `trycloudflare.com` quick tunnel, polled raw GitHub control files, self-healed the tunnel, and uploaded runtime evidence.

That behavior conflicts with the current StegVerse runtime contract:

- GitHub Actions are validation/evidence transport only, not resident execution or continuity authority;
- third-party carriers may be optional explicit fallback/interoperability paths only;
- canonical runtime execution belongs to the StegVerse resident worker/runtime;
- HB carries synchronization/freshness only and does not make a hosted runner the execution owner;
- TV/TVC remains credential authority;
- source/CI/merge are not runtime observation.

## Source retirement

The reusable workflow retains its historical `workflow_call` input shape only so callers do not silently redirect to another hosted implementation. It now:

1. uses `permissions: {}`;
2. refuses credential-bearing environments;
3. anonymously fetches exact source;
4. validates only heartbeat/lease input shape;
5. returns `RESIDENT_RUNTIME_REQUIRED` rather than hosted acceptance;
6. starts no StegGate process;
7. downloads no third-party carrier binary;
8. creates no public tunnel;
9. polls no GitHub control plane;
10. uploads no runtime artifact;
11. grants no execution, routing, publication, credential, continuity, heartbeat, or activation authority.

## Canonical continuation

```text
StegVerse resident worker/runtime
  -> canonical StegCore process
  -> resident/local StegGate service
  -> governed public rendezvous materialization when required
  -> third-party carrier only by explicit fallback selection
  -> health/self-test/evaluate observation
  -> exact runtime evidence and downstream reconciliation
```

A public rendezvous remains a real capability gap when direct public reachability is required. This source retirement does **not** claim that a provider-neutral public carrier has already been observed. It only prevents GitHub + Cloudflare from being recreated as the canonical runtime to fill that gap.

## Historical evidence

Historical GitHub-hosted/Cloudflare quick-tunnel receipts and URLs remain provenance. They may demonstrate prior compatibility or observation but must not be used as current endpoint identity, current liveness, production-continuity authority, or evidence that Cloudflare is required.

## Acceptance

- `cloudflared tunnel` absent from the active reusable workflow;
- `trycloudflare.com` absent from active workflow implementation;
- no `actions/checkout`, `actions/setup-python`, `actions/upload-artifact`, or raw GitHub control polling;
- no long-running hosted loop;
- output is `RESIDENT_RUNTIME_REQUIRED`;
- `STEGGATE_CLOUDFLARE_REQUIRED=false`;
- source validation remains non-authorizing;
- authentic resident runtime/public-rendezvous observation remains separately pending.

## Manual work

None during source retirement and validation. Do not create or authorize a Cloudflare tunnel for this task.
