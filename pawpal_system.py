"""PawPal+ core system.

This module holds the *logic* for PawPal+ (no Streamlit code here).
It is intentionally a set of STUBS: the class shapes and method signatures
are defined, but the bodies raise NotImplementedError. Your job is to fill
them in, one small step at a time, with tests backing each behavior.

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
        raise NotImplementedError


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

    def __post_init__(self) -> None:
        """Validate the task (e.g. duration must be positive)."""
        raise NotImplementedError


@dataclass
class Pet:
    """The pet the tasks are for."""

    name: str
    species: str  # "dog" | "cat" | "other"


@dataclass
class Owner:
    """The pet owner and their scheduling preferences."""

    name: str
    # e.g. total minutes the owner has available today
    available_minutes: int = 120


@dataclass
class ScheduledItem:
    """One task placed at a specific time in the day's plan."""

    task: Task
    start_minute: int  # minutes since start of the planning window (e.g. 0 == 08:00)

    @property
    def end_minute(self) -> int:
        """When this item finishes."""
        raise NotImplementedError


@dataclass
class Plan:
    """The result of scheduling: chosen tasks + the ones that didn't fit."""

    scheduled: list[ScheduledItem] = field(default_factory=list)
    skipped: list[Task] = field(default_factory=list)

    def explain(self) -> str:
        """Return a human-readable explanation of why the plan looks like it does."""
        raise NotImplementedError


class Scheduler:
    """Turns a list of tasks + constraints into a Plan.

    This is the heart of the project. Start simple (sort by priority,
    fit tasks until time runs out) and add smarter behavior incrementally.
    """

    def __init__(self, owner: Owner, day_start_minute: int = 0) -> None:
        self.owner = owner
        self.day_start_minute = day_start_minute

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order tasks before placing them (e.g. high priority first)."""
        raise NotImplementedError

    def build_plan(self, tasks: list[Task]) -> Plan:
        """Place tasks into the day, respecting the owner's available time.

        Tasks that don't fit go into Plan.skipped.
        """
        raise NotImplementedError
