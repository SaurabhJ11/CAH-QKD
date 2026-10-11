import os

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

# ── CSV filenames ────────────────────────────────────────────────────────────
QKD_FINAL_CSV = "qkd_final_20260209_085953.csv"
BBM92_CSV = "bbm92_20260210_205349.csv"
DECOYBB84_CSV = "decoybb84_20260210_230545.csv"
SARG04_CSV = "sarg04_20260210_133117.csv"
SIXSTATE_CSV = "sixstate_20260210_004703.csv"
NOVEL_CSV = "novel_protocols_20260303_002909.csv"

SINGLE_PROTOCOL_CSVS = [BBM92_CSV, DECOYBB84_CSV, SARG04_CSV, SIXSTATE_CSV]

# ── Columns shared across all datasets (used for unification) ────────────────
COMMON_COLUMNS = [
    "protocol",
    "platform",
    "platform_type",
    "distance_km",
    "noise_factor",
    "transmission",
    "single_qubit_fidelity",
    "two_qubit_fidelity",
    "T1",
    "T2",
    "qber",
    "raw_key_rate",
    "secure_key_rate",
]

# ── Model input features ─────────────────────────────────────────────────────
# 7 physical + 1 encoded platform_type + 10 one-hot protocol + 3 derived = 21
INPUT_FEATURES_BASE = [
    "distance_km",
    "transmission",
    "single_qubit_fidelity",
    "two_qubit_fidelity",
    "T1",
    "T2",
    "noise_factor",
    "platform_type_encoded",
    # derived
    "dist_transmission",
    "fidelity_product",
    "coherence_ratio",
]

# One-hot protocol columns are generated dynamically as proto_<Name>
PROTOCOL_FEATURE_PREFIX = "proto_"

TARGET = "secure_key_rate"

# ── All 10 QKD protocols (sorted alphabetically for stable encoding) ─────────
ALL_PROTOCOLS = [
    "AB-QKD",
    "B92",
    "BB84",
    "BBM92",
    "DS6-QKD",
    "Decoy-BB84",
    "E91",
    "EEPM-QKD",
    "SARG04",
    "Six-State",
]

PROTOCOL_TO_ID = {name: idx for idx, name in enumerate(ALL_PROTOCOLS)}
ID_TO_PROTOCOL = {idx: name for idx, name in enumerate(ALL_PROTOCOLS)}

# ── Platform type encoding ───────────────────────────────────────────────────
PLATFORM_TYPES = ["superconducting", "trapped_ion"]
PLATFORM_TYPE_TO_ID = {name: idx for idx, name in enumerate(PLATFORM_TYPES)}
ID_TO_PLATFORM_TYPE = {idx: name for idx, name in enumerate(PLATFORM_TYPES)}

# ── Hardware platform specifications (for inference-time lookup) ──────────────
PLATFORM_SPECS = {
    "ionq_aria": {
        "single_qubit_fidelity": 0.9995,
        "two_qubit_fidelity": 0.987,
        "T1": 10000,
        "T2": 1000,
        "platform_type": "trapped_ion",
    },
    "ionq_harmony": {
        "single_qubit_fidelity": 0.999,
        "two_qubit_fidelity": 0.975,
        "T1": 8000,
        "T2": 800,
        "platform_type": "trapped_ion",
    },
    "rigetti_aspen_m3": {
        "single_qubit_fidelity": 0.998,
        "two_qubit_fidelity": 0.952,
        "T1": 50,
        "T2": 30,
        "platform_type": "superconducting",
    },
    "oqc_lucy": {
        "single_qubit_fidelity": 0.997,
        "two_qubit_fidelity": 0.945,
        "T1": 45,
        "T2": 25,
        "platform_type": "superconducting",
    },
}

# Friendly display names for the CLI
PLATFORM_DISPLAY = {
    "ionq_aria": "IonQ Aria",
    "ionq_harmony": "IonQ Harmony",
    "rigetti_aspen_m3": "Rigetti Aspen-M3",
    "oqc_lucy": "OQC Lucy",
}


def compute_transmission(distance_km: float) -> float:
    """Channel transmission from fiber loss: T = 10^(-0.2 * d / 10)."""
    return 10 ** (-0.2 * distance_km / 10)


# ── Train / test split ───────────────────────────────────────────────────────
TEST_SIZE = 0.20
RANDOM_STATE = 42

# ── Model artifact filenames ─────────────────────────────────────────────────
MODEL_FILE = "xgb_model_trial.joblib"
ENCODERS_FILE = "encoders_trial.joblib"
