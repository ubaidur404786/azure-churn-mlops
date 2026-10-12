# Problems and fixes

Real problems from the [learning log](../LEARNING_LOG.md). In an interview, tell each one as **problem → cause → fix → lesson**.

## The 5 best stories

### 1. The cloud model could not be loaded by the API

- **Problem:** the model trained in Azure ML crashed the API tests with `Can't get attribute '_RemainderColsList'`.
- **Cause:** Azure ML's ready-made environment had scikit-learn 1.5.2, but the API image had 1.9.1. A pickled model only loads with the same library version.
- **Fix:** pin the same versions (scikit-learn 1.5.2 and matching numpy, pandas, joblib) in both requirement files, and test the cloud model locally before deploying.
- **Lesson:** training and serving must use the same library versions. Pin them.

### 2. GitHub could not log in to Azure (OIDC)

- **Problem:** the deploy failed with `AADSTS700213: No matching federated identity record`.
- **Cause:** GitHub now puts the owner id and repo id in the token subject (`repo:owner@id/repo@id:ref:refs/heads/main`), but the trust rule had the old format.
- **Fix:** copy the exact subject from the error into the federated credential, then re-run the workflow.
- **Lesson:** read the error message; it often contains the exact value you need.

### 3. CI failed because pytest ran the wrong file

- **Problem:** CI stopped with exit code 3 and `SystemExit`.
- **Cause:** pytest runs every file named `test_*.py`, so it also ran `scripts/test_live_api.py`, the live speed script.
- **Fix:** `testpaths = tests` in `pytest.ini`, so only the real tests run.
- **Lesson:** a file name can change what a tool does. Tell the tool exactly where to look.

### 4. The training workflow was red, but the job was fine

- **Problem:** the job in Azure ML Completed, but the GitHub workflow failed with `binascii.Error: Incorrect padding`.
- **Cause:** `az ml job stream` does not work with the OIDC login token.
- **Fix:** ask for the job status every 30 seconds (`az ml job show --query status`) instead of streaming the logs.
- **Lesson:** separate "did the job work?" from "did the watching tool work?".

### 5. KQL counted fewer requests than the portal

- **Problem:** `count()` said 14 requests, but the portal showed 31.
- **Cause:** the telemetry is sampled. One stored row can stand for several requests, and `itemCount` says how many.
- **Fix:** use `sum(itemCount)` instead of `count()`.
- **Lesson:** know how your monitoring data is collected before trusting the numbers.

## Smaller problems

| Problem | Cause | Fix |
|---|---|---|
| `az` not found | Azure CLI not installed or the terminal was old | `winget install -e --id Microsoft.AzureCLI`, open a new terminal |
| Budget saved with only one alert | the form kept only the first alert | edit the budget, add the alerts again, check the list |
| `gh repo create --push`: no commits | the files were never committed | `git add .`, `git commit`, then run it again |
| 11 customers with empty `TotalCharges` | new customers (tenure 0) | convert to numbers and fill with 0 |
| `repository "churn-api" is not found` in ACR | the image was built but not pushed | `docker push` |
| Second speed test overwrote the cold-start result | the app was already awake | the script now skips saving when the first request is under 5 s |
| `EmailAddressIsNotValid` | the placeholder `YOUR_EMAIL` was not replaced | put the address in a `$EMAIL` variable in the terminal only |
| Alert command printed `mismatched input '/'` | the CLI parser and the `/` in the dimension name | checked with `az monitor metrics alert show`: the filter was kept |
| Node.js 20 warnings in Actions | old action versions | `actions/checkout@v5`, `setup-python@v6`, `azure/login@v3` |
| Cost showed €0 for a day | cost data arrives 8–48 h late | wait before reading the cost |
