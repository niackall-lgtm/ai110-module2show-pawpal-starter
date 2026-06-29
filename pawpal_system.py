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

from dataclasses import dataclass, field
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
    """

    title: str
    duration_minutes: int
    priority: Priority
    frequency: str = "daily"  # e.g. "daily" | "weekly" | "once"
    completed: bool = False

    def __post_init__(self) -> None:
        """Validate the task (e.g. duration must be positive)."""
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True


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
