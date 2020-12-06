output "app_service_default_hostname" {
  value = "https://${azurerm_app_service.fe.default_site_hostname}"
}