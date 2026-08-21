# Personhood Continuity Mirror Handoff

## Source of truth

```text
organization: StegVerse-Labs
repository: StegCore
branch: main
goal_id: PERSONHOOD-CONTINUITY-001
status: ACTIVE_DISTINCT_SUPPORT
credential_authority: TV/TVC
non_tv_tvc_secrets_allowed: false
external_execution_default: DISABLED
```

This file is the durable source of truth for the StegVerse Personhood Continuity concept and its development requirements. It exists so this capability remains visible during development and does not depend on recovering prior conversation context.

## Core purpose

Personhood Continuity allows a person to deliberately preserve a governed, provenance-aware, temporally coherent record of their life so that other authorized people — including children, grandchildren, later descendants, or other explicitly permitted audiences — can ask their own StegVerse assistant questions about who that person was.

The system is not merely a profile, biography, memorial, or persona simulation. It is a governed life record with an analytical interface.

Examples of authorized questions include:

```text
What did this person like to eat?
What was their favorite color during a given period of life?
How did they make difficult decisions?
What was their work ethic like?
Were they compassionate toward people?
Why did they do this that way instead of another available way?
What alternatives did they appear to consider?
Was that decision typical of their behavior at the time?
Did later evidence show that they changed their mind?
Did their stated values align with their observed behavior?
```

## Foundational authority rule

The represented person controls what is available.

Preservation MUST NOT imply disclosure.
Analysis MUST NOT imply disclosure.
Existence MUST NOT imply availability.

A record may be preserved and analytically usable by the system while remaining unavailable to a requester. Disclosure is a separately governed transition evaluated at query time.

The person may govern availability by audience, relationship, subject, time, life period, evidence class, resolution, posthumous state, or other admissible policy dimensions.

Representative disclosure classes may include:

```text
PRIVATE_TO_SELF
SPOUSE_OR_PARTNER
CHILDREN
DESCENDANTS
NAMED_RELATIONSHIP_OR_GROUP
POSTHUMOUS_DESCENDANTS
PUBLIC
NEVER_DISCLOSE
```

These are conceptual classes, not yet canonical schema enums.

## Personhood is temporal, not a flat profile

Personhood MUST NOT be reduced to static attributes such as:

```text
favorite_color = blue
favorite_food = pizza
occupation = engineer
```

The system should preserve temporal claims and changes, for example:

```text
The person consistently identified blue as a favorite color during this period.
Their thinking about responsibility changed materially after this event or life stage.
They approached risk differently in earlier and later periods.
```

Later state must not silently overwrite earlier state.

## Evidence classes

The analytical assistant must preserve the distinction between at least the following conceptual evidence classes:

```text
DIRECT_TESTIMONY
OBSERVED_BEHAVIOR
THIRD_PARTY_TESTIMONY
CONTEMPORANEOUS_CONTEXT
OUTCOME_EVIDENCE
LATER_REFLECTION
AI_ANALYTICAL_INFERENCE
```

An answer MUST NOT collapse an AI inference into direct testimony or observed fact.

A requester should be able to ask, in ordinary language:

```text
Why do you think that?
What did they actually say?
What did they actually do?
What evidence supports that interpretation?
Was that known at the time or only learned later?
```

The system must be able to increase evidentiary resolution without changing the underlying historical record.

## Contemporaneous reconstruction vs retrospective evaluation

The system must distinguish:

```text
OCCURRED_STATE
CONTEMPORANEOUS_KNOWLEDGE_STATE
EXPRESSED_RATIONALE
BEHAVIORAL_PATTERN
AVAILABLE_ALTERNATIVES
OUTCOME_STATE
LATER_REFLECTION
RETROSPECTIVE_ANALYSIS
```

A query such as "Why did they make this decision?" should preferentially analyze what the person knew, believed, expressed, and could reasonably evaluate at the time.

A separate query such as "Knowing what happened afterward, was it a good decision?" may use later outcome evidence.

Future knowledge must not be silently injected into contemporaneous reconstruction.

## Analytical interface

The record must support new questions that were not anticipated while the person was alive. Future assistants may perform new analyses over preserved evidence without mutating the historical record.

The intended model is:

```text
stable governed evidence
        +
future analytical methods
        =
higher-resolution understanding without historical mutation
```

This enables intergenerational reasoning inheritance rather than merely factual biography.

## Human-facing representation

The ordinary user experience should remain conversational and human-readable. Machine structure should remain hidden unless greater resolution is requested.

Example progression:

```text
Q: Why did they do it that way?
A: Human-readable analytical answer.

Q: Why do you think that?
A: Concise explanation of the strongest evidence and uncertainty.

Q: Show me the evidence.
A: Authorized supporting events, statements, behavior, dates, and provenance.

Q: Show technical provenance.
A: Receipts, hashes, versions, policy resolution, continuity evidence, and reconstruction metadata where authorized.
```

