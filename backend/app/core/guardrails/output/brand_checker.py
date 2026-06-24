import re
from typing import Any
from app.core.guardrails.base import Guardrail, GuardrailResult


class BrandChecker(Guardrail):
    name = "brand_checker"

    def __init__(
        self,
        action: str = "warn",
        allowed_phrases: list[str] | None = None,
        disallowed_phrases: list[str] | None = None,
        tone_requirements: list[str] | None = None,
    ):
        self.action = action
        self._disallowed = [re.compile(re.escape(p), re.IGNORECASE) for p in (disallowed_phrases or [])]
        self._disallowed_raw = disallowed_phrases or []
        self._allowed = [(re.compile(re.escape(p), re.IGNORECASE), p) for p in (allowed_phrases or [])]
        self._tone = tone_requirements or []

    async def inspect_output(self, prompt: str, response: str, context: dict[str, Any]) -> GuardrailResult:
        violations: list[str] = []

        for pattern, raw in zip(self._disallowed, self._disallowed_raw):
            if pattern.search(response):
                violations.append(f"Disallowed phrase: '{raw}'")

        allowed_found = []
        for compiled, raw in self._allowed:
            if compiled.search(response):
                allowed_found.append(raw)

        if not violations and not self._tone:
            return GuardrailResult.ok(metadata={"allowed_phrases_found": allowed_found})

        if violations:
            if self.action == "block":
                return GuardrailResult.block(
                    f"Brand compliance violations: {'; '.join(violations)}",
                    metadata={"violations": violations},
                )
            return GuardrailResult.warn(
                f"Brand compliance violations: {'; '.join(violations)}",
                metadata={"violations": violations},
            )

        return GuardrailResult.ok(metadata={"allowed_phrases_found": allowed_found})
