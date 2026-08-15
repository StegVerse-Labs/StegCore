# StegVerse Micro-Ecosystem Mirror Handoff

## Goal

`STEGVERSE-MICRO-ECOSYSTEM-001`

Deliver the smallest portable StegVerse ecosystem unit that proves canonical StegGate/AdmittedCode governance can operate as an inspectable local micro-node ecosystem without creating a parallel evaluator, requiring a third-party host, requiring a provider account, or requiring any non-TV/TVC secret.

## Canonical owner and source of truth

- Repository: `StegVerse-Labs/StegCore`
- Canonical StegGate owner: `StegVerse-Labs/StegCore`
- Canonical runtime identity: `stegverse:steggate:canonical:three-layer:v1`
- Canonical evaluator: `stegcore.three_layer.evaluate_three_layer`
- Parent source of truth: `STEGCORE_MIRROR_HANDOFF.md`
- This file owns only the micro-ecosystem assembly/proof surface.

## Installed unit

```text
micro_ecosystem/manifest.json
tools/run_stegverse_micro_ecosystem.py
tests/test_stegverse_micro_ecosystem.py
examples/steggate_allow_request.json
```

The unit imports and exercises the existing canonical StegCore evaluator. It does not fork policy semantics.

## Proof command

```bash
python tools/run_stegverse_micro_ecosystem.py \
  --output artifacts/stegverse-micro-ecosystem-proof.json
```

The command must fail closed with a nonzero exit when any required proof invariant fails.

## Required proof invariants

- manifest schema is recognized;
- runtime identity matches the canonical StegGate identity;
- canonical owner matches StegCore;
- canonical evaluator path matches the runtime identity contract;
- deterministic four-disposition self-test is `PASS`;
- canonical three-layer binding is present;
- the canonical ALLOW fixture evaluates `ALLOW`;
- runtime exposes no execution authority;
- runtime exposes no continuity-minting authority;
- the unit requires no external host;
- the unit requires no provider account;
- the unit requires no non-TV/TVC secret;
- manifest, request, and result hashes are emitted.

## Authority boundary

```text
portable unit != policy authority
portable unit != execution authority
portable unit != continuity minting
local execution != identity authority
runtime availability != admissibility
proof receipt != custody
proof PASS != external release authorization
```

No secret or token is embedded in this unit. Any future network, publication, deployment, or credential use remains under its owning handoff and TV/TVC-managed secret boundary.

## Completion states

```text
ASSEMBLY_INSTALLED: manifest + proof runner + test exist
LOCALLY_PROVABLE: proof runner returns PASS under the packaged canonical runtime
HOSTED_VALIDATED: repository CI proves the test/runner on the implementation commit
MERGED: implementation is on main
RELEASED: explicit release authority has produced a version/tag or other governed release evidence
```

Do not collapse these states.

## Remaining work

1. Obtain hosted CI evidence for the implementation branch/PR.
2. Repair only concrete failures without weakening canonical invariants.
3. Merge after required checks pass and collision review remains clean.
4. Re-read this handoff and `STEGCORE_MIRROR_HANDOFF.md` on main.
5. Update completion evidence and percentages.
6. Consider a governed portable archive/container/native launcher only as a successor goal; do not make a third-party service mandatory.
7. When release/tag readiness is actually reached, verify downstream reconciliation with `StegVerse-Labs/Site`, `GCAT-BCAT-Engine/Publisher`, `StegVerse-Labs/admissibility-wiki`, and `StegVerse-002/stegguardian-wiki` under their own handoffs.

## Current claim

```yaml
task_id: STEGVERSE-MICRO-ECOSYSTEM-001
execution_owner: current implementation branch
claim_state: CLAIMED_FOR_IMPLEMENTATION
branch: feat/stegverse-micro-ecosystem-v0
collision_scope:
  - micro_ecosystem/manifest.json
  - tools/run_stegverse_micro_ecosystem.py
  - tests/test_stegverse_micro_ecosystem.py
  - docs/STEGVERSE_MICRO_ECOSYSTEM_MIRROR_HANDOFF.md
manual_execution_allowed: true
release_condition: required CI passes and PR is merged without modifying the canonical evaluator authority boundary
next_executable_action: open PR, inspect CI, repair exact failures, merge when green
```

## Current assessment

```text
canonical runtime reused: complete
micro-ecosystem manifest: installed on implementation branch
portable proof runner: installed on implementation branch
automated proof test: installed on implementation branch
non-TV/TVC secret dependency: none introduced
external host dependency: none introduced
provider account dependency: none introduced
hosted CI proof: pending
main-branch activation: pending
release/tag: not authorized yet
```
