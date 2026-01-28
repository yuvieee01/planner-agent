from datetime import datetime
import random

from utils.helpers import load_json, save_json
from agent.task_analyzer import analyze_tasks
from agent.priority_engine import score_tasks
from agent.schedule_planner import plan_schedule
from agent.reflection_engine import reflect_and_update
from llm.llm_client import LLMClient


TASKS_PATH = "inputs/tasks.json"
MEMORY_PATH = "memory/user_history.json"


def main():
    print("\n=== AUTONOMOUS PRODUCTIVITY AGENT ===\n")

    # -------- OBSERVE --------
    tasks_data = load_json(TASKS_PATH)
    memory = load_json(MEMORY_PATH)

    raw_tasks = tasks_data.get("tasks", [])
    print(f"[Observe] Loaded {len(raw_tasks)} tasks")
    print(f"[Observe] Past runs: {len(memory.get('past_runs', []))}")

    # -------- ANALYZE --------
    analyzed_tasks = analyze_tasks(raw_tasks, memory)
    print("[Analyze] Tasks normalized and effort estimated")

    # -------- REASON --------
    scored_tasks = score_tasks(analyzed_tasks, datetime.now())
    print("[Reason] Tasks prioritized")

    print("\nTop priorities:")
    for t in scored_tasks:
        print(f"  {t['id']} | score={t['priority_score']} | est={t['est_minutes']} mins")

    # -------- PLAN --------
    llm = LLMClient()
    plan = plan_schedule(scored_tasks, memory, llm)

    print("\n=== DAILY PLAN ===")
    for block in plan["schedule"]:
        print(
            f"{block['start']} → {block['end']} | "
            f"{block['task_id']} | {block['title']}"
        )

    if plan["postponed"]:
        print("\nPostponed tasks:")
        for t in plan["postponed"]:
            print(f"  {t['id']} | {t['title']}")

    print("\nPlanner rationale:")
    print(plan["planner_rationale"])

    # -------- ACT (SIMULATED EXECUTION) --------
    print("\n=== EXECUTION (SIMULATED) ===")
    completed_tasks = []

    for block in plan["schedule"]:
        # Longer tasks are harder to complete
        completion_probability = max(0.4, 1 - block["est_minutes"] / 300)
        completed = random.random() < completion_probability

        status = "DONE" if completed else "MISSED"
        print(f"{block['task_id']} → {status}")

        if completed:
            completed_tasks.append(block["task_id"])

    # -------- REFLECT + REMEMBER --------
    reflection, updated_memory = reflect_and_update(
        plan,
        completed_tasks,
        memory,
        llm
    )

    print("\n=== REFLECTION ===")
    print("Completion rate:", reflection["completion_rate"])
    for insight in reflection["insights"]:
        print("-", insight)

    print("\nUpdated preferences:")
    for k, v in reflection["updated_preferences"].items():
        print(f"  {k}: {v}")

    # -------- SAVE MEMORY --------
    save_json(MEMORY_PATH, updated_memory)
    print("\n[Memory] Updated and saved")


if __name__ == "__main__":
    main()
