# StegVerse Customer Pipeline Tracker

## Purpose

This tracker converts StegVerse Precision Compute outreach into measurable customer-validation evidence.

It is designed for the $0 to $10K validation phase and should be updated after every outbound message, customer conversation, submitted experiment, delivered verification report, payment, and repeat-use signal.

## Pipeline Status Flow

```text
Lead Identified
DM Sent
Replied
Pain Confirmed
Experiment Secured
Input Received
Run Queued
Run Verified
Report Delivered
Price Discussed
Paid
Repeat Use Requested
Lost
```

## Minimum Tracker Columns

| Column | Required | Description |
|---|---:|---|
| Lead ID | Yes | Stable internal identifier, for example `lead-0001`. |
| Name / Handle | Yes | Public name, handle, or company contact. |
| Source | Yes | X, Reddit, Hugging Face, LinkedIn, referral, inbound, or other. |
| Segment | Yes | AI eval builder, researcher, quant, governance team, other. |
| Status | Yes | Current status from the status flow. |
| Pain Statement | Yes | The result they do not trust or cannot reproduce. |
| Experiment Summary | Yes after secured | Plain-language description of the submitted run. |
| Precision Tier | Yes after secured | Starter, Pro, Critical, or custom. |
| Price Discussed | Optional until close | Quoted or proposed price. |
| Payment Status | Yes after pricing | None, requested, paid, declined, deferred. |
| Receipt Hash | Yes after delivery | Receipt hash from completed verification report. |
| Repeat Signal | Yes after delivery | None, weak, strong, requested, paid-repeat. |
| Next Action | Yes | The next concrete action. |
| Last Updated | Yes | ISO date. |
| Notes | Optional | Context, objections, decision criteria. |

## CSV Header

```csv
lead_id,name_or_handle,source,segment,status,pain_statement,experiment_summary,precision_tier,price_discussed,payment_status,receipt_hash,repeat_signal,next_action,last_updated,notes
```

## Example Row

```csv
lead-0001,@examplebuilder,X,AI eval builder,Report Delivered,"Eval result changes across runs","Small LLM benchmark run",Starter,150,requested,sha256:pending,strong,"Ask whether all important evals should be verified",2026-06-18,"First run delivered; user asked about batch support."
```

## Qualification Rules

A lead is qualified when all are true:

```text
1. They have a real experiment or result.
2. They cannot fully trust or reproduce that result.
3. The result affects a decision, claim, release, benchmark, model comparison, or research conclusion.
```

## Conversion Rules

A lead should be pushed to payment when any are true:

```text
1. They ask to verify another run.
2. They ask whether the workflow can be repeated automatically.
3. They ask about higher precision.
4. They ask for a report they can share with someone else.
5. They describe the cost of being wrong.
```

## Weekly Metrics

Track weekly:

```text
1. Leads identified.
2. DMs sent.
3. Replies received.
4. Experiments secured.
5. Reports delivered.
6. Paid conversions.
7. Repeat-use signals.
8. Revenue booked.
9. Average price accepted.
10. Main objection categories.
```

## Activation Evidence

The customer-validation activation gate requires:

```text
1. At least 3 real external experiments processed.
2. At least 1 paid customer.
3. At least 1 repeat-use signal.
4. Pricing tested against real willingness to pay.
```

Until those exist, this tracker is operational infrastructure, not market proof.

## Archive Readiness

This tracker defines the full customer-validation status flow, required evidence fields, qualification rules, conversion rules, weekly metrics, and activation evidence needed to continue without prior chat context.

StegVerse-Labs - 40% complete
StegCore - 34% complete
StegCore - 27% complete TO GOAL ACTIVATION;
Fully developed files vs scaffolding/stubs - 38% complete
Δ [StegCore: 34%vs40%] - Customer pipeline tracking is now defined and ready for use; activation remains blocked by real leads, delivered external experiments, payment, and repeat-use evidence.
