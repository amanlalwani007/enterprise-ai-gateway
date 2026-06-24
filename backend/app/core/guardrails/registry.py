from typing import Any
from app.core.guardrails.base import Guardrail, GuardrailResult
from app.core.guardrails.config import load_guardrail_config
from app.core.config import settings


class GuardrailRegistry:
    def __init__(self):
        self._input_guardrails: list[Guardrail] = []
        self._output_guardrails: list[Guardrail] = []

    def register(self, guardrail: Guardrail, side: str = "input") -> None:
        if side == "input":
            self._input_guardrails.append(guardrail)
        else:
            self._output_guardrails.append(guardrail)

    @property
    def input_guardrails(self) -> list[Guardrail]:
        return list(self._input_guardrails)

    @property
    def output_guardrails(self) -> list[Guardrail]:
        return list(self._output_guardrails)

    async def run_input(self, prompt: str, context: dict[str, Any]) -> list[GuardrailResult]:
        results: list[GuardrailResult] = []
        for g in self._input_guardrails:
            result = await g.inspect_input(prompt, context)
            results.append(result)
            if result.action == "block":
                break
        return results

    async def run_output(self, prompt: str, response: str, context: dict[str, Any]) -> list[GuardrailResult]:
        results: list[GuardrailResult] = []
        for g in self._output_guardrails:
            result = await g.inspect_output(prompt, response, context)
            results.append(result)
            if result.action == "block":
                break
        return results

    def clear(self) -> None:
        self._input_guardrails.clear()
        self._output_guardrails.clear()

    def load_from_config(self, config_path: str | None = None) -> None:
        cfg = load_guardrail_config(config_path)
        for entry in cfg.get("input", []):
            guardrail = self._instantiate(entry)
            if guardrail:
                self.register(guardrail, side="input")
        for entry in cfg.get("output", []):
            guardrail = self._instantiate(entry)
            if guardrail:
                self.register(guardrail, side="output")

    def _instantiate(self, entry: dict) -> Guardrail | None:
        class_path = entry.get("class")
        if not class_path:
            return None
        try:
            import importlib
            mod_name, cls_name = class_path.rsplit(".", 1)
            mod = importlib.import_module(mod_name)
            cls = getattr(mod, cls_name)
            params = entry.get("params", {})
            return cls(**params)
        except Exception:
            return None


registry = GuardrailRegistry()

if settings.GUARDRAILS_ENABLED:
    registry.load_from_config(settings.GUARDRAILS_CONFIG_PATH)
