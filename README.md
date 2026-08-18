# Doc-Assistant

A Tkinter-based desktop assistant for generating administrative documents such as business trip orders, business trip reports, new civil contracts, and civil contract reports. The application reads project and coworker data from JSON, populates DOCX templates, converts them to PDF, and can preview and digitally sign generated files.

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

- **Create new business trip**

  - Select a project and one or more coworkers.
  - Fill in trip details such as purpose, destination, travel dates, and expense options.
  - Generate business trip order and report documents from the configured templates.
  - Save business trip context data in the data.json. The status related to the business trip is GENERATED.
  - Save generated records and route outputs into the configured output folders. The output files and folders contains starting date, project and person(s) related ids.
- **Edit a previously generated business trip**

  - On tab selected - checks all saved in data.json business trips and displays all that are not in status REPORTED.
  - Based on business trip template and selected business trip - all data is pre-filled in the form fields.
  - Generate new business trip order and report documents from the configured templates. Saved business trip data in data.json has an additional property *based_on* holding modified business trip id.
- **Report a business trip**

  - Initially in the first dropdown are listed all business trips that are NOT with status REPORTED
  - When person is selected in the business trip initially generated id folder will be created new folder with person's id. There all files from the file upload section along with personal report will be placed
  - If checkbox is checked - only payment report will be generated.
  - When all persons reported and payment report is generated - status of the business trip will be changed to REPORTED.

### Civil contract workflow

- **Create new civil contract**

  - Select a project from the first dropdown
  - After project selection - person dropdown is populated by the project related co-workers.
  - Fill in contract details such as task description, dates, amount, and responsibilities.
  - Generate civil contract creation and reporting documents from the corresponding DOCX templates.
  - During the generation - civil contract data is saved in data.json with status GENERATED
- **Report a civil contract**

  - Select from the dropdown civil contract that are not in status REPORTED
  - Fill in report details
  - Generate personal report and report of findings in sub civil contract folder named like the if the reporting person.

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

## Setup the project

- Create *template* folder with subfolders *business_trip* and *civil_contract* containig all necessary templates described bellow. The templates have to own placeholders with all business trip and civil contract context object properties - for example: {{*bt_euro_per_day*}}.
- Create in *data* folder *data.json* object with described bellow data fields.
- Configure in settings/preferences.json the pdf output folder: preferences["output_folders"]["common"] and its sub-folders: preferences["output_folders"]["business_trip"] and preferences["output_folders"]["civil_contracts"]
- Before running the app: in data.json the co-workers and projects have to be predefined. **Note:** use for the co-worker id's short symbol sentences - for example first letters of his/hers names. The same for the project ids. Along with the starting date, both are used for the generated output folders and pdf names.
- There are sample template and data folders and files in the *sample_template_and_data.zip* file.

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

## Data file schema (data/data.json)

This project expects a JSON data file at `data/data.json`. The file contains several top-level sections used by the app; the following lists show the common and required fields the app reads and writes.

- `co_workers` (mapping of coworker_id -> coworker object)

  - `full_name` (string)
  - `titles` (string)
  - `names` (string)
  - `position` (string)
  - `department` (string)
  - `work_place` (string)
  - `email` (string)
  - `egn` (string)
  - `address` (object)
    - `main_line` (string)
    - `city` (string)
    - `zip` (string)
    - `municipality` (string)
  - `id` (object)
    - `number` (string)
    - `issue_date` (string)
    - `issuer` (string)
  - `iban` (string)
  - `car` (optional object)
    - `brand`, `model`, `year`, `plate`, `liters_per_100km`, `fuel_type`
- `projects` (mapping of project_id -> project object)

  - `name` (string)
  - `description` (string)
  - `start_date` (YYYY-MM-DD string)
  - `end_date` (YYYY-MM-DD string)
  - `team` (list of coworker IDs)
  - `project_lead` (coworker ID)
  - `number` (string)
- `common` (shared defaults)

  - `euro_per_day` (number)
  - `other_expences` (string)
- `output_folders` (paths)

  - `common` (path)
  - `civil_contracts` (subfolder)
  - `business_trip` (subfolder)
- `civil_contracts` (mapping of generated contract identifiers -> contract object)

  - `project_id`, `person_id`, `cc_task`, `cc_task_start_date`, `cc_task_end_date`,
    `doc_date_and_ids_identifier`, `status`, and optional fields such as `completed_task_description`, `personal_report`
- `business_trips` (mapping of generated trip identifiers -> trip object)

  - `project_id`, `bt_heading`, `person_ids` (list), `start_date` (DD/MM/YYYY),
    `end_date` (DD/MM/YYYY), `doc_date_and_ids_identifier`, `bt_travel_with`,
    `bt_day_money_from`, `bt_nights_money_from`, `bt_travel_money_from`,
    `bt_destination`, `bt_euro_per_day`, `bt_nights_max_value`, `bt_other_expences`, `bt_contract_info`,
    `leader_titles`, `leader_names`, `leader_full_name`, `leader_work_place`, `bt_all_persons`, `status`

Notes on date formats:

- Project `start_date` and `end_date` are stored as `YYYY-MM-DD`.
- Contract and trip UI date fields (used in templates) are typically `DD/MM/YYYY` in the JSON records when stored by the app.

If you edit `data/data.json` manually, keep the above field names and date formats to avoid validation and parsing errors in the UI.

## Docs templates properties and file names

### Business trip 'create' templates:

Necessary templates in folder: *templates/business_trip/*:  **business_trip_order.docx** and **business_trip_report.docx**

### Business trip 'edit' templates:

Necessary templates in folder: *templates/business_trip/*:  **business_trip_order.docx** and **business_trip_report.docx**

### Business trip 'report' templates:

Necessary templates in folder: *templates/business_trip/*: **business_trip_report_personal.docx** and/or **business_trip_report_money.docx**

### Civil contract 'create' templates:

Necessary templates in folder: *templates/civil_contract/*:  **cc_pl_report.docx** and **civil_contract_create.docx**

### Civil contract 'report' templates:

Necessary templates in folder: *templates/civil_contract/*:  **cc_report_of_findings.docx** and **civil_contract_person_report.docx**
