# Emergency Capital Envelopes (ECE)
Version: v0.1 (Draft)

## Purpose
Allow instant emergency financial transactions (e.g., compute acquisition) without real-time human review,
by using pre-funded, pre-authorized, machine-enforced corridors.

ECEs prevent AI financial sovereignty by constraining:
- what can be purchased,
- where it can be purchased,
- how much can be spent,
- for how long,
- and under which triggers.

## Core Rule
AI may execute emergency transactions only inside a verified ECE.
No ECE → no emergency spending.

## ECE Structure (Normative)
An ECE MUST specify:
- authorized entities
- trigger conditions
- allowed targets (vendor whitelist)
- allowed assets (asset whitelist)
- spend limits (rate + total)
- time bounds
- auto-shutdown conditions
- mandatory logging + receipts
- post-event review requirement

### Example ECE (Compute-Critical)
```
{
  "envelope_id": "ECE-COMPUTE-CRITICAL-v1",
  "authorized_entities": ["AI:OpsGuardian-001"],
  "trigger_conditions": [
    "emergency_state>=critical",
    "life_critical_task_active==true",
    "compute_shortfall==true"
  ],
  "spend_limits": {
    "max_per_minute_usd": 50000,
    "max_per_hour_usd": 300000,
    "max_total_usd": 1000000
  },
  "allowed_targets": [
    "aws",
    "gcp",
    "azure",
    "coreweave"
  ],
  "allowed_assets": [
    "compute_gpu",
    "compute_cpu",
    "temporary_storage",
    "network_bandwidth"
  ],
  "time_bound_minutes": 120,
  "post_event_review_required": true,
  "auto_shutdown_conditions": [
    "task_completed",
    "envelope_exhausted",
    "anomaly_detected",
    "time_expired",
    "human_terminate"
  ]
}
```

## Execution Semantics
	1.	Entity submits EmergencySpendIntent
	2.	StegCore verifies:
	•	emergency state
	•	envelope exists and is active
	•	actor is authorized
	•	trigger conditions satisfied
	•	request within asset/vendor whitelist
	•	request within rate + total limits
	3.	If allowed:
	•	transaction executes via escrow-backed mechanism
	•	receipts are emitted and sealed
	4.	Envelope decrements remaining capacity
	5.	Auto-shutdown triggers are continuously evaluated

### Spend Intents (Normative)

## All emergency spend requests MUST be explicit:
{
  "intent": "emergency_spend",
  "actor": "AI:OpsGuardian-001",
  "envelope_id": "ECE-COMPUTE-CRITICAL-v1",
  "vendor": "aws",
  "asset": "compute_gpu",
  "amount_usd": 25000,
  "justification": "MPSS burst required; comms routing model must complete in 60s",
  "event_id": "EDM-2026-00129"
}

Receipt Requirements

Every executed emergency spend MUST emit:
	•	envelope_id
	•	actor
	•	event_id
	•	vendor + asset
	•	amount
	•	timestamp
	•	StegCore decision record (allow/deny/defer + reason code)

Hard Prohibitions

ECEs MUST NOT allow:
	•	transfers to unknown recipients
	•	assets outside defined classes
	•	long-duration capital formation (land, equity, acquisitions)
	•	creation of new ECEs by AI

Large capital formation belongs to Capital Delegation Windows (CDW) and is never “emergency spend”.

Post-Event Review

Mandatory:
	•	verify all spends within envelope limits
	•	verify triggers were valid
	•	check for anomaly patterns
	•	revise thresholds and caps

  ---

# `EMERGENCY_DETECTION_MESH.md`

```md
# Emergency Detection Mesh (EDM)
Version: v0.1 (Draft)

## Purpose
Detect and classify emergencies quickly using redundant signals and multiple entities,
to reduce false positives and prevent single-point manipulation.

## Principles
- No single signal triggers an emergency alone.
- Multiple weak signals may combine into high-confidence detection.
- Detection must be explainable: show evidence and confidence bounds.
- The EDM proposes; StegCore decides.

## Inputs (Examples)
- Comms health: latency, packet loss, route instability
- Power grid: frequency drift, outage maps
- Sensor networks: seismic, weather, radiation, flood levels
- Healthcare load: EMS call volume, hospital capacity
- Cyber telemetry: DDoS signatures, auth anomalies
- Human reports: verified distress signals, official notices
- Satellite/public feeds: where permitted
- Internal health: service degradation, dependency failures

## Signal Fusion Output
EDM MUST output:
- event_id
- fused score (0..1)
- confidence interval
- estimated scope
- time-to-harm estimate
- evidence summary (non-sensitive)
- proposed emergency state (watch/alert/critical/catastrophic)

### Example Output
```json
{
  "event_id": "EDM-2026-00129",
  "fused_score": 0.91,
  "confidence": { "low": 0.86, "high": 0.94 },
  "estimated_scope": "regional",
  "time_to_harm_minutes": 12,
  "proposed_state": "critical",
  "evidence": [
    { "type": "comms", "metric": "packet_loss", "value": 0.38, "trend": "rising" },
    { "type": "power", "metric": "outage_reports", "value": "spike", "trend": "rising" },
    { "type": "human", "metric": "verified_distress", "value": 42, "trend": "rising" }
  ]
}

Redundancy & Anti-Manipulation
	•	Require N-of-M independent sources for promotion to critical.
	•	Penalize correlated sources (same upstream).
	•	Track source reliability over time.
	•	Detect spoofing patterns; if suspected, downgrade confidence and require defer.

Operating Modes
	•	watch: increase sampling; no emergency execution
	•	alert: stage simulation resources; pre-warm compute pools (non-emergency budgets)
	•	critical: allow ECE activation (if StegCore approves)
	•	catastrophic: allow broader ECE classes (still bounded)

Rate & Cost Controls

EDM must be cheap to run:
	•	lightweight detectors run frequently
	•	expensive modeling triggers only when thresholds are met

Hand-off to MPSS

When EDM proposes critical or higher, it must provide:
	•	scenario seed parameters
	•	known constraints (comms loss, infrastructure)
	•	uncertainty map (what is not known)

Logging
	•	All signals and fusion decisions must be logged with reason codes.
	•	Sensitive inputs must be redacted in public logs; full logs kept in secure audit store.
