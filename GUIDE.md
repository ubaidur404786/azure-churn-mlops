# Guide: build it yourself, step by step

This guide rebuilds the whole project. For **every step** it shows two ways side by side:

- **By code**: the command or file used in this project (repeatable, reviewable, deletable in one go).
- **By hand**: the same thing with clicks in the Azure portal, Azure ML studio or GitHub, which is the best way to see where things live when you are new.

Both give the same result. A good habit is to click through once to understand, then keep the code.

The real outputs, errors and screenshots of every command are in the [tutorial](docs/tutorial/README.md), one page per phase, each with a step-by-step diagram.

> The portal moves its menus from time to time. If a button has moved, use the search bar at the top of the portal, or the search box inside the resource menu.

## Where do you start?

| You have… | Do these steps |
|---|---|
| Nothing yet | all steps, in order |
| **Only a container image** (laptop or Docker Hub) | 0 → 2 → 3 → 4 → 5 → 6 (→ 7 for secrets) |
| **Only code on GitHub** | 0 → 2 → 3, then 8 → 12 to train in Azure ML, then 13 → 17 to build and deploy automatically (18 = training button), then 19 → 21 to monitor |

Every new PowerShell terminal (code way) starts in the project folder with:

```powershell
. .\scripts\names.ps1
```

[scripts/names.ps1](scripts/names.ps1) holds every name used below (`$RG`, `$ACR`, `$KV`…).

## Safety rules (free account)

- Never click **Upgrade**, "Pay-as-you-go" or anything that asks for a card.
- Pick the cheapest plans: Container Registry **Basic**, Container Apps **Consumption only**, Azure ML cluster **min 0 nodes**.
- Put everything in **one resource group**, so one delete removes everything.
- Tag everything: `project`, `owner`, `env` and one `feature` tag (data, training, registry, serving, secrets, monitoring).
- Cost data arrives 8–48 hours late, so €0 in the first days is normal.

---

## Part 1 — Prepare

### Step 0. Budget alert and tools

Why: a budget sends you an email before the cost grows, and the tools let you talk to Azure and GitHub from the laptop.

| | By code | By hand |
|---|---|---|
| Budget | (done in the portal in this project) | Portal → **Cost Management → Budgets** → **+ Add** → 5 USD per month → alerts at 50 %, 80 %, 100 % actual and 100 % forecast → your email |
| Tools | `winget install -e --id Microsoft.AzureCLI` (plus Python, Git, Docker Desktop, GitHub CLI) | download the installers from their websites |
| Log in to Azure | `az login` (the password is typed in the browser only) | sign in at portal.azure.com |
| Log in to GitHub | `gh auth login` | sign in at github.com |
| Add-ons | `az extension add -n ml` · `az extension add -n containerapp` · `az bicep install` | nothing to install |
| Resource providers | `az provider register -n Microsoft.App` (and 6 more) | Portal → **Subscriptions** → your subscription → **Settings → Resource providers** → select → **Register** |

Details and real outputs: [Phase 0](docs/tutorial/phase_00_setup.md).

### Step 1. Model and API on the laptop (no Azure yet)

Why: make sure the code works before paying for anything.

| | By code |
|---|---|
| Environment | `python -m venv .venv` · `.\.venv\Scripts\Activate.ps1` · `pip install -r requirements.txt` |
| Train | `python src/train.py` → `model/model.pkl`, accuracy 0.796 |
| Run the API | `uvicorn src.app:app --reload` → http://localhost:8000/docs |
| Test | `pytest` → 3 passed |
| Container | `docker build -t churn-api:local .` · `docker run --rm -p 8000:8000 churn-api:local` |

Files: [src/train.py](src/train.py), [src/app.py](src/app.py), [tests/test_app.py](tests/test_app.py), [Dockerfile](Dockerfile). Details: [Phase 1](docs/tutorial/phase_01_laptop.md).

---

## Part 2 — Azure resources

### Step 2. Resource group

Why: one folder for every resource. It is free, and deleting it deletes everything inside.

| By code | By hand |
|---|---|
| `az group create --name $RG --location $LOCATION --tags $TAGS` | Portal → **Resource groups** → **+ Create** → name `rg-churn-mlops`, region France Central → **Tags** tab: `project`, `owner`, `env` → **Review + create** |

### Step 3. All the base resources

Why: monitoring, secrets, storage, registry, ML workspace and the serving environment, each tagged with its feature.

**By code, one file and one command:** [infra/main.bicep](infra/main.bicep) describes everything. Preview it for free, then create it:

```powershell
az deployment group what-if --resource-group $RG --template-file infra/main.bicep --parameters userObjectId=$USER_ID
```

```powershell
az deployment group create --resource-group $RG --template-file infra/main.bicep --parameters userObjectId=$USER_ID
```

