import json

import zmq
import signal
import time
import argparse

from unified_planning.io.pddl_reader import PDDLReader
from unified_planning.model import Problem
from unified_planning.engines import PlanGenerationResult
from unified_planning.shortcuts import OneshotPlanner, get_all_applicable_engines
from unified_planning.grpc.proto_writer import ProtobufWriter


class PdSimUnityServer:
    def __init__(self, problem_model: Problem, plan_result: PlanGenerationResult, host, port):
        self.host = host
        self.port = port
        self.proto_writer = ProtobufWriter()
        self.problem = problem_model
        self.plan_result = plan_result

    def info(self):
        print("--------------------")
        print("--- PDSim Server ---")
        print("--------------------")
        print(f"Listening on {self.host}:{self.port}")

    def convert_to_protobuf(self, model):
        try:
            parse = self.proto_writer.convert(model)
        except Exception as exception:
            print(exception)
            return None
        return parse.SerializeToString()

    def server_loop(self):
        context = zmq.Context()
        socket: zmq.Socket = context.socket(zmq.REP)
        socket.bind('tcp://{}:{}'.format(self.host, self.port))
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.info()

        while True:
            request = socket.recv_json()
            if request['request'] == 'ping':
                socket.send_json(json.dumps({'status': 'OK'}))
            elif request['request'] == 'problem':
                converted_problem = self.convert_to_protobuf(self.problem)
                if converted_problem is not None:
                    socket.send(converted_problem)
            elif request['request'] == 'plan':
                print(self.plan_result)
                converted_plan = self.convert_to_protobuf(self.plan_result)
                if converted_plan is not None:
                    socket.send(converted_plan)
            else:
                print("Unknown request")
            time.sleep(0.1)


def usage():
    # host and port are optional
    print('''Usage: python 
                pdsim_unity.py --domain <domain_file> 
                                --problem <problem_file> 
                                [--planner <planner_name>]
                                [--host <host_address>] 
                                [--port <port>]
                                ''')


def select_planner(planners):
    print("Select planner:")
    for i, p in enumerate(planners):
        print(f"{i}. {p}")
    print("Enter number:")
    while True:
        try:
            planner_index = int(input())
            if planner_index < 0 or planner_index >= len(planners):
                raise ValueError
            break
        except ValueError:
            print("Invalid input, try again")
    return planners[planner_index]


def solve_problem(problem, planner_name):
    applicable_planners = get_all_applicable_engines(problem.kind)
    if len(applicable_planners) == 0:
        print(f"No planners applicable to problem {problem.kind}")
        exit(1)
    if planner_name not in applicable_planners:
        print(f"Planner {planner_name} not applicable to problem {problem.kind}")
        if len(applicable_planners) == 1:
            planner_name = applicable_planners[0]
            print(f"Using {applicable_planners[0]}")
        else:
            planner_name = select_planner(applicable_planners)
            print(f"Using {planner_name}")
    planner = OneshotPlanner(name=planner_name)
    return planner.solve(problem)


def launch_server(problem, result, host, port):
    server = PdSimUnityServer(problem, result, host, port)
    server.server_loop()

def pdsim_pddl(domain_path, problem_path, planner_name, host='127.0.0.1', port='5556'):
    try:
        problem_pddl = PDDLReader().parse_problem(domain_path, problem_path)
    except Exception as exception:
        print(exception)
        exit(1)
    try:
        result = solve_problem(problem_pddl, planner_name)
        if result.plan is None:
            print("No plan found")
            exit(1)
    except Exception as exception:
        print(exception)
        exit(1)
    launch_server(problem_pddl, result, host, port)


def pdsim_upf(problem_upf, planner_name, host='127.0.0.1', port='5556'):
    try:
        result = solve_problem(problem_upf, planner_name)
        if result.plan is None:
            print("No plan found")
            exit(1)
    except Exception as exception:
        print(exception)
        exit(1)
    launch_server(problem_upf, result, host, port)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PDSim server')
    parser.add_argument('--domain', type=str, help='Domain file')
    parser.add_argument('--problem', type=str, help='Problem file')
    parser.add_argument('--planner', type=str, default='fast-downward', help='Planner name')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host address')
    parser.add_argument('--port', type=str, default='5556', help='Port')

    args = parser.parse_args()

    # error checking args
    if args.domain is None or args.problem is None:
        usage()
        exit(1)
    else:
        # run server
        pdsim_pddl(args.domain, args.problem, args.planner, args.host, args.port)
