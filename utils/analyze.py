import pandas as pd
import os
import sys
import tarfile
import json

DIR=sys.argv[1] if len(sys.argv) > 1 else "."

for users in range(1,100):
    try:
        tar = tarfile.open(os.path.join(DIR,f"responses-{users}.tar.gz"), "r:gz")
    except FileNotFoundError:
        continue
    with open(os.path.join(DIR,f"processedResults-{users}.csv"), "w") as of:
        print("NodeResponseTime,ContainerInitTime,Duration", file=of)
        for member in tar.getmembers():
            f = tar.extractfile(member)
            if f is not None:
                content = f.read().decode("utf-8").strip()
                if len(content) == 0:
                    continue
                d = json.loads(content)
                print(f'{d["ResponseTime"]:.5f},{d["InitTime"]:.5f},{d["Duration"]:.5f}', file=of)


