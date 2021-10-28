import zmq
import time
from parser import PDDLParser
from solver import request_plan
from flask import Flask, render_template
from threading import Thread

HOST = '127.0.0.1'
PORT = 5556

app = Flask('app')
DATA = None


@app.route('/')
def index():
    return render_template('index.html.j2', data=DATA)


class Worker(Thread):

    def __init__(self):
        Thread.__init__(self)
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REP)
        self._pddl_parser = PDDLParser()
        self.active = True

    def run(self):
        self._socket.bind('tcp://{}:{}'.format(HOST, PORT))

        while self.active:
            #  Wait for next request from client
            unity_request = self._socket.recv_json()

            if unity_request['request'] == 'init':
                # json_obj = json.loads(message)
                self._pddl_parser.set_files(unity_request["domain"], unity_request["instance"])
                #  Send reply back to client
                self._socket.send_json(self._pddl_parser.parse_pddl())
            elif unity_request['request'] == 'plan':
                plan = request_plan(self._pddl_parser.current_domain,
                                    self._pddl_parser.current_instance)
                self._socket.send_json(plan)
            else:
                pass

            time.sleep(0.1)


if __name__ == '__main__':
    worker = Worker()
    worker.start()
    app.run()
