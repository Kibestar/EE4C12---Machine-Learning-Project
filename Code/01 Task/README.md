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



| Feature 1 | F1 | F2 | F3 | F4 | F5 | F6 | F7 | F8 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Normal** | False | False | False | False | False | False | False | False |
| **Sag** | False | Maybe True | False | True | True | False | maybe True | False |
| **Swell** | False | maybe True | True | False | True | False | maybe True | False |
| **Interrupt** | False | True | False | True | True | False | maybe True | True |
| **Osc. transient** | maybe True | maybe True | maybe True | False | False | maybe False | True | maybe True |
| **Harmonics** | True | False | False | False | False | True | True | False |
| **Voltage fluctuation** | False | maybe True | maybe True | maybe True | False | False | False | False |
| **Sag w. Harmonics** | True | maybe True | False | True | True | True | True | False |
| **Swell w. Harmonics** | True | maybe True | True | False | True | True | True | False |