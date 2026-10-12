# Services cheat sheet

One line per question: **What is it? Why here? Where is it?**

| Service | What it is | Why it was used here | Where |
|---|---|---|---|
| Resource group | a folder for Azure resources | everything in one place, deleted with one command | `rg-churn-mlops`, [scripts/names.ps1](../../scripts/names.ps1) |
| Tags | labels on resources (`key=value`) | `feature=...` gives the cost of each part | [infra/main.bicep](../../infra/main.bicep) |
| Bicep | Azure's language for infrastructure as code | the whole setup is a file, repeatable and reviewable | [infra/main.bicep](../../infra/main.bicep) |
| Azure CLI (`az`) | command-line tool for Azure | every step can be typed and saved | [GUIDE.md](../../GUIDE.md) |
| Storage account | stores files (blobs) | holds the dataset and Azure ML files | `stchurnub4786` |
| Azure Machine Learning workspace | home for ML jobs, runs and models | track runs and keep the model versions | `mlw-churn-mlops` |
| Compute cluster | VMs that Azure ML starts for jobs | trains in the cloud; 0 nodes when idle = €0 | [aml/cluster.yml](../../aml/cluster.yml) |
| Data asset | a named, versioned pointer to data | jobs use `churn-data:1`, not a laptop path | [GUIDE.md](../../GUIDE.md) |
| Command job | runs a script on the cluster | the same `train.py` runs in the cloud | [aml/train-job.yml](../../aml/train-job.yml) |
| Curated environment | a ready-made Docker image from Microsoft | no image build needed (faster, cheaper) | `sklearn-1.5` in [aml/train-job.yml](../../aml/train-job.yml) |
| MLflow | open-source tool to log metrics and models | the same code logs locally or to Azure ML | [src/train.py](../../src/train.py) |
| Model registry | versioned list of models | deploy picks `churn-model:1` with its history | Azure ML studio → Models |
| Docker | packs the app and its libraries into an image | runs the same on the laptop and in Azure | [Dockerfile](../../Dockerfile) |
| Container Registry (ACR) | private store for Docker images | the live app pulls its image from here | `acrchurnub4786` |
| Container Apps | runs containers without managing servers | HTTPS URL, scale to zero, simple | `ca-churn-api` |
| Container Apps environment | the shared space where apps run | sends app logs to Log Analytics | `cae-churn-mlops` |
| Managed identity | an Azure identity with no password | the app pulls images and reads secrets safely | `id-churn-api` |
| Key Vault | safe store for secrets | keeps the App Insights connection string out of code | `kv-churn-ub4786` |
| RBAC roles | permissions given to an identity | least privilege: AcrPull, Key Vault Secrets User, Contributor on the group only | [infra/main.bicep](../../infra/main.bicep) |
| Microsoft Entra ID | Azure's identity service | app registration for GitHub | `gh-churn-mlops` |
| OIDC (federated credential) | login with a short-lived token instead of a secret | GitHub logs in to Azure with no stored password | [infra/github-federated-credential.json](../../infra/github-federated-credential.json) |
| GitHub Actions | CI/CD pipelines on GitHub | test on every push, then deploy | [.github/workflows/](../../.github/workflows/ci.yml) |
| Log Analytics | log database, queried with KQL | stores all logs, capped at 0.5 GB per day | `log-churn-mlops` |
| Application Insights | app monitoring: requests, errors, speed | see what the live API does | `appi-churn-mlops`, [src/app.py](../../src/app.py) |
| KQL | the query language of Log Analytics | answers like "how many failed requests?" | [docs/kql/](../kql/failed_requests.kql) |
| Alert rule + action group | a rule that sends an email | more than 5 server errors in 5 minutes → email | `alert-churn-server-errors` |
| Cost Management | Azure's cost and budget tool | budget alert, cost per resource and per tag | [docs/cost/](../cost/COST_LOG.md) |

## The roles, in one table

| Who | Role | On what | Why |
|---|---|---|---|
| `id-churn-api` (the app) | AcrPull | the registry | pull its own image |
| `id-churn-api` (the app) | Key Vault Secrets User | the vault | read its one secret |
| `gh-churn-mlops` (GitHub) | Contributor | the resource group only | deploy and start training |
| the developer | Key Vault Secrets Officer | the vault | write the secret once |
