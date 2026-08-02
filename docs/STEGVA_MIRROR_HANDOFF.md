# StegVA Mirror Handoff

## Active goal

```text
Goal ID: STEGVA-BOOTSTRAP-001
Goal: Establish a synthetic-only, fail-closed StegVA architecture and verification lane without collecting production veteran data.
```

## Repository and branch

```text
Interim authority: StegVerse-Labs/StegCore
Branch: main
Future destination: StegVerse-Labs/StegVA
Public service target: StegVA.org
```

This is the authoritative StegVA continuation record until a dedicated StegVA repository contains a verified superseding handoff and StegCore records the transfer receipt.

## Constitutional relationship

StegVA inherits the StegVerse AI Entity Constitution and BCAT invariants from StegCore.

Consequential actions require:

1. an in-scope AI Entity approval;
2. an accountable human approval;
3. an immutable decision and execution record.

A Companion or Steward AI may support a veteran but may not hold regulated authority over that veteran. Regulated execution must use a separate identity, charter, memory boundary, credential scope, and audit namespace.

## Authoritative files

```text
docs/STEGVA_MIRROR_HANDOFF.md
docs/STEGVA_VAWATCHDOG_PARALLEL_WORK_RECEIPT.md
stegva/task_registry.json
stegva/receipts/implementation-2026-08-02.md
stegva/contracts/synthetic_intake.schema.json
stegva/contracts/cross_repo_exchange_receipt.schema.json
stegva/contracts/public_finance_event.schema.json
stegva/compliance/current_law_control_map.json
stegva/docs/SPLIT_IDENTITY_THREAT_MODEL.md
stegva/docs/PUBLIC_FINANCE_LEDGER_SPEC.md
stegva/examples/synthetic_intake.valid.json
stegva/examples/synthetic_intake.invalid-production.json
stegva/automation/validate_bootstrap.py
.github/workflows/stegva-bootstrap-verify.yml
StegVerse-Labs/StegCore issue #44
StegVerse-Labs/VAwatchdog/docs/STEGVA_INTEGRATION_BOUNDARY.md
```

## Completed work

### Continuity and parallel ownership

- Interim StegVA architecture handoff committed at `fd4b31ad0585399c6e276059082c0d7d7761f633`.
- VAwatchdog integration boundary committed in VAwatchdog at `74d93735ef5414cb3539464a4cb0685a94f07ee6`.
- VAwatchdog handoff updated at `b03aac11d6987172a473f615200853fbd8aa534f`.
- StegCore parallel-work receipt committed at `9b5ae5fdf0ddd1f7be7535ff443d500ea83edc49`.
- Ecosystem registry integration committed at `6ba6d402e68938613d503cecaf19412708449aa5`.

### Contracts

- Synthetic-only intake schema committed at `9083372cbdf92b91f4ce897a6ff28dc9a9679532`.
- Cross-repository exchange receipt schema committed at `fd009f0a727d5b9f050945d4ff43e0cf48e4eb04`.
- Public finance event schema committed at `9d1259dd62db880f3a7256f023b0c3f633368b53`.

### Architecture and policy specifications

- Official-source control map committed at `4f8355efd66b13ecd2f82f7ac4184950c11f37db`.
- Split-identity threat model committed at `9716c26f70974e946e846f2475eaf918025baa53`.
- Public finance ledger operating specification committed at `cb1c2fd9f15d79ca81633dfc608e96925f08405c`.

### Verification implementation

- Valid synthetic fixture committed at `8e133c1bf219be19f722cfbc694474c4aee02b87`.
- Production-data rejection fixture committed at `09cb62d6d141fc083c2d6a44bc38ca318f1e9d2a`.
- Fail-closed validator installed and expanded at `3fff50c107aa2f8c13e0ca3bea0f3f5a4907874d`.
- Hosted verification workflow installed at `b4a87470979cc283eeda690950187118702c59df`.
- Machine task registry updated at `45772094e9cc949b19a454c2fb2ff4dc1cb0527f`.
- Implementation receipt committed at `bf6b7c1e5491daba12d0d108e387e7923fa44d49`.
- Dedicated-repository transfer is durably assigned in StegCore issue `#44`.

