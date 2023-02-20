from unified_planning.shortcuts import *
from unified_planning.io.pddl_reader import PDDLReader
from unified_planning.model.problem import Problem
from unified_planning.model.action import InstantaneousAction
from unified_planning.model.fnode import FNode
from unified_planning.exceptions import *
from unified_planning.model.operators import OperatorKind

import pprint
class PDSimReader:
    def __init__(self, domain_path, problem_path) -> None:
        self.problem = PDDLReader().parse_problem(domain_path, problem_path)
    
    def pdsim_representation(self):
        if self.problem is None:
            raise Exception("Error: Parser Not Initialized")
        else:
            return self._pdsim_representation()

    def _pdsim_representation(self):
        # ==== DOMAIN FEATURES ====
        features = list(self.problem.kind.features)
        
        # ==== PROBLEM NAME ====
        problem_name = self.problem.name if self.problem.has_name else 'problem'

        # ==== TYPES ====
        
        types = dict()
        # root is object
        types.setdefault('object', [])

        # only 1 type (userdefined, or no types)
        if len(self.problem.user_types) == 1:
            if self.problem.user_types[0].name != 'object':
                types['object'].append(self.problem.user_types[0].name)
                types.setdefault(self.problem.user_types[0].name, [])
        #  if user types are defined
        elif len(self.problem.user_types) > 1:
            for t in self.problem.user_types:
                types.setdefault(t.name, [])
                parent_type = t.father
                if parent_type is None:
                    types['object'].append(t.name)
                else:
                    types.setdefault(parent_type.name, []).append(t.name)

        # ==== FLUENTS ====
        fluents = {}
        fluent: Fluent
        for fluent in self.problem.fluents:
            fluent_name: str = fluent.name
            fluents[fluent_name] = {}
            fluents[fluent_name]["arity"] : int = fluent.arity
            fluents[fluent_name]["args"] = {}
            for arg_type in fluent.signature:
                fluents[fluent_name]["args"][arg_type.name] :str = arg_type.type.name

        # ==== ACTIONS ====
        actions = {}
        for action in self.problem.actions:
            actions.setdefault(action.name, {})
            actions[action.name].setdefault("params", {})
            # Action's parameters  [name-type]
            for action_param in action.parameters:
                param_name: str = action_param.name
                type_name: str = action_param.type.name
                actions[action.name]["params"][param_name] = type_name
            actions[action.name].setdefault("effects", [])
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
            objects[obj.name] :str = obj.type.name
        
        # ==== INITIAL STATE ====
        initial_values = self.problem.explicit_initial_values
        init_block = {}
        for init in initial_values:
            fluent_name: str = init.fluent().name
            init_block.setdefault(fluent_name, [])
            args = []
            for arg in init.args:
                args.append(str(arg))
            init_block[fluent_name].append({
                "args": args,
                "value": bool(initial_values[init])
            })
        
        
        # ==== GOAL STATE====

        goals = self.problem.goals
        goal_block = {}

        for goal in goals:
            if goal.node_type == OperatorKind.FLUENT_EXP:
                fluent_name: str = goal.fluent().name
                goal_block.setdefault(fluent_name, [])
                args = []
                for arg in goal.args:
                    args.append(str(arg))
                goal_block[fluent_name].append({
                    "args": args,
                    "value": not goal.is_not()
                })
            elif goal.node_type == OperatorKind.AND:
                sub_goals = goal.args
                for sub_goal in sub_goals:
                    fluent_name: str = sub_goal.fluent().name
                    goal_block.setdefault(fluent_name, [])
                    args = []
                    for arg in sub_goal.args:
                        args.append(str(arg))
                    goal_block[fluent_name].append({
                        "args": args,
                        "value": not sub_goal.is_not()
                    })

        return {
            'features': features,
            'problem_name': problem_name,
            'types': types,
            'predicates': fluents,
            'actions': actions,
            'objects': objects,
            'init': init_block,
            'goal': goal_block}