# Code to hand in

This folder contains the notebooks and helper code used for both tasks of the
machine-learning project. The included `data/` directory makes the hand-in
self-contained.

## Requirements

Use Python 3.10 or newer. Install the packages listed in
[`requirements.txt`](requirements.txt), then start Jupyter from this folder:

```bash
cd "Code/Code to hand in"
python -m pip install -r requirements.txt
jupyter notebook
```

The notebooks use fixed random seeds where model selection or train-test
splitting is stochastic. They should be run from any working directory:
their data-loading code searches for the included hand-in data and then falls
back to the repository-level `Code/data` directory.

## Task 1: feature analysis

Run the notebooks in this order:

1. `01 Task/Feature_visualization.ipynb` creates the feature-distribution
   figure for the noiseless data.
2. `01 Task/Feature_statistical_interpretation.ipynb` computes one-vs-rest
   ANOVA F-scores and mutual-information scores and creates the relevance
   heatmaps.
3. `01 Task/Feature_elimination_bi_class.ipynb` performs greedy feature
   elimination with four classifiers and majority-votes the selected features.

`01 Task/bagging_feature_selection.py` contains the reusable implementation of
the feature-selection procedure. `01 Task/import_folder.py` contains the
shared CSV importer and the F1--F8 feature mapping.

## Task 2: multiclass classification

Run the random-search notebooks for the decision tree, random forest, and
multilayer perceptron. Finally, run
`02 Task/Final_Bagged_Model_Task_2.ipynb` to train the selected models and
evaluate their soft-voting ensemble on the held-out test set.

The random-search and final-model notebooks can take several minutes because
they evaluate multiple hyperparameter configurations with cross-validation.
Existing notebook outputs document the expected results; rerunning a notebook
replaces those outputs.
