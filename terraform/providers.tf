# initiate required Providers
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0" # or latest stable
  }
 }
}

provider "google" {
  alias   = "gcp_instances"
  project = null
  region  = null
  zone    = null
}

