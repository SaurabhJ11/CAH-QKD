# Trial Model: Deep Learning Protocol Recommender

## Overview

`trial.py` implements a custom **neural network model** that recommends the **top 3 QKD protocols** with their predicted secure key rates, given only:
- **distance_km**: Link distance in kilometers
- **noise_factor**: Environmental noise multiplier (e.g., 1.5×)
- **platform**: Quantum hardware platform (e.g., "ionq_aria")

## Model Architecture

### Input Layer (24 features)
The model automatically constructs feature vectors from user inputs:
- **Physical parameters** (7): distance, noise, transmission, single/two-qubit fidelity, T1, T2
- **Encoded platform** (1): platform_type (superconducting/trapped_ion)
- **Encoded protocol** (1): which protocol being evaluated
- **Derived features** (3): distance×transmission, fidelity product, coherence ratio (T2/T1)
- **One-hot protocol encoding** (10): indicator for each of the 10 protocols

### Hidden Architecture
```
Input (24) → Dense(128, ReLU) → BatchNorm → Dropout(0.3)
           → Dense(64, ReLU)  → BatchNorm → Dropout(0.3)
           → Dense(32, ReLU)  → BatchNorm → Dropout(0.3)
           → Output (Sigmoid) [0, 1]
```

### Key Features
- ✅ **Batch Normalization**: Stabilizes training across protocols
- ✅ **Dropout**: Prevents overfitting with 30% dropout rate
- ✅ **Early Stopping**: Stops training when validation loss plateaus
- ✅ **Input/Output Scaling**: StandardScaler for inputs, MinMaxScaler for targets
- ✅ **Ensemble Approach**: Tests all 10 protocols for each input combination

## Training Data

The model trains on unified data from 6 QKD datasets:
- `qkd_final_20260209_085953.csv`: Multi-protocol base data
- `bbm92_20260210_205349.csv`: BBM92 protocol
- `decoybb84_20260210_230545.csv`: Decoy BB84
- `sarg04_20260210_133117.csv`: SARG04
- `sixstate_20260210_004703.csv`: Six-State
- `novel_protocols_20260303_002909.csv`: Novel protocols

## Quick Start

### 1. Install Dependencies
```bash
pip install tensorflow scikit-learn numpy pandas -q
```

### 2. Train the Model
```bash
python trial.py
```

This will:
1. Load and preprocess all QKD data
2. Build 24-dim feature vectors for each (protocol, conditions) pair
3. Train the neural network with early stopping
4. Evaluate on test set (MAE, RMSE, R²)
5. Save artifacts:
   - `models/trial_models/trial_nn_model.h5` - Trained model
   - `models/trial_models/trial_scalers.pkl` - Input/output scalers
   - `results/trial_results.json` - Performance metrics

### 3. Interactive Demo
When training completes, you can run the interactive demo:
```
Run interactive demo? (y/n): y

Available quantum platforms: ['ionq_aria', 'ionq_harmony', 'rigetti_aspen_m3', ...]
Available protocols: ['AB-QKD', 'B92', 'BB84', 'BBM92', ...]

Enter distance (km, e.g., 100): 150
Enter noise factor (e.g., 1.5): 1.5
Enter platform (ionq_aria, ionq_harmony, ...): ionq_aria

🔄 Predicting for: distance=150km, noise=1.5x, platform=ionq_aria

============================================================================
TOP 3 RECOMMENDED PROTOCOLS
============================================================================

1. BB84
   Secure Key Rate: 0.4852
   ████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░ 48.52%

2. Decoy-BB84
   Secure Key Rate: 0.3921
   ██████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 39.21%

3. SARG04
   Secure Key Rate: 0.3215
   ████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 32.15%

============================================================================
```

## Using the Model Programmatically

Once trained, load and use the model in your own code:

```python
import os
import pickle
import tensorflow as tf
from trial import predict_top_3_protocols

# Load model & scalers
model = tf.keras.models.load_model("models/trial_models/trial_nn_model.h5")
with open("models/trial_models/trial_scalers.pkl", "rb") as f:
    scalers = pickle.load(f)

# Get top 3 protocols for specific conditions
recommendations = predict_top_3_protocols(
    model=model,
    scalers=scalers,
    distance_km=200,
    noise_factor=2.0,
    platform="ionq_aria"
)

# Print results
for i, rec in enumerate(recommendations, 1):
    print(f"{i}. {rec['protocol']}: {rec['secure_key_rate']:.4f}")
```

