"""
Visualization settings configuration for publication standards.
Manages font sizes and line thickness for all visualization windows.
"""

from PyQt6.QtCore import QObject, pyqtSignal as Signal


class VisualizationSettings(QObject):
    """Singleton class for managing visualization settings across all windows."""
    
    # Signals emitted when settings change
    axisFontSizeChanged = Signal(int)
    tickFontSizeChanged = Signal(int)
    lineThicknessChanged = Signal(float)
    settingsChanged = Signal()  # General signal for any change
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        super().__init__()
        
        # Default font sizes (in points)
        self._axis_font_size = 12
        self._tick_font_size = 10
        
        # Default line thickness
        self._line_thickness = 2.0
        
        # Bar properties
        self._bar_width_scale = 0.8  # proportion of neighbor gap used as bar width
        
        # Min and max values for validation
        self.MIN_FONT_SIZE = 6
        self.MAX_FONT_SIZE = 24
        self.MIN_LINE_THICKNESS = 0.5
        self.MAX_LINE_THICKNESS = 10.0
        self.MIN_BAR_WIDTH_SCALE = 0.3
        self.MAX_BAR_WIDTH_SCALE = 1.2
        
        self._initialized = True
    
    @property
    def axis_font_size(self):
        """Get axis label font size."""
        return self._axis_font_size
    
    @axis_font_size.setter
    def axis_font_size(self, value):
        """Set axis label font size."""
        if self.MIN_FONT_SIZE <= value <= self.MAX_FONT_SIZE:
            if self._axis_font_size != value:
                self._axis_font_size = value
                self.axisFontSizeChanged.emit(value)
                self.settingsChanged.emit()
    
    @property
    def tick_font_size(self):
        """Get tick label font size."""
        return self._tick_font_size
    
    @tick_font_size.setter
    def tick_font_size(self, value):
        """Set tick label font size."""
        if self.MIN_FONT_SIZE <= value <= self.MAX_FONT_SIZE:
            if self._tick_font_size != value:
                self._tick_font_size = value
                self.tickFontSizeChanged.emit(value)
                self.settingsChanged.emit()
    
    @property
    def line_thickness(self):
        """Get line thickness."""
        return self._line_thickness
    
    @line_thickness.setter
    def line_thickness(self, value):
        """Set line thickness."""
        if self.MIN_LINE_THICKNESS <= value <= self.MAX_LINE_THICKNESS:
            if self._line_thickness != value:
                self._line_thickness = value
                self.lineThicknessChanged.emit(value)
                self.settingsChanged.emit()
    
    def get_axis_style(self):
        """Get formatted style dict for axis labels."""
        return {
            'color': '#333',
            'font-size': f'{self._axis_font_size}pt',
            'font-weight': 'bold'
        }

    @property
    def bar_width_scale(self) -> float:
        """Get bar width scale (proportion of neighbor gap)."""
        return self._bar_width_scale

    @bar_width_scale.setter
    def bar_width_scale(self, value: float):
        """Set bar width scale with clamping to valid range."""
        if value is None:
            return
        try:
            v = float(value)
        except Exception:
            return
        v = max(self.MIN_BAR_WIDTH_SCALE, min(self.MAX_BAR_WIDTH_SCALE, v))
        if v != self._bar_width_scale:
            self._bar_width_scale = v
            self.settingsChanged.emit()
    
    def get_tick_style(self):
        """Get formatted style dict for tick labels."""
        return {
            'color': '#333',
            'font-size': f'{self._tick_font_size}pt'
        }
    
    def reset_to_defaults(self):
        """Reset all settings to default values."""
        self.axis_font_size = 12
        self.tick_font_size = 10
        self.line_thickness = 2.0
        self.bar_width_scale = 0.8
    
    def apply_preset(self, preset_name):
        """Apply a preset configuration for specific publication standards."""
        presets = {
            'nature': {
                'axis': 9,
                'tick': 8,
                'line': 1.5
            },
            'science': {
                'axis': 10,
                'tick': 9,
                'line': 1.5
            },
            'presentation': {
                'axis': 14,
                'tick': 12,
                'line': 3.0
            },
            'poster': {
                'axis': 16,
                'tick': 14,
                'line': 4.0
            }
        }
        
        if preset_name in presets:
            preset = presets[preset_name]
            self.axis_font_size = preset['axis']
            self.tick_font_size = preset['tick']
            self.line_thickness = preset['line']
