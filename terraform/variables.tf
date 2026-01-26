variable "GCP_EU_North" {
  description = "Map of GCP instances and networking configuration per VPC"
  type = map(object({
    gcp_region             = string
    gcp_zone               = string
    ssh_user               = string
    startup_script         = string

    gcp_vpc_name           = string
    gcp_subnet_name        = string
    gcp_private_ip         = string
    gcp_app_fqdn           = string
    gcp_instance_name      = string
    gcp_vm_key_pair_name   = string
    gcp_vpc_cidr           = string
    gcp_subnet_cidr        = string

    labels = map(string)
  }))
}

variable "projectid" {
  type = string
}
