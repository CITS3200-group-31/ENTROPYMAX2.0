import pandas as pd


def validate_csv_gps_structure(filepath):
    # Accept either 'Sample' or 'Sample Name' as first column; enforce order otherwise
    try:
        df = pd.read_csv(filepath)
        df.columns = [col.strip() for col in df.columns]

        cols = df.columns.tolist()
        # Normalize first column name to 'Sample'
        if len(cols) >= 1 and cols[0] in ("Sample", "Sample Name"):
            if cols[0] != "Sample":
                df = df.rename(columns={cols[0]: "Sample"})
        else:
            raise ValueError("First column must be 'Sample' or 'Sample Name'.")

        # Enforce the remaining two columns are Latitude, Longitude in order
        if df.columns.tolist()[1:] != ["Latitude", "Longitude"]:
            raise ValueError(f"Columns must be ['Sample', 'Latitude', 'Longitude'] in order, but found: {df.columns.tolist()}")

        if df["Sample"].isnull().any():
            raise ValueError("Missing values found in 'Sample' column.")

        for col in ["Latitude", "Longitude"]:
            if not pd.api.types.is_numeric_dtype(df[col]):
                raise ValueError(f"Column '{col}' must be numeric.")

        if not df["Latitude"].between(-90, 90).all():
            raise ValueError("One or more 'Latitude' values are outside the valid range (-90 to 90).")
        if not df["Longitude"].between(-180, 180).all():
            raise ValueError("One or more 'Longitude' values are outside the valid range (-180 to 180).")

        return True

    except Exception as e:
        raise ValueError(f"GPS CSV validation failed: {e}")
