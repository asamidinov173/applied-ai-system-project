# PawPal+ System Architecture

## Data Flow
User Input → Streamlit UI → PawPalAgent → Claude AI API
                                ↓
                         pawpal_system.py
                         (Owner, Pet, Task, Scheduler)
                                ↓
                         5-Step Agentic Loop:
                         1. PLAN   → Claude analyzes tasks
                         2. SCHEDULE → EDF Scheduler runs
                         3. CHECK  → Conflict detection
                         4. FIX    → Claude suggests fixes
                         5. EXPLAIN → Claude rates confidence
                                ↓
                         Results displayed in Streamlit UI