import pytest
from app.core.query_classifier import classify_query, get_strategy, extract_keywords

class TestQueryClassifier:
    def test_classify_factual_what_is(self):
        assert classify_query("What is the capital of France?") == "factual"

    def test_classify_factual_explain(self):
        assert classify_query("Explain quantum computing in simple terms") == "factual"

    def test_classify_code_def(self):
        assert classify_query("Write a Python function to sort a list") == "code"

    def test_classify_code_import(self):
        assert classify_query("import React from 'react' — what does this do?") == "code"

    def test_classify_creative_poem(self):
        assert classify_query("Write a poem about artificial intelligence") == "creative"

    def test_classify_creative_story(self):
        assert classify_query("Tell me a story about a robot learning to paint") == "creative"

    def test_classify_analytical_compare(self):
        assert classify_query("Compare and contrast Python and JavaScript") == "analytical"

    def test_classify_analytical_pros_cons(self):
        assert classify_query("What are the pros and cons of using microservices?") == "analytical"

    def test_classify_conversational_greeting(self):
        assert classify_query("Hello") == "conversational"

    def test_classify_conversational_thanks(self):
        assert classify_query("thank you") == "conversational"

    def test_classify_long_default_analytical(self):
        long = " ".join(["word"] * 60)
        assert classify_query(long) == "analytical"

class TestGetStrategy:
    def test_factual_strategy(self):
        s = get_strategy("factual")
        assert s["threshold"] >= 0.90
        assert s["ttl_seconds"] > 86400

    def test_code_strategy(self):
        s = get_strategy("code")
        assert s["threshold"] > 0.95
        assert s["use_keyword_fallback"] is True

    def test_creative_strategy(self):
        s = get_strategy("creative")
        assert s["threshold"] < 0.90
        assert s["ttl_seconds"] <= 3600

    def test_conversational_strategy(self):
        s = get_strategy("conversational")
        assert s["threshold"] < 0.85
        assert s["use_keyword_fallback"] is False

class TestExtractKeywords:
    def test_basic_keywords(self):
        result = extract_keywords("What is the capital of France?")
        assert "capital" in result
        assert "france" in result
        assert "what" not in result

    def test_stop_words_removed(self):
        result = extract_keywords("The quick brown fox jumps over the lazy dog")
        assert "quick" in result
        assert "brown" in result
        assert "the" not in result
        assert "over" not in result

    def test_max_keywords(self):
        result = extract_keywords("apple banana cherry date elderberry fig grape honeydew", max_keywords=3)
        assert len(result) <= 3
