"""
Training script for QKD secure key rate prediction model.
"""

import os
import sys
import numpy as np
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set random seeds for reproducibility
np.random.seed(42)

try:
    import tensorflow as tf
    tf.random.set_seed(42)
    USE_TENSORFLOW = True
except ImportError:
    USE_TENSORFLOW = False

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from preprocessing import prepare_data, load_preprocessing_artifacts, RESULT_DIR
from model import create_model, save_model, get_callbacks, USE_TENSORFLOW as MODEL_USE_TF

# Hyperparameters
EPOCHS = 200
BATCH_SIZE = 32
LEARNING_RATE = 0.001
VALIDATION_SPLIT = 0.2
TEST_SIZE = 0.2


def calculate_metrics(y_true, y_pred, output_names=['secure_key_rate', 'transmission']):
    """Calculate comprehensive metrics for multi-output model evaluation."""
    # Ensure 2D arrays
    if len(y_true.shape) == 1:
        y_true = y_true.reshape(-1, 1)
    if len(y_pred.shape) == 1:
        y_pred = y_pred.reshape(-1, 1)
    
    all_metrics = {}
    
    for i, name in enumerate(output_names):
        yt = y_true[:, i]
        yp = y_pred[:, i]
        
        mse = np.mean((yt - yp) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(yt - yp))
        
        # R-squared
        ss_res = np.sum((yt - yp) ** 2)
        ss_tot = np.sum((yt - np.mean(yt)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        # Mean Absolute Percentage Error (avoid division by zero)
        mask = yt != 0
        mape = np.mean(np.abs((yt[mask] - yp[mask]) / yt[mask])) * 100 if np.any(mask) else 0
        
        # Accuracy metric (predictions within 10% of actual)
        tolerance = 0.1
        within_tolerance = np.abs(yt - yp) <= tolerance * np.abs(yt + 1e-8)
        accuracy = np.mean(within_tolerance) * 100
        
        all_metrics[name] = {
            'mse': float(mse),
            'rmse': float(rmse),
            'mae': float(mae),
            'r2': float(r2),
            'mape': float(mape),
            'accuracy_10pct': float(accuracy)
        }
    
    # Calculate overall metrics (average across outputs)
    all_metrics['overall'] = {
        'mse': np.mean([all_metrics[n]['mse'] for n in output_names]),
        'rmse': np.mean([all_metrics[n]['rmse'] for n in output_names]),
        'mae': np.mean([all_metrics[n]['mae'] for n in output_names]),
        'r2': np.mean([all_metrics[n]['r2'] for n in output_names]),
        'mape': np.mean([all_metrics[n]['mape'] for n in output_names]),
        'accuracy_10pct': np.mean([all_metrics[n]['accuracy_10pct'] for n in output_names])
    }
    
    return all_metrics


def train_model(X_train, y_train, X_val, y_val, epochs=EPOCHS, batch_size=BATCH_SIZE):
    """Train the model and return training history."""
    
    # Create model
    num_protocols = len(np.unique(X_train[:, 0]))  # First column is protocol_encoded
    num_outputs = y_train.shape[1] if len(y_train.shape) > 1 else 1
    input_dim = X_train.shape[1]  # Number of input features
    model = create_model(input_dim=input_dim, num_protocols=num_protocols, num_outputs=num_outputs)
    
    print("\n" + "=" * 50)
    print("Training Model...")
    print("=" * 50)
    print(f"Training samples: {len(X_train)}")
    print(f"Validation samples: {len(X_val)}")
    print(f"Input features: {input_dim} (protocol, platform, distance, noise)")
    print(f"Epochs: {epochs}, Batch size: {batch_size}")
    print(f"Outputs: {num_outputs} (secure_key_rate, transmission)")
    print(f"Using {'TensorFlow/Keras' if USE_TENSORFLOW and MODEL_USE_TF else 'sklearn'} backend")
    
    if USE_TENSORFLOW and MODEL_USE_TF:
        # Keras training
        callbacks = get_callbacks()
        
        history = model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        return model, history.history
    else:
        # sklearn training
        history = model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            verbose=1
        )
        
        return model, history.history


def evaluate_model(model, X_test, y_test):
    """Evaluate model on test set."""
    print("\n" + "=" * 50)
    print("Evaluating Model...")
    print("=" * 50)
    
    # Get predictions
    predictions = model.predict(X_test)
    if len(predictions.shape) == 1:
        predictions = predictions.reshape(-1, 1)
    if len(y_test.shape) == 1:
        y_test = y_test.reshape(-1, 1)
    
    # Calculate metrics for multi-output
    output_names = ['secure_key_rate', 'transmission']
    metrics = calculate_metrics(y_test, predictions, output_names)
    
    print("\nPer-output metrics:")
    for name in output_names:
        m = metrics[name]
        print(f"\n  {name}:")
        print(f"    MSE: {m['mse']:.6f}, RMSE: {m['rmse']:.6f}")
        print(f"    MAE: {m['mae']:.6f}, R²: {m['r2']:.4f}")
        print(f"    MAPE: {m['mape']:.2f}%, Accuracy (10%): {m['accuracy_10pct']:.2f}%")
    
    print(f"\nOverall metrics:")
    m = metrics['overall']
    print(f"  R²: {m['r2']:.4f}")
    print(f"  Accuracy (within 10%): {m['accuracy_10pct']:.2f}%")
    
    return metrics, predictions


def save_training_results(metrics, history, data_stats):
    """Save training results and metrics."""
    os.makedirs(RESULT_DIR, exist_ok=True)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'hyperparameters': {
            'epochs': EPOCHS,
            'batch_size': BATCH_SIZE,
            'learning_rate': LEARNING_RATE,
            'validation_split': VALIDATION_SPLIT,
            'test_size': TEST_SIZE
        },
        'data_stats': data_stats,
        'test_metrics': metrics,
        'training_history': {
            'final_loss': history.get('loss', [0])[-1] if history.get('loss') else 0,
            'final_val_loss': history.get('val_loss', [0])[-1] if history.get('val_loss') else 0
        }
    }
    
    results_path = os.path.join(RESULT_DIR, 'training_results.json')
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {results_path}")
    return results


