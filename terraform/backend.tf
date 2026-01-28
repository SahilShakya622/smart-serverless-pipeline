terraform {
  backend "azurerm" {
    resource_group_name  = "tfstate-rg"
    storage_account_name = "tfstatesahil123"
    container_name       = "tfstate"
    key                  = "smart-serverless.tfstate"
  }
}
