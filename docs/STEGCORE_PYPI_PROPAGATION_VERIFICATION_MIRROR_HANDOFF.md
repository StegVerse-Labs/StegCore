# StegCore PyPI Propagation Verification Mirror Handoff

Updated: 2026-09-11
Repository: `StegVerse-Labs/StegCore`
Goal Task ID: `STEGCORE-PYPI-PROPAGATION-VERIFICATION-001`
Parent goal: `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`
Canonical issue: `StegVerse-Labs/StegCore#203`
Status: `ACTIVE / RELEASE READY / RELEASE PUBLICATION PENDING`

## Exact release identity

```text
source repository: StegVerse-Labs/StegCore
exact release candidate commit: 282f30e9e46efc3a8d0d867f48e08c3aa6534e22
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

Publish a GitHub Release tagged exactly `v0.3.0` from commit `282f30e9e46efc3a8d0d867f48e08c3aa6534e22`. The existing workflow is the only approved publication path for this task. Do not introduce token-based Twine credentials or an alternate package name.

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

The GitHub connector available in the current session cannot create a GitHub Release. The required manual action is to open the repository Releases page, create/publish release `v0.3.0` targeting exact commit `282f30e9e46efc3a8d0d867f48e08c3aa6534e22`, and make no other source change. After publication, automated propagation verification can continue from this handoff.
