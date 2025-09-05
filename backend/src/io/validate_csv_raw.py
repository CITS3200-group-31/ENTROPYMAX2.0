import pandas as pd

def validate_csv_structure(filepath):
    try:
        #Loads the CSV
        df = pd.read_csv(filepath)
        df.columns = [str(col).strip() for col in df.columns]

        #Checks that the first column is 'Sample Name'
        if df.columns[0] != "Sample Name":
            raise ValueError("First column must be 'Sample Name'.")

        #Validates the remaining columns are ascending numeric values
        numeric_headers = df.columns[1:]
        try:
            numeric_values = [float(col) for col in numeric_headers]
        except ValueError:
            raise ValueError("One or more column headers after 'Sample' are not numeric.")

        if numeric_values != sorted(numeric_values):
            raise ValueError("Column headers after 'Sample' are not in ascending order.")

        #Validates the 'Sample' values are non-empty 
        if df['Sample Name'].isnull().any() or (df['Sample Name'].astype(str).str.strip() == '').any():
            raise ValueError("'Sample Name' column contains empty values.")

        #Validates all data columns are numeric and contain no missing values
        data_columns = df.columns[1:]
        for col in data_columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                raise ValueError(f"Column '{col}' contains non-numeric values.")
            if df[col].isnull().any():
                raise ValueError(f"Column '{col}' contains missing values.")

        return True

    except Exception as e:
        raise ValueError(f"CSV validation failed: {e}")
