# Doc-Assistant

A Tkinter-based desktop assistant for generating administrative documents such as business trip orders, business trip reports, civil contract documents, and signed PDF exports. The application stores its working data in an encrypted SQLCipher database under the project data folder, loads UI labels from the JSON label catalog, and keeps non-sensitive configuration in the settings folder.

## What the app does

- Launches a desktop UI with a notebook-style interface.
- Provides separate tabs for:
  - business trip documents
  - civil contract documents
- Generates documents from DOCX templates using the selected project, person, and form data.
- Converts generated DOCX files to PDF using LibreOffice or, when available, docx2pdf.
- Supports PDF preview and visible signature placement.
- Can sign PDFs with a certificate file (for example PKCS#12 / PFX).
- Saves recurring application data in an encrypted database at `data/doc_assistant.db`.
- Requires a database password to be set when a new database is created and to be entered again every time the app starts before data is read and decrypted.

## Security model

The application now uses a password-protected encrypted database instead of a plain JSON file for personal records.

- Database location: `data/doc_assistant.db`
- Password requirement: set on first database creation and prompted again at every startup
- Protection: SQLCipher-backed encrypted SQLite database
- Key derivation: Argon2-based key material derived from the database password
- Secret storage: the password is stored in the OS keychain when available
- Legacy support: if an existing `data/data.json` file is still present, it is migrated into the database on first load
- Non-sensitive app settings: kept in `settings/preferences.json`

## Main workflows

### Business trip workflow

- **Create new business trip**

  - Select a project and one or more coworkers.
  - Select departure ("От:") and arrival ("До:") countries and cities using dropdown selectors. Per diem and accommodation rates are automatically loaded from `settings/countries.json` and synced to the daily (`bt_euro_per_day`) and accommodation (`bt_nights_max_value`) fields when enabled. Destination (`bt_destination`) is automatically formatted (e.g. `from city - to city - from city`).
  - Fill in trip details such as purpose, travel dates, and expense options.
  - Generate business trip order and report documents from the configured templates.
  - Save business trip context data in the encrypted app database. The status related to the business trip is `GENERATED`.
  - Save generated records and route outputs into the configured output folders. The output files and folders contain starting date, project, and person(s) related IDs.
- **Edit a previously generated business trip**

  - The app checks the encrypted database for saved business trips that are not in status `REPORTED`.
  - Based on the business trip template and selected business trip, all data is pre-filled in the form fields (including restoring country/city dropdown selections).
  - Generate new business trip order and report documents from the configured templates. Saved trip data retains any modified record metadata and the workflow status.
- **Report a business trip**

  - Initially in the first dropdown are listed all business trips that are NOT in status `REPORTED`.
  - When a person is selected, the business trip initially generated folder is created for that person. Files from the upload section and the personal report are placed there.
  - If the checkbox is selected, only the payment report is generated.
  - When all persons have reported and the payment report is generated, the business trip status is changed to `REPORTED`.

### Civil contract workflow

- **Create new civil contract**

  - Select a project from the first dropdown.
  - After a project is selected, the person dropdown is populated from the project-related coworkers.
  - Fill in contract details such as task description, dates, amount, and responsibilities.
  - Generate civil contract creation and reporting documents from the corresponding DOCX templates.
  - During generation, the civil contract data is saved in the encrypted database with status `GENERATED`.
- **Report a civil contract**

  - Select from the dropdown a civil contract that is not in status `REPORTED`.
  - Fill in report details.
  - Generate the personal report and report-of-findings in the appropriate civil contract subfolder.

## Project structure

- main.py — application entry point
- Helpers.py — shared utility methods and common export helpers
- classes/MainApp.py — app bootstrapper
- classes/DataMgr.py — encrypted database access, password handling, legacy JSON migration, and data persistence helpers
- classes/docs/ — document-specific implementations
  - classes/docs/business_trip/ — business trip order/report logic and export helpers
  - classes/docs/civil_contract/ — civil contract create/report logic and export helpers
- classes/tabs/ — tab container wiring for the UI
- ui/ — UI management, CountryCitySelector, and widget creation helpers
- templates/ — DOCX templates used for document generation
- data/ — runtime application data, including the encrypted database (`doc_assistant.db`) and legacy fallback (`data.json` if present)
- settings/ — configuration files:
  - `labels.json` — UI text and field labels
  - `preferences.json` — output folder paths, fonts, tab colors, digital signature styling
  - `countries.json` — countries, cities, per diem rates, and accommodation caps
- tests/ — unit tests for document export, selector, validation, and report helpers

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
- sqlcipher3-binary
- argon2-cffi
- keyring
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

## Setup the project

- Create the `templates` folder with subfolders `business_trip` and `civil_contract`, each containing the DOCX templates required for the app.
- Ensure the template placeholders match the data object structure used by the app, for example `{{ bt_euro_per_day }}` or similar project-specific fields.
- Configure the output folders in `settings/preferences.json` under `preferences["output_folders"]["common"]`, `preferences["output_folders"]["business_trip"]`, and `preferences["output_folders"]["civil_contracts"]`.
- Before the first run, add your projects and coworkers to the app data set. The IDs are used for generated output folders and PDF names.
- If an older `data/data.json` file exists, the app will migrate it into the encrypted database the first time it is opened.
- There are sample template and data folders and files in the `sample_template_and_data.zip` archive if available in the project environment.

## Run the app

After the environment is activated, run:

```bash
python main.py
```

When the app starts:

1. If no encrypted database exists, it prompts for a new database password and creates `data/doc_assistant.db`.
2. If a database exists, it asks for the database password before reading or decrypting any saved records.
3. If the password is wrong or the database is corrupt, the app stops and shows a validation error instead of silently reading unusable data.

## Run the tests

```bash
python -m unittest discover -s tests
```

## Notes

- LibreOffice should be installed and available in PATH for DOCX-to-PDF conversion.
- If LibreOffice is unavailable, the app will try docx2pdf when it is installed.
- The UI labels are configured in `settings/labels.json`, and the database password is required before any data is read and decrypted.

## Data model

The application stores its structured business data in the encrypted database as collections such as:

- `projects`
- `co_workers`
- `civil_contracts`
- `business_trips`
- `common`
- `output_folders`

The database remains the primary runtime storage path; `data/data.json` is treated as a legacy migration source only.

## Docs templates properties and file names

### Business trip 'create' templates:

Necessary templates in folder: `templates/business_trip/`: `business_trip_order.docx` and `business_trip_report.docx`

### Business trip 'edit' templates:

Necessary templates in folder: `templates/business_trip/`: `business_trip_order.docx` and `business_trip_report.docx`

### Business trip 'report' templates:

Necessary templates in folder: `templates/business_trip/`: `business_trip_report_personal.docx` and/or `business_trip_report_money.docx`

### Civil contract 'create' templates:

Necessary templates in folder: `templates/civil_contract/`: `cc_pl_report.docx` and `civil_contract_create.docx`

### Civil contract 'report' templates:

Necessary templates in folder: `templates/civil_contract/`: `cc_report_of_findings.docx` and `civil_contract_person_report.docx`
