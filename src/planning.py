import threading
import logging
import unified_planning as up
from unified_planning.io.pddl_reader import PDDLReader
from unified_planning.model import Problem
from unified_planning.plans import Plan
from unified_planning.engines import PlanGenerationResult, CompilationKind
from unified_planning.shortcuts import OneshotPlanner, get_all_applicable_engines, Compiler
from typing import Optional, List, Callable, Union

from exceptions import NoPlanFoundError, PlannerNotApplicableError, ParsingError
from server import PdSimUnityServer
from pdsim_problem import PdSimProblem

def compile_problem(problem: Problem) -> Problem:
    """
    Compiles the problem to remove quantifiers and conditional effects.
    """
    # Remove quantifiers
    with Compiler(
            problem_kind=problem.kind,
            compilation_kind=CompilationKind.QUANTIFIERS_REMOVING) as compiler:
        compilation_result = compiler.compile(problem)
    
    # Remove conditional effects
    with Compiler(
            problem_kind=problem.kind,
            compilation_kind=CompilationKind.CONDITIONAL_EFFECTS_REMOVING) as compiler:
        compilation_result = compiler.compile(compilation_result.problem)
        
    return compilation_result.problem

def solve_problem(problem: Problem, planner_name: str, planner_selection_callback: Optional[Callable[[List[str]], str]] = None) -> PlanGenerationResult:
    """
    Solves the given planning problem using the specified planner.
    
    Args:
        problem: The UP problem instance.
        planner_name: The name of the planner to use.
        planner_selection_callback: A function that takes a list of applicable planner names 
                                    and returns the selected planner name. Used if the requested 
                                    planner is not applicable.
    
    Returns:
        The result of the plan generation.
        
    Raises:
        PlannerNotApplicableError: If no applicable planner is found.
    """
    applicable_planners = get_all_applicable_engines(problem.kind)
    
    if len(applicable_planners) == 0:
        raise PlannerNotApplicableError(f"No planners applicable to problem kind: {problem.kind}")

    if planner_name not in applicable_planners:
        print(f"Planner '{planner_name}' not applicable to problem {problem.kind}")
        
        if len(applicable_planners) == 1:
            planner_name = applicable_planners[0]
            print(f"Automatically using the only available planner: {planner_name}")
        elif planner_selection_callback:
            planner_name = planner_selection_callback(applicable_planners)
            print(f"Selected planner: {planner_name}")
        else:
            # Fallback if no callback provided: just pick the first one or raise error?
            # Original behavior implies user interaction, so we default to first to avoid blocking if no callback.
            planner_name = applicable_planners[0]
            print(f"Defaulting to: {planner_name}")

    planner = OneshotPlanner(name=planner_name)
    result = planner.solve(problem)
    return result

def launch_server(problem: Problem, result: Union[PlanGenerationResult, Plan], host: str, port: str, 
                  planner_name: Optional[str] = None, 
                  solve_callback: Optional[Callable[[Problem, str], PlanGenerationResult]] = None,
                  stop_event: Optional[threading.Event] = None,
                  logger: Optional[logging.Logger] = None):
    """
    Starts the PDSim Unity Server.
    """
    # Wrap the unified_planning Problem in our PdSimProblem wrapper
    pdsim_problem = PdSimProblem(problem)
    server = PdSimUnityServer(pdsim_problem, result, host, port, 
                              planner_name=planner_name, 
                              solve_callback=solve_callback,
                              stop_event=stop_event,
                              logger=logger)
    server.server_loop()

def prepare_pddl_userplan(domain_path: str, problem_path: str, plan_path: str):
    try:
        print("Parsing domain and problem...")
        problem_pddl = PDDLReader().parse_problem(domain_path, problem_path)
        print("Parsing Complete")
        problem_pddl = compile_problem(problem_pddl)
        print("Compiling Complete")
        
        print(f"Parsing plan: {plan_path}")
        plan = PDDLReader().parse_plan(problem_pddl, plan_path)
        print("Parsing Plan Complete")
    except Exception as exception:
        raise ParsingError(f"Error loading plan or problem: {exception}") from exception
    
    return problem_pddl, plan

# PDSim UPF and PDDL entry points in main.py

def prepare_pddl_doplan(domain_path: str, problem_path: str, planner_name: str, planner_selection_callback: Optional[Callable[[List[str]], str]] = None):
    try:
        print(f"Parsing domain: {domain_path} and problem: {problem_path}")
        problem_pddl = PDDLReader().parse_problem(domain_path, problem_path)
        print("Parsing Complete")
        problem_pddl = compile_problem(problem_pddl)
    except Exception as exception:
        raise ParsingError(f"Error parsing problem: {exception}") from exception

    try:
        result = solve_problem(problem_pddl, planner_name, planner_selection_callback)
        if result.plan is None:
            raise NoPlanFoundError("The planner returned no plan.")
    except Exception as exception:
        raise exception # Re-raise to be handled by caller

    def replan_callback(prob, name):
         return solve_problem(prob, name, planner_selection_callback)
         
    return problem_pddl, result, replan_callback

def prepare_upf(problem_upf: Problem, planner_name: str, planner_selection_callback: Optional[Callable[[List[str]], str]] = None):
    up.shortcuts.get_environment().credits_stream = None
    try:
        result = solve_problem(problem_upf, planner_name, planner_selection_callback)
        if result.plan is None:
            raise NoPlanFoundError("No plan found for the UPF problem.")
    except Exception as exception:
        raise exception

    def replan_callback(prob, name):
         return solve_problem(prob, name, planner_selection_callback)
    
    return problem_upf, result, replan_callback

def pdsim_pddl_doplan(domain_path: str, problem_path: str, planner_name: str, host: str = '127.0.0.1', port: str = '5556', planner_selection_callback: Optional[Callable[[List[str]], str]] = None):
    """
    Parses PDDL, solves the problem, and launches the server.
    """
    problem_pddl, result, replan_callback = prepare_pddl_doplan(domain_path, problem_path, planner_name, planner_selection_callback)
    launch_server(problem_pddl, result, host, port, planner_name=planner_name, solve_callback=replan_callback)

def pdsim_pddl_userplan(domain_path: str, problem_path: str, plan_path: str, host: str = '127.0.0.1', port: str = '5556'):
    """
    Parses PDDL and a pre-existing plan, then launches the server.
    """
    problem_pddl, plan = prepare_pddl_userplan(domain_path, problem_path, plan_path)
    # User plan mode: we might not have a preferred planner for replanning.
    launch_server(problem_pddl, plan, host, port)


# TODO: check usage
def pdsim_upf(problem_upf: Problem, planner_name: str, host: str = '127.0.0.1', port: str = '5556', planner_selection_callback: Optional[Callable[[List[str]], str]] = None):
    """
    Solves a UPF problem object directly and launches the server.
    """
    problem_upf, result, replan_callback = prepare_upf(problem_upf, planner_name, planner_selection_callback)
    launch_server(problem_upf, result, host, port, planner_name=planner_name, solve_callback=replan_callback)
