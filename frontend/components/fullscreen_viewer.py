"""
Fullscreen viewer component for displaying widgets in fullscreen mode.
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QSizePolicy, QToolBar)
from PyQt6.QtCore import Qt, pyqtSignal as Signal
from PyQt6.QtGui import QAction, QKeySequence


class FullscreenViewer(QMainWindow):
    """A fullscreen viewer window that can display any widget in fullscreen mode."""
    
    closed = Signal()  # Emitted when the viewer is closed
    
    def __init__(self, widget_creator=None, title="", parent=None):
        super().__init__(parent)
        self.widget_creator = widget_creator  # A callable that creates the widget
        self.display_widget = None
        
        # No window title for cleaner look
        self.setWindowTitle("")
        # Set background color to match main window
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
        """)
        
        self._setup_ui()
        self._setup_shortcuts()
        
        # Create and add the widget
        if self.widget_creator:
            self.display_widget = self.widget_creator()
            if self.display_widget:
                self.container_layout.addWidget(self.display_widget)
        
    def _setup_ui(self):
        """Initialize the UI components."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout - no toolbar, just the widget
        self.container_layout = QVBoxLayout(central_widget)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(0)
        
        
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # ESC key to close window
        esc_action = QAction(self)
        esc_action.setShortcut(Qt.Key.Key_Escape)
        esc_action.triggered.connect(self.close)
        self.addAction(esc_action)
        
        # F11 to toggle fullscreen
        f11_action = QAction(self)
        f11_action.setShortcut(Qt.Key.Key_F11)
        f11_action.triggered.connect(self.toggle_fullscreen)
        self.addAction(f11_action)
        
    def toggle_fullscreen(self):
        """Toggle between fullscreen and normal window mode."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
            
        
    def closeEvent(self, event):
        """Handle close event."""
        self.closed.emit()
        super().closeEvent(event)