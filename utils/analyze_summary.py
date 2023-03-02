import pandas as pd
import sys
import os
import re

print("Users,ArrivalRate,Throughput,AvgRT")

DIR=sys.argv[1] if len(sys.argv) > 1 else "."

results = []

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

    df = pd.DataFrame(results).sort_values("users")
print(df)
