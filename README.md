
This repository contains scripts and utilities to easily deploy a
[Serverledge](https://github.com/grussorusso/serverledge)
cluster. We currently provide scripts to reproduce the following configuration:

- AWS-based infrastructure 
- 1+ Edge node(s) in a given AWS region
- 1+ Cloud node(s) in a given AWS region
- 1 Load Balancer deployed in one of the Cloud nodes
- 1 Etcd server deployed in one of the Cloud nodes
- *(Optional)* 1 Client node deployed alongside the Edge node(s)

We use Terraform for infrastructure configuration on AWS and Ansible for automated
deployment.

You should properly customize the scripts we provide depending on your needs.

## Requirements

	ansible-galaxy collection install geerlingguy.docker
	ansible-galaxy collection install community.docker

## Infrastructure Setup on AWS

We assume that the AWS CLI/SDK has already been configured with the required
credentials on the machine.

Enter the `terraform/` directory and run `terraform init`.

Edit the file `vars.tfvars` as needed. Use this file to define how many 
Edge/Cloud/Client nodes you desire.

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

### Benchmarking with JMeter

Make sure to have provisioned 1 Client node in the infrastructure.

Customize `jmeter/testplan.jmx`.

Launch a benchmark:

	make jmeter
