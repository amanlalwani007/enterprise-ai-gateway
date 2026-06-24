import json
from typing import Any
from app.core.guardrails.base import Guardrail, GuardrailResult


class SchemaValidator(Guardrail):
    name = "schema_validator"

    def __init__(self, action: str = "block", schema: dict | None = None):
        self.action = action
        self._schema = schema

    async def inspect_output(self, prompt: str, response: str, context: dict[str, Any]) -> GuardrailResult:
        schema = context.get("response_schema") or self._schema
        if not schema:
            return GuardrailResult.ok(metadata={"reason": "no schema configured"})

        try:
            data = json.loads(response)
        except (json.JSONDecodeError, ValueError):
            if self.action == "block":
                return GuardrailResult.block(
                    "Response is not valid JSON",
                    metadata={"required_schema": str(schema)},
                )
            return GuardrailResult.warn(
                "Response is not valid JSON",
                metadata={"required_schema": str(schema)},
            )

        errors = self._validate(data, schema)
        if errors:
            if self.action == "block":
                return GuardrailResult.block(
                    f"Response failed schema validation: {errors[0]}",
                    metadata={"errors": errors, "required_schema": str(schema)},
                )
            return GuardrailResult.warn(
                f"Response failed schema validation: {errors[0]}",
                metadata={"errors": errors, "required_schema": str(schema)},
            )
        return GuardrailResult.ok()

    def _validate(self, data: Any, schema: dict, path: str = "") -> list[str]:
        errors: list[str] = []
        if "type" in schema:
            expected = schema["type"]
            if expected == "object":
                if not isinstance(data, dict):
                    errors.append(f"{path}: expected object, got {type(data).__name__}")
                    return errors
                for key, prop_schema in schema.get("properties", {}).items():
                    if key in data:
                        errors.extend(self._validate(data[key], prop_schema, f"{path}.{key}" if path else key))
                    elif key in schema.get("required", []):
                        errors.append(f"{path}.{key}: required field missing")
            elif expected == "array":
                if not isinstance(data, list):
                    errors.append(f"{path}: expected array, got {type(data).__name__}")
                    return errors
                item_schema = schema.get("items", {})
                for i, item in enumerate(data):
                    errors.extend(self._validate(item, item_schema, f"{path}[{i}]"))
            elif expected == "string":
                if not isinstance(data, str):
                    errors.append(f"{path}: expected string, got {type(data).__name__}")
            elif expected == "number":
                if not isinstance(data, (int, float)):
                    errors.append(f"{path}: expected number, got {type(data).__name__}")
            elif expected == "boolean":
                if not isinstance(data, bool):
                    errors.append(f"{path}: expected boolean, got {type(data).__name__}")
        return errors
