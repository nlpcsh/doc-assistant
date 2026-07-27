# doc-assistant

A Tkinter-based assistant for generating administrative documents such as business trip orders and civil contracts. The application reads project and coworker data from JSON, populates document templates, converts them to PDF, and can preview and sign the generated PDF with a visible signature.

## Current functionality

### Main application

- Launches a desktop UI with a notebook-style interface.
- Provides separate tabs for:
  - business trip documents
  - civil contract documents

### Business trip workflow

- Selects a project and a person from the loaded data.
- Fills in trip details such as:
  - purpose
  - destination
  - travel dates
  - daily/night/travel expenses
- Uses the selected values to build the document context and generate the business trip documents from DOCX templates.
- Converts the generated DOCX files to PDF using LibreOffice/Office-compatible tools.
- Opens the generated PDF preview so the user can place a visible signature.

### Civil contract workflow

- Provides a contract document generation flow from the civil contract tab.
- Uses the shared document generation pipeline to create and process the document.

### Signature and PDF handling

- Allows the user to select a signature image.
- Opens a preview of the generated PDF.
- Lets the user click inside the preview to place a visible signature rectangle.
- Supports signing the PDF using a certificate file (for example PKCS#12 / PFX).
- Saves the signed output as a PDF and opens it after signing.

## Project structure

- main.py — application entry point
- classes/MainApp.py — app bootstrapper
- classes/UIMgr.py — centralized UI management and widget creation
- classes/docs/BaseDoc.py — shared document generation and signing logic
- classes/DataMgr.py — JSON data and label loading
- classes/docs/ — document-specific implementations
- templates/ — DOCX templates used for document generation
- data/ — data source files such as projects and coworkers
- settings/ — labels and UI text

## Requirements

Install the Python dependencies required by the project, including:

- tkinter
- docxtpl
- python-docx
- Pillow
- pymupdf
- pyhanko
- cryptography
- tkcalendar

## Running the app

From the project root, run:

```bash
python main.py
```

## Notes

- The application expects LibreOffice to be installed and available in PATH for DOCX-to-PDF conversion.
- The UI and labels are configured through the JSON files in the settings and data folders.
