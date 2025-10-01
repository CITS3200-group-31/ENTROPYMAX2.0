"""
Group detail popup component for displaying line charts for each group.
"""

import os
import csv
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QToolTip, QPushButton, QMainWindow, QToolBar, QFileDialog
from PyQt6.QtCore import Qt, pyqtSignal as Signal, QObject, QTimer
from PyQt6.QtGui import QAction
from collections import defaultdict
from .visualization_settings import VisualizationSettings
from .settings_dialog import SettingsDialog


class GroupDetailPopup(QObject):
    """Manager class for creating and managing group detail popup windows."""
    
    # Signal emitted when a sample line is clicked in any group detail window
    sampleLineClicked = Signal(str)  # sample_name
    
    def __init__(self):
        super().__init__()
        self.detail_windows = []
        self.data_path = None
        self.group_data = {}
        
    def set_data_path(self, path):
        """Set the path to the CSV data file."""
        self.data_path = path
        
    def load_and_show_popups(self, csv_path=None, k_value=None, x_unit='μm', y_unit='a.u.'):
        """
        Load data from CSV and create popup windows for each group.
        
        Args:
            csv_path: Path to the CSV file (optional, uses default if not provided)
            k_value: Number of groups (optional, uses mock data if not provided)
            x_unit: Unit label for the x-axis (default 'μm')
            y_unit: Unit label for the y-axis (default 'a.u.')
        """
        # Close any existing windows
        self.close_all()
        
        # Use provided path or default to sample data
        if csv_path is None:
            csv_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                'test', 'data', 'Input file GP for Entropy 20240910.csv'
            )
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Data file not found: {csv_path}")
        
        # Parse the CSV data
        grouped_samples = self._parse_csv_data(csv_path, k_value)
        
        # Create popup windows for each group
        self._create_popup_windows(grouped_samples, x_unit=x_unit, y_unit=y_unit)
    
    def _parse_csv_data(self, csv_path, k_value=None):
        """
        Parse CSV data and group samples.
        
        Args:
            csv_path: Path to the CSV file
            k_value: Number of groups (if None, uses 5 as default)
        
        Returns:
            Dictionary with group_id as key and list of sample values as value
        """
        grouped_samples = defaultdict(list)
        
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            
            # Extract column headers (grain sizes)
            self.x_labels = header[1:]  # Skip first column (sample name)
            # Convert grain sizes to numeric values for log scale
            self.x_values = self._parse_grain_sizes(self.x_labels)
            
            # Process each row of data
            for i, row in enumerate(reader):
                if not row:
                    continue
                
                # Mock grouping: distribute samples across k groups
                # In real implementation, this should come from the analysis results
                k = k_value if k_value else 5
                group_id = (i % k) + 1
                
                # Convert string values to float, skip the sample name
                try:
                    # Handle empty strings by converting them to 0.0
                    y_values = []
                    for val in row[1:]:
                        if val.strip() == '':
                            y_values.append(0.0)
                        else:
                            y_values.append(float(val))
                    grouped_samples[group_id].append({
                        'name': row[0],  # Sample name
                        'values': y_values
                    })
                except (ValueError, IndexError):
                    continue
        
        return grouped_samples
    
    def _parse_grain_sizes(self, labels):
        """
        Parse grain size labels to numeric values.
        Assumes grain sizes are numeric values (e.g., '0.1', '1', '10', '100')
        
        Args:
            labels: List of grain size labels
        
        Returns:
            NumPy array of numeric grain sizes
        """
        numeric_values = []
        for label in labels:
            try:
                # Remove unit if present and convert to float
                value_str = label.replace('μm', '').replace('um', '').strip()
                numeric_values.append(float(value_str))
            except (ValueError, AttributeError):
                # If can't parse, use index as fallback
                numeric_values.append(len(numeric_values) + 1)
        
        return np.array(numeric_values)
    
    def _create_popup_windows(self, grouped_samples, x_unit='μm', y_unit='a.u.'):
        """
        Create popup windows for each group showing line charts.
        
        Args:
            grouped_samples: Dictionary with group data
            x_unit: Unit label for x-axis
            y_unit: Unit label for y-axis
        """
        # Define colors for different groups (matching the main application style)
        base_colors = ['#2196F3', '#4CAF50', '#FF9800', '#F44336', '#9C27B0',
                      '#00BCD4', '#8BC34A', '#FFC107', '#E91E63', '#673AB7']
        
        for group_idx, (group_id, samples) in enumerate(sorted(grouped_samples.items())):
            if not samples:
                continue
            
            # Create window for this group
            window = GroupDetailWindow(
                group_id=group_id,
                samples=samples,
                x_labels=self.x_labels,
                x_values=self.x_values,
                color=base_colors[group_idx % len(base_colors)],
                x_unit=x_unit,
                y_unit=y_unit
            )
            
            # Position windows in a cascade
            window.setGeometry(
                150 + group_idx * 30,
                150 + group_idx * 30,
                900, 550
            )
            
            # Connect the lineClicked signal from each window to our sampleLineClicked signal
            window.lineClicked.connect(self.sampleLineClicked)
            
            window.show()
            self.detail_windows.append(window)
    
    def close_all(self):
        """Close all open detail windows."""
        for window in self.detail_windows:
            window.close()
        self.detail_windows.clear()


