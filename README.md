This repository contains scripts and utilities to easily deploy a Serverledge
cluster. We currently provide scripts to reproduce the following configuration:

- AWS-based infrastructure 
- 1+ Edge node in a given AWS region
- 2+ Cloud nodes in a given AWS region
- 1 Load Balancer deployed in one of the Cloud nodes
- 1 Etcd server deployed in one of the Cloud nodes

We use Terraform for infrastructure configuration on AWS and Ansible for automated
deployment.

## Infrastructure Setup on AWS

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

As Serverledge is currently under development, we deploy locally built binaries.
To this end, provide the local path to Serverledge binaries in `localvars.yml`:

	---
	serverledge_local_bin_dir: /path/to/serverledge/bin

Run the playbook:

	make

Run a simple check:

	make check
