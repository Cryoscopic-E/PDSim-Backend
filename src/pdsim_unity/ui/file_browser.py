import os
import questionary
from typing import List, Optional, Union, Callable
from rich.console import Console

console = Console()

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
