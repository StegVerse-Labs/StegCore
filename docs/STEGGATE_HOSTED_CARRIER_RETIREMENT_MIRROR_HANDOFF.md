# StegGate Hosted Carrier Retirement Mirror Handoff

Updated: 2026-09-09
Repository: `StegVerse-Labs/StegCore`
Parent handoff: `STEGCORE_MIRROR_HANDOFF.md`
Originating goal: `KV-CONNECTION-REVALIDATION-WORKER-001` / `SITE-497-THIRD-PARTY-DEPENDENDENCY-ERADICATION`
COSV: `50000000102000`
State: PRIMARY_HOSTED_CARRIER_RETIREMENT_MERGED / FALLBACK_HOSTED_CARRIER_RETIREMENT_MERGED / ANTI_REGRESSION_VALIDATED / RESIDENT_RUNTIME_OBSERVATION_SEPARATE
Authority effect: NONE

## Merged corrections

PR #193 merged at `084477a684193ad1b45d4403aa57844c5135638e`.

PR #194 merged at `07632a7dcbd12d16440322f33269a51413fa3049` after `No Required Hosted StegGate Carrier` run `34312571953` completed SUCCESS on exact PR head `b5c44cda574889dafacd8d53a8ae720fcfaf1d24`.

The two historical GitHub-hosted StegGate execution surfaces are now retired from runtime/carrier duty:

- `.github/workflows/steggate-heartbeat-worker-reusable.yml`
- `.github/workflows/steggate-fallback-public-runtime.yml`

Neither active workflow now starts Uvicorn, downloads Cloudflare tunnel software, creates a Cloudflare quick tunnel, polls GitHub as a runtime control plane, mutates a GitHub runtime registry, finalizes activation, pushes activation branches, uploads runtime evidence, or self-heals a hosted tunnel.

The heartbeat compatibility surface returns `RESIDENT_RUNTIME_REQUIRED`. The fallback surface is a manual declaration only and states:

- `STEGGATE_CANONICAL_RUNTIME=RESIDENT_STEGVERSE`
- `STEGGATE_HOSTED_RUNTIME=false`
- `STEGGATE_HOSTED_PUBLIC_TUNNEL=false`
- `STEGGATE_THIRD_PARTY_CARRIER_REQUIRED=false`
- `STEGGATE_FALLBACK_SELECTION=EXPLICIT_OPT_IN_ONLY`
- `STEGGATE_GITHUB_RUNTIME_AUTHORITY=NONE`
- `STEGGATE_ACTIVATION_EFFECT=NONE`
- `STEGGATE_REPOSITORY_MUTATION=NONE`
- `STEGGATE_RUNTIME_EVIDENCE_CREATED=false`

## Anti-regression boundary

`scripts/check_no_required_hosted_steggate_carrier.py` and `.github/workflows/no-required-hosted-steggate-carrier.yml` verify both historical hosted workflow surfaces remain free of executable hosted-carrier behavior.

Because this repository is private, GitHub is still used by that check as a read-only validation fallback with `contents: read` and `persist-credentials: false`. That validation transport does not own StegGate runtime, routing, activation, mutation, credential, custody, heartbeat, continuity, or publication state.

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

A provider-neutral/StegVerse-owned public rendezvous remains a real capability gap when direct public reachability is required. The merged source retirements do not claim that such a rendezvous has already been observed. They prevent GitHub + Cloudflare from being recreated as the canonical runtime merely to satisfy that gap.

## Historical evidence

Historical GitHub-hosted/Cloudflare quick-tunnel receipts and URLs remain provenance. They may demonstrate prior compatibility or prior observation but must not be used as current endpoint identity, current liveness, production-continuity dependency, or evidence that Cloudflare is required.

## Acceptance

- primary hosted heartbeat carrier retirement: MERGED #193;
- fallback hosted public runtime retirement: MERGED #194;
- anti-regression exact-head validation: PASS;
- Cloudflare tunnel-client execution in the two retired runtime workflows: NONE;
- rotating Cloudflare quick-tunnel creation in the two retired runtime workflows: NONE;
- hosted Uvicorn StegGate runtime in the two retired runtime workflows: NONE;
- GitHub runtime registry mutation/activation finalization in the two retired runtime workflows: NONE;
- canonical runtime declaration: `RESIDENT_STEGVERSE`;
- third-party carrier policy: explicit fallback only;
- authentic resident provider-neutral public-rendezvous observation: PENDING and must not be fabricated.

## Remaining dependency work

1. Reconcile downstream Site/provider inventories so they no longer classify Cloudflare quick tunnels as canonical or required runtime carriers.
2. Continue eliminating required GitHub publication/source/recovery dependence while retaining GitHub only as optional source/validation transport.
3. Establish deterministic DNS/edge portability and recovery so no single DNS/edge vendor is a continuity prerequisite.
4. Materialize and authentically observe a resident/provider-neutral public rendezvous before claiming public-carrier independence at runtime.
5. Preserve third-party carriers only as explicit fallback/interoperability choices.

## Manual work

None required. Do not create or authorize a Cloudflare tunnel for this task.
