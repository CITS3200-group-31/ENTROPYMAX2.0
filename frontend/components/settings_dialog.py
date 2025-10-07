"""
Settings dialog for adjusting visualization parameters for publication standards.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QLabel, QSlider, QSpinBox, QPushButton, QComboBox,
    QDialogButtonBox, QWidget, QGridLayout, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal as Signal
from PyQt6.QtGui import QFont
from .visualization_settings import VisualizationSettings


class SettingsDialog(QDialog):
    """Dialog for adjusting visualization settings for publication standards."""
    
    settingsApplied = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Visualization Settings - Publication Standards")
        self.setModal(False)  # Non-modal to see changes in real-time
        self.settings = VisualizationSettings()
        
        self._setup_ui()
        self._load_current_settings()
        self._connect_signals()
        
    def _setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Preset configurations
        preset_group = QGroupBox("Publication Presets")
        preset_layout = QHBoxLayout()
        
        preset_label = QLabel("Select preset:")
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "Custom",
            "Nature",
            "Science",
            "Presentation",
            "Poster"
        ])
        
        preset_layout.addWidget(preset_label)
        preset_layout.addWidget(self.preset_combo)
        preset_layout.addStretch()
        
        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)
        
        # Font Size Settings
        font_group = QGroupBox("Font Sizes (pt)")
        font_layout = QGridLayout()
        
        # Axis font size
        font_layout.addWidget(QLabel("Axis Labels:"), 0, 0)
        self.axis_size_spin = QSpinBox()
        self.axis_size_spin.setRange(
            self.settings.MIN_FONT_SIZE, 
            self.settings.MAX_FONT_SIZE
        )
        self.axis_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.axis_size_slider.setRange(
            self.settings.MIN_FONT_SIZE, 
            self.settings.MAX_FONT_SIZE
        )
        font_layout.addWidget(self.axis_size_spin, 0, 1)
        font_layout.addWidget(self.axis_size_slider, 0, 2)
        
        # Tick font size
        font_layout.addWidget(QLabel("Tick Labels:"), 1, 0)
        self.tick_size_spin = QSpinBox()
        self.tick_size_spin.setRange(
            self.settings.MIN_FONT_SIZE, 
            self.settings.MAX_FONT_SIZE
        )
        self.tick_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.tick_size_slider.setRange(
            self.settings.MIN_FONT_SIZE, 
            self.settings.MAX_FONT_SIZE
        )
        font_layout.addWidget(self.tick_size_spin, 1, 1)
        font_layout.addWidget(self.tick_size_slider, 1, 2)
        
        font_group.setLayout(font_layout)
        layout.addWidget(font_group)
        
        # Line Thickness Settings
        line_group = QGroupBox("Line Properties")
        line_layout = QGridLayout()
        
        line_layout.addWidget(QLabel("Curve Thickness:"), 0, 0)
        self.line_thickness_spin = QSpinBox()
        self.line_thickness_spin.setRange(
            int(self.settings.MIN_LINE_THICKNESS * 10), 
            int(self.settings.MAX_LINE_THICKNESS * 10)
        )
        self.line_thickness_spin.setSingleStep(5)
        self.line_thickness_spin.setSuffix(" pt")
        
        self.line_thickness_slider = QSlider(Qt.Orientation.Horizontal)
        self.line_thickness_slider.setRange(
            int(self.settings.MIN_LINE_THICKNESS * 10), 
            int(self.settings.MAX_LINE_THICKNESS * 10)
        )
        self.line_thickness_slider.setSingleStep(5)
        
        line_layout.addWidget(self.line_thickness_spin, 0, 1)
        line_layout.addWidget(self.line_thickness_slider, 0, 2)
        
        # Add preview label for line thickness
        self.line_preview = QLabel("━━━━━━━━━━")
        self.line_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        line_layout.addWidget(QLabel("Preview:"), 1, 0)
        line_layout.addWidget(self.line_preview, 1, 1, 1, 2)
        
        line_group.setLayout(line_layout)
        layout.addWidget(line_group)
        
        # Bar Properties Settings
        bar_group = QGroupBox("Bar Properties")
        bar_layout = QGridLayout()
        
        # Bar width scale (0.30x - 1.20x of neighbor gap)
        bar_layout.addWidget(QLabel("Bar Width Scale:"), 0, 0)
        self.bar_width_scale_spin = QDoubleSpinBox()
        self.bar_width_scale_spin.setDecimals(2)
        self.bar_width_scale_spin.setRange(self.settings.MIN_BAR_WIDTH_SCALE, self.settings.MAX_BAR_WIDTH_SCALE)
        self.bar_width_scale_spin.setSingleStep(0.05)
        self.bar_width_scale_spin.setSuffix(" ×")
        
        self.bar_width_scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.bar_width_scale_slider.setRange(int(self.settings.MIN_BAR_WIDTH_SCALE * 100), int(self.settings.MAX_BAR_WIDTH_SCALE * 100))
        self.bar_width_scale_slider.setSingleStep(5)
        
        bar_layout.addWidget(self.bar_width_scale_spin, 0, 1)
        bar_layout.addWidget(self.bar_width_scale_slider, 0, 2)
        bar_group.setLayout(bar_layout)
        layout.addWidget(bar_group)
        
        # Preview text
        preview_group = QGroupBox("Font Preview")
        preview_layout = QVBoxLayout()
        
        self.axis_preview = QLabel("Axis Label Preview")
        self.axis_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.tick_preview = QLabel("Tick Label Preview (0, 10, 20, 30)")
        self.tick_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        preview_layout.addWidget(self.axis_preview)
        preview_layout.addWidget(self.tick_preview)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.reset_btn = QPushButton("Reset to Defaults")
        
        button_layout.addWidget(self.reset_btn)
        button_layout.addStretch()
        
        # Add note about real-time application
        note_label = QLabel("Changes are applied in real-time")
        note_label.setStyleSheet("QLabel { color: #666; font-style: italic; }")
        button_layout.addWidget(note_label)
        
        layout.addLayout(button_layout)
        
        # Set dialog size
        self.setMinimumWidth(500)
        
    def _connect_signals(self):
        """Connect signals for real-time updates."""
        # Connect spin boxes and sliders
        self.axis_size_spin.valueChanged.connect(self.axis_size_slider.setValue)
        self.axis_size_slider.valueChanged.connect(self.axis_size_spin.setValue)
        self.axis_size_spin.valueChanged.connect(self._on_axis_size_changed)
        
        self.tick_size_spin.valueChanged.connect(self.tick_size_slider.setValue)
        self.tick_size_slider.valueChanged.connect(self.tick_size_spin.setValue)
        self.tick_size_spin.valueChanged.connect(self._on_tick_size_changed)
        
        self.line_thickness_spin.valueChanged.connect(self.line_thickness_slider.setValue)
        self.line_thickness_slider.valueChanged.connect(self.line_thickness_spin.setValue)
        self.line_thickness_spin.valueChanged.connect(self._on_line_thickness_changed)
        
        # Bar width scale connections
        self.bar_width_scale_spin.valueChanged.connect(lambda v: self.bar_width_scale_slider.setValue(int(v * 100)))
        self.bar_width_scale_slider.valueChanged.connect(lambda v: self.bar_width_scale_spin.setValue(v / 100.0))
        self.bar_width_scale_spin.valueChanged.connect(self._on_bar_width_scale_changed)
        
        # Connect preset combo
        self.preset_combo.currentTextChanged.connect(self._on_preset_changed)
        
        # Connect buttons
        self.reset_btn.clicked.connect(self._on_reset)
        
    def _load_current_settings(self):
        """Load current settings from the singleton."""
        self.axis_size_spin.setValue(self.settings.axis_font_size)
        self.tick_size_spin.setValue(self.settings.tick_font_size)
        self.line_thickness_spin.setValue(int(self.settings.line_thickness * 10))
        
        # Bar settings
        self.bar_width_scale_spin.setValue(self.settings.bar_width_scale)
        self.bar_width_scale_slider.setValue(int(self.settings.bar_width_scale * 100))
        
        self._update_previews()
        
    def _update_previews(self):
        """Update preview labels with current settings."""
        # Update font previews
        axis_font = QFont()
        axis_font.setPointSize(self.axis_size_spin.value())
        axis_font.setBold(True)
        self.axis_preview.setFont(axis_font)
        
        tick_font = QFont()
        tick_font.setPointSize(self.tick_size_spin.value())
        self.tick_preview.setFont(tick_font)
        
        # Update line preview
        thickness = self.line_thickness_spin.value() / 10.0
        line_height = max(1, int(thickness * 2))
        self.line_preview.setStyleSheet(
            f"QLabel {{ background-color: #2196F3; "
            f"min-height: {line_height}px; max-height: {line_height}px; }}"
        )
        
    def _on_axis_size_changed(self, value):
        """Handle axis size change."""
        self.settings.axis_font_size = value
        self._update_previews()
        
    def _on_tick_size_changed(self, value):
        """Handle tick size change."""
        self.settings.tick_font_size = value
        self._update_previews()
        
    def _on_line_thickness_changed(self, value):
        """Handle line thickness change."""
        self.settings.line_thickness = value / 10.0
        self._update_previews()
        
    def _on_preset_changed(self, preset_name):
        """Apply a preset configuration."""
        if preset_name == "Custom":
            return
            
        preset_map = {
            "Nature": "nature",
            "Science": "science",
            "Presentation": "presentation",
            "Poster": "poster"
        }
        
        if preset_name in preset_map:
            self.settings.apply_preset(preset_map[preset_name])
            self._load_current_settings()
            
    def _on_reset(self):
        """Reset all settings to defaults."""
        self.settings.reset_to_defaults()
        self._load_current_settings()
        self.preset_combo.setCurrentText("Custom")

    def _on_bar_width_scale_changed(self, value: float):
        """Handle bar width scale change."""
        self.settings.bar_width_scale = float(value)
        # No specific preview widget for bars; plot will update live via settingsChanged


class FloatingSettingsButton(QPushButton):
    """A floating button to open settings dialog."""
    
    def __init__(self, parent=None):
        super().__init__("Settings", parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Adjust visualization settings for publication standards")