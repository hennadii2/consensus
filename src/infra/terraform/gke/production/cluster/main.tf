terraform {
  backend "gcs" {
    bucket = "consensus-terraform"
    prefix = "production/cluster"
  }
}
variable "dedicated_machine_type" {}
variable "dedicated_min_nodes" {}
variable "dedicated_max_nodes" {}
variable "preemptible_machine_type" {}
variable "preemptible_min_nodes" {}
variable "preemptible_max_nodes" {}
variable "oauth_client_secret" {}

module "cluster" {
  source                   = "../../modules/cluster"
  env                      = "prod"
  environment              = "production"
  dedicated_machine_type   = var.dedicated_machine_type
  dedicated_min_nodes      = var.dedicated_min_nodes
  dedicated_max_nodes      = var.dedicated_max_nodes
  preemptible_machine_type = var.preemptible_machine_type
  preemptible_min_nodes    = var.preemptible_min_nodes
  preemptible_max_nodes    = var.preemptible_max_nodes
  oauth_client_secret      = var.oauth_client_secret
  ip_cidr_range            = "10.3.0.0/18"
  pod_ip_cidr_range        = "10.3.64.0/20"
  services_ip_cidr_range   = "10.3.128.0/20"
}

output "endpoint" {
  value = module.cluster.endpoint
}

output "cluster_ca_certificate" {
  value = module.cluster.cluster_ca_certificate
}
