import os
import time
import questionary
from rich.console import Console

from pdsim_unity.server_manager import ServerManager
from pdsim_unity.planning import prepare_pddl_doplan, prepare_pddl_userplan

from pdsim_unity.ui.dashboard import render_dashboard
from pdsim_unity.ui.inspector import inspect_problem_ui
from pdsim_unity.ui.file_browser import browse_files
from pdsim_unity.ui.prompts import cli_planner_selector
from pdsim_unity.ui.logs import view_logs
from pdsim_unity.script_runner import run_upf_script

console = Console()

def interactive_mode(host: str, port: str):
    manager = ServerManager(host, port)
    last_dir = None
    
    def dashboard_header():
        console.print(render_dashboard(manager))
        console.print("") # Spacing

    while True:
        console.clear()
        dashboard_header()

        action = questionary.select(
            "What would you like to do?",
            choices=[
                "Load PDDL Problem",
                "Run Python UPF Script",
                "Inspect Active Problem",
                "Stop Server",
                "View Live Logs",
                "Refresh Console",
                "Quit"
            ],
            instruction="(Ctrl+C to quit)",
            pointer="»",
            style=questionary.Style([
                ('qmark', 'fg:cyan bold'),
                ('question', 'bold'),
                ('answer', 'fg:cyan bold'),
                ('pointer', 'fg:cyan bold'),
                ('highlighted', 'fg:cyan bold'),
            ])
        ).ask()

        if action == "Load PDDL Problem":
            search_paths = ['/data', 'examples']
            
            domain_file = browse_files(search_paths, ".pddl", "Select Domain File:", initial_dir=last_dir, header_func=dashboard_header)
            if not domain_file: continue
            last_dir = os.path.dirname(domain_file)
            
            # Visual cue: Show the selected domain while picking the problem
            problem_file = browse_files(
                search_paths, 
                ".pddl", 
                "Select Problem File:", 
                initial_dir=last_dir,
                header_func=dashboard_header
            )
            if not problem_file: continue
            last_dir = os.path.dirname(problem_file)

            # Optional Plan
            provide_plan = questionary.confirm("Would you like to provide an existing plan file?", default=False).ask()
            plan_file = None
            if provide_plan:
                plan_file = browse_files(search_paths, [".plan", ".txt", ".soln", ".val"], "Select Plan File:", initial_dir=last_dir, header_func=dashboard_header)
                if plan_file: last_dir = os.path.dirname(plan_file)

            with console.status("[bold green]Parsing and Planning...[/bold green]", spinner="dots"):
                try:
                    if plan_file:
                        # Use prepare_pddl_userplan for pre-existing plans
                        problem, result = prepare_pddl_userplan(domain_file, problem_file, plan_file)
                        manager.start_server(
                            problem=problem,
                            result=result,
                            planner_name="User Provided Plan",
                            domain_name=os.path.basename(domain_file),
                            problem_name=os.path.basename(problem_file)
                        )
                    else:
                        # Use prepare_pddl_doplan to get objects without blocking
                        problem, result, cb = prepare_pddl_doplan(
                            domain_file, problem_file, 
                            planner_name='fast-downward', # Default, overridden by callback if needed
                            planner_selection_callback=cli_planner_selector
                        )
                        
                        manager.start_server(
                            problem=problem, 
                            result=result, 
                            planner_name='fast-downward',
                            solve_callback=cb,
                            domain_name=os.path.basename(domain_file),
                            problem_name=os.path.basename(problem_file)
                        )
                    console.print("[bold green]Server Started Successfully![/bold green]")
                    time.sleep(1) # Let user see success
                except Exception as e:
                    console.print(f"[bold red]Error starting server:[/bold red] {e}")
                    questionary.press_any_key_to_continue().ask()

        elif action == "Run Python UPF Script":
            if manager.is_running:
                console.print("[yellow]Stopping active server to free port...[/yellow]")
                manager.stop_server()
                
            search_paths = ['/data', 'examples']
            script_file = browse_files(search_paths, ".py", "Select Python Script:", initial_dir=last_dir, header_func=dashboard_header)
            
            if script_file:
                last_dir = os.path.dirname(script_file)
                console.print(f"[bold]Executing {script_file}...[/bold]")
                run_upf_script(manager, script_file)
                questionary.press_any_key_to_continue().ask()

        elif action == "Inspect Active Problem":
            inspect_problem_ui(manager)

        elif action == "Stop Server":
            manager.stop_server()
            console.print("[bold red]Server stopped.[/bold red]")
            time.sleep(1)

        elif action == "View Live Logs":
            view_logs(manager)

        elif action == "Refresh Console":
            pass # Loop handles clear

        elif action == "Quit" or action is None:
            manager.stop_server()
            console.print("[bold]Goodbye![/bold]")
            import sys
            sys.exit(0)
