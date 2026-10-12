// All Azure resources for the churn MLOps project.
// Deploy with: az deployment group create -g rg-churn-mlops -f infra/main.bicep -p userObjectId=<your id>

// Region: the same as the resource group
param location string = resourceGroup().location

// Short suffix so global names (storage, registry, key vault) are unique
param suffix string = 'ub4786'

// Your own Entra ID object id, so you can write secrets into Key Vault
param userObjectId string

// Tags that every resource gets (each resource adds its own feature tag)
var baseTags = {
  project: 'churn-mlops'
  owner: 'ubaid'
  env: 'demo'
}

// Resource names (same as scripts/names.ps1)
var lawName = 'log-churn-mlops'
var appiName = 'appi-churn-mlops'
var kvName = 'kv-churn-${suffix}'
var storageName = 'stchurn${suffix}'
var acrName = 'acrchurn${suffix}'
var amlName = 'mlw-churn-mlops'
var caeName = 'cae-churn-mlops'
var identityName = 'id-churn-api'

// Built-in role ids (the same in every Azure subscription)
var acrPullRole = '7f951dda-4ed3-4680-a7ca-43fe172d538d'
var kvSecretsUserRole = '4633458b-17de-408a-b874-0445c86b69e6'
var kvSecretsOfficerRole = 'b86a8fe4-44ce-4948-aee5-eccb2c155cd7'

// monitoring: Log Analytics workspace that stores all logs (first 5 GB per month free)
resource law 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: lawName
  location: location
  tags: union(baseTags, { feature: 'monitoring' })
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    // Stop collecting logs after 0.5 GB in one day, so logs can never cost much
    workspaceCapping: {
      dailyQuotaGb: json('0.5')
    }
  }
}

// monitoring: Application Insights, stores its data in the Log Analytics workspace
resource appi 'Microsoft.Insights/components@2020-02-02' = {
  name: appiName
  location: location
  kind: 'web'
  tags: union(baseTags, { feature: 'monitoring' })
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: law.id
  }
}

// secrets: Key Vault that uses Azure roles (RBAC) instead of access policies
resource kv 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: kvName
  location: location
  tags: union(baseTags, { feature: 'secrets' })
  properties: {
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    enableRbacAuthorization: true
    // Keep deleted vaults for only 7 days (the minimum)
    softDeleteRetentionInDays: 7
  }
}

// data: Storage account for the dataset and Azure ML files
resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageName
  location: location
  kind: 'StorageV2'
  tags: union(baseTags, { feature: 'data' })
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
  }
}

// registry: Container Registry for the Docker image (Basic plan, no admin user)
resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: acrName
  location: location
  tags: union(baseTags, { feature: 'registry' })
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: false
  }
}

// training: Azure ML workspace, linked to the storage, key vault and app insights above
resource aml 'Microsoft.MachineLearningServices/workspaces@2024-04-01' = {
  name: amlName
  location: location
  tags: union(baseTags, { feature: 'training' })
  sku: {
    name: 'Basic'
    tier: 'Basic'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    friendlyName: amlName
    storageAccount: storage.id
    keyVault: kv.id
    applicationInsights: appi.id
    publicNetworkAccess: 'Enabled'
  }
}

// serving: Container Apps environment (consumption plan), sends app logs to Log Analytics
resource cae 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: caeName
  location: location
  tags: union(baseTags, { feature: 'serving' })
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: law.properties.customerId
        sharedKey: law.listKeys().primarySharedKey
      }
    }
  }
}

// secrets: managed identity that the Container App will use (no passwords)
resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: identityName
  location: location
  tags: union(baseTags, { feature: 'secrets' })
}

// Role: the identity can pull images from the registry, nothing else
resource identityAcrPull 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, identity.id, acrPullRole)
  scope: acr
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', acrPullRole)
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// Role: the identity can read secrets from the key vault, nothing else
resource identityKvRead 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(kv.id, identity.id, kvSecretsUserRole)
  scope: kv
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', kvSecretsUserRole)
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// Role: you can write secrets into the key vault (needed in Phase 3)
resource userKvWrite 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(kv.id, userObjectId, kvSecretsOfficerRole)
  scope: kv
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', kvSecretsOfficerRole)
    principalId: userObjectId
    principalType: 'User'
  }
}

// Values printed after the deployment, used in the next phases
output acrLoginServer string = acr.properties.loginServer
output identityId string = identity.id
output identityClientId string = identity.properties.clientId
output environmentId string = cae.id
output keyVaultUri string = kv.properties.vaultUri
