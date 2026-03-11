import argparse
import sys
import os
import time
import runpy
from typing import List, Optional, Union, Callable


try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.align import Align
    from rich.text import Text
    from rich.tree import Tree
    import questionary
    from prompt_toolkit.key_binding import KeyBindings
except ImportError:
    print("Error: 'rich' and 'questionary' are required. Please install them.")
    sys.exit(1)

from planning import pdsim_pddl_doplan, pdsim_pddl_userplan, prepare_pddl_doplan, prepare_pddl_userplan, prepare_upf
from exceptions import PdSimError
from server_manager import ServerManager
from unified_planning.plans import Plan, SequentialPlan, TimeTriggeredPlan
from unified_planning.engines import PlanGenerationResult
from unified_planning.model import Problem

console = Console()

# Escape exit the cli.
def get_keybindings():
    kb = KeyBindings()
    
    @kb.add("escape")
    def _(event):
        event.app.exit(result=None)
    
    return kb

def cli_planner_selector(planners: List[str]) -> str:
    """
    Callback for selecting a planner via Questionary.
    """
    choice = questionary.select(
        "Select planner:",
        choices=planners,
        style=questionary.Style([('answer', 'fg:cyan bold')])
    ).ask()
    
    if choice is None:
        # Fallback default if cancelled (though select usually forces choice)
        return planners[0]
    return choice

def create_upf_interceptor(manager: ServerManager, script_name: str):
    """
    Creates a replacement function for pdsim_unity.pdsim_upf that captures data
    instead of blocking.
    """
    def interceptor(problem_upf: Problem, planner_name: str, host: str = '127.0.0.1', port: str = '5556', planner_selection_callback: Optional[any] = None):
        # We ignore host/port from the script in favor of the Manager's config,
        # or we could log that we are overriding them.
        
        # Use CLI selector if script didn't provide one
        real_cb = planner_selection_callback if planner_selection_callback else cli_planner_selector
        
        console.print(f"[dim]Intercepted pdsim_upf call from {script_name}[/dim]")
        
        with console.status("[bold green]Planning (UPF)...[/bold green]", spinner="dots"):
            try:
                # Prepare the problem and solve it
                prob, result, replan_cb = prepare_upf(problem_upf, planner_name, real_cb)
                
                # Start the server using the manager (non-blocking thread)
                manager.start_server(
                    problem=prob,
                    result=result,
                    planner_name=planner_name,
                    solve_callback=replan_cb,
                    domain_name="UPF Script",
                    problem_name=script_name
                )
                console.print("[bold green]Server Started Successfully via Script![/bold green]")
                time.sleep(1)
            except Exception as e:
                console.print(f"[bold red]Error in UPF Planning:[/bold red] {e}")
                raise e # Re-raise to stop script execution

    return interceptor

