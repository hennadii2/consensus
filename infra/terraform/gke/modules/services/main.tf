variable "env" {}

variable "image_tag" {}
variable "k8s_ca_cert" {}
variable "k8s_endpoint" {}
variable "environment" {}
variable "hostenv" {}
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

data "google_project" "project" {
}

data "google_client_config" "default" {

}

provider "google" {
  project = "consensus-334718"
  region  = "us-central1"
}

provider "helm" {
  kubernetes {
    host  = "https://${var.k8s_endpoint}"
    token = data.google_client_config.default.access_token
    cluster_ca_certificate = base64decode(
      var.k8s_ca_cert,
    )
  }
}

provider "kubernetes" {
  host  = "https://${var.k8s_endpoint}"
  token = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(
    var.k8s_ca_cert,
  )
}

variable "service" {}

resource "helm_release" "service" {
  name      = "${var.env}-web-${var.service["name"]}"
  chart     = "${path.module}/../charts/monochart"
  namespace = var.environment

  values = [templatefile("${path.module}/values-${var.service["name"]}.yaml",
    {
      name               = "${var.env}-web-${var.service["name"]}"
      env                = var.env
      replicas           = var.service["replicas"]
      cpu_limit          = var.service["cpu_limit"]
      memory_limit       = var.service["memory_limit"]
      cpu_request        = var.service["cpu_request"]
      memory_request     = var.service["memory_request"]
      namespace          = var.environment
      backend_env        = var.service["backend_env"]
      backend_db_env     = var.service["backend_db_env"]
      backend_search_env = var.service["backend_search_env"]
      search_index       = var.service["search_index"]
      autocomplete_index = var.service["autocomplete_index"]
      hostenv            = var.hostenv
    }
  )]
  set {
    name  = "image.tag"
    value = var.image_tag
  }
  set {
    name  = "image.repository"
    value = "gcr.io/consensus-334718/web_${var.service["name"]}"
  }
  set {
    name  = "image.pullSecrets"
    value = "{'gcr-creds'}"
  }
}

resource "kubernetes_horizontal_pod_autoscaler" "service" {
  metadata {
    name      = "${var.env}-web-${var.service["name"]}-hpa"
    namespace = var.environment
  }

  spec {
    min_replicas = var.service["min_replicas"]
    max_replicas = var.service["max_replicas"]

    scale_target_ref {
      api_version = "argoproj.io/v1alpha1"
      kind        = "Rollout"
      name        = "${var.env}-web-${var.service["name"]}-monochart"
    }

    target_cpu_utilization_percentage = var.service["scaling_cpu_target"]

  }
}
