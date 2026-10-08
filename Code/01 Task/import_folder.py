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