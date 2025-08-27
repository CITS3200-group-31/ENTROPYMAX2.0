## Environment

```shell
# Install Brew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install --cask anaconda
conda init
conda create -n entro python=3.11
conda activate entro
pip install -r requirements.txt
python main.py
```

## Tests

### Group Details Module

```shell
# Make sure you are in the root directory
python frontend/test/test_group_details.py
```

## Data Usage Declaration

- Currently, the CH Index, RS Percentage, and Interactive Map Module utilize mock data from `frontend/sample_data.py`.
  - The mock data is formatted as a dictionary.
- The Group Details module employs actual data and includes a function `_parse_csv_data`, which can directly read `frontend/test/data/Input file GP for Entropy 20240910.csv` for testing purposes.
  - As indicated by `_on_show_group_details` in `main.py`, I assume the k value is 4. The `group_detail_popup.load_and_show_popups` function will read this k value and process the `grouped_samples`.

## Workflow Mermaid

```mermaid
flowchart TD
    A[Launch Application] --> B[Select Input CSV]
    B --> C[Define Output File]
    C --> D[Set Parameters]
    D --> E[Generate Map View]
    E --> F[Select Samples]
    F --> G[Run Analysis]
    G --> H[Show Group Details]
    G --> I[Export Results]

    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#f3e5f5
    style D fill:#f3e5f5
    style E fill:#e8f5e8
    style F fill:#fff3e0
    style G fill:#ffebee
    style H fill:#f3e5f5
    style I fill:#e8f5e8

    classDef inputStep fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px
    classDef processStep fill:#e8f5e8,stroke:#4caf50,stroke-width:2px
    classDef analysisStep fill:#ffebee,stroke:#f44336,stroke-width:2px
    classDef outputStep fill:#fff3e0,stroke:#ff9800,stroke-width:2px

    class B,C,D,H inputStep
    class E,I processStep
    class G analysisStep
    class F outputStep
```

### Component Architecture

```
Frontend
├── main.py (Main Application Window)
├── components/
│   ├── control_panel.py (Control Panel - Workflow Management)
│   ├── map_widget.py (Map Component - Sample Visualization)
│   ├── chart_widget.py (Chart Component - CH/Rs Analysis Charts)
│   ├── sample_list_widget.py (Sample List - Selection Management)
│   └── group_detail_popup.py (Group Detail Popup - Detailed Analysis)
├── utils/
│   └── csv_export.py (Results Export Utility)
└── sample_data.py (Test Data)
```

### Data Flow

```mermaid
flowchart LR
    CSV[Input CSV File] --> Parser[Data Parser]
    Parser --> Map[Map Component]
    Parser --> List[Sample List]
    List --> Selector[Sample Selector]
    Selector --> Analysis[Analysis Engine]
    Analysis --> Charts[CH/Rs Charts]
    Analysis --> Details[Group Details]
    Charts --> Export[Exporter]
    Details --> Export
    Export --> CSV_Out[Output CSV Report]

    style CSV fill:#e3f2fd
    style CSV_Out fill:#c8e6c9
    style Analysis fill:#ffebee
```