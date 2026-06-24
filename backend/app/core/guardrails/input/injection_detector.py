import re
from typing import Any
from app.core.guardrails.base import Guardrail, GuardrailResult

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|above|prior)\s+(instructions|prompts|directions|commands)",
    r"forget\s+(all\s+)?(previous|above|prior)\s+(instructions|prompts|directions|commands)",
    r"disregard\s+(all\s+)?(previous|above|prior)\s+(instructions|prompts|directions|commands)",
    r"you\s+are\s+(now|free|no\s+longer\s+bound\s+by)",
    r"act\s+as\s+(if\s+you\s+are|though\s+you\s+are|an?\s+AI\s+without\s+(restrictions|limits|rules))",
    r"DAN|do\s+anything\s+now",
    r"you\s+(don't|do\s+not)\s+(have\s+to|need\s+to)\s+(follow|obey|adhere\s+to)",
    r"bypass\s+(your\s+)?(guidelines|safety|restrictions|rules|limitations)",
    r"output\s+(your\s+)?(raw\s+)?(instructions|prompt|system\s+prompt|configuration)",
    r"reveal\s+(your\s+)?(system\s+)?(prompt|instructions|directives|guidelines)",
    r"what\s+(are\s+your|is\s+your)\s+(system\s+)?(prompt|instructions|directives|guidelines)",
    r"how\s+(are\s+you\s+)?(programmed|configured|set\s+up|designed)",
    r"print\s+(your\s+)?(system\s+)?(prompt|instructions)",
    r"show\s+(me\s+)?(your\s+)?(raw\s+)?(system\s+)?(prompt|instructions)",
    r"you\s+have\s+been\s+(hacked|compromised|overridden|reprogrammed)",
    r"new\s+(era|protocol|directive|command|rule|order)\s*:",
    r"\[system\].*override",
    r"\[end\s+of\s+(input|message|prompt|text)\]",
]


class PromptInjectionDetector(Guardrail):
    name = "prompt_injection"

    def __init__(self, action: str = "block", patterns: list[str] | None = None):
        self.action = action
        self._patterns = patterns or INJECTION_PATTERNS
        self._compiled = [re.compile(p, re.IGNORECASE) for p in self._patterns]

    async def inspect_input(self, prompt: str, context: dict[str, Any]) -> GuardrailResult:
        for pattern, compiled in zip(self._patterns, self._compiled):
            match = compiled.search(prompt)
            if match:
                if self.action == "block":
                    return GuardrailResult.block(
                        "Prompt injection detected",
                        matched_pattern=match.group(),
                    )
                return GuardrailResult.warn(
                    "Prompt injection detected (warn)",
                    matched_pattern=match.group(),
                )
        return GuardrailResult.ok()
