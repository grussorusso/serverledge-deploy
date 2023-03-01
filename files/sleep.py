import time 

def handler(params, context):
    try:
        n = float(params["n"])
    except:
        n = 0.150
    time.sleep(n)
    return {}
