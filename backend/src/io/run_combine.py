import os
import sys
import pandas as pd

def combine_parquet_files(main_parquet_path, gps_parquet_path, output_parquet_path):
    try:
        # Read the main data and GPS data
        main_df = pd.read_parquet(main_parquet_path)
        gps_df = pd.read_parquet(gps_parquet_path)

        #Checks if the files are correct
        if "sample" not in main_df.columns:
            raise ValueError(f"'sample' column not found in main file: {main_parquet_path}")
        if not all(col in gps_df.columns for col in ["sample", "latitude", "longitude"]):
            raise ValueError(f"GPS file must contain 'sample', 'latitude', and 'longitude' columns.")

        #Strips whitespaces from the 'sample' columns
        main_df['sample'] = main_df['sample'].str.strip()
        gps_df['sample'] = gps_df['sample'].str.strip()

        #Merge data based on 'sample'
        combined_df = pd.merge(main_df, gps_df, on="sample", how="left")

        #Save the combined data to new Parquet file
        combined_df.to_parquet(output_parquet_path, index=False)
        print(f"Combined Parquet file saved to: {output_parquet_path}")

    except Exception as e:
        raise RuntimeError(f"Failed to combine Parquet files: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 combine_parquets_by_sample.py <main_parquet_path> <gps_parquet_path> <output_parquet_path>")
        sys.exit(1)

    main_parquet_path = sys.argv[1]
    gps_parquet_path = sys.argv[2]
    output_parquet_path = sys.argv[3]

    combine_parquet_files(main_parquet_path, gps_parquet_path, output_parquet_path)
