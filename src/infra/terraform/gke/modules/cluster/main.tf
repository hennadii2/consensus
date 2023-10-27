variable "env" {}
variable "environment" {}
variable "dedicated_machine_type" {}
variable "dedicated_min_nodes" {}
variable "dedicated_max_nodes" {}
variable "preemptible_machine_type" {}
variable "preemptible_min_nodes" {}
variable "preemptible_max_nodes" {}
variable "oauth_client_secret" {}

data "google_project" "project" {
}

data "google_client_config" "default" {

}

provider "google" {
  project = "consensus-334718"
  region  = "us-central1"
}

resource "google_container_cluster" "cluster" {
  name               = "${var.env}-cluster"
  location           = "us-central1"
  min_master_version = "1.26"
  # We can't create a cluster with no node pool defined, but we want to only use
  # separately managed node pools. So we create the smallest possible default
  # node pool and immediately delete it.
  remove_default_node_pool = true
  initial_node_count       = 1
  network                  = "dev-vpc"
  subnetwork               = "default-${var.env}"

  ip_allocation_policy {
    cluster_secondary_range_name  = "default-${var.env}-pods"
    services_secondary_range_name = "default-${var.env}-services"
  }

  workload_identity_config {
    workload_pool = "${data.google_project.project.project_id}.svc.id.goog"
  }
  depends_on = [
    google_compute_subnetwork.subnet
  ]
}

resource "google_container_node_pool" "primary_preemptible_nodes" {
  name     = "preemptible-pool"
  location = "us-central1"
  cluster  = google_container_cluster.cluster.name

  node_config {
    preemptible  = true
    machine_type = var.preemptible_machine_type

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
      "https://www.googleapis.com/auth/logging.write",
    ]
  }
  depends_on = [
    google_container_cluster.cluster
  ]
  autoscaling {
    location_policy      = "BALANCED"
    total_min_node_count = var.preemptible_min_nodes
    total_max_node_count = var.preemptible_max_nodes
    min_node_count       = 0
    max_node_count       = 0
  }
}

resource "google_container_node_pool" "primary_dedicated_nodes" {
  name     = "dedicated-pool"
  location = "us-central1"
  cluster  = google_container_cluster.cluster.name

  node_config {
    machine_type = var.dedicated_machine_type

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
      "https://www.googleapis.com/auth/logging.write",
    ]
  }
  depends_on = [
    google_container_cluster.cluster
  ]
  autoscaling {
    location_policy      = "BALANCED"
    total_min_node_count = var.dedicated_min_nodes
    total_max_node_count = var.dedicated_max_nodes
    min_node_count       = 0
    max_node_count       = 0
  }
}

provider "kubernetes" {
  host  = "https://${google_container_cluster.cluster.endpoint}"
  token = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(
    google_container_cluster.cluster.master_auth[0].cluster_ca_certificate,
  )
}

provider "helm" {
  kubernetes {
    host  = "https://${google_container_cluster.cluster.endpoint}"
    token = data.google_client_config.default.access_token
    cluster_ca_certificate = base64decode(
      google_container_cluster.cluster.master_auth[0].cluster_ca_certificate,
    )
  }
}

resource "kubernetes_namespace" "cert_manager" {
  metadata {
    name = "cert-manager"
    labels = {
      "certmanager.k8s.io/disable-validation" = "true"
    }
  }
  depends_on = [
    google_container_cluster.cluster
  ]
}

resource "helm_release" "cert_manager" {
  name       = "cert-manager"
  namespace  = "cert-manager"
  chart      = "cert-manager"
  version    = "v1.12.1"
  repository = "https://charts.jetstack.io"

  set {
    name  = "ingressShim.defaultIssuerName"
    value = "cluster-issuer-stage"
  }
  set {
    name  = "ingressShim.defaultIssuerKind"
    value = "cluster-issuer-stage"
  }
  set {
    name  = "installCRDs"
    value = "true"
  }
  depends_on = [
    kubernetes_namespace.cert_manager,
    google_container_cluster.cluster,
    google_container_node_pool.primary_preemptible_nodes,
    google_container_node_pool.primary_dedicated_nodes
  ]
}

resource "kubernetes_manifest" "cluster_issuer_stage" {
  manifest = {
    "apiVersion" = "cert-manager.io/v1"
    "kind"       = "ClusterIssuer"
    "metadata" = {
      "name" = "cluster-issuer-stage"
    }
    "spec" = {
      "acme" = {
        "server" = "https://acme-staging-v02.api.letsencrypt.org/directory"
        "email"  = "devops@consensus.app"
        "privateKeySecretRef" = {
          "name" = "cluster-issuer-stage-private-key"
        }
        "solvers" = [
          {
            "http01" = {
              "ingress" = {}
            }
          }
        ]
      }
    }
  }
  depends_on = [
    helm_release.cert_manager,
    google_container_cluster.cluster
  ]
}

