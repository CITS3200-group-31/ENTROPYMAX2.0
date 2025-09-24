"""
Group detail popup component for displaying line charts for each group.
"""

import os
import csv
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QToolTip
from PyQt6.QtCore import Qt, pyqtSignal as Signal, QObject, QTimer
from collections import defaultdict


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
            self.x_values = np.arange(len(self.x_labels))
            
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


class GroupDetailWindow(QWidget):
    """Individual popup window showing line chart for a specific group."""
    
    # Signal emitted when a line is clicked
    lineClicked = Signal(str)  # sample_name

    def __init__(self, group_id, samples, x_labels, x_values, color, x_unit='\u03bcm', y_unit='a.u.'):
        super().__init__()
        self.setWindowFlag(Qt.WindowType.Window, True)
        self.group_id = group_id
        self.samples = samples
        self.x_labels = x_labels
        self.x_values = x_values
        self.base_color = color
        self.x_unit = x_unit
        self.y_unit = y_unit
        self.plot_items = []  # Store plot items with sample names
        self.hover_tooltip = None  # For showing sample name on hover
        
        self._setup_ui()
        self._plot_data()
        
    def _setup_ui(self):
        """Initialize the UI for the popup window."""
        self.setWindowTitle(f"Group {self.group_id} - Grain Size Distribution")
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #333333;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header with group info
        header_layout = QHBoxLayout()
        
        # Group title
        title_label = QLabel(f"Group {self.group_id}")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333;
                padding: 5px;
            }
        """)
        header_layout.addWidget(title_label)
        
        # Sample count
        count_label = QLabel(f"Samples: {len(self.samples)}")
        count_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666;
                padding: 5px;
            }
        """)
        header_layout.addWidget(count_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Create plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        
        # Configure plot appearance with units
        label_style = {'color': '#333', 'font-size': '12pt', 'font-weight': 'bold'}
        self.plot_widget.setLabel('left', 'Value', units=self.y_unit, **label_style)
        self.plot_widget.setLabel('bottom', 'Grain Size', units=self.x_unit, **label_style)
        
        # Style the plot
        self.plot_widget.getAxis('left').setPen(pg.mkPen(color='#333', width=1))
        self.plot_widget.getAxis('bottom').setPen(pg.mkPen(color='#333', width=1))
        self.plot_widget.showGrid(x=True, y=True, alpha=0.2)
        
        layout.addWidget(self.plot_widget)
        
        # Connect range change for adaptive x-axis ticks
        self.plot_widget.getViewBox().sigRangeChanged.connect(self._on_range_changed)
    
    def _plot_data(self):
        """Plot the sample data on the chart."""
        # Initialize x-axis ticks
        self._update_x_ticks()
        
        # Convert color to RGBA (fully opaque for sample lines)
        color = pg.mkColor(self.base_color)
        r, g, b, _ = color.getRgb()
        
        # Clear existing plot items
        self.plot_items = []
        
        # Plot individual sample lines (opaque, normal width)
        for sample in self.samples:
            y_values = sample['values']
            pen = pg.mkPen(color=(r, g, b, 255), width=3.5)
            plot_item = self.plot_widget.plot(self.x_values, y_values, pen=pen)
            
            # Store plot item with sample name and original pen for click detection
            self.plot_items.append({
                'plot_item': plot_item,
                'sample_name': sample['name'],
                'original_pen': pen,
                'hover_pen': pg.mkPen(color=(r, g, b, 255), width=5.0),  # Thicker for hover
                'click_pen': pg.mkPen(color=(255, 165, 0, 255), width=4.5)  # Orange for click feedback
            })
        
        # Connect click and hover events to plot widget
        self.plot_widget.scene().sigMouseClicked.connect(self._on_plot_clicked)
        self.plot_widget.scene().sigMouseMoved.connect(self._on_mouse_hover)
    

    def _on_range_changed(self, *args):
        """Update x-axis ticks adaptively when view range changes."""
        self._update_x_ticks()
        
    def _update_x_ticks(self):
        """Adaptive x-axis tick labeling depending on zoom level."""
        ax = self.plot_widget.getAxis('bottom')
        vb = self.plot_widget.getViewBox()
        try:
            (xmin, xmax), _ = vb.viewRange()
        except Exception:
            xmin, xmax = 0, len(self.x_values)
        
        xmin = max(0, int(np.floor(xmin)))
        xmax = min(len(self.x_values) - 1, int(np.ceil(xmax)))
        visible = max(1, xmax - xmin + 1)
        
        ticks = []
        if visible > 30:
            # Zoomed out: show numeric ticks like Y-axis
            step = max(1, int(np.ceil(visible / 10)))
            start = xmin - (xmin % step)
            for pos in range(start, xmax + 1, step):
                ticks.append((pos, str(pos)))
        else:
            # Zoomed in: show actual grain size labels, possibly downsampled
            step = max(1, int(np.ceil(visible / 12)))
            for pos in range(xmin, xmax + 1, step):
                label = self.x_labels[pos] if pos < len(self.x_labels) else str(pos)
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
                    distances = np.sqrt((x_data - x_click)**2 + (y_data - y_click)**2)
                    min_idx = np.argmin(distances)
                    
                    if distances[min_idx] < min_distance:
                        min_distance = distances[min_idx]
                        closest_sample = sample_name
                        closest_item_data = item_data
            
            # If we found a line close enough to the click, provide feedback and emit signal
            if closest_sample and min_distance < 0.5:  # Threshold for "close enough"
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
                distances = np.sqrt((x_data - x_hover)**2 + (y_data - y_hover)**2)
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
        if closest_sample and min_distance < 0.3:  # Smaller threshold for hover
            # Convert scene position to global position for tooltip
            global_pos = self.plot_widget.mapToGlobal(pos.toPoint())
            QToolTip.showText(global_pos, f"Sample: {closest_sample}")
            
            # Apply hover effect - make line thicker
            if closest_item_data and (not hasattr(closest_item_data, '_is_clicked_feedback') or not closest_item_data['_is_clicked_feedback']):
                closest_item_data['plot_item'].setPen(closest_item_data['hover_pen'])
        else:
            # Hide tooltip if not hovering over a line
            QToolTip.hideText()
