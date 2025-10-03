"""
Simple CSV validation for EntropyMax input files.
"""

import csv
from pathlib import Path
from typing import Tuple


def validate_raw_data_csv(file_path: str) -> Tuple[bool, str]:
    """
    Validate raw data CSV file format.
    
    Expected format:
    - First column: Sample Name
    - Remaining columns: Numeric grain size bins
    - At least 2 rows (header + data)
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        (valid: bool, error_message: str)
    """
    try:
        # Check file exists
        if not Path(file_path).exists():
            return False, f"File not found: {file_path}"
        
        # Check file extension
        if not file_path.lower().endswith('.csv'):
            return False, "File must have .csv extension"
        
        # Read and validate structure
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            
            # Check header
            try:
                header = next(reader)
            except StopIteration:
                return False, "File is empty"
            
            if len(header) < 2:
                return False, "File must have at least 2 columns (Sample Name + grain sizes)"
            
            # Check first column name
            first_col = header[0].strip().lower()
            if 'sample' not in first_col and 'name' not in first_col:
                return False, f"First column should be 'Sample Name' or similar, found: '{header[0]}'"
            
            # Check if there's at least one numeric column
            numeric_found = False
            for col in header[1:]:
                try:
                    float(col.strip())
                    numeric_found = True
                    break
                except (ValueError, AttributeError):
                    pass
            
            if not numeric_found:
                return False, "No numeric grain size columns found in header"
            
            # Check at least one data row exists
            try:
                first_row = next(reader)
                if len(first_row) < 2:
                    return False, "Data rows must have at least 2 columns"
                
                # Verify first row has sample name
                if not first_row[0].strip():
                    return False, "Sample name cannot be empty"
                    
            except StopIteration:
                return False, "No data rows found (only header)"
        
        return True, ""
        
    except Exception as e:
        return False, f"Error reading file: {str(e)}"


def validate_gps_csv(file_path: str) -> Tuple[bool, str]:
    """
    Validate GPS coordinates CSV file format.
    
    Expected format:
    - Column 1: Sample Name (or similar)
    - Column 2: Latitude
    - Column 3: Longitude
    - At least 2 rows (header + data)
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        (valid: bool, error_message: str)
    """
    try:
        # Check file exists
        if not Path(file_path).exists():
            return False, f"File not found: {file_path}"
        
        # Check file extension
        if not file_path.lower().endswith('.csv'):
            return False, "File must have .csv extension"
        
        # Read and validate structure
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            
            # Check header
            try:
                header = next(reader)
            except StopIteration:
                return False, "File is empty"
            
            if len(header) < 3:
                return False, "GPS file must have at least 3 columns (Sample Name, Latitude, Longitude)"
            
            # Check column names (case-insensitive)
            header_lower = [col.strip().lower() for col in header]
            
            # Check for sample name column
            sample_col_found = False
            for col in header_lower:
                if 'sample' in col or 'name' in col:
                    sample_col_found = True
                    break
            
            if not sample_col_found:
                return False, "No 'Sample Name' column found in header"
            
            # Check for latitude column
            lat_col_found = any('lat' in col for col in header_lower)
            if not lat_col_found:
                return False, "No 'Latitude' column found in header"
            
            # Check for longitude column
            lon_col_found = any('lon' in col or 'long' in col for col in header_lower)
            if not lon_col_found:
                return False, "No 'Longitude' column found in header"
            
            # Check at least one data row exists
            try:
                first_row = next(reader)
                if len(first_row) < 3:
                    return False, "Data rows must have at least 3 columns"
                
                # Verify sample name
                if not first_row[0].strip():
                    return False, "Sample name cannot be empty"
                
                # Try to parse coordinates (assuming columns 2 and 3 are lat/lon)
                try:
                    float(first_row[1].strip())
                    float(first_row[2].strip())
                except (ValueError, IndexError):
                    return False, "Latitude and Longitude must be numeric values"
                    
            except StopIteration:
                return False, "No data rows found (only header)"
        
        return True, ""
        
    except Exception as e:
        return False, f"Error reading file: {str(e)}"


def quick_check_csv(file_path: str) -> Tuple[bool, str]:
    """
    Quick check if file is readable CSV with at least header and one row.
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        (valid: bool, error_message: str)
    """
    try:
        if not Path(file_path).exists():
            return False, "File not found"
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            first_row = next(reader)
            
            if not header or not first_row:
                return False, "File must have header and data"
            
        return True, ""
        
    except Exception as e:
        return False, str(e)
