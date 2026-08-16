# StegOS SDK Distribution Profile

## Purpose

Preserve established StegOS design rules while binding future StegOS builds to the same portable SDK distribution lifecycle used by StegVerse S and NS ecosystem packages.

## Established StegOS design rules

StegOS begins as a governed node operating layer, not a general-purpose phone/desktop OS. Its first-class properties are:

```text
low-power
offline-first
receipt-bound
safety-aware
network-modal
identity-aware
replacement-friendly
governed state transitions
```

StegOS internal responsibilities are software-governance nodes rather than a monolithic kernel surface. Expected internal nodes include identity, policy, session, transition, receipt, storage, network-gate, display-gate, power-scheduler, safety, attestation, and recovery responsibilities. Peripheral devices declare their own device-specific node specifications and are governed through shared transition rules.

Canonical architectural references:

```text
StegVerse-Labs/StegLenses/docs/STEGOS_CASE.md
StegVerse-Labs/StegLenses/docs/STEGOS_NODE_STRUCTURE.md
```

## Distribution lifecycle

StegOS follows the same evidence-driven lifecycle as other portable StegVerse products:

```text
canonical source
-> reproducible build
-> deterministic distributable artifacts
-> artifact receipt + SHA-256
-> SDK_EARLY_ACCESS
-> SDK_COMMUNITY
-> APP_PRODUCT_CANDIDATE
-> PAID_PRODUCT_CANDIDATE
```

No stage automatically promotes to the next stage.

## Deployment classes

A future StegOS SDK offering must preserve the explicit ecosystem deployment class selected for the installation:

```text
S  = isolated Sovereign deployment
NS = Node Sovereign profile requiring separate genuine-node activation evidence
```

StegOS may additionally declare an OS hardware/runtime profile, architecture, peripheral profile, or image type. Those are compatibility/build dimensions and do not replace S/NS sovereignty class.

Examples:

```text
S + stegos-simulator
S + stegos-arm64
NS + stegos-arm64
NS + stegos-lenses-reference
```

Selecting or installing an NS StegOS image does not create Node Sovereign membership.

## Required downloadable formats

Every portable SDK release package must publish both:

```text
*.zip
*.tar.gz
```

Both archives must contain the same declared payload and package receipt and must be independently hash-bound in the release catalog. A client may choose either format according to platform/tooling needs.

For StegOS, a release may additionally include bootable/installable image formats where appropriate, for example an image, disk image, installer bundle, or architecture-specific artifact. Such an image is an additional governed artifact; it does not replace the required `.zip` and `.tar.gz` source/runtime package pair unless a later explicit profile supersedes this rule.

## GitHub build allowance

StegOS artifacts may be created through the canonical GitHub repository or GitHub Actions when useful for reproducible source/build validation, provided all of the following remain true:

```text
GitHub is build/distribution infrastructure only
GitHub is not StegOS runtime authority
GitHub is not StegGate authority
GitHub is not Node Sovereign membership authority
no GitHub token becomes deployed runtime authority
protected credential semantics remain TV/TVC
build inputs are commit-pinned
build outputs are immutable/hash-bound before SDK activation
release receipt records source commit + build profile + artifact hashes
```

A GitHub-generated artifact is not automatically a governed release merely because a workflow succeeded. SDK remote download activates only after exact artifact locators and hashes are bound into the governed catalog.

## StegOS-specific proof requirements

In addition to the common portable-package checks, a StegOS release profile should prove as applicable:

```text
source commit identity
build profile / target architecture
archive hashes
image hash if present
boot or simulator-start proof
internal node manifest integrity
hardware/peripheral compatibility declaration
network-closed default
modal network transition behavior
receipt emission
update provenance
rollback capability
recovery/reconstruction capability
replacement/re-pairing behavior
no embedded protected secret material
S/NS deployment-class preservation
NS installation does not self-accredit membership
```

## Authority boundary

```text
build success != release authority
artifact verification != execution authority
installation != activation
boot success != admissibility
StegOS S install != ecosystem membership
StegOS NS install != Node Sovereign membership
GitHub artifact != runtime authority
transport availability != authority
```

## Successor implementation requirement

When the canonical StegOS implementation repository is selected/activated for production work, first recover its own `*_MIRROR_HANDOFF.md` and related repository build instructions. Reconcile those rules with this distribution profile rather than replacing them.
