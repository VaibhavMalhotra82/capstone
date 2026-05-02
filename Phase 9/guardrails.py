import re
from typing import Tuple, Optional
from fuzzywuzzy import process

# Simple rule-based guards
PII_PATTERNS = [
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN-like
    re.compile(r"\b\d{10}\b"),  # 10-digit numbers (phone-ish)
    re.compile(r"[\w\.-]+@[\w\.-]+"),  # emails
]

OUT_OF_SCOPE_KEYWORDS = [
    "risk free",
    "guaranteed return",
    "insider trading",
    "cryptocurrency",
    "fraud",
    "laundering",
    "crypto"
]

def identify_keywords(user_query):
    best_match = process.extractOne(user_query, OUT_OF_SCOPE_KEYWORDS)
    if best_match and best_match[1] > 80:  # Adjust the threshold as needed
        return best_match[0]
    return None

def pre_check(question: str) -> Tuple[bool, Optional[str]]:
    """Run rule-based pre-checks on the incoming question.

    Returns (allowed, reason). If allowed is False, reason explains why.
    """
    try:
        if not question:
            return False, "Empty question"

        q = question.lower()
        # PII detection
        for p in PII_PATTERNS:
            if p.search(question):
                return False, "Request contains potential PII"

        # out-of-scope detection
        disallowed_keyword = identify_keywords(q)
        if disallowed_keyword:
                return False, f"Request appears out of scope: avoid topics related to {disallowed_keyword}."

        return True, None
    except Exception as e:
        return False, f"Error during pre-check: {str(e)}"