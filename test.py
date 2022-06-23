# test parser
import pprint
from pdsim_pddl_reader import PDSimReader
from unified_planning.shortcuts import *
from unified_planning.io.pddl_reader import PDDLReader
from unified_planning.model.problem import Problem
from unified_planning.model.action import InstantaneousAction
from unified_planning.model.fnode import FNode


def main():
    #pdsim_reader: PDSimReader = PDSimReader('./pddl/blocks-domain.pddl',  './pddl/blocks-instance.pddl')
    pdsim_reader: PDSimReader = PDSimReader('./pddl/logistics-domain.pddl', './pddl/logistics-instance.pddl')
    #pdsim_reader: PDSimReader = PDSimReader('./pddl/elevator-domain-ut.pddl', './pddl/elevator-problem-ut.pddl')
    
    #pprint.pprint(pdsim_reader.pdsim_representation())
if __name__ == '__main__':
    main()
