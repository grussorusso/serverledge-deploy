from locust import HttpUser, between, task, constant, events, constant_throughput
import logging
import re
import locust.stats
import random
import time
import json
import subprocess
import os
from datetime import datetime
from threading import Lock, Thread

locust.stats.PERCENTILES_TO_REPORT = [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]

WORKFLOW_DATA = []

class WorkflowData:
    def __init__ (self, name, input_files):
        self.name = name
        self.inputs = self.load_input_files(input_files)
        self.__next_input = 0

    def load_input_files (self, input_files):
        inputs = []

        for f in input_files:
            with open(f, "r") as jsonf:
                inputs.append(jsonf.read())
        return inputs

    def get_next_input (self):
        f = self.inputs[self.__next_input]
        self.__next_input = (self.__next_input + 1) % len(self.inputs)
        return f

WORKFLOW_DATA.append(WorkflowData("weatherApp", [f"input/weather{i}.json" for i in [1,2,3]]))
WORKFLOW_DATA.append(WorkflowData("sentimentAnalysis", [f"input/sentiment{i}.json" for i in [1,2,3]]))
WORKFLOW_DATA.append(WorkflowData("personDetection", [f"input/personDetection1.json" for i in [1,2,3]]))


class ResponseLogger:
    """Thread-safe response logger with periodic flushing"""
    
    def __init__(self, output_file):
        """
        Args:
            output_dir: Directory to store response files
        """
        self.output_file = output_file
        self.responses_buffer = []
        self.lock = Lock()
        self.running = False
    
    def start(self):
        """Start the periodic flush thread"""
        self.running = True
    
    def stop(self):
        """Stop the flush thread and flush remaining data"""
        self.running = False
        self.flush_to_file()
    
    def add_response(self, url, response_time, status_code, jsonresp):
        """Add a response to the buffer (thread-safe)"""
        with self.lock:
            total_init = 0
            total_duration = 0
            func_area = []
            func_node = []
            func_warm = []
            func_duration = []
            try:
                reports = jsonresp["Reports"]
                for func, freport in reports.items():
                    func_area.append(f"{func}:{freport['ExecutionArea']}")
                    func_node.append(f"{func}:{freport['ExecutionNode']}")
                    func_warm.append(f"{func}:{freport['IsWarmStart']}")
                    duration = float(freport['Duration'])
                    init_time = float(freport['InitTime'])-float(freport['QueueingTime'])
                    func_duration.append(f"{func}:{duration+init_time}")
                    total_init += float(freport['InitTime'])
                    total_duration += duration
            except:
                pass
            areastr = "|".join(func_area)
            nodestr = "|".join(func_node)
            warmstr = "|".join(func_warm)
            durationstr = "|".join([str(x) for x in func_duration])

            try:
                scheduling_time = float(jsonresp["SchedulingTime"])
            except:
                scheduling_time = -1

            entry = f"{status_code}; {response_time}; {url}; {areastr}; {nodestr}; {warmstr}; {total_init}; {total_duration}; {durationstr}; {scheduling_time}"
            self.responses_buffer.append(entry)
    
    def flush_to_file(self):
        """Flush buffer to file (thread-safe)"""
        with self.lock:
            self._flush_unlocked()
    
    def _flush_unlocked(self):
        """Internal flush method (must be called with lock held)"""
        if not self.responses_buffer:
            return
        
        try:
            with open(self.output_file, 'w') as f:
                for response in self.responses_buffer:
                    f.write(f"{response}\n")
            
            print(f"Flushed {len(self.responses_buffer)} responses to {self.output_file}")
            
        except Exception as e:
            print(f"Error flushing responses to file: {e}")


# Create global logger instance
response_logger = ResponseLogger(
    output_file='response_times.txt',
)

@events.test_start.add_listener
def on_locust_init(environment, **kwargs):
    print("Starting test...")
    response_logger.start()

    serverledge_host = environment.host.replace("http://","")
    serverledge_host, serverledge_port = serverledge_host.split(":")

@events.test_stop.add_listener
def stop_handler(environment, **kw):
    print("Stopping test...")
    response_logger.stop()

    if environment.stats.total.fail_ratio > 0.9:
        logging.error("Test failed due to failure ratio > 90%")
        environment.process_exit_code = 1
    else:
        environment.process_exit_code = 0

class MyUser(HttpUser):
    #wait_time = between(0.1,0.2)
    wait_time = constant_throughput(1)

    @task
    def index(self):
        workflow = random.choice(WORKFLOW_DATA)
        input = workflow.get_next_input()
        #input["CanDoOffloading"] = True # MUST DESERIALIZE input str

        self.client.post(f"/workflow/invoke/{workflow.name}", data=input, headers={'content-type': 'application/json'}, timeout=60)

    @events.request.add_listener
    def my_request_handler(request_type, name, response_time, response_length, response,
            context, exception, start_time, url, **kwargs):
        global response_logger
        try:
            jsonresp = response.json()
        except:
            jsonresp = {}
        response_logger.add_response(url, response_time, response.status_code, jsonresp)
