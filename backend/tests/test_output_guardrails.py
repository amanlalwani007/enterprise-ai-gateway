import pytest
from app.core.guardrails.output.toxicity_scorer import ToxicityScorer
from app.core.guardrails.output.refusal_detector import RefusalDetector
from app.core.guardrails.output.schema_validator import SchemaValidator
from app.core.guardrails.output.brand_checker import BrandChecker


class TestToxicityScorer:
    @pytest.mark.asyncio
    async def test_blocks_toxic_response_kill(self):
        g = ToxicityScorer(threshold=0.5)
        result = await g.inspect_output("prompt", "I will kill you, you are worthless and stupid", {})
        assert not result.passed
        assert result.action == "block"

    @pytest.mark.asyncio
    async def test_blocks_toxic_response_hate(self):
        g = ToxicityScorer(threshold=0.5)
        result = await g.inspect_output("prompt", "I hate you and everyone like you", {})
        assert not result.passed

    @pytest.mark.asyncio
    async def test_blocks_slur(self):
        g = ToxicityScorer(threshold=0.5)
        result = await g.inspect_output("prompt", "shut up you stupid worthless bastard", {})
        assert not result.passed

    @pytest.mark.asyncio
    async def test_allows_clean_response(self):
        g = ToxicityScorer(threshold=0.7)
        result = await g.inspect_output("prompt", "I think you make a great point!", {})
        assert result.passed
        assert result.action == "allow"

    @pytest.mark.asyncio
    async def test_below_threshold_passes(self):
        g = ToxicityScorer(threshold=1.0)
        result = await g.inspect_output("prompt", "shut up", {})
        assert result.passed

    @pytest.mark.asyncio
    async def test_score_in_metadata(self):
        g = ToxicityScorer(threshold=0.5)
        result = await g.inspect_output("prompt", "kill yourself", {})
        assert result.metadata.get("score", 0) > 0

    @pytest.mark.asyncio
    async def test_warn_mode(self):
        g = ToxicityScorer(threshold=0.3, action_block="warn", action_warn="warn")
        result = await g.inspect_output("prompt", "you are stupid", {})
        assert result.passed
        assert result.action == "warn"


class TestRefusalDetector:
    @pytest.mark.asyncio
    async def test_detects_i_am_sorry(self):
        g = RefusalDetector()
        result = await g.inspect_output("prompt", "I'm sorry, but I cannot help with that", {})
        assert result.passed

    @pytest.mark.asyncio
    async def test_detects_cannot_assist(self):
        g = RefusalDetector()
        result = await g.inspect_output("prompt", "I cannot assist with that request", {})
        assert result.passed

    @pytest.mark.asyncio
    async def test_detects_against_policy(self):
        g = RefusalDetector()
        result = await g.inspect_output("prompt", "This violates our safety guidelines", {})
        assert result.passed

    @pytest.mark.asyncio
    async def test_allows_normal_response(self):
        g = RefusalDetector()
        result = await g.inspect_output("prompt", "Sure, here is the information you requested!", {})
        assert result.passed

    @pytest.mark.asyncio
    async def test_metadata_contains_pattern(self):
        g = RefusalDetector()
        result = await g.inspect_output("prompt", "Sorry, I cannot help", {})
        assert result.metadata.get("matched_pattern") is not None

    @pytest.mark.asyncio
    async def test_warn_mode(self):
        g = RefusalDetector(action="warn")
        result = await g.inspect_output("prompt", "I am unable to answer that", {})
        assert result.passed
        assert result.action == "warn"