def browse_files(base_paths: List[str], extensions: Union[str, List[str]], prompt: str, initial_dir: Optional[str] = None, header_func: Optional[Callable] = None) -> Optional[str]:
    if isinstance(extensions, str):
        extensions = [extensions]
    
    # Filter base paths to only existing ones
    valid_bases = [os.path.abspath(b) for b in base_paths if os.path.exists(b)]
    if not valid_bases:
        console.print(f"[bold red]None of the search paths exist: {base_paths}[/bold red]")
        return None

    current_dir = initial_dir
    
    # Ensure initial_dir is within one of the valid bases
    if current_dir:
        current_dir = os.path.abspath(current_dir)
        if not any(current_dir.startswith(base) for base in valid_bases):
            current_dir = None

    # If no valid initial_dir, pick a base
    if not current_dir:
        if len(valid_bases) == 1:
            current_dir = valid_bases[0]
        else:
            if header_func:
                console.clear()
                header_func()
            choices = [questionary.Choice(title=f"📁 {b}", value=b) for b in valid_bases]
            choices.append(questionary.Separator())
            choices.append(questionary.Choice(title="❌ Cancel", value="Cancel"))
            
            choice = questionary.select(
                "Select starting directory:",
                choices=choices,
                style=questionary.Style([('answer', 'fg:cyan bold')])
            ).ask()
            
            if choice == "Cancel" or choice is None:
                return None
            current_dir = choice

    while True:
        if header_func:
            console.clear()
            header_func()
            
        try:
            items = os.listdir(current_dir)
        except Exception as e:
            console.print(f"[bold red]Error accessing {current_dir}: {e}[/bold red]")
            # Fallback to nearest base
            current_dir = next((b for b in valid_bases if current_dir.startswith(b)), valid_bases[0])
            time.sleep(1)
            continue

        dirs = []
        files = []
        for item in items:
            if item.startswith('.'): continue
            full_path = os.path.join(current_dir, item)
            if os.path.isdir(full_path):
                dirs.append(item)
            elif any(item.endswith(ext) for ext in extensions):
                files.append(item)
        
        dirs.sort()
        files.sort()
        
        choices = []
        # Only allow going up if we are not already at a base path
        is_at_base = any(os.path.samefile(current_dir, b) for b in valid_bases)
        if not is_at_base:
            choices.append(questionary.Choice(title="⬆️  .. [Go Up]", value="UP"))
        elif len(valid_bases) > 1:
            choices.append(questionary.Choice(title="🔄 Switch Root Directory", value="SWITCH"))
        
        for d in dirs:
            choices.append(questionary.Choice(title=f"📁 {d}", value=os.path.join(current_dir, d)))
        
        for f in files:
            choices.append(questionary.Choice(title=f"📄 {f}", value=os.path.join(current_dir, f)))
            
        choices.append(questionary.Separator())
        choices.append(questionary.Choice(title="❌ Cancel", value="Cancel"))

        selected = questionary.select(
            prompt,
            choices=choices,
            instruction=f"Current Path: {current_dir}",
            qmark="",
            style=questionary.Style([
                ('answer', 'fg:cyan bold'),
                ('pointer', 'fg:cyan bold'),
                ('separator', 'fg:yellow'),
                ('selected', 'fg:cyan bold'),
                ('instruction', 'fg:cyan italic'),
            ])
        ).ask()
        
        if selected == "Cancel" or selected is None:
            return None
        
        if selected == "UP":
            current_dir = os.path.dirname(current_dir)
        elif selected == "SWITCH":
            # Restart base selection
            if header_func:
                console.clear()
                header_func()
            choices = [questionary.Choice(title=f"📁 {b}", value=b) for b in valid_bases]
            choices.append(questionary.Separator())
            choices.append(questionary.Choice(title="❌ Cancel", value="Cancel"))
            choice = questionary.select("Select starting directory:", choices=choices).ask()
            if choice == "Cancel" or choice is None: return None
            current_dir = choice
        elif os.path.isdir(selected):
            current_dir = selected
        else:
            return selected

def render_dashboard(manager: ServerManager) -> Panel:
    status = manager.get_status()
    
    # Status Color
    status_style = "bold green" if status['status'] == 'Running' else "bold red"
    
    grid = Table.grid(expand=True)
    grid.add_column(justify="center", ratio=1)
    grid.add_column(justify="center", ratio=1)
    
    # Info Table
    info_table = Table(show_header=False, box=None, padding=(0, 2))
    info_table.add_row("[bold]Address:[/bold]", f"{status['host']}:{status['port']}")
    info_table.add_row("[bold]Planner:[/bold]", status['planner'])
    
    # Active Problem
    problem_text = Text()
    if status['status'] == 'Running':
        problem_text.append(f"{status['domain']}", style="cyan")
        problem_text.append(" / ")
        problem_text.append(f"{status['problem']}", style="yellow")
    else:
        problem_text.append("None", style="dim")

    # Combine
    content = Table.grid(expand=True, padding=(1, 1))
    content.add_column(ratio=1)
    
    content.add_row(Align.center(Text(status['status'], style=status_style)))
    content.add_row(Align.center(problem_text))
    content.add_row(Align.center(info_table))

    return Panel(
        content,
        title="[bold blue]PDSim Server Control Plane[/bold blue]",
        border_style="blue",
        padding=(1, 2)
    )

