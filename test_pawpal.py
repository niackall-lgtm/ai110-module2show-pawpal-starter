"""Tests for PawPal+ scheduling behavior.

These are STARTER tests with the most important behaviors sketched out.
Several are marked xfail/skip until you implement the logic. As you fill in
pawpal_system.py, remove the markers and make each test pass.

Run with:  pytest        (or: pytest --cov)
"""

import pytest

from pawpal_system import (
    Owner,
    Plan,
    Priority,
    Scheduler,
    Task,
)


def make_task(title="Walk", minutes=20, priority=Priority.MEDIUM):
    return Task(title=title, duration_minutes=minutes, priority=priority)


class TestTask:
    def test_rejects_nonpositive_duration(self):
        with pytest.raises(ValueError):
            Task(title="bad", duration_minutes=0, priority=Priority.LOW)


class TestPriority:
    def test_from_str(self):
        assert Priority.from_str("high") == Priority.HIGH
        assert Priority.from_str("low") == Priority.LOW


class TestScheduler:
    def test_high_priority_scheduled_first(self):
        owner = Owner(name="Jordan", available_minutes=60)
        tasks = [
            make_task("Low task", 20, Priority.LOW),
            make_task("High task", 20, Priority.HIGH),
        ]
        plan = Scheduler(owner).build_plan(tasks)
        # The first scheduled item should be the high-priority task.
        assert plan.scheduled[0].task.title == "High task"

    def test_tasks_that_dont_fit_are_skipped(self):
        owner = Owner(name="Jordan", available_minutes=30)
        tasks = [make_task("A", 20), make_task("B", 20)]
        plan = Scheduler(owner).build_plan(tasks)
        assert len(plan.scheduled) == 1
        assert len(plan.skipped) == 1

    def test_no_time_overlap(self):
        owner = Owner(name="Jordan", available_minutes=120)
        tasks = [make_task("A", 30), make_task("B", 30)]
        plan = Scheduler(owner).build_plan(tasks)
        # Each item should start when the previous one ends (no overlap).
        for earlier, later in zip(plan.scheduled, plan.scheduled[1:]):
            assert later.start_minute >= earlier.end_minute

    def test_empty_task_list_gives_empty_plan(self):
        plan = Scheduler(Owner(name="Jordan")).build_plan([])
        assert plan.scheduled == []
        assert plan.skipped == []
