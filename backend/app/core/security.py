import re

# Simple regex patterns for common PII
PII_PATTERNS = {
    "EMAIL": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
    "CREDIT_CARD": r"\b(?:\d[ -]*?){13,16}\b",
    "PHONE": r"\b(?:\+?\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b"
}

from app.core.config import settings

def mask_pii(text: str) -> str:
    if not settings.PII_MASKING_ENABLED:
        return text
    masked_text = text
    for pii_type, pattern in PII_PATTERNS.items():
        masked_text = re.sub(pattern, f"[MASKED_{pii_type}]", masked_text)
    return masked_text

def unmask_pii(text: str, mapping: dict) -> str:
    """
    Optional: Unmasks PII if we decide to store a mapping for reconstruction.
    For this MVP, we will stick to one-way masking for maximum security.
    """
    return text
