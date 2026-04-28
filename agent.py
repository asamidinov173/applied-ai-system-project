import json
import logging
from datetime import time
from typing import Any
import anthropic
from pawpal_system import Owner, Pet, Task, Scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PawPalAgent:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.client = anthropic.Anthropic()
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
        self._log("PLAN", "Asking Claude to analyze tasks...")
        tasks = self._get_tasks_summary()
        if not tasks:
            return "No tasks to plan."
        prompt = f"You are a pet care assistant. Analyze these tasks in 2-3 sentences:\n{json.dumps(tasks, indent=2)}"
        response = self.client.messages.create(
            model="claude-opus-4-5",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        plan = response.content[0].text
        self._log("PLAN", f"Done: {plan[:80]}...")
        return plan

    def step2_schedule(self) -> list:
        self._log("SCHEDULE", "Running scheduler...")
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
            return "No conflicts detected."
        self._log("FIX", "Asking Claude for fixes...")
        prompt = f"Fix these pet care scheduling conflicts (1 sentence each):\n{chr(10).join(conflicts)}"
        response = self.client.messages.create(
            model="claude-opus-4-5",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        fix = response.content[0].text
        self._log("FIX", f"Done: {fix[:80]}...")
        return fix

    def step5_explain(self, plan: list, conflicts: list) -> dict:
        self._log("EXPLAIN", "Asking Claude to explain the schedule...")
        tasks = self._get_tasks_summary()
        prompt = f"""Explain this pet care schedule in JSON format:
Tasks: {json.dumps(tasks, indent=2)}
Conflicts: {conflicts if conflicts else ["None"]}
Return only JSON: {{"explanation": "2-3 sentences", "confidence": 8, "suggestion": "one tip"}}"""
        response = self.client.messages.create(
            model="claude-opus-4-5",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.content[0].text.strip()
        try:
            clean = raw.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean)
        except json.JSONDecodeError:
            result = {"explanation": raw, "confidence": "N/A", "suggestion": "Could not parse response."}
        self._log("EXPLAIN", f"Confidence: {result.get('confidence')}/10")
        return result

    def run(self) -> dict:
        self._log("START", f"Agent starting for owner: {self.owner.name}")
        results = {}
        results["plan"] = self.step1_plan()
        results["schedule"] = self.step2_schedule()
        results["conflicts"] = self.step3_check()
        results["fixes"] = self.step4_fix(results["conflicts"])
        results["explanation"] = self.step5_explain(results["schedule"], results["conflicts"])
        results["logs"] = self.logs
        self._log("DONE", "Agent completed successfully.")
        return results
