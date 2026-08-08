# doc-assistant

A Tkinter-based desktop assistant for generating administrative documents such as business trip orders, business trip reports, civil contract drafts, and civil contract reports. The application reads project and coworker data from JSON, populates DOCX templates, converts them to PDF, and can preview and sign generated files.

## What the app does

- Launches a desktop UI with a notebook-style interface.
- Provides separate tabs for:
  - business trip documents
  - civil contract documents
- Generates documents from DOCX templates using the selected project, person, and form data.
- Converts generated DOCX files to PDF using LibreOffice or, when available, docx2pdf.
- Supports PDF preview and visible signature placement.
- Can sign PDFs with a certificate file (for example PKCS#12 / PFX).

## Main workflows

### Business trip workflow

- Select a project and one or more coworkers.
- Fill in trip details such as purpose, destination, travel dates, and expense options.
- Generate business trip order and report documents from the configured templates.
- Save generated records and route outputs into the configured output folders.

### Civil contract workflow

- Select a project and a person.
- Fill in contract details such as task description, dates, amount, and responsibilities.
- Generate civil contract creation and reporting documents from the corresponding DOCX templates.

## Project structure

- main.py — application entry point
- Helpers.py — shared utility methods and common export helpers
- classes/MainApp.py — app bootstrapper
- classes/DataMgr.py — JSON data loading and persistence helpers
- classes/docs/ — document-specific implementations
  - classes/docs/business_trip/ — business trip order/report logic and export helpers
  - classes/docs/civil_contract/ — civil contract create/report logic and export helpers
- classes/tabs/ — tab container wiring for the UI
- ui/ — UI management and widget creation helpers
- templates/ — DOCX templates used for document generation
- data/ — input data files such as projects and coworkers
- settings/ — labels and UI text configuration
- tests/ — unit tests for document export and report helpers

## Requirements

Install the dependencies from requirements.txt:

```bash
pip install -r requirements.txt
```

The most important runtime packages include:

- tkinter
- docxtpl
- python-docx
- Pillow
- pymupdf
- pyhanko
- cryptography
- tkcalendar
- docx2pdf (optional, for Word-based DOCX-to-PDF conversion on Windows/macOS)

## Installation

### Linux

From the project root, run:

```bash
chmod +x install.sh
./install.sh
```

### Windows (PowerShell)

From the project root, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

## Run the app

After the environment is activated, run:

```bash
python main.py
```

## Run the tests

```bash
python -m unittest discover -s tests
```

## Notes

- LibreOffice should be installed and available in PATH for DOCX-to-PDF conversion.
- If LibreOffice is unavailable, the app will try docx2pdf when it is installed.
- The UI labels and some defaults are configured through the JSON files in the settings and data folders.
