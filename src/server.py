import zmq
import signal
import time
from typing import Optional, Union, Callable
from unified_planning.model import Problem
from unified_planning.plans import Plan
from unified_planning.engines import PlanGenerationResult

from request_handlers import RequestHandler
from pdsim_problem import PdSimProblem

class PdSimUnityServer:
    def __init__(self, problem_model: PdSimProblem, plan_result: Union[PlanGenerationResult, Plan], host: str, port: str, 
                 planner_name: Optional[str] = None, 
                 solve_callback: Optional[Callable[[Problem, str], PlanGenerationResult]] = None):
        self.host = host
        self.port = port
        self.problem = problem_model
        self.planner_name = planner_name
        self.solve_callback = solve_callback
        
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
        print("####################################")
        print("#####       PDSim Server       #####")
        print("####################################")
        print(f"--- Listening on {self.host}:{self.port} ---")
        print("####################################")

    def server_loop(self) -> None:
        context = zmq.Context()
        socket: zmq.Socket = context.socket(zmq.REP)
        socket.bind('tcp://{}:{}'.format(self.host, self.port))
        
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        
        self.info()

        while True:
            try:
                request = socket.recv_json()
                req_type = request.get('request')
                data = request.get('data', {})
                
                if req_type in self.request_handlers:
                    response = self.request_handlers[req_type](data)
                    # Handle both JSON and raw bytes (for protobuf) responses
                    if isinstance(response, bytes):
                        socket.send(response)
                    else:
                        socket.send_json(response)
                else:
                    print(f"Unknown request: {request}")
                    socket.send_json({'error': 'Unknown request'})
                    
                time.sleep(0.1)
            except zmq.ZMQError as e:
                print(f"ZMQ Error: {e}")
                break
            except Exception as e:
                print(f"Server Error: {e}")