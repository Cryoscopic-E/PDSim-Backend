from unified_planning.shortcuts import *
from unified_planning.io.pddl_reader import PDDLReader

from unified_planning.model.problem import Problem
from unified_planning.model.action import InstantaneousAction
from unified_planning.model.fnode import FNode
from unified_planning.model.object import Object


class PDSimReader:
    def __init__(self, domain_path, problem_path):
        self.domain_path: str = domain_path
        self.problem_path: str = problem_path
        self.reader: PDDLReader = PDDLReader()
        self.problem: Problem = self.reader.parse_problem(self.domain_path, self.problem_path)

    def pdsim_representation(self):
        # ==== DOMAIN REQUIREMENTS ====
        features = self.problem.kind().features()

        # ==== PROBLEM NAME ====
        problem_name = self.problem.name

        # ==== TYPES ====
        types = dict()
        # root is object
        types['object'] = list()
        for t in self.problem.user_types():

            # put type in list, if it doesn't exist
            if types.get(t.name()) is None:
                types[t.name()] = list()

            parent_type = t.father()
            if parent_type is None:
                types['object'].append(t.name())

            else:
                if types.get(parent_type.name()) is None:
                    types[parent_type.name()] = list()
                types[parent_type.name()].append(t.name())

        # ==== PREDICATES ====

        for fluent in self.problem.fluents():
            print(fluent.name())
            print(fluent.arity())
            for arg_type in fluent.signature():
                print(arg_type.name())

            # ==== ACTIONS ====
        for action in self.problem.actions():
            # print(f'Action Name: {action.name}')

            # Action's parameters  [name-type]
            for action_param in action.parameters():
                param_name: str = action_param.name()
                type_name = action_param.type().name()
                # print('\t',param_name, f'<{type_name}>')

            # Action's effects [negated, name, arity, arguments (maps to parameters)]
            if isinstance(action, InstantaneousAction):
                for effect in action.effects():
                    fluent_node: FNode = effect.fluent()
                    fluent: Fluent = fluent_node.fluent()
                    is_negated = not effect.value().is_true()
                    arguments = fluent_node.args()
                    # print(f'Fluent Name: {fluent.name()}')
                    # print(f'Negated:{is_negated}')
                    # print(f'Arity:{fluent.arity()}')
                    # print(f'Args:{arguments}')
                    # print('\n')
        # ==== OBJECTS ====
        for obj in self.problem.all_objects():
            self.problem_objects(obj)

        # ==== INITIAL FLUENTS ====
        init = self.problem.initial_values()

        return {
            'features': features,
            'problem_name': problem_name,
            'types': types,
            'predicates': fluents,
            'init': init
        }
