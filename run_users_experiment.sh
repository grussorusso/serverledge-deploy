# XXX
/home/gabriele/utils/fix_cpu_freq
# XXX

RESULTS_DIR="results_nero_cap3_noturbo_fixfreq"

[[ -d $RESULTS_DIR ]] || mkdir -p $RESULTS_DIR 

ansible-playbook deploy_serverledge.yml

#for users in $(seq 17 2 71); do
for users in 1 5 10 15 20 25 30 40 50 60 70; do
#for users in 60 80 100 120 140; do
#for users in 140 150 170 180; do
#for users in 200 220 240; do
	ansible-playbook -vv -e "users=${users}" \
		-e "local_results_file=${RESULTS_DIR}/results-$users.csv"\
		-e "local_responses_file=${RESULTS_DIR}/responses-$users.tar.gz"\
		-e "local_output_dir=${RESULTS_DIR}/"\
		run_experiment.yml 
done

# XXX
/home/gabriele/utils/reset_cpu_freq
# XXX
