"""
Module preview card component for main window
"""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal as Signal


class ModulePreviewCard(QFrame):
    """Preview card for each module"""
    
    openRequested = Signal()
    
    def __init__(self, title, description="", parent=None):
        super().__init__(parent)
        self.title = title
        self.description = description
        self.status_text = "Not loaded"
        self._setup_ui()
        
    def _setup_ui(self):
        self.setStyleSheet("""
            ModulePreviewCard {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #333;
        """)
        layout.addWidget(title_label)
        
        # Description
        if self.description:
            desc_label = QLabel(self.description)
            desc_label.setStyleSheet("color: #666; font-size: 12px;")
            layout.addWidget(desc_label)
        
        # Status
        self.status_label = QLabel(self.status_text)
        self.status_label.setStyleSheet("color: #999; font-size: 11px;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # Open button
        self.open_btn = QPushButton("Open Window")
        self.open_btn.setStyleSheet("""
            QPushButton {
                background-color: #009688;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00796b;
            }
            QPushButton:pressed {
                background-color: #004d40;
            }
        """)
        self.open_btn.clicked.connect(self.openRequested.emit)
        layout.addWidget(self.open_btn)
        
    def update_status(self, status_text):
        """Update status display"""
        self.status_text = status_text
        self.status_label.setText(status_text)
        
    def set_enabled(self, enabled):
        """Enable or disable the open button"""
        self.open_btn.setEnabled(enabled)
        if not enabled:
            self.open_btn.setStyleSheet("""
                QPushButton {
                    background-color: #cccccc;
                    color: white;
                    border: none;
                    padding: 8px 15px;
                    border-radius: 4px;
                    font-weight: bold;
                }
            """)
        else:
            self.open_btn.setStyleSheet("""
                QPushButton {
                    background-color: #009688;
                    color: white;
                    border: none;
                    padding: 8px 15px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #00796b;
                }
                QPushButton:pressed {
                    background-color: #004d40;
                }
            """)