"""
Trial: Custom Deep Learning Model for Top-3 Protocol Recommendation
=====================================================================

This module trains a neural network model that predicts the secure key rate
for each QKD protocol given user inputs:
  - distance_km: Required link distance
  - noise_factor: Measured/estimated noise level
  - platform: Quantum hardware platform

The model then recommends the TOP 3 protocols with highest predicted key rates.

Architecture:
  - Input: (distance_km, noise_factor, platform_specs, protocol_id) -> 24 dims
  - Hidden: 128 -> 64 -> 32 neurons with ReLU + Dropout
  - Output: secure_key_rate prediction
  
Training Strategy:
  - Train 10 models (one per protocol) that each predict key rate
  - Ensemble-like approach: each protocol gets specialized attention
  - Normalize inputs & scale outputs for numerical stability
"""

import os
import json
import pickle
import warnings

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from keras import layers, callbacks, optimizers
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
warnings.filterwarnings('ignore')

from src.config import (
    DATA_DIR, MODELS_DIR, RESULTS_DIR,
    QKD_FINAL_CSV, SINGLE_PROTOCOL_CSVS, NOVEL_CSV,
    ALL_PROTOCOLS, PROTOCOL_TO_ID, PLATFORM_TYPE_TO_ID,
    PLATFORM_SPECS, COMMON_COLUMNS
)
from src.data_loader import load_unified_data


# ════════════════════════════════════════════════════════════════════════════
# CONFIGURATION & CONSTANTS
# ════════════════════════════════════════════════════════════════════════════

TRIAL_MODEL_DIR = os.path.join(MODELS_DIR, "trial_models")
TRIAL_SCALER_FILE = os.path.join(TRIAL_MODEL_DIR, "trial_scalers.pkl")
TRIAL_RESULTS_FILE = os.path.join(RESULTS_DIR, "trial_results.json")

RANDOM_STATE = 42

# Neural network hyperparameters
NN_EPOCHS = 100
NN_BATCH_SIZE = 32
NN_VAL_SPLIT = 0.2
NN_DROPOUT_RATE = 0.3
NN_LEARNING_RATE = 0.001


# ════════════════════════════════════════════════════════════════════════════
# DATA PREPARATION
# ════════════════════════════════════════════════════════════════════════════

def build_input_features(row: pd.Series, protocol: str) -> np.ndarray:
    """
    Build 24-dim feature vector for a single (protocol, conditions) pair.
    
    Features:
      - distance_km (1)
      - noise_factor (1)
      - transmission (1)
      - single_qubit_fidelity (1)
      - two_qubit_fidelity (1)
      - T1 (1)
      - T2 (1)
      - platform_type_encoded (1)
      - protocol_encoded (1)
      - dist_transmission (1)
      - fidelity_product (1)
      - coherence_ratio (1)
      - 10 one-hot protocol features (10)
    
    Args:
        row: pandas Series with qkd data
        protocol: protocol name (for one-hot encoding)
    
    Returns:
        24-dim feature vector
    """
    features = []
    
    # Physical parameters
    features.extend([
        float(row["distance_km"]),
        float(row["noise_factor"]),
        float(row["transmission"]),
        float(row["single_qubit_fidelity"]),
        float(row["two_qubit_fidelity"]),
        float(row["T1"]),
        float(row["T2"]),
    ])
    
    # Encoded platform type
    platform_type = row["platform_type"]
    features.append(float(PLATFORM_TYPE_TO_ID.get(platform_type, 0)))
    
    # Encoded protocol (input protocol)
    features.append(float(PROTOCOL_TO_ID.get(protocol, 0)))
    
    # Derived features
    dist_trans = float(row["distance_km"]) * float(row["transmission"])
    fid_prod = float(row["single_qubit_fidelity"]) * float(row["two_qubit_fidelity"])
    coh_ratio = float(row["T2"]) / (float(row["T1"]) + 1e-6)
    features.extend([dist_trans, fid_prod, coh_ratio])
    
    # One-hot protocol encoding (10 features)
    for p in ALL_PROTOCOLS:
        features.append(1.0 if p == protocol else 0.0)
    
    return np.array(features, dtype=np.float32)


