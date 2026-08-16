# StegVerse Micro-Ecosystem Mirror Handoff

## Goal

`STEGVERSE-MICRO-ECOSYSTEM-001`

Deliver the smallest portable StegVerse ecosystem unit that proves canonical StegGate/AdmittedCode governance can operate as an inspectable local micro-node ecosystem without creating a parallel evaluator, requiring a third-party host, requiring a provider account, or requiring any non-TV/TVC secret.

The portable unit has a mandatory implementation-time deployment choice:

- `S` — **StegVerse S Ecosystem / Sovereign**: an isolated, individually operated sovereign deployment.
- `NS` — **StegVerse NS Ecosystem / Node Sovereign**: a deployment profile intended to become a genuine node of the sovereign StegVerse ecosystem only after the Node Sovereign activation contract is evidenced.

The choice selects deployment topology/status. It does not create a second evaluator or change canonical StegGate governance semantics.

## Canonical owner and source of truth

- Repository: `StegVerse-Labs/StegCore`
- Canonical StegGate owner: `StegVerse-Labs/StegCore`
- Canonical runtime identity: `stegverse:steggate:canonical:three-layer:v1`
- Canonical evaluator: `stegcore.three_layer.evaluate_three_layer`
- Parent source of truth: `STEGCORE_MIRROR_HANDOFF.md`
- Node Sovereign explanation: `docs/STEGVERSE_NODE_SOVEREIGN_DEFINITION.md`
- Machine-readable Node Sovereign contract: `micro_ecosystem/node_sovereign_profile.v1.json`
- This file owns only the micro-ecosystem assembly/proof surface.

## Installed unit

```text
micro_ecosystem/manifest.json
micro_ecosystem/node_sovereign_profile.v1.json
tools/run_stegverse_micro_ecosystem.py
tests/test_stegverse_micro_ecosystem.py
docs/STEGVERSE_NODE_SOVEREIGN_DEFINITION.md
examples/steggate_allow_request.json
```

The unit imports and exercises the existing canonical StegCore evaluator. It does not fork policy semantics.

## Mandatory deployment-class choice

A requested implementation must explicitly select one and only one deployment class. No default is permitted.

### `S` — StegVerse S Ecosystem

```text
sovereignty_class: Sovereign
node_status_requested: false
isolated: true
individually_operated: true
ecosystem_membership_required: false
```

This is a sovereign StegVerse deployment that remains isolated and individually operated. It may use the same portable governance artifacts and runtime contracts but is not represented as a genuine node of the sovereign ecosystem.

### `NS` — StegVerse NS Ecosystem

```text
sovereignty_class: Node Sovereign
node_status_requested: true
node_status_self_assertable: false
ecosystem_membership_required: true
node_activation_profile: micro_ecosystem/node_sovereign_profile.v1.json
```

Selecting `NS` does not itself create node status. A local assembly proof may prove the NS profile is correctly assembled while remaining explicitly:

```text
node_activation_state: PROFILE_DEFINED_NOT_ACTIVE
membership_proof_present: false
node_sovereign_active: false
```

A genuine Node Sovereign must later satisfy the complete activation profile: continuity-bearing node identity/state, continuity envelope, receipt-bearing events, governed peer exchange, independent receiver admission, authority monotonicity, inspectable membership proof, anti-Sybil standing, recovery/reconstruction, selective participation, canonical governed-execution boundary, least-stable viable execution, and contribution receipts.

Node membership does not itself grant policy authority, execution authority, continuity-minting authority, custody, or release authority.

## Proof commands

Sovereign isolated deployment:

```bash
python tools/run_stegverse_micro_ecosystem.py \
  --deployment-class S \
  --output artifacts/stegverse-s-micro-ecosystem-proof.json
```

Node Sovereign profile assembly:

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
- `NS` proves the normative Node Sovereign profile is selected and refuses to self-accredit node membership;
- deployment class does not change canonical governance semantics;
- runtime exposes no execution authority;
- runtime exposes no continuity-minting authority;
- the unit requires no external host;
- the unit requires no provider account;
- the unit requires no non-TV/TVC secret;
- manifest, request, and result hashes are emitted.

## Node Sovereign definition recovered from prior StegVerse work

The prior portable-node architecture established that a genuine portable node is a continuity-bearing participation mechanism rather than merely an application interface. It carries or controls node identity/state and continuity, creates or preserves receipts, participates in peer exchange/corroboration, supports recovery, and can provide governed ecosystem services.

