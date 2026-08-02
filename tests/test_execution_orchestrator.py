from stegcore.execution_orchestrator import Task, TaskState, classify_task, derive_execution_state


def task(
    task_id: str = "A",
    dependencies: tuple[str, ...] = (),
    resolver: str = "repository_workflow",
    authority_required: bool = False,
) -> Task:
    return Task(
        task_id=task_id,
        repository="org/repo",
        issue="org/repo#1",
        workflow=".github/workflows/example.yml",
        evidence_path="data/example.json",
        stop_condition={"status": "PASS"},
        dependencies=dependencies,
        resolver=resolver,
        successor=None,
        retry_policy="hourly",
        authority_required=authority_required,
    )


def test_complete_when_condition_matches() -> None:
    assert classify_task(task(), {"status": "PASS"}, [], True) == TaskState.COMPLETE


def test_observation_blocked_is_not_failure() -> None:
    assert classify_task(task(), None, [], False) == TaskState.OBSERVATION_BLOCKED


def test_dependency_wait_does_not_halt_graph() -> None:
    state = derive_execution_state(
        [task("A"), task("B", ("A",))],
        {"A": {"status": "FAIL"}, "B": {"status": "PASS"}},
    )
    assert state["development_halt"] is False
    assert [record["state"] for record in state["tasks"]] == [
        "RESOLVING",
        "WAITING_FOR_EVIDENCE",
    ]


def test_authority_wait_is_explicit() -> None:
    assert (
        classify_task(task(authority_required=True), {"status": "FAIL"}, [], True)
        == TaskState.WAITING_FOR_AUTHORITY
    )


def test_independent_branch_can_complete() -> None:
    state = derive_execution_state(
        [task("A"), task("B")],
        {"A": {"status": "FAIL"}, "B": {"status": "PASS"}},
    )
    assert [record["state"] for record in state["tasks"]] == [
        "RESOLVING",
        "COMPLETE",
    ]
