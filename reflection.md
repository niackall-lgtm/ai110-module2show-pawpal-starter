# PawPal+ Project Reflection

## 1. System Design

Three core actions a user should be able to perform in PawPal+:

1. **Add a pet**: enter a pet's name and species so the app knows who the care tasks are for.
2. **Add a care task**:  create a task (e.g. "Morning walk") with a duration and a priority (low/medium/high).
3. **Generate today's plan**: given the owner's available time, produce a daily schedule that fits the most important tasks and shows which tasks didn't fit.

**a. Initial design**

My initial UML has seven classes:

- **Owner**: holds the owner's name and how many minutes they have available in a day. Represents the person and their scheduling constraint.
- **Pet**: holds the pet's name and species. Identifies who the tasks are for.
- **Task**: a single care task with a title, duration in minutes, and a priority. This is the unit the scheduler works with.
- **Priority**: an enumeration (LOW, MEDIUM, HIGH) used to rank tasks so the most important ones get placed first.
- **Scheduler**:the core logic. It sorts tasks by priority and fits them into the owner's available time, then produces a Plan.
- **ScheduledItem**: wraps a Task with a start time, representing one task placed in the day.
- **Plan**: the scheduler's output: a list of scheduled items plus a list of skipped tasks, and an `explain()` method to justify the result.

The main relationships are: an Owner has Pets, a Pet has Tasks, the Scheduler uses the Owner's constraints to turn Tasks into a Plan, and a Plan contains ScheduledItems (which each wrap a Task).

**b. Design changes**

Yes. My original UML (matching the starter stubs) showed how the objects were used together but never drew the ownership hierarchy. I added two relationships — `Owner --> Pet : has` and `Pet --> Task : has` — so the diagram reflects the real structure: an owner has pets, and a pet has the care tasks. This makes it clear where tasks come from before the Scheduler turns them into a Plan, instead of leaving that connection implied.

**AI review of the skeleton.** I asked my AI assistant to review `pawpal_system.py` for missing relationships and potential logic bottlenecks. Its main points:

- **`Scheduler.build_plan` carries too much responsibility.** All the real complexity (sorting, fitting tasks into available time, skip logic, and later conflict/recurring handling) is funneled into one method. As the algorithm grows, I should extract helpers like `fits_in_remaining_time()` and `detect_conflicts()`.
- **Code doesn't model Pet→Task yet.** Tasks are passed loose into `build_plan(tasks)`; the Pet class has no `tasks` list or `add_task()`. The diagram now shows the relationship, but the code is still a gap to close during implementation.
- **No overlap/conflict validation.** Time is stored as plain `int` minutes with nothing preventing two scheduled items from overlapping — conflict detection still needs to be added.
- **`Priority.from_str` raises on unknown input.** I need to decide how the UI should handle an invalid priority value.

