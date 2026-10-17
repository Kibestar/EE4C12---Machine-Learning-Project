"""Bootstrap one-vs-rest feature selection for the PQD data set."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate
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
            class_weight="balanced", max_iter=200, random_state=random_state
        ),
        "linear_svm": SVC(kernel="linear", class_weight="balanced", random_state=random_state),
        "rbf_svm": SVC(kernel="rbf", class_weight="balanced", random_state=random_state),
        "decision_tree": DecisionTreeClassifier(
            class_weight="balanced", max_depth=8, random_state=random_state
        ),
    }


@dataclass(frozen=True)
class FeatureSelectionResult:
    """Store the selected features and cross-validation history for one class/model."""

    target_label: str
    classifier: str
    selected_features: tuple[str, ...]
    score: float
    history: pd.DataFrame


def _cross_validation_score(
    estimator: Any,
    x: pd.DataFrame,
    y: pd.Series,
    features: Sequence[str],
    n_splits: int,
    random_state: int,
) -> tuple[float, float]:
    """Score a feature subset using stratified k-fold cross-validation.

    Args:
        estimator: Unfitted estimator evaluated independently in every fold.
        x: Data frame containing all candidate feature columns.
        y: Binary target values for one-vs-rest classification.
        features: Columns used for this particular evaluation.
        n_splits: Number of stratified folds.
        random_state: Seed used to shuffle the fold assignments.

    Returns:
        The mean and standard deviation of the validation binary F1 scores.
    """
    # ``class_counts`` ensures every fold can contain both binary classes.
    class_counts = y.value_counts()
    if class_counts.min() < n_splits:
        raise ValueError(
            f"n_splits={n_splits} exceeds the smallest class size "
            f"({class_counts.min()})"
        )
    # The scaler remains inside ``estimator`` and is fitted separately per fold.
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    scores = cross_validate(
        estimator,
        x[list(features)],
        y,
        cv=cv,
        scoring="f1",
        error_score="raise",
    )["test_score"]
    return float(np.mean(scores)), float(np.std(scores, ddof=0))


def select_features_for_classifier(
    data: pd.DataFrame,
    estimator: Any,
    classifier_name: str,
    target_label: str,
    *,
    features: Sequence[str] = FEATURES,
    n_splits: int = 5,
    min_improvement: float = 0.002,
    random_state: int = 42,
) -> FeatureSelectionResult:
    """Select features for one class using one-vs-rest k-fold F1 scoring.

    Args:
        data: Full data frame containing features and the string ``label``.
        estimator: Unfitted classifier being evaluated.
        classifier_name: Display name stored in the result.
        target_label: Class converted to the positive one-vs-rest target.
        features: Initial candidate feature columns.
        n_splits: Number of stratified folds for each candidate subset.
        min_improvement: Tolerance for accepting a feature removal.
        random_state: Seed used to shuffle the cross-validation folds.

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
    # ``active`` is the current feature subset; it shrinks during elimination.
    active = list(features)
    # ``history`` records every accepted subset and its cross-validation score.
    history: list[dict[str, Any]] = []
    current_score, current_std = _cross_validation_score(
        estimator, x, y, active, n_splits, random_state
    )
    history.append({"classifier": classifier_name, "features": tuple(active), "removed": None,
                    "mean_f1": current_score, "std_f1": current_std})

    while len(active) > 1:
        # Evaluate every possible feature removal before accepting the best one.
        # ``candidates`` holds the score obtained by removing each active
        # feature once during this elimination round.
        candidates = []
        for candidate in active:
            subset = [feature for feature in active if feature != candidate]
            mean_f1, std_f1 = _cross_validation_score(
                estimator, x, y, subset, n_splits, random_state
            )
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


def majority_vote_features(
    results: Sequence[FeatureSelectionResult],
    *,
    min_classifiers: int | None = None,
) -> dict[str, tuple[str, ...]]:
    """Return one majority-voted feature set for every target class.

    Args:
        results: Classifier-specific results returned by
            :func:`run_feature_selection`.
        min_classifiers: Minimum number of classifiers that must select a
            feature. By default, a strict majority is required.

    Returns:
        A mapping from each target class to its recommended feature tuple.
        If no feature reaches the vote threshold for a class, the feature
        selected most often is returned so every class has a usable set.

    Raises:
        ValueError: If no results are supplied or the vote threshold is
            outside the valid range.
    """
    if not results:
        raise ValueError("At least one feature-selection result is required")

    # Group classifier selections by the class they were trained to detect.
    results_by_class: dict[str, list[FeatureSelectionResult]] = {}
    for result in results:
        results_by_class.setdefault(result.target_label, []).append(result)

    recommendations: dict[str, tuple[str, ...]] = {}
    for target_label, class_results in results_by_class.items():
        classifier_count = len(class_results)
        threshold = min_classifiers or (classifier_count // 2 + 1)
        if not 1 <= threshold <= classifier_count:
            raise ValueError(
                f"min_classifiers must be between 1 and {classifier_count} "
                f"for class {target_label}"
            )

        # Count each feature at most once per classifier, even if a malformed
        # result contains a duplicate feature name.
        feature_counts = pd.Series(0, index=FEATURES, dtype=int)
        for result in class_results:
            selected = set(result.selected_features)
            feature_counts.loc[feature_counts.index.intersection(selected)] += 1

        voted_features = tuple(
            feature for feature in FEATURES if feature_counts[feature] >= threshold
        )
        if not voted_features:
            # Keep the output usable when classifiers disagree completely.
            highest_count = feature_counts.max()
            voted_features = tuple(
                feature for feature in FEATURES if feature_counts[feature] == highest_count
            )
        recommendations[target_label] = voted_features

    return recommendations
