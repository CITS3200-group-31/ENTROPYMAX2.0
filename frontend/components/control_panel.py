"""
Control panel component for EntropyMax frontend.
Handles input/output selection and processing options.
"""

from PyQt6.QtWidgets import (QWidget, QGroupBox, QVBoxLayout, QHBoxLayout,
                             QPushButton, QRadioButton, QCheckBox, QSpinBox,
                             QLabel, QGridLayout, QFileDialog, QMessageBox)
from PyQt6.QtCore import pyqtSignal


class ControlPanel(QWidget):
    """Control panel with input/output and processing options."""
    
    # Signals
    inputFileSelected = pyqtSignal(str)  # Path to selected file
    outputFileSelected = pyqtSignal(str)  # Path to output file
    loadTestDataRequested = pyqtSignal()
    runAnalysisRequested = pyqtSignal(dict)  # Analysis parameters
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        """Initialize the UI components."""
        layout = QGridLayout(self)
        
        # Input Group
        input_group = self._create_input_group()
        layout.addWidget(input_group, 0, 0)
        
        # Output Group
        output_group = self._create_output_group()
        layout.addWidget(output_group, 0, 1)
        
        # Processing Options Group
        processing_group = self._create_processing_group()
        layout.addWidget(processing_group, 0, 2, 1, 2)
        
    def _create_input_group(self):
        """Create input selection group."""
        group = QGroupBox("Input")
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        # Select input file button
        select_input_btn = QPushButton("Select Input File")
        select_input_btn.clicked.connect(self._on_select_input)
        layout.addWidget(select_input_btn)
        
        # Load test data button
        load_test_btn = QPushButton("Load Test Data")
        load_test_btn.clicked.connect(lambda: self.loadTestDataRequested.emit())
        layout.addWidget(load_test_btn)
        
        return group
    
    def _create_output_group(self):
        """Create output options group."""
        group = QGroupBox("Output")
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        # Output file button
        output_btn = QPushButton("Define Output Filename")
        output_btn.clicked.connect(self._on_select_output)
        layout.addWidget(output_btn)
        
        # Output format options
        options_layout = QHBoxLayout()
        self.composite_radio = QRadioButton("Composite")
        self.composite_radio.setChecked(True)
        self.individual_radio = QRadioButton("Individual")
        self.both_radio = QRadioButton("Both")
        
        options_layout.addWidget(self.composite_radio)
        options_layout.addWidget(self.individual_radio)
        options_layout.addWidget(self.both_radio)
        layout.addLayout(options_layout)
        
        return group
    
    def _create_processing_group(self):
        """Create processing options group."""
        group = QGroupBox("Processing Options")
        layout = QGridLayout()
        group.setLayout(layout)
        
        # Checkboxes
        self.perm_check = QCheckBox("Do Permutations")
        self.perm_check.setChecked(True)
        self.prop_check = QCheckBox("Take row proportions")
        
        # Group range controls
        group_label = QLabel("Groups Range:")
        self.min_groups_spin = QSpinBox()
        self.min_groups_spin.setRange(2, 84)
        self.min_groups_spin.setValue(2)
        self.min_groups_spin.setPrefix("Min: ")
        
        self.max_groups_spin = QSpinBox()
        self.max_groups_spin.setRange(2, 84)
        self.max_groups_spin.setValue(20)
        self.max_groups_spin.setPrefix("Max: ")
        
        # Ensure min <= max
        self.min_groups_spin.valueChanged.connect(self._validate_group_range)
        self.max_groups_spin.valueChanged.connect(self._validate_group_range)
        
        # Layout
        layout.addWidget(self.perm_check, 0, 0)
        layout.addWidget(self.prop_check, 0, 1)
        layout.addWidget(group_label, 1, 0)
        layout.addWidget(self.min_groups_spin, 1, 1)
        layout.addWidget(self.max_groups_spin, 1, 2)
        
        return group
    
    def _validate_group_range(self):
        """Ensure min_groups <= max_groups."""
        if self.min_groups_spin.value() > self.max_groups_spin.value():
            self.max_groups_spin.setValue(self.min_groups_spin.value())
    
    def _on_select_input(self):
        """Handle input file selection."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Input File", 
            "", 
            "CSV Files (*.csv)"
        )
        if file_path:
            self.inputFileSelected.emit(file_path)
    
    def _on_select_output(self):
        """Handle output file selection."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Define Output Filename", 
            "", 
            "CSV Files (*.csv)"
        )
        if file_path:
            self.outputFileSelected.emit(file_path)
    
    def get_analysis_parameters(self):
        """Get current analysis parameters."""
        return {
            'min_groups': self.min_groups_spin.value(),
            'max_groups': self.max_groups_spin.value(),
            'do_permutations': self.perm_check.isChecked(),
            'take_proportions': self.prop_check.isChecked(),
            'output_format': self._get_output_format()
        }
    
    def _get_output_format(self):
        """Get selected output format."""
        if self.composite_radio.isChecked():
            return 'composite'
        elif self.individual_radio.isChecked():
            return 'individual'
        else:
            return 'both'