def prepare_training_data():
    """
    Load, preprocess, and prepare training data for neural network.
    
    Returns:
        X_train, X_test, y_train, y_test: normalized feature/target arrays
        scalers: dict of input & output scalers
    """
    print("Loading unified data...")
    df = load_unified_data()
    
    # Remove rows with missing values in critical columns
    df = df.dropna(subset=["secure_key_rate", "noise_factor", "distance_km", "platform_type"])
    
    # Filter outliers (secure_key_rate should be [0, 1])
    df = df[(df["secure_key_rate"] >= 0) & (df["secure_key_rate"] <= 1)]
    
    print(f"Training data shape: {df.shape}")
    print(f"Protocols: {df['protocol'].unique()}")
    
    # Build feature matrix: for each row, create features for ALL protocols
    X_list = []
    y_list = []
    
    for idx, row in df.iterrows():
        actual_protocol = row["protocol"]
        actual_key_rate = float(row["secure_key_rate"])
        
        # For each protocol, create a feature vector
        for protocol in ALL_PROTOCOLS:
            features = build_input_features(row, protocol)
            X_list.append(features)
            
            # Target: if this is the actual protocol, use actual key rate
            # Otherwise, we're learning the model's predictions for other protocols
            # For now, we'll use the actual key rate as the ground truth
            # (model learns: given protocol & conditions, predict its key rate)
            y_list.append(actual_key_rate if protocol == actual_protocol else 0.0)
    
    X = np.array(X_list, dtype=np.float32)
    y = np.array(y_list, dtype=np.float32)
    
    print(f"Total training samples: {X.shape[0]} (6 protocols × data rows)")
    
    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE
    )
    
    # Normalize inputs
    input_scaler = StandardScaler()
    X_train_scaled = input_scaler.fit_transform(X_train)
    X_test_scaled = input_scaler.transform(X_test)
    
    # Normalize outputs
    output_scaler = MinMaxScaler(feature_range=(0, 1))
    y_train_scaled = output_scaler.fit_transform(y_train.reshape(-1, 1)).ravel()
    y_test_scaled = output_scaler.transform(y_test.reshape(-1, 1)).ravel()
    
    scalers = {
        "input": input_scaler,
        "output": output_scaler,
    }
    
    return X_train_scaled, X_test_scaled, y_train_scaled, y_test_scaled, scalers


# ════════════════════════════════════════════════════════════════════════════
# NEURAL NETWORK MODEL
# ════════════════════════════════════════════════════════════════════════════

def build_nn_model(input_dim: int = 24) -> keras.Model:
    """
    Build a neural network for secure key rate prediction.
    
    Args:
        input_dim: Number of input features (24)
    
    Returns:
        Compiled Keras model
    """
    model = keras.Sequential([
        layers.Input(shape=(input_dim,)),
        
        # Dense block 1
        layers.Dense(128, activation='relu', kernel_initializer='he_normal'),
        layers.BatchNormalization(),
        layers.Dropout(NN_DROPOUT_RATE),
        
        # Dense block 2
        layers.Dense(64, activation='relu', kernel_initializer='he_normal'),
        layers.BatchNormalization(),
        layers.Dropout(NN_DROPOUT_RATE),
        
        # Dense block 3
        layers.Dense(32, activation='relu', kernel_initializer='he_normal'),
        layers.BatchNormalization(),
        layers.Dropout(NN_DROPOUT_RATE),
        
        # Output layer (normalized to [0, 1])
        layers.Dense(1, activation='sigmoid'),
    ])
    
    model.compile(
        optimizer=optimizers.Adam(learning_rate=NN_LEARNING_RATE),
        loss='mse',
        metrics=['mae', 'mse']
    )
    
    return model


