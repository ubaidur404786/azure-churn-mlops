# CV lines

Draft bullets with real numbers. Copy them into the CV project. Claim the Azure skills only once the shutdown (Phase 8) and the final cost report (Phase 9) are confirmed.

## English

**Churn Prediction on Azure — End-to-End MLOps** | GitHub: github.com/ubaidur404786/azure-churn-mlops | 2026

- Provisioned the full Azure stack with one Bicep deployment (Azure ML, Container Registry, Container Apps, Key Vault, managed identity, Application Insights), tagged by feature to track cost.
- Trained and registered the model with Azure ML command jobs and MLflow on a scale-to-zero CPU cluster: 3 reproducible cloud runs (ROC-AUC 0.838, accuracy 0.796).
- Served a FastAPI scoring API on Azure Container Apps (HTTPS, scale to zero, about 0.2–0.6 s per warm request); no secrets in code, using managed identity, Key Vault and least-privilege RBAC.
- Built CI/CD with GitHub Actions and passwordless OIDC login: tests on every push (about 1 min), then automatic deploy of a commit-tagged image (about 2.5 min).
- Monitored with Application Insights, KQL queries and an email alert. Tracked cost per feature: the whole project cost €0.12.

## Français

**Prédiction du churn sur Azure — MLOps de bout en bout** | GitHub : github.com/ubaidur404786/azure-churn-mlops | 2026

- Déploiement de toute l'infrastructure Azure en une commande Bicep (Azure ML, Container Registry, Container Apps, Key Vault, identité managée, Application Insights), avec des tags par fonctionnalité pour suivre les coûts.
- Entraînement et enregistrement du modèle avec des jobs Azure ML et MLflow sur un cluster CPU qui descend à zéro : 3 exécutions cloud reproductibles (ROC-AUC 0,838, accuracy 0,796).
- API FastAPI sur Azure Container Apps (HTTPS, scale to zero, environ 0,2 à 0,6 s par requête) ; aucun secret dans le code grâce à l'identité managée, Key Vault et des rôles RBAC minimaux.
- CI/CD avec GitHub Actions et connexion OIDC sans mot de passe : tests à chaque push (environ 1 min), puis déploiement automatique d'une image taguée par commit (environ 2,5 min).
- Supervision avec Application Insights, requêtes KQL et alerte e-mail. Suivi du coût par fonctionnalité : coût total du projet 0,12 €.

## Skills to add

Microsoft Azure · Azure CLI · Bicep · Azure Machine Learning (jobs, compute clusters, data assets, MLflow, model registry) · Docker · Azure Container Registry · Azure Container Apps · Microsoft Entra ID (managed identity, RBAC, OIDC) · Key Vault · GitHub Actions · Application Insights · Log Analytics · KQL · Azure Cost Management

Not claimable from this project: AKS, Databricks, Spark, Data Factory, Azure OpenAI, networking (VNet, private endpoints).