resource "kubernetes_manifest" "cluster_issuer_prod" {
  manifest = {
    "apiVersion" = "cert-manager.io/v1"
    "kind"       = "ClusterIssuer"
    "metadata" = {
      "name" = "cluster-issuer-prod"
    }
    "spec" = {
      "acme" = {
        "server" = "https://acme-v02.api.letsencrypt.org/directory"
        "email"  = "devops@concensus.app"
        "privateKeySecretRef" = {
          "name" = "cluster-issuer-prod-private-key"
        }
        "solvers" = [
          {
            "http01" = {
              "ingress" = {}
            }
          }
        ]
      }
    }
  }
  depends_on = [
    helm_release.cert_manager,
    google_container_cluster.cluster
  ]
}

resource "kubernetes_namespace" "namespace" {
  metadata {
    name = var.environment
  }
  depends_on = [
    google_container_cluster.cluster
  ]
}

resource "kubernetes_service_account" "github_actions" {
  metadata {
    name      = "github-actions"
    namespace = var.environment
    annotations = {
      "iam.gke.io/gcp-service-account" : "github-actions@consensus-334718.iam.gserviceaccount.com"
    }
  }
}

resource "google_service_account_iam_binding" "github_actions_binding" {
  count              = var.env == "staging" ? 1 : 0
  service_account_id = "projects/consensus-334718/serviceAccounts/github-actions@consensus-334718.iam.gserviceaccount.com"
  role               = "roles/iam.workloadIdentityUser"

  members = [
    "serviceAccount:consensus-334718.svc.id.goog[development/github-actions]",
    "serviceAccount:consensus-334718.svc.id.goog[staging/github-actions]",
    "serviceAccount:consensus-334718.svc.id.goog[production/github-actions]"
  ]
}

resource "google_service_account" "storage_viewer" {
  account_id = "${var.env}-storage-viewer"
}

resource "google_project_iam_member" "storage_viewer" {
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.storage_viewer.email}"
  project = "consensus-334718"
}

resource "google_service_account_key" "storage_viewer" {
  service_account_id = google_service_account.storage_viewer.name
  public_key_type    = "TYPE_X509_PEM_FILE"
}

resource "kubernetes_secret" "kubernetes_storage_secret" {
  metadata {
    name      = "gcr-creds"
    namespace = var.environment
  }
  data = {
    ".dockerconfigjson" = jsonencode({
      auths = {
        "https://gcr.io" = {
          registry = "https://gcr.io"
          username = "_json_key"
          password = base64decode(google_service_account_key.storage_viewer.private_key)
        }
      }
    })
  }
  type = "kubernetes.io/dockerconfigjson"
}

resource "google_project_iam_member" "log_writer" {
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:387183870805-compute@developer.gserviceaccount.com"
  project = "consensus-334718"
}

output "endpoint" {
  value = google_container_cluster.cluster.endpoint
}

output "cluster_ca_certificate" {
  value = google_container_cluster.cluster.master_auth[0].cluster_ca_certificate
}

resource "kubernetes_namespace" "development" {
  count = var.env == "staging" ? 1 : 0
  metadata {
    name = "development"
  }
  depends_on = [
    google_container_cluster.cluster
  ]
}

resource "kubernetes_service_account" "dev_github_actions" {
  count = var.env == "staging" ? 1 : 0
  metadata {
    name      = "github-actions"
    namespace = "development"
    annotations = {
      "iam.gke.io/gcp-service-account" : "github-actions@consensus-334718.iam.gserviceaccount.com"
    }
  }
}

resource "kubernetes_secret" "kubernetes_storage_secret_dev" {
  count = var.env == "staging" ? 1 : 0
  metadata {
    name      = "gcr-creds"
    namespace = "development"
  }
  data = {
    ".dockerconfigjson" = jsonencode({
      auths = {
        "https://gcr.io" = {
          registry = "https://gcr.io"
          username = "_json_key"
          password = base64decode(google_service_account_key.storage_viewer.private_key)
        }
      }
    })
  }
  type = "kubernetes.io/dockerconfigjson"
}

resource "kubernetes_secret" "oauth_secret" {
  metadata {
    name      = "oauth-secret"
    namespace = var.environment
  }

  data = {
    client_id     = "387183870805-cpurf3ackucpp7aqbfvugpm6ufq85kdm.apps.googleusercontent.com"
    client_secret = "${var.oauth_client_secret}"
  }
}

resource "kubernetes_manifest" "backend_config" {
  manifest = {
    "apiVersion" = "cloud.google.com/v1"
    "kind"       = "BackendConfig"
    "metadata" = {
      "name"      = "be-config"
      "namespace" = "${var.environment}"
    }
    "spec" = {
      "iap" = {
        "enabled" = "true"
        "oauthclientCredentials" = {
          "secretName" = "oauth-secret"
        }
      }
    }
  }
  depends_on = [
    kubernetes_secret.oauth_secret
  ]
}

resource "helm_release" "argo_rollouts" {
  chart      = "argo-rollouts"
  version    = "2.32.0"
  name       = "argo-rollouts"
  repository = "https://argoproj.github.io/argo-helm"
}
