# Learning log

One entry per step: date, what we did, key commands, errors and fixes.

## Phase 0 — Safety, cost tracking and setup

### 2026-10-11 — 0.1 Check the subscription
- Portal → Subscriptions: "Azure subscription 1", Azure Plan (Microsoft Customer Agreement free account).
- Credit: $200 (€175.99), ends about 2026-11-10. The new free account has no "spending limit" toggle: when the credit ends, the account stops unless it is upgraded. We never upgrade.
- Screenshot: `00_credit_start.png`.

### 2026-10-11 — 0.2 Budget alert
- Portal → Cost Management → Budgets: budget of 5 USD per month, alerts at 5%, 50%, 80%, 100% actual and 100% forecast, sent by email.
- Error: the first save kept only the 5% alert. Fix: edit the budget, add the other alerts again, save, and check the list.
- Screenshot: `00_budget.png`.

### 2026-10-11 — 0.3 Cost estimate
- Wrote `docs/cost/estimate.md`: about $1.70 for 7 days. Biggest risk: a compute cluster left with min nodes above 0.

### 2026-10-11 — 0.4 Install the tools
- Python 3.12, Git, VS Code, Docker Desktop, Azure CLI, GitHub CLI.
- Error: `az` was not found. Fix: `winget install -e --id Microsoft.AzureCLI`, then open a new terminal.

### 2026-10-12 — 0.5 Logins
- `az login`, `az account show` (subscription Enabled), `gh auth login` (scopes include `repo` and `workflow`).

### 2026-10-12 — 0.6 CLI extensions and resource providers
- `az extension add -n ml`, `az extension add -n containerapp`, `az bicep install`.
- `az provider register -n <namespace>` for 7 providers (App, OperationalInsights, ContainerRegistry, KeyVault, MachineLearningServices, Insights, Storage).
- Note: providers show "Registering" for a few minutes before "Registered". Registering is free.

### 2026-10-12 — 0.7 Git and GitHub
- `git init -b main`, `git add .`, `git commit`, `gh repo create azure-churn-mlops --public --source . --remote origin --push`.
- Error: "`--push` enabled but no commits found". Cause: the files were never staged, so there was no commit. Fix: `git add .`, `git commit`, then run `gh repo create` again.

### 2026-10-12 — 0.8 Project files
- Added `.gitignore`, `requirements.txt`, `scripts/names.ps1`, this log, `docs/cost/COST_LOG.md` and `docs/results/`.
- Kept private files out of Git: `PLAN.md`, `CLAUDE.md` and `.claude/` are in `.gitignore`. PLAN.md was already pushed, so: `git rm --cached PLAN.md`, `git commit --amend`, `git push --force origin main`.
- Checked `. .\scripts\names.ps1` loads. Credit at the end of Phase 0: €175.99 (no resources yet).

## Phase 1 — Simple model + API on the laptop

### 2026-10-12 — 1.1 Virtual environment and dataset
- `python -m venv .venv`, `.\.venv\Scripts\Activate.ps1`, `pip install -r requirements.txt`.
- Downloaded the IBM Telco Customer Churn CSV to `data/churn.csv` with `Invoke-WebRequest`: 7,043 customers, 21 columns.

### 2026-10-12 — 1.2 Training script
- `src/train.py`: logistic regression in a scikit-learn pipeline (scaling + one-hot encoding), 8 features, 80/20 split.
- 11 customers have an empty `TotalCharges` (tenure 0). Fix: convert to numbers and fill with 0.
- MLflow 3 stores local runs in `mlflow.db` (SQLite) by default, plus artifacts in `mlruns/`. Both are git-ignored.
- Result: accuracy 0.796, F1 0.584, ROC-AUC 0.838 (test set of 1,409 customers).

### 2026-10-12 — 1.3 Web API
- `src/app.py`: FastAPI with `GET /health` and `POST /predict`. It loads `model/model.pkl` once at start (path can be changed with the `MODEL_PATH` variable).
- Run locally: `uvicorn src.app:app --reload`, then open http://localhost:8000/docs.

### 2026-10-12 — 1.4 Tests
- `tests/test_app.py`: 3 pytest tests (health check, valid prediction between 0 and 1, missing field gives error 422).
- `pytest.ini` sets `pythonpath = .` so the tests can import `src.app`.
- The tests need `model/model.pkl`, so run `python src/train.py` first (CI does the same).

