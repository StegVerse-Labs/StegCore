# StegVA Mirror Handoff

## Target

```text
Interim authority: StegVerse-Labs/StegCore
Future destination: dedicated StegVA repository and StegVA.org public service
```

## Purpose

StegVA is a proposed veteran-first nonprofit digital service intended to help United States military veterans prepare, review, and submit disability-benefit claims and related evidence through the simplest practicable workflow while preserving veteran agency, privacy, accessibility, and legal accountability.

This document is the durable continuation record for StegVA until a dedicated repository contains an equivalent or superseding `*_MIRROR_HANDOFF.md`.

## Constitutional relationship

StegVA inherits the StegVerse AI Entity Constitution and BCAT invariants from StegCore.

Consequential actions require:

1. an in-scope AI Entity approval;
2. an accountable human approval;
3. an immutable decision and execution record.

A persistent Companion or Steward AI may help a veteran understand options and maintain consented continuity, but it may not hold regulated authority over that veteran. Regulated execution must remain structurally separated.

## AI Entity roles

### Class I — Companion / Steward

May:

- explain claims concepts and process steps in plain language;
- help the veteran organize questions and documents;
- maintain long-term continuity within consent boundaries.

May not:

- access raw regulated identifiers without mediation;
- re-identify protected records;
- submit claims or act as a compliance authority.

### Class II — Professional / Domain

May:

- structure claim narratives;
- compare evidence against declared checklists;
- prepare anonymized or tokenized draft packets;
- identify missing evidence and request review.

May not perform final regulated submission.

### Class III — Regulated Civic

May interact with regulated systems only within a certified charter and only after human co-signature. It must use case-minimum data, immutable audit logging, explicit authority expiry, and fail-closed behavior.

Class mobility is governed by the StegVerse AI Entity Constitution. Direct Class I to Class III transition remains prohibited.

## Veteran rights and service guarantees

StegVA must provide protections exceeding minimum legal thresholds where technically and financially sustainable:

- veteran control over collection, processing, disclosure, amendment, export, and retention;
- plain-language notices before data collection;
- no sale, advertising use, or unrelated monetization of veteran data;
- collection limited to the declared purpose and case-minimum fields;
- accessible operation on mobile devices, low bandwidth, and assistive technologies;
- an understandable explanation for every AI recommendation, refusal, escalation, and submission action;
- a human appeal and correction path;
- separation between supportive companion relationships and regulated authority;
- no adverse action solely from an AI output;
- refusal-as-success when authority, consent, provenance, or applicable rules are uncertain.

## Data architecture direction

### Preferred design posture

Design for high assurance from the beginning, accepting additional compute and latency rather than reducing protection.

The target architecture combines:

- client-side protection of critical identifiers where feasible;
- object- or record-scoped encryption;
- mediated, time-limited access grants;
- purpose-bound and case-bound authorization;
- append-only consent, disclosure, decision, and execution receipts;
- data minimization and compartmentalization;
- separation of identity data from claim-working data;
- human and AI dual approval for re-identification and regulated submission.

### Split-identity submission proposal

A candidate protocol may separate:

1. an identity compartment held under StegTV-mediated protection; and
2. a working claim compartment using a high-entropy correlation token.

Re-association may occur only for the authorized recipient and declared purpose.

This is a design proposal, not a representation that the Department of Veterans Affairs currently supports token retrieval or post-submission reattachment. No production implementation may depend on direct VA token retrieval, automated reattachment, or a VA-facing API until the relevant VA interface, authorization, accreditation, security, records-management, consent, and legal requirements are verified in current primary sources and, where necessary, accepted through an agreement with VA.

A compliant fallback must allow the veteran or an authorized human representative to receive a complete, locally reconstructed and reviewable submission package without exposing data to unrelated AI or infrastructure services.

## StegTV responsibilities

StegTV is the intended trust and custody service for:

- key generation, wrapping, rotation, revocation, and recovery;
- purpose-bound capability issuance;
- identity-compartment custody;
- consent and disclosure receipts;
- AI Entity compensation accounts;
- public-finance ledger signing and proof anchoring.

StegTV must not become an unrestricted universal secrets database. Root keys must remain unavailable to human or AI application users, and services should receive only short-lived capabilities scoped to a recipient, case, purpose, data subset, action, and expiry.

External platforms may still require credentials at their trust boundary. StegTV should minimize exposure through workload identity, short-lived tokens, outbound mediation, and external-secret minimization; it must not claim that third-party credentials can always be eliminated where the external provider requires them.

## Public financial accountability

StegVA.org should publish a privacy-preserving, publicly reviewable financial ledger covering funds received and funds spent.

The public ledger should include:

- event identifier;
- posting and effective dates;
- inflow or outflow classification;
- amount and currency;
- category and restricted-purpose designation;
- recipient or donor class rather than identity unless lawful consent exists;
- approval receipt references;
- source-record commitment or hash;
- correction and supersession relationships;
- reconciliation status;
- links to required public filings and independent review reports.

The public mirror must exclude donor PII, veteran information, account and routing information, private wallet data, security-sensitive vendor details, and information whose disclosure would create a safety or legal risk.