The reconciled Node Sovereign definition is now normative in `docs/STEGVERSE_NODE_SOVEREIGN_DEFINITION.md` and `micro_ecosystem/node_sovereign_profile.v1.json`.

Key rules preserved:

```text
sender admission != receiver admission
downstream authority may narrow, never silently broaden
temporal adjacency != continuity
identity equality != continuity
process persistence != continuity
reconstruction alone != continuity
admissibility != continuity
node membership != execution authority
micro-node execution != sovereign node status
continuity must not become surveillance
```

## Authority boundary

```text
portable unit != policy authority
portable unit != execution authority
portable unit != continuity minting
S sovereign isolation != ecosystem node membership
NS profile selection != ecosystem node membership
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
ASSEMBLY_INSTALLED: manifest + proof runner + tests exist
DUAL_CLASS_IMPLEMENTED: S and NS are explicit deployment classes
NODE_DEFINITION_CAPTURED: normative Node Sovereign prose + machine profile exist
LOCALLY_PROVABLE: selected class/profile assembly proof returns PASS under packaged canonical runtime
NS_PROFILE_READY: NS assembly refuses self-accreditation and identifies membership activation requirements
NODE_SOVEREIGN_ACTIVE: all required Node Sovereign capabilities and membership evidence are inspectably satisfied
HOSTED_VALIDATED: repository CI proves current assembly/tests on the implementation commit
MERGED: implementation is on main
RELEASED: explicit release authority has produced a version/tag or other governed release evidence
```

Do not collapse these states.

## Remaining work

1. Obtain hosted CI evidence for the current head, including S, NS non-self-accreditation, and invalid-class fail-closed behavior.
2. Repair only concrete failures without weakening canonical invariants.
3. Merge after required checks pass and collision review remains clean.
4. Re-read this handoff and `STEGCORE_MIRROR_HANDOFF.md` on main.
5. Update completion evidence and percentages.
6. Implement the genuine NS membership/continuity integration contract using the normative Node Sovereign profile; do not fabricate membership from local proof.
7. Bind portable node continuity identity/vault/envelope and node-to-node exchange through their destination-owned continuity/network contracts.
8. Bind membership/anti-Sybil evidence and independent receiver admission.
9. Consider a governed portable archive/container/native launcher only as a successor goal; do not make a third-party service mandatory.
10. When release/tag readiness is actually reached, verify downstream reconciliation with `StegVerse-Labs/Site`, `GCAT-BCAT-Engine/Publisher`, `StegVerse-Labs/admissibility-wiki`, and `StegVerse-002/stegguardian-wiki` under their own handoffs.

## Current claim

```yaml
task_id: STEGVERSE-MICRO-ECOSYSTEM-001
execution_owner: current implementation branch
claim_state: CLAIMED_FOR_IMPLEMENTATION
branch: feat/stegverse-micro-ecosystem-v0
collision_scope:
  - micro_ecosystem/manifest.json
  - micro_ecosystem/node_sovereign_profile.v1.json
  - tools/run_stegverse_micro_ecosystem.py
  - tests/test_stegverse_micro_ecosystem.py
  - docs/STEGVERSE_NODE_SOVEREIGN_DEFINITION.md
  - docs/STEGVERSE_MICRO_ECOSYSTEM_MIRROR_HANDOFF.md
manual_execution_allowed: true
release_condition: required CI proves both deployment classes/profile behavior and PR is merged without modifying the canonical evaluator authority boundary
next_executable_action: inspect replacement CI on the node-definition head, repair exact failures, merge when green
```

## Current assessment

```text
canonical runtime reused: complete
micro-ecosystem manifest: installed on implementation branch
mandatory S/NS implementation choice: installed
S isolated sovereign profile: installed
NS Node Sovereign profile definition: installed
NS machine-readable activation contract: installed
NS self-accreditation prevention: installed
portable proof runner: installed on implementation branch
automated S proof test: installed
automated NS non-self-accreditation proof test: installed
invalid-class fail-closed test: installed
non-TV/TVC secret dependency: none introduced
external host dependency: none introduced
provider account dependency: none introduced
actual NS network membership binding: successor integration work, not falsely claimed by local proof
hosted CI proof on current head: pending
main-branch activation: pending
release/tag: not authorized yet
```
