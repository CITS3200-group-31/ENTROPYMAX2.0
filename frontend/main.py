import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QFrame, QMessageBox, QMenu, QFileDialog)
from components.control_panel import ControlPanel
from components.group_detail_popup import GroupDetailPopup
from components.module_preview_card import ModulePreviewCard
from components.standalone_window import StandaloneWindow
from components.simple_map_sample_widget import SimpleMapSampleWidget
from components.chart_widget import ChartWidget
from components.settings_dialog import SettingsDialog
from help import FormatExamplesDialog


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
        self.selected_samples = []
        self.current_analysis_data = {}
        self.selected_k_for_details = None  # User-selected K value for group details
        self.group_detail_popup = GroupDetailPopup()
        
        # Initialize settings dialog
        self.settings_dialog = SettingsDialog(self)
        
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
        self.control_panel.runAnalysisRequested.connect(self._on_run_analysis)
        self.control_panel.showMapRequested.connect(self._on_show_map)
        self.control_panel.exportResultsRequested.connect(self._on_export_results)
        
        # Connect signals from map-sample widget
        self.map_sample_widget.selectionChanged.connect(self._on_selection_changed)
        self.map_sample_widget.sampleLocateRequested.connect(self._on_locate_sample)
        
        # Connect signal from group detail popup to sample list
        self.group_detail_popup.sampleLineClicked.connect(self._on_sample_line_clicked)
        
        # Connect K value selection signals from charts - auto show group details
        self.rs_chart.kValueSelected.connect(self._on_k_value_selected_and_show_details)
        self.ch_chart.kValueSelected.connect(self._on_k_value_selected_and_show_details)
        
    def _on_input_file_selected(self, file_path):
        self.input_file_path = file_path
        # Validate raw data CSV format
        from utils.csv_validator import validate_raw_data_csv
        
        valid, error_msg = validate_raw_data_csv(file_path)
        if valid:
            self.statusBar().showMessage("Raw data file loaded successfully.", 3000)
        else:
            QMessageBox.warning(self, "Invalid Raw Data File", 
                              f"File validation failed:\n{error_msg}")
            self.input_file_path = None
            self.control_panel.input_file = None
            self.control_panel.input_label.setText("No file selected")
            self.control_panel.input_label.setStyleSheet("color: gray; padding: 5px;")
            self.control_panel._update_button_states()
    
    def _on_gps_file_selected(self, file_path):
        self.gps_file_path = file_path
        # Validate GPS CSV format
        from utils.csv_validator import validate_gps_csv
        
        valid, error_msg = validate_gps_csv(file_path)
        if valid:
            self.statusBar().showMessage("GPS file loaded successfully.", 3000)
        else:
            QMessageBox.warning(self, "Invalid GPS File", 
                              f"File validation failed:\n{error_msg}")
            self.gps_file_path = None
            self.control_panel.gps_file = None
            self.control_panel.gps_label.setText("No GPS file selected")
            self.control_panel.gps_label.setStyleSheet("color: gray; padding: 5px;")
            self.control_panel._update_button_states()
        
    def _on_show_map(self):
        """Load map data from Parquet and display."""
        try:
            if not hasattr(self, 'current_analysis_data') or not self.current_analysis_data:
                QMessageBox.warning(self, "No Analysis Data", 
                                  "Please run analysis first.")
                return
            
            # Get optimal K GPS data from analysis
            optimal_k = self.current_analysis_data.get('optimal_k')
            if not optimal_k:
                raise Exception("No optimal K found in analysis data")
            
            gps_data = self.current_analysis_data['gps_data'][optimal_k]
            
            # Convert to markers format
            markers = []
            for sample_id, info in gps_data.items():
                markers.append({
                    'name': sample_id,
                    'lat': info['lat'],
                    'lon': info['lon'],
                    'group': info['group'],
                    'selected': False
                })
            
            # Load map with grouped data
            self.map_sample_widget.load_data(markers)
            
            # Update preview card - show sample count only
            self.map_preview_card.update_status(f"Loaded {len(markers)} samples")
            
            self.statusBar().showMessage(f"Map loaded with {len(markers)} samples (K={optimal_k})", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Error Loading Map", str(e))
            
    def _on_selection_changed(self, selected_samples):
        self.selected_samples = selected_samples
        
    def _on_locate_sample(self, name, lat, lon):
        self.map_widget.zoom_to_location(lat, lon)
    

        
    def _on_sample_line_clicked(self, sample_name):
        """Handle sample line click from group detail popup."""
        # Just highlight the sample normally in the sample list
        self.sample_list.highlight_sample(sample_name)
        self.statusBar().showMessage(f"Highlighted sample: {sample_name}", 3000)
    
    def _on_k_value_selected_and_show_details(self, k_value):
        """Handle K value selection from charts and automatically show group details."""
        self.selected_k_for_details = k_value
        optimal_k = self.current_analysis_data.get('optimal_k', None)
        
        # Update status bar
        if k_value == optimal_k:
            self.statusBar().showMessage(
                f"Selected K={k_value} (Optimal). Loading group details...", 
                3000
            )
        else:
            self.statusBar().showMessage(
                f"Selected K={k_value}. Loading group details...", 
                3000
            )
        
        # Automatically show group details for selected K
        self._on_show_group_details()
        
    def _update_map_groups(self, gps_data):
        """Update map markers with group assignments from analysis"""
        # Get current markers
        current_markers = self.map_sample_widget.get_all_samples_data()
        
        # Update group assignments based on analysis results
        updated_markers = []
        for marker in current_markers:
            sample_name = marker['name']
            if sample_name in gps_data:
                marker['group'] = gps_data[sample_name]['group']
            updated_markers.append(marker)
        
        # Reload map with updated groups
        self.map_sample_widget.load_data(updated_markers)
        
    def _on_run_analysis(self, params):
        """Run analysis using real CLI"""
        from PyQt6.QtWidgets import QProgressDialog
        from PyQt6.QtCore import Qt
        from utils.temp_manager import TempFileManager
        from utils.cli_integration import CLIIntegration
        from utils.data_pipeline import DataPipeline
        
        # Initialize managers
        self.temp_manager = TempFileManager()
        
        try:
            # Setup binary from bundle (always copy to ensure integrity)
            try:
                binary_path = self.temp_manager.setup_binary_from_bundle()
            except Exception as e:
                raise Exception(f"Failed to setup CLI binary: {e}")
            
            cli = CLIIntegration(cli_path=binary_path)
            pipeline = DataPipeline()
            
            # Show progress dialog
            progress = QProgressDialog("Running analysis...", None, 0, 5, self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.show()
            
            # Step 1: Setup binary
            progress.setLabelText("Preparing analysis environment...")
            progress.setValue(1)
            QApplication.processEvents()
            
            # Step 2: Run CLI
            progress.setLabelText("Running EntropyMax analysis...")
            progress.setValue(2)
            QApplication.processEvents()
            
            output_csv = str(self.temp_manager.get_path('cli_output'))
            success, message = cli.run_analysis(
                params['input_file'],
                params['gps_file'], 
                output_csv,
                params,
                working_dir=str(self.temp_manager.session_dir)
            )
            
            if not success:
                raise Exception(f"CLI failed: {message}")
                
            # Step 3: Convert to Parquet
            progress.setLabelText("Converting to Parquet format...")
            progress.setValue(3)
            QApplication.processEvents()
            
            parquet_path = str(self.temp_manager.get_path('parquet'))
            if not pipeline.csv_to_parquet(output_csv, parquet_path):
                raise Exception("Failed to convert CSV to Parquet")
                
            # Step 4: Extract data
            progress.setLabelText("Extracting analysis results...")
            progress.setValue(4)
            QApplication.processEvents()
            
            analysis_data = pipeline.extract_analysis_data(parquet_path)
            if not analysis_data:
                raise Exception("Failed to extract data from Parquet")
                
            # Step 5: Update UI
            progress.setLabelText("Updating visualizations...")
            progress.setValue(5)
            QApplication.processEvents()
            
            # Save analysis data
            optimal_k = analysis_data.get('optimal_k')
            self.current_analysis_data = {
                **params,
                **analysis_data,
                'parquet_path': parquet_path
            }
            
            # Plot results
            self._plot_analysis_results()
            
            # Update status (don't update map yet, wait for Step 4)
            self.ch_preview_card.update_status("Analysis complete")
            self.rs_preview_card.update_status("Analysis complete")
            self.map_preview_card.update_status("Ready - Click 'Show Map View' to display results")
            
            # Enable next step buttons
            self.control_panel.show_map_btn.setEnabled(True)
            self.control_panel.export_btn.setEnabled(True)
            
            progress.close()
            self.statusBar().showMessage(f"Analysis complete. Optimal K={optimal_k}. Click 'Show Map View' to see results.", 5000)
            
        except Exception as e:
            if 'progress' in locals():
                progress.close()
            QMessageBox.critical(self, "Analysis Error", str(e))
            self.statusBar().showMessage("Analysis failed.", 3000)
            # Cleanup on error
            if hasattr(self, 'temp_manager'):
                self.temp_manager.cleanup()
        
    def _on_show_group_details(self):
        """Show group detail popups with line charts for each group."""
        if not hasattr(self, 'current_analysis_data') or not self.current_analysis_data:
            QMessageBox.warning(self, "No Analysis Data", 
                              "Please run analysis first.")
            return
        
        try:
            from utils.data_pipeline import DataPipeline
            
            # Use user-selected K if available, otherwise use optimal K
            if self.selected_k_for_details is not None:
                k_value = self.selected_k_for_details
            else:
                k_value = self.current_analysis_data.get('optimal_k', 4)
            
            parquet_path = self.current_analysis_data.get('parquet_path')
            
            if not parquet_path:
                raise Exception("Parquet file path not found in analysis data")
            
            # Extract group details from Parquet
            pipeline = DataPipeline()
            group_details = pipeline.extract_group_details(parquet_path, k_value)
            
            if not group_details:
                raise Exception(f"No group data found for K={k_value}")
            
            # Show group detail popups with extracted data
            self.group_detail_popup.load_and_show_popups_from_data(
                group_details, k_value, x_unit='μm', y_unit='%'
            )
            
            optimal_k = self.current_analysis_data.get('optimal_k', None)
            if k_value == optimal_k:
                self.statusBar().showMessage(f"Showing details for K={k_value} groups (Optimal).", 3000)
            else:
                self.statusBar().showMessage(f"Showing details for K={k_value} groups.", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Error Showing Group Details", str(e))
    
    def _on_export_results(self):
        """Export analysis results CSV and cleanup temp files."""
        if not self.current_analysis_data:
            QMessageBox.warning(self, "No Results", 
                              "Please run an analysis first.")
            return
        
        if not hasattr(self, 'temp_manager'):
            QMessageBox.warning(self, "No Temp Files", 
                              "No temporary files found to export.")
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
            from pathlib import Path
            
            # Ensure .csv extension
            if not file_path.endswith('.csv'):
                file_path += '.csv'
            
            # Export the processed CSV from temp directory
            self.temp_manager.export_to('cli_output', Path(file_path))
            
            # Clean up temporary files after successful export
            self.temp_manager.cleanup()
            
            QMessageBox.information(self, "Export Successful", 
                                f"Results saved to:\n{file_path}\n\nTemporary files have been cleaned up.")
            
            self.statusBar().showMessage(f"Results exported to {Path(file_path).name}", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", 
                              f"Failed to export results:\n{str(e)}")
            
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
        # Clean up temp files if they exist
        if hasattr(self, 'temp_manager'):
            try:
                self.temp_manager.cleanup()
            except Exception as e:
                print(f"Warning: Failed to cleanup temp files: {e}")
        
        # Reset file paths
        self.input_file_path = None
        self.gps_file_path = None
        self.selected_samples = []
        self.selected_k_for_details = None
        
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
    
    def closeEvent(self, event):
        """Handle window close event and cleanup entire cache directory."""
        from utils.temp_manager import TempFileManager
        
        # Close all group detail popups before closing the main window
        self.group_detail_popup.close_all()
        
        # Clean up cache directory contents on app exit
        try:
            TempFileManager.cleanup_entire_cache()
            print("Cache directory contents cleaned up on exit")
        except Exception as e:
            print(f"Warning: Failed to cleanup cache directory on exit: {e}")
        
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = EntropyMaxFinal()
    window.show()
    sys.exit(app.exec())
