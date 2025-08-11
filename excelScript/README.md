# CITS3200 Team Leader Spreadsheet Automation

Automates weekly deliverables from a master Google Sheet into Excel files and uploads them to Google Drive.

### What it does
- Copies the master workbook from Google Drive via `rclone`.
- Generates a group timesheet from `templates/TimeSheet_GroupX_WkY.xlsx`:
  - Transfers `PerPerson` weekly totals (weeks 2–11) using exact, case‑insensitive name matching.
  - Copies key metrics from `Results` (B2–B6).
- Generates six individual timesheets from `templates/Booked_Hours_YourName.xlsx`.
- Creates a zip archive with all individual timesheets.
- Uploads outputs to `REMOTE:BASE_PATH/WeekY/` using `rclone mkdir` and `rclone copy`.

### Prerequisites
- Python 3.8+
- `rclone` installed and configured with a Google Drive remote.
- Templates present in `templates/`:
  - `TimeSheet_GroupX_WkY.xlsx` with sheets: `PerPerson`, `Results`.
  - `Booked_Hours_YourName.xlsx` with sheet: `BookedHours`.

### Install
```bash
cd excelScript
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configuration (optional)
You can configure via environment variables or a YAML file (pass with `--config path/to/config.yaml`).

- Remote and paths:
  - `REMOTE_NAME` (default: `gdrive`)
  - `REMOTE_BASE_PATH` (default: `CITS3200`)
- Filenames and locations:
  - `MASTER_FILE` (default: `CITS3200_Group_31.xlsx`)
  - `GROUP_TEMPLATE` (default: `templates/TimeSheet_GroupX_WkY.xlsx`)
  - `INDIVIDUAL_TEMPLATE` (default: `templates/Booked_Hours_YourName.xlsx`)
  - `OUTPUT_DIR` (default: `output`)
- Team metadata:
  - `GROUP_NUMBER` (default: `31`)
  - `TEAM_MEMBERS` (comma‑separated, default: `Steve,Ben,Dongkai,William,Jeremy,Noah`)

YAML keys mirror the variable names above.

### Run
```bash
# Prompt for week
python main.py

# Specify week (2–11)
python main.py --week 7

# Dry‑run (no writes/uploads)
python main.py --week 7 --dry-run

