# Learning log

One entry per step: date, what we did, key commands, errors and fixes.

## Phase 0 — Safety, cost tracking and setup

### 2026-10-11 — 0.1 Check the subscription
- Portal → Subscriptions: "Azure subscription 1", Azure Plan (Microsoft Customer Agreement free account).
- Credit: $200 (€175.99), ends about 2026-11-10. The new free account has no "spending limit" toggle: when the credit ends, the account stops unless it is upgraded. We never upgrade.
- Screenshot: `00_credit_start.png`.

### 2026-10-11 — 0.2 Budget alert
- Portal → Cost Management → Budgets: budget of 5 USD per month, alerts at 5%, 50%, 80%, 100% actual and 100% forecast, sent by email.
- Error: the first save kept only the 5% alert. Fix: edit the budget, add the other alerts again, save, and check the list.
- Screenshot: `00_budget.png`.

### 2026-10-11 — 0.3 Cost estimate
- Wrote `docs/cost/estimate.md`: about $1.70 for 7 days. Biggest risk: a compute cluster left with min nodes above 0.

### 2026-10-11 — 0.4 Install the tools
- Python 3.12, Git, VS Code, Docker Desktop, Azure CLI, GitHub CLI.
- Error: `az` was not found. Fix: `winget install -e --id Microsoft.AzureCLI`, then open a new terminal.

### 2026-10-12 — 0.5 Logins
- `az login`, `az account show` (subscription Enabled), `gh auth login` (scopes include `repo` and `workflow`).

### 2026-10-12 — 0.6 CLI extensions and resource providers
- `az extension add -n ml`, `az extension add -n containerapp`, `az bicep install`.
- `az provider register -n <namespace>` for 7 providers (App, OperationalInsights, ContainerRegistry, KeyVault, MachineLearningServices, Insights, Storage).
- Note: providers show "Registering" for a few minutes before "Registered". Registering is free.

### 2026-10-12 — 0.7 Git and GitHub
- `git init -b main`, `git add .`, `git commit`, `gh repo create azure-churn-mlops --public --source . --remote origin --push`.
- Error: "`--push` enabled but no commits found". Cause: the files were never staged, so there was no commit. Fix: `git add .`, `git commit`, then run `gh repo create` again.

### 2026-10-12 — 0.8 Project files
- Added `.gitignore`, `requirements.txt`, `scripts/names.ps1`, this log, `docs/cost/COST_LOG.md` and `docs/results/`.
- Kept private files out of Git: `PLAN.md`, `CLAUDE.md` and `.claude/` are in `.gitignore`. PLAN.md was already pushed, so: `git rm --cached PLAN.md`, `git commit --amend`, `git push --force origin main`.
- Checked `. .\scripts\names.ps1` loads. Credit at the end of Phase 0: €175.99 (no resources yet).
