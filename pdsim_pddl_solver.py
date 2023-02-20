from unified_planning.shortcuts import *
from unified_planning.engines import PlanGenerationResultStatus
from unified_planning.plans.plan import ActionInstance
import requests
import sys


class PlanningDomainsSolver:
    def __init__(self, domain_file:str, problem_file:str) -> None:
        self.data = {'domain': open(domain_file, 'r').read(),
                    'problem': open(problem_file, 'r').read()}

    def solve(self):
        resp = requests.post('http://solver.planning.domains/solve',verify=False, json=self.data).json()
        return resp['result']
    


class PDSimSolver:
    def __init__(self, problem : Problem, domain_file:str, problem_file:str, solver:str='pyperplan') -> None:
        self.cached_problem : Problem = problem
        if solver == 'fast-downward':
            self.planner = OneshotPlanner(name='fast-downward')
        elif solver == 'planning-domains':
            self.planner = PlanningDomainsSolver(domain_file, problem_file)
        else:
            self.planner = OneshotPlanner(name='pyperplan')


    def action_info(self, action_instance : ActionInstance):
        params = map(str,action_instance.actual_parameters)
        return {'action_name': action_instance.action.name, 'parameters': list(params)}

    def parse_planning_domains_action(self, action_name : str):
        
        action = action_name[1:-1].split(' ')
        return {'action_name': action[0], 'parameters': action[1:]}

    def solve(self):
        print("Solving problem...")
        planner_output = {}
        action_list = []
        result = None
        if self.planner.__class__.__name__ == 'PlanningDomainsSolver':
            result = self.planner.solve()
            print(result)
            if result['parse_status'] == 'ok':
                for action in result['plan']:
                    action_list.append(self.parse_planning_domains_action(action['name']))
                planner_output['actions'] = action_list
            else:
                planner_output['error'] = result['error']
                print(result['error'])
        else:
            result = self.planner.solve(self.cached_problem)
            print(result)
            if result.status == PlanGenerationResultStatus.SOLVED_SATISFICING:
                for action in result.plan.actions:
                    action_list.append(self.action_info(action))
                planner_output['actions'] = action_list
                planner_output['actions'] = action_list
            else:
                planner_output['error'] = 'Error solving plan'
                print(result['error'])
        return planner_output
