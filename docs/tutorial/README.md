# Tutorial: build this project step by step

Each page below is one phase. Every page starts with a **step-by-step diagram** of that phase and a table with one row per arrow: the command, the tool it calls, what is sent and what comes back. Then, for every step, it shows:

- what the step does and why
- each command exactly as it was run
- the real output (shortened; subscription IDs, emails and secrets removed)
- what the output means
- any error, its cause and the fix
- the screenshots of that step

Every new terminal starts with:

```powershell
. .\scripts\names.ps1
```

Big picture first: [the architecture diagram](../architecture/architecture.svg) and the [project README](../../README.md).

| Phase | Page |
|---|---|
| 0 — Safety, cost tracking and setup | [phase_00_setup.md](phase_00_setup.md) |
| 1 — Simple model + API on the laptop | [phase_01_laptop.md](phase_01_laptop.md) |
| 2 — Azure resources with Bicep | [phase_02_bicep.md](phase_02_bicep.md) |
| 3 — Live API on Azure Container Apps | [phase_03_container_apps.md](phase_03_container_apps.md) |
| 4 — Train in Azure Machine Learning | [phase_04_azure_ml.md](phase_04_azure_ml.md) |
| 5 — CI/CD with GitHub Actions + OIDC | [phase_05_cicd.md](phase_05_cicd.md) |
| 6 — Monitoring with Application Insights | [phase_06_monitoring.md](phase_06_monitoring.md) |
| 7 — Proof pack while everything is live | [phase_07_proof.md](phase_07_proof.md) |

Want to rebuild it yourself? [GUIDE.md](../../GUIDE.md) has every step **by code and by hand in the Azure portal side by side**, including where to start if you only have a container image or only code on GitHub.
