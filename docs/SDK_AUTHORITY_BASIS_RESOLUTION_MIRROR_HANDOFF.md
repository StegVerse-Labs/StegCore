# SDK Authority Basis Resolution Mirror Handoff

Goal Task ID: `SDK-EVALUATOR-GOVERNANCE-POSTURE-MANIFEST-001`
Repository: `StegVerse-Labs/StegCore`
Supporting branch: `sdk-authority-basis-resolution-001`
Status: `VALIDATED_MERGED`

## Determination

The structured-role gap is not caused by a hidden general role resolver that the SDK merely failed to expose.

Canonical StegCore already requires resolved commit-time authority and delegation facts, and its current runtime separately verifies present authority state, target binding, temporal validity, and evidence currentness. The repository also contains authority/delegation record schemas for the correctability domain. Adjacent repositories contain domain-specific role-transition enforcement (StegEntity), delegation eligibility (Ecosystem-Delegation), node authority classes (StegOS), and scoped authority issuance/verification (TV/TVC).

None of those existing surfaces is a general external-organizational role hierarchy resolver that may safely be copied into the SDK. StegCore's canonical three-layer contract explicitly expects already-resolved authority/delegation facts. Therefore the missing evaluator capability is a bounded compilation/resolution seam, not a new authority plane.

## Implemented seam

`src/stegcore/authority_basis.py` adds a deterministic, non-authorizing evaluator-facing resolver over frozen structured assertions.

Inputs bind:

- exact actor identity;
- optional role label for preserved context only;
- exact candidate action, target, and scope;
- authority assertions with status, time window, source reference, and evidence references;
- delegation assertions, when delegation is required;
- explicit `authority_basis_complete` / `delegation_basis_complete` declarations;
- the evaluation instant.

Outputs derive:

- `actor_authority_current`;
- `delegation_current`;
- ALLOW / DENY / FAIL_CLOSED current-basis disposition;
- selected assertion identities and evidence references;
- target binding when current authority is established.

The resolver does not interpret a role label as authority, issue or mint authority, verify TVC credentials, mutate policy, perform governance execution, or replace Interlock/InTr.

## Fail-closed semantics

```text
role label alone -> no authority effect
incomplete authority basis with no match -> FAIL_CLOSED
complete authority basis with no current candidate-covering match -> DENY
delegation required + incomplete delegation basis with no match -> FAIL_CLOSED
delegation required + complete basis with no current candidate-covering match -> DENY
current scoped authority (+ current required delegation) -> ALLOW currentness facts
```

An ALLOW from this resolver is not execution authority. It establishes only the represented authority/delegation currentness facts that canonical StegGate consumes downstream.

## Authority boundaries

```text
structured evaluator evidence -> StegCore authority-basis resolution
StegCore resolution -> currentness facts for StegGate
StegGate -> admissibility
Interlock/InTr -> governed transition authority
TV/TVC -> protected credential / scoped authority issuance and verification
Master Records -> organization records/reconstruction where applicable
```

The SDK must not gain an independent role-policy engine, token issuer, credential verifier, or authority graph with separate semantics.

## Current implementation

Created on branch `sdk-authority-basis-resolution-001` from StegCore main `1410c110983ae44c10be17f8180ca20066c526cc`:

```text
src/stegcore/authority_basis.py
tests/test_authority_basis.py
README.md
docs/SDK_AUTHORITY_BASIS_RESOLUTION_MIRROR_HANDOFF.md
```

Focused tests cover role-label non-authority, scoped authority matching, missing-basis fail-closed behavior, current delegated authority, and revoked-delegation denial.

## Validation state

Exact-head `acf210f073a8d4350f56642b1ac6119fc68fbe52` passed the focused Authority Basis Resolution Validation in workflow run `35287845446`, the StegVerse 001/002 Validator in run `35287845509`, and StegCore Package Version Identity Validation in run `35287845651`. The BCAT lane was not applicable and was skipped rather than asserted as a credential-authority pass.

PR #219 merged with expected-head protection to StegCore main as `1c045362726fd7ede0af3c1d6afb960d8dff70b8`. That merge is now the canonical SDK authority-basis resolver source pin.

No live TV/TVC credential verification, live Interlock/InTr execution, or production role-policy resolution is claimed by this change.

## SDK integration completion

The SDK integration steps are complete at the merged source-contract level. The public SDK now preserves the structured request as non-authorizing evidence, invokes an injected canonical resolver rather than reimplementing StegCore semantics, binds the resulting authority/delegation currentness facts into the exact governance request, preserves the resolution binding, rejects pre-authored currentness conclusions, and documents the proven claim boundary. SDK completeness integration merged through PR #254 as `16d4bf1e40b4eac7313b3399e48ab880a6f53001`; final SDK source closeout merged through PR #255 as `ca5b349b76a3548a385aa65299d8b08664feedaa`.

The parent Goal Task remains ACTIVE because authentic SDK-to-live StegOS/InTr posture-bound governance execution is still unproven. This supporting StegCore source work does not claim public resolver distribution, live TV/TVC credential verification, live Interlock/InTr transition execution, or production role-policy resolution.

## Manual work

None.


## Completeness correction — 2026-09-17

Post-merge review identified one material unknown-versus-false edge in the first resolver revision: a non-matching assertion set cannot prove absence of authority unless the caller also asserts that the relevant basis is complete. Treating any non-matching partial set as DENY would convert missing evidence into an affirmative negative finding.

The patch on `authority-basis-completeness-001` therefore requires explicit `authority_basis_complete` and `delegation_basis_complete` booleans. A matching current assertion can establish TRUE regardless of set completeness. When no match exists, incomplete basis remains UNKNOWN/FAIL_CLOSED; only a declared complete basis can establish FALSE/DENY.

This correction preserves StegCore's canonical UNKNOWN-versus-false contract. Exact head `df03835dfa8046da190521d7ef55ece9634a576a` passed Authority Basis Resolution Validation run `35288540217`, StegVerse 001/002 validation, and package-version identity validation; PR #221 then merged with expected-head protection as `f45d52cb62db29418d88752fe38f68e9bcc3cf12`. The canonical resolver now requires explicit authority/delegation basis completeness before a no-match condition can establish FALSE/DENY.