class GroupDetailWindow(QMainWindow):
    """Individual popup window showing line chart for a specific group."""
    
    # Signal emitted when a line is clicked
    lineClicked = Signal(str)  # sample_name

    def __init__(self, group_id, samples, x_labels, x_values, color, x_unit='\u03bcm', y_unit='a.u.'):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.Window)
        self.group_id = group_id
        self.samples = samples
        self.x_labels = x_labels
        self.x_values = x_values
        self.base_color = color
        self.x_unit = x_unit
        self.y_unit = y_unit
        self.plot_items = []  # Store plot items with sample names
        self.hover_tooltip = None  # For showing sample name on hover
        self.is_log_scale = True  # Default to logarithmic scale
        self.original_x_values = None  # Store original x values for switching
        
        # Get visualization settings instance
        self.settings = VisualizationSettings()
        
        # Initialize settings dialog
        self.settings_dialog = SettingsDialog(self)
        
        self._setup_ui()
        self._plot_data()
        
        # Connect to settings changes
        self.settings.settingsChanged.connect(self._update_plot_styling)
        
    def _setup_ui(self):
        """Initialize the UI for the popup window."""
        self.setWindowTitle(f"Group {self.group_id} - Grain Size Distribution")
        
        # Setup toolbar first
        self._setup_toolbar()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create plot widget directly without header
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        
        # Apply initial styling from settings
        self._apply_plot_styling()
        
        # Show grid
        self.plot_widget.showGrid(x=True, y=True, alpha=0.2)
        
        layout.addWidget(self.plot_widget)
        
        # Connect range change for adaptive x-axis ticks
        self.plot_widget.getViewBox().sigRangeChanged.connect(self._on_range_changed)
    
    def _apply_plot_styling(self):
        """Apply current settings to plot styling."""
        axis_style = self.settings.get_axis_style()
        tick_style = self.settings.get_tick_style()
        
        # Apply axis labels with settings
        self.plot_widget.setLabel('left', 'Value', units=self.y_unit, **axis_style)
        self.plot_widget.setLabel('bottom', 'Grain Size', units=self.x_unit, **axis_style)
        
        # Apply tick font styling
        left_axis = self.plot_widget.getAxis('left')
        bottom_axis = self.plot_widget.getAxis('bottom')
        
        # Create pens for axis
        axis_pen = pg.mkPen(color='#333', width=1)
        left_axis.setPen(axis_pen)
        bottom_axis.setPen(axis_pen)
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
    
    def _update_plot_styling(self):
        """Update plot styling when settings change."""
        self._apply_plot_styling()
        # Replot data with new line thickness
        self._plot_data()
    
    def _setup_toolbar(self):
        """Setup toolbar with scale toggle and export actions."""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Scale toggle action
        self.scale_action = QAction("Switch to Linear", self)
        self.scale_action.setToolTip("Toggle between logarithmic and linear scale")
        self.scale_action.triggered.connect(self._toggle_scale)
        toolbar.addAction(self.scale_action)
        
        # Separator
        toolbar.addSeparator()
        
        # Settings action
        settings_action = QAction("Settings", self)
        settings_action.setToolTip("Adjust visualization settings for publication standards")
        settings_action.triggered.connect(self._show_settings)
        toolbar.addAction(settings_action)
        
        # Separator
        toolbar.addSeparator()
        
        # Export action
        export_action = QAction("Export as PNG", self)
        export_action.setToolTip("Export current view as PNG")
        export_action.triggered.connect(self._export_as_png)
        toolbar.addAction(export_action)
    
    def _show_settings(self):
        """Show visualization settings dialog."""
        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()
    
    def _toggle_scale(self):
        """Toggle between logarithmic and linear scale for X-axis."""
        self.is_log_scale = not self.is_log_scale
        
        # Update action text
        if self.is_log_scale:
            self.scale_action.setText("Switch to Linear")
        else:
            self.scale_action.setText("Switch to Log")
        
        # Replot data with new scale
        self._plot_data()
        
        # Auto-range the view to fit the data
        self.plot_widget.autoRange()
    
    def _export_as_png(self):
        """Export the current plot as PNG image."""
        # Create file dialog for saving
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            f"Export Group {self.group_id} as PNG",
            f"group_{self.group_id}_grain_distribution.png",
            "PNG Files (*.png)"
        )
        
        if file_path:
            # Get the central widget which contains the plot
            central_widget = self.centralWidget()
            pixmap = central_widget.grab()
            
            # Save the pixmap
            if pixmap.save(file_path):
                print(f"Successfully exported to {file_path}")
                # Show status in window title temporarily
                original_title = self.windowTitle()
                self.setWindowTitle(f"{original_title} - Exported!")
                QTimer.singleShot(2000, lambda: self.setWindowTitle(original_title))
            else:
                print(f"Failed to export to {file_path}")
    
    def _plot_data(self):
        """Plot the sample data on the chart."""
        # Store original x values
        if self.original_x_values is None:
            self.original_x_values = self.x_values.copy()
        
        # Convert color to RGBA (fully opaque for sample lines)
        color = pg.mkColor(self.base_color)
        r, g, b, _ = color.getRgb()
        
        # Clear existing plot items
        self.plot_widget.clear()
        self.plot_items = []
        
        # Plot individual sample lines based on scale
        if self.is_log_scale:
            # Use log scale for x-axis (handle zero/negative values)
            x_plot_values = np.where(self.original_x_values > 0, 
                                    np.log10(self.original_x_values), 
                                    np.nan)
            # Filter out NaN values
            valid_mask = ~np.isnan(x_plot_values)
            
            for sample in self.samples:
                y_values = sample['values']
                # Use settings for line thickness
                pen = pg.mkPen(color=(r, g, b, 255), width=self.settings.line_thickness)
                plot_item = self.plot_widget.plot(x_plot_values[valid_mask], 
                                                 np.array(y_values)[valid_mask], 
                                                 pen=pen)
                
                # Store plot item with sample name and original pen for click detection
                hover_width = self.settings.line_thickness + 1.5
                click_width = self.settings.line_thickness + 1.0
                self.plot_items.append({
                    'plot_item': plot_item,
                    'sample_name': sample['name'],
                    'original_pen': pen,
                    'hover_pen': pg.mkPen(color=(r, g, b, 255), width=hover_width),  # Thicker for hover
                    'click_pen': pg.mkPen(color=(255, 165, 0, 255), width=click_width)  # Orange for click feedback
                })
        else:
            # Linear scale - use indices as x-values
            x_indices = np.arange(len(self.original_x_values))
            
            for sample in self.samples:
                y_values = sample['values']
                # Use settings for line thickness
                pen = pg.mkPen(color=(r, g, b, 255), width=self.settings.line_thickness)
                plot_item = self.plot_widget.plot(x_indices, y_values, pen=pen)
                
                # Store plot item with sample name and original pen for click detection
                hover_width = self.settings.line_thickness + 1.5
                click_width = self.settings.line_thickness + 1.0
                self.plot_items.append({
                    'plot_item': plot_item,
                    'sample_name': sample['name'],
                    'original_pen': pen,
                    'hover_pen': pg.mkPen(color=(r, g, b, 255), width=hover_width),  # Thicker for hover
                    'click_pen': pg.mkPen(color=(255, 165, 0, 255), width=click_width)  # Orange for click feedback
                })
        
        # Update x-axis ticks after plotting
        self._update_x_ticks()
        
        # Connect click and hover events to plot widget
        self.plot_widget.scene().sigMouseClicked.connect(self._on_plot_clicked)
        self.plot_widget.scene().sigMouseMoved.connect(self._on_mouse_hover)
        
        # Connect click and hover events to plot widget
        self.plot_widget.scene().sigMouseClicked.connect(self._on_plot_clicked)
        self.plot_widget.scene().sigMouseMoved.connect(self._on_mouse_hover)
    

    def _on_range_changed(self, *args):
        """Update x-axis ticks adaptively when view range changes."""
        self._update_x_ticks()
        
    def _update_x_ticks(self):
        """Adaptive x-axis tick labeling depending on zoom level and scale type."""
        ax = self.plot_widget.getAxis('bottom')
        vb = self.plot_widget.getViewBox()
        
        if self.is_log_scale:
            # For log scale, create custom tick labels
            ticks = []
            
            # Generate log-spaced tick positions
            if self.original_x_values is not None and len(self.original_x_values) > 0:
                min_val = np.min(self.original_x_values[self.original_x_values > 0])
                max_val = np.max(self.original_x_values)
                
                # Create tick positions at powers of 10 and intermediate values
                log_min = np.floor(np.log10(min_val))
                log_max = np.ceil(np.log10(max_val))
                
                # Major ticks at powers of 10
                for exp in range(int(log_min), int(log_max) + 1):
                    val = 10 ** exp
                    if min_val <= val <= max_val:
                        log_pos = np.log10(val)
                        # Format label based on value magnitude
                        if val >= 1:
                            label = f"{int(val)}" if val == int(val) else f"{val:.1f}"
                        else:
                            label = f"{val:.2f}" if val >= 0.1 else f"{val:.3f}"
                        ticks.append((log_pos, label))
                
                # Add intermediate ticks for better resolution
                if log_max - log_min <= 2:
                    for exp in range(int(log_min), int(log_max) + 1):
                        for mult in [2, 5]:
                            val = mult * (10 ** exp)
                            if min_val <= val <= max_val:
                                log_pos = np.log10(val)
                                label = f"{val:.1f}" if val >= 1 else f"{val:.2f}"
                                ticks.append((log_pos, label))
            
            ax.setTicks([ticks])
        else:
            # Linear scale - create ticks based on actual grain size values
            if self.original_x_values is not None and len(self.original_x_values) > 0:
                # Get actual data range
                min_val = np.min(self.original_x_values)
                max_val = np.max(self.original_x_values)
                
                # Create tick values in the actual grain size range
                num_ticks = min(10, len(self.original_x_values))
                
                # Select evenly spaced indices
                indices = np.linspace(0, len(self.original_x_values) - 1, num_ticks, dtype=int)
                ticks = []
                
                for idx in indices:
                    pos = idx  # Position in the array
                    val = self.original_x_values[idx]  # Actual grain size value
                    
                    # Format label based on value magnitude
                    if val >= 100:
                        label = f"{int(val)}"
                    elif val >= 1:
                        label = f"{val:.1f}" if val != int(val) else f"{int(val)}"
                    elif val >= 0.1:
                        label = f"{val:.2f}"
                    else:
                        label = f"{val:.3f}"
                    
                    ticks.append((pos, label))
                
                ax.setTicks([ticks])
        
        ax.setTextPen('#333')
    
    def _on_plot_clicked(self, event):
        """Handle mouse click on the plot to detect which line was clicked."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Get the click position in plot coordinates
            pos = event.scenePos()
            mouse_point = self.plot_widget.plotItem.vb.mapSceneToView(pos)
            x_click = mouse_point.x()
            y_click = mouse_point.y()
            
            # Apply scale transformation for click detection
            if self.is_log_scale and self.original_x_values is not None:
                x_plot_values = np.where(self.original_x_values > 0,
                                        np.log10(self.original_x_values),
                                        np.nan)
            else:
                x_plot_values = self.original_x_values if self.original_x_values is not None else self.x_values
            
            # Find the closest line to the click
            min_distance = float('inf')
            closest_sample = None
            closest_item_data = None
            
            for item_data in self.plot_items:
                plot_item = item_data['plot_item']
                sample_name = item_data['sample_name']
                
                # Get the data from the plot item
                x_data, y_data = plot_item.getData()
                
                # Find the closest point on this line to the click
                if len(x_data) > 0:
                    # Calculate normalized distances for better scale-independent detection
                    x_range = self.plot_widget.viewRange()[0]
                    y_range = self.plot_widget.viewRange()[1]
                    x_scale = x_range[1] - x_range[0] if x_range[1] != x_range[0] else 1
                    y_scale = y_range[1] - y_range[0] if y_range[1] != y_range[0] else 1
                    
                    distances = np.sqrt(((x_data - x_click)/x_scale)**2 + ((y_data - y_click)/y_scale)**2)
                    min_idx = np.argmin(distances)
                    
                    if distances[min_idx] < min_distance:
                        min_distance = distances[min_idx]
                        closest_sample = sample_name
                        closest_item_data = item_data
            
            # If we found a line close enough to the click, provide feedback and emit signal
            if closest_sample and min_distance < 0.05:  # Threshold for "close enough" (normalized)
                # Visual click feedback - briefly change line color
                if closest_item_data:
                    plot_item = closest_item_data['plot_item']
                    click_pen = closest_item_data['click_pen']
                    original_pen = closest_item_data['original_pen']
                    
                    # Set click color and mark as in feedback state
                    plot_item.setPen(click_pen)
                    closest_item_data['_is_clicked_feedback'] = True
                    
                    # Reset to original color after a short delay
                    def reset_color():
                        plot_item.setPen(original_pen)
                        closest_item_data['_is_clicked_feedback'] = False
                    QTimer.singleShot(200, reset_color)
                
                self.lineClicked.emit(closest_sample)
    
    def _on_mouse_hover(self, pos):
        """Handle mouse hover to show sample name tooltip and provide visual feedback."""
        # Convert scene position to plot coordinates
        mouse_point = self.plot_widget.plotItem.vb.mapSceneToView(pos)
        x_hover = mouse_point.x()
        y_hover = mouse_point.y()
        
        # Get plot ranges for normalized distance calculation
        x_range = self.plot_widget.viewRange()[0]
        y_range = self.plot_widget.viewRange()[1]
        x_scale = x_range[1] - x_range[0] if x_range[1] != x_range[0] else 1
        y_scale = y_range[1] - y_range[0] if y_range[1] != y_range[0] else 1
        
        # Find the closest line to the hover position
        min_distance = float('inf')
        closest_sample = None
        closest_item_data = None
        
        for item_data in self.plot_items:
            plot_item = item_data['plot_item']
            sample_name = item_data['sample_name']
            
            # Get the data from the plot item
            x_data, y_data = plot_item.getData()
            
            # Find the closest point on this line to the hover position
            if len(x_data) > 0:
                # Calculate normalized distances for scale-independent detection
                distances = np.sqrt(((x_data - x_hover)/x_scale)**2 + ((y_data - y_hover)/y_scale)**2)
                min_idx = np.argmin(distances)
                
                if distances[min_idx] < min_distance:
                    min_distance = distances[min_idx]
                    closest_sample = sample_name
                    closest_item_data = item_data
        
        # Reset all lines to original pen (remove previous hover effects)
        for item_data in self.plot_items:
            if not hasattr(item_data, '_is_clicked_feedback') or not item_data['_is_clicked_feedback']:
                item_data['plot_item'].setPen(item_data['original_pen'])
        
        # Show tooltip and hover effect if we're close enough to a line
        if closest_sample and min_distance < 0.03:  # Threshold for hover (normalized)
            # Convert scene position to global position for tooltip
            global_pos = self.plot_widget.mapToGlobal(pos.toPoint())
            QToolTip.showText(global_pos, f"Sample: {closest_sample}")
            
            # Apply hover effect - make line thicker
            if closest_item_data and (not hasattr(closest_item_data, '_is_clicked_feedback') or not closest_item_data['_is_clicked_feedback']):
                closest_item_data['plot_item'].setPen(closest_item_data['hover_pen'])
        else:
            # Hide tooltip if not hovering over a line
            QToolTip.hideText()
