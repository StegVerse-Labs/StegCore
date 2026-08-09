# Neural Bidirectional Physical Channel Model

Status: implementation model for `STEGCORE-NEURAL-ENDTOEND-002`

## Purpose

This model defines the device-independent physical boundary required to test governed transport to and from an addressed neural micro-node. It does **not** claim that software can identify arbitrary neural targets, read thoughts, write semantic content, or establish safe human stimulation parameters.

A real adapter owns the mapping between its modality and these normalized variables. StegCore owns only the governance semantics around whether sufficient physical evidence exists to permit a modeled transition.

## Physical topology

```text
external/source state
  -> encoder / waveform constructor
  -> transducer or electrode interface
  -> physical channel
  -> bounded neural target
  -> biological response
  -> sensor / acquisition interface
  -> signal conditioning
  -> decoder / observation adapter
  -> bounded receiver observation
```

For outbound read paths, information flow begins with target activity and travels through the acquisition path. For inbound write paths, information flow begins with a proposed consequence and travels through the stimulation path. A bidirectional adapter may support both, but the two directions have separate calibration and evidence requirements.

## Addressing

A `receiver_locator` is an adapter-defined locator, not a universal brain address. Its validity depends on the adapter profile and empirical calibration. The model requires:

- target resolved;
- target not ambiguous;
- locator profile match;
- calibration present and valid;
- targeting confidence at or above the transition's declared minimum.

Failure of any of these conditions is fail-closed.

## Normalized physical variables

The software model deliberately uses dimensionless normalized quantities instead of biological dosage instructions:

- `targeting_confidence` in `[0,1]`;
- `coupling_quality` in `[0,1]`;
- `transfer_efficiency` in `[0,1]`;
- `noise_fraction` in `[0,1]`;
- `observation_quality` in `[0,1]`;
- `normalized_intensity` in `[0,1]`, where `1.0` means the maximum **adapter-declared governed envelope**, not a universal safe human value;
- `latency_ms` as measured/declared adapter latency.

A real adapter MUST define how physical units map to the normalized governed envelope and MUST establish that mapping outside StegCore using appropriate empirical, engineering, clinical, and regulatory evidence.

## Write-path transfer model

For a modeled inbound physical consequence:

```text
physical_delivery_score =
    targeting_confidence
  * coupling_quality
  * transfer_efficiency
  * (1 - noise_fraction)
```

This is a deterministic conformance metric, not a biophysical neural-response equation. It answers only whether the adapter-declared physical channel evidence satisfies the transition's minimum delivery threshold.

A write attempt is eligible only if:

1. target is resolved and unambiguous;
2. calibration is valid;
3. a safe-envelope declaration is available;
4. requested normalized intensity is within that declared envelope;
5. latency/freshness is within the packet limit;
6. delivery score meets the transition minimum;
7. full StegGate governance independently returns ALLOW;
8. commit coherence independently returns ALLOW.

Physical eligibility never grants execution authority by itself.

## Read-path observation model

For modeled neural -> external observation:

```text
observation_score =
    targeting_confidence
  * coupling_quality
  * transfer_efficiency
  * (1 - noise_fraction)
  * sensor_quality
```

Again, this is a conformance score. It does not establish semantic accuracy, subjective meaning, intent, consent, or authorization. The resulting observation is passed to `neural_micronode.py`, which translates only transition-relative assertions with provenance.

## Bidirectional state machine

```text
UNRESOLVED
  -> CALIBRATED
  -> PRE_OBSERVED
  -> GOVERNANCE_PENDING
  -> ADMITTED | REFUSED | FAIL_CLOSED
  -> PHYSICAL_CONSEQUENCE (only if admitted + coherent)
  -> POST_OBSERVED
  -> RECEIPT
```

If post-consequence observation is unavailable, the receipt must state that explicitly. Absence of observation must never be rewritten as success.

## Failure classes

Physical-layer fail-closed reasons include:

- `PHYSICAL_TARGET_UNRESOLVED`
- `PHYSICAL_TARGET_AMBIGUOUS`
- `PHYSICAL_CALIBRATION_MISSING`
- `PHYSICAL_CALIBRATION_INVALID`
- `PHYSICAL_SAFE_ENVELOPE_UNAVAILABLE`
- `PHYSICAL_INTENSITY_OUT_OF_ENVELOPE`
- `PHYSICAL_TARGETING_CONFIDENCE_LOW`
- `PHYSICAL_CHANNEL_QUALITY_LOW`
- `PHYSICAL_LATENCY_EXCEEDED`
- `PHYSICAL_OBSERVATION_QUALITY_LOW`

These are evidence failures. They are not medical diagnoses and do not state that a biological effect did or did not occur.

## Scientific grounding and limitation

Current neural-interface engineering demonstrates recording and stimulation through multiple invasive and non-invasive modalities. Intracortical BCIs classically separate sensor, decoder, and effector; bidirectional interfaces combine recording with stimulation. Emerging low-intensity focused ultrasound work demonstrates targeted non-invasive neuromodulation and emphasizes the importance of targeting, beamforming, tissue-dependent propagation, and monitoring. Those capabilities justify modeling sensor, decoder, channel, targeting, stimulation, and feedback as separate surfaces.

They do **not** justify assuming a universal neural packet transport layer or universal mapping from an information object to a neural state. Consequently this model is intentionally adapter-neutral and fail-closed.

## Real-adapter conformance boundary

A future hardware adapter must supply, at minimum:

```text
adapter_profile
modality
receiver_locator + locator_profile
calibration_ref + calibration validity
physical-unit -> normalized-envelope mapping
targeting confidence evidence
coupling / transfer evidence
noise / interference estimate
latency evidence
sensor observation quality
stimulation consequence class
post-consequence observation capability
```

Until such an adapter exists with empirical evidence, StegCore can validate governance and deterministic channel semantics only. `software_model_validated != biological_transport_activated`.
