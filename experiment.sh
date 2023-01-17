RESULTS_DIR="results_cpu05"

[[ -d $RESULTS_DIR ]] || mkdir -p $RESULTS_DIR 

for users in $(seq 73 2 85); do
	make restart-serverledge
	sleep 5
	ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -v -i inventory.aws_ec2.yaml \
		-u ec2-user --extra-vars "@local_vars.yml" -e "users=${users}" jmeter-benchmark.yml 

	# move results
	mv jmeter_results.csv ${RESULTS_DIR}/results-$users.csv
	mv jmeter_responses.tar.gz ${RESULTS_DIR}/responses-$users.tar.gz
done
