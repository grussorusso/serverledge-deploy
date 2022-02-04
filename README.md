## Deploying Etcd and Serverledge from locally built binaries

Provide the local path to Serverledge binaries in, e.g., `localvars.yml`:

	---
	serverledge_local_bin_dir: /path/to/serverledge/bin

Run the playbook:

	ansible-playbook -i <INVENTORY> --extra-vars "@localvars.yml" site.yml

## Stopping Serverledge service

	ansible-playbook -i <INVENTORY> stop.yml
