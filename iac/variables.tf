variable "subscription_id" { description = "ID della subscription Azure" }
variable "resource_group_name" { default = "trustme-rg" }
variable "location" { default = "italynorth" }
variable "app_service_plan_name" { default = "trustme-appserviceplan" }
variable "app_service_name" { default = "trustme-appservice" }
variable "container_registry_name" { default = "trustmeregistry" }
