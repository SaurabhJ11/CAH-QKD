# Copilot Instructions for QKD Protocol Recommendation System

## Project Overview

This is a machine learning system that predicts secure key rates and transmission efficiency for Quantum Key Distribution (QKD) protocols. Given a quantum hardware architecture, transmission distance, and environmental noise, the model recommends the top 3 protocols with the highest predicted secure key rates.

## Build, Test & Run Commands

### Core Commands

```bash
# Data preprocessing and model training
python train_model.py

# Interactive prediction interface
python predict.py

# Comprehensive model testing and validation
python test_model.py

# Data preprocessing only (generates encoders and scalers)
python preprocessing.py

# Verify model creation without training
python model.py
```

### Running Individual Tests

The test suite in `test_model.py` runs multiple test categories (edge cases, protocol validation, output consistency). To run it and get a test report:

```bash
python test_model.py
```

This generates:
- Console output with pass/fail statistics
- `result/test_report.json` - Detailed test results
- `result/test_visualizations.png` - Prediction vs. actual plots

## Architecture Overview

### Data Pipeline
1. **Data Loading** (`preprocessing.py`): Loads 6+ CSV datasets from `data/` directory (one per QKD protocol)
2. **Feature Engineering**: Combines datasets, encodes protocols/platforms, scales numerical features
3. **Train/Test Split**: 80/20 split with fixed random seed (42) for reproducibility

### Model Architecture
- **Dual-backend support**: TensorFlow/Keras (primary) or sklearn ensemble (fallback)
- **Keras model** (when TensorFlow available):
  - 4 inputs: [protocol_encoded, platform_encoded, distance_km_scaled, noise_factor_scaled]
  - 4 hidden layers: 128→64→32→16 neurons with ReLU activation
  - Batch normalization + dropout (0.1-0.2) for regularization
  - 2 outputs: [secure_key_rate, transmission]
  
- **Sklearn ensemble** (fallback):
  - 3 models per output: GradientBoosting (40%), RandomForest (30%), MLP (30%)
  - Weighted average of 3 models for robustness

### Input/Output Specification

**Inputs:**
- `architecture`: One of 4 platforms (IonQ Aria, IonQ Harmony, Rigetti Aspen-M-3, OQC Lucy)
- `distance`: 5-200 km (float)
- `noise_factor`: 0.5-3.0 (float)

**Outputs:**
- `secure_key_rate`: 0-1 range (predicted quantum key generation rate)
- `transmission`: 0-1 range (channel transmission efficiency)

## Key Conventions

### File Organization
- `preprocessing.py`: Data loading, cleaning, encoding, scaling—all preprocessing artifacts saved to `result/`
- `model.py`: Model creation, compilation, training callbacks, and save/load logic
- `train_model.py`: Full training pipeline with metrics calculation and visualization
- `predict.py`: User-facing CLI with protocol ranking
- `test_model.py`: Validation suite with edge cases and performance benchmarking

### Data Encoding
- **Protocols**: Label-encoded to 0-9 (BB84, BBM92, SARG04, Six-State, Decoy-BB84, E91, B92, AB-QKD, DS6-QKD, EEPM-QKD)
- **Platforms**: Label-encoded to 0-3, user-friendly names mapped in `PLATFORM_MAPPING`
- **Numerical features**: StandardScaled (mean=0, std=1)
- **All encoders/scalers**: Persisted in `result/` for inference consistency

### Artifacts Structure (`result/` directory)
```
result/
├── best_model.keras           # Trained Keras model (if TensorFlow available)
├── sklearn_model.pkl          # Fallback sklearn ensemble model
├── label_encoder.pkl          # Protocol name → numeric encoding
├── platform_encoder.pkl       # Architecture name → numeric encoding
├── scaler.pkl                 # StandardScaler for distance/noise
├── data_stats.pkl             # Input ranges and protocol list (for inference validation)
├── training_results.json      # Hyperparameters, metrics, and history
├── training_plots.png         # 6-subplot visualization (loss, predictions, errors, metrics)
├── test_report.json           # Detailed test results
└── test_visualizations.png    # Test prediction vs. actual plots
```

### Reproducibility & Random Seeds
- `numpy.random.seed(42)` set in both `train_model.py` and `test_model.py`
- TensorFlow seed also set when available
- This ensures consistent results across runs

### Multi-Output Prediction
All outputs are regression tasks (not classification):
- Model predicts continuous values for both secure_key_rate and transmission
- Metrics calculated independently per output (MSE, MAE, R²) then averaged
- Accuracy metric: % of predictions within 10% of actual value

### Protocol Ranking
In `predict.py`, all 10 protocols are predicted for a given architecture + distance + noise combination, then sorted by secure_key_rate (descending) to show top 3 recommendations.

### Error Handling
- Missing values dropped during preprocessing
- Extreme outliers removed (>3 std deviations)
- Negative secure key rates filtered out
- Platform/protocol names auto-mapped to internal format (case-flexible)
- Fallback to sklearn model if TensorFlow import fails

## Dependencies

**Required:**
- numpy, pandas, scikit-learn, matplotlib

**Optional:**
- tensorflow (for GPU-accelerated training; sklearn fallback available)

Install with: `pip install numpy pandas scikit-learn matplotlib`

Or for GPU support: `pip install tensorflow numpy pandas scikit-learn matplotlib`

## Success Criteria (MVP)

- ✓ Model achieves >90% R² on validation/test set
- ✓ All test cases pass with acceptable error margins
- ✓ Predictions fall within physically plausible ranges (0-1)
- ✓ Reproducible results (fixed random seeds)
- ✓ Inference works with both TensorFlow and sklearn backends

## Data Sources

Training data in `data/` includes simulated QKD experiments:
- `bbm92_*.csv`, `decoybb84_*.csv`, `qkd_final_*.csv`, `sarg04_*.csv`, `sixstate_*.csv`, `novel_protocols_*.csv`
- Each file: protocol, platform, distance_km, noise_factor, secure_key_rate, transmission columns
- Distance range: 5-200 km; Noise factor: 0.5-3.0
