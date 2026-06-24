import os
import tempfile
import yaml
import pytest
from app.core.guardrails.base import Guardrail, GuardrailResult
from app.core.guardrails.registry import GuardrailRegistry


# --- Mock guardrails for testing ---

class AllowGuardrail(Guardrail):
    name = "allow_all"

    async def inspect_input(self, prompt, context):
        return GuardrailResult.ok()

    async def inspect_output(self, prompt, response, context):
        return GuardrailResult.ok()


class BlockInputGuardrail(Guardrail):
    name = "block_bad_input"

    async def inspect_input(self, prompt, context):
        if "bad" in prompt.lower():
            return GuardrailResult.block("Bad input detected", matched_pattern="bad")
        return GuardrailResult.ok()

    async def inspect_output(self, prompt, response, context):
        return GuardrailResult.ok()


class BlockOutputGuardrail(Guardrail):
    name = "block_bad_output"

    async def inspect_input(self, prompt, context):
        return GuardrailResult.ok()

    async def inspect_output(self, prompt, response, context):
        if "bad" in response.lower():
            return GuardrailResult.block("Bad output detected", matched_pattern="bad")
        return GuardrailResult.ok()


class WarnGuardrail(Guardrail):
    name = "warn_test"

    async def inspect_input(self, prompt, context):
        if "warn" in prompt.lower():
            return GuardrailResult.warn("Warning triggered", matched_pattern="warn")
        return GuardrailResult.ok()

    async def inspect_output(self, prompt, response, context):
        return GuardrailResult.ok()


# --- GuardrailResult tests ---

class TestGuardrailResult:
    def test_ok_result(self):
        r = GuardrailResult.ok("all good")
        assert r.passed
        assert r.action == "allow"
        assert r.reason == "all good"

    def test_block_result(self):
        r = GuardrailResult.block("blocked", matched_pattern="test")
        assert not r.passed
        assert r.action == "block"
        assert r.matched_pattern == "test"

    def test_warn_result(self):
        r = GuardrailResult.warn("warning")
        assert r.passed
        assert r.action == "warn"

    def test_mask_result(self):
        r = GuardrailResult.mask("masked", metadata={"field": "email"})
        assert r.passed
        assert r.action == "mask"
        assert r.metadata["field"] == "email"


# --- GuardrailRegistry tests ---

