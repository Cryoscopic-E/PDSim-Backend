import json
import zmq
import time
import signal
from pdsim_pddl_reader import PDSimReader
from solver import request_plan
from pyparsing.exceptions import ParseBaseException
from os.path import isfile

HOST = '127.0.0.1'
PORT = 5556

def server_main():
        pdsim_reader : PDSimReader = None
        context = zmq.Context()
        socket: zmq.Socket = context.socket(zmq.REP)
        active = True


        print ('##########################')
        print ('####   PDSim SERVER   ####')
        print ('##########################')

        socket.bind('tcp://{}:{}'.format(HOST, PORT))
        
        print(f'Server running on port {PORT}..')
        
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        while active:
            #  Wait for next request from client
            request = socket.recv_json()
            
            if request['request'] == 'init':
                d_path = request['domain_path']
                p_path = request['problem_path']

                d_file_exist = isfile(d_path)
                p_file_exist = isfile(p_path)

                error_msg = ""
                # Check if files exists
                if not (d_file_exist and p_file_exist):

                    if not d_file_exist:
                        error_msg += "<Domain>"
                    if not p_file_exist:
                        error_msg += "<Problem>"
                    socket.send_json(json.dumps(
                        {'error': f'File(s) not in the specified path ({error_msg})'}).encode('utf-8'))
                else:
                    try:
                        pdsim_reader: PDSimReader = PDSimReader(d_path, p_path)
                        socket.send_json({'OK': 'Initialized'})
                    except ParseBaseException as pbe:
                        pdsim_reader = None
                        error_msg += pbe.msg
                        socket.send_json({'parse_error': f'Parse Error: ({error_msg})'})
                    except SyntaxError as se:
                        pdsim_reader = None
                        error_msg += se.msg
                        socket.send_json({'syntax_error': f'Parse Error: ({error_msg})'})
                    except AssertionError:
                        pdsim_reader = None
                        error_msg += 'Check domain/problem files'
                        socket.send_json({'assertion_error': f'Parse Error: {error_msg}'})
                    except Exception:
                        pdsim_reader = None
                        error_msg += 'Check validity domain and/or problem files'
                        socket.send_json({'error': f'Parse Error: ({error_msg})'})
                    finally:
                        if error_msg:
                            print(f'Error? {error_msg}')
                            print('Server not initialized')
                        else:
                            print(f'Server initialized with domain at: {d_path}')
                            print(f'Server initialized with problem at: {p_path}')

            elif request['request'] == 'components':
                if pdsim_reader is not None:
                    socket.send_json(pdsim_reader.pdsim_representation())
                else:
                    socket.send_json(json.dumps({'error': f'Server parser not initialized'}))

            elif request['request'] == 'plan':
                socket.send_json({'error': f'Not Implemented'})
            else:
                print('Invalid Request..')
                socket.send_json({'error': 'Invalid request'})
            time.sleep(0.1)


if __name__ == '__main__':
    server_main()
