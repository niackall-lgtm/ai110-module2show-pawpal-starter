"""CLI demo for PawPal+.

A temporary "testing ground" that builds a small scenario and prints today's
schedule to the terminal, so we can verify the backend logic before wiring it
into the Streamlit UI. Run with:  python main.py
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

    # 3. Add at least three tasks across the pets.
    biscuit.add_task(Task("Morning walk", 30, Priority.HIGH))
    biscuit.add_task(Task("Feeding", 10, Priority.HIGH))
    mochi.add_task(Task("Litter cleanup", 15, Priority.MEDIUM))
    mochi.add_task(Task("Play time", 20, Priority.LOW))

    # 4. Build and print today's schedule.
    plan = Scheduler(owner).build_plan()

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


if __name__ == "__main__":
    main()
