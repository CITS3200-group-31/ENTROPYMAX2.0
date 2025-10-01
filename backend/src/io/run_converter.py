import os
import sys
from convert_csv_to_parquet import convert_csv_to_parquet
from validate_csv_raw import validate_csv_structure
from validate_csv_gps import validate_csv_gps_structure

def validate(csvfilepath, validator):
    #In case of wrong file type during testing
    if not csvfilepath.lower().endswith(".csv"):
        raise ValueError("Input file must be a .csv")
    
    #Validates the csv structures 
    validator(csvfilepath)

def convert(csvfilepath):
    #Changes file type to .parquet so it only needs the path of the csv file as an input
    parquetfilepath = os.path.splitext(csvfilepath)[0] + ".parquet"
    #Calls the function to convert
    convert_csv_to_parquet(csvfilepath, parquetfilepath)
    
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 run_converter.py <csv_file_path1> <csv_file_path2>")
        sys.exit(1)

    try:
        #Checks the first file by validating raw data csv structure
        validate(sys.argv[1], validate_csv_structure)
        
        #Checks the second file by validating gps csv structure
        validate(sys.argv[2], validate_csv_gps_structure)
        convert(sys.argv[2])
        
    except Exception as e:
        print(f"Error during processing: {e}")
        sys.exit(1)

