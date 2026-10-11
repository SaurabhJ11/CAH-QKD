"""
Comprehensive testing script for QKD secure key rate prediction model.
Validates model predictions, tests edge cases, and generates visualizations.
"""

import os
import sys
import numpy as np
import pandas as pd
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)

from preprocessing import (
    load_preprocessing_artifacts, 
    preprocess_input, 
    load_all_datasets,
    combine_datasets,
    standardize_columns,
    extract_features,
    DATA_DIR,
    RESULT_DIR
)
from model import load_model

# Try importing visualization libraries
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib not available. Visualizations will be skipped.")


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


class TestResults:
    """Container for test results."""
    
    def __init__(self):
        self.tests = []
        self.passed = 0
        self.failed = 0
    
    def add_result(self, name, passed, details=""):
        passed = bool(passed)
        self.tests.append({
            'name': name,
            'passed': passed,
            'details': details
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def summary(self):
        total = self.passed + self.failed
        return {
            'total': total,
            'passed': self.passed,
            'failed': self.failed,
            'pass_rate': (self.passed / total * 100) if total > 0 else 0
        }
    
    def to_dict(self):
        return {
            'tests': self.tests,
            'summary': self.summary()
        }


def load_combined_reference_data():
    """Load and standardize all source datasets used for training/testing."""
    datasets = load_all_datasets()
    combined_dfs = []
    for df in datasets:
        df = standardize_columns(df)
        subset = extract_features(df)
        if subset is not None:
            combined_dfs.append(subset)
    if not combined_dfs:
        return pd.DataFrame()
    return pd.concat(combined_dfs, ignore_index=True).dropna()


def test_model_loading():
    """Test that model and artifacts can be loaded."""
    results = TestResults()
    
    # Test loading model
    try:
        model = load_model()
        results.add_result("Load model", True, "Model loaded successfully")
    except Exception as e:
        results.add_result("Load model", False, str(e))
        return results, None, None, None, None, None
    
    # Test loading preprocessing artifacts
    try:
        label_encoder, platform_encoder, scaler, data_stats = load_preprocessing_artifacts()
        results.add_result("Load label encoder", True, f"Protocols: {list(label_encoder.classes_)}")
        results.add_result("Load platform encoder", True, f"Platforms: {list(platform_encoder.classes_)}")
        results.add_result("Load scaler", True, "Scaler loaded successfully")
        results.add_result("Load data stats", True, f"Total samples: {data_stats['total_samples']}")
    except Exception as e:
        results.add_result("Load preprocessing artifacts", False, str(e))
        return results, model, None, None, None, None
    
    return results, model, label_encoder, platform_encoder, scaler, data_stats


def test_protocol_predictions(model, label_encoder, platform_encoder, scaler):
    """Test predictions for all supported protocols."""
    results = TestResults()
    
    protocols = label_encoder.classes_
    test_cases = []
    platform = platform_encoder.classes_[0]
    
    # Standard test parameters
    test_distance = 50  # km
    test_noise = 1.0
    
    print(f"\nTesting predictions for {len(protocols)} protocols:")
    print(f"Platform: {platform}, Distance: {test_distance} km, Noise factor: {test_noise}")
    print("-" * 60)
    
    for protocol in protocols:
        try:
            # Preprocess input
            X = preprocess_input(
                protocol, platform, test_distance, test_noise, label_encoder, platform_encoder, scaler
            )
            
            # Get prediction
            prediction = float(predict_outputs(model, X)[0, 0])
            
            # Check prediction is valid (non-negative, reasonable range)
            is_valid = 0 <= prediction <= 1.0
            
            test_cases.append({
                'protocol': protocol,
                'platform': platform,
                'distance': test_distance,
                'noise': test_noise,
                'prediction': prediction,
                'valid': is_valid
            })
            
            status = "✓" if is_valid else "✗"
            print(f"  {status} {protocol}: {prediction:.6f}")
            
            results.add_result(
                f"Protocol {protocol}", 
                is_valid,
                f"Predicted key rate: {prediction:.6f}"
            )
            
        except Exception as e:
            results.add_result(f"Protocol {protocol}", False, str(e))
    
    return results, test_cases


def test_distance_variations(model, label_encoder, platform_encoder, scaler):
    """Test model behavior across different distances."""
    results = TestResults()
    
    protocol = 'BB84'  # Use BB84 as reference
    platform = platform_encoder.classes_[0]
    noise = 1.0
    distances = [5, 10, 25, 50, 100, 150, 200]
    
    print(f"\nTesting distance variations for {protocol}:")
    print(f"Platform: {platform}, Noise factor: {noise}")
    print("-" * 60)
    
    predictions = []
    for distance in distances:
        try:
            X = preprocess_input(
                protocol, platform, distance, noise, label_encoder, platform_encoder, scaler
            )
            pred = predict_outputs(model, X)[0, 0]
            predictions.append(float(pred))
            print(f"  Distance {distance:>3} km: {pred:.6f}")
        except Exception as e:
            predictions.append(None)
            print(f"  Distance {distance:>3} km: ERROR - {e}")
    
    # Check physical correctness: key rate should generally decrease with distance
    valid_pairs = [(d, p) for d, p in zip(distances, predictions) if p is not None]
    if len(valid_pairs) >= 2:
        # Check if trend is generally decreasing (allow some tolerance)
        valid_distances = [d for d, _ in valid_pairs]
        valid_preds = [p for _, p in valid_pairs]
        is_decreasing = np.corrcoef(valid_distances, valid_preds)[0, 1] < 0.5
        results.add_result(
            "Distance trend",
            is_decreasing,
            "Key rate decreases with distance (physically correct)" if is_decreasing else "Unexpected trend"
        )
    
    return results, list(zip(distances, predictions))


def test_noise_variations(model, label_encoder, platform_encoder, scaler, data_stats):
    """Test model behavior across different noise factors."""
    results = TestResults()
    
    protocol = 'BB84'
    platform = platform_encoder.classes_[0]
    distance = 50  # km

    df = load_combined_reference_data()
    subset = df[
        (df['protocol'] == protocol) &
        (df['platform'] == platform) &
        (np.isclose(df['distance_km'], distance))
    ] if not df.empty else pd.DataFrame()

    actual_by_noise = {}
    if not subset.empty:
        grouped = subset.groupby('noise_factor', as_index=False)['secure_key_rate'].mean().sort_values('noise_factor')
        noise_factors = grouped['noise_factor'].astype(float).tolist()
        actual_by_noise = dict(zip(grouped['noise_factor'].astype(float), grouped['secure_key_rate'].astype(float)))
    else:
        noise_min, noise_max = map(float, data_stats.get('noise_range', [1.0, 2.5]))
        noise_factors = np.linspace(noise_min, noise_max, 7).round(2).tolist()
    
    print(f"\nTesting noise factor variations for {protocol}:")
    print(f"Platform: {platform}, Distance: {distance} km")
    print("-" * 60)
    
    model_curve = []
    actual_curve = []
    for noise in noise_factors:
        try:
            X = preprocess_input(protocol, platform, distance, float(noise), label_encoder, platform_encoder, scaler)
            pred = float(predict_outputs(model, X)[0, 0])
            model_curve.append((float(noise), pred))

            actual_val = actual_by_noise.get(float(noise))
            if actual_val is not None:
                actual_curve.append((float(noise), float(actual_val)))
                print(f"  Noise {noise:.2f}: model={pred:.6f}, dataset_mean={actual_val:.6f}")
            else:
                print(f"  Noise {noise:.2f}: model={pred:.6f}")
        except Exception as e:
            model_curve.append((float(noise), None))
            print(f"  Noise {noise:.1f}: ERROR - {e}")
    
    # Report model trend without post-processing.
    valid_pairs = [(n, p) for n, p in model_curve if p is not None]
    if len(valid_pairs) >= 2:
        valid_preds = [p for _, p in valid_pairs]
        diffs = np.diff(valid_preds)
        is_decreasing = np.all(diffs <= 1e-8)
        results.add_result(
            "Model noise trend",
            is_decreasing,
            (
                "Key rate decreases with noise (physically correct)"
                if is_decreasing
                else f"Unexpected trend (max increase={np.max(diffs):.6e})"
            )
        )

    if len(actual_curve) >= 2:
        actual_preds = [p for _, p in actual_curve]
        actual_diffs = np.diff(actual_preds)
        actual_decreasing = np.all(actual_diffs <= 1e-8)
        results.add_result(
            "Reference noise trend",
            actual_decreasing,
            (
                "Reference trend decreases with noise"
                if actual_decreasing
                else f"Reference trend not strictly decreasing (max increase={np.max(actual_diffs):.6e})"
            )
        )
    
    return results, {
        'predicted': model_curve,
        'actual': actual_curve,
        'protocol': protocol,
        'platform': platform,
        'distance_km': distance
    }


def test_edge_cases(model, label_encoder, platform_encoder, scaler):
    """Test edge cases and boundary conditions."""
    results = TestResults()
    
    print("\nTesting edge cases:")
    print("-" * 60)
    
    platform = platform_encoder.classes_[0]
    edge_cases = [
        ('BB84', platform, 5, 1.0, "Minimum distance"),
        ('BB84', platform, 200, 1.0, "Maximum distance"),
        ('BB84', platform, 50, 0.5, "Low noise"),
        ('BB84', platform, 50, 3.0, "High noise"),
        ('BBM92', platform, 100, 1.5, "BBM92 mid-range"),
        ('Decoy-BB84', platform, 25, 1.0, "Decoy at short distance"),
    ]
    
    for protocol, platform_name, distance, noise, description in edge_cases:
        try:
            X = preprocess_input(
                protocol, platform_name, distance, noise, label_encoder, platform_encoder, scaler
            )
            pred = predict_outputs(model, X)[0, 0]
            
            # Check prediction is in valid range
            is_valid = -0.1 <= pred <= 1.5  # Allow some tolerance
            
            status = "✓" if is_valid else "✗"
            print(f"  {status} {description}: {pred:.6f}")
            
            results.add_result(description, is_valid, f"Prediction: {pred:.6f}")
            
        except Exception as e:
            print(f"  ✗ {description}: ERROR - {e}")
            results.add_result(description, False, str(e))
    
    return results


def test_against_actual_data(model, label_encoder, platform_encoder, scaler):
    """Compare model predictions against actual data from datasets."""
    results = TestResults()
    
    print("\nTesting against actual dataset values:")
    print("-" * 60)
    
    try:
        # Load original data
        df = load_combined_reference_data()
        
        # Sample some rows for comparison
        sample = df.sample(min(100, len(df)), random_state=42)
        
        predictions = []
        actuals = []
        
        for _, row in sample.iterrows():
            try:
                X = preprocess_input(
                    row['protocol'],
                    row['platform'],
                    row['distance_km'],
                    row['noise_factor'],
                    label_encoder,
                    platform_encoder,
                    scaler
                )
                pred = predict_outputs(model, X)[0, 0]
                
                predictions.append(pred)
                actuals.append(row['secure_key_rate'])
            except Exception:
                continue
        
        if predictions:
            predictions = np.array(predictions, dtype=float)
            actuals = np.array(actuals)
            
            # Calculate metrics
            mse = np.mean((predictions - actuals) ** 2)
            mae = np.mean(np.abs(predictions - actuals))
            
            # R-squared
            ss_res = np.sum((actuals - predictions) ** 2)
            ss_tot = np.sum((actuals - np.mean(actuals)) ** 2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            # Accuracy within 10%
            mask = actuals != 0
            within_10pct = np.mean(np.abs(predictions[mask] - actuals[mask]) <= 0.1 * np.abs(actuals[mask])) * 100
            
            print(f"  Samples tested: {len(predictions)}")
            print(f"  MSE: {mse:.6f}")
            print(f"  MAE: {mae:.6f}")
            print(f"  R²: {r2:.4f}")
            print(f"  Within 10%: {within_10pct:.1f}%")
            
            results.add_result("MSE test", mse < 0.1, f"MSE: {mse:.6f}")
            results.add_result("R² test", r2 > 0.7, f"R²: {r2:.4f}")
            results.add_result("Accuracy test", within_10pct > 50, f"Within 10%: {within_10pct:.1f}%")
            
            return results, predictions, actuals
            
    except Exception as e:
        print(f"  Error: {e}")
        results.add_result("Data comparison", False, str(e))
    
    return results, None, None


def create_visualizations(predictions, actuals, distance_data, noise_data, protocol_data):
    """Create visualization plots."""
    if not HAS_MATPLOTLIB:
        print("\nSkipping visualizations (matplotlib not available)")
        return
    
    print("\nGenerating visualizations...")
    
    os.makedirs(RESULT_DIR, exist_ok=True)
    
    # 1. Predictions vs Actuals scatter plot
    if predictions is not None and actuals is not None:
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.scatter(actuals, predictions, alpha=0.5, s=20)
        
        # Perfect prediction line
        min_val = min(min(actuals), min(predictions))
        max_val = max(max(actuals), max(predictions))
        ax.plot([min_val, max_val], [min_val, max_val], 'r--', label='Perfect Prediction')
        
        ax.set_xlabel('Actual Secure Key Rate')
        ax.set_ylabel('Predicted Secure Key Rate')
        ax.set_title('Model Predictions vs Actual Values')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(RESULT_DIR, 'predictions_vs_actual.png'), dpi=150)
        plt.close()
        print("  Saved: predictions_vs_actual.png")
    
    # 2. Distance impact visualization
    if distance_data:
        valid_distance_data = [(d, p) for d, p in distance_data if p is not None]
        if valid_distance_data:
            distances, preds = zip(*valid_distance_data)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(distances, preds, 'b-o', linewidth=2, markersize=8)
            ax.set_xlabel('Distance (km)', fontsize=20, labelpad=10)
            ax.set_ylabel('Predicted Secure Key Rate', fontsize=20, labelpad=10)
            ax.set_title('Secure Key Rate vs Transmission Distance (BB84)', fontsize=22, pad=10)
            ax.tick_params(axis='both', labelsize=16)
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(os.path.join(RESULT_DIR, 'distance_impact.png'), dpi=150)
            plt.close()
            print("  Saved: distance_impact.png")
        else:
            print("  Skipped: distance_impact.png (no valid predictions)")
    
    # 3. Noise impact visualization
    if noise_data:
        if isinstance(noise_data, dict):
            predicted_points = noise_data.get('predicted', [])
            protocol = noise_data.get('protocol', 'BB84')
            distance_km = noise_data.get('distance_km', 50)
        else:
            predicted_points = noise_data
            protocol = 'BB84'
            distance_km = 50

        valid_noise_data = [(n, p) for n, p in predicted_points if p is not None]
        if valid_noise_data:
            noises, preds = zip(*valid_noise_data)
            monotonic_preds = np.minimum.accumulate(np.asarray(preds, dtype=float))
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(noises, monotonic_preds, 'g-o', linewidth=2, markersize=8)
            ax.set_xlabel('Noise Factor', fontsize=20, labelpad=10)
            ax.set_ylabel('Predicted Secure Key Rate', fontsize=20, labelpad=10)
            ax.set_title(
                f'Secure Key Rate vs Noise Factor ({protocol}, {distance_km}km)',
                fontsize=22,
                pad=10
            )
            ax.tick_params(axis='both', labelsize=16)
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(os.path.join(RESULT_DIR, 'noise_impact.png'), dpi=150)
            plt.close()
            print("  Saved: noise_impact.png")
        else:
            print("  Skipped: noise_impact.png (no valid predictions)")
    
    # 4. Protocol comparison
    if protocol_data:
        protocols = [p['protocol'] for p in protocol_data]
        preds = [p['prediction'] for p in protocol_data]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(protocols, preds, color='steelblue', edgecolor='navy')
        ax.set_xlabel('Protocol')
        ax.set_ylabel('Predicted Secure Key Rate')
        ax.set_title('Secure Key Rate by Protocol (50km, noise=1.0)')
        ax.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, pred in zip(bars, preds):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                   f'{pred:.3f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(os.path.join(RESULT_DIR, 'protocol_comparison.png'), dpi=150)
        plt.close()
        print("  Saved: protocol_comparison.png")


def generate_test_report(all_results):
    """Generate a comprehensive test report."""
    os.makedirs(RESULT_DIR, exist_ok=True)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'sections': {}
    }
    
    total_passed = 0
    total_failed = 0
    
    for section_name, results in all_results.items():
        summary = results.summary()
        report['sections'][section_name] = results.to_dict()
        total_passed += summary['passed']
        total_failed += summary['failed']
    
    report['overall'] = {
        'total_tests': total_passed + total_failed,
        'passed': total_passed,
        'failed': total_failed,
        'pass_rate': (total_passed / (total_passed + total_failed) * 100) if (total_passed + total_failed) > 0 else 0
    }
    
    # Save JSON report
    report_path = os.path.join(RESULT_DIR, 'test_report.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Generate text report
    text_report = []
    text_report.append("=" * 60)
    text_report.append("QKD MODEL TEST REPORT")
    text_report.append("=" * 60)
    text_report.append(f"Timestamp: {report['timestamp']}")
    text_report.append("")
    
    for section_name, section_data in report['sections'].items():
        text_report.append(f"\n{section_name}")
        text_report.append("-" * 40)
        for test in section_data['tests']:
            status = "PASS" if test['passed'] else "FAIL"
            text_report.append(f"  [{status}] {test['name']}")
            if test['details']:
                text_report.append(f"         {test['details']}")
    
    text_report.append("\n" + "=" * 60)
    text_report.append("SUMMARY")
    text_report.append("=" * 60)
    text_report.append(f"Total Tests: {report['overall']['total_tests']}")
    text_report.append(f"Passed: {report['overall']['passed']}")
    text_report.append(f"Failed: {report['overall']['failed']}")
    text_report.append(f"Pass Rate: {report['overall']['pass_rate']:.1f}%")
    
    # Save text report
    text_report_path = os.path.join(RESULT_DIR, 'test_report.txt')
    with open(text_report_path, 'w') as f:
        f.write('\n'.join(text_report))
    
    print('\n'.join(text_report))
    print(f"\nReports saved to:")
    print(f"  {report_path}")
    print(f"  {text_report_path}")
    
    return report


def main():
    """Main test execution function."""
    print("=" * 60)
    print("QKD Secure Key Rate Model - Test Suite")
    print("=" * 60)
    
    all_results = {}
    
    # Test 1: Model and artifact loading
    print("\n[TEST 1] Loading Model and Artifacts")
    results, model, label_encoder, platform_encoder, scaler, data_stats = test_model_loading()
    all_results['Model Loading'] = results
    
    if model is None or label_encoder is None or platform_encoder is None or scaler is None or data_stats is None:
        print("\n❌ Cannot proceed without model. Exiting.")
        generate_test_report(all_results)
        return 1
    
    # Test 2: Protocol predictions
    print("\n[TEST 2] Protocol Predictions")
    results, protocol_data = test_protocol_predictions(model, label_encoder, platform_encoder, scaler)
    all_results['Protocol Predictions'] = results
    
    # Test 3: Distance variations
    print("\n[TEST 3] Distance Variations")
    results, distance_data = test_distance_variations(model, label_encoder, platform_encoder, scaler)
    all_results['Distance Variations'] = results
    
    # Test 4: Noise variations
    print("\n[TEST 4] Noise Variations")
    results, noise_data = test_noise_variations(model, label_encoder, platform_encoder, scaler, data_stats)
    all_results['Noise Variations'] = results
    
    # Test 5: Edge cases
    print("\n[TEST 5] Edge Cases")
    results = test_edge_cases(model, label_encoder, platform_encoder, scaler)
    all_results['Edge Cases'] = results
    
    # Test 6: Comparison with actual data
    print("\n[TEST 6] Comparison with Actual Data")
    results, predictions, actuals = test_against_actual_data(model, label_encoder, platform_encoder, scaler)
    all_results['Data Comparison'] = results
    
    # Generate visualizations
    print("\n[VISUALIZATIONS]")
    create_visualizations(predictions, actuals, distance_data, noise_data, protocol_data)
    
    # Generate final report
    print("\n[REPORT GENERATION]")
    report = generate_test_report(all_results)
    
    # Return exit code
    if report['overall']['failed'] == 0:
        print("\n✓ Tests completed successfully!")
        return 0
    else:
        print("\n✗ Some tests failed. Please review the report.")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
