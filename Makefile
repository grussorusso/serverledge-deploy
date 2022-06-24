ANS_FLAGS=--extra-vars "@local_vars.yml"

all:
	ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i inventory.aws_ec2.yaml -u ec2-user $(ANS_FLAGS) site.yml
check:
	ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -v -i inventory.aws_ec2.yaml -u ec2-user $(ANS_FLAGS) check.yml

