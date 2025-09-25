"""
Handles interactive map display with sample selection and arrow drawing functionality.
"""

import os
import folium
from statistics import mean
from PyQt6.QtCore import QUrl
from PyQt6.QtCore import pyqtSignal as Signal
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWidgets import QWidget, QVBoxLayout


class MapWidget(QWidget):
    """Interactive map widget with sample selection and arrow drawing capability."""
    
    # Signal emitted when samples are selected/deselected
    selectionChanged = Signal(list)  # list of selected sample names
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_samples = []
        self.markers_data = []
        self._setup_ui()
        
    def _setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Create web view for map
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(300)
        
        # Configure web engine settings
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        
        layout.addWidget(self.web_view)
        
    def render_map(self, markers_data, center=None, zoom=None):
        """
        Render the interactive map with markers and arrow drawing capability.
        
        Args:
            markers_data: List of dictionaries with 'lat', 'lon', 'name', 'group' keys
            center: Optional tuple (lat, lon) to center the map
            zoom: Optional zoom level
        """
        self.markers_data = markers_data
        
        if center is None:
            if not markers_data:
                center = (-25.0, 133.0)  # Australia center
            else:
                center = (
                    mean([m["lat"] for m in markers_data]), 
                    mean([m["lon"] for m in markers_data])
                )
        
        if zoom is None:
            zoom = 5
        
        # Create map with satellite imagery only, disable zoom controls
        m = folium.Map(
            location=center, 
            zoom_start=zoom, 
            zoom_control=False,  # Disable zoom in/out buttons
            control_scale=True, 
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            width='100%',
            height='100%'
        )
        
        # Simplified color palette - using blue tones for unselected, green for selected
        colors = ['lightblue', 'blue', 'darkblue']
        
        # Add markers
        for mk in markers_data:
            group = mk.get('group', 1)
            color = colors[group % len(colors)]
            
            # Check if this sample is selected
            if mk['name'] in self.selected_samples:
                icon = folium.Icon(color='darkgreen', icon='ok-sign')
            else:
                icon = folium.Icon(color=color, icon='info-sign')
            
            # Create popup with better formatting
            popup_html = f"""
            <div style="font-family: Arial, sans-serif; min-width: 150px;">
                <b>{mk.get('name', 'Unknown')}</b><br>
                Location: ({mk['lat']:.4f}, {mk['lon']:.4f})<br>
                Group: {mk.get('group', 'N/A')}<br>
                <div id="status_{mk.get('name', '').replace(' ', '_')}">
                    {'✓ Selected' if mk['name'] in self.selected_samples else 'Click marker to select'}
                </div>
            </div>
            """
            
            # Add marker with tooltip
            marker = folium.Marker(
                location=(mk['lat'], mk['lon']),
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{mk.get('name', 'Sample')} (Group {group})",
                icon=icon
            )
            
            marker.add_to(m)
        
        # Add arrow drawing capability using optimized tool
        self._add_arrow_tool(m)
        
        # Save and load HTML
        html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'map.html'))
        m.save(html_path)
        self.web_view.setUrl(QUrl.fromLocalFile(html_path))
        
    def toggle_sample_selection(self, sample_name):
        """Toggle selection of a sample."""
        if sample_name in self.selected_samples:
            self.selected_samples.remove(sample_name)
        else:
            self.selected_samples.append(sample_name)
        
        self.selectionChanged.emit(self.selected_samples)
        # Re-render map to update marker colors
        self.render_map(self.markers_data)
        
    def clear_selection(self):
        """Clear all selected samples."""
        self.selected_samples = []
        self.selectionChanged.emit(self.selected_samples)
        self.render_map(self.markers_data)
        
    def get_selected_samples(self):
        """Return list of selected sample names."""
        return self.selected_samples
    
    def zoom_to_location(self, lat, lon, sample_name=None):
        """
        Zoom the map to a specific location.
        
        Args:
            lat: Latitude
            lon: Longitude
            sample_name: Optional sample name to highlight
        """
        # Re-render map centered on the location
        self.render_map(self.markers_data, center=(lat, lon), zoom=10)
        
    def update_selected_markers(self, selected_names):
        """
        Update the visual state of markers based on selection.
        
        Args:
            selected_names: List of selected sample names
        """
        self.selected_samples = selected_names
        # Re-render to update marker colors
        self.render_map(self.markers_data)
        
    def _add_arrow_tool(self, folium_map):
        """
        Add arrow drawing functionality to the map.
        """
        try:
            from .arrow_tool import SimpleArrowTool
            map_var_name = folium_map.get_name()
            # Position it at top-left
            arrow_html = SimpleArrowTool.get_arrow_html(map_var_name, position="topleft")
            folium_map.get_root().html.add_child(folium.Element(arrow_html))
        except Exception as e:
            print(f"Warning: Could not add arrow tool: {e}")
