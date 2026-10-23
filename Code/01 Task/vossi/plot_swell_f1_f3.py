"""Create a 2D plot of F1 and F3, highlighting Swell samples."""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib.pyplot as plt


CURRENT_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = CURRENT_DIR.parents[2]
sys.path.insert(0, str(CURRENT_DIR))

from bagging_feature_selection import load_dataset


NOISE_LEVELS = (
    "SNR_noiseless",
    "SNR_50db",
    "SNR_40db",
    "SNR_30db",
    "SNR_20db",
)
TARGET_LABEL = "Swell"


def create_plot(output_path: Path) -> None:
    """Plot F1 against F3 for all samples and highlight Swell samples."""
    data = load_dataset(REPOSITORY_ROOT / "Code" / "data" / level for level in NOISE_LEVELS)
    swell = data["label"].eq(TARGET_LABEL)
    figure, axes = plt.subplots(figsize=(3.5, 3.2))
    axes.scatter(
    data.loc[~swell, "F1"],
    data.loc[~swell, "F3"],
    s=8,
    alpha=0.8,
    linewidths=0,
    label="Other PQDs",
    )
    axes.scatter(
        data.loc[swell, "F1"],
        data.loc[swell, "F3"],
        s=10,
        alpha=0.8,
        linewidths=0,
        label=TARGET_LABEL,
    )
    axes.set_xlabel("F1")
    axes.set_ylabel("F3")
    axes.legend()
    figure.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, bbox_inches="tight")
    plt.close(figure)


if __name__ == "__main__":
    create_plot(REPOSITORY_ROOT / "Paper - IEEE" / "02_Plots" / "swell_f1_f3.pdf")
