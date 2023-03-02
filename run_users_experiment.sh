RESULTS_DIR="results_nero_cap3"

[[ -d $RESULTS_DIR ]] || mkdir -p $RESULTS_DIR 

ansible-playbook deploy_serverledge.yml

#for users in $(seq 17 2 71); do
#for users in 1 5 10 20 30 40 50; do
#for users in 60 80 100 120 140; do
#for users in 140 150 170 180; do
#for users in 200 220 240; do
for users in 320 340 360 380 400 420; do
	ansible-playbook -vv -e "users=${users}" \
		-e "local_results_file=${RESULTS_DIR}/results-$users.csv"\
		-e "local_responses_file=${RESULTS_DIR}/responses-$users.tar.gz"\
		run_experiment.yml 
done
