locals {
  env = {
    dev = {
      name     = "dev",
      hostname = "dev.consensus.app",
      service  = "default"
    },
    staging = {
      name     = "staging",
      hostname = "staging.consensus.app"
      service  = "staging-frontend"
    }
    production = {
      name     = "production",
      hostname = "consensus.app"
      service  = "production-frontend"
    }
    labeling = {
      name     = "labeling",
      hostname = "labeling.consensus.app"
      service  = "labeling"
    }
    track = {
      name     = "track",
      hostname = "track.consensus.app"
      service  = "analytics-proxy"
    }
    chat_dev = {
      name     = "dev-chat",
      hostname = "dev.chat.consensus.app"
      service  = "dev-chat"
    }
    chat_production = {
      name     = "production-chat",
      hostname = "chat.consensus.app"
      service  = "production-chat"
    }
  }
  env_vars  = contains(keys(local.env), terraform.workspace) ? terraform.workspace : "dev"
  workspace = local.env[local.env_vars]
}

variable "oauth_client_secret" {}

terraform {
  backend "gcs" {
    bucket = "consensus-terraform"
    prefix = "appengine-load-balancer"
  }
}

provider "google" {
  project = "consensus-334718"
  region  = "us-central1"
}

resource "google_certificate_manager_certificate" "certificate" {
  name        = "${local.workspace.name}-dns-cert"
  description = "The ${local.workspace.name} cert"
  scope       = "DEFAULT"
  managed {
    domains = [
      google_certificate_manager_dns_authorization.dns_auth.domain,
      google_certificate_manager_dns_authorization.www_dns_auth.domain,
    ]
    dns_authorizations = [
      google_certificate_manager_dns_authorization.dns_auth.id,
      google_certificate_manager_dns_authorization.www_dns_auth.id,
    ]
  }
}

resource "google_certificate_manager_dns_authorization" "dns_auth" {
  name        = "${local.workspace.name}-dns-auth"
  description = "The ${local.workspace.name} dnss"
  domain      = local.workspace.hostname
}

resource "google_certificate_manager_dns_authorization" "www_dns_auth" {
  name        = "www-${local.workspace.name}-dns-auth"
  description = "The www.${local.workspace.name} dnss"
  domain      = "www.${local.workspace.hostname}"
}

resource "google_compute_global_address" "appengine_ip" {
  name = "${local.workspace.name}-appengine-ip"
}

resource "google_compute_region_network_endpoint_group" "appengine_neg" {
  name                  = "${local.workspace.name}-appengine-neg"
  network_endpoint_type = "SERVERLESS"
  region                = "us-central1"
  app_engine {
    service = local.workspace.service
  }
}

resource "google_compute_backend_service" "backend_service" {
  name                  = "${local.workspace.name}-backend-service"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  iap {
    oauth2_client_id     = "387183870805-cpurf3ackucpp7aqbfvugpm6ufq85kdm.apps.googleusercontent.com"
    oauth2_client_secret = var.oauth_client_secret
  }
  backend {
    group = google_compute_region_network_endpoint_group.appengine_neg.id
  }
}

resource "google_compute_url_map" "urlmap" {
  name        = "${local.workspace.name}-urlmap"
  description = "${local.workspace.name} appengine urlmap"

  default_service = google_compute_backend_service.backend_service.id
}

resource "google_certificate_manager_certificate_map" "cert_map" {
  name        = "${local.workspace.name}-cert-map"
  description = "${local.workspace.name} certificate map"
}

resource "google_certificate_manager_certificate_map_entry" "cert_map_entry" {
  name         = "${local.workspace.name}-cert-map-entry"
  description  = "${local.workspace.name} certificate map entry"
  map          = google_certificate_manager_certificate_map.cert_map.name
  certificates = [google_certificate_manager_certificate.certificate.id]
  hostname     = google_certificate_manager_dns_authorization.dns_auth.domain
}

resource "google_certificate_manager_certificate_map_entry" "www_cert_map_entry" {
  name         = "www-${local.workspace.name}-cert-map-entry"
  description  = "${local.workspace.name} certificate map entry"
  map          = google_certificate_manager_certificate_map.cert_map.name
  certificates = [google_certificate_manager_certificate.certificate.id]
  hostname     = google_certificate_manager_dns_authorization.www_dns_auth.domain
}

resource "google_compute_target_https_proxy" "appengine_proxy" {
  name            = "${local.workspace.name}-appengine-proxy"
  url_map         = google_compute_url_map.urlmap.id
  certificate_map = "certificatemanager.googleapis.com/${google_certificate_manager_certificate_map.cert_map.id}"
}

resource "google_compute_global_forwarding_rule" "forwarding_rule" {
  name                  = "${local.workspace.name}-forwarding-rule"
  ip_protocol           = "TCP"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  port_range            = "443"
  target                = google_compute_target_https_proxy.appengine_proxy.id
  ip_address            = google_compute_global_address.appengine_ip.address
}



output "record_name_to_insert" {
  value = google_certificate_manager_dns_authorization.dns_auth.dns_resource_record.0.name
}

output "record_type_to_insert" {
  value = google_certificate_manager_dns_authorization.dns_auth.dns_resource_record.0.type
}

output "record_data_to_insert" {
  value = google_certificate_manager_dns_authorization.dns_auth.dns_resource_record.0.data
}
