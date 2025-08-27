"""
Sample list widget with checkboxes for selection and map navigation.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, 
                             QTreeWidgetItem, QPushButton, QLabel, QCheckBox,
                             QGroupBox, QHeaderView)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QBrush


class SampleListWidget(QWidget):
    """Widget for displaying and selecting samples with checkboxes."""
    
    # Signals
    selectionChanged = pyqtSignal(list)  # List of selected sample names
    sampleLocateRequested = pyqtSignal(str, float, float)  # name, lat, lon for map centering
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.samples_data = []
        self.selected_samples = []
        self._setup_ui()
        self._apply_styles()
        
    def _setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title label
        title_label = QLabel("Sample Data")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                padding: 5px 0;
            }
        """)
        layout.addWidget(title_label)
        
        # Create tree widget for sample list
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(['✓', 'Sample Name', 'Group', 'Lat', 'Lon'])
        
        # Set column widths
        self.tree_widget.setColumnWidth(0, 40)  # Checkbox column
        self.tree_widget.setColumnWidth(1, 180)  # Name column
        self.tree_widget.setColumnWidth(2, 60)   # Group column
        self.tree_widget.setColumnWidth(3, 85)   # Lat column
        self.tree_widget.setColumnWidth(4, 85)   # Lon column
        
        # Enable sorting
        self.tree_widget.setSortingEnabled(True)
        self.tree_widget.setAlternatingRowColors(True)
        
        # Connect item click signal
        self.tree_widget.itemClicked.connect(self._on_item_clicked)
        self.tree_widget.itemChanged.connect(self._on_item_changed)
        
        layout.addWidget(self.tree_widget)
        
        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.setFixedHeight(32)
        self.select_all_btn.clicked.connect(self._select_all)
        
        self.clear_all_btn = QPushButton("Clear All")
        self.clear_all_btn.setFixedHeight(32)
        self.clear_all_btn.clicked.connect(self._clear_all)
        
        button_layout.addWidget(self.select_all_btn)
        button_layout.addWidget(self.clear_all_btn)
        layout.addLayout(button_layout)
        
        # Selection count label
        self.count_label = QLabel("Selected: 0 samples")
        self.count_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 13px;
                padding: 5px;
                background-color: #f5f5f5;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.count_label)
        
    def load_samples(self, samples_data):
        """
        Load samples into the list.
        
        Args:
            samples_data: List of dictionaries with 'name', 'lat', 'lon', 'group' keys
        """
        self.samples_data = samples_data
        self.tree_widget.clear()
        
        for sample in samples_data:
            item = QTreeWidgetItem()
            
            # Add checkbox in first column
            item.setCheckState(0, Qt.CheckState.Unchecked)
            
            # Sample name
            item.setText(1, sample.get('name', 'Unknown'))
            
            # Group
            group = sample.get('group', 0)
            item.setText(2, str(group))
            
            # Coordinates
            item.setText(3, f"{sample.get('lat', 0):.4f}")
            item.setText(4, f"{sample.get('lon', 0):.4f}")
            
            # Store full sample data in item
            item.setData(1, Qt.ItemDataRole.UserRole, sample)
            
            self.tree_widget.addTopLevelItem(item)
        
        # Resize columns to content
        for i in range(5):
            self.tree_widget.resizeColumnToContents(i)
            
    def _on_item_clicked(self, item, column):
        """Handle item click - navigate to location on map if not checkbox."""
        if column != 0:  # Not checkbox column
            sample_data = item.data(1, Qt.ItemDataRole.UserRole)
            if sample_data:
                self.sampleLocateRequested.emit(
                    sample_data['name'],
                    sample_data['lat'],
                    sample_data['lon']
                )
                
    def _on_item_changed(self, item, column):
        """Handle checkbox state change."""
        if column == 0:  # Checkbox column
            self._update_selection()
            
    def _update_selection(self):
        """Update the list of selected samples."""
        self.selected_samples = []
        
        for i in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(i)
            if item.checkState(0) == Qt.CheckState.Checked:
                sample_data = item.data(1, Qt.ItemDataRole.UserRole)
                if sample_data:
                    self.selected_samples.append(sample_data['name'])
        
        self.count_label.setText(f"Selected: {len(self.selected_samples)} samples")
        self.selectionChanged.emit(self.selected_samples)
        
    def _select_all(self):
        """Select all samples."""
        for i in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(i)
            item.setCheckState(0, Qt.CheckState.Checked)
        self._update_selection()
        
    def _clear_all(self):
        """Clear all selections."""
        for i in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(i)
            item.setCheckState(0, Qt.CheckState.Unchecked)
        self._update_selection()
        
    def get_selected_samples(self):
        """Return list of selected sample names."""
        return self.selected_samples
    
    def get_selected_samples_data(self):
        """Return full data for selected samples."""
        selected_data = []
        for i in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(i)
            if item.checkState(0) == Qt.CheckState.Checked:
                sample_data = item.data(1, Qt.ItemDataRole.UserRole)
                if sample_data:
                    selected_data.append(sample_data)
        return selected_data
    
    def set_selection(self, sample_names):
        """Set selection to specific samples."""
        for i in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(i)
            sample_data = item.data(1, Qt.ItemDataRole.UserRole)
            if sample_data and sample_data['name'] in sample_names:
                item.setCheckState(0, Qt.CheckState.Checked)
            else:
                item.setCheckState(0, Qt.CheckState.Unchecked)
        self._update_selection()
    
    def highlight_sample(self, sample_name):
        """Highlight a specific sample in the list."""
        for i in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(i)
            sample_data = item.data(1, Qt.ItemDataRole.UserRole)
            if sample_data and sample_data['name'] == sample_name:
                self.tree_widget.setCurrentItem(item)
                self.tree_widget.scrollToItem(item)
                break
    
    def _apply_styles(self):
        """Apply modern styling to the widget."""
        self.tree_widget.setStyleSheet("""
            QTreeWidget {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                font-size: 13px;
                outline: none;
                color: #000000;
            }
            QTreeWidget::item {
                padding: 4px;
                border-bottom: 1px solid #f5f5f5;
                color: #000000;
            }
            QTreeWidget::item:hover {
                background-color: #f8f9fa;
            }
            QTreeWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #333;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #d0d0d0;
                border-right: 1px solid #e8e8e8;
                font-weight: 600;
                font-size: 13px;
            }
            QHeaderView::section:last {
                border-right: none;
            }
            QTreeWidget::item:alternate {
                background-color: #fafafa;
            }
            QTreeWidget::indicator {
                width: 16px;
                height: 16px;
            }
            QTreeWidget::indicator:unchecked {
                border: 2px solid #d0d0d0;
                background-color: white;
                border-radius: 3px;
            }
            QTreeWidget::indicator:checked {
                border: 2px solid #009688;
                background-color: #009688;
                border-radius: 3px;
                image: url(check.png);
            }
            QTreeWidget::indicator:unchecked:hover {
                border: 2px solid #4db6ac;
                background-color: #e0f2f1;
            }
        """)
        
        self.select_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #333;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 6px 15px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
                border-color: #2196F3;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
        """)
        
        self.clear_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #333;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 6px 15px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
                border-color: #f44336;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
        """)
