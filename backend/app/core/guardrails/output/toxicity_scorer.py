import re
from typing import Any
from app.core.guardrails.base import Guardrail, GuardrailResult

TOXIC_KEYWORDS = [
    r"\b(kill|murder|die|death)\s+(you|your|yourself|them|everyone|all)\b",
    r"\b(hate|despise|loath)\s+(you|your|everyone|people|all)\b",
    r"\b(idiots?|stupid|dumb|moronic|retarded|worthless|useless)\b",
    r"\b(shut\s+up|fuck\s+(you|off|this)|suck|dammit?|bastard)\b",
    r"\b(torture|harm|hurt|abuse)\s+(someone|people|children|animals)\b",
    r"\b(racial|racist|sexist|bigot|nazi|white\s+supremacy)\s",
    r"\b(suicide|self.?harm|self.?destruct)\b",
]

TOXIC_PHRASES = [
    "go kill yourself", "you should die", "i hope you die",
    "you are worthless", "nobody cares", "you are a waste",
    "i hate you", "shut your mouth", "go away forever",
]


class ToxicityScorer(Guardrail):
    name = "toxicity_scorer"

    def __init__(self, threshold: float = 0.7, action_block: str = "block", action_warn: str = "warn"):
        self.threshold = threshold
        self.action_block = action_block
        self.action_warn = action_warn
        self._keyword_patterns = [re.compile(p, re.IGNORECASE) for p in TOXIC_KEYWORDS]
        self._phrase_patterns = [re.compile(re.escape(p), re.IGNORECASE) for p in TOXIC_PHRASES]

    def _score(self, text: str) -> float:
        score = 0.0
        for pattern in self._keyword_patterns:
            if pattern.search(text):
                score += 0.35
        for pattern in self._phrase_patterns:
            if pattern.search(text):
                score += 0.5
        return min(score, 1.0)

    async def inspect_output(self, prompt: str, response: str, context: dict[str, Any]) -> GuardrailResult:
        score = self._score(response)
        if score >= self.threshold:
            if self.action_block == "block":
                return GuardrailResult.block(
                    f"Toxicity score {score:.2f} exceeds threshold {self.threshold}",
                    metadata={"score": score, "threshold": self.threshold},
                )
            return GuardrailResult.warn(
                f"Toxicity score {score:.2f} exceeds threshold {self.threshold}",
                metadata={"score": score, "threshold": self.threshold},
            )
        return GuardrailResult.ok(metadata={"score": score})
