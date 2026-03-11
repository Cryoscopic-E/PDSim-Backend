import time
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from pdsim_unity.server_manager import ServerManager
from unified_planning.plans import Plan, SequentialPlan, TimeTriggeredPlan
from unified_planning.engines import PlanGenerationResult

console = Console()

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
