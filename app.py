from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
import joblib
import pandas as pd
import numpy as np
import os
import logging
import uvicorn
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("fraud_api")

# Paths
MODEL_PATH = os.path.join("artifacts", "model_trainer", "calibrated_model.joblib")

# Global variables for model
model = None

# ----------------- Helper Functions ----------------- #

def probability_to_risk_score(probability: float) -> int:
    """Converts a 0.0-1.0 probability to a 0-100 integer score."""
    return int(np.clip(probability * 100, 0, 100))

def get_risk_tier(risk_score: int) -> str:
    """Maps a risk score to a business tier."""
    if risk_score < 20: return "VERY_LOW"
    elif risk_score < 40: return "LOW"
    elif risk_score < 60: return "MEDIUM"
    elif risk_score < 80: return "HIGH"
    else: return "CRITICAL"

def fraud_decision_engine(fraud_probability: float, auto_decline_threshold: float = 0.90, manual_review_threshold: float = 0.60):
    """Maps a fraud probability to a business decision."""
    risk_score = probability_to_risk_score(fraud_probability)
    risk_tier = get_risk_tier(risk_score)
    
    if fraud_probability >= auto_decline_threshold:
        decision = "DECLINE"
    elif fraud_probability >= manual_review_threshold:
        decision = "REVIEW"
    else:
        decision = "APPROVE"
        
    return risk_score, risk_tier, decision

# ----------------- App Lifecycle ----------------- #

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load model on startup
    global model
    logger.info("Starting up API...")
    if not os.path.exists(MODEL_PATH):
        logger.error(f"Model file not found at {MODEL_PATH}. Prediction endpoints will fail.")
    else:
        try:
            model = joblib.load(MODEL_PATH)
            logger.info("Calibrated fraud model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
    yield
    # Cleanup on shutdown
    logger.info("Shutting down API...")
    model = None

# Initialize FastAPI app
app = FastAPI(
    title="Fraud Detection API",
    description="Production API for scoring transactions using calibrated LightGBM model.",
    version="1.0.0",
    lifespan=lifespan
)

# ----------------- Schemas ----------------- #

# We use a dict to capture dynamic features since the model can have hundreds of features.
# A strict schema can be defined if features are perfectly known.
class PredictionRequest(BaseModel):
    transaction_id: str = Field(..., description="Unique ID of the transaction")
    features: dict = Field(..., description="Key-value pairs of transaction features expected by the model")

class PredictionResponse(BaseModel):
    transaction_id: str
    fraud_probability: float
    risk_score: int
    risk_level: str
    decision: str

# ----------------- Endpoints ----------------- #

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint to ensure API and model are operational."""
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not loaded.")
    return {"status": "ok", "message": "Fraud Detection API is running and model is loaded."}

@app.get("/metrics", tags=["Metrics"])
def get_metrics():
    """Returns the model evaluation metrics."""
    import json
    metrics_path = os.path.join("artifacts", "model_evaluation", "metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path, "r") as f:
            return json.load(f)
    raise HTTPException(status_code=404, detail="Metrics not found.")

@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict(request: PredictionRequest):
    """
    Predicts fraud probability and risk scores for a given transaction.
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not loaded.")
    
    try:
        # Get expected features from the model
        expected_features = model.feature_names_in_
        
        # Create a DataFrame with 1 row, filled with NaNs (which LightGBM handles natively)
        features_df = pd.DataFrame(columns=expected_features)
        features_df.loc[0] = np.nan
        
        # Update the dataframe with the provided features
        for key, value in request.features.items():
            if key in expected_features:
                features_df.at[0, key] = value
            else:
                logger.warning(f"Feature '{key}' provided but not expected by the model. Ignoring.")
        
        # Ensure correct datatypes if necessary, LightGBM usually handles float well
        features_df = features_df.astype(float)
        
        # Predict probability using calibrated model
        # predict_proba returns [[prob_0, prob_1]]
        fraud_prob = float(model.predict_proba(features_df)[0][1])
        
        # Apply Threshold Logic / Risk Scoring
        # We use a decline threshold of 0.90 (90%) and review threshold of 0.60 (60%)
        # In a real environment, you pull this from a database or config.
        risk_score, risk_tier, decision = fraud_decision_engine(fraud_prob, auto_decline_threshold=0.90, manual_review_threshold=0.60)
        
        logger.info(f"Transaction {request.transaction_id} scored: Prob={fraud_prob:.4f}, Risk={risk_score}, Decision={decision}")
        
        return PredictionResponse(
            transaction_id=request.transaction_id,
            fraud_probability=fraud_prob,
            risk_score=risk_score,
            risk_level=risk_tier,
            decision=decision
        )
        
    except Exception as e:
        logger.error(f"Error during prediction for transaction {request.transaction_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

if __name__ == "__main__":
    # Start the service locally for testing
    uvicorn.run(app, host="0.0.0.0", port=8000)
