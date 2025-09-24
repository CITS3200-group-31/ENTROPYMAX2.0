import sys
import os

# Add backend path to sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'src', 'io')
if backend_path not in sys.path:
    sys.path.append(backend_path)

from validate_csv_raw import validate_csv_structure

def test_validation():
    """Test the CSV validation function."""
    csv_path = "../data/raw/sample_input.csv"
    
    try:
        result = validate_csv_structure(csv_path)
        print("Validation PASSED!")
        print(f"Result: {result}")
    except Exception as e:
        print("Validation FAILED!")
        print(f"Error: {e}")

if __name__ == "__main__":
    test_validation()