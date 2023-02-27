import pandas as pd
import sys
import os

print("Users,ArrivalRate,Throughput,AvgRT")

DIR=sys.argv[1] if len(sys.argv) > 1 else "."

for users in range(1,100):
    try:
        df = pd.read_csv(os.path.join(DIR,f"results-{users}.csv"))
    except:
        continue
    experiment_time = (df.timeStamp.max()-df.timeStamp.min())/1000.0
    completed = df[df.responseCode==200]
    completed_count = completed.responseCode.count()
    avg_rt = completed.elapsed.mean()/1000.0
    tput = completed_count/experiment_time
    arrivalRate = df.responseCode.count()/experiment_time
    print(f"{users},{arrivalRate:.3f},{tput:.3f},{avg_rt:.3f}")

