"""
Base classes for creating compatible custom tools.
"""


class LeafletDrawCompatibleTool:
    """
    Base class for creating custom tools.
    """
    
    @staticmethod
    def get_base_css():
        """Returns the base CSS."""
        return """
        <style>
        .custom-draw-toolbar {
            margin-top: 0;
        }
        .custom-draw-toolbar .leaflet-draw-section {
            position: relative;
            display: block;
        }
        .custom-draw-toolbar a {
            background-color: #fff;
            border: 1px solid #ccc;
            width: 26px;
            height: 26px;
            line-height: 24px;
            display: block;
            text-align: center;
            text-decoration: none;
            color: black;
            cursor: pointer;
            box-shadow: 0 1px 5px rgba(0,0,0,0.2);
        }
        .custom-draw-toolbar a:hover {
            background-color: #f4f4f4;
        }
        .custom-draw-toolbar .custom-draw-active {
            background-color: #a0c5e8;
            border-color: #58a1db;
        }
        .custom-draw-toolbar .custom-draw-active:hover {
            background-color: #8fb8dc;
        }
        </style>
        """
    
    @staticmethod
    def get_position_style(position="topleft"):
        """
        Get CSS positioning for toolbar placement.
        
        Args:
            position: 'topleft', 'topright', 'bottomleft', or 'bottomright'
            
        Returns:
            str: CSS positioning style
        """
        position_styles = {
            "topleft": "top: 10px; left: 10px;",
            "topright": "top: 10px; right: 10px;", 
            "bottomleft": "bottom: 10px; left: 10px;",
            "bottomright": "bottom: 10px; right: 10px;"
        }
        return position_styles.get(position, position_styles["topleft"])
    
    @staticmethod
    def create_toolbar_container(toolbar_id, position="topleft", additional_classes=""):
        """
        Create a toolbar container with consistent styling.
        
        Args:
            toolbar_id: Unique ID for the toolbar
            position: Position on the map
            additional_classes: Additional CSS classes
            
        Returns:
            str: HTML for toolbar container
        """
        pos_style = LeafletDrawCompatibleTool.get_position_style(position)
        
        return f"""
        <div id="{toolbar_id}" class="custom-draw-toolbar leaflet-bar leaflet-control {additional_classes}" style="
            position: absolute;
            {pos_style}
            z-index: 1000;
            pointer-events: auto;
        ">
            <div class="leaflet-draw-section">
        """
    
    @staticmethod
    def close_toolbar_container():
        """Close the toolbar container."""
        return """
            </div>
        </div>
        """
    
    @staticmethod
    def create_tool_button(button_id, css_class, title, svg_icon=None):
        """
        Create a tool button with consistent styling.
        
        Args:
            button_id: Unique ID for the button
            css_class: CSS class for the button
            title: Tooltip text
            svg_icon: Optional SVG icon as data URL
            
        Returns:
            str: HTML for the button
        """
        style = ""
        if svg_icon:
            style = f"""style="
                background-image: url('{svg_icon}');
                background-position: 4px 4px;
                background-repeat: no-repeat;
                background-size: 18px 18px;
            \""""
        
        return f"""<a id="{button_id}" 
                   class="{css_class}" 
                   href="#" 
                   title="{title}"
                   {style}>
                </a>"""


class GPSDistanceTool(LeafletDrawCompatibleTool):
    """
    GPS distance measurement tool
    """
    
    @staticmethod
    def get_distance_tool_html(map_var_name="map", position="topleft"):
        """
        Future implementation for GPS distance measurement tool.
        
        Args:
            map_var_name: JavaScript map variable name
            position: Toolbar position
            
        Returns:
            str: HTML and JavaScript for distance tool
        """
        # This will be implemented later when needed
        return """
        """