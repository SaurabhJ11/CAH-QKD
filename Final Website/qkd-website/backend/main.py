"""FastAPI backend for QKD Secure Key Rate Prediction using Keras model."""

import os
from datetime import datetime
from typing import Literal

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Suppress TensorFlow logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# ── Configuration ────────────────────────────────────────────────────────────
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BACKEND_DIR))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
MODEL_FILE = "best_model.keras"
SCALER_FILE = "scaler.pkl"
LABEL_ENCODER_FILE = "label_encoder.pkl"
PLATFORM_ENCODER_FILE = "platform_encoder.pkl"
DATA_STATS_FILE = "data_stats.pkl"

# ── Protocol and Platform Constants ─────────────────────────────────────────
# Protocols supported by the Keras model (from label encoder)
ALL_PROTOCOLS = [
    "AB-QKD", "B92", "BB84", "BBM92", "DS6-QKD", 
    "Decoy-BB84", "EEPM-QKD", "SARG04", "Six-State"
]

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


# ── Pydantic Models ──────────────────────────────────────────────────────────
PlatformType = Literal["ionq_aria", "ionq_harmony", "rigetti_aspen_m3", "oqc_lucy"]


class RecommendRequest(BaseModel):
    distance_km: float = Field(..., ge=5, le=200, description="Fiber distance in km")
    platform: PlatformType = Field(..., description="Quantum platform identifier")
    noise_factor: float = Field(..., ge=0.5, le=3.0, description="Noise factor")
    top_n: int = Field(default=3, ge=1, le=9, description="Number of top protocols")


class ProtocolResult(BaseModel):
    name: str
    secure_key_rate: float
    transmission: float = 0.0
    rank: int


class RecommendResponse(BaseModel):
    protocols: list[ProtocolResult]
    request: RecommendRequest
    timestamp: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    timestamp: str


# ── QKD Predictor Class (Keras) ──────────────────────────────────────────────
class QKDPredictor:
    """Load a trained Keras model and recommend best QKD protocols."""

    def __init__(self, model_path: str, scaler_path: str, label_enc_path: str, platform_enc_path: str):
        from tensorflow import keras
        
        self.model = keras.models.load_model(model_path)
        self.scaler = joblib.load(scaler_path)
        self.label_encoder = joblib.load(label_enc_path)
        self.platform_encoder = joblib.load(platform_enc_path)
        
        # Get protocol classes from label encoder
        self.protocols = list(self.label_encoder.classes_)
        self.platforms = list(self.platform_encoder.classes_)
        print(f"Keras model loaded. Protocols: {self.protocols}, Platforms: {self.platforms}")
        print(f"Scaler expects features: {list(self.scaler.feature_names_in_)}")

    def predict_top_protocols(
        self,
        distance_km: float,
        platform: str,
        noise_factor: float,
        top_n: int = 3,
    ) -> list[dict]:
        """Predict secure key rate for every protocol and return top_n results."""
        import pandas as pd
        
        # Platform encoder uses lowercase names directly (ionq_aria, etc.)
        try:
            platform_encoded = self.platform_encoder.transform([platform])[0]
        except ValueError:
            platform_encoded = 0
            print(f"Warning: Platform '{platform}' not found, using fallback")

        # Scale distance and noise using DataFrame with proper feature names
        features_df = pd.DataFrame(
            [[distance_km, noise_factor]], 
            columns=['distance_km', 'noise_factor']
        )
        features_scaled = self.scaler.transform(features_df)

        results = []
        for protocol in self.protocols:
            # Encode protocol
            protocol_encoded = self.label_encoder.transform([protocol])[0]
            
            # Build full feature vector for model: [protocol_encoded, platform_encoded, scaled_distance, scaled_noise]
            model_input = np.array([[protocol_encoded, platform_encoded, features_scaled[0][0], features_scaled[0][1]]])
            
            # Predict
            prediction = self.model.predict(model_input, verbose=0)
            
            # Model outputs [secure_key_rate, transmission]
            secure_key_rate = float(np.clip(prediction[0][0], 0, 1))
            transmission = float(np.clip(prediction[0][1], 0, 1))
            
            results.append({
                "protocol": protocol,
                "secure_key_rate": secure_key_rate,
                "transmission": transmission,
            })

        # Sort by secure key rate descending
        results.sort(key=lambda r: r["secure_key_rate"], reverse=True)
        return results[:top_n]

    def predict_all_protocols(
        self,
        distance_km: float,
        platform: str,
        noise_factor: float,
    ) -> list[dict]:
        """Predict secure key rate for all protocols."""
        return self.predict_top_protocols(distance_km, platform, noise_factor, top_n=len(self.protocols))


# ── FastAPI App ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="QKD Secure Key Rate Prediction API",
    description="Predict optimal QKD protocols using Keras neural network model",
    version="2.0.0",
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model on startup
predictor: QKDPredictor | None = None


@app.on_event("startup")
async def load_model():
    global predictor
    model_path = os.path.join(MODELS_DIR, MODEL_FILE)
    scaler_path = os.path.join(MODELS_DIR, SCALER_FILE)
    label_enc_path = os.path.join(MODELS_DIR, LABEL_ENCODER_FILE)
    platform_enc_path = os.path.join(MODELS_DIR, PLATFORM_ENCODER_FILE)

    # Check all required files exist
    required_files = [
        (model_path, "Keras model"),
        (scaler_path, "Scaler"),
        (label_enc_path, "Label encoder"),
        (platform_enc_path, "Platform encoder"),
    ]
    
    for path, name in required_files:
        if not os.path.exists(path):
            print(f"WARNING: {name} not found at {path}")
            return

    try:
        predictor = QKDPredictor(model_path, scaler_path, label_enc_path, platform_enc_path)
        print("QKD Keras Predictor initialized successfully!")
    except Exception as e:
        print(f"ERROR loading model: {e}")
        import traceback
        traceback.print_exc()


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        model_loaded=predictor is not None,
        timestamp=datetime.now().isoformat(),
    )


@app.post("/api/recommend", response_model=RecommendResponse)
async def recommend_protocols(request: RecommendRequest):
    """Recommend top QKD protocols for given experimental conditions."""
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        print(f"Received recommendation request: {request}")
        # results = predictor.predict_top_protocols(
        #     distance_km=request.distance_km,
        #     platform=request.platform,
        #     noise_factor=request.noise_factor,
        #     top_n=request.top_n,
        # )

        results = predictor.predict_top_protocols(
            distance_km=request.distance_km,
            platform=request.platform,
            noise_factor=request.noise_factor,
            top_n=10,
        )
        

        protocols = [
            ProtocolResult(
                name=r["protocol"],
                secure_key_rate=r["secure_key_rate"],
                transmission=r.get("transmission", 0.0),
                rank=idx + 1,
            )
            for idx, r in enumerate(results)
        ]

        return RecommendResponse(
            protocols=protocols,
            request=request,
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/protocols")
async def get_all_protocol_rates(
    distance: float = 100,
    platform: PlatformType = "ionq_aria",
    noise: float = 1.5,
):
    """Get predicted rates for all protocols."""
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        results = predictor.predict_all_protocols(
            distance_km=distance,
            platform=platform,
            noise_factor=noise,
        )

        return [
            ProtocolResult(
                name=r["protocol"],
                secure_key_rate=r["secure_key_rate"],
                transmission=r.get("transmission", 0.0),
                rank=idx + 1,
            )
            for idx, r in enumerate(results)
        ]
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
