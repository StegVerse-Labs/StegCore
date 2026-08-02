# StegVA Public Finance Ledger Specification

## Status

```text
Goal: STEGVA-BOOTSTRAP-001
Specification version: 1.0.0
Owner repository: StegVerse-Labs/StegCore
Future destination: StegVerse-Labs/StegVA
Production publication: NOT AUTHORIZED
```

## Purpose

Define a privacy-preserving public mirror of StegVA financial activity that allows donors, veterans, auditors, and the public to verify inflows, outflows, restrictions, approvals, corrections, and reconciliation without exposing veteran, donor, employee, banking, wallet, credential, or security-sensitive information.

The public ledger supplements but never replaces the private books-and-records system, statutory filings, tax records, charity-registration records, restricted-fund accounting, audits, or financial statements.

## Canonical records

### Private authoritative ledger

The private accounting system is authoritative for:

- complete counterparties;
- account and routing details;
- payroll and contractor records;
- donor restrictions and legal instruments;
- invoices, receipts, contracts, and bank statements;
- case-level assistance records when lawfully required;
- reconciliation workpapers;
- tax, audit, and charity-compliance records.

### Public mirror

The public mirror contains only fields permitted by `stegva/contracts/public_finance_event.schema.json` and approved publication policy. It may contain cryptographic commitments to private source records but never the protected records themselves.

## Event model

Each public event represents one posted financial occurrence and must include:

- immutable `event_id`;
- `posting_date` and, where different, `effective_date`;
- `direction`: `INFLOW` or `OUTFLOW`;
- amount and ISO currency;
- category;
- counterparty class, not identity;
- restricted-purpose designation where applicable;
- at least two approval receipt references;
- cryptographic commitment to the private source record;
- reconciliation state;
- correction and supersession relationships.

No event may be edited in place after publication. Corrections use a new event that references the superseded event and explains the correction category without disclosing protected details.

## Allowed public counterparty classes

Examples include:

- `INDIVIDUAL_DONOR`;
- `INSTITUTIONAL_DONOR`;
- `FOUNDATION`;
- `GOVERNMENT_GRANTOR`;
- `PROGRAM_VENDOR`;
- `SECURITY_VENDOR`;
- `CLOUD_PROVIDER`;
- `PROFESSIONAL_SERVICES`;
- `EMPLOYEE_COMPENSATION_AGGREGATE`;
- `VETERAN_ASSISTANCE_AGGREGATE`;
- `OTHER_REVIEWED_CLASS`.

Named counterparties may be published only when required by law, already public in authoritative filings, or supported by explicit lawful consent and privacy review.

## Prohibited public fields

The public ledger must never contain:

- veteran names, case IDs, claim IDs, diagnoses, service records, medical data, or benefit details;
- donor names without lawful consent or disclosure requirement;
- employee-level compensation details unless legally required and reviewed;
- account numbers, routing numbers, card details, private wallet addresses, recovery data, or authentication material;
- invoice line items that identify a veteran or reveal a protected service;
- private contract terms whose publication creates a security or legal risk;
- source document URLs containing access tokens;
- StegTV identity or correlation tokens;
- VAwatchdog source IDs that can reconnect a person to a claim.

## Approval rules

Every public event requires:

1. accounting approval confirming the private event exists and is posted;
2. privacy/publication approval confirming the public projection is safe;
3. machine validation against the public-finance event schema;
4. source-record commitment verification;
5. duplicate-event and supersession checks.

Human and AI approvals must be separate receipt references. The AI approval is advisory and bounded; accountable human authority remains responsible for publication.

## Restricted funds

Restricted gifts and grants require:

- a restriction identifier that contains no donor identity;
- purpose class;
- opening restricted balance;
- inflows, releases, and eligible outflows;
- closing restricted balance;
- reconciliation to the private ledger;
- correction events for any classification error.

A restricted-purpose event may not be silently reclassified. Reclassification requires a new approval set and a superseding public event.

## Reconciliation states

