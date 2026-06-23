import fnmatch
import json
import os
from typing import Any

class Route:
    def __init__(self, pattern: str, provider: str, model: str | None = None, max_budget: float | None = None, fallback: str | None = None):
        self.pattern = pattern
        self.provider = provider
        self.model = model
        self.max_budget = max_budget
        self.fallback = fallback

    def matches(self, model_name: str) -> bool:
        return fnmatch.fnmatch(model_name, self.pattern)

class ModelRouter:
    def __init__(self, routes_file: str | None = None):
        self.routes: list[Route] = []
        if routes_file and os.path.exists(routes_file):
            self.load_from_file(routes_file)

    def load_from_file(self, path: str):
        with open(path) as f:
            data = json.load(f)
        for entry in data.get("routes", []):
            self.routes.append(Route(**entry))

    def add_route(self, pattern: str, provider: str, model: str | None = None, max_budget: float | None = None, fallback: str | None = None):
        self.routes.append(Route(pattern, provider, model, max_budget, fallback))

    def route_for(self, model_name: str) -> Route | None:
        for route in self.routes:
            if route.matches(model_name):
                return route
        return None

    def resolve(self, model_name: str) -> dict[str, Any]:
        route = self.route_for(model_name)
        if not route:
            return {"model": model_name, "provider": None, "fallback": None}
        resolved_model = route.model or model_name
        resolved = {"model": resolved_model, "provider": route.provider, "fallback": route.fallback}
        if route.max_budget is not None:
            resolved["max_budget"] = route.max_budget
        return resolved


router = ModelRouter()

def init_routes():
    routes_json = os.getenv("MODEL_ROUTES")
    if routes_json:
        data = json.loads(routes_json)
        for entry in data:
            router.add_route(**entry)
    else:
        router.add_route("gpt-4*", "openai")
        router.add_route("gpt-3.5*", "openai")
        router.add_route("claude-*", "anthropic")
        router.add_route("gemini-*", "gemini")
        router.add_route("*", "openai")
