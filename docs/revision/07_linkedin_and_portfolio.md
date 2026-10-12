# LinkedIn post and portfolio card

Real facts only. Add the screenshot `docs/results/demo.gif` or `docs/screenshots/03_predict_response.png` as the image.

## LinkedIn post

I built an end-to-end MLOps project on Microsoft Azure, from a CSV file to a live, monitored API, for €0.12.

The model is simple on purpose (logistic regression for customer churn). The work was everything around it:

🔹 One Bicep file creates the whole Azure setup with one command
🔹 Azure Machine Learning trains the model on a cluster that scales to zero, with MLflow tracking and a model registry
🔹 A FastAPI app in Docker runs on Azure Container Apps over HTTPS, and also scales to zero
🔹 No passwords anywhere: GitHub logs in to Azure with OIDC, and the app uses a managed identity and Key Vault
🔹 GitHub Actions tests every push and deploys automatically
🔹 Application Insights + KQL for monitoring, with an email alert on server errors
🔹 Cost tracked per feature with tags: €0.12 in total, then everything deleted

What I learned most came from the problems, for example:
- a scikit-learn version mismatch between cloud training and serving
- a change in GitHub's OIDC token format
- why KQL `count()` was wrong when the data is sampled

Code, step-by-step guide and screenshots: github.com/ubaidur404786/azure-churn-mlops

#Azure #MLOps #MachineLearning #AzureML #GitHubActions #Docker

## Portfolio project card

**Title:** Churn Prediction on Azure — End-to-End MLOps

**One line:** A churn model trained in Azure ML and served as a live HTTPS API on Container Apps, with infrastructure as code, passwordless CI/CD, monitoring and cost tracking. Total cost: €0.12.

**Tags:** Azure ML · Container Apps · Bicep · GitHub Actions · OIDC · Application Insights · Docker · FastAPI

**Links:** GitHub repo · demo GIF · step-by-step guide (GUIDE.md)
