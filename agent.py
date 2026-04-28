import json
import logging
from datetime import time
from typing import Any
import anthropic
from pawpal_system import Owner, Pet, Task, Scheduler
 
# Set up logging so we can track every step the agent takes
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
 
 
class PawPalAgent:
    """
    AI-powered agent that plans, schedules, detects conflicts,
    and explains a daily pet care schedule using Claude AI.
    """
 
    def __init__(self, owner: Owner):
        self.owner = owner
        self.client = anthropic.Anthropic()
        self.logs = []
 
    def _log(self, step: str, message: str):
        """Record a step in the agent's diary."""
        entry = f"[{step}] {message}"
        self.logs.append(entry)
        logger.info(entry)
 
    def _get_tasks_summary(self) -> list[dict]:
        """Convert all pet tasks into a simple list of dicts for Claude."""
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
        """Step 1: Ask Claude to analyze the tasks and make a plan."""
        self._log("PLAN", "Asking Claude to analyze tasks...")
 
        tasks = self._get_tasks_summary()
 
        if not tasks:
            self._log("PLAN", "No tasks found. Skipping planning step.")
            return "No tasks to plan."
 
        prompt = f"""
You are a pet care scheduling assistant. Here are today's pet care tasks:
 
{json.dumps(tasks, indent=2)}
 
Briefly analyze these tasks in 2-3 sentences:
- What should be prioritized and why?
- Any potential timing issues you notice?
Keep it short and practical.
"""
 
        response = self.client.messages.create(
            model="claude-opus-4-5",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
 
        plan = response.content[0].text
        self._log("PLAN", f"Claude's analysis: {plan[:100]}...")
        return plan
 
    def step2_schedule(self) -> list:
        """Step 2: Use existing Scheduler to generate the schedule."""
        self._log("SCHEDULE", "Running scheduler (EDF + priority)...")
 
        scheduler = Scheduler(self.owner)
        plan = scheduler.generate_plan()
 
        self._log("SCHEDULE", f"Generated {len(plan)} scheduled tasks.")
        return plan
 
    def step3_check(self) -> list[str]:
        """Step 3: Detect conflicts in the schedule."""
        self._log("CHECK", "Running conflict detection...")
 
        scheduler = Scheduler(self.owner)
        conflicts = scheduler.detect_conflicts()
 
        if conflicts:
            self._log("CHECK", f"Found {len(conflicts)} conflict(s)!")
        else:
            self._log("CHECK", "No conflicts found.")
 
        return conflicts
 
    def step4_fix(self, conflicts: list[str]) -> str:
        """Step 4: Ask Claude to suggest fixes for any conflicts."""
        if not conflicts:
            self._log("FIX", "No conflicts to fix.")
            return "No conflicts detected — schedule looks clean!"
 
        self._log("FIX", "Asking Claude to suggest conflict fixes...")
 
        prompt = f"""
The pet care scheduler detected these conflicts:
 
{chr(10).join(conflicts)}
 
Suggest a simple fix for each conflict in plain language (1 sentence per conflict).
Be specific — suggest a new time if relevant.
"""
 
        response = self.client.messages.create(
            model="claude-opus-4-5",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
 
        fix = response.content[0].text
        self._log("FIX", f"Claude's fix: {fix[:100]}...")
        return fix
 
    def step5_explain(self, plan: list, conflicts: list[str]) -> dict:
        """Step 5: Ask Claude to explain the schedule and rate its confidence."""
        self._log("EXPLAIN", "Asking Claude to explain the final schedule...")
 
        tasks = self._get_tasks_summary()
        conflict_info = conflicts if conflicts else ["None"]
 
        prompt = f"""
You are a pet care assistant. Here is today's finalized schedule:
 
Tasks: {json.dumps(tasks, indent=2)}
Conflicts detected: {conflict_info}
 
Please provide:
1. A 2-3 sentence explanation of why this schedule makes sense for the pet owner.
2. A confidence score from 1-10 rating how good this schedule is.
3. One suggestion to improve it.
 
Format your response as JSON like this:
{{
  "explanation": "...",
  "confidence": 8,
  "suggestion": "..."
}}
"""
 
        response = self.client.messages.create(
            model="claude-opus-4-5",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
 
        raw = response.content[0].text.strip()
 
        # Safely parse JSON response
        try:
            # Strip markdown code fences if present
            clean = raw.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean)
        except json.JSONDecodeError:
            result = {
                "explanation": raw,
                "confidence": "N/A",
                "suggestion": "Could not parse structured response."
            }
 
        self._log("EXPLAIN", f"Confidence: {result.get('confidence')}/10")
        return result
 
    def run(self) -> dict[str, Any]:
        """
        Run the full agentic loop:
        Plan → Schedule → Check → Fix → Explain
        Returns a dict with all results and logs.
        """
        self._log("START", f"Agent starting for owner: {self.owner.name}")
 
        results = {}
 
        # Step 1 — Plan
        results["plan"] = self.step1_plan()
 
        # Step 2 — Schedule
        results["schedule"] = self.step2_schedule()
 
        # Step 3 — Check
        results["conflicts"] = self.step3_check()
 
        # Step 4 — Fix
        results["fixes"] = self.step4_fix(results["conflicts"])
 
        # Step 5 — Explain
        results["explanation"] = self.step5_explain(
            results["schedule"],
            results["conflicts"]
        )
 
        results["logs"] = self.logs
        self._log("DONE", "Agent completed successfully.")
 
        return resultsß