### 2026-10-12 — 1.5 Docker image
- `Dockerfile`: `python:3.12-slim`, installs `requirements-api.txt`, copies `src/` and `model/`, runs as a non-root user, serves on port 8000.
- `requirements-api.txt` holds only the API packages, pinned to the laptop versions, so the pickled model loads with the same scikit-learn. MLflow and pytest stay out of the image.
- `.dockerignore` keeps `.venv`, data, docs and private files out of the build.
- Commands: `docker build -t churn-api:local .` and `docker run --rm -p 8000:8000 churn-api:local`.
- Result: container built and running; `/docs` returns 0.728 for the test customer, same as uvicorn. Screenshot `01_local_docs.png`.
- Opening http://localhost:8000/ gives 404: normal, the API only has `/health`, `/predict` and `/docs`.

### 2026-10-12 — 1.6 Model metrics
- `docs/results/model_metrics.md`: setup, test-set metrics, baseline (always "no churn" = 0.735 accuracy), and the example prediction.

## Phase 2 — Azure resources with Bicep

### 2026-10-12 — 2.1 Bicep file
- `infra/main.bicep` describes every resource in one file. Each one has the tags `project`, `owner`, `env` and one `feature` tag.
- Resources: Log Analytics (0.5 GB daily cap), Application Insights, Key Vault (RBAC mode, 7-day soft delete), Storage (Standard LRS, no public blobs), ACR Basic (no admin user), Azure ML workspace, Container Apps environment, user-assigned managed identity.
- Roles: the identity gets AcrPull on the registry and Key Vault Secrets User on the vault. The user gets Key Vault Secrets Officer on the vault to write the secret in Phase 3.
- The Azure ML workspace is not linked to our ACR. The curated sklearn environment needs no image build, so no extra registry is created.

### 2026-10-12 — 2.2 Resource group
- `az group create --name $RG --location $LOCATION --tags $TAGS` created `rg-churn-mlops` in francecentral with the 3 base tags. A resource group is free.

### 2026-10-12 — 2.3 What-if preview
- `$USER_ID = az ad signed-in-user show --query id -o tsv` gets your Entra ID object id (not a secret).
- `az deployment group what-if --resource-group $RG --template-file infra/main.bicep --parameters userObjectId=$USER_ID` → `Resource changes: 11 to create`. Free, creates nothing.

### 2026-10-12 — 2.4 Deployment
- `az deployment group create --resource-group $RG --template-file infra/main.bicep --parameters userObjectId=$USER_ID` → `Succeeded`. All 11 resources created.
- Cost starts now: mainly ACR Basic (about €0.16/day). The rest is free or a few cents while idle.
- Screenshot `02_bicep_deployment.png`.

### 2026-10-12 — 2.5 What each resource does
- **log-churn-mlops (Log Analytics, monitoring):** one place that stores logs from all services, searched with KQL. Capped at 0.5 GB a day so it stays in the free 5 GB a month.
- **appi-churn-mlops (Application Insights, monitoring):** tracks the API's requests, response times and errors. Its data lives inside the Log Analytics workspace.
- **kv-churn-ub4786 (Key Vault, secrets):** a safe store for secrets, so none are in code or Git. RBAC mode: access is given with Azure roles, not access policies.
- **id-churn-api (managed identity, secrets):** an Azure identity with no password. The Container App uses it to pull images (AcrPull) and read secrets (Key Vault Secrets User).
- **stchurnub4786 (Storage, data):** holds the dataset and the files Azure ML writes. Standard LRS (3 copies in one datacenter), HTTPS only, no public blobs.
- **acrchurnub4786 (Container Registry, registry):** a private Docker Hub for our API image. Basic plan, no admin user, pulled with the managed identity.
- **mlw-churn-mlops (Azure ML workspace, training):** the home for training jobs, MLflow runs and the model registry. The workspace is free; only compute costs money.
- **cae-churn-mlops (Container Apps environment, serving):** the shared space where the Container App will run, with its logs sent to Log Analytics. No cost until an app runs.
- **3 role assignments:** the identity gets AcrPull on the registry and Key Vault Secrets User on the vault; the user gets Key Vault Secrets Officer on the vault.
- The Deployments list also shows a failed `Failure-Anomalies-Alert-Rule-Deployment-...`, created 9 minutes after `main`. Azure starts it by itself to add a "smart detection" alert to Application Insights. It is not from our Bicep, it creates nothing and costs nothing. Our own deployment `main` succeeded. (Likely cause: the `Microsoft.AlertsManagement` provider is not registered. Not needed; Phase 6 adds our own alert.)
- The resource group now shows 9 items: Azure also added an action group "Application Insights Smart Detection" (global, untagged) when App Insights was created. It is free and is deleted with the resource group in Phase 8.
- Screenshots: `02_resource_group.png`, `02_bicep_deployment.png` (Deployments → main), `02_tags.png` (Portal → Tags: all 6 `feature` values plus the 3 base tags).
