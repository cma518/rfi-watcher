from __future__ import annotations

import json
import time
from dataclasses import asdict
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from .config import (
    DOWNLOAD_DIR,
    GOOGLE_DRIVE_FOLDER_ID,
    GOOGLE_SERVICE_ACCOUNT_FILE,
    OUTPUT_DIR,
    POLL_INTERVAL_SECONDS,
    SCOPES,
    STATE_FILE,
)
from .extract import RFIExtractor


def load_seen_ids() -> set[str]:
    if not STATE_FILE.exists():
        return set()
    return set(json.loads(STATE_FILE.read_text()))


def save_seen_ids(seen_ids: set[str]) -> None:
    STATE_FILE.write_text(json.dumps(sorted(seen_ids), indent=2))


def build_drive_service():
    credentials = service_account.Credentials.from_service_account_file(
        GOOGLE_SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
    )
    return build("drive", "v3", credentials=credentials)


def list_pdfs(service, folder_id: str) -> list[dict]:
    response = (
        service.files()
        .list(
            q=(
                f"'{folder_id}' in parents and mimeType='application/pdf' and trashed=false"
            ),
            fields="files(id, name, modifiedTime)",
            orderBy="modifiedTime desc",
        )
        .execute()
    )
    return response.get("files", [])


def download_pdf(service, file_id: str, destination: Path) -> None:
    request = service.files().get_media(fileId=file_id)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()


def process_new_pdf(service, extractor: RFIExtractor, file_meta: dict) -> None:
    pdf_name = file_meta["name"]
    file_id = file_meta["id"]
    local_path = DOWNLOAD_DIR / pdf_name
    download_pdf(service, file_id, local_path)

    structured = extractor.extract_from_pdf(local_path)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"{Path(pdf_name).stem}.json"
    output_path.write_text(json.dumps(asdict(structured), indent=2))
    print(f"Processed {pdf_name} -> {output_path}")


def validate_config() -> None:
    if not GOOGLE_DRIVE_FOLDER_ID:
        raise ValueError("GOOGLE_DRIVE_FOLDER_ID is required.")
    if not Path(GOOGLE_SERVICE_ACCOUNT_FILE).exists():
        raise FileNotFoundError(
            f"Google service account file not found: {GOOGLE_SERVICE_ACCOUNT_FILE}"
        )


def main() -> None:
    validate_config()
    service = build_drive_service()
    extractor = RFIExtractor()
    seen_ids = load_seen_ids()

    while True:
        files = list_pdfs(service, GOOGLE_DRIVE_FOLDER_ID)
        for file_meta in reversed(files):
            file_id = file_meta["id"]
            if file_id in seen_ids:
                continue
            process_new_pdf(service, extractor, file_meta)
            seen_ids.add(file_id)
            save_seen_ids(seen_ids)

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