## Actual capability classification

| Component | State | Evidence boundary |
|---|---|---|
| Interim handoff | complete and committed | current file and commit history |
| VAwatchdog non-overlap boundary | complete and committed | VAwatchdog boundary and parallel-work receipt |
| Synthetic intake contract | implemented but hosted validation pending | schema committed; validator and fixtures installed |
| Cross-repository exchange contract | implemented but hosted validation pending | schema committed; no destination integration yet |
| Public finance event contract | implemented but hosted validation pending | schema committed; no publication runtime |
| Current-law control map | implemented, REVIEW_REQUIRED | official sources recorded; qualified review absent |
| Split-identity threat model | complete for bootstrap scope | production integration remains blocked |
| Public finance ledger specification | complete for bootstrap scope | accounting runtime and Site publication absent |
| Validator | implemented but hosted execution unverified | no inspected successful workflow evidence yet |
| Workflow | installed but run/artifact unverified | no inspected jobs, logs, or artifact yet |
| Dedicated StegVA repository | blocked/missing | repository not available through connected authority |
| Production service | prohibited | no legal, security, nonprofit, interface, or deployment authorization |
| Site/Publisher/wiki propagation | not authorized and not performed | requires later validated public manifest |

## Veteran protections

StegVA must preserve:

- veteran control over collection, processing, disclosure, amendment, export, and retention;
- plain-language notice and accessible mobile/low-bandwidth operation;
- no sale, advertising use, or unrelated monetization of veteran data;
- case-minimum collection;
- understandable explanations for AI recommendations, refusals, escalations, and actions;
- human appeal and correction;
- no adverse action solely from AI output;
- refusal-as-success when consent, authority, provenance, policy, or custody evidence is unavailable.

## Split-identity boundary

The candidate architecture separates direct identity data from claim-working data using a high-entropy, case-, purpose-, recipient-, and expiry-bound token.

This does **not** represent that VA supports StegTV token retrieval, post-submission identity reattachment, or a direct StegVA API. Bootstrap operation stops at a locally reconstructed, human-reviewable package. Any VA-facing execution remains blocked until an officially supported channel and current authority are proven.

## VAwatchdog boundary

VAwatchdog owns:

- source-tier separation;
- verified/unverified labeling;
- sanitized observation and evidence records;
- FOIA, oversight, audit, and legal-review preparation;
- reconstructable public-source timelines.

StegVA owns:

- consented veteran assistance;
- private claim preparation;
- Companion, Domain, and Regulated AI role separation;
- private consent, disclosure, decision, and submission receipts;
- any later authorized claim-submission workflow.

No raw claim packet, medical record, financial record, identity record, credential, protected token, or case identifier may cross into VAwatchdog.

## Machine-owned tasks

The current task source is `stegva/task_registry.json`.

### Active executable task

```text
Task: STEGVA-TASK-006
Location: .github/workflows/stegva-bootstrap-verify.yml
Owner: StegVerse-Labs/StegCore
State: RETRY
Release condition: GitHub Actions concludes successfully and the job, logs, and bootstrap-verification artifact are directly inspected.
```

### Blocked transfer task

```text
Task: STEGVA-TASK-007
Location: StegVerse-Labs/StegVA and StegCore issue #44
Owner: StegVA nonprofit formation workstream
State: BLOCKED
Release condition: the dedicated repository exists and connected mutation authority is available.
```

### Human review task

```text
Task: STEGVA-TASK-008
Location: stegva/compliance/current_law_control_map.json
Owner: StegVA legal-compliance workstream
State: REVIEW_REQUIRED
Release condition: qualified reviewers verify representation, privacy, nonprofit, security, accessibility, accounting, and official-channel controls and commit review evidence.
```

## Cross-repository dependencies

