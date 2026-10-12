# Save the metrics of every Azure ML training run to a CSV file.
# Usage: python scripts/export_aml_runs.py <mlflow-tracking-uri>
# Get the uri with: az ml workspace show -g $RG -n $AML_WORKSPACE --query mlflow_tracking_uri -o tsv

import sys

import mlflow

# Point MLflow at the Azure ML workspace
mlflow.set_tracking_uri(sys.argv[1])

# Read all runs of the training experiment as a table
runs = mlflow.search_runs(experiment_names=["churn-training"])

# Keep only the useful columns
columns = ["run_id", "status", "start_time", "end_time",
           "metrics.accuracy", "metrics.f1", "metrics.roc_auc"]
runs = runs[[c for c in columns if c in runs.columns]]

# Write the table to the results folder
runs.to_csv("docs/results/aml_runs.csv", index=False)
print(runs.to_string(index=False))
