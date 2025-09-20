import pandas as pd
import sys
import os

# Add backend path to sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'src', 'io')
if backend_path not in sys.path:
    sys.path.append(backend_path)

def debug_csv_headers(filepath):
    """Debug CSV headers to find the problematic column."""
    try:
        # Load the CSV
        df = pd.read_csv(filepath)
        print("Original columns:")
        for i, col in enumerate(df.columns):
            print(f"  {i}: '{col}' (type: {type(col)}, repr: {repr(col)})")
        
        # Strip whitespace from headers
        df.columns = [str(col).strip() for col in df.columns]
        print("\nAfter stripping:")
        for i, col in enumerate(df.columns):
            print(f"  {i}: '{col}' (type: {type(col)}, repr: {repr(col)})")
        
        # Check first column
        print(f"\nFirst column check: '{df.columns[0]}' == 'Sample Name' ? {df.columns[0] == 'Sample Name'}")
        
        # Get numeric headers (after filtering empty ones and unnamed columns)
        numeric_headers = [col for col in df.columns[1:] if col.strip() and not col.startswith('Unnamed:')]
        print(f"\nNumeric headers after filtering ({len(numeric_headers)} total):")
        for i, col in enumerate(numeric_headers):
            print(f"  {i}: '{col}' (type: {type(col)}, repr: {repr(col)})")
        
        # Try to convert each header to float
        print("\nTrying to convert each header to float:")
        problematic_headers = []
        for i, col in enumerate(numeric_headers):
            try:
                float_val = float(col)
                print(f"  {i}: '{col}' -> {float_val} ✓")
            except ValueError as e:
                print(f"  {i}: '{col}' -> ERROR: {e} ✗")
                problematic_headers.append((i, col))
        
        if problematic_headers:
            print(f"\nProblematic headers found: {len(problematic_headers)}")
            for i, col in problematic_headers:
                print(f"  Index {i}: '{col}' (repr: {repr(col)})")
        else:
            print("\nAll headers can be converted to float successfully!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    csv_path = "../data/raw/sample_input.csv"
    debug_csv_headers(csv_path)