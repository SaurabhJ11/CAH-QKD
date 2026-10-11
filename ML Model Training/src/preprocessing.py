"""Feature engineering, encoding, and train/test splitting."""

import pandas as pd
from sklearn.model_selection import train_test_split

from src.config import (
    ALL_PROTOCOLS,
    INPUT_FEATURES_BASE,
    PLATFORM_TYPE_TO_ID,
    PROTOCOL_FEATURE_PREFIX,
    RANDOM_STATE,
    TARGET,
    TEST_SIZE,
)


def get_input_feature_names() -> list[str]:
    """Return the full ordered list of model input feature names."""
    proto_cols = [f"{PROTOCOL_FEATURE_PREFIX}{p}" for p in ALL_PROTOCOLS]
    return INPUT_FEATURES_BASE + proto_cols


def prepare_features(df: pd.DataFrame):
    """Encode categoricals, compute derived features, and split into train/test.

    Returns:
        X_train, X_test, y_train, y_test, encoders (dict)
    """
    data = df.copy()

    # ── Label-encode platform_type (binary, fine for trees) ──────────────
    data["platform_type_encoded"] = data["platform_type"].map(PLATFORM_TYPE_TO_ID)

    # ── One-hot encode protocol ──────────────────────────────────────────
    for proto in ALL_PROTOCOLS:
        data[f"{PROTOCOL_FEATURE_PREFIX}{proto}"] = (data["protocol"] == proto).astype(int)

    # ── Derived features ─────────────────────────────────────────────────
    data["dist_transmission"] = data["distance_km"] * data["transmission"]
    data["fidelity_product"] = data["single_qubit_fidelity"] * data["two_qubit_fidelity"]
    data["coherence_ratio"] = data["T2"] / data["T1"]

    # ── Select model inputs & target ─────────────────────────────────────
    feature_cols = get_input_feature_names()
    X = data[feature_cols]
    y = data[TARGET]

    # ── Stratified split by protocol ─────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=data["protocol"],
    )

    encoders = {
        "platform_type": PLATFORM_TYPE_TO_ID,
    }

    print(f"Train: {X_train.shape[0]} rows, {X_train.shape[1]} features  |  Test: {X_test.shape[0]} rows")
    return X_train, X_test, y_train, y_test, encoders
