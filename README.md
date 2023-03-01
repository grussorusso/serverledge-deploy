This repository contains scripts and utilities to automate the deployment of
[Serverledge](https://github.com/grussorusso/serverledge).

The repository mostly consists of Ansible playbooks and roles, which can be
used to deploy Serverledge over existing hosts.
In addition, we also provide Terraform scripts in the `terraform` directory,
which can be used to provision a set of Amazon EC2 instances.

Currently, we only support deployment to Debian-based Linux distributions
or to Amazon Linux 2.

**Important note**: while sensible defaults are used for most the variables,
you should check and customize the scripts we provide before using them.

## Requirements

Install the following Ansible role, which is used to configure Docker:

	ansible-galaxy install geerlingguy.docker

## Infrastructure Setup on AWS

We currently provide scripts to reproduce the following configuration:

- AWS-based infrastructure 
- 1+ Edge node(s) in a given AWS region
- 1+ Cloud node(s) in a given AWS region
- 1 Load Balancer deployed in one of the Cloud nodes
- 1 Etcd server deployed in one of the Cloud nodes
- *(Optional)* 1 Client node deployed alongside the Edge node(s)

We assume that the AWS CLI/SDK has already been configured with the required
credentials on the machine.

Enter the `terraform/` directory and run `terraform init`.

Edit the file `vars.tfvars` as needed. Use this file to define how many 
Edge/Cloud/Client nodes you desire.

Configure the infrastructure:

	make tf

When you are done, clean up:

	make destroy

## Ansible

### Inventory

Create an Ansible inventory file (default path is `inventory/default.ini`).

If you provisioned the infrastructure in EC2, you can also use
`inventory.aws_ec2.yaml` that allows Ansible to
dynamically retrieve information about our EC2 instances.
Update `inventory.aws_ec2.yaml` (if needed) to set the regions where EC2
instances have been launched.

You can check that everything works by running:

	ansible-inventory -i <inventory_file> --list


### Deployment

As Serverledge is currently under development, we deploy locally built binaries.
To this end, you must provide the local path to Serverledge binaries 
updating the `serverledge_local_bin_dir` variable (either modifying the relevant
file or providing Ansible  "local vars").

Run the playbook:

	ansible-playbook [-i <inventory_file>] deploy_serverledge.yml

Run a simple check to verify that the cluster is up:

	ansible-playbook [-i <inventory_file>] check.yml

### Benchmarking with JMeter

	ansible-playbook [-i <inventory_file>] run_experiment.yml
