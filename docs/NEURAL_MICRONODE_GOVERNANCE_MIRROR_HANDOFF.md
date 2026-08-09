# Neural Micro-Node Governance Mirror Handoff

Status: ACTIVE — UNIQUE WORK REMAINS
Date: 2026-08-08
Repository: `StegVerse-Labs/StegCore`
Branch: `main`
Active goal: `STEGCORE-NEURAL-ENDTOEND-002`
Predecessor goal: `STEGCORE-NEURAL-MICRONODE-001`
Canonical issue: `#71` (predecessor validation record; successor issue required)

## Correction to prior completion claim

The predecessor lane correctly installed and validated an adapter-neutral neural evidence boundary, but the prior archival conclusion was too broad. It did **not** establish either of the two additional capabilities required by the originating session insight:

1. a full end-to-end StegGate governance composition that can be tested from neural receiver evidence through canonical admissibility, commit coherence, consequence invocation, and receipt; or
2. a physical bidirectional transmit/receive model that represents addressing, coupling, channel quality, stimulation/observation bounds, noise, calibration, and post-consequence observation.

Therefore `STEGCORE-NEURAL-MICRONODE-001` remains a completed predecessor, while this handoff is reopened for `STEGCORE-NEURAL-ENDTOEND-002`. No claim is made that present hardware can perform arbitrary neural read/write or that a software simulation proves biological capability.

## Governing sources and collision control

Read and preserve:

- `docs/STEGCORE_MIRROR_HANDOFF.md`
- `docs/STEGGATE_NETWORK_GOVERNANCE_MIRROR_HANDOFF.md`
- `docs/STEGGATE_PORTABLE_MICRONODE.md`
- `docs/STEGGATE_PRODUCT_REVIEW_V4.md`
- `src/stegcore/steggate.py`
- `src/stegcore/steggate_runtime.py`
- `src/stegcore/neural_micronode.py`

Existing StegCore external-evidence and portable-micro-node lanes remain distinct. The successor lane may consume canonical `evaluate_admissibility` / `governed_steggate_execute` surfaces but must not redefine them.

## Originating session goal

Develop the insight that least-stable ephemeral micro-node governance can address a specific downstream neural receiver while the BCI is transport/translation infrastructure. The receiver signature is translated into exactly the transition-relative admissibility evidence required for the incoming or outgoing packet.

## Preserved receiver model

The BCI/sensor/stimulator/decoder/encoder is transport or translation infrastructure, not automatically the receiver and never automatically an authority. The receiver is the specifically addressed downstream neural micro-node: a bounded region, ensemble, pathway, or other experimentally supportable functional target.

```text
source micro-node
 -> payload candidate + transition requirements
 -> transport / neural interface
 -> addressed neural micro-node
 -> receiver observation/signature
 -> bounded admissibility translation
 -> transition-relative evidence
 -> canonical StegGate governance
 -> commit coherence
 -> separately authorized consequence or non-consequence
 -> post-consequence observation
 -> receipt
```

Required non-equivalences:

```text
neural activity != thought
thought != intended meaning
intended meaning != instruction
instruction != authorization
authorization != admissibility
admissibility != execution
observation != receiver state in full
receiver signature != authority
translation confidence != authority
transport success != admissibility
physical coupling != semantic delivery
stimulation != intended neural state transition
```

## Completed predecessor implementation

Installed and hosted-validated:

- `schemas/neural-micronode-packet.schema.json`
- `src/stegcore/neural_micronode.py`
- `tests/test_neural_micronode.py`
- `.github/workflows/neural-micronode.yml`
- `data/neural-micronode-session-inventory.json`

Hosted evidence: run `31289736205`, job `93184768876`, SUCCESS; schema valid; `7 passed in 0.05s`; authority-boundary literal verification passed.

## Active implementation claim

```text
task_id: STEGCORE-NEURAL-ENDTOEND-002
originating_goal: full testable governance + physical bidirectional model for addressed neural micro-node transport
organization: StegVerse-Labs
repository: StegCore
branch: main
claimant: this execution lane
role: CLAIMED_FOR_IMPLEMENTATION
claim_created: 2026-08-09
claim_release_condition: end-to-end governance composition, physical channel model, tests, hosted validation, durable inventory, and handoff evidence complete; remaining hardware/biological capability boundaries explicitly transferred
collision_boundary:
  - docs/NEURAL_MICRONODE_GOVERNANCE_MIRROR_HANDOFF.md
  - docs/NEURAL_BIDIRECTIONAL_PHYSICAL_MODEL.md
  - src/stegcore/neural_physical_channel.py
  - src/stegcore/neural_governance_system.py
  - tests/test_neural_end_to_end.py
  - .github/workflows/neural-end-to-end.yml
  - data/neural-end-to-end-session-inventory.json
next_task_after_release: hardware-adapter conformance only when a real adapter/device and empirical calibration evidence exist
```