The rigor remains underneath the human representation. Technical data must not be exposed merely because it exists.

## Minimum-resolution interaction rule

Observable complexity should expand only to the minimum resolution necessary for the requester's current intent and authorization.

The system should not require users to choose a technical competency level before use. Resolution should be inferred from the request and increased only when requested or necessary.

## Third-party privacy

A person's authority to preserve their own life does not automatically grant authority to disclose private information about other people appearing in that life record.

The system must support preserving a person's experience or analytical pattern while withholding, redacting, abstracting, or otherwise governing third-party-identifying evidence.

An authorized interpretation may be discloseable while one or more underlying evidence items remain restricted.

## Persona simulation boundary

Personhood Continuity is not equivalent to a synthetic resurrection or persona simulation.

The architecture must distinguish:

```text
HISTORICAL_PERSONHOOD_RECORD = governed evidence and provenance
INTERPRETIVE_MODEL = derived analysis over that record
PERSONA_SIMULATION = optional generated representation requiring separate explicit authority
```

The default capability is understanding the person, not pretending the person is presently speaking.

If no sufficient evidence exists, the assistant must be permitted and expected to answer that the record does not support a reliable conclusion.

## Anti-idealization requirement

The analytical layer must support contradictory, unfavorable, or unresolved evidence. It must not automatically create an idealized memorial narrative.

Valid analytical questions include:

```text
Were they wrong here?
Did their behavior contradict their stated values?
What mistakes did they repeat?
Did they learn from this failure?
Did different observers describe them differently?
What evidence weakens the dominant interpretation?
```

## Core invariant

```text
preserve evidence;
govern availability;
separate provenance classes;
retain temporal state;
permit future analysis;
never rewrite inference into history.
```

## Relationship to StegVerse governance

Personhood Continuity should reuse existing StegVerse principles rather than create a parallel authority model:

```text
identity continuity
permission / admissibility
provenance
state transition history
replay and reconstruction
temporal versioning
selective disclosure
receipts and evidence
TV/TVC credential authority
```

No model output confers disclosure or execution authority by itself.

## Development requirements

The following remain to be designed or implemented before this capability can be considered built:

```text
1. Canonical personhood-record schema.
2. Temporal claim and evidence model.
3. Disclosure-policy schema and audience/relationship resolution.
4. Query-time admissibility contract for personhood disclosure.
5. Evidence-class provenance representation.
6. Contemporaneous-state reconstruction contract.
7. Retrospective-analysis contract.
8. Third-party privacy / selective-disclosure rules.
9. Derived-analysis provenance and confidence/uncertainty representation.
10. Human-readable minimum-resolution answer surface.
11. Evidentiary drill-down / technical provenance surface.
12. Explicit persona-simulation separation and authority gate.
13. Tests for unsupported inference, contradictory evidence, temporal drift, unauthorized disclosure, and third-party privacy.
14. Replay/reconstruction fixtures demonstrating that later analyses do not mutate historical evidence.
15. Cross-repository integration mapping for Continuity/StegID, Auri/StegTalk, Governance, Site, Publisher, admissibility-wiki, and stegguardian-wiki where appropriate.
```

## Installation destinations currently anticipated

```text
StegVerse-Labs/StegCore
  - canonical analytical and admissibility contracts
  - query-time decision/evaluation surface

StegVerse-Labs/Continuity or current StegID continuity authority
  - durable identity/evidence continuity and receipt linkage

StegVerse-Labs/StegTalk / Auri surface
  - conversational access and minimum-resolution human representation

StegVerse-Labs/Governance
  - disclosure policy, delegated authority, posthumous policy, relationship constraints

Propagation candidates after owning release gates authorize publication
  - StegVerse-Labs/Site
  - GCAT-BCAT-Engine/Publisher
  - admissibility-wiki
  - stegguardian-wiki
```

These destinations are architectural candidates and must be reconciled with each repository's applicable mirror handoff before mutation.

## Current status

```text
concept: DOCUMENTED
source_of_truth_handoff: INSTALLED
canonical_schema: NOT_BUILT
runtime: NOT_BUILT
query_time_governance: NOT_BUILT
continuity_binding: NOT_BUILT
Auri_conversational_surface: NOT_BUILT
cross_repo_propagation: NOT_STARTED
release: NOT_READY
activation: NOT_AUTHORIZED
archive_ready: false
```

## Next executable goal

Perform a non-duplicative architecture reconciliation against current StegCore permission/admissibility, Continuity/StegID evidence, Governance disclosure, and Auri conversational handoffs. Then define the smallest canonical Personhood Continuity schema and query-time admissibility contract that reuses those existing primitives instead of duplicating them.

## Archive condition

Do not archive this workstream merely because the concept is documented. Archive only after responsibility for all required schema, governance, continuity, conversational, validation, release/propagation, and activation work is either completed or durably transferred to explicit owning handoffs/tasks and consumed by those owners.
