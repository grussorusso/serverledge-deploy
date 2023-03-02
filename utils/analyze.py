import pandas as pd
import re
import os
import sys
import tarfile
import json

DIR=sys.argv[1] if len(sys.argv) > 1 else "."

for entry in os.listdir(DIR):
    m = re.match("responses-(\d+).tar.gz", entry)
    if m is None:
        continue
    users = int(m.groups()[0])
    tar = tarfile.open(os.path.join(DIR,entry), "r:gz")

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


