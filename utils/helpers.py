import json
import os
from datetime import datetime, time, timedelta

def load_json(path, default=None):
    """
    Safely load JSON from disk.
    Returns default if file does not exist.
    """
    try:
        if not os.path.exists(path):
            return default
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load JSON from {path}: {e}")

def save_json(path, data):
    """
    Safely save JSON to disk with pretty formatting.
    """
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        raise RuntimeError(f"Failed to save JSON to {path}: {e}")

def parse_iso_datetime(value):
    """
    Parse ISO datetime string into datetime object.
    Returns None if parsing fails.
    """
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None

def to_iso(dt):
    """
    Convert datetime to ISO string.
    """
    if not dt:
        return None
    return dt.isoformat()

def clamp(value, min_value, max_value):
    """
    Clamp numeric value between min and max.
    """
    return max(min_value, min(value, max_value))

def get_work_window_for_date(date, preferences):
    """
    Given a date and user preferences, return work start and end datetimes.
    """
    start_str = preferences.get("work_start", "09:00")
    end_str = preferences.get("work_end", "17:00")

    start_hour, start_min = map(int, start_str.split(":"))
    end_hour, end_min = map(int, end_str.split(":"))

    start_dt = datetime.combine(date.date(), time(start_hour, start_min))
    end_dt = datetime.combine(date.date(), time(end_hour, end_min))

    if end_dt <= start_dt:
        end_dt += timedelta(days=1)

    return start_dt, end_dt
