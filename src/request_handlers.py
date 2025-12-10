from typing import List, Any, Union, Optional
from unified_planning.grpc.proto_writer import ProtobufWriter

class RequestHandler:
    def __init__(self, server):
        self.server = server
        self.proto_writer = ProtobufWriter()

    def convert_to_protobuf(self, model) -> Optional[bytes]:
        try:
            parse = self.proto_writer.convert(model)
        except Exception as exception:
            print(f"Protobuf conversion error: {exception}")
            return None
        return parse.SerializeToString()

    def handle_ping(self, _data: dict) -> dict:
        return {'status': 'OK'}

    def handle_get_problem(self, _data: dict) -> Union[bytes, dict]:
        # Access the underlying UP problem for protobuf conversion
        converted_problem = self.convert_to_protobuf(self.server.problem.up_problem)
        if converted_problem is not None:
            return converted_problem
        return {'error': 'Failed to convert problem'}

    def handle_get_plan(self, _data: dict) -> Union[bytes, dict]:
        converted_plan = self.convert_to_protobuf(self.server.plan_result)
        if converted_plan is not None:
            return converted_plan
        return {'error': 'Failed to convert plan'}

    def handle_new_object(self, data: dict) -> dict:
        """
        Handles the creation of a new object in the problem.
        Expected data: {"name": "obj_name", "type": "type_name"}
        """
        obj_name = data.get('name')
        type_name = data.get('type')
        
        if not obj_name or not type_name:
            return {'error': 'Missing name or type for new object'}
            
        try:
            self.server.problem.add_object(obj_name, type_name)
            print(f"Added object: {obj_name} of type {type_name}")
            return {'status': 'OK', 'message': f'Object {obj_name} added'}
        except Exception as e:
            print(f"Error adding object: {e}")
            return {'error': str(e)}

    def handle_set_initial_value(self, data: dict) -> dict:
        """
        Sets the initial value of a fluent.
        Expected data: {"fluent_name": "on", "objects": ["a", "b"], "value": true}
        """
        fluent_name = data.get('fluent_name')
        objects = data.get('objects', [])
        value = data.get('value')
        
        if not fluent_name or value is None:
            return {'error': 'Missing fluent_name or value'}

        try:
            desc = self.server.problem.set_initial_value(fluent_name, objects, value)
            print(f"Set init: {desc}")
            return {'status': 'OK', 'message': f'Initial value set for {fluent_name}'}
        except Exception as e:
            print(f"Error setting initial value: {e}")
            return {'error': str(e)}

    def handle_add_goal(self, data: dict) -> dict:
        """
        Adds a goal to the problem.
        Expected data: {"fluent_name": "on", "objects": ["a", "b"]}
        """
        fluent_name = data.get('fluent_name')
        objects = data.get('objects', [])
        
        if not fluent_name:
            return {'error': 'Missing fluent_name'}

        try:
            desc = self.server.problem.add_goal(fluent_name, objects)
            print(f"Added goal: {desc}")
            return {'status': 'OK', 'message': f'Goal added: {fluent_name}'}
        except Exception as e:
            print(f"Error adding goal: {e}")
            return {'error': str(e)}

    def handle_replan(self, _data: dict) -> dict:
        """
        Triggers a replan using the current problem state.
        """
        if not self.server.solve_callback or not self.server.planner_name:
            return {'error': 'Replanning not configured (missing callback or planner name)'}
            
        print("Replanning requested...")
        try:
            # Re-solve the problem. IMPORTANT: Access underlying UP problem here!
            result = self.server.solve_callback(self.server.problem.up_problem, self.server.planner_name)
            
            # Update the plan result on the server instance
            self.server.plan_result = result
            
            if result.plan:
                 print("New plan found.")
                 return {'status': 'OK', 'message': 'Plan updated'}
            else:
                 print("No plan found during replanning.")
                 return {'status': 'FAILED', 'message': 'No plan found'}
        except Exception as e:
            print(f"Replanning error: {e}")
            return {'error': str(e)}