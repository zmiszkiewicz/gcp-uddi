terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}



locals {
  startup_script_content = file("${path.root}/${var.startup_script}")
}

resource "google_compute_network" "vpc" {
  name                    = var.vpc_name
  auto_create_subnetworks = false
  project = var.project

}

resource "google_compute_subnetwork" "subnet" {
  name          = var.subnet_name
  ip_cidr_range = var.subnet_cidr
  region        = var.region
  network       = google_compute_network.vpc.id
  project = var.project

}

resource "tls_private_key" "ssh_key" {
  algorithm = "RSA"
  rsa_bits  = 4096

}

resource "local_sensitive_file" "private_key_pem" {
  filename        = "./${var.instance_name}.pem"
  content         = tls_private_key.ssh_key.private_key_pem
  file_permission = "0400"

}

resource "google_compute_firewall" "allow-ssh" {
  name    = "${var.vpc_name}-allow-ssh"
  network = google_compute_network.vpc.name
  project = var.project

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
}

resource "google_compute_firewall" "custom-fw" {
  name    = "${var.vpc_name}-custom-fw"
  network = google_compute_network.vpc.name
  project = var.project

  allow {
    protocol = "tcp"
    ports    = ["5000", "5201", "5432"]
  }

  allow {
    protocol = "udp"
    ports    = ["5201"]
  }

  allow {
    protocol = "icmp"
  }

  source_ranges = [
    "10.0.0.0/8",
    "20.113.88.59/32",
    "72.14.201.91/32"
  ]
}

resource "google_compute_address" "static_ip" {
  name   = "${var.vpc_name}-static-ip"
  region = var.region
  labels = var.labels
  project = var.project
}

resource "google_compute_instance" "vm_instance" {
  name         = var.instance_name
  machine_type = var.machine_type
  zone         = var.zone
  labels = var.labels
  project = var.project

  boot_disk {
    initialize_params {
      image = var.image
    }
  }

  network_interface {
  subnetwork         = google_compute_subnetwork.subnet.self_link
  network_ip         = var.private_ip

  access_config {
    nat_ip = google_compute_address.static_ip.address
  }
}

  metadata_startup_script = local.startup_script_content

  metadata = {
    ssh-keys = "${var.ssh_user}:${tls_private_key.ssh_key.public_key_openssh}"

  }

  tags = ["web"]
}
