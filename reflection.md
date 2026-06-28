# PawPal+ Project Reflection

## 1. System Design

Three core actions a user should be able to perform in PawPal+:

1. **Add a pet** — enter a pet's name and species so the app knows who the care tasks are for.
2. **Add a care task** — create a task (e.g. "Morning walk") with a duration and a priority (low/medium/high).
3. **Generate today's plan** — given the owner's available time, produce a daily schedule that fits the most important tasks and shows which tasks didn't fit.

**a. Initial design**

My initial UML has seven classes:

- **Owner** — holds the owner's name and how many minutes they have available in a day. Represents the person and their scheduling constraint.
- **Pet** — holds the pet's name and species. Identifies who the tasks are for.
- **Task** — a single care task with a title, duration in minutes, and a priority. This is the unit the scheduler works with.
- **Priority** — an enumeration (LOW, MEDIUM, HIGH) used to rank tasks so the most important ones get placed first.
- **Scheduler** — the core logic. It sorts tasks by priority and fits them into the owner's available time, then produces a Plan.
- **ScheduledItem** — wraps a Task with a start time, representing one task placed in the day.
- **Plan** — the scheduler's output: a list of scheduled items plus a list of skipped tasks, and an `explain()` method to justify the result.

The main relationships are: an Owner has Pets, a Pet has Tasks, the Scheduler uses the Owner's constraints to turn Tasks into a Plan, and a Plan contains ScheduledItems (which each wrap a Task).

**b. Design changes**

Yes. My original UML (matching the starter stubs) showed how the objects were used together but never drew the ownership hierarchy. I added two relationships — `Owner --> Pet : has` and `Pet --> Task : has` — so the diagram reflects the real structure: an owner has pets, and a pet has the care tasks. This makes it clear where tasks come from before the Scheduler turns them into a Plan, instead of leaving that connection implied.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
