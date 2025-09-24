# Frontend Overview

This document describes the modular PyQt6 frontend in `frontend/`: what each part does, how to run it, and the overall application workflow.

## Layout

```
frontend/
├── main.py                     # Main application entry point
├── components/
│   ├── control_panel.py        # UI for file selection and analysis parameters
│   ├── interactive_map_widget.py # Interactive map for sample selection
│   ├── sample_list_widget.py   # List of samples with selection
│   ├── simple_map_sample_widget.py # Combined map and sample list view
│   ├── group_detail_popup.py   # Popup windows for group analysis
│   ├── chart_widget.py         # Reusable widget for plotting CH and Rs
│   ├── module_preview_card.py  # UI card for each module in the main window
│   └── ...
├── utils/
│   └── csv_export.py           # Utility for exporting analysis results
├── help/
│   └── format_examples_dialog.py # Dialog showing CSV format examples
├── interactive_map.html        # HTML template for the map
└── requirements.txt            # Python dependencies
```

## Responsibilities

- **`main.py`**:
    - The main entry point for the application.
    - Initializes the main window (`EntropyMaxFinal`), which holds the control panel and module preview cards.
    - Manages the overall application state, including file paths, analysis data, and window references.
    - Connects signals and slots between different components to orchestrate the workflow.

- **`components/control_panel.py`**:
    - Provides the main user interface for interacting with the application.
    - Follows a step-by-step workflow:
        1.  **Input Data**: Select input grain size and GPS CSV files.
        2.  **Analysis Parameters**: Configure parameters like group range and processing options.
        3.  **Generate Map**: Load GPS data and display samples on the map.
        4.  **Run Analysis**: Execute the analysis (currently using mock data).
        5.  **Show Group Details**: Open popups with detailed charts for each group.
        6.  **Export Results**: Save analysis results to a CSV file.

- **`components/interactive_map_widget.py`**:
    - Displays an interactive map using `folium` and `QWebEngineView`.
    - Allows users to select samples directly on the map via clicking, box selection, and multi-selection (Option on Mac and Alt on Win).
    - Visualizes sample locations and their assigned groups with colored markers.
    - Communicates with the Python backend via a `QWebChannel` bridge.

- **`components/sample_list_widget.py`**:
    - Displays a list of all samples loaded from the GPS data.
    - Allows for sample selection, which is synchronized with the map.
    - Provides a "Locate" button to zoom to a specific sample on the map.

- **`components/simple_map_sample_widget.py`**:
    - A container widget that combines the `InteractiveMapWidget` and `SampleListWidget` in a splitter view.

- **`components/group_detail_popup.py`**:
    - Manages and displays popup windows, one for each group identified by the analysis.
    - Each popup contains a line chart (`pyqtgraph`) showing the grain size distribution for all samples within that group.
    - Allows for highlighting a specific sample's line chart by clicking on it.

- **`components/chart_widget.py`**:
    - A reusable widget for displaying analysis results like the Calinski-Harabasz (CH) index and Rs percentage.
    - Used in standalone windows for CH and Rs analysis.

- **`utils/csv_export.py`**:
    - A utility function to export the analysis parameters and results into a formatted CSV file.

- **`help/format_examples_dialog.py`**:
    - A simple dialog that shows users the expected format for the input CSV files (GPS and grain size).

## Data Workflow

1.  **File Selection**: The user selects a grain size data CSV and a GPS coordinates CSV via the `ControlPanel`.
2.  **Map Generation**:
    - The GPS CSV is parsed to extract sample names and their latitude/longitude coordinates.
    - The `InteractiveMapWidget` renders these locations as selectable markers on a map.
    - The `SampleListWidget` is populated with the sample names.
3.  **Analysis**:
    - The user triggers the analysis from the `ControlPanel`.
    - Currently, this uses mock data to generate CH and Rs values for a range of `k` (number of groups).
    - The results are plotted in the `ChartWidget` windows.
4.  **Group Visualization**:
    - The user requests to see group details.
    - The `GroupDetailPopup` manager reads the actual grain size CSV and creates a separate popup window for each group.
    - Each popup displays an overlay of line charts, where each line represents a sample's grain size distribution.
5.  **Export**:
    - The user exports the results.
    - The `csv_export` utility writes the analysis parameters, selected samples, and CH/Rs values to a new CSV file.

## Logic Workflow

The application is event-driven, using PyQt's signal and slot mechanism.

1.  **Initialization**: `EntropyMaxFinal` in `main.py` sets up the main UI, including the `ControlPanel` and the preview cards for different modules (Map, CH Analysis, Rs Analysis).
2.  **File Loading**:
    - The user clicks "Select Input CSV" or "Select GPS CSV" in the `ControlPanel`.
    - A file dialog opens. Upon selection, the `ControlPanel` emits a signal (`inputFileSelected` or `gpsFileSelected`).
    - `EntropyMaxFinal` receives this signal and updates its internal state with the file path. The backend's validation functions are called to check the CSV structure.
3.  **Map Generation**:
    - Once both files are selected, the "Generate Map" button is enabled.
    - Clicking it emits the `generateMapRequested` signal from the `ControlPanel`.
    - `EntropyMaxFinal`'s `_on_generate_map` slot is called, which parses the GPS data and loads it into the `SimpleMapSampleWidget`.
4.  **Sample Selection**:
    - The user can select samples in the `InteractiveMapWidget` or the `SampleListWidget`.
    - Selection changes in one widget emit a `selectionChanged` signal, which is received by the other widget to keep the selection synchronized.
5.  **Analysis Execution**:
    - The "Run Analysis" button (enabled after map generation) emits the `runAnalysisRequested` signal.
    - `EntropyMaxFinal`'s `_on_run_analysis` slot is triggered. It gathers parameters from the `ControlPanel`, runs the analysis (currently with mock data), and plots the results on the CH and Rs chart widgets.
6.  **Viewing Group Details**:
    - The "Show Group Details" button (enabled after analysis) emits `showGroupDetailsRequested`.
    - `EntropyMaxFinal`'s `_on_show_group_details` slot calls the `GroupDetailPopup` manager to load the grain size data and display the popup windows for each group.
7.  **Exporting Results**:
    - The "Export Results" button emits `exportResultsRequested`.
    - `EntropyMaxFinal`'s `_on_export_results` slot opens a file save dialog and then calls the `export_analysis_results` function to write the data to a CSV file.

## How to Run

1.  **Install Dependencies**:
    ```bash
    pip install -r frontend/requirements.txt
    ```

2.  **Run the Application**:
    ```bash
    python frontend/main.py
    ```
