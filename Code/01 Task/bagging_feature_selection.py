"""Bootstrap feature selection for the power-quality disturbance data.

The module keeps data loading, model evaluation, feature selection, and
consensus selection separate so the workflow can be reused outside a notebook.
"""

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
    """Load one or more SNR folders into a frame with F1..F8 and ``label``."""
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
    """Return diverse classifiers suitable for the small eight-feature data set."""
    return {
        "logistic_regression": LogisticRegression(
            class_weight="balanced", max_iter=2000, random_state=random_state
        ),
        "linear_svm": SVC(kernel="linear", class_weight="balanced", random_state=random_state),
        "rbf_svm": SVC(kernel="rbf", class_weight="balanced", random_state=random_state),
        "decision_tree": DecisionTreeClassifier(
            class_weight="balanced", max_depth=8, random_state=random_state
        ),
    }


@dataclass(frozen=True)
class FeatureSelectionResult:
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
    """Return mean and standard deviation of macro-F1 on bootstrap OOB sets."""
    scores: list[float] = []
    indices = np.arange(len(y))
    for _ in range(n_bootstraps):
        train_indices = rng.choice(indices, size=len(indices), replace=True)
        out_of_bag = np.setdiff1d(indices, np.unique(train_indices))
        if len(out_of_bag) == 0 or y.iloc[train_indices].nunique() < 2:
            continue
        model = clone(estimator)
        model.fit(x.iloc[train_indices][list(features)], y.iloc[train_indices])
        prediction = model.predict(x.iloc[out_of_bag][list(features)])
        scores.append(f1_score(y.iloc[out_of_bag], prediction, average="macro", zero_division=0))
    if not scores:
        raise ValueError("No usable out-of-bag bootstrap samples were produced")
    return float(np.mean(scores)), float(np.std(scores, ddof=0))


def select_features_for_classifier(
    data: pd.DataFrame,
    estimator: Any,
    classifier_name: str,
    *,
    features: Sequence[str] = FEATURES,
    n_bootstraps: int = 20,
    min_improvement: float = 0.002,
    random_state: int = 42,
) -> FeatureSelectionResult:
    """Greedily remove features when bootstrap macro-F1 does not decrease."""
    missing = set(features) - set(data.columns)
    if missing or "label" not in data:
        raise ValueError(f"Data is missing required columns: {sorted(missing | {'label'} - set(data.columns))}")
    x = data
    y = data["label"]
    estimator = Pipeline([("scale", StandardScaler()), ("classifier", estimator)])
    rng = np.random.default_rng(random_state)
    active = list(features)
    history: list[dict[str, Any]] = []
    current_score, current_std = _bootstrap_score(estimator, x, y, active, rng, n_bootstraps)
    history.append({"classifier": classifier_name, "features": tuple(active), "removed": None,
                    "mean_f1": current_score, "std_f1": current_std})

    while len(active) > 1:
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

    return FeatureSelectionResult(classifier_name, tuple(active), current_score, pd.DataFrame(history))


def select_overall_features(
    results: Sequence[FeatureSelectionResult],
    *,
    min_classifiers: int | None = None,
) -> tuple[str, ...]:
    """Return features selected by the strongest consensus of the classifiers."""
    if not results:
        raise ValueError("At least one classifier result is required")
    threshold = min_classifiers or (len(results) + 1) // 2
    counts = pd.Series(0, index=FEATURES, dtype=int)
    for result in results:
        counts[list(result.selected_features)] += 1
    selected = tuple(feature for feature in FEATURES if counts[feature] >= threshold)
    if not selected:
        selected = tuple(counts.sort_values(ascending=False).head(1).index)
    return selected


def run_feature_selection(
    data: pd.DataFrame,
    classifiers: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> tuple[list[FeatureSelectionResult], tuple[str, ...]]:
    """Run selection for every classifier and return results plus consensus."""
    models = classifiers or default_classifiers(kwargs.pop("random_state", 42))
    results = [
        select_features_for_classifier(data, estimator, name, **kwargs)
        for name, estimator in models.items()
    ]
    return results, select_overall_features(results)
