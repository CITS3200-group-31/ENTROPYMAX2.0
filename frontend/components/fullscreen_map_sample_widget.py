"""
Fullscreen-capable map and sample list combined widget with bidirectional selection.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QFrame, QLabel, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal as Signal
from .interactive_map_widget import InteractiveMapWidget
from .sample_list_widget import SampleListWidget
from .fullscreen_viewer import FullscreenViewer


class FullscreenMapSampleWidget(QWidget):
    """Combined map and sample list widget with fullscreen capability."""
    
    # Forward signals from child widgets
    selectionChanged = Signal(list)
    sampleLocateRequested = Signal(str, float, float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fullscreen_viewer = None
        self.markers_data = []
        self.selected_samples = []
        
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Header with only fullscreen button (no title)
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        header_frame.setFixedHeight(40)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(5, 5, 5, 0)
        
        header_layout.addStretch()
        
        # Fullscreen button - no background, just icon
        self.fullscreen_btn = QPushButton("⛶")
        self.fullscreen_btn.setToolTip("Fullscreen")
        self.fullscreen_btn.setFixedSize(25, 25)
        self.fullscreen_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #009688;
                border: none;
                font-size: 18px;
                padding: 0;
                text-align: center;
            }
            QPushButton:hover {
                color: #00796b;
            }
            QPushButton:pressed {
                color: #004d40;
            }
        """)
        self.fullscreen_btn.clicked.connect(self.open_fullscreen)
        header_layout.addWidget(self.fullscreen_btn)
        
        layout.addWidget(header_frame)
        
        # Create splitter for map and sample list
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Create interactive map widget with selection capabilities
        self.map_widget = InteractiveMapWidget()
        self.splitter.addWidget(self.map_widget)
        
        # Create sample list widget
        self.sample_list = SampleListWidget()
        self.splitter.addWidget(self.sample_list)
        
        # Set initial sizes (3:2 ratio)
        self.splitter.setSizes([600, 400])
        
        layout.addWidget(self.splitter)
        
    def _connect_signals(self):
        """Connect internal signals for bidirectional synchronization."""
        # Bidirectional selection synchronization
        self.map_widget.selectionChanged.connect(self._on_map_selection_changed)
        self.sample_list.selectionChanged.connect(self._on_list_selection_changed)
        
        # Location requests from sample list
        self.sample_list.sampleLocateRequested.connect(self._on_sample_locate_requested)
        
    def _on_map_selection_changed(self, selected_samples):
        """Handle selection change from map."""
        # Avoid circular updates
        if selected_samples != self.selected_samples:
            self.selected_samples = selected_samples
            # Update sample list to match map selection
            self.sample_list.set_selection(selected_samples)
            # Emit to parent
            self.selectionChanged.emit(selected_samples)
    
    def _on_list_selection_changed(self, selected_samples):
        """Handle selection change from sample list."""
        # Avoid circular updates
        if selected_samples != self.selected_samples:
            self.selected_samples = selected_samples
            # Update map to match list selection
            self.map_widget.set_selection(selected_samples)
            # Emit to parent
            self.selectionChanged.emit(selected_samples)
        
    def _on_sample_locate_requested(self, name, lat, lon):
        """Handle sample locate request."""
        self.map_widget.zoom_to_location(lat, lon)
        self.sampleLocateRequested.emit(name, lat, lon)
        
    def load_data(self, markers_data):
        """
        Load data into both map and sample list.
        
        Args:
            markers_data: List of dictionaries with 'lat', 'lon', 'name', 'group' keys
        """
        self.markers_data = markers_data
        self.map_widget.render_map(markers_data)
        self.sample_list.load_samples(markers_data)
        
    def get_selected_samples_data(self):
        """Get data for selected samples."""
        return self.sample_list.get_selected_samples_data()
    
    def clear_selection(self):
        """Clear all selections in both map and list."""
        self.selected_samples = []
        self.map_widget.clear_selection()
        self.sample_list.clear_all()
        
    def _create_fullscreen_widget(self):
        """Create a new combined widget for fullscreen display."""
        # Create container widget
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create splitter for fullscreen view
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Create new interactive map widget
        fullscreen_map = InteractiveMapWidget()
        fullscreen_map.render_map(self.markers_data)
        fullscreen_map.set_selection(self.selected_samples)
        
        # Create new sample list widget
        fullscreen_sample_list = SampleListWidget()
        fullscreen_sample_list.load_samples(self.markers_data)
        fullscreen_sample_list.set_selection(self.selected_samples)
        
        # Connect bidirectional selection in fullscreen
        fullscreen_map.selectionChanged.connect(
            lambda samples: fullscreen_sample_list.set_selection(samples)
        )
        fullscreen_sample_list.selectionChanged.connect(
            lambda samples: fullscreen_map.set_selection(samples)
        )
        fullscreen_sample_list.sampleLocateRequested.connect(
            lambda name, lat, lon: fullscreen_map.zoom_to_location(lat, lon)
        )
        
        # Add to splitter
        splitter.addWidget(fullscreen_map)
        splitter.addWidget(fullscreen_sample_list)
        
        # Set sizes (60:40 ratio for better fullscreen view)
        splitter.setSizes([960, 640])
        
        layout.addWidget(splitter)
        
        return container
        
    def open_fullscreen(self):
        """Open the map and sample list in a fullscreen viewer."""
        if self.fullscreen_viewer and self.fullscreen_viewer.isVisible():
            self.fullscreen_viewer.raise_()
            self.fullscreen_viewer.activateWindow()
            return
            
        self.fullscreen_viewer = FullscreenViewer(
            widget_creator=self._create_fullscreen_widget
        )
        
        self.fullscreen_viewer.closed.connect(self._on_fullscreen_closed)
        self.fullscreen_viewer.show()
        
    def _on_fullscreen_closed(self):
        """Handle fullscreen viewer close."""
        self.fullscreen_viewer = None