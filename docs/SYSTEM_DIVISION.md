# System division

This document gives the role boundaries for StegCore/StegGate. StegGovernance governs the manifested data; StegCore applies established rules and records their application. The mechanism does not establish those rules.

## Owner statement

The owner statement was filed on November 10, 2026 under [DOC-IMPL-001](https://github.com/StegVerse-Labs/.github/issues/3443#issuecomment-6786709429), with [paired provenance](https://github.com/StegVerse-Labs/.github/issues/3467#issuecomment-6786711760). The seven items are preserved below without changing their substance.

1. StegGovernance is the capability to govern the data carried by manifest to the
   governance mechanism. The governed object is the DATA; governance travels with the
   data under its manifest.
2. A manifest states the route.
3. InTr is the transfer protocol between Orgs. A manifest either passes the InTr hop or
   it does not. If it does not, exactly one of two things is true: the manifest is wrong
   and needs remediation, OR the InTr hop isn't working and needs repair. There is no
   third location. InTr admits nothing, denies nothing, and dispositions nothing.
4. Governance rules are established first. The governance mechanism (StegCore) is the
   application of those established rules and the record of the application — nothing
   more: it does not author rules.
5. Orgs admit at ingress, under their own established rules, into their own ledgers.
   Inter-Org continuity is the matched, dual-recorded receipt pair; it is evidence of
   the transfer, not authority over either Org's internal state.
6. The SDK of record is identified from its tags and releases — never from branch
   recency. A release candidate whose tag and package publication are pending is not
   a release.
7. How the ecosystem is built: what is discussed is documented in the locations that
   matter (the repos and Org records where lanes pick up work), and implemented there.
   Documentation that lives only in a chat, a memory, or a coordination filing does not
   exist for the fleet. Lanes pick documented work up, deliberate over the solution,
   and apply it in the repos of record.

## Reading an implementation record

Distinguish the transfer outcome from the receiving Organization's ingress decision. A transfer receipt pair evidences continuity across the two Organizations. The receiving Organization applies its own established ingress rules and records that application in its ledger. StegCore applies established governance rules to the manifested data; it does not author rules. A manifest states the route.

Documentation presence, source implementation, source validation, an observed transfer, Organization ingress and a released version are separate claims. Establish each from its own evidence. When existing code or a retained historical record uses different vocabulary, retain that evidence and identify the concrete source/contract difference rather than silently changing the record or assigning admission authority to InTr.

## Work record

Canonical Goal Task ID: `INTERLOCK-INTR-RUNTIME-INDEPENDENT-PROTOCOL-001`; COSV `50000000102000`. DOC-IMPL-001 is the queue task under that existing goal, not a replacement identity or a counter reset. [Documentation handoff](SYSTEM_DIVISION_DOCUMENTATION_MIRROR_HANDOFF.md) records the source and remaining integration evidence.
