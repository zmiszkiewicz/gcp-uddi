GCP_EU_North = {
  VPC1 = {
    gcp_region     = "europe-north1"
    gcp_zone       = "europe-north1-a"
    ssh_user       = "terraform"
    startup_script = "../scripts/gcp_user_data.sh"

    gcp_vpc_name         = "websvcsprodeu1"
    igw_name             = "Websvcs"
    rt_name              = "websvcsprodeu1-rt"
    gcp_subnet_name      = "websvcsprodeu1-subnet"
    gcp_private_ip       = "10.30.0.100"
    gcp_app_fqdn         = "app1.infolab.com"
    gcp_instance_name    = "webserverprodeu1"
    gcp_vm_key_pair_name = "eu_west_webprod1_gcp"
    gcp_vpc_cidr         = "10.30.0.0/24"
    gcp_subnet_cidr      = "10.30.0.0/24"

    labels = {
      environment   = "prod"
      resourceowner = "igor-racic"
    }
  }
}

