"""
Neural Network model architecture for QKD secure key rate prediction.
"""

import numpy as np
import os

# Check for TensorFlow/Keras availability and use sklearn as fallback
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, Model
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
    USE_TENSORFLOW = True
except ImportError:
    USE_TENSORFLOW = False
    print("TensorFlow not available. Using scikit-learn model as fallback.")

from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.neural_network import MLPRegressor
import pickle

RESULT_DIR = os.path.join(os.path.dirname(__file__), 'result')


def create_keras_model(input_dim=4, num_protocols=10, num_outputs=2):
    """
    Create a neural network model for secure key rate and transmission prediction.
    
    Architecture:
    - Input: [protocol_encoded, platform_encoded, distance_km_scaled, noise_factor_scaled]
    - Dense layers with batch normalization and dropout
    - Output: [secure_key_rate, transmission] predictions
    """
    inputs = keras.Input(shape=(input_dim,), name='input_features')
    
    # First dense block
    x = layers.Dense(128, activation='relu', kernel_regularizer=keras.regularizers.l2(0.001))(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.2)(x)
    
    # Second dense block
    x = layers.Dense(64, activation='relu', kernel_regularizer=keras.regularizers.l2(0.001))(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.2)(x)
    
    # Third dense block
    x = layers.Dense(32, activation='relu', kernel_regularizer=keras.regularizers.l2(0.001))(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.1)(x)
    
    # Fourth dense block
    x = layers.Dense(16, activation='relu')(x)
    
    # Output layer (multi-output regression)
    outputs = layers.Dense(num_outputs, activation='linear', name='outputs')(x)
    
    model = Model(inputs=inputs, outputs=outputs, name='QKD_MultiOutput_Model')
    
    return model


def compile_model(model, learning_rate=0.001):
    """Compile the Keras model with optimizer and loss."""
    optimizer = keras.optimizers.Adam(learning_rate=learning_rate)
    
    model.compile(
        optimizer=optimizer,
        loss='mse',
        metrics=['mae', 'mse']
    )
    
    return model


def get_callbacks(model_path=None):
    """Get training callbacks for Keras model."""
    if model_path is None:
        model_path = os.path.join(RESULT_DIR, 'best_model.keras')
    
    callbacks = [
        EarlyStopping(
            monitor='val_loss',
            patience=20,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=10,
            min_lr=1e-6,
            verbose=1
        ),
        ModelCheckpoint(
            filepath=model_path,
            monitor='val_loss',
            save_best_only=True,
            verbose=1
        )
    ]
    
    return callbacks


class SklearnEnsembleModel:
    """
    Ensemble model using sklearn regressors as fallback when TensorFlow is not available.
    Combines GradientBoosting, RandomForest, and MLP for robust predictions.
    Supports multi-output regression (secure_key_rate and transmission).
    """
    
    def __init__(self, num_outputs=2):
        self.num_outputs = num_outputs
        # Create separate models for each output
        self.models = {}
        for i in range(num_outputs):
            self.models[i] = {
                'gb': GradientBoostingRegressor(
                    n_estimators=200,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=42
                ),
                'rf': RandomForestRegressor(
                    n_estimators=200,
                    max_depth=10,
                    random_state=42
                ),
                'mlp': MLPRegressor(
                    hidden_layer_sizes=(128, 64, 32, 16),
                    activation='relu',
                    solver='adam',
                    max_iter=500,
                    early_stopping=True,
                    random_state=42
                )
            }
        self.weights = {'gb': 0.4, 'rf': 0.3, 'mlp': 0.3}
        self.is_fitted = False
    
    def fit(self, X, y, validation_data=None, epochs=None, batch_size=None, callbacks=None, verbose=1):
        """Train all ensemble models for each output."""
        history = {'loss': [], 'val_loss': []}
        
        # Handle multi-output y
        if len(y.shape) == 1:
            y = y.reshape(-1, 1)
        
        for out_idx in range(self.num_outputs):
            y_out = y[:, out_idx]
            for name, model in self.models[out_idx].items():
                if verbose:
                    print(f"Training {name} for output {out_idx}...")
                model.fit(X, y_out)
        
        self.is_fitted = True
        
        # Calculate pseudo-history for compatibility
        train_pred = self.predict(X)
        train_mse = np.mean((train_pred - y) ** 2)
        history['loss'].append(train_mse)
        
        if validation_data is not None:
            X_val, y_val = validation_data
            if len(y_val.shape) == 1:
                y_val = y_val.reshape(-1, 1)
            val_pred = self.predict(X_val)
            val_mse = np.mean((val_pred - y_val) ** 2)
            history['val_loss'].append(val_mse)
        
        return type('History', (), {'history': history})()
    
    def predict(self, X):
        """Weighted ensemble prediction for all outputs."""
        if not self.is_fitted:
            raise ValueError("Model not fitted yet!")
        
        predictions = np.zeros((len(X), self.num_outputs))
        for out_idx in range(self.num_outputs):
            out_pred = np.zeros(len(X))
            for name, model in self.models[out_idx].items():
                pred = model.predict(X)
                out_pred += self.weights[name] * pred
            predictions[:, out_idx] = out_pred
        
        return predictions
    
    def evaluate(self, X, y, verbose=1):
        """Evaluate model performance."""
        if len(y.shape) == 1:
            y = y.reshape(-1, 1)
        predictions = self.predict(X)
        mse = np.mean((predictions - y) ** 2)
        mae = np.mean(np.abs(predictions - y))
        return [mse, mae, mse]
    
    def save(self, filepath):
        """Save model to file."""
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)
    
    @staticmethod
    def load(filepath):
        """Load model from file."""
        with open(filepath, 'rb') as f:
            return pickle.load(f)


