"""CLI demo for PawPal+.

A temporary "testing ground" that builds a small scenario and exercises the
backend logic in the terminal, so we can verify it before wiring it into the
Streamlit UI. Run with:  python main.py
"""

from pawpal_system import Owner, Pet, Priority, Scheduler, Task


def minutes_to_clock(minute: int, day_start_hour: int = 8) -> str:
    """Turn 'minutes since the planning window started' into a HH:MM clock time."""
    total = day_start_hour * 60 + minute
    return f"{total // 60:02d}:{total % 60:02d}"


def main() -> None:
    # 1. Create an owner with a limited time budget for the day.
    owner = Owner(name="Jordan", available_minutes=60)

    # 2. Create at least two pets.
    biscuit = Pet(name="Biscuit", species="dog")
    mochi = Pet(name="Mochi", species="cat")
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    # 3. Add tasks OUT OF ORDER and with a deliberate time conflict at 08:00.
    biscuit.add_task(Task("Evening walk", 30, Priority.HIGH, time="18:00"))
    biscuit.add_task(Task("Morning walk", 30, Priority.HIGH, time="08:00"))
    biscuit.add_task(Task("Feeding", 10, Priority.HIGH, time="08:00"))  # conflict!
    mochi.add_task(Task("Litter cleanup", 15, Priority.MEDIUM, time="12:00"))
    mochi.add_task(Task("Play time", 20, Priority.LOW, time="15:00"))

    scheduler = Scheduler(owner)

    # --- Priority-based day plan (respects available time) -----------------
    plan = scheduler.build_plan()
    print(f"Today's Schedule for {owner.name} ({owner.available_minutes} min available)")
    print("=" * 52)
    for item in plan.scheduled:
        clock = minutes_to_clock(item.start_minute)
        print(
            f"  {clock} — {item.task.title} "
            f"({item.task.duration_minutes} min) [priority: {item.task.priority.name.lower()}]"
        )
    if plan.skipped:
        print("\nDidn't fit today:")
        for task in plan.skipped:
            print(f"  - {task.title} ({task.duration_minutes} min)")

    # --- Sorting by time of day -------------------------------------------
    print("\nAll tasks sorted by time of day:")
    for task in scheduler.sort_by_time():
        print(f"  {task.time} — {task.title}")

    # --- Filtering --------------------------------------------------------
    print("\nBiscuit's tasks (filter_by_pet):")
    for task in scheduler.filter_by_pet("Biscuit"):
        print(f"  {task.time} — {task.title}")

    # --- Conflict detection -----------------------------------------------
    print("\nConflict check:")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"  {warning}")
    else:
        print("  No conflicts found.")

    # --- Recurring task demo ----------------------------------------------
    print("\nRecurring task demo:")
    feeding = biscuit.tasks[2]  # the daily "Feeding" task
    print(f"  Before: '{feeding.title}' completed={feeding.completed}, "
          f"Biscuit has {len(biscuit.tasks)} tasks")
    next_feeding = scheduler.complete_and_reschedule(biscuit, feeding)
    print(f"  After completing it: completed={feeding.completed}, "
          f"Biscuit has {len(biscuit.tasks)} tasks")
    if next_feeding:
        print(f"  Auto-created next occurrence due {next_feeding.due_date}")


if __name__ == "__main__":
    main()
