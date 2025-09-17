import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QFrame, QMessageBox, QLabel)

# Import components and utils
from components.control_panel import ControlPanel
from components.map_widget import MapWidget
from components.chart_widget import ChartWidget
from components.sample_list_widget import SampleListWidget
from components.group_detail_popup import GroupDetailPopup
from utils.csv_export import export_analysis_results

# Import sample GPS CH, RS AND K mock data
from sample_data import EXTENDED_GPS_DATA, SAMPLE_CH_RS_DATA, get_optimal_k


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
        self.output_file_path = None
        self.selected_samples = []
        self.current_analysis_data = {}
        self.group_detail_popup = GroupDetailPopup()
        
        self._setup_ui()
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
        
        # Top right: Map and sample list (fixed layout)
        top_container = QWidget()
        top_layout = QHBoxLayout(top_container)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(15)
        
        # Map widget
        map_box = BentoBox(title="Map View")
        map_layout = QVBoxLayout(map_box)
        map_layout.setContentsMargins(10, 10, 10, 10)
        
        self.map_widget = MapWidget()
        map_layout.addWidget(self.map_widget)
        top_layout.addWidget(map_box, 3)  # 3:2 ratio for map:sample list
        
        # Sample list widget
        sample_box = BentoBox(title="Sample Selection")
        sample_layout = QVBoxLayout(sample_box)
        sample_layout.setContentsMargins(5, 5, 5, 5)
        self.sample_list = SampleListWidget()
        sample_layout.addWidget(self.sample_list)
        top_layout.addWidget(sample_box, 2)  # 3:2 ratio for map:sample list
        
        # Add top container to right layout with stretch factor
        right_layout.addWidget(top_container, 5)  # 5:4 ratio for top:bottom
        
        # Bottom right: Charts (fixed layout)
        bottom_container = QWidget()
        bottom_layout = QHBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(15)
        
        # CH Chart
        ch_box = BentoBox(title="CH Analysis")
        ch_layout = QVBoxLayout(ch_box)
        ch_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add title for CH chart
        ch_title = QLabel("Calinski-Harabasz Index")
        ch_title.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: 600;
                color: #333;
                padding: 5px 0;
            }
        """)
        ch_layout.addWidget(ch_title)
        
        self.ch_chart = ChartWidget(title="CH Index", ylabel="CH Index")
        ch_layout.addWidget(self.ch_chart)
        bottom_layout.addWidget(ch_box)
        
        # Rs Chart
        rs_box = BentoBox(title="Rs Analysis")
        rs_layout = QVBoxLayout(rs_box)
        rs_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add title for Rs chart
        rs_title = QLabel("Rs Percentage")
        rs_title.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: 600;
                color: #333;
                padding: 5px 0;
            }
        """)
        rs_layout.addWidget(rs_title)
        
        self.rs_chart = ChartWidget(title="Rs %", ylabel="Rs %")
        rs_layout.addWidget(self.rs_chart)
        bottom_layout.addWidget(rs_box)

        
        
        # Add bottom container to right layout with stretch factor
        right_layout.addWidget(bottom_container, 4)  # 5:4 ratio for top:bottom
        
        main_layout.addWidget(right_container)
        
    def _connect_signals(self):
        """Connect all signals to their handlers."""
        self.control_panel.inputFileSelected.connect(self._on_input_file_selected)
        self.control_panel.outputFileSelected.connect(self._on_output_file_selected)
        self.control_panel.generateMapRequested.connect(self._on_generate_map)
        self.control_panel.runAnalysisRequested.connect(self._on_run_analysis)
        self.control_panel.showGroupDetailsRequested.connect(self._on_show_group_details)
        self.control_panel.exportResultsRequested.connect(self._on_export_results)
        
        self.sample_list.selectionChanged.connect(self._on_selection_changed)
        self.sample_list.sampleLocateRequested.connect(self._on_locate_sample)
        
    def _on_input_file_selected(self, file_path):
        self.input_file_path = file_path
        
    def _on_output_file_selected(self, file_path):
        self.output_file_path = file_path
        
    def _on_generate_map(self):
        """Load data from CSV and render map."""
        try:
            # TODO: Replace with actual CSV parsing from backend API
            # Backend should return structured data with lat, lon, name, group
            markers = self._parse_marker_csv(self.input_file_path)
            self.sample_list.load_samples(markers)
            self.map_widget.render_map(markers)
            self.statusBar().showMessage("Map and sample list loaded.", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error Loading File", str(e))
            self._reset_workflow()
            
    def _on_selection_changed(self, selected_samples):
        self.selected_samples = selected_samples
        self.map_widget.update_selected_markers(selected_samples)
        self.control_panel.run_analysis_btn.setEnabled(len(selected_samples) > 0)
        
    def _on_locate_sample(self, name, lat, lon):
        self.map_widget.zoom_to_location(lat, lon)
        
    def _on_run_analysis(self, params):
        """Run analysis on selected data."""
        selected_data = self.sample_list.get_selected_samples_data()
        if not selected_data:
            QMessageBox.warning(self, "No Samples Selected", 
                              "Please select samples from the list.")
            return
        
        # TODO: Import Parquet data
        # It should contains:
        # - k_values array
        # - ch_values array (Calinski-Harabasz index values)
        # - rs_values array (Rs percentage values)
        # - optimal_k value
        
        # For now, use sample data for demonstration
        self.current_analysis_data = {
            **params,
            'num_samples': len(selected_data),
            'selected_samples': selected_data,
            'k_values': SAMPLE_CH_RS_DATA['k_values'],
            'ch_values': SAMPLE_CH_RS_DATA['ch_values'],
            'rs_values': SAMPLE_CH_RS_DATA['rs_values'],
            'optimal_k': get_optimal_k()
        }
        
        self._plot_analysis_results()
        self.control_panel.enable_analysis_buttons(True)
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
        self.control_panel.reset_workflow()
        self.map_widget.render_map([])
        self.sample_list.load_samples([])
        self.ch_chart.clear()
        self.rs_chart.clear()
        self.group_detail_popup.close_all()
        self.current_analysis_data = {}
        self.statusBar().showMessage("Workflow reset. Select an input file to begin.", 5000)
        
    def _parse_marker_csv(self, path):
        """Parse the input CSV file for map markers."""
        # TODO: Implement actual data parsing by using Jeremy's function, read from the Parquet file.
        # Expected CSV format:
        # - lat: latitude column
        # - lon: longitude column  
        # - name: sample identifier
        # - group: optional grouping category
        # Backend API should handle CSV parsing and return structured data and stored it in Parquet format.
        # For now, return sample data for testing
        return EXTENDED_GPS_DATA


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = EntropyMaxFinal()
    window.show()
    sys.exit(app.exec())
