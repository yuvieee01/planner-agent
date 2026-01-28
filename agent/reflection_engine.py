from datetime import datetime
import json
from llm.llm_client import REFLECTION_PROMPT, MEMORY_UPDATE_PROMPT
from utils.helpers import to_iso

def reflect_and_update(plan, completed_task_ids, memory, llm_client):
    """
    Reflect on execution results and update long-term memory.
    """

    scheduled = plan.get("schedule", [])
    planned_ids = [t["task_id"] for t in scheduled]
    completed_ids = set(completed_task_ids)

    # Build reflection context
    context = {
        "planned": scheduled,
        "completed": [t for t in scheduled if t["task_id"] in completed_ids]
    }

    # Call LLM for reflection
    reflection_response = llm_client.call(REFLECTION_PROMPT, context=context)

    try:
        reflection_data = json.loads(reflection_response)
    except Exception:
        reflection_data = {
            "completion_rate": 0,
            "insights": ["Failed to parse reflection output."],
            "adjustments": {}
        }

    completion_rate = reflection_data.get("completion_rate", 0)
    adjustments = reflection_data.get("adjustments", {})

    # ---- Update memory preferences ----
    prefs = memory.get("preferences", {})

    # Estimation bias update
    bias_delta = adjustments.get("estimation_bias_delta", 0)
    prefs["estimation_bias"] = round(
        max(0.7, min(1.5, prefs.get("estimation_bias", 1.0) + bias_delta)), 2
    )

    # Capacity update (stored as hours)
    cap_delta_min = adjustments.get("daily_capacity_delta_minutes", 0)
    cap_delta_hr = cap_delta_min // 60
    prefs["daily_capacity_minutes"] = max(
        4, min(12, prefs.get("daily_capacity_minutes", 8) + cap_delta_hr)
    )

    # ---- Save run history ----
    run_record = {
        "date": to_iso(datetime.now()),
        "planned_task_ids": planned_ids,
        "completed_task_ids": list(completed_ids),
        "completion_rate": completion_rate,
        "insights": reflection_data.get("insights", [])
    }

    memory.setdefault("past_runs", []).append(run_record)

    # ---- Update aggregates ----
    aggregates = memory.setdefault("aggregates", {})
    prev_avg = aggregates.get("average_completion_rate")

    if prev_avg is None:
        aggregates["average_completion_rate"] = completion_rate
    else:
        aggregates["average_completion_rate"] = round(
            prev_avg * 0.8 + completion_rate * 0.2, 2
        )

    return {
        "completion_rate": completion_rate,
        "insights": reflection_data.get("insights", []),
        "updated_preferences": prefs
    }, memory
