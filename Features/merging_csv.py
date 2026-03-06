import pandas as pd
import glob
import os
import numpy as np

# =================================================================
# 1) CONFIGURATION
# =================================================================
# Replace this with the folder where your unzipped CSVs are
folder_path = r'C:\Users\LENOVO\Downloads\MachineLearningCSV\MachineLearningCVE'
output_filename = r'C:\Users\LENOVO\Downloads\MachineLearningCSV\CIC_IDS_2017_Merged.csv'

# =================================================================
# 2) FIND AND MERGE FILES
# =================================================================
search_pattern = os.path.join(folder_path, "*.csv")
all_files = glob.glob(search_pattern)

if len(all_files) == 0:
    print(f"❌ Error: No CSV files found in {folder_path}")
else:
    print(f"✅ Found {len(all_files)} files. Merging now... (This may take a minute)")

    # Load all CSVs into a list
    df_list = []
    for f in all_files:
        print(f"Reading: {os.path.basename(f)}")
        temp_df = pd.read_csv(f)
        df_list.append(temp_df)

    # Concatenate them all
    df = pd.concat(df_list, ignore_index=True)

    # =================================================================
    # 3) DATA CLEANING (Critical for CIC-IDS2017)
    # =================================================================
    print("Cleaning data...")

    # Remove leading/trailing spaces from column names
    df.columns = df.columns.str.strip()

    # Replace Infinity values with NaN and then drop them
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)

    # =================================================================
    # 4) SAVE AND VERIFY
    # =================================================================
    print(f"Saving merged file to: {output_filename}...")
    df.to_csv(output_filename, index=False)

    print("-" * 30)
    print("SUCCESS!")
    print(f"Total Rows: {len(df)}")
    print("\nAttack counts in the merged file:")
    print(df['Label'].value_counts())
    print("-" * 30)
    print(f"You can now find '{output_filename}' in your project folder.")