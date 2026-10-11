"""Load all 6 QKD CSV files and unify them into a single DataFrame."""

import csv
import os

import pandas as pd

from src.config import (
    COMMON_COLUMNS,
    DATA_DIR,
    NOVEL_CSV,
    QKD_FINAL_CSV,
    SINGLE_PROTOCOL_CSVS,
)


def _load_qkd_final() -> pd.DataFrame:
    """Load qkd_final CSV, handling E91 rows that have 2 extra trailing columns."""
    path = os.path.join(DATA_DIR, QKD_FINAL_CSV)

    # Read header to get the 29 expected column names
    with open(path, newline="") as f:
        reader = csv.reader(f)
        header = next(reader)

    n_cols = len(header)
    rows = []
    with open(path, newline="") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            rows.append(row[:n_cols])  # truncate E91 extra fields

    df = pd.DataFrame(rows, columns=header)

    # Cast numeric columns
    numeric_cols = [
        "distance_km", "noise_factor", "run", "n_qubits",
        "transmission", "channel_loss_db", "sifted_length",
        "raw_key_rate", "secure_key_rate", "effective_key_bits",
        "effective_secure_bits", "qber_base", "qber_hardware",
        "qber_channel", "qber_total", "single_qubit_fidelity",
        "two_qubit_fidelity", "T1", "T2", "depolarizing_1q", "depolarizing_2q",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Map qber_total → qber for common schema
    df["qber"] = df["qber_total"]

    return df


def _load_single_protocol(filename: str) -> pd.DataFrame:
    """Load one of the 4 single-protocol CSVs (bbm92, decoybb84, sarg04, sixstate)."""
    return pd.read_csv(os.path.join(DATA_DIR, filename))


def _load_novel_protocols() -> pd.DataFrame:
    """Load the novel_protocols CSV (AB-QKD, DS6-QKD, EEPM-QKD)."""
    return pd.read_csv(os.path.join(DATA_DIR, NOVEL_CSV))


def load_unified_data() -> pd.DataFrame:
    """Load all 6 CSV files and return a single DataFrame with COMMON_COLUMNS only."""
    frames = []

    # 1. qkd_final (BB84, E91, B92)
    df_final = _load_qkd_final()
    frames.append(df_final[COMMON_COLUMNS])

    # 2. Four single-protocol files
    for csv_file in SINGLE_PROTOCOL_CSVS:
        df = _load_single_protocol(csv_file)
        frames.append(df[COMMON_COLUMNS])

    # 3. Novel protocols
    df_novel = _load_novel_protocols()
    frames.append(df_novel[COMMON_COLUMNS])

    unified = pd.concat(frames, ignore_index=True)

    # Validate
    assert unified[COMMON_COLUMNS].notna().all().all(), "Unexpected NaN in common columns"
    print(f"Unified dataset: {unified.shape[0]} rows, {unified.shape[1]} columns")
    print(f"Protocols ({unified['protocol'].nunique()}):", sorted(unified["protocol"].unique()))
    print(f"Platforms ({unified['platform'].nunique()}):", sorted(unified["platform"].unique()))

    return unified