(`$USER_ID = az ad signed-in-user show --query id -o tsv` first: your own id, so the file can give you the right to write secrets.)

**By hand, one resource at a time** (Portal → **Create a resource** → search the name → **Create**; pick `rg-churn-mlops` and France Central each time):

| Resource (feature tag) | Settings to choose |
|---|---|
| Log Analytics workspace (`monitoring`) | name `log-churn-mlops`; then **Usage and estimated costs → Daily cap** 0.5 GB |
| Application Insights (`monitoring`) | name `appi-churn-mlops`, resource mode workspace-based → `log-churn-mlops` |
| Key Vault (`secrets`) | name `kv-churn-ub4786`, Standard, **Access configuration: Azure role-based access control**, soft-delete 7 days |
| Storage account (`data`) | name `stchurnub4786`, Standard, LRS; **Advanced**: allow blob anonymous access **off**, minimum TLS 1.2 |
| Container Registry (`registry`) | name `acrchurnub4786`, plan **Basic**; keep **Access keys → Admin user off** |
| Azure Machine Learning (`training`) | name `mlw-churn-mlops`, pick the storage, key vault and App Insights above, container registry **None** |
| User assigned managed identity (`secrets`) | name `id-churn-api` |
| Container Apps environment (`serving`) | name `cae-churn-mlops`, plan **Consumption only**, logs → `log-churn-mlops` |

Roles (by hand: the resource → **Access control (IAM)** → **+ Add → Add role assignment**):

| Who | Role | On |
|---|---|---|
| `id-churn-api` (managed identity) | AcrPull | the registry |
| `id-churn-api` | Key Vault Secrets User | the key vault |
| you | Key Vault Secrets Officer | the key vault (even the owner cannot write secrets without it) |

Check: Portal → resource group → list of resources, and **Tags** to see the `feature` values. Details: [Phase 2](docs/tutorial/phase_02_bicep.md).

---

## Part 3 — Serve the API

### Step 4. Put the image in the registry

If the image is **public on Docker Hub**, a Container App can pull it directly (image source "Docker Hub or other registries") and you can skip this step. For a private image, `az acr import --name $ACR --source docker.io/<user>/<image>:<tag> --image churn-api:v1` copies it into your registry; nothing goes through your laptop.

| By code | By hand |
|---|---|
| `az acr login --name $ACR` | the portal has **no upload button** for images, so use the code way or `az acr import` (above) |
| `docker build -t "${IMAGE}:v1" .` | |
| `docker push "${IMAGE}:v1"` | |
| Check: `az acr repository show-tags --name $ACR --repository churn-api -o table` | Check: registry → **Services → Repositories** → `churn-api` → tag `v1` |

### Step 5. Create the Container App

Why: runs the image with a public HTTPS address, pulls it with the identity (no password), and scales to zero.

| | By code | By hand |
|---|---|---|
| Create | resource `app` in [infra/main.bicep](infra/main.bicep), then the same `az deployment group create` as step 3 | Portal → **Create a resource** → **Container App** → **Create** |
| Basics | `managedEnvironmentId: cae.id` | environment `cae-churn-mlops` |
| Image | `image: '${acr.properties.loginServer}/churn-api:${imageTag}'` | **Container** tab: untick quickstart image → Azure Container Registry → `acrchurnub4786` / `churn-api` / `v1` |
| Pull without password | `registries: [{ server, identity: identity.id }]` | authentication **Managed identity** → `id-churn-api` |
| Size | `cpu: 0.5`, `memory: '1Gi'` | 0.5 CPU, 1 Gi |
| Public HTTPS | `ingress: { external: true, targetPort: 8000 }` | **Ingress** tab: enabled, from anywhere, target port **8000** |
| Scale to zero | `scale: { minReplicas: 0, maxReplicas: 1 }` | after creation: **Application → Scale** → min 0, max 1 → **Save** |
| Address | output `apiUrl` | **Overview → Application Url** |

Test: open `<Application Url>/docs` → `POST /predict` → **0.728**, churn true. Speed: `python scripts/test_live_api.py` (cold start ~25 s, warm ~0.2 s). Details: [Phase 3](docs/tutorial/phase_03_container_apps.md).

### Step 6. Deploy a new image version

| By code | By hand |
|---|---|
| `az containerapp update --name $CA --resource-group $RG --image "${IMAGE}:<tag>"` (our [deploy.yml](.github/workflows/deploy.yml) runs this on every green push) | Container App → **Application → Containers** → **Edit and deploy** → change the tag → **Create**. A new **revision** gets the traffic |

### Step 7. A secret from Key Vault (no secret in code)

