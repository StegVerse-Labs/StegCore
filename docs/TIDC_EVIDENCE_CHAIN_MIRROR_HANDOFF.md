# TIDC Evidence-Chain Ecosystem Mirror Handoff

## Target

```text
source_repo: StegVerse-Labs/Site
management_repo: StegVerse-Labs/StegCore
layer: blinded second-coding evidence chain
```

## Determination

The Site-level TIDC blinded-return layer is built and activated. Before this record, the StegVerse ecosystem-management layer did not contain a dedicated machine-readable handoff, verification contract, or task coordination surface for that evidence chain.

This handoff establishes the StegCore management mirror without transferring research, adjudication, publication, or proof authority away from `StegVerse-Labs/Site`.

## Authoritative Site records

```text
Site issue: #126
activation_commit: 32f2e2111c5d49678659960a7a7ad1784c6a432f
packet: data/tidc/blinded-coding/BCP-2026-07-27-01.md
workflow: .github/workflows/check-tidc-research.yml
return_validator: scripts/validate_tidc_blinded_return.py
receipt_generator: scripts/create_tidc_blinded_return_receipt.py
comparison_engine: scripts/compare_tidc_blinded_coding.py
adjudication_protocol: docs/TIDC_BLINDED_CODING_ADJUDICATION_PROTOCOL.md
```

## Ecosystem-management role

StegCore may:

- track the external-return dependency;
- verify that required Site artifacts exist;
- coordinate receipt, comparison, and adjudication tasks;
- record downstream mirror-verification tasks;
- determine archive readiness from committed evidence.

StegCore may not:

- invent or repair the blinded return;
- adjudicate scientific classifications by management fiat;
- convert AI coding into human replication;
- promote a research note into proof;
- grant publication, execution, or research authority.

## State machine

```text
SITE_LAYER_BUILT
-> SITE_LAYER_ACTIVATED
-> EXTERNAL_RETURN_PENDING
-> RETURN_PRESERVED
-> STRUCTURAL_VALIDATION_PASSED
-> RECEIPT_GENERATED
-> COMPARISON_GENERATED
-> DISAGREEMENTS_RECORDED
-> ADJUDICATION_STATUSES_ASSIGNED
-> RELEASE_2_ACTIVE
-> DOWNSTREAM_MIRRORS_VERIFIED
-> ARCHIVE_READY
```

The current state is:

```text
SITE_LAYER_ACTIVATED
EXTERNAL_RETURN_PENDING
```

## Completion criteria

The ecosystem layer is operationally complete when:

1. the untouched return is committed in Site;
2. Site CI validates it;
3. receipt and comparison artifacts are preserved;
4. every disagreement has a recorded status;
5. Release 2 is advanced only under the declared boundary;
6. downstream public mirrors are checked;
7. an archive-readiness receipt is committed.

## Coordinated repositories

```text
StegVerse-Labs/Site                   research source and public mirror
StegVerse-Labs/StegCore               ecosystem task coordination
GCAT-BCAT-Engine/Publisher             downstream publication verification
admissibility-wiki                     downstream doctrine/mirror verification
stegguardian-wiki                      downstream governance mirror verification
```

## Non-overlap

This layer does not modify the TIDC seed event ledger, perform scientific adjudication, or interfere with unrelated StegCore provider, financial, HIL, or StegVA task chains.

## Archive rule

Do not announce archive readiness while the external return, comparison, adjudication, or downstream verification chain remains open.
