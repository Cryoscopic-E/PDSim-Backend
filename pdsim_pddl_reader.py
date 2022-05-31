from unified_planning.shortcuts import *
from unified_planning.io.pddl_reader import PDDLReader
from unified_planning.model.problem import Problem
from unified_planning.model.action import InstantaneousAction
from unified_planning.model.fnode import FNode


class PDSimReader:
    def __init__(self, domain_path, problem_path):
        self.domain_path: str = domain_path
        self.problem_path: str = problem_path
        self.reader: PDDLReader = PDDLReader()
        self.problem: Problem = self.reader.parse_problem(
            self.domain_path, self.problem_path)

    def pdsim_representation(self):

       # ==== DOMAIN REQUIREMENTS ====
        features = list(self.problem.kind.features)

        # ==== PROBLEM NAME ====
        problem_name = self.problem.name

        # ==== TYPES ====
        types = dict()
        # root is object
        types['object'] = list()
        #  if user types are defined
        print(self.problem.user_types)
        if len(self.problem.user_types) >= 1:
            for t in self.problem.user_types:
                # put type in list, if it doesn't exist
                if types.get(t.name) is None:
                    types[t.name] = list()

                parent_type = t.father
                if parent_type is None:
                    types['object'].append(t.name)

                else:
                    if types.get(parent_type.name) is None:
                        types[parent_type.name] = list()
                    types[parent_type.name].append(t.name)

        # ==== PREDICATES ====
        fluents = {}
        fluent: Fluent
        for fluent in self.problem.fluents:
            fluent_name: str = fluent.name
            fluents[fluent_name] = {}
            fluents[fluent_name]["arity"] = fluent.arity
            fluents[fluent_name]["args"] = {}
            for arg_type in fluent.signature:
                fluents[fluent_name]["args"][arg_type.name] = arg_type.type.name

            # ==== ACTIONS ====
        actions = {}
        for action in self.problem.actions:
            actions[action.name] = {}
            actions[action.name]["params"] = {}
            # Action's parameters  [name-type]
            for action_param in action.parameters:
                param_name: str = action_param.name
                type_name = action_param.type.name
                actions[action.name]["params"][param_name] = type_name
            actions[action.name]["effects"] = []
            # Action's effects [name, negated, arguments (maps to parameters)]
            if isinstance(action, InstantaneousAction):
                for effect in action.effects:
                    fluent_node: FNode = effect.fluent
                    fluent: str = fluent_node.fluent().name
                    is_negated: bool = not effect.value.is_true()
                    arguments = []
                    for arg in fluent_node.args:
                        arguments.append(str(arg))
                    actions[action.name]["effects"].append({
                        'fluent': fluent,
                        'negated': is_negated,
                        'args': arguments
                    })

        # ==== OBJECTS ====
        objects = {}
        for obj in self.problem.all_objects:
            objects[obj.name] = obj.type.name

        # ==== INITIAL FLUENTS ====
        initial_values = self.problem.initial_values
        init_block = {}
        for init in initial_values:
            fluent_name: str = init.fluent().name
            if not init_block.get(fluent_name):
                init_block[fluent_name] = []
            args = []
            for arg in fluent_node.args:
                args.append(str(arg))
            init_block[fluent_name].append({
                "args": args,
                "value": bool(initial_values[init])
            })

        return {
            'features': features,
            'problem_name': problem_name,
            'types': types,
            'actions': actions,
            'objects': objects,
            'predicates': fluents,
            'init': init_block
        }
