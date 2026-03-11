from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.text import Text
from pdsim_unity.server_manager import ServerManager

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
