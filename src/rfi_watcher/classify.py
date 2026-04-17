from __future__ import annotations

from .models import ClassificationResult


KEYWORDS = {
    "design": ["design", "drawing", "specification", "architect", "engineering"],
    "commercial": ["pricing", "quote", "cost", "budget", "commercial"],
    "schedule": ["schedule", "timeline", "deadline", "duration", "milestone"],
    "technical": ["technical", "submittal", "material", "installation", "performance"],
    "general": ["rfi", "request for information", "clarification"],
}


def classify_rfi_type(text: str) -> ClassificationResult:
    normalized = (text or "").lower()
    scores: dict[str, int] = {}

    for label, terms in KEYWORDS.items():
        scores[label] = sum(normalized.count(term) for term in terms)

    label, score = max(scores.items(), key=lambda item: item[1])
    total = sum(scores.values()) or 1
    confidence = round(score / total, 2)

    if score == 0:
        return ClassificationResult(
            label="unknown",
            confidence=0.0,
            reason="No classification keywords matched the extracted text.",
        )

    return ClassificationResult(
        label=label,
        confidence=confidence,
        reason=f"Matched {score} keyword hits for '{label}'.",
    )
