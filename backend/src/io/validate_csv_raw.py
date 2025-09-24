import pandas as pd


def validate_csv_structure(filepath):
    try:
        # Load CSV and normalize headers
        df = pd.read_csv(filepath)
        df.columns = ["" if pd.isna(col) else str(col).strip() for col in df.columns]

        # Drop any trailing/blank header columns beyond the first, and any pandas 'Unnamed:' spill columns
        keep_cols = [df.columns[0]] + [
            c for c in df.columns[1:]
            if c != "" and not c.lower().startswith("unnamed:")
        ]
        if len(keep_cols) != len(df.columns):
            df = df.loc[:, keep_cols]

        # First column must be exact 'Sample Name'
        if df.columns[0] != "Sample Name":
            raise ValueError("First column must be 'Sample Name'.")

        # Remaining headers must be numeric and strictly ascending
        numeric_headers = df.columns[1:]
        try:
            numeric_values = [float(col) for col in numeric_headers]
        except ValueError:
            raise ValueError("One or more column headers after 'Sample' are not numeric.")

        if numeric_values != sorted(numeric_values):
            raise ValueError("Column headers after 'Sample' are not in ascending order.")

        # 'Sample Name' values must be non-empty
        if df['Sample Name'].isnull().any() or (df['Sample Name'].astype(str).str.strip() == '').any():
            raise ValueError("'Sample Name' column contains empty values.")

        # Data columns must be numeric (missing values allowed; treated as 0 downstream)
        data_columns = df.columns[1:]
        for col in data_columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                raise ValueError(f"Column '{col}' contains non-numeric values.")
            # Allow NaNs here; downstream conversion/processing can fill with 0 as needed

        return True

    except Exception as e:
        raise ValueError(f"CSV validation failed: {e}")
