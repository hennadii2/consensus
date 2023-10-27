variable "ip_cidr_range" {}
variable "pod_ip_cidr_range" {}
variable "services_ip_cidr_range" {}


resource "google_compute_router" "default" {
  # allows NAT to be attached
  name    = "default-${var.env}-router"
  region  = "us-central1"
  network = "projects/consensus-334718/global/networks/dev-vpc"

  bgp {
    asn = 64603
  }
}

resource "google_compute_address" "nat_address" {
  name   = "default-${var.env}-nat-address"
  region = "us-central1"
}

resource "google_compute_router_nat" "default" {
  name                               = "default-${var.env}-nat"
  router                             = google_compute_router.default.name
  nat_ip_allocate_option             = "MANUAL_ONLY"
  nat_ips                            = ["${google_compute_address.nat_address.self_link}"]
  source_subnetwork_ip_ranges_to_nat = "LIST_OF_SUBNETWORKS"
  subnetwork {
    name                    = "projects/consensus-334718/regions/us-central1/subnetworks/default-${var.env}"
    source_ip_ranges_to_nat = ["ALL_IP_RANGES"]
  }
  min_ports_per_vm = 64
}

resource "google_compute_subnetwork" "subnet" {
  # pre-allocation for GKE
  name                     = "default-${var.env}"
  network                  = "projects/consensus-334718/global/networks/dev-vpc"
  ip_cidr_range            = var.ip_cidr_range
  region                   = "us-central1"
  private_ip_google_access = true

  secondary_ip_range {
    range_name    = "default-${var.env}-pods"
    ip_cidr_range = var.pod_ip_cidr_range
  }

  secondary_ip_range {
    range_name    = "default-${var.env}-services"
    ip_cidr_range = var.services_ip_cidr_range
  }
}

resource "google_compute_global_address" "dev_address" {
  count = var.env == "staging" ? 1 : 0
  name  = "dev-frontend-ip"
}

resource "google_compute_global_address" "address" {
  name = "${var.env}-frontend-ip"
}

resource "google_compute_global_address" "labeling_address" {
  count = var.env == "prod" ? 1 : 0
  name  = "${var.env}-labeling-ip"
}

resource "google_compute_global_address" "track_address" {
  count = var.env == "prod" ? 1 : 0
  name  = "${var.env}-track-ip"
}
