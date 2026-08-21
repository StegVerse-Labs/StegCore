# LLM / User Surface Mechanics Mirror Handoff

## Source of truth

```text
organization: StegVerse-Labs
repository: StegCore
branch: main
goal_id: LLM-USER-SURFACE-MECHANICS-001
status: ACTIVE_DISTINCT_SUPPORT
parent_goal: PERSONHOOD-CONTINUITY-001
parent_handoff: docs/PERSONHOOD_CONTINUITY_MIRROR_HANDOFF.md
credential_authority: TV/TVC
non_tv_tvc_secrets_allowed: false
```

This handoff makes durable the mechanical separation between the LLM / governed machine surfaces and the information actually displayed to a human. It exists because the development requirement is broader than Personhood Continuity: StegVerse must absorb machine complexity rather than transfer responsibility for understanding that complexity to the user.

## Core design rule

```text
machine complexity may increase;
user-visible complexity should not increase merely because machine complexity increased.
```

Anything that appears to be computer-generated status, schema, system metadata, machine state, policy output, receipt data, diagnostic text, model/runtime state, hashes, identifiers, confidence values, manifests, logs, configuration, or other implementation detail is hidden from the ordinary user surface unless it is necessary for the user's current intent or the user requests greater resolution.

Development, debugging, validation, evidentiary review, and administrative surfaces may expose these details. Ordinary product surfaces should not.

## Mechanical surface separation

The implementation must distinguish at least the following conceptual surfaces:

```text
S0_GOVERNED_STATE
  canonical state, provenance, policy, receipts, permissions, continuity, evidence, runtime facts

S1_MODEL_CONTEXT
  authorized context made available to the LLM or analytical model for the current task

S2_MODEL_ANALYSIS
  derived interpretation / candidate answer / candidate action; no authority by itself

S3_ADMISSIBILITY_AND_DISCLOSURE
  governance resolution determining what may be used, disclosed, transformed, or acted upon

S4_HUMAN_REPRESENTATION
  minimum-resolution, human-readable representation appropriate to the user's intent

S5_EVIDENTIARY_DRILLDOWN
  progressively greater supporting detail when requested and authorized

S6_TECHNICAL_PROVENANCE
  receipts, hashes, versions, policy decisions, reconstruction metadata, logs, and other machine detail
```

These surfaces must not be collapsed into one UI or one undifferentiated model response.

## Authority boundary

```text
model can interpret != model can disclose
model can see authorized context != user can see all model context
record exists != record is discloseable
analysis exists != analysis is discloseable
technical state exists != technical state belongs on the user surface
```

The LLM / model produces candidates and interpretations. The governed system determines admissibility and disclosure. The human-facing renderer presents only the authorized minimum-resolution representation.

Model output never becomes disclosure or execution authority merely because it was generated.

## Minimum-resolution rendering

The renderer should answer at the lowest useful resolution that fully satisfies the user's intent.

Example:

```text
User: Did the message go through?
Visible answer: Yes. It was delivered.
```

The ordinary surface should not automatically add:

```text
DELIVERY_STATE=CONFIRMED
POLICY=steg.delivery.v4
RECEIPT=...
CONFIDENCE=...
TRANSPORT=...
HASH=...
```

If the user asks why or requests evidence, resolution may increase:

```text
User: How do you know?
Visible answer: The verified recipient confirmed delivery at 10:42 AM.

User: Show me the evidence.
Visible answer: Authorized receipt/evidence summary.

User: Show technical provenance.
Visible answer: Canonical receipts, hashes, policy/version details, reconstruction evidence.
```

## Competency must not be a setup burden

The system should not force a user to choose "beginner", "intermediate", or "advanced" before interacting.

User intent determines resolution dynamically. A user who asks an ordinary human question should receive an ordinary human answer. A user who asks for technical detail should receive progressively deeper information when authorized.

The system may learn interaction preferences over time, but preference adaptation must not silently increase disclosure authority.

## Human statement preference

Where a human-readable statement can faithfully represent the governed state, prefer the human statement over exposing the machine representation.

Examples:

```text
"You're protected."
not
"Security status: ACTIVE"

"This would share your location. Share it this time?"
not
"LOCATION_DISCLOSURE obligation triggered under policy SV-GOV-47"

"I can't tell from the available evidence."
not
"confidence=0.41; threshold failure"
```