def create_training_plots(history, y_test, predictions, metrics):
    """Create and save training visualization plots."""
    if not HAS_MATPLOTLIB:
        print("Matplotlib not available - skipping plots")
        return
    
    os.makedirs(RESULT_DIR, exist_ok=True)
    
    # Ensure 2D arrays
    if len(y_test.shape) == 1:
        y_test = y_test.reshape(-1, 1)
    if len(predictions.shape) == 1:
        predictions = predictions.reshape(-1, 1)
    
    output_names = ['secure_key_rate', 'transmission']
    
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    
    # Plot 1: Training & Validation Loss
    ax1 = axes[0, 0]
    if history.get('loss') and len(history['loss']) > 1:
        epochs_range = range(1, len(history['loss']) + 1)
        ax1.plot(epochs_range, history['loss'], 'b-', label='Training Loss', linewidth=2)
        if history.get('val_loss'):
            ax1.plot(epochs_range, history['val_loss'], 'r-', label='Validation Loss', linewidth=2)
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Loss (MSE)')
        ax1.set_title('Training and Validation Loss')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
    else:
        ax1.text(0.5, 0.5, 'Training history not available\n(sklearn model)', 
                ha='center', va='center', transform=ax1.transAxes)
        ax1.set_title('Training Loss')
    
    # Plot 2: Secure Key Rate - Predictions vs Actual
    ax2 = axes[0, 1]
    ax2.scatter(y_test[:, 0], predictions[:, 0], alpha=0.5, s=20, c='steelblue')
    min_val = min(min(y_test[:, 0]), min(predictions[:, 0]))
    max_val = max(max(y_test[:, 0]), max(predictions[:, 0]))
    ax2.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect')
    ax2.set_xlabel('Actual')
    ax2.set_ylabel('Predicted')
    ax2.set_title(f'Secure Key Rate (R² = {metrics["secure_key_rate"]["r2"]:.4f})')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Transmission - Predictions vs Actual
    ax3 = axes[0, 2]
    ax3.scatter(y_test[:, 1], predictions[:, 1], alpha=0.5, s=20, c='green')
    min_val = min(min(y_test[:, 1]), min(predictions[:, 1]))
    max_val = max(max(y_test[:, 1]), max(predictions[:, 1]))
    ax3.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect')
    ax3.set_xlabel('Actual')
    ax3.set_ylabel('Predicted')
    ax3.set_title(f'Transmission (R² = {metrics["transmission"]["r2"]:.4f})')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Error Distribution - Secure Key Rate
    ax4 = axes[1, 0]
    errors_skr = predictions[:, 0] - y_test[:, 0]
    ax4.hist(errors_skr, bins=50, edgecolor='black', alpha=0.7, color='steelblue')
    ax4.axvline(x=0, color='r', linestyle='--', linewidth=2)
    ax4.set_xlabel('Prediction Error')
    ax4.set_ylabel('Frequency')
    ax4.set_title(f'Secure Key Rate Error (MAE = {metrics["secure_key_rate"]["mae"]:.4f})')
    ax4.grid(True, alpha=0.3)
    
    # Plot 5: Error Distribution - Transmission
    ax5 = axes[1, 1]
    errors_trans = predictions[:, 1] - y_test[:, 1]
    ax5.hist(errors_trans, bins=50, edgecolor='black', alpha=0.7, color='green')
    ax5.axvline(x=0, color='r', linestyle='--', linewidth=2)
    ax5.set_xlabel('Prediction Error')
    ax5.set_ylabel('Frequency')
    ax5.set_title(f'Transmission Error (MAE = {metrics["transmission"]["mae"]:.4f})')
    ax5.grid(True, alpha=0.3)
    
    # Plot 6: Metrics Summary Bar Chart
    ax6 = axes[1, 2]
    metric_names = ['SKR R²', 'Trans R²', 'SKR Acc', 'Trans Acc']
    metric_values = [
        metrics['secure_key_rate']['r2'], 
        metrics['transmission']['r2'],
        metrics['secure_key_rate']['accuracy_10pct'] / 100,
        metrics['transmission']['accuracy_10pct'] / 100
    ]
    colors = ['steelblue', 'green', 'steelblue', 'green']
    bars = ax6.bar(metric_names, metric_values, color=colors, edgecolor='black', alpha=0.8)
    ax6.axhline(y=0.9, color='red', linestyle='--', alpha=0.5, label='90% Target')
    ax6.set_ylabel('Score')
    ax6.set_title('Model Performance Metrics')
    ax6.set_ylim(0, 1.1)
    for bar, val in zip(bars, metric_values):
        ax6.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.2f}', ha='center', va='bottom', fontweight='bold')
    ax6.legend()
    ax6.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle('QKD Multi-Output Model - Training Results', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    plot_path = os.path.join(RESULT_DIR, 'training_plots.png')
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Training plots saved to {plot_path}")


def main():
    """Main training pipeline."""
    print("=" * 60)
    print("QKD Secure Key Rate Prediction - Model Training")
    print("=" * 60)
    
    # Step 1: Prepare data
    print("\nStep 1: Data Preprocessing")
    X_train, X_test, y_train, y_test, label_encoder, platform_encoder, scaler, data_stats = prepare_data(
        test_size=TEST_SIZE, random_state=42
    )
    
    # Create validation split from training data
    val_split_idx = int(len(X_train) * (1 - VALIDATION_SPLIT))
    X_val = X_train[val_split_idx:]
    y_val = y_train[val_split_idx:]
    X_train = X_train[:val_split_idx]
    y_train = y_train[:val_split_idx]
    
    print(f"\nFinal splits:")
    print(f"  Train: {len(X_train)} samples")
    print(f"  Validation: {len(X_val)} samples")
    print(f"  Test: {len(X_test)} samples")
    
    # Step 2: Train model
    print("\nStep 2: Model Training")
    model, history = train_model(X_train, y_train, X_val, y_val, epochs=EPOCHS, batch_size=BATCH_SIZE)
    
    # Step 3: Evaluate model
    print("\nStep 3: Model Evaluation")
    metrics, predictions = evaluate_model(model, X_test, y_test)
    
    # Step 4: Save model and results
    print("\nStep 4: Saving Artifacts")
    model_path = save_model(model)
    results = save_training_results(metrics, history, data_stats)
    
    # Step 5: Create training plots
    print("\nStep 5: Creating Visualizations")
    create_training_plots(history, y_test, predictions, metrics)
    
    # Summary
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    print(f"Model saved to: {model_path}")
    print(f"Outputs: secure_key_rate, transmission")
    print(f"Overall R² Score: {metrics['overall']['r2']:.4f}")
    print(f"Overall Accuracy (within 10%): {metrics['overall']['accuracy_10pct']:.2f}%")
    
    # Check if meets success criteria
    if metrics['overall']['r2'] >= 0.90:
        print("\n✓ Model meets >90% R² target!")
    else:
        print(f"\n! Model R² ({metrics['overall']['r2']:.2f}) below 90% target. Consider tuning hyperparameters.")
    
    return model, metrics


if __name__ == '__main__':
    model, metrics = main()
