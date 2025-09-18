"""
Fullscreen-capable chart widget that wraps the existing ChartWidget.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QFrame, QLabel)
from PyQt6.QtCore import Qt
from .chart_widget import ChartWidget
from .fullscreen_viewer import FullscreenViewer


class FullscreenChartWidget(QWidget):
    """Chart widget with fullscreen capability."""
    
    def __init__(self, title="Chart", ylabel="Value", chart_title_display="", parent=None):
        super().__init__(parent)
        self.title = title
        self.ylabel = ylabel
        self.chart_title_display = chart_title_display or title
        self.fullscreen_viewer = None
        
        # Store plot data for recreation in fullscreen
        self.plot_data_cache = []
        self.optimal_marker_cache = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Header with title and fullscreen button
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(5, 5, 5, 0)
        
        # Title label
        title_label = QLabel(self.chart_title_display)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #333;
                padding: 5px 0;
            }
        """)
        header_layout.addWidget(title_label)
        
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
        
        # Create the main chart widget
        self.chart_widget = ChartWidget(title=self.title, ylabel=self.ylabel)
        layout.addWidget(self.chart_widget)
        
    def plot_data(self, k_values, y_values, color='b', symbol='o', name=None):
        """
        Plot data on the chart.
        
        Args:
            k_values: Array of k values (x-axis)
            y_values: Array of corresponding values (y-axis)
            color: Line/marker color
            symbol: Marker symbol
            name: Legend name for the plot
        """
        # Cache the plot data
        self.plot_data_cache = [{
            'k_values': k_values,
            'y_values': y_values,
            'color': color,
            'symbol': symbol,
            'name': name
        }]
        
        # Plot on the main widget
        self.chart_widget.plot_data(k_values, y_values, color, symbol, name)
        
    def add_optimal_marker(self, k_value, y_value):
        """
        Add a marker for the optimal k value.
        
        Args:
            k_value: Optimal k value
            y_value: Corresponding y value
        """
        # Cache the optimal marker
        self.optimal_marker_cache = {'k_value': k_value, 'y_value': y_value}
        
        # Add to the main widget
        self.chart_widget.add_optimal_marker(k_value, y_value)
        
    def clear(self):
        """Clear the chart."""
        self.plot_data_cache = []
        self.optimal_marker_cache = None
        self.chart_widget.clear()
        
    def _create_fullscreen_widget(self):
        """Create a new chart widget for fullscreen display."""
        # Create a BentoBox-style container to match the main UI
        from main import BentoBox
        container = BentoBox()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Add title label (same as in main view)
        title_label = QLabel(self.chart_title_display)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: 600;
                color: #333;
                padding: 5px 0;
            }
        """)
        layout.addWidget(title_label)
        
        # Create a new chart widget with the same configuration
        fullscreen_chart = ChartWidget(title=self.title, ylabel=self.ylabel)
        
        # Recreate all plots from cache
        for plot_data in self.plot_data_cache:
            fullscreen_chart.plot_data(
                plot_data['k_values'],
                plot_data['y_values'],
                plot_data['color'],
                plot_data['symbol'],
                plot_data['name']
            )
        
        # Add optimal marker if exists
        if self.optimal_marker_cache:
            fullscreen_chart.add_optimal_marker(
                self.optimal_marker_cache['k_value'],
                self.optimal_marker_cache['y_value']
            )
            
        # Make the plot widget larger in fullscreen
        fullscreen_chart.plot_widget.setMinimumHeight(600)
        
        layout.addWidget(fullscreen_chart)
        
        return container
        
    def open_fullscreen(self):
        """Open the chart in a fullscreen viewer."""
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