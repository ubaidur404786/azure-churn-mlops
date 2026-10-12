import logging
import os

# Send requests and logs to Application Insights, only when Azure gives us the connection string
# (this must run before FastAPI is imported, so every request is recorded)
if os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
    from azure.monitor.opentelemetry import configure_azure_monitor

    configure_azure_monitor(logger_name="churn-api")

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

# Our own logger: its messages go to Application Insights as traces
logger = logging.getLogger("churn-api")
logger.setLevel(logging.INFO)

# Load the trained model once, when the API starts
MODEL_PATH = os.getenv("MODEL_PATH", "model/model.pkl")
model = joblib.load(MODEL_PATH)

app = FastAPI(title="Churn prediction API")


# The customer fields the API expects (same as in train.py)
class Customer(BaseModel):
    tenure: int
    MonthlyCharges: float
    TotalCharges: float
    SeniorCitizen: int
    Contract: str
    InternetService: str
    PaymentMethod: str
    PaperlessBilling: str


# Simple check that the API is running
@app.get("/health")
def health():
    return {"status": "ok"}


# Return the churn probability for one customer
@app.post("/predict")
def predict(customer: Customer):
    # Put the customer in a one-row table, like the training data
    data = pd.DataFrame([customer.model_dump()])

    # Ask the model for the probability of churn
    probability = model.predict_proba(data)[0, 1]

    # Write one log line per prediction (no personal data, only the result)
    logger.info("prediction churn_probability=%.3f", probability)

    return {
        "churn_probability": round(float(probability), 3),
        "churn": bool(probability >= 0.5),
    }
