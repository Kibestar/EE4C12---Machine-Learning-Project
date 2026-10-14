import os
import pandas as pd

# Global mapping dictionary for labels
PQD_INDICES = {
    'Normal': 0,
    'Sag': 1,
    'Swell': 2,
    'Interruption': 3,
    'Harmonics': 4,
    'Sag_harmonics': 5,
    'Swell_harmonics': 6,
    'Transient': 7,
    'Flicker': 8
}

# 1. Positional mapping of raw CSV columns (0-7) to feature dicts
POSITIONAL_MAPPING = {
    0: ('Feature 2', 'std_TmA'),         # Col 1 in CSV
    1: ('Feature 3', 'max_TmA'),         # Col 2 in CSV
    2: ('Feature 4', 'min_TmA'),         # Col 3 in CSV
    3: ('Feature 5', 'num_peaks'),       # Col 4 in CSV
    4: ('Feature 6', 'std_FmA_3_7'),     # Col 5 in CSV
    5: ('Feature 7', 'std_FmA_gt3'),     # Col 6 in CSV
    6: ('Feature 1', 'avg_abs_ST_3rd'),  # Col 7 in CSV
    7: ('Feature 8', 'near_zero_cnt')    # Col 8 in CSV
}

# 2. Desired numerical feature order (Feature 1 -> Feature 8)
FEATURE_ORDER = [
    'avg_abs_ST_3rd', # Feature 1
    'std_TmA',        # Feature 2
    'max_TmA',        # Feature 3
    'min_TmA',        # Feature 4
    'num_peaks',      # Feature 5
    'std_FmA_3_7',    # Feature 6
    'std_FmA_gt3',    # Feature 7
    'near_zero_cnt'   # Feature 8
]


def import_single_noiselevel_data(folder: str) -> pd.DataFrame:
    """
    Imports CSV files for a specific noise level, renames feature columns,
    reorders them sequentially (Feature 1 to Feature 8), and adds the label.
    """
    csv_files = [f for f in os.listdir(folder) if f.endswith('.csv')]
    dataframes = []

    for file in csv_files:
        label_name = os.path.splitext(file)[0]
        if label_name not in PQD_INDICES:
            print(f"Warning: File '{file}' skipped. Label '{label_name}' not in PQD_INDICES.")
            continue

        # Load CSV, treating first column as index
        df = pd.read_csv(os.path.join(folder, file), index_col=0)

        # Rename raw positional columns to named features
        df.columns = [POSITIONAL_MAPPING[i][1] for i in range(len(df.columns))]

        # Reorder columns explicitly from Feature 1 to Feature 8
        df = df[FEATURE_ORDER]

        # Add label column
        df['label'] = PQD_INDICES[label_name]
        dataframes.append(df)

    if not dataframes:
        raise ValueError(f"No valid PQD CSV files found in directory: {folder}")

    return pd.concat(dataframes, ignore_index=True)


def import_all_noiselevel_data(folders: list[str], add_noise_column: bool = True) -> pd.DataFrame:
    """
    Imports CSV files from multiple noise level folders, applies column 
    reordering (Feature 1 to 8), and aggregates them into a single DataFrame.
    """
    dataframes = []
    
    for folder in folders:
        df = import_single_noiselevel_data(folder)
        
        if add_noise_column:
            df['noise_level'] = os.path.basename(os.path.normpath(folder))
            
        dataframes.append(df)

    if not dataframes:
        raise ValueError(f"No data could be loaded from the provided folders: {folders}")

    return pd.concat(dataframes, ignore_index=True)