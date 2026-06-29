"""PawPal+ Streamlit UI.

This is the presentation layer. All the real logic lives in pawpal_system.py;
this file just collects input, calls the backend, and displays the results.
"""

import streamlit as st

from pawpal_system import Owner, Pet, Priority, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("A smart pet-care planner. Add pets, add tasks, and build a daily plan.")

# --- Application "memory" --------------------------------------------------
# Streamlit re-runs this script top-to-bottom on every interaction, so we keep
# the Owner (and everything it contains) in st.session_state so it survives
# across reruns instead of being recreated empty each time.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=120)

owner: Owner = st.session_state.owner

# --- Owner settings --------------------------------------------------------
with st.sidebar:
    st.header("Owner")
    owner.name = st.text_input("Owner name", value=owner.name)
    owner.available_minutes = st.number_input(
        "Available minutes today", min_value=10, max_value=600, value=owner.available_minutes, step=10
    )

# --- Add a pet -------------------------------------------------------------
st.subheader("1. Add a pet")
with st.form("add_pet", clear_on_submit=True):
    pet_name = st.text_input("Pet name", value="")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    if st.form_submit_button("Add pet") and pet_name.strip():
        owner.add_pet(Pet(name=pet_name.strip(), species=species))
        st.success(f"Added {pet_name.strip()} the {species}!")

if not owner.pets:
    st.info("No pets yet. Add one above to get started.")
    st.stop()

st.write("**Your pets:** " + ", ".join(f"{p.name} ({p.species})" for p in owner.pets))

# --- Add a task ------------------------------------------------------------
st.subheader("2. Add a task")
with st.form("add_task", clear_on_submit=True):
    target_pet = st.selectbox("For which pet?", [p.name for p in owner.pets])
    col1, col2 = st.columns(2)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col2:
        task_time = st.text_input("Time (HH:MM)", value="08:00")
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    frequency = st.selectbox("Frequency", ["daily", "weekly", "once"])
    if st.form_submit_button("Add task"):
        pet = next(p for p in owner.pets if p.name == target_pet)
        pet.add_task(
            Task(
                title=task_title,
                duration_minutes=int(duration),
                priority=Priority.from_str(priority),
                time=task_time,
                frequency=frequency,
            )
        )
        st.success(f"Added '{task_title}' for {target_pet}.")

st.divider()

# --- Build & display the schedule -----------------------------------------
st.subheader("3. Today's plan")
scheduler = Scheduler(owner)

if not owner.get_all_tasks():
    st.info("No tasks yet. Add a few above, then build the plan.")
else:
    # Conflict warnings first, so the owner sees them prominently.
    conflicts = scheduler.detect_conflicts()
    for warning in conflicts:
        st.warning(warning)
    if not conflicts:
        st.success("No scheduling conflicts found. ✅")

    # Priority-based plan (respects the owner's available time).
    plan = scheduler.build_plan()
    if plan.scheduled:
        st.markdown("**Scheduled (by priority, within your available time):**")
        st.table(
            [
                {
                    "Task": item.task.title,
                    "Duration (min)": item.task.duration_minutes,
                    "Priority": item.task.priority.name.title(),
                }
                for item in plan.scheduled
            ]
        )
    if plan.skipped:
        st.markdown("**Didn't fit today:**")
        st.table([{"Task": t.title, "Duration (min)": t.duration_minutes} for t in plan.skipped])

    # Full task list sorted by time of day.
    st.markdown("**All tasks sorted by time of day:**")
    st.table(
        [
            {
                "Time": t.time,
                "Task": t.title,
                "Frequency": t.frequency,
                "Done": "✅" if t.completed else "—",
            }
            for t in scheduler.sort_by_time()
        ]
    )