class TestGuardrailRegistry:
    @pytest.mark.asyncio
    async def test_register_and_run_input_allow(self):
        reg = GuardrailRegistry()
        reg.register(AllowGuardrail(), side="input")
        results = await reg.run_input("hello", {})
        assert len(results) == 1
        assert results[0].passed

    @pytest.mark.asyncio
    async def test_register_and_run_input_block(self):
        reg = GuardrailRegistry()
        reg.register(BlockInputGuardrail(), side="input")
        results = await reg.run_input("bad stuff", {})
        assert len(results) == 1
        assert not results[0].passed
        assert results[0].action == "block"

    @pytest.mark.asyncio
    async def test_input_block_stops_execution(self):
        reg = GuardrailRegistry()
        reg.register(BlockInputGuardrail(), side="input")
        reg.register(WarnGuardrail(), side="input")
        results = await reg.run_input("bad stuff here", {})
        assert len(results) == 1
        assert results[0].action == "block"

    @pytest.mark.asyncio
    async def test_input_allows_through(self):
        reg = GuardrailRegistry()
        reg.register(AllowGuardrail(), side="input")
        reg.register(WarnGuardrail(), side="input")
        results = await reg.run_input("normal query", {})
        assert len(results) == 2
        assert all(r.passed for r in results)

    @pytest.mark.asyncio
    async def test_output_guardrails(self):
        reg = GuardrailRegistry()
        reg.register(BlockOutputGuardrail(), side="output")
        results = await reg.run_output("prompt", "this is bad output", {})
        assert len(results) == 1
        assert not results[0].passed
        assert results[0].action == "block"

    @pytest.mark.asyncio
    async def test_output_allows_good(self):
        reg = GuardrailRegistry()
        reg.register(BlockOutputGuardrail(), side="output")
        results = await reg.run_output("prompt", "good output", {})
        assert len(results) == 1
        assert results[0].passed

    def test_separate_input_output_lists(self):
        reg = GuardrailRegistry()
        reg.register(BlockInputGuardrail(), side="input")
        reg.register(BlockOutputGuardrail(), side="output")
        assert len(reg.input_guardrails) == 1
        assert len(reg.output_guardrails) == 1
        assert reg.input_guardrails[0].name == "block_bad_input"
        assert reg.output_guardrails[0].name == "block_bad_output"

    def test_clear_registry(self):
        reg = GuardrailRegistry()
        reg.register(AllowGuardrail(), side="input")
        reg.clear()
        assert len(reg.input_guardrails) == 0
        assert len(reg.output_guardrails) == 0

    @pytest.mark.asyncio
    async def test_warn_does_not_block(self):
        reg = GuardrailRegistry()
        reg.register(WarnGuardrail(), side="input")
        results = await reg.run_input("this is a warn test", {})
        assert len(results) == 1
        assert results[0].passed
        assert results[0].action == "warn"

    def test_load_from_yaml_config(self):
        config = {
            "input": [
                {"class": "tests.test_guardrails.BlockInputGuardrail", "params": {}}
            ],
            "output": [
                {"class": "tests.test_guardrails.BlockOutputGuardrail", "params": {}}
            ]
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config, f)
            config_path = f.name

        try:
            reg = GuardrailRegistry()
            reg.load_from_config(config_path)
            assert len(reg.input_guardrails) == 1
            assert len(reg.output_guardrails) == 1
            assert reg.input_guardrails[0].name == "block_bad_input"
            assert reg.output_guardrails[0].name == "block_bad_output"
        finally:
            os.unlink(config_path)

    def test_load_from_empty_config(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump({"input": [], "output": []}, f)
            config_path = f.name

        try:
            reg = GuardrailRegistry()
            reg.load_from_config(config_path)
            assert len(reg.input_guardrails) == 0
            assert len(reg.output_guardrails) == 0
        finally:
            os.unlink(config_path)

    def test_load_from_missing_file(self):
        reg = GuardrailRegistry()
        reg.load_from_config("/nonexistent/path.yaml")
        assert len(reg.input_guardrails) == 0
        assert len(reg.output_guardrails) == 0


# --- Integration test: full pipeline ---

class TestGuardrailPipeline:
    @pytest.mark.asyncio
    async def test_input_block_returns_403(self):
        reg = GuardrailRegistry()
        reg.register(BlockInputGuardrail(), side="input")

        results = await reg.run_input("bad query", {"api_key": "test"})
        blocked = [r for r in results if r.action == "block"]
        assert len(blocked) == 1

    @pytest.mark.asyncio
    async def test_output_block_returns_error(self):
        reg = GuardrailRegistry()
        reg.register(BlockOutputGuardrail(), side="output")

        results = await reg.run_output("good prompt", "bad response", {"api_key": "test"})
        blocked = [r for r in results if r.action == "block"]
        assert len(blocked) == 1

    @pytest.mark.asyncio
    async def test_pipeline_allow(self):
        reg = GuardrailRegistry()
        reg.register(AllowGuardrail(), side="input")
        reg.register(AllowGuardrail(), side="output")

        input_results = await reg.run_input("hello", {})
        output_results = await reg.run_output("hello", "world", {})

        assert all(r.passed for r in input_results)
        assert all(r.passed for r in output_results)

    @pytest.mark.asyncio
    async def test_warn_passes_through(self):
        reg = GuardrailRegistry()
        reg.register(WarnGuardrail(), side="input")

        results = await reg.run_input("this is a warn me query", {})
        assert len(results) == 1
        assert results[0].passed
        assert results[0].action == "warn"
