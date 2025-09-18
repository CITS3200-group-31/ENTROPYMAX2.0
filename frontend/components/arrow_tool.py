"""
Custom arrow drawing tool.
"""


class SimpleArrowTool: 
    @staticmethod
    def get_arrow_html(map_var_name="map", position="topleft"):
        """
        Returns the HTML and JavaScript code for arrow drawing functionality.
        Styled to match Leaflet.draw toolbar appearance.
        
        Args:
            map_var_name: The JavaScript variable name for the Leaflet map instance
            position: Position of the toolbar ('topleft', 'topright', 'bottomleft', 'bottomright')
            
        Returns:
            str: Complete HTML and JavaScript code for arrow functionality
        """
        position_styles = {
            "topleft": "top: 90px; left: 10px;",
            "topright": "top: 90px; right: 10px;",
            "bottomleft": "bottom: 50px; left: 10px;",
            "bottomright": "bottom: 10px; right: 10px;"
        }
        
        pos_style = position_styles.get(position, position_styles["topleft"])
        
        return f"""
        <style>
        .leaflet-draw-toolbar {{
            margin-top: 0;
        }}
        .arrow-draw-toolbar {{
            position: absolute;
            {pos_style}
            z-index: 1000;
            pointer-events: auto;
        }}
        .arrow-draw-toolbar .leaflet-draw-section {{
            position: relative;
            display: block;
        }}
        .arrow-draw-toolbar a {{
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
        }}
        .arrow-draw-toolbar a:hover {{
            background-color: #f4f4f4;
        }}
        .arrow-draw-toolbar .arrow-draw-active {{
            background-color: #a0c5e8;
            border-color: #58a1db;
        }}
        .arrow-draw-toolbar .arrow-draw-active:hover {{
            background-color: #8fb8dc;
        }}
        .arrow-draw-toolbar .leaflet-draw-draw-arrow {{
            background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12,5 19,12 12,19"></polyline></svg>');
            background-position: 4px 4px;
            background-repeat: no-repeat;
            background-size: 18px 18px;
        }}
        .arrow-draw-toolbar .leaflet-draw-draw-clear {{
            background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3,6 5,6 21,6"></polyline><path d="m19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>');
            background-position: 4px 4px;
            background-repeat: no-repeat;
            background-size: 18px 18px;
        }}
        </style>
        
        <div class="arrow-draw-toolbar leaflet-bar leaflet-control">
            <div class="leaflet-draw-section">
                <a id="arrow-draw-btn" 
                   class="leaflet-draw-draw-arrow" 
                   href="#" 
                   title="Draw arrows between points">
                </a>
                <a id="arrow-clear-btn" 
                   class="leaflet-draw-draw-clear" 
                   href="#" 
                   title="Clear all arrows">
                </a>
            </div>
        </div>

        <script>
        (function() {{
            // Wait for map to be available
            function initArrowTool() {{
                var mapInstance = window.{map_var_name};
                
                if (!mapInstance) {{
                    // Try to find map instance dynamically
                    var mapKeys = Object.keys(window).filter(key => key.startsWith('map_'));
                    if (mapKeys.length > 0) {{
                        mapInstance = window[mapKeys[0]];
                    }}
                }}
                
                if (!mapInstance) {{
                    console.warn('Map instance not found, retrying...');
                    setTimeout(initArrowTool, 500);
                    return;
                }}
                
                console.log('Arrow tool initialized with map:', mapInstance);
                
                var isDrawingArrow = false;
                var arrowLayer = L.layerGroup().addTo(mapInstance);
                var startPoint = null;
                var previewLine = null;
                var drawButton = document.getElementById('arrow-draw-btn');
                var clearButton = document.getElementById('arrow-clear-btn');
                
                if (!drawButton || !clearButton) {{
                    console.error('Arrow tool buttons not found');
                    return;
                }}
                
                // Initialize global flag if not exists
                if (typeof window.isArrowModeActive === 'undefined') {{
                    window.isArrowModeActive = false;
                }}
                
                // Draw button click handler
                drawButton.addEventListener('click', function(e) {{
                    e.preventDefault();
                    isDrawingArrow = !isDrawingArrow;
                    
                    // Set global flag to prevent marker selection
                    window.isArrowModeActive = isDrawingArrow;
                    
                    if (isDrawingArrow) {{
                        this.className = this.className + ' arrow-draw-active';
                        mapInstance.getContainer().style.cursor = 'crosshair';
                        console.log('Arrow drawing mode activated');
                    }} else {{
                        this.className = this.className.replace(' arrow-draw-active', '');
                        mapInstance.getContainer().style.cursor = '';
                        startPoint = null;
                        if (previewLine) {{
                            mapInstance.removeLayer(previewLine);
                            previewLine = null;
                        }}
                        console.log('Arrow drawing mode deactivated');
                    }}
                }});
                
                // Clear button click handler
                clearButton.addEventListener('click', function(e) {{
                    e.preventDefault();
                    arrowLayer.clearLayers();
                    isDrawingArrow = false;
                    window.isArrowModeActive = false;
                    drawButton.className = drawButton.className.replace(' arrow-draw-active', '');
                    mapInstance.getContainer().style.cursor = '';
                    startPoint = null;
                    if (previewLine) {{
                        mapInstance.removeLayer(previewLine);
                        previewLine = null;
                    }}
                    console.log('All arrows cleared');
                }});
                
                // Map click handler
                mapInstance.on('click', function(e) {{
                    if (!isDrawingArrow) return;
                    
                    e.originalEvent.stopPropagation();
                    
                    if (!startPoint) {{
                        // First click - set start point
                        startPoint = e.latlng;
                        console.log('Arrow start point set:', startPoint);
                    }} else {{
                        // Second click - create arrow
                        createArrow(startPoint, e.latlng);
                        startPoint = null;
                        if (previewLine) {{
                            mapInstance.removeLayer(previewLine);
                            previewLine = null;
                        }}
                        console.log('Arrow created');
                    }}
                }});
                
                // Mouse move handler for preview
                mapInstance.on('mousemove', function(e) {{
                    if (!isDrawingArrow || !startPoint) return;
                    
                    if (previewLine) {{
                        mapInstance.removeLayer(previewLine);
                    }}
                    
                    previewLine = L.polyline([startPoint, e.latlng], {{
                        color: '#b30404',
                        weight: 2,
                        opacity: 0.6,
                        dashArray: '8, 8'
                    }});
                    mapInstance.addLayer(previewLine);
                }});
                
                // Create arrow function
                function createArrow(start, end) {{
                    var arrowGroup = L.layerGroup();
                    
                    // Main arrow line
                    var mainLine = L.polyline([start, end], {{
                        color: '#b30404',
                        weight: 4,
                        opacity: 0.8
                    }});
                    
                    // Calculate arrow head
                    var startPixel = mapInstance.latLngToContainerPoint(start);
                    var endPixel = mapInstance.latLngToContainerPoint(end);
                    
                    var dx = endPixel.x - startPixel.x;
                    var dy = endPixel.y - startPixel.y;
                    var angle = Math.atan2(dy, dx);
                    
                    var headLength = 20;
                    var headAngle = Math.PI / 6; // 30 degrees
                    
                    // Calculate arrow head points
                    var head1Pixel = L.point(
                        endPixel.x - headLength * Math.cos(angle - headAngle),
                        endPixel.y - headLength * Math.sin(angle - headAngle)
                    );
                    var head2Pixel = L.point(
                        endPixel.x - headLength * Math.cos(angle + headAngle),
                        endPixel.y - headLength * Math.sin(angle + headAngle)
                    );
                    
                    var head1LatLng = mapInstance.containerPointToLatLng(head1Pixel);
                    var head2LatLng = mapInstance.containerPointToLatLng(head2Pixel);
                    
                    // Arrow head lines
                    var headLine1 = L.polyline([end, head1LatLng], {{
                        color: '#b30404',
                        weight: 4,
                        opacity: 0.8
                    }});
                    var headLine2 = L.polyline([end, head2LatLng], {{
                        color: '#b30404',
                        weight: 4,
                        opacity: 0.8
                    }});
                    
                    // Add info popup
                    var distance = (start.distanceTo(end) / 1000).toFixed(2);
                    var popupContent = `
                        <div style="font-family: Arial, sans-serif; min-width: 200px;">
                            <h4 style="margin: 0 0 8px 0; color: #b30404;">Arrow Information</h4>
                            <b>Start:</b> ${{start.lat.toFixed(6)}}, ${{start.lng.toFixed(6)}}<br>
                            <b>End:</b> ${{end.lat.toFixed(6)}}, ${{end.lng.toFixed(6)}}<br>
                            <b>Distance:</b> ${{distance}} km
                        </div>
                    `;
                    
                    mainLine.bindPopup(popupContent);
                    
                    // Add all parts to group
                    arrowGroup.addLayer(mainLine);
                    arrowGroup.addLayer(headLine1);
                    arrowGroup.addLayer(headLine2);
                    
                    // Add to main layer
                    arrowLayer.addLayer(arrowGroup);
                }}
                
                console.log('Arrow tool fully initialized');
            }}
            
            // Initialize after DOM is ready
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', function() {{
                    setTimeout(initArrowTool, 1000);
                }});
            }} else {{
                setTimeout(initArrowTool, 1000);
            }}
        }})();
        </script>
        """


def add_arrow_tool_to_map(folium_map, map_var_name=None, position="topleft"):
    """
    Add arrow drawing tool to a Folium map with Leaflet.draw compatible styling.
    
    Args:
        folium_map: Folium Map object
        map_var_name: Optional map variable name (auto-detected if None)
        position: Position of the toolbar ('topleft', 'topright', 'bottomleft', 'bottomright')
        
    Returns:
        Folium Map object with arrow tool added
    """
    try:
        import folium
        
        # Try to get the map variable name automatically
        if map_var_name is None:
            map_var_name = folium_map.get_name()
        
        # Create arrow tool HTML with specified position
        arrow_html = SimpleArrowTool.get_arrow_html(map_var_name, position)
        
        # Add to map
        folium_map.get_root().html.add_child(folium.Element(arrow_html))
        
        return folium_map
        
    except ImportError:
        print("Warning: Folium not available, arrow tool cannot be added")
        return folium_map
    except Exception as e:
        print(f"Warning: Could not add arrow tool: {e}")
        return folium_map


# Example usage
if __name__ == "__main__":
    print("SimpleArrowTool utility module")
    print("Use add_arrow_tool_to_map() to add arrow functionality to your Folium maps")