# Neural Micro-Node Governance Mirror Handoff

Status: ACTIVE — DISTINCT VALIDATION / PHYSICAL-INTEGRATION WORK REMAINS
Date: 2026-08-08
Repository: `StegVerse-Labs/StegCore`
Branch: `main`
Active goal: `STEGCORE-NEURAL-ENDTOEND-002`
Predecessor goal: `STEGCORE-NEURAL-MICRONODE-001`
Canonical successor issue: `#72`
Predecessor issue: `#71`

## Correction to prior completion claim

The predecessor lane correctly installed and validated an adapter-neutral neural evidence boundary, but the prior archival conclusion was too broad. It did **not** establish either of the two additional capabilities required by the originating session insight:

1. a full end-to-end StegGate governance composition testable from neural receiver evidence through canonical admissibility, commit coherence, consequence invocation, and receipt; or
2. a physical bidirectional transmit/receive model representing addressing, coupling, channel quality, stimulation/observation bounds, noise, calibration, and post-consequence observation.

`STEGCORE-NEURAL-MICRONODE-001` remains a completed predecessor. `STEGCORE-NEURAL-ENDTOEND-002` corrects and extends it. No software result is biological activation evidence.

## Governing sources and collision control

Read and preserve:

- `docs/STEGCORE_MIRROR_HANDOFF.md`
- `docs/STEGGATE_NETWORK_GOVERNANCE_MIRROR_HANDOFF.md`
- `docs/STEGGATE_PORTABLE_MICRONODE.md`
- `docs/STEGGATE_PRODUCT_REVIEW_V4.md`
- `src/stegcore/steggate.py`
- `src/stegcore/steggate_runtime.py`
- `src/stegcore/neural_micronode.py`

Existing external-evidence and portable-micro-node lanes remain distinct. This successor consumes canonical StegGate and commit-coherence surfaces and does not redefine them.

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

Hosted predecessor evidence: run `31289736205`, job `93184768876`, SUCCESS; schema valid; `7 passed in 0.05s`; authority-boundary verification passed.

## Active successor claim

```text
task_id: STEGCORE-NEURAL-ENDTOEND-002
originating_goal: full testable governance + physical bidirectional model for addressed neural micro-node transport
organization: StegVerse-Labs
repository: StegCore
branch: main
claimant: this execution lane
role: CLAIMED_FOR_VALIDATION
claim_created: 2026-08-09
claim_release_condition: latest end-to-end hosted workflow succeeds including reference-transceiver checks; job/log evidence is inspected; issue #72 and inventory are reconciled; remaining real-hardware boundary is durably assigned
collision_boundary:
  - docs/NEURAL_MICRONODE_GOVERNANCE_MIRROR_HANDOFF.md
  - docs/NEURAL_BIDIRECTIONAL_PHYSICAL_MODEL.md
  - docs/NEURAL_REFERENCE_BIDIRECTIONAL_ULTRASOUND_MODEL.md
  - docs/NEURAL_END_TO_END_VALIDATION_PLAN.md
  - src/stegcore/neural_physical_channel.py
  - src/stegcore/neural_governance_system.py
  - tests/test_neural_end_to_end.py
  - .github/workflows/neural-end-to-end.yml
  - data/neural-end-to-end-session-inventory.json
next_task_after_release: real adapter conformance only when a named adapter/device repository and empirical calibration/safety evidence exist
```

## Full formal governance system — installed

`src/stegcore/neural_governance_system.py` now composes:

```text
packet candidate-hash binding
 -> neural receiver evidence decision
 -> physical channel eligibility
 -> bounded evidence refs added to canonical AdmissibilityRequest
 -> canonical StegGate / three-layer evaluation
 -> capability + continuity + approval predicates
 -> independent commit-coherence gate
 -> modeled physical consequence only after ALLOW + coherence ALLOW
 -> receipt binding neural, physical, StegGate, and commit hashes
```

The neural and physical layers add evidence references only. They do not synthesize actor authority, policy currency, delegation, evidence currency, capability, continuity, approval, consent, or execution authority.

`tests/test_neural_end_to_end.py` proves positive and negative paths including candidate mismatch, decoder authority-upgrade rejection, physical envelope failure, canonical policy denial, commit-coherence denial, missing commit authority, and weak READ observations.

## Device-independent physical model — installed

`docs/NEURAL_BIDIRECTIONAL_PHYSICAL_MODEL.md` and `src/stegcore/neural_physical_channel.py` define separate READ and WRITE physical eligibility using adapter-scoped target resolution, calibration, targeting confidence, coupling, transfer efficiency, noise, sensor quality, latency, and an adapter-declared normalized governed envelope.

The generic channel score is a deterministic conformance quantity, not a biophysical neural-response equation.

## Reference physical transceiver — installed

`docs/NEURAL_REFERENCE_BIDIRECTIONAL_ULTRASOUND_MODEL.md` instantiates the generic model against a concrete non-invasive research architecture with distinct ultrasound READ and WRITE paths.

Reference READ model:

