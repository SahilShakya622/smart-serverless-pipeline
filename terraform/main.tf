#################################
# Resource Group
#################################
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

#################################
# Storage Account (Blob Trigger)
#################################
resource "azurerm_storage_account" "storage" {
  name                     = "smartblobstore01"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

# ⚠️ REQUIRED to use storage_account_name here
# (Ignore VS Code deprecation warning – provider still requires it)
resource "azurerm_storage_container" "input" {
  name                  = "input-files"
  storage_account_name  = azurerm_storage_account.storage.name
  container_access_type = "private"
}

#################################
# Cosmos DB (SQL API – Provisioned)
#################################
resource "azurerm_cosmosdb_account" "cosmos" {
  name                = "smartcosmosdb01"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"

  consistency_policy {
    consistency_level = "Session"
  }

  geo_location {
    location          = azurerm_resource_group.rg.location
    failover_priority = 0
  }
}

resource "azurerm_cosmosdb_sql_database" "db" {
  name                = "processingdb"
  resource_group_name = azurerm_resource_group.rg.name
  account_name        = azurerm_cosmosdb_account.cosmos.name
}

resource "azurerm_cosmosdb_sql_container" "results" {
  name                = "results"
  resource_group_name = azurerm_resource_group.rg.name
  account_name        = azurerm_cosmosdb_account.cosmos.name
  database_name       = azurerm_cosmosdb_sql_database.db.name
  partition_key_paths = ["/fileType"]
  throughput          = 400
}

#################################
# Function Service Plan (Serverless)
#################################
resource "azurerm_service_plan" "plan" {
  name                = "func-consumption-plan"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  os_type             = "Linux"
  sku_name            = "Y1"
}

#################################
# Application Insights
#################################
resource "azurerm_application_insights" "appi" {
  name                = "smart-ai"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  application_type    = "web"
  lifecycle {
ignore_changes = [
workspace_id
]
}
}

#################################
# Azure Function App (Python)
#################################
resource "azurerm_linux_function_app" "function" {
  name                = "smart-serverless-func"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  service_plan_id     = azurerm_service_plan.plan.id

  storage_account_name = azurerm_storage_account.storage.name
  storage_account_access_key = azurerm_storage_account.storage.primary_access_key

app_settings = {
  AzureWebJobsStorage                   = azurerm_storage_account.storage.primary_connection_string
  FUNCTIONS_WORKER_RUNTIME              = "python"
  COSMOS_ENDPOINT                       = azurerm_cosmosdb_account.cosmos.endpoint
  COSMOS_KEY                            = azurerm_cosmosdb_account.cosmos.primary_key
  APPLICATIONINSIGHTS_CONNECTION_STRING = azurerm_application_insights.appi.connection_string
  FUNCTIONS_EXTENSION_VERSION           = "~4"
}

site_config {
  application_stack {
    python_version = "3.10"
  }
}
}