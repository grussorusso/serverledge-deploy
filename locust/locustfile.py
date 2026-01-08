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

@events.quitting.add_listener
def _(environment, **kw):
    if environment.stats.total.fail_ratio > 0.5:
        logging.error("Test failed due to failure ratio > 50%")
        environment.process_exit_code = 1
    else:
        environment.process_exit_code = 0

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
