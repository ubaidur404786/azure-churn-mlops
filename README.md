# Azure Churn MLOps

An end-to-end machine learning project on Microsoft Azure. A customer-churn model is trained in Azure Machine Learning, versioned in the model registry and served as a public HTTPS API on Azure Container Apps. The infrastructure is code (Bicep), and every change is tested and deployed by GitHub Actions, which logs in to Azure without any stored password (OIDC).

The model is deliberately simple. The focus is the cloud work around it: infrastructure as code, cloud training, deployment, security, CI/CD and cost control.

![Architecture](docs/architecture/architecture.svg)

## What it does

- **Infrastructure as code**: one Bicep file creates every Azure resource and role, each tagged by feature for cost tracking.
- **Cloud training**: Azure ML runs the training script on a cluster that scales to 0 nodes when idle, logs metrics with MLflow and registers the model.
- **Serving**: a FastAPI app in a Docker image runs on Azure Container Apps over HTTPS, and scales to zero when nobody uses it.
- **CI/CD**: every push trains the model and runs the tests. After a green run, the registered model is packed into a new image, tagged with the commit id, and deployed.
- **Monitoring**: the API sends its requests and logs to Application Insights; saved KQL queries show traffic, failures and speed, and an alert emails when the server fails.
- **Security**: no keys or passwords in code. GitHub uses OIDC; the app uses a managed identity and Key Vault; every identity gets the smallest role it needs.
- **Cost control**: free credit only, a budget alert, scale-to-zero everywhere, and the cost of each feature measured.

## Results

| | |
|---|---|
| Model (test set) | accuracy 0.796 · F1 0.584 · ROC-AUC 0.838, the same on the laptop and in Azure ML |
| Live API | cold start about 25 s after scale to zero, then about 0.2–0.4 s per request |
| Pipelines | CI about 1 min · deploy about 2.5 min |
| Cost so far | about €0.03 of the free credit |

Details: [docs/results/](docs/results/model_metrics.md).

## Built with

Azure Machine Learning · Azure Container Apps · Azure Container Registry · Key Vault · Managed identity · Storage · Application Insights · Log Analytics · Bicep · Microsoft Entra ID (OIDC) · GitHub Actions · Docker · FastAPI · scikit-learn · MLflow · pytest

## Learn and rebuild it

- [GUIDE.md](GUIDE.md): every step to rebuild the project, **by code and by hand in the Azure portal side by side**. It includes where to start if you only have a container image or only code on GitHub.
- [Tutorial](docs/tutorial/README.md): one page per phase with a step-by-step diagram, each command, its real output, the errors met and their fixes, and screenshots.

## Run it locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src/train.py
uvicorn src.app:app --reload
```

Then open http://localhost:8000/docs.

> Status: the setup, laptop model, Bicep, Container Apps, Azure ML, CI/CD and monitoring phases are done. The proof pack, the final cost report and the shutdown come next. All Azure resources are deleted at the end of the project.
