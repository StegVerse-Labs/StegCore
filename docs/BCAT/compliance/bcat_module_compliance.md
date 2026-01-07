# BCAT Compliance Check for New Modules

All new StegVerse modules must demonstrate BCAT compliance prior to integration.

This is not a checklist for approval.
It is a proof of governability.

## Required Declarations

Each module must explicitly document:

1. **Authority Source**
   - How is authority granted?
   - What boundary conditions enable it?

2. **Trust Continuity**
   - What assumptions must remain true over time?
   - How does the module detect continuity breaks?

3. **Boundary Conditions**
   - What conditions constrain autonomy?
   - How are they inspected and audited?

4. **Degradation Behavior**
   - How does the module reduce or refuse action?
   - Is non-action explainable?

5. **Human Accountability**
   - Who is responsible when the module acts?
   - Who is responsible when it refuses?

## Prohibited Patterns

Modules must not:
- self-authorize
- silently escalate scope
- auto-renew authority without review
- treat refusal as error
- obscure custody or responsibility

## Acceptance Principle

A module is BCAT-compliant if it can clearly answer:

> “Under what conditions should this system *stop* acting — and how will humans know why?”

If that answer is unclear, the module is not governable.
