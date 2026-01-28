"""
LLM client abstraction.

This module defines structured prompts used by the agent and provides
a mock LLM implementation so the system runs offline.

Later, this can be replaced with OpenAI / Gemini calls without changing
any agent logic.
"""

import json

# ----------- Structured Prompts -----------

PLANNER_PROMPT = """
You are an intelligent planning assistant.

Input:
- List of tasks with estimated minutes, importance, and deadlines
- Available work time for today

Your job:
- Explain why certain tasks were scheduled today
- Identify overload if total effort exceeds capacity
- Suggest one corrective action if overloaded

Return JSON with keys:
- rationale
- overload_reason (or null)
- suggested_action
"""

REFLECTION_PROMPT = """
You are reflecting on a completed plan.

Input:
- Planned tasks
- Completed tasks

Your job:
- Compute completion rate
- Identify reasons for missed tasks
- Suggest small improvements for future planning

Return JSON with keys:
- completion_rate
- insights (list of strings)
- adjustments (dictionary)
"""

MEMORY_UPDATE_PROMPT = """
You are updating long-term memory.

Input:
- Previous memory values
- Reflection analysis

Your job:
- Suggest conservative updates to planning preferences

Return JSON with keys:
- estimation_bias_delta
- daily_capacity_delta_minutes
- notes
"""

# ----------- LLM Client -----------

class LLMClient:
    def __init__(self, mock_mode=True):
        self.mock_mode = mock_mode

    def call(self, prompt, context=None):
        """
        Call the LLM with a prompt and optional context.
        In mock mode, returns deterministic responses.
        """
        if self.mock_mode:
            return self._mock_response(prompt, context)
        else:
            raise NotImplementedError("Real LLM calls not implemented yet")

    def _mock_response(self, prompt, context):
        """
        Deterministic mock responses for offline execution.
        """
        if "planning assistant" in prompt:
            overload = context.get("overload", False)
            return json.dumps({
                "rationale": "Tasks with highest importance and closest deadlines were scheduled first.",
                "overload_reason": "Total estimated effort exceeded daily capacity." if overload else None,
                "suggested_action": "Postpone low-priority tasks or split large tasks." if overload else "Proceed as planned."
            })

        if "reflecting on a completed plan" in prompt:
            planned = context.get("planned", [])
            completed = context.get("completed", [])
            completion_rate = round(100 * len(completed) / max(1, len(planned)), 1)
            return json.dumps({
                "completion_rate": completion_rate,
                "insights": [
                    "Missed tasks correlate with overloaded schedules.",
                    "Large tasks are more likely to slip."
                ],
                "adjustments": {
                    "estimation_bias_delta": 0.05 if completion_rate < 70 else -0.02,
                    "daily_capacity_delta_minutes": 0
                }
            })

        if "updating long-term memory" in prompt:
            return json.dumps({
                "estimation_bias_delta": 0.02,
                "daily_capacity_delta_minutes": 0,
                "notes": "Minor adjustment based on recent completion trends."
            })

        return json.dumps({"message": "Mock LLM response"})
