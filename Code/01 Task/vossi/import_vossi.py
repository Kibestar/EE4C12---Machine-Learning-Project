# General Imports
import os
from pathlib import Path
import numpy as np
import pandas as pd
from fnmatch import fnmatch
from time import time

# Machine Learning Imports
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix


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








def data_import(Folder: list[str], Features: list[str]) -> tuple[list[np.ndarray], list[int]]:
    """
    Imports the data from the given folders and returns one entry per sample.

    :param Folder: The folders containing the data files.

    :param Features: The features to be kept from the data (F1, F2, ...).

    :return: A tuple containing the samples and one corresponding label per sample.
    """
    data = []
    labels = []
    for folder in Folder:
        # Get the path to the data folder and list the files in it
        data_dir = _resolve_noise_folder(folder)
        # print('Number of files in the dataset folder: ', len(os.listdir(data_dir)))

        # Loop through the files in the data folder and read the data from each file
        for filename in os.listdir(data_dir):
            if filename.endswith(".csv"): # Check if the file is a CSV file
                file = data_dir / filename # Get the full path to the file
                data_pd = pd.read_csv(file) # Read the data from the CSV file into a pandas

                # replace the features (features = ["avg abs","sd","max","min","no. pks","sd fma","sd fma 3","no. pt near 0"]) with F2, F3, F4, F5, F6, F7, F1, F8.
                data_pd = data_pd.rename(columns={
                    "avg abs": "F2",
                    "sd": "F3",
                    "max": "F4",
                    "min": "F5",
                    "no. pks": "F6",
                    "sd fma": "F7",
                    "sd fma 3": "F1",
                    "no. pt near 0": "F8"
                })
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


def find_best_feature_to_drop(files: list, features: list, target_label: str, feature_dropped: list, best_f1_n0: float, model):
    """
    Finds the best feature to drop based on the F1 score while iterating through n-1/n features.

    :param features: list of features to use for classification
    :param target_label: the label to classify against all other labels
    :param feature_dropped: list of features that have already been dropped
    :param best_f1_n0: the best F1 score from the previous iteration (with n features)

    :return: a tuple containing:
    1. the feature that, when dropped, gives the best F1 score
    2. the best F1 score achieved by dropping a feature
    """

    active_features = [f for f in features if f not in feature_dropped]
    best_feature = None
    best_f1_local = 0

    for feature in active_features:
        # drop the feature n
        features_to_use = [f for f in active_features if f != feature]

        data, sample_labels = data_import(files, features_to_use)
        full_data = pd.DataFrame(data, columns=features_to_use)

        # Change labels to binary classification: 1 for the target class, 0 for all other events
        binary_labels = [int(sample_label == target_label) for sample_label in sample_labels]

        # add labels to the dataframe
        full_data['Label'] = binary_labels

        X_train, X_test, y_train, y_test = train_test_split(data, binary_labels, test_size=0.2, random_state=42, stratify=binary_labels)

        metrics, metrics_test = Classifier(model, X_train, y_train, X_test, y_test, title=f"{model.__class__.__name__} - " + target_label + " - Feature not used: " + str(feature), graph=False)
        # find the best F1 score and the corresponding feature to drop
        if metrics["F1 Score"] > best_f1_local:
            best_f1_local = metrics["F1 Score"]
            best_feature = feature
    # check if the best F1 score is better than the previous best F1 score (best_f1_n0) with a small subtraction to account for performance improvements that are not significant
    if best_f1_local > best_f1_n0 - 0.01:
        best_f1 = best_f1_local
    else:
        best_f1 = None  # If no improvement, return None to indicate that dropping any feature does not improve F1 score

    return best_feature, best_f1


def Classifier(clf, x_train, y_train, x_test, y_test, title="Classifier", graph=True):
    '''
    Classifies the data using the provided classifier and evaluates its performance.

    :param clf: The classifier to use
    :param x_train: The training data
    :param y_train: The training labels
    :param x_test: The test data
    :param y_test: The test labels
    :param title: The title of the plot
    :param graph: Whether to display the results in a graph

    :return: A dictionary containing the performance metrics
    :return: A plot of the confusion matrix and a bar chart of the performance metrics if graph is True
    '''

    # Train the classifier
    clf.fit(x_train, y_train)
    y_pred = clf.predict(x_test)

    # # Calculate performance metrics wit CV
    skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    cv_results = cross_validate(clf, x_train, y_train, cv=skf, scoring=['accuracy', 'precision', 'recall', 'f1'])
    metrics = {
        "Accuracy": np.mean(cv_results['test_accuracy']),
        "Precision": np.mean(cv_results['test_precision']),
        "Recall": np.mean(cv_results['test_recall']),
        "F1 Score": np.mean(cv_results['test_f1']),
    }
    # Calculate performance metrics without CV
    metrics_test = {
        "Accuracy": accuracy_score(y_test, y_pred),
        "Precision": precision_score(
            y_test, y_pred, average="macro", zero_division=0
        ),
        "Recall": recall_score(
            y_test, y_pred, average="macro", zero_division=0
        ),
        "F1 Score": f1_score(
            y_test, y_pred, average="macro", zero_division=0
        ),
    }

    # Graphic output if graph is True
    # Plot confusion matrix and metrics in a bar chart
    if graph:
        import matplotlib.pyplot as plt
        import seaborn as sns

        print(f"{title} - Iterations: {getattr(clf, 'n_iter_', 'N/A')}")
        # Create a figure with two subplots: one for the confusion matrix and one for the metrics
        fig, axes = plt.subplots(
            1, 3,
            figsize=(10, 4),
            gridspec_kw={"width_ratios": [1.2, 1, 1]}
        )


        # Confusion matrix
        sns.heatmap(
            confusion_matrix(y_test, y_pred),
            annot=True,
            fmt="d",
            cmap="Blues",
            cbar=False,
            ax=axes[0]
        )
        axes[0].set_title(f"Confusion Matrix")
        axes[0].set_xlabel("Predicted Labels")
        axes[0].set_ylabel("True Labels")
        # make axes[0] square
        axes[0].set_aspect("equal")

        # Metrics
        metric_names = list(metrics.keys())
        metric_values = list(metrics.values())

        axes[1].barh(metric_names, metric_values, color="steelblue")
        axes[1].set_xlim(0, 1)
        axes[1].set_xlabel("Score")
        axes[1].set_title("Performance Metrics")

        # Add the metric values as text on the bars
        for i, value in enumerate(metric_values):
            axes[1].text(value - 0.2, i, f"{value:.3f}", va="center", color="white", fontweight="bold")

        # plot the predicted probabilities per sample in a bar chart if y_proba is not None
        # (samples on X and predicted probability for class 1 on Y), sort them by probability
        y_proba = clf.predict_proba(x_test) if hasattr(clf, "predict_proba") else None
        if y_proba is not None:
            sorted_indices = np.argsort(y_proba[:, 1])
            sorted_proba = y_proba[sorted_indices, 1]
            axes[2].bar(range(len(sorted_proba)), sorted_proba, color="steelblue")
            axes[2].set_ylim(0, 1)
            axes[2].set_xlabel("Samples (sorted by predicted probability)")
            axes[2].set_ylabel("Predicted Probability for Class 1")
            axes[2].set_title("Predicted Probabilities")
        # Title over all subplots
        plt.suptitle(f"{title}", fontsize=16, y=1.05)
        plt.tight_layout()
        plt.show()

    return metrics, metrics_test