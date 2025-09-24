"""
This refactor simplifies a previously complex, error-prone full-screen window implementation 
by introducing a new `StandaloneWindow` class to eliminate duplicated code and streamline state management.
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QToolBar
from PyQt6.QtCore import pyqtSignal as Signal, Qt
from PyQt6.QtGui import QAction


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
        """Setup toolbar with export function"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Export action
        export_action = QAction("Export as PNG", self)
        export_action.setToolTip("Export current view as PNG")
        export_action.triggered.connect(self.exportRequested.emit)
        toolbar.addAction(export_action)
        
    def closeEvent(self, event):
        """Handle window close"""
        self.closed.emit()
        super().closeEvent(event)