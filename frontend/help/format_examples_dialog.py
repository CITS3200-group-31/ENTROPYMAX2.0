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
A11642G_Q,52.3111833333,1.7110000000
A20858G_Q,52.2900166667,1.7203833333
A21107G_Q,52.2910000000,1.7103166667
A21134G_Q,52.2642000000,1.7050666667

Notes:
• First column: Sample Name (must exactly match the grain-size CSV)
• Latitude: -90 to 90
• Longitude: -180 to 180"""
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
"""Sample Name,0.02,0.023520823,0.027661457,0.032531013,0.038257812,0.044992763,0.052913343,0.062228271,0.07318301,0.086066235,0.101217438,0.119035877,0.139991095,0.164635295,0.193617889,0.227702614,0.267787655,0.314929314,0.370369847,0.435570198,0.512248497,0.602425336,0.708477013,0.833198154,0.979875354,1.152373784,1.355239044,1.593816947,1.87439439,2.204365021,2.592424078,3.048797515,3.585511478,4.216709209,4.959023745,5.83201622,6.858691334,8.066103565,9.486070089,11.15600922,13.11992643,15.42957398,18.14581465,21.34022558,25.09698443,29.51508761,34.71095895,40.8215177,48.00778653,56.45913473,66.39826837,78.087099,91.83364535,108.0001502,127.0126259,149.3720805,175.6677203,206.5924761,242.9612628,285.7324542,336.0331374,395.1888131,464.7583247,546.5749364,642.7946423,755.9529803,889.0318477,1045.538078,1229.595853,1446.055378,1700.620697,2000
A11642G_Q,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,6.72E-09,0.068368819,0.121366926,0.177243822,0.22048144,0.234456846,0.20720076,0.147737615,0.09451605,0.116816857,0.301139047,0.728232349,1.425006554,2.349697635,3.379585622,4.335322393,5.076287065,5.524016746,5.74611809,5.889921151,6.117149585,6.511728386,7.032213795,7.552725392,7.889095955,7.881876657,7.403069547,6.337458917,4.681113106,2.450052867,0
A20858G_Q,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.005297333,0.122686499,0.231829277,0.39511117,0.623536584,0.902589517,1.208994276,1.519025177,1.807243485,2.080460225,2.367288308,2.727687278,3.228044281,3.907022047,4.772806688,5.749997203,6.75086513,7.634164803,8.264819816,8.512502581,8.290591432,7.586931953,6.515371129,5.244523081,3.984023953,2.840505474,1.835476238,0.890605064,0

Notes:
• First column: Sample Name (must match GPS CSV exactly)
• Header row: Grain-size bin edges as numeric values; use the exact floats exported by your instrument (no rounding)
• Data values: Raw counts/intensity per bin; the app converts each row to proportions by default (configurable)
• Typical bin range: ~0.02–2000"""
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
        
