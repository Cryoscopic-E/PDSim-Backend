import argparse
import sys
from typing import List

from planning import pdsim_pddl_doplan, pdsim_pddl_userplan
from exceptions import PdSimError

def cli_planner_selector(planners: List[str]) -> str:
    """
    Callback for selecting a planner via CLI input.
    """
    print("Select planner:")
    for i, p in enumerate(planners):
        print(f"{i}. {p}")
    
    while True:
        try:
            print("Enter number:", end=" ")
            user_input = input()
            planner_index = int(user_input)
            if 0 <= planner_index < len(planners):
                return planners[planner_index]
            else:
                print(f"Invalid number. Please choose between 0 and {len(planners) - 1}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def main():
    parser = argparse.ArgumentParser(description='PDSim Backend Server')
    parser.add_argument('--domain', type=str, required=True, help='Path to the PDDL domain file')
    parser.add_argument('--problem', type=str, required=True, help='Path to the PDDL problem file')
    parser.add_argument('--plan', type=str, help='Path to an existing plan file (optional)')
    parser.add_argument('--planner', type=str, default='fast-downward', help='Name of the planner to use (default: fast-downward)')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Server host address (default: 127.0.0.1)')
    parser.add_argument('--port', type=str, default='5556', help='Server port (default: 5556)')

    args = parser.parse_args()

    try:
        if args.plan:
            pdsim_pddl_userplan(
                domain_path=args.domain,
                problem_path=args.problem,
                plan_path=args.plan,
                host=args.host,
                port=args.port
            )
        else:
            pdsim_pddl_doplan(
                domain_path=args.domain,
                problem_path=args.problem,
                planner_name=args.planner,
                host=args.host,
                port=args.port,
                planner_selection_callback=cli_planner_selector
            )
    except PdSimError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
