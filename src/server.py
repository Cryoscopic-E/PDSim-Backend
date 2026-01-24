import zmq
import threading
import logging
from typing import Optional, Union, Callable
from unified_planning.model import Problem
from unified_planning.plans import Plan
from unified_planning.engines import PlanGenerationResult

from request_handlers import RequestHandler
from pdsim_problem import PdSimProblem

class PdSimUnityServer:
    def __init__(self, problem_model: PdSimProblem, plan_result: Union[PlanGenerationResult, Plan], host: str, port: str, 
                 planner_name: Optional[str] = None, 
                 solve_callback: Optional[Callable[[Problem, str], PlanGenerationResult]] = None,
                 stop_event: Optional[threading.Event] = None,
                 logger: Optional[logging.Logger] = None):
        self.host = host
        self.port = port
        self.problem = problem_model
        self.planner_name = planner_name
        self.solve_callback = solve_callback
        self.stop_event = stop_event
        
        # Setup Logger
        self.logger = logger if logger else logging.getLogger("PdSimServer")
        if not self.logger.handlers:
             logging.basicConfig(level=logging.INFO)

        # Handle both PlanGenerationResult (from planner) and Plan (loaded from file)
        if isinstance(plan_result, PlanGenerationResult):
            self.plan_result = plan_result
        else:
             self.plan_result = plan_result
        
        # Initialize the request handler logic
        self.handler = RequestHandler(self)
        
        self.request_handlers = {
            'ping': self.handler.handle_ping,
            'problem': self.handler.handle_get_problem,
            'plan': self.handler.handle_get_plan,
            'new_object': self.handler.handle_new_object,
            'set_initial_value': self.handler.handle_set_initial_value,
            'add_goal': self.handler.handle_add_goal,
            'replan': self.handler.handle_replan
        }

    def info(self) -> None:
        self.logger.info("####################################")
        self.logger.info("#####       PDSim Server       #####")
        self.logger.info("####################################")
        self.logger.info(f"--- Listening on {self.host}:{self.port} ---")
        self.logger.info("####################################")

    def server_loop(self) -> None:
        context = zmq.Context()
        socket: zmq.Socket = context.socket(zmq.REP)
        try:
            socket.bind('tcp://{}:{}'.format(self.host, self.port))
        except zmq.ZMQError as e:
            self.logger.error(f"Failed to bind port {self.port}: {e}")
            return

        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)
        
        self.info()

        while True:
            # Check stop event
            if self.stop_event and self.stop_event.is_set():
                self.logger.info("Stop event received. Shutting down server...")
                break

            try:
                # Poll for 100ms
                socks = dict(poller.poll(100))
                
                if socket in socks and socks[socket] == zmq.POLLIN:
                    request = socket.recv_json()
                    req_type = request.get('request')
                    data = request.get('data', {})
                    
                    if req_type in self.request_handlers:
                        # self.logger.info(f"Handling request: {req_type}") # Optional: verbose logging
                        response = self.request_handlers[req_type](data)
                        
                        if isinstance(response, bytes):
                            socket.send(response)
                        else:
                            socket.send_json(response)
                    else:
                        self.logger.warning(f"Unknown request: {request}")
                        socket.send_json({'error': 'Unknown request'})
                
            except zmq.ZMQError as e:
                self.logger.error(f"ZMQ Error: {e}")
                break
            except Exception as e:
                self.logger.error(f"Server Error: {e}")
                # Don't break on general application errors, try to continue
        
        # Cleanup
        socket.close()
        context.term()
        self.logger.info("Server stopped.")