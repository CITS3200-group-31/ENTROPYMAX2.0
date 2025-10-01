"""
Help - CSV Format Examples
Shows format examples for GPS and Grain Size CSV files.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QTextEdit)
from PyQt6.QtCore import Qt


class FormatExamplesDialog(QDialog):
    """Dialog showing CSV format examples."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CSV Format Examples")
        self.setModal(True)
        self.setFixedSize(800, 650)
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
        """)
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # GPS Format Section
        gps_label = QLabel("GPS File Format:")
        gps_label.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color: #009688;
            margin-top: 5px;
            margin-bottom: 5px;
        """)
        layout.addWidget(gps_label)
        
        gps_text = QTextEdit()
        gps_text.setReadOnly(True)
        gps_text.setPlainText(
"""Sample Name,Latitude,Longitude
Sample_A,52.3111,1.7110
Sample_B,52.2900,1.7204
Sample_C,52.2910,1.7103
Sample_D,-31.9523,115.8613
Sample_E,-33.8610,121.8891

Notes:
• First column: Sample identification (must match grain size data)
• Latitude: Valid range -90 to 90 degrees
• Longitude: Valid range -180 to 180 degrees
• Column names can also be 'Sample' instead of 'Sample Name'"""
        )
        gps_text.setFixedHeight(220)  # Fixed height to show all content
        gps_text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        gps_text.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        gps_text.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 12px;
                font-family: 'Courier New', monospace;
                font-size: 13px;
                color: #2c3e50;
                line-height: 1.5;
            }
        """)
        layout.addWidget(gps_text)
        
        # Grain Size Format Section
        grain_label = QLabel("Grain Size File Format:")
        grain_label.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color: #009688;
            margin-top: 15px;
            margin-bottom: 5px;
        """)
        layout.addWidget(grain_label)
        
        grain_text = QTextEdit()
        grain_text.setReadOnly(True)
        grain_text.setPlainText(
"""Sample_Name,0.02,0.024,0.028,0.033,0.038,0.045,0.053,0.062,0.073,0.086,...
Sample_A,0.0,0.1,0.3,0.5,0.8,1.2,1.8,2.4,3.1,3.8,...
Sample_B,0.0,0.2,0.4,0.7,1.0,1.5,2.1,2.8,3.5,4.2,...
Sample_C,0.0,0.1,0.2,0.4,0.6,0.9,1.3,1.7,2.2,2.8,...
Sample_D,0.0,0.3,0.6,0.9,1.3,1.8,2.4,3.1,3.8,4.6,...
Sample_E,0.0,0.2,0.5,0.8,1.2,1.6,2.2,2.8,3.5,4.3,...

Notes:
• First column: Sample name (must match GPS data)
• Header row: Grain sizes in micrometers (μm)
• Data values: Percentage for each grain size
• Range: 0-2000 μm (adjustable)"""
        )
        grain_text.setFixedHeight(220)  # Fixed height to show all content
        grain_text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        grain_text.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        grain_text.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 12px;
                font-family: 'Courier New', monospace;
                font-size: 13px;
                color: #2c3e50;
                line-height: 1.5;
            }
        """)
        layout.addWidget(grain_text)
        
        # Add stretch to push content to top
        layout.addStretch()