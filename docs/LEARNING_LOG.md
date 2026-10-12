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

## Phase 3 — Live API on Azure Container Apps

### 2026-10-12 — 3.1 Image pushed to ACR
- `$IMAGE` added to `scripts/names.ps1` (`acrchurnub4786.azurecr.io/churn-api`).
- `az acr login --name $ACR` (uses the Azure login, no admin user), `docker build -t "${IMAGE}:v1" .`, `docker push "${IMAGE}:v1"`.
- Built on the laptop, not with `az acr build`: free-trial subscriptions often block ACR Tasks.
- First `show-tags` gave `repository "churn-api" is not found`. Cause: the build was done but the push was skipped. Fix: run `docker push`.
- No Docker Hub upload is needed: the image name starts with the ACR address, so `docker push` goes straight to the private registry.

### 2026-10-12 — 3.2 Secret in Key Vault
- `$APPI_CS = az resource show ... --query properties.ConnectionString -o tsv`, then `az keyvault secret set --vault-name $KV --name appinsights-connection-string --value $APPI_CS --query name -o tsv`. The value is never printed.
- It worked because Bicep gave the user the Key Vault Secrets Officer role.
- The same secret is now also in `infra/main.bicep`, so a fresh redeploy creates it in one command.

### 2026-10-12 — 3.3 Container App deployed
- Added to `infra/main.bicep`: the Key Vault secret and the Container App `ca-churn-api` (HTTPS ingress to port 8000, min 0 / max 1 replicas, image pulled and secret read with the managed identity, 0.5 CPU / 1 GB).
- `az deployment group create ... --query properties.outputs.apiUrl.value -o tsv` → `https://ca-churn-api.yellowcliff-1636b7fd.francecentral.azurecontainerapps.io`.
- Screenshot `03_container_app.png` (subscription ID hidden).

### 2026-10-12 — 3.4 Live test
- `/docs` works over HTTPS. `/predict` with the test customer → 200, `churn_probability` 0.728, `churn` true: same as the laptop and local Docker.
- Screenshots `03_live_docs.png`, `03_predict_response.png`.
- New: `docs/tutorial/` keeps every command with its real output and screenshots, phase by phase, for later study.

### 2026-10-12 — 3.5 Live API speed
- `scripts/test_live_api.py` (built-in `urllib`, no extra package): 1 cold request, then 20 warm requests; writes `docs/results/api_speed.md`.
- Result after about 10 minutes idle: cold start 25.91 s. Average of 20 requests 513 ms, but the first 2 were still warming up (4.5 s, 1.7 s). Requests 3–20 average 223 ms; median 238 ms.
- Lesson: scale to zero = €0 when idle, paid for with a ~26 s first request.

## Phase 4 — Train in Azure Machine Learning

### 2026-10-12 — 4.1 Data asset
- `az ml data create --name churn-data --version 1 --type uri_file --path data/churn.csv ...` uploaded the CSV to `workspaceblobstore` (storage `stchurnub4786`).
- A data asset is a named, versioned pointer: jobs use `churn-data:1`, not a laptop path.

### 2026-10-12 — 4.2 Compute cluster
- `aml/cluster.yml` + `az ml compute create --file aml/cluster.yml ...` → `cpu-cluster` Succeeded: Standard_DS11_v2, dedicated, min 0 / max 1, off after 120 s idle, tagged `feature=training`. No quota error.
- `ssh_public_access_enabled: true` is harmless: no SSH user or key was set.

### 2026-10-12 — 4.3 Cloud training job
- `aml/train-job.yml`: command job, `code: ../src`, input `churn-data:1`, output folder `model`, curated env `sklearn-1.5` (version 55), compute `cpu-cluster`.
- `$JOB = az ml job create --file aml/train-job.yml ... --query name -o tsv`, then `az ml job stream --name $JOB ...` → job `joyful_grass_9w8dwr40k9` Completed in 3 min 6 s.
- Metrics in the studio: accuracy 0.7956, f1 0.5838, roc_auc 0.8375 — identical to the laptop (same code, data and split).
- The red "experimental class ... NativeCommandError" lines are harmless warnings on stderr; PowerShell 5.1 colours all stderr red.

