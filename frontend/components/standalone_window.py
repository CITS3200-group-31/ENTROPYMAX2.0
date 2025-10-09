"""
This refactor simplifies a previously complex, error-prone full-screen window implementation 
by introducing a new `StandaloneWindow` class to eliminate duplicated code and streamline state management.
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QToolBar
from PyQt6.QtCore import pyqtSignal as Signal, Qt
from PyQt6.QtGui import QAction
from .settings_dialog import SettingsDialog
from .visualization_settings import VisualizationSettings


class StandaloneWindow(QMainWindow):
    """Standalone window for module display"""
    
    closed = Signal()
    exportRequested = Signal()
    exportKMLRequested = Signal()  # New signal for KML export
    
    def __init__(self, title, widget, parent=None, enable_kml_export=False):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.content_widget = widget
        self.enable_kml_export = enable_kml_export
        
        # Set as independent window
        self.setWindowFlags(Qt.WindowType.Window)
        
        # Initialize settings dialog lazily to avoid early QObject init issues
        self.settings_dialog = None
        
        self._setup_ui()
        self._setup_toolbar()
        
    def _setup_ui(self):
        """Initialize UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(self.content_widget)
        
        # Default size
        self.resize(1200, 800)
        
    def _setup_toolbar(self):
        """Setup toolbar with export and settings functions"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # First, allow content widget to add its own actions (module-specific) on the left
        try:
            if hasattr(self.content_widget, 'augment_toolbar') and callable(self.content_widget.augment_toolbar):
                self.content_widget.augment_toolbar(toolbar)
                # Separator before standard actions
                toolbar.addSeparator()
        except Exception:
            # Do not break window if augmentation fails
            pass
        
        # Reset all visuals to defaults
        reset_action = QAction("Reset", self)
        reset_action.setToolTip("Reset all visuals to defaults")
        reset_action.triggered.connect(self._reset_all_visuals)
        toolbar.addAction(reset_action)
        
        # Visualization Settings action
        settings_action = QAction("Settings", self)
        settings_action.setToolTip("Adjust visualization settings for publication standards")
        settings_action.triggered.connect(self._show_settings)
        toolbar.addAction(settings_action)
        
        # Separator
        toolbar.addSeparator()
        
        # Export action
        export_action = QAction("Export as PNG", self)
        export_action.setToolTip("Export current view as PNG")
        export_action.triggered.connect(self.exportRequested.emit)
        toolbar.addAction(export_action)
        
        # KML Export action (only for map window)
        if self.enable_kml_export:
            export_kml_action = QAction("Export as KML", self)
            export_kml_action.setToolTip("Export map data as KML file for Google Earth")
            export_kml_action.triggered.connect(self.exportKMLRequested.emit)
            toolbar.addAction(export_kml_action)
    
    def _show_settings(self):
        """Show visualization settings dialog."""
        if self.settings_dialog is None:
            self.settings_dialog = SettingsDialog(self)
        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()
        
    def _reset_all_visuals(self):
        """Reset global visualization settings and let content reset its own view."""
        try:
            # Reset shared styling
            VisualizationSettings().reset_to_defaults()
        except Exception:
            pass
        
        # Let content widget reset its own state (scale/chart type/view)
        try:
            if hasattr(self.content_widget, 'reset_to_defaults') and callable(self.content_widget.reset_to_defaults):
                self.content_widget.reset_to_defaults()
        except Exception:
            pass
        
    def closeEvent(self, event):
        """Handle window close"""
        self.closed.emit()
        super().closeEvent(event)