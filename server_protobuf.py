import json
import zmq
import time
import signal

from unified_planning.grpc.proto_writer import ProtobufWriter
from unified_planning.io import PDDLReader


HOST = '127.0.0.1'
PORT = 5556


def server_main():
    context = zmq.Context()
    socket: zmq.Socket = context.socket(zmq.REP)
    active = True

    socket.bind('tcp://{}:{}'.format(HOST, PORT))

    print(f'Server running on port {PORT}..')

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    while active:
        #  Wait for next request from client
        request = socket.recv_json()
        if request['request'] == 'test-proto':
            writer = ProtobufWriter()
            pddl_reader = PDDLReader()

            problem = pddl_reader.parse_problem('./pddl/rover-temporal.pddl', './pddl/rover-temporal-problem.pddl')

            converted = writer.convert(problem)

            socket.send(converted.SerializeToString())

        time.sleep(1)
    socket.close()


if __name__ == '__main__':
    server_main()
