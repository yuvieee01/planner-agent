from datetime import datetime, timedelta
from utils.helpers import get_work_window_for_date, to_iso
from llm.llm_client import PLANNER_PROMPT

def plan_schedule(scored_tasks, memory, llm_client, date=None):
    """
    Create a realistic daily schedule from scored tasks.

    Returns:
    - schedule: list of scheduled task blocks
    - postponed: tasks that could not fit
    - overload: boolean
    - planner_rationale: LLM explanation
    """

    if date is None:
        date = datetime.now()

    preferences = memory.get("preferences", {})

    # Determine work window
    work_start, work_end = get_work_window_for_date(date, preferences)
    total_available_minutes = int((work_end - work_start).total_seconds() / 60)

    # Daily capacity (stored as hours)
    daily_capacity_hours = preferences.get("daily_capacity_minutes", 8)
    daily_capacity_minutes = int(daily_capacity_hours * 60)

    available_minutes = min(total_available_minutes, daily_capacity_minutes)

    schedule = []
    postponed = []
    current_time = work_start
    remaining_minutes = available_minutes

    for task in scored_tasks:
        task_minutes = task["est_minutes"]

        if task_minutes <= remaining_minutes:
            start_time = current_time
            end_time = start_time + timedelta(minutes=task_minutes)

            schedule.append({
                "task_id": task["id"],
                "title": task["title"],
                "start": to_iso(start_time),
                "end": to_iso(end_time),
                "est_minutes": task_minutes,
                "importance": task["importance"]
            })

            current_time = end_time
            remaining_minutes -= task_minutes
        else:
            postponed.append(task)

    overload = len(postponed) > 0

    # Ask LLM for explanation
    context = {
        "overload": overload,
        "scheduled_tasks": schedule,
        "postponed_tasks": postponed,
        "available_minutes": available_minutes
    }

    planner_rationale = llm_client.call(PLANNER_PROMPT, context=context)

    return {
        "date": to_iso(date),
        "work_window": {
            "start": to_iso(work_start),
            "end": to_iso(work_end)
        },
        "available_minutes": available_minutes,
        "scheduled_minutes": available_minutes - remaining_minutes,
        "remaining_minutes": remaining_minutes,
        "schedule": schedule,
        "postponed": postponed,
        "overload": overload,
        "planner_rationale": planner_rationale
    }
