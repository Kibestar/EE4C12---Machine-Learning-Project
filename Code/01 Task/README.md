# Features
### Voltage Sag
- Magnitude Drop (Time)

### Voltage Swell
- Magnitude Increase (Time)

### Interruption
- Magnitude Drop (Time Long)

### Oscillation Transient
- High harmonic for a specific time

### Harmonics
- Harmonics all the time

### Voltage Fluctuations
- Varying Voltage over time

### Voltage Sag with Harmonics
- Magnitude decrease
- Magnitude change (freq.)

### Voltage Swell with Harmonics
- Magnitude increase (time)
- Magnitude change (freq.)



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



Target Label  Accuracy  Precision    Recall  F1 Score
2        Transient  0.996283   0.983871  0.997908  0.990755
8     Interruption  0.996283   0.983871  0.997908  0.990755
4           Normal  0.985130   0.941176  0.991632  0.964531
6        Harmonics  0.985130   0.962483  0.962483  0.962483
7            Swell  0.981413   0.989754  0.916667  0.949369
3  Swell_harmonics  0.966543   0.981855  0.850000  0.902524
1    Sag_harmonics  0.962825   0.927904  0.877057  0.900341
0              Sag  0.947955   0.909551  0.810391  0.850981
5          Flicker  0.936803   0.833654  0.862413  0.847185