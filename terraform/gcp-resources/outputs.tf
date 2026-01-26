output "gcp_vpc_id" {
  description = "The self link of the created VPC"
  value       = google_compute_network.vpc.self_link
}

output "gcp_subnet_id" {
  description = "The self link of the created subnet"
  value       = google_compute_subnetwork.subnet.self_link
}

output "gcp_instance_private_ip" {
  description = "Private IP address of the instance"
  value       = var.private_ip
}

output "gcp_instance_public_ip" {
  description = "Public (external) IP address of the instance"
  value       = google_compute_address.static_ip.address
}

output "ssh_access" {
  description = "SSH command to access the GCP instance"
  value       = "${var.instance_name} - ${var.private_ip} => ssh -i '${var.instance_name}.pem' ${var.ssh_user}@${google_compute_address.static_ip.address}"
}
