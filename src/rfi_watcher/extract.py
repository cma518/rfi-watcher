from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from anthropic import Anthropic
from pypdf import PdfReader

from .classify import classify_rfi_type
from .config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL
from .models import RFIData


class RFIExtractor:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or ANTHROPIC_API_KEY
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is required.")
        self.model = model or ANTHROPIC_MODEL
        self.client = Anthropic(api_key=self.api_key)

    @staticmethod
    def extract_pdf_text(pdf_path: str | Path) -> str:
        reader = PdfReader(str(pdf_path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages).strip()

    def extract_structured_data(self, text: str) -> RFIData:
        classification = classify_rfi_type(text)

        prompt = f"""
You are extracting structured data from a construction RFI PDF.
Return valid JSON only with these keys:
project_name, rfi_number, subject, requested_by, date_submitted, due_date,
question, suggested_answer, referenced_sheets, referenced_spec_sections.
Use null when unknown. Arrays must always be arrays.

RFI text:
{text[:30000]}
""".strip()

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1200,
            messages=[{"role": "user", "content": prompt}],
        )

        content_text = "".join(
            block.text for block in response.content if getattr(block, "type", None) == "text"
        )
        payload = json.loads(content_text)

        return RFIData(
            project_name=payload.get("project_name"),
            rfi_number=payload.get("rfi_number"),
            subject=payload.get("subject"),
            requested_by=payload.get("requested_by"),
            date_submitted=payload.get("date_submitted"),
            due_date=payload.get("due_date"),
            question=payload.get("question"),
            suggested_answer=payload.get("suggested_answer"),
            referenced_sheets=payload.get("referenced_sheets") or [],
            referenced_spec_sections=payload.get("referenced_spec_sections") or [],
            classification=asdict(classification),
            raw_text_excerpt=text[:2000],
        )

    def extract_from_pdf(self, pdf_path: str | Path) -> RFIData:
        text = self.extract_pdf_text(pdf_path)
        if not text:
            raise ValueError(f"No extractable text found in PDF: {pdf_path}")
        return self.extract_structured_data(text)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Extract structured RFI data from a PDF.")
    parser.add_argument("pdf_path", help="Path to the RFI PDF")
    args = parser.parse_args()

    extractor = RFIExtractor()
    result = extractor.extract_from_pdf(args.pdf_path)
    print(json.dumps(asdict(result), indent=2))


if __name__ == "__main__":
    main()
