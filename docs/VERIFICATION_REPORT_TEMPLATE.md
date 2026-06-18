# Verification Report Template

## Purpose

This template standardizes the output returned after a StegVerse verification engagement.

## Definition Of Done

The report is complete when it records the result, verification status, receipt status, reproducibility notes, boundary limits, and commercial follow-up signal.

## Report Header

```text
Report ID:
Customer / Prospect:
Verification Name:
Precision Tier:
Urgency Tier:
Report Date UTC:
Status: complete | complete_with_boundary_limits | failed
```

## 1. Result Summary

```text
Summary:
Primary Output:
Expected Output Match: yes | no | partial | not_declared
```

## 2. Verification Status

```text
Validation Status: passed | failed | partial | not_applicable
Receipt Status: generated | not_generated
Receipt Hash Or Reason:
Stability Classification: stable | unstable | inconclusive
```

## 3. Declared Boundary

```text
Work Reference:
Evidence Reference:
Environment Notes:
Version / Seed Notes:
Known Boundary Limits:
```

## 4. Reproduction Notes

```text
Required Inputs:
Required Environment:
Review Steps:
Expected Re-check Result:
```

## 5. Variance / Precision Notes

```text
Observed Variance:
Precision Tier Applied:
Reason For Tier:
Upgrade Recommendation:
```

## 6. Interpretation

```text
Is the result reproducible under the declared conditions?
What uncertainty remains?
What should be verified next?
```

## 7. Commercial Follow-Up

```text
Value Signal: low | medium | high | urgent
Repeat-Use Signal: none | possible | requested | subscription-interest
Recommended Next Offer: starter | pro | critical | subscription
```

## Final Line

```text
This result is reproducible under the same declared conditions unless boundary limits above state otherwise.
```