def inspect_problem_ui(manager: ServerManager):
    if not manager.active_problem:
        console.print("[bold red]No problem is currently loaded![/bold red]")
        time.sleep(1)
        return

    problem = manager.active_problem
    result = manager.active_result
    
    while True:
        console.clear()
        console.print(Panel("[bold cyan]Problem Inspector[/bold cyan]", border_style="cyan"))
        console.print(f"[bold]Domain:[/bold] {manager.current_domain}")
        console.print(f"[bold]Problem:[/bold] {manager.current_problem}")
        console.print("")

        action = questionary.select(
            "What would you like to inspect?",
            choices=[
                "View Generated Plan",
                "View Problem Objects",
                "View Fluents & Actions",
                "View Initial State",
                "Back to Main Menu"
            ],
            instruction="(Ctrl+C to go back)",
            pointer="»",
            style=questionary.Style([('answer', 'fg:cyan bold')])
        ).ask()
        
        if action == "Back to Main Menu" or action is None:
            break
            
        elif action == "View Generated Plan":
            console.print("\n[bold underline]Generated Plan[/bold underline]")
            
            # Extract plan from result if needed
            plan = None
            if isinstance(result, PlanGenerationResult):
                plan = result.plan
            elif isinstance(result, Plan):
                plan = result
            
            if not plan:
                console.print("[yellow]No plan available (or problem deemed unsolvable).[/yellow]")
            else:
                table = Table(show_header=True, header_style="bold magenta")
                
                if isinstance(plan, SequentialPlan):
                    table.add_column("Step", style="dim")
                    table.add_column("Action")
                    for i, action in enumerate(plan.actions):
                        table.add_row(str(i), str(action))
                elif isinstance(plan, TimeTriggeredPlan):
                    table.add_column("Start", style="dim")
                    table.add_column("Action")
                    table.add_column("Duration", style="dim")
                    for start, action, duration in plan.timed_actions:
                        table.add_row(str(start), str(action), str(duration))
                else:
                    table.add_column("Content")
                    table.add_row(str(plan))
                    
                console.print(table)
                
        elif action == "View Problem Objects":
            console.print("\n[bold underline]Problem Objects[/bold underline]")
            tree = Tree("[bold]Objects by Type[/bold]")
            
            # Group objects by type
            objects_by_type = {}
            for obj in problem.all_objects:
                t_name = str(obj.type)
                if t_name not in objects_by_type:
                    objects_by_type[t_name] = []
                objects_by_type[t_name].append(obj.name)
            
            for t_name, objs in objects_by_type.items():
                branch = tree.add(f"[cyan]{t_name}[/cyan]")
                for o in objs:
                    branch.add(o)
            
            console.print(tree)
            
        elif action == "View Fluents & Actions":
            console.print("\n[bold underline]Fluents (Predicates/Functions)[/bold underline]")
            f_table = Table(show_header=True, header_style="bold yellow")
            f_table.add_column("Name", style="bold")
            f_table.add_column("Signature")
            
            for f in problem.fluents:
                sig = ", ".join([f"{p.name}: {p.type}" for p in f.signature])
                f_table.add_row(f.name, f"({sig}) -> {f.type}")
            console.print(f_table)
            
            console.print("\n[bold underline]Actions[/bold underline]")
            a_table = Table(show_header=True, header_style="bold green")
            a_table.add_column("Name", style="bold")
            a_table.add_column("Parameters")
            
            for a in problem.actions:
                params = ", ".join([f"{p.name}: {p.type}" for p in a.parameters])
                a_table.add_row(a.name, f"({params})")
            console.print(a_table)
            
        elif action == "View Initial State":
            console.print("\n[bold underline]Initial State[/bold underline]")
            table = Table(show_header=True, header_style="bold blue")
            table.add_column("Fluent")
            table.add_column("Value")
            
            # Problem.initial_values is a dictionary
            # Note: This can be large
            count = 0
            for f, v in problem.initial_values.items():
                table.add_row(str(f), str(v))
                count += 1
                if count >= 100:
                    table.add_row("...", "Trancated (Too many items)")
                    break
            console.print(table)
            
        questionary.press_any_key_to_continue().ask()

def view_logs(manager: ServerManager):
    console.print("\n[bold]--- Server Logs (Press Ctrl+C to exit) ---[/bold]")
    try:
        while True:
            logs = manager.drain_logs()
            for log in logs:
                # Basic coloring for log levels
                if "ERROR" in log:
                    console.print(log, style="red")
                elif "WARNING" in log:
                    console.print(log, style="yellow")
                else:
                    console.print(log)
            time.sleep(0.5)
    except KeyboardInterrupt:
        console.print("\n[dim]Exiting logs view...[/dim]")

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
                
                # Prepare environment for execution
                script_dir = os.path.dirname(script_file)
                script_name = os.path.basename(script_file)
                
                # Save original state
                original_sys_path = sys.path[:]
                
                import planning
                original_prepare_upf = planning.prepare_upf
                
                # Patch
                sys.path.insert(0, script_dir)
                
                try:
                    # Execute script in this process
                    runpy.run_path(script_file, run_name="__main__")
                except KeyboardInterrupt:
                    console.print("\n[yellow]Script interrupted.[/yellow]")
                except Exception as e:
                    console.print(f"[bold red]Error executing script:[/bold red] {e}")
                finally:
                    # Restore state
                    sys.path = original_sys_path
                
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
            sys.exit(0)

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
