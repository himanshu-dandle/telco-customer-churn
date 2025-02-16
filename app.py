import os
import logging
import time
import pandas as pd
import xgboost as xgb
from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from logging.handlers import RotatingFileHandler

# Initialize logging
log_handler = RotatingFileHandler("api_logs.log", maxBytes=5*1024*1024, backupCount=5)
logging.basicConfig(handlers=[log_handler], level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()

# Azure Key Vault Configuration
KEY_VAULT_NAME = "HimanshuKeyVault"  # Ensure this is the correct Key Vault name
SECRET_NAME = "API-KEY"

# Retrieve API Key
API_KEY = None
try:
    logging.info("Attempting to retrieve API key from Azure Key Vault...")
    credential = DefaultAzureCredential()
    keyvault_url = f"https://{KEY_VAULT_NAME}.vault.azure.net"
    secret_client = SecretClient(vault_url=keyvault_url, credential=credential)
    API_KEY = secret_client.get_secret(SECRET_NAME).value.strip()

    if API_KEY:
        logging.info(f"Successfully retrieved API Key: {API_KEY[:5]}****")  # Mask key for security
    else:
        logging.error("API Key is empty. Check Azure Key Vault.")
except Exception as e:
    logging.error(f"Failed to fetch API Key from Key Vault: {str(e)}")
    API_KEY = None  # Ensure it remains None on failure

# Load the XGBoost model
MODEL_PATH = "/app/data/output/xgboost_model_v5.json"
model = None

# Check if the model file exists
if not os.path.exists(MODEL_PATH):
    logging.error(f"Model file not found at {MODEL_PATH}. Check deployment.")
else:
    try:
        logging.info(f"Loading model from {MODEL_PATH}...")
        model = xgb.Booster()
        model.load_model(MODEL_PATH)
        logging.info("Model loaded successfully.")
    except Exception as e:
        logging.error(f"Error loading XGBoost model: {str(e)}")
        model = None  # Ensure it's explicitly set to None on failure

# Define request body
class ChurnRequest(BaseModel):
    TotalCharges: float
    MonthlyCharges: float
    tenure: int
    Contract: int
    PaymentMethod: int
    OnlineSecurity: int

# API Key Authentication
def validate_api_key(x_api_key: str = Header(None)):
    if API_KEY is None:
        logging.error("API Key is not available. Check Azure Key Vault permissions.")
        raise HTTPException(status_code=500, detail="Server configuration error")
    
    if x_api_key is None or x_api_key.strip() != API_KEY.strip():
        logging.warning(f"Invalid API Key attempt: Received '{x_api_key}', Expected '{API_KEY[:5]}****'")
        raise HTTPException(status_code=403, detail="Invalid API Key")

# Prediction Endpoint
@app.post("/predict")
async def predict_churn(request: Request, data: ChurnRequest, x_api_key: str = Header(None)):
    validate_api_key(x_api_key)
    start_time = time.time()
    
    try:
        if model is None:
            logging.error("Prediction failed: Model is not loaded.")
            raise HTTPException(status_code=500, detail="Model is not loaded properly!")

        # Convert request to DataFrame
        df = pd.DataFrame([data.dict()])
        
        # Log input data
        logging.info(f"Received prediction request: {df.to_dict(orient='records')}")

        # Convert to DMatrix for XGBoost
        dtest = xgb.DMatrix(df)
        
        # Make prediction
        probability = float(model.predict(dtest)[0])
        churn_prediction = 1 if probability > 0.5 else 0

        # Log prediction result
        logging.info(f"Prediction: {churn_prediction}, Probability: {round(probability, 4)}")

        return {
            "churn_prediction": churn_prediction,
            "churn_probability": round(probability, 4),
            "response_time": round(time.time() - start_time, 4)
        }
    except Exception as e:
        logging.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Health Check Endpoint
@app.get("/")
async def home():
    return {"message": "Customer Churn Prediction API is running!"}

# Run the FastAPI app
import uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