### 2026-10-12 — 4.4 Model registered
- `az ml model create --name churn-model --version 1 --type custom_model --path "azureml://jobs/$JOB/outputs/model" ...` → `churn-model:1`, `job_name` joyful_grass_9w8dwr40k9 (lineage back to the job, data and commit).
- To do in Phase 5: this model was trained with scikit-learn 1.5 (curated env) but the API image pins 1.9.1. Align the versions before deploy loads it.

### 2026-10-12 — 4.5 Cluster back to 0 nodes
- `az ml compute list-nodes --name $AML_CLUSTER ...` → `[]`. Studio: current node count 0, "Succeeded (0 nodes)" at 4:23 AM, about 5 minutes after the job ended (120 s idle + removal).
- Screenshots `04_model_registry.png` (subscription id hidden) and `04_cluster_zero_nodes.png`.

### 2026-10-12 — 4.6 Fallback not needed
- The free-trial quota allowed the 2-vCPU cluster, so laptop training with remote MLflow tracking was not used.

## Phase 5 — CI/CD with GitHub Actions + OIDC

### 2026-10-12 — 5.1 OIDC identity for GitHub
- `az ad app create --display-name gh-churn-mlops`, `az ad sp create --id $APP_ID`, `az ad app federated-credential create --id $APP_ID --parameters infra/github-federated-credential.json`.
- Client id `f2d95e42-...`; federated credential `github-main` trusts only `repo:ubaidur404786/azure-churn-mlops:ref:refs/heads/main`. No secret exists.

### 2026-10-12 — 5.2 Contributor on the resource group
- `az role assignment create --assignee-object-id $SP_ID --assignee-principal-type ServicePrincipal --role Contributor --scope $RG_ID` → ServicePrincipal on rg-churn-mlops. Nothing at subscription level.

### 2026-10-12 — 5.3 Repository variables
- `gh variable set AZURE_CLIENT_ID / AZURE_TENANT_ID / AZURE_SUBSCRIPTION_ID --repo $GH_REPO`; `gh variable list` shows all 3. Variables, not secrets: they are ids only.

### 2026-10-12 — 5.4 CI workflow
- `.github/workflows/ci.yml`: checkout, Python 3.12, `pip install -r requirements.txt`, `python src/train.py`, `pytest`. First run 38197476280: success in 1 min 34 s.
- Warning "Node.js 20 is deprecated" for `checkout@v4` / `setup-python@v5`. Fix: `actions/checkout@v5`, `actions/setup-python@v6`.
- Screenshot `05_ci_green.png`; link in `docs/results/pipeline_runs.md`.

### 2026-10-12 — 5.5 Version mismatch between Azure ML and the API
- `az ml model download --name churn-model --version 1 --download-path model_cloud`, `$env:MODEL_PATH = ...`, `pytest` → `AttributeError: Can't get attribute '_RemainderColsList'` plus `InconsistentVersionWarning ... from version 1.5.2 when using version 1.9.1`.
- Cause: the curated `sklearn-1.5` env (Python 3.10, numpy 1.22, pandas 1.5, scikit-learn 1.5.2) pickled classes that 1.9.1 no longer has.
- Fix: pin `scikit-learn==1.5.2`, `numpy==2.1.3`, `pandas==2.2.3`, `joblib==1.4.2` in `requirements.txt` and `requirements-api.txt`. Tested in a scratch venv: loads without warning, predicts 0.728. A custom AML environment was rejected (needs an image build and a second registry).
- Also: a second run of `test_live_api.py` on a warm app overwrote `docs/results/api_speed.md` with a 0.42 s "cold start". Restored the real result; the script now refuses to save when the first request is under 5 s.
- After `pip install -r requirements.txt`, `pytest` with the cloud model → 3 passed.
- A second `test_live_api.py` run after a real idle period gave cold start 22.95 s, average 357 ms. `api_speed.md` now shows both runs.

### 2026-10-12 — 5.5 Deploy workflow
- `.github/workflows/deploy.yml`: runs after CI succeeds on main (`workflow_run`) or by hand. OIDC login → download `churn-model:1` → build image tagged with the commit SHA → test `/health` on the runner → push to ACR → `az containerapp update --image` → check live `/health`.
- Watch out: `infra/main.bicep` has `imageTag = 'v1'`; a Bicep redeploy must pass the current tag.