## Full governance system requirement

A completed software governance model must test the entire following chain, not only the neural evidence boundary:

```text
physical pre-observation
 -> neural evidence boundary
 -> canonical AdmissibilityRequest binding
 -> three-layer StegCore judgment/signal/execution evaluation
 -> capability / continuity / approval predicates
 -> StegGate disposition
 -> independent commit-coherence gate
 -> physical consequence callback only after ALLOW + coherence ALLOW
 -> post-consequence observation
 -> reconstructable receipt
```

The neural evidence decision is an admitted signal/evidence reference. It cannot fill or synthesize actor authority, policy currency, delegation, consent, approval, continuity, or capability predicates.

## Physical bidirectional model requirement

The physical model must represent the smallest device-independent variables necessary to reason about whether a packet can be physically coupled to and observed from an addressed neural target:

- modality/profile identity;
- source and target locator;
- targeting uncertainty and ambiguity;
- calibration state;
- coupling quality;
- channel attenuation / transfer efficiency;
- noise / interference;
- stimulation energy/intensity normalized to an adapter-specific safe envelope rather than universal biological units;
- observation sensitivity / specificity or equivalent bounded quality metrics;
- latency and freshness;
- write consequence class and reversibility declaration;
- read observation provenance;
- post-consequence observation when available.

The model must fail closed when target identity, calibration, channel bounds, safe envelope, or observation quality cannot be established.

## Scientific boundary

Current science supports multiple recording and stimulation modalities, including invasive electrical recording/stimulation and emerging non-invasive focused-ultrasound neuromodulation, but does not establish a universal addressable neural packet transport layer. The StegCore model is therefore a conformance/simulation abstraction: a real hardware adapter must supply empirically justified locator semantics, calibration, safety envelope, transfer characteristics, and observations.

No software test may be reported as proof of safe human stimulation, accurate thought decoding, semantic writing, consent detection, or biological activation.

## Active deliverables

1. `docs/NEURAL_BIDIRECTIONAL_PHYSICAL_MODEL.md`
2. `src/stegcore/neural_physical_channel.py`
3. `src/stegcore/neural_governance_system.py`
4. `tests/test_neural_end_to_end.py`
5. `.github/workflows/neural-end-to-end.yml`
6. `data/neural-end-to-end-session-inventory.json`
7. successor issue with claim/evidence
8. hosted workflow pass with job/log inspection
9. final handoff reconciliation

## Cross-repository obligations

- `StegVerse-Labs/ara-admissibility-interop`: schema/profile propagation remains destination-owned and requires its live handoff to admit the work.
- Site / Publisher / admissibility-wiki / stegguardian-wiki: not release/publication targets until this becomes a public or released capability.
- No real hardware repository is currently identified as a canonical neural adapter owner. This is a specific unresolved integration boundary, not an unspecified external task. The release condition for hardware integration is: a named adapter/device repository plus empirical calibration and safety evidence becomes available and accepts the interface contract.

## Validation commands planned

```text
pytest -q tests/test_neural_micronode.py tests/test_neural_end_to_end.py
python -m json.tool data/neural-end-to-end-session-inventory.json >/dev/null
```

## Completion assessment

```text
predecessor_task_completion: 9/9
successor_task_completion: 1/9 (handoff corrected/reopened)
developed_files: 1/7 successor files (handoff only)
scaffolding_or_stubs: 0
missing_required_files: 6
validation: 0/4 successor validation classes
integration: 0/3 successor integration classes
session_consolidation: 9/11 goals durable; 2 newly recognized goals active
archival_readiness: false
```

## Archive condition

This session is not archive-ready until the testable full governance composition and physical bidirectional model are installed and hosted-validated, their limitations are durably assigned, and the handoff records final evidence. A real human neural interface is not required for software-model completion, but absence of real hardware must remain an explicit non-activation boundary.