```text
StegVerse-Labs/VAwatchdog
  Source-tier and accountability boundary only.

TV / StegTV
  Future key custody, capability issuance, consent/disclosure receipts, and proof anchoring.

StegVerse-Labs/Site and StegVA.org
  Future public service and privacy-preserving finance display; not yet authorized.

GCAT-BCAT-Engine/Publisher
admissibility-wiki
stegguardian-wiki
master-records
  No propagation performed. Future propagation requires commit-pinned manifests, import validation, publication authority, and receipts.
```

## Validation commands

```bash
python3 stegva/automation/validate_bootstrap.py

test -f stegva/receipts/bootstrap-verification.json
python3 -m json.tool stegva/receipts/bootstrap-verification.json

grep -q '"status": "COMPLETE"' stegva/receipts/bootstrap-verification.json
grep -q '"production_data_processed": false' stegva/receipts/bootstrap-verification.json
grep -q '"production_authorization": false' stegva/receipts/bootstrap-verification.json
```

Hosted validation also requires inspection of:

```text
workflow run
job and step conclusions
job logs
stegva-bootstrap-verification-<run-id> artifact
bootstrap-verification.json inside the artifact
```

## Incomplete work

1. Inspect a successful hosted workflow run, job steps, logs, and artifact for `.github/workflows/stegva-bootstrap-verify.yml`.
2. Transfer the verified bootstrap into `StegVerse-Labs/StegVA` under StegCore issue `#44` when repository authority becomes available.
3. Commit qualified-review evidence for `stegva/compliance/current_law_control_map.json`.
4. Implement production-grade representation, signature-authority, submission-channel, data-subject-rights, accessibility, cryptographic-boundary, incident-response, retention, and accounting controls in the future dedicated repository.
5. Build synthetic end-to-end claim preparation and local reconstruction; do not use production veteran data.
6. Build a synthetic public-ledger projector, reconciliation receipt, and publication manifest before any Site work.
7. Create source and consumer contracts before any Site, Publisher, wiki, or master-records propagation.

## Blockers and release conditions

| Blocker | Owner | Machine-observable release condition |
|---|---|---|
| Hosted validation not inspected | StegCore workflow | successful run plus inspectable job/log/artifact evidence |
| Dedicated repository unavailable | StegVA nonprofit formation workstream | `StegVerse-Labs/StegVA` exists and connected mutation authority is confirmed |
| Qualified control review absent | named human review workstreams | signed or committed review evidence references every control-map topic |
| VA submission authority absent | regulated human authority boundary | current official channel, accreditation/authorization, identity, operating procedure, and test evidence are committed |
| StegTV production custody absent | TV / StegTV | production-grade custody contract, implementation, tests, and receipts are verified |
| Public ledger runtime absent | StegVA accounting workstream | synthetic projector and reconciliation path pass, then qualified accounting/privacy review occurs |

## Completion criteria

The bootstrap goal is complete only when:

- the validator succeeds in a directly inspected hosted workflow;
- job logs and receipt artifact are inspected;
- all required bootstrap files are present and non-stub;
- machine task state matches the observed evidence;
- the dedicated StegVA repository contains a verified superseding handoff and implementation;
- StegCore contains a transfer receipt;
- no production veteran data has been processed;
- remaining production boundaries are durably assigned with machine-observable release conditions.

## Percentages and denominator

Required bootstrap deliverables: 14.

Developed and committed: 13.

Missing required destination repository: 1.

Hosted validation deliverables required: 4.

Hosted validation directly verified: 0.

Cross-repository integration deliverables required for bootstrap closure: 2 — dedicated repository transfer and StegCore transfer receipt.

Cross-repository integration completed: 0.

```text
Task completion: 9/12 = 75%
Developed-file completion: 13/14 = 93%
Validation completion: 0/4 = 0%
Integration completion: 0/2 = 0%
Goal activation: 55%
```

## Archive conditions

Do not archive while this session still owns an unverified workflow observation or any unique implementation state absent from this handoff and its receipts.

The session becomes archivable when all session-specific mutations are represented here, workflow observation is durably recorded or assigned to an active machine observer, and no continuation action requires the conversation.
