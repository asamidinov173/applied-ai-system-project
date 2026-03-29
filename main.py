from datetime import time
from pawpal_system import Owner, Pet, FeedingTask, WalkTask, MedicationTask, Scheduler


# Create owner
owner = Owner(name="Alikhan", email="alikhan@email.com")

# Create pets
dog = Pet(name="Buddy", species="Dog", age=3)
cat = Pet(name="Whiskers", species="Cat", age=5)

# Add tasks to dog
dog.add_task(FeedingTask(
    title="Morning feed",
    deadline=time(8, 0),
    priority=2,
    duration=10,
    food_type="kibble",
    portion=1.5
))
dog.add_task(WalkTask(
    title="Morning walk",
    deadline=time(9, 0),
    priority=1,
    duration=30,
    route="Park loop",
    distance=2.0
))

# Add tasks to cat
cat.add_task(FeedingTask(
    title="Cat breakfast",
    deadline=time(8, 30),
    priority=2,
    duration=5,
    food_type="wet food",
    portion=0.5
))
cat.add_task(MedicationTask(
    title="Flea medication",
    deadline=time(7, 0),
    priority=3,
    duration=5,
    drug="Frontline",
    dose=1.0
))

# Add pets to owner
owner.add_pet(dog)
owner.add_pet(cat)

# Run scheduler
scheduler = Scheduler(owner)
plan = scheduler.generate_plan()

# Print today's schedule
print("=" * 40)
print("        TODAY'S SCHEDULE")
print("=" * 40)
for i, (pet_name, task) in enumerate(plan, 1):
    status = "DONE" if task.is_done else "pending"
    print(f"{i}. [{task.deadline}] {task.title} ({pet_name})")
    print(f"   Priority: {task.priority} | Duration: {task.duration} mins | Status: {status}")
    print()