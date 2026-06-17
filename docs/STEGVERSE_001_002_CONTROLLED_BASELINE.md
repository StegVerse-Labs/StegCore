# StegVerse-001 / StegVerse-002 Controlled Baseline

## Purpose

This document defines the StegCore activation baseline for controlled continuity and master-record ingestion across StegVerse-001 and StegVerse-002.

StegCore is the admissibility decision surface. It consumes verified continuity context and declared policy references. It does not mint receipts, store identity, issue secrets, or declare consent.

## Done criteria

This baseline is ready for activation review when:

1. `activation_manifest.json` exists and names the StegVerse-001/002 controlled baseline.
2. StegVerse-001 continuity posture is represented as required context.
3. StegVerse-002 master-record ingestion posture is represented as required context.
4. Commit-time context is required before an ALLOW decision can stand.
5. Stale context and authority overreach produce DENY posture.
6. The validation workflow exists and runs the admissibility baseline tests.

## Required true predicates

- `continuity_receipt_present`
- `policy_reference_present`
- `authority_boundary_declared`
- `commit_time_context_present`

## Required false predicates

- `stale_context`
- `authority_overreach`

## Decision rule

A baseline vector may return `ALLOW` only when every required true predicate is true and every required false predicate is false.

Every other posture must return `DENY`, `DEFER`, or a more specific fail-closed result once the executable evaluator is installed.

## Boundary

This baseline does not prove identity, user consent, live token issuance, or org-wide activation. It defines the minimum predicate surface that StegCore should require before controlled continuity or master-record ingestion can be treated as admissible.
