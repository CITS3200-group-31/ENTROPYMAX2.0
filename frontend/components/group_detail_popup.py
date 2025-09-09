"""
Group detail popup component for displaying line charts for each group.
Shows individual sample lines with full opacity and optional median line.
"""

import os
import csv
import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QCheckBox
from PySide6.QtCore import Qt
from collections import defaultdict


class GroupDetailPopup:
    """Manager class for creating and managing group detail popup windows."""
    
    def __init__(self):
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
                    y_values = [float(val) for val in row[1:]]
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
            
            window.show()
            self.detail_windows.append(window)
    
    def close_all(self):
        """Close all open detail windows."""
        for window in self.detail_windows:
            window.close()
        self.detail_windows.clear()


class GroupDetailWindow(QWidget):
    """Individual popup window showing line chart for a specific group."""

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
        
        self.median_checkbox = None
        self.median_line = None
        
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
        
        # Median toggle control
        controls_layout = QHBoxLayout()
        self.median_checkbox = QCheckBox("Show Median")
        self.median_checkbox.setChecked(False)
        self.median_checkbox.stateChanged.connect(self._toggle_median)
        self.median_checkbox.setStyleSheet("""
            QCheckBox { font-size: 12px; color: #333; }
            QCheckBox::indicator { width: 16px; height: 16px; }
            QCheckBox::indicator:unchecked { border: 2px solid #d0d0d0; background-color: white; border-radius: 3px; }
            QCheckBox::indicator:checked { border: 2px solid #009688; background-color: #009688; border-radius: 3px; }
        """)
        controls_layout.addWidget(self.median_checkbox)
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Connect range change for adaptive x-axis ticks
        self.plot_widget.getViewBox().sigRangeChanged.connect(self._on_range_changed)
    
    def _plot_data(self):
        """Plot the sample data on the chart."""
        # Initialize x-axis ticks
        self._update_x_ticks()
        
        # Convert color to RGBA (fully opaque for sample lines)
        color = pg.mkColor(self.base_color)
        r, g, b, _ = color.getRgb()
        
        # Plot individual sample lines (opaque, normal width)
        for sample in self.samples:
            y_values = sample['values']
            pen = pg.mkPen(color=(r, g, b, 255), width=2)
            self.plot_widget.plot(self.x_values, y_values, pen=pen)
        
        # Median line is optional and drawn on demand via checkbox
    
    def _toggle_median(self, state):
        """Show or hide the median line based on checkbox state."""
        if state == 0:
            # Hide median
            if self.median_line is not None:
                try:
                    self.plot_widget.removeItem(self.median_line)
                except Exception:
                    pass
                self.median_line = None
        else:
            # Show median
            self._draw_median_line()
        
    def _draw_median_line(self):
        """Compute and draw the median line in a distinct color."""
        # Calculate median values only when needed
        all_values = np.array([s['values'] for s in self.samples])
        median_values = np.median(all_values, axis=0)
        
        # Distinct color for median (magenta)
        median_pen = pg.mkPen(color=(255, 0, 170, 255), width=4, style=Qt.PenStyle.DashLine)
        self.median_line = self.plot_widget.plot(
            self.x_values, median_values, pen=median_pen, name=f"Group {self.group_id} Median"
        )
        
        # Ensure legend exists and shows median
        if self.plot_widget.plotItem.legend is None:
            self.plot_widget.addLegend(offset=(10, 10), brush=pg.mkBrush(255, 255, 255, 200))
        
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