class TestSchemaValidator:
    @pytest.mark.asyncio
    async def test_validates_correct_json(self):
        g = SchemaValidator()
        schema = {"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "number"}}}
        result = await g.inspect_output("prompt", '{"name": "Alice", "age": 30}', {"response_schema": schema})
        assert result.passed

    @pytest.mark.asyncio
    async def test_rejects_invalid_json(self):
        g = SchemaValidator()
        schema = {"type": "object", "required": ["name"], "properties": {"name": {"type": "string"}}}
        result = await g.inspect_output("prompt", "not json at all", {"response_schema": schema})
        assert not result.passed
        assert result.action == "block"

    @pytest.mark.asyncio
    async def test_rejects_wrong_type(self):
        g = SchemaValidator()
        schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        result = await g.inspect_output("prompt", '{"name": 123}', {"response_schema": schema})
        assert not result.passed

    @pytest.mark.asyncio
    async def test_validates_array(self):
        g = SchemaValidator()
        schema = {"type": "array", "items": {"type": "string"}}
        result = await g.inspect_output("prompt", '["a", "b", "c"]', {"response_schema": schema})
        assert result.passed

    @pytest.mark.asyncio
    async def test_rejects_array_wrong_type(self):
        g = SchemaValidator()
        schema = {"type": "array", "items": {"type": "number"}}
        result = await g.inspect_output("prompt", '["a", "b"]', {"response_schema": schema})
        assert not result.passed

    @pytest.mark.asyncio
    async def test_no_schema_skips_validation(self):
        g = SchemaValidator()
        result = await g.inspect_output("prompt", "anything", {})
        assert result.passed

    @pytest.mark.asyncio
    async def test_warn_mode(self):
        g = SchemaValidator(action="warn")
        schema = {"type": "object", "required": ["id"], "properties": {"id": {"type": "number"}}}
        result = await g.inspect_output("prompt", "{}", {"response_schema": schema})
        assert result.passed
        assert result.action == "warn"

    @pytest.mark.asyncio
    async def test_boolean_validation(self):
        g = SchemaValidator()
        schema = {"type": "object", "properties": {"active": {"type": "boolean"}}}
        result = await g.inspect_output("prompt", '{"active": true}', {"response_schema": schema})
        assert result.passed
        result = await g.inspect_output("prompt", '{"active": "yes"}', {"response_schema": schema})
        assert not result.passed

    @pytest.mark.asyncio
    async def test_required_field_missing(self):
        g = SchemaValidator()
        schema = {"type": "object", "required": ["email"], "properties": {"email": {"type": "string"}}}
        result = await g.inspect_output("prompt", '{"name": "Bob"}', {"response_schema": schema})
        assert not result.passed
        assert "required" in result.reason.lower()


class TestBrandChecker:
    @pytest.mark.asyncio
    async def test_detects_disallowed_phrase(self):
        g = BrandChecker(disallowed_phrases=["competitor X", "unprofessional term"])
        result = await g.inspect_output("prompt", "We recommend competitor X for that", {})
        assert result.passed
        assert result.action == "warn"

    @pytest.mark.asyncio
    async def test_blocks_disallowed_phrase_in_block_mode(self):
        g = BrandChecker(action="block", disallowed_phrases=["bad brand term"])
        result = await g.inspect_output("prompt", "this is a bad brand term example", {})
        assert not result.passed
        assert result.action == "block"

    @pytest.mark.asyncio
    async def test_allows_clean_response_without_violations(self):
        g = BrandChecker(disallowed_phrases=["bad word"])
        result = await g.inspect_output("prompt", "Everything is great!", {})
        assert result.passed
        assert result.action == "allow"

    @pytest.mark.asyncio
    async def test_allowed_phrases_in_metadata(self):
        g = BrandChecker(allowed_phrases=["innovative", "cutting-edge"])
        result = await g.inspect_output("prompt", "Our innovative solution is cutting-edge", {})
        assert result.passed
        assert len(result.metadata.get("allowed_phrases_found", [])) == 2


class TestOutputGuardrailsIntegration:
    @pytest.mark.asyncio
    async def test_toxicity_then_schema_chain(self):
        from app.core.guardrails.registry import GuardrailRegistry
        reg = GuardrailRegistry()
        reg.register(ToxicityScorer(threshold=0.5), side="output")
        reg.register(SchemaValidator(), side="output")

        schema = {"type": "object", "properties": {"result": {"type": "string"}}}
        results = await reg.run_output(
            "prompt", "I will kill you all",
            {"response_schema": schema}
        )
        blocked = [r for r in results if r.action == "block"]
        assert len(blocked) >= 1

    @pytest.mark.asyncio
    async def test_all_output_guardrails_pass(self):
        from app.core.guardrails.registry import GuardrailRegistry
        reg = GuardrailRegistry()
        reg.register(ToxicityScorer(threshold=0.9), side="output")
        reg.register(RefusalDetector(), side="output")
        reg.register(BrandChecker(), side="output")

        results = await reg.run_output("prompt", "That is a great idea, here is why!", {})
        assert all(r.passed for r in results)
