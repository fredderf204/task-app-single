provider "azurerm" {
  version = "~>2.0"
  features {}
}

resource "random_string" "prefix" {
  length  = 5
  special = false
  upper   = false
  lower = true
}

resource "azurerm_resource_group" "rg" {
  name     = "${random_string.prefix.result}-rg"
  location = var.location
}

resource "azurerm_cosmosdb_account" "example" {
  name                = "${random_string.prefix.result}-cosacc"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  offer_type          = "Standard"
  kind                = "MongoDB"

  capabilities {
    name = "MongoDBv3.4"
  }

  consistency_policy {
    consistency_level       = "Eventual"
  }

  geo_location {
    location          = azurerm_resource_group.rg.location
    failover_priority = 0
  }
}

resource "azurerm_cosmosdb_mongo_database" "example" {
  name                = "${random_string.prefix.result}-mogdb"
  resource_group_name = azurerm_resource_group.rg.name
  account_name        = azurerm_cosmosdb_account.example.name
}

resource "azurerm_cosmosdb_mongo_collection" "example" {
  name                = "${random_string.prefix.result}-mogcol"
  resource_group_name = azurerm_resource_group.rg.name
  account_name        = azurerm_cosmosdb_account.example.name
  database_name       = azurerm_cosmosdb_mongo_database.example.name

  default_ttl_seconds = 0
  shard_key           = "_id"
}

resource "azurerm_app_service_plan" "example" {
  name                = "${random_string.prefix.result}-asp"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  kind                = "Linux"
  reserved            = true

  sku {
    tier = "Standard"
    size = "S1"
  }
}

resource "azurerm_app_service" "api" {
  name                = "${random_string.prefix.result}-api"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  app_service_plan_id = azurerm_app_service_plan.example.id

  site_config {
    app_command_line = ""
    linux_fx_version = "DOCKER|${var.api-image}"
    cors {
      allowed_origins = ["https://${random_string.prefix.result}-fe.azurewebsites.net"]
    }
  }

  app_settings = {
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
    "WEBSITES_PORT" = var.api-port
    "mongoacct" = azurerm_cosmosdb_account.example.name
    "mongodb" = azurerm_cosmosdb_mongo_database.example.name
    "mongocol" = azurerm_cosmosdb_mongo_collection.example.name
    "mongopwd" = azurerm_cosmosdb_account.example.primary_key
    # Settings for private Container Registires  
    "DOCKER_REGISTRY_SERVER_URL"      = var.docker-url
    "DOCKER_REGISTRY_SERVER_USERNAME" = var.docker-username
    "DOCKER_REGISTRY_SERVER_PASSWORD" = var.docker-password

  }

}

resource "azurerm_app_service" "fe" {
  name                = "${random_string.prefix.result}-fe"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  app_service_plan_id = azurerm_app_service_plan.example.id

  site_config {
    app_command_line = ""
    linux_fx_version = "DOCKER|${var.fe-image}"
  }

  app_settings = {
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
    "WEBSITES_PORT" = var.fe-port
    "tenantname" = var.tenant-name
    "tenant" = random_string.prefix.result
    "api" = "https://${azurerm_app_service.api.name}.azurewebsites.net/task"
    # Settings for private Container Registires  
    "DOCKER_REGISTRY_SERVER_URL"      = var.docker-url
    "DOCKER_REGISTRY_SERVER_USERNAME" = var.docker-username
    "DOCKER_REGISTRY_SERVER_PASSWORD" = var.docker-password

  }


}