# Phase 7 — Proof pack while everything is live

Goal: collect all the proof **before** deleting anything. After Phase 8 the Azure resources are gone, so every screenshot, metric and number must be saved now.

No new Azure resource is created in this phase. Cost: €0.

---

## 7.1 Check the screenshots

All screenshots of Phases 0–6 are listed in PLAN.md. Each one was checked in `docs/screenshots/`: all 20 are there, none missing.

---

## 7.2 Demo

A short animated picture, [docs/results/demo.gif](../results/demo.gif), shows the project in 10 steps: resource group → Bicep → Azure ML job → model registry → CI → deploy → live `/predict` → Application Insights → KQL → cost.

It is made from the real screenshots, with one caption per picture, using the Pillow library in Python. A narrated video can be added later; see [docs/results/video.md](../results/video.md).

![Demo](../results/demo.gif)

---

## 7.3 Export the Azure ML run metrics

The training script logs its metrics with MLflow, so the same MLflow library can read them back from the workspace.

First get the MLflow address of the workspace:

```powershell
$URI = az ml workspace show -g $RG -n $AML_WORKSPACE --query mlflow_tracking_uri -o tsv
```

Then read all runs and save them as a CSV file with [scripts/export_aml_runs.py](../../scripts/export_aml_runs.py):

```powershell
python scripts/export_aml_runs.py $URI
```

Real output (shortened):

```text
                  run_id   status  metrics.accuracy  metrics.f1  metrics.roc_auc
 joyful_grass_9w8dwr40k9 FINISHED            0.7956    0.583815         0.837503
bubbly_camera_5dd7jr740n FINISHED            0.7956    0.583815         0.837503
   frank_fowl_hl4mg2hqg3 FINISHED            0.7956    0.583815         0.837503
```

What it means: 3 cloud runs (one by hand, two from GitHub Actions) give exactly the same numbers, because the data split uses a fixed `random_state`. The file is [docs/results/aml_runs.csv](../results/aml_runs.csv).

One more live speed test was also run:

```powershell
python scripts/test_live_api.py
```

Result: warm requests 570 ms on average, fastest 237 ms. The row is added to [docs/results/api_speed.md](../results/api_speed.md).

---

## 7.4 README

The [README](../../README.md) now has: a CI badge, the demo, a table "service → why → file", the results, six screenshots and "deploy it in 4 commands".

---

## 7.5 Cost before shutdown

Portal → **Cost Management** → **Cost analysis** → **Resource groups** → expand `rg-churn-mlops`.

![Cost before shutdown](../screenshots/07_cost_before_shutdown.png)

| Resource | Cost |
|---|---|
| Azure ML workspace `mlw-churn-mlops` | €0.06 |
| Container Registry `acrchurnub4786` | €0.06 |
| Key Vault | under €0.01 |
| Storage account | under €0.01 |
| Log Analytics | €0.00 |
| **Total** | **€0.12** |

Credit left on the free account: $199.86 of $200. The Container App costs €0 because it scales to zero and stays inside the monthly free grant.

Azure cost data arrives 8–48 hours late, so the final numbers come in Phase 9.

---

## What was learned

- Capture all proof **before** shutdown; nothing can be re-captured after.
- MLflow can read runs back, not only write them: `mlflow.search_runs()` with the workspace address.
- Some Azure screens show the subscription ID in unexpected places (here, a hidden tag of the Azure ML workspace). Check every screenshot before saving it.
