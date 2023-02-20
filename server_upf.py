import json
import zmq
import time
import pprint
import signal
from pdsim_pddl_reader import PDSimReader
from pdsim_pddl_solver import PDSimSolver
from pyparsing.exceptions import ParseBaseException
from os.path import isfile

HOST = '127.0.0.1'
PORT = 5556

def server_main():
        pdsim_reader : PDSimReader = None
        pdsim_solver : PDSimSolver = None
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
            print(request)
            if request['request'] == 'parse':
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
                        pdsim_solver: PDSimSolver = PDSimSolver(pdsim_reader.problem, d_path, p_path, 'fast-downward')
                        response = pdsim_reader.pdsim_representation()
                        plan = pdsim_solver.solve()
                        response['plan'] = plan
                        plan = pdsim_solver.solve()
                        response['plan'] = plan
                        response['status'] = 'OK'
                        pprint.pprint(plan)
                        try:
                            j = json.dumps(response).encode('utf-8')
                        except Exception as e:
                            print(e)
                        try:
                            socket.send_string(j.decode('utf-8'))
                        except Exception as e:
                            print("FEfwegwg")
                            print(e)
                    except ParseBaseException as pbe:
                        pdsim_reader = None
                        pdsim_solver = None
                        error_msg += pbe.msg
                        socket.send_json({'status':'ERR','parse_error': f'Parse Error: ({error_msg})'})
                    except SyntaxError as se:
                        pdsim_reader = None
                        pdsim_solver = None
                        error_msg += se.msg
                        socket.send_json({'status':'ERR','syntax_error': f'Parse Error: ({error_msg})'})
                    except AssertionError:
                        pdsim_reader = None
                        pdsim_solver = None
                        error_msg += 'Check domain/problem files'
                        socket.send_json({'status':'ERR','assertion_error': f'Parse Error: {error_msg}'})
                    except TimeoutError:
                        pdsim_reader = None
                        pdsim_solver = None
                        error_msg += 'Timeout'
                        socket.send_json({'status':'ERR','timeout_error': f'Parse Error: {error_msg}'})
                    except TypeError as te:
                        pdsim_reader = None
                        pdsim_solver = None
                        print(te)
                        error_msg += 'Inappropriate argument type: ' + str(te)
                        socket.send_json({'status':'ERR','type_error': f'Type Error: {error_msg}'})
                    except Exception as e:
                        pdsim_reader = None
                        pdsim_solver = None
                        print(e)
                        socket.send_json({'status':'ERR','error': f'Check Server logs'})
                    finally:
                        if error_msg:
                            print(f'Error? {error_msg}')
                        else:
                            print('Response sent')

            elif request['request'] == 'test':
                print("Test request received")
                socket.send_json({'status': 'OK'})
            else:
                print('Invalid Request..')
                socket.send_json({'status':'ERR','error': 'Invalid request'})
            time.sleep(0.1)


if __name__ == '__main__':
    server_main()
