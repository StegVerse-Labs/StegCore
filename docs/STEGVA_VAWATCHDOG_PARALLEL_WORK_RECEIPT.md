# StegVA and VAwatchdog Parallel-Work Receipt

## Review target

```text
StegVerse-Labs/VAwatchdog
StegVerse-Labs/StegCore/docs/STEGVA_MIRROR_HANDOFF.md
```

## Review result

VAwatchdog already contains activated parallel work for preserving and separating VA-related observations, public evidence, unverified claims, technical hypotheses, financial estimates, and oversight questions.

Its current handoff identifies it as an accountability and reconstructability repository, not an individual veteran claims-assistance service.

StegVA remains the proposed consented veteran-facing nonprofit service for claim preparation, review, and authorized submission support.

The two efforts are complementary and must remain structurally separated.

## Duplication avoided

StegVA must reuse rather than recreate VAwatchdog methods for:

- source-tier separation;
- verified-versus-unverified labeling;
- source registry and verification matrix patterns;
- sanitized observation records;
- correction and supersession history;
- FOIA, oversight, audit, and legal-review question preparation;
- reconstructable public-source timelines.

VAwatchdog must not duplicate StegVA capabilities for:

- veteran onboarding and companion continuity;
- private claim and medical-record custody;
- consented claim narrative preparation;
- benefits-form workflow;
- regulated submission authorization;
- case-specific human and AI dual approval;
- veteran amendment, export, and retention controls.

## Durable boundary

The cross-repository rules are recorded in:

```text
StegVerse-Labs/VAwatchdog/docs/STEGVA_INTEGRATION_BOUNDARY.md
```

That file prohibits raw claim, medical, financial, identity, authentication, and protected-token transfers; requires independent evidence-tier review; and separates StegVA user-service entities from VAwatchdog evidence-review entities.

## Completed mutations

```text
VAwatchdog commit 74d93735ef5414cb3539464a4cb0685a94f07ee6
  Added docs/STEGVA_INTEGRATION_BOUNDARY.md

VAwatchdog commit b03aac11d6987172a473f615200853fbd8aa534f
  Updated docs/VAWATCHDOG_MIRROR_HANDOFF.md to version 1.1.1
  Recorded StegVA integration and non-overlap rules
```

## Next task

Bootstrap the dedicated StegVA repository without copying VAwatchdog evidence records or treating VAwatchdog as a claims database.

The StegVA bootstrap should reference the VAwatchdog integration boundary and implement only:

- program governance and nonprofit posture;
- synthetic-only veteran intake;
- privacy and consent architecture;
- split-identity threat model;
- claim preparation and review workflow;
- public-finance-ledger specification;
- regulated submission gates;
- cross-repository exchange receipt schema.

## Verification

```bash
# In VAwatchdog
test -f docs/STEGVA_INTEGRATION_BOUNDARY.md
grep -q "No raw claim packet" docs/STEGVA_INTEGRATION_BOUNDARY.md
grep -q "StegVA parallel-work boundary: complete" docs/VAWATCHDOG_MIRROR_HANDOFF.md

# In StegCore
test -f docs/STEGVA_MIRROR_HANDOFF.md
test -f docs/STEGVA_VAWATCHDOG_PARALLEL_WORK_RECEIPT.md
```

## Ownership and archive state

```text
VAwatchdog evidence work: owned by VAwatchdog handoff
StegVA program bootstrap: owned by StegVA nonprofit formation workstream
Constitutional boundaries: owned by StegCore
Active StegFin provider chain: unchanged and not claimed here
```

This review slice is complete and no longer requires conversational context.
