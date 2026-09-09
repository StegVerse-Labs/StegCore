# StegGate Hosted Carrier Retirement Mirror Handoff

Updated: 2026-09-09
Repository: `StegVerse-Labs/StegCore`
Parent handoff: `STEGCORE_MIRROR_HANDOFF.md`
Originating goal: `KV-CONNECTION-REVALIDATION-WORKER-001` / `SITE-497-THIRD-PARTY-DEPENDENCY-ERADICATION`
COSV: `50000000102000`
State: PRIMARY_HOSTED_CARRIER_RETIREMENT_MERGED / FALLBACK_HOSTED_CARRIER_RETIREMENT_IN_VALIDATION / RESIDENT_RUNTIME_OBSERVATION_SEPARATE
Authority effect: NONE

## Merged correction

PR #193 merged at `084477a684193ad1b45d4403aa57844c5135638e`.

The historical `.github/workflows/steggate-heartbeat-worker-reusable.yml` no longer acts as a long-running GitHub-hosted StegGate micro-node. It no longer starts the canonical service in a hosted runner, downloads Cloudflare tunnel software, creates a Cloudflare quick tunnel, polls raw GitHub control files, self-heals a hosted tunnel, or uploads runtime evidence. Its compatibility output is `RESIDENT_RUNTIME_REQUIRED`.

## Residual defect discovered after #193

A second active workflow remained: `.github/workflows/steggate-fallback-public-runtime.yml`.

Before the current repair it still:

- launched Uvicorn on a GitHub-hosted runner;
- downloaded the Cloudflare tunnel client from GitHub releases;
- created a rotating Cloudflare quick tunnel;
- treated that public tunnel as StegGate acceptance transport;
- patched a GitHub issue comment as a runtime registry;
- could finalize activation from hosted evidence;
- created and pushed activation branches;
- uploaded runtime artifacts;
- supervised and self-healed the hosted tunnel for an extended lease window.

That is a real runtime/carrier dependency and is not acceptable as a canonical StegVerse path.

## Current repair — PR #194

PR: `https://github.com/StegVerse-Labs/StegCore/pull/194`

The fallback workflow is being reduced to an explicit manual fallback declaration only. It now:

1. has no repository-dispatch runtime trigger;
2. has no write permission;
3. refuses credential-bearing environments;
4. starts no StegGate service;
5. downloads no tunnel software;
6. creates no public tunnel;
7. mutates no GitHub registry/comment/branch;
8. finalizes no activation;
9. uploads no runtime evidence;
10. performs no hosted supervision/self-heal;
11. declares `STEGGATE_CANONICAL_RUNTIME=RESIDENT_STEGVERSE`;
12. declares `STEGGATE_THIRD_PARTY_CARRIER_REQUIRED=false`;
13. declares `STEGGATE_FALLBACK_SELECTION=EXPLICIT_OPT_IN_ONLY`.

A repository anti-regression validator now checks both historical StegGate hosted workflow surfaces so tunnel/runtime/mutation behavior cannot silently return.

## Validation boundary

The repository is private, so the new anti-regression workflow uses GitHub only as a read-only CI fallback to fetch the source under test. That CI read dependency is not runtime, routing, activation, mutation, credential, custody, or continuity authority. The first anonymous-fetch version failed because a private repository cannot be fetched anonymously; the validation workflow was repaired to use `contents: read` with `persist-credentials: false`.

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

A public rendezvous remains a real capability gap when direct public reachability is required. These source retirements do **not** claim that a provider-neutral public carrier has already been observed. They prevent GitHub + Cloudflare from being recreated as the canonical runtime merely to satisfy that gap.

## Historical evidence

Historical GitHub-hosted/Cloudflare quick-tunnel receipts and URLs remain provenance. They may demonstrate prior compatibility or observation but must not be used as current endpoint identity, current liveness, production-continuity authority, or evidence that Cloudflare is required.

## Acceptance

- primary hosted heartbeat carrier retirement: MERGED;
- fallback hosted public runtime retirement: PR #194 IN VALIDATION;
- no Cloudflare tunnel-client execution in either active canonical workflow after #194;
- no rotating Cloudflare quick-tunnel creation in either active canonical workflow after #194;
- no hosted Uvicorn StegGate runtime in either active canonical workflow after #194;
- no GitHub runtime registry mutation or activation finalization in either active canonical workflow after #194;
- canonical runtime declaration: `RESIDENT_STEGVERSE`;
- third-party carrier policy: explicit fallback only;
- authentic resident public-rendezvous observation: still pending and must not be fabricated.

## Manual work

None during source retirement and validation. Do not create or authorize a Cloudflare tunnel for this task.
