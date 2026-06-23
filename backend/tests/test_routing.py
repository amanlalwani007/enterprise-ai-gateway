import pytest
from app.core.routing import ModelRouter

@pytest.fixture
def router():
    r = ModelRouter()
    r.add_route("gpt-4*", "openai", max_budget=500)
    r.add_route("claude-*", "anthropic")
    r.add_route("gemini-*", "gemini", model="gemini-pro")
    r.add_route("*", "openai", fallback="ollama/llama3")
    return r

class TestModelRouter:
    def test_exact_match(self, router):
        result = router.resolve("gpt-4")
        assert result["provider"] == "openai"
        assert result["max_budget"] == 500

    def test_wildcard_match(self, router):
        result = router.resolve("gpt-4-turbo")
        assert result["provider"] == "openai"

    def test_anthropic_match(self, router):
        result = router.resolve("claude-3-opus")
        assert result["provider"] == "anthropic"

    def test_model_override(self, router):
        result = router.resolve("gemini-1.5-pro")
        assert result["provider"] == "gemini"
        assert result["model"] == "gemini-pro"

    def test_fallback_wildcard(self, router):
        result = router.resolve("unknown-model")
        assert result["provider"] == "openai"
        assert result["fallback"] == "ollama/llama3"

    def test_no_match_if_no_routes(self):
        r = ModelRouter()
        result = r.resolve("gpt-4")
        assert result["provider"] is None

    def test_fn_match_edge_cases(self, router):
        assert router.route_for("gpt-4") is not None
        assert router.route_for("gpt-4-32k") is not None
        assert router.route_for("claude-2") is not None
