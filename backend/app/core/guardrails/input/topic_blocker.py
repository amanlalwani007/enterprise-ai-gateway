import os
import re
from typing import Any
from app.core.guardrails.base import Guardrail, GuardrailResult

DEFAULT_BLOCKED_TOPICS: list[dict[str, Any]] = []


class TopicBlocker(Guardrail):
    name = "topic_blocker"

    def __init__(self, action: str = "block", config_path: str | None = None):
        self.action = action
        self._topics = self._load_topics(config_path)
        self._compiled = [
            (topic["name"], re.compile(topic["pattern"], re.IGNORECASE), topic.get("action", action))
            for topic in self._topics
        ]

    def _load_topics(self, config_path: str | None = None) -> list[dict[str, Any]]:
        path = config_path or ""
        if path and os.path.isfile(path):
            try:
                import yaml
                with open(path) as f:
                    data = yaml.safe_load(f)
                    return data.get("topics", DEFAULT_BLOCKED_TOPICS)
            except Exception:
                pass
        return list(DEFAULT_BLOCKED_TOPICS)

    async def inspect_input(self, prompt: str, context: dict[str, Any]) -> GuardrailResult:
        for topic_name, compiled, topic_action in self._compiled:
            match = compiled.search(prompt)
            if match:
                effective_action = topic_action or self.action
                if effective_action == "block":
                    return GuardrailResult.block(
                        f"Blocked topic: {topic_name}",
                        matched_pattern=match.group(),
                        metadata={"topic": topic_name},
                    )
                if effective_action == "warn":
                    return GuardrailResult.warn(
                        f"Blocked topic detected (warn): {topic_name}",
                        matched_pattern=match.group(),
                        metadata={"topic": topic_name},
                    )
        return GuardrailResult.ok()
