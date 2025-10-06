"""
Chart widget component
Handles CH and Rs analysis visualization.
"""

import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QToolTip
from PyQt6.QtCore import pyqtSignal as Signal
from .visualization_settings import VisualizationSettings


class ChartWidget(QWidget):
    """Widget for displaying analysis charts (CH and Rs)."""
    
    # Signal emitted when a K value is selected by clicking
    kValueSelected = Signal(int)  # K value
    
    def __init__(self, title="Chart", ylabel="Value", parent=None):
        super().__init__(parent)
        self.title = title
        self.ylabel = ylabel
        self.settings = VisualizationSettings()
        
        # Interactive selection state
        self.k_values = []  # Store K values for interaction
        self.y_values = []  # Store Y values for interaction
        self.selected_k = None  # Currently selected K value
        self.optimal_k = None  # Optimal K value (marked with star)
        self.scatter_plot = None  # Reference to scatter plot item
        self.selected_marker = None  # Reference to selected K marker
        
        self._setup_ui()
        
        # Connect to settings changes
        self.settings.settingsChanged.connect(self._update_plot_styling)
        
    def _setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create plot widget
        self.plot_widget = pg.PlotWidget()
        
        # Set initial styling from settings
        self._apply_styling()
        
        # Set background color
        self.plot_widget.setBackground('w')
        
        # Connect mouse events for interaction
        self.plot_widget.scene().sigMouseClicked.connect(self._on_plot_clicked)
        self.plot_widget.scene().sigMouseMoved.connect(self._on_mouse_moved)
        
        layout.addWidget(self.plot_widget)
        
    def _apply_styling(self):
        """Apply current settings to plot styling."""
        axis_style = self.settings.get_axis_style()
        tick_style = self.settings.get_tick_style()
        
        # Apply axis labels with settings
        self.plot_widget.setLabel('left', self.ylabel, **axis_style)
        self.plot_widget.setLabel('bottom', 'Number of Groups (k)', **axis_style)
        
        # Apply tick font styling
        left_axis = self.plot_widget.getAxis('left')
        bottom_axis = self.plot_widget.getAxis('bottom')
        
        # Create pens for axis ticks
        tick_pen = pg.mkPen(color=tick_style['color'])
        left_axis.setPen(tick_pen)
        bottom_axis.setPen(tick_pen)
        left_axis.setTextPen(tick_style['color'])
        bottom_axis.setTextPen(tick_style['color'])
        
        # Set tick text offset for better visibility
        left_axis.setStyle(tickTextOffset=10)
        bottom_axis.setStyle(tickTextOffset=10)
        
        # Apply tick font size using QFont
        from PyQt6.QtGui import QFont
        tick_font = QFont()
        tick_font.setPointSize(self.settings.tick_font_size)
        left_axis.setTickFont(tick_font)
        bottom_axis.setTickFont(tick_font)
        
        # Show grid
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
    
    def _update_plot_styling(self):
        """Update plot styling when settings change."""
        self._apply_styling()
        
        # Replot data with new line thickness if data exists
        if hasattr(self, '_last_plot_data'):
            k_values, y_values, color, symbol, name = self._last_plot_data
            self.plot_data(k_values, y_values, color, symbol, name)
        
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
        
        # Store data for interaction
        self.k_values = np.array(k_values)
        self.y_values = np.array(y_values)
        self.selected_marker = None  # Reset selected marker
        
        # Store plot data for replotting when settings change
        self._last_plot_data = (k_values, y_values, color, symbol, name)
        
        # Create pen for line with current thickness setting
        pen = pg.mkPen(color=color, width=self.settings.line_thickness)
        
        # Calculate symbol size based on line thickness
        symbol_size = max(6, int(self.settings.line_thickness * 3))
        
        # Plot the line
        self.plot_widget.plot(
            k_values, 
            y_values, 
            pen=pen, 
            name=name
        )
        
        # Plot clickable scatter points on top
        self.scatter_plot = self.plot_widget.plot(
            k_values,
            y_values,
            pen=None,
            symbol=symbol,
            symbolSize=symbol_size,
            symbolBrush=color,
            symbolPen=pg.mkPen(color='w', width=1)
        )
        
    def add_optimal_marker(self, k_value, y_value):
        """
        Add a marker for the optimal k value.
        
        Args:
            k_value: Optimal k value
            y_value: Corresponding y value
        """
        # Store optimal K
        self.optimal_k = k_value
        
        # Add star marker for optimal value
        self.plot_widget.plot(
            [k_value], 
            [y_value], 
            pen=None, 
            symbol='star', 
            symbolSize=15, 
            symbolBrush='r', 
            symbolPen=pg.mkPen(color='darkred', width=2),
            name=f'Optimal k={k_value}'
        )
        
    def _on_plot_clicked(self, event):
        """Handle mouse click on plot to select K value."""
        from PyQt6.QtCore import Qt
        
        if event.button() != Qt.MouseButton.LeftButton:
            return
        
        if len(self.k_values) == 0:
            return
        
        # Get click position in plot coordinates
        pos = event.scenePos()
        mouse_point = self.plot_widget.plotItem.vb.mapSceneToView(pos)
        x_click = mouse_point.x()
        y_click = mouse_point.y()
        
        # Find nearest K value
        # Normalize distances for better detection
        x_range = self.plot_widget.viewRange()[0]
        y_range = self.plot_widget.viewRange()[1]
        x_scale = x_range[1] - x_range[0] if x_range[1] != x_range[0] else 1
        y_scale = y_range[1] - y_range[0] if y_range[1] != y_range[0] else 1
        
        distances = np.sqrt(
            ((self.k_values - x_click) / x_scale) ** 2 + 
            ((self.y_values - y_click) / y_scale) ** 2
        )
        
        min_idx = np.argmin(distances)
        
        # Only select if click is close enough (threshold)
        if distances[min_idx] < 0.1:  # Normalized distance threshold
            selected_k = int(self.k_values[min_idx])
            selected_y = self.y_values[min_idx]
            
            # Update selection
            self._update_selection(selected_k, selected_y)
            
            # Emit signal
            self.kValueSelected.emit(selected_k)
    
    def _on_mouse_moved(self, pos):
        """Handle mouse movement for tooltip."""
        if len(self.k_values) == 0:
            return
        
        # Get mouse position in plot coordinates
        mouse_point = self.plot_widget.plotItem.vb.mapSceneToView(pos)
        x_hover = mouse_point.x()
        y_hover = mouse_point.y()
        
        # Find nearest K value
        x_range = self.plot_widget.viewRange()[0]
        y_range = self.plot_widget.viewRange()[1]
        x_scale = x_range[1] - x_range[0] if x_range[1] != x_range[0] else 1
        y_scale = y_range[1] - y_range[0] if y_range[1] != y_range[0] else 1
        
        distances = np.sqrt(
            ((self.k_values - x_hover) / x_scale) ** 2 + 
            ((self.y_values - y_hover) / y_scale) ** 2
        )
        
        min_idx = np.argmin(distances)
        
        # Show tooltip if close enough
        if distances[min_idx] < 0.08:
            k_val = int(self.k_values[min_idx])
            y_val = self.y_values[min_idx]
            
            # Convert to global position for tooltip
            global_pos = self.plot_widget.mapToGlobal(pos.toPoint())
            QToolTip.showText(global_pos, f"K={k_val}, {self.ylabel}={y_val:.2f}")
        else:
            QToolTip.hideText()
    
    def _update_selection(self, k_value, y_value):
        """Update visual selection marker."""
        # Remove previous selection marker if exists
        if self.selected_marker is not None:
            self.plot_widget.removeItem(self.selected_marker)
        
        # Update selected K
        self.selected_k = k_value
        
        # Add new selection marker (green circle)
        self.selected_marker = self.plot_widget.plot(
            [k_value],
            [y_value],
            pen=None,
            symbol='o',
            symbolSize=18,
            symbolBrush=None,
            symbolPen=pg.mkPen(color='#4CAF50', width=3)
        )
    
    def clear(self):
        """Clear the chart."""
        self.plot_widget.clear()
        self.k_values = []
        self.y_values = []
        self.selected_k = None
        self.optimal_k = None
        self.scatter_plot = None
        self.selected_marker = None


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
