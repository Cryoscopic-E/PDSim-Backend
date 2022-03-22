# test parser
from pddl_parser import PDDLParser
from unified_planning.shortcuts import *
from unified_planning.io.pddl_reader import PDDLReader

from unified_planning.model.problem import Problem
from unified_planning.model.action import Action, InstantaneousAction, DurativeAction
from unified_planning.model.types import Type
from unified_planning.model.effect import Effect
from unified_planning.model.fnode import FNode


def main():

    pddl_read = PDDLReader()
    prob : Problem = pddl_read.parse_problem('./pddl/domain.pddl','./pddl/instance-1.pddl')
    #action : Action = prob.action('UNLOAD-TRUCK')

    for action in prob.actions():
      print(f'Action Name: {action.name}')

      # Action's parameters  [name-type]
      for action_param in action.parameters():
            param_name: str = action_param.name()
            type_name = action_param.type().name()
            print('\t',param_name, f'<{type_name}>')

      # Action's effects [negated, name, arity, arguments (maps to parameters)]
      if isinstance(action, InstantaneousAction):
        for effect in action.effects():
          fluent_node :FNode = effect.fluent()
          fluent : Fluent = fluent_node.fluent()
          is_negated = not effect.value().is_true()
          arguments = fluent_node.args()
          print(f'Fluent Name: {fluent.name()}')
          print(f'Negated:{is_negated}')
          print(f'Arity:{fluent.arity()}')
          print(f'Args:{arguments}')
          print('\n')

      


if __name__ == '__main__':
    main()
