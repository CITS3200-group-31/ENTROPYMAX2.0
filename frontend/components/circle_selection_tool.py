"""
Circle selection tool for selecting multiple markers within a circular area.
"""


class CircleSelectionTool:
    @staticmethod
    def get_circle_selection_html(map_var_name="map", position="topleft", top_offset=198):
        """
        Returns the HTML and JavaScript code for circle area selection functionality.
        
        Args:
            map_var_name: The JavaScript variable name for the Leaflet map instance
            position: Position of the toolbar ('topleft', 'topright', 'bottomleft', 'bottomright')
            top_offset: Vertical offset from top (or bottom for bottom positions)
            
        Returns:
            str: Complete HTML and JavaScript code for circle selection functionality
        """
        position_styles = {
            "topleft": f"top: {top_offset}px; left: 10px;",
            "topright": f"top: {top_offset}px; right: 10px;",
            "bottomleft": f"bottom: {top_offset}px; left: 10px;",
            "bottomright": f"bottom: {top_offset}px; right: 10px;"
        }
        
        pos_style = position_styles.get(position, position_styles["topleft"])
        
        return f"""
        <style>
        .circle-selection-toolbar {{
            position: absolute;
            {pos_style}
            z-index: 1000;
            pointer-events: auto;
        }}
        .circle-selection-toolbar .leaflet-draw-section {{
            position: relative;
            display: block;
        }}
        .circle-selection-toolbar a {{
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
        .circle-selection-toolbar a:hover {{
            background-color: #f4f4f4;
        }}
        .circle-selection-toolbar .circle-select-active {{
            background-color: #a0c5e8;
            border-color: #58a1db;
        }}
        .circle-selection-toolbar .circle-select-active:hover {{
            background-color: #8fb8dc;
        }}
        .circle-selection-toolbar .leaflet-draw-draw-circle {{
            background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="8"></circle><circle cx="12" cy="12" r="1" fill="currentColor"></circle></svg>');
            background-position: 4px 4px;
            background-repeat: no-repeat;
            background-size: 18px 18px;
        }}
        .circle-selection-toolbar .leaflet-draw-clear-circle {{
            background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="8" y1="12" x2="16" y2="12"></line></svg>');
            background-position: 4px 4px;
            background-repeat: no-repeat;
            background-size: 18px 18px;
        }}
        .selection-circle {{
            fill: rgba(33, 150, 243, 0.2);
            stroke: #2196F3;
            stroke-width: 2;
            stroke-dasharray: 5, 5;
        }}
        .selection-info {{
            font-family: Arial, sans-serif;
            font-size: 12px;
            font-weight: bold;
            padding: 4px 8px;
            background: rgba(255, 255, 255, 0.95);
            border: 2px solid #2196F3;
            border-radius: 4px;
            color: #2196F3;
        }}
        </style>
        
        <div class="circle-selection-toolbar leaflet-bar leaflet-control">
            <div class="leaflet-draw-section">
                <a id="circle-select-btn" 
                   class="leaflet-draw-draw-circle" 
                   href="#" 
                   title="Select points within a circular area">
                </a>
                <a id="circle-clear-btn" 
                   class="leaflet-draw-clear-circle" 
                   href="#" 
                   title="Clear circle selection">
                </a>
            </div>
        </div>

        <script>
        (function() {{
            // Wait for map to be available
            function initCircleSelectionTool() {{
                var mapInstance = window.{map_var_name};
                
                if (!mapInstance) {{
                    // Try to find map instance dynamically
                    var mapKeys = Object.keys(window).filter(key => key.startsWith('map_'));
                    if (mapKeys.length > 0) {{
                        mapInstance = window[mapKeys[0]];
                    }}
                }}
                
                if (!mapInstance) {{
                    console.warn('Map instance not found for circle selection tool, retrying...');
                    setTimeout(initCircleSelectionTool, 500);
                    return;
                }}
                
                console.log('Circle selection tool initialized');
                
                var isCircleSelecting = false;
                var selectionCircle = null;
                var centerPoint = null;
                var isDrawingCircle = false;
                var altPressed = false;
                var selectButton = document.getElementById('circle-select-btn');
                var clearButton = document.getElementById('circle-clear-btn');
                
                if (!selectButton || !clearButton) {{
                    console.error('Circle selection buttons not found');
                    return;
                }}
                
                // Initialize global flag if not exists
                if (typeof window.isCircleSelectionActive === 'undefined') {{
                    window.isCircleSelectionActive = false;
                }}
                
                // Track Alt/Option key state (Alt on Windows/Linux, Option on macOS)
                document.addEventListener('keydown', function(e) {{
                    // Check for Alt key or Option key (altKey property works on all platforms)
                    if ((e.key === 'Alt' || e.altKey) && isCircleSelecting) {{
                        altPressed = true;
                        mapInstance.getContainer().style.cursor = 'crosshair';
                        e.preventDefault(); // Prevent default Alt/Option behavior
                    }}
                }});
                
                document.addEventListener('keyup', function(e) {{
                    // Check for Alt key or when altKey is released
                    if (e.key === 'Alt' || !e.altKey) {{
                        altPressed = false;
                        if (isCircleSelecting && !isDrawingCircle) {{
                            mapInstance.getContainer().style.cursor = 'default';
                        }}
                    }}
                }});
                
                // Select button click handler
                selectButton.addEventListener('click', function(e) {{
                    e.preventDefault();
                    isCircleSelecting = !isCircleSelecting;
                    
                    // Set global flag
                    window.isCircleSelectionActive = isCircleSelecting;
                    
                    if (isCircleSelecting) {{
                        this.className = this.className + ' circle-select-active';
                        mapInstance.getContainer().style.cursor = 'default';
                        // Show hint to user (detect platform for proper key name)
                        var hint = L.control({{position: 'topright'}});
                        hint.onAdd = function() {{
                            var div = L.DomUtil.create('div', 'circle-hint');
                            // Check if Mac for proper key name
                            var isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
                            var keyName = isMac ? 'Option (⌥)' : 'Alt';
                            div.innerHTML = '<div style="background: white; padding: 8px; border: 2px solid #2196F3; border-radius: 4px; font-weight: bold; color: #2196F3;">Hold ' + keyName + ' + Drag to select area</div>';
                            return div;
                        }};
                        hint.addTo(mapInstance);
                        window.circleHintControl = hint;
                        var isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
                        var keyInstruction = isMac ? 'Option (⌥)' : 'Alt';
                        console.log('Circle selection mode activated - Hold ' + keyInstruction + ' and drag to draw selection circle');
                    }} else {{
                        this.className = this.className.replace(' circle-select-active', '');
                        mapInstance.getContainer().style.cursor = '';
                        centerPoint = null;
                        isDrawingCircle = false;
                        altPressed = false;
                        if (selectionCircle) {{
                            mapInstance.removeLayer(selectionCircle);
                            selectionCircle = null;
                        }}
                        if (window.circleHintControl) {{
                            mapInstance.removeControl(window.circleHintControl);
                            window.circleHintControl = null;
                        }}
                        console.log('Circle selection mode deactivated');
                    }}
                }});
                
                // Clear button click handler
                clearButton.addEventListener('click', function(e) {{
                    e.preventDefault();
                    if (selectionCircle) {{
                        mapInstance.removeLayer(selectionCircle);
                        selectionCircle = null;
                    }}
                    isCircleSelecting = false;
                    isDrawingCircle = false;
                    altPressed = false;
                    window.isCircleSelectionActive = false;
                    selectButton.className = selectButton.className.replace(' circle-select-active', '');
                    mapInstance.getContainer().style.cursor = '';
                    centerPoint = null;
                    if (window.circleHintControl) {{
                        mapInstance.removeControl(window.circleHintControl);
                        window.circleHintControl = null;
                    }}
                    
                    // Clean up any lingering marker styles
                    document.querySelectorAll('.custom-marker').forEach(function(marker) {{
                        // Remove any inline styles that might have been added
                        if (marker.style.border && marker.style.border.includes('#2196F3')) {{
                            marker.style.border = '';
                        }}
                        if (marker.style.boxShadow && marker.style.boxShadow.includes('#2196F3')) {{
                            marker.style.boxShadow = '';
                        }}
                    }});
                    
                    console.log('Circle selection cleared');
                }});
                
                // Mouse down handler - only works when Alt/Option is pressed
                mapInstance.on('mousedown', function(e) {{
                    // Also check e.originalEvent.altKey for immediate response
                    if (!isCircleSelecting || (!altPressed && !e.originalEvent.altKey)) return;
                    
                    // Prevent normal map dragging
                    e.originalEvent.preventDefault();
                    e.originalEvent.stopPropagation();
                    
                    isDrawingCircle = true;
                    centerPoint = e.latlng;
                    mapInstance.dragging.disable();
                    
                    // Create initial circle with 0 radius
                    if (selectionCircle) {{
                        mapInstance.removeLayer(selectionCircle);
                    }}
                    
                    selectionCircle = L.circle(centerPoint, {{
                        radius: 0,
                        color: '#2196F3',
                        weight: 2,
                        opacity: 0.8,
                        fillColor: '#2196F3',
                        fillOpacity: 0.2,
                        dashArray: '5, 5',
                        className: 'selection-circle'
                    }}).addTo(mapInstance);
                    
                    console.log('Circle center set at', centerPoint.lat, centerPoint.lng);
                }});
                
                // Mouse move handler for adjusting radius
                mapInstance.on('mousemove', function(e) {{
                    if (!isDrawingCircle || !centerPoint || !selectionCircle) return;
                    
                    // Calculate radius based on distance from center
                    var radius = centerPoint.distanceTo(e.latlng);
                    selectionCircle.setRadius(radius);
                    
                    // Count markers within current radius
                    var count = 0;
                    document.querySelectorAll('.custom-marker').forEach(function(marker) {{
                        var lat = parseFloat(marker.dataset.lat);
                        var lon = parseFloat(marker.dataset.lon);
                        var markerLatLng = L.latLng(lat, lon);
                        if (centerPoint.distanceTo(markerLatLng) <= radius) {{
                            count++;
                        }}
                    }});
                    
                    // Update tooltip with radius and count
                    var radiusText = radius < 1000 ? 
                        Math.round(radius) + ' m' : 
                        (radius / 1000).toFixed(2) + ' km';
                    
                    selectionCircle.unbindTooltip();
                    selectionCircle.bindTooltip('Radius: ' + radiusText + ' | Points: ' + count, {{
                        permanent: true,
                        direction: 'top',
                        className: 'selection-info'
                    }}).openTooltip();
                }});
                
                // Mouse up handler for finalizing selection
                mapInstance.on('mouseup', function(e) {{
                    if (!isDrawingCircle || !centerPoint || !selectionCircle) return;
                    
                    // Re-enable map dragging
                    mapInstance.dragging.enable();
                    isDrawingCircle = false;
                    
                    // Find all markers within the circle
                    var center = selectionCircle.getLatLng();
                    var radius = selectionCircle.getRadius();
                    
                    var selectedMarkers = [];
                    document.querySelectorAll('.custom-marker').forEach(function(marker) {{
                        var lat = parseFloat(marker.dataset.lat);
                        var lon = parseFloat(marker.dataset.lon);
                        var name = marker.dataset.sampleName;
                        
                        var markerLatLng = L.latLng(lat, lon);
                        var distance = center.distanceTo(markerLatLng);
                        
                        if (distance <= radius) {{
                            selectedMarkers.push(name);
                            // Don't directly modify marker styles - let the selection system handle it
                        }}
                    }});
                    
                    // Send selection to Python via bridge
                    if (window.mapBridge && selectedMarkers.length > 0) {{
                        window.mapBridge.onBoxSelection(JSON.stringify(selectedMarkers));
                        console.log('Selected', selectedMarkers.length, 'markers within circle');
                    }} else if (selectedMarkers.length === 0) {{
                        console.log('No markers found within circle');
                    }}
                    
                    // Update visual feedback
                    var infoText = 'Selected: ' + selectedMarkers.length + ' points';
                    selectionCircle.bindTooltip(infoText, {{
                        permanent: true,
                        direction: 'center',
                        className: 'selection-info'
                    }}).openTooltip();
                    
                    // Reset for next selection
                    centerPoint = null;
                    mapInstance.getContainer().style.cursor = altPressed ? 'crosshair' : 'default';
                    
                    // Keep circle visible for 3 seconds then fade out
                    setTimeout(function() {{
                        if (selectionCircle) {{
                            selectionCircle.setStyle({{
                                opacity: 0.3,
                                fillOpacity: 0.1
                            }});
                        }}
                    }}, 3000);
                }});
                
                console.log('Circle selection tool fully initialized');
            }}
            
            // Initialize after DOM is ready
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', function() {{
                    setTimeout(initCircleSelectionTool, 1000);
                }});
            }} else {{
                setTimeout(initCircleSelectionTool, 1000);
            }}
        }})();
        </script>
        """