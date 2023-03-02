import numpy as np
import tarfile
import json
import pandas as pd
import sys
import os
import re

ANALYZE_RESPONSES=True
results = []

DIR=sys.argv[1] if len(sys.argv) > 1 else "."


for entry in os.listdir(DIR):
    m = re.match("results-(\d+).csv", entry)
    if m is None:
        continue
    users = int(m.groups()[0])
    df = pd.read_csv(os.path.join(DIR,entry))

    experiment_time = (df.timeStamp.max()-df.timeStamp.min())/1000.0
    completed = df[df.responseCode==200]
    completed_count = completed.responseCode.count()
    avg_rt = completed.elapsed.mean()/1000.0
    tput = completed_count/experiment_time
    arrivalRate = df.responseCode.count()/experiment_time
    results.append({"users":users,
        "arrivalRate": arrivalRate,
        "throughput": tput,
        "avgRespTime": avg_rt,
        "duration": experiment_time})
df = pd.DataFrame(results)

results_responses = []
if ANALYZE_RESPONSES:
    for entry in os.listdir(DIR):
        m = re.match("responses-(\d+).tar.gz", entry)
        if m is None:
            continue
        users = int(m.groups()[0])
        tar = tarfile.open(os.path.join(DIR,entry), "r:gz")
        resp_times = []
        serv_times = []

        for member in tar.getmembers():
            f = tar.extractfile(member)
            if f is not None:
                content = f.read().decode("utf-8").strip()
                if len(content) == 0:
                    continue
                d = json.loads(content)
                resp_times.append(float(d["ResponseTime"]))
                serv_times.append(float(d["Duration"]))
        results_responses.append({"users": users,
            "avgInternalRespTime": np.mean(resp_times),
            "avgServiceTime": np.mean(serv_times)})
    df = pd.merge(df,pd.DataFrame(results_responses))


print(df.sort_values("users"))
