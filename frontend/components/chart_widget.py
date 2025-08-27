"""
Chart widget component for EntropyMax frontend.
Handles CH and Rs analysis visualization.
"""

import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox


class ChartWidget(QWidget):
    """Widget for displaying analysis charts (CH and Rs)."""
    
    def __init__(self, title="Chart", ylabel="Value", parent=None):
        super().__init__(parent)
        self.title = title
        self.ylabel = ylabel
        self._setup_ui()
        
    def _setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Create plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('left', self.ylabel)
        self.plot_widget.setLabel('bottom', 'Number of Groups (k)')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Set background color
        self.plot_widget.setBackground('w')
        
        layout.addWidget(self.plot_widget)
        
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
        self.plot_widget.clear()
        
        # Create pen for line
        pen = pg.mkPen(color=color, width=2)
        
        # Plot the data
        self.plot_widget.plot(
            k_values, 
            y_values, 
            pen=pen, 
            symbol=symbol, 
            symbolSize=8,
            symbolBrush=color, 
            name=name
        )
        
    def add_optimal_marker(self, k_value, y_value):
        """
        Add a marker for the optimal k value.
        
        Args:
            k_value: Optimal k value
            y_value: Corresponding y value
        """
        # Add star marker for optimal value
        self.plot_widget.plot(
            [k_value], 
            [y_value], 
            pen=None, 
            symbol='star', 
            symbolSize=15, 
            symbolBrush='r', 
            name=f'Optimal k={k_value}'
        )
        
    def clear(self):
        """Clear the chart."""
        self.plot_widget.clear()


class DualChartWidget(QWidget):
    """Widget containing both CH and Rs charts side by side."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Create CH chart
        self.ch_chart = ChartWidget(
            title="Calinski-Harabasz Index",
            ylabel="CH Index"
        )
        
        # Create Rs chart
        self.rs_chart = ChartWidget(
            title="Rs Percentage",
            ylabel="Rs %"
        )
        
    def plot_analysis_results(self, k_values, ch_values, rs_values, optimal_k=None):
        """
        Plot both CH and Rs analysis results.
        
        Args:
            k_values: Array of k values
            ch_values: Array of CH values
            rs_values: Array of Rs values
            optimal_k: Optimal k value to highlight
        """
        # Plot CH values
        self.ch_chart.plot_data(
            k_values, 
            ch_values, 
            color='b', 
            symbol='o', 
            name='CH Index'
        )
        
        # Plot Rs values
        self.rs_chart.plot_data(
            k_values, 
            rs_values, 
            color='r', 
            symbol='s', 
            name='Rs %'
        )
        
        # Add optimal marker if provided
        if optimal_k is not None:
            # Find the index of optimal k
            optimal_idx = np.where(k_values == optimal_k)[0]
            if len(optimal_idx) > 0:
                optimal_idx = optimal_idx[0]
                self.ch_chart.add_optimal_marker(optimal_k, ch_values[optimal_idx])
                
    def clear(self):
        """Clear both charts."""
        self.ch_chart.clear()
        self.rs_chart.clear()
