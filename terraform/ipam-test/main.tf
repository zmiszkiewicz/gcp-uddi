terraform {
  required_providers {
    bloxone = {
      source  = "infobloxopen/bloxone"
      version = ">= 1.5.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

provider "bloxone" {
  csp_url = "https://csp.infoblox.com"
  api_key = var.ddi_api_key

  default_tags = {
    managed_by = "terraform"
    site       = "Site A"
  }
}

# -----------------------------
# Variables
# -----------------------------
variable "ddi_api_key" {}
variable "aws_region" {
  default = "eu-west-2"
}
variable "availability_zone" {
  default = "eu-west-2a"
}
variable "project_name" {
  default = "infoblox-aws-integration"
}

# -----------------------------
# Lookup Realm and Federated Block
# -----------------------------
data "bloxone_federation_federated_realms" "acme" {
  filters = {
    name = "ACME Corporation"
  }
}

data "bloxone_federation_federated_blocks" "aws_block" {
  filters = {
    name = "AWS"
  }
}

# -----------------------------
# Create Infoblox IPAM Resources
# -----------------------------
resource "bloxone_ipam_ip_space" "ip_space_acme" {
  name    = "acme-ip-space"
  comment = "IP space for ACME via Terraform"

  default_realms = [data.bloxone_federation_federated_realms.acme.results[0].id]

  tags = {
    project     = var.project_name
    environment = "dev"
  }
}

resource "bloxone_ipam_address_block" "block_aws_vpc" {
  address = "10.20.20.0"
  cidr    = 24
  name    = "aws-vpc-block"
  space   = bloxone_ipam_ip_space.ip_space_acme.id

  federated_realms = [data.bloxone_federation_federated_realms.acme.results[0].id]

  tags = {
    origin          = "federated"
    provisioned_by  = "terraform"
    block_type      = "materialized"
  }
}

resource "bloxone_ipam_subnet" "subnet_aws_vpc" {
  next_available_id = bloxone_ipam_address_block.block_aws_vpc.id
  cidr              = 26
  space             = bloxone_ipam_ip_space.ip_space_acme.id

  name = "aws-vpc-subnet"

  tags = {
    network_type = "vpc-subnet"
    cloud        = "aws"
  }
}




# -----------------------------
# Create AWS Networking
# -----------------------------
resource "aws_vpc" "vpc_from_infoblox" {
  cidr_block           = "${bloxone_ipam_subnet.subnet_aws_vpc.address}/${bloxone_ipam_subnet.subnet_aws_vpc.cidr}"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name        = "acme-vpc"
    Project     = var.project_name
    Environment = "dev"
    ManagedBy   = "terraform"
  }
}

resource "aws_subnet" "subnet_from_infoblox" {
  vpc_id                  = aws_vpc.vpc_from_infoblox.id
  cidr_block              = aws_vpc.vpc_from_infoblox.cidr_block
  availability_zone       = var.availability_zone
  map_public_ip_on_launch = true

  tags = {
    Name        = "acme-subnet"
    Project     = var.project_name
    Environment = "dev"
    ManagedBy   = "terraform"
  }
}

resource "aws_internet_gateway" "igw_acme" {
  vpc_id = aws_vpc.vpc_from_infoblox.id

  tags = {
    Name        = "acme-igw"
    Project     = var.project_name
    Environment = "dev"
    ManagedBy   = "terraform"
  }
}

resource "aws_route_table" "rt_public" {
  vpc_id = aws_vpc.vpc_from_infoblox.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw_acme.id
  }

  tags = {
    Name        = "acme-public-rt"
    Project     = var.project_name
    Environment = "dev"
    ManagedBy   = "terraform"
  }
}

resource "aws_route_table_association" "rt_assoc_public" {
  subnet_id      = aws_subnet.subnet_from_infoblox.id
  route_table_id = aws_route_table.rt_public.id
}

# -----------------------------
# Outputs
# -----------------------------
output "infoblox_allocated_cidr" {
  description = "CIDR block allocated from Infoblox"
  value       = "${bloxone_ipam_subnet.subnet_aws_vpc.address}/${bloxone_ipam_subnet.subnet_aws_vpc.cidr}"
}

output "vpc_id" {
  description = "AWS VPC ID"
  value       = aws_vpc.vpc_from_infoblox.id
}

output "subnet_id" {
  description = "AWS Subnet ID"
  value       = aws_subnet.subnet_from_infoblox.id
}
