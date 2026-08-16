# StegVerse Node Sovereign Definition

## Purpose

This document captures the implementation definition for a genuine **StegVerse NS Ecosystem / Node Sovereign** deployment so future portable-unit work does not reduce node status to application installation, runtime availability, or a self-declared label.

Machine-readable companion:

```text
micro_ecosystem/node_sovereign_profile.v1.json
```

## Core definition

A **Node Sovereign** deployment is a genuine continuity-bearing participation endpoint of the sovereign StegVerse ecosystem.

It is not merely:

- an installed StegVerse application;
- a running StegGate process;
- a local model;
- a heartbeat;
- a reachable service;
- a transport connection;
- a micro-node work unit;
- an isolated sovereign deployment; or
- a deployment that calls itself a node.

A Node Sovereign must establish its own node identity and continuity state, participate through governed interoperable exchange, independently admit received transitions, preserve reconstructable receipt chains, prove ecosystem membership without self-accreditation, and retain the StegGate authority boundary for consequential actions.

## Relationship to S deployments

### StegVerse S Ecosystem — Sovereign

An `S` deployment is sovereign because it is isolated and individually operated. It may run the same canonical StegGate/AdmittedCode governance core and may possess local continuity, receipts, local models, and user-controlled data.

It does **not** claim genuine sovereign-ecosystem node membership.

### StegVerse NS Ecosystem — Node Sovereign

An `NS` deployment adds an ecosystem relationship that must be established and evidenced. Node Sovereign status therefore requires more than local sovereignty.

The distinction is:

```text
S  = sovereign operation without required ecosystem membership
NS = sovereign operation + established governed node membership
```

Membership does not transfer or enlarge canonical StegGate authority.

## Minimum activation contract

A deployment may claim `NODE_SOVEREIGN_ACTIVE` only when all required activation capabilities in `node_sovereign_profile.v1.json` are inspectably satisfied.

### 1. Portable node continuity identity

The node requires a continuity-bearing identity that belongs to the portable node, not to a cloud provider, AI vendor account, IP address, host URL, transport tunnel, or model runtime.

The identity must support continuity across recovery, runtime replacement, and transport changes without treating mere identity equality as proof of continuity.

### 2. Local continuity state / vault

The node must retain or control the continuity material necessary to reconstruct its governed state. At minimum this includes applicable identity material, prior-state linkage, policy/evidence references, receipts, recovery material, and continuity metadata.

This may be implemented through a local continuity vault or a compatible user/node-controlled substrate.

### 3. Shared continuity envelope

Artifacts and events exchanged or preserved by the node need a stable continuity representation capable of binding, as applicable:

```text
object/event identity
created / observed / received time
origin node
artifact hash
metadata hash
previous receipt
custody events
disclosure posture
correlation permissions
attached evidence profiles
signatures or verification references
```

Evidence profiles may evolve independently; they do not retroactively create the continuity chain.

### 4. Artifact and event receipts

Meaningful capture, observation, governed transition, exchange, and contribution events must be receipt-bearing or linked to reconstructable receipts.

Receipts should support replay/reconstruction and should distinguish observation, evidence characterization, admission, execution, custody, and settlement roles rather than collapsing them.

### 5. Governed node-to-node exchange

An NS deployment requires at least one real governed node-to-node exchange path. Transport is implementation-neutral: direct, relayed, queued, MCP/A2A, StegTalk, local network, or another compatible carrier may move information.

Transport itself never grants authority.

### 6. Independent receiver admission

A sender's StegGate result does not authorize the receiving node.

The receiving Node Sovereign must independently evaluate the exact incoming candidate under its current authority, policy, evidence, continuity, and affected-entity conditions.

Canonical rule:

```text
sender admission != receiver admission
```

### 7. Authority monotonicity

During forwarding, delegation, transformation, or downstream use:

```text
downstream authority may narrow
but may never silently broaden
```

A denied, stale, incomparable, or insufficient upstream admission cannot be promoted into broader onward authority merely because another node received it.

### 8. Membership proof and anti-Sybil standing

A node cannot self-accredit as `NS`.

There must be inspectable evidence that the deployment has been admitted as a genuine sovereign-ecosystem node under the applicable membership mechanism. That mechanism must also prevent or materially constrain fake-node creation, self-corroboration through controlled identities, and duplicate standing created solely to manipulate corroboration, contribution, quorum, or rewards.

