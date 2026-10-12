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
