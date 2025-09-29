"""
This refactor simplifies a previously complex, error-prone full-screen window implementation 
by introducing a new `StandaloneWindow` class to eliminate duplicated code and streamline state management.
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QToolBar
from PyQt6.QtCore import pyqtSignal as Signal, Qt
from PyQt6.QtGui import QAction
from .settings_dialog import SettingsDialog


class StandaloneWindow(QMainWindow):
    """Standalone window for module display"""
    
    closed = Signal()
    exportRequested = Signal()
    
    def __init__(self, title, widget, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.content_widget = widget
        
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
    
    def _show_settings(self):
        """Show visualization settings dialog."""
        if self.settings_dialog is None:
            self.settings_dialog = SettingsDialog(self)
        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()
        
    def closeEvent(self, event):
        """Handle window close"""
        self.closed.emit()
        super().closeEvent(event)