Machine data remains available beneath the representation where authorized.

## No false simplification

Hiding machine complexity must not mean deleting evidence or weakening rigor.

The same governed event may have multiple representations:

```text
HUMAN
  "Your message was delivered privately."

INTERESTED_USER
  "It was delivered directly to the verified recipient. No location information was shared."

ADVANCED
  "Identity verified; transport protected; metadata disclosure: none; delivery confirmed."

EVIDENTIARY
  canonical receipt, policy evaluation, signatures, versions, hashes, replay/reconstruction material
```

All representations refer to the same underlying governed state. Increasing resolution reveals more representation; it does not create a different historical fact.

## LLM mechanics for Personhood Continuity

For Personhood Continuity specifically, the future requester may ask their own StegVerse assistant ordinary questions such as:

```text
What did he like to eat?
Why did he make that decision instead of the other one?
Was that typical of him?
Did his actions match what he said he believed?
```

The LLM may need access to multiple authorized evidence classes and temporal states to answer. That internal analytical work should remain invisible by default.

The visible answer should distinguish fact from inference in natural language without dumping machine labels.

Example:

```text
"He never gave a direct explanation for that decision. The strongest evidence suggests he was trying to avoid giving a third party control over something he considered important. He made similar choices several times during that period."
```

Only if the requester asks for evidence should the interface descend into supporting statements, behaviors, dates, provenance, and eventually technical receipts.

## Displayed-surface invariant

```text
DISPLAY(user, request) = minimum faithful authorized representation of governed state needed to satisfy current intent
```

The displayed surface must not be a raw serialization of model state, database state, governance state, or receipt state.

## Development / diagnostic exception

Developer, verifier, administrator, audit, debugging, and evidentiary modes may expose machine-native representations when that is the user's actual intent and authority.

This exception must not leak into ordinary product UI simply because those data are easy for developers to render.

## Required implementation mechanics

```text
1. A typed separation between governed state, model context, candidate analysis, disclosure decision, and rendered answer.
2. A renderer or presentation contract that supports progressive resolution.
3. A disclosure gate after model analysis and before user-visible output where required.
4. A mechanism for withholding unauthorized context even when the model used an authorized derived representation.
5. A mechanism for exposing interpretations without necessarily exposing restricted underlying evidence.
6. A drill-down contract for "why", "show evidence", and "show technical provenance" requests.
7. Tests proving that hidden machine data do not appear on ordinary user surfaces.
8. Tests proving that requesting more resolution does not bypass disclosure authority.
9. Tests proving that model output does not become authority.
10. Tests proving that simple human answers remain faithful to the canonical governed state.
11. UI review criteria that treat unnecessary machine-looking text as product friction / defect on ordinary surfaces.
12. Accessibility and low-competency testing against interfaces that do not assume familiarity with technical terminology.
```

## Relationship to other work

```text
PERSONHOOD_CONTINUITY_MIRROR_HANDOFF.md
  applies these mechanics to intergenerational life records and analytical personhood queries

AURI / StegTalk
  likely owns major conversational human-facing presentation surfaces

StegCore
  owns or participates in analytical/admissibility boundaries and candidate evaluation

Governance
  owns or participates in disclosure authority and policy resolution

Continuity / StegID
  owns or participates in durable evidence identity / continuity
```

Exact ownership must be reconciled against each repository's applicable *_MIRROR_HANDOFF.md before mutation.

## Current status

```text
mechanical principle: DOCUMENTED
surface separation: DOCUMENTED_CONCEPTUALLY
typed implementation: NOT_BUILT
renderer contract: NOT_BUILT
disclosure/output gate integration: NOT_BUILT
progressive drilldown tests: NOT_BUILT
ordinary-surface friction tests: NOT_BUILT
release: NOT_READY
activation: NOT_AUTHORIZED
archive_ready: false
```

## Next executable goal

During Personhood Continuity architecture reconciliation, map S0-S6 to existing StegCore, Governance, Continuity/StegID, and StegTalk/Auri primitives. Reuse existing authority boundaries where they exist, then create only the missing typed contracts and tests needed to enforce the LLM-to-user surface separation.

## Archive condition

Do not archive this lane merely because the mechanics are documented. Archive only when the required implementation responsibilities are completed or durably assigned to explicit owning handoffs/tasks and those owners have consumed the responsibility.
