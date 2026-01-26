## Output variable definitions

#output "ssh_access_aws_us" {
#  value = values(module.aws__instances_us)[*].ssh_access
#}

output "gcp_vpc_ids" {
  description = "Map of GCP VPC IDs created by the gcp_instances module"
  value       = { for key, instance in module.gcp_instances : key => instance.gcp_vpc_id }
}
