# test parser
import pprint
from unified_planning.shortcuts import *
from unified_planning.io.pddl_reader import PDDLReader
from unified_planning.model.problem import Problem
from unified_planning.model.action import InstantaneousAction
from unified_planning.model.fnode import FNode


def main():
    pddl_read = PDDLReader()
    problem: Problem = pddl_read.parse_problem('./pddl/domain.pddl', './pddl/instance-1.pddl')

    # ==== DOMAIN REQUIREMENTS ====
    features = list(problem.kind.features)

    # ==== PROBLEM NAME ====
    problem_name = problem.name

    # ==== TYPES ====
    types = dict()
    # root is object
    types['object'] = list()
    for t in problem.user_types:

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
    for fluent in problem.fluents:
        fluent_name: str = fluent.name
        fluents[fluent_name] = {}
        fluents[fluent_name]["arity"] = fluent.arity
        fluents[fluent_name]["args"] = []
        for arg_type in fluent.signature:
            fluents[fluent_name]["args"].append(arg_type.name)

        # ==== ACTIONS ====
    actions = {}
    for action in problem.actions:
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
    for obj in problem.all_objects:
        objects[obj.name] = obj.type.name

    # ==== INITIAL FLUENTS ====
    initial_values = problem.initial_values
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

    pprint.pprint({
        'features': features,
        'problem_name': problem_name,
        'types': types,
        'actions': actions,
        'objects': objects,
        'predicates': fluents,
        'init': init_block
    })


if __name__ == '__main__':
    main()
