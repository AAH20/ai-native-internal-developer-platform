targetScope = 'resourceGroup'

param suffix string
param location string = resourceGroup().location

param tags object = {
  workload: 'ai-native-internal-developer-platform'
  managedBy: 'bicep'
}

resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'law-launchrail-${suffix}'
  location: location
  tags: tags
  properties: {retentionInDays: 30, sku: {name: 'PerGB2018'}}
}

resource insights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'appi-launchrail-${suffix}'
  location: location
  kind: 'web'
  tags: tags
  properties: {Application_Type: 'web', WorkspaceResourceId: workspace.id}
}

resource registry 'Microsoft.ContainerRegistry/registries@2023-11-01-preview' = {
  name: 'acrlaunchrail${suffix}'
  location: location
  tags: tags
  sku: {name: 'Basic'}
  properties: {adminUserEnabled: false, publicNetworkAccess: 'Enabled'}
}

resource vault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: 'kv-launchrail-${suffix}'
  location: location
  tags: tags
  properties: {
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enablePurgeProtection: true
    softDeleteRetentionInDays: 90
    sku: {family: 'A', name: 'standard'}
  }
}

resource receipts 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: 'stlaunchrail${suffix}'
  location: location
  tags: tags
  sku: {name: 'Standard_LRS'}
  kind: 'StorageV2'
  properties: {allowBlobPublicAccess: false, minimumTlsVersion: 'TLS1_2', supportsHttpsTrafficOnly: true}
}

output applicationInsightsId string = insights.id
output containerRegistryId string = registry.id
output keyVaultId string = vault.id
output receiptStorageId string = receipts.id
