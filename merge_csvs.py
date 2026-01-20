"""
Merge multiple CSV files from each dataset folder into single combined CSV files.
"""

import os
import glob
import pandas as pd

# Base path
BASE_PATH = os.path.dirname(__file__)
DATASETS_PATH = os.path.join(BASE_PATH, "datasets")

# Dataset folders to process
DATASET_FOLDERS = [
    "api_data_aadhar_biometric",
    "api_data_aadhar_demographic",
    "api_data_aadhar_enrolment"
]


def merge_csv_files(folder_name):
    """
    Merge all CSV files in a folder into a single combined CSV file.
    """
    folder_path = os.path.join(DATASETS_PATH, folder_name)
    csv_files = sorted(glob.glob(os.path.join(folder_path, "*.csv")))
    
    if not csv_files:
        print(f"Warning: No CSV files found in {folder_path}")
        return
    
    print(f"\nProcessing: {folder_name}")
    print(f"  Found {len(csv_files)} CSV files")
    
    # Read and concatenate all CSV files
    dfs = []
    total_rows = 0
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        dfs.append(df)
        total_rows += len(df)
        print(f"  - {os.path.basename(csv_file)}: {len(df):,} rows")
    
    # Combine all dataframes
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Output file path (in datasets folder)
    output_file = os.path.join(DATASETS_PATH, f"{folder_name}_combined.csv")
    
    # Save combined CSV
    combined_df.to_csv(output_file, index=False)
    
    print(f"  ✅ Combined {total_rows:,} rows into: {os.path.basename(output_file)}")
    return output_file


def main():
    print("=" * 60)
    print("CSV File Merger")
    print("=" * 60)
    
    output_files = []
    for folder_name in DATASET_FOLDERS:
        output_file = merge_csv_files(folder_name)
        if output_file:
            output_files.append(output_file)
    
    print("\n" + "=" * 60)
    print("✅ All files merged successfully!")
    print("\nOutput files:")
    for f in output_files:
        size_mb = os.path.getsize(f) / (1024 * 1024)
        print(f"  - {os.path.basename(f)} ({size_mb:.1f} MB)")
    print("=" * 60)


if __name__ == "__main__":
    main()
