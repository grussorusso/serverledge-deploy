import sys
from os import listdir
from os.path import isfile, join
import json
import requests
import argparse


def profile_workflow (workflow_json, endpoints, payloads_directory, n=10):
    functions = set()

    with open(workflow_json, "r") as aslfile:
        asl = json.loads(aslfile.read())

    for _,state in asl["States"].items():
        if state["Type"] == "Task":
            functions.add(state["Resource"])


    for fun in functions:
        # parsa JSON di input
        payloads = []
        input_directory = join(payloads_directory, fun)
        input_files = [f for f in listdir(input_directory) if isfile(join(input_directory, f))]
        for f in input_files:
            with open(join(input_directory, f), "r") as jsonf:
                payloads.append(json.loads(jsonf.read()))

        if len(payloads) < 1:
            print(f"Skipping function {fun}: no input data available")
            continue

        # TODO: in parallelo su ogni endpoint (i.e., edge e cloud)
        for endpoint in endpoints:
            print(f"Sending {n} requests to {endpoint}")
            for i in range(n):
                payload = payloads[i % len(payloads)]
                data = {
                    "Params": payload,
                    "CanDoOffloading": False
                }
                url = endpoint + "/invoke/" + fun
                response = requests.post(url, json=data)

                if response.status_code != 200:
                    print(f"Failed req to {fun}, endpoint={endpoint}, status={response.status_code}")

parser = argparse.ArgumentParser()
parser.add_argument('-w','--workflows', nargs='+', help='JSON files', required=True, default=[])
parser.add_argument('-e','--endpoints', nargs='+', help='http://HOST:PORT', required=False, default=["http://127.0.0.1:1323"])
parser.add_argument('-i','--input_directory', action="store", required=True, default='./saved-inputs')
parser.add_argument('-n','--nrequests', action="store", type=int, required=False, default=10)

cli_args = parser.parse_args()

print(f"Searching for input JSON files in {cli_args.input_directory}")

# JSON files are passed
# Workflows are already registered in Serverledge
workflows = cli_args.workflows

print(workflows)

for w in workflows:
    print(f"Profiling {w}")
    profile_workflow(w, cli_args.endpoints, cli_args.input_directory, cli_args.nrequests)
