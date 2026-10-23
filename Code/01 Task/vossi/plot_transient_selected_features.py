"""Create the report plot for the bagging-selected transient features."""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman"],
    "font.size": 7,           # Matches \footnotesize
    "axes.labelsize": 8,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "figure.titlesize": 9
})


CURRENT_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = CURRENT_DIR.parents[2]
sys.path.insert(0, str(CURRENT_DIR))

from bagging_feature_selection import load_dataset


SELECTED_FEATURES = ("F1", "F6", "F7")
TARGET_LABEL = "Transient"
NOISE_LEVELS = (
    "SNR_noiseless",
    "SNR_50db",
    "SNR_40db",
    "SNR_30db",
    "SNR_20db",
)


def create_plot(output_path: Path) -> None:
    """Plot all samples in the selected feature space and highlight transients."""
    data = load_dataset(REPOSITORY_ROOT / "Code" / "data" / level for level in NOISE_LEVELS)
    transient = data["label"].eq(TARGET_LABEL)
    figure = plt.figure(figsize=(3.5, 3.2))
    axes = figure.add_subplot(projection="3d")
    axes.scatter(
        data.loc[~transient, SELECTED_FEATURES[0]],
        data.loc[~transient, SELECTED_FEATURES[1]],
        data.loc[~transient, SELECTED_FEATURES[2]],
        s=8,
        alpha=0.8,
        linewidths=0,
        label="Other PQDs",
    )
    axes.scatter(
        data.loc[transient, SELECTED_FEATURES[0]],
        data.loc[transient, SELECTED_FEATURES[1]],
        data.loc[transient, SELECTED_FEATURES[2]],
        s=10,
        alpha=0.8,
        linewidths=0,
        label=TARGET_LABEL,
    )
    axes.set_xlabel(SELECTED_FEATURES[0])
    axes.set_ylabel(SELECTED_FEATURES[1])
    axes.set_zlabel(SELECTED_FEATURES[2])
    axes.legend(frameon=False, loc="upper left")
    axes.view_init(elev=24, azim=-58)
    figure.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, bbox_inches="tight")
    plt.close(figure)


if __name__ == "__main__":
    create_plot(
        REPOSITORY_ROOT / "Paper - IEEE" / "02_Plots" / "transient_selected_features.pdf"
    )