def train_nn_model(X_train, X_test, y_train, y_test):
    """
    Train the neural network model with early stopping.
    
    Args:
        X_train, X_test: Normalized feature arrays
        y_train, y_test: Normalized target arrays
    
    Returns:
        Trained model and history
    """
    print("\n" + "="*70)
    print("Training Neural Network Model")
    print("="*70)
    
    model = build_nn_model(input_dim=X_train.shape[1])
    
    # Early stopping callback
    early_stop = callbacks.EarlyStopping(
        monitor='val_loss',
        patience=15,
        restore_best_weights=True,
        verbose=1
    )
    
    # Train
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=NN_EPOCHS,
        batch_size=NN_BATCH_SIZE,
        callbacks=[early_stop],
        verbose=1
    )
    
    return model, history


# ════════════════════════════════════════════════════════════════════════════
# INFERENCE & TOP-3 RECOMMENDATION
# ════════════════════════════════════════════════════════════════════════════

def predict_top_3_protocols(
    model: keras.Model,
    scalers: dict,
    distance_km: float,
    noise_factor: float,
    platform: str
) -> list[dict]:
    """
    Predict top 3 protocols and their secure key rates given user inputs.
    
    Args:
        model: Trained neural network
        scalers: Input/output scalers
        distance_km: Link distance in km
        noise_factor: Environmental noise multiplier
        platform: Quantum hardware platform (e.g., "ionq_aria")
    
    Returns:
        List of 3 dicts: [{"protocol": str, "secure_key_rate": float}, ...]
    """
    # Validate platform
    if platform not in PLATFORM_SPECS:
        raise ValueError(f"Unknown platform: {platform}. Available: {list(PLATFORM_SPECS.keys())}")
    
    # Get platform specs
    specs = PLATFORM_SPECS[platform]
    platform_type = specs["platform_type"]
    
    # Create a temporary row with specs
    temp_row = pd.Series({
        "distance_km": distance_km,
        "noise_factor": noise_factor,
        "transmission": np.exp(-0.2 * distance_km),  # Realistic transmission decay
        "single_qubit_fidelity": specs["single_qubit_fidelity"],
        "two_qubit_fidelity": specs["two_qubit_fidelity"],
        "T1": specs["T1"],
        "T2": specs["T2"],
        "platform_type": platform_type,
    })
    
    predictions = []
    
    for protocol in ALL_PROTOCOLS:
        # Build 24-dim feature vector
        features = build_input_features(temp_row, protocol)
        
        # Normalize using training scalers
        features_scaled = scalers["input"].transform([features])
        
        # Predict (scaled output)
        y_pred_scaled = model.predict(features_scaled, verbose=0)[0, 0]
        
        # Inverse transform to get actual key rate
        y_pred = scalers["output"].inverse_transform([[y_pred_scaled]])[0, 0]
        
        # Clip to valid range
        y_pred = np.clip(y_pred, 0.0, 1.0)
        
        predictions.append({
            "protocol": protocol,
            "secure_key_rate": float(y_pred),
        })
    
    # Sort by secure_key_rate and return top 3
    predictions.sort(key=lambda x: x["secure_key_rate"], reverse=True)
    return predictions[:3]


# ════════════════════════════════════════════════════════════════════════════
# EVALUATION & METRICS
# ════════════════════════════════════════════════════════════════════════════

def evaluate_model(model, X_test, y_test, scalers):
    """
    Evaluate model performance on test set.
    
    Args:
        model: Trained model
        X_test: Test features (normalized)
        y_test: Test targets (normalized)
        scalers: Input/output scalers
    
    Returns:
        metrics dict
    """
    print("\n" + "="*70)
    print("Model Evaluation")
    print("="*70)
    
    # Predictions
    y_pred_scaled = model.predict(X_test, verbose=0).ravel()
    
    # Inverse transform to actual scale
    y_test_actual = scalers["output"].inverse_transform(y_test.reshape(-1, 1)).ravel()
    y_pred_actual = scalers["output"].inverse_transform(y_pred_scaled.reshape(-1, 1)).ravel()
    
    # Clip to valid range
    y_pred_actual = np.clip(y_pred_actual, 0.0, 1.0)
    
    # Metrics
    mse = mean_squared_error(y_test_actual, y_pred_actual)
    mae = mean_absolute_error(y_test_actual, y_pred_actual)
    r2 = r2_score(y_test_actual, y_pred_actual)
    rmse = np.sqrt(mse)
    
    metrics = {
        "mse": float(mse),
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": float(r2),
    }
    
    print(f"  MAE:  {mae:.6f}")
    print(f"  RMSE: {rmse:.6f}")
    print(f"  R²:   {r2:.6f}")
    
    return metrics


