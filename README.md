# Doc-Assistant

A Tkinter-based desktop assistant for generating administrative documents such as business trip orders, business trip reports, civil contract documents, and signed PDF exports. The application stores its working data in an encrypted SQLCipher database under the project data folder, loads UI labels from the JSON label catalog, and keeps non-sensitive configuration in the settings folder.

## What the app does

- Launches a desktop UI with a notebook-style interface.
- Provides separate tabs for:
  - business trip documents
  - civil contract documents
  - database management (co-workers, projects, and database password change)
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
- Password rules: at least 6 characters, with an uppercase letter, a lowercase letter, a digit, and a special character
- Password change: available from the database management tab; the database is re-encrypted with the new key into a temporary file that then replaces the original
- Non-sensitive app settings: kept in `settings/preferences.json` (created from `settings/preferences.example.json` on first run and not tracked in git)

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
  - Fill in contract details such as task description, dates, amount, and responsibilities. All contract fields are required; missing or invalid fields are highlighted before generation.
  - Generate civil contract creation and reporting documents from the corresponding DOCX templates.
  - During generation, the civil contract data (including the task dates and amount) is saved in the encrypted database with status `GENERATED`.
- **Report a civil contract**

  - Select from the dropdown a civil contract that is not in status `REPORTED`. The list is refreshed every time the report tab is shown, so contracts created in the same session appear immediately.
  - Fill in the completed task description and the personal report, and optionally attach files.
  - Generate the personal report, report-of-findings, and payment report in the appropriate civil contract subfolder. The contract amount, task dates, and the person's work place and IBAN are filled in from the saved contract and co-worker records.
  - After generation, the contract status is changed to `REPORTED` and the report texts are saved with the contract.

### Database management workflow

- **Co-workers** and **Projects** tabs: select a record, edit its fields, and save; add new records or remove the selected one.
  - Record IDs are required, must be unique, and may contain at most 6 Latin letters, digits, or underscores. They are used in output folder and file names.
  - Removing a co-worker also removes them from every project team and clears them as project lead where applicable.
- **Password** tab: change the database password (current password, new password, and confirmation).

## Project structure

- main.py — application entry point
- Helpers.py — shared utility methods and common export helpers
- classes/MainApp.py — app bootstrapper
- classes/DataMgr.py — encrypted database access, password handling, legacy JSON migration, and data persistence helpers
- classes/docs/ — document-specific implementations
  - classes/docs/business_trip/ — business trip order/report logic and export helpers
  - classes/docs/civil_contract/ — civil contract create/report logic and export helpers
  - classes/docs/db_management/ — co-workers, projects, and password change management tabs
- classes/digisign/ — PDF preview, signature overlay, certificate handling, and PDF signing
- classes/tabs/ — tab container wiring for the UI
- enums/Enums.py — business trip (`BTStatus`) and civil contract (`CCStatus`) status enums
- ui/ — UI management, CountryCitySelector, and widget creation helpers
- templates/ — DOCX templates used for document generation (extracted from `templates_folder.zip` by the install scripts)
- data/ — runtime application data, including the encrypted database (`doc_assistant.db`) and legacy fallback (`data.json` if present)
- settings/ — configuration files:
  - `labels.json` — UI text and field labels
  - `preferences.json` — output folder paths, fonts, tab colors, digital signature styling, common defaults (local, not in git)
  - `preferences.example.json` — template used to create `preferences.json`
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
- sqlcipher3-binary (Linux) / sqlcipher3-wheels (Windows, macOS)
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

- The install scripts extract `templates_folder.zip` into the `templates` folder (subfolders `business_trip` and `civil_contract`). If you set up manually, create these folders with the DOCX templates listed below.
- Ensure the template placeholders match the data object structure used by the app, for example `{{ bt_euro_per_day }}` or similar project-specific fields.
- Configure the output folders in `settings/preferences.json` under `preferences["output_folders"]["common"]`, `preferences["output_folders"]["business_trip"]`, and `preferences["output_folders"]["civil_contracts"]`.
- After the first run, add your co-workers and projects from the database management tab. The IDs are used for generated output folders and PDF names.
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

### Storage layout

The encrypted database `data/doc_assistant.db` contains a single table:

```sql
CREATE TABLE app_data (collection TEXT PRIMARY KEY, payload TEXT NOT NULL)
```

Each row holds one collection, serialized as a JSON object that maps record IDs to records. Four collections are persisted:

| Collection        | Record key                                   | Created by                                   |
| ----------------- | -------------------------------------------- | -------------------------------------------- |
| `co_workers`      | co-worker ID (max 6 chars: `A-Z a-z 0-9 _`)  | Database management → Co-workers             |
| `projects`        | project ID (max 6 chars: `A-Z a-z 0-9 _`)    | Database management → Projects               |
| `business_trips`  | `doc_date_and_ids_identifier` of the trip    | Business trip create / edit                  |
| `civil_contracts` | `doc_date_and_ids_identifier` of the contract | Civil contract create                       |

