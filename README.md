# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## ✨ Features

PawPal+ represents owners, pets, and tasks as Python objects and applies simple
algorithms to plan a pet owner's day:

- **Priority-based day plan** — fits the most important tasks into the owner's available time (`Scheduler.build_plan`).
- **Sorting by time of day** — orders tasks chronologically by their `HH:MM` time (`Scheduler.sort_by_time`).
- **Filtering** — by completion status (`Scheduler.filter_by_status`) or by pet (`Scheduler.filter_by_pet`).
- **Conflict warnings** — flags tasks scheduled at the same time instead of crashing (`Scheduler.detect_conflicts`).
- **Recurring tasks** — completing a daily/weekly task auto-creates its next occurrence (`Scheduler.complete_and_reschedule` + `Task.next_occurrence`).

## 🖥️ Sample Output

Output from running `python main.py`:

```
Today's Schedule for Jordan (60 min available)
====================================================
  08:00 — Evening walk (30 min) [priority: high]
  08:30 — Morning walk (30 min) [priority: high]

Didn't fit today:
  - Feeding (10 min)
  - Litter cleanup (15 min)
  - Play time (20 min)

All tasks sorted by time of day:
  08:00 — Morning walk
  08:00 — Feeding
  12:00 — Litter cleanup
  15:00 — Play time
  18:00 — Evening walk

Biscuit's tasks (filter_by_pet):
  18:00 — Evening walk
  08:00 — Morning walk
  08:00 — Feeding

Conflict check:
  ⚠️ Conflict at 08:00: Morning walk, Feeding

Recurring task demo:
  Before: 'Feeding' completed=False, Biscuit has 3 tasks
  After completing it: completed=True, Biscuit has 4 tasks
  Auto-created next occurrence due 2026-06-29
```

The `build_plan` scheduler packs tasks by priority into the available time, while
`sort_by_time`, `detect_conflicts`, and the recurrence logic operate on each
task's time-of-day and frequency.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_tasks`, `Scheduler.sort_by_time` | By priority for the day plan; chronologically (`HH:MM`) for the timeline |
| Filtering | `Scheduler.filter_by_status`, `Scheduler.filter_by_pet` | Skip tasks that don't fit available time; filter by done/not-done or by pet |
| Conflict handling | `Scheduler.detect_conflicts` | Groups tasks by time slot; returns warning strings for same-time collisions |
| Recurring tasks | `Scheduler.complete_and_reschedule`, `Task.next_occurrence` | Daily = +1 day, weekly = +7 days via `timedelta`; "once" tasks don't recur |

## 🧪 Testing PawPal+

Run the test suite from the project root:

```bash
python -m pytest          # run all tests
python -m pytest --cov    # with coverage
```

The suite (in `tests/test_pawpal.py`) covers:

- **Task & Priority** — duration validation, `Priority.from_str`, `mark_complete`
- **Pet & Owner** — `add_task` increases task count, `get_all_tasks` across pets
- **Scheduler day plan** — priority ordering, time-fitting/skip, no overlaps
- **Sorting** — `sort_by_time` returns chronological order
- **Filtering** — by completion status and by pet
- **Recurrence** — completing a daily task creates a next-day task; one-off tasks don't recur
- **Conflict detection** — same-time tasks are flagged, different times are not
- **Edge cases** — empty task list, pet with no tasks

Successful run:

```
============================= test session starts ==============================
platform darwin -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
collected 17 items

tests/test_pawpal.py .................                                   [100%]

============================== 17 passed in 0.02s ==============================
```

**Confidence level: ★★★★☆ (4/5).** All core behaviors and key edge cases pass.
Held back one star because conflict detection only catches exact same-time
collisions (not partial duration overlaps), which would be the next thing to test.

## 📸 Demo Walkthrough

PawPal+ runs as a Streamlit web app. Start it with:

```bash
streamlit run app.py
```

**Main UI features / actions a user can perform:**

1. **Set owner details** in the sidebar (name + minutes available today).
2. **Add a pet** (name + species) — creates a `Pet` object stored in `st.session_state`.
3. **Add a task** for a chosen pet (title, duration, time, priority, frequency) — calls `Pet.add_task`.
4. **View today's plan** — the app builds and displays the schedule automatically.

**Example workflow:** add a pet (Biscuit the dog) → add a task (Morning walk at 08:00, high priority) → add another task at the same time → view today's plan, where the app shows the priority-ordered schedule, the by-time timeline, and a ⚠️ conflict warning.

**Key Scheduler behaviors shown in the UI:**

- Priority-based plan rendered with `st.table` (plus tasks that didn't fit).
- A time-of-day timeline using `sort_by_time`.
- Conflict warnings surfaced with `st.warning`; a green `st.success` when there are none.

**Sample CLI output** from `python main.py` is in the [Sample Output](#️-sample-output) section above.
