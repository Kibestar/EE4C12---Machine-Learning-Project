import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from time import time
import matplotlib.pyplot as plt
import seaborn as sns



def Classifier(clf, x_train, y_train, x_test, y_test, title="Classifier"):
    
    # Train the classifier
    clf.fit(x_train, y_train) 
    print(f"{title} - Iterations: {getattr(clf, 'n_iter_', 'N/A')}")
    y_pred = clf.predict(x_test)

    # Calculate performance metrics
    metrics = {
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

    # Create a figure with two subplots: one for the confusion matrix and one for the metrics
    fig, axes = plt.subplots(
        1, 2,
        figsize=(10, 4),
        gridspec_kw={"width_ratios": [1.2, 1]}
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

    plt.tight_layout()
    plt.show()

    return metrics