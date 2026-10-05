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
