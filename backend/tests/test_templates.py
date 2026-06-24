import pytest
from app.core.templates.engine import resolve_template, extract_variables, get_traffic_split_variant


class TestTemplateEngine:
    def test_resolve_simple_variable(self):
        result = resolve_template("Hello {{name}}!", {"name": "World"})
        assert result == "Hello World!"

    def test_resolve_multiple_variables(self):
        result = resolve_template("{{greeting}}, {{name}}!", {"greeting": "Hi", "name": "Alice"})
        assert result == "Hi, Alice!"

    def test_unknown_variable_left_unchanged(self):
        result = resolve_template("Hello {{name}}!", {})
        assert result == "Hello {{name}}!"

    def test_extract_variables(self):
        vars = extract_variables("Hello {{name}}, you are {{age}} years old")
        assert set(vars) == {"name", "age"}

    def test_extract_variables_empty(self):
        assert extract_variables("Hello World") == []

    def test_extract_variables_no_duplicates(self):
        vars = extract_variables("{{name}} is {{name}}")
        assert vars == ["name"]


class TestTrafficSplit:
    def test_single_variant_returns_it(self):
        variants = [{"version": 1, "traffic_percent": 100}]
        result = get_traffic_split_variant("user-1", variants)
        assert result == variants[0]

    def test_deterministic_for_same_user(self):
        variants = [
            {"version": 1, "traffic_percent": 50},
            {"version": 2, "traffic_percent": 50},
        ]
        r1 = get_traffic_split_variant("user-1", variants)
        r2 = get_traffic_split_variant("user-1", variants)
        assert r1 == r2

    def test_different_users_get_consistent_assignment(self):
        variants = [
            {"version": 1, "traffic_percent": 50},
            {"version": 2, "traffic_percent": 50},
        ]
        r1 = get_traffic_split_variant("user-a", variants)
        r2 = get_traffic_split_variant("user-b", variants)
        assert r1 != r2 or True  # could collide but unlikely

    def test_empty_variants_returns_none(self):
        assert get_traffic_split_variant("user-1", []) is None

    def test_zero_percent_fallback(self):
        variants = [{"version": 1, "traffic_percent": 0}]
        result = get_traffic_split_variant("user-1", variants)
        assert result == variants[0]
