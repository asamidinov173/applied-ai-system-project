import streamlit as st
from datetime import time
from pawpal_system import Owner, Pet, FeedingTask, WalkTask, MedicationTask, AppointmentTask, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.markdown("A smart pet care planning assistant.")

if "owner" not in st.session_state:
    st.session_state.owner = None
if "pet" not in st.session_state:
    st.session_state.pet = None
if "tasks" not in st.session_state:
    st.session_state.tasks = []

st.subheader("Owner & Pet Info")
owner_name = st.text_input("Owner name", value="Alikhan")
owner_email = st.text_input("Owner email", value="alikhan@email.com")
pet_name = st.text_input("Pet name", value="Buddy")
species = st.selectbox("Species", ["dog", "cat", "other"])
pet_age = st.number_input("Pet age", min_value=0, max_value=30, value=3)

if st.button("Save owner & pet"):
    owner = Owner(name=owner_name, email=owner_email)
    pet = Pet(name=pet_name, species=species, age=pet_age)
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.session_state.pet = pet
    st.session_state.tasks = []
    st.success(f"Saved! Owner: {owner_name}, Pet: {pet_name}")

if st.session_state.pet:
    st.subheader("Add Tasks")
    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (mins)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", [1, 2, 3], format_func=lambda x: {1: "Low", 2: "Medium", 3: "High"}[x])

    deadline_hour = st.slider("Deadline hour", 0, 23, 8)
    task_type = st.selectbox("Task type", ["Feeding", "Walk", "Medication", "Appointment"])
    frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

    if st.button("Add task"):
        deadline = time(deadline_hour, 0)
        if task_type == "Feeding":
            task = FeedingTask(title=task_title, deadline=deadline, priority=priority, duration=duration, frequency=frequency)
        elif task_type == "Walk":
            task = WalkTask(title=task_title, deadline=deadline, priority=priority, duration=duration, frequency=frequency)
        elif task_type == "Medication":
            task = MedicationTask(title=task_title, deadline=deadline, priority=priority, duration=duration, frequency=frequency)
        else:
            task = AppointmentTask(title=task_title, deadline=deadline, priority=priority, duration=duration, frequency=frequency)

        st.session_state.pet.add_task(task)
        st.session_state.owner.pets[0] = st.session_state.pet
        st.session_state.tasks.append({
            "Title": task_title,
            "Deadline": str(deadline),
            "Priority": priority,
            "Duration (mins)": duration,
            "Frequency": frequency,
            "Done": False
        })
        st.success(f"Added: {task_title}")

    if st.session_state.tasks:
        st.write("Current tasks:")
        st.table(st.session_state.tasks)

if st.session_state.owner:
    st.subheader("Build Schedule")

    if st.button("Generate schedule (basic)"):
        scheduler = Scheduler(st.session_state.owner)
        plan = scheduler.generate_plan()
        conflicts = scheduler.detect_conflicts()

        if conflicts:
            for c in conflicts:
                st.warning(c)
        else:
            st.success("No scheduling conflicts detected.")

        st.markdown("**Today's Schedule**")
        for i, task in enumerate(plan, 1):
            if isinstance(task, tuple):
                st.markdown(f"{i}. {task}")
            else:
                pet_name_display = ""
                for pet in st.session_state.owner.pets:
                    if task in pet.tasks:
                        pet_name_display = pet.name
                status = "✅ Done" if task.is_done else "⏳ Pending"
                st.markdown(f"{i}. [{task.deadline}] **{task.title}** ({pet_name_display}) — Priority: {task.priority} | Duration: {task.duration} mins | {status}")

    st.divider()

    st.subheader("🤖 Run AI Agent")
    st.caption("The AI agent will plan, schedule, detect conflicts, suggest fixes, and explain the result.")

    if st.button("Run AI Agent"):
        if not st.session_state.tasks:
            st.warning("Please add at least one task first.")
        else:
            with st.spinner("Agent is thinking..."):
                try:
                    from agent import PawPalAgent
                    agent = PawPalAgent(st.session_state.owner)
                    results = agent.run()

                    st.markdown("### Step 1 — Plan")
                    st.info(results["plan"])

                    st.markdown("### Step 2 — Schedule")
                    for i, task in enumerate(results["schedule"], 1):
                        if isinstance(task, tuple):
                            st.markdown(f"{i}. {task}")
                        else:
                            status = "✅ Done" if task.is_done else "⏳ Pending"
                            st.markdown(f"{i}. [{task.deadline}] **{task.title}** — Priority: {task.priority} | {status}")

                    st.markdown("### Step 3 — Conflicts")
                    if results["conflicts"]:
                        for c in results["conflicts"]:
                            st.warning(c)
                    else:
                        st.success("No conflicts detected!")

                    st.markdown("### Step 4 — Fixes")
                    st.write(results["fixes"])

                    st.markdown("### Step 5 — Explanation")
                    exp = results["explanation"]
                    st.write(exp.get("explanation", exp))
                    st.metric("Confidence Score", f"{exp.get('confidence', 'N/A')}/10")
                    st.info(f"💡 Suggestion: {exp.get('suggestion', '')}")

                    st.markdown("### Agent Logs")
                    with st.expander("View logs"):
                        for log in results["logs"]:
                            st.text(log)

                except Exception as e:
                    st.error(f"Agent error: {e}")