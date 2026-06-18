# Verification Intake Fields

## Purpose

This file defines the customer-facing fields needed before StegVerse can evaluate a verification request.

## Definition Of Done

A request is ready for planning when all required fields below are present and the request has a clear verification goal.

## Required Fields

| Field | Description |
| --- | --- |
| submitter_name | Person submitting the request. |
| submitter_contact | Contact route for follow-up. |
| experiment_name | Short name for the requested verification. |
| experiment_goal | What result should be verified. |
| job_reference | Repository path, notebook reference, command description, or artifact reference. |
| data_reference | Dataset reference, fixture reference, sample hash, or declared no-data condition. |
| precision_tier | exploratory, analytical, or critical. |
| urgency | async, priority, or immediate. |
| handling_class | public, private, restricted, or unknown. |
| submitter_authorization | Confirmation that the submitter may provide the referenced materials for review. |

## Optional Fields

| Field | Description |
| --- | --- |
| organization | Team, company, lab, or independent user. |
| expected_output | What the submitter expects to happen. |
| reproducibility_notes | Seeds, version pins, environment constraints, hardware constraints, or assumptions. |
| billing_track | free_validation, starter, pro, critical, or subscription. |

## Planning Status Values

```text
received
needs_clarification
accepted_for_planning
held_for_handling_review
verification_planned
complete
complete_with_boundary_limits
failed
```

## Completion Rule

Every completed verification must include either a receipt hash or a clear reason that a receipt could not be generated.
