import threading
import zmq
import signal
import time

from unified_planning.io.pddl_reader import PDDLReader
from unified_planning.environment import get_environment
from unified_planning.engines import PlanGenerationResultStatus
from unified_planning.shortcuts import OneshotPlanner, get_all_applicable_engines

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
