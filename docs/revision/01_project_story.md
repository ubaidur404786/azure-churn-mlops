# Project story (2 minutes)

Use this when an interviewer says "Tell me about a project you built".
It follows a simple order: **problem → what I built → how it works → results → what I learned**.

## English

**Problem.** Many ML models stay in notebooks. I wanted to show the full path from data to a live, monitored service in the cloud, the way a real team would run it, on Microsoft Azure and on a free account.

**What I built.** A customer-churn API. The model is deliberately simple, a logistic regression on the IBM Telco dataset, because the goal was the cloud work around it.

**How it works.**
- All Azure resources are described in one **Bicep** file and created with one command, each tagged by feature so I can see what each part costs.
- The same training script runs on my laptop, as an **Azure Machine Learning** job on a cluster that scales to zero, and in CI. It logs metrics with MLflow, and the model is saved in the Azure ML **model registry**.
- The model is packed into a **Docker** image, stored in **Azure Container Registry** and served by a **FastAPI** app on **Azure Container Apps** over HTTPS. It also scales to zero.
- **Security:** there are no passwords anywhere. GitHub logs in to Azure with **OIDC**. The app uses a **managed identity** to pull its image and to read its one secret from **Key Vault**. Each identity has only the role it needs.
- **CI/CD:** on every push, **GitHub Actions** trains the model and runs the tests. If they pass, it downloads the registered model, builds an image tagged with the commit id, and updates the live app.
- **Monitoring:** **Application Insights** collects every request. I wrote **KQL** queries for traffic, errors and speed, and an alert emails me when the server fails.

**Results.**
- Model: accuracy 0.796, ROC-AUC 0.838, identical on the laptop and in three cloud runs.
- API: about 25 s cold start after scaling to zero, then about 0.2–0.6 s per request.
- CI takes about 1 minute, deploy about 2.5 minutes.
- The whole project cost **€0.12** of the free credit. Then I deleted everything with one command.

**What I learned.** The hard parts were not the model. They were the real-world problems:
- a scikit-learn version mismatch between the cloud training image and my API
- a GitHub OIDC subject format change
- pytest picking up the wrong file

I also learned how scale-to-zero trades a cold start for a near-zero cost.

## Français

**Problème.** Beaucoup de modèles de ML restent dans des notebooks. Je voulais montrer tout le chemin, des données jusqu'à un service en ligne et surveillé dans le cloud, comme le ferait une vraie équipe, sur Microsoft Azure et avec un compte gratuit.

**Ce que j'ai construit.** Une API qui prédit le départ des clients (churn). Le modèle est volontairement simple, une régression logistique sur le jeu de données IBM Telco, car l'objectif était le travail cloud autour du modèle.

**Comment ça marche.**
- Toutes les ressources Azure sont décrites dans un seul fichier **Bicep** et créées en une commande. Chacune porte un tag de fonctionnalité pour suivre son coût.
- Le même script d'entraînement tourne sur mon ordinateur, comme job **Azure Machine Learning** sur un cluster qui descend à zéro, et dans la CI. Il enregistre les métriques avec MLflow, et le modèle est stocké dans le **registre de modèles** Azure ML.
- Le modèle est mis dans une image **Docker**, stockée dans **Azure Container Registry**, et servi par une application **FastAPI** sur **Azure Container Apps** en HTTPS. Elle descend aussi à zéro.
- **Sécurité :** aucun mot de passe nulle part. GitHub se connecte à Azure avec **OIDC**. L'application utilise une **identité managée** pour télécharger son image et lire son seul secret dans **Key Vault**. Chaque identité a uniquement le rôle nécessaire.
- **CI/CD :** à chaque push, **GitHub Actions** entraîne le modèle et lance les tests. S'ils réussissent, il télécharge le modèle enregistré, construit une image avec l'identifiant du commit, et met à jour l'application en ligne.
- **Supervision :** **Application Insights** collecte chaque requête. J'ai écrit des requêtes **KQL** (trafic, erreurs, vitesse) et une alerte m'envoie un e-mail en cas d'erreurs serveur.

**Résultats.**
- Modèle : accuracy 0,796, ROC-AUC 0,838, identiques sur l'ordinateur et dans trois exécutions cloud.
- API : environ 25 s au démarrage à froid, puis 0,2 à 0,6 s par requête.
- CI en 1 minute environ, déploiement en 2,5 minutes.
- Coût total : **0,12 €** du crédit gratuit. Ensuite j'ai tout supprimé en une commande.

**Ce que j'ai appris.** Les difficultés n'étaient pas le modèle mais les problèmes réels :
- une différence de version de scikit-learn entre l'image d'entraînement cloud et mon API
- un changement du format OIDC de GitHub
- pytest qui exécutait le mauvais fichier

J'ai aussi compris le compromis du « scale to zero » : un démarrage plus lent contre un coût presque nul.
