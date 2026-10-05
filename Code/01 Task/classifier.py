import numpy as np
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from time import time
import matplotlib.pyplot as plt
import seaborn as sns



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
    cv_results = cross_validate(clf, x_train, y_train, cv=skf, scoring=['accuracy', 'precision', 'recall', 'f1_weighted'])
    metrics = {
        "Accuracy": np.mean(cv_results['test_accuracy']),
        "Precision": np.mean(cv_results['test_precision']),
        "Recall": np.mean(cv_results['test_recall']),
        "F1 Score": np.mean(cv_results['test_f1_weighted']),
    }
    # # Calculate performance metrics
    # metrics = {
    #     "Accuracy": accuracy_score(y_test, y_pred),
    #     "Precision": precision_score(
    #         y_test, y_pred, average="macro", zero_division=0
    #     ),
    #     "Recall": recall_score(
    #         y_test, y_pred, average="macro", zero_division=0
    #     ),
    #     "F1 Score": f1_score(
    #         y_test, y_pred, average="macro", zero_division=0
    #     ),
    # }

    # Graphic output if graph is True
    # Plot confusion matrix and metrics in a bar chart
    if graph:
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
        axes[0].set_title(f"{title} - Confusion Matrix")
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
        plt.tight_layout()
        plt.show()

    return metrics