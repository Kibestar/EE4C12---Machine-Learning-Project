import os
from fnmatch import fnmatch
import matplotlib.image as mpimg
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler




def data_import(Folder: list[str], Features: list[str]) -> tuple[list[np.ndarray], list[int]]:
    """
    Imports the data from the given folders and returns one entry per sample.

    :param Folder: The folders containing the data files.

    :param Features: The features to be kept from the data (F1, F2, ...).

    :return: A tuple containing the samples and one corresponding label per sample.
    """
    data = []
    labels = []
    for Folder in Folder:
        # Get the path to the data folder and list the files in it
        data_dir = os.path.join(os.getcwd(), Folder)
        # print('Number of files in the dataset folder: ', len(os.listdir(data_dir)))

        # Loop through the files in the data folder and read the data from each file
        for filename in os.listdir(data_dir):
            if filename.endswith(".csv"): # Check if the file is a CSV file
                file = os.path.join(data_dir, filename) # Get the full path to the file
                data_pd = pd.read_csv(file) # Read the data from the CSV file into a pandas

                # replace the features (features = ["avg abs","sd","max","min","no. pks","sd fma","sd fma 3","no. pt near 0"]) with F1, F2, ...
                data_pd.columns = [f'F{i}' for i in range(len(data_pd.columns))]
                data_pd = data_pd[Features]  # Select the specified features

                # Each row is one sample. The filename supplies its label.
                samples = data_pd.to_numpy()
                data.extend(samples)

                if fnmatch(filename, "Flicker*"):
                    label = "Flicker"
                elif fnmatch(filename, "Harmonics*"):
                    label = "Harmonics"
                elif fnmatch(filename, "Interruption*"):
                    label = "Interruption"
                elif fnmatch(filename, "Normal*"):
                    label = "Normal"
                elif fnmatch(filename, "Sag_harmonics*"):
                    label = "Sag_harmonics"
                elif fnmatch(filename, "Sag*"):
                    label = "Sag"
                elif fnmatch(filename, "Swell_harmonics*"):
                    label = "Swell_harmonics"
                elif fnmatch(filename, "Swell*"):
                    label = "Swell"
                elif fnmatch(filename, "Transient*"):
                    label = "Transient"
                else:
                    raise ValueError('Unknown class: %s' % (filename))

                labels.extend([label] * len(samples)) # Add the label for each sample in the file
                
    # scale the data to have zero mean and unit variance
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data)
    return scaled_data, labels