`common` and `output_folders` are **not** stored in the database. They are read from `settings/preferences.json` and only kept in memory next to the collections at runtime.

`data/data.json` is treated as a legacy migration source only: if the database is empty and the file exists, its four collections are imported once.

All dates are stored as strings in `DD.MM.YYYY` format unless noted otherwise.

### `co_workers`

```json
{
  "<co_worker_id>": {
    "full_name": "", "names": "", "titles": "",
    "egn": "", "email": "", "iban": "",
    "position": "", "department": "", "work_place": "",
    "address": { "main_line": "", "city": "", "zip": "", "municipality": "" },
    "id":      { "number": "", "issue_date": "", "issuer": "" },
    "car":     { "brand": "", "model": "", "year": "", "plate": "", "liters_per_100km": "", "fuel_type": "" }
  }
}
```

- `names` is the short name and `full_name` the full legal name used in contracts.
- `id` is the personal identity document.

### `projects`

```json
{
  "<project_id>": {
    "name": "",
    "description": "",
    "number": "",
    "project_lead": "<co_worker_id>",
    "start_date": "",
    "end_date": "",
    "team": ["<co_worker_id>", "..."]
  }
}
```

- `team` lists the co-workers available for business trips and civil contracts on this project.
- `end_date` is used to preselect the latest project in the civil contract create tab.

### `business_trips`

Record key: `<YYYY_MM_DD>_<project_id>_<person_ids>` (start date, project, and participants).

```json
{
  "<doc_date_and_ids_identifier>": {
    "doc_date_and_ids_identifier": "",
    "project_id": "<project_id>",
    "status": "GENERATED",
    "bt_heading": "",
    "bt_order_number": "",
    "person_ids": ["<co_worker_id>", "..."],
    "reported_ids": ["<co_worker_id>", "..."],
    "start_date": "",
    "end_date": "",
    "bt_travel_with": "",
    "bt_day_money_from": "",
    "bt_nights_money_from": "",
    "bt_travel_money_from": "",
    "bt_destination": "",
    "bt_destination_obj": { "from": ["<country>", "<city>"], "to": ["<country>", "<city>"] },
    "bt_euro_per_day": "",
    "bt_nights_max_value": "",
    "bt_other_expences": "",
    "bt_contract_info": "",
    "leader_titles": "",
    "leader_names": "",
    "leader_full_name": "",
    "leader_work_place": "",
    "bt_all_persons": "",
    "based_on": "<previous doc_date_and_ids_identifier>"
  }
}
```

- `bt_heading` holds the trip purpose.
- `bt_order_number` is filled in when the trip is reported.
- `reported_ids` lists the participants who have already submitted their personal report.
- `based_on` is present only on records created from the edit tab and points to the original trip.

Status (`BTStatus`) lifecycle:

| Status            | Meaning                                                                  |
| ----------------- | ------------------------------------------------------------------------ |
| `GENERATED`       | Documents generated; the trip has not started yet                        |
| `ONGOING`         | Current date is after the start date and on or before the end date      |
| `READY_TO_REPORT` | Current date is after the end date                                       |
| `PL_REPORTED`     | The project lead has reported, or the payment report has been generated  |
| `REPORTED`        | All participants have reported and the trip is `PL_REPORTED`             |

`GENERATED` → `ONGOING` → `READY_TO_REPORT` are recalculated from the dates when the business trip report tab loads.

### `civil_contracts`

Record key: `<YYYY_MM_DD>_<project_id>_<co_worker_id>` (task start date, project, and person), or `no_start_date_<project_id>_<co_worker_id>` if no start date is set.

```json
{
  "<doc_date_and_ids_identifier>": {
    "doc_date_and_ids_identifier": "",
    "project_id": "<project_id>",
    "person_id": "<co_worker_id>",
    "status": "GENERATED",
    "cc_number": "",
    "cc_task": "",
    "cc_task_start_date": "",
    "cc_task_end_date": "",
    "cc_task_amount": "",
    "completed_task_description": "",
    "personal_report": ""
  }
}
```

- `cc_number` is reserved for the contract number and is currently left empty.
- `completed_task_description` and `personal_report` are added when the contract is reported.

Status (`CCStatus`) values: `GENERATED`, `ONGOING`, `READY_TO_REPORT`, `REPORTED`. The create tab sets `GENERATED` and the report tab sets `REPORTED`.

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

Necessary templates in folder: `templates/civil_contract/`: `civil_contract_person_report.docx`, `cc_report_of_findings.docx`, and `civil_contract_report_payment.docx`
