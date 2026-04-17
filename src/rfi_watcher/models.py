from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ClassificationResult:
    label: str
    confidence: float
    reason: str


@dataclass(slots=True)
class RFIData:
    project_name: str | None
    rfi_number: str | None
    subject: str | None
    requested_by: str | None
    date_submitted: str | None
    due_date: str | None
    question: str | None
    suggested_answer: str | None
    referenced_sheets: list[str]
    referenced_spec_sections: list[str]
    classification: dict[str, Any]
    raw_text_excerpt: str
