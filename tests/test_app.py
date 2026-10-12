from fastapi.testclient import TestClient

from src.app import app

# A test client sends requests to the API without starting a server
client = TestClient(app)

# A new customer who pays a lot every month (likely to leave)
RISKY_CUSTOMER = {
    "tenure": 2,
    "MonthlyCharges": 85.5,
    "TotalCharges": 171,
    "SeniorCitizen": 0,
    "Contract": "Month-to-month",
    "InternetService": "Fiber optic",
    "PaymentMethod": "Electronic check",
    "PaperlessBilling": "Yes",
}


# The health check answers "ok"
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# A valid customer gets a probability between 0 and 1
def test_predict_returns_probability():
    response = client.post("/predict", json=RISKY_CUSTOMER)
    assert response.status_code == 200
    probability = response.json()["churn_probability"]
    assert 0 <= probability <= 1


# A customer with a missing field is refused with error 422
def test_predict_missing_field():
    customer = dict(RISKY_CUSTOMER)
    del customer["tenure"]
    response = client.post("/predict", json=customer)
    assert response.status_code == 422
