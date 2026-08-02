# StegVA Split-Identity Threat Model

## Status

```text
Goal: STEGVA-BOOTSTRAP-001
Owner repository: StegVerse-Labs/StegCore
Future destination: StegVerse-Labs/StegVA
Production authorization: DENIED
Model version: 1.0.0
```

## Security objective

Permit a veteran to prepare and review a claim package while separating direct identity attributes from claim-working data, without asserting that VA currently supports token retrieval, post-submission reattachment, or an external StegTV identity-resolution API.

The safe bootstrap outcome is a locally reconstructable package reviewed by the veteran or an authorized human representative. Any direct VA-facing integration remains blocked until an official channel and authority are verified.

## Protected assets

- veteran identity attributes, including SSN and VA file number;
- medical, service, financial, contact, and dependent information;
- claim narrative, evidence, form selections, and draft outputs;
- authentication credentials and session artifacts;
- identity-to-case correlation values;
- consent, disclosure, approval, amendment, and submission receipts;
- encryption, wrapping, recovery, rotation, and revocation material;
- public-ledger source records and private accounting data.

## Trust zones

1. **Veteran-controlled client** — prepares or reviews local material and displays consent and approval prompts.
2. **Identity compartment** — stores direct identifiers separately under StegTV-mediated custody or an equivalent approved custody service.
3. **Claim-working compartment** — stores the minimum claim-specific content under a case-scoped pseudonymous identifier.
4. **Approval boundary** — requires an in-scope AI Entity decision and accountable human co-signature for re-identification, disclosure, or submission.
5. **Authorized submission boundary** — an official VA claimant or accredited-representative channel, not assumed to exist as a programmable API.
6. **VAwatchdog boundary** — accepts only permitted sanitized or public material under `StegVerse-Labs/VAwatchdog/docs/STEGVA_INTEGRATION_BOUNDARY.md`.
7. **Public accountability boundary** — publishes redacted finance and governance evidence without veteran or donor PII.

## Required identifiers

A working claim must use independently generated, high-entropy values for:

- `case_id` — internal case identifier with no embedded identity meaning;
- `correlation_token` — single-purpose, case-bound association value;
- `consent_receipt_id` — points to the active consent state;
- `authority_receipt_id` — points to verified human and AI authority;
- `package_commitment` — SHA-256 or stronger approved commitment to the exact review package.

No identifier may contain initials, birth date, service number, SSN fragments, VA file number fragments, diagnosis codes, or other predictable personal material.

## Threat actors

- unauthenticated external attacker;
- compromised client or browser extension;
- malicious or over-privileged operator;
- compromised AI or model-provider path;
- compromised application service;
- insider with access to only one compartment;
- unauthorized accredited-representative account;
- public-ledger observer attempting linkage;
- VAwatchdog reviewer attempting accidental or intentional re-identification;
- third-party provider compelled or induced to disclose data;
- automation replaying or duplicating an earlier authorized action.

## Threats and mandatory controls

### T1 — Correlation by shared metadata

**Risk:** timestamps, filenames, sizes, network data, or stable identifiers reconnect identity and claim compartments.

**Controls:**

- remove identity-bearing filenames and metadata;
- normalize or bucket nonessential timestamps and sizes where operationally safe;
- prohibit stable cross-case identifiers;
- use recipient-, purpose-, and case-scoped tokens;
- test re-identification risk before any cross-boundary disclosure.

### T2 — Token guessing, reuse, or substitution

**Risk:** predictable or reused tokens allow case discovery or package substitution.

**Controls:**

- cryptographically random tokens with at least 128 bits of entropy;
- one case, one purpose, one destination, and one validity window per token;
- server-side hash or keyed commitment rather than plaintext lookup where possible;
- revocation and replay detection;
- exact package commitment included in approval receipts.

### T3 — Unauthorized re-identification

**Risk:** one actor or service joins identity and working data without valid authority.

**Controls:**

- deny unilateral re-identification;
- require current consent, in-scope AI approval, accountable human approval, purpose, destination, expiry, and immutable receipt;
- isolate companion memory from regulated execution state;
- deny when authority, consent, provenance, or policy is missing or stale.

### T4 — Companion/regulated-role conflict

**Risk:** a persistent companion relationship gains regulated authority over the same veteran.

