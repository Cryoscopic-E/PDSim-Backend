import threading
import zmq
import signal
import time

from unified_planning.io.pddl_reader import PDDLReader
from unified_planning.model import Problem
from unified_planning.environment import get_environment
from unified_planning.engines import PlanGenerationResultStatus
from unified_planning.shortcuts import OneshotPlanner, get_all_applicable_engines
from unified_planning.grpc.proto_writer import ProtobufWriter


class PdSimUnityServer:
    def __init__(self, host='localhost', port='5556', problem=None, plan=None):
        self.host = host
        self.port = port
        self.pddl_reader = PDDLReader()
        self.proto_writer = ProtobufWriter()

        self.planner = None
        self.planner_running = False

        self.plan = None
        self.plan_result_computed = False

        if problem is not None:
            self.active_problem = problem
        else:
            self.active_problem = None
        self.main_thread = threading.Thread(target=self.server_loop)

    def info(self):
        print("--------------------")
        print("--- PDSim Server ---")
        print("--------------------")
        print(f"Listening on {self.host}:{self.port}")

    def clear_problem(self) -> None:
        self.active_problem = None

    def parse_problem(self, domain_path, problem_path):
        if self.active_problem is not None:
            self.clear_problem()
        try:
            self.active_problem = self.pddl_reader.parse_problem(domain_path, problem_path)
        except Exception as e:
            print(e)
            return {'status': 'ERROR', 'msg': str(e)}
        return {'status': 'OK', 'msg': 'Problem parsed successfully'}

    def get_problem(self) -> Problem:
        return self.active_problem

    def convert_to_protobuf(self):
        if self.active_problem is None:
            return ''
        try:
            parse = self.proto_writer.convert(self.active_problem)
        except Exception as e:
            print(e)
            return {'status': 'ERROR', 'msg': 'Could not convert to protobuf'}
        return {'status': 'OK', 'msg': 'Problem converted successfully', 'data': parse.SerializeToString()}

    def set_planner(self, planner_name):
        if self.active_problem is None:
            return
        self.planner = OneshotPlanner(name=planner_name, problem_kind=self.active_problem)

    def get_planners(self):
        if self.active_problem is None:
            return []
        return get_all_applicable_engines(self.active_problem)

    def server_loop(self):
        context = zmq.Context()
        socket: zmq.Socket = context.socket(zmq.REP)
        socket.bind('tcp://{}:{}'.format(self.host, self.port))
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.info()

        while True:
            request = socket.recv_json()
            if request['request'] == 'pddl':
                self.clear_problem()

                domain_path = request['domain_path']
                problem_path = request['problem_path']

                parse_result = self.parse_problem(domain_path, problem_path)

                pass
            elif request['request'] == 'protobuf':
                self.clear_problem()
                # check if a protobuf representation exists
                pass
            elif request['request'] == 'planner_status':
                if self.planner is None:
                    socket.send_json({'status': 'ERROR', 'msg': 'No planner selected'})
                elif self.planner_running:
                    socket.send_json({'status': 'OK', 'msg': 'Planner is running'})
                else:
                    socket.send_json({'status': 'OK', 'msg': 'Planner is not running'})
            else:
                print("Unknown request")

            time.sleep(0.1)

    def planner_loop(self):
        if self.planner is None:
            return
        self.planner_running = True
        self.plan_result_computed = False
        self.plan = self.planner.solve()
        self.planner_running = False
        self.plan_result_computed = True

