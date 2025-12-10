from typing import Any, List, Optional
from unified_planning.model import Problem, Object, FNode

class PdSimProblem:
    """
    Wrapper around unified_planning.model.Problem to handle dynamic modifications
    from the PDSim Unity client.
    """
    def __init__(self, up_problem: Problem):
        self.up_problem = up_problem

    def has_object(self, name: str) -> bool:
        return self.up_problem.has_object(name)

    def has_type(self, name: str) -> bool:
        return self.up_problem.has_type(name)
    
    def user_type(self, name: str):
        return self.up_problem.user_type(name)

    def add_object(self, name: str, type_name: str) -> None:
        if self.has_object(name):
             raise ValueError(f"Object {name} already exists")
        
        if not self.has_type(type_name):
            raise ValueError(f"Type {type_name} not found in problem")
            
        user_type = self.user_type(type_name)
        new_obj = Object(name, user_type)
        self.up_problem.add_object(new_obj)

    def _parse_fluent_expression(self, fluent_name: str, object_names: List[str]) -> FNode:
        if not self.up_problem.has_fluent(fluent_name):
            raise ValueError(f"Fluent {fluent_name} not found")
        
        fluent = self.up_problem.fluent(fluent_name)
        
        objects = []
        for name in object_names:
            if not self.up_problem.has_object(name):
                raise ValueError(f"Object {name} not found")
            objects.append(self.up_problem.object(name))
            
        return fluent(*objects)

    def _parse_value(self, value: Any) -> Any:
        if isinstance(value, str):
            if self.up_problem.has_object(value):
                return self.up_problem.object(value)
        return value

    def set_initial_value(self, fluent_name: str, object_names: List[str], value: Any) -> None:
        expression = self._parse_fluent_expression(fluent_name, object_names)
        parsed_value = self._parse_value(value)
        self.up_problem.set_initial_value(expression, parsed_value)
        # Return description for logging if needed
        return f"{expression} = {parsed_value}"

    def add_goal(self, fluent_name: str, object_names: List[str]) -> None:
        expression = self._parse_fluent_expression(fluent_name, object_names)
        self.up_problem.add_goal(expression)
        return f"{expression}"
