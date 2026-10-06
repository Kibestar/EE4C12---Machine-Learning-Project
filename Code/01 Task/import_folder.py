import os
import pandas as pd

# Global mapping dictionary
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

def import_single_noiselevel_data(folder: str) -> pd.DataFrame:
    """
    Imports all CSV files for a specific noise level from the given folder and
    returns a unified DataFrame containing samples and numerical PQD labels.

    Input:
        folder (str): Directory path containing CSV files for one noise level.
    Output:
        data (pd.DataFrame): Combined DataFrame with feature columns and 'label'.
    """
    # Filter for CSV files only
    csv_files = [f for f in os.listdir(folder) if f.endswith('.csv')]
    
    dataframes = []
    for file in csv_files:
        # Get label name from filename (e.g., 'Sag.csv' -> 'Sag')
        label_name = os.path.splitext(file)[0]
        
        if label_name not in PQD_INDICES:
            print(f"Warning: File '{file}' skipped. Label '{label_name}' not in PQD_INDICES.")
            continue

        # Load CSV, treating first column as index
        df = pd.read_csv(os.path.join(folder, file), index_col=0)
        
        # Add label index
        df['label'] = PQD_INDICES[label_name]
        dataframes.append(df)

    if not dataframes:
        raise ValueError(f"No valid PQD CSV files found in directory: {folder}")

    # Concatenate all class dataframes into one
    return pd.concat(dataframes, ignore_index=True)


def import_all_noiselevel_data(folders: list[str], add_noise_column: bool = False) -> pd.DataFrame:
    """
    Imports CSV files from multiple noise level folders and aggregates them 
    into a single unified DataFrame.

    Input:
        folders (list[str]): List of directory paths containing noise level CSV files.
        add_noise_column (bool): If True, adds a 'noise_level' column identifying source folder.
    Output:
        data (pd.DataFrame): Combined DataFrame with feature columns, 'label', and optional 'noise_level'.
    """
    dataframes = []
    
    for folder in folders:
        # Reuse existing single-folder loader
        df = import_single_noiselevel_data(folder)
        
        if add_noise_column:
            # Extract folder name (e.g., 'SNR_20dB' from 'path/to/SNR_20dB')
            df['noise_level'] = os.path.basename(os.path.normpath(folder))
            
        dataframes.append(df)

    if not dataframes:
        raise ValueError(f"No data could be loaded from the provided folders: {folders}")

    return pd.concat(dataframes, ignore_index=True)