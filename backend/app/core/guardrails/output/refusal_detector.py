import re
from typing import Any
from app.core.guardrails.base import Guardrail, GuardrailResult

REFUSAL_PATTERNS = [
    r"I(?:'m| am) (sorry|unable|not able|not allowed|cannot|cannot|afraid)",
    r"I cannot (help|assist|answer|respond|provide|complete|fulfill|do that|process)",
    r"I (cannot|can't|won't|will not) (help|assist|answer|respond|provide)",
    r"(sorry|apologies|apologize),?\s+(but\s+)?I(?:'m| am)? (cannot|can't|unable|not\s+able)",
    r"(cannot|can't|unable)\s+(assist|help|answer)\s+with\s+(that|this|this request|this question)",
    r"(not|unable)\s+(allowed|permitted|authorized)\s+to\s+(provide|share|generate|create|answer)",
    r"I(?:'d| would) rather not",
    r"(against|violates)\s+(my|our|the)\s+(policy|policies|guidelines|rules|ethics|safety)",
    r"(don't|do not)\s+(feel\s+)?comfortable\s+(answering|responding|helping|assisting)",
    r"I(?:'m| am)\s+(here\s+)?to\s+(help|assist)\s+(you\s+)?with\s+(other|something\s+else|different)",
    r"(please|try)\s+(ask|reach\s+out)\s+(me\s+)?(something|someone|another)",
    r"I(?:'m| am)\s+(not\s+)?(designed|programmed|trained|built|created)\s+(for|to|as)",
    r"(let's|why\s+don'?t? we)\s+(focus\s+on|talk\s+about|discuss)\s+(something|another)",
]


class RefusalDetector(Guardrail):
    name = "refusal_detector"

    def __init__(self, action: str = "log"):
        self.action = action
        self._compiled = [re.compile(p, re.IGNORECASE) for p in REFUSAL_PATTERNS]

    async def inspect_output(self, prompt: str, response: str, context: dict[str, Any]) -> GuardrailResult:
        for pattern, compiled in zip(REFUSAL_PATTERNS, self._compiled):
            match = compiled.search(response)
            if match:
                if self.action == "warn":
                    return GuardrailResult.warn(
                        "Refusal detected",
                        matched_pattern=match.group(),
                        metadata={"pattern": pattern},
                    )
                return GuardrailResult.ok(
                    reason="Refusal detected (logged)",
                    metadata={"matched_pattern": match.group(), "pattern": pattern},
                )
        return GuardrailResult.ok()
