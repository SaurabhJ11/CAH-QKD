"""
Example: Using the Trial Deep Learning Model for Protocol Prediction
======================================================================

This script demonstrates how to:
1. Train the trial model (if not already trained)
2. Load the trained model
3. Make predictions for specific QKD conditions
4. Get top 3 protocol recommendations
"""

import os
import sys
import pickle

# Setup environment
import warnings
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trial import (
    train_trial_model,
    predict_top_3_protocols,
    TRIAL_MODEL_DIR,
    TRIAL_SCALER_FILE,
)


def example_1_train_model():
    """Example 1: Train the model from scratch"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Train the Model")
    print("="*70)
    
    print("\nTraining the neural network model...")
    model, scalers, metrics = train_trial_model()
    
    print("\nTraining complete! Metrics:")
    print(f"  - MAE (Mean Absolute Error): {metrics['mae']:.6f}")
    print(f"  - RMSE (Root Mean Squared Error): {metrics['rmse']:.6f}")
    print(f"  - R² Score: {metrics['r2']:.6f}")
    
    return model, scalers


def example_2_load_model():
    """Example 2: Load pre-trained model"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Load Pre-trained Model")
    print("="*70)
    
    model_path = os.path.join(TRIAL_MODEL_DIR, "trial_nn_model.h5")
    scaler_path = TRIAL_SCALER_FILE
    
    if not os.path.exists(model_path):
        print(f"\n[INFO] Model not found at {model_path}")
        print("[INFO] Training model first...")
        return None, None
    
    print(f"\nLoading model from: {model_path}")
    model = tf.keras.models.load_model(model_path)
    
    print(f"Loading scalers from: {scaler_path}")
    with open(scaler_path, 'rb') as f:
        scalers = pickle.load(f)
    
    print("[OK] Model and scalers loaded successfully!")
    return model, scalers


def example_3_single_prediction(model, scalers):
    """Example 3: Make a single prediction"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Single Prediction")
    print("="*70)
    
    if model is None:
        print("[SKIP] Model not available")
        return
    
    # Define scenario
    distance_km = 100
    noise_factor = 1.5
    platform = "ionq_aria"
    
    print(f"\nScenario:")
    print(f"  Distance: {distance_km} km")
    print(f"  Noise Factor: {noise_factor}x")
    print(f"  Platform: {platform}")
    
    # Get predictions
    try:
        top_3 = predict_top_3_protocols(model, scalers, distance_km, noise_factor, platform)
        
        print(f"\nTop 3 Recommended Protocols:")
        for i, rec in enumerate(top_3, 1):
            protocol = rec['protocol']
            rate = rec['secure_key_rate']
            print(f"  {i}. {protocol:<20} -> Secure Key Rate: {rate:.4f}")
    
    except Exception as e:
        print(f"[ERROR] Prediction failed: {e}")


def example_4_batch_predictions(model, scalers):
    """Example 4: Batch predictions across different distances"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Batch Predictions (Vary Distance)")
    print("="*70)
    
    if model is None:
        print("[SKIP] Model not available")
        return
    
    distances = [50, 100, 150, 200, 300]
    noise = 1.5
    platform = "ionq_aria"
    
    print(f"\nFixing: noise={noise}x, platform={platform}")
    print(f"Varying distances: {distances} km\n")
    
    for distance in distances:
        try:
            top_3 = predict_top_3_protocols(model, scalers, distance, noise, platform)
            top_protocol = top_3[0]
            
            print(f"Distance {distance:3d} km -> Best: {top_protocol['protocol']:<15} "
                  f"(rate: {top_protocol['secure_key_rate']:.4f})")
        
        except Exception as e:
            print(f"Distance {distance:3d} km -> ERROR: {e}")


def example_5_platform_comparison(model, scalers):
    """Example 5: Compare protocols across platforms"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Platform Comparison")
    print("="*70)
    
    if model is None:
        print("[SKIP] Model not available")
        return
    
    platforms = ["ionq_aria", "ionq_harmony", "rigetti_aspen_m3"]
    distance = 100
    noise = 1.5
    
    print(f"\nFixing: distance={distance} km, noise={noise}x")
    print(f"Comparing platforms: {platforms}\n")
    
    for platform in platforms:
        try:
            top_3 = predict_top_3_protocols(model, scalers, distance, noise, platform)
            top_protocol = top_3[0]
            
            print(f"{platform:<20} -> Best: {top_protocol['protocol']:<15} "
                  f"(rate: {top_protocol['secure_key_rate']:.4f})")
        
        except Exception as e:
            print(f"{platform:<20} -> ERROR: {e}")


def main():
    """Run all examples"""
    print("\n" + "#"*70)
    print("# Deep Learning QKD Protocol Recommender - Examples")
    print("#"*70)
    
    # Try to load existing model
    model, scalers = example_2_load_model()
    
    # If no model, train one
    if model is None:
        print("\n[INFO] Training model for examples...")
        model, scalers = example_1_train_model()
    
    # Run examples
    if model is not None and scalers is not None:
        example_3_single_prediction(model, scalers)
        example_4_batch_predictions(model, scalers)
        example_5_platform_comparison(model, scalers)
    
    print("\n" + "#"*70)
    print("# Examples Complete!")
    print("#"*70 + "\n")


if __name__ == "__main__":
    # Suppress TensorFlow warnings for cleaner output
    import logging
    logging.getLogger('tensorflow').setLevel(logging.ERROR)
    
    main()