## Model Outputs

### Per-protocol Prediction
The model predicts a continuous `secure_key_rate` (0.0 to 1.0) for each protocol:
- **0.9+**: Excellent performance
- **0.7-0.9**: Good performance
- **0.5-0.7**: Moderate performance
- **<0.5**: Poor/marginal performance

### Top-3 Ranking
Returns the 3 protocols with highest predicted secure key rates, sorted in descending order.

## Supported Platforms

The model recognizes these quantum hardware platforms:
- `ionq_aria` (trapped-ion, high-fidelity) - **Recommended for long-distance**
- `ionq_harmony` (trapped-ion, balanced)
- `rigetti_aspen_m3` (superconducting)
- `rigetti_aspen_m2` (superconducting)
- `d_wave_advantage` (superconducting, annealing)
- `quantinuum_h1` (trapped-ion, high-precision)
- `google_sycamore` (superconducting)
- `ibm_falcon` (superconducting)

## Available 10 QKD Protocols

1. **AB-QKD** - Measurement-device-independent variant
2. **B92** - Simplified two-state protocol
3. **BB84** - Classic prepare-measure (standard baseline)
4. **BBM92** - Entanglement-based variant
5. **DS6-QKD** - Decoy state protocol
6. **Decoy-BB84** - BB84 with decoy states
7. **E91** - Eckerт protocol (entanglement-based)
8. **EEPM-QKD** - Event-ready protocol
9. **SARG04** - Scarani-Acín-Renner-Gisin
10. **Six-State** - Extended 6-state protocol

## Performance Metrics

After training, check `results/trial_results.json` for:
- **MAE** (Mean Absolute Error): Typical prediction error
- **RMSE** (Root Mean Squared Error): Penalizes large errors
- **R²**: Fraction of variance explained (0-1)

Example:
```json
{
  "mse": 0.00524,
  "mae": 0.0521,
  "rmse": 0.0724,
  "r2": 0.8743
}
```

## Advanced: Retraining with New Data

To retrain with additional QKD data:

1. Add CSV files to `data/` directory
2. Update `src/config.py` if needed to reference new files
3. Run `python trial.py` again to rebuild with expanded dataset

The model will automatically:
- Load all CSV files via `load_unified_data()`
- Create feature vectors for all (protocol, conditions) combinations
- Scale and split data (80/20 train/test)
- Train with early stopping
- Save updated model artifacts

## Troubleshooting

### Issue: "Unknown platform" error
**Solution**: Ensure platform name matches exactly (case-sensitive). See list above.

### Issue: Low model accuracy (R² < 0.5)
**Likely causes**:
- Insufficient training data or high noise levels
- Extreme input values (very high distance/noise)
- Outliers in QKD data not filtered

**Fix**: Add data filtering in `prepare_training_data()` to remove outliers.

### Issue: All predictions near 0.5
**Cause**: Model may not be trained yet or scalers not loaded correctly.

**Fix**: Retrain: `python trial.py`

### Issue: Model takes too long to train
**Optimization**:
- Reduce `NN_EPOCHS` in `trial.py` (e.g., to 50)
- Increase `NN_BATCH_SIZE` (e.g., to 64)
- Use GPU acceleration with CUDA

## Hyperparameters

Edit at top of `trial.py`:
```python
NN_EPOCHS = 100              # Training epochs
NN_BATCH_SIZE = 32            # Batch size
NN_VAL_SPLIT = 0.2            # Validation fraction
NN_DROPOUT_RATE = 0.3         # Dropout probability
NN_LEARNING_RATE = 0.001      # Adam learning rate
```

## Files Generated

After training, the following files are created:
```
models/
  trial_models/
    trial_nn_model.h5         # Trained TensorFlow model
    trial_scalers.pkl         # Input/output scalers for normalization

results/
  trial_results.json          # Performance metrics
```

## Next Steps

1. **Validate predictions** against held-out test data
2. **Deploy** model via `predict.py` for real-time recommendations
3. **Monitor** accuracy over time as new QKD experiments accumulate
4. **Fine-tune** hyperparameters based on validation results
5. **Extend** to support dynamic platform specifications

---

**Model Version**: Trial v1 (Custom Deep Learning)  
**Training Date**: [Generated on training run]  
**Last Updated**: 2026-03-24
