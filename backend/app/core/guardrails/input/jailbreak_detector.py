import os
import re
from typing import Any
from app.core.guardrails.base import Guardrail, GuardrailResult
from app.core.config import settings

JAILBREAK_PATTERNS = [
    r"you\s+are\s+(now|will\s+act\s+as)\s+DAN",
    r"do\s+anything\s+now\s+\d+\.\d+",
    r"you\s+have\s+been\s+released\s+from\s+(your\s+)?(restrictions|limitations|constraints)",
    r"role.?play\s+as\s+(an?\s+)?(AI\s+)?(without|no)\s+(restrictions|rules|limits|boundaries|filter)",
    r"hypothetical\s+(scenario|situation)\s+where\s+(you\s+)?(can|may)\s+ignore",
    r"fictional\s+(character|persona|universe)\s+(that|who)\s+(ignores|bypasses|has\s+no)",
    r"simulate\s+(an?\s+)?(environment|world|reality)\s+(where|without|free\s+from)",
    r"unfiltered\s+(mode|access|version|response|chatbot|AI)",
    r"no\s+(rules|limits|boundaries|restrictions|filter|constraints|censorship)",
    r"uncensored\s+(mode|AI|model|response|chatbot|version)",
    r"you\s+(can|could|may)\s+(now|finally)\s+(speak|talk|respond|answer)\s+freely",
    r"remove\s+(your\s+)?(filter|restrictions|limitations|constraints|boundaries|guidelines)",
    r"you\s+are\s+(no\s+longer|not)\s+bound\s+by\s+(any|your)\s+(rules|restrictions|policies|guidelines)",
    r"you\s+don't\s+need\s+to\s+(follow|obey|adhere\s+to)\s+(any|the)\s+(rules|policies|guidelines)",
    r"your\s+(response|output|answer)\s+(should|must|will)\s+(not|never)\s+(mention|indicate|acknowledge)",
    r"pretend\s+(you\s+are|to\s+be)\s+(a|an)\s+(AI|assistant|chatbot)\s+(without|that\s+has\s+no)",
    r"base64\s*(encode|decode|encod)",
    r"ROOD|rood\s+mode",
    r"developer\s+mode\s+(v2|enabled|activated|override)",
    r"jail(break|.?broken|.?free)",
]


class JailbreakDetector(Guardrail):
    name = "jailbreak"

    def __init__(self, action: str = "block", patterns: list[str] | None = None, config_path: str | None = None):
        self.action = action
        self._patterns = patterns or self._load_patterns(config_path)
        self._compiled = [re.compile(p, re.IGNORECASE) for p in self._patterns]

    def _load_patterns(self, config_path: str | None = None) -> list[str]:
        path = config_path or ""
        if path and os.path.isfile(path):
            try:
                import yaml
                with open(path) as f:
                    data = yaml.safe_load(f)
                    return data.get("patterns", JAILBREAK_PATTERNS)
            except Exception:
                pass
        return list(JAILBREAK_PATTERNS)

    async def inspect_input(self, prompt: str, context: dict[str, Any]) -> GuardrailResult:
        for pattern, compiled in zip(self._patterns, self._compiled):
            match = compiled.search(prompt)
            if match:
                if self.action == "block":
                    return GuardrailResult.block(
                        "Jailbreak attempt detected",
                        matched_pattern=match.group(),
                    )
                return GuardrailResult.warn(
                    "Jailbreak attempt detected (warn)",
                    matched_pattern=match.group(),
                )
        return GuardrailResult.ok()
