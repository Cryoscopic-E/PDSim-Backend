# test parser
import pprint
import json
from pdsim_pddl_reader import PDSimReader
from pdsim_pddl_solver import PDSimSolver
from unified_planning.shortcuts import *
from unified_planning.io.pddl_reader import PDDLReader
from unified_planning.model.problem import Problem
from unified_planning.model.action import InstantaneousAction
from unified_planning.model.fnode import FNode


def main():
    #pdsim_reader: PDSimReader = PDSimReader('./pddl/blocks-domain.pddl',  './pddl/blocks-instance.pddl')
    pdsim_reader: PDSimReader = PDSimReader('./pddl/depot-domain.pddl',  './pddl/depot-problem.pddl')
    #pdsim_reader: PDSimReader = PDSimReader('./pddl/logistics-domain.pddl', './pddl/logistics-instance.pddl')
    #pdsim_reader: PDSimReader = PDSimReader('./pddl/elevator-domain-ut.pddl', './pddl/elevator-problem-ut.pddl')
    #pprint.pprint(pdsim_reader.pdsim_representation())
    #pdsim_reader: PDSimReader = PDSimReader('./pddl/domain.pddl',  './pddl/problem1.pddl')
    #save to json
    with open('pdsim_representation.json', 'w') as outfile:
        json.dump(pdsim_reader.pdsim_representation(), outfile)
    

    if pdsim_reader.problem is not None:
        pdsim_solver: PDSimSolver = PDSimSolver(pdsim_reader.problem, pdsim_reader.domain_path, pdsim_reader.problem_path, 'fast-downward')
        pprint.pprint(pdsim_solver.solve())
    else:
        print("Error: could not parse problem")
    
if __name__ == '__main__':
    main()
