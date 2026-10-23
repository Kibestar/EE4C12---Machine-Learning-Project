# This file contains functions that will be used in the jupyter notebook for the statistical analysis of the PQD data set. The functions are used to load the data, run the statistical tests, and evaluate the results.

import os
from pathlib import Path
import pandas as pd


DATA_ROOT = Path(__file__).resolve().parents[2] / "data"


def _resolve_noise_folder(folder: str | os.PathLike[str]) -> Path:
    """Resolve a noise-level name against the shared Code/data directory."""
    candidate = Path(folder)
    if candidate.is_dir():
        return candidate
    shared_folder = DATA_ROOT / candidate
    if shared_folder.is_dir():
        return shared_folder
    matching = [path for path in DATA_ROOT.iterdir()
                if path.is_dir() and path.name.lower() == candidate.name.lower()]
    if matching:
        return matching[0]
    raise FileNotFoundError(f"Data folder does not exist: {folder}")

# Global mapping dictionary for PQD class labels
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

# 1. Positional mapping of raw CSV columns (0-7) to feature names (F1 - F8)
POSITIONAL_MAPPING = {
    0: 'F2:std_TmA',         # Col 1 in raw CSV
    1: 'F3:max_TmA',         # Col 2 in raw CSV
    2: 'F4:min_TmA',         # Col 3 in raw CSV
    3: 'F5:num_peaks',       # Col 4 in raw CSV
    4: 'F6:std_FmA_3_7',     # Col 5 in raw CSV
    5: 'F7:std_FmA_gt3',     # Col 6 in raw CSV
    6: 'F1:avg_abs_ST_3rd',  # Col 7 in raw CSV
    7: 'F8:near_zero_cnt'    # Col 8 in raw CSV
}

# 2. Desired numerical feature order (F1 to F8)
FEATURE_ORDER = [
    'F1:avg_abs_ST_3rd',
    'F2:std_TmA',
    'F3:max_TmA',
    'F4:min_TmA',
    'F5:num_peaks',
    'F6:std_FmA_3_7',
    'F7:std_FmA_gt3',
    'F8:near_zero_cnt'
]


def import_single_noiselevel_data(folder: str) -> pd.DataFrame:
    """
    Imports all CSV files for a specific noise level from the given folder,
    renames feature columns with the 'F<num>:<name>' format, reorders them 
    sequentially from F1 to F8, and adds numerical PQD labels.

    Input:
        folder (str): Directory path containing CSV files for one noise level.
    Output:
        data (pd.DataFrame): Combined DataFrame with columns F1 to F8 and 'label'.
    """
    folder_path = _resolve_noise_folder(folder)
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    dataframes = []

    for file in csv_files:
        label_name = os.path.splitext(file)[0]
        if label_name not in PQD_INDICES:
            print(f"Warning: File '{file}' skipped. Label '{label_name}' not in PQD_INDICES.")
            continue

        # Load CSV, treating first column as index
        df = pd.read_csv(folder_path / file, index_col=0)

        # Map positional columns to named features
        df.columns = [POSITIONAL_MAPPING[i] for i in range(len(df.columns))]

        # Reorder columns explicitly from F1 to F8
        df = df[FEATURE_ORDER]

        # Add numerical label
        df['label'] = PQD_INDICES[label_name]
        dataframes.append(df)

    if not dataframes:
        raise ValueError(f"No valid PQD CSV files found in directory: {folder_path}")

    return pd.concat(dataframes, ignore_index=True)


def import_all_noiselevel_data(folders: list[str], add_noise_column: bool = True) -> pd.DataFrame:
    """
    Imports CSV files from multiple noise level folders, applies column 
    reordering (F1 to F8), and aggregates them into a single unified DataFrame.

    Input:
        folders (list[str]): List of directory paths containing CSV files.
        add_noise_column (bool): If True, adds a 'noise_level' column identifying source folder.
    Output:
        data (pd.DataFrame): Combined DataFrame with feature columns F1 to F8, 'label', 
                             and optional 'noise_level'.
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