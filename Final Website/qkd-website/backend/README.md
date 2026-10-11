# QKD Prediction Backend

FastAPI backend for QKD Secure Key Rate Prediction using Keras neural network model.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure models are in place:
The backend expects these model files in `../../models/`:
- `best_model.keras` - Trained Keras neural network
- `scaler.pkl` - Feature scaler
- `label_encoder.pkl` - Protocol label encoder
- `platform_encoder.pkl` - Platform encoder

## Running the Server

```bash
# Development mode
uvicorn main:app --reload --port 8001

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8001
```

## API Endpoints

### Health Check
```
GET /health
```

### Recommend Protocols
```
POST /api/recommend
Content-Type: application/json

{
  "distance_km": 100,
  "platform": "ionq_aria",
  "noise_factor": 1.5,
  "top_n": 3
}
```

### Get All Protocol Rates
```
GET /api/protocols?distance=100&platform=ionq_aria&noise=1.5
```

## Available Platforms
- `ionq_aria` - IonQ Aria (trapped ion)
- `ionq_harmony` - IonQ Harmony (trapped ion)
- `rigetti_aspen_m3` - Rigetti Aspen-M3 (superconducting)
- `oqc_lucy` - OQC Lucy (superconducting)

## Supported Protocols
- BB84 - Original QKD protocol
- BBM92 - Entanglement-based protocol
- SARG04 - Modified BB84 with improved PNS attack resistance
- Six-State - Extended BB84 using three conjugate bases
- Decoy-BB84 - BB84 with decoy states
- Novel - Experimental protocol variations

## API Documentation
Once running, visit:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc
