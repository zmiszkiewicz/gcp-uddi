variable "project" {
  type = string
}
variable "region" {}
variable "zone" {}

variable "vpc_name" {}
variable "subnet_name" {}
variable "subnet_cidr" {}

variable "private_ip" {}
variable "instance_name" {}
variable "machine_type" {
  default = "e2-medium"
}
variable "image" {
  default = "projects/debian-cloud/global/images/family/debian-11"
}
variable "startup_script" {}
variable "ssh_user" {
  default = "debian"
}

variable "labels" {
  description = "Common labels applied to all GCP resources"
  type        = map(string)
  default     = {}
}
