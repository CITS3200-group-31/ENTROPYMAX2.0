# CITS3200 Team Leader Spreadsheet Automation

## Project Overview
This Python script automates the conversion of Google Sheets data to Excel (.xlsx) deliverables for CITS3200 team leader weekly reports at the University of Western Australia. The automation handles the complete workflow from data extraction to file generation and cloud storage.

## Purpose
- **Input**: Master Google Sheet accessible by the whole team
- **Output**: 7 Excel files (6 booked hours sheets + 1 group hours sheet) + cloud backup
- **Problem Solved**: Google Sheets formulas don't translate well to Excel format
- **Workflow**: Complete automation from data fetch to cloud upload

## Requirements

### Input Data
- **Master Google Sheet**: `CITS3200/CITS3200_Group_31.xlsx` (accessed via rclone)
- **Template Files**:
  - `templates/TimeSheet_GroupX_WkY.xlsx` - Group timesheet template
  - `templates/Booked_Hours_YourName.xlsx` - Individual booked hours template
- **Access**: Google Drive via rclone (mounted at `~/gdrive`)

### Master File Structure
The master file contains 12 sheets:
1. **Instructions** - Project guidelines and setup
2. **General Tasks** - Overall project task tracking
3. **Requirements** - Software requirements tracking
4. **PerPerson** - Weekly hours summary for all team members
5. **Steve** - Individual hours tracking for Steve
6. **Ben** - Individual hours tracking for Ben
7. **Dongkai** - Individual hours tracking for Dongkai
8. **William** - Individual hours tracking for William
9. **Jeremy** - Individual hours tracking for Jeremy
10. **Noah** - Individual hours tracking for Noah
11. **Results** - Overall project statistics and budget tracking
12. **Contact** - Team contact information

### Team Information
- **Group**: 31
- **Team Members**:
  - Steve (Team Leader)
  - William
  - Dongkai
  - Jeremy
  - Noah
  - Ben

## Output Files

### Local Files (in `output/` directory)
1. **1 Group Timesheet** (`TimeSheet_Group31_WkY.xlsx`) - Overall team hour summary
2. **6 Individual Timesheets** (`Booked_Hours_[Name].xlsx`) - Individual team member hour tracking
3. **1 Zip File** (`Booked_Group31_WkY.zip`) - Contains all 6 individual timesheets

### Cloud Files (in Google Drive)
- **Upload Location**: `CITS3200/WeekY/` directory
- **Uploaded Files**:
  - `TimeSheet_Group31_WkY.xlsx` - Group timesheet
  - `Booked_Group31_WkY.zip` - Individual timesheets archive

## Key Features
- **Cell Value Transfer**: Reads actual cell values, not formulas
- **Name Updates**: Automatically updates team member names
- **Template-Based**: Uses provided Excel templates as base
- **Automated Processing**: Single script execution generates all deliverables
- **Google Drive Integration**: Automatically uploads deliverables to Google Drive
- **Cleanup**: Removes temporary files after processing
- **Dynamic Mapping**: Programmatically identifies and maps data between sheets
- **Week-Specific Organization**: Creates week directories in Google Drive

## Technical Stack
- **Python 3.8+**: Core automation language
- **rclone**: Google Drive file access and synchronization
- **openpyxl**: Excel file reading/writing (with `data_only=True` for values)
- **zipfile**: Built-in Python module for archive creation
- **subprocess**: Command-line tool execution
- **os/shutil**: File system operations

## File Structure
```
excelScript/
├── README.md                    # Project documentation
├── main.py                      # Main automation script
├── requirements.txt             # Python dependencies
├── templates/                   # Excel template files
│   ├── TimeSheet_GroupX_WkY.xlsx
│   └── Booked_Hours_YourName.xlsx
├── output/                      # Generated deliverables
│   ├── TimeSheet_Group31_WkY.xlsx
│   ├── Booked_Hours_[Name].xlsx (6 files)
│   └── Booked_Group31_WkY.zip
├── config/                      # Configuration directory
├── venv/                       # Python virtual environment
└── .DS_Store                   # macOS system file
```

