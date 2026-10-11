"""
Data preprocessing pipeline for Quantum Key Distribution (QKD) model.
Loads, combines, and preprocesses data from multiple protocol datasets.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
import os
import pickle
import warnings
warnings.filterwarnings('ignore')

# Constants
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
RESULT_DIR = os.path.join(os.path.dirname(__file__), 'result')

# Protocol mapping for standardization
PROTOCOL_MAPPING = {
    'BB84': 'BB84',
    'BBM92': 'BBM92', 
    'SARG04': 'SARG04',
    'Six-State': 'Six-State',
    'Decoy-BB84': 'Decoy-BB84',
    'E91': 'E91',
    'B92': 'B92',
    'AB-QKD': 'AB-QKD',
    'DS6-QKD': 'DS6-QKD',
    'EEPM-QKD': 'EEPM-QKD'
}

# Platform/Architecture mapping for user-friendly names
PLATFORM_MAPPING = {
    'ionq_aria': 'IonQ Aria',
    'ionq_harmony': 'IonQ Harmony',
    'rigetti_aspen_m3': 'Rigetti Aspen-M-3',
    'oqc_lucy': 'OQC Lucy',
    # Reverse mappings for user input
    'IonQ Aria': 'ionq_aria',
    'IonQ Harmony': 'ionq_harmony',
    'Rigetti Aspen-M-3': 'rigetti_aspen_m3',
    'OQC Lucy': 'oqc_lucy'
}

# Available architectures for user selection
ARCHITECTURES = ['IonQ Aria', 'IonQ Harmony', 'Rigetti Aspen-M-3', 'OQC Lucy']


def load_all_datasets():
    """Load all CSV datasets from the data directory."""
    datasets = []
    required_cols = ['protocol', 'platform', 'distance_km', 'noise_factor', 'secure_key_rate', 'transmission']
    
    # Find all CSV files in data directory
    csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
    
    for csv_file in csv_files:
        filepath = os.path.join(DATA_DIR, csv_file)
        try:
            # Read only required feature columns so trailing extra fields do not drop valid rows.
            df = pd.read_csv(filepath, usecols=required_cols, on_bad_lines='skip')
            print(f"Loaded {csv_file}: {len(df)} rows, columns: {list(df.columns)[:5]}...")
            datasets.append(df)
        except Exception as e:
            print(f"Warning: Could not load {csv_file}: {e}")
            continue
    
    return datasets


def standardize_columns(df):
    """Standardize column names across different dataset formats."""
    # Rename columns to standard names if needed
    column_mapping = {
        'qber': 'qber_total',  # Some datasets use 'qber' instead of 'qber_total'
    }
    
    df = df.rename(columns=column_mapping)
    return df


def extract_features(df):
    """Extract relevant features for model training."""
    # Required columns for our model (inputs + outputs)
    required_cols = ['protocol', 'platform', 'distance_km', 'noise_factor', 'secure_key_rate', 'transmission']
    
    # Check which required columns exist
    available_cols = [col for col in required_cols if col in df.columns]
    
    if len(available_cols) < len(required_cols):
        missing = set(required_cols) - set(available_cols)
        print(f"  Warning: Missing columns: {missing}")
        return None
    
    # Extract only required columns
    subset = df[required_cols].copy()
    
    # Map protocol names to standard names
    subset['protocol'] = subset['protocol'].astype(str).str.strip().map(lambda x: PROTOCOL_MAPPING.get(x, x))
    
    return subset


def combine_datasets(datasets):
    """Combine all datasets into a single DataFrame."""
    combined_dfs = []
    
    for i, df in enumerate(datasets):
        df = standardize_columns(df)
        subset = extract_features(df)
        
        if subset is not None:
            combined_dfs.append(subset)
            print(f"  Dataset {i+1}: Added {len(subset)} rows")
        else:
            print(f"  Dataset {i+1}: Skipped (missing columns)")
    
    if not combined_dfs:
        raise ValueError("No valid datasets found!")
    
    combined = pd.concat(combined_dfs, ignore_index=True)
    print(f"\nTotal combined rows: {len(combined)}")
    
    return combined


def clean_data(df):
    """Clean the combined dataset."""
    initial_len = len(df)
    
    # Remove rows with missing values
    df = df.dropna()
    
    # Remove rows with negative secure key rates (invalid)
    df = df[df['secure_key_rate'] >= 0]
    
    # Remove extreme outliers (beyond 3 standard deviations)
    for col in ['distance_km', 'noise_factor', 'secure_key_rate']:
        if col in df.columns:
            mean = df[col].mean()
            std = df[col].std()
            df = df[(df[col] >= mean - 3*std) & (df[col] <= mean + 3*std)]
    
    print(f"Data cleaning: {initial_len} -> {len(df)} rows")
    return df


def encode_protocols(df, encoder=None):
    """Encode protocol names to numerical values."""
    if encoder is None:
        encoder = LabelEncoder()
        df['protocol_encoded'] = encoder.fit_transform(df['protocol'])
    else:
        df['protocol_encoded'] = encoder.transform(df['protocol'])
    
    return df, encoder


def encode_platforms(df, encoder=None):
    """Encode platform/architecture names to numerical values."""
    if encoder is None:
        encoder = LabelEncoder()
        df['platform_encoded'] = encoder.fit_transform(df['platform'])
    else:
        df['platform_encoded'] = encoder.transform(df['platform'])
    
    return df, encoder


def scale_features(df, scaler=None, feature_cols=['distance_km', 'noise_factor']):
    """Scale numerical features using StandardScaler."""
    if scaler is None:
        scaler = StandardScaler()
        df[feature_cols] = scaler.fit_transform(df[feature_cols])
    else:
        df[feature_cols] = scaler.transform(df[feature_cols])
    
    return df, scaler


def prepare_data(test_size=0.2, random_state=42):
    """
    Main preprocessing function.
    Returns train/test splits and preprocessing artifacts.
    """
    print("=" * 50)
    print("Loading datasets...")
    print("=" * 50)
    
    # Load all datasets
    datasets = load_all_datasets()
    
    print("\n" + "=" * 50)
    print("Combining datasets...")
    print("=" * 50)
    
    # Combine datasets
    df = combine_datasets(datasets)
    
    print("\n" + "=" * 50)
    print("Cleaning data...")
    print("=" * 50)
    
    # Clean data
    df = clean_data(df)
    
    print("\n" + "=" * 50)
    print("Encoding and scaling...")
    print("=" * 50)
    
    # Encode protocols
    df, label_encoder = encode_protocols(df)
    
    # Print protocol mapping
    print("\nProtocol encoding:")
    for proto, encoded in zip(label_encoder.classes_, range(len(label_encoder.classes_))):
        print(f"  {proto} -> {encoded}")
    
    # Encode platforms/architectures
    df, platform_encoder = encode_platforms(df)
    
    # Print platform mapping
    print("\nPlatform encoding:")
    for platform, encoded in zip(platform_encoder.classes_, range(len(platform_encoder.classes_))):
        print(f"  {platform} -> {encoded}")
    
    # Scale features
    feature_cols = ['distance_km', 'noise_factor']
    df_scaled = df.copy()
    df_scaled, scaler = scale_features(df_scaled, feature_cols=feature_cols)
    
    print("\n" + "=" * 50)
    print("Preparing train/test splits...")
    print("=" * 50)
    
    # Prepare features and targets (multi-output: secure_key_rate and transmission)
    # Input features: protocol_encoded, platform_encoded, distance_km, noise_factor
    X = df_scaled[['protocol_encoded', 'platform_encoded', 'distance_km', 'noise_factor']].values
    y = df_scaled[['secure_key_rate', 'transmission']].values  # Multi-output
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    print(f"Input features: protocol, platform, distance_km, noise_factor")
    print(f"Output features: secure_key_rate, transmission")
    
    # Save preprocessing artifacts
    os.makedirs(RESULT_DIR, exist_ok=True)
    
    with open(os.path.join(RESULT_DIR, 'label_encoder.pkl'), 'wb') as f:
        pickle.dump(label_encoder, f)
    
    with open(os.path.join(RESULT_DIR, 'platform_encoder.pkl'), 'wb') as f:
        pickle.dump(platform_encoder, f)
    
    with open(os.path.join(RESULT_DIR, 'scaler.pkl'), 'wb') as f:
        pickle.dump(scaler, f)
    
    # Save original data stats for reference
    data_stats = {
        'protocols': list(label_encoder.classes_),
        'platforms': list(platform_encoder.classes_),
        'distance_range': [float(df['distance_km'].min()), float(df['distance_km'].max())],
        'noise_range': [float(df['noise_factor'].min()), float(df['noise_factor'].max())],
        'key_rate_range': [float(df['secure_key_rate'].min()), float(df['secure_key_rate'].max())],
        'transmission_range': [float(df['transmission'].min()), float(df['transmission'].max())],
        'total_samples': len(df),
        'input_features': ['protocol', 'platform', 'distance_km', 'noise_factor'],
        'output_features': ['secure_key_rate', 'transmission']
    }
    
    with open(os.path.join(RESULT_DIR, 'data_stats.pkl'), 'wb') as f:
        pickle.dump(data_stats, f)
    
    print(f"\nPreprocessing artifacts saved to {RESULT_DIR}/")
    
    return X_train, X_test, y_train, y_test, label_encoder, platform_encoder, scaler, data_stats


def load_preprocessing_artifacts():
    """Load saved preprocessing artifacts."""
    with open(os.path.join(RESULT_DIR, 'label_encoder.pkl'), 'rb') as f:
        label_encoder = pickle.load(f)
    
    with open(os.path.join(RESULT_DIR, 'platform_encoder.pkl'), 'rb') as f:
        platform_encoder = pickle.load(f)
    
    with open(os.path.join(RESULT_DIR, 'scaler.pkl'), 'rb') as f:
        scaler = pickle.load(f)
    
    with open(os.path.join(RESULT_DIR, 'data_stats.pkl'), 'rb') as f:
        data_stats = pickle.load(f)
    
    return label_encoder, platform_encoder, scaler, data_stats


def preprocess_input(protocol, platform, distance_km, noise_factor, label_encoder=None, platform_encoder=None, scaler=None):
    """
    Preprocess a single input for model inference.
    
    Args:
        protocol: Protocol name (e.g., 'BB84', 'BBM92')
        platform: Platform/Architecture name (e.g., 'IonQ Aria', 'ionq_aria')
        distance_km: Transmission distance in km
        noise_factor: Environmental noise factor
        label_encoder: Fitted LabelEncoder for protocols (loads from file if None)
        platform_encoder: Fitted LabelEncoder for platforms (loads from file if None)
        scaler: Fitted StandardScaler (loads from file if None)
    
    Returns:
        Preprocessed input array ready for model prediction
    """
    if label_encoder is None or platform_encoder is None or scaler is None:
        label_encoder, platform_encoder, scaler, _ = load_preprocessing_artifacts()
    
    # Map protocol name if needed
    protocol = PROTOCOL_MAPPING.get(protocol, protocol)
    
    # Resolve platform name against fitted encoder classes to support both
    # user-friendly and internal naming formats.
    platform_candidates = []
    for candidate in (
        platform,
        PLATFORM_MAPPING.get(platform, platform),
        PLATFORM_MAPPING.get(PLATFORM_MAPPING.get(platform, platform), PLATFORM_MAPPING.get(platform, platform))
    ):
        if candidate not in platform_candidates:
            platform_candidates.append(candidate)
    
    platform_classes = set(platform_encoder.classes_)
    platform_internal = next((p for p in platform_candidates if p in platform_classes), None)
    if platform_internal is None:
        raise ValueError(
            f"Unknown platform '{platform}'. Expected one of: {sorted(platform_classes)}"
        )
    
    # Encode protocol
    protocol_encoded = label_encoder.transform([protocol])[0]
    
    # Encode platform
    platform_encoded = platform_encoder.transform([platform_internal])[0]
    
    # Scale numerical features
    scaled = scaler.transform([[distance_km, noise_factor]])[0]
    
    return np.array([[protocol_encoded, platform_encoded, scaled[0], scaled[1]]])


if __name__ == '__main__':
    # Run preprocessing pipeline
    X_train, X_test, y_train, y_test, encoder, platform_enc, scaler, stats = prepare_data()
    
    print("\n" + "=" * 50)
    print("Data Statistics:")
    print("=" * 50)
    print(f"Protocols: {stats['protocols']}")
    print(f"Platforms: {stats['platforms']}")
    print(f"Distance range: {stats['distance_range']} km")
    print(f"Noise factor range: {stats['noise_range']}")
    print(f"Secure key rate range: {stats['key_rate_range']}")