# ════════════════════════════════════════════════════════════════════════════
# MAIN TRAINING PIPELINE
# ════════════════════════════════════════════════════════════════════════════

def train_trial_model():
    """
    Main training pipeline: prepare data -> build & train model -> evaluate -> save.
    """
    print("\n" + "="*70)
    print("Trial: Custom Deep Learning Model for QKD Protocol Recommendation")
    print("="*70)
    
    # 1. Prepare data
    X_train, X_test, y_train, y_test, scalers = prepare_training_data()
    
    # 2. Build & train model
    model, history = train_nn_model(X_train, X_test, y_train, y_test)
    
    # 3. Evaluate
    metrics = evaluate_model(model, X_test, y_test, scalers)
    
    # 4. Save artifacts
    os.makedirs(TRIAL_MODEL_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    model_path = os.path.join(TRIAL_MODEL_DIR, "trial_nn_model.h5")
    model.save(model_path)
    print(f"\n[OK] Model saved: {model_path}")
    
    with open(TRIAL_SCALER_FILE, "wb") as f:
        pickle.dump(scalers, f)
    print(f"[OK] Scalers saved: {TRIAL_SCALER_FILE}")
    
    with open(TRIAL_RESULTS_FILE, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[OK] Results saved: {TRIAL_RESULTS_FILE}")
    
    return model, scalers, metrics


# ════════════════════════════════════════════════════════════════════════════
# INTERACTIVE INFERENCE
# ════════════════════════════════════════════════════════════════════════════

def interactive_demo(model, scalers):
    """
    Interactive demo: get user inputs and recommend top 3 protocols.
    """
    print("\n" + "="*70)
    print("Interactive Top-3 Protocol Recommendation Demo")
    print("="*70)
    
    available_platforms = list(PLATFORM_SPECS.keys())
    print(f"\nAvailable quantum platforms: {available_platforms}")
    print(f"Available protocols: {ALL_PROTOCOLS}\n")
    
    while True:
        try:
            # Get user inputs
            distance = float(input("Enter distance (km, e.g., 100): "))
            noise = float(input("Enter noise factor (e.g., 1.5): "))
            platform = input(f"Enter platform ({', '.join(available_platforms)}): ").strip()
            
            # Validate inputs
            if distance <= 0:
                print("[ERROR] Distance must be positive")
                continue
            if noise <= 0:
                print("[ERROR] Noise factor must be positive")
                continue
            if platform not in available_platforms:
                print(f"[ERROR] Unknown platform. Choose from: {available_platforms}")
                continue
            
            # Get recommendations
            print(f"\n>>> Predicting for: distance={distance}km, noise={noise}x, platform={platform}")
            top_3 = predict_top_3_protocols(model, scalers, distance, noise, platform)
            
            # Display results
            print("\n" + "="*70)
            print("TOP 3 RECOMMENDED PROTOCOLS")
            print("="*70)
            for i, rec in enumerate(top_3, 1):
                rate = rec["secure_key_rate"]
                protocol = rec["protocol"]
                bar = "#" * int(rate * 50) + "-" * (50 - int(rate * 50))
                print(f"\n{i}. {protocol}")
                print(f"   Secure Key Rate: {rate:.4f}")
                print(f"   {bar} {rate*100:.2f}%")
            print("\n" + "="*70)
            
        except ValueError as e:
            print(f"[ERROR] Invalid input: {e}")
        except KeyboardInterrupt:
            print("\n\n[INFO] Exiting demo...")
            break


# ════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Train the model
    model, scalers, metrics = train_trial_model()
    
    # Optional: Run interactive demo
    print("\n" + "="*70)
    demo_choice = input("Run interactive demo? (y/n): ").strip().lower()
    if demo_choice == 'y':
        interactive_demo(model, scalers)
    
    print("\n[OK] Trial training complete!")
