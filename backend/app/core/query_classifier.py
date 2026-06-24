import re
from typing import Literal

QueryType = Literal["factual", "code", "creative", "analytical", "conversational"]

CODE_INDICATORS = [
    r"def\s+\w+\s*\(", r"function\s+\w+\s*\(", r"class\s+\w+", r"import\s+\w+",
    r"const\s+\w+\s*=", r"let\s+\w+\s*=", r"var\s+\w+\s*=", r"```\w*",
    r"write\s+a\s+(python|javascript|rust|go|typescript|java|sql)\s+(function|program|script|class)",
    r"explain\s+(this\s+)?code", r"what\s+does\s+this\s+code\s+do", r"regex\s+(for|to|pattern)",
    r"git\s+command", r"terminal|bash|shell\s+command",
    r"npm|pip|yarn|cargo|go\s+get", r"api\s+endpoint",
]

FACTUAL_INDICATORS = [
    r"what\s+(is|are|was|were|does)\s", r"who\s+(is|was|are)\s",
    r"when\s+(did|was|were|is)\s", r"where\s+(is|are|was|were)\s",
    r"why\s+(is|are|do|does|did)\s", r"how\s+(many|much|long|far|tall|old)\s",
    r"define\s", r"explain\s", r"summarize\s", r"list\s",
    r"what's\s", r"tell\s+me\s+(about|what|how)",
    r"difference\s+between", r"meaning\s+of",
    r"capital\s+of", r"population\s+of",
]

CREATIVE_INDICATORS = [
    r"write\s+(a|an|me)\s+(poem|story|essay|article|blog|letter|email|song)",
    r"create\s+(a|an)\s+(story|poem|character|world|plot)",
    r"compose\s+(a|an)\s+(poem|song|melody|music|lyrics)",
    r"generate\s+(a|an)\s+(story|poem|image\s+prompt|idea)",
    r"imagine\s", r"make\s+(up|me)\s+(a|an)\s+(story|poem)",
    r"tell\s+me\s+a\s+(story|joke|riddle|bedtime\s+story)",
    r"draft\s+(a|an)\s+(email|letter|proposal|outline)",
]

ANALYTICAL_INDICATORS = [
    r"compare\s+(and\s+)?contrast", r"analyze\s", r"evaluate\s",
    r"pros\s+and\s+cons", r"advantages?\s+and\s+disadvantages?",
    r"strengths?\s+and\s+weaknesses?", r"trade.?offs?",
    r"what\s+are\s+the\s+(key|main|primary|critical)\s+(differences|factors|aspects|implications)",
    r"impact\s+of", r"effect\s+of", r"relationship\s+between",
    r"correlation", r"trend", r"predict\s",
]


def classify_query(prompt: str) -> QueryType:
    lowered = prompt.strip().lower()
    word_count = len(lowered.split())

    # Code check first (highest priority)
    for pattern in CODE_INDICATORS:
        if re.search(pattern, lowered, re.IGNORECASE):
            return "code"

    # Short or greeting-like queries
    if word_count <= 3:
        greetings = {"hello", "hi", "hey", "thanks", "thank you", "goodbye", "bye", "ok", "okay"}
        if lowered.strip() in greetings or any(g in lowered for g in greetings):
            return "conversational"

    # Check creative indicators
    for pattern in CREATIVE_INDICATORS:
        if re.search(pattern, lowered, re.IGNORECASE):
            return "creative"

    # Check analytical indicators
    for pattern in ANALYTICAL_INDICATORS:
        if re.search(pattern, lowered, re.IGNORECASE):
            return "analytical"

    # Check factual indicators
    for pattern in FACTUAL_INDICATORS:
        if re.search(pattern, lowered, re.IGNORECASE):
            return "factual"

    # Long queries tend to be analytical or factual
    if word_count > 50:
        return "analytical"

    # Default for medium-length queries without clear indicators
    return "factual"


def get_strategy(query_type: QueryType) -> dict:
    strategies = {
        "factual": {
            "threshold": 0.94,
            "ttl_seconds": 604800,
            "use_keyword_fallback": True,
            "description": "High threshold, long cache life",
        },
        "code": {
            "threshold": 0.97,
            "ttl_seconds": 604800,
            "use_keyword_fallback": True,
            "description": "Very high threshold, exact-like matching",
        },
        "creative": {
            "threshold": 0.85,
            "ttl_seconds": 3600,
            "use_keyword_fallback": False,
            "description": "Low threshold, short cache life",
        },
        "analytical": {
            "threshold": 0.91,
            "ttl_seconds": 86400,
            "use_keyword_fallback": True,
            "description": "Medium threshold, daily cache life",
        },
        "conversational": {
            "threshold": 0.80,
            "ttl_seconds": 1800,
            "use_keyword_fallback": False,
            "description": "Low threshold, short cache life",
        },
    }
    return strategies.get(query_type, strategies["factual"])


def extract_keywords(prompt: str, max_keywords: int = 8) -> list[str]:
    stop_words = {
        "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "need", "dare", "ought",
        "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
        "as", "into", "through", "during", "before", "after", "above", "below",
        "between", "out", "off", "over", "under", "again", "further", "then",
        "once", "here", "there", "when", "where", "why", "how", "all", "each",
        "every", "both", "few", "more", "most", "other", "some", "such", "no",
        "nor", "not", "only", "own", "same", "so", "than", "too", "very",
        "just", "because", "but", "and", "or", "if", "while", "about", "up",
    }

    words = re.findall(r'\b[a-zA-Z]{3,}\b', prompt.lower())
    keywords = [w for w in words if w not in stop_words]
    return list(dict.fromkeys(keywords))[:max_keywords]
