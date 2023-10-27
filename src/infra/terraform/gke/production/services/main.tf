terraform {
  backend "gcs" {
    bucket = "consensus-terraform"
    prefix = "production/services"
  }
}

data "terraform_remote_state" "cluster" {
  backend = "gcs"

  config = {
    bucket = "consensus-terraform"
    prefix = "production/cluster"
  }
}

variable "replicas" {}
variable "cpu_limit" {}
variable "cpu_request" {}
variable "memory_limit" {}
variable "memory_request" {}
variable "min_replicas" {}
variable "max_replicas" {}
variable "scaling_cpu_target" {}
variable "image_tag" {}
variable "backend_env" {
  default = ""
}
variable "backend_db_env" {
  default = ""
}
variable "backend_search_env" {
  default = ""
}
variable "search_index" {
  default = ""
}
variable "autocomplete_index" {
  default = ""
}

module "services" {
  source       = "../../modules/services"
  env          = "prod"
  environment  = "production"
  k8s_ca_cert  = data.terraform_remote_state.cluster.outputs.cluster_ca_certificate
  k8s_endpoint = data.terraform_remote_state.cluster.outputs.endpoint
  image_tag    = var.image_tag
  hostenv      = ""

  service = {
    "name"               = terraform.workspace
    "replicas"           = var.replicas
    "cpu_limit"          = var.cpu_limit
    "memory_limit"       = var.memory_limit
    "cpu_request"        = var.cpu_request
    "memory_request"     = var.memory_request
    "min_replicas"       = var.min_replicas
    "max_replicas"       = var.max_replicas
    "scaling_cpu_target" = var.scaling_cpu_target
    "backend_env"        = var.backend_env
    "backend_db_env"     = var.backend_db_env
    "backend_search_env" = var.backend_search_env
    "search_index"       = var.search_index
    "autocomplete_index" = var.autocomplete_index
  }
}
