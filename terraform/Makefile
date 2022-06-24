VARFILE="vars.tfvars"

tf:
	terraform apply -var-file=$(VARFILE)

destroy:
	terraform destroy -var-file=$(VARFILE)

.PHONY: tf destroy 
