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


LogReg

      Target Label  F1 Score               Features to Use
0              Sag  0.900184              [F1, F4, F6, F8]
1    Sag_harmonics  0.718898  [F1, F3, F4, F5, F6, F7, F8]
2        Transient  0.892980              [F1, F2, F5, F7]
3  Swell_harmonics  0.757450      [F1, F2, F3, F5, F6, F7]
4           Normal  0.657236                  [F1, F2, F7]
5          Flicker  0.541868                  [F2, F6, F7]
6        Harmonics  0.932776                      [F1, F2]
7            Swell  0.940210                      [F1, F3]
8     Interruption  0.961885                      [F1, F8]

Svm Lin
      Target Label  F1 Score                   Features to Use
0              Sag  0.912313                  [F1, F4, F6, F8]
1    Sag_harmonics  0.800535          [F1, F2, F3, F6, F7, F8]
2        Transient  0.940797                          [F1, F7]
3  Swell_harmonics  0.855661                      [F1, F3, F6]
4           Normal  0.799740                  [F2, F3, F7, F8]
5          Flicker  0.000000  [F1, F2, F3, F4, F5, F6, F7, F8]
6        Harmonics  0.978596                          [F1, F2]
7            Swell  0.940436                          [F1, F3]
8     Interruption  0.972670                          [F1, F8]

Svm rbf
      Target Label  F1 Score       Features to Use
0              Sag  0.975402          [F1, F4, F8]
1    Sag_harmonics  0.988134              [F1, F4]
2        Transient  0.954811              [F1, F7]
3  Swell_harmonics  1.000000              [F1, F3]
4           Normal  0.911013  [F1, F2, F5, F6, F7]
5          Flicker  0.938516      [F2, F3, F5, F7]
6        Harmonics  0.996671              [F1, F2]
7            Swell  0.994088              [F1, F3]
8     Interruption  0.987493              [F1, F8]

SVM poly
      Target Label  F1 Score   Features to Use
0              Sag  0.874806  [F1, F4, F6, F8]
1    Sag_harmonics  0.854532  [F1, F3, F4, F6]
2        Transient  0.915102      [F1, F2, F7]
3  Swell_harmonics  0.966151      [F1, F3, F4]
4           Normal  0.747189  [F1, F2, F3, F7]
5          Flicker  0.738517      [F1, F5, F7]
6        Harmonics  0.993342          [F1, F2]
7            Swell  0.956161      [F1, F3, F4]
8     Interruption  0.980003          [F1, F8]