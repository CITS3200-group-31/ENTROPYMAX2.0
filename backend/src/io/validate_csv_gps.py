import pandas as pd

def validate_csv_gps_structure(filepath):
    # The expected column names (order-insensitive), allowing 'Sample Name' synonym
    expected_columns = {"Sample", "Latitude", "Longitude"}

    try:
        #Loads the entire CSV
        df = pd.read_csv(filepath)
        df.columns = [col.strip() for col in df.columns]  # Strip spaces from headers
        # Allow 'Sample Name' as synonym for 'Sample'
        if "Sample" not in df.columns and "Sample Name" in df.columns:
            df = df.rename(columns={"Sample Name": "Sample"})

        # Checks for required columns (order-insensitive)
        if not expected_columns.issubset(set(df.columns)):
            raise ValueError(f"CSV must contain columns {sorted(expected_columns)}, but found: {df.columns.tolist()}")

        #Checks for missing values in the Sample column
        if df["Sample"].isnull().any():
            raise ValueError("Missing values found in 'Sample' column.")

        #Checks that the Latitude and Longitude are numeric values
        for col in ["Latitude", "Longitude"]:
            if not pd.api.types.is_numeric_dtype(df[col]):
                raise ValueError(f"Column '{col}' must be numeric.")

        #Checks that the lat/lon are in the ranges
        if not df["Latitude"].between(-90, 90).all():
            raise ValueError("One or more 'Latitude' values are outside the valid range (-90 to 90).")

        if not df["Longitude"].between(-180, 180).all():
            raise ValueError("One or more 'Longitude' values are outside the valid range (-180 to 180).")

        return True

    except Exception as e:
        raise ValueError(f"GPS CSV validation failed: {e}")
