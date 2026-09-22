# Repository Hygiene Adoption Mirror Handoff

Updated: 2026-09-21
Repository: `StegVerse-Labs/StegCore`
Goal Task ID: `HYGIENE-CAUSAL-ROOTS-001`
COSV task.v1: `10100000100000`
Canonical ecosystem handoff: `StegVerse-Labs/.github/docs/REPOSITORY_HYGIENE_MIRROR_HANDOFF.md`
Repository role: terminal sink / canonical StegGate runtime owner
Observed pre-adoption branch count: `138`

## Adoption

This private repository uses an in-repository thin caller with `contents: read` only and no retained checkout credentials. It invokes the shared classifier workflow pinned to `3928394653f3be42e58bb0e791b56956de3506d4`; the shared workflow acquires the current canonical classifier read-only from StegVerse-Labs/.github.

The classifier inventories ancestry and default-branch references and produces non-authorizing evidence. It cannot delete branches, close PRs/issues, grant runtime/release/governance authority, or treat age/name as deletion authority. Actual ref mutation remains solely under `HYGIENE-BRANCH-REF-RETIREMENT`.

The central public-repository bulk census could not anonymously clone StegCore. That transport failure is not a classification result. This caller is the private-repository baseline path.
