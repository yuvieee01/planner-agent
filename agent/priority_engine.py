from datetime import datetime
import math

def _days_until_deadline(deadline, now):
    if deadline is None:
        return None
    delta = deadline - now
    return delta.total_seconds() / (60 * 60 * 24)

def score_tasks(tasks, now=None):
    """
    Assign priority scores to tasks based on:
    - Importance
    - Deadline urgency
    - Task size penalty
    """

    if now is None:
        now = datetime.now()

    scored_tasks = []

    for task in tasks:
        importance = task.get("importance", 3)

        # Importance score (normalized)
        importance_score = importance / 5.0  # 0.2 → 1.0

        # Urgency score
        days_left = _days_until_deadline(task.get("deadline"), now)
        if days_left is None:
            urgency_score = 0.2
        elif days_left <= 0:
            urgency_score = 1.0
        else:
            urgency_score = 1 / (1 + days_left)

        # Size penalty (large tasks slightly deprioritized)
        est_minutes = task.get("est_minutes", 60)
        size_penalty = min(0.3, math.log1p(est_minutes) / 10)

        # Final priority score
        priority_score = (
            0.6 * importance_score +
            0.5 * urgency_score -
            0.3 * size_penalty
        )

        task_with_score = task.copy()
        task_with_score["priority_score"] = round(priority_score, 4)
        task_with_score["days_until_deadline"] = days_left

        scored_tasks.append(task_with_score)

    # Sort highest priority first
    scored_tasks.sort(key=lambda x: x["priority_score"], reverse=True)

    return scored_tasks
