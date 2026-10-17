# Code layout

- `data/` contains the shared SNR data folders.
- `01 Task/paul/` contains Paul's notebooks, legacy experiments, and import helper.
- `01 Task/vossi/` contains Vossi's notebooks, feature-selection pipeline, and import helper.
- `02 Task/Vossi/` contains the Task 2 notebooks.

# Features

| | F1 | F2 | F3 | F4 | F5 | F6 | F7 | F8 | Unique Comb |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Sag** | 🟢 | 🔴 | 🔴 | 🔴 | 🔴 | ⚪ | 🔴 | 🔴 | F1, F2, F7, F8 |
| **Sag_harm** | 🟢 | 🔴 | 🔴 | 🔴 | 🟢 | 🟢 | 🟢 | 🔴 | F1, F2, F7 |
| **Transient** | 🔴 | ⚪ | ⚪ | 🔴 | 🟢 | 🟢 | 🔴 | 🔴 | F1, F7 |
| **Swell_harm** | 🟢 | 🟢 | 🟢 | 🔴 | 🟢 | 🟢 | 🟢 | 🔴 | F1, F2, F7 |
| **Normal** | 🔴 | ⚪ | ⚪ | 🟢 | 🔴 | 🔴 | 🔴 | 🔴 | F1, F5 |
| **Flicker** | ⚪ | 🟢 | ⚪ | 🟢 | 🔴 | 🔴 | 🔴 | 🔴 | F1, F2, F4, F8 |
| **Harmonics** | 🔴 | ⚪ | ⚪ | 🟢 | 🟢 | 🟢 | 🟢 | 🔴 | F1, F4, F5, F7 |
| **Swell** | 🟢 | 🟢 | 🟢 | 🔴 | 🔴 | ⚪ | 🔴 | 🔴 | F3, F4, F7 |
| **Interruption** | 🟢 | 🔴 | 🔴 | 🔴 | ⚪ | ⚪ | 🔴 | 🟢 | F8 |




### Feature Naming Convention:
# 1. Positional mapping of raw CSV columns (0-7) to feature names (F1 - F8)
| Dictionary Index | Feature Name | Raw CSV Reference |
| :---: | :--- | :--- |
| **0** | `F2:std_TmA` | Col 1 |
| **1** | `F3:max_TmA` | Col 2 |
| **2** | `F4:min_TmA` | Col 3 |
| **3** | `F5:num_peaks` | Col 4 |
| **4** | `F6:std_FmA_3_7` | Col 5 |
| **5** | `F7:std_FmA_gt3` | Col 6 |
| **6** | `F1:avg_abs_ST_3rd` | Col 7 |
| **7** | `F8:near_zero_cnt` | Col 8 |

| Target Label | F1 Score | Features Vossi | Features Paul |
| :--- | :---: | :--- | :--- |
| **Sag** | 0.975402 | `[F1, F4, F8]` | `[F1, F2, F3, F4, F6, F7, F8]` |
| **Sag_harmonics** | 0.988134 | `[F1, F4]` | `[F1, F2, F3, F4, F6, F7, F8]` |
| **Transient** | 0.954811 | `[F1, F7]` | `[F1, F2, F6, F7]` |
| **Swell_harmonics** | 1.000000 | `[F1, F3]` | `[F1, F3, F4, F5, F6]` |
| **Normal** | 0.911013 | `[F1, F2, F5, F6, F7]` | `[F1, F2, F4, F5, F6, F7]` |
| **Flicker** | 0.938516 | `[F2, F3, F5, F7]` | `[F1, F2, F3, F4, F5, F6, F7]` |
| **Harmonics** | 0.996671 | `[F1, F2]` | `[F1, F2]` |
| **Swell** | 0.994088 | `[F1, F3]` | `[F1, F3, F4, F6, F8]` |
| **Interruption** | 0.987493 | `[F1, F8]` | `[F1, F2, F4, F6, F8]` |
