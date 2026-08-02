from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable


class TaskState(str, Enum):
    RUNNABLE = "RUNNABLE"
    WAITING_FOR_EVIDENCE = "WAITING_FOR_EVIDENCE"
    WAITING_FOR_AUTHORITY = "WAITING_FOR_AUTHORITY"
    OBSERVATION_BLOCKED = "OBSERVATION_BLOCKED"
    RESOLVING = "RESOLVING"
    COMPLETE = "COMPLETE"
    DENIED = "DENIED"


@dataclass(frozen=True)
class Task:
    task_id: str
    repository: str
    issue: str
    workflow: str
    evidence_path: str
    stop_condition: dict[str, Any]
    dependencies: tuple[str, ...] = ()
    resolver: str = "repository_workflow"
    successor: str | None = None
    retry_policy: str = "hourly"
    authority_required: bool = False


def condition_matches(value: dict[str, Any], condition: dict[str, Any]) -> bool:
    return all(value.get(key) == expected for key, expected in condition.items())


def classify_task(
    task: Task,
    evidence: dict[str, Any] | None,
    dependency_states: Iterable[TaskState],
    observation_available: bool,
) -> TaskState:
    dependencies = tuple(dependency_states)
    if any(state == TaskState.DENIED for state in dependencies):
        return TaskState.DENIED
    if any(state != TaskState.COMPLETE for state in dependencies):
        return TaskState.WAITING_FOR_EVIDENCE
    if not observation_available:
        return TaskState.OBSERVATION_BLOCKED
    if evidence is not None and condition_matches(evidence, task.stop_condition):
        return TaskState.COMPLETE
    if task.authority_required:
        return TaskState.WAITING_FOR_AUTHORITY
    if task.resolver:
        return TaskState.RESOLVING
    return TaskState.RUNNABLE


def derive_execution_state(tasks: list[Task], observations: dict[str, dict[str, Any] | None]) -> dict[str, Any]:
    states: dict[str, TaskState] = {}
    task_records: list[dict[str, Any]] = []
    for task in tasks:
        dependency_states = [states.get(dep, TaskState.WAITING_FOR_EVIDENCE) for dep in task.dependencies]
        evidence = observations.get(task.task_id)
        state = classify_task(task, evidence, dependency_states, task.task_id in observations)
        states[task.task_id] = state
        task_records.append({
            "task_id": task.task_id,
            "repository": task.repository,
            "issue": task.issue,
            "workflow": task.workflow,
            "evidence_path": task.evidence_path,
            "state": state.value,
            "stop_condition": task.stop_condition,
            "dependencies": list(task.dependencies),
            "resolver": task.resolver,
            "successor": task.successor,
            "retry_policy": task.retry_policy,
            "development_halt": False,
        })
    return {
        "state": "COMPLETE" if all(v == TaskState.COMPLETE for v in states.values()) else "ACTIVE",
        "development_halt": False,
        "continuation_mode": "ADVANCE_INDEPENDENT_RUNNABLE_BRANCHES",
        "tasks": task_records,
        "authority": {"execution": False, "publication": False, "release": False, "live": False},
    }
