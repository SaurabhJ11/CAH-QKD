"""Inference pipeline: simplified user input -> top-N protocol recommendations."""

import os

import joblib
import numpy as np
import pandas as pd

from src.config import (
    ALL_PROTOCOLS,
    ENCODERS_FILE,
    MODEL_FILE,
    MODELS_DIR,
    PLATFORM_SPECS,
    PLATFORM_TYPE_TO_ID,
    PROTOCOL_FEATURE_PREFIX,
    compute_transmission,
)
from src.preprocessing import get_input_feature_names


class QKDPredictor:
    """Load a trained model and recommend best QKD protocols for given conditions."""

    def __init__(
        self,
        model_path: str | None = None,
        encoders_path: str | None = None,
    ):
        model_path = model_path or os.path.join(MODELS_DIR, MODEL_FILE)
        encoders_path = encoders_path or os.path.join(MODELS_DIR, ENCODERS_FILE)
        self.model = joblib.load(model_path)
        self.encoders = joblib.load(encoders_path)
        self.feature_names = get_input_feature_names()

    def predict_top_protocols(
        self,
        distance_km: float,
        platform: str,
        noise_factor: float,
        top_n: int = 3,
    ) -> list[dict]:
        """Predict secure key rate for every protocol and return top_n results."""
        specs = PLATFORM_SPECS[platform]
        transmission = compute_transmission(distance_km)
        platform_type_enc = PLATFORM_TYPE_TO_ID[specs["platform_type"]]

        rows = []
        for proto in ALL_PROTOCOLS:
            row = {
                "distance_km": distance_km,
                "transmission": transmission,
                "single_qubit_fidelity": specs["single_qubit_fidelity"],
                "two_qubit_fidelity": specs["two_qubit_fidelity"],
                "T1": specs["T1"],
                "T2": specs["T2"],
                "noise_factor": noise_factor,
                "platform_type_encoded": platform_type_enc,
                "dist_transmission": distance_km * transmission,
                "fidelity_product": specs["single_qubit_fidelity"] * specs["two_qubit_fidelity"],
                "coherence_ratio": specs["T2"] / specs["T1"],
            }
            # One-hot protocol columns
            for p in ALL_PROTOCOLS:
                row[f"{PROTOCOL_FEATURE_PREFIX}{p}"] = 1 if p == proto else 0
            rows.append(row)

        X = pd.DataFrame(rows, columns=self.feature_names)
        preds = self.model.predict(X)
        preds = np.clip(preds, 0, None)

        results = [
            {"protocol": proto, "secure_key_rate": float(rate)}
            for proto, rate in zip(ALL_PROTOCOLS, preds)
        ]
        results.sort(key=lambda r: r["secure_key_rate"], reverse=True)
        return results[:top_n]
