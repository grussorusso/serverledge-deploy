
Deploy Serverledge:

	ansible-playbook [-i <inventory_file>] deploy_serverledge.yml
	ansible-playbook [-i <inventory_file>] create_functions_and_workflows.yml

	ansible-playbook [-i <inventory_file>] profile_workflows.yml

### Benchmarking with Locust

	ansible-playbook [-i <inventory_file>] run_experiment.yml
