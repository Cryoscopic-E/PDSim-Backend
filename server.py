import json
import zmq
import time
from pddl_parser import PDDLParser
from solver import request_plan
from flask import Flask, render_template, url_for
from threading import Thread
from os.path import isfile

HOST = '127.0.0.1'
PORT = 5556

app = Flask('app')
DATA = {
				"domain":
				""";; logistics domain Typed version.
;;

(define (domain logistics)
		(:requirements :strips :typing)
		(:types city place physobj - object
										airport location - place
										package vehicle - physobj
										truck airplane - vehicle
										)

		(:predicates 	(in-city ?loc - place ?city - city)
		(at ?obj - physobj ?loc - place)
		(in ?pkg - package ?veh - vehicle))

(:action LOAD-TRUCK
			:parameters    (?pkg - package ?truck - truck ?loc - place)
			:precondition  (and (at ?truck ?loc) (at ?pkg ?loc))
			:effect        (and (not (at ?pkg ?loc)) (in ?pkg ?truck)))

(:action LOAD-AIRPLANE
		:parameters   (?pkg - package ?airplane - airplane ?loc - place)
		:precondition (and (at ?pkg ?loc) (at ?airplane ?loc))
		:effect       (and (not (at ?pkg ?loc)) (in ?pkg ?airplane)))

(:action UNLOAD-TRUCK
		:parameters   (?pkg - package ?truck - truck ?loc - place)
		:precondition (and (at ?truck ?loc) (in ?pkg ?truck))
		:effect       (and (not (in ?pkg ?truck)) (at ?pkg ?loc)))

(:action UNLOAD-AIRPLANE
		:parameters    (?pkg - package ?airplane - airplane ?loc - place)
		:precondition  (and (in ?pkg ?airplane) (at ?airplane ?loc))
		:effect        (and (not (in ?pkg ?airplane)) (at ?pkg ?loc)))

(:action DRIVE-TRUCK
		:parameters (?truck - truck ?loc-from - place ?loc-to - place ?city - city)
		:precondition
			(and (at ?truck ?loc-from) (in-city ?loc-from ?city) (in-city ?loc-to ?city))
		:effect
			(and (not (at ?truck ?loc-from)) (at ?truck ?loc-to)))

(:action FLY-AIRPLANE
		:parameters (?airplane - airplane ?loc-from - airport ?loc-to - airport)
		:precondition
			(at ?airplane ?loc-from)
		:effect
			(and (not (at ?airplane ?loc-from)) (at ?airplane ?loc-to)))
)""",
				"problem":
				"""(define (problem logistics-4-0)
(:domain logistics)
(:objects
	apn1 - airplane
	apt1 apt2 - airport
	pos2 pos1 - location
	cit2 cit1 - city
	tru2 tru1 - truck
	obj23 obj22 obj21 obj13 obj12 obj11 - package)

(:init (at apn1 apt2) (at tru1 pos1) (at obj11 pos1)
	(at obj12 pos1) (at obj13 pos1) (at tru2 pos2) (at obj21 pos2) (at obj22 pos2)
	(at obj23 pos2) (in-city pos1 cit1) (in-city apt1 cit1) (in-city pos2 cit2)
	(in-city apt2 cit2))

(:goal (and (at obj11 apt1) (at obj23 pos1) (at obj13 apt1) (at obj21 pos1)))
)"""
}


@app.route('/')
def index():
	return render_template('index.html', data=DATA)


class Worker(Thread):
	def __init__(self):
		Thread.__init__(self)
		self._context = zmq.Context()
		self._socket = self._context.socket(zmq.REP)
		self._pddl_parser = PDDLParser()
		self.active = True
		self.domain_path = None
		self.instance_path = None

	def run(self):
		self._socket.bind('tcp://{}:{}'.format(HOST, PORT))

		while self.active:
			#  Wait for next request from client
			unity_request = self._socket.recv_json()

			if unity_request['request'] == 'init':
				d_path = unity_request['domain_path']
				p_path = unity_request['instance_path']

				d_file_exist = isfile(d_path)
				p_file_exist = isfile(p_path)
				
				# Check if files exists
				if not (d_file_exist and p_file_exist): 
					error_msg = ""
					if not d_file_exist:
						error_msg += "<Domain>"
					if not p_file_exist:
						error_msg += "<Instance>"
					self._socket.send_json(json.dump({'error':f'File(s) not in the specified path ({error_msg})'}))
				# Set paths
				else:
					self.domain_path = unity_request['domain_path']
					self.instance_path = unity_request['instance_path']

			elif unity_request['request'] == 'parse':
				# if server hasn't been initialise return error
				if self.domain_path is None and self.instance_path is None:
					self._socket.send_json(json.dump({'error':'Server not initialized, Make sure you have started a new Simulation in unity'}))
				else:
					# reset parser if exist
					if self._pddl_parser is not None:
						self._pddl_parser = PDDLParser()
						self._pddl_parser.set_files(unity_request["domain"],unity_request["instance"])
						self._socket.send_json(self._pddl_parser.parse_pddl())

					elif unity_request['request'] == 'plan':
						plan = request_plan(self._pddl_parser.current_domain,self._pddl_parser.current_instance)
						self._socket.send_json(plan)
					else:
						pass

			time.sleep(0.1)



if __name__ == '__main__':
	worker = Worker()
	worker.start()
	app.run()
