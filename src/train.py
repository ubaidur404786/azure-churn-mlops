import argparse
import os

import joblib
import mlflow
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Columns the model uses (the API sends the same fields)
NUMBER_COLUMNS = ["tenure", "MonthlyCharges", "TotalCharges", "SeniorCitizen"]
TEXT_COLUMNS = ["Contract", "InternetService", "PaymentMethod", "PaperlessBilling"]
FEATURES = NUMBER_COLUMNS + TEXT_COLUMNS

# Read the paths from the command line (Azure ML passes its own paths)
parser = argparse.ArgumentParser()
parser.add_argument("--data", default="data/churn.csv")
parser.add_argument("--model-dir", default="model")
args = parser.parse_args()

# Read the customer table from the CSV file
data = pd.read_csv(args.data)

# TotalCharges has 11 empty values for new customers: turn them into 0
data["TotalCharges"] = pd.to_numeric(data["TotalCharges"], errors="coerce").fillna(0)

# Turn the target "Yes"/"No" into 1/0
target = (data["Churn"] == "Yes").astype(int)
data = data[FEATURES]

# Keep 20% of the customers aside to test the model
x_train, x_test, y_train, y_test = train_test_split(
    data, target, test_size=0.2, random_state=42, stratify=target
)

# Scale the number columns and one-hot encode the text columns
prepare = ColumnTransformer([
    ("numbers", StandardScaler(), NUMBER_COLUMNS),
    ("text", OneHotEncoder(handle_unknown="ignore"), TEXT_COLUMNS),
])

# Join the preparation and the model into one pipeline
model = Pipeline([
    ("prepare", prepare),
    ("classifier", LogisticRegression(max_iter=1000)),
])

# Start an MLflow run (locally or in Azure ML, the same code works)
with mlflow.start_run():
    # Train the model
    model.fit(x_train, y_train)

    # Predict on the test customers
    prediction = model.predict(x_test)
    probability = model.predict_proba(x_test)[:, 1]

    # Compute the metrics
    accuracy = accuracy_score(y_test, prediction)
    f1 = f1_score(y_test, prediction)
    roc_auc = roc_auc_score(y_test, probability)
    print(f"accuracy: {accuracy:.3f}")
    print(f"f1:       {f1:.3f}")
    print(f"roc_auc:  {roc_auc:.3f}")

    # Log the settings and the metrics to MLflow
    mlflow.log_param("model", "LogisticRegression")
    mlflow.log_param("features", len(FEATURES))
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("f1", f1)
    mlflow.log_metric("roc_auc", roc_auc)

    # Save the model file and attach it to the MLflow run
    os.makedirs(args.model_dir, exist_ok=True)
    model_path = os.path.join(args.model_dir, "model.pkl")
    joblib.dump(model, model_path)
    mlflow.log_artifact(model_path)
    print(f"model saved to {model_path}")
