"""
Interactive prediction script for QKD protocol recommendation.
Accepts user inputs (architecture, distance, noise) and predicts the top 3 protocols.
"""

import os
import sys
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from preprocessing import load_preprocessing_artifacts, preprocess_input, ARCHITECTURES
from model import load_model


def predict_outputs(model, X):
    """Predict model outputs with a backend-compatible API."""
    try:
        prediction = model.predict(X, verbose=0)
    except TypeError:
        prediction = model.predict(X)

    prediction = np.asarray(prediction)
    if prediction.ndim == 1:
        prediction = prediction.reshape(-1, 1)
    return prediction

# Available architectures for user selection
ARCHITECTURE_OPTIONS = {
    '1': 'IonQ Aria',
    '2': 'IonQ Harmony',
    '3': 'Rigetti Aspen-M-3',
    '4': 'OQC Lucy'
}


def get_user_inputs():
    """Get architecture, distance and noise factor from user input."""
    print("\n" + "=" * 60)
    print("QKD Protocol Recommendation System")
    print("=" * 60)
    print("\nEnter the transmission parameters:\n")
    
    # Get architecture
    print("Select Architecture:")
    for key, value in ARCHITECTURE_OPTIONS.items():
        print(f"  {key}. {value}")
    
    while True:
        choice = input("\nEnter choice (1-4): ").strip()
        if choice in ARCHITECTURE_OPTIONS:
            architecture = ARCHITECTURE_OPTIONS[choice]
            break
        print("Invalid choice. Please enter 1, 2, 3, or 4.")
    
    # Get distance
    while True:
        try:
            distance = float(input("\nDistance (km) [5-200]: "))
            if 0 < distance <= 500:
                break
            print("Please enter a valid distance (0-500 km)")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    # Get noise factor
    while True:
        try:
            noise = float(input("Noise Factor [0.5-3.0]: "))
            if 0 < noise <= 5:
                break
            print("Please enter a valid noise factor (0-5)")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    return architecture, distance, noise


def predict_all_protocols(model, label_encoder, platform_encoder, scaler, architecture, distance, noise):
    """Predict secure key rate and transmission for all protocols with given architecture."""
    protocols = label_encoder.classes_
    results = []
    
    for protocol in protocols:
        try:
            X = preprocess_input(protocol, architecture, distance, noise, label_encoder, platform_encoder, scaler)
            prediction = predict_outputs(model, X)
            secure_key_rate = float(prediction[0, 0])
            transmission = float(prediction[0, 1]) if prediction.shape[1] > 1 else 0.0
            
            # Ensure non-negative values
            secure_key_rate = max(0, secure_key_rate)
            transmission = max(0, min(1, transmission))  # Transmission should be 0-1
            
            results.append({
                'protocol': protocol,
                'secure_key_rate': secure_key_rate,
                'transmission': transmission,
                'score': secure_key_rate * 0.7 + transmission * 0.3  # Weighted score
            })
            
        except Exception as e:
            print(f"Warning: Could not predict for {protocol}: {e}")
            continue
    
    return results


def display_results(results, architecture, distance, noise, top_n=3):
    """Display the top N protocol recommendations."""
    # Sort by secure key rate (primary) 
    sorted_results = sorted(results, key=lambda x: x['secure_key_rate'], reverse=True)
    
    print("\n" + "=" * 60)
    print(f"PREDICTION RESULTS")
    print(f"Architecture: {architecture}")
    print(f"Distance: {distance} km | Noise Factor: {noise}")
    print("=" * 60)
    
    print(f"\n{'='*60}")
    print(f"  TOP {top_n} RECOMMENDED PROTOCOLS")
    print(f"{'='*60}\n")
    
    for i, result in enumerate(sorted_results[:top_n], 1):
        print(f"  #{i} {result['protocol']}")
        print(f"     ├─ Secure Key Rate: {result['secure_key_rate']:.6f}")
        print(f"     └─ Transmission:    {result['transmission']:.6f}")
        print()
    
    # Also show comparison table
    print(f"{'─'*60}")
    print(f"  ALL PROTOCOLS COMPARISON")
    print(f"{'─'*60}")
    print(f"\n  {'Protocol':<15} {'Key Rate':>12} {'Transmission':>14}")
    print(f"  {'-'*15} {'-'*12} {'-'*14}")
    
    for result in sorted_results:
        print(f"  {result['protocol']:<15} {result['secure_key_rate']:>12.6f} {result['transmission']:>14.6f}")
    
    print()
    return sorted_results[:top_n]


def main():
    """Main function to run the prediction interface."""
    try:
        # Load model and preprocessing artifacts
        print("\nLoading model...")
        model = load_model()
        label_encoder, platform_encoder, scaler, _ = load_preprocessing_artifacts()
        print(f"Model loaded successfully!")
        print(f"Available protocols: {', '.join(label_encoder.classes_)}")
        print(f"Available architectures: {', '.join(ARCHITECTURES)}")
        
    except FileNotFoundError as e:
        print(f"\nError: Model not found. Please train the model first using train_model.py")
        print(f"Details: {e}")
        return 1
    except Exception as e:
        print(f"\nError loading model: {e}")
        return 1
    
    # Interactive loop
    while True:
        # Get user inputs
        architecture, distance, noise = get_user_inputs()
        
        # Make predictions
        print("\nAnalyzing protocols...")
        results = predict_all_protocols(model, label_encoder, platform_encoder, scaler, architecture, distance, noise)
        
        if not results:
            print("Error: Could not generate predictions.")
            continue
        
        # Display results
        top_protocols = display_results(results, architecture, distance, noise, top_n=3)
        
        # Ask if user wants to continue
        print("=" * 60)
        choice = input("\nWould you like to try different parameters? (y/n): ").strip().lower()
        if choice != 'y':
            print("\nThank you for using the QKD Protocol Recommendation System!")
            break
    
    return 0


def predict_single(architecture, distance, noise, verbose=True):
    """
    Programmatic interface for making predictions.
    
    Args:
        architecture: Architecture name (e.g., 'IonQ Aria')
        distance: Transmission distance in km
        noise: Noise factor
        verbose: Print results if True
    
    Returns:
        List of protocol predictions sorted by secure key rate
    """
    model = load_model()
    label_encoder, platform_encoder, scaler, _ = load_preprocessing_artifacts()
    
    results = predict_all_protocols(model, label_encoder, platform_encoder, scaler, architecture, distance, noise)
    sorted_results = sorted(results, key=lambda x: x['secure_key_rate'], reverse=True)
    
    if verbose:
        display_results(results, architecture, distance, noise)
    
    return sorted_results


if __name__ == '__main__':
    sys.exit(main())
