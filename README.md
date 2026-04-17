# RFI Watcher

Simple Python project for watching a Google Drive folder, downloading new PDF RFIs, extracting structured fields with Anthropic, and classifying the RFI type.

## Layout

```text
src/rfi_watcher/
  config.py
  models.py
  classify.py
  extract.py
  watch.py
tests/
```

## Setup

1. Create a virtualenv and install dependencies:
   ```bash
   pip install -e .
   ```
2. Copy `.env.example` to `.env` and fill in values.
3. Add your Google service account JSON as `service-account.json` or point `GOOGLE_SERVICE_ACCOUNT_FILE` to it.
4. Share the target Google Drive folder with the service account email.

## Run

Extract one PDF:
```bash
rfi-extract path/to/file.pdf
```

Watch Drive folder continuously:
```bash
rfi-watch
```

You can still run the compatibility wrappers directly:
```bash
python extract.py path/to/file.pdf
python watch.py
```