## Installation & Setup

### Prerequisites
1. **Python 3.8+** installed
2. **rclone** configured for Google Drive access
3. **Template files** placed in `templates/` directory

### Environment Setup
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage
```bash
# Activate virtual environment
source venv/bin/activate

# Run the automation script
python main.py
```

### Complete Workflow
The script performs the following steps:

1. **📝 Prompt for week number** (2-11)
2. **📥 Copy master file** from Google Drive (`gdrive:CITS3200/CITS3200_Group_31.xlsx`)
3. **📊 Create group timesheet** (`TimeSheet_Group31_WkY.xlsx`)
   - Transfer PerPerson data with dynamic row mapping
   - Transfer Results data
4. **👥 Create 6 individual timesheets** (`Booked_Hours_[Name].xlsx`)
   - One for each team member
   - Transfer individual hour data
5. **📦 Create zip archive** (`Booked_Group31_WkY.zip`)
   - Contains all 6 individual timesheets
6. **🧹 Clean up** downloaded master file from project directory
7. **☁️ Upload to Google Drive** in `CITS3200/WeekY/` directory
   - Creates week directory if it doesn't exist
   - Uploads group timesheet and zip file
8. **💾 Save local copies** in `output/` directory

### Output Summary
After execution, you'll have:
- **Local files**: 8 files in `output/` directory
- **Cloud files**: 2 files in `gdrive:CITS3200/WeekY/`
- **Clean project**: No temporary files left behind

## Configuration

### Template Files
- **Location**: `templates/` directory
- **Pre-processing**: Templates have been cleaned up:
  - Removed extraneous sheets (Sheet2, Sheet3) from booked hours template
  - Updated team member names in group template
  - Configured for dynamic data mapping

### Output Configuration
- **Local Output**: `output/` directory
- **Cloud Output**: `gdrive:CITS3200/WeekY/` directory
- **File Naming**: Consistent naming convention with week numbers

## Dependencies

### Required Python Packages
```
openpyxl>=3.0.0
pandas>=1.3.0
```

### System Requirements
- **Python**: 3.8 or higher
- **rclone**: Configured for Google Drive access
- **Operating System**: macOS, Linux, or Windows

## Technical Details

### Data Transfer Method
- **Cell Values Only**: Uses `openpyxl.load_workbook(data_only=True)` to read actual values
- **Dynamic Mapping**: Programmatically finds team member rows in both source and target sheets
- **Error Handling**: Comprehensive try-catch blocks for robust operation

### Google Drive Integration
- **Directory Creation**: Automatically creates week-specific directories
- **File Upload**: Uploads group timesheet and zip file
- **Error Handling**: Graceful handling of network and permission issues

### Cleanup Process
- **Temporary File Removal**: Deletes downloaded master file after processing
- **Project Hygiene**: Maintains clean project directory

## Troubleshooting

### Common Issues
1. **rclone not configured**: Ensure rclone is set up for Google Drive access
2. **Template files missing**: Verify templates are in `templates/` directory
3. **Permission errors**: Check Google Drive permissions and rclone configuration
4. **Python environment**: Ensure virtual environment is activated

### Error Messages
- `❌ Error copying master file`: Check rclone configuration and file path
- `❌ Error transferring data`: Verify template file structure
- `❌ Error uploading to Google Drive`: Check network connection and permissions

## Notes
- **Cell Values**: Script reads cell values, not formulas, to avoid translation issues
- **Team Names**: Team member names are automatically updated from master sheet
- **Templates**: Templates serve as the base format for all output files
- **Week Numbers**: Only supports weeks 2-11 (typical CITS3200 semester)
- **Backup Strategy**: Files are stored both locally and in Google Drive

## Future Enhancements
- Support for different semester configurations
- Additional output formats (PDF, CSV)
- Email notification of completion
- Batch processing for multiple weeks