# With config file
python main.py --week 7 --config config.yaml
```

### Outputs
- Local (`OUTPUT_DIR`):
  - `TimeSheet_Group<group>_Wk<week>.xlsx`
  - `Booked_Hours_<Name>.xlsx` (for each team member)
  - `Booked_Group<group>_Wk<week>.zip`
- Cloud: uploaded to `REMOTE_NAME:REMOTE_BASE_PATH/Week<week>/`.

### Behaviour and guarantees
- Exact, case‑insensitive matching for member names between master and templates.
- Value‑only reads from the master (no formula copying).
- Validates required templates and sheets before running; fails fast with non‑zero exit code.
- Structured logging to console; `--dry-run` prints planned actions without side effects.

### Dependencies
Pinned in `requirements.txt`:
- `openpyxl`, `rich`, `PyYAML`, `python-dotenv`

System:
- `rclone` configured with the desired remote.

### Troubleshooting
- “Group/Individual template not found” → ensure the files exist under `templates/` and contain the required sheet names.
- “Failed to copy master file” → check `rclone` remote name and base path; verify the file exists in Drive.
- “Upload failed” → ensure the remote is authenticated and you have permission to write to the target path.

## Implementation Review

### Exactly what the script does
Based on `main.py`, the automation performs the following end‑to‑end workflow:

1. Prompts for a week number (2–11). The week number is used in output file names and the Google Drive week folder name (`WeekY`).
2. Copies `gdrive:CITS3200/CITS3200_Group_31.xlsx` locally via `rclone copy` using a remote named `gdrive`.
3. Creates a group timesheet:
   - Copies `templates/TimeSheet_GroupX_WkY.xlsx` to `output/TimeSheet_Group31_WkY.xlsx`.
   - Loads the master (`data_only=True`) and output workbooks and transfers:
     - `PerPerson` weekly totals for the six team members by dynamically mapping rows (columns B–L).
     - Five key `Results` cells: B2–B6.
4. Creates six individual timesheets:
   - For each of `Steve, Ben, Dongkai, William, Jeremy, Noah`, copies `templates/Booked_Hours_YourName.xlsx` to `output/Booked_Hours_[Name].xlsx`.
   - In each file, updates cell A1 title to include the member’s name and transfers row data from the member’s sheet in the master (rows 4–≤100, columns 1–8), if that sheet exists.
5. Creates `output/Booked_Group31_WkY.zip` containing all six individual timesheets.
6. Deletes the downloaded master file from the working directory.
7. Uploads to Google Drive under `gdrive:CITS3200/WeekY/` using `rclone`:
   - Checks for the `WeekY` folder by calling `rclone ls`; if missing, attempts to create it by copying a temporary `README.md` and deleting it.
   - Uploads the group timesheet and the zip archive.
8. Prints a summary of created files in `output/`.

### Does it do it well? What’s missing?
- Overall, the core flow executes correctly and is reasonably robust: it guards for missing sheets, reads values (not formulae), and produces the required local and cloud artefacts.
- The dynamic row mapping in `PerPerson` and the value‑only reads are appropriate to avoid formula translation issues.
- Missing or fragile aspects:
  - The Google Drive folder creation uses a brittle workaround (copying/deleting a file) instead of `rclone mkdir`. It also assumes `README.md` exists in the current working directory.
  - The week number is not used to filter data; it only affects file/folder names. If week‑specific extraction is expected, this is currently missing.
  - Name matching for `PerPerson` uses substring matching and may mis‑map similar names (e.g. “Ben” vs “Benji”).
  - Assumes a fixed remote name `gdrive` and fixed file `CITS3200_Group_31.xlsx` with hard‑coded team members; not configurable.
  - Error handling is print‑based without clear exit codes or structured logs; failures in intermediate steps do not always abort the run.
  - Imports and dependencies are out of sync: `pandas`, `datetime`, and `json` are imported but unused; `gspread`/Google Auth packages are listed but not used.
  - Documentation mismatches: mentions a `config/` directory (not present) and a mounted path, whereas the code uses `rclone` remote commands.

### Improvements aligned to the requirements
- Google Drive operations
  - Use `rclone mkdir gdrive:CITS3200/WeekY` for folder creation instead of the copy/delete hack.
  - Make the remote name and base path configurable (env var or CLI flag), e.g. `--remote gdrive --base-path CITS3200`.
- Configuration and inputs
  - Add CLI flags (with sensible defaults) alongside the interactive prompt: `--week`, `--group`, `--members`, `--master`, `--remote`, `--output`, `--no-upload`.
  - Externalise team members, group number, and file names into a small config file (e.g. `config.yaml`) or environment variables.
- Data handling
  - Optionally restrict transfers to the selected week (e.g. copy only column for week Y in `PerPerson`, and filter individual rows by week).
  - Switch to exact, case‑insensitive name matching (or a mapping table) to avoid substring collisions.
- Robustness and UX
  - Fail fast on critical errors (return non‑zero exit on failure), and use structured logging (or at least consistent prefixes) for easier diagnostics.
  - Validate template presence and expected sheet names up front before processing.
  - Add a dry‑run mode that skips file writes and uploads while printing the planned actions.
- Code and dependencies
  - Remove unused imports; pin dependency versions; drop unused packages from `requirements.txt` (`gspread` and Google Auth libs) if not adopting the Sheets API.
  - Prefer `pathlib` over `os.path` for path operations.

### Documentation corrections (to align with current implementation)
- Access method: the script uses `rclone` remote commands (e.g. `rclone copy gdrive:...`), not a mounted filesystem at `~/gdrive`. Update wording accordingly, or add both options with the current default being the remote.
- Dependencies: `pandas` is not used; `gspread`/Google Auth libraries are not used. Either document future intent or remove from `requirements.txt`.
- File structure: `config/` is not present; either create it for future configuration or remove from the tree in this document.
- Name updates: names are updated in the individual timesheet title cell only; the group template assumes correct names already exist. Clarify this expectation.