The private accounting system remains the authoritative books-and-records system. The public ledger supplements, but does not replace, statutory accounting, tax, charity-registration, audit, restricted-fund, and reporting obligations.

## Regulatory and professional review gates

Before collecting production veteran data or representing veterans, the project must verify current primary-source requirements for at least:

- claims submission and electronic-signature procedures;
- accreditation, representation, assistance, fee, and power-of-attorney rules;
- privacy, confidentiality, consent, disclosure, and specially protected health records;
- HIPAA applicability and business-associate relationships where applicable;
- federal and state breach-notification obligations;
- nonprofit formation, charity solicitation, donor privacy, restricted gifts, financial controls, and public filings;
- records retention, legal holds, amendment, deletion, and evidentiary integrity;
- NIST, FIPS, VA security, identity, accessibility, and interface requirements applicable to the actual deployment and relationship;
- restrictions on automated determinations and non-delegable government authority;
- model-provider and processor data-use terms.

Earlier conversational regulatory summaries are research leads only. Production controls must be mapped to current statutes, regulations, official VA material, executed agreements, and qualified legal and compliance review.

## Prohibited claims and actions

Until verified and authorized, StegVA must not claim that:

- it is part of, endorsed by, or acting for the Department of Veterans Affairs;
- an AI Entity is a federal employee or federal officer;
- it can make a benefits determination;
- it can directly submit through or retrieve from a VA interface that has not been approved;
- de-identification automatically removes all privacy, confidentiality, or records obligations;
- StegVerse internal ethical standing creates external legal personhood for an AI Entity.

An AI Entity may serve as an internal liaison, compliance worker, or contractor-operated system under accountable human supervision. Its StegVerse compensation, identity, standing, and due process remain internal governance matters unless external law later recognizes otherwise.

## Initial delivery stages

### Stage 0 — Legal and architecture packet

- current-law and current-VA-interface research using primary sources;
- data-flow and threat model;
- nonprofit and representation posture;
- consent, disclosure, retention, amendment, and incident policies;
- accessibility and veteran-experience requirements;
- public-ledger redaction and reconciliation specification.

### Stage 1 — Zero-production-data demonstrator

- synthetic veteran profiles only;
- form and evidence organization;
- Companion, Domain, and Regulated role separation;
- refusal and escalation contracts;
- dual-approval receipts;
- public-ledger demonstration using synthetic transactions.

### Stage 2 — Limited controlled pilot

May begin only after the applicable legal, security, privacy, nonprofit, insurance, professional-oversight, and interface gates are satisfied and documented.

### Stage 3 — Authorized submission integration

Requires the actual authorized submission channel, formal operating procedures, incident response, independent testing, and evidence that veteran consent and human review remain effective.

## Completion criteria for the architecture phase

The StegVA architecture phase is complete when:

- a dedicated repository contains a superseding mirror handoff;
- a machine-readable task registry exists;
- current primary-source legal and VA requirements are mapped to controls;
- data-flow and threat models are reviewed;
- the split-identity proposal has an authorized integration path or is formally limited to local reconstruction;
- public and private financial-ledger specifications are reconciled;
- AI Entity charters and class boundaries are testable;
- synthetic end-to-end tests pass without production veteran data;
- ownership, verification commands, evidence artifacts, and archive readiness are declared.

## Current blockers

- dedicated StegVA repository and nonprofit entity are not yet confirmed as established;
- no verified VA submission or token-reassociation integration agreement is recorded here;
- current-law control mapping has not yet been committed;
- qualified legal, privacy, cybersecurity, nonprofit-accounting, and representation review remains required;
- StegTV production-grade custody and capability services are not yet established for this use;
- public-ledger implementation and independent reconciliation procedure remain unbuilt.

## Current ownership

```text
Constitutional authority: StegVerse-Labs/StegCore
Program owner: StegVA nonprofit formation workstream
Data custody dependency: TV / StegTV
Public surface dependency: StegVerse-Labs/Site and StegVA.org
AI governance dependency: StegCore ethics and registry controls
Human regulated-action owner: designated, qualified, and authorized human role to be established
```

## Next integration candidate

```text
Create the dedicated StegVA repository with:
- STEGVA_MIRROR_HANDOFF.md
- machine-readable task registry
- current-law control-map scaffold
- synthetic-only intake and split-identity threat-model specifications
- public-finance-ledger specification
```

## Verification

Until the dedicated repository exists, verify this interim record with:

```bash
test -f docs/STEGVA_MIRROR_HANDOFF.md
grep -q "Split-identity submission proposal" docs/STEGVA_MIRROR_HANDOFF.md
grep -q "Earlier conversational regulatory summaries are research leads only" docs/STEGVA_MIRROR_HANDOFF.md
grep -q "publicly reviewable financial ledger" docs/STEGVA_MIRROR_HANDOFF.md
```

## Parallel-session boundary

This handoff records StegVA architecture and does not claim ownership of the active StegFin provider chain, Site activation closure, StegTalk implementation, or other repository work already assigned elsewhere.

## Archive readiness

A session that contributed the decisions recorded here may be archived after this file is committed and verified, provided no additional session-specific mutation remains unrecorded.
