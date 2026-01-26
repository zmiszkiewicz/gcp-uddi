# 🌐 GCP Terraform Module – VPC, Subnet, Firewall, VM with SSH Access

This Terraform module provisions the following GCP infrastructure components:

- ✅ VPC network (custom)
- ✅ Subnet in a specified region
- ✅ Firewall rules for SSH and custom ports
- ✅ Static external IP address
- ✅ VM instance with:
  - Custom startup script
  - Assigned private and public IP
  - Per-instance SSH key (saved locally)

---

## 📦 Resources Created

| Resource Type             | Name Format                   |
|---------------------------|-------------------------------|
| VPC Network               | `${var.vpc_name}`             |
| Subnet                   | `${var.subnet_name}`          |
| Firewall Rule (SSH)      | `${var.vpc_name}-allow-ssh`   |
| Firewall Rule (Custom)   | `${var.vpc_name}-custom-fw`   |
| Static IP                | `${var.vpc_name}-static-ip`   |
| VM Instance              | `${var.instance_name}`        |
| SSH Key File             | `./keys/${instance_name}.pem` |

---

## 📥 Module Inputs

| Name               | Type     | Description                                  | Required |
|--------------------|----------|----------------------------------------------|----------|
| `project`          | string   | GCP project ID                               | ✅       |
| `region`           | string   | Region for resources                         | ✅       |
| `zone`             | string   | Zone for the VM                              | ✅       |
| `vpc_name`         | string   | Name of the VPC                              | ✅       |
| `subnet_name`      | string   | Name of the subnet                           | ✅       |
| `subnet_cidr`      | string   | Subnet IP range in CIDR                      | ✅       |
| `private_ip`       | string   | Fixed internal IP for the VM                 | ✅       |
| `instance_name`    | string   | Name of the VM instance                      | ✅       |
| `machine_type`     | string   | VM machine type (default: `e2-medium`)       | ❌       |
| `image`            | string   | Image to use (default: Debian 11)            | ❌       |
| `ssh_user`         | string   | Username for SSH access (default: `terraform`)| ❌       |
| `startup_script`   | string   | Path to startup script file (.sh)            | ✅       |

---

## 📤 Module Outputs

| Output Name              | Description                             |
|--------------------------|-----------------------------------------|
| `gcp_instance_private_ip`| Internal IP of the VM                   |
| `gcp_instance_public_ip` | External IP of the VM                   |
| `ssh_access`             | SSH command string for direct access    |
| `private_key_file_path`  | Path to the generated `.pem` file       |

---

## 🚀 Example Usage

```hcl
module "gcp_instances" {
  source       = "./modules/gcp-resources"
  for_each     = var.GCP_EU_North

  project         = var.project
  region          = var.region
  zone            = var.zone

  vpc_name        = each.value["gcp_vpc_name"]
  subnet_name     = each.value["gcp_subnet_name"]
  subnet_cidr     = each.value["gcp_subnet_cidr"]
  private_ip      = each.value["gcp_private_ip"]
  instance_name   = each.value["gcp_instance_name"]
  startup_script  = var.startup_script
  ssh_user        = var.ssh_user
}
```

## To SSH into your VM:

```
ssh -i "./keys/<instance_name>.pem" terraform@<external_ip>
```

## 📁 Project Structure

```
.
├── main.tf
├── variables.tf
├── outputs.tf
├── README.md
├── keys/
│   └── <instance>.pem
├── scripts/
│   └── gcp-user-data.sh
```

## ✅ Requirements
	•	Terraform ≥ 1.3
	•	GCP Project with Compute Engine API enabled
	•	Service account with Compute Admin, Service Account User roles

## 👨‍💻 Maintainer

This module is maintained by [Igor Racic].
