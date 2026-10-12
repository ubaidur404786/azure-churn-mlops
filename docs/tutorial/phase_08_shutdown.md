# Phase 8 — Shutdown and disconnect

Goal: delete everything in Azure and cut every link between GitHub and Azure, so nothing keeps running and nothing can cost money.

Do this right after Phase 7: all the proof is already saved in the repo.

Every new terminal starts with:

```powershell
. .\scripts\names.ps1
```

The order matters: first stop GitHub from talking to Azure, then remove its login, then delete the resources, then check.

---

## 8.1 Stop the workflows that touch Azure

Disable the Deploy workflow:

```powershell
gh workflow disable deploy.yml --repo $GH_REPO
```

Disable the training workflow:

```powershell
gh workflow disable train.yml --repo $GH_REPO
```

No output means it worked. CI stays on: it only trains on the GitHub runner and never touches Azure.

---

## 8.2 Delete the GitHub repo variables

These 3 variables told GitHub which Azure app, tenant and subscription to log in to.

```powershell
gh variable delete AZURE_CLIENT_ID --repo $GH_REPO
```

```powershell
gh variable delete AZURE_TENANT_ID --repo $GH_REPO
```

```powershell
gh variable delete AZURE_SUBSCRIPTION_ID --repo $GH_REPO
```

Each prints `✓ Deleted variable ...`.

---

## 8.3 Delete the Entra app that GitHub used

Find the app id by its name:

```powershell
$APP_ID = az ad app list --display-name $GH_APP --query "[0].appId" -o tsv
```

Delete the app. This also deletes its trust rule (federated credential) and its service principal:

```powershell
az ad app delete --id $APP_ID
```

No output means it worked.

---

## 8.4 Delete the resource group

This deletes every resource inside it: Azure ML workspace, cluster, storage, registry, Container App and its environment, Key Vault, identity, Log Analytics, Application Insights, the alert rule and the action group. It takes 5–15 minutes.

```powershell
az group delete --name $RG --yes
```

The command waits, then prints nothing.

---

## 8.5 Check that nothing is left

List all resource groups:

```powershell
az group list -o table
```

`rg-churn-mlops` must be gone. Also no `ME_...` group (made by Container Apps) and no `DefaultResourceGroup-...` group. If one is still there, delete it the same way with `az group delete --name <name> --yes`.

List all resources:

```powershell
az resource list -o table
```

The list must be empty.

Screenshot `08_all_deleted.png`: Portal → **Resource groups** (the empty list).

---

## 8.6 Remove the soft-deleted Key Vault and Azure ML workspace

Azure keeps deleted Key Vaults and Azure ML workspaces for a while ("soft delete"), so they can be restored. They cost nothing, but their names stay reserved.

Check the deleted Key Vault:

```powershell
az keyvault list-deleted -o table
```

Remove it for good (this cannot be undone):

```powershell
az keyvault purge --name $KV
```

For the workspace: Portal → **Azure Machine Learning** → **Recently deleted** → select `mlw-churn-mlops` → **Permanently delete**.

---

## 8.7 Keep the budget alert

The budget alert stays until the free subscription ends. It is free and still emails if anything ever costs money.

## 8.8 Log out (optional)

```powershell
az logout
```

---

## What was learned

- Delete in this order: GitHub workflows → GitHub variables → Entra app → resource group → check.
- One resource group = one delete command for the whole project. This is why every resource was put in `rg-churn-mlops`.
- "Deleted" is not always gone: Key Vault and Azure ML keep a soft-deleted copy that must be purged.
