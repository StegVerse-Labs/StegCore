# HIL Non-Halting Coordination Protocol

## Rule

There are no external HIL tasks. Every unresolved condition is classified as one of:

1. observable internal work;
2. internal observation gap;
3. internal implementation tranche;
4. internal evidence-import tranche;
5. internal authorization gate.

None of these states permits development to stop at a status report.

## Task locations

| Task | Authoritative location | Work that continues before final evidence |
|---|---|---|
| Hosted receiver and durable controlled cycle | `StegVerse-Labs/Site#81` | deployment-profile validation, readiness fixtures, evidence packet validation, restart-cycle runner, managed deployment-path selection |
| TVC lifecycle and private review | `StegVerse-Labs/TVC#8` | lifecycle schema, write-once review validator, replay/substitution tests, Site projection receipt fixture |
| Master Record candidate | `master-records/orchestration#13` | candidate schema, deterministic canonicalization, negative tests, validation-only result fixture |
| Participant lifecycle projection | `StegVerse-Labs/Site#67` | stable response projection, private-review view, candidate-state view, browser/accessibility validation |
| Cross-repository activation | `StegVerse-Labs/StegCore#41` | state contract, monotonic transition validator, contradiction detection, action queue, activation-decision fixture |

## Observer

The authoritative registry is:

`data/hil-lifecycle-task-registry.json`

The observer and action selector is:

`scripts/coordinate_hil_lifecycle.py`

The scheduled execution surface is:

`.github/workflows/coordinate-hil-lifecycle.yml`

Every generated action contains the exact repository and issue location. An unavailable observation produces `ACTIONABLE_INTERNAL_OBSERVATION_GAP`, not `BLOCKED_EXTERNAL` or `WAITING`.

## Completion loop

For each scheduled or manually dispatched cycle:

1. observe every registered task;
2. verify its repository and issue location;
3. classify closed tasks as requiring completion-evidence validation;
4. classify open tasks as internal work;
5. classify inaccessible tasks as an internal observation gap;
6. select the next implementation, fixture, validator, observation, or evidence-import action;
7. emit `HIL-STEGVERSE-ACTION-QUEUE-v1`;
8. continue until the registry contains no open or actionable task;
9. only then emit `ARCHIVE_SESSION`.

## Prohibited halt states

The coordinator rejects:

- `external_tasks` containing any entry;
- `blocking: true` on a generated action;
- a task without an exact GitHub location;
- a status-only action with no executable next step;
- `ARCHIVE_SESSION` while any registered task is open, unobserved, or awaiting evidence validation.

## Authority boundary

The coordinator may observe, classify, validate, generate fixtures, and select internal work. It does not silently grant deployment, review, publication, release, or Master Record authority. Authorization gates remain internal tasks with exact locations and evidence requirements; they do not halt all other executable development.
