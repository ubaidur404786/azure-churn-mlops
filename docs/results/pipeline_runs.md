# Pipeline runs

GitHub deletes run logs after 90 days, so each run also has a screenshot in `docs/screenshots/`.

| Date | Workflow | Result | Duration | Link |
|---|---|---|---|---|
| 2026-10-12 | CI (train + pytest) | success | 1 min 34 s | https://github.com/ubaidur404786/azure-churn-mlops/actions/runs/38197476280 |
| 2026-10-12 | CI #2 | failure (pytest collected `scripts/test_live_api.py`) | 46 s | https://github.com/ubaidur404786/azure-churn-mlops/actions/runs/38199072950 |
| 2026-10-12 | CI #3 | success | 1 min 8 s | https://github.com/ubaidur404786/azure-churn-mlops/actions/runs/38228905218 |
| 2026-10-12 | Deploy #2, attempt 1 | failure (OIDC subject mismatch, AADSTS700213) | 14 s | https://github.com/ubaidur404786/azure-churn-mlops/actions/runs/38229036853/attempts/1 |
| 2026-10-12 | Deploy #2, attempt 2 | success: image `churn-api:7abc56c...`, revision `ca-churn-api--0000001` | 2 min 26 s | https://github.com/ubaidur404786/azure-churn-mlops/actions/runs/38229036853 |
