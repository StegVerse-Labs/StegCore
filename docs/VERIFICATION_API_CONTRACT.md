# Verification API Contract

## Purpose

This file defines the first contract for connecting intake records to the StegVerse verification planning workflow.

## Definition Of Done

The contract is complete when a request can be assigned a stable job identifier, tracked through status states, and returned with a report reference.

## Request Fields

Required fields:

```text
submitter_name
submitter_contact
request_name
verification_goal
work_reference
evidence_reference
precision_tier
urgency
handling_class
authorization_confirmed
```

Optional fields:

```text
organization
expected_result
reproducibility_notes
billing_track
```

## Status Values

```text
received
needs_clarification
accepted_for_planning
held_for_review
planned
complete
complete_with_limits
failed
```

## Result Fields

```text
job_id
status
result_summary
receipt_status
receipt_hash_or_reason
stability_classification
precision_tier
boundary_limits
report_reference
```

## Receipt Rule

```text
Every completed verification must include either a receipt hash or a clear reason that no receipt hash was generated.
```

## Boundary Rule

```text
No report may claim full reproducibility unless the declared references, assumptions, and boundary limits are recorded.
```
