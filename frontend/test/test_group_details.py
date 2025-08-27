#!/usr/bin/env python3
"""
Test script for verifying the Show Group Details functionality.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from components.group_detail_popup import GroupDetailPopup

def test_group_details():
    """Test the group detail popup functionality."""
    app = QApplication(sys.argv)
    
    # Create the popup manager
    popup_manager = GroupDetailPopup()
    
    # Set the path to the sample data
    csv_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'test', 'data', 'Input file GP for Entropy 20240910.csv'
    )
    
    print(f"Testing with CSV file: {csv_path}")
    print(f"File exists: {os.path.exists(csv_path)}")
    
    try:
        # Load and show popups with 5 groups (default)
        popup_manager.load_and_show_popups(csv_path, k_value=5)
        print("✓ Successfully created group detail popups")
        print("✓ Close the popup windows to exit the test")
        
        # Run the application
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    test_group_details()
