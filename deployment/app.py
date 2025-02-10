from fastapi import FastAPI, Header, HTTPException, Request
import pandas as pd
from pydantic import BaseModel
import logging
import os
import time
import xgboost as xgb
from logging.handlers import RotatingFileHandler
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import uvicorn  # Ensure uvicorn is imported

# Initialize logging with rotation (5MB per log file, up to 5 backups)
log_handler = RotatingFileHandler("api_logs.log", maxBytes=5*1024*1024, backupCount=5)
logging.basicConfig(handlers=[log_handler], level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize FastAPI app
app = FastAPI()

# Azure Key Vault Configuration
KEY_VAULT_NAME = "HimanshuKeyVault"  # Replace with your Key Vault name
SECRET_NAME = "API-KEY"  # Name of the secret in Key Vault

try:
    # Authenticate with Azure Key Vault
    credential = DefaultAzureCredential()
    keyvault_url = f"https://{KEY_VAULT_NAME}.vault.azure.net"
    secret_client = SecretClient(vault_url=keyvault_url, credential=credential)

    # Retrieve API Key from Key Vault
    API_KEY = secret_client.get_secret(SECRET_NAME).value
    logging.info("Successfully retrieved API Key from Azure Key Vault")
except Exception as e:
    logging.error(f"Failed to fetch API Key from Key Vault: {str(e)}")
    API_KEY = None  # Ensure API key isn't None to avoid errors

# Load the saved XGBoost model from JSON
try:
    model = xgb.Booster()
    model.load_model("output/xgboost_model_v5.json")
    logging.info("Model loaded successfully.")
except Exception as e:
    logging.error(f"Error loading XGBoost model: {str(e)}")
    model = None  # Set to None if loading fails

# Define feature names (must match training order)
FEATURES = ['TotalCharges', 'MonthlyCharges', 'tenure', 'Contract', 'PaymentMethod', 'OnlineSecurity']

# Define request body format
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
        logging.error("API Key is not set. Check Azure Key Vault configuration.")
        raise HTTPException(status_code=500, detail="Server configuration error")

    if x_api_key != API_KEY:
        logging.warning("Unauthorized API Key attempt detected!")
        raise HTTPException(status_code=403, detail="Invalid API Key")

@app.post("/predict")
async def predict_churn(request: Request, data: ChurnRequest, x_api_key: str = Header(None)):
    validate_api_key(x_api_key)  # Validate API Key

    client_ip = request.client.host
    start_time = time.time()  # Start timing

    try:
        # Ensure model is loaded
        if model is None:
            raise ValueError("Model is not loaded properly!")

        # Convert input data to DataFrame
        df = pd.DataFrame([data.dict()])

        # Convert to XGBoost DMatrix format
        dtest = xgb.DMatrix(df)

        # Make a prediction
        prediction = model.predict(dtest)[0]
        probability = float(prediction)  # Convert to Python float

        response_time = round(time.time() - start_time, 4)  # End timing

        # Log API call with details
        logging.info(f"IP: {client_ip}, Request: {data.dict()}, Prediction: {prediction}, Probability: {probability}, Response Time: {response_time}s")

        return {
            "churn_prediction": 1 if probability > 0.5 else 0,  # Convert to binary classification
            "churn_probability": round(probability, 4),
            "response_time": response_time
        }

    except Exception as e:
        logging.error(f"Error: {str(e)} | Request: {data.dict()} | IP: {client_ip}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/")
async def home():
    return {"message": "Customer Churn Prediction API is running!"}

# ✅ Ensure the API listens on the correct port for Azure deployment
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Read PORT from environment variables
    uvicorn.run(app, host="0.0.0.0", port=port)
