from unified_planning.shortcuts import *
from unified_planning.engines import PlanGenerationResultStatus
from unified_planning.plans.plan import ActionInstance

class PDSimSolver:
    def __init__(self, problem : Problem) -> None:
        self.cached_problem : Problem = problem
        self.planner = OneshotPlanner(name="fast-downward")

    def update_problem(self, problem : Problem) -> None:
        self.cached_problem = problem

    def action_info(self, action_instance : ActionInstance):
        return {"action_name": action_instance.action.name, "parameters": list(action_instance.actual_parameters)}

    def solve(self):
        result = self.planner.solve(self.cached_problem)
        planner_output = []
        if result.status == PlanGenerationResultStatus.SOLVED_SATISFICING:
            for action in result.plan.actions:
                planner_output.append(self.action_info(action))
        else:
            planner_output = {"error": "generic error solving plan"}
        return planner_output