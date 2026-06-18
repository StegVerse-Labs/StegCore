# StegVerse Precision Compute API Contract

## Purpose

This contract defines the minimum API bridge for moving StegVerse Precision Compute from manual customer intake to repeatable governed verification workflows.

The API does not replace governed ingestion. It prepares customer submissions for governed ingestion.

## Flow

```text
submit -> intake schema validation -> bundle generation -> governed ingestion -> execution -> verification -> receipt -> report -> delivery
```

## Required Invariant

Every accepted job must eventually produce one of the following:

```text
1. A verification report with receipt hash.
2. A blocked report with a clear reason no receipt could be generated.
```

No job should silently disappear.

## Endpoint 1 — Submit Experiment

```text
POST /submit
```

### Request Body

The request body must conform to:

```text
docs/STEGVERSE_PRECISION_COMPUTE_INTAKE_SCHEMA.json
```

### Minimal Example

```json
{
  "submission_id": "spc-0001-example-eval",
  "submitted_utc": "2026-06-18T00:00:00Z",
  "customer_ref": {
    "customer_id": "lead-0001",
    "contact_channel": "X",
    "segment": "ai_eval_builder"
  },
  "experiment": {
    "title": "Example Model Eval",
    "summary": "Verify whether the evaluation result reproduces under declared conditions.",
    "script_ref": "customer-provided-script.py",
    "data_ref": "customer-provided-dataset"
  },
  "precision": {
    "tier": "starter",
    "target": "1e-2",
    "priority": "standard"
  },
  "execution_boundary": {
    "environment": "python:3.11",
    "dependencies": ["requirements.txt"],
    "allowed_network": false,
    "allowed_external_state": false,
    "notes": "No network during verification."
  },
  "success_condition": {
    "type": "threshold",
    "description": "Metric result remains within declared tolerance.",
    "threshold": "1e-2"
  },
  "receipt_required": true,
  "delivery": {
    "report_format": "both"
  }
}
```

### Response

```json
{
  "job_id": "job-spc-0001-example-eval",
  "submission_id": "spc-0001-example-eval",
  "status": "accepted",
  "next": "validate_intake"
}
```

## Endpoint 2 — Check Status

```text
GET /status/{job_id}
```

### Status Values

```text
accepted
intake_validated
bundle_generated
ingestion_queued
ingestion_blocked
running
verification_failed
verified
report_ready
delivered
```

### Response

```json
{
  "job_id": "job-spc-0001-example-eval",
  "submission_id": "spc-0001-example-eval",
  "status": "running",
  "updated_utc": "2026-06-18T00:00:00Z"
}
```

## Endpoint 3 — Fetch Result

```text
GET /result/{job_id}
```

### Verified Response

```json
{
  "job_id": "job-spc-0001-example-eval",
  "submission_id": "spc-0001-example-eval",
  "status": "verified",
  "receipt_hash": "sha256:...",
  "report_ref": "reports/job-spc-0001-example-eval.md",
  "reproduction_ref": "reports/job-spc-0001-example-eval.reproduce.md"
}
```

### Blocked Response

```json
{
  "job_id": "job-spc-0001-example-eval",
  "submission_id": "spc-0001-example-eval",
  "status": "ingestion_blocked",
  "receipt_hash": null,
  "blocked_reason": "Input did not declare required execution boundary.",
  "report_ref": "reports/job-spc-0001-example-eval.blocked.md"
}
```

## Bundle Generation Requirements

The API bridge must generate a bundle containing:

```text
1. submission.json
2. execution_boundary.json
3. declared_inputs.json
4. success_condition.json
5. customer_manifest.json
6. pending_report.md
```

## Governance Boundary

The API may accept a submission, but only governed ingestion may determine whether the job is admissible for execution.

The API must not claim:

```text
1. Verification before execution completes.
2. Scientific truth of the submitted hypothesis.
3. Adoption, endorsement, or production readiness.
4. Customer payment or repeat-use signal unless recorded in the customer pipeline tracker.
```

## Activation Checklist

This API contract is ready for implementation when:

```text
1. Intake schema exists.
2. Report template exists.
3. Bundle fields are defined.
4. Status values are defined.
5. Blocked and verified result paths are defined.
```

Implementation activation requires:

```text
1. Running endpoint or equivalent GitHub issue/form bridge.
2. Schema validation.
3. Bundle generation.
4. Ingestion handoff.
5. Report generation.
6. Receipt generation.
7. Delivery path.
```

## Archive Readiness

This contract contains the minimum API surface, request schema, response formats, status values, bundle requirements, governance boundary, and activation checklist needed to continue without prior chat context.

StegVerse-Labs - 43% complete
StegCore - 41% complete
StegCore - 42% complete TO GOAL ACTIVATION;
Fully developed files vs scaffolding/stubs - 49% complete
Δ [StegCore: 41%vs43%] - API bridge contract is defined and ready for implementation; activation still needs endpoint/form implementation, customer runs, paid conversion, and repeat-use proof.
