import threading
import logging
import logging.handlers
import queue
import time
from typing import Optional, Any, Callable, List
from unified_planning.model import Problem
from unified_planning.engines import PlanGenerationResult

from planning import launch_server

class ServerManager:
    def __init__(self, host: str = '0.0.0.0', port: str = '5556'):
        self.host = host
        self.port = port
        self.server_thread: Optional[threading.Thread] = None
        self.stop_event: Optional[threading.Event] = None
        self.log_queue = queue.Queue()
        self.logger = logging.getLogger("PdSimServerManager")
        self.logger.setLevel(logging.INFO)
        
        # Configure logger to write to queue
        queue_handler = logging.handlers.QueueHandler(self.log_queue)
        self.logger.addHandler(queue_handler)
        
        # State tracking
        self.current_domain: str = "None"
        self.current_problem: str = "None"
        self.current_planner: str = "None"
        self.active_problem: Optional[Problem] = None
        self.active_result: Any = None
        self.is_running = False

    def start_server(self, problem: Problem, result: Any, planner_name: Optional[str] = None, 
                     solve_callback: Optional[Callable] = None,
                     domain_name: str = "Unknown", problem_name: str = "Unknown"):
        
        if self.is_running:
            self.stop_server()
            
        self.stop_event = threading.Event()
        self.current_domain = domain_name
        self.current_problem = problem_name
        self.current_planner = planner_name if planner_name else "N/A"
        self.active_problem = problem
        self.active_result = result
        
        # We need to use a wrapper to run launch_server because it expects arguments
        def thread_target():
            # We instantiate the server directly here or use launch_server. 
            # Using launch_server is easier but we need to pass the logger and stop_event.
            try:
                launch_server(problem, result, self.host, self.port, 
                              planner_name=planner_name, 
                              solve_callback=solve_callback, 
                              stop_event=self.stop_event,
                              logger=self.logger)
            except Exception as e:
                self.logger.error(f"Server thread crashed: {e}")
            finally:
                self.is_running = False
        
        self.server_thread = threading.Thread(target=thread_target, daemon=True)
        self.server_thread.start()
        self.is_running = True
        self.logger.info(f"Server started on {self.host}:{self.port}")

    def stop_server(self):
        if self.server_thread and self.server_thread.is_alive():
            self.logger.info("Stopping server...")
            if self.stop_event:
                self.stop_event.set()
            
            self.server_thread.join(timeout=5)
            if self.server_thread.is_alive():
                self.logger.error("Server thread did not exit cleanly.")
            else:
                self.logger.info("Server stopped.")
        
        self.is_running = False
        self.server_thread = None
        self.stop_event = None
        self.current_domain = "None"
        self.current_problem = "None"
        self.current_planner = "None"
        self.active_problem = None
        self.active_result = None

    def get_status(self) -> dict:
        return {
            "status": "Running" if self.is_running else "Stopped",
            "host": self.host,
            "port": self.port,
            "domain": self.current_domain,
            "problem": self.current_problem,
            "planner": self.current_planner
        }

    def drain_logs(self) -> List[str]:
        logs = []
        while not self.log_queue.empty():
            try:
                record = self.log_queue.get_nowait()
                msg = self.logger.handlers[0].format(record) if self.logger.handlers else record.msg
                # Simple formatting if handler format fails or isn't set up fully for queue
                if isinstance(record, logging.LogRecord):
                    msg = f"[{record.levelname}] {record.getMessage()}"
                logs.append(msg)
            except queue.Empty:
                break
        return logs
