# Model metrics

The model is deliberately simple. The project is about running it on Azure, not about beating a leaderboard.

## Setup

- Data: IBM Telco Customer Churn, 7,043 customers, of whom 1,869 churned (26.5%).
- Features (8): `tenure`, `MonthlyCharges`, `TotalCharges`, `SeniorCitizen`, `Contract`, `InternetService`, `PaymentMethod`, `PaperlessBilling`.
- Model: logistic regression in a scikit-learn pipeline (scaling of the numbers, one-hot encoding of the text columns).
- Split: 80% train, 20% test (1,409 customers), stratified, `random_state=42`.
- Script: `src/train.py`, logged with MLflow.

## Results on the test set

| Metric | Value |
|---|---|
| Accuracy | 0.796 |
| F1 (churn class) | 0.584 |
| ROC-AUC | 0.838 |

Baseline: always predicting "no churn" gives an accuracy of 0.735, so the model's main value is in ROC-AUC and F1.

## Where each run was trained

| Date | Where | Accuracy | F1 | ROC-AUC |
|---|---|---|---|---|
| 2026-10-12 | Laptop (Phase 1) | 0.796 | 0.584 | 0.838 |
| 2026-10-12 | Azure ML job `joyful_grass_9w8dwr40k9` on cpu-cluster (Phase 4) | 0.796 | 0.584 | 0.838 |
| 2026-10-12 | Azure ML job `bubbly_camera_5dd7jr740n`, started from GitHub Actions (Phase 5) | 0.796 | 0.584 | 0.838 |

## Example prediction

A new month-to-month fiber customer (tenure 2, €85.50 per month, electronic check) gets a churn probability of **0.728**. The same value comes from `uvicorn` on the laptop and from the Docker container.
