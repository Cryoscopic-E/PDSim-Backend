import sys
import os
import runpy
from typing import Optional, Callable
from rich.console import Console
from unified_planning.model import Problem
from pdsim_unity.server_manager import ServerManager
from pdsim_unity.ui.prompts import cli_planner_selector
import pdsim_unity.planning as planning

console = Console()

def create_upf_interceptor(manager: ServerManager, script_name: str):
    """
    Creates a replacement function for pdsim_unity.pdsim_upf that captures data
    instead of blocking.
    """
    def interceptor(problem_upf: Problem, planner_name: str, host: str = '127.0.0.1', port: str = '5556', planner_selection_callback: Optional[Callable] = None):
        # Use CLI selector if script didn't provide one
        real_cb = planner_selection_callback if planner_selection_callback else cli_planner_selector
        
        console.print(f"[dim]Intercepted pdsim_upf call from {script_name}[/dim]")
        
        with console.status("[bold green]Planning (UPF)...[/bold green]", spinner="dots"):
            try:
                # Prepare the problem and solve it
                prob, result, replan_cb = planning.prepare_upf(problem_upf, planner_name, real_cb)
                
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
            except Exception as e:
                console.print(f"[bold red]Error in UPF Planning:[/bold red] {e}")
                raise e # Re-raise to stop script execution

    return interceptor

def run_upf_script(manager: ServerManager, script_file: str):
    script_dir = os.path.dirname(script_file)
    script_name = os.path.basename(script_file)
    
    # Save original state
    original_sys_path = sys.path[:]
    original_pdsim_upf = getattr(planning, 'pdsim_upf', None)
    
    # Patch
    sys.path.insert(0, script_dir)
    setattr(planning, 'pdsim_upf', create_upf_interceptor(manager, script_name))

    # Add pdsim_unity to sys.modules under 'pdsim_unity' if it's not already there
    # This allows scripts to do 'from pdsim_unity import pdsim_upf'
    import pdsim_unity
    sys.modules['pdsim_unity'] = pdsim_unity

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
        if original_pdsim_upf:
            setattr(planning, 'pdsim_upf', original_pdsim_upf)
