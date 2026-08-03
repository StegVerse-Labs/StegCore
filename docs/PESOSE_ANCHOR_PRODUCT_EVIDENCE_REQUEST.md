# PESOSE Anchor-Product Evidence Request

## Purpose

This record transfers the NSF PESOSE Track 1 anchor-product dependency from StegScholar into the canonical StegCore repository without declaring StegCore eligible, production-ready, licensed, adopted, or sponsor-ready.

## Source workstream

- Source repository: `StegVerse-Labs/StegScholar`
- Application: `FUNDING-NSF-PESOSE-2026-001`
- Source handoff: `funding/applications/active/PESOSE_SUPPORT_MIRROR_HANDOFF.md`
- Source task: `PESOSE-SUPPORT-REFERENCES-002`
- Receiving repository: `StegVerse-Labs/StegCore`
- Receiving authority boundary: StegCore maintainers own product-boundary, implementation, release, and license evidence; StegScholar owns sponsor drafting and citation control.

## Current repository evidence

As inspected on 2026-08-02:

- the repository is publicly accessible;
- `docs/STEGCORE_PROOF_ANCHOR_MIRROR_HANDOFF.md` identifies StegCore as the single technical proof anchor for StegVerse;
- `README.md` describes StegCore as a commit-time allow, deny, or defer decision engine;
- `README.md` also states that v0.1 is documentation-first;
- `README.md` states that code in `src/stegcore/` is scaffolding and substrate for future runtimes;
- no root `LICENSE` file was found;
- no evidence in this inspection establishes a sponsor-ready public product release, governing open-source license, independent users, or contributors.

Therefore StegCore is a **candidate proof anchor**, not yet a verified PESOSE anchor product.

## Required evidence package

The PESOSE anchor-product gate may be released only when StegCore maintainers provide all of the following:

1. **Product boundary**
   - exact implemented capability proposed as the existing product;
   - included and excluded modules;
   - distinction between implemented runtime behavior, specifications, tests, examples, and scaffolding.

2. **Open-source license**
   - governing root license file;
   - confirmation that the license applies to the proposed product boundary;
   - identification of incompatible or differently licensed dependencies or subtrees.

3. **Immutable release**
   - version or tag;
   - commit SHA;
   - release notes or equivalent immutable release record;
   - reproducible installation or execution instructions.

4. **Operational validation**
   - deterministic test or workflow evidence for the bounded product capability;
   - workflow run, job, logs, and artifacts where available;
   - explicit limitations and unresolved defects.

5. **Public availability**
   - public repository or release pointer suitable for a References Cited entry;
   - no reliance on private services or unpublished artifacts for the core product claim.

6. **Users and contributors**
   - inspectable evidence of current independent users or contributors;
   - no repository owner, automated bot, or proposing-team member counted as independent merely because they committed code;
   - permission pathway for three to five PESOSE collaboration letters.

7. **Authority and disclosure review**
   - maintainer approval of the product description;
   - IP/disclosure classification for sponsor use;
   - confirmation that citation and proposal language do not imply unsupported production maturity, adoption, certification, or endorsement.

## Fail-closed state

Until the complete evidence package exists:

- StegScholar must keep `ANCHOR-1` blocked;
- StegCore must not be described as a verified production product;
- repository visibility must not be treated as proof of an open-source license;
- documentation and tests must not be treated as proof of user adoption;
- the PESOSE application must remain `DRAFTING` and not submission-ready.

## Next executable action

StegCore maintainers should select one bounded implemented capability and produce a machine-readable evidence manifest containing the seven evidence classes above. If no capability satisfies the gate, record a `NO_GO` or select a different public product rather than weakening the evidence standard.

## Completion receipt location

When complete, install the StegCore-side evidence manifest at:

`evidence/pesose-anchor-product.json`

and record the release commit, validation evidence, and StegScholar consumer update in this file or its canonical successor handoff.
