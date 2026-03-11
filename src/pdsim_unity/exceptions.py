class PdSimError(Exception):
    """Base exception for PDSim Backend."""
    pass

class NoPlanFoundError(PdSimError):
    """Raised when no plan can be found for the problem."""
    pass

class PlannerNotApplicableError(PdSimError):
    """Raised when the requested planner cannot solve the problem."""
    pass

class ParsingError(PdSimError):
    """Raised when PDDL parsing fails."""
    pass
