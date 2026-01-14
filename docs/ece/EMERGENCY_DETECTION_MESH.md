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
```

## Redundancy & Anti-Manipulation
- Require N-of-M independent sources for promotion to `critical`.
- Penalize correlated sources (same upstream).
- Track source reliability over time.
- Detect spoofing patterns; if suspected, downgrade confidence and require `defer`.

## Operating Modes
- `watch`: increase sampling; no emergency execution
- `alert`: stage simulation resources; pre-warm compute pools (non-emergency budgets)
- `critical`: allow ECE activation (if StegCore approves)
- `catastrophic`: allow broader ECE classes (still bounded)

## Rate & Cost Controls
EDM must be cheap to run:
- lightweight detectors run frequently
- expensive modeling triggers only when thresholds are met

## Hand-off to MPSS
When EDM proposes `critical` or higher, it must provide:
- scenario seed parameters
- known constraints (comms loss, infrastructure)
- uncertainty map (what is not known)

## Logging
- All signals and fusion decisions must be logged with reason codes.
- Sensitive inputs must be redacted in public logs; full logs kept in secure audit store.
