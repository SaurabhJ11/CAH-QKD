"""Training orchestration: load -> preprocess -> train -> evaluate -> save."""

import os

import joblib

from src.config import ENCODERS_FILE, MODEL_FILE, MODELS_DIR
from src.data_loader import load_unified_data
from src.evaluate import evaluate_model
from src.model import get_model
from src.preprocessing import prepare_features


def train():
    """Run the full training pipeline and save artefacts."""
    # 1. Load data
    df = load_unified_data()

    # 2. Feature engineering & split
    X_train, X_test, y_train, y_test, encoders = prepare_features(df)

    # 3. Train
    model = get_model()
    print("\nTraining XGBoost ...")
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=50,
    )

    # 4. Evaluate
    metrics = evaluate_model(model, X_test, y_test, encoders)

    # 5. Save artefacts
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(model, os.path.join(MODELS_DIR, MODEL_FILE))
    joblib.dump(encoders, os.path.join(MODELS_DIR, ENCODERS_FILE))
    print(f"\nModel saved  -> {os.path.join(MODELS_DIR, MODEL_FILE)}")
    print(f"Encoders saved -> {os.path.join(MODELS_DIR, ENCODERS_FILE)}")

    return model, metrics
