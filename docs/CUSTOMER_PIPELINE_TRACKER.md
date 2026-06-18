# Customer Pipeline Tracker

## Purpose

This tracker converts GTM activity into measurable revenue signal for StegVerse Precision Compute.

## Definition Of Done

The tracker is complete when every prospect can be placed in one status and every completed engagement records whether it produced payment, repeat-use signal, or pricing resistance.

## Minimum Columns

| Column | Required | Description |
| --- | --- | --- |
| prospect_id | yes | Stable internal identifier. |
| name | yes | Person, team, or company. |
| source | yes | X, Reddit, Hugging Face, LinkedIn, Discord, referral, inbound, other. |
| segment | yes | AI eval builder, quant, researcher, governance, enterprise, other. |
| status | yes | Current pipeline status. |
| pain_point | yes | The result or workflow they do not trust. |
| verification_request | no | The candidate verification request. |
| precision_tier | no | Exploratory, Analytical, Critical. |
| price_discussed_usd | no | Price anchor or quoted amount. |
| value_signal | no | Low, medium, high, urgent. |
| outcome | no | open, won, lost, deferred, no-fit. |
| repeat_signal | no | none, asked-for-more, recurring-needed, subscription-interest. |
| notes | no | Context for next follow-up. |
| last_contacted_utc | no | Last outbound or inbound touch. |
| next_action | yes | The next specific action. |

## Status Flow

```text
lead_identified
outreach_sent
replied
verification_requested
verification_reviewed
report_delivered
value_confirmed
price_discussed
paid
repeat_workflow
closed_lost
```

## Qualification Rules

```text
Qualified prospect:
- Has a computational result they do not fully trust.
- Can explain what wrongness or variance costs them.
- Can define what kind of verification would be useful.

High-priority prospect:
- Has repeated verification need.
- Uses AI evaluations or experiments in active work.
- Cares about correctness more than novelty.
- Can pay or influence payment.
```

## Success Metrics

```text
Weekly:
- 20 to 30 targeted outreaches.
- 3 to 5 replies.
- 2 to 3 received verification requests.
- 1 paid conversion attempt.

Activation:
- 3 external verification reports processed.
- 1 paid user.
- 1 repeat-use signal.
```
