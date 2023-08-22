# XXX
/home/gabriele/utils/fix_cpu_freq
# XXX

EXP_TAG="prova"
RESULTS_DIR="results_${EXP_TAG}"

[[ -d $RESULTS_DIR ]] || mkdir -p $RESULTS_DIR 

ansible-playbook deploy_serverledge.yml

for users in 1 5; do
	sleep 30
	ansible-playbook -vv -e "users=${users}" \
		-e "local_results_file=${RESULTS_DIR}/results-$users.csv"\
		-e "local_responses_file=${RESULTS_DIR}/responses-$users.tar.gz"\
		-e "local_output_dir=${RESULTS_DIR}/"\
		run_experiment.yml 
done

# XXX
/home/gabriele/utils/reset_cpu_freq
# XXX
