from typing import List
import questionary

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