```text
y_r(t) = H_r(theta_r, target) [x(t)] + n_r(t)
observation = D_r(y_r, calibration, provenance)
```

Reference WRITE model:

```text
e(target,t) = H_w(theta_w, target) [u(t)]
x_after = B(x_before, e, biological_context)
```

StegCore governs evidence about target identity, transfer operators/calibration, envelope compliance, observations, and commit-time authority. It does not assume a generic biological response operator `B` and therefore preserves:

```text
physical_focus_established != desired_neural_state_established
stimulation_delivered != semantic_content_delivered
```

The reference hardware surfaces explicitly require structural registration, target mapping, receive acquisition/beamforming, transmit/focus control, propagation calibration, signal conditioning, envelope/interlock enforcement, synchronization, and pre/post observation.

## Installed successor files and commits

```text
d79ebdebec6210b25fd385f8670b279b1a4008e9  reopen/correct handoff
8c03214db15b34ffe9cd42700bb174c61c58da8a  physical model specification
a71269447dfddd82fedeffecae593ab8320e1d76  physical channel runtime
7c7d4183ceba164adda9fc2f1d74088eb2aa09e2  full governance composition
7a3c16c48d1fac84f40d97d46e0207eea50cf3c6  end-to-end tests
8d0ba55be999bceda878febddf8eed8e19020030  initial end-to-end workflow
464a4469f94ebbe1723d472be26df0d083eac4d5  execution inventory
bb264ca647a76f85dcd5f60cab3263950cf7d9f8  validation plan
4e9afbea2876db0db899fda24a22909824f6cfb0  reference ultrasound transceiver model
f378b626e1448cbe42c095aeb7e6b677cf6bf700  reference-model workflow validation
```

## Hosted validation evidence

First workflow run after workflow creation: `31290103299` — FAILED because the workflow was created before its required inventory file existed. This ordering failure is preserved and not treated as implementation failure.

Successor run after inventory installation: `31290114046`, job `93185727730` — SUCCESS. Logs show:

```text
15 passed in 0.19s
inventory JSON valid
full governance composition present
physical non-activation boundary present
```

Latest run `31290171371` validates the additional reference ultrasound transceiver model and is the current machine-owned release condition. At handoff update time it remains pending/in progress; final claim release requires direct inspection of its completed job/log state.

## Durable inventory and issue

- `data/neural-end-to-end-session-inventory.json`
- `StegVerse-Labs/StegCore#72`

Issue #72 records the successor collision boundary and release condition. It must not be closed until latest hosted validation is directly observed successful and the inventory is reconciled.

## Scientific grounding and boundary

The reference physical architecture is consistent with established separation of neural sensors/decoders/effectors and with research on bidirectional interfaces. Non-invasive focused ultrasound provides a plausible targeted WRITE research modality; functional ultrasound imaging provides a plausible ultrasonic READ research modality. These are separate capabilities and neither establishes a universal neural packet transport system.

No software test may be reported as proof of safe human stimulation, accurate thought decoding, semantic writing, consent detection, biological activation, or a clinically deployable device.

## Real-hardware integration blocker

No named StegVerse neural hardware adapter repository currently exists. Hardware activation is therefore `BLOCKED`, owned by a future named adapter/device repository.

Machine-observable release condition:

```text
A specific adapter/device repository exists
AND accepts the StegCore neural adapter contract
AND supplies empirical target/registration evidence
AND supplies transmit + receive calibration evidence
AND supplies physical-unit -> governed-envelope mapping
AND supplies targeting/coupling/noise/latency evidence
AND supplies applicable safety evidence
AND supplies post-consequence observation capability/evidence
```

This is a real boundary, not an unspecified external task. The software report can complete while biological activation remains explicitly blocked, but the ecosystem must never equate the two.

## Cross-repository obligations

- `StegVerse-Labs/ara-admissibility-interop`: schema/profile propagation remains destination-owned and requires its live handoff to admit the work.
- Site / Publisher / admissibility-wiki / stegguardian-wiki: not publication targets until a public/release claim exists.

## Validation commands

```text
pytest -q tests/test_neural_micronode.py tests/test_neural_end_to_end.py
python -m json.tool data/neural-end-to-end-session-inventory.json >/dev/null
```

## Completion assessment

```text
predecessor_task_completion: 9/9
successor_task_completion: 8/10 complete; latest hosted reference-model validation + final reconciliation pending
developed_files: 8/8 successor implementation/evidence files installed
scaffolding_or_stubs: 0
missing_required_files: 0
validation: 3/4 complete; final hosted reference-model run pending observation
integration: 2/3 complete; full software governance + reference physical model installed, real hardware blocked by named evidence condition
session_consolidation: 10/11 goals durable; final validation/consolidation pending
archival_readiness: false
```

## Archive condition

Do not archive until run `31290171371` is completed and inspected, issue #72 and the durable inventory record the result, and no correction is required. Even after software-model completion, real neural hardware/biological activation remains a separate blocked integration goal and must stay explicitly non-activated until its release condition is satisfied.
