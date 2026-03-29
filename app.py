import streamlit as st
from datetime import time
from pawpal_system import Owner, Pet, FeedingTask, WalkTask, MedicationTask, AppointmentTask, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("A smart pet care planning assistant.")

# --- Session state setup ---
if "owner" not in st.session_state:
    st.session_state.owner = None

# --- Owner + Pet Setup ---
st.subheader("Owner & Pet Info")

owner_name = st.text_input("Owner name", value="Jordan")
owner_email = st.text_input("Owner email", value="jordan@email.com")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
pet_age = st.number_input("Pet age", min_value=0, max_value=30, value=2)

if st.button("Save owner & pet"):
    pet = Pet(name=pet_name, species=species, age=pet_age)
    owner = Owner(name=owner_name, email=owner_email)
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.success(f"Saved! Owner: {owner_name} | Pet: {pet_name} ({species}, age {pet_age})")

st.divider()

# --- Add Tasks ---
st.subheader("Add Tasks")

if st.session_state.owner is None:
    st.warning("Please save your owner & pet info first.")
else:
    pet = st.session_state.owner.pets[0]

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (mins)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", [1, 2, 3],
                                format_func=lambda x: {1: "low", 2: "medium", 3: "high"}[x])

    col4, col5 = st.columns(2)
    with col4:
        deadline_hour = st.slider("Deadline hour", min_value=0, max_value=23, value=8)
    with col5:
        task_type = st.selectbox("Task type", ["Feeding", "Walk", "Medication", "Appointment"])

    frequency = st.selectbox("Frequency", ["none", "daily", "weekly"])

    if st.button("Add task"):
        deadline = time(deadline_hour, 0)
        freq = None if frequency == "none" else frequency

        if task_type == "Feeding":
            task = FeedingTask(title=task_title, deadline=deadline, priority=priority, duration=duration, frequency=freq)
        elif task_type == "Walk":
            task = WalkTask(title=task_title, deadline=deadline, priority=priority, duration=duration, frequency=freq)
        elif task_type == "Medication":
            task = MedicationTask(title=task_title, deadline=deadline, priority=priority, duration=duration, frequency=freq)
        else:
            task = AppointmentTask(title=task_title, deadline=deadline, priority=priority, duration=duration, frequency=freq)

        pet.add_task(task)
        st.success(f"Task added: {task_title} at {deadline_hour}:00")

    if pet.tasks:
        st.write("Current tasks:")
        st.table([{
            "Title": t.title,
            "Deadline": str(t.deadline),
            "Priority": {1: "low", 2: "medium", 3: "high"}[t.priority],
            "Duration (mins)": t.duration,
            "Frequency": t.frequency or "none",
            "Done": t.is_done
        } for t in pet.tasks])
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# --- Generate Schedule ---
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    if st.session_state.owner is None:
        st.error("Please save your owner & pet info first.")
    elif not st.session_state.owner.pets[0].tasks:
        st.error("Please add at least one task first.")
    else:
        scheduler = Scheduler(st.session_state.owner)

        # Conflict detection
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            st.warning("Conflicts detected — two tasks are scheduled at the same time:")
            for c in conflicts:
                st.warning(f"⚠️ {c}")
        else:
            st.success("No scheduling conflicts detected.")

        # Display sorted schedule
        st.markdown("### Today's Schedule")
        plan = scheduler.generate_plan()
        for i, (pet_name, task) in enumerate(plan, 1):
            status = "✅ Done" if task.is_done else "⏳ Pending"
            priority_label = {1: "low", 2: "medium", 3: "high"}[task.priority]
            with st.container():
                st.markdown(f"**{i}. [{task.deadline}] {task.title}** ({pet_name})")
                st.caption(f"Priority: {priority_label} | Duration: {task.duration} mins | Frequency: {task.frequency or 'none'} | {status}")
                st.divider()

        # Filter: pending only
        st.markdown("### Pending Tasks Only")
        pending = scheduler.filter_by_status(done=False)
        if pending:
            for pet_name, task in pending:
                st.markdown(f"- **{task.title}** ({pet_name}) at {task.deadline}")
        else:
            st.info("All tasks are complete!")