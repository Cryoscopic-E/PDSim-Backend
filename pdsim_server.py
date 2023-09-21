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

HOST = 'localhost'
PORT = 5556


def info(host, port):
    print("--------------------")
    print("--- PDSim Server ---")
    print("--------------------")
    print(f"Listening on {host}:{port}")


def check_planner_status():
    while True:
        global planner_finished
        if planner_finished:
            print("Planner has finished")
        else:
            print("Planner is still working...")
        time.sleep(5)  # Sleep for 5 seconds before checking again


class UnityServer:
    def __init__(self):
        self.pddl_reader = PDDLReader()
        self.proto_writer = ProtobufWriter()
        self.planner: OneshotPlanner = None
        self.active_problem = None

    def clear_problem(self) -> None:
        self.active_problem = None

    def parse_pddl(self, domain_path, problem_path) -> Problem:
        self.active_problem = self.pddl_reader.parse_problem(domain_path, problem_path)
        return self.active_problem

    def get_problem(self) -> Problem:
        return self.active_problem

    def convert_to_protobuf(self) -> str:
        if self.active_problem is None:
            return ''
        parse = self.proto_writer.convert(self.active_problem)
        return parse.SerializeToString()

    def set_planner(self, planner_name):
        if self.active_problem is None:
            return
        self.planner = OneshotPlanner(name=planner_name, problem_kind=self.active_problem)

    def get_planners(self):
        if self.active_problem is None:
            return []
        return get_all_applicable_engines(self.active_problem)

    def server_thread(self):
        context = zmq.Context()
        socket: zmq.Socket = context.socket(zmq.REP)
        socket.bind('tcp://{}:{}'.format(HOST, PORT))
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        info(HOST, PORT)

        while True:
            request = socket.recv_json()
            if request['request'] == 'pddl':
                # handle parse domain and problem and planning
                pass
            elif request['request'] == 'protobuf':
                # check if a protobuf representation exists
                pass
            elif request['request'] == 'planner':
                # check status of the planner
                pass
            else:
                print("Unknown request")

            time.sleep(0.1)


# Function to handle requests from Unity
def handle_unity_requests():
    context = zmq.Context()
    socket: zmq.Socket = context.socket(zmq.REP)
    socket.bind('tcp://{}:{}'.format(HOST, PORT))
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    info(HOST, PORT)

    while True:
        request = socket.recv_json()
        if request['request'] == 'pddl':
            # handle parse domain and problem and planning
            pass
        elif request['request'] == 'protobuf':
            # check if a protobuf representation exists
            pass
        elif request['request'] == 'planner':
            # check status of the planner
            pass
        else:
            print("Unknown request")

        time.sleep(0.1)


def pdsim_run_pddl(domain_path, problem_path):
    pddl_reader = PDDLReader()

    # Parse the domain and problem files
    problem = pddl_reader.parse_problem(domain_path, problem_path)


def pdsim_run_protobuf(data):
    # Create a PDDL reader
    pddl_reader = PDDLReader()

    # Parse the domain and problem files
    problem = pddl_reader.parse_problem('./pddl/rover-temporal.pddl', './pddl/rover-temporal-problem.pddl')

    # Get the environment
    env = get_environment(problem)

    # Get all applicable engines
    engines = get_all_applicable_engines()

    # Create a planner
    planner = OneshotPlanner(env, engines)

    # Run the planner
    result = planner.run()

    # Check the result
    if result.status == PlanGenerationResultStatus.SUCCESS:
        print("Success!")
        print(result.plan)
    elif result.status == PlanGenerationResultStatus.FAILURE:
        print("Failure!")
    elif result.status == PlanGenerationResultStatus.TIMEOUT:
        print("Timeout!")
    elif result.status == PlanGenerationResultStatus.ERROR:
        print("Error!")
    else:
        print("Unknown status!")


if __name__ == "__main__":
    # Create separate threads for checking planner status, handling Unity requests, and simulating planner work
    planner_thread = threading.Thread(target=check_planner_status)
    unity_thread = threading.Thread(target=handle_unity_requests)

    # Start the threads
    planner_thread.start()
    unity_thread.start()

    # Wait for the threads to finish (you can add a mechanism for graceful exit)
    planner_thread.join()
    unity_thread.join()
