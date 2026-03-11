import argparse
import sys

from pdsim_unity.exceptions import PdSimError
from pdsim_unity.planning import pdsim_pddl_doplan, pdsim_pddl_userplan
from pdsim_unity.ui.prompts import cli_planner_selector
from pdsim_unity.interactive import interactive_mode

def main():
    parser = argparse.ArgumentParser(description='PDSim Backend Server')
    parser.add_argument('--domain', type=str, required=False, help='Path to the PDDL domain file')
    parser.add_argument('--problem', type=str, required=False, help='Path to the PDDL problem file')
    parser.add_argument('--plan', type=str, help='Path to an existing plan file (optional)')
    parser.add_argument('--planner', type=str, default='fast-downward', help='Name of the planner to use (default: fast-downward)')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Server host address (default: 127.0.0.1)')
    parser.add_argument('--port', type=str, default='5556', help='Server port (default: 5556)')

    args = parser.parse_args()

    # Check if we are in interactive mode (no domain/problem provided)
    if not args.domain and not args.problem and not args.plan:
        interactive_mode(args.host, args.port)
        return

    try:
        if args.plan:
            # If plan is provided, we need domain and problem
            if not args.domain or not args.problem:
                print("Error: --domain and --problem are required when providing --plan.")
                sys.exit(1)

            pdsim_pddl_userplan(
                domain_path=args.domain,
                problem_path=args.problem,
                plan_path=args.plan,
                host=args.host,
                port=args.port
            )
        elif args.domain and args.problem:
            pdsim_pddl_doplan(
                domain_path=args.domain,
                problem_path=args.problem,
                planner_name=args.planner,
                host=args.host,
                port=args.port,
                planner_selection_callback=cli_planner_selector
            )
        else:
            print("Error: Please provide --domain and --problem, or run without arguments for interactive mode.")
            sys.exit(1)
            
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
