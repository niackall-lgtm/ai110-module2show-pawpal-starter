"""PawPal+ core system.

This module holds the *logic* for PawPal+ (no Streamlit code here).
It defines the core entities (Owner, Pet, Task, Priority) and the Scheduler
that turns an owner's tasks into a daily Plan, respecting available time and
task priority. Behavior is verified by the suite in tests/test_pawpal.py.

Workflow reminder (see README):
  1. Draft UML  ->  2. Class stubs (this file)  ->  3. Implement logic
  ->  4. Tests  ->  5. Wire into app.py  ->  6. Update UML
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from enum import Enum
from typing import Optional


class Priority(Enum):
    """Task priority. Higher value = more important."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3

    @classmethod
    def from_str(cls, label: str) -> "Priority":
        """Convert 'low'/'medium'/'high' (as the UI sends) into a Priority."""
        try:
            return cls[label.strip().upper()]
        except KeyError as exc:
            raise ValueError(f"Unknown priority: {label!r}") from exc


@dataclass
class Task:
    """A single pet-care task to potentially schedule.

    Attributes:
        title: Human-readable name, e.g. "Morning walk".
        duration_minutes: How long the task takes.
        priority: How important the task is.
        time: Time of day the task should happen, in "HH:MM" 24h format.
        frequency: How often it repeats: "daily" | "weekly" | "once".
        completed: Whether the task has been done.
        due_date: The calendar date the task is due (used for recurrence).
    """

    title: str
    duration_minutes: int
    priority: Priority
    time: str = "08:00"
    frequency: str = "daily"  # e.g. "daily" | "weekly" | "once"
    completed: bool = False
    due_date: Optional[date] = None

    def __post_init__(self) -> None:
        """Validate the task (e.g. duration must be positive)."""
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def next_occurrence(self) -> Optional["Task"]:
        """Return a fresh, uncompleted copy due on the next date, or None if one-off.

        Uses timedelta to advance the due date: +1 day for "daily", +7 for "weekly".
        """
        step = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}.get(self.frequency)
        if step is None:
            return None  # "once" tasks do not recur
        base = self.due_date or date.today()
        return replace(self, completed=False, due_date=base + step)


@dataclass
class Pet:
    """The pet the tasks are for, plus the tasks that belong to it."""

    name: str
    species: str  # "dog" | "cat" | "other"
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)


@dataclass
class Owner:
    """The pet owner: their pets and their scheduling preferences."""

    name: str
    # e.g. total minutes the owner has available today
    available_minutes: int = 120
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Collect every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


@dataclass
class ScheduledItem:
    """One task placed at a specific time in the day's plan."""

    task: Task
    start_minute: int  # minutes since start of the planning window (e.g. 0 == 08:00)

    @property
    def end_minute(self) -> int:
        """When this item finishes."""
        return self.start_minute + self.task.duration_minutes


@dataclass
class Plan:
    """The result of scheduling: chosen tasks + the ones that didn't fit."""

    scheduled: list[ScheduledItem] = field(default_factory=list)
    skipped: list[Task] = field(default_factory=list)

    def explain(self) -> str:
        """Return a human-readable explanation of why the plan looks like it does."""
        lines = []
        for item in self.scheduled:
            lines.append(
                f"Scheduled '{item.task.title}' at minute {item.start_minute} "
                f"({item.task.duration_minutes} min, priority {item.task.priority.name})."
            )
        for task in self.skipped:
            lines.append(
                f"Skipped '{task.title}' ({task.duration_minutes} min) — not enough time left."
            )
        return "\n".join(lines) if lines else "No tasks to plan."


class Scheduler:
    """Turns a list of tasks + constraints into a Plan.

    This is the heart of the project. Start simple (sort by priority,
    fit tasks until time runs out) and add smarter behavior incrementally.
    """

    def __init__(self, owner: Owner, day_start_minute: int = 0) -> None:
        self.owner = owner
        self.day_start_minute = day_start_minute

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order tasks before placing them (highest priority first)."""
        return sorted(tasks, key=lambda t: t.priority.value, reverse=True)

    def build_plan(self, tasks: Optional[list[Task]] = None) -> Plan:
        """Place tasks into the day, respecting the owner's available time.

        If no tasks are given, pulls every task from the owner's pets.
        Tasks that don't fit go into Plan.skipped.
        """
        if tasks is None:
            tasks = self.owner.get_all_tasks()

        plan = Plan()
        current = self.day_start_minute
        end_of_day = self.day_start_minute + self.owner.available_minutes

        for task in self.sort_tasks(tasks):
            if current + task.duration_minutes <= end_of_day:
                plan.scheduled.append(ScheduledItem(task=task, start_minute=current))
                current += task.duration_minutes
            else:
                plan.skipped.append(task)
        return plan

    # --- Phase 4: algorithmic layer -------------------------------------

    def sort_by_time(self, tasks: Optional[list[Task]] = None) -> list[Task]:
        """Return tasks in chronological order by their "HH:MM" time string.

        "HH:MM" strings sort correctly with plain string comparison because the
        zero-padded, fixed-width format is lexicographically ordered.
        """
        if tasks is None:
            tasks = self.owner.get_all_tasks()
        return sorted(tasks, key=lambda t: t.time)

    def filter_by_status(self, completed: bool, tasks: Optional[list[Task]] = None) -> list[Task]:
        """Return only the tasks whose completion status matches `completed`."""
        if tasks is None:
            tasks = self.owner.get_all_tasks()
        return [t for t in tasks if t.completed == completed]

    def filter_by_pet(self, pet_name: str) -> list[Task]:
        """Return all tasks belonging to the pet with the given name."""
        return [
            task
            for pet in self.owner.pets
            if pet.name.lower() == pet_name.lower()
            for task in pet.tasks
        ]

    def detect_conflicts(self, tasks: Optional[list[Task]] = None) -> list[str]:
        """Return warning strings for any tasks sharing the same time slot.

        Lightweight strategy: group by the "HH:MM" time and warn on any slot
        with more than one task. Returns messages instead of raising, so the
        caller (CLI or UI) can surface them gracefully.
        """
        if tasks is None:
            tasks = self.owner.get_all_tasks()

        by_time: dict[str, list[Task]] = {}
        for task in tasks:
            by_time.setdefault(task.time, []).append(task)

        warnings = []
        for time_slot, group in sorted(by_time.items()):
            if len(group) > 1:
                titles = ", ".join(t.title for t in group)
                warnings.append(f"⚠️ Conflict at {time_slot}: {titles}")
        return warnings

    def complete_and_reschedule(self, pet: Pet, task: Task) -> Optional[Task]:
        """Mark a task complete and, if it recurs, add its next occurrence to the pet.

        Returns the newly created task, or None for one-off tasks.
        """
        task.mark_complete()
        upcoming = task.next_occurrence()
        if upcoming is not None:
            pet.add_task(upcoming)
        return upcoming
