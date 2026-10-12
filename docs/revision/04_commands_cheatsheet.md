# Commands cheat sheet

All commands of the project, phase by phase, in PowerShell. Every new terminal starts with `. .\scripts\names.ps1`, which loads the names (`$RG`, `$ACR`, `$KV`, ...).

The full explanation of each one, with its real output, is in the [tutorial](../tutorial/README.md).

## Phase 0 — Setup

| Command | What it does |
|---|---|
| `az login` | log in to Azure in the browser |
| `az account show` | show the current subscription |
| `gh auth login` | log in to GitHub |
| `az extension add -n ml` | add the Azure ML commands |
| `az extension add -n containerapp` | add the Container Apps commands |
| `az bicep install` | install Bicep |
| `az provider register -n Microsoft.App` | allow the subscription to use a service (repeat for each of the 7) |
| `git init -b main` | start a git repository |
| `gh repo create azure-churn-mlops --public --source . --remote origin --push` | create the GitHub repo and push |

## Phase 1 — Laptop

| Command | What it does |
|---|---|
| `python -m venv .venv` | create a Python environment |
| `.\.venv\Scripts\Activate.ps1` | turn it on |
| `pip install -r requirements.txt` | install the packages |
| `python src/train.py` | train and save `model/model.pkl` |
| `uvicorn src.app:app --reload` | run the API on http://localhost:8000 |
| `pytest` | run the 3 tests |
| `docker build -t churn-api:local .` | build the image |
| `docker run --rm -p 8000:8000 churn-api:local` | run the image |

## Phase 2 — Azure resources with Bicep

| Command | What it does |
|---|---|
| `az group create --name $RG --location $LOCATION --tags $TAGS` | create the resource group |
| `$USER_ID = az ad signed-in-user show --query id -o tsv` | get the logged-in user id |
| `az deployment group what-if --resource-group $RG --template-file infra/main.bicep --parameters userObjectId=$USER_ID` | preview, creates nothing |
| `az deployment group create --resource-group $RG --template-file infra/main.bicep --parameters userObjectId=$USER_ID` | create everything |

## Phase 3 — Live API

| Command | What it does |
|---|---|
| `az acr login --name $ACR` | let Docker push to the registry |
| `docker build -t "${IMAGE}:v1" .` | build the image with the registry name |
| `docker push "${IMAGE}:v1"` | upload it |
| `az acr repository show-tags --name $ACR --repository churn-api -o table` | check it is there |
| `az keyvault secret set --vault-name $KV --name appinsights-connection-string --value $APPI_CS --query name -o tsv` | store the secret |
| `python scripts/test_live_api.py` | measure cold start and speed |

## Phase 4 — Azure ML

| Command | What it does |
|---|---|
| `az ml data create --name churn-data --version 1 --type uri_file --path data/churn.csv --resource-group $RG --workspace-name $AML_WORKSPACE` | upload the data as an asset |
| `az ml compute create --file aml/cluster.yml --resource-group $RG --workspace-name $AML_WORKSPACE` | create the cluster (min 0 nodes) |
| `$JOB = az ml job create --file aml/train-job.yml --resource-group $RG --workspace-name $AML_WORKSPACE --query name -o tsv` | start training |
| `az ml job stream --name $JOB --resource-group $RG --workspace-name $AML_WORKSPACE` | follow the job |
| `az ml model create --name churn-model --version 1 --type custom_model --path "azureml://jobs/$JOB/outputs/model" --resource-group $RG --workspace-name $AML_WORKSPACE` | register the model |
| `az ml compute list-nodes --name $AML_CLUSTER --resource-group $RG --workspace-name $AML_WORKSPACE` | check the cluster is back to 0 nodes |

## Phase 5 — CI/CD

| Command | What it does |
|---|---|
| `$APP_ID = az ad app create --display-name $GH_APP --query appId -o tsv` | create the app GitHub logs in as |
| `az ad sp create --id $APP_ID` | create its service principal |
| `az ad app federated-credential create --id $APP_ID --parameters infra/github-federated-credential.json` | trust this repo and branch (OIDC) |
| `az role assignment create --assignee-object-id $SP_ID --assignee-principal-type ServicePrincipal --role Contributor --scope $RG_ID` | Contributor on the group only |
| `gh variable set AZURE_CLIENT_ID --body $APP_ID --repo $GH_REPO` | save the ids in GitHub (also tenant and subscription) |
| `gh run list --limit 5` | see the latest pipeline runs |
| `gh run watch` | follow a run |
| `gh workflow run train.yml` | start cloud training from GitHub |

## Phase 6 — Monitoring

| Command | What it does |
|---|---|
| `az monitor action-group create --name $ACTION_GROUP --resource-group $RG --short-name churnmail --action email me $EMAIL` | who gets the email |
| `az monitor metrics alert create --name $ALERT --resource-group $RG --scopes $APPI_ID --condition "count requests/failed > 5 where request/resultCode includes 500" --window-size 5m --evaluation-frequency 1m --severity 2 --action $ACTION_GROUP` | the alert rule |
| Portal → `appi-churn-mlops` → Logs → paste a query from `docs/kql/` | run KQL |

## Phase 7 — Proof

| Command | What it does |
|---|---|
| `$URI = az ml workspace show -g $RG -n $AML_WORKSPACE --query mlflow_tracking_uri -o tsv` | MLflow address of the workspace |
| `python scripts/export_aml_runs.py $URI` | save all run metrics to `docs/results/aml_runs.csv` |

## Phase 8 — Shutdown

| Command | What it does |
|---|---|
| `gh workflow disable deploy.yml --repo $GH_REPO` | stop deploys (same for `train.yml`) |
| `gh variable delete AZURE_CLIENT_ID --repo $GH_REPO` | remove the ids (same for tenant and subscription) |
| `az ad app delete --id $APP_ID` | remove GitHub's Azure login |
| `az group delete --name $RG --yes` | delete every resource |
| `az group list -o table` | check nothing is left |
| `az keyvault purge --name $KV` | remove the soft-deleted vault |
