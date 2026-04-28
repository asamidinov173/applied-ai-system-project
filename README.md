# 🐾 PawPal+ Applied AI System

## Original Project
This project extends **PawPal+** (Module 2), a pet care planning app built with Python and Streamlit. The original system used OOP classes (Owner, Pet, Task, Scheduler) to manage daily pet care tasks with an Earliest Deadline First scheduling algorithm and conflict detection.

## What This Version Adds
This version extends PawPal+ into a full **agentic AI system** powered by Claude AI. The AI agent plans, schedules, detects conflicts, suggests fixes, and explains its reasoning — all automatically.

## AI Feature: Agentic Workflow
The system uses a 5-step agentic loop:
1. **PLAN** — Claude analyzes tasks and identifies priorities
2. **SCHEDULE** — EDF scheduler generates the daily plan
3. **CHECK** — Conflict detection runs automatically
4. **FIX** — Claude suggests fixes for any conflicts
5. **EXPLAIN** — Claude explains the schedule and gives a confidence score (1-10)

## System Architecture
User Input → Streamlit UI → PawPalAgent → Claude AI API
                                ↓
                         pawpal_system.py
                         (Owner, Pet, Task, Scheduler)
                                ↓
                         5-Step Agentic Loop
                                ↓
                         Results in Streamlit UI

## Setup Instructions
1. Clone the repo: git clone https://github.com/asamidinov173/applied-ai-system-project.git
2. Enter folder: cd applied-ai-system-project
3. Create venv: python3 -m venv .venv
4. Activate venv: source .venv/bin/activate
5. Install packages: pip install -r requirements.txt
6. Set API key: export ANTHROPIC_API_KEY="your-key-here"
7. Run app: streamlit run app.py

## Sample Interactions
**Input:** Owner: Alikhan, Pet: Buddy (dog), Tasks: Morning walk (8am), Feeding (8am), Medication (7am)

**Agent Output:**
- Step 1 Plan: "Medication should be prioritized first as it has the earliest deadline..."
- Step 3 Conflict: "Morning walk and Feeding are both scheduled at 08:00"
- Step 4 Fix: "Move Feeding to 8:30am to avoid overlap"
- Step 5 Confidence: 8/10

## Design Decisions
- Used agentic workflow over RAG because PawPal+ is a planning system — reasoning and fixing is more valuable than retrieval
- Claude AI handles the thinking steps; existing Python scheduler handles the logic steps
- Logging tracks every agent step for transparency and debugging

## Testing Summary
- 10 pytest tests cover task completion, conflict detection, scheduling, and filtering
- All 10 tests pass
- Agent error handling catches API failures gracefully with try/except

## Reflection
Building this taught me that agentic AI systems work best when you combine deterministic logic (the scheduler) with AI reasoning (Claude). The AI does not replace the code — it makes it smarter by explaining and improving it.

## Demo Walkthrough
Loom video link: (add after recording)

## Repository
https://github.com/asamidinov173/applied-ai-system-project