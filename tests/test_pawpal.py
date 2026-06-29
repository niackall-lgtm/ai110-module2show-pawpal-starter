"""Tests for PawPal+.

Covers scheduling behavior (priority ordering, time-fitting, no overlap) and
the Phase 2 task-tracking behaviors (mark_complete, Pet.add_task).

Run with:  python -m pytest
"""

import pytest

from pawpal_system import (
    Owner,
    Pet,
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


class TestTaskCompletion:
    def test_mark_complete_changes_status(self):
        task = make_task()
        assert task.completed is False
        task.mark_complete()
        assert task.completed is True


class TestTaskAddition:
    def test_adding_task_increases_pet_task_count(self):
        pet = Pet(name="Biscuit", species="dog")
        assert len(pet.tasks) == 0
        pet.add_task(make_task("Morning walk"))
        assert len(pet.tasks) == 1
        pet.add_task(make_task("Feeding", 10, Priority.HIGH))
        assert len(pet.tasks) == 2


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

    def test_build_plan_pulls_from_owner_pets(self):
        owner = Owner(name="Jordan", available_minutes=120)
        pet = Pet(name="Biscuit", species="dog")
        pet.add_task(make_task("Walk", 30, Priority.HIGH))
        owner.add_pet(pet)
        plan = Scheduler(owner).build_plan()  # no explicit tasks -> uses owner's pets
        assert len(plan.scheduled) == 1
        assert plan.scheduled[0].task.title == "Walk"
