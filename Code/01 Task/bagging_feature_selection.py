"""Bootstrap one-vs-rest feature selection for the PQD data set."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier


LABELS = {
    "Normal": 0,
    "Sag": 1,
    "Swell": 2,
    "Interruption": 3,
    "Harmonics": 4,
    "Sag_harmonics": 5,
    "Swell_harmonics": 6,
    "Transient": 7,
    "Flicker": 8,
}
FEATURES = [f"F{i}" for i in range(1, 9)]
RAW_FEATURE_NAMES = [
    "avg abs",
    "sd",
    "max",
    "min",
    "no. pks",
    "sd fma",
    "sd fma 3",
    "no. pt near 0",
]
RAW_TO_FEATURE = dict(zip(RAW_FEATURE_NAMES, ["F2", "F3", "F4", "F5", "F6", "F7", "F1", "F8"]))


def load_dataset(folders: Iterable[str | Path]) -> pd.DataFrame:
    """Load SNR folders and return one row per sample with named features.

    Args:
        folders: Directories containing one CSV file per PQD class.

    Returns:
        A data frame containing ``F1``-``F8``, the string ``label``, and the
        source ``noise_level`` for every sample.
    """
    # ``rows`` stores each class/noise-level table before concatenation.
    rows: list[pd.DataFrame] = []
    for folder in folders:
        folder_path = Path(folder)
        if not folder_path.is_dir():
            raise FileNotFoundError(f"Data folder does not exist: {folder_path}")
        for csv_path in sorted(folder_path.glob("*.csv")):
            label = csv_path.stem
            if label not in LABELS:
                continue
            frame = pd.read_csv(csv_path)
            frame = frame.drop(columns=[frame.columns[0]], errors="ignore")
            if set(RAW_TO_FEATURE).issubset(frame.columns):
                frame = frame.rename(columns=RAW_TO_FEATURE)
            if not set(FEATURES).issubset(frame.columns):
                if len(frame.columns) != len(FEATURES):
                    raise ValueError(f"Expected eight feature columns in {csv_path}")
                frame.columns = FEATURES
            frame = frame[FEATURES].apply(pd.to_numeric, errors="raise")
            frame["label"] = label
            frame["noise_level"] = folder_path.name
            rows.append(frame)
    if not rows:
        raise ValueError("No recognised PQD CSV files were found")
    return pd.concat(rows, ignore_index=True)


def default_classifiers(random_state: int = 42) -> dict[str, Any]:
    """Create the classifiers used to compare feature subsets.

    Args:
        random_state: Seed used by estimators that contain randomized steps.

    Returns:
        A mapping from readable classifier names to unfitted estimators.
    """
    return {
        "logistic_regression": LogisticRegression(
            class_weight="balanced", max_iter=2000, random_state=random_state
        ),
        "linear_svm": SVC(kernel="linear", class_weight="balanced", random_state=random_state),
        # "rbf_svm": SVC(kernel="rbf", class_weight="balanced", random_state=random_state),
        # "decision_tree": DecisionTreeClassifier(
        #     class_weight="balanced", max_depth=8, random_state=random_state
        # ),
    }


@dataclass(frozen=True)
class FeatureSelectionResult:
    """Store the selected features and bootstrap history for one class/model."""

    target_label: str
    classifier: str
    selected_features: tuple[str, ...]
    score: float
    history: pd.DataFrame


def _bootstrap_score(
    estimator: Any,
    x: pd.DataFrame,
    y: pd.Series,
    features: Sequence[str],
    rng: np.random.Generator,
    n_bootstraps: int,
) -> tuple[float, float]:
    """Score a feature subset using repeated bootstrap out-of-bag samples.

    Args:
        estimator: Unfitted estimator or pipeline to clone for each bootstrap.
        x: Data frame containing all candidate feature columns.
        y: Binary target values for one-vs-rest classification.
        features: Columns used for this particular evaluation.
        rng: Random number generator controlling bootstrap sampling.
        n_bootstraps: Number of bootstrap/OOB repetitions.

    Returns:
        The mean and standard deviation of the OOB binary F1 scores.
    """
    # ``scores`` contains one F1 value for every usable OOB repetition.
    scores: list[float] = []
    # ``indices`` lets us sample rows without changing the original index.
    indices = np.arange(len(y))
    for _ in range(n_bootstraps):
        # ``train_indices`` is the bootstrap training sample; repeated indices
        # are expected because sampling is performed with replacement.
        train_indices = rng.choice(indices, size=len(indices), replace=True)
        # ``out_of_bag`` contains rows not selected for this bootstrap sample.
        out_of_bag = np.setdiff1d(indices, np.unique(train_indices))
        # OOB samples are never used to fit or scale the model.
        if len(out_of_bag) == 0 or y.iloc[train_indices].nunique() < 2:
            continue
        # Clone prevents a previous bootstrap from influencing this model.
        model = clone(estimator)
        model.fit(x.iloc[train_indices][list(features)], y.iloc[train_indices])
        prediction = model.predict(x.iloc[out_of_bag][list(features)])
        # Binary F1 measures performance on the selected class, not the
        # usually much larger negative class.
        scores.append(f1_score(y.iloc[out_of_bag], prediction, zero_division=0))
    if not scores:
        raise ValueError("No usable out-of-bag bootstrap samples were produced")
    return float(np.mean(scores)), float(np.std(scores, ddof=0))


def select_features_for_classifier(
    data: pd.DataFrame,
    estimator: Any,
    classifier_name: str,
    target_label: str,
    *,
    features: Sequence[str] = FEATURES,
    n_bootstraps: int = 20,
    min_improvement: float = 0.002,
    random_state: int = 42,
) -> FeatureSelectionResult:
    """Select features for one class using one-vs-rest bootstrap F1 scoring.

    Args:
        data: Full data frame containing features and the string ``label``.
        estimator: Unfitted classifier being evaluated.
        classifier_name: Display name stored in the result.
        target_label: Class converted to the positive one-vs-rest target.
        features: Initial candidate feature columns.
        n_bootstraps: Bootstrap repetitions for each candidate subset.
        min_improvement: Tolerance for accepting a feature removal.
        random_state: Seed used by the bootstrap generator.

    Returns:
        A result containing the selected features, final F1 score, and history.
    """
    missing = set(features) - set(data.columns)
    if missing or "label" not in data:
        raise ValueError(f"Data is missing required columns: {sorted(missing | {'label'} - set(data.columns))}")
    if target_label not in set(data["label"]):
        raise ValueError(f"Target label is not present in the data: {target_label}")

    # ``x`` is kept as a data-frame so candidate columns can be selected by name.
    x = data
    # Convert the multiclass labels into the binary target-vs-all task.
    y = data["label"].eq(target_label).astype(int)
    estimator = Pipeline([("scale", StandardScaler()), ("classifier", estimator)])
    # Reusing this generator makes the selection reproducible for this class.
    rng = np.random.default_rng(random_state)
    # ``active`` is the current feature subset; it shrinks during elimination.
    active = list(features)
    # ``history`` records every accepted subset and its bootstrap score.
    history: list[dict[str, Any]] = []
    current_score, current_std = _bootstrap_score(estimator, x, y, active, rng, n_bootstraps)
    history.append({"classifier": classifier_name, "features": tuple(active), "removed": None,
                    "mean_f1": current_score, "std_f1": current_std})

    while len(active) > 1:
        # Evaluate every possible feature removal before accepting the best one.
        # ``candidates`` holds the score obtained by removing each active
        # feature once during this elimination round.
        candidates = []
        for candidate in active:
            subset = [feature for feature in active if feature != candidate]
            mean_f1, std_f1 = _bootstrap_score(estimator, x, y, subset, rng, n_bootstraps)
            candidates.append((mean_f1, std_f1, candidate, subset))
        candidate_score, candidate_std, removed, subset = max(candidates, key=lambda item: item[0])
        if candidate_score + min_improvement < current_score:
            break
        active = subset
        current_score, current_std = candidate_score, candidate_std
        history.append({"classifier": classifier_name, "features": tuple(active), "removed": removed,
                        "mean_f1": current_score, "std_f1": current_std})

    return FeatureSelectionResult(
        target_label, classifier_name, tuple(active), current_score, pd.DataFrame(history)
    )


def run_feature_selection(
    data: pd.DataFrame,
    classifiers: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> list[FeatureSelectionResult]:
    """Run independent one-vs-rest selection for every class and classifier.

    Args:
        data: Full labelled data frame returned by :func:`load_dataset`.
        classifiers: Optional mapping of names to unfitted estimators.
        **kwargs: Selection settings forwarded to
            :func:`select_features_for_classifier`.

    Returns:
        A flat list with one result for every class/classifier combination.
        The list is intentionally not unpacked into an overall feature set.
    """
    models = classifiers or default_classifiers(kwargs.pop("random_state", 42))
    # ``results`` preserves every class-specific recommendation for the caller.
    results = []
    # Each class receives a separate binary target and independent selection.
    for target_label in sorted(data["label"].unique()):
        for classifier_name, estimator in models.items():
            results.append(
                select_features_for_classifier(
                    data, estimator, classifier_name, target_label, **kwargs
                )
            )
    return results