I kept the current class shapes (they're clean and the dataclasses are appropriate) but noted these as work items for the implementation phase rather than redesigning the skeleton now.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers two main constraints. First, **time**: the owner has a fixed number of `available_minutes` in a day, and `build_plan` only schedules tasks that still fit in the remaining time, sending the rest to a `skipped` list. Second, **priority**: tasks are sorted HIGH → LOW before placement, so the most important tasks claim time first. I treated priority as the most important constraint because the whole point of the app is helping a busy owner make sure the *essential* care (walks, feeding, meds) happens even when there isn't time for everything.

**b. Tradeoffs**

One deliberate tradeoff is in **conflict detection**: `detect_conflicts` only flags tasks that share the *exact same* `HH:MM` start time, not tasks whose durations overlap (e.g. a 30-minute task at 08:00 and another at 08:15). I chose exact-match because it's simple, fast, and easy to reason about, and it catches the most common real mistake, which is accidentally scheduling two things for the same slot. Full interval-overlap detection would be more accurate but adds complexity (parsing times into minutes and comparing ranges) that isn't worth it for a first version aimed at a single busy owner. A second tradeoff: `build_plan` packs tasks back-to-back by priority and ignores each task's preferred time of day, so it optimizes for "fit the important things" over "honor the exact clock time."

---

## 3. AI Collaboration

**a. How you used AI**

I used my AI coding assistant across every phase: brainstorming the class design and generating the first Mermaid UML, scaffolding the dataclass stubs, implementing the algorithmic methods (sorting, filtering, recurrence, conflict detection), and drafting the pytest suite. The most helpful prompts were **specific and scoped**, like "how should the Scheduler retrieve all tasks from the Owner's pets?" and "how do I use `timedelta` to compute the next due date for a daily task?" Narrow questions produced answers I could drop in and verify, whereas vague ones produced over-engineered code.

**b. Judgment and verification**

I did not accept AI suggestions blindly. For example, when extending the classes for Phase 2's task-tracking model (`completed`, `frequency`, `mark_complete`), the straightforward AI suggestion was to *replace* the existing duration/priority-based `Task` and `Scheduler`. I rejected that because it would have broken the passing scheduler tests. Instead I **added** the new fields and methods on top of the existing design, keeping defaults so old call sites still worked. I verified every change the same way: by running `python main.py` (the CLI demo) and `python -m pytest` after each step, so behavior was confirmed by output and tests rather than by trusting the generated code.

---

## 4. Testing and Verification

**a. What you tested**

I tested: task validation and `Priority.from_str`; `mark_complete` flipping status; `Pet.add_task` increasing the task count; the day plan's priority ordering, time-fitting/skip behavior, and no-overlap guarantee; `sort_by_time` returning chronological order; filtering by status and by pet; recurrence (completing a daily task creates a next-day task, and one-off tasks don't recur); and conflict detection flagging same-time tasks. I also added edge cases — an empty task list and a pet with no tasks. These matter because they're exactly the behaviors a pet owner relies on, and the edge cases are where scheduling code usually breaks.

**b. Confidence**

I'm fairly confident, specifically 4 out of 5. All 17 tests pass and the CLI demo behaves as expected. If I had more time I'd test **partial-duration overlaps** (the case my conflict detection currently ignores), tasks crossing midnight, invalid time strings like `"25:00"`, and weekly recurrence landing on the correct date across month boundaries.

---

## 5. Reflection

**a. What went well**

I'm most satisfied with the clean separation between the logic layer (`pawpal_system.py`) and the UI (`app.py`). Because I followed the CLI-first workflow and verified everything with `main.py` and pytest before touching Streamlit, wiring up the UI was quick and I was confident the "brain" already worked.

**b. What you would improve**

I'd upgrade conflict detection to real interval-overlap checking, and make `build_plan` respect each task's preferred time of day instead of packing tasks back-to-back. I'd also let the UI mark tasks complete and show recurring tasks regenerating, so the recurrence feature is visible to the user and not just in the CLI demo.

**c. Key takeaway**

The biggest thing I learned is what it means to be the **lead architect** rather than just a prompter: AI is fastest when I give it a clear, well-scoped design to build against, and most dangerous when I let it make structural decisions. Keeping the design in my head, adding to the system instead of letting AI rewrite it, and verifying every step with tests is what kept the project coherent.

---

## 6. AI Strategy (Phase 6)

- **Most effective AI features:** inline/agent editing for filling in method bodies from a clear signature, and chat for scoped "how do I…" questions (e.g. `timedelta`, sorting `HH:MM` strings with a lambda key). Generating the first Mermaid diagram from a class list was also a big time-saver.
- **A suggestion I modified:** the AI proposed replacing my class design when adding task-tracking features; I instead extended it additively so existing tests kept passing (see 3b).
- **Separate chat sessions per phase** kept context clean: design discussion didn't bleed into testing, so each session's suggestions stayed relevant to the task at hand and I didn't get answers polluted by earlier, now-outdated decisions.
- **Lead-architect takeaway:** powerful AI tools amplify whatever direction you give them. Owning the architecture, the constraints, and the verification loop, and treating AI output as a draft to review, helped me create a website as effeciently as possible.
