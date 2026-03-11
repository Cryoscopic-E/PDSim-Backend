import time
from rich.console import Console
from pdsim_unity.server_manager import ServerManager

console = Console()

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
