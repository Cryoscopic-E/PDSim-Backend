import json
import zmq
import time
from pdsim_pddl_reader import PDSimReader
from solver import request_plan
from flask import Flask, render_template, url_for
from pyparsing.exceptions import ParseBaseException
from threading import Thread
from os.path import isfile

HOST = '127.0.0.1'
PORT = 5556


class Worker(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.pdsim_reader = None
        self._context = zmq.Context()
        self._socket: zmq.Socket = self._context.socket(zmq.REP)
        self.active = True

    def run(self):
        self._socket.bind('tcp://{}:{}'.format(HOST, PORT))
        
        while self.active:
            #  Wait for next request from client
            unity_request = self._socket.recv_json()

            if unity_request['request'] == 'init':
                d_path = unity_request['domain_path']
                p_path = unity_request['problem_path']

                d_file_exist = isfile(d_path)
                p_file_exist = isfile(p_path)

                error_msg = ""
                # Check if files exists
                if not (d_file_exist and p_file_exist):

                    if not d_file_exist:
                        error_msg += "<Domain>"
                    if not p_file_exist:
                        error_msg += "<Problem>"
                    self._socket.send_json(json.dumps(
                        {'error': f'File(s) not in the specified path ({error_msg})'}).encode('utf-8'))
                else:
                    try:
                        self.pdsim_reader: PDSimReader = PDSimReader(d_path, p_path)
                    except ParseBaseException as pbe:
                        self.pdsim_reader = None
                        error_msg += pbe.msg
                        self._socket.send_json({'parse_error': f'Parse Error: ({error_msg})'})
                    except SyntaxError as se:
                        self.pdsim_reader = None
                        error_msg += se.msg
                        self._socket.send_json({'syntax_error': f'Parse Error: ({error_msg})'})
                    finally:
                        self._socket.send_json({'OK': 'Initialized'})

                print(f'Error? {error_msg}')
                print(f'Init with domain path {d_path}')
                print(f'Init with problem path {p_path}')

            elif unity_request['request'] == 'components':
                if self.pdsim_reader is not None:
                    self._socket.send_json(self.pdsim_reader.pdsim_representation())
                else:
                    self._socket.send_json(json.dumps({'error': f'Server parser not initialized'}).encode('utf-8'))

            elif unity_request['request'] == 'plan':
                self._socket.send_json({'error': f'Not Implemented'})
            else:
                pass

            time.sleep(0.1)


if __name__ == '__main__':
    worker = Worker()
    worker.start()
