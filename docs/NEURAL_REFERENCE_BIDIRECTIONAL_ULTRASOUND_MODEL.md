# Reference Bidirectional Ultrasound Neural Transceiver Model

Status: research/reference physical architecture for `STEGCORE-NEURAL-ENDTOEND-002`; not a medical-device design or activation claim.

## Why a reference modality is needed

The generic physical-channel abstraction is sufficient to test governance semantics, but not sufficient to answer whether there is a plausible physical transmit/receive architecture. This document therefore instantiates the abstraction against a concrete non-invasive research candidate: ultrasound-based read and write paths.

The reference combines two distinct physical capabilities that must never be conflated:

- **READ:** ultrasound-based acquisition / functional ultrasound imaging or another adapter-supported ultrasonic observation path;
- **WRITE:** low-intensity focused ultrasound neuromodulation or another adapter-supported focused ultrasonic stimulation path.

The fact that both use ultrasound does not make them the same transducer mode, calibration, biological observable, semantic channel, or authority surface.

## Reference hardware surfaces

A complete bidirectional research transceiver would require at minimum:

```text
structural co-registration / target map
        |
        v
adapter-defined neural target locator
        |
        +--------------------+
        |                    |
        v                    v
READ PATH                WRITE PATH
receive array            transmit array / shared capable array
acquisition timing       waveform / pulse-sequence constructor
receive beamforming      transmit beamforming
signal conditioning      target/focus control
motion correction        skull/tissue transfer compensation
feature extraction       envelope / interlock enforcement
observation adapter      consequence adapter
        |                    |
        +--------+-----------+
                 v
        synchronized governance boundary
                 |
        pre/post observation + receipts
```

A practical device could share physical elements, but StegCore treats the logical surfaces independently so a capability on one path cannot silently imply capability on the other.

## Address model

The receiver is represented as a bounded target volume rather than a universal symbolic brain address.

```text
TargetVolume = {
  locator_profile,
  structural_map_ref,
  target_ref,
  spatial_extent_ref,
  registration_ref,
  targeting_uncertainty,
  calibration_ref
}
```

The `target_ref` is meaningful only under the named structural map, registration, adapter profile, and calibration. A packet addressed to a target cannot be replayed onto another subject/session/device merely because a string locator matches.

## Read-path physical model

Let:

- `x(t)` be an unknown local biological state or proxy state;
- `H_r(theta_r, target)` be the calibrated receive transfer operator;
- `n_r(t)` be measurement noise/interference;
- `y_r(t)` be acquired physical data;
- `D_r` be the adapter's bounded observation mapping.

The reference model is:

```text
y_r(t) = H_r(theta_r, target) [x(t)] + n_r(t)
observation = D_r(y_r, calibration, provenance)
```

StegCore never assumes that `D_r(y_r)` equals thought, meaning, intent, consent, or authorization. It produces only bounded assertions permitted by the neural micro-node packet.

A conforming READ adapter must report at least:

- target/registration identity;
- acquisition calibration identity;
- receive transfer-quality estimate;
- noise/interference estimate;
- observation latency;
- observation quality/uncertainty;
- mapping/decoder identity;
- raw-observation commitment or reference;
- derived assertion provenance.

## Write-path physical model

Let:

- `u(t)` be the adapter-generated physical drive signal inside its externally established governed envelope;
- `H_w(theta_w, target)` be the calibrated transmit/focus transfer operator;
- `e(target,t)` be physical exposure/coupling at the target;
- `B` be the unknown biological response operator.

The reference model is:

```text
e(target,t) = H_w(theta_w, target) [u(t)]
x_after = B(x_before, e, biological_context)
```

StegCore may govern evidence about `u`, `H_w`, target identity, envelope compliance, and post-observation. It does **not** claim to know `B` generically. Therefore:

```text
physical_focus_established != desired_neural_state_established
stimulation_delivered != semantic_content_delivered
```

A real WRITE adapter must report at least:

- target/registration identity;
- transmit calibration identity;
- transfer/focus-quality estimate;
- adapter-defined physical-unit to governed-envelope mapping;
- interlock/envelope status;
- requested consequence class;
- measured or estimated delivery evidence;
- latency;
- post-consequence observation capability and result when available.

## Round-trip model

The minimum bidirectional closed-loop cycle is:

```text
1. Resolve target volume.
2. Establish session/device calibration.
3. READ pre-state / receiver evidence.
4. Construct candidate + minimal governance packet.
5. Evaluate neural evidence boundary.
6. Evaluate physical WRITE eligibility.
7. Evaluate full canonical StegGate request.
8. Evaluate independent commit coherence.
9. Only then permit WRITE-path consequence.
10. READ post-state when technically available.
11. Compare pre/post observations without claiming semantic equivalence.
12. Emit a receipt binding all decision and physical-evidence hashes.
```

For neural -> external action, READ occurs before candidate construction and the resulting decoded candidate still proceeds through separate authorization, admissibility, and commit boundaries.

## Calibration domains

The reference architecture requires distinct calibration evidence for:

- structural registration;
- transmit focusing / propagation;
- receive acquisition / propagation;
- transducer/device state;
- session state;
- decoder/observation mapping.

A calibration reference is scoped. A receive calibration cannot satisfy a transmit requirement unless the adapter contract explicitly proves equivalence.

## What can be simulated now

StegCore can deterministically simulate and test:

- target-resolution gates;
- calibration presence/validity;
- normalized transfer/coupling/noise constraints;
- separate READ and WRITE eligibility;
- candidate binding;
- full StegGate predicates;
- commit coherence;
- modeled consequence reachability;
- pre/post observation receipt structure.

## What cannot be activated without hardware evidence

The following remain blocked until a real adapter/device supplies empirical evidence:

- actual transcranial target localization accuracy;
- actual subject-specific acoustic propagation;
- actual receive signal sensitivity/specificity;
- actual neuromodulatory response;
- actual physical-unit safety envelope;
- actual semantic encoding/decoding;
- actual post-stimulation biological outcome.

This is deliberate. The reference model answers **what physical system would have to exist and what evidence it would have to expose** before StegGate could govern it. It does not pretend that the device already exists as a StegVerse-controlled neural transceiver.
