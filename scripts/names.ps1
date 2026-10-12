# All resource names for the project.
# Run this at the start of every new terminal:  . .\scripts\names.ps1

# Resource group and region
$RG = "rg-churn-mlops"
$LOCATION = "francecentral"

# Short suffix so global names (storage, registry, key vault) are unique
$SUFFIX = "ub4786"

# data: storage account (lowercase letters and numbers only)
$STORAGE = "stchurn$SUFFIX"

# training: Azure ML workspace and compute cluster
$AML_WORKSPACE = "mlw-churn-mlops"
$AML_CLUSTER = "cpu-cluster"

# registry: container registry (lowercase letters and numbers only)
$ACR = "acrchurn$SUFFIX"

# registry: full image name inside the registry (add a tag like :v1 when using it)
$IMAGE = "$ACR.azurecr.io/churn-api"

# serving: Container Apps environment and app
$CAE = "cae-churn-mlops"
$CA = "ca-churn-api"

# secrets: Key Vault and managed identity
$KV = "kv-churn-$SUFFIX"
$IDENTITY = "id-churn-api"

# monitoring: Log Analytics and Application Insights
$LAW = "log-churn-mlops"
$APPI = "appi-churn-mlops"

# Tags that every resource gets (plus one feature tag)
$TAGS = @("project=churn-mlops", "owner=ubaid", "env=demo")

# GitHub repository
$GH_REPO = "ubaidur404786/azure-churn-mlops"

# Show that the names are loaded
Write-Host "Names loaded for $RG in $LOCATION"
