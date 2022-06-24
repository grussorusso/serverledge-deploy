
## Infrastructure Setup on AWS

You can use Terraform to easily configure the required infrastructure on AWS.
We assume that the AWS CLI/SDK has already been configured with the required
credentials on the machine.

Enter the `terraform/` directory and run `terraform init`.

Edit the file `vars.tfvars` as needed. 

Configure the infrastructure:

	make tf

When you are done, clean up:

	make destroy

## Ansible Deployment

### Inventory

The repository contains `inventory.aws_ec2.yaml` that allows Ansible to
dynamically retrieve information about our EC2 instances.

Update `inventory.aws_ec2.yaml` (if needed) to set the regions where EC2
instances have been launched.

You can check that everything works by running:

	ansible-inventory -i inventory.aws_ec2.yaml --list

### Deploying Serverledge

To install Docker:

	ansible-galaxy install geerlingguy.docker

## Deploying Etcd and Serverledge from locally built binaries

Provide the local path to Serverledge binaries in, e.g., `localvars.yml`:

	---
	serverledge_local_bin_dir: /path/to/serverledge/bin

Run the playbook:

	ansible-playbook -i <INVENTORY> --extra-vars "@localvars.yml" site.yml

## Stopping Serverledge service

	ansible-playbook -i <INVENTORY> stop.yml
