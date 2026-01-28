from utils.helpers import parse_iso_datetime, clamp

def analyze_tasks(raw_tasks, memory):
    """
    Analyze and normalize raw task input.

    Responsibilities:
    - Ensure required fields exist
    - Estimate time if not provided
    - Apply estimation bias from memory
    """

    analyzed_tasks = []

    estimation_bias = memory.get("preferences", {}).get("estimation_bias", 1.0)

    for task in raw_tasks:
        try:
            task_id = task.get("id")
            title = task.get("title", "Untitled Task")
            description = task.get("description", "")
            importance = int(task.get("importance", 3))
            deadline = parse_iso_datetime(task.get("deadline"))

            # Estimate effort
            if task.get("estimated_minutes") is not None:
                estimated_minutes = int(task["estimated_minutes"])
            else:
                # Simple heuristic: based on description length and importance
                word_count = max(1, len(description.split()))
                base_estimate = word_count * 1.5
                estimated_minutes = int(base_estimate * (1 + (importance - 3) * 0.15))

            # Apply user estimation bias
            estimated_minutes = int(estimated_minutes * estimation_bias)

            # Clamp estimate between 10 min and 8 hours
            estimated_minutes = clamp(estimated_minutes, 10, 8 * 60)

            analyzed_tasks.append({
                "id": task_id,
                "title": title,
                "description": description,
                "importance": importance,
                "deadline": deadline,
                "est_minutes": estimated_minutes,
                "tags": task.get("tags", []),
                "status": task.get("status", "pending")
            })

        except Exception as e:
            print(f"[task_analyzer] Skipping invalid task due to error: {e}")

    return analyzed_tasks
