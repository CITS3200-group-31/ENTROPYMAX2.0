import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QFrame, QMessageBox, QLabel, QMenuBar,
                             QMenu)
from PyQt6.QtCore import QTimer
from components.control_panel import ControlPanel
from components.group_detail_popup import GroupDetailPopup
from components.fullscreen_chart_widget import FullscreenChartWidget
from components.fullscreen_map_sample_widget import FullscreenMapSampleWidget
from utils.csv_export import export_analysis_results
from help import FormatExamplesDialog

# Import sample GPS CH, RS AND K mock data
from sample_data import SAMPLE_CH_RS_DATA, get_optimal_k
import os
import sys
import shutil
import subprocess
import pandas as pd
import pyarrow.parquet as pq
import time


class BentoBox(QFrame):
    """A styled frame to create the bento box effect."""
    def __init__(self, parent=None, title=""):
        super().__init__(parent)
        self.title = title
        self.setStyleSheet("""
            BentoBox {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        self.setFrameShape(QFrame.Shape.NoFrame)


class EntropyMaxFinal(QMainWindow):
    """Final application with a minimalist, bento box design."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EntropyMax 2.0")
        self.setGeometry(100, 100, 1600, 900)
        self.setStyleSheet("""
            QMainWindow { 
                background-color: #f8f9fa; 
            }
            QStatusBar {
                background-color: #ffffff;
                border-top: 1px solid #e0e0e0;
                font-size: 12px;
                color: #666;
            }
        """)
        
        # State variables
        self.input_file_path = None
        self.gps_file_path = None
        self.output_file_path = None
        self.selected_samples = []
        self.current_analysis_data = {}
        self.group_detail_popup = GroupDetailPopup()
        
        self._setup_ui()
        self._setup_menu()
        self._connect_signals()
        self._reset_workflow()
        
    def _setup_ui(self):
        """Initialize the bento box UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Left panel: Controls (fixed width)
        left_panel = BentoBox(title="Controls")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        self.control_panel = ControlPanel()
        left_layout.addWidget(self.control_panel)
        left_layout.addStretch()
        left_panel.setFixedWidth(340)
        main_layout.addWidget(left_panel)
        
        # Right panel: Data visualization (fixed layout, no resizing)
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        # Top right: Map and sample list with fullscreen capability
        top_box = BentoBox()
        top_layout = QVBoxLayout(top_box)
        top_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create fullscreen-capable map and sample widget
        self.map_sample_widget = FullscreenMapSampleWidget()
        self.map_widget = self.map_sample_widget.map_widget
        self.sample_list = self.map_sample_widget.sample_list
        top_layout.addWidget(self.map_sample_widget)
        
        # Add top container to right layout with stretch factor
        right_layout.addWidget(top_box, 5)  # 5:4 ratio for top:bottom
        
        # Bottom right: Charts (fixed layout)
        bottom_container = QWidget()
        bottom_layout = QHBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(15)
        
        # CH Chart with fullscreen capability
        ch_box = BentoBox(title="CH Analysis")
        ch_layout = QVBoxLayout(ch_box)
        ch_layout.setContentsMargins(10, 10, 10, 10)
        
        self.ch_chart = FullscreenChartWidget(
            title="CH Index",
            ylabel="CH Index",
            chart_title_display="Calinski-Harabasz Index"
        )
        ch_layout.addWidget(self.ch_chart)
        bottom_layout.addWidget(ch_box)
        
        # Rs Chart with fullscreen capability
        rs_box = BentoBox(title="Rs Analysis")
        rs_layout = QVBoxLayout(rs_box)
        rs_layout.setContentsMargins(10, 10, 10, 10)
        
        self.rs_chart = FullscreenChartWidget(
            title="Rs %",
            ylabel="Rs %",
            chart_title_display="Rs Percentage"
        )
        rs_layout.addWidget(self.rs_chart)
        bottom_layout.addWidget(rs_box)

        
        
        # Add bottom container to right layout with stretch factor
        right_layout.addWidget(bottom_container, 4)  # 5:4 ratio for top:bottom
        
        main_layout.addWidget(right_container)
    
    def _setup_menu(self):
        """Setup the menu bar with Help menu."""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #ffffff;
                border-bottom: 1px solid #e0e0e0;
                padding: 5px;
            }
            QMenuBar::item {
                padding: 5px 10px;
                background: transparent;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #e0f2f1;
            }
            QMenuBar::item:pressed {
                background-color: #b2dfdb;
            }
        """)
        
        # Help menu
        help_menu = QMenu('Help', self)
        help_menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
            }
            QMenu::item {
                padding: 8px 25px;
                background: transparent;
            }
            QMenu::item:selected {
                background-color: #e0f2f1;
            }
        """)
        
        # Add Format Examples action
        format_action = help_menu.addAction('Format Examples')
        format_action.triggered.connect(self._show_format_examples)
        
        menubar.addMenu(help_menu)
    
    def _show_format_examples(self):
        """Show dialog with format examples for CSV files."""
        dialog = FormatExamplesDialog(self)
        dialog.exec()
        
    def _connect_signals(self):
        """Connect all signals to their handlers."""
        self.control_panel.inputFileSelected.connect(self._on_input_file_selected)
        self.control_panel.gpsFileSelected.connect(self._on_gps_file_selected)
        self.control_panel.outputFileSelected.connect(self._on_output_file_selected)
        self.control_panel.generateMapRequested.connect(self._on_generate_map)
        self.control_panel.runAnalysisRequested.connect(self._on_run_analysis)
        self.control_panel.showGroupDetailsRequested.connect(self._on_show_group_details)
        self.control_panel.exportResultsRequested.connect(self._on_export_results)
        
        # Connect signals from the fullscreen map-sample widget
        self.map_sample_widget.selectionChanged.connect(self._on_selection_changed)
        self.map_sample_widget.sampleLocateRequested.connect(self._on_locate_sample)
        
    def _on_input_file_selected(self, file_path):
        self.input_file_path = file_path
        # Lightweight validation: ensure file is readable and first column is a sample identifier
        try:
            df_head = pd.read_csv(file_path, nrows=1)
            if df_head.shape[1] < 2:
                raise ValueError("Expected at least 2 columns (Sample + data bins).")
            first_col = str(df_head.columns[0]).strip().lower()
            if "sample" not in first_col:
                raise ValueError("First column header should contain 'Sample'.")
            self.statusBar().showMessage("Raw data file loaded successfully.", 3000)
        except Exception as e:
            QMessageBox.warning(self, "Raw Data File Validation", str(e))
            self.input_file_path = None
            self.control_panel.input_file = None
            self.control_panel.input_label.setText("No file selected")
            self.control_panel.input_label.setStyleSheet("color: gray; padding: 5px;")
            self.control_panel._update_button_states()
    
    def _on_gps_file_selected(self, file_path):
        self.gps_file_path = file_path
        # Lightweight validation: ensure required columns are present
        try:
            df_head = pd.read_csv(file_path, nrows=1)
            cols = [str(c).strip().lower() for c in df_head.columns]
            has_sample = any("sample" in c for c in cols)
            has_lat = any("lat" in c for c in cols)
            has_lon = any(("lon" in c) or ("long" in c) for c in cols)
            if not (has_sample and has_lat and has_lon):
                raise ValueError("GPS CSV must include Sample, Latitude and Longitude columns.")
            self.statusBar().showMessage("GPS file loaded successfully.", 3000)
        except Exception as e:
            QMessageBox.warning(self, "GPS File Validation", str(e))
            self.gps_file_path = None
            self.control_panel.gps_file = None
            self.control_panel.gps_label.setText("No GPS file selected")
            self.control_panel.gps_label.setStyleSheet("color: gray; padding: 5px;")
            self.control_panel._update_button_states()
        
    def _on_output_file_selected(self, file_path):
        self.output_file_path = file_path
        
    def _on_generate_map(self):
        """Load data from CSV and render map."""
        try:
            # Check both files are selected
            if not self.input_file_path or not self.gps_file_path:
                QMessageBox.warning(self, "Missing Files", 
                                  "Please select both grain size and GPS files.")
                return
            # Initial map load should NOT reflect analysis groupings. Always use GPS CSV
            # and set default group to 1 for all samples.
            markers = self._parse_gps_csv(self.gps_file_path)
            for m in markers:
                m['group'] = 1
            self.statusBar().showMessage("Map and sample list loaded from GPS data.", 3000)
            self.map_sample_widget.load_data(markers)
        except Exception as e:
            QMessageBox.critical(self, "Error Loading File", str(e))
            self._reset_workflow()
            
    def _on_selection_changed(self, selected_samples):
        self.selected_samples = selected_samples
        self.control_panel.run_analysis_btn.setEnabled(len(selected_samples) > 0)
        
    def _on_locate_sample(self, name, lat, lon):
        self.map_widget.zoom_to_location(lat, lon)
        
    def _on_run_analysis(self, params):
        """Run analysis on selected data."""
        selected_data = self.map_sample_widget.get_selected_samples_data()
        if not selected_data:
            QMessageBox.warning(self, "No Samples Selected", 
                              "Please select samples from the list.")
            return
        try:
            # 1) Run compiled backend to generate Parquet
            start_ts = time.time()
            self._run_compiled_backend()
            # 2) Load metrics from Parquet
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            # Wait briefly for a fresh, non-empty Parquet (handles slow AV/disk)
            parquet_path = None
            for _ in range(40):  # ~6s max
                latest = self._find_latest_parquet(project_root, min_mtime=start_ts)
                if latest and os.path.exists(latest):
                    try:
                        st = os.stat(latest)
                        # Require file modified at or after start time and non-empty
                        if st.st_mtime >= start_ts and st.st_size > 0:
                            parquet_path = latest
                            break
                    except Exception:
                        pass
                time.sleep(0.15)
            if not parquet_path:
                raise RuntimeError("Parquet not refreshed after backend run.")
            k_values, ch_values, rs_values, optimal_k = self._load_metrics_from_parquet(parquet_path)
            self.current_analysis_data = {
                **params,
                'num_samples': len(selected_data),
                'selected_samples': selected_data,
                'k_values': k_values,
                'ch_values': ch_values,
                'rs_values': rs_values,
                'optimal_k': optimal_k
            }
            # 3) Update group assignments on map/list for selected/optimal K
            try:
                k_for_groups = optimal_k if optimal_k is not None else (k_values[0] if k_values else None)
                if k_for_groups is not None:
                    sample_to_group = self._load_group_assignments(parquet_path, k_for_groups)
                    self._apply_group_assignments(sample_to_group)
            except Exception as ge:
                # Surface but do not block charts if grouping fails
                QMessageBox.warning(self, "Grouping Update Warning", str(ge))
            # 4) Refresh markers from freshly generated Parquet to avoid stale view
            try:
                markers = self._parse_markers_from_parquet(parquet_path)
                if markers:
                    self.map_sample_widget.load_data(markers)
            except Exception:
                pass
            self._plot_analysis_results()
            self.control_panel.enable_analysis_buttons(True)
            self.statusBar().showMessage("Analysis complete.", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Analysis Error", str(e))
        
    def _on_show_group_details(self):
        """Show group detail popups with line charts for each group."""
        if not self.input_file_path:
            QMessageBox.warning(self, "No Input File", 
                              "Please select an input file first.")
            return
        
        try:
            # Use a default k value or get it from analysis if available
            k_value = 4  # Default value
            
            # Load and show the popup windows with real data from CSV
            self.group_detail_popup.load_and_show_popups(self.input_file_path, k_value, x_unit='μm', y_unit='%')
            self.statusBar().showMessage(f"Showing details for {k_value} groups using real data.", 3000)
            
        except FileNotFoundError as e:
            QMessageBox.critical(self, "Error Loading Data", f"Input file not found: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error Showing Group Details", str(e))
    
    def _on_export_results(self):
        """Export current analysis results."""
        if not self.current_analysis_data:
            QMessageBox.warning(self, "No Results", 
                              "Please run an analysis first.")
            return
        
        try:
            saved_path = export_analysis_results(
                self.output_file_path, 
                self.current_analysis_data
            )
            QMessageBox.information(self, "Export Successful", 
                                f"Results saved to:\n{saved_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))
            
    def _plot_analysis_results(self):
        """Plot the analysis results."""
        k_values = self.current_analysis_data['k_values']
        ch_values = self.current_analysis_data['ch_values']
        rs_values = self.current_analysis_data['rs_values']
        optimal_k = self.current_analysis_data['optimal_k']
        
        self.ch_chart.plot_data(k_values, ch_values, '#2196F3', 'o', 'CH Index')  # Blue
        self.rs_chart.plot_data(k_values, rs_values, '#4CAF50', 's', 'Rs %')  # Green
        # self.group_graph_widget.plot_analysis_results(x_values, group_values, peak_k)
        # self.group_graph_widget.plot_analysis_results(x_values, group_values)
        
        if optimal_k is not None:
            idx = list(k_values).index(optimal_k)
            self.ch_chart.add_optimal_marker(optimal_k, ch_values[idx])
            
    def _reset_workflow(self):
        """Reset the UI to its initial state."""
        # Reset file paths
        self.input_file_path = None
        self.gps_file_path = None
        self.output_file_path = None
        self.selected_samples = []
        # Reset UI components
        self.control_panel.reset_workflow()
        self.map_sample_widget.load_data([])
        self.ch_chart.clear()
        self.rs_chart.clear()
        self.group_detail_popup.close_all()
        self.current_analysis_data = {}
        self.statusBar().showMessage("Workflow reset. Select input files to begin.", 5000)
        
    def _parse_gps_csv(self, file_path):
        """Parse GPS CSV file to get marker data."""
        # For now, use the sample GPS data as fallback
        # In production, this should read from the parquet file
        import pandas as pd
        try:
            df = pd.read_csv(file_path)
            # Handle various column name formats
            col_mapping = {}
            for col in df.columns:
                col_lower = col.lower().strip()
                if 'sample' in col_lower or 'name' in col_lower:
                    col_mapping['name'] = col
                elif 'lat' in col_lower:
                    col_mapping['lat'] = col
                elif 'lon' in col_lower or 'long' in col_lower:
                    col_mapping['lon'] = col
            
            if 'name' in col_mapping and 'lat' in col_mapping and 'lon' in col_mapping:
                markers = []
                for _, row in df.iterrows():
                    markers.append({
                        'name': str(row[col_mapping['name']]),
                        'lat': float(row[col_mapping['lat']]),
                        'lon': float(row[col_mapping['lon']]),
                        'group': 1,  # Default group, will be updated after analysis
                        'selected': False
                    })
                return markers
            else:
                raise ValueError("GPS file missing required columns")
        except Exception as e:
            print(f"Error parsing GPS file: {e}")

    def _parse_markers_from_parquet(self, parquet_path):
        """Parse markers (name, lat, lon, optional group) from Parquet output."""
        table = pq.read_table(parquet_path)
        cols = [f.name for f in table.schema]
        def find_col(sub):
            for c in cols:
                if sub.lower() in c.lower():
                    return c
            return None
        name_col = 'Sample' if 'Sample' in cols else find_col('sample')
        lat_col = 'latitude' if 'latitude' in cols else find_col('latitude')
        lon_col = 'longitude' if 'longitude' in cols else find_col('longitude')
        grp_col = 'Group' if 'Group' in cols else find_col('group')
        if not name_col or not lat_col or not lon_col:
            return []
        df = table.select([c for c in [name_col, lat_col, lon_col, grp_col] if c]).to_pandas()
        df = df.dropna(subset=[name_col, lat_col, lon_col])
        # Deduplicate on name (first occurrence)
        df = df.drop_duplicates(subset=[name_col], keep='first')
        markers = []
        for _, row in df.iterrows():
            try:
                markers.append({
                    'name': str(row[name_col]).strip(),
                    'lat': float(row[lat_col]),
                    'lon': float(row[lon_col]),
                    'group': int(row[grp_col]) if grp_col and pd.notna(row[grp_col]) else 1,
                    'selected': False
                })
            except Exception:
                continue
        return markers

    def _find_backend_executable(self):
        """Locate the compiled backend runner executable across common build layouts."""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidates = [
            os.path.join(project_root, 'backend', 'build-vcpkg', 'Release', 'run_entropymax.exe'),
            os.path.join(project_root, 'backend', 'build-vcpkg', 'Debug', 'run_entropymax.exe'),
            os.path.join(project_root, 'backend', 'build-vcpkg', 'run_entropymax.exe'),
            os.path.join(project_root, 'backend', 'build', 'run_entropymax.exe'),
            os.path.join(project_root, 'backend', 'build', 'Release', 'run_entropymax.exe'),
            os.path.join(project_root, 'backend', 'build', 'Debug', 'run_entropymax.exe'),
            os.path.join(project_root, 'backend', 'run_entropymax.exe'),
            os.path.join(project_root, 'run_entropymax.exe'),
            os.path.join(project_root, 'backend', 'build', 'run_entropymax'),
        ]
        for p in candidates:
            if os.path.exists(p):
                return p
        return None

    def _run_compiled_backend(self):
        """Copy selected inputs into backend expected locations and execute the runner."""
        if not self.input_file_path or not self.gps_file_path:
            raise RuntimeError("Input and GPS files must be selected before running analysis.")
        exe_path = self._find_backend_executable()
        if not exe_path:
            raise FileNotFoundError("Could not locate run_entropymax executable. Please build the backend.")
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_raw = os.path.join(project_root, 'data', 'raw')
        os.makedirs(data_raw, exist_ok=True)
        # Remove stale Parquet before running
        try:
            out_dir = os.path.join(project_root, 'data', 'parquet')
            os.makedirs(out_dir, exist_ok=True)
            stale = os.path.join(out_dir, 'output.parquet')
            if os.path.exists(stale):
                os.remove(stale)
        except Exception:
            pass
        target_raw = os.path.join(data_raw, 'sample_input.csv')
        target_gps = os.path.join(data_raw, 'sample_coordinates.csv')
        def _same_path(a, b):
            try:
                return os.path.samefile(a, b)
            except Exception:
                return os.path.normcase(os.path.normpath(a)) == os.path.normcase(os.path.normpath(b))
        try:
            if not _same_path(self.input_file_path, target_raw):
                shutil.copyfile(self.input_file_path, target_raw)
            if not _same_path(self.gps_file_path, target_gps):
                shutil.copyfile(self.gps_file_path, target_gps)
        except Exception as e:
            raise RuntimeError(f"Failed to stage input files: {e}")
        # Execute backend with fixed IO paths (runner ignores CLI args)
        try:
            proc = subprocess.run([exe_path], cwd=project_root, capture_output=True, text=True, timeout=180)
        except subprocess.TimeoutExpired:
            raise TimeoutError("Backend execution timed out.")
        if proc.returncode != 0:
            stderr = proc.stderr.strip()
            stdout = proc.stdout.strip()
            raise RuntimeError(f"Backend failed (exit {proc.returncode}).\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}")
        # Wait for Parquet to be generated
        parquet_path = os.path.join(project_root, 'data', 'parquet', 'output.parquet')
        if not os.path.exists(parquet_path):
            raise FileNotFoundError(f"Expected Parquet not found after backend run: {parquet_path}")
        # Wait for Parquet to be generated
        max_wait_time = 30 # seconds
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            if os.path.exists(parquet_path):
                break
            time.sleep(1)
        if not os.path.exists(parquet_path):
            raise FileNotFoundError(f"Parquet file did not appear after backend run: {parquet_path}")

    def _load_metrics_from_parquet(self, parquet_path):
        """Extract k, CH and Rs series and optimal K from the processed Parquet."""
        table = pq.read_table(parquet_path)
        cols = [f.name for f in table.schema]
        # Find column names robustly
        def find_col(sub):
            for c in cols:
                if sub.lower() in c.lower():
                    return c
            return None
        k_col = 'K' if 'K' in cols else find_col('k')
        ch_col = find_col('Calinski-Harabasz')
        rs_col = find_col('% explained')
        if not k_col or not ch_col or not rs_col:
            raise ValueError(f"Required columns not found in Parquet. Have: {cols}")
        df = table.select([k_col, ch_col, rs_col]).to_pandas()
        # Aggregate by K (values repeated per row within K)
        agg = df.groupby(k_col, as_index=False).first().sort_values(k_col)
        k_values = agg[k_col].to_list()
        ch_values = agg[ch_col].astype(float).to_list()
        rs_values = agg[rs_col].astype(float).to_list()
        # Optimal K by max CH
        if len(ch_values) == 0:
            raise ValueError("No CH values found in Parquet.")
        optimal_idx = int(pd.Series(ch_values).idxmax())
        optimal_k = int(k_values[optimal_idx])
        return k_values, ch_values, rs_values, optimal_k

    def _load_group_assignments(self, parquet_path, k_value):
        """Return mapping of sample name -> group id for a given K from Parquet."""
        table = pq.read_table(parquet_path)
        cols = [f.name for f in table.schema]
        def find_col(sub):
            for c in cols:
                if sub.lower() in c.lower():
                    return c
            return None
        k_col = 'K' if 'K' in cols else find_col('k')
        group_col = 'Group' if 'Group' in cols else find_col('group')
        sample_col = 'Sample' if 'Sample' in cols else find_col('sample')
        if not k_col or not group_col or not sample_col:
            raise ValueError(f"Required columns not found for grouping. Have: {cols}")
        # Filter rows by K == k_value
        # Use Pandas for robust filtering by K
        df_all = table.select([sample_col, group_col, k_col]).to_pandas()
        df = df_all[df_all[k_col] == k_value]
        if df.empty:
            raise ValueError(f"No rows found for K={k_value} in Parquet.")
        mapping = {}
        for _, row in df.iterrows():
            name = str(row[sample_col]).strip()
            try:
                grp = int(row[group_col])
            except Exception:
                continue
            if name and name not in mapping:
                mapping[name] = grp
        if not mapping:
            raise ValueError("Grouping mapping is empty after filtering.")
        return mapping

    def _apply_group_assignments(self, sample_to_group):
        """Apply group ids to current markers and refresh view while preserving selection."""
        markers = list(self.map_sample_widget.markers_data) if hasattr(self.map_sample_widget, 'markers_data') else []
        if not markers:
            return
        selected_before = list(self.map_sample_widget.selected_samples)
        for m in markers:
            name = str(m.get('name','')).strip()
            if name in sample_to_group:
                m['group'] = int(sample_to_group[name])
        self.map_sample_widget.load_data(markers)
        # Restore selection
        if selected_before:
            self.map_sample_widget.sample_list.set_selection(selected_before)

    def _find_latest_parquet(self, project_root, min_mtime=None):
        """Return the path to the newest .parquet in data/parquet (optionally newer than min_mtime)."""
        try:
            pdir = os.path.join(project_root, 'data', 'parquet')
            if not os.path.isdir(pdir):
                return None
            candidates = []
            for name in os.listdir(pdir):
                if name.lower().endswith('.parquet'):
                    full = os.path.join(pdir, name)
                    try:
                        st = os.stat(full)
                        if min_mtime is None or st.st_mtime >= float(min_mtime):
                            candidates.append((st.st_mtime, full))
                    except Exception:
                        continue
            if not candidates:
                return None
            candidates.sort(reverse=True)
            return candidates[0][1]
        except Exception:
            return None


if __name__ == '__main__':
    # Graceful Ctrl+C/SIGTERM handling
    import signal
    def _handle_sig(signum, frame):
        try:
            _app = QApplication.instance()
            if _app is not None:
                _app.quit()
        except Exception:
            pass
    try:
        signal.signal(signal.SIGINT, _handle_sig)
    except Exception:
        pass
    try:
        signal.signal(signal.SIGTERM, _handle_sig)
    except Exception:
        pass

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Timer tick ensures Python signal handlers are processed during Qt event loop
    _sig_timer = QTimer()
    _sig_timer.timeout.connect(lambda: None)
    _sig_timer.start(250)

    window = EntropyMaxFinal()
    window.show()

    # Debug mode: preload sample files and default output
    try:
        if '--debug' in sys.argv:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            input_path = os.path.join(project_root, 'data', 'raw', 'inputs', 'sample_group_3_input.csv')
            gps_path = os.path.join(project_root, 'data', 'raw', 'gps', 'sample_group_3_coordinates.csv')
            output_path = os.path.join(project_root, 'output.csv')

            cp = window.control_panel

            # Preload input CSV
            cp.input_file = input_path
            cp.input_label.setText(f"✓ {os.path.basename(input_path)}")
            cp.input_label.setStyleSheet("color: green; padding: 5px;")
            cp.inputFileSelected.emit(input_path)

            # Preload GPS CSV
            cp.gps_file = gps_path
            cp.gps_label.setText(f"✓ {os.path.basename(gps_path)}")
            cp.gps_label.setStyleSheet("color: green; padding: 5px;")
            cp.gpsFileSelected.emit(gps_path)

            # Preload output CSV (project root)
            cp.output_file = output_path
            display_name = os.path.basename(output_path)
            if display_name.endswith('.csv'):
                display_name = display_name[:-4]
            cp.output_label.setText(f"✓ {display_name}")
            cp.output_label.setStyleSheet("color: green; padding: 5px;")
            cp.outputFileSelected.emit(output_path)

            cp._update_button_states()
            window.statusBar().showMessage("Debug mode: preloaded sample files.", 3000)
    except Exception as e:
        # Surface debug preload issues in the console without interrupting the app
        print(f"DEBUG preload failed: {e}", file=sys.stderr)
    sys.exit(app.exec())