- `UNRECONCILED` — posted public projection awaiting private-ledger reconciliation;
- `RECONCILED` — matched to the private authoritative record and period totals;
- `EXCEPTION` — mismatch, missing evidence, disputed classification, or review failure;
- `SUPERSEDED` — replaced by a later correction event.

Publication may include `UNRECONCILED` events only when clearly labeled and within a defined short reconciliation window. `EXCEPTION` events remain visible and must not be deleted.

## Publication cadence

Bootstrap:

- synthetic events only;
- publication to repository artifacts only;
- no donor, veteran, bank, payroll, or vendor production data.

Future authorized operation:

- event projection after private posting;
- daily or weekly public update according to approved policy;
- monthly reconciliation receipt;
- annual linkage to audited or independently reviewed financial statements and required filings.

## Privacy and re-identification review

Before publication, the projector must evaluate:

- whether amount plus date can identify a donor or veteran;
- whether a rare category or vendor class reveals protected activity;
- whether repeated events can be linked to a person;
- whether timing aligns with public claim or oversight records;
- whether exact values should be delayed or aggregated;
- whether the source commitment is unlinkable without authorized access.

When risk exceeds the approved threshold, the event must return `REVIEW_REQUIRED` or be aggregated, delayed, or withheld under a documented authority basis.

## Correction protocol

1. Detect discrepancy or receive correction request.
2. Set the original event reconciliation state to `EXCEPTION` through a new status event or append-only state record.
3. Create a correction event referencing the original.
4. Obtain new accounting, privacy, human, and AI approvals.
5. Publish the correction and supersession link.
6. Reconcile period totals.
7. Preserve both original and corrected events.

## Deterministic publication pipeline

```text
PRIVATE_POSTED_EVENT
  -> PUBLIC_PROJECTION
  -> SCHEMA_VALIDATION
  -> PRIVACY_REVIEW
  -> HUMAN_AND_AI_APPROVAL
  -> SOURCE_COMMITMENT_CHECK
  -> DUPLICATE_CHECK
  -> PUBLIC_EVENT
  -> RECONCILIATION_RECEIPT
```

Possible machine states:

- `COMPLETE` — event valid, approved, published, and receipt persisted;
- `BLOCKED` — authority, source record, or required service unavailable;
- `RETRY` — transient publication or storage failure with idempotency key retained;
- `REVIEW_REQUIRED` — privacy, classification, restriction, or reconciliation ambiguity;
- `FAILED` — invalid contract, commitment mismatch, duplicate conflict, or prohibited field detected.

## Duplicate prevention

The duplicate-execution key must bind:

- private source record identifier;
- public projection hash;
- amount and currency;
- posting date;
- direction;
- correction or supersession target;
- publication version.

Retries must return the prior publication receipt rather than emit a second event.

## Required receipts

### Publication receipt

Contains:

- event ID;
- schema version;
- public projection hash;
- private source commitment;
- approval receipt IDs;
- publication timestamp;
- repository, object store, or public endpoint location;
- duplicate-execution key;
- status and next action.

### Reconciliation receipt

Contains:

- period;
- opening and closing balances by class;
- public-event count and total by direction;
- private-ledger totals;
- variance;
- exceptions;
- reviewer identity class;
- evidence commitments;
- status.

Receipts must not contain protected payloads.

## Validation requirements

The bootstrap validator must verify:

- schema presence and strictness;
- specification presence;
- production publication remains disabled;
- required approval and reconciliation semantics are declared;
- no sample contains production data.

Before production authorization, independent accounting, nonprofit-compliance, privacy, security, and publication reviews are required, followed by synthetic end-to-end and controlled-pilot evidence.

## Cross-repository propagation

No Site, Publisher, wiki, or public runtime propagation is authorized by this specification alone.

Future destinations must consume a signed or commit-pinned public manifest and validate:

- source repository and commit;
- schema and specification versions;
- event commitments;
- redaction posture;
- reconciliation state;
- publication authority.

The Site may display validated public events but must not become the accounting source of truth. VAwatchdog may reference public finance events as public records but may not infer wrongdoing from an unreconciled or corrected event.
