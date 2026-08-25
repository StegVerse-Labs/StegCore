# StegCore Post-0.2 Release Identity Mirror Handoff

Updated: 2026-08-25
Repository: `StegVerse-Labs/StegCore`

## Purpose

Prevent moving StegCore source that contains post-0.2 canonical standing/interlock work from continuing to identify itself as frozen release `0.2.0`.

## Live source baseline

The 0.3 development line is based on current main after:

```text
PR #146 merge: 26b18204b135a213231d160b718e47ca6ab46f28
  canonical SPE standing re-hash/fail-closed consumption

PR #148 merge: 124ea6b53ff79db8f514cacf1aab295f03cacf74
  bounded public interlock -> standing -> canonical consequence traversal proof
```

The #148 runner intentionally stops before SDK interlock return assembly and does not by itself prove reciprocal return, Master Records custody, or full production activation. Those downstream proof stages are owned by the SDK successor POST_RETURN runner and successor aggregate release lane.

## Package identity

```text
historical frozen release identity: 0.2.0
moving post-0.2 source identity: 0.3.0.dev0
moving main is a release identity: FALSE
```

A build of moving source must not identify as `0.2.0`.

## Successor release intent

Target successor release identity:

```text
StegCore v0.3.0
```

No `v0.3.0` tag, immutable release commit, or publication is claimed by this handoff. The exact 0.3 executable/release coordinate must be frozen through the successor release process after package/version validation.

The successor proof capability remains:

```text
STEGCORE_SPE_STANDING_BINDING_V1
feature commit: f09eb36abcd3b317f35638e5c0b0c4a802d0aecf
```

A later 0.3 release coordinate must prove that feature commit is an ancestor or equal. Current main additionally contains #148 bounded interlock traversal.

## Resident-admission evidence caveat

PR #146 is merged, but the canonical TVC records inspected after merge do not yet contain an observed resident private-source admission receipt for exact head `f09eb36abcd3b317f35638e5c0b0c4a802d0aecf`.

Therefore:

```text
PR merged: TRUE
hosted exact-head validation: PASS
resident private-source admission receipt observed: FALSE
merge itself satisfies missing resident evidence: FALSE
```

The evidence gap must remain open and may not be retroactively inferred from merge status.

## Authority boundary

```text
version bump grants release authority: FALSE
source CI grants release authority: FALSE
GitHub merge grants TV/TVC authority: FALSE
moving main substitutes immutable release: FALSE
credential authority: TV/TVC
```

## Completion

This source lane is complete when exact-head package/version validation passes and the identity repair merges. Successor release completion additionally requires an exact 0.3 freeze, TV/TVC guarded release evidence, proof-capability containment, and downstream sovereign POST_RETURN execution.
