import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QFrame, QMessageBox, QMenu, QFileDialog)
from components.control_panel import ControlPanel
from components.group_detail_popup import GroupDetailPopup
from components.module_preview_card import ModulePreviewCard
from components.standalone_window import StandaloneWindow
from components.simple_map_sample_widget import SimpleMapSampleWidget
from components.chart_widget import ChartWidget
from utils.csv_export import export_analysis_results
from help import FormatExamplesDialog

# Import sample GPS CH, RS AND K mock data
from sample_data import SAMPLE_CH_RS_DATA, get_optimal_k


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
    """Main application with module preview cards."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EntropyMax 2.0")
        self.setGeometry(100, 100, 1200, 700)
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
        
        # Window references
        self.map_window = None
        self.ch_window = None
        self.rs_window = None
        
        self._setup_ui()
        self._setup_menu()
        self._init_standalone_windows()
        self._connect_signals()
        self._reset_workflow()
        
    def _setup_ui(self):
        """Initialize UI with preview cards."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Left panel: Controls
        left_panel = BentoBox(title="Controls")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        self.control_panel = ControlPanel()
        left_layout.addWidget(self.control_panel)
        left_layout.addStretch()
        left_panel.setFixedWidth(340)
        main_layout.addWidget(left_panel)
        
        # Right panel: Module preview cards
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        # Map preview card
        self.map_preview_card = ModulePreviewCard(
            title="Map & Sample List",
            description="View GPS locations and manage sample selection"
        )
        self.map_preview_card.openRequested.connect(self._open_map_window)
        right_layout.addWidget(self.map_preview_card)
        
        # CH analysis preview card
        self.ch_preview_card = ModulePreviewCard(
            title="CH Analysis",
            description="Calinski-Harabasz Index visualization"
        )
        self.ch_preview_card.openRequested.connect(self._open_ch_window)
        right_layout.addWidget(self.ch_preview_card)
        
        # RS analysis preview card
        self.rs_preview_card = ModulePreviewCard(
            title="Rs Analysis", 
            description="Rs Percentage visualization"
        )
        self.rs_preview_card.openRequested.connect(self._open_rs_window)
        right_layout.addWidget(self.rs_preview_card)
        
        right_layout.addStretch()
        main_layout.addWidget(right_container)
    
    def _init_standalone_windows(self):
        """Initialize standalone window components"""
        # Map window
        self.map_sample_widget = SimpleMapSampleWidget()
        self.map_window = StandaloneWindow("Map & Sample List", self.map_sample_widget)
        self.map_window.exportRequested.connect(lambda: self._export_window_content(self.map_sample_widget, "map"))
        self.map_widget = self.map_sample_widget.map_widget
        self.sample_list = self.map_sample_widget.sample_list
        
        # CH chart window
        self.ch_chart = ChartWidget(
            title="CH Index",
            ylabel="CH Index"
        )
        self.ch_window = StandaloneWindow("CH Analysis", self.ch_chart)
        self.ch_window.exportRequested.connect(lambda: self._export_window_content(self.ch_chart, "ch"))
        
        # RS chart window
        self.rs_chart = ChartWidget(
            title="Rs %",
            ylabel="Rs %"
        )
        self.rs_window = StandaloneWindow("Rs Analysis", self.rs_chart)
        self.rs_window.exportRequested.connect(lambda: self._export_window_content(self.rs_chart, "rs"))
    
    def _open_map_window(self):
        """Open map window"""
        if self.map_window:
            self.map_window.show()
            self.map_window.raise_()
            self.map_window.activateWindow()
    
    def _open_ch_window(self):
        """Open CH analysis window"""
        if self.ch_window:
            self.ch_window.show()
            self.ch_window.raise_()
            self.ch_window.activateWindow()
    
    def _open_rs_window(self):
        """Open RS analysis window"""
        if self.rs_window:
            self.rs_window.show()
            self.rs_window.raise_()
            self.rs_window.activateWindow()
    
    def _export_window_content(self, widget, window_type):
        """Export window content as PNG"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            f"Export {window_type.upper()} as PNG",
            f"{window_type}_export.png",
            "PNG Files (*.png)"
        )
        
        if file_path:
            pixmap = widget.grab()
            pixmap.save(file_path)
            self.statusBar().showMessage(f"Exported to {file_path}", 3000)
    
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
        self.control_panel.generateMapRequested.connect(self._on_generate_map)
        self.control_panel.runAnalysisRequested.connect(self._on_run_analysis)
        self.control_panel.showGroupDetailsRequested.connect(self._on_show_group_details)
        self.control_panel.exportResultsRequested.connect(self._on_export_results)
        
        # Connect signals from map-sample widget
        self.map_sample_widget.selectionChanged.connect(self._on_selection_changed)
        self.map_sample_widget.sampleLocateRequested.connect(self._on_locate_sample)
        
        # Connect signal from group detail popup to sample list
        self.group_detail_popup.sampleLineClicked.connect(self._on_sample_line_clicked)
        
    def _on_input_file_selected(self, file_path):
        self.input_file_path = file_path
        # Validate raw data file using backend validation
        try:
            import sys
            import os
            
            # Add backend path to sys.path
            backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'src', 'io')
            if backend_path not in sys.path:
                sys.path.append(backend_path)
            
            from validate_csv_raw import validate_csv_structure
            
            validate_csv_structure(file_path)
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
        # Validate GPS file using backend validation
        try:
            import sys
            import os
            
            # Add backend path to sys.path
            backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'src', 'io')
            if backend_path not in sys.path:
                sys.path.append(backend_path)
            
            from validate_csv_gps import validate_csv_gps_structure
            
            validate_csv_gps_structure(file_path)
            self.statusBar().showMessage("GPS file loaded successfully.", 3000)
        except Exception as e:
            QMessageBox.warning(self, "GPS File Validation", str(e))
            self.gps_file_path = None
            self.control_panel.gps_file = None
            self.control_panel.gps_label.setText("No GPS file selected")
            self.control_panel.gps_label.setStyleSheet("color: gray; padding: 5px;")
            self.control_panel._update_button_states()
        
    def _on_generate_map(self):
        """Load data from CSV and render map."""
        try:
            # Check both files are selected
            if not self.input_file_path or not self.gps_file_path:
                QMessageBox.warning(self, "Missing Files", 
                                  "Please select both grain size and GPS files.")
                return
            
            # Parse GPS file to get coordinates
            markers = self._parse_gps_csv(self.gps_file_path)
            self.map_sample_widget.load_data(markers)
            
            # Update preview cards status
            self.map_preview_card.update_status(f"Loaded {len(markers)} samples")
            self.ch_preview_card.update_status("Ready for analysis")
            self.rs_preview_card.update_status("Ready for analysis")
            
            # Enable run analysis button after successful map generation
            self.control_panel.run_analysis_btn.setEnabled(True)
            self.statusBar().showMessage("Map and sample list loaded from GPS data. Analysis ready.", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error Loading File", str(e))
            self._reset_workflow()
            
    def _on_selection_changed(self, selected_samples):
        self.selected_samples = selected_samples
        
    def _on_locate_sample(self, name, lat, lon):
        self.map_widget.zoom_to_location(lat, lon)
    

        
    def _on_sample_line_clicked(self, sample_name):
        """Handle sample line click from group detail popup."""
        # Just highlight the sample normally in the sample list
        self.sample_list.highlight_sample(sample_name)
        self.statusBar().showMessage(f"Highlighted sample: {sample_name}", 3000)
        
    def _on_run_analysis(self, params):
        """Run analysis on all loaded data."""
        # Get all samples data
        all_data = self.map_sample_widget.get_all_samples_data()
        if not all_data:
            QMessageBox.warning(self, "No Sample Data", 
                              "Please load data first by generating the map.")
            return
        
        # Use sample data for demonstration
        self.current_analysis_data = {
            **params,
            'num_samples': len(all_data),
            'selected_samples': all_data,
            'k_values': SAMPLE_CH_RS_DATA['k_values'],
            'ch_values': SAMPLE_CH_RS_DATA['ch_values'],
            'rs_values': SAMPLE_CH_RS_DATA['rs_values'],
            'optimal_k': get_optimal_k()
        }
        
        self._plot_analysis_results()
        self.control_panel.enable_analysis_buttons(True)
        
        # Update preview cards status
        optimal_k = self.current_analysis_data['optimal_k']
        self.ch_preview_card.update_status(f"Analysis complete (k={optimal_k})")
        self.rs_preview_card.update_status(f"Analysis complete (k={optimal_k})")
        
        self.statusBar().showMessage("Analysis complete.", 3000)
        
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
        
        # Let user choose output file location
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Analysis Results", 
            "analysis_results.csv", 
            "CSV Files (*.csv)"
        )
        
        if not file_path:  # User cancelled
            return
        
        try:
            saved_path = export_analysis_results(
                file_path, 
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
        
        # Reset preview cards
        self.map_preview_card.update_status("Not loaded")
        self.ch_preview_card.update_status("Not loaded")
        self.rs_preview_card.update_status("Not loaded")
        
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = EntropyMaxFinal()
    window.show()
    sys.exit(app.exec())
