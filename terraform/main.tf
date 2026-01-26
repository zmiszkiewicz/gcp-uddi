locals {
  GCP_EU_North_final = {
    for k, v in var.GCP_EU_North : k => merge(v, {
      gcp_project = var.projectid
    })
  }
}

# Create Linux and Networking Infrastructure in GCP

module "gcp_instances" {
  source   = "./gcp-resources"
  for_each = local.GCP_EU_North_final
  providers = {
    google = google.gcp_instances
  }

  project         = each.value["gcp_project"]
  region          = each.value["gcp_region"]
  zone            = each.value["gcp_zone"]

  vpc_name        = each.value["gcp_vpc_name"]
  subnet_name     = each.value["gcp_subnet_name"]
  subnet_cidr     = each.value["gcp_subnet_cidr"]
  private_ip      = each.value["gcp_private_ip"]
  instance_name   = each.value["gcp_instance_name"]

  startup_script = each.value["startup_script"] # just the string path
  ssh_user        = each.value["ssh_user"]

  labels          = each.value["labels"]
}