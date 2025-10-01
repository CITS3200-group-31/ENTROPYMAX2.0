#!/usr/bin/env python3
"""
Test script for logarithmic X-axis in grain size distribution graphs.
Run in conda environment with: python test_log_axis.py
"""

import sys
import os
import numpy as np
import csv
from PyQt6.QtWidgets import QApplication

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.group_detail_popup import GroupDetailPopup

def create_test_data():
    """Create test CSV with grain sizes in logarithmic scale."""
    test_file = 'test_grain_data.csv'
    
    # Grain sizes from 0.1 to 1000 μm (logarithmic scale)
    grain_sizes = [0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
    header = ['Sample'] + [f'{size}' for size in grain_sizes]
    
    # Generate sample data with different distribution patterns
    samples = []
    for i in range(15):
        # Create different distribution patterns
        if i % 3 == 0:
            # Fine-grained distribution
            values = [100 * np.exp(-((np.log10(size) - np.log10(1))**2) / 0.5) for size in grain_sizes]
        elif i % 3 == 1:
            # Coarse-grained distribution  
            values = [100 * np.exp(-((np.log10(size) - np.log10(100))**2) / 0.5) for size in grain_sizes]
        else:
            # Bimodal distribution
            values = [50 * np.exp(-((np.log10(size) - np.log10(5))**2) / 0.3) + 
                     50 * np.exp(-((np.log10(size) - np.log10(200))**2) / 0.3) for size in grain_sizes]
        
        samples.append([f'Sample_{i+1:03d}'] + [f'{v:.2f}' for v in values])
    
    # Write to CSV
    with open(test_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(samples)
    
    print(f"✓ Created test data file: {test_file}")
    return test_file

def main():
    """Main test function."""
    print("=" * 60)
    print("Testing Logarithmic X-axis for Grain Size Distribution")
    print("=" * 60)
    
    # Create QApplication
    app = QApplication(sys.argv)
    
    # Create test data
    test_file = create_test_data()
    
    # Create and configure popup manager
    popup_manager = GroupDetailPopup()
    
    try:
        # Load and show popups with test data
        popup_manager.load_and_show_popups(
            csv_path=test_file,
            k_value=3,  # 3 groups for testing
            x_unit='μm',
            y_unit='%'
        )
        
        print("\n✓ Group detail windows opened successfully")
        print("\nFeatures to test:")
        print("1. X-axis should display in logarithmic scale by default")
        print("2. Click 'Switch to Linear' button to toggle scale")
        print("3. Tick labels should adjust appropriately for each scale")
        print("4. Hover over lines to see sample names")
        print("5. Click on lines to select samples")
        print("\nPress Ctrl+C to exit...")
        
        # Run the application
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"\n✓ Cleaned up test file: {test_file}")

if __name__ == '__main__':
    main()