# Quantum Key Distribution (QKD) Protocol Recommendation System

A machine learning-based system that predicts secure key rates and transmission efficiency for various Quantum Key Distribution protocols based on hardware architecture, transmission distance, and noise factors.

## Overview

This project implements a neural network model that helps users select the optimal QKD protocol for their quantum communication setup. Given the hardware platform, transmission distance, and environmental noise level, the system recommends the top 3 protocols with the highest predicted secure key rates.

## Features

- **Multi-output prediction**: Predicts both secure key rate and transmission efficiency
- **Multiple protocol support**: BB84, BBM92, SARG04, Six-State, Decoy-BB84, E91, B92, AB-QKD, DS6-QKD, and EEPM-QKD
- **Hardware-aware**: Supports multiple quantum computing architectures
- **Interactive CLI**: User-friendly command-line interface for predictions
- **Visualization**: Training plots and performance metrics

## Supported Architectures

| Architecture | Platform Type |
|-------------|---------------|
| IonQ Aria | Trapped Ion |
| IonQ Harmony | Trapped Ion |
| Rigetti Aspen-M-3 | Superconducting |
| OQC Lucy | Superconducting |

## Supported Protocols

- **BB84**: Original QKD protocol
- **BBM92**: Entanglement-based protocol
- **SARG04**: Modified BB84 with improved photon-number-splitting attack resistance
- **Six-State**: Extended BB84 using three conjugate bases
- **Decoy-BB84**: BB84 with decoy states for enhanced security
- **E91**: Entanglement-based Ekert protocol
- **B92**: Two-state protocol variant
- **AB-QKD**: Adaptive-basis protocol variant
- **DS6-QKD**: Dynamic six-state protocol variant
- **EEPM-QKD**: Entanglement-enhanced prepare-and-measure protocol

## Installation

### Prerequisites

- Python 3.8+
- pip package manager

### Dependencies

```bash
pip install numpy pandas scikit-learn matplotlib
```

For GPU-accelerated training (optional):
```bash
pip install tensorflow
```

## Project Structure

```
Final Model/
├── data/                      # Training datasets
│   ├── bbm92_*.csv
│   ├── decoybb84_*.csv
│   ├── novel_protocols_*.csv
│   ├── qkd_final_*.csv
│   ├── sarg04_*.csv
│   └── sixstate_*.csv
├── result/                    # Model artifacts and outputs
│   ├── best_model.keras       # Trained Keras model
│   ├── sklearn_model.pkl      # Trained sklearn model (fallback)
│   ├── label_encoder.pkl      # Protocol encoder
│   ├── platform_encoder.pkl   # Architecture encoder
│   ├── scaler.pkl             # Feature scaler
│   ├── training_plots.png     # Training visualizations
│   └── training_results.json  # Performance metrics
├── preprocessing.py           # Data preprocessing pipeline
├── model.py                   # Model architecture definition
├── train_model.py             # Training script
├── predict.py                 # Interactive prediction CLI
├── test_model.py              # Testing and validation
├── MVP_TASKS.md               # Project tasks and requirements
└── README.md                  # This file
```

## Usage

### 1. Training the Model

```bash
python train_model.py
```

This will:
- Load and preprocess all datasets from `data/`
- Train the neural network model
- Save model artifacts to `result/`
- Generate training plots

### 2. Making Predictions

```bash
python predict.py
```

Interactive prompts will guide you through:
1. Select architecture (1-4)
2. Enter transmission distance (km)
3. Enter noise factor

**Example session:**
```
============================================================
QKD Protocol Recommendation System
============================================================

Select Architecture:
  1. IonQ Aria
  2. IonQ Harmony
  3. Rigetti Aspen-M-3
  4. OQC Lucy

Enter choice (1-4): 1

Distance (km) [5-200]: 50
Noise Factor [0.5-3.0]: 1.0

============================================================
PREDICTION RESULTS
Architecture: IonQ Aria
Distance: 50.0 km | Noise Factor: 1.0
============================================================

  TOP 3 RECOMMENDED PROTOCOLS

  #1 Decoy-BB84
     ├─ Secure Key Rate: 0.523456
     └─ Transmission:    0.794328

  #2 BB84
     ├─ Secure Key Rate: 0.492485
     └─ Transmission:    0.794328

  #3 BBM92
     ├─ Secure Key Rate: 0.481163
     └─ Transmission:    0.794328
```

### 3. Programmatic Usage

```python
from predict import predict_single

# Get predictions for specific parameters
results = predict_single(
    architecture='IonQ Aria',
    distance=50,
    noise=1.0,
    verbose=True
)

# Access top protocol
best_protocol = results[0]['protocol']
best_key_rate = results[0]['secure_key_rate']
```

### 4. Running Tests

```bash
python test_model.py
```

Generates a comprehensive test report including:
- Protocol prediction validation
- Distance and noise variation tests
- Edge case testing
- Comparison with actual data
- Visualization plots

## Input/Output Specification

### Inputs
| Parameter | Type | Range | Description |
|-----------|------|-------|-------------|
| Architecture | Categorical | 4 options | Quantum hardware platform |
| Distance | Float | 5-200 km | Transmission distance |
| Noise Factor | Float | 0.5-3.0 | Environmental noise level |

### Outputs
| Parameter | Type | Range | Description |
|-----------|------|-------|-------------|
| Secure Key Rate | Float | 0-1 | Predicted secure key generation rate |
| Transmission | Float | 0-1 | Channel transmission efficiency |

## Model Architecture

The system uses a neural network with:
- **Input layer**: 4 features (protocol, platform, distance, noise)
- **Hidden layers**: 128 → 64 → 32 → 16 neurons with ReLU activation
- **Batch normalization** and **dropout** for regularization
- **Output layer**: 2 neurons (secure_key_rate, transmission)

Falls back to sklearn ensemble (GradientBoosting + RandomForest + MLP) if TensorFlow is unavailable.

## Performance Metrics

Target criteria:
- ✓ Model achieves >90% R² on validation set
- ✓ All test cases pass with acceptable error margins
- ✓ Predictions fall within physically plausible ranges

## Data Sources

Training data includes simulated QKD experiments across:
- Multiple protocol types
- Various hardware platforms
- Distance ranges: 5-200 km
- Noise factors: 0.5-3.0

## License

This project is developed for academic purposes at PICT as part of the BE Quantum Teleportation Project.

## Authors

Developed as part of the Quantum Teleportation Project - Phase 2

## References

- Bennett, C. H., & Brassard, G. (1984). BB84 Protocol
- Bennett, C. H., Brassard, G., & Mermin, N. D. (1992). BBM92 Protocol
- Scarani, V., et al. (2004). SARG04 Protocol
- Bruß, D. (1998). Six-State Protocol
- Hwang, W. Y. (2003). Decoy State Protocol
