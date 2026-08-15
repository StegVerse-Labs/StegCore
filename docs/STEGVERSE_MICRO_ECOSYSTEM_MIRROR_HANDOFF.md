# StegVerse Micro-Ecosystem Mirror Handoff

## Goal

`STEGVERSE-MICRO-ECOSYSTEM-001`

Deliver the smallest portable StegVerse ecosystem unit that proves canonical StegGate/AdmittedCode governance can operate as an inspectable local micro-node ecosystem without creating a parallel evaluator, requiring a third-party host, requiring a provider account, or requiring any non-TV/TVC secret.

The portable unit has a mandatory implementation-time deployment choice:

- `S` — **StegVerse S Ecosystem / Sovereign**: an isolated, individually operated sovereign deployment.
- `NS` — **StegVerse NS Ecosystem / Node Sovereign**: a genuine node of the sovereign StegVerse ecosystem.

The choice selects deployment topology/status. It does not create a second evaluator or change canonical StegGate governance semantics.

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

## Mandatory deployment-class choice

A requested implementation must explicitly select one and only one deployment class. No default is permitted.

### `S` — StegVerse S Ecosystem

```text
sovereignty_class: Sovereign
genuine_sovereign_ecosystem_node: false
isolated: true
individually_operated: true
ecosystem_membership_required: false
```

This is a sovereign StegVerse deployment that remains isolated and individually operated. It may use the same portable governance artifacts and runtime contracts but is not represented as a genuine node of the sovereign ecosystem.

### `NS` — StegVerse NS Ecosystem

```text
sovereignty_class: Node Sovereign
genuine_sovereign_ecosystem_node: true
ecosystem_membership_required: true
```

This is a Node Sovereign deployment and must be represented as a genuine node of the sovereign StegVerse ecosystem. Node membership does not itself grant policy authority, execution authority, continuity-minting authority, custody, or release authority.

## Proof commands

Sovereign isolated deployment:

```bash
python tools/run_stegverse_micro_ecosystem.py \
  --deployment-class S \
  --output artifacts/stegverse-s-micro-ecosystem-proof.json
```

Node Sovereign deployment:

```bash
python tools/run_stegverse_micro_ecosystem.py \
  --deployment-class NS \
  --output artifacts/stegverse-ns-micro-ecosystem-proof.json
```

Omitting `--deployment-class` is an invalid implementation request and the CLI refuses to run. An unknown class fails closed in the callable proof path.

## Required proof invariants

- manifest schema is recognized;
- runtime identity matches the canonical StegGate identity;
- canonical owner matches StegCore;
- canonical evaluator path matches the runtime identity contract;
- deterministic four-disposition self-test is `PASS`;
- canonical three-layer binding is present;
- the canonical ALLOW fixture evaluates `ALLOW`;
- deployment choice is explicit;
- selected deployment class is recognized;
- `S` proves isolated + individually operated + non-node status;
- `NS` proves genuine sovereign ecosystem node + membership-required status;
- deployment class does not change canonical governance semantics;
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
S sovereign isolation != ecosystem node membership
NS ecosystem node membership != policy authority
NS ecosystem node membership != execution authority
local execution != identity authority
runtime availability != admissibility
proof receipt != custody
proof PASS != external release authorization
```

No secret or token is embedded in this unit. Any future network, publication, deployment, or credential use remains under its owning handoff and TV/TVC-managed secret boundary.

## Completion states

```text
ASSEMBLY_INSTALLED: manifest + proof runner + test exist
DUAL_CLASS_IMPLEMENTED: S and NS are explicit, independently testable deployment classes
LOCALLY_PROVABLE: selected class proof runner returns PASS under the packaged canonical runtime
HOSTED_VALIDATED: repository CI proves both classes and fail-closed invalid choice on the implementation commit
MERGED: implementation is on main
RELEASED: explicit release authority has produced a version/tag or other governed release evidence
```

Do not collapse these states.

## Remaining work

1. Obtain hosted CI evidence for both `S` and `NS` on the implementation PR head.
2. Repair only concrete failures without weakening canonical invariants.
3. Merge after required checks pass and collision review remains clean.
4. Re-read this handoff and `STEGCORE_MIRROR_HANDOFF.md` on main.
5. Update completion evidence and percentages.
6. Successor work for `NS` must bind actual sovereign ecosystem membership/continuity transport through its owning network/continuity contracts; do not fabricate node membership from the local proof alone.
7. Consider a governed portable archive/container/native launcher only as a successor goal; do not make a third-party service mandatory.
8. When release/tag readiness is actually reached, verify downstream reconciliation with `StegVerse-Labs/Site`, `GCAT-BCAT-Engine/Publisher`, `StegVerse-Labs/admissibility-wiki`, and `StegVerse-002/stegguardian-wiki` under their own handoffs.

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
release_condition: required CI proves both deployment classes and the PR is merged without modifying the canonical evaluator authority boundary
next_executable_action: inspect replacement CI on the dual-class head, repair exact failures, merge when green
```

## Current assessment

```text
canonical runtime reused: complete
micro-ecosystem manifest: installed on implementation branch
mandatory S/NS implementation choice: installed
S isolated sovereign profile: installed
NS Node Sovereign profile: installed
portable proof runner: installed on implementation branch
automated S proof test: installed
automated NS proof test: installed
invalid-class fail-closed test: installed
non-TV/TVC secret dependency: none introduced
external host dependency: none introduced
provider account dependency: none introduced
actual NS network membership binding: successor integration work, not falsely claimed by local proof
hosted CI proof on dual-class head: pending
main-branch activation: pending
release/tag: not authorized yet
```
