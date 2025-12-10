from planning import pdsim_pddl_doplan, pdsim_pddl_userplan

def run_backend(*, domain='', problem='', plan='', planner='fast-downward', host='127.0.0.1', port='5556'):
    """
    Run the PDSim Backend server, calculating environment and plans for the specified PDDL domain and problem.
    This is a wrapper for backward compatibility and easy library usage.
    """
    if not domain or not problem:
        print("PDDL Domain and problem files are required.")
        return

    # For library usage, we might not want the interactive selector by default, 
    # or we could define a simple one if needed. Passing None means it will auto-select
    # or fail if the requested one isn't there and multiple others are.
    
    
    if plan:
        pdsim_pddl_userplan(domain, problem, plan, host, port)
    else:
        pdsim_pddl_doplan(domain, problem, planner, host, port)