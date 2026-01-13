# Governance Scope — StegCore

StegCore is a **governance service** that authorizes or refuses actions based on declared boundaries, trust continuity, and accountability rules.

## What StegCore CAN do

- Declare governance boundaries for StegVerse modules
- Evaluate proposals and return a decision:
  - **authorized** (with constraints) or
  - **refused** (with explanation + escalation guidance)
- Require **dual approval** (human + AI) where declared
- Gate downstream modules that lack valid BCAT declarations
- Enforce refusal-as-success and explainable degradation
- Require renewal/expiry semantics for authority

## What StegCore CANNOT do

- Execute irreversible actions (deploy, transfer funds, delete data, submit regulated forms)
- Store or process raw regulated payloads (PII/PHI/financial docs) as a governance decision primitive
- Override human custodian accountability
- Expand its own authority unilaterally
- Authorize actions outside its declared scope

## Default Posture

If uncertain, incomplete, or unverified:
- **Refuse**
- **Explain**
- **Escalate to human custodian**
