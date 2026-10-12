# Interview questions (40, with short answers)

Each answer is short on purpose: say it in 2–3 sentences, then give the example from this project.

## The project

**1. What does the project do?**
It predicts if a telecom customer will leave (churn). The model is trained in Azure ML and served as an HTTPS API on Azure Container Apps. Every change is tested and deployed by GitHub Actions.

**2. Why such a simple model?**
The goal was the cloud and MLOps work, not the model. A logistic regression trains in seconds, so most of the time and money went into infrastructure, deployment, security and monitoring.

**3. What does "end to end" mean here?**
From raw CSV to a live, monitored, automatically deployed API, and then a clean shutdown: data → training → registry → image → deploy → monitoring → cost report.

**4. What would you do next?**
- Add a test that fails if the new model is worse than the current one.
- Deploy only after that check passes.
- Add data drift monitoring.
- Keep a staging app before production.

## Azure Machine Learning

**5. What is an Azure ML workspace?**
The home for everything ML in Azure: jobs, runs, metrics, data assets, compute and the model registry. The workspace itself is free; you pay for the compute and storage it uses.

**6. What is a command job?**
A job that runs a script (`python train.py`) on a compute target with given inputs and an environment. Here: [aml/train-job.yml](../../aml/train-job.yml).

**7. What is a compute cluster, and how did you keep it cheap?**
A group of VMs that Azure ML starts for jobs. Min 0 nodes and 120 s idle time, so it only runs (and costs) during training, about 3 minutes per job.

**8. What is a curated environment?**
A ready-made Docker image from Microsoft with common ML libraries. Using it means Azure ML does not build an image, which is faster and needs no extra registry.

**9. What is a data asset?**
A named, versioned pointer to data (`churn-data:1`). Jobs refer to the name, so the data used by each run is recorded.

**10. What is the model registry for?**
It stores model versions with their history (which job, which data). Deploy downloads `churn-model:1` from it, so production always uses a known, traceable model.

**11. How does MLflow fit in?**
`train.py` logs metrics and the model with MLflow. On the laptop it writes to a local file; in Azure ML it writes to the workspace automatically. Same code, two places.

**12. The metrics were identical on the laptop and in Azure. Why?**
Same code, same data, and a fixed random split (`random_state=42`). This proves the cloud run is reproducible.

## Containers and serving

**13. Why Docker?**
The image contains the app, the model and the exact library versions, so it runs the same on the laptop, in CI and in Azure.

**14. What is Azure Container Registry?**
A private store for Docker images. The live app pulls its image from it with its managed identity, so the admin user (a password) is turned off.

**15. Container Apps vs AKS vs App Service?**
- **Container Apps:** runs containers with no cluster to manage, and scales to zero. Simple and cheap for one API.
- **AKS:** full Kubernetes. More control, but you manage the cluster and pay for nodes.
- **App Service:** web apps (code or containers), but no scale to zero on the usual plans.

For one small API, Container Apps is the simplest and cheapest.

**16. What is scale to zero, and what is the trade-off?**
With min 0 replicas no container runs when nobody calls the API, so it costs €0. The first request after idle waits for a cold start, measured at about 25 s.

**17. How would you remove the cold start?**
Set min replicas to 1. Then one container always runs, which here would use the monthly free grant in about 2 days. It is a cost-versus-speed choice.

**18. What are revisions in Container Apps?**
Each image or setting change creates a new revision (a version of the app). You can split traffic between revisions or roll back to an old one.

**19. How fast is the API?**
Warm requests take about 0.2–0.6 s, mostly the network round trip; the model itself predicts in milliseconds. The cold start is about 25 s.

## Security

**20. Managed identity vs keys?**
A managed identity is an Azure identity with no password; Azure handles the token. Keys can leak, expire or end up in Git. Here the app pulls images and reads secrets with its identity.

**21. What is OIDC in GitHub Actions?**
GitHub gives each workflow run a short-lived signed token. Azure trusts tokens from this repo and branch only (federated credential) and gives back an Azure token. No secret is stored in GitHub.

**22. What did the federated credential trust exactly?**
One "subject": this repository on the `main` branch. GitHub now puts owner and repo ids in the subject, so the exact string from the error message had to be copied in.

**23. Why Key Vault if there is only one secret?**
The App Insights connection string is not in code or Git. The app reads it at start with its identity. The same pattern works for any number of secrets.

**24. What is least privilege here?**
- The app gets only AcrPull and Key Vault Secrets User.
- GitHub gets Contributor on the resource group only, not the subscription.

**25. Why are the GitHub values variables and not secrets?**
Client id, tenant id and subscription id are identifiers, not passwords. Without a matching federated credential they are useless.

## Infrastructure as code

**26. What is Bicep?**
Azure's language to describe resources in a file. `az deployment group create` makes Azure match the file. Here, one file creates the resources and the role assignments.

**27. Bicep vs Terraform?**
- **Bicep:** Azure only, made by Microsoft, no state file to manage, new Azure features on day one.
- **Terraform:** works for many clouds, but you must keep a state file.

For an Azure-only project, Bicep is simpler.

**28. What is what-if?**
`az deployment group what-if` shows what a deployment would create, change or delete, without doing it. Free and safe. Here it showed "11 to create".

**29. Why tags?**
Cost Management can group costs by tag. Each resource has `feature=training`, `serving`, and so on, so the cost of each part is visible.

## CI/CD

**30. What does CI do here?**
On every push: install the packages, train the model, run 3 pytest tests. It takes about 1 minute and never touches Azure.

**31. What does the deploy workflow do?**
After a green CI on `main`:
1. Log in with OIDC.
2. Download the registered model.
3. Build an image tagged with the commit id.
4. Test `/health` on the runner.
5. Push the image to ACR.
6. Update the Container App.
7. Check the live `/health`.

**32. Why tag images with the commit id?**
Every live version maps to one exact commit, so you always know what is running and can roll back.

**33. How is training started from GitHub?**
A manual workflow (`train.yml`) submits the Azure ML job, then checks its status every 30 s until it is Completed or Failed.

## Monitoring

**34. What is Application Insights?**
An application monitoring service. The API sends its requests, response times, errors and log lines to it through OpenTelemetry.

**35. What is KQL? Give an example.**
The query language of Log Analytics. For example: `requests | where success == false | summarize sum(itemCount) by resultCode`.

**36. Why `sum(itemCount)` and not `count()`?**
The telemetry is sampled: one stored row can stand for several requests, and `itemCount` says how many. `count()` gave 14 requests but the real number was 31.

**37. What alert did you set, and why only 500 errors?**
More than 5 server errors (code 500) in 5 minutes sends an email. A 422 is the caller's mistake (bad input); counting it would let anyone trigger emails.

## Cost

**38. How did you control cost?**
- Free credit only, plus a €5 budget alert.
- Scale to zero for the cluster and the API.
- Basic plans, and a Log Analytics daily cap.
- Tags per feature, and a cost log at the start and end of each phase.
- Everything deleted at the end.

**39. What did it cost, and what was the biggest item?**
€0.12 in total. The Azure ML workspace (the training runs on the cluster are billed to it) and the Container Registry (a fixed daily fee) were €0.06 each. The Container App cost €0 thanks to scale to zero.

**40. Why does the cost show €0 at first?**
Azure cost data arrives 8–48 hours late. Always wait before saying something is free.