**Controls:**

- distinct AI identity, charter, memory boundary, credentials, and audit namespace;
- direct Class I to Class III transition prohibited;
- no companion access to raw identifiers or submission credentials;
- independent regulated review before consequential action.

### T5 — Unsupported VA integration assumption

**Risk:** implementation depends on VA retrieving a StegTV token or reattaching identity after submission.

**Controls:**

- treat this path as blocked until documented official capability and agreement exist;
- require local reconstruction into an ordinary human-reviewable package;
- require veteran or authorized representative review and official-channel submission;
- fail closed if the submission-channel registry lacks a current approved entry.

### T6 — Credential or session compromise

**Risk:** attacker uses claimant or representative credentials to submit or access records.

**Controls:**

- never store raw passwords or long-lived session tokens in the application data plane;
- prefer provider-supported workload identity and short-lived credentials;
- bind submissions to current authority, package commitment, and explicit user review;
- detect anomalous sessions and require reauthentication for consequential actions;
- retain no authentication artifact in VAwatchdog or public receipts.

### T7 — Public-ledger linkage

**Risk:** timing, amount, counterparty, or reference data reveals veteran or donor identity.

**Controls:**

- publish counterparty class rather than identity;
- prohibit case IDs and exact private-record references in public events;
- permit delayed or aggregated publication where necessary;
- conduct re-identification review before publication;
- maintain a separate authoritative private accounting ledger.

### T8 — Cross-repository leakage

**Risk:** claim material enters VAwatchdog, Site, Publisher, a wiki, or another public surface.

**Controls:**

- use the cross-repository exchange receipt schema;
- allow only public, separately consented sanitized, aggregated, or cryptographic-commitment artifacts;
- preserve the source confidence tier;
- prohibit raw claim, identity, medical, financial, credential, and protected-token transfer;
- destination import validator must fail closed.

### T9 — Duplicate or replayed execution

**Risk:** a valid approval is reused for another package, destination, or time.

**Controls:**

- duplicate-execution key scoped to action, package commitment, destination, authority, and expiry;
- atomic consume-once execution receipt;
- idempotent retries return the prior receipt rather than repeat the action;
- supersession and revocation pointers are mandatory.

### T10 — Key loss or misuse

**Risk:** data becomes unrecoverable or root keys expose all cases.

**Controls:**

- envelope encryption and compartment-specific data keys;
- no root-key access by application users or AI Entities;
- governed rotation, recovery, revocation, and destruction procedures;
- recovery requires separate authority and produces an immutable receipt;
- test restoration without production veteran data before pilot authorization.

## Data-flow states

```text
SYNTHETIC_INTAKE
  -> PREPARED
  -> VETERAN_REVIEW
  -> HUMAN_AND_AI_APPROVED
  -> LOCALLY_RECONSTRUCTED
  -> AUTHORIZED_CHANNEL_READY
  -> SUBMITTED
```

During bootstrap, transition beyond `LOCALLY_RECONSTRUCTED` is prohibited. `AUTHORIZED_CHANNEL_READY` and `SUBMITTED` require current official-channel evidence and production authorization.

## Fail-closed conditions

The system must return `BLOCKED` or `REVIEW_REQUIRED`, never success, when:

- production data is detected during bootstrap;
- consent, authority, purpose, destination, expiry, or package commitment is missing;
- the identity and claim compartments share prohibited identifiers;
- re-identification risk exceeds the approved threshold;
- official submission-channel authority is absent, stale, or unverifiable;
- a requested exchange conflicts with the VAwatchdog boundary;
- a duplicate execution key has already been consumed;
- cryptographic custody or audit continuity cannot be verified.

## Required verification cases

- synthetic happy path through local reconstruction;
- production-data marker rejected;
- reused correlation token rejected;
- mismatched package commitment rejected;
- expired consent rejected;
- missing human or AI approval rejected;
- Companion AI submission request rejected;
- VAwatchdog raw-payload transfer rejected;
- duplicate execution returns prior receipt without re-execution;
- unavailable custody service produces `BLOCKED`, not implicit success.

## Residual boundaries

This threat model does not prove legal compliance, FIPS validation, VA accreditation, VA interface authorization, nonprofit readiness, deployment security, or runtime accessibility. Those require separate evidence and remain blocked in the task registry.
