from unified_planning.shortcuts import *
from unified_planning.engines import PlanGenerationResultStatus
from unified_planning.plans.plan import ActionInstance

class PDSimSolver:
    def __init__(self, problem : Problem) -> None:
        self.cached_problem : Problem = problem
        self.planner = OneshotPlanner(name='fast-downward')

    def update_problem(self, problem : Problem) -> None:
        self.cached_problem = problem

    def action_info(self, action_instance : ActionInstance):
        params = map(str,action_instance.actual_parameters)
        return {'action_name': action_instance.action.name, 'parameters': list(params)}

    def solve(self):
        result = self.planner.solve(self.cached_problem)
        planner_output = {}
        action_list = []
        if result.status == PlanGenerationResultStatus.SOLVED_SATISFICING:
            for action in result.plan.actions:
                action_list.append(self.action_info(action))
            planner_output['plan'] = action_list
        else:
            planner_output['error'] = 'Generic error solving plan'
        return planner_output