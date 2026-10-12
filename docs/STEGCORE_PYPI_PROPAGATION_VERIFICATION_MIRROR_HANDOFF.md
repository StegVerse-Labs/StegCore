# StegCore PyPI Propagation Verification Mirror Handoff

Updated: 2026-09-11
Repository: `StegVerse-Labs/StegCore`
Goal Task ID: `STEGCORE-PYPI-PROPAGATION-VERIFICATION-001`
Parent goal: `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`
Canonical issue: `StegVerse-Labs/StegCore#203`
Status: `RELEASE IDENTITY CONFLICT / FAIL_CLOSED FOR PUBLICATION UNTIL TV/TVC RESOLUTION`

## Exact release identity

```text
source repository: StegVerse-Labs/StegCore
historical downstream requested commit: 282f30e9e46efc3a8d0d867f48e08c3aa6534e22
frozen TVC source parent: ef38410505b0ef3e84148892b1d6e3cdef20f300
frozen TVC note-only release commit: 58445bb14642c1889cf9802666c15bd48c6d2e39
canonical source package: stegcore
source version: 0.3.0
public distribution: stegverse-stegcore
required tag: v0.3.0
publish workflow: .github/workflows/publish-pypi.yml
```

`pyproject.toml` is version `0.3.0`. `docs/STEGVERSE_STEGCORE_PYPI_DISTRIBUTION.md` fixes the public distribution identity as `stegverse-stegcore` while preserving the `stegcore` import namespace. The existing publish workflow verifies source identity, performs the deterministic distribution-name substitution only in the build workspace, builds wheel + sdist, verifies import identity, and uses PyPI Trusted Publishing only when a GitHub Release is published.

## Current observation

- `v0.3.0` tag: NOT PRESENT at reconciliation time.
- GitHub Release `v0.3.0`: NOT PRESENT at reconciliation time.
- public `stegverse-stegcore==0.3.0`: NOT PROVEN.
- connector release-mutation action in the current ChatGPT session: NOT AVAILABLE; no release publication claim is made.

## Release publication predicate

DO NOT publish `v0.3.0` from `282f30e9e46efc3a8d0d867f48e08c3aa6534e22`: this later descendant is not the immutable note-only release commit frozen under TVC. The TVC release-candidate contract specifies `58445bb14642c1889cf9802666c15bd48c6d2e39` with parent `ef38410505b0ef3e84148892b1d6e3cdef20f300`. Obtain current TV/TVC authorization and independently verify the exact tag/release state before publication. The earlier issue #203 instruction is superseded for release-target selection, not erased as historical evidence. The existing workflow is the only approved publication path for this task. Do not introduce token-based Twine credentials or an alternate package name.

## Propagation verification sequence

After the release is published:

1. verify the tag resolves exactly to the release candidate commit;
2. verify the trusted-publishing workflow succeeds;
3. verify PyPI exposes `stegverse-stegcore==0.3.0`;
4. perform an anonymous install and confirm `import stegcore` resolves version `0.3.0`;
5. rerun the downstream SDK anonymous governed-runtime installation only after public index propagation;
6. verify applicable downstream propagation in `StegVerse-Labs/Site`, `GCAT-BCAT-Engine/Publisher`, `StegVerse-Labs/admissibility-wiki`, and `StegVerse-Labs/stegguardian-wiki`;
7. feed exact publication/propagation evidence into `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`.

## Authority boundary

This task grants no governance, runtime, credential, signing, or arbitrary publication authority. GitHub Actions is publishing/evidence transport only. Existing StegCore governance and branch-protection requirements remain unchanged.

## README review

Root `README.md` was reviewed for this release task. No new runtime capability is being introduced; the public distribution name/version is already separately documented in `docs/STEGVERSE_STEGCORE_PYPI_DISTRIBUTION.md`. No README wording change is required before publication.

## Human action

The GitHub connector available in the current session cannot create a GitHub Release. The required manual action is to open the repository Releases page, do not publish a release from the historical #203 commit; resolve the TVC release authority and frozen exact commit first. No alternate machine or manual action is a prerequisite for this documentation reconciliation. After publication, automated propagation verification can continue from this handoff.
