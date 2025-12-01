from locust import HttpUser, between, task, constant, events, constant_throughput
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
    def __init__ (self, name, json_file, func_create_cmds, input_files):
        self.name = name
        self.json_file = json_file
        self.func_create_cmds = func_create_cmds
        self.inputs = self.load_input_files(input_files)
        self.__next_input = 0

    def load_input_files (self, input_files):
        inputs = []

        for f in input_files:
            with open(f, "r") as jsonf:
                inputs.append(jsonf.read())
        print(inputs) # TODO
        return inputs

    def create(self, serverledge_cli, serverledge_host, serverledge_port):
        base_cmd = f"{serverledge_cli} -H {serverledge_host} -P {serverledge_port} "

        for create_cmd in self.func_create_cmds:
            cmd = base_cmd + create_cmd 
            output = subprocess.check_output(cmd, shell=True)
            print(output)

        cmd = base_cmd + f"create-workflow -s {self.json_file} -f {self.name}"
        try:
            output = subprocess.check_output(cmd, shell=True)
            print(output)
        except:
            pass

    def get_next_input (self):
        f = self.inputs[self.__next_input]
        self.__next_input = (self.__next_input + 1) % len(self.inputs)
        return f

#
# WEATHER APP
#
cmds = []

cmds.append("create -u -f weather --memory 500 --runtime custom --custom_image grussorusso/weatherfunc --input gemini_api_key:Text --input latitude:Float --input longitude:Float --output gemini_api_key:Text --output current_temperature:Float --output daily_rain_sum:ArrayFloat --output daily_max_temp:ArrayFloat --output daily_min_temp:ArrayFloat" )

cmds.append("create -u -f adapter --memory 200 --runtime python310 --handler adapter.handler --src src/weather/adapter.py  --input gemini_api_key:Text --input current_temperature:Float --input daily_rain_sum:ArrayFloat --input daily_max_temp:ArrayFloat --input daily_min_temp:ArrayFloat --output prompt:Text --output gemini_api_key:Text")

cmds.append("create -u -f gemini --memory 500 --runtime custom --custom_image grussorusso/geminifunc --input gemini_api_key:Text --input prompt:Text --output response:Text")

WORKFLOW_DATA.append(WorkflowData("weatherApp", "src/weather/weather.json", cmds, ["input/weather1.json"]))

class ResponseLogger:
    """Thread-safe response logger with periodic flushing"""
    
    def __init__(self, output_dir='responses', flush_interval=10, batch_size=100):
        """
        Args:
            output_dir: Directory to store response files
            flush_interval: Seconds between automatic flushes
            batch_size: Number of responses to accumulate before flushing
        """
        self.output_dir = output_dir
        self.flush_interval = flush_interval
        self.batch_size = batch_size
        self.responses_buffer = []
        self.lock = Lock()
        self.file_counter = 0
        self.flush_thread = None
        self.running = False
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
    
    def start(self):
        """Start the periodic flush thread"""
        self.running = True
        self.flush_thread = Thread(target=self._periodic_flush, daemon=True)
        self.flush_thread.start()
    
    def stop(self):
        """Stop the flush thread and flush remaining data"""
        self.running = False
        if self.flush_thread:
            self.flush_thread.join(timeout=5)
        self.flush_to_file()
    
    def _periodic_flush(self):
        """Background thread that flushes data periodically"""
        while self.running:
            time.sleep(self.flush_interval)
            self.flush_to_file()
    
    def add_response(self, response_data):
        """Add a response to the buffer (thread-safe)"""
        with self.lock:
            self.responses_buffer.append(response_data)
            
            # Flush if batch size reached
            if len(self.responses_buffer) >= self.batch_size:
                self._flush_unlocked()
    
    def flush_to_file(self):
        """Flush buffer to file (thread-safe)"""
        with self.lock:
            self._flush_unlocked()
    
    def _flush_unlocked(self):
        """Internal flush method (must be called with lock held)"""
        if not self.responses_buffer:
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(
            self.output_dir, 
            f'responses_{timestamp}_{self.file_counter}.jsonl'
        )
        
        try:
            # Write as JSON Lines format (one JSON object per line)
            with open(filename, 'w') as f:
                for response in self.responses_buffer:
                    f.write(json.dumps(response) + '\n')
            
            print(f"Flushed {len(self.responses_buffer)} responses to {filename}")
            
            # Clear buffer and increment counter
            self.responses_buffer.clear()
            self.file_counter += 1
            
        except Exception as e:
            print(f"Error flushing responses to file: {e}")


# Create global logger instance
response_logger = ResponseLogger(
    output_dir='responses',
    flush_interval=20,  # Flush every 10 seconds
    batch_size=100      # Or when 100 responses accumulated
)

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    if response_logger is not None:
        response_logger.start()

    serverledge_host = environment.host.replace("http://","")
    serverledge_host, serverledge_port = serverledge_host.split(":")

    # Create workflows
    print(f"Creating {len(WORKFLOW_DATA)} workflows...")
    for workflow in WORKFLOW_DATA:
        workflow.create("serverledge/serverledge-cli", serverledge_host, serverledge_port)


class MyUser(HttpUser):
    #wait_time = between(0.1,0.2)
    #wait_time = constant_throughput(5)

    @task
    def index(self):
        workflow = random.choice(WORKFLOW_DATA)
        input = workflow.get_next_input()

        self.client.post(f"/workflow/invoke/{workflow.name}", data=input, headers={'content-type': 'application/json'})

    def on_stop(self):
        global response_logger
        if response_logger is not None:
            response_logger.stop()

    @events.request.add_listener
    def my_request_handler(request_type, name, response_time, response_length, response,
            context, exception, start_time, url, **kwargs):
        global response_logger
        if not exception:
            response_logger.add_response(response.text)
