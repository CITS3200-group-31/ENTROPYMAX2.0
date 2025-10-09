"""
Validation Quick Rules dialog.
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit
from PyQt6.QtCore import Qt


class ValidationRulesDialog(QDialog):
    """Dialog showing concise validation rules for CSV inputs."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Validation Quick Rules")
        self.setModal(True)
        self.setFixedSize(800, 500)
        self.setStyleSheet("""
            QDialog { background-color: #f8f9fa; }
        """)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Validation quick rules:")
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color: #009688;
            margin-top: 5px;
            margin-bottom: 5px;
        """)
        layout.addWidget(title)

        rules_text = QTextEdit()
        rules_text.setReadOnly(True)
        rules_text.setPlainText(
"""Headers (case-sensitive):
• Raw: first column must be exactly 'Sample Name'
• GPS: header must be exactly 'Sample Name, Latitude, Longitude' (in order)

Sample names:
• Allowed to repeat; must not be empty
• Case-sensitive across files (Raw and GPS must match exactly)

Grain-size columns (Raw):
• All headers after 'Sample Name' must be numeric (floats)
• Order is not enforced

Data cells:
• Raw: all grain-size values must be numeric and non-missing
• GPS: Latitude/Longitude must be numeric; Latitude in [-90, 90], Longitude in [-180, 180]

Column counts:
• GPS: exactly 3 columns after removing blank/Unnamed ones
• Raw: at least 2 columns ('Sample Name' + one grain-size bin)

Notes:
• Trailing blank/Unnamed columns (e.g., from extra commas) are ignored, remaining columns must still satisfy rules
• Raw values can be raw counts/intensity; app converts rows to Frequency (%) during analysis"""
        )
        rules_text.setFixedHeight(360)
        rules_text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        rules_text.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        rules_text.setStyleSheet("""
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
        layout.addWidget(rules_text)

        layout.addStretch()