def create_model(input_dim=4, num_protocols=10, num_outputs=2, use_keras=None):
    """
    Create and return the appropriate model based on available libraries.
    
    Args:
        input_dim: Number of input features (default: 4 for protocol, platform, distance, noise)
        num_protocols: Number of unique protocols
        num_outputs: Number of output features (default: 2 for secure_key_rate and transmission)
        use_keras: Force Keras (True) or sklearn (False). None = auto-detect.
    
    Returns:
        Model instance
    """
    if use_keras is None:
        use_keras = USE_TENSORFLOW
    
    if use_keras and USE_TENSORFLOW:
        model = create_keras_model(input_dim, num_protocols, num_outputs)
        model = compile_model(model)
        print(f"Created Keras model with {model.count_params()} parameters ({num_outputs} outputs)")
        return model
    else:
        model = SklearnEnsembleModel(num_outputs=num_outputs)
        print(f"Created sklearn ensemble model (GradientBoosting + RandomForest + MLP) with {num_outputs} outputs")
        return model


def load_model(model_path=None):
    """Load a trained model from disk."""
    if model_path is None:
        # Try Keras model first, then sklearn
        keras_path = os.path.join(RESULT_DIR, 'best_model.keras')
        sklearn_path = os.path.join(RESULT_DIR, 'sklearn_model.pkl')
        
        if USE_TENSORFLOW and os.path.exists(keras_path):
            model_path = keras_path
        elif os.path.exists(sklearn_path):
            model_path = sklearn_path
        else:
            raise FileNotFoundError("No trained model found!")
    
    if model_path.endswith('.keras') or model_path.endswith('.h5'):
        if not USE_TENSORFLOW:
            raise ImportError("TensorFlow required to load Keras model")
        return keras.models.load_model(model_path)
    else:
        return SklearnEnsembleModel.load(model_path)


def save_model(model, model_path=None):
    """Save model to disk."""
    os.makedirs(RESULT_DIR, exist_ok=True)
    
    if hasattr(model, 'save'):
        if isinstance(model, SklearnEnsembleModel):
            if model_path is None:
                model_path = os.path.join(RESULT_DIR, 'sklearn_model.pkl')
            model.save(model_path)
        else:
            # Keras model
            if model_path is None:
                model_path = os.path.join(RESULT_DIR, 'best_model.keras')
            model.save(model_path)
    
    print(f"Model saved to {model_path}")
    return model_path


if __name__ == '__main__':
    # Test model creation
    print("Testing model creation...")
    model = create_model()
    
    if USE_TENSORFLOW:
        model.summary()
    else:
        print("Model components:", list(model.models.keys()))
