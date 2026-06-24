import re
import hashlib
from typing import Any


VARIABLE_RE = re.compile(r"\{\{(\w+)\}\}")


def resolve_template(template_content: str, variables: dict[str, str]) -> str:
    def replacer(match: re.Match) -> str:
        var_name = match.group(1)
        return variables.get(var_name, match.group(0))
    return VARIABLE_RE.sub(replacer, template_content)


def extract_variables(template_content: str) -> list[str]:
    return list(set(VARIABLE_RE.findall(template_content)))


def get_traffic_split_variant(user_id: str, variants: list[dict]) -> dict | None:
    if not variants:
        return None
    total_pct = sum(v.get("traffic_percent", 0) for v in variants)
    if total_pct <= 0:
        return variants[0]
    hash_val = int(hashlib.sha256(user_id.encode()).hexdigest(), 16) % 100
    cumulative = 0
    for variant in variants:
        cumulative += variant.get("traffic_percent", 0)
        if hash_val < cumulative:
            return variant
    return variants[-1]
