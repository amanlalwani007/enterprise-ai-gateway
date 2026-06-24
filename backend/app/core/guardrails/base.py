from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Literal, Any

GuardrailAction = Literal["allow", "block", "warn", "mask"]


@dataclass
class GuardrailResult:
    passed: bool
    action: GuardrailAction = "allow"
    reason: str = ""
    matched_pattern: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def ok(cls, reason: str = "", metadata: dict | None = None) -> "GuardrailResult":
        return cls(passed=True, action="allow", reason=reason, metadata=metadata or {})

    @classmethod
    def block(cls, reason: str, matched_pattern: str | None = None, metadata: dict | None = None) -> "GuardrailResult":
        return cls(passed=False, action="block", reason=reason, matched_pattern=matched_pattern, metadata=metadata or {})

    @classmethod
    def warn(cls, reason: str, matched_pattern: str | None = None, metadata: dict | None = None) -> "GuardrailResult":
        return cls(passed=True, action="warn", reason=reason, matched_pattern=matched_pattern, metadata=metadata or {})

    @classmethod
    def mask(cls, reason: str, matched_pattern: str | None = None, metadata: dict | None = None) -> "GuardrailResult":
        return cls(passed=True, action="mask", reason=reason, matched_pattern=matched_pattern, metadata=metadata or {})


class Guardrail(ABC):
    name: str

    async def inspect_input(self, prompt: str, context: dict[str, Any]) -> GuardrailResult:
        return GuardrailResult.ok()

    async def inspect_output(self, prompt: str, response: str, context: dict[str, Any]) -> GuardrailResult:
        return GuardrailResult.ok()
