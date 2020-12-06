variable "api-image" {
    description = "Docker image to be used for the api"
    default = "mfriedrich.azurecr.io/task-api-python:0.15"
}

variable "api-port" {
    description = "The port used by the api service"
    default = 5000
}

variable "docker-url" {
    description = "docker registry server url"
    default = "https://mfriedrich.azurecr.io"
}

variable "docker-username" {
    description = "docker registry server username"
}

variable "docker-password" {
    description = "docker registry server password"
}

variable "fe-image" {
    description = "Docker image to be used for front end"
    default = "mfriedrich.azurecr.io/taskfend:0.27"
}

variable "fe-port" {
    description = "The port used by the front end service"
    default = 3000
}

variable "location" {
    description = "location for the resources to be deployed"
    default = "Australia East"
}

variable "tenant-name" {
    description = "The name of the tenant. Captured in web form"
    default = "Tailwind Traders"
}