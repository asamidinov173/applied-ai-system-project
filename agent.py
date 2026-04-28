import json
import logging
from datetime import time
from pawpal_system import Owner, Pet, Task, Scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PawPalAgent:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.logs = []

    def _log(self, step: str, message: str):
        entry = f"[{step}] {message}"
        self.logs.append(entry)
        logger.info(entry)

    def _get_tasks_summary(self) -> list:
        tasks = []
        for pet in self.owner.pets:
            for task in pet.tasks:
                tasks.append({
                    "pet": pet.name,
                    "title": task.title,
                    "deadline": str(task.deadline),
                    "priority": task.priority,
                    "duration": task.duration,
                    "type": type(task).__name__,
                })
        return tasks

    def step1_plan(self) -> str:
        self._log("PLAN", "Analyzing tasks...")
        tasks = self._get_tasks_summary()
        if not tasks:
            return "No tasks to plan."
        high = [t for t in tasks if t["priority"] == 3]
        plan = f"Found {len(tasks)} tasks. "
        if high:
            plan += f"High priority tasks: {', '.join([t['title'] for t in high])}. These should be scheduled first."
        else:
            plan += "All tasks are low to medium priority. Scheduling by earliest deadline."
        self._log("PLAN", f"Done: {plan[:80]}...")
        return plan

    def step2_schedule(self) -> list:
        self._log("SCHEDULE", "Running EDF scheduler...")
        scheduler = Scheduler(self.owner)
        plan = scheduler.generate_plan()
        self._log("SCHEDULE", f"Generated {len(plan)} tasks.")
        return plan

    def step3_check(self) -> list:
        self._log("CHECK", "Running conflict detection...")
        scheduler = Scheduler(self.owner)
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            self._log("CHECK", f"Found {len(conflicts)} conflict(s)!")
        else:
            self._log("CHECK", "No conflicts found.")
        return conflicts

    def step4_fix(self, conflicts: list) -> str:
        if not conflicts:
            self._log("FIX", "No conflicts to fix.")
            return "No conflicts detected — schedule looks clean!"
        self._log("FIX", "Generating fixes...")
        fixes = []
        for c in conflicts:
            fixes.append(f"Suggestion: Move one of the conflicting tasks 30 minutes later to avoid overlap.")
        return "\n".join(fixes)

    def step5_explain(self, plan: list, conflicts: list) -> dict:
        self._log("EXPLAIN", "Generating explanation...")
        task_count = len(plan)
        conflict_count = len(conflicts)
        confidence = 9 if conflict_count == 0 else 7
        explanation = (
            f"The schedule contains {task_count} tasks ordered by deadline and priority. "
            f"{'No conflicts were detected — the schedule is clean.' if conflict_count == 0 else f'{conflict_count} conflict(s) were detected and fixes were suggested.'} "
            f"High priority tasks are placed first to ensure critical care is not missed."
        )
        suggestion = (
            "Consider spreading tasks evenly across the day to avoid fatigue."
            if task_count > 3
            else "Add more tasks to build a complete daily routine."
        )
        self._log("EXPLAIN", f"Confidence: {confidence}/10")
        return {
            "explanation": explanation,
            "confidence": confidence,
            "suggestion": suggestion
        }

    def run(self) -> dict:
        self._log("START", f"Agent starting for owner: {self.owner.name}")
        results = {}
        results["plan"] = self.step1_plan()
        results["schedule"] = self.step2_schedule()
        results["conflicts"] = self.step3_check()
        results["fixes"] = self.step4_fix(results["conflicts"])
        results["explanation"] = self.step5_explain(
            results["schedule"], results["conflicts"]
        )
        results["logs"] = self.logs
        self._log("DONE", "Agent completed successfully.")
        return results