The exact admission authority/mechanism can evolve, but the requirement for externally established node standing cannot disappear.

### 9. Recovery and reconstruction

The node must be recoverable or reconstructable from preserved continuity material and receipts when its runtime, device, host, or transport changes.

However:

```text
reconstruction != continuity unless the governed relationship is established
process persistence != continuity
runtime uptime != continuity
identity equality != continuity
```

Recovery proves the node can reconstruct state; continuity requires the governed relationship across the states.

### 10. Selective network participation and privacy

The node must remain useful even when the user contributes nothing to the wider network.

Participation should be explicit and graduated. A user may choose, where supported, among postures such as:

```text
local only
anonymous existence confirmation
privacy-preserving presence/corroboration
encrypted trusted-group exchange
research contribution
public evidence submission
```

Node status must not become a surveillance mandate. Presence or corroboration should reveal only what is necessary for the authorized claim and need not expose civil identity, long-term location history, home address, unrelated nearby activity, or a full social graph.

### 11. Governed execution boundary

Node membership does not itself authorize consequences.

Consequential transitions continue through the canonical StegGate/AdmittedCode governance path. A node's availability, membership, contribution history, transport identity, model confidence, or economic standing cannot substitute for a current admissibility decision.

### 12. Least-stable viable execution

Execution capability inside a Node Sovereign should be minimized to the capability actually admitted for the task. Least-stable viable micro-node construction and ephemeral-by-default execution are preferred where viable.

Micro-nodes remain scoped, receipt-bearing, revocable work units. They do not become sovereign merely because they execute inside a Node Sovereign.

### 13. Contribution receipts and economic transparency

A Node Sovereign may provide useful ecosystem capacity such as relay, storage, compute, preservation, verification, research, correlation, or testing.

Such contribution should be attributable through receipts showing, when applicable:

```text
what the node contributed
who or what used it
what authority permitted the use
what value/service was produced
what fee or credit was generated
what the node received
what the ecosystem retained
what receipt proves the accounting
```

Economic capacity may purchase service. It may not purchase truth, evidence standing, private access, policy authority, execution authority, or node admission.

## Minimum personal utility

A portable node should provide direct value before asking a user to contribute to the wider network. The minimum useful direction previously identified includes:

- private governed interaction / Ecosystem Chat;
- local or user-controlled memory and continuity state;
- secure communication;
- capture and preservation with provenance;
- authorship/timing or receipt evidence where applicable;
- recovery;
- user-controlled sharing.

A healthy adoption loop is therefore:

```text
immediate personal utility
→ routine voluntary use
→ continuity-bearing receipts
→ independent node exchange/corroboration
→ stronger ecosystem continuity and knowledge
→ increased utility
```

## Optional node services

The following are ecosystem services, not prerequisites for every node unless a specific profile requires them:

- privacy-preserving peer presence correlation;
- multimodal event correlation;
- repository-specific evidence-profile evaluation;
- storage contribution;
- compute/inference contribution;
- relay/delivery;
- independent verification;
- research contribution;
- provisional contribution credits;
- StegCoin service settlement;
- StegToken earned standing or governance eligibility.

A node may legitimately provide none, some, or many of these while retaining node status if its minimum activation contract remains satisfied.

## Node Sovereign status is fail-closed

The implementation must refuse the `NODE_SOVEREIGN_ACTIVE` claim when any required membership or continuity invariant is absent.

Examples include:

```text
self-declared NS with no membership proof                  -> FAIL_CLOSED
running StegGate but no node continuity identity          -> FAIL_CLOSED
peer packet accepted solely because sender allowed it     -> FAIL_CLOSED
downstream capability exceeds admitted upstream scope     -> FAIL_CLOSED
fake/duplicate identity can manufacture node standing     -> FAIL_CLOSED
node state cannot be linked to prior governed state        -> FAIL_CLOSED
execution bypasses canonical StegGate                      -> FAIL_CLOSED
```

This prevents the ecosystem from accumulating nominal nodes that are actually unrelated sovereign installations, transient processes, or ungoverned peers.

## Concise explanation

A **StegVerse S Ecosystem** owns and governs itself.

A **StegVerse NS Ecosystem** owns and governs itself **and has an established, receipt-bearing, independently admissible relationship with the wider sovereign StegVerse ecosystem**.

That relationship—not software installation—is what makes it a genuine node.