| | By code | By hand |
|---|---|---|
| Store the secret | `az keyvault secret set --vault-name $KV --name appinsights-connection-string --value $APPI_CS --query name -o tsv` (or resource `appiSecret` in Bicep) | Key Vault → **Objects → Secrets** → **+ Generate/Import** → name + value (App Insights → **Overview → Connection String**) |
| Give it to the app | `secrets: [{ name, keyVaultUrl, identity }]` and `env: [{ name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', secretRef }]` in Bicep | Container App → **Settings → Secrets** → **+ Add** → **Key Vault reference** → secret URL + identity; then **Containers → Edit and deploy → Environment variables** → reference the secret |

---

## Part 4 — Train in Azure Machine Learning

Open the studio by hand: workspace → **Overview** → **Launch studio** (or https://ml.azure.com).

### Step 8. Upload the dataset

| By code | By hand |
|---|---|
| `az ml data create --name churn-data --version 1 --type uri_file --path data/churn.csv --resource-group $RG --workspace-name $AML_WORKSPACE` | Studio → **Assets → Data** → **+ Create** → name `churn-data`, type **File (uri_file)** → **From local files** → `churn.csv` → **Create** |

### Step 9. A compute cluster that costs €0 when idle

| By code | By hand |
|---|---|
| [aml/cluster.yml](aml/cluster.yml) + `az ml compute create --file aml/cluster.yml --resource-group $RG --workspace-name $AML_WORKSPACE` | Studio → **Manage → Compute → Compute clusters** → **+ New** → Dedicated, CPU, `Standard_DS11_v2` → name `cpu-cluster`, **min nodes 0**, max 1, idle seconds 120 → **Create** |

### Step 10. Run the training script as a job

| | By code | By hand |
|---|---|---|
| Submit | [aml/train-job.yml](aml/train-job.yml) + `az ml job create --file aml/train-job.yml --resource-group $RG --workspace-name $AML_WORKSPACE --query name -o tsv` | Studio → **Jobs** → **+ Create job** (Custom) |
| Code | `code: ../src` | upload the `src` folder |
| Command | `python train.py --data ${{inputs.data}} --model-dir ${{outputs.model}}` | same command |
| Input / output | `churn-data:1` / folder `model` | same |
| Environment | `azureml://registries/azureml/environments/sklearn-1.5/labels/latest` | curated **sklearn-1.5** |
| Compute | `azureml:cpu-cluster` | `cpu-cluster` |
| Watch | `az ml job stream --name $JOB …` | the job page: status, **Metrics**, **Outputs + logs** |

Result: accuracy 0.796, f1 0.584, roc_auc 0.838, the same as on the laptop. Note: the model is saved with scikit-learn **1.5.2** (the version in `sklearn-1.5`), so the API pins the same version in [requirements-api.txt](requirements-api.txt). Otherwise it cannot open the model.

### Step 11. Register the model

| By code | By hand |
|---|---|
| `az ml model create --name churn-model --version 1 --type custom_model --path "azureml://jobs/$JOB/outputs/model" --resource-group $RG --workspace-name $AML_WORKSPACE` | the finished job page → **Register model** → Custom, output `model` → name `churn-model` → **Register** |

### Step 12. Check the cluster is back to 0 nodes

| By code | By hand |
|---|---|
| `az ml compute list-nodes --name $AML_CLUSTER --resource-group $RG --workspace-name $AML_WORKSPACE` → `[]` | Studio → **Compute → Compute clusters → cpu-cluster** → **Current node count 0** |

Details: [Phase 4](docs/tutorial/phase_04_azure_ml.md).

---

## Part 5 — Automate with GitHub Actions (no password)

### Step 13. An identity for GitHub (OIDC)

Why: GitHub gets a short-lived token per run; Azure trusts only this repo's `main` branch. No secret is stored anywhere.

| | By code | By hand |
|---|---|---|
| App | `$APP_ID = az ad app create --display-name $GH_APP --query appId -o tsv` | Portal → **Microsoft Entra ID → App registrations** → **+ New registration** → `gh-churn-mlops` |
| Service principal | `az ad sp create --id $APP_ID` | created automatically by the portal |
| Trust rule | `az ad app federated-credential create --id $APP_ID --parameters infra/github-federated-credential.json` | the app → **Certificates & secrets → Federated credentials** → **+ Add credential** → **GitHub Actions deploying Azure resources** → org, repo, entity **Branch**, `main` |

If a workflow fails with `AADSTS700213 ... subject 'repo:owner@id/repo@id:ref:refs/heads/main'`, copy that exact subject into the trust rule ([infra/github-federated-credential.json](infra/github-federated-credential.json)). GitHub now sends ids in the subject.

### Step 14. Give it a role on the resource group only

| By code | By hand |
|---|---|
| `az role assignment create --assignee-object-id $SP_ID --assignee-principal-type ServicePrincipal --role Contributor --scope $RG_ID` | resource group → **Access control (IAM)** → **+ Add → Add role assignment** → **Contributor** → members: `gh-churn-mlops` → **Review + assign** |

### Step 15. Tell GitHub the ids (not secrets)

| By code | By hand |
|---|---|
| `gh variable set AZURE_CLIENT_ID --body $APP_ID --repo $GH_REPO` (same for `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`) | GitHub repo → **Settings → Secrets and variables → Actions → Variables** → **New repository variable** × 3 |

### Step 16. CI: train and test on every push

| By code | By hand |
|---|---|
| [.github/workflows/ci.yml](.github/workflows/ci.yml): checkout → Python 3.12 → `pip install` → `python src/train.py` → `pytest`. Starts on every `git push` | GitHub repo → **Actions** → see the runs; **Re-run jobs** to run again |

### Step 17. CD: build and deploy after a green CI

| By code | By hand |
|---|---|
| [.github/workflows/deploy.yml](.github/workflows/deploy.yml): OIDC login → download `churn-model:1` → `docker build` → test `/health` → `docker push` (tag = commit id) → `az containerapp update` → check the live `/health` | Container App → **Settings → Deployment** (or **Continuous deployment**) → sign in to GitHub → repo + branch `main` → registry `acrchurnub4786`, Dockerfile `./Dockerfile` → identity / OIDC → **Start**. The portal writes a workflow into your repo that builds and deploys on every push (without our extra steps: wait for CI, add the registered model, test before push) |

### Step 18. A "Train in Azure ML" button

| By code | By hand |
|---|---|
| [.github/workflows/train.yml](.github/workflows/train.yml), started with `gh workflow run train.yml --repo $GH_REPO`; it submits [aml/train-job.yml](aml/train-job.yml) and checks the status every 30 s | GitHub → **Actions → Train in Azure ML → Run workflow**, or submit the job in the studio (step 10) |

Details: [Phase 5](docs/tutorial/phase_05_cicd.md).

---

## Part 6 — Monitor the live API

Application Insights and its Log Analytics workspace already exist (step 3), and the Container App already gets the connection string from Key Vault (step 7).

### Step 19. Send requests and logs to Application Insights

| By code | By hand |
|---|---|
| In [src/app.py](src/app.py), call `configure_azure_monitor()` **before** `from fastapi import FastAPI`, only when `APPLICATIONINSIGHTS_CONNECTION_STRING` is set. Add `azure-monitor-opentelemetry` to [requirements-api.txt](requirements-api.txt). Push, and the deploy workflow ships it | The code part has no portal button. Check the setting: Container App → **Settings → Containers** → **Environment variables** → `APPLICATIONINSIGHTS_CONNECTION_STRING` (from the Key Vault secret). Then Application Insights → **Overview**: requests, failures and response time appear a few minutes after the first calls |

### Step 20. Ask questions with KQL

| By code | By hand |
|---|---|
| The queries in [docs/kql/](docs/kql/requests_per_hour.kql): requests per hour, failed requests, average response time. Count with `sum(itemCount)`, because the app keeps only a sample of the requests | Application Insights → **Monitoring → Logs** → close the welcome windows → switch **Agent** off → **KQL mode** → paste a query → **Run** |

### Step 21. Email when the server fails

| By code | By hand |
|---|---|
| `az monitor action-group create --resource-group $RG --name $ACTION_GROUP --short-name churnmail --action email me $EMAIL …` then `az monitor metrics alert create --resource-group $RG --name $ALERT --scopes $APPI_ID --condition "count requests/failed > 5 where request/resultCode includes 500" --window-size 5m --evaluation-frequency 1m --severity 2 --action $ACTION_GROUP …` | Application Insights → **Monitoring → Alerts → + Create → Alert rule** → signal **Failed requests** → filter **Result code = 500** → Greater than 5, Count, every 1 min, lookback 5 min → **+ Create action group** → Email → your address → severity 2 → name → **Review + create** |

Details: [Phase 6](docs/tutorial/phase_06_monitoring.md).

---

## Cost and clean-up

| | By code | By hand |
|---|---|---|
| Credit left | — | Portal → **Subscriptions** → your subscription → **Overview** |
| Cost per feature | — | Portal → **Cost Management → Cost analysis** → scope `rg-churn-mlops` → **Group by: Tag → feature** |
| Delete everything | `az group delete --name $RG --yes` | resource group → **Delete resource group** → type the name |
| Free the Key Vault name | `az keyvault purge --name $KV` | **Key vaults → Manage deleted vaults** → **Purge** |
| Remove the Azure ML workspace for good | — | **Azure Machine Learning → Recently deleted** → delete permanently |
| Remove the GitHub identity | `az ad app delete --id $APP_ID` | **Entra ID → App registrations** → `gh-churn-mlops` → **Delete** |
| Leftover groups | `az group list -o table` | **Resource groups**: no `ME_...` or `DefaultResourceGroup-...` left |
